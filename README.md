# Vertex AI to OpenAI API Adapter

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个功能齐全、经过全面测试的API适配器，它允许您使用标准的OpenAI API格式和SDK，无缝调用Google的Vertex AI Gemini系列模型。

---

## ✨ 功能特性

- ✅ **完整的API兼容性**: 支持标准的 `/v1/chat/completions` 和 `/v1/models` 端点。
- ✅ **基础与流式对话**: 同时支持非流式和流式的对话模式。流式输出经过优化，按自然的句子/段落分块，而非杂乱的字符。
- ✅ **函数调用 (Function Calling)**: 完全支持流式和非流式的函数调用。
- ✅ **视觉能力 (Vision)**: 支持 `gpt-4-vision-preview` 风格的多模态请求，可处理图像输入。
- ✅ **智能模型映射**: 自动将常见的OpenAI模型名称（如`gpt-4o`, `gpt-3.5-turbo`）映射到指定的Gemini模型。
- ✅ **健壮的错误处理**: 能优雅地捕获和报告来自上游API（如Google安全策略）的错误。

## ⚙️ 环境准备

在开始之前，请确保您的系统（我们已在Windows上成功验证）已安装以下软件：

1.  **Python 3.9+**: [下载地址](https://www.python.org/downloads/)
2.  **Google Cloud CLI**: [安装指南](https://cloud.google.com/sdk/docs/install)
    -   安装后，请运行 `gcloud init` 来初始化CLI并登录您的Google账户。

## 🚀 安装与配置

### 1. 克隆代码库

```bash
git clone https://github.com/dogami567/vertex-01.git
cd vertex-01
```

### 2. 安装Python依赖

我们建议使用虚拟环境来管理项目依赖。

```bash
# 创建虚拟环境 (可选，但推荐)
python -m venv venv

# 激活虚拟环境
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 核心：Google Cloud认证

**这是最关键的一步。** 我们不使用传统的 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量。请按照以下方式进行认证：

1.  运行以下命令，它会打开浏览器让您登录Google账户，并授权应用默认凭据。
    ```bash
    gcloud auth application-default login
    ```
2.  此命令会在您的用户配置文件夹下创建一个 `application_default_credentials.json` 文件，Python客户端库会自动找到并使用它。

### 4. 设置代理 (如果需要)

如果您的网络环境需要代理才能访问Google Cloud，请设置 `HTTPS_PROXY` 环境变量。

```powershell
# Windows (PowerShell)
$env:HTTPS_PROXY="http://127.0.0.1:7890"

# macOS/Linux
export HTTPS_PROXY="http://127.0.0.1:7890"
```

## ▶️ 运行适配器

一切准备就绪后，使用以下命令启动Flask服务器。

> **注意**: 该命令组合了我们所有的最佳实践：临时清空可能存在的旧凭据变量，并设置代理。

```powershell
# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS=""; $env:HTTPS_PROXY="http://127.0.0.1:7890"; python simplest.py

# macOS/Linux
GOOGLE_APPLICATION_CREDENTIALS="" HTTPS_PROXY="http://127.0.0.1:7890" python simplest.py
```

服务器默认在 `http://0.0.0.0:5000` 上运行。

## 🔬 测试

我们提供了一个全面的测试套件来验证所有功能。在启动服务器后，打开一个新的终端并运行：

```bash
python run_all_tests.py
```

您应该能看到所有测试都成功通过的报告。

## 📝 API 使用示例

您可以使用任何兼容OpenAI的客户端库来调用适配器。

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:5000/v1",
    api_key="任何字符串都可以" # API密钥在此适配器中不被校验
)

# 示例：基础对话
response = client.chat.completions.create(
    model="gpt-4o", # 将被映射到 gemini-2.5-pro
    messages=[{"role": "user", "content": "你好，世界！"}]
)
print(response.choices[0].message.content)

# 示例：流式函数调用
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "波士顿现在天气怎么样？请用华氏度。"}],
    tools=[...], # 在此定义您的工具
    stream=True
)
for chunk in stream:
    # 处理您的业务逻辑
    print(chunk)
```

## 🗺️ 模型映射

适配器内部维护一个模型映射表。默认配置如下：

| OpenAI 模型名称         | 映射到的 Vertex AI 模型      |
| ----------------------- | -------------------------- |
| `gpt-4`, `gpt-4-turbo`, `gpt-4o` | `gemini-2.5-pro`           |
| `gpt-3.5-turbo`, `gpt-3.5-turbo-16k` | `gemini-2.5-pro`           |
| `gemini-flash`          | `gemini-2.5-pro`           |
| `gpt-4-vision-preview`  | `gemini-2.5-pro-vision`    |

您可以直接在 `simplest.py` 文件中修改 `MODEL_MAPPING` 字典来自定义映射关系。

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。 