#!/usr/bin/env python3
"""Claude CLI MCPサーバーの簡単な動作確認テスト"""

import asyncio
import sys
import os
import platform

# srcディレクトリをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_cli_server import session_manager, execute_claude, get_current_session, reset_session

async def test_basic_functionality():
    """基本機能のテスト"""
    print("=" * 60)
    print("Claude CLI MCPサーバー 動作確認テスト")
    print(f"OS: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    print("=" * 60)
    
    # 1. Claude CLIの探索テスト
    print("\n1. Claude CLIの探索:")
    try:
        claude_cmd = await session_manager.get_claude_command()
        if isinstance(claude_cmd, list):
            print(f"   ✅ 見つかりました: {' '.join(claude_cmd)}")
        else:
            print(f"   ✅ 見つかりました: {claude_cmd}")
    except FileNotFoundError as e:
        print(f"   ❌ エラー: {e}")
        return
    
    # 2. 基本的な実行テスト
    print("\n2. 基本的な実行テスト:")
    print("   プロンプト: 'What is 2+2?'")
    
    result = await execute_claude("What is 2+2?", timeout=30)
    
    if result["success"]:
        print(f"   ✅ 成功")
        print(f"   回答: {result['response']}")
        print(f"   実行時間: {result['execution_time']:.2f}秒")
    else:
        print(f"   ❌ 失敗: {result['error']}")
        return
    
    # 3. セッション確認
    print("\n3. セッション情報:")
    session_info = await get_current_session()
    print(f"   セッションID: {session_info['session_id']}")
    print(f"   セッション有効: {session_info['has_session']}")
    
    # 4. セッション継続テスト
    if session_info['has_session']:
        print("\n4. セッション継続テスト:")
        print("   プロンプト: 'What was my previous question?'")
        
        result2 = await execute_claude("What was my previous question?", timeout=30)
        
        if result2["success"]:
            print(f"   ✅ 成功")
            print(f"   回答: {result2['response']}")
            print(f"   実行時間: {result2['execution_time']:.2f}秒")
        else:
            print(f"   ❌ 失敗: {result2['error']}")
    
    # 5. セッションリセット
    print("\n5. セッションリセット:")
    reset_result = await reset_session()
    print(f"   {reset_result['message']}")
    
    print("\n" + "=" * 60)
    print("テスト完了！")

async def main():
    """メイン処理"""
    try:
        await test_basic_functionality()
    except KeyboardInterrupt:
        print("\n\nテストを中断しました")
    except Exception as e:
        print(f"\n予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())