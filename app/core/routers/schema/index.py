from fastapi import APIRouter
from app.core.routers.schema.user import index as users_router


router = APIRouter()
router.include_router(users_router.router, prefix="/users")