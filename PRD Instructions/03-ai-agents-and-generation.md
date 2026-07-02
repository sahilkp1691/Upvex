# AI Agents & Content Generation — v1

## Two distinct AI concerns — kept separate by design
1. **Generation** (creative, probabilistic) — writing lesson content and quizzes.
2. **Evaluation** (consistent, auditable) — deciding where a user actually is.

These must not be combined into one prompt/call. Evaluation logic needs to be testable,
versionable, and trustworthy; generation needs room for variation. Mixing them produces
inconsistent, untestable scoring.

---

## GenerationContract
A versioned, admin-managed spec that governs ALL content generation calls. Stored in the
`GenerationContract` table; only one version active at a time; content is tagged with the
version it was generated under.

Contains:
- **Persona** — tone, how the AI explains things, encouragement level, analogy use, humor level.
- **Structural template** — fixed lesson shape, e.g.: concept intro → explanation → example →
  check-for-understanding. Quizzes follow their own fixed shape (question type mix, length).
- **Constraints** — stay strictly on the module's stated learning objective; avoid wandering into
  adjacent topics; flag uncertainty rather than asserting unclear technical specifics
  confidently; output must be valid structured JSON matching the defined schema.

This contract is injected into every generation prompt alongside the per-user variables
(profile, gap, module objective). Changing the contract is the primary lever for fixing
drift/consistency issues globally, without touching individual content entries.

## Content Generation Pipeline
1. Triggered on cache miss (see data model: `GeneratedContent` keyed by `ProfileSignature`).
2. Celery task assembles the prompt: GenerationContract (active version) + module objective +
   user's relevant gap/difficulty + learning style + tone preference.
3. Calls OpenRouter, model selected per task type (lesson vs quiz may use different
   models/configs — test for cost/quality tradeoff).
4. Expects structured JSON output (lesson body + quiz body) matching the template schema —
   use tool-calling/structured output mode where the selected model supports it, to reduce
   parsing/consistency issues.
5. Result stored in `GeneratedContent`, tagged with signature + contract version + model used.
6. Served to user; future requests matching the same signature hit cache.

### Caching philosophy
Cache aggressively. The system should converge toward a self-building content library over time
as more users hit existing signatures, with generation cost concentrated in the early/cold-start
period. Signature granularity is lesson-level (one focused concept, ~5–10 min of content) — fine
enough to personalize meaningfully, coarse enough that real reuse happens across similar
learners.

---

## Agent 1 (v1): Diagnostic Evaluator
**Job:** Given quiz/diagnostic response data, output a structured assessment of the user's
current level — including concept-level gap scores AND root-cause gaps traced through the
knowledge graph. Nothing else — no content generation, no recommendations, no personality.

**Input schema (example shape):**
```json
{
  "topic_id": "...",
  "responses": [
    {
      "question_id": "...",
      "concept_node_id": "spark_partitioning",
      "difficulty": "medium",
      "type": "multiple_choice",
      "correct": true
    },
    {
      "question_id": "...",
      "concept_node_id": "spark_optimization",
      "difficulty": "hard",
      "type": "short_answer",
      "answer_text": "...",
      "expected_concepts": ["shuffle", "partition_pruning"]
    }
  ]
}
```

**Output schema (example shape):**
```json
{
  "level_score": 62,
  "confidence": 0.78,
  "concept_scores": {
    "spark_dataframes": 85,
    "spark_partitioning": 35,
    "spark_optimization": 40,
    "distributed_storage": 50
  },
  "root_gap_concepts": ["distributed_storage", "spark_partitioning"],
  "gap_reasoning": "Weak scores on partitioning and optimization both trace back to a foundational gap in distributed storage concepts — addressing this root node first is recommended.",
  "notes": "Strong on core API usage, weak on performance tuning."
}
```

**The graph traversal step — how root gaps are found:**
After scoring each concept, the Evaluator queries the ConceptEdge table using a Postgres
recursive CTE to walk *upstream* (prerequisite direction) from each weak concept node.
Concepts with weak scores that ALSO have a weak-or-untested ancestor are flagged as
`root_gap_concepts` — they are the foundational gaps driving multiple surface weaknesses.
This is a deterministic database query, not an LLM call, and should be fast.

Example: user scores weak on both `spark_partitioning` and `spark_optimization`. Graph
traversal reveals both have `distributed_storage_fundamentals` as a common ancestor with
a weak/untested score. Root gap = `distributed_storage_fundamentals`. The sequencing logic
then surfaces that concept first, before either surface-level module.

**Implementation approach — hybrid, not pure LLM:**
- Deterministic scoring in code for objective items (multiple choice correctness weighted by
  difficulty and bloom_level).
- Graph traversal in Postgres (recursive CTE) for root-cause identification — no LLM needed
  here, it's a pure graph query.
- LLM tool-call only for judgment-requiring parts: grading free-text/short-answer responses
  against expected concepts, assigning partial credit, generating the human-readable
  `gap_reasoning` summary.
- Low temperature, tightly constrained prompt, structured output enforced.

**Used in two places:**
1. Initial diagnostic (sets starting `UserGoal.level_score`, `concept_gap_map`, and
   `root_gap_concepts`).
2. Post-lesson quiz re-scoring (lighter pass — updates concept scores incrementally,
   re-runs graph traversal to check if root gaps have been resolved).

### Evals for this agent
Since consistency matters most here, plan to:
- Build a small fixed set of known quiz-response patterns with expected score ranges.
- Run the Evaluator against these whenever the prompt/model changes; check output stays within
  expected bounds.
- Separately test the graph traversal logic with known concept graphs and expected root-gap
  outputs — this is pure deterministic logic and should be unit-tested like regular code.
- Use OpenRouter to A/B different models for the LLM-assist portion (free-text grading only)
  — this agent does NOT need your most expensive/creative model; it needs your most reliable one.

---

## Future Agents (post-v1 — documented now so architecture isn't boxed in)

### Profile Advisor
Input: persistent UserProfile + active/new UserGoal. Output: recommendations feeding into the
per-user variables of the GenerationContract injection (e.g. suggested pacing given stated time
availability, tone/format leaning, flags like "stated background may not match diagnostic
result"). More advisory/probabilistic than the Evaluator — feeds suggestions, not hard gates.

### Sequencing Agent
Input: Evaluator output (concept_gap_map + root_gap_concepts) + ConceptNode/ConceptEdge graph
for the topic. Output: ordered recommended learning path — which concept nodes to surface as
"do first", "next", "available", "locked" in the roadmap. Traverses the prerequisite graph
downstream from the user's root gap concepts to find the optimal path to the user's goal
concepts. Mostly deterministic graph traversal (Postgres recursive CTE); LLM assist for
ambiguous cases where multiple valid paths exist and user profile context should influence the
choice (e.g. a user with more time available might take a broader path vs. a user optimising
for speed to a specific outcome).

### Admin Chat-to-Refine
Not a backend "agent" in the scoring sense — a UI/workflow feature where an admin selects a
`GeneratedContent` entry, chats with AI to adjust it, and the result becomes the new canonical
version for that signature going forward. Natural extension of the Content Review Queue (which
ships read-only in v1).
