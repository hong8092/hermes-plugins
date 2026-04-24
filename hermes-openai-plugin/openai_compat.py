import os
import yaml
import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "plugin.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "hermes"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7

@router.post("/v1/chat/completions")
async def openai_chat_completions(
    req: ChatRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    api_key = authorization.split(" ")[1]
    valid_keys = config.get("api_keys", [])
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    response_content = await call_hermes_core(req.messages)

    return {
        "id": "chatcmpl-hermes",
        "object": "chat.completion",
        "model": req.model,
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }
        ]
    }

async def call_hermes_core(messages: List[ChatMessage]) -> str:
    hermes_config = config.get("hermes_core", {})
    core_url = hermes_config.get("url", "http://localhost:10101")
    api_path = hermes_config.get("api_path", "/chat")

    async with httpx.AsyncClient(timeout=30.0) as client:
        hermes_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]
        response = await client.post(
            f"{core_url}{api_path}",
            json={"messages": hermes_messages}
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, dict) and "content" in result:
            return result["content"]
        elif isinstance(result, dict) and "response" in result:
            return result["response"]
        elif isinstance(result, str):
            return result
        else:
            return str(result)
