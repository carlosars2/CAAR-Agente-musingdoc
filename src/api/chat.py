from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.agent.chain import agent_chain

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required")

    response = await agent_chain.chat(
        session_id=request.session_id,
        message=request.message,
    )

    return ChatResponse(
        response=response,
        session_id=request.session_id,
    )
