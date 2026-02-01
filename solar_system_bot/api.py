# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from main import get_bot_reply  # reuse your existing chatbot logic

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    reply = get_bot_reply(payload.message)
    return ChatResponse(reply=reply)
