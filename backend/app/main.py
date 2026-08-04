import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine
from .migrations import run_migrations
from .routes import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("upvex")


def _on_railway() -> bool:
    return bool(
        os.environ.get("RAILWAY_ENVIRONMENT")
        or os.environ.get("RAILWAY_PROJECT_ID")
        or os.environ.get("RAILWAY_SERVICE_ID")
    )


def _assert_runtime_config() -> None:
    """Fail fast with a clear message when deploy env is misconfigured.

    Railway does not ship backend/.env — DATABASE_URL must be set in Variables.
    Without it we default to localhost Postgres and crash during migrations,
    which makes /health return service unavailable.
    """
    db = settings.database_url
    local_db = "localhost" in db or "127.0.0.1" in db
    if _on_railway() and local_db:
        raise RuntimeError(
            "Running on Railway but DATABASE_URL points at localhost. "
            "In Railway → Variables, set DATABASE_URL to your Supabase "
            "session-pooler URI (postgresql+asyncpg://...@....pooler.supabase.com:5432/postgres)."
        )
    if local_db and settings.app_env == "production":
        raise RuntimeError(
            "DATABASE_URL points at localhost but APP_ENV=production. "
            "Set DATABASE_URL to your Supabase session-pooler URI."
        )
    if local_db:
        logger.warning(
            "DATABASE_URL targets localhost (%s). Fine for local docker-compose; "
            "on Railway you must set DATABASE_URL in service variables.",
            db.split("@")[-1] if "@" in db else db,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _assert_runtime_config()
    logger.info(
        "Starting %s (env=%s, db_host=%s, railway=%s)",
        settings.app_name,
        settings.app_env,
        settings.database_url.split("@")[-1] if "@" in settings.database_url else "(unset)",
        _on_railway(),
    )
    try:
        await run_migrations()
    except Exception:
        logger.exception(
            "Startup migrations failed — cannot reach the database. "
            "Check DATABASE_URL (Supabase session pooler, postgresql+asyncpg://)."
        )
        raise
    yield
    await engine.dispose()


app = FastAPI(title="Upvex API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
