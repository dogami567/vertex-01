#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gemini API 综合测试脚本
包含多种调用方式和功能测试
"""

import os
import time
import sys

# 显示环境信息
print("="*50)
print("环境信息:")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"HTTP代理: {os.environ.get('HTTP_PROXY', '未设置')}")
print(f"HTTPS代理: {os.environ.get('HTTPS_PROXY', '未设置')}")
print(f"应用凭据: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'ADC模式 (未设置)')}")
print("="*50)

# =====================================================================
# 测试1: 使用 Vertex AI SDK 调用 Gemini 2.5 Pro (ADC认证)
# =====================================================================
print("\n\n测试1: 使用 Vertex AI SDK 调用 Gemini 2.5 Pro (ADC认证)")
print("-"*50)

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    
    PROJECT_ID = "cursor-use-api"
    LOCATION = "us-central1"
    
    print(f"初始化Vertex AI (项目: {PROJECT_ID}, 区域: {LOCATION})...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    print("加载 Gemini 2.5 Pro 模型...")
    model = GenerativeModel("gemini-2.5-pro")
    
    prompt = "你好，请用中文写一首关于夏天的五言绝句。"
    print(f"发送提示: '{prompt}'")
    
    start_time = time.time()
    response = model.generate_content(prompt)
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("模型回复:")
    print(response.text)
    print("\n测试1结果: 成功 ✓")
    
except Exception as e:
    print(f"测试1失败: {e}")

# =====================================================================
# 测试2: 使用 Vertex AI SDK 进行对话 (ADC认证)
# =====================================================================
print("\n\n测试2: 使用 Vertex AI SDK 进行对话 (ADC认证)")
print("-"*50)

try:
    from vertexai.generative_models import ChatSession
    
    print("创建聊天会话...")
    chat = ChatSession(model)
    
    print("发送第一条消息: '你好，请介绍一下自己'")
    start_time = time.time()
    response = chat.send_message("你好，请介绍一下自己")
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("模型回复:")
    print(response.text)
    
    print("\n发送第二条消息: '你能帮我解决什么问题?'")
    start_time = time.time()
    response = chat.send_message("你能帮我解决什么问题?")
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("模型回复:")
    print(response.text)
    print("\n测试2结果: 成功 ✓")
    
except Exception as e:
    print(f"测试2失败: {e}")

# =====================================================================
# 测试3: 使用 Vertex AI SDK 设置生成参数 (ADC认证)
# =====================================================================
print("\n\n测试3: 使用 Vertex AI SDK 设置生成参数 (ADC认证)")
print("-"*50)

try:
    from vertexai.generative_models import GenerationConfig
    
    print("创建自定义生成配置...")
    generation_config = GenerationConfig(
        temperature=0.2,          # 降低随机性
        max_output_tokens=256,    # 限制输出长度
        top_p=0.8,                # 控制多样性
        top_k=40                  # 控制多样性
    )
    
    prompt = "请用中文写一个简短的科幻故事开头，100字以内。"
    print(f"发送提示: '{prompt}'")
    
    start_time = time.time()
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("模型回复:")
    print(response.text)
    print("\n测试3结果: 成功 ✓")
    
except Exception as e:
    print(f"测试3失败: {e}")

# =====================================================================
# 测试4: 使用 Vertex AI SDK 流式输出 (ADC认证)
# =====================================================================
print("\n\n测试4: 使用 Vertex AI SDK 流式输出 (ADC认证)")
print("-"*50)

try:
    prompt = "请用中文写一个关于人工智能的短段落。"
    print(f"发送提示: '{prompt}'")
    print("开始流式输出:")
    
    start_time = time.time()
    responses = model.generate_content(
        prompt,
        stream=True
    )
    
    full_response = ""
    for response in responses:
        chunk = response.text
        full_response += chunk
        print(chunk, end="", flush=True)
    
    end_time = time.time()
    print("\n")
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("\n测试4结果: 成功 ✓")
    
except Exception as e:
    print(f"测试4失败: {e}")

# =====================================================================
# 测试5: 使用 Google Generative AI Python SDK (API密钥方式)
# =====================================================================
print("\n\n测试5: 使用 Google Generative AI Python SDK (API密钥方式)")
print("-"*50)
print("注意: 此测试需要有效的API密钥，如果未设置将跳过")

try:
    import google.generativeai as genai
    
    # 检查是否有API密钥
    API_KEY = os.environ.get("GOOGLE_API_KEY", "")
    
    if not API_KEY:
        print("未设置GOOGLE_API_KEY环境变量，跳过此测试")
    else:
        print("配置Google Generative AI SDK...")
        genai.configure(api_key=API_KEY)
        
        print("加载Gemini模型...")
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        prompt = "请用中文写一句名言警句。"
        print(f"发送提示: '{prompt}'")
        
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        
        print(f"请求耗时: {end_time - start_time:.2f} 秒")
        print("模型回复:")
        print(response.text)
        print("\n测试5结果: 成功 ✓")
        
except ImportError:
    print("未安装google-generativeai包，跳过此测试")
except Exception as e:
    print(f"测试5失败: {e}")

# =====================================================================
# 测试6: 模型能力测试 - 代码生成
# =====================================================================
print("\n\n测试6: 模型能力测试 - 代码生成")
print("-"*50)

try:
    prompt = """请用Python编写一个简单的计算器函数，要求：
    1. 接受两个数字和一个操作符（+, -, *, /）作为参数
    2. 返回计算结果
    3. 处理除零错误
    4. 包含简单的文档字符串
    """
    print(f"发送提示: '{prompt}'")
    
    model = GenerativeModel("gemini-2.5-pro")
    start_time = time.time()
    response = model.generate_content(prompt)
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("模型回复:")
    print(response.text)
    print("\n测试6结果: 成功 ✓")
    
except Exception as e:
    print(f"测试6失败: {e}")

# =====================================================================
# 测试7: 模型能力测试 - 中文理解与生成
# =====================================================================
print("\n\n测试7: 模型能力测试 - 中文理解与生成")
print("-"*50)

try:
    prompt = """请解释以下成语的含义，并给出一个使用场景：
    1. 一鸣惊人
    2. 守株待兔
    3. 刻舟求剑
    """
    print(f"发送提示: '{prompt}'")
    
    model = GenerativeModel("gemini-2.5-pro")
    start_time = time.time()
    response = model.generate_content(prompt)
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print("模型回复:")
    print(response.text)
    print("\n测试7结果: 成功 ✓")
    
except Exception as e:
    print(f"测试7失败: {e}")

print("\n\n")
print("="*50)
print("测试完成!")
print("="*50) 