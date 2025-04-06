from fastapi import FastAPI
from app.api.v1.api_router import router as api_router
import app.db.init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PromptAI Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 Allow all origins (for dev only!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")