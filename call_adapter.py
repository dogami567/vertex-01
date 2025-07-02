import requests
import json

# --- 您需要配置的三个关键信息 ---

# 1. 适配器地址 (我们部署在5001端口)
ADAPTER_URL = "http://127.0.0.1:5001/v1/chat/completions"

# 2. 固定的API Key
API_KEY = "sk-test123456789"

# 3. 您想要提问的内容和使用的模型
user_prompt = "请用一句话解释什么是人工智能。"
model_to_use = "gpt-3.5-turbo" # 这次我们测试 gpt-3.5-turbo, 它应该映射到 gemini-2.5-flash

# --- 标准的OpenAI API调用逻辑 ---

# 设置请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 构造请求体
payload = {
    "model": model_to_use,
    "messages": [
        {"role": "user", "content": user_prompt}
    ]
}

print(f"正在向 {ADAPTER_URL} 发送请求...")
# 发送POST请求
try:
    response = requests.post(ADAPTER_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()  # 检查请求是否成功

    # 解析并打印响应
    result = response.json()
    print("请求成功！")
    print("---")
    print("模型回复内容:")
    print(result["choices"][0]["message"]["content"])
    print("---")

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}") 