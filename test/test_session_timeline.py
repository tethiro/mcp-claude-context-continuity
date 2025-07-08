#!/usr/bin/env python3
"""セッションのタイムライン確認テスト"""

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
    print("=== セッションタイムラインテスト ===\n")
    
    # 1. 会話1
    print("1. 会話1: 自己紹介")
    r1 = await execute_claude("私は太郎です")
    s1 = await get_current_session()
    session_after_1 = s1['session_id']
    print(f"セッション after 会話1: {session_after_1}")
    
    # 2. 会話2（session_after_1を使用）
    print("\n2. 会話2: 天気の話")
    r2 = await execute_claude("今日は晴れです")
    s2 = await get_current_session()
    session_after_2 = s2['session_id']
    print(f"セッション after 会話2: {session_after_2}")
    
    # 3. 会話3（session_after_2を使用）
    print("\n3. 会話3: 山の話")
    r3 = await execute_claude("富士山について教えて")
    print(f"応答: {r3['response'][:50]}...")
    s3 = await get_current_session()
    session_after_3 = s3['session_id']
    print(f"セッション after 会話3: {session_after_3}")
    
    # リセット
    await reset_session()
    
    # 各時点に戻るテスト
    print("\n=== 各時点への復元テスト ===")
    
    # session_after_1に戻る（会話1の直後）
    print(f"\n4. session_after_1（{session_after_1}）に戻る")
    await set_current_session(session_after_1)
    r4 = await execute_claude("何を話しましたか？")
    print(f"応答: {r4['response'][:100]}...")
    print("期待: 太郎の名前だけ")
    
    await reset_session()
    
    # session_after_2に戻る（会話2の直後）
    print(f"\n5. session_after_2（{session_after_2}）に戻る")
    await set_current_session(session_after_2)
    r5 = await execute_claude("何を話しましたか？")
    print(f"応答: {r5['response'][:100]}...")
    print("期待: 太郎の名前と晴れの話")
    
    await reset_session()
    
    # session_after_3に戻る（会話3の直後）
    print(f"\n6. session_after_3（{session_after_3}）に戻る")
    await set_current_session(session_after_3)
    r6 = await execute_claude("何を話しましたか？")
    print(f"応答: {r6['response'][:100]}...")
    print("期待: 太郎の名前、晴れ、富士山の話")
    
    print("\n=== 結論 ===")
    print("各セッションIDは、その時点までの会話履歴を保持している")
    print("一度使われたセッションIDでも、その時点の状態に戻ることができる")


if __name__ == "__main__":
    asyncio.run(main())