from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User, UserProfile

router = APIRouter()


class OnboardingPayload(BaseModel):
    learning_style: str = Field(pattern="^(visual|reading|hands_on|mixed)$")
    time_availability: str = Field(pattern="^(under_30|30_to_60|over_60)$")
    motivation: str = Field(pattern="^(career_switch|upskilling|curiosity|interview_prep)$")
    tech_background: str = Field(pattern="^(none|some_scripting|professional_dev|data_adjacent)$")
    tone_preference: str = Field(pattern="^(playful|professional|neutral)$")
    raw_answers: dict = Field(default_factory=dict)
    display_name: str | None = None


def _profile_dict(profile: UserProfile | None) -> dict | None:
    if profile is None:
        return None
    return {
        "learning_style": profile.learning_style,
        "time_availability": profile.time_availability,
        "motivation": profile.motivation,
        "tech_background": profile.tech_background,
        "tone_preference": profile.tone_preference,
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    ).scalar_one_or_none()
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
        "email_verified": user.email_verified,
        "onboarded": profile is not None,
        "profile": _profile_dict(profile),
    }


@router.post("/onboarding")
async def save_onboarding(
    payload: OnboardingPayload,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    ).scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=user.id, **{
            k: getattr(payload, k)
            for k in ("learning_style", "time_availability", "motivation", "tech_background", "tone_preference")
        }, raw_onboarding_answers=payload.raw_answers)
        db.add(profile)
    else:
        for k in ("learning_style", "time_availability", "motivation", "tech_background", "tone_preference"):
            setattr(profile, k, getattr(payload, k))
        profile.raw_onboarding_answers = payload.raw_answers
    if payload.display_name:
        user.display_name = payload.display_name
    await db.commit()
    return {"ok": True, "profile": _profile_dict(profile)}
