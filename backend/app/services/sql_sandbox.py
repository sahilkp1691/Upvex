"""SQL sandbox datasets and server-side verification (SQLite).

Client-side sql.js provides instant Run feedback; submit-quiz re-verifies
answers here so scores cannot be trivially spoofed.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from typing import Any

SQL_DATASETS: dict[str, dict[str, Any]] = {
    "employees": {
        "label": "HR & Sales",
        "description": "Classic employee / department / sales schema for joins and aggregations.",
        "tables": {
            "departments": {
                "columns": [
                    {"name": "dept_id", "type": "INTEGER", "pk": True},
                    {"name": "name", "type": "TEXT"},
                ],
                "rows": [
                    [1, "Engineering"],
                    [2, "Sales"],
                    [3, "Marketing"],
                    [4, "HR"],
                ],
            },
            "employees": {
                "columns": [
                    {"name": "emp_id", "type": "INTEGER", "pk": True},
                    {"name": "name", "type": "TEXT"},
                    {"name": "dept_id", "type": "INTEGER"},
                    {"name": "salary", "type": "REAL"},
                    {"name": "manager_id", "type": "INTEGER"},
                ],
                "rows": [
                    [1, "Alice Chen", 1, 120000, None],
                    [2, "Bob Martinez", 1, 95000, 1],
                    [3, "Carol White", 2, 88000, None],
                    [4, "David Kim", 2, 76000, 3],
                    [5, "Eva Patel", 3, 82000, None],
                    [6, "Frank Lopez", 1, 71000, 1],
                    [7, "Grace Nguyen", 4, 69000, None],
                    [8, "Henry Brown", 2, 54000, 3],
                ],
            },
            "regions": {
                "columns": [
                    {"name": "region_id", "type": "INTEGER", "pk": True},
                    {"name": "emp_id", "type": "INTEGER"},
                    {"name": "region_name", "type": "TEXT"},
                ],
                "rows": [
                    [1, 3, "West"],
                    [2, 3, "East"],
                    [3, 4, "West"],
                    [4, 8, "East"],
                ],
            },
            "sales": {
                "columns": [
                    {"name": "sale_id", "type": "INTEGER", "pk": True},
                    {"name": "emp_id", "type": "INTEGER"},
                    {"name": "amount", "type": "REAL"},
                    {"name": "sale_date", "type": "TEXT"},
                    {"name": "region", "type": "TEXT"},
                ],
                "rows": [
                    [1, 3, 42000, "2025-01-15", "West"],
                    [2, 4, 18500, "2025-01-22", "West"],
                    [3, 8, 9200, "2025-02-03", "East"],
                    [4, 3, 31000, "2025-02-18", "East"],
                    [5, 4, 22100, "2025-03-01", "West"],
                    [6, 8, 14800, "2025-03-12", "East"],
                ],
            },
        },
    },
    "orders": {
        "label": "E-commerce",
        "description": "Customers, products, and order lines for filtering and GROUP BY practice.",
        "tables": {
            "customers": {
                "columns": [
                    {"name": "customer_id", "type": "INTEGER", "pk": True},
                    {"name": "name", "type": "TEXT"},
                    {"name": "city", "type": "TEXT"},
                    {"name": "country", "type": "TEXT"},
                ],
                "rows": [
                    [1, "Acme Corp", "London", "UK"],
                    [2, "Globex", "Paris", "FR"],
                    [3, "Initech", "Berlin", "DE"],
                    [4, "Umbrella Co", "Madrid", "ES"],
                ],
            },
            "products": {
                "columns": [
                    {"name": "product_id", "type": "INTEGER", "pk": True},
                    {"name": "name", "type": "TEXT"},
                    {"name": "category", "type": "TEXT"},
                    {"name": "unit_price", "type": "REAL"},
                ],
                "rows": [
                    [1, "Widget A", "Hardware", 29.99],
                    [2, "Widget B", "Hardware", 49.99],
                    [3, "Cloud Plan", "SaaS", 99.0],
                    [4, "Support Pack", "Services", 199.0],
                ],
            },
            "order_lines": {
                "columns": [
                    {"name": "line_id", "type": "INTEGER", "pk": True},
                    {"name": "order_id", "type": "INTEGER"},
                    {"name": "customer_id", "type": "INTEGER"},
                    {"name": "product_id", "type": "INTEGER"},
                    {"name": "quantity", "type": "INTEGER"},
                    {"name": "order_date", "type": "TEXT"},
                ],
                "rows": [
                    [1, 1001, 1, 1, 10, "2025-01-05"],
                    [2, 1001, 1, 3, 1, "2025-01-05"],
                    [3, 1002, 2, 2, 5, "2025-01-12"],
                    [4, 1003, 3, 1, 20, "2025-02-01"],
                    [5, 1004, 1, 4, 2, "2025-02-14"],
                    [6, 1005, 4, 3, 3, "2025-03-02"],
                ],
            },
        },
    },
}


def dataset_for_client(name: str) -> dict | None:
    """Schema + sample rows for the UI — no solution data."""
    ds = SQL_DATASETS.get(name)
    if not ds:
        return None
    tables = {}
    for tname, tdef in ds["tables"].items():
        cols = tdef["columns"]
        rows = tdef["rows"][:5]
        tables[tname] = {
            "columns": cols,
            "sample_rows": rows,
            "row_count": len(tdef["rows"]),
        }
    return {"name": name, "label": ds["label"], "description": ds["description"], "tables": tables}


def _create_connection(dataset_name: str) -> sqlite3.Connection:
    ds = SQL_DATASETS.get(dataset_name)
    if not ds:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    conn = sqlite3.connect(":memory:")
    for tname, tdef in ds["tables"].items():
        col_defs = ", ".join(
            f"{c['name']} {c['type']}" + (" PRIMARY KEY" if c.get("pk") else "")
            for c in tdef["columns"]
        )
        conn.execute(f"CREATE TABLE {tname} ({col_defs})")
        if tdef["rows"]:
            placeholders = ", ".join("?" * len(tdef["columns"]))
            conn.executemany(
                f"INSERT INTO {tname} VALUES ({placeholders})",
                tdef["rows"],
            )
    conn.commit()
    return conn


def _normalize_cell(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value).strip()


def _result_to_rows(cursor: sqlite3.Cursor) -> tuple[list[str], list[list[str]]]:
    columns = [d[0] for d in (cursor.description or [])]
    raw = cursor.fetchall()
    rows = [[_normalize_cell(v) for v in row] for row in raw]
    return columns, rows


def execute_query(dataset_name: str, sql: str) -> dict:
    """Run a single SELECT (or WITH…SELECT) statement; reject mutations."""
    cleaned = sql.strip().rstrip(";")
    if not cleaned:
        raise ValueError("Query is empty")
    upper = re.sub(r"\s+", " ", cleaned.upper())
    forbidden = ("INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ", "CREATE ", "ATTACH ", "PRAGMA ")
    if any(tok in upper for tok in forbidden):
        raise ValueError("Only read-only SELECT queries are allowed in the sandbox")
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise ValueError("Query must start with SELECT or WITH")

    conn = _create_connection(dataset_name)
    try:
        cur = conn.execute(cleaned)
        columns, rows = _result_to_rows(cur)
        return {"columns": columns, "rows": rows, "row_count": len(rows)}
    except sqlite3.Error as exc:
        raise ValueError(str(exc)) from exc
    finally:
        conn.close()


def _normalize_columns(columns: list[str]) -> list[str]:
    return [c.strip().lower() for c in columns]


def _rows_signature(columns: list[str], rows: list[list[str]], order_sensitive: bool) -> str:
    norm_cols = _normalize_columns(columns)
    if order_sensitive:
        payload = {"columns": norm_cols, "rows": rows}
    else:
        sorted_rows = sorted(rows)
        payload = {"columns": sorted(norm_cols), "rows": sorted_rows}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def compare_results(
    expected: dict,
    actual: dict,
    *,
    order_sensitive: bool = False,
) -> dict:
    """Compare two query results; return pass/fail and human-readable diff hints."""
    exp_cols = _normalize_columns(expected.get("columns") or [])
    act_cols = _normalize_columns(actual.get("columns") or [])
    exp_rows = expected.get("rows") or []
    act_rows = actual.get("rows") or []

    col_match = exp_cols == act_cols or (not order_sensitive and sorted(exp_cols) == sorted(act_cols))
    exp_sig = _rows_signature(expected.get("columns") or [], exp_rows, order_sensitive)
    act_sig = _rows_signature(actual.get("columns") or [], act_rows, order_sensitive)
    data_match = exp_sig == act_sig

    issues: list[str] = []
    if not col_match:
        issues.append(f"Expected columns {exp_cols}, got {act_cols}")
    elif len(exp_rows) != len(act_rows):
        issues.append(f"Expected {len(exp_rows)} row(s), got {len(act_rows)}")
    elif not data_match:
        issues.append("Row values do not match the expected result")
        if not order_sensitive:
            issues.append("Tip: ORDER BY may be required, or row order differs")

    return {
        "passed": col_match and data_match,
        "column_match": col_match,
        "row_count_match": len(exp_rows) == len(act_rows),
        "expected_row_count": len(exp_rows),
        "actual_row_count": len(act_rows),
        "issues": issues,
    }


def verify_sandbox_answer(
    dataset_name: str,
    user_sql: str,
    solution_sql: str,
    *,
    order_sensitive: bool = False,
) -> dict:
    """Execute user + solution queries and compare."""
    try:
        expected = execute_query(dataset_name, solution_sql)
    except ValueError as exc:
        return {"passed": False, "error": f"Invalid solution SQL: {exc}", "issues": [str(exc)]}

    try:
        actual = execute_query(dataset_name, user_sql)
    except ValueError as exc:
        return {
            "passed": False,
            "error": str(exc),
            "issues": [str(exc)],
            "expected_row_count": expected["row_count"],
        }

    comparison = compare_results(expected, actual, order_sensitive=order_sensitive)
    comparison["expected_columns"] = expected["columns"]
    comparison["actual_columns"] = actual["columns"]
    comparison["expected"] = expected
    comparison["actual"] = actual
    return comparison
