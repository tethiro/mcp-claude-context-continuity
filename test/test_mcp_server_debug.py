#!/usr/bin/env python3
"""MCPサーバーのデバッグテスト"""

import asyncio
import sys
import os

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import claude_cli_server

async def test_tools():
    """各ツールを直接テスト"""
    print("=== MCP Server Debug Test ===\n")
    
    # 1. Claude CLIの動作確認
    print("1. Testing test_claude_cli...")
    result = await claude_cli_server.test_claude_cli()
    print(f"Result: {result}")
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Success: {result.get('success')}")
    print()
    
    # 2. 基本的な実行
    print("2. Testing execute_claude...")
    result = await claude_cli_server.execute_claude("こんにちは、私は山田太郎です")
    print(f"Tool name: {result.get('tool_name')}")
    response = result.get('response', '')
    if response:
        print(f"Response: {response[:100]}...")
    else:
        print(f"Response: None")
    print(f"Session ID saved: {claude_cli_server.session_manager.before_session_id}")
    print()
    
    # 3. セッション継続性の確認
    print("3. Testing session continuity...")
    result = await claude_cli_server.execute_claude("私の名前を覚えていますか？")
    print(f"Tool name: {result.get('tool_name')}")
    response = result.get('response', '')
    if response:
        print(f"Response: {response[:100]}...")
    else:
        print(f"Response: None")
    print()
    
    # 4. 実行履歴の確認
    print("4. Testing get_execution_history...")
    result = await claude_cli_server.get_execution_history(limit=5)
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Total entries: {result.get('total_entries')}")
    print(f"Current session: {result.get('current_session_id')}")
    print()
    
    # 5. ファイルコンテキスト
    print("5. Testing execute_claude_with_context...")
    result = await claude_cli_server.execute_claude_with_context(
        "このファイルの目的を一言で説明して",
        "README.md"
    )
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Context file: {result.get('context_file')}")
    response = result.get('response', '')
    if response:
        print(f"Response: {response[:100]}...")
    else:
        print(f"Response: None")
    print()
    
    # 6. 存在しないファイル（エラーテスト）
    print("6. Testing error handling...")
    result = await claude_cli_server.execute_claude_with_context(
        "このファイルを説明して",
        "/tmp/not_exist.txt"
    )
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    print()
    
    # 7. 現在のセッション
    print("7. Testing get_current_session...")
    result = await claude_cli_server.get_current_session()
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Session ID: {result.get('session_id')}")
    print(f"Has session: {result.get('has_session')}")
    print()
    
    # 8. セッションリセット
    print("8. Testing reset_session...")
    result = await claude_cli_server.reset_session()
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Old session ID: {result.get('old_session_id')}")
    print()
    
    # 9. リセット後の確認
    print("9. Testing after reset...")
    result = await claude_cli_server.execute_claude("私の名前を覚えていますか？")
    print(f"Tool name: {result.get('tool_name')}")
    response = result.get('response', '')
    if response:
        print(f"Response: {response[:100]}...")
    else:
        print(f"Response: None")
    print()
    
    # 10. 履歴クリア
    print("10. Testing clear_execution_history...")
    result = await claude_cli_server.clear_execution_history()
    print(f"Tool name: {result.get('tool_name')}")
    print(f"Cleared count: {result.get('cleared_count')}")
    print()

async def main():
    try:
        await test_tools()
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())