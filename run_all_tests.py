from test_function_calling import test_function_calling
from test_vision import test_vision
from test_embeddings import test_embeddings

def main():
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