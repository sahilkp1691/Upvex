# Upvex (Early Development)

An AI-driven, gamified learning platform for tech skills — derived from "upward vector".
Upvex diagnoses what a learner actually knows, traces weaknesses to their root cause through
a prerequisite knowledge graph, and generates personalized lesson content live instead of
serving a fixed course.

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | SvelteKit (Svelte 5, plain JS, SPA mode) — two competing skins |
| Backend | FastAPI (async), SQLAlchemy 2 |
| Database | Postgres + JSONB (Supabase Postgres or any Postgres) |
| Tasks | Celery + Redis (content generation, daily streak job) |
| Auth | Supabase Auth (JWT verified backend-side; dev bypass mode for local work) |
| AI | OpenRouter — model configurable per task type |

## Repository layout

```
backend/
  app/                 FastAPI app, routes, services, generation, tasks, seed
  tests/
frontend-playful/      Full Playful skin (individuals demo) — port 5173
frontend-soft/         Softened Playful skin (corporate demo) — port 5174
frontend/              Pointer README only (do not deploy)
designs/               Static HTML design references
docker-compose.yml     Redis + local Postgres for development
.env.example           all configuration knobs
```

Both frontends share one backend. Demo either URL independently; promote one to production later by pointing the custom domain at that Railway service.
## Getting started (local development)

Prerequisites: Python 3.11+, Node 20+, Docker.

```bash
# 1. Infrastructure (Redis + local Postgres)
docker compose up -d

# 2. Backend
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp ../.env.example .env          # defaults work out of the box for local dev
.venv/bin/uvicorn app.main:app --port 8000 --reload

# 3. Frontend — pick a skin (or run both)
cd frontend-playful
npm install
npm run dev                      # http://localhost:5173  (full Playful)

# optional second terminal
cd frontend-soft
npm install
npm run dev                      # http://localhost:5174  (softened)
```

Copy the same `VITE_*` keys into each frontend `.env`. Backend `CORS_ORIGINS` must include both local ports (default in `.env.example`).
On first startup the backend creates all tables and seeds: the Data Engineering category,
Apache Spark + SQL topics with full prerequisite graphs, ~60 diagnostic questions, the v1
GenerationContract, and milestone badges.

### Dev mode defaults

- `DEV_AUTH_BYPASS=true` — no Supabase project needed; requests without a token act as a
  local admin user ("Continue as Dev User" on the auth page).
- `CELERY_TASK_ALWAYS_EAGER=true` — content generation runs inline in the API process; no
  worker needed.
- `OPENROUTER_API_KEY` empty — lessons are served as deterministic stubs so every flow works
  offline. Set a key to enable real generation.

### Production-style setup

1. Create a Supabase project. Put its URL, anon key, and JWT secret in `backend/.env`
   (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`) and in both
   `frontend-playful/.env` and `frontend-soft/.env`
   (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`). Set `DEV_AUTH_BYPASS=false`.
   Add both frontend origins (and later the production winner) under Supabase Redirect URLs.
2. Point `DATABASE_URL` at Supabase's Postgres (session pooler, `postgresql+asyncpg://` scheme).
3. Set `CELERY_TASK_ALWAYS_EAGER=false` and run a worker + beat:

```bash
cd backend
.venv/bin/celery -A app.tasks.celery_app worker --loglevel=info
.venv/bin/celery -A app.tasks.celery_app beat --loglevel=info   # daily streak job
```

4. Set `OPENROUTER_API_KEY` and pick models per task type:
   `MODEL_LESSON_GENERATION`, `MODEL_QUIZ_GENERATION`, `MODEL_DIAGNOSTIC_EVALUATOR`.

To grant a user admin access, set `is_admin = true` on their row in the `users` table.

## Tests

```bash
cd backend
.venv/bin/python -m pytest tests/ -q            # unit tests (scoring, graph traversal, sequencing, signature)
.venv/bin/python tests/e2e_smoke.py             # full-flow smoke test against a running server
```

## Railway (one API, two frontends)

| Service | Root Directory | Config file | Typical use |
| --- | --- | --- | --- |
| `api` | `/backend` | `/backend/railway.toml` | Shared API |
| `web-playful` | `/frontend-playful` | `/frontend-playful/railway.toml` | Individuals demo |
| `web-soft` | `/frontend-soft` | `/frontend-soft/railway.toml` | Corporate demo |

Both web services use the same `VITE_API_URL` pointing at the API service. On the API, set
`CORS_ORIGINS` to a comma list of both Railway frontend URLs (plus local ports for dev).

**Promote a winner:** attach the production custom domain to that web service, update
`CORS_ORIGINS` + Supabase redirect URLs, then stop or delete the other web service.

## How the core loop works

1. Onboarding stores a persistent profile (learning style, time, motivation, background, tone).
2. Picking a topic creates a `UserGoal` and starts an adaptive diagnostic (branches up/down
   on correctness, questions tagged to concept nodes).
3. The Diagnostic Evaluator scores deterministically (difficulty + Bloom weighting), grades
   free text via LLM (keyword heuristic as fallback), and finds root gap concepts with a
   recursive CTE walking the prerequisite graph upstream from weak scores.
4. The roadmap labels every concept: tested-out, recommended-next (root gaps first),
   available, or locked.
5. Opening a concept computes a ProfileSignature (topic + concept + difficulty band + root
   gap + learning style + tone) and checks the `GeneratedContent` cache: hit → serve; miss →
   Celery task assembles the active GenerationContract + user variables, calls OpenRouter,
   validates the structured JSON, stores and serves it.
6. Quiz results feed back through the Evaluator: gap map updates, root gaps re-checked,
   XP/streaks/badges awarded, roadmap re-renders.
