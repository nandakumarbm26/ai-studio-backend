import strawberry
from typing import List, Optional
from datetime import datetime
from app.models.agent import PromptEngineeredAgent
from app.schemas.graphql.auth import User
from app.db.session import get_db
from app.lib.gql import map_model
from app.lib.gql import requires_auth
from strawberry.types import Info

# --- GraphQL Types ---
@strawberry.input
class TrainingPrompt:
    userPrompt: str
    expectedResponse: str

@strawberry.input
class CreatePromptEngineeredAgent:
    agentName: str
    description: str
    system: str
    responseTemplate: str
    trainingPrompts: List[TrainingPrompt]

@strawberry.input
class UpdatePromptEngineeredAgent:
    agentName: Optional[str] = None
    description: Optional[str] = None
    system: Optional[str] = None
    responseTemplate: Optional[str] = None
    trainingPrompts: Optional[List[TrainingPrompt]] = None

@strawberry.type
class ResponseCreatePromptEngineeredAgent:
    id: int
    agentName: Optional[str]
    description: Optional[str]
    system: Optional[str]
    responseTemplate: Optional[str]
    trainingPrompts: Optional[str]
    createdDate: Optional[datetime]
    updatedDate: Optional[datetime]

# --- Mutations ---
@strawberry.type
class AgentMutation:
    @strawberry.mutation
    @requires_auth
    def create_agent(self, input: CreatePromptEngineeredAgent) -> ResponseCreatePromptEngineeredAgent:
        from json import dumps
        db = next(get_db())
        db_agent = PromptEngineeredAgent(
        agentName=input.agentName,
            description=input.description,
            system=input.system,
            responseTemplate=input.responseTemplate,
            trainingPrompts=dumps([tp.__dict__ for tp in input.trainingPrompts]),
        )
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return ResponseCreatePromptEngineeredAgent(**db_agent.__dict__)

    @strawberry.mutation
    @requires_auth
    def update_agent(self, id: int, input: UpdatePromptEngineeredAgent) -> Optional[ResponseCreatePromptEngineeredAgent]:
        from json import dumps
        db = next(get_db())
        agent = db.query(PromptEngineeredAgent).filter(PromptEngineeredAgent.id == id).first()
        if not agent:
            return None
        if input.agentName is not None:
            agent.agentName = input.agentName
        if input.description is not None:
            agent.description = input.description
        if input.system is not None:
            agent.system = input.system
        if input.responseTemplate is not None:
            agent.responseTemplate = input.responseTemplate
        if input.trainingPrompts is not None:
            agent.trainingPrompts = dumps([tp.__dict__ for tp in input.trainingPrompts])
        db.commit()
        db.refresh(agent)
        return ResponseCreatePromptEngineeredAgent(**agent.__dict__)

    @strawberry.mutation
    @requires_auth
    def delete_agent(self, id: int) -> bool:
        db = next(get_db())
        agent = db.query(PromptEngineeredAgent).filter(PromptEngineeredAgent.id == id).first()
        if agent:
            db.delete(agent)
            db.commit()
            return True
        return False

# --- Queries ---
@strawberry.type
class AgentQuery:
    @strawberry.field
    @requires_auth
    def agent(self, id: int) -> Optional[ResponseCreatePromptEngineeredAgent]:
        db = next(get_db())
        agent = db.query(PromptEngineeredAgent).filter(PromptEngineeredAgent.id == id).first()

        return map_model(agent,ResponseCreatePromptEngineeredAgent) if agent else None

    @strawberry.field
    @requires_auth
    def list_agents(self, info:Info) -> List[ResponseCreatePromptEngineeredAgent]:
        user = info.context.get("user")
        db = next(get_db())
        agents = db.query(PromptEngineeredAgent).all()
        # agents = db.query(PromptEngineeredAgent).filter(PromptEngineeredAgent.email == user.email)
        return [map_model(a,ResponseCreatePromptEngineeredAgent) for a in agents] if len(agents) else None


