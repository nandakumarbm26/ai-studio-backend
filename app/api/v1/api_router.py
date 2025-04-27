from fastapi import APIRouter
from app.api.v1.endpoints import gql


router = APIRouter()


router.include_router(gql.router, prefix="/gql", tags=["gql"])
