from fastapi import APIRouter
from app.api.v1.endpoints import items, chat, agent





router = APIRouter()

router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(agent.router, prefix="/agents", tags=["agents"])
