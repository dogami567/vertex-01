#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接测试VertexAI API调用
"""

import os
import sys
import time

# 设置代理
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
except ImportError:
    print("正在安装vertexai库...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vertexai"])
    import vertexai
    from vertexai.generative_models import GenerativeModel

# 项目信息
PROJECT_ID = "cursor-use-api"
LOCATION = "us-central1"

def main():
    print(f"直接测试VertexAI API (项目: {PROJECT_ID}, 区域: {LOCATION})")
    
    # 输出环境信息，便于诊断问题
    print("\n环境信息：")
    print(f"vertexai 版本: {vertexai.__version__}")
    print(f"Python 版本: {sys.version}")
    print(f"代理设置: {os.environ.get('HTTPS_PROXY', '未设置')}")
    print(f"凭证路径: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '使用应用程序默认凭据')}")
    
    try:
        print("\n初始化VertexAI...")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("初始化成功!")
        
        # 尝试最新的Gemini模型名称 (根据您提供的屏幕截图)
        model_names = [
            "gemini-2.5-pro", 
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite-preview-06-17",
            "gemini-2.0-flash-preview-image-generation",
            # 旧版本模型作为备选
            "gemini-pro", 
            "gemini-flash",
            "text-bison"
        ]
        
        print("\n测试各个模型...")
        for model_name in model_names:
            print(f"\n尝试模型: {model_name}")
            try:
                start_time = time.time()
                model = GenerativeModel(model_name)
                response = model.generate_content("你好，请简短地介绍一下自己")
                print(f"✅ 成功! 模型 {model_name} 可用!")
                print(f"响应时间: {time.time() - start_time:.2f} 秒")
                print(f"回复: {response.text[:100]}...")
                
                # 一旦找到一个可用的模型，尝试流式响应
                print("\n测试流式响应...")
                try:
                    stream_response = model.generate_content("给我讲一个短故事", stream=True)
                    print("流式回复: ", end="")
                    for chunk in stream_response:
                        if hasattr(chunk, "text"):
                            print(chunk.text, end="", flush=True)
                    print("\n✅ 流式响应成功!")
                except Exception as e:
                    print(f"❌ 流式响应失败: {e}")
                
                # 找到一个工作的模型后退出循环
                break
            except Exception as e:
                print(f"❌ 失败! 模型 {model_name} 不可用!")
                print(f"错误: {str(e)[:150]}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 