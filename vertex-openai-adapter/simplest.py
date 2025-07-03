#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最简单的Vertex AI到OpenAI API适配器
支持：
- 基本聊天功能
- 流式响应
- 函数调用
- 视觉模型
- 联网搜索（通过函数调用实现）
"""

import os
import json
import base64
import logging
import time
import traceback
import uuid
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    Content,
    Tool,
    FunctionDeclaration,
    GenerationConfig,
    GenerationResponse,
    HarmCategory,
    HarmBlockThreshold
)

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 环境变量配置
PROJECT_ID = os.environ.get("PROJECT_ID", "cursor-use-api")
LOCATION = os.environ.get("LOCATION", "us-central1")

# 模型映射
MODEL_MAPPING = {
    "gpt-4": "gemini-2.5-pro",
    "gpt-4-turbo": "gemini-2.5-pro",
    "gpt-4o": "gemini-2.5-flash",
    "gpt-3.5-turbo": "gemini-2.5-flash",
    "gpt-3.5-turbo-16k": "gemini-2.5-flash",
    "gpt-4-vision-preview": "gemini-2.5-pro",
    "gemini-pro": "gemini-2.5-pro",
    "gemini-flash": "gemini-2.5-flash",
}

# 初始化Vertex AI
try:
    logger.info(f"正在初始化Vertex AI (项目: {PROJECT_ID}, 区域: {LOCATION})...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logger.info("Vertex AI 初始化成功。")
except Exception as e:
    logger.error(f"初始化Vertex AI失败: {e}")
    # exit(1)

# 安全设置
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

# --- 辅助函数 ---

def _create_openai_stream_chunk(model_name, content=None, tool_calls=None, finish_reason=None):
    """创建OpenAI格式的流式响应块。"""
    chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}]
    }
    if content:
        chunk["choices"][0]["delta"]["content"] = content
    if tool_calls:
        chunk["choices"][0]["delta"]["tool_calls"] = tool_calls
    return f"data: {json.dumps(chunk)}\n\n"

def stream_response(model, contents, generation_config, tools, is_json_mode, model_name):
    """处理流式响应。"""
    try:
        responses = model.generate_content(
            contents,
            generation_config=generation_config,
            tools=tools,
            stream=True
        )
        
        for response in responses:
            if not response.candidates:
                continue

            candidate = response.candidates[0]
            
            # 处理函数调用
            if candidate.content.parts and candidate.content.parts[0].function_call:
                tool_calls = []
                for part in candidate.content.parts:
                    if part.function_call:
                        args_dict = {key: value for key, value in part.function_call.args.items()}
                        tool_calls.append({
                            "id": f"call_{uuid.uuid4().hex}",
                            "type": "function",
                            "function": {
                                "name": part.function_call.name,
                                "arguments": json.dumps(args_dict)
                            }
                        })
                yield _create_openai_stream_chunk(model_name, tool_calls=tool_calls)
            
            # 处理文本响应
            elif candidate.content and candidate.content.parts and hasattr(candidate.content.parts[0], 'text'):
                yield _create_openai_stream_chunk(model_name, content=candidate.content.parts[0].text)

        # 发送流结束标志
        yield _create_openai_stream_chunk(model_name, finish_reason="stop")
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"流式响应生成失败: {e}")
        logger.error(traceback.format_exc())
        error_chunk = _create_openai_stream_chunk(model_name, content=f"Error: {e}", finish_reason="error")
        yield error_chunk
        yield "data: [DONE]\n\n"

def normal_response(model, contents, generation_config, tools, is_json_mode, model_name):
    """处理非流式响应。"""
    try:
        response = model.generate_content(
            contents,
            generation_config=generation_config,
            tools=tools,
            stream=False
        )
        return convert_vertex_to_openai_response(response, model_name)
    except Exception as e:
        logger.error(f"普通响应生成失败: {e}")
        return {"error": str(e)}, 500

def convert_vertex_to_openai_response(response, model_name):
    """将Vertex AI的响应转换为OpenAI格式。"""
    if not response or not response.candidates:
        return {"error": "Invalid response from Vertex AI"}, 500
    
    candidate = response.candidates[0]
    
    # 处理函数调用
    if candidate.content.parts and candidate.content.parts[0].function_call:
        tool_calls = []
        for part in candidate.content.parts:
            if part.function_call:
                args_dict = {key: value for key, value in part.function_call.args.items()}
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex}",
                    "type": "function",
                    "function": {
                        "name": part.function_call.name,
                        "arguments": json.dumps(args_dict)
                    }
                })
        
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls
                },
                "finish_reason": "tool_calls"
            }],
            "usage": { "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0 }
        }
    
    # 处理文本响应
    text_content = ""
    if candidate.content and candidate.content.parts:
        try:
            text_content = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
        except Exception as e:
            logger.warning(f"处理响应文本时出错: {e}")
            # 尝试直接获取内容
            try:
                text_content = str(candidate.text)
            except:
                text_content = "无法提取响应内容"

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": text_content
            },
            "finish_reason": "stop"
        }],
        "usage": { "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0 }
    }

def convert_messages_to_vertex_format(messages):
    """将OpenAI格式的消息列表转换为Vertex AI格式。"""
    vertex_contents = []
    system_instruction = None

    for message in messages:
        role = message.get("role")
        content = message.get("content")

        if role == "system":
            system_instruction = Part.from_text(content)
            continue
        
        # 兼容旧格式的 'tool' 角色
        vertex_role = "model" if role == "assistant" else "user"
        if role == "tool":
            vertex_role = "user" # Tool/function responses are from user
            part = Part.from_function_response(
                name=message.get("name"),
                response={"content": content}
            )
            vertex_contents.append(Content(role=vertex_role, parts=[part]))
            continue

        parts = []
        if isinstance(content, str):
            parts.append(Part.from_text(content))
        elif isinstance(content, list):
            # 处理多模态内容
            for item in content:
                if item.get("type") == "text":
                    parts.append(Part.from_text(item.get("text", "")))
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image"):
                        # Base64
                        mime_type, base64_data = image_url.split(";", 1)
                        _, mime_type = mime_type.split(":", 1)
                        _, base64_data = base64_data.split(",", 1)
                        image_data = base64.b64decode(base64_data)
                        parts.append(Part.from_data(image_data, mime_type=mime_type))
                    else:
                        # URL
                        parts.append(Part.from_uri(uri=image_url, mime_type="image/jpeg"))

        # 处理工具调用请求
        if message.get("tool_calls"):
            for tool_call in message.get("tool_calls"):
                fc = tool_call.get("function", {})
                parts.append(Part.from_function_call(
                    name=fc.get("name"),
                    args={k: v for k, v in json.loads(fc.get("arguments", "{}")).items()}
                ))

        vertex_contents.append(Content(role=vertex_role, parts=parts))

    return vertex_contents, system_instruction

# --- API Endpoints ---

@app.route("/v1/models", methods=["GET"])
def list_models():
    """列出可用的模型"""
    model_data = []
    for model_key in MODEL_MAPPING.keys():
        model_data.append({
            "id": model_key,
            "object": "model",
            "owned_by": "vertex-ai",
            "created": int(time.time())
        })
    return jsonify({"object": "list", "data": model_data})

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """处理聊天请求"""
    openai_request = request.json
    model_name = openai_request.get("model", "gpt-4")
    vertex_model_name = MODEL_MAPPING.get(model_name, "gemini-2.5-pro")
    stream = openai_request.get("stream", False)
    
    is_json_mode = openai_request.get("response_format", {}).get("type") == "json_object"
    
    temperature = openai_request.get("temperature", 0.7)
    max_tokens = openai_request.get("max_tokens")

    logger.info(f"收到请求: model={model_name}, vertex_model={vertex_model_name}, stream={stream}")
    
    generation_config_dict = {
        "temperature": temperature,
        "candidate_count": 1,
    }

    is_vision_request = any(isinstance(msg.get("content"), list) for msg in openai_request.get("messages", []))
    if not is_vision_request and max_tokens is not None:
        generation_config_dict["max_output_tokens"] = max_tokens
    
    generation_config = GenerationConfig(**generation_config_dict)

    if is_json_mode:
        generation_config.response_mime_type = "application/json"

    messages = openai_request.get("messages", [])
    contents, system_instruction = convert_messages_to_vertex_format(messages)
    
    model_params = {}
    if system_instruction:
        model_params["system_instruction"] = system_instruction

    model = GenerativeModel(vertex_model_name, safety_settings=safety_settings, **model_params)
    
    tools_config = openai_request.get("tools")
    tools = []
    if tools_config:
        for tool in tools_config:
            if tool.get("type") == "function":
                function_decl = FunctionDeclaration(
                    name=tool["function"]["name"],
                    description=tool["function"]["description"],
                    parameters=tool["function"]["parameters"]
                )
                tools.append(Tool(function_declarations=[function_decl]))

    if stream:
        return Response(stream_with_context(stream_response(model, contents, generation_config, tools, is_json_mode, model_name)), mimetype="text/event-stream")
    else:
        try:
            response = normal_response(model, contents, generation_config, tools, is_json_mode, model_name)
            if isinstance(response, tuple) and response[1] != 200:
                 return jsonify({"error": {"message": str(response[0]), "type": "server_error"}}), response[1]
            return jsonify(response)
        except Exception as e:
            logger.error(f"处理普通响应时出错: {e}")
            logger.error(traceback.format_exc())
            return jsonify({"error": {"message": str(e), "type": "server_error"}}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
