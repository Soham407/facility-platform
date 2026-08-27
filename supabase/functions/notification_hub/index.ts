import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const whatsappToken = Deno.env.get("WHATSAPP_TOKEN") ?? "";
const twilioSid = Deno.env.get("TWILIO_ACCOUNT_SID") ?? "";
const twilioToken = Deno.env.get("TWILIO_AUTH_TOKEN") ?? "";

const supabase = createClient(supabaseUrl, supabaseServiceKey);

serve(async (req) => {
  try {
    // Expected to be triggered via pg_net or cron, reading from notification_queue
    const { data: notifications, error } = await supabase
      .from("notification_queue")
      .select("*")
      .eq("status", "pending")
      .limit(10);

    if (error) throw error;
    if (!notifications || notifications.length === 0) {
      return new Response(JSON.stringify({ message: "No pending notifications" }), {
        headers: { "Content-Type": "application/json" },
        status: 200,
      });
    }

    const processed = [];
    const failed = [];

    for (const notif of notifications) {
      try {
        // Mark as processing
        await supabase
          .from("notification_queue")
          .update({ status: "processing" })
          .eq("id", notif.id);

        let dispatchSuccess = false;

        // Route logic: Try WhatsApp first (per ADHD provocation)
        if (whatsappToken) {
          console.log(`Sending WhatsApp message for ${notif.entity_type}:${notif.entity_id}`);
          // Simulate WhatsApp dispatch
          // const res = await fetch('https://graph.facebook.com/v17.0/PHONE_ID/messages', { ... })
          dispatchSuccess = true; 
        } 
        
        // Fallback to Twilio if WhatsApp not configured or failed
        if (!dispatchSuccess && twilioSid && twilioToken) {
          console.log(`Sending Twilio SMS fallback for ${notif.entity_type}:${notif.entity_id}`);
          // Simulate Twilio dispatch
          dispatchSuccess = true;
        }

        if (dispatchSuccess) {
          await supabase
            .from("notification_queue")
            .update({ status: "completed", processed_at: new Date().toISOString() })
            .eq("id", notif.id);
          processed.push(notif.id);
        } else {
          throw new Error("No dispatch providers configured or all failed");
        }
      } catch (err) {
        console.error(`Failed to process notification ${notif.id}`, err);
        await supabase
          .from("notification_queue")
          .update({ 
            status: "failed", 
            error_message: err instanceof Error ? err.message : "Unknown error",
            processed_at: new Date().toISOString() 
          })
          .eq("id", notif.id);
        failed.push(notif.id);
      }
    }

    return new Response(JSON.stringify({ processed, failed }), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  } catch (err) {
    console.error("Hub Execution Error", err);
    return new Response(JSON.stringify({ error: err instanceof Error ? err.message : "Unknown error" }), {
      headers: { "Content-Type": "application/json" },
      status: 500,
    });
  }
});
