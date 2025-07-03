# Gemini API 测试工具

这个目录包含了用于测试 Google Gemini API 的综合测试脚本。

## 前提条件

1. 已安装 Python 3.8+
2. 已安装必要的依赖包
3. 已完成 Google Cloud 身份验证 (使用 `gcloud auth application-default login`)
4. 如果需要，已配置代理设置

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

### 综合测试

运行所有测试用例：

```bash
python gemini_comprehensive_test.py
```

### 环境变量设置

可以通过设置以下环境变量来配置测试：

- `HTTPS_PROXY`: 设置HTTPS代理 (例如: `http://127.0.0.1:7890`)
- `HTTP_PROXY`: 设置HTTP代理
- `GOOGLE_APPLICATION_CREDENTIALS`: 如果不使用ADC认证，可以指定服务账号密钥文件路径
- `GOOGLE_API_KEY`: 如果要测试直接API密钥方式调用，需要设置此环境变量

## 测试内容

综合测试脚本 `gemini_comprehensive_test.py` 包含以下测试：

1. 使用 Vertex AI SDK 调用 Gemini 2.5 Pro (ADC认证)
2. 使用 Vertex AI SDK 进行对话 (ADC认证)
3. 使用 Vertex AI SDK 设置生成参数 (ADC认证)
4. 使用 Vertex AI SDK 流式输出 (ADC认证)
5. 使用 Google Generative AI Python SDK (API密钥方式)
6. 模型能力测试 - 代码生成
7. 模型能力测试 - 中文理解与生成

## 故障排除

如果遇到连接问题，请检查：

1. 网络连接是否正常
2. 代理设置是否正确
3. 身份验证是否成功
4. 项目是否已启用 Vertex AI API

## 注意事项

- 测试脚本默认使用项目ID `cursor-use-api`，请根据需要修改
- 默认使用区域 `us-central1`，可根据需要修改
- 使用ADC认证方式，确保已通过 `gcloud auth application-default login` 登录 