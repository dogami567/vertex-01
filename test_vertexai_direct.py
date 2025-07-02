#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接测试Vertex AI连接是否正常
"""

import os
import logging
import time

# 设置环境变量
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    print("Directly testing VertexAI API (Project: cursor-use-api, Location: us-central1)\n")
    
    # 收集环境信息
    print("Environment Info:")
    
    try:
        import vertexai
        print(f"  - vertexai version: {vertexai.__version__}")
    except ImportError:
        print("  - vertexai is not installed")
    
    import sys
    print(f"  - Python version: {sys.version}")
    print(f"  - Proxy: {os.environ.get('HTTPS_PROXY', 'Not set')}")
    print(f"  - Credentials: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Using Application Default Credentials')}")
    print()
    
    # 尝试初始化Vertex AI
    try:
        print("Initializing VertexAI...")
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project="cursor-use-api", location="us-central1")
        print("[SUCCESS] Initialization successful!")
        print()
        
        # 测试模型访问
        print("Testing models...")
        
        # 测试gemini-pro模型
        test_models = [
            "gemini-2.5-pro",
        ]
        
        for model_name in test_models:
            print(f"\nAttempting model: {model_name}")
            
            try:
                model = GenerativeModel(model_name)
                response = model.generate_content("Hello, please briefly introduce yourself.")
                
                print(f"[SUCCESS] Model {model_name} is available!")
                print(f"  - Response: {response.text[:100]}...")
                
                # 测试流式响应
                print("\n  Testing streaming response...")
                start_time = time.time()
                
                responses = model.generate_content(
                    "Respond to my greeting in the form of a poem.", stream=True
                )
                
                print("  - Streamed response:")
                for response_chunk in responses:
                    try:
                        print(f"{response_chunk.text}", end="")
                    except:
                        print(f"[Partial response parsing failed]", end="")
                
                end_time = time.time()
                print(f"\n\n  - Streaming response time: {end_time - start_time:.2f}s")
                
            except Exception as e:
                print(f"[FAILURE] Model {model_name} is not available!")
                print(f"  - Error: {e}")
    
    except Exception as e:
        print(f"[FAILURE] Initialization failed: {e}")

if __name__ == "__main__":
    main() 