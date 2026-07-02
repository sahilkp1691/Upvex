# Data Model — v1

Postgres, with JSONB columns used for flexible/variable-shape fields (profile answers, generated
content body, gap maps). This is an entity/field outline, not a final DDL — refine during
implementation.

## User
- id (PK)
- email, auth_provider_id (via Supabase Auth)
- created_at

## UserProfile (1:1 with User)
- user_id (FK)
- learning_style (enum: visual / reading / hands_on / mixed)
- time_availability (enum)
- motivation (enum or short text)
- tech_background (text or structured)
- tone_preference (enum: playful / professional / neutral)
- raw_onboarding_answers (JSONB — full record of all answers, for future re-analysis)

## Category
- id (PK)
- name (e.g. "Data Engineering")
- description
- is_active

## Topic
- id (PK)
- category_id (FK)
- name (e.g. "Apache Spark")
- description
- is_active
- created_by_admin_id

## CurriculumSkeleton / Module
The curriculum is modelled as a directed acyclic graph (DAG) of Concept nodes per Topic,
with explicit prerequisite edges between them. This is the knowledge graph layer — it powers
the Diagnostic Evaluator's root-cause tracing and the Sequencing Agent's path reasoning.
Stored in Postgres and queried with recursive CTEs (no separate graph DB needed in v1;
migrate to Neo4j if the concept graph grows beyond a single domain at scale).

### ConceptNode
- id (PK)
- topic_id (FK)
- title (e.g. "Spark Partitioning")
- learning_objective
- difficulty_tag (enum: beginner / intermediate / advanced)
- bloom_level (enum: remember / understand / apply / analyse — for diagnostic depth)
- estimated_duration_mins
- is_root (bool — true if no prerequisites; entry points into the graph)

### ConceptEdge (prerequisite graph edges)
- id (PK)
- from_concept_id (FK → ConceptNode) — the prerequisite concept
- to_concept_id (FK → ConceptNode) — the concept that depends on it
- edge_type (enum: required / recommended — required = hard gate, recommended = soft nudge)
- topic_id (FK — denormalized for fast topic-scoped graph queries)

-- Index on (topic_id, to_concept_id) for fast prerequisite lookups
-- Index on (topic_id, from_concept_id) for fast downstream lookups

NOTE: Postgres recursive CTEs can traverse this graph efficiently at v1 scale.
Example query shape: "give me all ancestor concepts of ConceptNode X within Topic Y" —
used by the Evaluator to find root-cause gaps behind a surface-level weak score.

## UserGoal
- id (PK)
- user_id (FK)
- topic_id (FK)
- status (enum: diagnostic_pending / active / completed / paused)
- level_score (0–100, from Diagnostic Evaluator)
- concept_gap_map (JSONB — per-ConceptNode scores, e.g. {"concept_id": score_0_to_100})
- root_gap_concepts (JSONB — array of ConceptNode IDs identified as root causes via graph
  traversal; these are the foundational gaps driving surface-level weaknesses)
- pacing_choice (enum: casual / regular / intense)
- target_deadline (per concept or overall, TBD during implementation)
- created_at, updated_at

## DiagnosticAttempt
- id (PK)
- user_goal_id (FK)
- responses (JSONB — question, answer, correctness, difficulty, concept_node_id tagged per question)
- evaluator_output (JSONB — overall score, confidence, per-concept scores, root_gap_concepts
  derived from graph traversal)

## GenerationContract
- id (PK)
- version (int, incrementing)
- persona_text
- structural_template
- constraints_text
- is_active (only one active version at a time)
- created_at

## ProfileSignature (conceptual key, may be a computed/hashed field rather than its own table)
- topic_id + concept_node_id + difficulty_level + root_gap_concept_id + learning_style
- Used as the lookup key into GeneratedContent.
- Grounded at concept-node level (not module level) so caching precision matches the graph.

## GeneratedContent
- id (PK)
- signature (the ProfileSignature, indexed)
- topic_id, concept_node_id (FK, denormalized for querying)
- lesson_body (JSONB — structured per the GenerationContract template)
- quiz_body (JSONB — questions tagged with concept_node_id for post-quiz re-scoring)
- generation_contract_version (FK/version ref)
- model_used (string — which OpenRouter model generated this)
- created_at
- (v2: review_status, admin_edited_version)

## LessonCompletion
- id (PK)
- user_id (FK)
- concept_node_id (FK)
- generated_content_id (FK)
- quiz_score
- concept_score_delta (how much this completion moved the concept's score in concept_gap_map)
- completed_at

## XPLedger
- id (PK)
- user_id (FK)
- amount
- reason (enum: lesson_complete / quiz_score / streak_bonus / milestone)
- related_id (FK to LessonCompletion or other source)
- created_at

## Streak
- user_id (FK, 1:1 or 1:per-topic — TBD)
- current_streak
- longest_streak
- last_active_date

## Leaderboard
- Not necessarily its own table in v1 — likely a query over XPLedger grouped by user + time
  window + scope (friends/cohort). Revisit if performance requires materialization.

## Badge / Milestone
- id (PK)
- name, description, criteria (structured — e.g. "sub-skill X reaches 80+")
## UserBadge
- user_id (FK), badge_id (FK), earned_at
