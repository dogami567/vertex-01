#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vertex AI 到 OpenAI API 适配器 (流式稳定版)
此版本回归到已知能工作的最简流式功能
"""

import os
import time
import json
from flask import Flask, request, jsonify, Response
import vertexai
from vertexai.generative_models import GenerativeModel

# --- 初始化 ---
app = Flask(__name__)

PROJECT_ID = "cursor-use-api"
LOCATION = "us-central1"
API_KEY = "sk-test123456789"

try:
    print(f"正在初始化Vertex AI (项目: {PROJECT_ID}, 区域: {LOCATION})...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    print("Vertex AI 初始化成功。")
    HAS_VERTEX_AI = True
except Exception as e:
    print(f"!!! Vertex AI 初始化失败: {e}")
    HAS_VERTEX_AI = False

# 模型映射表 - 使用最新的模型名称
MODEL_MAPPING = {
    "gpt-4o": "gemini-2.5-pro",
    "gpt-4": "gemini-2.5-pro",
    "gpt-3.5-turbo": "gemini-2.5-flash",
    "default": "gemini-2.5-flash"
}

# --- 核心路由 ---
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer ') or auth_header[7:] != API_KEY:
        return jsonify({"error": "无效的API密钥"}), 401
    
    if not HAS_VERTEX_AI:
        return jsonify({"error": "Vertex AI后端未初始化"}), 503

    try:
        data = request.json
        model_name = data.get('model', 'default')
        messages = data.get('messages', [])
        stream = data.get('stream', False)

        # 简化处理：只获取最后一个用户消息作为prompt
        prompt = ""
        if messages and messages[-1].get('role') == 'user':
            # 仅处理字符串格式的内容
            if isinstance(messages[-1].get('content'), str):
                 prompt = messages[-1].get('content', "")

        if not prompt:
            return jsonify({"error": "未找到有效的用户prompt"}), 400

        vertex_model_name = MODEL_MAPPING.get(model_name, MODEL_MAPPING['default'])
        model = GenerativeModel(vertex_model_name)

        # --- 流式传输实现 ---
        if stream:
            def generate():
                try:
                    responses = model.generate_content(prompt, stream=True)
                    for chunk in responses:
                        if not hasattr(chunk, 'text') or not chunk.text:
                            continue
                        
                        stream_chunk = {
                            "id": f"chatcmpl-{os.urandom(4).hex()}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model_name,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": chunk.text},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(stream_chunk)}\n\n"

                    end_chunk = {
                        "id": f"chatcmpl-{os.urandom(4).hex()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model_name,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                    }
                    yield f"data: {json.dumps(end_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    print(f"!!! 流式传输过程中发生错误: {e}")
            return Response(generate(), mimetype='text/event-stream')

        # --- 非流式传输实现 ---
        else:
            response = model.generate_content(prompt)
            content = response.text
            openai_response = {
                "id": f"chatcmpl-{os.urandom(4).hex()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_name,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
            return jsonify(openai_response)

    except Exception as e:
        print(f"!!! 严重错误: {e}")
        return jsonify({"error": {"message": str(e), "type": "internal_server_error"}}), 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    return jsonify({
        "object": "list",
        "data": [
            {"id": "gpt-4o", "object": "model", "owned_by": "google"},
            {"id": "gpt-4", "object": "model", "owned_by": "google"},
            {"id": "gpt-3.5-turbo", "object": "model", "owned_by": "google"}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
