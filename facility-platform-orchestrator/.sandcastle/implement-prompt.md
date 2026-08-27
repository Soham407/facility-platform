# TASK

Implement issue {{TASK_ID}}: {{ISSUE_TITLE}}

Fetch the full issue spec (including the Agent Brief comment):

```bash
gh issue view {{TASK_ID}} --comments --repo Soham407/Solvesxx_mobile
```

The **"## Agent Brief"** comment is the authoritative contract. The issue body is context only.

Work on branch `{{BRANCH}}`.

Read `AGENTS.md` at the repo root before writing any code.

---

# CONTEXT

Recent commits:

<recent-commits>

!`git log -n 10 --format="%H %ad %s" --date=short`

</recent-commits>

This is **Solvesxx_mobile** — a React Native / Expo SDK 55 app.

## Key architecture

- **Role navigators**: `src/navigation/{Role}Navigator.tsx` — bottom-tab shell per role
- **Screens**: `src/screens/{role}/{Role}{Feature}Screen.tsx`
- **Stores**: `src/store/use{Role}Store.ts` — Zustand with `bootstrap(profile)` + `hasHydrated`
- **Backend**: `src/lib/{role}Backend.ts` — Supabase RPC wrappers only
- **Navigation types**: `src/navigation/types.ts` — tab param list types
- **Maestro flows**: `qa_agent/maestro/` — E2E smoke tests (written BEFORE implementation)

## Files you MUST NOT modify

These were set up in Issue 0 (the pre-stub issue) to prevent merge conflicts:

- `src/navigation/RoleNavigator.tsx` — already imports and routes your role
- `src/navigation/types.ts` — already has your tab param list type
- `src/lib/mobileBackend.ts` — shared file; use `src/lib/{role}Backend.ts` instead
- `src/screens/auth/LoginScreen.tsx` — already has your preview login button

## Pattern files to read before writing

```bash
cat src/navigation/BuyerNavigator.tsx        # navigator pattern
cat src/store/useBuyerStore.ts               # store pattern (first 60 lines)
cat qa_agent/maestro/buyer_smoke.yaml        # Maestro flow pattern
cat src/screens/buyer/BuyerHomeScreen.tsx    # screen pattern
```

---

# TEST-DRIVEN DEVELOPMENT (TDD)

Use vertical slices: one behavior at a time — RED then GREEN.

## STEP 1 — RED: Write the Maestro smoke test FIRST

Create `qa_agent/maestro/{role}_smoke.yaml` BEFORE writing any screen code.

This file is your specification contract. It defines exactly what testIDs and labels the screens must expose.

Pattern (adapt `{role}`, `{prefix}`, and tab names from the Agent Brief):

```yaml
appId: com.facilitypro.mobile
---
- launchApp
- extendedWaitUntil:
    visible: "Mobile OTP Sign-In"
    timeout: 30000
- scrollUntilVisible:
    element:
      id: qa_login_preview_{role}
    direction: DOWN
    timeout: 30000
- tapOn:
    id: qa_login_preview_{role}
- extendedWaitUntil:
    visible:
      id: qa_{prefix}_tab_home
    timeout: 30000
- assertVisible:
    id: qa_{prefix}_tab_{tab2}
- assertVisible:
    id: qa_{prefix}_tab_{tab3}
- tapOn:
    id: qa_{prefix}_tab_{tab2}
- assertVisible: "{Tab2 visible label}"
- tapOn:
    id: qa_{prefix}_tab_home
- assertVisible: "{Home visible label}"
```

Example for `company_hod` role with prefix `hod`:
- Login button testID: `qa_login_preview_company_hod`
- Home tab testID: `qa_hod_tab_home`
- Approvals tab testID: `qa_hod_tab_approvals`
- Team tab testID: `qa_hod_tab_team`

The testIDs in your Maestro YAML must match the `tabBarButtonTestID` values in your Navigator EXACTLY.

## STEP 2 — GREEN: Implement the navigator

Your stub navigator at `src/navigation/{Role}Navigator.tsx` was created by Issue 0. Replace its placeholder content with a real bottom-tab navigator.

**Rules**:
- Copy `src/navigation/BuyerNavigator.tsx` as the base pattern
- `tabBarButtonTestID` values must match your Maestro YAML exactly
- Call `bootstrap(profile)` from your store on mount via `useEffect`
- Show `<LoadingScreen />` while `!hasHydrated`
- Use icons from `lucide-react-native`

## STEP 3 — GREEN: Create each screen (one at a time)

For each tab, create `src/screens/{role}/{Role}{Tab}Screen.tsx`.

**Rules**:
- Read data from your role store, not from `mobileBackend.ts` directly
- Show a loading state while data loads
- Show the data content described in the Agent Brief
- Expose at least one visible text string that the Maestro `assertVisible` can match

## STEP 4 — GREEN: Create the Zustand store

Create `src/store/use{Role}Store.ts`.

Must export:
- `bootstrap(profile: AppUserProfile | null): void` — called on navigator mount
- `hasHydrated: boolean` — false until first load completes
- All state and actions described in the Agent Brief

Call your backend from the store, not from screens.

## STEP 5 — GREEN: Create the backend file

Create `src/lib/{role}Backend.ts`. Example structure:

```ts
import { supabase } from './supabase';
import type { AppUserProfile } from '../types/app';

export async function fetch{Role}Summary(profile: AppUserProfile) {
  const { data, error } = await supabase.rpc('get_{role}_summary', {
    p_user_id: profile.userId,
    p_company_id: profile.companyId,
  });
  if (error) throw error;
  return data as {Role}SummaryRecord[];
}
```

Use `supabase.rpc(...)` for all reads and mutations. Match RPC function names from the Agent Brief.

---

# VERIFICATION

After all screens are implemented:

```bash
npx tsc --noEmit
```

Fix every TypeScript error before committing. Do not suppress errors with `any` or `@ts-ignore` unless the Agent Brief explicitly permits it.

---

# COMMIT

One commit per completed behavior cycle is fine. Final commit must:

1. Start with `SOLVESXX:` prefix
2. Reference the issue: `(#{{TASK_ID}})`
3. List all files created
4. List the tab testIDs added (for Maestro traceability)

Example:
```
SOLVESXX: Add HODNavigator + screens + store for company_hod (#2)

Files created:
- src/navigation/HODNavigator.tsx
- src/screens/company_hod/HODHomeScreen.tsx
- src/screens/company_hod/HODApprovalsScreen.tsx
- src/screens/company_hod/HODTeamScreen.tsx
- src/store/useHODStore.ts
- src/lib/hodBackend.ts
- qa_agent/maestro/company_hod_smoke.yaml

Tab testIDs: qa_hod_tab_home, qa_hod_tab_approvals, qa_hod_tab_team
```

Do **not** close the issue — the merge phase does that.

Once complete, output `<promise>COMPLETE</promise>`.

---

# STRICT RULES

1. DO NOT modify `src/navigation/RoleNavigator.tsx`
2. DO NOT modify `src/navigation/types.ts`
3. DO NOT modify `src/lib/mobileBackend.ts`
4. DO NOT modify `src/screens/auth/LoginScreen.tsx`
5. Work ONLY on the single issue `{{TASK_ID}}` — no scope creep
6. Tab `testID` values in Navigator MUST match your Maestro YAML exactly
7. Create `src/lib/{role}Backend.ts` (NOT inside mobileBackend.ts)
8. Maestro YAML goes in `qa_agent/maestro/{role}_smoke.yaml` (create `qa_agent/maestro/` dir if missing)
