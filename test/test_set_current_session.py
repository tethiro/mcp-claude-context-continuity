#!/usr/bin/env python3
"""set_current_sessionツールのテストスクリプト"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.claude_cli_server import (
    execute_claude, 
    get_current_session, 
    reset_session,
    set_current_session
)


async def main():
    print("=== set_current_session機能テスト ===\n")
    
    try:
        # 1. 会話セッション1開始
        print("1. 会話セッション1開始")
        result = await execute_claude("私は太郎です。富士山について教えてください")
        print(f"応答: {result['response'][:100]}...")
        print(f"成功: {result['success']}\n")
        
        # 2. 会話セッション1継続
        print("2. 会話セッション1継続")
        result = await execute_claude("私の名前を覚えていますか？また、先ほど話した山の高さは？")
        print(f"応答: {result['response'][:100]}...")
        print(f"成功: {result['success']}\n")
        
        # 3. セッション1のID取得
        print("3. セッション1のID取得")
        result = await get_current_session()
        session1_id = result['session_id']
        print(f"セッション1 ID: {session1_id}\n")
        
        # 4. セッションリセット
        print("4. セッションリセット")
        result = await reset_session()
        print(f"リセット完了: {result['success']}\n")
        
        # 5. 会話セッション2開始
        print("5. 会話セッション2開始")
        result = await execute_claude("私は花子です。桜について教えてください")
        print(f"応答: {result['response'][:100]}...")
        print(f"成功: {result['success']}\n")
        
        # 6. 会話セッション2継続
        print("6. 会話セッション2継続")
        result = await execute_claude("私の名前を覚えていますか？また、先ほど話した花の特徴は？")
        print(f"応答: {result['response'][:100]}...")
        print(f"成功: {result['success']}\n")
        
        # 7. セッション2のID取得
        print("7. セッション2のID取得")
        result = await get_current_session()
        session2_id = result['session_id']
        print(f"セッション2 ID: {session2_id}\n")
        
        # 8. セッション1復活
        print("8. セッション1復活")
        result = await set_current_session(session1_id)
        print(f"セッション1設定: {result['success']}")
        print(f"メッセージ: {result['message']}\n")
        
        # 9. セッション1の記憶確認
        print("9. セッション1の記憶確認")
        result = await execute_claude("私の名前と、最初に話した山についてもう一度教えてください")
        print(f"応答: {result['response'][:200]}...")
        print(f"太郎と富士山を覚えているか確認\n")
        
        # 10. セッション2復活
        print("10. セッション2復活")
        result = await set_current_session(session2_id)
        print(f"セッション2設定: {result['success']}")
        print(f"メッセージ: {result['message']}\n")
        
        # 11. セッション2の記憶確認
        print("11. セッション2の記憶確認")
        result = await execute_claude("私の名前と、最初に話した花についてもう一度教えてください")
        print(f"応答: {result['response'][:200]}...")
        print(f"花子と桜を覚えているか確認\n")
        
        print("=== テスト完了 ===")
        print(f"セッション1 ID: {session1_id}")
        print(f"セッション2 ID: {session2_id}")
        
    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())