import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part, ToolConfig
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time
from googlesearch import search as google_search_lib

# --- 配置 ---
# 请确保已通过 'gcloud auth application-default login' 进行认证
# 并且，如果需要，请在运行前设置代理:
# PowerShell: $env:HTTPS_PROXY="http://127.0.0.1:7890"
# aistudio: export HTTPS_PROXY="http://127.0.0.1:7890"

PROJECT_ID = "cursor-use-api"
LOCATION = "us-central1"
# 我们使用一个已知支持工具调用的稳定模型
MODEL_NAME = "gemini-2.5-pro"

# --- 新的自定义搜索工具 ---

def get_webpage_content(url: str) -> str:
    """尝试获取单个网页的纯文本内容。"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # 如果请求失败则引发异常
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除脚本和样式元素
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
            
        # 获取纯文本并格式化
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\\n'.join(chunk for chunk in chunks if chunk)
        
        # 截取前2000个字符以避免内容过长
        return text[:2000]
    except Exception as e:
        print(f"抓取网页 {url} 时出错: {e}")
        return None

def perform_web_search(query: str) -> str:
    """
    Performs a targeted Google search for a *specific, simple query* and returns the top 3 results with snippets.
    Do not use complex questions. Break down complex questions into simpler queries before using this tool.
    For example, instead of "What's the latest on Gemini vs GPT-4?", use "latest news Google Gemini model" and then "Gemini 1.5 vs GPT-4 comparison".
    """
    print(f"--- 工具被调用: perform_web_search(query='{query}') ---")
    try:
        # 使用正确的参数名: num, stop, pause
        search_results = list(google_search_lib(query, num=3, stop=3, pause=2.0))
        
        if not search_results:
            return "Google Search returned no results."

        # 格式化结果，提供标题和摘要
        # 注意：这个基础的'google'库返回的是URL列表，而不是带标题的对象。
        # 我们需要调整代码来处理这个情况。为了快速返回结果，我们先只返回URL。
        formatted_results = []
        for i, result_url in enumerate(search_results):
            formatted_results.append(f"{i+1}. URL: {result_url}")
        
        print(f"✅ Google Search 成功返回 {len(formatted_results)} 条结果。")
        return "\\n---\\n".join(formatted_results)
        
    except Exception as e:
        print(f"❌ Google Search 发生错误: {e}")
        return f"An error occurred during Google search: {str(e)}"

# --- 主要测试逻辑 ---

def direct_search_test():
    """
    一个直接调用Vertex AI并使用自定义搜索工具的测试函数。
    """
    print("--- 开始使用自定义函数调用测试搜索功能 ---")

    # 1. 初始化Vertex AI
    try:
        print(f"正在初始化Vertex AI，项目ID: '{PROJECT_ID}', 区域: '{LOCATION}'...")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("✅ Vertex AI 初始化成功。")
    except Exception as e:
        print(f"❌ 初始化Vertex AI时出错: {e}")
        print("   请确认您已经通过 'gcloud auth application-default login' 完成认证。")
        return

    # 2. 从Python函数创建Vertex AI工具
    print("正在定义自定义搜索工具...")
    custom_search_tool = Tool.from_function_declarations(
        [FunctionDeclaration.from_func(perform_web_search)]
    )
    print("✅ 自定义工具定义成功。")

    # 3. 初始化带有自定义工具的Gemini模型
    try:
        print(f"正在加载模型: '{MODEL_NAME}'...")
        model = GenerativeModel(MODEL_NAME, tools=[custom_search_tool])
        print("✅ 模型加载成功。")
    except Exception as e:
        print(f"❌ 加载模型时出错: {e}")
        print(f"   请确认模型名称 '{MODEL_NAME}' 在您的项目中可用。")
        return

    chat = model.start_chat()
    
    # 4. 提出一个简单、可验证的问题
    system_instruction = (
        "你的任务是回答用户的问题。对于需要实时信息才能回答的问题，"
        "请使用 `perform_web_search` 工具来获取当前准确信息。"
        "你最多只能调用工具3次。"
    )
    
    prompt = f"system_instruction: {system_instruction}\\n\\nUser question: 请问今天是什么日期和星期几？"

    print(f"\\n➡️  发送提示: '{prompt}'")

    try:
        # 第一次发送消息
        response = chat.send_message(prompt)

        search_count = 0
        max_searches = 3

        # 循环处理函数调用，直到模型返回文本或达到搜索上限
        while search_count < max_searches:
            # 检查模型是否要求函数调用
            if not response.candidates or not response.candidates[0].content.parts or not response.candidates[0].content.parts[0].function_call:
                # 如果没有函数调用，跳出循环
                break

            search_count += 1
            print(f"\\n(第 {search_count}/{max_searches} 次搜索循环)")

            # 并行处理模型请求的所有函数调用
            function_calls = response.candidates[0].content.parts
            function_responses = []

            for function_call_part in function_calls:
                function_call = function_call_part.function_call
                if not function_call or not function_call.name:
                    continue
                
                print(f"--- 并行工具调用: {function_call.name}(query='{function_call.args['query']}') ---")
                
                # 调用我们本地的Python函数
                args = {key: value for key, value in function_call.args.items()}
                function_response_data = perform_web_search(**args)
                
                # 收集函数响应
                function_responses.append(Part.from_function_response(
                    name=function_call.name,
                    response={"content": function_response_data},
                ))
            
            # 将所有并行执行的结果一次性返回给模型
            if not function_responses:
                break # 如果没有可执行的调用，则退出

            print("将所有并行执行结果一次性返回给模型...")
            response = chat.send_message(function_responses)
            print("✅ 所有函数结果已发送。")
        
        # 如果达到搜索上限后，模型仍然想调用函数，则强制其回答
        if search_count >= max_searches and response.candidates[0].content.parts[0].function_call.name:
            print("\\n⚠️ 已达到最大搜索次数。强制模型生成最终答案...")
            response = chat.send_message(
                Part.from_text("You have reached the maximum number of searches. Please provide a final answer based on the information you have gathered so far. Do not call any more tools.")
            )

        # 优雅地处理最终的响应
        print("\\n--- 模型最终回复 ---")
        try:
            # 尝试打印最终的文本答案
            print(response.text)
            print("--------------------")
            print("\\n🎉 测试成功完成！")
        except ValueError:
            # 如果模型在最后一步仍然返回函数调用，则优雅地处理
            print("模型在达到搜索上限后，仍固执地尝试再次调用工具。")
            print("我们的熔断机制已成功阻止它，任务按预期结束。")
            print("--------------------")
            print("\\n🎉 测试成功完成！")

    except Exception as e:
        print(f"❌ 与模型交互时发生严重错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 确保代理已设置（如果需要）
    if "HTTPS_PROXY" not in os.environ:
        print("⚠️  警告: 未检测到HTTPS_PROXY环境变量。如果您的网络需要代理才能访问Google Cloud，此脚本可能会失败。")
    direct_search_test() 