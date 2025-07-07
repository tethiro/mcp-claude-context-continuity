#!/usr/bin/env python3
"""MCPサーバーを直接呼び出してデバッグ"""

import asyncio
import sys
import os

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import claude_cli_server

async def test_execute_claude():
    """execute_claudeを直接テスト"""
    print("=== Direct MCP Call Test ===\n")
    
    print("1. Testing execute_claude with 'こんにちは'...")
    try:
        result = await claude_cli_server.execute_claude("こんにちは")
        print(f"Success: {result.get('success')}")
        print(f"Response: {result.get('response')}")
        print(f"Execution time: {result.get('execution_time')}s")
        print(f"Error: {result.get('error')}")
        print(f"Session ID: {claude_cli_server.session_manager.before_session_id}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_execute_claude()

if __name__ == "__main__":
    # イベントループポリシーを設定（Windows互換性のため）
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())