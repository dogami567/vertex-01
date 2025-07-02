# Vertex AI to OpenAI API Adapter

This project provides a lightweight adapter to convert OpenAI API requests to Google's Vertex AI API. It allows you to use OpenAI-compatible clients and libraries with Google's powerful Generative Models (like Gemini) without any code changes on the client side.

This adapter is implemented in Python using the Flask framework.

## ✨ Features

- 🔄 **Protocol Translation**: Translates OpenAI Chat Completions API requests to Vertex AI `generate_content` format.
- 🚀 **Model Mapping**: Maps common OpenAI model names (e.g., `gpt-4`, `gpt-3.5-turbo`) to specified Vertex AI models (e.g., `gemini-2.5-pro`).
- 💬 **Basic Chat**: Supports standard request/response chat.
- 🌊 **Streaming**: Supports real-time streaming of responses.
- 🛠️ **Function Calling**: Supports OpenAI's function calling/tools format.
- 👁️ **Vision Support**: Supports multimodal requests with images (both URL and base64 encoded).
- models-listing **Models Listing**: Provides an endpoint (`/v1/models`) that lists available models, ensuring compatibility with clients that perform this check.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python**: Version 3.8 or higher.
2.  **Google Cloud SDK**: The `gcloud` command-line tool. You can install it from [here](https://cloud.google.com/sdk/docs/install).
3.  **pip**: Python's package installer.

## ⚙️ Setup & Deployment

Follow these steps to get the adapter up and running.

### 1. Clone the Repository

Clone this project to your local machine.

```bash
# This step is assumed to be done.
# git clone <your-repository-url>
# cd vertex-openai-adapter
```

### 2. Install Dependencies

Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

### 3. Authenticate with Google Cloud

You need to authenticate your environment to allow the adapter to make calls to the Vertex AI API. The recommended way is to use Application Default Credentials (ADC).

Run the following command and follow the instructions to log in with your Google account:

```bash
gcloud auth application-default login
```

This will store your credentials in a local file that the Vertex AI SDK can automatically find.

### 4. Configure Environment (Optional)

The adapter can be configured via environment variables.

-   `PROJECT_ID`: Your Google Cloud Project ID. Defaults to `cursor-use-api`.
-   `LOCATION`: The Google Cloud region for Vertex AI. Defaults to `us-central1`.
-   `HTTPS_PROXY`: If you are in a restricted network environment, you may need to set a proxy. Example: `http://127.0.0.1:7890`.

### 5. Run the Adapter

Start the Flask server. The following command ensures that any potentially incorrect global `GOOGLE_APPLICATION_CREDENTIALS` variable is ignored (preferring the ADC from step 3) and sets a proxy if you need one.

**On Windows (PowerShell):**

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS=""; $env:HTTPS_PROXY="http://127.0.0.1:7890"; python simplest.py
```

**On Linux/macOS:**

```bash
GOOGLE_APPLICATION_CREDENTIALS="" HTTPS_PROXY="http://127.0.0.1:7890" python simplest.py
```

The server will start on `http://127.0.0.1:5000` by default.

## 🔌 Usage

Once the server is running, you can configure your OpenAI-compatible client to use it.

-   **API Base URL / Endpoint**: `http://127.0.0.1:5000/v1`
    *(Note: Some clients may require you to enter `http://127.0.0.1:5000` and they will add the `/v1` suffix automatically.)*
-   **API Key**: Any string will work (e.g., `sk-12345`). The adapter does not validate it.
-   **Model**: Use any of the model names mapped in the script, such as `gpt-4`, `gpt-4-turbo`, or `gpt-4o`.

You can now send requests from your client, and they will be processed by Vertex AI's Gemini model.

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