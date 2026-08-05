"""Prompt assembly for content generation: GenerationContract + concept objective +
per-user variables. The contract is the global lever; user variables personalize."""

import json

from ..models import ConceptNode, GenerationContract
from ..services.sandbox_problems import is_sql_topic
from ..services.sql_sandbox import datasets_prompt_block

LEARNING_STYLE_HINTS = {
    "visual": (
        "Prioritize section 'visual' blocks (bar, line, flow, compare, stack) that the UI renders as "
        "charts and diagrams. Pair each visual with a short caption. Still write clear prose; do not "
        "rely on ASCII art."
    ),
    "reading": "Favor precise prose and well-organized text; depth of written explanation over gimmicks. Still include one visual when a comparison or process is hard to see in words alone.",
    "hands_on": "Anchor every section in concrete code snippets or realistic scenarios the learner can trace through. Add a visual when it clarifies scale, cost, or process flow.",
    "mixed": "Blend prose, examples, and at least one structured visual (chart or diagram) when it builds intuition.",
}


SANDBOX_SCHEMA_RULES = (
    "Every sandbox problem runs against one of the two fixed datasets below, created "
    "exactly as shown before the learner's query executes. These are the only tables and "
    "columns that exist.\n"
    "- Never invent a table, column, or data type that is not listed here.\n"
    "- Never describe a schema inside a question prompt (no 'the table has columns "
    "id, name, ...'). The learner already sees the real schema in the UI; a restated "
    "schema that disagrees with it is worse than none.\n"
    "- Refer to tables and columns by their real names, and only where they exist "
    "(for example department is a row in `departments`, not a column on `employees`, "
    "and there is no hire date anywhere).\n"
    "- If the concept you are teaching cannot be practised with these columns, choose a "
    "problem that can be. Do not bend the schema to fit the lesson.\n"
    "- Every solution_sql must be a single SQLite SELECT (or WITH ... SELECT) that runs "
    "successfully against these tables as written."
)


def sandbox_schema_prompt() -> str:
    return f"SQL SANDBOX SCHEMA:\n{SANDBOX_SCHEMA_RULES}\n\n{datasets_prompt_block()}"


def _build_system(contract: GenerationContract, node: ConceptNode) -> str:
    parts = [
        contract.persona_text,
        f"STRUCTURE:\n{contract.structural_template}",
        f"CONSTRAINTS:\n{contract.constraints_text}",
    ]
    if is_sql_topic(node.topic_id):
        parts.append(sandbox_schema_prompt())
    return "\n\n".join(parts)


def build_lesson_prompt(
    contract: GenerationContract,
    node: ConceptNode,
    user_vars: dict,
) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the lesson generation call."""
    system = _build_system(contract, node)
    style = user_vars.get("learning_style", "mixed")
    payload = {
        "task": "Generate the LESSON only (JSON object matching the LESSON SHAPE).",
        "concept": {
            "title": node.title,
            "learning_objective": node.learning_objective,
            "difficulty_tag": node.difficulty_tag,
            "bloom_level": node.bloom_level,
            "target_duration_mins": node.estimated_duration_mins,
        },
        "learner": {
            "difficulty_band": user_vars.get("difficulty_band", "untested"),
            "learning_style": style,
            "style_guidance": LEARNING_STYLE_HINTS.get(style, LEARNING_STYLE_HINTS["mixed"]),
            "tone_preference": user_vars.get("tone_preference", "neutral"),
            "root_gap_context": user_vars.get("root_gap_context") or
                "No specific foundational gap identified — teach the concept on its own terms.",
        },
    }
    return system, json.dumps(payload, indent=2)


def build_quiz_prompt(
    contract: GenerationContract,
    node: ConceptNode,
    user_vars: dict,
    lesson_body: dict,
) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the quiz generation call."""
    system = _build_system(contract, node)
    lesson_summary = {
        "title": lesson_body.get("title"),
        "section_headings": [s.get("heading") for s in lesson_body.get("sections", [])],
        "key_takeaways": lesson_body.get("key_takeaways", []),
    }
    payload = {
        "task": "Generate the QUIZ only (JSON object matching the QUIZ SHAPE) testing the lesson below.",
        "concept": {
            "title": node.title,
            "learning_objective": node.learning_objective,
            "difficulty_tag": node.difficulty_tag,
            "bloom_level": node.bloom_level,
        },
        "learner_difficulty_band": user_vars.get("difficulty_band", "untested"),
        "lesson_taught": lesson_summary,
    }
    return system, json.dumps(payload, indent=2)


def build_root_gap_context(root_gap_title: str | None) -> str | None:
    if not root_gap_title:
        return None
    return (
        f"This learner has an identified foundational gap in '{root_gap_title}'. Where this concept "
        f"touches that foundation, briefly reinforce it rather than assuming it."
    )
