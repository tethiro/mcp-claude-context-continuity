#!/usr/bin/env python3
"""ツール登録をチェックするテスト"""

import sys
import os

print("Python:", sys.version)

# claude_cli_serverのインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import claude_cli_server

print("\nChecking MCP instance...")
print(f"MCP instance: {claude_cli_server.mcp}")

print("\nChecking registered tools...")
try:
    # ツール一覧を取得
    tools = claude_cli_server.mcp.list_tools()
    print(f"Number of tools: {len(tools)}")
    
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
        
except Exception as e:
    print(f"Error listing tools: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\nChecking tool decorator...")
# デコレータが正しく機能しているか確認
print(f"execute_claude function: {claude_cli_server.execute_claude}")
print(f"Is coroutine: {claude_cli_server.execute_claude.__class__.__name__}")