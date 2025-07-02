import requests
import json
import os

# 从环境变量或默认值获取服务器地址
# 这使得测试更灵活，例如在Docker容器中运行测试
BASE_URL = os.environ.get("SIMPLEST_URL", "http://127.0.0.1:5000")
ADAPTER_URL = f"{BASE_URL}/v1/embeddings"

def test_embeddings(printer=print):
    """
    测试嵌入端点。
    发送一个包含文本的请求，并验证响应是否符合预期的格式和内容。
    """
    printer("--- Running Test: Embeddings ---")

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer no-key"
    }
    data = {
        "model": "text-embedding-3-small",  # 这个模型名会被映射到 text-embedding-004
        "input": "你好，世界！"
    }

    try:
        response = requests.post(ADAPTER_URL, headers=headers, json=data)
        response.raise_for_status()  # 如果响应状态码不是2xx，则抛出异常

        response_data = response.json()
        
        # 1. 验证基本结构
        assert "object" in response_data, "响应缺少 'object' 字段"
        assert response_data["object"] == "list", f"响应 'object' 字段值不为 'list'，而是 '{response_data['object']}'"
        assert "data" in response_data, "响应缺少 'data' 字段"
        assert isinstance(response_data["data"], list), "响应 'data' 字段不是一个列表"
        assert len(response_data["data"]) > 0, "响应 'data' 列表为空"
        
        # 2. 验证嵌入对象的结构
        embedding_item = response_data["data"][0]
        assert "object" in embedding_item, "嵌入对象缺少 'object' 字段"
        assert embedding_item["object"] == "embedding", f"嵌入对象的 'object' 字段值不为 'embedding'，而是 '{embedding_item['object']}'"
        assert "index" in embedding_item, "嵌入对象缺少 'index' 字段"
        assert embedding_item["index"] == 0, "嵌入对象的 'index' 不为0"
        assert "embedding" in embedding_item, "嵌入对象缺少 'embedding' 字段"
        
        # 3. 验证嵌入向量本身
        embedding_vector = embedding_item["embedding"]
        assert isinstance(embedding_vector, list), "嵌入向量不是一个列表"
        assert len(embedding_vector) == 768, f"嵌入向量的维度不为768，而是 {len(embedding_vector)}" # text-embedding-004 的维度是 768
        assert all(isinstance(val, float) for val in embedding_vector), "嵌入向量中包含非浮点数值"

        printer("[SUCCESS] Embeddings test passed.")
        return True

    except requests.exceptions.RequestException as e:
        printer(f"[FAILURE] 请求失败: {e}")
    except KeyError as e:
        printer(f"[FAILURE] 响应JSON中缺少关键字段: {e}")
        printer("收到的响应:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    except AssertionError as e:
        printer(f"[FAILURE] 断言失败: {e}")
        printer("收到的响应:", json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        printer(f"[FAILURE] 发生未知错误: {e}")
        if 'response' in locals():
            printer("收到的响应:", response.text)

    return False

if __name__ == "__main__":
    test_embeddings() 