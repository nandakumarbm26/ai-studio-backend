from fastapi import FastAPI
from app.api.v1.api_router import router as api_router
import app.db.init_db


app = FastAPI(title="PromptAI Platform")

app.include_router(api_router, prefix="/api/v1")