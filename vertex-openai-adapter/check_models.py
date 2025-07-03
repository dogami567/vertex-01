#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
这个脚本用于检查在当前Google项目中可用的所有Gemini模型
"""

import os
import vertexai
from vertexai.generative_models import GenerativeModel

# 设置环境变量
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 设置项目和位置
PROJECT_ID = "cursor-use-api"
LOCATION = "us-central1"

# 尝试的模型名称列表
MODEL_NAMES_TO_TRY = [
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-1.5-flash",
    "gemini-flash",
    "gemini-pro-vision",
    "gemini-1.0-pro",
    "gemini-1.0-pro-vision",
    "gemini-1.0-pro-001",
    "gemini-ultra-vision",
    "text-bison",
    "text-unicorn"
]

def main():
    print(f"正在初始化Vertex AI (项目: {PROJECT_ID}, 区域: {LOCATION})...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    print("Vertex AI 初始化成功。")
    
    print("\n开始测试可用的模型:")
    print("=" * 50)
    
    for model_name in MODEL_NAMES_TO_TRY:
        print(f"\n尝试模型: {model_name}")
        try:
            model = GenerativeModel(model_name)
            response = model.generate_content("你好，请简短地介绍一下自己。")
            print(f"✓ 成功! 模型 {model_name} 可用!")
            print(f"  回复: {response.text[:100]}...")
        except Exception as e:
            print(f"✗ 失败! 模型 {model_name} 不可用!")
            print(f"  错误: {str(e)[:150]}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 