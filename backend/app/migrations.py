"""Hand-rolled idempotent migration + seed runner, invoked on FastAPI startup.

Steps are named and recorded in schema_migrations; each runs at most once.
Table creation itself uses SQLAlchemy metadata (create_all is already idempotent).
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base, async_session_factory, engine
from .models import (
    Badge,
    Category,
    ConceptEdge,
    ConceptNode,
    DiagnosticQuestion,
    GenerationContract,
    SchemaMigration,
    Topic,
)
from .seed import seed_data

logger = logging.getLogger("upvex.migrations")


async def _seed_catalog(session: AsyncSession) -> None:
    session.add(Category(**seed_data.CATEGORY, is_active=True))
    for t in seed_data.TOPICS:
        session.add(Topic(**t, is_active=True))
    await session.flush()
    for node in seed_data.CONCEPT_NODES:
        (nid, topic_id, title, objective, difficulty, bloom, duration, is_root) = node
        session.add(ConceptNode(
            id=nid, topic_id=topic_id, title=title, learning_objective=objective,
            difficulty_tag=difficulty, bloom_level=bloom,
            estimated_duration_mins=duration, is_root=is_root,
        ))
    # flush so edge FKs resolve — without relationships, the unit of work won't
    # order these inserts for us
    await session.flush()
    node_topic = {n[0]: n[1] for n in seed_data.CONCEPT_NODES}
    for from_id, to_id, edge_type in seed_data.CONCEPT_EDGES:
        session.add(ConceptEdge(
            from_concept_id=from_id, to_concept_id=to_id,
            edge_type=edge_type, topic_id=node_topic[to_id],
        ))


async def _seed_questions(session: AsyncSession) -> None:
    for q in seed_data.DIAGNOSTIC_QUESTIONS:
        (topic_id, concept_id, difficulty, qtype, text, options, correct, expected) = q
        session.add(DiagnosticQuestion(
            topic_id=topic_id, concept_node_id=concept_id, difficulty=difficulty,
            type=qtype, question_text=text, options=options,
            correct_option=correct, expected_concepts=expected,
        ))


async def _seed_contract(session: AsyncSession) -> None:
    session.add(GenerationContract(**seed_data.GENERATION_CONTRACT_V1, is_active=True))


async def _seed_badges(session: AsyncSession) -> None:
    for b in seed_data.BADGES:
        session.add(Badge(**b))


MIGRATION_STEPS = [
    ("0001_seed_catalog", _seed_catalog),
    ("0002_seed_diagnostic_questions", _seed_questions),
    ("0003_seed_generation_contract_v1", _seed_contract),
    ("0004_seed_badges", _seed_badges),
]


async def run_migrations() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        applied = set(
            (await session.execute(select(SchemaMigration.name))).scalars().all()
        )
        for name, step in MIGRATION_STEPS:
            if name in applied:
                continue
            logger.info("Applying migration step: %s", name)
            await step(session)
            session.add(SchemaMigration(name=name))
            await session.commit()
