#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试使用函数调用实现的搜索功能的客户端脚本
"""

import os
import json
import time
import sys
from openai import OpenAI
import requests
try:
    from googlesearch import search as google_search
except ImportError:
    print("错误: 缺少 'google' 模块。请安装它: pip install google")
    print("正在尝试安装...")
    os.system("pip install google")
    try:
        from googlesearch import search as google_search
    except ImportError:
        print("无法自动安装 'google' 模块。请手动安装后重试。")
        sys.exit(1)

# 配置OpenAI客户端以连接到本地适配器
client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:5000/v1"
)

# 实现搜索函数，与adapter中的函数声明匹配
def search_on_web(query: str, max_results: int = 3):
    """
    通过Google搜索引擎搜索查询，返回结果URL和摘要
    """
    print(f"\n--> 执行搜索: '{query}'")
    try:
        results = []
        for url in google_search(query, stop=max_results):
            results.append(url)
            print(f"  找到结果: {url}")
            
            # 尝试获取页面标题和简短摘要
            try:
                res = requests.get(url, timeout=3)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.title.string if soup.title else "无标题"
                print(f"  标题: {title}")
            except Exception as e:
                print(f"  无法获取页面详情: {e}")
        
        search_result = {
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query
        }
        print(f"  搜索完成，找到 {len(results)} 个结果")
        return search_result
    except Exception as e:
        print(f"搜索过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query
        }

def test_search_function(question):
    """
    测试搜索功能，使用-search后缀的模型名称，并处理函数调用
    """
    print(f"问题: {question}")
    print("--> 准备发送请求...")

    try:
        messages = [
            {"role": "system", "content": "你是一个可以帮助用户获取最新信息的助手。对于用户询问的最新信息，请先使用search_on_web工具来搜索，然后根据搜索结果回答。总是先搜索再回答。"},
            {"role": "user", "content": question}
        ]
        
        # 第一步：发送初始请求
        print("--> 发送请求到模型...")
        response = client.chat.completions.create(
            model="gpt-4o-search",  # 使用-search后缀触发搜索功能
            temperature=0,  # 使用更低的温度，使模型更倾向于使用工具
            stream=False,
            messages=messages
        )
        
        # 打印原始响应用于调试
        print("\n--> 收到响应:")
        print(f"响应类型: {type(response)}")
        print(f"响应JSON: {json.dumps(response.model_dump(), indent=2)}")
        
        # 检查是否有函数调用
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            print("\n--> 模型请求调用搜索函数...")
            
            # 执行所有工具调用
            for tool_call in response.choices[0].message.tool_calls:
                print(f"工具调用ID: {tool_call.id}")
                print(f"工具类型: {tool_call.type}")
                print(f"函数名称: {tool_call.function.name}")
                print(f"函数参数: {tool_call.function.arguments}")
                
                if tool_call.function.name == "search_on_web":
                    # 解析参数
                    args = json.loads(tool_call.function.arguments)
                    query = args.get("query", "")
                    max_results = args.get("max_results", 3)
                    
                    # 调用搜索函数
                    search_result = search_on_web(query, max_results)
                    print(f"\n--> 搜索结果: {json.dumps(search_result, ensure_ascii=False, indent=2)}")
                    
                    # 将结果添加到消息历史
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": "search_on_web",
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "search_on_web", 
                        "content": json.dumps(search_result)
                    })
            
            # 第二步：发送包含工具结果的请求
            print("\n--> 发送工具执行结果...")
            final_response = client.chat.completions.create(
                model="gpt-4o-search",
                messages=messages,
                stream=False,
            )
            
            # 显示最终回复
            print("\n--- 模型最终回复 ---")
            if hasattr(final_response.choices[0].message, 'content') and final_response.choices[0].message.content:
                print(final_response.choices[0].message.content)
            else:
                print("模型未返回内容")
                print(f"完整响应: {json.dumps(final_response.model_dump(), indent=2)}")
            
        else:
            # 如果模型直接回复（没有工具调用）
            print("\n--- 模型直接回复（未使用搜索工具） ---")
            if hasattr(response.choices[0].message, 'content') and response.choices[0].message.content:
                print(response.choices[0].message.content)
            else:
                print("模型未返回内容")
            
    except Exception as e:
        print(f"\n--> 请求失败，发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n--> 测试脚本执行结束。")

if __name__ == "__main__":
    # 如果需要代理
    if "HTTPS_PROXY" not in os.environ:
        print("⚠️  警告: 未检测到HTTPS_PROXY环境变量。可能需要设置代理才能访问搜索功能。")
    
    # 定义要测试的问题列表
    questions = [
        "今天是星期几？",
        "国际金价现在多少？",
        "下一个中国法定节假日是什么？"
    ]
    
    # 依次测试每个问题
    for i, question in enumerate(questions):
        print(f"\n\n===== 测试问题 {i+1}/{len(questions)} =====")
        test_search_function(question)
        time.sleep(2)  # 避免请求过于频繁 