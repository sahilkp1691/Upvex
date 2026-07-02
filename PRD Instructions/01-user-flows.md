# User Flows — v1

## 1. Sign Up / Onboarding
1. User lands on marketing/landing page → clicks Sign Up.
2. Auth via Supabase Auth (email/password and/or OAuth).
3. On first login, user enters onboarding: 5–10 questions covering:
   - Learning style preference (visual / reading / hands-on / mixed)
   - Time availability (e.g. <30min/day, 30-60min/day, 1hr+/day)
   - Motivation / context (career switch, upskilling for current job, curiosity, etc.)
   - Prior tech background (general — not topic-specific level)
   - Tone preference (playful/gamified vs. professional/neutral)
4. Answers saved to persistent User Profile. This profile is NOT topic-specific and is reused
   across all future goals.
5. User is routed to Category/Topic browse screen.

## 2. Goal Setting + Diagnostic
1. User browses Categories (v1: Data Engineering only) and selects a Topic (e.g. Apache Spark).
2. System creates a `UserGoal` record (status: diagnostic_pending).
3. User takes an adaptive diagnostic quiz:
   - Starts at medium difficulty.
   - Branches up/down based on correctness.
   - ~10–15 questions, mix of multiple choice and short answer, each tagged against a specific
     `ConceptNode` in the topic's knowledge graph.
4. On completion, quiz responses are sent to the Diagnostic Evaluator agent.
5. Evaluator returns: overall level score (0–100), per-concept score breakdown (e.g. strong on
   DataFrames, weak on Partitioning), root gap concepts (foundational concepts identified via
   graph traversal as the underlying cause of multiple surface-level weaknesses), and a
   confidence score.
6. Results screen shown to user in plain language ("You're stronger on X than Y, and it looks
   like brushing up on Z would unlock progress on both") — not just a number. This is a key
   trust-building moment, should feel like a real assessment, and surfacing root gaps here is
   part of what makes it feel genuinely diagnostic rather than a generic quiz score.
7. `UserGoal` updated with level score, concept_gap_map, and root_gap_concepts. Status: active.

## 3. Roadmap / Curriculum View
1. System loads the Topic's admin-defined knowledge graph (`ConceptNode`s connected by
   `ConceptEdge` prerequisite relationships).
2. Sequencing logic traverses the graph from the user's root gap concepts and marks each concept
   node as: tested-out (skip), recommended-next (surfaces root gaps first, since resolving them
   unlocks progress on dependent concepts), available (unlocked but not next), or locked
   (required prerequisite concepts not yet met).
3. User sees this as a visual roadmap/graph — can jump into ANY unlocked concept, not forced
   linear. Locked concepts show which prerequisite concept(s) need to be completed first.
4. User selects pacing option (e.g. casual / regular / intense) which sets target deadlines per
   concept — this also feeds the streak/gamification system.

## 4. Lesson Delivery (Content Generation Loop)
1. User opens a concept node.
2. Backend computes a ProfileSignature (topic + concept_node + difficulty + root gap concept +
   learning style).
3. Cache check against `GeneratedContent`:
   - HIT → serve immediately.
   - MISS → enqueue Celery task → frontend shows a branded loading state (not a bare spinner —
     this is a gamification/personality touchpoint, e.g. "Crafting your lesson...") → task calls
     OpenRouter with GenerationContract + user variables → structured JSON response (lesson +
     quiz) → stored in `GeneratedContent` keyed by signature + contract version → served to user.
4. User completes lesson, attempts quiz (quiz questions tagged by concept_node_id).
5. Quiz responses sent to Diagnostic Evaluator again (lighter re-scoring pass) → updates
   `UserGoal.concept_gap_map`, re-runs graph traversal to check whether previously identified
   root gaps have been resolved, and updates concept completion status.
6. Roadmap re-renders with updated state (concept marked complete, downstream concepts may
   unlock, next recommendation may shift if a root gap was just resolved).

## 5. Gamification Loop
1. On lesson/quiz completion: XP awarded (amount may vary by difficulty/performance).
2. Daily Celery job evaluates streak continuation/breakage per user.
3. Leaderboard (friends/cohort scope for v1) ranks by XP within a time window (e.g. weekly).
4. Milestone badges awarded on meaningful checkpoints (e.g. a root gap concept resolved, or a
   cluster of related concept nodes mastered — not arbitrary point totals).

## 6. Admin Flows
### Topic/Knowledge Graph Management
1. Admin creates a Category (v1: pre-seeded with Data Engineering).
2. Admin creates a Topic within a Category.
3. Admin defines the topic's knowledge graph: individual `ConceptNode`s (each with a title,
   learning objective, difficulty tag, and Bloom level) connected by `ConceptEdge` prerequisite
   relationships (required or recommended). (AI may assist by proposing a draft graph structure;
   admin edits/approves — content generation for actual lessons happens later, live, per-user.)

### GenerationContract Management
1. Admin views/edits the current GenerationContract (persona, structural template, constraints).
2. Changes are saved as a new version (old versions retained, content stays tagged with the
   version it was generated under).

### Content Review (v1: read-only / light edit)
1. Admin browses `GeneratedContent` entries (filterable by topic/concept_node/signature).
2. Admin can view what's been served to real users.
3. (v2+) Admin can chat with AI to refine a specific entry, creating a new canonical version for
   that signature.

### Analytics
1. Admin views completion rates, drop-off points per concept node, and common root gap concept
   patterns across users — both for product insight and as future signal for knowledge graph and
   content tuning (e.g. if many users share the same root gap, that concept may need a clearer
   or earlier placement in the graph).
