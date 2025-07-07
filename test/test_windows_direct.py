#!/usr/bin/env python3
"""Windows環境で直接MCPサーバーを起動するテスト"""

import sys
import os
import asyncio
import json

async def test_mcp_server():
    # claude_cli_serverのインポート
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    import claude_cli_server
    
    print("MCP Server Test")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # ツール一覧を取得
    try:
        tools = await claude_cli_server.mcp.list_tools()
        print(f"\nRegistered tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}")
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # テストでexecute_claudeを呼び出す
    try:
        print("\nTesting execute_claude...")
        result = await claude_cli_server.execute_claude("echo test")
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error executing claude: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())