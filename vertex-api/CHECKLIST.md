# Google Gemini API 部署检查列表

使用此检查列表来验证您的Google Gemini API配置是否正确。

## 前置条件检查

- [ ] 拥有有效的Google Cloud账户
- [ ] 已创建Google Cloud项目
- [ ] 已启用结算功能（如需要）

## 安装检查

- [ ] Google Cloud SDK安装成功
  ```bash
  gcloud --version  # 应显示版本信息
  ```

- [ ] Python环境准备就绪（3.8+）
  ```bash
  python --version  # 应显示3.8或更高版本
  ```

- [ ] 已安装所需的Python库
  ```bash
  pip list | findstr "google-cloud-aiplatform vertexai google-generativeai"
  ```

## 配置检查

- [ ] Google Cloud SDK已初始化
  ```bash
  gcloud auth list  # 应显示您的账户
  ```

- [ ] 应用默认凭据(ADC)已设置
  ```bash
  # Windows
  echo %APPDATA%\gcloud\application_default_credentials.json
  # 应显示文件路径
  ```

- [ ] Vertex AI API已启用
  - 访问 [API库](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
  - 确认API状态为"已启用"

## 网络检查

- [ ] 可以访问Google服务
  ```bash
  ping www.google.com  # 应能成功ping通
  ```

- [ ] 代理设置（如需要）
  ```bash
  # Windows CMD
  set HTTPS_PROXY=http://127.0.0.1:7890
  
  # Windows PowerShell
  $env:HTTPS_PROXY="http://127.0.0.1:7890"
  ```

## 功能测试

- [ ] 基本连接测试
  ```bash
  python -c "import vertexai; vertexai.init(project='YOUR_PROJECT_ID', location='us-central1'); print('连接成功')"
  # 应输出"连接成功"
  ```

- [ ] 基本模型调用
  ```bash
  python -c "import vertexai; from vertexai.generative_models import GenerativeModel; vertexai.init(project='YOUR_PROJECT_ID', location='us-central1'); model = GenerativeModel('gemini-2.5-pro'); response = model.generate_content('你好'); print(response.text)"
  # 应返回模型回复
  ```

- [ ] 运行综合测试
  ```bash
  python gemini_comprehensive_test.py
  # 至少部分测试应成功
  ```

## 常见问题排查

如果遇到问题，请检查：

1. **网络连接错误**
   - [ ] 确认网络连接正常
   - [ ] 确认代理设置正确
   - [ ] 尝试不同的代理服务器

2. **认证错误**
   - [ ] 重新运行 `gcloud auth application-default login`
   - [ ] 确认项目已启用结算功能
   - [ ] 检查IAM权限设置

3. **模型不可用**
   - [ ] 检查模型ID拼写是否正确
   - [ ] 尝试使用不同的区域
   - [ ] 确认项目已启用Vertex AI API

4. **内容被安全过滤器拦截**
   - [ ] 修改提示词，避免敏感话题
   - [ ] 调整生成参数，如降低temperature值

## 部署完成确认

当您能够成功运行以下测试时，说明部署已完成：

- [ ] 基本文本生成测试成功
- [ ] 聊天会话测试成功
- [ ] 流式输出测试成功

恭喜！您已成功部署Google Gemini API。 