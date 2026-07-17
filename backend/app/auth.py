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
from .models import User, utcnow

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


def _apply_email_verified(user: User, email_verified: bool) -> None:
    """Mirror Supabase's confirmation state onto the local user, stamping the
    verification time the first time it flips true."""
    if email_verified and not user.email_verified:
        user.email_verified_at = utcnow()
    user.email_verified = email_verified


async def _upsert_user(
    db: AsyncSession,
    auth_id: str,
    email: str,
    display_name: str | None,
    *,
    is_admin: bool = False,
    email_verified: bool = False,
) -> User:
    user = (
        await db.execute(select(User).where(User.auth_provider_id == auth_id))
    ).scalar_one_or_none()
    if user is None:
        # Same email can return with a new Supabase auth id after delete + re-signup.
        user = (
            await db.execute(select(User).where(User.email == email))
        ).scalar_one_or_none()
        if user is not None:
            user.auth_provider_id = auth_id
            if display_name:
                user.display_name = display_name
            _apply_email_verified(user, email_verified)
            await db.commit()
            await db.refresh(user)
            return user
        user = User(
            auth_provider_id=auth_id,
            email=email,
            display_name=display_name or email.split("@")[0],
            is_admin=is_admin,
        )
        _apply_email_verified(user, email_verified)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    if user.email_verified != email_verified:
        _apply_email_verified(user, email_verified)
        await db.commit()
        await db.refresh(user)
    return user


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else None

    if not token:
        if settings.dev_auth_bypass:
            return await _upsert_user(
                db,
                DEV_USER["auth_provider_id"],
                DEV_USER["email"],
                DEV_USER["display_name"],
                is_admin=True,
                email_verified=True,
            )
        raise HTTPException(status_code=401, detail="Missing bearer token")

    claims = _decode_token(token)
    auth_id = claims.get("sub")
    email = claims.get("email") or f"{auth_id}@unknown.upvex"
    meta = claims.get("user_metadata") or {}
    display_name = meta.get("full_name") or meta.get("name")
    # Supabase stores email confirmation state in the user_metadata claim; a
    # confirmed `email_confirmed_at` also implies verified.
    email_verified = bool(meta.get("email_verified") or claims.get("email_confirmed_at"))
    if not auth_id:
        raise HTTPException(status_code=401, detail="Token missing subject")
    return await _upsert_user(db, auth_id, email, display_name, email_verified=email_verified)


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
