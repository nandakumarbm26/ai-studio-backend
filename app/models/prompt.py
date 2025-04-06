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

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: str
    # refusal : Any
    # role : Literal["system", "user", "assistant"]
    # annotations : Any
    # audio : Any
    # function_call : Any
    # tool_calls : Any