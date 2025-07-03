import requests
import json
import time

def test_embeddings():
    """
    测试嵌入（Embeddings）功能
    """
    print("\n--- 测试嵌入功能 ---")
    url = "http://127.0.0.1:5000/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer whatever" 
    }
    data = {
        "model": "text-embedding-ada-002", # 将映射到 text-embedding-004
        "input": "你好，世界"
    }

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        end_time = time.time()
        
        result = response.json()
        
        print("响应状态码:", response.status_code)
        
        # 简单的验证
        if "data" in result and len(result["data"]) > 0 and "embedding" in result["data"][0]:
            print("✅ 嵌入功能测试成功")
            print(f"   - 模型: {result.get('model')}")
            print(f"   - 向量维度: {len(result['data'][0]['embedding'])}")
            print(f"   - 耗时: {end_time - start_time:.2f} 秒")
            return True
        else:
            print("❌ 嵌入功能测试失败: 响应格式不正确")
            print("响应内容:", json.dumps(result, indent=2, ensure_ascii=False))
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ 嵌入功能测试失败: 请求异常 - {e}")
        return False
    except Exception as e:
        print(f"❌ 嵌入功能测试失败: 未知错误 - {e}")
        return False

if __name__ == '__main__':
    # 确保服务已经启动
    print("请先在另一个终端运行 'python simplest.py'")
    print("等待5秒让服务启动...")
    time.sleep(5)
    test_embeddings() 