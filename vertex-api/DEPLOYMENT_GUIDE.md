# Google Gemini API 部署指南

> 版本: 1.0.0 | 更新日期: 2024-07-01

本指南提供了在Windows环境下配置和部署Google Gemini API的详细步骤，包括常见问题及解决方案。

## 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [代码示例](#代码示例)
- [常见问题](#常见问题)
- [测试方法](#测试方法)
- [最佳实践](#最佳实践)

## 系统要求

### 硬件和软件
- **操作系统**: Windows 10/11, Linux, macOS
- **Python**: 3.8 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 2GB 可用空间

### 账户需求
- **Google Cloud 账户**: 需要一个有效的Google Cloud账户 ([注册链接](https://cloud.google.com/))
- **结算功能**: 需要启用结算功能（某些API调用可能会产生费用）

## 安装步骤

### 步骤1: 安装Google Cloud SDK

Google Cloud SDK是与Google Cloud服务交互的命令行工具。

#### Windows安装方法:
1. 下载安装程序: [https://cloud.google.com/sdk/docs/install-sdk#windows](https://cloud.google.com/sdk/docs/install-sdk#windows)
2. 运行安装程序并按照提示操作
3. 选择「不设置默认组件」选项
4. 完成安装后，打开「Google Cloud SDK Shell」

#### Linux安装方法(Debian/Ubuntu):
```bash
sudo apt-get update && sudo apt-get install apt-transport-https ca-certificates gnupg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

**验证安装**:
```bash
gcloud --version
```
应显示Google Cloud SDK的版本信息。

### 步骤2: 初始化Google Cloud SDK

配置SDK并进行身份验证:
```bash
gcloud init
```

这将启动交互式设置过程，引导您完成以下步骤:
1. 登录Google账户（会打开浏览器进行OAuth认证）
2. 选择一个Google Cloud项目
3. 配置默认计算区域和可用区

**验证初始化**:
```bash
gcloud auth list
```
应显示您的Google账户已登录。

### 步骤3: 设置应用默认凭据(ADC)

配置本地开发环境的身份验证凭据:
```bash
gcloud auth application-default login
```

这将打开浏览器进行OAuth认证，并将凭据保存在本地。

**验证凭据设置**:
```bash
# Windows
echo %APPDATA%\gcloud\application_default_credentials.json

# Linux/macOS
echo $HOME/.config/gcloud/application_default_credentials.json
```

应显示凭据文件的路径。这一步创建的凭据文件将被Google Cloud客户端库自动使用。

### 步骤4: 启用必要的API

在Google Cloud Console中启用Vertex AI API:
1. 访问 [https://console.cloud.google.com/apis/library/aiplatform.googleapis.com](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
2. 确保选择了正确的项目
3. 点击「启用」按钮
4. 等待API启用完成

**验证API启用**:
在Google Cloud Console中，Vertex AI API的状态应显示为「已启用」。

### 步骤5: 安装Python依赖

安装必要的Python库:
```bash
pip install google-cloud-aiplatform vertexai google-generativeai requests
```

**验证安装**:
```bash
# Windows
pip list | findstr "google-cloud-aiplatform vertexai google-generativeai"

# Linux/macOS
pip list | grep "google-cloud-aiplatform\|vertexai\|google-generativeai"
```

应显示已安装的库及其版本。

## 配置说明

### 环境变量设置

#### 代理设置
如果您在中国或其他需要代理的地区，可能需要设置代理:

**Windows CMD**:
```cmd
set HTTPS_PROXY=http://127.0.0.1:7890
```

**Windows PowerShell**:
```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
```

**Linux/macOS**:
```bash
export HTTPS_PROXY=http://127.0.0.1:7890
```

> 注意: 将7890替换为您的实际代理端口

#### 凭据设置
默认使用ADC认证，无需设置GOOGLE_APPLICATION_CREDENTIALS变量。如果需要使用服务账号，可以设置GOOGLE_APPLICATION_CREDENTIALS指向JSON密钥文件。

### 项目设置

#### 项目ID
您的Google Cloud项目ID，可在Google Cloud Console的首页或设置中找到，例如: `cursor-use-api`

#### 区域设置
Vertex AI服务的区域，推荐使用: `us-central1`

> 注意: 不同区域可能支持不同的模型，请参考文档

#### 模型选择
可用的Gemini模型:
- **gemini-2.5-pro**: 最强大的Gemini 2.5版本，支持多种复杂任务
- **gemini-1.5-pro**: Gemini 1.5专业版，适合大多数应用场景
- **gemini-1.5-flash**: Gemini 1.5快速版，响应更快但能力略低

## 代码示例

### 基本调用示例
```python
import vertexai
from vertexai.generative_models import GenerativeModel

# 初始化Vertex AI
vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

# 加载模型
model = GenerativeModel("gemini-2.5-pro")

# 发送提示并获取回复
response = model.generate_content("你好，请用中文写一首关于夏天的五言绝句。")
print(response.text)
```

### 聊天会话示例
```python
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

# 初始化Vertex AI
vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

# 加载模型
model = GenerativeModel("gemini-2.5-pro")

# 创建聊天会话
chat = ChatSession(model)

# 发送第一条消息
response = chat.send_message("你好，请介绍一下自己")
print(response.text)

# 发送第二条消息
response = chat.send_message("你能帮我解决什么问题?")
print(response.text)
```

### 流式输出示例
```python
import vertexai
from vertexai.generative_models import GenerativeModel

# 初始化Vertex AI
vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

# 加载模型
model = GenerativeModel("gemini-2.5-pro")

# 流式生成内容
responses = model.generate_content("请用中文写一个关于人工智能的短段落。", stream=True)

# 处理流式响应
for response in responses:
    print(response.text, end="", flush=True)
```

## 常见问题

### 1. 网络连接错误

**错误信息**: `503 failed to connect to all addresses`

**可能原因**:
- 网络连接问题
- 防火墙阻止
- 需要代理但未设置

**解决方案**:
- 检查网络连接是否正常
- 设置HTTPS_PROXY环境变量
- 确认代理服务器是否正常运行
- 尝试使用不同的代理服务器

### 2. 认证错误

**错误信息**: `Unauthorized`

**可能原因**:
- 未完成gcloud auth application-default login
- 凭据已过期
- 项目没有启用结算

**解决方案**:
- 运行 gcloud auth application-default login 重新认证
- 确认项目已启用结算功能
- 检查IAM权限设置

### 3. 模型不可用

**错误信息**: `Publisher Model was not found or your project does not have access to it`

**可能原因**:
- 模型ID拼写错误
- 所选区域不支持该模型
- 项目没有访问该模型的权限

**解决方案**:
- 检查模型ID是否正确
- 尝试使用不同的区域
- 确认项目已启用Vertex AI API
- 检查配额和使用限制

### 4. 内容被安全过滤器拦截

**错误信息**: `Cannot get the response text. Response candidate content has no parts (and thus no text). The candidate is likely blocked by the safety filters.`

**可能原因**:
- 生成的内容触发了安全过滤器
- 提示词可能包含敏感内容

**解决方案**:
- 修改提示词，避免敏感话题
- 调整生成参数，如降低temperature值
- 尝试使用不同的提示词表达方式

## 测试方法

### 基本连接测试
验证API连接和认证是否正常:
```bash
python -c "import vertexai; vertexai.init(project='YOUR_PROJECT_ID', location='us-central1'); print('连接成功')"
```

预期输出: `连接成功`

### 模型可用性测试
验证指定的模型是否可用:
```bash
python gemini_comprehensive_test.py
```

预期输出: 至少有部分测试成功完成

### 综合测试
提供的综合测试脚本 `gemini_comprehensive_test.py` 可测试多种功能，包括基本调用、聊天会话、参数设置、流式输出等。

## 最佳实践

### 使用代理
在中国等地区，设置代理通常是必要的。建议使用稳定的代理服务，并正确设置环境变量。

### 错误处理
添加适当的错误处理代码，捕获并处理可能的异常，提供友好的错误信息。

### 凭据管理
正确管理认证凭据，优先使用ADC认证方式，避免在代码中硬编码凭据。

### 模型选择
根据需求选择合适的模型，对于一般任务，可以使用flash版本；对于复杂任务，使用pro版本。 