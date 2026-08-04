import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

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
    """Fail fast with a clear message when deploy env is misconfigured."""
    db = settings.database_url
    local_db = "localhost" in db or "127.0.0.1" in db
    # Direct db.<ref>.supabase.co is IPv6-only; Railway has no outbound IPv6.
    if "db." in db and "supabase.co" in db and "pooler.supabase.com" not in db:
        raise RuntimeError(
            "DATABASE_URL uses the Supabase direct host (IPv6). "
            "Railway cannot open outbound IPv6 connections. "
            "In Supabase → Connect, copy the Session pooler URI "
            "(host ends with pooler.supabase.com, port 5432), "
            "use scheme postgresql+asyncpg://, and set that as DATABASE_URL."
        )
    if _on_railway() and local_db:
        raise RuntimeError(
            "Running on Railway but DATABASE_URL points at localhost. "
            "Set DATABASE_URL to your Supabase session-pooler URI."
        )
    if local_db and settings.app_env == "production":
        raise RuntimeError(
            "DATABASE_URL points at localhost but APP_ENV=production. "
            "Set DATABASE_URL to your Supabase session-pooler URI."
        )
    if local_db:
        logger.warning(
            "DATABASE_URL targets localhost (%s).",
            db.split("@")[-1] if "@" in db else db,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Bind the HTTP server first so /health can pass, then migrate.

    Awaiting migrations before yield kept the port closed; any slow/failed DB
    connect made Railway report 'service unavailable' for the whole window.
    """
    _assert_runtime_config()
    logger.info(
        "Starting %s (env=%s, db_host=%s, railway=%s)",
        settings.app_name,
        settings.app_env,
        settings.database_url.split("@")[-1] if "@" in settings.database_url else "(unset)",
        _on_railway(),
    )
    app.state.db_ready = False

    async def _migrate() -> None:
        try:
            await run_migrations()
            app.state.db_ready = True
            logger.info("Startup migrations complete")
        except Exception:
            logger.exception(
                "Startup migrations failed — cannot reach the database. "
                "Check DATABASE_URL (Supabase session pooler, pooler.supabase.com)."
            )
            os._exit(1)

    migrate_task = asyncio.create_task(_migrate())
    try:
        yield
    finally:
        migrate_task.cancel()
        with suppress(asyncio.CancelledError):
            await migrate_task
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
    return {
        "status": "ok",
        "app": settings.app_name,
        "db_ready": bool(getattr(app.state, "db_ready", False)),
    }
