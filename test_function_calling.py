#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Vertex AI到OpenAI适配器的函数调用功能
"""

import os
import json
import requests
import time
import argparse

# 设置环境变量
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 测试配置
API_URL = "http://localhost:5000/v1"  # 本地适配器地址
API_KEY = "sk-test123456789"  # 测试用API密钥

def print_result(test_name, success, duration, details=""):
    """打印测试结果"""
    status = "[SUCCESS]" if success else "[FAILURE]"
    print("-" * 60)
    print(f"Test: {test_name}")
    print(f"Status: {status}")
    print(f"Duration: {duration:.2f}s")
    if details:
        print(f"Details: {details}")
    print("-" * 60)

# 测试函数调用
def test_function_calling(stream=False):
    """测试基本的函数调用功能"""
    
    test_name = "Function Calling (Streaming)" if stream else "Function Calling (Non-streaming)"
    print(f"\n{'='*20} {test_name} {'='*20}\n")
    
    # 定义函数架构
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The unit of temperature"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    # 创建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "gpt-4o",
        "messages": [{
            "role": "user", 
            "content": "What's the weather like in Boston, MA? Please use fahrenheit."
        }],
        "tools": tools,
        "stream": stream
    }
    
    start_time = time.time()
    success = False
    details = ""

    try:
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=data, stream=stream)
        
        if response.status_code != 200:
            details = f"Request failed with status {response.status_code}: {response.text}"
        elif stream:
            # Handle streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data:"):
                        content = line_str[5:].strip()
                        if content == "[DONE]":
                            break
                        chunk = json.loads(content)
                        tool_calls = chunk.get("choices", [{}])[0].get("delta", {}).get("tool_calls")
                        if tool_calls and tool_calls[0].get("function", {}).get("name") == "get_weather":
                            success = True
                            details = "Streamed function call received correctly."
                            break
            if not success:
                details = "Stream ended without a valid function call."
        else:
            # Handle non-streaming response
            result = response.json()
            message = result.get("choices", [{}])[0].get("message", {})
            if "tool_calls" in message:
                tool_call = message["tool_calls"][0]
                if tool_call.get("function", {}).get("name") == "get_weather":
                    success = True
                    details = f"Function call returned: {tool_call['function']['name']}"
                else:
                    details = f"Incorrect function name in tool call: {result}"
            else:
                details = f"Did not receive correct tool call. Response: {result}"

    except Exception as e:
        details = f"An exception occurred: {e}"

    end_time = time.time()
    print_result(test_name, success, end_time - start_time, details)
    return success

# 主函数
def main():
    parser = argparse.ArgumentParser(description="Test function calling.")
    parser.add_argument("--stream", action="store_true", help="Enable stream mode.")
    args = parser.parse_args()

    if not test_function_calling(stream=args.stream):
        exit(1)

if __name__ == "__main__":
    main() 