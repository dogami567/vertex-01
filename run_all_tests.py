#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
综合测试运行脚本 - 使用gemini-2.5-pro
"""

import os
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 清除环境变量并设置代理
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# 创建Rich控制台
console = Console()

def print_header(title):
    """打印带格式的标题"""
    console.print(f"\n[bold blue]{'=' * 60}[/bold blue]")
    console.print(f"[bold white on blue]{title.center(60)}[/bold white on blue]")
    console.print(f"[bold blue]{'=' * 60}[/bold blue]\n")

def run_test(name, command):
    """运行单个测试"""
    print_header(f"运行{name}测试")
    console.print(f"[bold cyan]执行命令:[/bold cyan] {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        console.print(Panel(result.stdout, title=f"[green]{name}测试结果", border_style="green"))
        return True
    except subprocess.CalledProcessError as e:
        console.print(Panel(f"错误代码: {e.returncode}\n\n{e.stdout}\n\n{e.stderr}", 
                           title=f"[red]{name}测试失败", border_style="red"))
        return False

def main():
    """主函数 - 运行所有测试"""
    print_header("Vertex AI 到 OpenAI API 适配器全面测试")
    
    # 测试结果表格
    results_table = Table(title="测试结果汇总")
    results_table.add_column("测试名称", style="cyan")
    results_table.add_column("状态", style="bold")
    
    # 先启动适配器服务器
    console.print("[yellow]注意: 请确保适配器服务器已经启动[/yellow]")
    console.print("[yellow]如果尚未启动，请在另一个终端执行:[/yellow]")
    console.print("[bold]$env:GOOGLE_APPLICATION_CREDENTIALS=\"\"; $env:HTTPS_PROXY=\"http://127.0.0.1:7890\"; python vertex-openai-adapter/simplest.py[/bold]")
    
    input("\n按回车键继续测试...")
    
    # 1. 基本测试
    basic_test = run_test("基本连接", "python vertex-openai-adapter/test_vertexai_direct.py")
    results_table.add_row("基本连接测试", "[green]通过[/green]" if basic_test else "[red]失败[/red]")
    
    # 2. API适配器测试
    adapter_test = run_test("API适配器", "python vertex-openai-adapter/call_adapter.py")
    results_table.add_row("API适配器测试", "[green]通过[/green]" if adapter_test else "[red]失败[/red]")
    
    # 3. 流式响应测试
    stream_test = run_test("流式响应", "python vertex-openai-adapter/test_all_features.py --test streaming_chat")
    results_table.add_row("流式响应测试", "[green]通过[/green]" if stream_test else "[red]失败[/red]")
    
    # 4. 视觉功能测试
    vision_test = run_test("视觉功能", "python vertex-openai-adapter/test_vision.py")
    results_table.add_row("视觉功能测试", "[green]通过[/green]" if vision_test else "[red]失败[/red]")
    
    # 5. 函数调用测试
    function_test = run_test("函数调用", "python vertex-openai-adapter/test_function_calling.py")
    results_table.add_row("函数调用测试", "[green]通过[/green]" if function_test else "[red]失败[/red]")
    
    # 6. 流式函数调用测试
    stream_function_test = run_test("流式函数调用", "python vertex-openai-adapter/test_function_calling.py --stream")
    results_table.add_row("流式函数调用测试", "[green]通过[/green]" if stream_function_test else "[red]失败[/red]")
    
    # 打印结果表格
    console.print("\n")
    console.print(results_table)
    
    # 计算通过率
    total_tests = 6
    passed_tests = sum([basic_test, adapter_test, stream_test, vision_test, function_test, stream_function_test])
    pass_rate = (passed_tests / total_tests) * 100
    
    # 打印总结
    console.print(f"\n[bold]测试完成: {passed_tests}/{total_tests} 通过 ({pass_rate:.1f}%)[/bold]")
    
    if passed_tests == total_tests:
        console.print("\n[bold green]✅ 所有测试通过![/bold green]")
    else:
        console.print(f"\n[bold yellow]⚠️ {total_tests - passed_tests}个测试失败，请检查详细日志[/bold yellow]")

if __name__ == "__main__":
    main() 