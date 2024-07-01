from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid


class ChatHeaders(BaseModel):
    pass


class ChatModel(BaseModel):
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique session ID")
    prompt: str

    @field_validator("session_id", mode="after")
    def default_session_id(cls, v):
        if not v:
            return str(uuid.uuid4())
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "prompt": "What are the tax implications of selling property in India?"
            }
        }


class ChatResponse(BaseModel):
    pass
