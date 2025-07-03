import requests
import json
import time

# --- 您需要配置的三个关键信息 ---

# 1. 适配器地址 (我们部署在5000端口)
API_URL = "http://127.0.0.1:5000/v1/chat/completions"

# 2. 固定的API Key
API_KEY = "dummy_key"

# 3. 您想要提问的内容和使用的模型
user_prompt = "请用一句话解释什么是人工智能。"
model_to_use = "gpt-3.5-turbo" # 这次我们测试 gpt-3.5-turbo, 它应该映射到 gemini-2.5-flash

# --- 标准的OpenAI API调用逻辑 ---

def call_adapter():
    """发送一个简单的请求来测试适配器"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "gpt-3.5-turbo",  # This will be mapped
        "messages": [
            {"role": "user", "content": "What's the weather like in San Francisco today?"}
        ],
        "stream": False
    }

    print(f"Sending request to {API_URL}...")
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            print("Request successful!")
            result = response.json()
            
            print("---")
            print("Response JSON:")
            print(json.dumps(result, indent=2))
            print("---")

            # Check for content or tool_calls
            message = result.get("choices", [{}])[0].get("message", {})
            if "content" in message and message["content"]:
                print("Model replied with content:")
                print(message["content"])
            elif "tool_calls" in message:
                print("Model replied with a tool call:")
                print(json.dumps(message["tool_calls"], indent=2))
            else:
                print("[WARNING] Model response is empty or in an unexpected format.")
        else:
            print(f"Request failed: {response.status_code} {response.reason}")
            print(response.text)
            exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        exit(1)

if __name__ == "__main__":
    call_adapter() 