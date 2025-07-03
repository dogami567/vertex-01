#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查服务器连接的简单脚本
"""

import requests
import sys

def check_server(url="http://localhost:5000/v1/models"):
    """尝试连接到服务器并获取模型列表"""
    print(f"尝试连接到: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"成功! 状态码: {response.status_code}")
            print(f"响应内容: {response.json()}")
            return True
        else:
            print(f"连接成功但返回错误状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"连接错误: {e}")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        return False

if __name__ == "__main__":
    # 尝试不同的地址和端口组合
    urls_to_try = [
        "http://localhost:5000/v1/models",
        "http://127.0.0.1:5000/v1/models",
        "http://0.0.0.0:5000/v1/models"
    ]
    
    success = False
    for url in urls_to_try:
        print(f"\n=== 检查 {url} ===")
        if check_server(url):
            success = True
            print(f"✓ 服务器可在 {url} 访问")
            break
    
    if not success:
        print("\n❌ 无法连接到服务器。请确保服务器正在运行。")
        sys.exit(1)
    else:
        print("\n✓ 服务器检查成功!") 