# Vertex AI 到 OpenAI API 适配器

这个项目实现了一个简单的API适配器，将Vertex AI的API转换为OpenAI格式的API。这使得原本使用OpenAI API的应用程序可以无缝地切换到Vertex AI，而无需修改代码。

## 功能特点

- 支持OpenAI风格的API端点 `/v1/chat/completions`
- 支持模型列表查询 `/v1/models`
- 提供简单的API密钥验证机制
- 将OpenAI格式的请求转换为Vertex AI格式
- 将Vertex AI的响应转换回OpenAI格式

## 模型映射

适配器将OpenAI的模型名称映射到Vertex AI的模型:

- `gpt-3.5-turbo` → `gemini-1.5-pro`
- `gpt-4` → `gemini-2.5-pro`
- `gpt-4o` → `gemini-2.5-pro`

## 安装和设置

1. 克隆此仓库:

```bash
git clone https://github.com/yourusername/vertex-openai-adapter.git
cd vertex-openai-adapter
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 配置Vertex AI认证:

- 配置您的Google Cloud凭据 (您需要安装并配置 [gcloud CLI](https://cloud.google.com/sdk/docs/install))
- 导出GOOGLE_APPLICATION_CREDENTIALS环境变量:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
```

4. 在`simplest.py`文件中修改:
   - `PROJECT_ID`: 您的Google Cloud项目ID
   - `LOCATION`: Vertex AI服务区域
   - `API_KEY`: 您自定义的API密钥

## 运行适配器

启动适配器服务器:

```bash
python simplest.py
```

默认情况下，服务器将在`http://localhost:5000`上运行。

## 使用示例

使用`test_client.py`测试适配器:

```bash
python test_client.py "这是一个测试问题"
```

通过API调用:

```python
import requests

API_BASE = "http://localhost:5000"
API_KEY = "sk-test123456789"  # 替换为您设置的API密钥

response = requests.post(
    f"{API_BASE}/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "你是一个乐于助人的AI助手。"},
            {"role": "user", "content": "介绍一下北京的历史"}
        ]
    }
)

print(response.json())
```

## 限制

这个适配器是一个简化版本，有以下限制:

- 不支持流式输出
- 不支持函数调用
- 不支持多轮对话上下文管理
- Token计数是近似值

## 扩展

您可以扩展此适配器以支持:

- 流式输出 (使用Flask的响应流)
- 函数调用
- 完整的对话历史管理
- 精确的Token计数

## 许可证

MIT 