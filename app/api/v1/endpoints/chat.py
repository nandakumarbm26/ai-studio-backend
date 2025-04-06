

from fastapi import APIRouter, HTTPException
from app.lib.openai_wrapper import OpenAI
from app.models.prompt import ChatRequest, ChatResponse

router = APIRouter()
openai_client = OpenAI()


print("chat router loaded")
@router.post("/", response_model=ChatResponse)
def chat_with_openai(request: ChatRequest):
    try:

        payload = [m.dict() for m in request.messages]


        response = openai_client.chat_completion(payload)

        if not response:
            raise HTTPException(status_code=500, detail="OpenAI response error")

        return ChatResponse(response=response)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
