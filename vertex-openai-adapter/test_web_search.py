#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试联网搜索功能的客户端脚本
"""

import os
from openai import OpenAI
import requests
import json

# 配置OpenAI客户端以连接到本地适配器
client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:5000/v1"
)

def test_web_search():
    """
    发送一个需要联网搜索才能回答的问题，并打印结果。
    """
    question = "中国的下一个公共假期是哪一天？"
    print(f"问题: {question}\\n")

    print("--> 准备发送请求...")
    try:
        # 使用带有 '-search' 后缀的模型名称来触发服务器的联网功能
        chat_completion = client.chat.completions.create(
            model="gemini-2.5-pro-search",  # 关键点：使用-search后缀
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            stream=False, # 使用非流式以获得完整、清晰的响应对象，方便调试
        )

        # 打印响应
        print("--> 请求成功完成！")
        print("\\n模型回答:")
        if chat_completion.choices:
            print(chat_completion.choices[0].message.content)
        else:
            print("模型没有返回有效回答。")
        
        print("\\n--- 原始响应对象 ---")
        print(chat_completion)
        print("--------------------")

    except Exception as e:
        print(f"\\n--> 请求失败，发生错误: {e}")

    print("\\n--> 测试脚本执行结束。")

if __name__ == "__main__":
    test_web_search() 