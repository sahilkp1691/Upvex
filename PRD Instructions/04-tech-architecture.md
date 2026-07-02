# Technical Architecture — v1

## Stack
- **Frontend:** SvelteKit
- **Backend:** FastAPI (Python, async-native — needed for non-blocking AI calls and Celery
  integration)
- **Database:** Postgres (JSONB columns for flexible/variable-shape data — profile answers,
  generated content, gap maps)
- **Task Queue:** Celery + Redis (Redis serves as broker; also usable later for caching hot
  reads like leaderboards)
- **Auth:** Supabase Auth
- **AI Routing:** OpenRouter — model selection configurable per task type (lesson generation,
  quiz generation, diagnostic evaluation), allowing independent cost/quality tuning per
  use case rather than one model for everything

## Why this shape
- FastAPI + Celery is a natural fit for "trigger AI generation, don't block the request" —
  generation calls take seconds, need a background-job pattern with a frontend loading state,
  not a synchronous API response.
- Postgres + JSONB avoids running two databases (relational + document) for a solo-built v1.
  Structured entities (users, topics, concept nodes) stay relational; variable-shape AI outputs
  (lesson bodies, gap maps, raw onboarding answers) live in JSONB columns on the relevant table.
- OpenRouter as an abstraction layer means model choice is a config decision, not a code
  rewrite — important given the explicit goal of testing models for cost/quality per task
  (e.g. Diagnostic Evaluator prioritizes reliability over creativity; lesson generation may
  prioritize the opposite).
- Supabase Auth offloads auth entirely (managed, faster to ship) without requiring the rest of
  the backend to live inside Supabase — FastAPI/Postgres/Celery remain self-managed for full
  control over the core product logic.

## Request/Job Flow (content generation case)
```
SvelteKit (frontend)
   │  user opens concept node
   ▼
FastAPI endpoint
   │  check GeneratedContent cache by ProfileSignature
   ├─ HIT  → return cached content immediately
   └─ MISS → enqueue Celery task → return "pending" status
                 │
                 ▼
           Celery worker (Redis broker)
                 │  assemble prompt: GenerationContract + user vars
                 ▼
           OpenRouter API call (model per task type)
                 │  structured JSON response
                 ▼
           Store in GeneratedContent (Postgres)
                 │
                 ▼
           Frontend polls/subscribes for completion → renders content
```

Frontend should poll or use a lightweight push mechanism (e.g. short-interval polling is fine
for v1; websockets/SSE is a nice-to-have, not required) to know when a pending generation task
completes, and should show branded loading messaging during the wait (gamification touchpoint,
not a bare spinner).

## Diagnostic Evaluator Flow (different from content generation)
Diagnostics are interactive and adaptive within the quiz itself (branching question-to-question),
so this is more likely a **direct synchronous call** (fast model, tight prompt) rather than a
Celery job — latency matters more here than for lesson generation, and the per-question branching
logic needs a quick response to pick the next question.

Final scoring (after quiz completion) can also be synchronous given the Evaluator is designed to
be fast/cheap/reliable rather than creative.

## Deployment (suggested, confirm before building)
- Backend (FastAPI) + Celery workers: containerized, deployed to a platform like Railway,
  Render, or Fly.io for v1 simplicity (avoid full AWS/K8s complexity for a solo-run MVP).
- Postgres: managed instance (Railway/Render/Supabase-hosted Postgres all viable — if using
  Supabase only for Auth, a separate managed Postgres avoids coupling auth and core data,
  though using Supabase's Postgres for both is simpler operationally; decide based on appetite
  for one fewer service to manage vs. cleaner separation).
- Redis: managed instance (most platforms above offer this natively).
- Frontend (SvelteKit): Vercel or same platform as backend, depending on preference.
- Environment/secrets: OpenRouter API key, Supabase keys, DB connection string — standard env
  var management per platform.

## Open Items to Confirm Before/During Build
- Final hosting platform choice.
- Whether Supabase Postgres is reused for core data or kept separate from a dedicated Postgres
  instance.
- Specific OpenRouter models to start testing for: lesson generation, quiz generation,
  diagnostic evaluation (likely three different model choices).
- Polling vs. push mechanism for generation-pending UI state.
- Exact pacing/deadline data shape (per-concept deadlines vs. one overall target date).
