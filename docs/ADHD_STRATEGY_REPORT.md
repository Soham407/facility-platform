# 🧠 ADHD — Divergent Strategy for Closing Facility Platform Gaps

> **Brief:** 68 client requirements audited. 46 done, 14 partial, 5 missing, 13 cross-cutting gaps. The obvious answer is "fix them one by one." We went past that.
>
> **Reframe:** This isn't a feature checklist problem. It's an *architecture completeness* problem — the plumbing (validation, notifications, permissions, file storage) that ties features together is missing.

---

## Wide Set — 30 Ideas, 5 Clusters

### Cluster 1: "Centralize the missing plumbing" plays

| Idea | N | V | F | Score |
|------|---|---|---|-------|
| Hub-and-spoke Edge Function for all missing side-effects (SMS, batch, photos) | 7 | 7 | 8 | **7.25** |
| Blanket Next.js middleware checkpoint quarantining unvalidated POSTs | 6 | 8 | 7 | **7.05** |
| Centralized notification queue table with rate-limiting `[N6 V9 F9]` | 6 | 9 | 9 | **7.95** |
| Durable background job queue for external I/O with exponential backoff | 6 | 8 | 8 | **7.30** |
| Next.js middleware blocking routes unless prerequisite gates cleared | 5 | 8 | 8 | **6.95** |
| pg_net trigger → Make.com for SMS, Push, workflow logic | 8 | 6 | 7 | **7.15** |

### Cluster 2: "Database-as-the-truth" plays

| Idea | N | V | F | Score |
|------|---|---|---|-------|
| RLS policies BEFORE frontend Permission Toggles `[N6 V9 F9]` | 6 | 9 | 9 | **7.95** |
| RLS-exclusive workflow enforcement, not Next.js middleware | 7 | 8 | 9 | **7.90** |
| Materialized views for Soft Services dashboards | 5 | 8 | 7 | **6.70** |
| Append-only event logs for critical state changes | 8 | 6 | 6 | **6.70** |
| Pre-aggregated SQL views for dashboards | 5 | 8 | 7 | **6.70** |

### Cluster 3: "Auto-heal the codebase" plays

| Idea | N | V | F | Score |
|------|---|---|---|-------|
| Zod-crawler scripts auto-converting untyped Supabase fetches `[N8 V7 F8]` | 8 | 7 | 8 | **7.60** |
| Git-hook rule: PRs touching 'partial' files must resolve one gap | 7 | 7 | 7 | **7.00** |
| Stub UI with frustration counters for usage-driven prioritization | 8 | 5 | 6 | **6.30** |
| Upload spore components failing compilation until storage connected | 7 | 5 | 6 | **5.95** |

### Cluster 4: "Graceful degradation" plays

| Idea | N | V | F | Score |
|------|---|---|---|-------|
| Kill-switches hiding broken UI instead of throwing `[N6 V9 F7]` | 6 | 9 | 7 | **7.45** |
| Rip out placeholders → hard error boundaries until integrated | 7 | 7 | 6 | **6.75** |
| Dead buttons → automated intent metric logging | 7 | 6 | 5 | **6.10** |
| Consolidated shipment — collapse 5 missing dashboards into 1 generic view | 5 | 7 | 6 | **6.05** |

### Cluster 5: "Shortcut the unbuilt" plays

| Idea | N | V | F | Score |
|------|---|---|---|-------|
| Cross-docking via webhooks for Recruitment/Ad-Space | 6 | 6 | 5 | **5.75** |
| Fetch interceptor parsing PostgreSQL errors into toasts | 7 | 6 | 5 | **6.10** |
| Reverse logistics 'Returns' table for failing validations | 7 | 5 | 6 | **6.45** |
| JIT support tickets for dead buttons | 5 | 3 | 4 | **3.95** |
| SCENT-LEVEL comments in code for priority signaling | 9 | 4 | 5 | **5.00** |

> Score = `Novelty×0.35 + Viability×0.40 + Fit×0.25`

---

## Converge — Shortlist

### Top 3 Picks

| # | Strategy | Score | Why |
|---|----------|-------|-----|
| ★ | **Database-as-Truth Architecture** | 7.95 | Solves permissions, workflows, AND notifications in one migration. Non-obvious because everyone defaults to fixing the frontend first. |
| 2 | **Hub-and-Spoke + Auto-Healing Crawlers** | 7.60 | Centralizes all scattered plumbing into one Edge Function while automating the tedious Zod typing work. High leverage. |
| 3 | **Graceful Degradation + Durable Queues** | 7.45 | Makes the system shippable *today* by being resilient to its own incompleteness. Buys time. |

### 🚨 Traps (Attractive but Dangerous)

| Idea | Why It's a Trap |
|------|----------------|
| Embedded Notion/Google Forms for missing modules | Unprofessional for an enterprise client who paid for a custom platform |
| Raw JSONB editor for Permission Toggles | Terrible UX, one typo = security hole, client will reject on sight |
| Base64 encode photos into text columns | Bloats PostgreSQL, destroys read performance, kills mobile experience |
| DOM scraping for CSV export | Fragile — breaks on complex cell renderers, JSX tooltips, and nested components |
| JIT support tickets for dead buttons | Delays real implementation, client interprets as "unfinished product" |

---

## Focus — Top 3 Deepened

### ★ Branch 1: Database-as-Truth Architecture

> **Sketch:** All core domain logic moves into PostgreSQL via Supabase. RLS policies restrict data access at the row level. Workflow state transitions (e.g., `Pending → Approved`) are enforced using database triggers and check constraints — invalid updates are physically impossible. When a valid state change occurs, a trigger inserts a payload into a centralized `notification_queue` table. An isolated Supabase Edge Function processes this queue asynchronously, managing rate-limits and dispatching to SMS/Push providers. The Next.js frontend becomes a "dumb" presentation layer that only renders what the database permits. Any unauthorized actions return standard Postgres errors that the frontend translates into user-friendly alerts.

> **Load-bearing risk:** Business logic becomes tightly coupled to PostgreSQL triggers and RLS policies, creating a "black box" that's incredibly difficult to debug, test, and version control without specialized database observability tools.

> **First concrete step:** Write a single SQL migration script to create the `notification_queue` table and apply initial RLS policies to the most critical workflow entity (e.g., `service_requests`).

> **Child ideas:**
> 1. **Dynamic UI generation** — Frontend queries Postgres metadata and RLS definitions to automatically render, hide, or disable buttons without duplicating permission logic in React
> 2. **Audit log byproduct** — Create an append-only `workflow_events` table populated by the same triggers for compliance and time-travel debugging
> 3. **Zero-trust API layer** — Safely expose PostgREST directly to mobile apps, knowing all authorization is bulletproof at the DB level
> 4. **Idempotent notification edge workers** — Dedicated edge function with retries, deduplication, and dead-letter queues entirely outside the core app

---

### Branch 2: Hub-and-Spoke + Auto-Healing Crawlers

> **Sketch:** A single `rpc/hub` Supabase Edge Function acts as a unified command dispatcher for all side-effects. Instead of scattering API calls across Next.js, components dispatch intents (like `TRIGGER_SMS` or `VALIDATE_PHOTO`) to this single hub. The hub uses a strategy pattern to route each intent to its handler with centralized logging and secret management. Concurrently, an AST-based Zod-crawler script runs as a git pre-commit hook, scanning for raw `supabase.from()` fetches. The crawler reads the generated Supabase types, infers the expected data shape, and automatically injects `z.object().parse()` validation wrappers. Developers plug holes by centralizing business logic in one deployable unit while the crawler autonomously hardens data boundaries.

> **Load-bearing risk:** The Edge Function hub becomes a monolithic "God function" with excessive cold start times, deployment collisions, and a blast radius where one failing handler crashes all side-effects.

> **First concrete step:** Write a small AST script using `ts-morph` that scans a single component, finds an untyped `supabase.from()` call, and injects a basic Zod schema import and parser.

> **Child ideas:**
> 1. **Self-Healing Forms** — Crawler auto-generates `react-hook-form` scaffolding whenever it detects new database columns in Supabase types
> 2. **Hub-to-Queue** — Integrate Upstash QStash to convert synchronous intents into durable, retriable background jobs
> 3. **Chaos Engineering** — Hub randomly simulates failures in staging to verify frontend error-handling UI
> 4. **Shadow-Syncing Edge Cache** — Hub caches frequent permission checks in Redis, reducing DB reads

---

### Branch 3: Graceful Degradation + Durable Queues

> **Sketch:** Wrap unfinished features in a Next.js `FeatureToggle` component tied to an edge config acting as a remote kill-switch. When a feature is disabled or errors, the component renders a fallback (silently hides) and logs a telemetry event to Supabase. For critical I/O like photo uploads and SMS, offload from API routes to a durable queue (Inngest or pgmq). The API accepts the payload, enqueues, and immediately returns 200 OK. Background workers process with exponential backoff. This shifts the platform from fragile synchronous errors to resilient async processing and silent feature degradation.

> **Load-bearing risk:** The queue gets clogged with failing jobs (malformed payloads) leading to silent data loss. Users expect immediate feedback but receive none.

> **First concrete step:** Implement an edge-configurable `FeatureToggle` React component, wrap a known incomplete feature (e.g., an export button), and verify it silently logs telemetry instead of crashing.

> **Child ideas:**
> 1. **Optimistic UI + Background Reconciliation** — Show immediate success for uploads; queues reconcile and notify only on permanent failure
> 2. **Analytics-Driven Prioritization** — Telemetry from users clicking degraded features drives the dev backlog
> 3. **Progressive Feature Rollout** — Repurpose kill-switch infra for gradual rollouts to trusted users
> 4. **Automated Degradation on Latency** — Auto-trigger kill-switches if external APIs exceed latency thresholds

---

## 🔮 Provocation

**What if the platform shipped with zero SMS integration and zero file uploads — but with a dead-simple WhatsApp bot that guards, managers, and residents could message, and that wrote directly to the Supabase notification queue?** The scope doc assumes SMS. But the actual users are in India. They already live in WhatsApp. A WhatsApp Business API integration might cover visitor notifications, panic alerts, and checklist reminders in a single channel — cheaper than Twilio SMS, higher engagement, and the client would perceive it as exceeding scope rather than cutting corners.
