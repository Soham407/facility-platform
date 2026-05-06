Project: FacilityPro (Next.js 16 App Router + Supabase)   
  Working dir: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web           
                                                                                       
  ## Status as of 2026-04-26                                                           
                                                                                       
  E2E suite: 115/115 passing on smoke-chromium profile.                                
                                                                                
  RLS: 19/19 passing (test_rls.sh in facility-platform/).                              
  All guard/resident tables locked down. Done.                                         
                                                                                       
  ## What exists already                                                               
                                                            
  Interaction specs already written (full suite, not smoke):                           
  - e2e/procurement-interactions.spec.ts       (211 lines — raise PO, send to vendor,  
  PO detail)                                                                         
  - e2e/society-security-interactions.spec.ts  (575 lines — guard station, visitor     
  register/exit,                                                                  
                                                 resident quick actions, panic alerts, 
  checklists, etc.)                                                                   
  - e2e/buyer-request-interactions.spec.ts     (135 lines)                             
  - e2e/supplier-indent-interactions.spec.ts   (232 lines)  
                                                          
  These run in full suite (E2E_SUITE=full) but NOT in smoke.
  Smoke profile only runs: roles-*.spec.ts, auth-rbac-edge-cases, auth-certification,  
  api-authz, security-baseline, admin-procurement, buyer-order-flow, guard-routine.  
                                                                                       
  ## Task                                                   
                                                                                       
  Run the interaction specs to see which pass/fail, then fix failures.
  Start with:                                                                          
    npx playwright test e2e/procurement-interactions.spec.ts --project=chromium
  --reporter=list                                                                      
    npx playwright test e2e/society-security-interactions.spec.ts --project=chromium   
  --reporter=list                                                                   
                                                                                       
  Auth: uses fixtures in e2e/fixtures/ and global-setup.ts (Supabase magic-link token
  approach).                                                                           
  Supabase URL: https://wwhbdgwfodumognpkgrf.supabase.co
  Anon key and service key are in .env.local.                                          
                                                                                       
  Key RLS context: guard auth chain is                                                 
    auth.uid() → employees.auth_user_id → security_guards.employee_id                  
    gps_tracking.employee_id stores security_guards.id (not employees.id)              
  Resident: auth.uid() → residents.auth_user_id                                        
  Only working helper fn in live DB: get_user_role()::TEXT                             
                                                                                       
  Test user emails: sohamb1@gmail.com (guard), resident@test.com (resident)            
  Admin login is handled by global-setup.ts (check that file for credentials). 