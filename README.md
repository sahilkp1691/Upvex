# Upvex

An AI-driven, gamified learning platform for tech skills — derived from "upward vector".
Upvex diagnoses what a learner actually knows, traces weaknesses to their root cause through
a prerequisite knowledge graph, and generates personalized lesson content live instead of
serving a fixed course.

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | SvelteKit (Svelte 5, plain JS, SPA mode) |
| Backend | FastAPI (async), SQLAlchemy 2 |
| Database | Postgres + JSONB (Supabase Postgres or any Postgres) |
| Tasks | Celery + Redis (content generation, daily streak job) |
| Auth | Supabase Auth (JWT verified backend-side; dev bypass mode for local work) |
| AI | OpenRouter — model configurable per task type |

## Repository layout

```
backend/
  app/
    main.py            FastAPI app, startup migrations
    config.py          pydantic-settings (.env)
    models.py          all entities (User, ConceptNode/Edge, UserGoal, GeneratedContent, ...)
    migrations.py      idempotent migration + seed runner
    auth.py            Supabase JWT verification + dev bypass
    routes/            me, catalog, goals, diagnostic, roadmap, content, gamification, admin
    services/          scoring, graph_traversal (recursive CTEs), sequencing, signature, xp
    agents/evaluator.py  Diagnostic Evaluator (deterministic + LLM assist)
    generation/        OpenRouter client + prompt assembly from GenerationContract
    tasks/             Celery app, generate_content, daily streak evaluation
    seed/              Data Engineering catalog, Spark + SQL graphs, question banks
  tests/               unit tests + e2e_smoke.py
frontend/
  src/routes/          landing, auth, onboarding, topics, diagnostic, roadmap, lesson,
                       leaderboard, profile, admin/*
  src/lib/             api.js, supabase.js, stores.js, shared components
docker-compose.yml     Redis + local Postgres for development
.env.example           all configuration knobs
```

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

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

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
   (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`) and in `frontend/.env`
   (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`). Set `DEV_AUTH_BYPASS=false`.
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
