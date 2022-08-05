from fastapi import APIRouter
from app.core.routers.schema import index as clients_router


router = APIRouter()
router.include_router(clients_router.router, prefix="/clients")