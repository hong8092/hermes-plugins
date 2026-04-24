# Hermes 远程客户端插件

Hermes 远程客户端插件，用于连接局域网或外网的服务端程序，作为中间层代理。

## 功能特性

- 支持多个服务端配置（本地、开发、生产）
- 标准 OpenAI 格式 API 接口
- 自动重试机制
- 服务端健康检查
- 可通过配置文件灵活管理

## 目录结构

```
hermes-remote-client/
├── plugin.yaml       # 配置文件
├── __init__.py       # 插件初始化
├── main.py           # 主入口
├── client_compat.py  # 业务逻辑
└── README.md         # 说明文档
```

## 安装依赖

```bash
pip install fastapi uvicorn pyyaml httpx
```

## 配置

编辑 `plugin.yaml` 文件：

```yaml
plugin:
  name: hermes-remote-client
  version: 1.0.0

servers:
  default:  # 本地服务
    url: http://localhost:10101
    api_path: /v1/chat/completions
    api_key: sk-hermes-1234567890
  dev:      # 开发环境
    url: http://192.168.1.100:10101
    api_path: /v1/chat/completions
    api_key: sk-hermes-dev-123456
  prod:     # 生产环境
    url: https://api.example.com
    api_path: /v1/chat/completions
    api_key: sk-hermes-prod-789012

client:
  timeout: 30    # 请求超时时间（秒）
  retries: 3     # 重试次数
  retry_delay: 1 # 重试延迟（秒）

api_keys:
  - sk-hermes-client-1234567890
  - sk-hermes-client-0987654321

server:
  host: 0.0.0.0
  port: 10102

defaults:
  model: gpt-3.5-turbo
  temperature: 0.7
  stream: false
  server: default
```

## 启动

```bash
cd hermes-remote-client
python main.py
```

服务将在 `http://0.0.0.0:10102` 运行。

## API 接口

### 1. 聊天完成接口

**请求：**
```bash
curl -X POST http://localhost:10102/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-hermes-client-1234567890" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好！"}],
    "server": "default"
  }'
```

**参数说明：**
- `model`: 模型名称
- `messages`: 消息列表
- `server`: 服务端名称（default、dev、prod）
- `temperature`: 温度参数
- `stream`: 是否流式输出

### 2. 服务端列表

**请求：**
```bash
curl http://localhost:10102/v1/servers
```

**响应：**
```json
{
  "servers": [
    {
      "name": "default",
      "url": "http://localhost:10101",
      "api_path": "/v1/chat/completions"
    }
  ]
}
```

### 3. 服务端健康检查

**请求：**
```bash
curl "http://localhost:10102/v1/servers/test?server_name=default"
```

**响应：**
```json
{
  "status": "ok",
  "server": "default",
  "response": {"status": "healthy"}
}
```

### 4. 健康检查

**请求：**
```bash
curl http://localhost:10102/health
```

**响应：**
```json
{"status": "healthy"}
```

### 5. 配置信息

**请求：**
```bash
curl http://localhost:10102/config
```

**响应：**
```json
{"servers": ["default", "dev", "prod"]}
```

## 集成到 Hermes 项目

在你的 Hermes 主程序中添加：

```python
from hermes_remote_client import app

# 挂载插件路由
# 你的现有代码...
```

## 故障排查

### 常见问题

1. **连接超时**
   - 检查服务端地址是否正确
   - 检查网络连接是否正常
   - 调整 `client.timeout` 配置

2. **API Key 错误**
   - 检查服务端的 API Key 是否正确
   - 检查客户端的 API Key 是否在 `api_keys` 列表中

3. **服务端未响应**
   - 检查服务端是否正在运行
   - 使用 `/v1/servers/test` 接口测试连接

4. **配置错误**
   - 检查 `plugin.yaml` 文件格式是否正确
   - 确保所有必要的配置项都已填写

## 版本信息

- 版本：1.0.0
- 更新日期：2026-04-25
- 作者：Hermes Team
