from fastapi import APIRouter
from app.api.v1.endpoints import items, chat, agent, auth, gql


router = APIRouter()

router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(agent.router, prefix="/agents", tags=["agents"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(gql.router, prefix="/gql", tags=["gql"])
