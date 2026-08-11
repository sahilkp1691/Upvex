"""Diagnostic bank readiness, validation, stub drafts, and start-goal gating."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Category, ConceptNode, DiagnosticQuestion, Topic, User, UserGoal
from app.services import diagnostic_bank as bank

pytestmark = pytest.mark.anyio


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(Category(id="c1", name="Cat", description=""))
        session.add(Topic(id="t1", category_id="c1", name="SQL", description="SQL topic", is_active=True))
        for i, title in enumerate(["A", "B", "C", "D"]):
            session.add(
                ConceptNode(
                    id=f"n{i}",
                    topic_id="t1",
                    title=title,
                    learning_objective=f"Learn {title}",
                    difficulty_tag="beginner",
                    bloom_level="understand",
                    is_root=i == 0,
                )
            )
        session.add(
            User(
                id="u1",
                email="learner@example.com",
                auth_provider_id="dev-u1",
                display_name="Learner",
                is_admin=False,
            )
        )
        await session.commit()
        yield session
    await engine.dispose()


async def test_readiness_not_ready_without_questions(db):
    ready = await bank.readiness(db, "t1")
    assert ready["ready"] is False
    assert ready["question_count"] == 0
    assert any("8" in issue for issue in ready["issues"])


async def _seed_bank(db):
    diffs = ["easy", "medium", "hard", "easy", "medium", "hard", "easy", "medium"]
    concepts = ["n0", "n1", "n2", "n0", "n1", "n2", "n3", "n0"]
    for i, (diff, cid) in enumerate(zip(diffs, concepts)):
        db.add(
            DiagnosticQuestion(
                id=f"q{i}",
                topic_id="t1",
                concept_node_id=cid,
                difficulty=diff,
                type="multiple_choice",
                question_text=f"Question number {i} about concept?",
                options=["a", "b", "c", "d"],
                correct_option=0,
            )
        )
    await db.commit()


async def test_readiness_ready_with_bank(db):
    await _seed_bank(db)
    ready = await bank.readiness(db, "t1")
    assert ready["ready"] is True
    assert ready["question_count"] == 8
    assert ready["concepts_covered"] >= 3


def test_validate_mc_and_sa():
    assert (
        bank.validate_question_payload(
            {
                "type": "multiple_choice",
                "difficulty": "easy",
                "question_text": "What is a join?",
                "options": ["A", "B", "C"],
                "correct_option": 1,
            }
        )
        is None
    )
    assert (
        bank.validate_question_payload(
            {
                "type": "short_answer",
                "difficulty": "medium",
                "question_text": "Explain indexing briefly.",
                "expected_concepts": ["index", "lookup"],
            }
        )
        is None
    )
    assert bank.validate_question_payload(
        {
            "type": "multiple_choice",
            "difficulty": "easy",
            "question_text": "Bad",
            "options": ["only-one"],
            "correct_option": 0,
        }
    )


async def test_stub_and_draft_without_api_key(db):
    topic = await db.get(Topic, "t1")
    nodes = (await db.execute(select(ConceptNode).where(ConceptNode.topic_id == "t1"))).scalars().all()
    stubs = bank._stub_drafts(topic, nodes, 2)
    assert len(stubs) == len(nodes) * 2
    assert all(bank.validate_question_payload(d) is None for d in stubs)

    drafts = await bank.draft_questions(db, topic, count_per_concept=1)
    assert len(drafts) >= 4
    assert all("concept_node_id" in d for d in drafts)


async def test_create_goal_blocked_until_bank_ready(db):
    from fastapi import HTTPException
    from app.routes import goals as goals_route
    from app.models import User

    user = await db.get(User, "u1")

    class Payload:
        topic_id = "t1"

    with pytest.raises(HTTPException) as exc:
        await goals_route.create_goal(Payload(), user=user, db=db)
    assert exc.value.status_code == 422

    await _seed_bank(db)
    result = await goals_route.create_goal(Payload(), user=user, db=db)
    assert result["status"] == "diagnostic_pending"
    assert result["topic_id"] == "t1"

    # Idempotent return of existing goal
    again = await goals_route.create_goal(Payload(), user=user, db=db)
    assert again["id"] == result["id"]
