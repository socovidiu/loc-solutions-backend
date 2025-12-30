from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import router as api_router
from app.db.database import engine, Base

settings = get_settings()



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Localization Solutions Backend API",
    docs_url="/docs" if settings.ENV != "prod" else None,
    redoc_url="/redoc" if settings.ENV != "prod" else None,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.ENV,
        "tms": settings.TMS_PROVIDER,
        "llm": settings.LLM_PROVIDER,
    }

app.include_router(api_router, prefix="/api")

