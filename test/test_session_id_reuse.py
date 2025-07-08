#!/usr/bin/env python3
"""セッションIDが使われた後でも復元できるかのテスト"""

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
    print("=== セッションID再利用テスト ===\n")
    
    # 1. 会話A開始
    print("1. 会話A開始")
    r1 = await execute_claude("私は太郎です。今日は晴れです。")
    print(f"応答: {r1['response'][:50]}...")
    
    # 2. セッションIDを保存（reset_sessionをしない！）
    print("\n2. セッションIDを保存（reset_sessionをしない！）")
    s1 = await get_current_session()
    saved_session_id = s1['session_id']
    print(f"保存したセッションID: {saved_session_id}")
    
    # 3. reset_sessionせずに会話を続ける（保存したIDが使われる）
    print(f"\n3. reset_sessionせずに会話を続ける（{saved_session_id}が使われる）")
    r2 = await execute_claude("富士山について教えて")
    print(f"応答: {r2['response'][:50]}...")
    print(f"警告: {r2.get('warning', 'なし')}")
    
    # 4. さらに会話を続ける
    print("\n4. さらに会話を続ける")
    r3 = await execute_claude("高さは？")
    print(f"応答: {r3['response'][:50]}...")
    
    # 5. ここでreset_session
    print("\n5. ここでreset_session")
    await reset_session()
    print("リセット完了")
    
    # 6. 新しい会話B
    print("\n6. 新しい会話B開始")
    r4 = await execute_claude("私は花子です。今日は雨です。")
    print(f"応答: {r4['response'][:50]}...")
    
    # 7. 最初に保存したIDで会話Aに戻れるか？
    print(f"\n7. 最初に保存したID（{saved_session_id}）で会話Aに戻れるか？")
    await set_current_session(saved_session_id)
    
    # 8. 会話Aの内容を覚えているか確認
    print("\n8. 会話Aの内容を覚えているか確認")
    r5 = await execute_claude("私の名前と天気、そして先ほど話した山について教えて")
    print(f"応答: {r5['response'][:200]}...")
    print(f"警告: {r5.get('warning', 'なし')}")
    
    # 結果の分析
    print("\n=== 結果 ===")
    if "太郎" in r5['response'] and ("晴れ" in r5['response'] or "富士山" in r5['response']):
        print("✅ 成功: セッションIDが一度使われた後でも、会話の復元ができました！")
    else:
        print("❌ 失敗: セッションIDが使われた後は、会話を復元できませんでした")
    
    # デバッグ情報
    print(f"\n保存したセッションID: {saved_session_id}")
    print("このIDは手順3で既に使用されています")


if __name__ == "__main__":
    asyncio.run(main())