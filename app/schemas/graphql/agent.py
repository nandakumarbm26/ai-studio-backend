import strawberry
from datetime import datetime

import strawberry.types
from app.models.agent import PromptEngineeredAgent
from app.db.session import get_db
from app.lib.graphql.gql import map_model
from app.lib.graphql.gql import requires_auth
from strawberry.types import Info
from fastapi import HTTPException
from app.crud.agent import get_prompt_agent
from app.lib.openai_wrapper import OpenAI
import json
from json.decoder import JSONDecodeError
from typing import List, Optional,Type
from enum import Enum
from sqlalchemy import or_
from app.lib.graphql.get_items import list_items, get_item_by_id
SQL_RECORDS_LIMIT =  10


@strawberry.enum
class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@strawberry.enum
class InputEnum(Enum):
    TEXT = "text"
    IMAGE_URL = "image_url"

# Define message types for content (Text and Image)
@strawberry.input
class Input:
    type: InputEnum  # Content type, e.g., "text"
    text: Optional[str] = None  # The actual message content
    imageUrl: Optional[str] = None  # The actual message content

@strawberry.input
class Content:
    text:Optional[Input] = None
    image:Optional[Input] = None

# Define Message Type that uses the Role Enum and Content (Text or Image)
@strawberry.input
class Message:
    role: Role  # Role of the sender: system, user, or assistant
    content: Content # Content of the message (Text or Image)

    def to_dict(self):
        parts = []

        if self.content.text and self.content.text.text:
            parts.append(self.content.text.text)

        if self.content.image and self.content.image.imageUrl:
            parts.append({
                "type": "image_url",
                "image_url": {"url": self.content.image.imageUrl}
            })

        content = parts[0] if len(parts) == 1 and isinstance(parts[0], str) else parts

        return {
            "role": self.role.value,
            "content": content
        }


# Define the query filters (optional fields)
@strawberry.input
class PromptAgentQueryRequest:
    id: Optional[int] = None  # Optional unique identifier
    agentName: Optional[str] = None  # Agent name (optional)
    system: Optional[str] = None  # System name or identifier (optional)
    s: Optional[str] = None  # Search or query parameter


# Define the input object for the chat request
@strawberry.input
class ChatRequest:
    messages: List[Message]  # List of messages for the chat
    filters: Optional[PromptAgentQueryRequest] = None  # Optional filters for the query


# Define the response type for the chat completion (output type)
@strawberry.type
class ChatResponse:
    content: str
    refusal: Optional[str]
    role: str
    annotations: Optional[str]
    audio: Optional[str]
    function_call: Optional[str]
    tool_calls: Optional[str]

    
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

@strawberry.input
class ResponseCreatePromptEngineeredAgentRes:
    id: int
    agentName: Optional[str]
    description: Optional[str]
    system: Optional[str]
    responseTemplate: Optional[str]
    trainingPrompts: Optional[str]
    createdDate: Optional[datetime]
    updatedDate: Optional[datetime]

@strawberry.type
class ListAgentResponse:
    items : List[ResponseCreatePromptEngineeredAgent]
    has_more : bool
    page : int

@strawberry.input
class ListAgentres:
    agents : List[ResponseCreatePromptEngineeredAgentRes]
    has_more : bool
    page : int

@strawberry.input
class ListAgentsRequest:
    page: int
    s: Optional[str] = None
    order_by: Optional[str] = None

@strawberry.input
class AgentRequest:
    id:int

@strawberry.input
class ListAgentFilters:
    search: Optional[str] = None
    order_by: Optional[str] = "createdDate"  # default ordering
    descending: Optional[bool] = True        # descending by default

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


    # Define the mutation to handle chat completions using OpenAI
    @strawberry.mutation
    # @requires_auth  # Assuming this decorator is already defined to handle authentication
    def open_ai_completion(self, info:Info,  chatrequest: ChatRequest) -> ChatResponse:
        try:
            openai_client = OpenAI()  # Assuming OpenAI is your custom class for API interaction
            db = next(get_db())  # Get the database session
            agents = get_prompt_agent(db, chatrequest.filters)  # Retrieve agents based on the provided filters
            if not agents:
                raise HTTPException(status_code=404, detail="No agent found for given filters")

            chat_context = agents[0].__dict__
            context = []

            # Ensure required keys exist
            required_keys = ["agentName", "description", "system", "responseTemplate", "trainingPrompts"]
            for key in required_keys:
                if key not in chat_context:
                    raise HTTPException(status_code=500, detail=f"Missing key in agent context: {key}")

            # Load training prompts safely
            try:
                training_data = json.loads(chat_context["trainingPrompts"])
            except (JSONDecodeError, TypeError):
                raise HTTPException(status_code=500, detail="Invalid or malformed trainingPrompts")

            # Validate training data structure
            if not isinstance(training_data, list):
                raise HTTPException(status_code=500, detail="trainingPrompts must be a list of prompt/response pairs")

            trainer_prompts = []
            for item in training_data:
                if not all(k in item for k in ["userPrompt", "expectedResponse"]):
                    raise HTTPException(status_code=500, detail="Invalid training prompt format")
                trainer_prompts.extend([
                    {"role": "user", "content": item["userPrompt"]},
                    {"role": "assistant", "content": item["expectedResponse"]}
                ])

            # Build context with agent info and training prompts
            context = [
                {"role": "assistant", "content": f"Your name is {chat_context['agentName']}"},
                {"role": "assistant", "content": f"Description: {chat_context['description']}"},
                {"role": "assistant", "content": chat_context["system"]},
                {"role": "assistant", "content": f"You should only respond using the following template:\n\n{chat_context['responseTemplate']}"},
                {"role": "assistant", "content": "Here are some prompt-response examples:"},
                *trainer_prompts
            ]
            # Add user messages to context
            
            try:
                context.extend([m.to_dict() for m in chatrequest.messages])
            except Exception as e:
                raise HTTPException(status_code=422, detail=f"Invalid request messages format: {str(e)}")
            # Call OpenAI's chat completion API
            try:
                response = openai_client.chat_completion(context)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Invalid OpenAI response :{e}")

            # Return the completion response as a ChatResponse
            return ChatResponse(**response)

        except HTTPException as he:
            raise he  # Let FastAPI handle it
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
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
    @list_items(
        model=PromptEngineeredAgent,
        map_to=lambda r: map_model(r, ResponseCreatePromptEngineeredAgent),
        search_fields=["agentName", "description", "system"],
        default_order_by="createdDate",
        responseModel=ListAgentResponse,
        requestModel = ListAgentsRequest
    )
    def list_agents_beta(self, info: Info, request:ListAgentsRequest, data:Optional[ListAgentres]) -> ListAgentResponse:
        return data
    
    @strawberry.field
    @requires_auth
    @get_item_by_id(
        model=PromptEngineeredAgent,
        map_to=lambda r: map_model(r, ResponseCreatePromptEngineeredAgent),
        responseModel=ResponseCreatePromptEngineeredAgent,
        requestModel = AgentRequest
    )
    def agent_by_id(self, info: Info, request:AgentRequest, data:Optional[ListAgentres]) -> ResponseCreatePromptEngineeredAgent:
        return data

