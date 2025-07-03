#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试API服务器 - 提供前端测试页面并解决跨域问题
"""

import os
from flask import Flask, send_from_directory, request, jsonify, Response
import requests
import json
import sys
import traceback

app = Flask(__name__)

# 适配器API配置
ADAPTER_URL = "http://localhost:5001/v1"
API_KEY = "sk-test123456789"

# 设置CORS头，允许所有来源访问
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

# 提供前端测试页面
@app.route('/')
def index():
    return send_from_directory('.', 'test_frontend.html')

# 代理API请求到适配器
@app.route('/proxy/<path:endpoint>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_request(endpoint):
    if request.method == 'OPTIONS':
        return '', 200
    
    url = f"{ADAPTER_URL}/{endpoint}"
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 从请求中获取授权头
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['Authorization'] = auth_header
    else:
        headers['Authorization'] = f"Bearer {API_KEY}"
    
    try:
        if request.method == 'GET':
            response = requests.get(url, headers=headers)
            return response.content, response.status_code, {'Content-Type': response.headers.get('Content-Type')}
        elif request.method == 'POST':
            # 获取请求体
            json_data = request.get_json(silent=True)
            
            # 检查是否是流式请求
            is_stream = False
            if json_data and json_data.get('stream', False):
                is_stream = True
            
            if is_stream:
                # 处理流式响应
                def generate():
                    try:
                        # 转发请求到适配器
                        stream_response = requests.post(
                            url, 
                            headers=headers, 
                            json=json_data,
                            stream=True
                        )
                        
                        # 检查响应状态
                        if stream_response.status_code != 200:
                            yield f"data: {{\"error\": \"适配器返回错误: {stream_response.status_code}\"}}\n\n"
                            yield "data: [DONE]\n\n"
                            return
                        
                        # 转发流式数据
                        for chunk in stream_response.iter_content(chunk_size=None):
                            if chunk:
                                yield chunk.decode('utf-8')
                    except Exception as e:
                        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
                        yield "data: [DONE]\n\n"
                
                return app.response_class(
                    generate(),
                    content_type='text/event-stream'
                )
            else:
                # 处理普通请求
                response = requests.post(url, headers=headers, json=json_data)
                return response.content, response.status_code, {'Content-Type': response.headers.get('Content-Type')}
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"请求适配器时出错: {e}"}), 502

@app.route('/run-tests', methods=['GET'])
def run_tests():
    """执行后端自动化测试并返回结果"""
    def generate():
        try:
            import subprocess
            import sys
            
            logger.info("开始执行后端测试...")
            command = [sys.executable, 'run_all_tests.py']
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace', # 替换任何编码错误
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            yield f"data: {json.dumps({'output': '--- 开始执行后端测试 ---'})}\\n\\n"
            
            for line in iter(process.stdout.readline, ''):
                yield f"data: {json.dumps({'output': line})}\\n\\n"
            
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                yield f"data: {json.dumps({'output': '--- 所有测试通过 ---'})}\\n\\n"
            else:
                yield f"data: {json.dumps({'output': f'--- 测试失败，退出码: {return_code} ---'})}\\n\\n"

        except Exception as e:
            error_message = f"执行测试脚本时发生严重错误: {traceback.format_exc()}"
            logger.error(error_message)
            yield f"data: {json.dumps({'output': error_message})}\\n\\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    print("启动测试API服务器...")
    print("前端测试页面: http://localhost:5002/")
    app.run(host='0.0.0.0', port=5002, debug=True) 