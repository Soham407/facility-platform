-- ============================================================
-- GUARD & RESIDENT DEMO SEED — Run in Supabase Studio SQL Editor
-- Remote project: wwhbdgwfodumognpkgrf.supabase.co
--
-- FULL PROCESS (read before running):
--
--  STEP 1  → Go to Supabase Studio → Authentication → Users → Add User
--            Create two users (email + any password — used for auth linkage only):
--              Guard:    email = guard.demo@facilitypro.local   password = FacilityPro@2026
--              Resident: email = resident.demo@facilitypro.local password = FacilityPro@2026
--            Copy both UUIDs.
--
--  STEP 2  → Replace the 4 placeholders below with real values:
--              GUARD_AUTH_UUID     → UUID of the guard auth user you just created
--              GUARD_PHONE         → phone number the guard will type in the app (e.g. +919876543210)
--              RESIDENT_AUTH_UUID  → UUID of the resident auth user
--              RESIDENT_PHONE      → phone number the resident will type in the app
--
--  STEP 3  → Run Part 1 (foundation)
--  STEP 4  → Run Part 2 (guard)
--  STEP 5  → Run Part 3 (resident)
--  STEP 6  → Run the Verification query at the bottom
--
--  STEP 7  → Set Vercel env vars (see instructions at end of this file)
-- ============================================================


-- ============================================================
-- PART 1: Foundation — societies, building, flat, gate location
-- Safe to run multiple times (ON CONFLICT DO NOTHING).
-- ============================================================

-- Add society_id to company_locations if the column doesn't exist yet
ALTER TABLE company_locations
  ADD COLUMN IF NOT EXISTS society_id UUID REFERENCES societies(id);

-- Demo society
INSERT INTO societies (id, society_code, society_name, address, city, state, pincode, is_active)
VALUES (
  'a0000000-0000-0000-0000-000000000001',
  'DEMO-SOC-01',
  'FacilityPro Demo Society',
  '100 Tech Park Road',
  'Mumbai',
  'Maharashtra',
  '400001',
  true
) ON CONFLICT (society_code) DO NOTHING;

-- Main gate — linked to society
INSERT INTO company_locations (id, location_code, location_name, location_type, is_active, society_id)
VALUES (
  'b0000000-0000-0000-0000-000000000002',
  'GATE-MAIN-01',
  'Main Gate',
  'gate',
  true,
  'a0000000-0000-0000-0000-000000000001'
) ON CONFLICT (location_code) DO NOTHING;

-- Building
INSERT INTO buildings (id, building_code, building_name, society_id, total_floors, is_active)
VALUES (
  'c0000000-0000-0000-0000-000000000003',
  'WING-A',
  'Wing A',
  'a0000000-0000-0000-0000-000000000001',
  5,
  true
) ON CONFLICT DO NOTHING;

-- Flat (for resident)
INSERT INTO flats (id, flat_number, building_id, floor_number, flat_type, is_occupied, is_active)
VALUES (
  'd0000000-0000-0000-0000-000000000004',
  '101',
  'c0000000-0000-0000-0000-000000000003',
  1,
  '2bhk',
  true,
  true
) ON CONFLICT DO NOTHING;

-- Demo shift (required by demo OTP verification for guard)
INSERT INTO shifts (id, shift_code, shift_name, start_time, end_time, duration_hours, is_active)
VALUES (
  'e0000000-0000-0000-0000-000000000005',
  'SHIFT-DAY',
  'Day Shift',
  '08:00:00',
  '20:00:00',
  12.0,
  true
) ON CONFLICT (shift_code) DO NOTHING;

SELECT 'Part 1 complete — foundation created' AS status;


-- ============================================================
-- PART 2: Guard setup
-- Replace GUARD_AUTH_UUID and GUARD_PHONE before running.
-- ============================================================

DO $$
DECLARE
  v_guard_auth_id  UUID := 'GUARD_AUTH_UUID';        -- ← REPLACE
  v_guard_phone    TEXT := '+91GUARD_PHONE';          -- ← REPLACE (e.g. +919876543210)
  v_guard_email    TEXT := 'guard.demo@facilitypro.local';
  v_employee_id    UUID := 'f0000000-0000-0000-0000-000000000006';
  v_guard_id       UUID := '10000000-0000-0000-0000-000000000010';
  v_role_id        UUID;
BEGIN
  IF v_guard_auth_id::TEXT = 'GUARD_AUTH_UUID' THEN
    RAISE EXCEPTION 'Replace GUARD_AUTH_UUID with the real auth user UUID from Studio.';
  END IF;

  IF v_guard_phone = '+91GUARD_PHONE' THEN
    RAISE EXCEPTION 'Replace GUARD_PHONE with the guard''s test phone number.';
  END IF;

  -- Get security_guard role ID
  SELECT id INTO v_role_id FROM roles WHERE role_name = 'security_guard' LIMIT 1;
  IF v_role_id IS NULL THEN
    RAISE EXCEPTION 'Role "security_guard" not found in roles table. Run the roles seed migration first.';
  END IF;

  -- Employee record
  INSERT INTO employees (id, employee_code, first_name, last_name, phone, date_of_joining, is_active, auth_user_id)
  VALUES (v_employee_id, 'EMP-G-DEMO-01', 'Demo', 'Guard', v_guard_phone, CURRENT_DATE, true, v_guard_auth_id)
  ON CONFLICT (employee_code) DO UPDATE SET auth_user_id = v_guard_auth_id, phone = v_guard_phone;

  -- Security guard record
  INSERT INTO security_guards (id, employee_id, guard_code, grade, is_active, assigned_location_id)
  VALUES (v_guard_id, v_employee_id, 'GRD-DEMO-01', 'A', true, 'b0000000-0000-0000-0000-000000000002')
  ON CONFLICT (guard_code) DO UPDATE SET employee_id = v_employee_id, assigned_location_id = 'b0000000-0000-0000-0000-000000000002';

  -- Shift assignment (required by demo OTP verify flow)
  INSERT INTO employee_shift_assignments (employee_id, shift_id, assigned_from, is_active)
  VALUES (v_employee_id, 'e0000000-0000-0000-0000-000000000005', CURRENT_DATE, true)
  ON CONFLICT DO NOTHING;

  -- public.users row (required by get_guard_id() and demo OTP verify)
  INSERT INTO public.users (id, employee_id, role_id, username, full_name, email, phone, is_active)
  VALUES (
    v_guard_auth_id,
    v_employee_id,
    v_role_id,
    'guard_demo_01',
    'Demo Guard',
    v_guard_email,
    v_guard_phone,
    true
  )
  ON CONFLICT (id) DO UPDATE
    SET employee_id = v_employee_id,
        role_id = v_role_id,
        phone = v_guard_phone;

  RAISE NOTICE 'Guard setup complete. employee_id=%, guard_id=%', v_employee_id, v_guard_id;
END $$;

SELECT 'Part 2 complete — guard created' AS status;


-- ============================================================
-- PART 3: Resident setup
-- Replace RESIDENT_AUTH_UUID and RESIDENT_PHONE before running.
-- ============================================================

DO $$
DECLARE
  v_resident_auth_id UUID := 'RESIDENT_AUTH_UUID';   -- ← REPLACE
  v_resident_phone   TEXT := '+91RESIDENT_PHONE';    -- ← REPLACE (e.g. +919999988888)
  v_resident_email   TEXT := 'resident.demo@facilitypro.local';
  v_resident_id      UUID := '20000000-0000-0000-0000-000000000020';
  v_role_id          UUID;
BEGIN
  IF v_resident_auth_id::TEXT = 'RESIDENT_AUTH_UUID' THEN
    RAISE EXCEPTION 'Replace RESIDENT_AUTH_UUID with the real auth user UUID from Studio.';
  END IF;

  IF v_resident_phone = '+91RESIDENT_PHONE' THEN
    RAISE EXCEPTION 'Replace RESIDENT_PHONE with the resident''s test phone number.';
  END IF;

  -- Get resident role ID
  SELECT id INTO v_role_id FROM roles WHERE role_name = 'resident' LIMIT 1;
  IF v_role_id IS NULL THEN
    RAISE EXCEPTION 'Role "resident" not found in roles table.';
  END IF;

  -- Resident record
  INSERT INTO residents (
    id, resident_code, flat_id, full_name, relation,
    phone, is_primary_contact, move_in_date, is_active, auth_user_id
  ) VALUES (
    v_resident_id, 'RES-DEMO-01',
    'd0000000-0000-0000-0000-000000000004',
    'Demo Resident', 'owner',
    v_resident_phone, true, CURRENT_DATE, true, v_resident_auth_id
  )
  ON CONFLICT (resident_code) DO UPDATE
    SET auth_user_id = v_resident_auth_id,
        phone = v_resident_phone;

  -- public.users row (required by demo OTP verify — it checks role = 'resident')
  INSERT INTO public.users (id, role_id, username, full_name, email, phone, is_active)
  VALUES (
    v_resident_auth_id,
    v_role_id,
    'resident_demo_01',
    'Demo Resident',
    v_resident_email,
    v_resident_phone,
    true
  )
  ON CONFLICT (id) DO UPDATE
    SET role_id = v_role_id,
        phone = v_resident_phone;

  RAISE NOTICE 'Resident setup complete. resident_id=%', v_resident_id;
END $$;

SELECT 'Part 3 complete — resident created' AS status;


-- ============================================================
-- VERIFICATION — Run after all 3 parts
-- ============================================================
SELECT
  'Guard' AS role,
  u.full_name, u.phone,
  sg.guard_code,
  cl.location_name AS gate,
  s.society_name,
  (SELECT COUNT(*)::TEXT FROM employee_shift_assignments esa
   WHERE esa.employee_id = e.id AND esa.is_active = true) || ' active shift(s)' AS shifts
FROM public.users u
JOIN employees e ON e.id = u.employee_id
JOIN security_guards sg ON sg.employee_id = e.id
JOIN company_locations cl ON cl.id = sg.assigned_location_id
JOIN societies s ON s.id = cl.society_id
WHERE u.username = 'guard_demo_01'

UNION ALL

SELECT
  'Resident' AS role,
  u.full_name, u.phone,
  r.resident_code AS guard_code,
  f.flat_number AS gate,
  s.society_name,
  'flat ' || f.flat_number || ', ' || b.building_name AS shifts
FROM public.users u
JOIN residents r ON r.auth_user_id = u.id
JOIN flats f ON f.id = r.flat_id
JOIN buildings b ON b.id = f.building_id
JOIN societies s ON s.id = b.society_id
WHERE u.username = 'resident_demo_01';


-- ============================================================
-- VERCEL ENV VARS — set these in your Vercel project dashboard
-- Project Settings → Environment Variables → Production + Preview
--
--   DEMO_OTP_ENABLED         = true
--   DEMO_OTP_CODE            = 123456
--   DEMO_OTP_ALLOWED_PHONES  = +91GUARD_PHONE,+91RESIDENT_PHONE
--
-- Also update Solvesxx_web/.env.local (already done):
--   Replace +91GUARD_PHONE and +91RESIDENT_PHONE with the actual numbers.
-- ============================================================
