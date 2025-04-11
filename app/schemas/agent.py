from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Literal, Union, List, Optional
from typing import Union, Dict, List, Literal, Any

class Text(BaseModel):
    type: Literal["text"]
    text: str


class Image(BaseModel):
    type: Literal["image_url"]
    image_url: dict  # Can define URL validation if needed


# One content item can be either text or image_url
Content = Union[Text, Image]


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: Union[str, Dict[str, Any], List[Any]]

class PromptAgentQueryRequest(BaseModel):
    id: Optional[int] = None
    agentName: Optional[str] = None
    system: Optional[str] = None
    s: Optional[str] = None
    
class ChatRequest(BaseModel):
    messages: List[Message]
    filters : PromptAgentQueryRequest 



class ChatResponse(BaseModel):
    response: str
    # refusal : Any
    # role : Literal["system", "user", "assistant"]
    # annotations : Any
    # audio : Any
    # function_call : Any
    # tool_calls : Any
    
class TrainingPrompt(BaseModel):
    userPrompt: str
    expectedResponse: str

class CreatePromptEngineeredAgent(BaseModel):
    agentName: str
    description: str
    system: str
    responseTemplate: str
    trainingPrompts: List[TrainingPrompt]

class UpdatePromptEngineeredAgent(BaseModel):
    agentName: Optional[str] = None
    description: Optional[str] = None
    system: Optional[str] = None
    responseTemplate: Optional[str] = None
    trainingPrompts: Optional[List[TrainingPrompt]] = None

class ResponsePromptAgentContext(Message):
    agentName:str
    agentDescription:str
    

class ResponseCreatePromptEngineeredAgent(UpdatePromptEngineeredAgent):
    id:int
    trainingPrompts:Optional[str] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None
    class Config:
        orm_mode = True