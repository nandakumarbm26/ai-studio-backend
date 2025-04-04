from fastapi import APIRouter
from app.api.v1.endpoints import items

router = APIRouter()

router.include_router(items.router, prefix="/items", tags=["items"])
# router.include_router(users.router, prefix="/users", tags=["users"])