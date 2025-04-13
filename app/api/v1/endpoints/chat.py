from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.agent import ChatRequest, ChatResponse
from app.api.v1.endpoints.agent import read_all
from app.lib.openai_wrapper import OpenAI
import json
from json.decoder import JSONDecodeError

router = APIRouter()
openai_client = OpenAI()


@router.post("/", response_model=ChatResponse)
def chat_with_openai(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        agents = read_all(filters=request.filters, db=db)

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

        # Build context
        context = [
            {"role": "assistant", "content": f"Your name is {chat_context['agentName']}"},
            {"role": "assistant", "content": f"Description: {chat_context['description']}"},
            {"role": "assistant", "content": chat_context["system"]},
            {"role": "assistant", "content": f"You should only respond using the following template:\n\n{chat_context['responseTemplate']}"},
            {"role": "assistant", "content": "Here are some prompt-response examples:"},
            *trainer_prompts
        ]

        # Add user messages
        try:
            context.extend([m.dict() for m in request.messages])
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid request messages format: {str(e)}")

        # Call OpenAI
        response = openai_client.chat_completion(context)

        if not response or not isinstance(response, str):
            raise HTTPException(status_code=500, detail="Invalid OpenAI response")

        return ChatResponse(response=response)

    except HTTPException as he:
        raise he  # Let FastAPI handle it
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
