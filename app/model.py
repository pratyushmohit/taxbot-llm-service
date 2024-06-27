from pydantic import BaseModel


class ChatHeaders(BaseModel):
    pass


class ChatModel(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    pass
