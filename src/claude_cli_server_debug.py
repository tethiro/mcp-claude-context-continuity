#!/usr/bin/env python3
"""Claude CLI MCP Server - デバッグ版"""

import sys
import os
import platform
import json
from datetime import datetime

# デバッグ情報をファイルに出力
debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'debug_mcp_startup.log')
with open(debug_log_path, 'w') as f:
    f.write(f"=== MCP Server Debug Log ===\n")
    f.write(f"Started at: {datetime.now().isoformat()}\n")
    f.write(f"Platform: {platform.system()}\n")
    f.write(f"Python: {sys.version}\n")
    f.write(f"Current directory: {os.getcwd()}\n")
    f.write(f"Script path: {__file__}\n")
    f.write(f"Python path: {sys.path[:3]}\n")

try:
    # Windowsでのインポートエラーを回避するためにsys.pathに追加
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        with open(debug_log_path, 'a') as f:
            f.write(f"\nAdded to sys.path: {current_dir}\n")
    
    # メインのclaude_cli_serverをインポート
    from claude_cli_server import *
    
    with open(debug_log_path, 'a') as f:
        f.write(f"\n✅ Successfully imported claude_cli_server\n")
        f.write(f"MCP instance: {mcp}\n")
        
    # ツールの登録状況を確認
    import asyncio
    async def check_tools():
        tools = await mcp.list_tools()
        with open(debug_log_path, 'a') as f:
            f.write(f"\nRegistered tools: {len(tools)}\n")
            for tool in tools:
                f.write(f"  - {tool.name}\n")
    
    # ツールチェックを実行
    asyncio.run(check_tools())
    
except Exception as e:
    with open(debug_log_path, 'a') as f:
        f.write(f"\n❌ Error: {type(e).__name__}: {e}\n")
        import traceback
        f.write(traceback.format_exc())
    raise

# メインエントリーポイント
if __name__ == "__main__":
    with open(debug_log_path, 'a') as f:
        f.write(f"\nStarting MCP server via stdio...\n")
    
    # stdio経由でサーバーを起動
    asyncio.run(mcp.run_stdio_async())