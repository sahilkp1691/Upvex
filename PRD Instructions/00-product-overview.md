# Product Overview — AI EdTech Platform (v1)

## Vision
An AI-driven, gamified learning platform for tech skills. Unlike static course platforms,
the system builds a profile of each learner, diagnoses their actual current level per topic,
and generates personalized lesson content live — rather than serving a fixed pre-built course
to everyone. Learning is structured like a roadmap (so users always know what exists and where
they are) but the content itself adapts to the individual.

Think: Duolingo's gamification + engagement loop, applied to tech skills, with AI generating
and personalizing the actual curriculum content instead of a fixed content library.

## Core Loop
1. User signs up, completes a moderate onboarding (persistent profile).
2. User selects a Category (e.g. Data Engineering) and a Topic within it (e.g. Apache Spark).
3. User takes an adaptive diagnostic quiz for that topic.
4. A Diagnostic Evaluator agent scores their level (0–100) and maps sub-skill gaps.
5. User sees a personalized roadmap over the topic's knowledge graph — concept nodes marked as
   tested-out, recommended-next, available, or locked, with root gap concepts (foundational
   weaknesses identified via prerequisite graph traversal) surfaced first.
6. User opens a concept node → system serves cached content if available for their
   profile-signature,
   or generates it live (lesson + quiz) via an AI pipeline, then caches it.
7. User completes lessons and quizzes → XP, streaks, leaderboard, badges. Quiz results feed back
   into their level/gap map, updating their roadmap.

## v1 Scope (in)
- Web app only (SvelteKit frontend, FastAPI backend).
- One Category: Data Engineering. Topics within it: e.g. Apache Spark, SQL, Airflow, Data
  Modeling (final topic list TBD, admin-extensible).
- Persistent user profile via moderate onboarding (5–10 questions).
- Per-topic adaptive diagnostic quiz.
- One AI agent: Diagnostic Evaluator (deterministic scoring + LLM-assisted judgment for
  free-text/partial-credit grading).
- Live AI-generated lesson content (text/conceptual) + adaptive quizzes, cached and reused by
  profile-signature.
- Admin-defined knowledge graph per topic: `ConceptNode`s (title, objective, difficulty, Bloom
  level, no content) connected by `ConceptEdge` prerequisite relationships.
- Admin-defined, versioned GenerationContract (persona, structural template, constraints) that
  governs all content generation.
- Gamification: XP, streaks, scoped leaderboards (friends/cohort), milestone badges, user-chosen
  pacing options tied to deadlines.
- Admin surface: manage categories/topics/knowledge graphs (concept nodes + prerequisite edges),
  manage GenerationContract,
  read-only/basic content review queue, basic analytics (completion, drop-off, common gaps).
- Auth via Supabase Auth.
- Free for all users in v1 (no billing/tiers).

## v1 Scope (out — explicitly deferred)
- Mobile app.
- Runnable/checked code exercises (Spark etc. will use read/analyze code snippets, not
  execution/sandboxing).
- Profile Advisor agent and Sequencing Agent (only Diagnostic Evaluator ships in v1).
- Admin "chat to refine" content editing (groundwork only — content review queue exists, chat
  interface does not).
- Monetization/billing.
- Categories/topics beyond Data Engineering (architecture supports it, content does not yet
  exist).

## Key Product Principles
- **Curated graph, generated flesh.** Admins control the map — the concept nodes and their
  prerequisite relationships (what exists, what depends on what); AI controls the content
  within each node.
- **Consistency over novelty for evaluation.** Anything that decides "where is this user at"
  must be structured, auditable, and versioned — not freeform AI judgment.
- **Cache by design, not as an afterthought.** Generation is expensive; reuse across similar
  learners is a first-class system behavior, not an optimization bolted on later.
- **Admin is a small team of one (for now).** Every admin-facing feature should assume a single
  non-technical-content-but-technical-product person operating it, not a content team.
