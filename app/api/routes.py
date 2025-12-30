from fastapi import APIRouter
from app.api.jobs import router as jobs_router
from app.api.webhooks import router as webhooks_router

router = APIRouter()
router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
