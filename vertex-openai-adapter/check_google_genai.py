#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用google.generativeai库直接测试模型可用性
"""

import os
import sys

# 设置代理
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

try:
    import google.generativeai as genai
except ImportError:
    print("安装google.generativeai库...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

# 定义要测试的模型
MODELS_TO_TRY = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-pro",
    "gemini-flash"
]

def main():
    print("列出可用的模型...")
    try:
        for m in genai.list_models():
            print(f"找到模型: {m.name}")
    except Exception as e:
        print(f"列出模型时出错: {e}")

    print("\n尝试使用各个模型...")
    for model_name in MODELS_TO_TRY:
        print(f"\n测试模型: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("你好，请用一句话介绍自己")
            print(f"✓ 成功! 模型 {model_name} 可用!")
            print(f"回复: {response.text[:100]}")
        except Exception as e:
            print(f"✗ 失败! 模型 {model_name} 不可用!")
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 