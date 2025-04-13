from fastapi import APIRouter, HTTPException
from app.schemas.agent import ResponseCreatePromptEngineeredAgent, CreatePromptEngineeredAgent, PromptAgentQueryRequest
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.agent import create_prompt_agent, get_prompt_agent
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=ResponseCreatePromptEngineeredAgent)
def create_prompt_agent_handler(promptAgent: CreatePromptEngineeredAgent, db: Session = Depends(get_db)):
    try:
        return create_prompt_agent(db, promptAgent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ResponseCreatePromptEngineeredAgent|list[ResponseCreatePromptEngineeredAgent])
def read_all(filters: PromptAgentQueryRequest = Depends(),db: Session = Depends(get_db)):
    try:
        return get_prompt_agent(db, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))