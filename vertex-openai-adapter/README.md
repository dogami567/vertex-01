# Vertex AI 到 OpenAI API 适配器

这个项目实现了一个简单的适配器，将 Vertex AI API（特别是 Gemini 模型）转换为 OpenAI API 格式。
这允许使用期望 OpenAI API 的工具和服务能够无缝地与 Vertex AI 模型一起使用。

## 特性

- ✅ 将 OpenAI API 请求转换为 Vertex AI 请求
- ✅ 支持流式传输（stream）模式，实现打字机效果
- ✅ 自动映射模型名称（例如 gpt-4o → gemini-2.5-pro）
- ✅ 支持函数调用（Function calling）功能
- ✅ 支持视觉模型（Vision models）功能
- ✅ **(更新)** 支持联网搜索（通过函数调用实现，使用`-search`后缀触发）

## 版本历史

- v0.0.1：基本功能，支持简单对话和流式传输
- v0.0.2：添加函数调用和视觉模型支持
- v0.0.3：增加联网搜索功能（使用function calling实现），并修复Windows环境下的代理连接问题

## 模型映射

| OpenAI 模型名称 | Vertex AI 模型名称 |
|-----------------|-----------------|
| gpt-4o | gemini-2.5-pro |
| gpt-4o-search | gemini-2.5-pro (带函数调用搜索) |
| gpt-4-vision-preview | gemini-2.5-pro-vision |
| gpt-4-turbo | gemini-2.5-pro |
| gpt-4 | gemini-2.5-pro |
| gpt-3.5-turbo | gemini-2.5-flash |
| gpt-3.5-turbo-search | gemini-2.5-flash (带函数调用搜索) |

## 安装与使用

### 前提条件

1.  Python 3.8+
2.  设置 Google Cloud 项目
3.  启用 Vertex AI API
4.  设置适当的身份验证（推荐使用 `gcloud auth application-default login`）

### 使用 Docker

```bash
# 构建 Docker 镜像
docker build -t vertex-openai:v0.0.3 .

# 运行容器
docker run -p 5000:5000 \
  -v /path/to/your/google_credentials.json:/app/credentials.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  vertex-openai:v0.0.3
```

### 手动运行

1.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

2.  **设置认证**
    推荐在您的终端运行此命令，它会自动处理好认证事宜：
    ```bash
    gcloud auth application-default login
    ```

3.  **设置环境变量（关键步骤！）**

    **Windows (PowerShell):**
    在运行服务前，**必须**设置代理。请根据您的代理软件端口修改。
    ```powershell
    # 设置代理并运行服务
    $env:HTTPS_PROXY="http://127.0.0.1:7890"; python simplest.py
    ```

    **Linux / macOS:**
    ```bash
    export HTTPS_PROXY="http://127.0.0.1:7890"
    python simplest.py
    ```
    
    > **为什么需要代理?**
    > 在某些网络环境中，直接访问 Google Cloud API 可能会失败。设置此环境变量可以确保Python脚本通过您本地的网络代理进行连接，从而解决 `503 failed to connect` 等网络问题。

4.  **运行服务**
    ```bash
    python simplest.py
    ```
    服务默认运行在 `http://localhost:5000`。

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

### 联网搜索示例

要使用联网搜索功能，只需在请求的模型名称后添加 `-search` 后缀。系统将自动为模型添加搜索函数定义，并通过函数调用机制实现联网搜索能力。

```python
import requests
import json
import time
from googlesearch import search

url = "http://localhost:5000/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-any-key"
}

# 第1步：发送初始请求
data = {
    "model": "gpt-4o-search",  # 使用-search后缀触发搜索功能
    "messages": [
        {"role": "user", "content": "2024年欧洲杯的冠军是哪支球队？"}
    ]
}

# 确保在运行此脚本的终端也设置了代理
# export HTTPS_PROXY="http://127.0.0.1:7890"

response = requests.post(url, headers=headers, json=data).json()

# 检查是否有函数调用请求
if "choices" in response and response["choices"][0]["message"].get("tool_calls"):
    tool_call = response["choices"][0]["message"]["tool_calls"][0]
    if tool_call["function"]["name"] == "search_on_web":
        # 解析搜索查询
        args = json.loads(tool_call["function"]["arguments"])
        query = args.get("query", "")
        
        # 执行实际搜索（需要安装 google 库）
        results = []
        for url in search(query, stop=3):
            results.append(url)
            
        # 构建搜索结果
        search_result = {
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 第2步：发送带有搜索结果的后续请求
        follow_up_data = {
            "model": "gpt-4o-search",
            "messages": [
                {"role": "user", "content": "2024年欧洲杯的冠军是哪支球队？"},
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": "search_on_web",
                    "content": json.dumps(search_result)
                }
            ]
        }
        
        final_response = requests.post(url, headers=headers, json=follow_up_data).json()
        print(json.dumps(final_response, indent=2, ensure_ascii=False))
else:
    print(json.dumps(response, indent=2, ensure_ascii=False))
```

## 测试脚本

项目包含多个测试脚本，用于验证适配器的各种功能：

- `test_client.py`：测试基本的聊天功能
- `test_vertexai_direct.py`：直接测试Vertex AI API
- `test_function_calling.py`：测试函数调用功能
- `test_vision.py`：测试视觉模型功能
- `test_function_search.py`: 测试基于函数调用的联网搜索功能
- `run_all_tests.py`：运行所有测试

要运行测试，请确保适配器正在运行，然后在一个**同样设置了代理**的终端中执行：

```bash
# Windows (PowerShell)
$env:HTTPS_PROXY="http://127.0.0.1:7890"; python test_function_search.py

# Linux / macOS
export HTTPS_PROXY="http://127.0.0.1:7890"
python test_function_search.py
```

## 限制

- 目前仅支持基本的聊天完成功能
- 令牌计数是估算的，不精确
- 不支持嵌入（embeddings）或编辑功能

## 许可证

MIT

## 贡献

欢迎提交PR和问题报告！ 