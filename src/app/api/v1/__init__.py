from fastapi import APIRouter

from .images import router as images_router

router = APIRouter(prefix="/v1")
router.include_router(images_router)

