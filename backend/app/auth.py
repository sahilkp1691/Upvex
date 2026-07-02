"""Supabase JWT verification + local user upsert.

Two verification paths:
- SUPABASE_JWT_SECRET set  -> HS256 (Supabase legacy JWT secret)
- otherwise                -> JWKS from {SUPABASE_URL}/auth/v1/.well-known/jwks.json (RS256/ES256)

DEV_AUTH_BYPASS=true lets local development run without a Supabase project:
requests without a Bearer token act as a fixed local dev user (an admin).
"""

import jwt
from fastapi import Depends, HTTPException, Request
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .models import User

_jwks_client: PyJWKClient | None = None

DEV_USER = {
    "auth_provider_id": "dev-local-user",
    "email": "dev@upvex.local",
    "display_name": "Dev User",
}


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(url, cache_keys=True)
    return _jwks_client


def _decode_token(token: str) -> dict:
    try:
        if settings.supabase_jwt_secret:
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


async def _upsert_user(db: AsyncSession, auth_id: str, email: str, display_name: str | None, *, is_admin: bool = False) -> User:
    user = (
        await db.execute(select(User).where(User.auth_provider_id == auth_id))
    ).scalar_one_or_none()
    if user is None:
        user = User(
            auth_provider_id=auth_id,
            email=email,
            display_name=display_name or email.split("@")[0],
            is_admin=is_admin,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else None

    if not token:
        if settings.dev_auth_bypass:
            return await _upsert_user(
                db, DEV_USER["auth_provider_id"], DEV_USER["email"], DEV_USER["display_name"], is_admin=True
            )
        raise HTTPException(status_code=401, detail="Missing bearer token")

    claims = _decode_token(token)
    auth_id = claims.get("sub")
    email = claims.get("email") or f"{auth_id}@unknown.upvex"
    meta = claims.get("user_metadata") or {}
    display_name = meta.get("full_name") or meta.get("name")
    if not auth_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
    return await _upsert_user(db, auth_id, email, display_name)


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
