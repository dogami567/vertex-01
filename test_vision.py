#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Vertex AI到OpenAI适配器的视觉功能
"""

import os
import json
import base64
import requests
import time
import argparse

# 设置环境变量
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 测试配置
API_URL = "http://localhost:5000/v1"  # 本地适配器地址
API_KEY = "sk-test123456789"  # 测试用API密钥

# 默认测试图像路径
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_images", "test_image.jpg")

# 测试图像处理功能
def test_vision():
    """测试基本的图像处理功能"""
    
    print("=" * 50)
    print("Testing Vision Feature...")
    
    # 准备测试图像
    if not os.path.exists(IMAGE_PATH):
        print(f"[ERROR] Test image not found at: {IMAGE_PATH}")
        print("Please provide a valid path to the test image.")
        return
    
    # 读取并编码图像
    try:
        with open(IMAGE_PATH, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Could not read or encode image: {e}")
        return
    
    # 创建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "What is in this picture? Please describe in detail."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "stream": False,
        "max_tokens": 1000
    }
    
    # 发送请求
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=data)
        end_time = time.time()
        
        print(f"Request took: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status Code: {response.status_code}")
            print("Response Content:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 检查响应是否包含对图像的描述
            if "choices" in result and result["choices"]:
                message = result["choices"][0]["message"]
                if "content" in message and message["content"] and "error" not in message["content"].lower():
                    print("\n[SUCCESS] Model returned a description for the image.")
                else:
                    print(f"\n[FAILURE] Model did not return valid content. Response: {message.get('content')}")
            else:
                print("\n[FAILURE] Response format is incorrect.")
        else:
            print(f"[FAILURE] Request failed with status code: {response.status_code}")
            print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"[FAILURE] Request exception: {e}")
    
    print("=" * 50)

# 测试视觉流式响应
def test_vision_stream():
    """测试视觉功能的流式响应"""
    
    print("=" * 50)
    print("开始测试视觉流式响应...")
    
    # 准备测试图像
    if not os.path.exists(IMAGE_PATH):
        print(f"[错误] 测试图像不存在: {IMAGE_PATH}")
        print("请提供有效的测试图像路径")
        return
    
    # 读取并编码图像
    try:
        with open(IMAGE_PATH, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"[错误] 无法读取或编码图像: {e}")
        return
    
    # 创建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "请分析这张图片并告诉我你看到了什么？"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "stream": True,
        "max_tokens": 1000
    }
    
    # 发送请求
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=data, stream=True)
        
        if response.status_code == 200:
            print(f"状态码: {response.status_code}")
            print("流式响应内容:")
            
            content_received = False
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        line = line[6:]  # 移除 "data: " 前缀
                    
                    if line == "[DONE]":
                        print("\n流式响应结束")
                        continue
                    
                    try:
                        chunk = json.loads(line)
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                content_received = True
                                print(content, end="", flush=True)
                    except json.JSONDecodeError:
                        print(f"无法解析JSON: {line}")
            
            end_time = time.time()
            print(f"\n\n请求耗时: {end_time - start_time:.2f}秒")
            
            if content_received:
                print("\n[成功] 在流式响应中收到了图像描述")
                print(f"完整响应长度: {len(full_response)}字符")
            else:
                print("\n[错误] 在流式响应中没有收到内容")
        else:
            print(f"[错误] 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"[错误] 请求异常: {e}")
    
    print("=" * 50)

# 主函数
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="测试视觉功能")
    parser.add_argument("--image", type=str, help="指定测试图像路径", 
                        default=os.path.join(os.path.dirname(__file__), "test_images", "test_image.jpg"))
    parser.add_argument("--stream", action="store_true", help="使用流式响应模式")
    
    args = parser.parse_args()
    
    # 如果指定了图像路径，更新全局变量
    if args.image:
        IMAGE_PATH = args.image
    
    # 运行测试
    if args.stream:
        test_vision_stream()
    else:
        test_vision() 