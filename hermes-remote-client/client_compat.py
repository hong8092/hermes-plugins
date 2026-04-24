import os
import yaml
import httpx
import asyncio
from fastapi import APIRouter, Header, HTTPException, Query
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
    model: str = "gpt-3.5-turbo"
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    server: Optional[str] = "default"

class RemoteClient:
    def __init__(self):
        self.clients = {}
        self.client_config = config.get("client", {})
        self.timeout = self.client_config.get("timeout", 30)
        self.retries = self.client_config.get("retries", 3)
        self.retry_delay = self.client_config.get("retry_delay", 1)

    def get_server_config(self, server_name):
        servers = config.get("servers", {})
        if server_name not in servers:
            raise HTTPException(status_code=400, detail=f"Server '{server_name}' not configured")
        return servers[server_name]

    async def send_request(self, server_name, payload):
        server_config = self.get_server_config(server_name)
        url = f"{server_config['url']}{server_config['api_path']}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {server_config['api_key']}"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.retries):
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    return response.json()
                except httpx.RequestError as e:
                    if attempt == self.retries - 1:
                        raise HTTPException(status_code=503, detail=f"Failed to connect to server: {str(e)}")
                    await asyncio.sleep(self.retry_delay)
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

remote_client = RemoteClient()

@router.post("/v1/chat/completions")
async def remote_chat_completions(
    req: ChatRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    api_key = authorization.split(" ")[1]
    valid_keys = config.get("api_keys", [])
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    payload = {
        "model": req.model,
        "messages": [msg.dict() for msg in req.messages],
        "stream": req.stream,
        "temperature": req.temperature
    }

    response = await remote_client.send_request(req.server, payload)
    return response

@router.get("/v1/servers")
async def list_servers():
    servers = config.get("servers", {})
    return {
        "servers": [
            {
                "name": name,
                "url": server["url"],
                "api_path": server["api_path"]
            }
            for name, server in servers.items()
        ]
    }

@router.post("/v1/servers/test")
async def test_server(
    server_name: str = Query(..., description="Server name to test")
):
    try:
        server_config = remote_client.get_server_config(server_name)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{server_config['url']}/health")
            response.raise_for_status()
            return {"status": "ok", "server": server_name, "response": response.json()}
    except Exception as e:
        return {"status": "error", "server": server_name, "message": str(e)}
