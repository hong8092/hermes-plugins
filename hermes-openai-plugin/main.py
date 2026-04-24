import os
import yaml
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .openai_compat import router

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "plugin.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

app = FastAPI(
    title="Hermes OpenAI Plugin",
    description="让 Hermes 支持标准大模型 API 格式",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hermes OpenAI Plugin is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    server_config = config.get("server", {})
    uvicorn.run(
        app,
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 10101)
    )
