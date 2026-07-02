from fastapi import APIRouter

from . import admin, catalog, content, diagnostic, gamification, goals, me, roadmap

api_router = APIRouter()
api_router.include_router(me.router, tags=["me"])
api_router.include_router(catalog.router, tags=["catalog"])
api_router.include_router(goals.router, tags=["goals"])
api_router.include_router(diagnostic.router, tags=["diagnostic"])
api_router.include_router(roadmap.router, tags=["roadmap"])
api_router.include_router(content.router, tags=["content"])
api_router.include_router(gamification.router, tags=["gamification"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
