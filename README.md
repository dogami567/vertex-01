# Vertex AI 到 OpenAI API 适配器

这个项目实现了一个简单的适配器，将 Vertex AI API（特别是 Gemini 模型）转换为 OpenAI API 格式。
这允许使用期望 OpenAI API 的工具和服务能够无缝地与 Vertex AI 模型一起使用。

## 特性

- ✅ 将 OpenAI API 请求转换为 Vertex AI 请求
- ✅ 支持流式传输（stream）模式，实现打字机效果
- ✅ 自动映射模型名称（例如 gpt-4o → gemini-2.5-pro）
- ✅ 支持函数调用（Function calling）功能
- ✅ 支持视觉模型（Vision models）功能
- ✅ 简单轻量级设计

## 版本历史

- v0.0.1：基本功能，支持简单对话和流式传输
- v0.0.2：添加函数调用和视觉模型支持

## 模型映射

| OpenAI 模型名称 | Vertex AI 模型名称 |
|---------------|-----------------|
| gpt-4o | gemini-2.5-pro |
| gpt-4-vision-preview | gemini-2.5-pro-vision |
| gpt-4-turbo | gemini-2.5-pro |
| gpt-4 | gemini-2.5-pro |
| gpt-3.5-turbo | gemini-2.5-flash |

## 安装与使用

### 前提条件

1. 设置 Google Cloud 项目
2. 启用 Vertex AI API
3. 设置适当的身份验证

### 使用 Docker

```bash
# 构建 Docker 镜像
docker build -t vertex-openai:v0.0.2 .

# 运行容器
docker run -p 5001:5000 \
  -v /path/to/your/google_credentials.json:/app/credentials.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  vertex-openai:v0.0.2
```

### 手动运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google_credentials.json"

# 在Windows上使用
# $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\google_credentials.json"

# 运行服务
python simplest.py
```

## API 使用示例

### 标准聊天完成（非流式）

```python
import requests
import json

url = "http://localhost:5001/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-test123456789"  # 任意密钥，实际不会验证
}
data = {
    "model": "gpt-4o",  # 将映射到 gemini-2.5-pro
    "messages": [
        {"role": "user", "content": "你好，请介绍一下你自己。"}
    ]
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

### 流式传输聊天完成

```python
import requests
import json

url = "http://localhost:5001/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-test123456789"  # 任意密钥，实际不会验证
}
data = {
    "model": "gpt-4o",  # 将映射到 gemini-2.5-pro
    "messages": [
        {"role": "user", "content": "请用诗歌形式描述春天。"}
    ],
    "stream": True
}

response = requests.post(url, headers=headers, json=data, stream=True)
for line in response.iter_lines():
    if line:
        line_text = line.decode('utf-8')
        if line_text.startswith("data: "):
            content = line_text[6:]
            if content == "[DONE]":
                break
            try:
                chunk = json.loads(content)
                if "choices" in chunk and chunk["choices"]:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        print(delta["content"], end="", flush=True)
            except json.JSONDecodeError:
                pass
```

### 函数调用示例

```python
import requests
import json

url = "http://localhost:5001/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-test123456789"
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取特定位置的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

data = {
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "今天北京的天气怎么样？"}
    ],
    "tools": tools
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 视觉模型示例

```python
import requests
import json
import base64

# 读取图像文件并转换为base64
with open("test_images/test_image.jpg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

url = "http://localhost:5001/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-test123456789"
}

data = {
    "model": "gpt-4-vision-preview",  # 将映射到 gemini-2.5-pro-vision
    "messages": [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "这张图片里有什么内容？请详细描述。"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 测试脚本

项目包含多个测试脚本，用于验证适配器的各种功能：

- `test_client.py`：测试基本的聊天功能
- `test_vertexai_direct.py`：直接测试Vertex AI API
- `test_function_calling.py`：测试函数调用功能
- `test_vision.py`：测试视觉模型功能
- `run_all_tests.py`：运行所有测试

要运行测试，请确保适配器正在运行，然后执行：

```bash
python run_all_tests.py
```

## 限制

- 目前仅支持基本的聊天完成功能
- 令牌计数是估算的，不精确
- 不支持嵌入（embeddings）或编辑功能

## 许可证

MIT

## 贡献

欢迎提交PR和问题报告！ 