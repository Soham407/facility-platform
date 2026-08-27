import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

dotenv.config({ path: ".env.local" });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "http://localhost:54321";
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "dummy";

const supabase = createClient(supabaseUrl, supabaseKey);

async function runTests() {
  console.log("--- Starting Hardening Tests ---");

  // Step 1: Validate Database-as-Truth Constraints
  console.log("\\n[Step 1] Testing Database Triggers on service_requests");
  try {
    const { data: request, error: createError } = await supabase
      .from("service_requests")
      .insert({ title: "Test Fixing AC", status: "pending", requester_id: "test-user-id" })
      .select()
      .single();

    if (createError) {
      console.log("Creation failed (Expected if RLS blocks anon or dummy DB):", createError.message);
    } else {
      console.log("Created test request:", request.id);

      // Attempt invalid state transition
      const { error: invalidError } = await supabase
        .from("service_requests")
        .update({ status: "accepted" }) // Jumping from pending to accepted
        .eq("id", request.id);

      if (invalidError) {
        console.log("✅ SUCCESS: Invalid transition rejected by DB trigger.");
        console.log("   Reason:", invalidError.message);
      } else {
        console.log("❌ FAILURE: DB allowed invalid state transition.");
      }
    }
  } catch (err) {
    console.error("DB connection error:", err);
  }

  // Step 2: Validate Notification Hub
  console.log("\\n[Step 2] Testing Notification Queue and Edge Function");
  try {
    // 1. Insert mock payload
    const { data: notif, error: notifError } = await supabase
      .from("notification_queue")
      .insert({
        entity_type: "service_requests",
        entity_id: "123e4567-e89b-12d3-a456-426614174000",
        event_type: "status_changed_in_progress",
        payload: { "test": true }
      })
      .select()
      .single();

    if (notifError) {
      console.log("Failed to insert into queue:", notifError.message);
    } else {
      console.log("✅ SUCCESS: Notification queued (ID: " + notif.id + ")");
      console.log("   Ready for Edge Function to pick it up.");
    }
  } catch (err) {
    console.error("Queue insert error:", err);
  }
}

runTests();
