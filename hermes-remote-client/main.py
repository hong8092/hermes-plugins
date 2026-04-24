import os
import yaml
from fastapi import FastAPI
from .client_compat import router

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "plugin.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

app = FastAPI(
    title="Hermes Remote Client Plugin",
    description="Hermes 远程客户端插件，连接局域网或外网的服务端程序",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hermes Remote Client Plugin is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/config")
async def get_config():
    return {"servers": list(config.get("servers", {}).keys())}

if __name__ == "__main__":
    import uvicorn
    server_config = config.get("server", {})
    uvicorn.run(
        app,
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 10102)
    )
