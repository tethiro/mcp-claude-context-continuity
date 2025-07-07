#!/usr/bin/env python3
"""ツール登録をチェックするテスト（非同期版）"""

import sys
import os
import asyncio

async def main():
    print("Python:", sys.version)

    # claude_cli_serverのインポート
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    import claude_cli_server

    print("\nChecking MCP instance...")
    print(f"MCP instance: {claude_cli_server.mcp}")

    print("\nChecking registered tools...")
    try:
        # ツール一覧を取得
        tools = await claude_cli_server.mcp.list_tools()
        print(f"Number of tools: {len(tools)}")
        
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"Error listing tools: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\nChecking tool attributes...")
    # デコレータが正しく機能しているか確認
    print(f"execute_claude function: {claude_cli_server.execute_claude}")
    
    # mcp._toolsを直接確認
    if hasattr(claude_cli_server.mcp, '_tools'):
        print(f"\nDirect access to _tools: {claude_cli_server.mcp._tools}")
    
    # デコレータの適用を確認
    if hasattr(claude_cli_server.execute_claude, '__mcp_tool__'):
        print(f"execute_claude has __mcp_tool__ attribute")
    else:
        print(f"execute_claude does NOT have __mcp_tool__ attribute")

if __name__ == "__main__":
    asyncio.run(main())