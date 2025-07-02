import openai
import os
import time
import httpx

# --- 配置 ---
# 定义代理
PROXY_URL = "http://127.0.0.1:7890"

# 使用 mounts 参数来配置代理，以兼容不同版本的 httpx
# 这是更现代且向后兼容的方式
transport = httpx.HTTPTransport(proxy=PROXY_URL)
http_client = httpx.Client(transport=transport)

# 将配置好的http客户端传递给OpenAI
client = openai.OpenAI(
    base_url="http://127.0.0.1:5001/v1",
    api_key="sk-test123456789",
    http_client=http_client
)

MODEL_NAME = "gpt-4o" # 使用一个会映射到 gemini-1.5-pro 的模型

# --- 测试用例 ---

def run_test(test_name, test_function):
    """一个简单的测试运行器，用于打印状态"""
    print(f"--- 运行测试: {test_name} ---")
    try:
        test_function()
        print(f"✅ 测试通过: {test_name}\n")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {test_name}")
        print(f"   错误: {e}\n")
        return False

def test_basic_chat():
    """测试1: 非流式的简单对话"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "你好！你叫什么名字？"}
        ],
        stream=False
    )
    response_content = completion.choices[0].message.content
    print(f"   模型回复: {response_content}")
    assert len(response_content) > 0, "模型回复不应为空"

def test_streaming_chat():
    """测试2: 流式传输的简单对话"""
    print("   模型回复 (流式): ", end="")
    chunks = []
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "请用一句话介绍一下什么是大型语言模型。"}
        ],
        stream=True
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            chunks.append(content)
    print() # 换行
    assert len(chunks) > 1, "流式响应应该包含多个数据块"

# --- 主函数 ---
def main():
    print("=============================")
    print("  开始对Vertex适配器进行测试 (稳定版)  ")
    print("=============================\n")
    
    # 运行所有测试
    results = [
        run_test("基础对话 (非流式)", test_basic_chat),
        run_test("简单对话 (流式)", test_streaming_chat),
    ]
    
    print("-----------------------------")
    if all(results):
        print("🎉🎉🎉 恭喜！所有核心测试均已通过！适配器已准备就绪。🎉🎉🎉")
    else:
        print("🔥🔥🔥 注意：部分测试失败，请检查适配器容器的日志。🔥🔥🔥")
        # 退出并返回一个非零代码，以便CI/CD等工具可以捕获失败
        exit(1)

if __name__ == "__main__":
    main() 