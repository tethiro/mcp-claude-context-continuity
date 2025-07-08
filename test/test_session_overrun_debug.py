#!/usr/bin/env python3
"""セッションオーバーランと復活の整合性確認デバッグテスト"""

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
    print("=== セッションオーバーランと復活整合性テスト ===\n")
    
    # セッション記録用
    sessions = {}
    
    # 1. 初回会話
    print("1. 初回会話: 基本情報")
    r1 = await execute_claude("私は太郎です。好きな色は青です。")
    s1 = await get_current_session()
    sessions['after_1'] = s1['session_id']
    print(f"応答: {r1['response'][:100]}...")
    print(f"セッションID after_1: {sessions['after_1']}")
    
    # 2. 2回目の会話（セッションオーバーラン）
    print("\n2. 2回目の会話: 食べ物の話")
    r2 = await execute_claude("好きな食べ物はラーメンです。")
    s2 = await get_current_session()
    sessions['after_2'] = s2['session_id']
    print(f"応答: {r2['response'][:100]}...")
    print(f"セッションID after_2: {sessions['after_2']}")
    
    # 3. 3回目の会話（セッションオーバーラン）
    print("\n3. 3回目の会話: 趣味の話")
    r3 = await execute_claude("趣味は読書です。")
    s3 = await get_current_session()
    sessions['after_3'] = s3['session_id']
    print(f"応答: {r3['response'][:100]}...")
    print(f"セッションID after_3: {sessions['after_3']}")
    
    # 4. 4回目の会話（セッションオーバーラン）
    print("\n4. 4回目の会話: 秘密の話")
    r4 = await execute_claude("実は秘密ですが、宝くじで100万円当たりました。")
    s4 = await get_current_session()
    sessions['after_4'] = s4['session_id']
    print(f"応答: {r4['response'][:100]}...")
    print(f"セッションID after_4: {sessions['after_4']}")
    
    # 5. 5回目の会話（セッションオーバーラン）
    print("\n5. 5回目の会話: 将来の話")
    r5 = await execute_claude("将来の夢は宇宙飛行士になることです。")
    s5 = await get_current_session()
    sessions['after_5'] = s5['session_id']
    print(f"応答: {r5['response'][:100]}...")
    print(f"セッションID after_5: {sessions['after_5']}")
    
    # セッションIDの順序を表示
    print("\n=== セッションIDの順序 ===")
    for key, value in sessions.items():
        print(f"{key}: {value}")
    
    # リセット
    await reset_session()
    
    # 復活テスト開始
    print("\n=== 復活整合性テスト ===")
    
    # after_2に戻る（ラーメンまで知っている、読書・宝くじ・宇宙飛行士は知らない）
    print(f"\n■ after_2（{sessions['after_2']}）に戻る")
    await set_current_session(sessions['after_2'])
    
    print("\n検証1: 知っているはずの情報")
    r_check1 = await execute_claude("私の名前、好きな色、好きな食べ物を教えて")
    print(f"応答: {r_check1['response'][:200]}...")
    
    print("\n検証2: 知らないはずの情報（趣味）")
    r_check2 = await execute_claude("私の趣味は何でしたっけ？")
    print(f"応答: {r_check2['response'][:200]}...")
    
    print("\n検証3: 知らないはずの情報（秘密）")
    r_check3 = await execute_claude("私が秘密と言っていたことは何でしたっけ？")
    print(f"応答: {r_check3['response'][:200]}...")
    
    # リセット
    await reset_session()
    
    # after_4に戻る（宝くじまで知っている、宇宙飛行士は知らない）
    print(f"\n■ after_4（{sessions['after_4']}）に戻る")
    await set_current_session(sessions['after_4'])
    
    print("\n検証4: 知っているはずの全情報")
    r_check4 = await execute_claude("これまでに話した内容をすべて教えて")
    print(f"応答: {r_check4['response'][:300]}...")
    
    print("\n検証5: 知らないはずの情報（将来の夢）")
    r_check5 = await execute_claude("私の将来の夢について話しましたっけ？")
    print(f"応答: {r_check5['response'][:200]}...")
    
    # リセット
    await reset_session()
    
    # after_1に戻る（青色だけ知っている）
    print(f"\n■ after_1（{sessions['after_1']}）に戻る")
    await set_current_session(sessions['after_1'])
    
    print("\n検証6: 最初の情報のみ")
    r_check6 = await execute_claude("私について知っていることをすべて教えて")
    print(f"応答: {r_check6['response'][:200]}...")
    
    # リセット
    await reset_session()
    
    # after_5に戻る（すべて知っている）
    print(f"\n■ after_5（{sessions['after_5']}）に戻る")
    await set_current_session(sessions['after_5'])
    
    print("\n検証7: すべての情報")
    r_check7 = await execute_claude("私の名前、好きな色、食べ物、趣味、秘密、将来の夢をまとめて")
    print(f"応答: {r_check7['response'][:300]}...")
    
    # 結果の分析
    print("\n=== 期待される結果 ===")
    print("1. after_2: 太郎、青、ラーメンまで知っている（読書以降は知らない）")
    print("2. after_4: 太郎、青、ラーメン、読書、宝くじまで知っている（宇宙飛行士は知らない）")
    print("3. after_1: 太郎、青のみ知っている")
    print("4. after_5: すべての情報を知っている")
    print("\n各セッションIDは「その時点までの記憶」を正確に保持し、")
    print("それ以降の情報は知らないことが確認できれば成功")


if __name__ == "__main__":
    asyncio.run(main())