"""Generated sandbox problems must match the fixed sandbox schema.

Guards the failure mode where the model invents a plausible table (e.g. an
`employees.department` column) and the learner gets an unanswerable challenge.
"""

from app.generation.prompts import sandbox_schema_prompt
from app.services.sandbox_problems import (
    SQL_SANDBOX_PROBLEMS,
    SQL_SURPRISE_VARIANTS,
    fallback_problem,
)
from app.services.sql_sandbox import solution_sql_error
from app.tasks.generate import _sanitize_interactive, _validate_quiz

INVENTED_SCHEMA_SQL = (
    "SELECT * FROM employees WHERE department = 'Engineering' "
    "AND hire_date > '2020-01-01' ORDER BY hire_date DESC"
)


def test_curated_problems_all_run():
    for cid, p in SQL_SANDBOX_PROBLEMS.items():
        assert solution_sql_error(p["dataset"], p["solution_sql"]) is None, cid


def test_surprise_variants_all_run():
    for i, v in enumerate(SQL_SURPRISE_VARIANTS):
        assert solution_sql_error(v["dataset"], v["solution_sql"]) is None, i


def test_solution_sql_error_flags_invented_column():
    err = solution_sql_error("employees", INVENTED_SCHEMA_SQL)
    assert err is not None
    assert "department" in err


def test_solution_sql_error_flags_unknown_dataset():
    assert solution_sql_error("payroll", "SELECT 1") is not None


def test_mini_sandbox_with_invented_schema_is_replaced():
    cleaned = _sanitize_interactive({
        "type": "mini_sandbox",
        "prompt": "The employees table has columns id, name, department, hire_date, salary...",
        "dataset": "employees",
        "starter_sql": "SELECT ",
        "solution_sql": INVENTED_SCHEMA_SQL,
        "hints": ["Use WHERE"],
    })
    assert cleaned["prompt"] != "The employees table has columns id, name, department, hire_date, salary..."
    assert solution_sql_error(cleaned["dataset"], cleaned["solution_sql"]) is None


def test_mini_sandbox_with_valid_schema_is_kept():
    cleaned = _sanitize_interactive({
        "type": "mini_sandbox",
        "prompt": "Return each employee's name and salary.",
        "dataset": "employees",
        "starter_sql": "SELECT ",
        "solution_sql": "SELECT name, salary FROM employees",
        "hints": ["Two columns is all you need."],
    })
    assert cleaned["prompt"] == "Return each employee's name and salary."
    assert cleaned["solution_sql"] == "SELECT name, salary FROM employees"


def test_quiz_sandbox_question_with_invented_schema_is_replaced():
    quiz = {
        "mode": "mixed",
        "questions": [
            {
                "type": "sandbox_sql",
                "question_text": "Find Engineering employees hired after 2020-01-01.",
                "dataset": "employees",
                "starter_sql": "SELECT ",
                "solution_sql": INVENTED_SCHEMA_SQL,
                "hints": [],
            },
            {"type": "multiple_choice", "question_text": "?", "options": ["a", "b"], "correct_option": 0},
            {"type": "multiple_choice", "question_text": "?", "options": ["a", "b"], "correct_option": 1},
        ],
    }
    _validate_quiz(quiz)
    q = quiz["questions"][0]
    assert solution_sql_error(q["dataset"], q["solution_sql"]) is None
    assert "hire" not in q["question_text"].lower()


def test_fallback_problem_respects_dataset():
    assert fallback_problem("sql_joins", "orders")["dataset"] == "orders"
    assert fallback_problem(None, None)["dataset"] == "employees"


def test_schema_prompt_lists_real_columns_only():
    prompt = sandbox_schema_prompt()
    assert "CREATE TABLE employees" in prompt
    assert "manager_id INTEGER" in prompt
    assert "hire_date" not in prompt
