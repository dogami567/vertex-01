#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查Vertex AI SDK中可用的搜索相关工具
"""

import os
import sys
import inspect
import vertexai
from vertexai.generative_models import Tool, grounding
import google.cloud.aiplatform as aiplatform

# 设置代理
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 初始化Vertex AI
PROJECT_ID = "cursor-use-api"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

def check_methods(obj, name):
    """检查对象的方法和属性"""
    print(f"\n{'='*20} {name} {'='*20}")
    print(f"类型: {type(obj)}")
    
    # 检查方法
    methods = [method for method in dir(obj) if not method.startswith('_')]
    print(f"\n可用方法和属性:")
    for method in methods:
        try:
            attr = getattr(obj, method)
            if inspect.ismethod(attr) or inspect.isfunction(attr):
                signature = str(inspect.signature(attr))
                print(f" - {method}{signature}")
            else:
                print(f" - {method}: {type(attr)}")
        except (TypeError, ValueError) as e:
            print(f" - {method}: 无法获取信息 ({e})")
    
    # 检查类方法 (只对类进行检查)
    if isinstance(obj, type):
        print(f"\n类方法:")
        class_methods = [m[0] for m in inspect.getmembers(obj, predicate=inspect.isfunction)]
        for method in class_methods:
            if not method.startswith('_'):
                try:
                    signature = str(inspect.signature(getattr(obj, method)))
                    print(f" - {method}{signature}")
                except (TypeError, ValueError) as e:
                    print(f" - {method}: 无法获取信息 ({e})")

# 检查Tool类和grounding模块
check_methods(Tool, "Tool类")
check_methods(grounding, "grounding模块")

# 检查是否有Google搜索相关的类
print("\n\n检查是否有Google搜索相关的类:")
has_google_search = hasattr(grounding, "GoogleSearch")
has_google_search_retrieval = hasattr(grounding, "GoogleSearchRetrieval")
print(f"grounding.GoogleSearch 存在: {has_google_search}")
print(f"grounding.GoogleSearchRetrieval 存在: {has_google_search_retrieval}")

if has_google_search:
    check_methods(grounding.GoogleSearch, "GoogleSearch类")
    try:
        print("\n尝试创建GoogleSearch实例:")
        gs = grounding.GoogleSearch()
        print("成功创建GoogleSearch实例")
        check_methods(gs, "GoogleSearch实例")
    except Exception as e:
        print(f"创建GoogleSearch实例时出错: {e}")

if has_google_search_retrieval:
    check_methods(grounding.GoogleSearchRetrieval, "GoogleSearchRetrieval类")
    try:
        print("\n尝试创建GoogleSearchRetrieval实例:")
        gsr = grounding.GoogleSearchRetrieval()
        print("成功创建GoogleSearchRetrieval实例")
        check_methods(gsr, "GoogleSearchRetrieval实例")
    except Exception as e:
        print(f"创建GoogleSearchRetrieval实例时出错: {e}")

# 检查Tool类的from_方法
print("\n\n检查Tool类的from_方法:")
from_methods = [m for m in dir(Tool) if m.startswith('from_')]
for method in from_methods:
    print(f" - {method}")
    try:
        signature = str(inspect.signature(getattr(Tool, method)))
        print(f"   签名: {signature}")
    except (TypeError, ValueError) as e:
        print(f"   无法获取签名: {e}")

print("\n脚本执行完毕") 