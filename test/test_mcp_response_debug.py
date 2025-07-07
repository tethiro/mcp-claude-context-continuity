#!/usr/bin/env python3
"""MCP応答デバッグテスト"""

import sys
import os
import json

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# FastMCPをインポートする前にstdoutをキャプチャ
original_stdout = sys.stdout
original_stderr = sys.stderr

# ログファイルに出力を記録
log_file = open('/tmp/mcp_response_debug.log', 'w')

class TeeOutput:
    def __init__(self, *files):
        self.files = files
    
    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()

# stdoutとstderrをキャプチャ
sys.stdout = TeeOutput(original_stdout, log_file)
sys.stderr = TeeOutput(original_stderr, log_file)

import asyncio
import claude_cli_server

async def test_mcp_response():
    """MCP応答をデバッグ"""
    print("=== MCP Response Debug ===\n", flush=True)
    
    # 1. test_claude_cli（成功する）
    print("1. Testing test_claude_cli...", flush=True)
    result = await claude_cli_server.test_claude_cli()
    print(f"Result type: {type(result)}", flush=True)
    print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}", flush=True)
    
    # 2. execute_claude（タイムアウトする）
    print("\n2. Testing execute_claude...", flush=True)
    try:
        result = await claude_cli_server.execute_claude("こんにちは")
        print(f"Result type: {type(result)}", flush=True)
        print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}", flush=True)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    print("\nTest completed", flush=True)

async def main():
    await test_mcp_response()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # ファイルを閉じる
        log_file.close()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        
        # ログファイルの内容を表示
        print("\n=== Log file content ===")
        with open('/tmp/mcp_response_debug.log', 'r') as f:
            print(f.read())