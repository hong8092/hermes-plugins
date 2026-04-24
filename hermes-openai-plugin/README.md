# Hermes OpenAI 兼容插件

让 Hermes 支持标准大模型 API 格式（BASE_URL + API_KEY），作为纯插件形式，无需修改 Hermes 内核。

## 目录结构

```
hermes-openai-plugin/
├── plugin.yaml       # 配置文件
├── __init__.py       # 插件初始化
├── main.py           # 主入口
├── openai_compat.py  # 业务逻辑
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
  name: hermes-openai-plugin
  version: 1.0.0

api_keys:
  - sk-hermes-1234567890

hermes_core:
  url: http://localhost:10101
  api_path: /chat

server:
  host: 0.0.0.0
  port: 10101
```

## 集成到 Hermes 项目

在你的 Hermes 主程序中添加：

```python
from hermes_openai_plugin import app

# 挂载插件路由
# 你的现有代码...
```

## 启动

```bash
cd hermes-openai-plugin
python main.py
```

## API 调用

```bash
curl -X POST http://localhost:10101/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-hermes-1234567890" \
  -d '{"model": "hermes", "messages": [{"role": "user", "content": "你好！"}]}'
```

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| api_keys | API Key 列表 | sk-hermes-1234567890 |
| hermes_core.url | Hermes 内核地址 | http://localhost:10101 |
| hermes_core.api_path | Hermes 内核路径 | /chat |
| server.host | 服务监听地址 | 0.0.0.0 |
| server.port | 服务监听端口 | 10101 |
