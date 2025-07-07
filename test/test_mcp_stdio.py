#!/usr/bin/env python3
"""MCPサーバーのstdio通信をテストするスクリプト"""

import sys
import os
import json
import asyncio
import subprocess

def test_mcp_initialization():
    """MCPサーバーの初期化をテスト"""
    print("Testing MCP Server initialization...")
    
    # 初期化リクエスト
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    # Pythonスクリプトのパスを取得
    # script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'claude_cli_server.py')
    script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'minimal_mcp_server.py')
    script_path = os.path.abspath(script_path)
    
    print(f"Script path: {script_path}")
    
    # MCPサーバーを起動
    try:
        if sys.platform == "win32":
            # Windows環境
            cmd = ["python", script_path]
        else:
            # Unix環境
            cmd = ["python3", script_path]
            
        print(f"Running command: {' '.join(cmd)}")
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 初期化リクエストを送信
        request_str = json.dumps(init_request) + "\n"
        print(f"Sending: {request_str.strip()}")
        
        proc.stdin.write(request_str)
        proc.stdin.flush()
        
        # レスポンスを読み取る
        response_line = proc.stdout.readline()
        if response_line:
            print(f"Received: {response_line.strip()}")
            response = json.loads(response_line)
            
            if "result" in response:
                print("\n✅ Server initialized successfully!")
                print(f"Server name: {response['result']['serverInfo']['name']}")
                print(f"Server version: {response['result']['serverInfo']['version']}")
                
                # ツール一覧を要求
                tools_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 2
                }
                
                request_str = json.dumps(tools_request) + "\n"
                print(f"\nSending tools/list request...")
                proc.stdin.write(request_str)
                proc.stdin.flush()
                
                response_line = proc.stdout.readline()
                if response_line:
                    print(f"Received: {response_line.strip()}")
                    response = json.loads(response_line)
                    if "result" in response and "tools" in response["result"]:
                        tools = response["result"]["tools"]
                        print(f"\n✅ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"  - {tool['name']}")
                    else:
                        print("\n❌ No tools found in response")
                        print(f"Response: {json.dumps(response, indent=2)}")
                else:
                    print("\n❌ No response for tools/list")
                    # エラー出力を確認
                    stderr_output = proc.stderr.read()
                    if stderr_output:
                        print(f"Server stderr:\n{stderr_output}")
            else:
                print("\n❌ Server initialization failed")
                print(f"Error: {response.get('error', 'Unknown error')}")
        else:
            print("\n❌ No response from server")
            
        # サーバーを終了
        proc.terminate()
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_initialization()