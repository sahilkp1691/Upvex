"""Start the Upvex FastAPI backend for local development.

Usage (from the backend directory, with the venv active):
    python run_app.py
"""

import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
    )
