import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON as GenericJSON

from .database import Base

# JSONB on Postgres, plain JSON elsewhere (SQLite in tests)
JSON = GenericJSON().with_variant(JSONB(), "postgresql")


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    auth_provider_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # Supabase user id
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    profile: Mapped["UserProfile | None"] = relationship(back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    learning_style: Mapped[str] = mapped_column(String(20))  # visual | reading | hands_on | mixed
    time_availability: Mapped[str] = mapped_column(String(20))  # under_30 | 30_to_60 | over_60
    motivation: Mapped[str] = mapped_column(String(40))  # career_switch | upskilling | curiosity | interview_prep
    tech_background: Mapped[str] = mapped_column(String(40))  # none | some_scripting | professional_dev | data_adjacent
    tone_preference: Mapped[str] = mapped_column(String(20))  # playful | professional | neutral
    raw_onboarding_answers: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped[User] = relationship(back_populates="profile")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    topics: Mapped[list["Topic"]] = relationship(back_populates="category")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_admin_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    category: Mapped[Category] = relationship(back_populates="topics")
    concept_nodes: Mapped[list["ConceptNode"]] = relationship(back_populates="topic")


class ConceptNode(Base):
    __tablename__ = "concept_nodes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    learning_objective: Mapped[str] = mapped_column(Text)
    difficulty_tag: Mapped[str] = mapped_column(String(20))  # beginner | intermediate | advanced
    bloom_level: Mapped[str] = mapped_column(String(20))  # remember | understand | apply | analyse
    estimated_duration_mins: Mapped[int] = mapped_column(Integer, default=10)
    is_root: Mapped[bool] = mapped_column(Boolean, default=False)

    topic: Mapped[Topic] = relationship(back_populates="concept_nodes")


class ConceptEdge(Base):
    __tablename__ = "concept_edges"
    __table_args__ = (
        Index("ix_concept_edges_topic_to", "topic_id", "to_concept_id"),
        Index("ix_concept_edges_topic_from", "topic_id", "from_concept_id"),
        UniqueConstraint("from_concept_id", "to_concept_id", name="uq_concept_edge_pair"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    from_concept_id: Mapped[str] = mapped_column(ForeignKey("concept_nodes.id"))  # prerequisite
    to_concept_id: Mapped[str] = mapped_column(ForeignKey("concept_nodes.id"))  # dependent
    edge_type: Mapped[str] = mapped_column(String(20), default="required")  # required | recommended
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"))  # denormalized for topic-scoped queries


class UserGoal(Base):
    __tablename__ = "user_goals"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_user_goal_topic"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="diagnostic_pending")
    # diagnostic_pending | active | completed | paused
    level_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    concept_gap_map: Mapped[dict] = mapped_column(JSON, default=dict)  # {concept_id: 0-100}
    root_gap_concepts: Mapped[list] = mapped_column(JSON, default=list)  # [concept_id, ...]
    completed_concepts: Mapped[list] = mapped_column(JSON, default=list)  # [concept_id, ...]
    pacing_choice: Mapped[str | None] = mapped_column(String(20), nullable=True)  # casual | regular | intense
    target_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    topic: Mapped[Topic] = relationship()


class DiagnosticQuestion(Base):
    """Seeded per-topic question bank powering the adaptive diagnostic quiz."""

    __tablename__ = "diagnostic_questions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True)
    concept_node_id: Mapped[str] = mapped_column(ForeignKey("concept_nodes.id"), index=True)
    difficulty: Mapped[str] = mapped_column(String(10))  # easy | medium | hard
    type: Mapped[str] = mapped_column(String(20))  # multiple_choice | short_answer
    question_text: Mapped[str] = mapped_column(Text)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)  # for multiple_choice
    correct_option: Mapped[int | None] = mapped_column(Integer, nullable=True)  # index into options
    expected_concepts: Mapped[list | None] = mapped_column(JSON, nullable=True)  # for short_answer grading


class DiagnosticAttempt(Base):
    __tablename__ = "diagnostic_attempts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_goal_id: Mapped[str] = mapped_column(ForeignKey("user_goals.id"), index=True)
    responses: Mapped[list] = mapped_column(JSON, default=list)
    evaluator_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")  # in_progress | completed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class GenerationContract(Base):
    __tablename__ = "generation_contracts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    version: Mapped[int] = mapped_column(Integer, unique=True)
    persona_text: Mapped[str] = mapped_column(Text)
    structural_template: Mapped[str] = mapped_column(Text)
    constraints_text: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class GeneratedContent(Base):
    __tablename__ = "generated_content"
    __table_args__ = (Index("ix_generated_content_sig_version", "signature", "generation_contract_version"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    signature: Mapped[str] = mapped_column(String(64), index=True)  # ProfileSignature hash
    signature_inputs: Mapped[dict] = mapped_column(JSON, default=dict)  # human-readable signature components
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True)
    concept_node_id: Mapped[str] = mapped_column(ForeignKey("concept_nodes.id"), index=True)
    lesson_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    quiz_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generation_contract_version: Mapped[int] = mapped_column(Integer)
    model_used: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | ready | failed
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LessonCompletion(Base):
    __tablename__ = "lesson_completions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    user_goal_id: Mapped[str] = mapped_column(ForeignKey("user_goals.id"), index=True)
    concept_node_id: Mapped[str] = mapped_column(ForeignKey("concept_nodes.id"), index=True)
    generated_content_id: Mapped[str] = mapped_column(ForeignKey("generated_content.id"))
    quiz_score: Mapped[float] = mapped_column(Float)  # 0-100
    concept_score_delta: Mapped[float] = mapped_column(Float, default=0)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class XPLedger(Base):
    __tablename__ = "xp_ledger"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(30))  # lesson_complete | quiz_score | streak_bonus | milestone
    related_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Streak(Base):
    __tablename__ = "streaks"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    criteria: Mapped[dict] = mapped_column(JSON, default=dict)
    # criteria examples:
    #   {"type": "root_gap_resolved"}
    #   {"type": "concepts_completed", "count": 5}
    #   {"type": "streak_days", "days": 7}
    #   {"type": "first_lesson"}


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    badge_id: Mapped[str] = mapped_column(ForeignKey("badges.id"))
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SchemaMigration(Base):
    """Tracks applied hand-rolled migration steps (idempotent runner)."""

    __tablename__ = "schema_migrations"

    name: Mapped[str] = mapped_column(String(120), primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
