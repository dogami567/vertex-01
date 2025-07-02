#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
综合测试脚本 - 测试Vertex AI适配器的所有功能
"""

import os
import json
import time
import base64
import requests
import argparse

# 设置环境变量
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 测试配置
API_URL = "http://localhost:5000/v1"
API_KEY = "sk-test123456789"
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'test_images', 'test_image.jpg')

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50 + "\n")

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

def test_models_endpoint():
    """测试模型列表端点"""
    print_header("测试模型列表端点")
    
    start_time = time.time()
    
    try:
        print("正在获取模型列表...")
        
        response = requests.get(
            f"{API_URL}/models",
            headers={
                "Authorization": f"Bearer {API_KEY}"
            }
        )
    
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            model_names = [model.get("id") for model in models]
            
            print("\n可用模型:")
            print("-" * 40)
            print(f"{'模型ID':<20} | {'对应Vertex AI模型':<20}")
            print("-" * 40)
            
            for model in models:
                print(f"{model.get('id'):<20} | {model.get('object', ''):<20}")
            
            print("-" * 40 + "\n")
            
            print_result(
                "模型列表端点",
                True,
                end_time - start_time
            )
            return True
        else:
            print_result(
                "模型列表端点",
                False,
                end_time - start_time
            )
            return False
    
    except Exception as e:
        end_time = time.time()
        print_result(
            "模型列表端点",
            False,
            end_time - start_time
        )
        return False

def test_basic_chat():
    """测试基本的非流式对话功能"""
    test_name = "Basic Chat (Non-streaming)"
    print(f"\n{'='*20} {test_name} {'='*20}\n")
    start_time = time.time()
    success = False
    details = ""

    try:
        data = {
            "model": "gemini-2.5-pro",
            "messages": [{"role": "user", "content": "Hello! Can you tell me a joke?"}],
            "stream": False
        }
        response = requests.post(f"{API_URL}/chat/completions", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"][0]["message"]["content"]:
                success = True
                details = f"Response: {result['choices'][0]['message']['content'][:50]}..."
            else:
                details = f"Invalid response format: {result}"
        else:
            details = f"Request failed with status {response.status_code}: {response.text}"
            
    except Exception as e:
        details = f"An exception occurred: {e}"

    end_time = time.time()
    print_result(test_name, success, end_time - start_time, details)
    return success

def test_streaming_chat():
    """测试流式对话功能"""
    test_name = "Streaming Chat"
    print(f"\n{'='*20} {test_name} {'='*20}\n")
    start_time = time.time()
    success = False
    details = ""
    full_response = ""
    
    try:
        data = {
            "model": "gemini-2.5-pro",
            "messages": [{"role": "user", "content": "Write a short story about a robot who discovers music."}],
            "stream": True
        }
        response = requests.post(f"{API_URL}/chat/completions", json=data, stream=True)
        
        if response.status_code == 200:
            print("流式响应开始传输...\n")
            chunk_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data:"):
                        content = line_str[5:].strip()
                        if content == "[DONE]":
                            print("\n[DONE] 流式传输结束")
                            break
                        
                        chunk = json.loads(content)
                        chunk_count += 1
                        
                        if "choices" in chunk and chunk["choices"][0]["delta"].get("content"):
                            chunk_text = chunk["choices"][0]["delta"]["content"]
                            full_response += chunk_text
                            print(f"块 #{chunk_count} (长度: {len(chunk_text)}): {chunk_text}")
            
            if len(full_response) > 50:
                success = True
                details = f"Streamed response received, length: {len(full_response)}. Total chunks: {chunk_count}"
            else:
                details = f"Streamed response was too short or empty. Length: {len(full_response)}"
        else:
            details = f"Request failed with status {response.status_code}: {response.text}"

    except Exception as e:
        details = f"An exception occurred: {e}"

    end_time = time.time()
    print_result(test_name, success, end_time - start_time, details)
    return success

def test_vision():
    """测试视觉功能"""
    test_name = "Vision"
    print(f"\n{'='*20} {test_name} {'='*20}\n")
    start_time = time.time()
    success = False
    details = ""

    try:
        with open(IMAGE_PATH, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        data = {
            "model": "gemini-2.5-pro-vision",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "stream": False
        }
        response = requests.post(f"{API_URL}/chat/completions", json=data)

        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content and "error" not in content.lower():
                success = True
                details = f"Vision model responded. Length: {len(content)}"
            else:
                details = f"Vision model returned an error or empty content: {content}"
        else:
            details = f"Request failed with status {response.status_code}: {response.text}"

    except Exception as e:
        details = f"An exception occurred: {e}"

    end_time = time.time()
    print_result(test_name, success, end_time - start_time, details)
    return success

def test_function_calling():
    """测试函数调用功能"""
    test_name = "Function Calling (Non-streaming)"
    print(f"\n{'='*20} {test_name} {'='*20}\n")
    start_time = time.time()
    success = False
    details = ""

    try:
        tools = [{"type": "function", "function": {"name": "get_weather", "description": "Get weather", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}}}]
        data = {"model": "gemini-2.5-pro", "messages": [{"role": "user", "content": "What's the weather in London?"}], "tools": tools}
        response = requests.post(f"{API_URL}/chat/completions", json=data)
        
        if response.status_code == 200:
            result = response.json()
            tool_calls = result.get("choices", [{}])[0].get("message", {}).get("tool_calls")
            if tool_calls and tool_calls[0].get("function", {}).get("name") == "get_weather":
                success = True
                details = f"Function call returned: {tool_calls[0]['function']['name']}"
            else:
                details = f"Did not receive correct tool call. Response: {result}"
        else:
            details = f"Request failed with status {response.status_code}: {response.text}"

    except Exception as e:
        details = f"An exception occurred: {e}"

    end_time = time.time()
    print_result(test_name, success, end_time - start_time, details)
    return success

def test_streaming_function_calling():
    """测试流式函数调用功能"""
    test_name = "Function Calling (Streaming)"
    print(f"\n{'='*20} {test_name} {'='*20}\n")
    start_time = time.time()
    success = False
    details = ""

    try:
        tools = [{"type": "function", "function": {"name": "get_weather", "description": "Get weather", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}}}]
        data = {"model": "gemini-2.5-pro", "messages": [{"role": "user", "content": "What's the weather in Paris?"}], "tools": tools, "stream": True}
        response = requests.post(f"{API_URL}/chat/completions", json=data, stream=True)
        
        if response.status_code == 200:
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
            details = f"Request failed with status {response.status_code}: {response.text}"

    except Exception as e:
        details = f"An exception occurred: {e}"

    end_time = time.time()
    print_result(test_name, success, end_time - start_time, details)
    return success

def run_all_tests():
    """运行所有测试"""
    print_header("Vertex AI 到 OpenAI API 适配器综合测试")
    
    start_time = time.time()
    
    # 运行所有测试
    results = {
        "模型列表端点": test_models_endpoint(),
        "基础聊天": test_basic_chat(),
        "流式响应": test_streaming_chat(),
        "函数调用": test_function_calling(),
        "流式函数调用": test_streaming_function_calling(),
        "视觉功能": test_vision()
    }
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 打印总结
    print_header("测试结果总结")
    
    print(f"测试结果 (总耗时: {total_time:.2f}秒)")
    print("-" * 60)
    print(f"{'测试名称':<20} | {'结果':<10}")
    print("-" * 60)
    
    success_count = 0
    for name, result in results.items():
        status = "[SUCCESS]" if result else "[FAILURE]"
        if result:
            success_count += 1
        print(f"{name:<20} | {status:<10}")
    
    print("-" * 60)
    print(f"总计: {success_count}/{len(results)} 测试通过")
    
    if success_count == len(results):
        print("\n恭喜！所有测试都通过了！")
    else:
        print(f"\n注意：有 {len(results) - success_count} 个测试失败。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vertex AI 适配器综合测试工具")
    parser.add_argument("--url", help="适配器API URL", default=API_URL)
    parser.add_argument("--key", help="API密钥", default=API_KEY)
    parser.add_argument("--test", help="指定要运行的测试 (models, basic_chat, streaming_chat, function_calling, streaming_function_calling, vision)")
    parser.add_argument("--proxy", help="HTTP代理", default="http://127.0.0.1:7890")
    
    args = parser.parse_args()
    
    # 更新配置
    API_URL = args.url
    API_KEY = args.key
    os.environ["HTTPS_PROXY"] = args.proxy
    
    if args.test:
        test_function = {
            "models": test_models_endpoint,
            "basic_chat": test_basic_chat,
            "streaming_chat": test_streaming_chat,
            "function_calling": test_function_calling,
            "streaming_function_calling": test_streaming_function_calling,
            "vision": test_vision
        }.get(args.test)
        
        if test_function:
            test_function()
        else:
            # 提供友好的错误消息和有效测试选项提示
            print(f"[bold red]错误: 未知的测试名称 '{args.test}'[/bold red]")
            print("[blue]有效的测试名称:[/blue]")
            print("- models: 测试模型列表端点")
            print("- basic_chat: 测试基础聊天功能")
            print("- streaming_chat: 测试流式响应")
            print("- function_calling: 测试函数调用")
            print("- streaming_function_calling: 测试流式函数调用")
            print("- vision: 测试视觉功能")
    else:
        run_all_tests() 