#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vertex AI 到 OpenAI API 适配器测试客户端
此脚本测试适配器的基本功能
"""

import requests
import json
import sys

# 适配器运行的URL
# 注意：这个端口必须与您启动Docker容器时 -p 参数后面的第一个端口号一致
# 例如: docker run ... -p 5001:5000 ...
BASE_URL = "http://localhost:5001/v1"
API_KEY = "sk-test123456789"  # 使用脚本中定义的固定key

def test_list_models():
    """测试 /v1/models 端点"""
    print("\n测试获取模型列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/models",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        response.raise_for_status()  # 如果请求失败则抛出异常
        models = response.json()
        print("✓ 测试成功!")
        print("获取到的模型:")
        print(json.dumps(models, indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        print("✗ 测试失败!")

def test_chat_completions():
    """测试 /v1/chat/completions 端点"""
    print("\n测试聊天完成...")
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "你好，请用中文简单介绍一下自己。"}
        ]
    }
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        completion = response.json()
        print("✓ 测试成功!")
        print("获取到的响应:")
        print(json.dumps(completion, indent=2, ensure_ascii=False))
        # 打印出模型返回的具体内容
        if completion.get("choices"):
            print("\n模型回复内容:")
            print(completion["choices"][0]["message"]["content"])
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        print("✗ 测试失败!")

if __name__ == "__main__":
    print("=" * 50)
    print("Vertex AI 到 OpenAI API 适配器测试客户端")
    print("=" * 50)
    test_list_models()
    test_chat_completions()
    print("\n全部测试完成!")
