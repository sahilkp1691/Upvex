"""Suggested subtopics and concept nodes for admin graph authoring.

Sources (in order):
1. Curated catalog templates matched by topic name (Spark, SQL, Airflow, …)
2. Optional OpenRouter generation when ``use_ai`` and an API key are configured
3. Generic data-engineering scaffold as a last resort

Suggestions are filtered against nodes already on the topic graph (title match,
case-insensitive) so the admin only sees what's still missing.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..generation import openrouter
from ..models import ConceptNode, Topic

logger = logging.getLogger("upvex.graph_suggestions")

# Catalog entries: stable suggestion keys (not DB ids) so apply can be idempotent
# by title. Edges use title references so they resolve after nodes are created.

CATALOG: dict[str, dict[str, Any]] = {
    "apache spark": {
        "match": ("spark", "apache spark"),
        "subtopics": [
            {
                "id": "spark_foundations",
                "name": "Foundations",
                "description": "Why distributed compute exists and how Spark is shaped.",
                "nodes": [
                    ("Big Data Fundamentals", "Explain why single-machine processing breaks down at scale and what problems distributed compute frameworks solve.", "beginner", "understand", 8, True),
                    ("Distributed Storage Fundamentals", "Describe how distributed file systems and object stores (HDFS, S3) split and replicate data, and why data locality matters.", "beginner", "understand", 10, True),
                    ("Spark Architecture", "Identify the roles of the driver, executors, and cluster manager, and trace how a Spark application is scheduled and run.", "beginner", "understand", 12, False),
                ],
            },
            {
                "id": "spark_core_apis",
                "name": "Core APIs",
                "description": "RDDs, laziness, and the DataFrame / SQL surface.",
                "nodes": [
                    ("RDDs and Lazy Evaluation", "Explain what an RDD is, how lineage enables fault tolerance, and why Spark evaluates lazily.", "beginner", "understand", 10, False),
                    ("Transformations vs Actions", "Distinguish transformations from actions and predict when a Spark job actually executes.", "beginner", "apply", 8, False),
                    ("DataFrames and the SQL API", "Use the DataFrame API and Spark SQL to express typical transformations, and explain how Catalyst optimizes them.", "intermediate", "apply", 12, False),
                ],
            },
            {
                "id": "spark_execution",
                "name": "Execution & Performance",
                "description": "Partitions, shuffles, joins, memory, and tuning.",
                "nodes": [
                    ("Spark Partitioning", "Explain how data is partitioned across executors, choose sensible partition counts, and repartition vs coalesce correctly.", "intermediate", "apply", 12, False),
                    ("Shuffles and Wide Dependencies", "Identify which operations trigger shuffles, why shuffles are expensive, and how to minimize them.", "intermediate", "analyse", 12, False),
                    ("Join Strategies", "Compare broadcast, sort-merge, and shuffle-hash joins and choose the right strategy for skewed or large datasets.", "advanced", "analyse", 12, False),
                    ("Caching and Persistence", "Decide when to cache or persist a DataFrame, choose a storage level, and avoid common caching pitfalls.", "intermediate", "apply", 10, False),
                    ("Memory Management", "Describe Spark's unified memory model (execution vs storage) and diagnose out-of-memory failures.", "advanced", "analyse", 12, False),
                    ("Performance Tuning and Optimization", "Read the Spark UI and query plans to find bottlenecks, and apply tuning levers: partitioning, AQE, broadcast hints, skew handling.", "advanced", "analyse", 15, False),
                ],
            },
            {
                "id": "spark_ops",
                "name": "Streaming & Ops",
                "description": "Structured Streaming and cluster sizing.",
                "nodes": [
                    ("Structured Streaming", "Build an incremental pipeline with Structured Streaming, explaining micro-batches, watermarks, and output modes.", "advanced", "apply", 15, False),
                    ("Deployment and Cluster Sizing", "Choose deploy modes and right-size executors (cores, memory, instances) for a given workload.", "advanced", "apply", 12, False),
                ],
            },
        ],
        "edges": [
            ("Big Data Fundamentals", "Spark Architecture", "required"),
            ("Distributed Storage Fundamentals", "Spark Partitioning", "required"),
            ("Spark Architecture", "RDDs and Lazy Evaluation", "required"),
            ("RDDs and Lazy Evaluation", "Transformations vs Actions", "required"),
            ("RDDs and Lazy Evaluation", "DataFrames and the SQL API", "required"),
            ("DataFrames and the SQL API", "Spark Partitioning", "required"),
            ("Transformations vs Actions", "Shuffles and Wide Dependencies", "required"),
            ("Spark Partitioning", "Shuffles and Wide Dependencies", "required"),
            ("Shuffles and Wide Dependencies", "Join Strategies", "required"),
            ("DataFrames and the SQL API", "Caching and Persistence", "required"),
            ("Spark Partitioning", "Caching and Persistence", "recommended"),
            ("Spark Architecture", "Memory Management", "required"),
            ("Caching and Persistence", "Memory Management", "recommended"),
            ("Shuffles and Wide Dependencies", "Performance Tuning and Optimization", "required"),
            ("Memory Management", "Performance Tuning and Optimization", "required"),
            ("Join Strategies", "Performance Tuning and Optimization", "recommended"),
            ("DataFrames and the SQL API", "Structured Streaming", "required"),
            ("Spark Partitioning", "Structured Streaming", "recommended"),
            ("Spark Architecture", "Deployment and Cluster Sizing", "required"),
            ("Performance Tuning and Optimization", "Deployment and Cluster Sizing", "recommended"),
        ],
    },
    "sql": {
        "match": ("sql", "structured query"),
        "subtopics": [
            {
                "id": "sql_basics",
                "name": "Query Basics",
                "description": "Relational model through filters and aggregates.",
                "nodes": [
                    ("The Relational Model", "Explain tables, rows, keys, and relationships, and why relational databases enforce schemas.", "beginner", "understand", 8, True),
                    ("SELECT Fundamentals", "Write SELECT queries with projections, aliases, ordering, and LIMIT.", "beginner", "apply", 8, False),
                    ("Filtering and Predicates", "Filter rows with WHERE using comparison, logical, range, set, and pattern predicates, handling NULL correctly.", "beginner", "apply", 8, False),
                    ("Aggregations and GROUP BY", "Summarize data with aggregate functions and GROUP BY, and filter groups with HAVING.", "beginner", "apply", 10, False),
                ],
            },
            {
                "id": "sql_composition",
                "name": "Composition",
                "description": "Joins, subqueries, CTEs, and windows.",
                "nodes": [
                    ("Joins", "Combine tables with INNER, LEFT, RIGHT, and FULL joins and predict row counts for each.", "intermediate", "apply", 12, False),
                    ("Subqueries and CTEs", "Structure multi-step logic with subqueries and common table expressions, including correlated subqueries.", "intermediate", "apply", 12, False),
                    ("Window Functions", "Use OVER with PARTITION BY and ORDER BY for rankings, running totals, and offsets without collapsing rows.", "intermediate", "apply", 12, False),
                ],
            },
            {
                "id": "sql_modeling_perf",
                "name": "Modeling & Performance",
                "description": "Schema design, indexes, transactions, plans.",
                "nodes": [
                    ("Normalization and Data Modeling", "Apply normal forms to reduce redundancy and decide when denormalization is justified for analytics.", "intermediate", "analyse", 12, False),
                    ("Indexes and Query Performance", "Explain how B-tree indexes speed up lookups, when indexes help or hurt, and how to spot missing-index symptoms.", "intermediate", "analyse", 10, False),
                    ("Transactions and Isolation", "Describe ACID properties and isolation levels, and reason about anomalies like dirty and phantom reads.", "intermediate", "understand", 10, False),
                    ("Query Optimization and Execution Plans", "Read execution plans (EXPLAIN) to identify scans, join order, and misestimates, and rewrite queries for performance.", "advanced", "analyse", 15, False),
                    ("Advanced Analytical Patterns", "Solve gaps-and-islands, sessionization, and pivot problems by combining window functions and CTEs.", "advanced", "analyse", 15, False),
                ],
            },
        ],
        "edges": [
            ("The Relational Model", "SELECT Fundamentals", "required"),
            ("SELECT Fundamentals", "Filtering and Predicates", "required"),
            ("Filtering and Predicates", "Aggregations and GROUP BY", "required"),
            ("Filtering and Predicates", "Joins", "required"),
            ("Joins", "Subqueries and CTEs", "required"),
            ("Aggregations and GROUP BY", "Subqueries and CTEs", "required"),
            ("Aggregations and GROUP BY", "Window Functions", "required"),
            ("Subqueries and CTEs", "Window Functions", "recommended"),
            ("The Relational Model", "Normalization and Data Modeling", "required"),
            ("Joins", "Normalization and Data Modeling", "required"),
            ("Joins", "Indexes and Query Performance", "required"),
            ("The Relational Model", "Transactions and Isolation", "required"),
            ("Indexes and Query Performance", "Query Optimization and Execution Plans", "required"),
            ("Subqueries and CTEs", "Query Optimization and Execution Plans", "required"),
            ("Window Functions", "Advanced Analytical Patterns", "required"),
            ("Subqueries and CTEs", "Advanced Analytical Patterns", "recommended"),
        ],
    },
    "airflow": {
        "match": ("airflow", "apache airflow", "orchestration"),
        "subtopics": [
            {
                "id": "af_core",
                "name": "Core Concepts",
                "description": "DAGs, operators, and the scheduler.",
                "nodes": [
                    ("Workflow Orchestration Basics", "Explain why data pipelines need orchestration and what problems schedulers solve.", "beginner", "understand", 8, True),
                    ("DAGs and Tasks", "Model a pipeline as a DAG of tasks with clear dependencies and idempotent units of work.", "beginner", "understand", 10, False),
                    ("Operators and Sensors", "Choose operators and sensors for common jobs and wait-for-condition patterns.", "beginner", "apply", 10, False),
                    ("Scheduling and Catchup", "Configure schedules, start dates, catchup, and backfills without accidental re-runs.", "intermediate", "apply", 12, False),
                ],
            },
            {
                "id": "af_ops",
                "name": "Reliability & Ops",
                "description": "Retries, XComs, pools, and deployment.",
                "nodes": [
                    ("Retries, Timeouts, and SLAs", "Configure failure handling so flaky tasks recover without hiding real bugs.", "intermediate", "apply", 10, False),
                    ("XComs and Task Communication", "Pass small metadata between tasks safely and know when not to use XComs.", "intermediate", "apply", 10, False),
                    ("Pools, Queues, and Parallelism", "Control concurrency with pools and queues to protect shared systems.", "intermediate", "analyse", 12, False),
                    ("Airflow Deployment Patterns", "Compare executor types and outline a production-ready Airflow layout.", "advanced", "analyse", 15, False),
                ],
            },
        ],
        "edges": [
            ("Workflow Orchestration Basics", "DAGs and Tasks", "required"),
            ("DAGs and Tasks", "Operators and Sensors", "required"),
            ("DAGs and Tasks", "Scheduling and Catchup", "required"),
            ("Operators and Sensors", "Retries, Timeouts, and SLAs", "required"),
            ("DAGs and Tasks", "XComs and Task Communication", "required"),
            ("Scheduling and Catchup", "Pools, Queues, and Parallelism", "recommended"),
            ("Retries, Timeouts, and SLAs", "Airflow Deployment Patterns", "recommended"),
            ("Pools, Queues, and Parallelism", "Airflow Deployment Patterns", "required"),
        ],
    },
    "data modeling": {
        "match": ("data modeling", "dimensional modeling", "data model"),
        "subtopics": [
            {
                "id": "dm_foundations",
                "name": "Foundations",
                "description": "Entities, grains, and warehouse shapes.",
                "nodes": [
                    ("Entities and Relationships", "Identify entities, attributes, and cardinality for an analytical domain.", "beginner", "understand", 10, True),
                    ("Grain and Facts", "Define fact table grain and choose additive vs semi-additive measures.", "beginner", "understand", 10, False),
                    ("Dimensions and Slow Changes", "Design dimensions and choose SCD strategies for changing attributes.", "intermediate", "apply", 12, False),
                    ("Star vs Snowflake Schemas", "Compare star and snowflake layouts and pick one for a given workload.", "intermediate", "analyse", 10, False),
                    ("Data Vault Basics", "Explain hubs, links, and satellites and when Data Vault fits.", "advanced", "understand", 12, False),
                ],
            },
        ],
        "edges": [
            ("Entities and Relationships", "Grain and Facts", "required"),
            ("Grain and Facts", "Dimensions and Slow Changes", "required"),
            ("Dimensions and Slow Changes", "Star vs Snowflake Schemas", "required"),
            ("Entities and Relationships", "Data Vault Basics", "recommended"),
        ],
    },
}

GENERIC_SCAFFOLD = {
    "subtopics": [
        {
            "id": "generic_foundations",
            "name": "Foundations",
            "description": "Core vocabulary and mental models for this topic.",
            "nodes": [
                ("Core Concepts", "Define the essential vocabulary and mental model for this topic.", "beginner", "understand", 10, True),
                ("Key Building Blocks", "Identify the primary components or constructs and how they relate.", "beginner", "understand", 10, False),
                ("First Practical Workflow", "Complete a minimal end-to-end workflow using the basics.", "beginner", "apply", 12, False),
            ],
        },
        {
            "id": "generic_intermediate",
            "name": "Intermediate Practice",
            "description": "Patterns used in real work.",
            "nodes": [
                ("Common Patterns", "Apply the patterns practitioners use most often in this topic.", "intermediate", "apply", 12, False),
                ("Debugging and Failure Modes", "Diagnose typical failures and explain their root causes.", "intermediate", "analyse", 12, False),
            ],
        },
        {
            "id": "generic_advanced",
            "name": "Advanced",
            "description": "Performance, design trade-offs, and production concerns.",
            "nodes": [
                ("Performance and Scale", "Tune for performance and reason about scaling limits.", "advanced", "analyse", 15, False),
                ("Production Readiness", "Design for reliability, observability, and operability in production.", "advanced", "analyse", 15, False),
            ],
        },
    ],
    "edges": [
        ("Core Concepts", "Key Building Blocks", "required"),
        ("Key Building Blocks", "First Practical Workflow", "required"),
        ("First Practical Workflow", "Common Patterns", "required"),
        ("Common Patterns", "Debugging and Failure Modes", "required"),
        ("Debugging and Failure Modes", "Performance and Scale", "required"),
        ("Performance and Scale", "Production Readiness", "recommended"),
    ],
}


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:48] or "concept"


def _node_dict(tuple_or_dict: Any) -> dict:
    if isinstance(tuple_or_dict, dict):
        return {
            "title": tuple_or_dict["title"],
            "learning_objective": tuple_or_dict.get("learning_objective")
            or tuple_or_dict.get("objective", ""),
            "difficulty_tag": tuple_or_dict.get("difficulty_tag", "beginner"),
            "bloom_level": tuple_or_dict.get("bloom_level", "understand"),
            "estimated_duration_mins": int(tuple_or_dict.get("estimated_duration_mins", 10)),
            "is_root": bool(tuple_or_dict.get("is_root", False)),
        }
    title, objective, difficulty, bloom, mins, is_root = tuple_or_dict
    return {
        "title": title,
        "learning_objective": objective,
        "difficulty_tag": difficulty,
        "bloom_level": bloom,
        "estimated_duration_mins": mins,
        "is_root": is_root,
    }


def _normalize_template(raw: dict[str, Any]) -> dict[str, Any]:
    subtopics = []
    for st in raw.get("subtopics", []):
        nodes = [_node_dict(n) for n in st.get("nodes", [])]
        for n in nodes:
            n["suggestion_key"] = _slug(n["title"])
        subtopics.append(
            {
                "id": st.get("id") or _slug(st.get("name", "subtopic")),
                "name": st.get("name", "Subtopic"),
                "description": st.get("description", ""),
                "nodes": nodes,
            }
        )
    edges = []
    for e in raw.get("edges", []):
        if isinstance(e, dict):
            edges.append(
                {
                    "from_title": e.get("from_title") or e.get("from"),
                    "to_title": e.get("to_title") or e.get("to"),
                    "type": e.get("type") or e.get("edge_type") or "required",
                }
            )
        else:
            edges.append({"from_title": e[0], "to_title": e[1], "type": e[2] if len(e) > 2 else "required"})
    return {"subtopics": subtopics, "edges": edges}


def match_catalog(topic_name: str) -> tuple[str | None, dict[str, Any] | None]:
    name = (topic_name or "").strip().lower()
    for key, entry in CATALOG.items():
        for needle in entry["match"]:
            if needle in name or name in needle:
                return key, _normalize_template(entry)
    return None, None


async def _ai_template(topic: Topic) -> dict[str, Any] | None:
    if not openrouter.is_configured():
        return None
    system = (
        "You design learning knowledge graphs for tech skills. "
        "Return JSON with keys: subtopics (array of {id, name, description, nodes}), "
        "edges (array of {from_title, to_title, type}). "
        "Each node: {title, learning_objective, difficulty_tag, bloom_level, "
        "estimated_duration_mins, is_root}. "
        "difficulty_tag in beginner|intermediate|advanced; "
        "bloom_level in remember|understand|apply|analyse; "
        "edge type in required|recommended. "
        "Aim for 3-5 subtopics, 8-16 nodes total, a valid DAG, 1-3 roots."
    )
    user = (
        f"Topic: {topic.name}\nDescription: {topic.description or '(none)'}\n"
        "Propose a prerequisite knowledge graph an admin can edit."
    )
    try:
        from ..config import settings

        data = await openrouter.chat_json(
            settings.model_diagnostic_evaluator,
            system,
            user,
            temperature=0.4,
            max_tokens=4000,
        )
        return _normalize_template(data)
    except Exception as exc:  # noqa: BLE001 — fallback is intentional
        logger.warning("AI graph suggestions failed: %s", exc)
        return None


def _annotate_against_existing(
    template: dict[str, Any],
    existing_by_title: dict[str, str],
) -> dict[str, Any]:
    """Mark nodes already on the graph; drop edges that are fully present."""
    subtopics = []
    missing = 0
    present = 0
    for st in template["subtopics"]:
        nodes = []
        for n in st["nodes"]:
            title_key = n["title"].strip().lower()
            match_id = existing_by_title.get(title_key)
            item = {**n, "already_added": match_id is not None, "match_node_id": match_id}
            nodes.append(item)
            if match_id:
                present += 1
            else:
                missing += 1
        subtopics.append({**st, "nodes": nodes})

    edges = []
    for e in template.get("edges", []):
        ft = (e["from_title"] or "").strip().lower()
        tt = (e["to_title"] or "").strip().lower()
        edges.append(
            {
                **e,
                "from_exists": ft in existing_by_title,
                "to_exists": tt in existing_by_title,
                "both_exist": ft in existing_by_title and tt in existing_by_title,
            }
        )

    return {
        "subtopics": subtopics,
        "edges": edges,
        "stats": {"missing_nodes": missing, "present_nodes": present},
    }


async def build_suggestions(
    db: AsyncSession,
    topic: Topic,
    *,
    use_ai: bool = False,
) -> dict[str, Any]:
    existing = (
        await db.execute(select(ConceptNode).where(ConceptNode.topic_id == topic.id))
    ).scalars().all()
    existing_by_title = {n.title.strip().lower(): n.id for n in existing}

    catalog_key, template = match_catalog(topic.name)
    source = "catalog"
    if template is None and use_ai:
        template = await _ai_template(topic)
        source = "ai" if template else "generic"
    if template is None:
        # Personalized generic scaffold titles with topic name where useful
        template = _normalize_template(GENERIC_SCAFFOLD)
        source = "generic"
        # Rewrite first node objective to mention topic
        if template["subtopics"]:
            first = template["subtopics"][0]["nodes"][0]
            first["learning_objective"] = (
                f"Define the essential vocabulary and mental model for {topic.name}."
            )

    annotated = _annotate_against_existing(template, existing_by_title)
    return {
        "topic_id": topic.id,
        "topic_name": topic.name,
        "source": source,
        "catalog_key": catalog_key,
        "ai_available": openrouter.is_configured(),
        **annotated,
    }
