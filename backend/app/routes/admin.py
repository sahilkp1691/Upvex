"""Admin surface: catalog + knowledge graph management, GenerationContract
versioning, read-only content review queue, and basic analytics."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_admin_user
from ..database import get_db
from ..models import (
    Category,
    ConceptEdge,
    ConceptNode,
    GeneratedContent,
    GenerationContract,
    LessonCompletion,
    Topic,
    User,
    UserGoal,
)

router = APIRouter(dependencies=[Depends(get_admin_user)])


# ---------- Categories / Topics ----------

class CategoryPayload(BaseModel):
    name: str
    description: str = ""
    is_active: bool = True


class TopicPayload(BaseModel):
    category_id: str
    name: str
    description: str = ""
    is_active: bool = True


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    cats = (await db.execute(select(Category))).scalars().all()
    return [{"id": c.id, "name": c.name, "description": c.description, "is_active": c.is_active} for c in cats]


@router.post("/categories")
async def create_category(payload: CategoryPayload, db: AsyncSession = Depends(get_db)):
    cat = Category(**payload.model_dump())
    db.add(cat)
    await db.commit()
    return {"id": cat.id}


@router.patch("/categories/{category_id}")
async def update_category(category_id: str, payload: CategoryPayload, db: AsyncSession = Depends(get_db)):
    cat = await db.get(Category, category_id)
    if cat is None:
        raise HTTPException(404, "Category not found")
    for k, v in payload.model_dump().items():
        setattr(cat, k, v)
    await db.commit()
    return {"ok": True}


@router.get("/topics")
async def list_topics(db: AsyncSession = Depends(get_db)):
    topics = (await db.execute(select(Topic))).scalars().all()
    node_counts = dict(
        (await db.execute(select(ConceptNode.topic_id, func.count()).group_by(ConceptNode.topic_id))).all()
    )
    return [
        {
            "id": t.id, "category_id": t.category_id, "name": t.name,
            "description": t.description, "is_active": t.is_active,
            "concept_count": node_counts.get(t.id, 0),
        }
        for t in topics
    ]


@router.post("/topics")
async def create_topic(
    payload: TopicPayload,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    if await db.get(Category, payload.category_id) is None:
        raise HTTPException(404, "Category not found")
    topic = Topic(**payload.model_dump(), created_by_admin_id=admin.id)
    db.add(topic)
    await db.commit()
    return {"id": topic.id}


@router.patch("/topics/{topic_id}")
async def update_topic(topic_id: str, payload: TopicPayload, db: AsyncSession = Depends(get_db)):
    topic = await db.get(Topic, topic_id)
    if topic is None:
        raise HTTPException(404, "Topic not found")
    for k, v in payload.model_dump().items():
        setattr(topic, k, v)
    await db.commit()
    return {"ok": True}


# ---------- Knowledge graph: ConceptNodes + ConceptEdges ----------

class ConceptNodePayload(BaseModel):
    title: str
    learning_objective: str
    difficulty_tag: str = Field(pattern="^(beginner|intermediate|advanced)$")
    bloom_level: str = Field(pattern="^(remember|understand|apply|analyse)$")
    estimated_duration_mins: int = 10
    is_root: bool = False


class ConceptEdgePayload(BaseModel):
    from_concept_id: str
    to_concept_id: str
    edge_type: str = Field(default="required", pattern="^(required|recommended)$")


@router.get("/topics/{topic_id}/graph")
async def get_graph(topic_id: str, db: AsyncSession = Depends(get_db)):
    nodes = (
        await db.execute(select(ConceptNode).where(ConceptNode.topic_id == topic_id))
    ).scalars().all()
    edges = (
        await db.execute(select(ConceptEdge).where(ConceptEdge.topic_id == topic_id))
    ).scalars().all()
    return {
        "nodes": [
            {
                "id": n.id, "title": n.title, "learning_objective": n.learning_objective,
                "difficulty_tag": n.difficulty_tag, "bloom_level": n.bloom_level,
                "estimated_duration_mins": n.estimated_duration_mins, "is_root": n.is_root,
            }
            for n in nodes
        ],
        "edges": [
            {"id": e.id, "from": e.from_concept_id, "to": e.to_concept_id, "type": e.edge_type}
            for e in edges
        ],
    }


@router.post("/topics/{topic_id}/nodes")
async def create_node(topic_id: str, payload: ConceptNodePayload, db: AsyncSession = Depends(get_db)):
    if await db.get(Topic, topic_id) is None:
        raise HTTPException(404, "Topic not found")
    node = ConceptNode(topic_id=topic_id, **payload.model_dump())
    db.add(node)
    await db.commit()
    return {"id": node.id}


@router.patch("/nodes/{node_id}")
async def update_node(node_id: str, payload: ConceptNodePayload, db: AsyncSession = Depends(get_db)):
    node = await db.get(ConceptNode, node_id)
    if node is None:
        raise HTTPException(404, "Node not found")
    for k, v in payload.model_dump().items():
        setattr(node, k, v)
    await db.commit()
    return {"ok": True}


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, db: AsyncSession = Depends(get_db)):
    node = await db.get(ConceptNode, node_id)
    if node is None:
        raise HTTPException(404, "Node not found")
    await db.execute(delete(ConceptEdge).where(
        (ConceptEdge.from_concept_id == node_id) | (ConceptEdge.to_concept_id == node_id)
    ))
    await db.delete(node)
    await db.commit()
    return {"ok": True}


async def _would_create_cycle(db: AsyncSession, topic_id: str, from_id: str, to_id: str) -> bool:
    """Adding from->to creates a cycle iff `from` is reachable from `to`."""
    edges = (
        await db.execute(select(ConceptEdge).where(ConceptEdge.topic_id == topic_id))
    ).scalars().all()
    adjacency: dict[str, list[str]] = {}
    for e in edges:
        adjacency.setdefault(e.from_concept_id, []).append(e.to_concept_id)
    stack, seen = [to_id], set()
    while stack:
        current = stack.pop()
        if current == from_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, []))
    return False


@router.post("/topics/{topic_id}/edges")
async def create_edge(topic_id: str, payload: ConceptEdgePayload, db: AsyncSession = Depends(get_db)):
    from_node = await db.get(ConceptNode, payload.from_concept_id)
    to_node = await db.get(ConceptNode, payload.to_concept_id)
    if not from_node or not to_node or from_node.topic_id != topic_id or to_node.topic_id != topic_id:
        raise HTTPException(404, "Both concepts must exist in this topic")
    if payload.from_concept_id == payload.to_concept_id:
        raise HTTPException(422, "A concept cannot be its own prerequisite")
    if await _would_create_cycle(db, topic_id, payload.from_concept_id, payload.to_concept_id):
        raise HTTPException(422, "Edge would create a cycle — the graph must stay a DAG")
    edge = ConceptEdge(
        topic_id=topic_id,
        from_concept_id=payload.from_concept_id,
        to_concept_id=payload.to_concept_id,
        edge_type=payload.edge_type,
    )
    db.add(edge)
    await db.commit()
    return {"id": edge.id}


@router.delete("/edges/{edge_id}")
async def delete_edge(edge_id: str, db: AsyncSession = Depends(get_db)):
    edge = await db.get(ConceptEdge, edge_id)
    if edge is None:
        raise HTTPException(404, "Edge not found")
    await db.delete(edge)
    await db.commit()
    return {"ok": True}


# ---------- GenerationContract ----------

class ContractPayload(BaseModel):
    persona_text: str
    structural_template: str
    constraints_text: str


@router.get("/contracts")
async def list_contracts(db: AsyncSession = Depends(get_db)):
    contracts = (
        await db.execute(select(GenerationContract).order_by(GenerationContract.version.desc()))
    ).scalars().all()
    return [
        {
            "id": c.id, "version": c.version, "is_active": c.is_active,
            "persona_text": c.persona_text, "structural_template": c.structural_template,
            "constraints_text": c.constraints_text, "created_at": c.created_at.isoformat(),
        }
        for c in contracts
    ]


@router.post("/contracts")
async def create_contract_version(payload: ContractPayload, db: AsyncSession = Depends(get_db)):
    """Saving always creates a NEW version and activates it; old versions are retained."""
    max_version = (
        await db.execute(select(func.coalesce(func.max(GenerationContract.version), 0)))
    ).scalar_one()
    active = (
        await db.execute(select(GenerationContract).where(GenerationContract.is_active.is_(True)))
    ).scalars().all()
    for c in active:
        c.is_active = False
    contract = GenerationContract(version=max_version + 1, is_active=True, **payload.model_dump())
    db.add(contract)
    await db.commit()
    return {"id": contract.id, "version": contract.version}


# ---------- Content review queue (read-only in v1) ----------

@router.get("/content")
async def review_content(
    topic_id: str | None = None,
    concept_node_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(GeneratedContent).order_by(GeneratedContent.created_at.desc()).limit(min(limit, 200))
    if topic_id:
        query = query.where(GeneratedContent.topic_id == topic_id)
    if concept_node_id:
        query = query.where(GeneratedContent.concept_node_id == concept_node_id)
    if status:
        query = query.where(GeneratedContent.status == status)
    items = (await db.execute(query)).scalars().all()
    node_titles = dict((await db.execute(select(ConceptNode.id, ConceptNode.title))).all())
    return [
        {
            "id": c.id, "signature": c.signature, "signature_inputs": c.signature_inputs,
            "topic_id": c.topic_id, "concept_node_id": c.concept_node_id,
            "concept_title": node_titles.get(c.concept_node_id),
            "status": c.status, "model_used": c.model_used,
            "generation_contract_version": c.generation_contract_version,
            "created_at": c.created_at.isoformat(), "error": c.error,
        }
        for c in items
    ]


@router.get("/content/{content_id}")
async def review_content_detail(content_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(GeneratedContent, content_id)
    if c is None:
        raise HTTPException(404, "Content not found")
    return {
        "id": c.id, "signature": c.signature, "signature_inputs": c.signature_inputs,
        "topic_id": c.topic_id, "concept_node_id": c.concept_node_id,
        "status": c.status, "model_used": c.model_used,
        "generation_contract_version": c.generation_contract_version,
        "lesson_body": c.lesson_body, "quiz_body": c.quiz_body,
        "created_at": c.created_at.isoformat(), "error": c.error,
    }


# ---------- Analytics ----------

@router.get("/analytics")
async def analytics(db: AsyncSession = Depends(get_db)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_goals = (await db.execute(select(func.count(UserGoal.id)))).scalar_one()
    goals_by_status = dict(
        (await db.execute(select(UserGoal.status, func.count()).group_by(UserGoal.status))).all()
    )
    completions_by_concept = dict(
        (await db.execute(
            select(LessonCompletion.concept_node_id, func.count()).group_by(LessonCompletion.concept_node_id)
        )).all()
    )
    avg_quiz_by_concept = {
        cid: round(float(avg), 1)
        for cid, avg in (await db.execute(
            select(LessonCompletion.concept_node_id, func.avg(LessonCompletion.quiz_score))
            .group_by(LessonCompletion.concept_node_id)
        )).all()
    }
    cache_stats = dict(
        (await db.execute(select(GeneratedContent.status, func.count()).group_by(GeneratedContent.status))).all()
    )

    # common root gaps across active goals
    goals = (await db.execute(select(UserGoal).where(UserGoal.status == "active"))).scalars().all()
    root_gap_counts: dict[str, int] = {}
    for g in goals:
        for cid in g.root_gap_concepts or []:
            root_gap_counts[cid] = root_gap_counts.get(cid, 0) + 1

    node_titles = dict((await db.execute(select(ConceptNode.id, ConceptNode.title))).all())
    return {
        "total_users": total_users,
        "total_goals": total_goals,
        "goals_by_status": goals_by_status,
        "generated_content_by_status": cache_stats,
        "concept_stats": [
            {
                "concept_node_id": cid,
                "title": node_titles.get(cid, cid),
                "completions": count,
                "avg_quiz_score": avg_quiz_by_concept.get(cid),
            }
            for cid, count in sorted(completions_by_concept.items(), key=lambda kv: -kv[1])
        ],
        "common_root_gaps": [
            {"concept_node_id": cid, "title": node_titles.get(cid, cid), "user_count": count}
            for cid, count in sorted(root_gap_counts.items(), key=lambda kv: -kv[1])[:15]
        ],
    }
