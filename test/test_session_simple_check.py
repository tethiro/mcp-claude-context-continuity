#!/usr/bin/env python3
"""セッション復活の簡単な確認テスト"""

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
    print("=== セッション復活の簡単な確認 ===\n")
    
    # 1. 会話A
    print("1. 会話A: 太郎")
    r1 = await execute_claude("私は太郎です")
    s1 = await get_current_session()
    session_a = s1['session_id']
    print(f"セッションA: {session_a}")
    
    # 2. 会話B（オーバーラン）
    print("\n2. 会話B: ラーメン")
    r2 = await execute_claude("好きな食べ物はラーメンです")
    s2 = await get_current_session()
    session_b = s2['session_id']
    print(f"セッションB: {session_b}")
    
    # 3. 会話C（オーバーラン）
    print("\n3. 会話C: 秘密")
    r3 = await execute_claude("秘密ですが宝くじに当たりました")
    s3 = await get_current_session()
    session_c = s3['session_id']
    print(f"セッションC: {session_c}")
    
    # リセット
    await reset_session()
    
    # セッションBに戻る
    print(f"\n4. セッションB（{session_b}）に戻る")
    await set_current_session(session_b)
    r4 = await execute_claude("私について何を知っていますか？")
    print(f"応答: {r4['response'][:150]}...")
    
    print("\n5. 秘密について聞く")
    r5 = await execute_claude("私が秘密と言っていたことはありますか？")
    print(f"応答: {r5['response'][:150]}...")
    
    print("\n=== 結果 ===")
    print("セッションBでは「太郎」と「ラーメン」は知っているが、")
    print("「宝くじの秘密」は知らないはずです。")


if __name__ == "__main__":
    asyncio.run(main())