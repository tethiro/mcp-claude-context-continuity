#!/usr/bin/env python3
"""WSL環境でのMCP stdio通信テスト"""

import subprocess
import json
import time

def test_mcp_stdio():
    """MCP stdioプロトコルでの通信テスト"""
    print("=== MCP stdio Test (WSL) ===\n")
    
    # MCPサーバーを起動
    cmd = ["python3", "/mnt/c/prj/AI/prg/mcp-claude-context-continuity/src/claude_cli_server.py"]
    print(f"Starting MCP server: {' '.join(cmd)}")
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # テストリクエスト（MCP仕様に従ったJSON-RPC）
    requests = [
        # 1. Initialize
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": 1
        },
        # 2. List tools
        {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        },
        # 3. Call test_claude_cli
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "test_claude_cli",
                "arguments": {}
            },
            "id": 3
        },
        # 4. Call execute_claude
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "execute_claude",
                "arguments": {
                    "prompt": "こんにちは"
                }
            },
            "id": 4
        }
    ]
    
    for i, request in enumerate(requests, 1):
        print(f"\n{i}. Sending request: {request['method']}")
        request_str = json.dumps(request) + "\n"
        
        try:
            # リクエスト送信
            proc.stdin.write(request_str)
            proc.stdin.flush()
            
            # 応答を待つ（タイムアウト付き）
            start_time = time.time()
            response_line = ""
            
            # ノンブロッキングで読み取り
            import select
            timeout = 10  # 10秒タイムアウト
            
            ready, _, _ = select.select([proc.stdout], [], [], timeout)
            if ready:
                response_line = proc.stdout.readline()
                elapsed = time.time() - start_time
                
                if response_line:
                    try:
                        response = json.loads(response_line)
                        print(f"Response ({elapsed:.2f}s):")
                        print(json.dumps(response, indent=2, ensure_ascii=False)[:500])
                    except json.JSONDecodeError:
                        print(f"Invalid JSON response: {response_line[:200]}")
                else:
                    print("No response received")
            else:
                print(f"Timeout after {timeout}s")
                
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
    
    # エラー出力を確認
    print("\n=== stderr ===")
    try:
        import select
        ready, _, _ = select.select([proc.stderr], [], [], 0.1)
        if ready:
            stderr_content = proc.stderr.read()
            if stderr_content:
                print(stderr_content[:1000])
        else:
            print("No stderr output")
    except:
        pass
    
    # プロセスを終了
    proc.terminate()
    proc.wait()
    print("\nTest completed")

if __name__ == "__main__":
    test_mcp_stdio()