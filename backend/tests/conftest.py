import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import ConceptEdge, ConceptNode, Topic, Category


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db():
    """Fresh in-memory SQLite session with a known test graph.

    Graph shape (topic t1):
        storage (root) --required--> partitioning --required--> shuffles
        arch (root)    --required--> partitioning
        shuffles --required--> optimization
    """
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(Category(id="c1", name="Cat", description=""))
        session.add(Topic(id="t1", category_id="c1", name="Topic", description=""))
        nodes = [
            ("storage", True), ("arch", True),
            ("partitioning", False), ("shuffles", False), ("optimization", False),
        ]
        for nid, is_root in nodes:
            session.add(ConceptNode(
                id=nid, topic_id="t1", title=nid, learning_objective=nid,
                difficulty_tag="intermediate", bloom_level="understand", is_root=is_root,
            ))
        edges = [
            ("storage", "partitioning"), ("arch", "partitioning"),
            ("partitioning", "shuffles"), ("shuffles", "optimization"),
        ]
        for f, t in edges:
            session.add(ConceptEdge(from_concept_id=f, to_concept_id=t, edge_type="required", topic_id="t1"))
        await session.commit()
        yield session
    await engine.dispose()
