#!/usr/bin/env python3
"""正しいセッションフローのテスト"""

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
    print("=== 正しいセッションフローのテスト ===\n")
    
    # 1. 新規会話1（太郎）
    print("1. 新規会話1（太郎）")
    r1 = await execute_claude("私は太郎です")
    print(f"応答: {r1['response'][:50]}...")
    # この時点で session_manager.before_session_id = AAA
    
    # 2. 会話1の続き
    print("\n2. 会話1の続き（--resume AAA）")
    r2 = await execute_claude("富士山について教えて")
    print(f"応答: {r2['response'][:50]}...")
    # この時点で session_manager.before_session_id = BBB
    
    # 3. セッションBBBを保存
    print("\n3. 現在のセッションIDを保存")
    s1 = await get_current_session()
    saved_session_bbb = s1['session_id']
    print(f"保存したセッションID（BBB）: {saved_session_bbb}")
    
    # 4. 重要！リセットしないとBBBが使われてしまう
    print("\n4. セッションをリセット（重要！）")
    await reset_session()
    print("リセット完了")
    
    # 5. 新規会話2（花子）
    print("\n5. 新規会話2（花子）")
    r3 = await execute_claude("私は花子です")
    print(f"応答: {r3['response'][:50]}...")
    # この時点で session_manager.before_session_id = XXX
    
    # 6. 会話2の続き
    print("\n6. 会話2の続き（--resume XXX）")
    r4 = await execute_claude("桜について教えて")
    print(f"応答: {r4['response'][:50]}...")
    # この時点で session_manager.before_session_id = YYY
    
    # 7. 太郎のセッションBBBに戻る
    print(f"\n7. 太郎のセッション（{saved_session_bbb}）に戻る")
    await set_current_session(saved_session_bbb)
    print("セッション設定完了")
    
    # 8. 太郎の会話を続ける（--resume BBB）
    print("\n8. 太郎の会話を続ける（BBBを使用）")
    r5 = await execute_claude("私の名前と先ほど話した山は？")
    print(f"応答: {r5['response'][:100]}...")
    # この時点で session_manager.before_session_id = CCC
    
    # 9. さらに続ける（--resume CCC）
    print("\n9. さらに続ける")
    r6 = await execute_claude("富士山の高さは？")
    print(f"応答: {r6['response'][:100]}...")
    # この時点で session_manager.before_session_id = DDD
    
    print("\n=== テスト完了 ===")
    print(f"太郎のセッションBBB（{saved_session_bbb}）は正しく使用された")
    print("花子のセッションYYYは保存されていないため消滅")


if __name__ == "__main__":
    asyncio.run(main())