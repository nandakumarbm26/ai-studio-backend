from sqlalchemy.orm import Session
from app.models.agent import PromptEngineeredAgent
from app.schemas.agent import CreatePromptEngineeredAgent, PromptAgentQueryRequest
import json
from fastapi.encoders import jsonable_encoder

def create_prompt_agent(db: Session, promptAgent: CreatePromptEngineeredAgent):
    promptAgent.trainingPrompts = json.dumps([tp.dict() for tp in promptAgent.trainingPrompts])
    db_item = PromptEngineeredAgent(**promptAgent.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_prompt_agent(db: Session, filters: PromptAgentQueryRequest):
    query = db.query(PromptEngineeredAgent)
    filter_dict = jsonable_encoder(filters)
    if filter_dict["s"]:
        query = db.query(*[getattr(PromptEngineeredAgent, attr) for attr in filter_dict['s'].split(',')])

    for attr, value in filter_dict.items():
        if value is not None and attr in PromptEngineeredAgent.__dict__:
            query = query.filter(getattr(PromptEngineeredAgent, attr) == value)

    return query.all()