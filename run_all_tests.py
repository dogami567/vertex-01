import sys
import os

# 添加vertex-openai-adapter目录到搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'vertex-openai-adapter'))

from test_client import test_client
from test_function_calling import test_function_calling
from test_vision import test_vision
from test_embeddings import test_embeddings

def main():
    results = {}  # 初始化结果字典
    
    all_tests = [
        test_client,
        test_function_calling,
        test_vision,
        test_embeddings
    ]
    for test_func in all_tests:
        try:
            success = test_func()
            results[test_func.__name__] = "✅ 成功" if success else "❌ 失败"
        except Exception as e:
            results[test_func.__name__] = f"❌ 错误: {e}"

    print("\n--- 所有测试完成 ---") 
    
    # 打印测试结果
    for test_name, result in results.items():
        print(f"{test_name}: {result}")

if __name__ == "__main__":
    main() 