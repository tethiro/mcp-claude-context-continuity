#!/usr/bin/env python3
"""Claude CLI MCP Server - WSLデバッグ版"""

import sys
import os
import datetime

# デバッグログファイル
debug_file = os.path.join(os.path.dirname(__file__), '..', 'mcp_debug_wsl.log')

def debug_log(message):
    """デバッグメッセージをファイルに記録"""
    with open(debug_file, 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        f.flush()

debug_log("=== MCP Server Starting (WSL Debug) ===")
debug_log(f"Python: {sys.version}")
debug_log(f"Platform: {sys.platform}")
debug_log(f"CWD: {os.getcwd()}")
debug_log(f"__file__: {__file__}")

# 元のサーバーをインポート
try:
    from claude_cli_server import *
    debug_log("Successfully imported claude_cli_server")
except Exception as e:
    debug_log(f"Failed to import: {e}")
    raise

# FastMCPのrun_stdio_asyncをラップ
original_run = mcp.run_stdio_async

async def debug_run():
    """デバッグ情報付きでサーバーを起動"""
    debug_log("Starting MCP stdio server...")
    try:
        await original_run()
    except Exception as e:
        debug_log(f"Server error: {type(e).__name__}: {e}")
        raise
    finally:
        debug_log("Server stopped")

mcp.run_stdio_async = debug_run

if __name__ == "__main__":
    debug_log("Main block executing...")
    import asyncio
    asyncio.run(mcp.run_stdio_async())