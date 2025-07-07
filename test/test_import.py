#!/usr/bin/env python3
"""インポートエラーをチェックするテスト"""

import sys
import os

print("Python:", sys.version)
print("Path:", sys.path[:3])

try:
    # FastMCPのインポートテスト
    print("\nTrying to import FastMCP...")
    from mcp.server.fastmcp import FastMCP
    print("✅ FastMCP imported successfully")
except Exception as e:
    print(f"❌ FastMCP import error: {type(e).__name__}: {e}")

try:
    # claude_cli_serverのインポートテスト
    print("\nTrying to import claude_cli_server...")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    import claude_cli_server
    print("✅ claude_cli_server imported successfully")
    # FastMCPのツール情報を取得
    print("✅ Checking MCP tools...")
    print(f"MCP instance: {claude_cli_server.mcp}")
    print(f"Available attributes: {[attr for attr in dir(claude_cli_server.mcp) if not attr.startswith('_')]}")
except Exception as e:
    print(f"❌ claude_cli_server import error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()