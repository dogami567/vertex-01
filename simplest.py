#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最简单的Vertex AI到OpenAI API适配器
支持：
- 基本聊天功能
- 流式响应
- 函数调用
- 视觉模型
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
from vertexai.generative_models import GenerativeModel, Part, Content, Tool, FunctionDeclaration, GenerationConfig
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

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
    "gpt-4o": "gemini-2.5-pro",
    "gpt-3.5-turbo": "gemini-2.5-pro",  # 按用户要求，默认使用2.5-pro
    "gpt-3.5-turbo-16k": "gemini-2.5-pro",  # 按用户要求，默认使用2.5-pro
    "gpt-4-vision-preview": "gemini-2.5-pro-vision",
    # 原始Gemini模型名称也支持
    "gemini-pro": "gemini-2.5-pro",
    "gemini-flash": "gemini-2.5-pro",  # 按用户要求，默认使用2.5-pro
}

# 初始化Vertex AI
try:
    logger.info(f"正在初始化Vertex AI (项目: {PROJECT_ID}, 区域: {LOCATION})...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logger.info("Vertex AI 初始化成功。")
except Exception as e:
    logger.error(f"初始化Vertex AI失败: {e}")

# 安全设置 (禁用所有安全过滤器)
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# 辅助函数：将OpenAI请求转换为Vertex AI请求
def convert_openai_to_vertex(openai_request, model_name):
    messages = openai_request.get("messages", [])
    vertex_contents = []
    
    # 检查是否有图像内容
    has_image = False
    for msg in messages:
        if msg.get("role") == "user" and msg.get("content") and isinstance(msg["content"], list):
            for content_part in msg["content"]:
                if content_part.get("type") == "image_url":
                    has_image = True
                    break
    
    # 如果有图像内容，使用支持视觉的模型
    if has_image and "vision" not in model_name:
        logger.info("检测到视觉请求，使用支持视觉的模型")
        model_name = "gemini-2.5-pro-vision"
    
    # 转换消息格式
    for msg in messages:
        role = msg.get("role", "user")
        
        # 映射角色
        if role == "system":
            role = "user"
        elif role == "assistant":
            role = "model"
        
        # 处理内容
        content = msg.get("content", "")
        
        # 处理多模态内容（如图像）
        if isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "text":
                    parts.append(part.get("text", ""))
                elif part.get("type") == "image_url":
                    image_url = part.get("image_url", {})
                    if isinstance(image_url, dict) and "url" in image_url:
                        url = image_url["url"]
                        # 处理base64图像
                        if url.startswith("data:image"):
                            try:
                                # 提取base64部分
                                base64_data = url.split(",")[1]
                                image_bytes = base64.b64decode(base64_data)
                                parts.append(Part.from_data(mime_type="image/jpeg", data=image_bytes))
                            except Exception as e:
                                logger.error(f"处理base64图像时出错: {str(e)}")
                        else:
                            # 处理URL图像
                            parts.append(Part.from_uri(uri=url))
            
            vertex_contents.append(Content(role=role, parts=parts))
        else:
            # 处理纯文本内容
            vertex_contents.append(Content(role=role, parts=[content]))
    
    # 处理函数调用工具
    tools = None
    if "tools" in openai_request:
        openai_tools = openai_request.get("tools", [])
        vertex_tools = []
        
        for tool in openai_tools:
            if tool.get("type") == "function":
                function_spec = tool.get("function", {})
                
                # 转换函数声明
                function = FunctionDeclaration(
                    name=function_spec.get("name", ""),
                    description=function_spec.get("description", ""),
                    parameters=function_spec.get("parameters", {})
                )
                
                vertex_tools.append(Tool(function_declarations=[function]))
        
        if vertex_tools:
            logger.info(f"转换函数调用工具: {len(vertex_tools)} 个工具")
            tools = vertex_tools
    
    # 处理生成配置
    generation_config = {}
    
    if "temperature" in openai_request:
        generation_config["temperature"] = openai_request["temperature"]
    
    if "max_tokens" in openai_request:
        generation_config["max_output_tokens"] = openai_request["max_tokens"]
    
    if "top_p" in openai_request:
        generation_config["top_p"] = openai_request["top_p"]
    
    # 返回转换后的请求
    return {
        "contents": vertex_contents,
        "tools": tools,
        "generation_config": generation_config if generation_config else None,
        "stream": openai_request.get("stream", False)
    }

# 辅助函数：将Vertex AI响应转换为OpenAI响应
def convert_vertex_to_openai(response, model_name):
    """将Vertex AI的非流式响应转换为OpenAI格式"""
    # ... (code for this function will be updated) ...
    # This function needs to be robust against safety-blocked responses.
    pass

# 辅助函数：创建标准格式的OpenAI流式响应块
def _create_openai_stream_chunk(model_name, content, finish_reason=None):
    """创建标准格式的OpenAI流式响应块"""
    return {
        "id": f"chatcmpl-{str(uuid.uuid4())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model_name,
        "choices": [{
            "index": 0,
            "delta": {"content": content} if content else {},
            "finish_reason": finish_reason
        }]
    }

def stream_response(model, content_list, generation_config, tools):
    """处理流式响应"""
    def generate():
        try:
            responses = model.generate_content(
                content_list,
                generation_config=generation_config,
                tools=tools,
                stream=True,
                safety_settings=safety_settings  # 应用安全设置
            )
            
            # 初始化文本缓冲区和函数调用标志
            text_buffer = ""
            function_call_sent = False
            sentence_endings = ['.', '!', '?', '。', '！', '？', '\n']
            min_chunk_size = 15  # 最小块大小（字符数）
            
            for response in responses:
                # 检查是否有函数调用，如果有，直接发送
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'function_calls') and candidate.function_calls and not function_call_sent:
                        chunk = convert_to_openai_stream_format(response, model._model_name, is_function_call=True)
                        function_call_sent = True
                        yield f"data: {json.dumps(chunk)}\n\n"
                        continue
                
                # 提取文本内容
                current_text = ""
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    current_text = part.text
                                    break
                        elif hasattr(candidate.content, 'text'):
                            current_text = candidate.content.text
                
                # 将当前文本添加到缓冲区
                if current_text:
                    text_buffer += current_text
                    
                    # 检查是否应该发送缓冲区内容
                    should_send = False
                    
                    # 检查是否有句子结束符
                    for ending in sentence_endings:
                        if ending in text_buffer:
                            should_send = True
                            break
                    
                    # 如果缓冲区足够大，也发送
                    if len(text_buffer) >= min_chunk_size:
                        should_send = True
                    
                    # 如果应该发送，创建并发送块
                    if should_send:
                        chunk = convert_to_openai_stream_format(response, model._model_name, buffered_text=text_buffer)
                        text_buffer = ""  # 清空缓冲区
                        yield f"data: {json.dumps(chunk)}\n\n"
            
            # 发送任何剩余的缓冲区内容
            if text_buffer:
                final_chunk = {
                    "id": f"chatcmpl-{str(uuid.uuid4())}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model._model_name,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": text_buffer},
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in stream_response generate(): {e}\n{traceback.format_exc()}")
            error_chunk = {"error": {"message": str(e), "type": "stream_error"}}
            yield f"data: {json.dumps(error_chunk)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def convert_to_openai_stream_format(chunk, model_name, buffered_text=None, is_function_call=False):
    """将Vertex AI的流式响应块转换为OpenAI流式格式"""
    try:
        # 如果提供了缓冲文本，直接使用它
        if buffered_text is not None:
            return {
                "id": f"chatcmpl-{str(uuid.uuid4())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "delta": {"content": buffered_text},
                    "finish_reason": None
                }]
            }
            
        # 如果是函数调用请求
        if is_function_call and hasattr(chunk, 'candidates') and chunk.candidates:
            candidate = chunk.candidates[0]
            if hasattr(candidate, 'function_calls') and candidate.function_calls:
                for fc in candidate.function_calls:
                    # 添加对 fc 是否为 None 的检查
                    if fc is None:
                        logger.warning("Received None function call in stream response")
                        continue
                        
                    try:
                        # 确保 fc 有 name 和 args 属性
                        if not hasattr(fc, 'name') or not hasattr(fc, 'args'):
                            logger.warning(f"Function call missing required attributes: {fc}")
                            continue
                            
                        tool_call_id = str(uuid.uuid4())
                        return {
                            "id": f"chatcmpl-{str(uuid.uuid4())}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model_name,
                            "choices": [{
                                "index": 0,
                                "delta": {
                                    "tool_calls": [{
                                        "index": 0,
                                        "id": tool_call_id,
                                        "type": "function",
                                        "function": {"name": fc.name, "arguments": json.dumps(fc.args)}
                                    }]
                                },
                                "finish_reason": None
                            }]
                        }
                    except Exception as e:
                        logger.error(f"Error processing function call in stream: {e}")
                        continue

        # 对于普通的流式响应，返回空块（因为我们使用缓冲区）
        return {
            "id": f"chatcmpl-{str(uuid.uuid4())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": None
            }]
        }
        
    except Exception as e:
        logger.error(f"Error converting stream chunk: {e}\n{traceback.format_exc()}")
        return {
            "id": f"chatcmpl-{str(uuid.uuid4())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "index": 0,
                "delta": {"content": f"[ERROR: {str(e)}]"},
                "finish_reason": "error"
            }]
        }

# API路由：获取模型列表
@app.route("/v1/models", methods=["GET"])
def list_models():
    """列出可用的模型"""
    models = []
    for openai_model, vertex_model in MODEL_MAPPING.items():
        models.append({
            "id": openai_model,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "vertex-ai"
        })
    
    return jsonify({
        "object": "list",
        "data": models
    })

# API路由：聊天完成
@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """处理聊天完成请求"""
    try:
        data = request.json
        logger.debug(f"收到请求: {json.dumps(data)}")
        
        # 获取模型名称
        model_name = data.get('model', 'gpt-3.5-turbo')
        vertex_model_name = MODEL_MAPPING.get(model_name, "gemini-2.5-flash")
        logger.info(f"使用模型: {vertex_model_name}")
        
        # 检查是否为流式请求
        stream = data.get('stream', False)
        
        # 处理消息
        messages = data.get('messages', [])
        logger.debug(f"处理消息: {json.dumps(messages)}")
        
        # 检查是否有函数定义
        tools = data.get('tools', [])
        vertex_tools = None
        
        if tools:
            logger.info(f"转换函数调用工具: {len(tools)} 个工具")
            vertex_tools = []
            for tool in tools:
                if tool.get('type') == 'function':
                    function_info = tool.get('function', {})
                    vertex_tools.append(
                        Tool(
                            function_declarations=[
                                FunctionDeclaration(
                                    name=function_info.get('name', ''),
                                    description=function_info.get('description', ''),
                                    parameters=function_info.get('parameters', {})
                                )
                            ]
                        )
                    )
        
        # 检查是否有视觉内容
        has_image = False
        for message in messages:
            if message.get('role') == 'user' and message.get('content'):
                content = message.get('content')
                if isinstance(content, list):
                    for item in content:
                        if item.get('type') == 'image_url':
                            has_image = True
                            break
        
        # 如果有图像，使用支持视觉的模型
        if has_image:
            logger.info("检测到视觉请求，使用支持视觉的模型")
            vertex_model_name = "gemini-2.5-pro"
        
        # 创建模型实例
        model = GenerativeModel(vertex_model_name)
        
        # 构建生成配置
        generation_config = GenerationConfig(
            temperature=data.get('temperature', 0.7),
            top_p=data.get('top_p', 0.95),
            top_k=data.get('top_k', 40),
            max_output_tokens=data.get('max_tokens', 8192),
        )
        
        # 构建提示
        content_list = []
        
        for message in messages:
            role = message.get('role')
            content = message.get('content')
            
            if role == 'system':
                # 系统消息作为用户消息添加
                content_list.append(Content(role="user", parts=[Part.from_text(f"System instruction: {content}")]))
                content_list.append(Content(role="model", parts=[Part.from_text("I'll follow these instructions.")]))
            elif role == 'assistant':
                # 助手消息
                content_list.append(Content(role="model", parts=[Part.from_text(content)]))
            elif role == 'user':
                # 用户消息
                if isinstance(content, str):
                    content_list.append(Content(role="user", parts=[Part.from_text(content)]))
                elif isinstance(content, list):
                    # 处理多模态内容
                    parts = []
                    for item in content:
                        if item.get('type') == 'text':
                            parts.append(Part.from_text(item.get('text', '')))
                        elif item.get('type') == 'image_url':
                            image_url = item.get('image_url', {})
                            if isinstance(image_url, dict) and 'url' in image_url:
                                url = image_url.get('url', '')
                                if url.startswith('data:image'):
                                    try:
                                        # 处理base64编码的图像
                                        image_data = url.split(',')[1]
                                        image_bytes = base64.b64decode(image_data)
                                        parts.append(Part.from_data(mime_type="image/jpeg", data=image_bytes))
                                    except Exception as e:
                                        logger.error(f"处理base64图像时出错: {e}")
                                else:
                                    parts.append(Part.from_uri(url))
                    
                    if parts:
                        content_list.append(Content(role="user", parts=parts))
        
        # 确保内容列表不为空
        if not content_list:
            # 如果没有有效的消息，添加一个默认消息
            content_list.append(Content(role="user", parts=[Part.from_text("Hello")]))
            logger.warning("没有有效的消息内容，使用默认消息")
        
        if stream:
            logger.info("处理流式请求")
            return stream_response(model, content_list, generation_config, vertex_tools)
        else:
            logger.info("处理普通请求")
            return normal_response(model, content_list, generation_config, vertex_tools)
    except Exception as e:
        logger.error(f"处理请求时出错: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": {
                "message": str(e),
                "type": "server_error",
                "code": 500
            }
        }), 500

def normal_response(model, content_list, generation_config, tools):
    """处理非流式响应"""
    try:
        response = model.generate_content(
            content_list,
            generation_config=generation_config,
            tools=tools,
            safety_settings=safety_settings  # 应用安全设置
        )
        openai_response = convert_to_openai_format(response, model._model_name)
        return jsonify(openai_response)
    except Exception as e:
        logger.error(f"Error in normal_response: {e}\n{traceback.format_exc()}")
        return jsonify({"error": f"Failed to generate content: {e}"}), 500

def convert_to_openai_format(response, model_name):
    """将Vertex AI的非流式响应转换为OpenAI格式"""
    try:
        if not hasattr(response, 'candidates') or not response.candidates:
            content = f"Response has no candidates. Raw response: {response}"
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                content = f"Prompt was blocked with reason: {response.prompt_feedback.block_reason_message}"
            return _create_openai_response_format(model_name, content, "error")

        candidate = response.candidates[0]
        
        # 1. Check for function calls
        if hasattr(candidate, 'function_calls') and candidate.function_calls:
            tool_calls = []
            for fc in candidate.function_calls:
                args_dict = {key: value for key, value in fc.args.items()}
                tool_calls.append({
                    "id": f"call_{uuid.uuid4().hex[:8]}",
                    "type": "function",
                    "function": {
                        "name": fc.name,
                        "arguments": json.dumps(args_dict)
                    }
                })
            return _create_openai_response_format(model_name, None, "tool_calls", tool_calls=tool_calls)

        # 2. Try to get text content, handling failures gracefully
        try:
            content = candidate.text
            finish_reason = "stop" # Default
            if hasattr(candidate, 'finish_reason'):
                reason_name = candidate.finish_reason.name
                if reason_name == "MAX_TOKENS":
                    finish_reason = "length"
                elif reason_name == "SAFETY":
                    finish_reason = "content_filter"
                elif reason_name not in ("STOP", "FINISH_REASON_UNSPECIFIED"):
                    finish_reason = reason_name.lower()
            return _create_openai_response_format(model_name, content, finish_reason)
        except ValueError as e:
            logger.warning(f"Could not get text from candidate, likely blocked. Error: {e}")
            content = f"[ERROR] Response content blocked or empty. Finish Reason: {candidate.finish_reason.name}"
            return _create_openai_response_format(model_name, content, "content_filter")

    except Exception as e:
        logger.error(f"Error converting to OpenAI format: {e}\n{traceback.format_exc()}")
        return _create_openai_response_format(model_name, f"[ERROR] Conversion failed: {e}", "error")

def _create_openai_response_format(model, content, finish_reason, tool_calls=None):
    """一个辅助函数，用于创建OpenAI格式的响应字典"""
    message = {"role": "assistant"}
    if content:
        message["content"] = content
    if tool_calls:
        message["tool_calls"] = tool_calls

    return {
        "id": f"chatcmpl-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": message,
            "finish_reason": finish_reason
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

# 主程序入口
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
