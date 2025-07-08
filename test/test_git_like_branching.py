#!/usr/bin/env python3
"""Git的なブランチ管理のデモンストレーション"""

import asyncio
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.claude_cli_server import (
    execute_claude, 
    get_current_session, 
    reset_session,
    set_current_session
)


async def main():
    print("=== Git的ブランチ管理デモ ===\n")
    
    # コミット履歴を保存
    commits = {}
    
    # 1. 初期コミット
    print("📝 Initial commit: プロジェクト開始")
    r1 = await execute_claude("新しいECサイトプロジェクトを開始します。プロジェクト名は『QuickShop』です。")
    s1 = await get_current_session()
    commits['initial'] = s1['session_id']
    print(f"Commit ID: {commits['initial'][:8]}...")
    
    # 2. フロントエンド選定
    print("\n📝 Commit 2: フロントエンド技術選定")
    r2 = await execute_claude("フロントエンドはReact + TypeScriptで実装します。")
    s2 = await get_current_session()
    commits['frontend-react'] = s2['session_id']
    print(f"Commit ID: {commits['frontend-react'][:8]}...")
    
    # 3. バックエンド選定（main branch）
    print("\n📝 Commit 3: バックエンド技術選定")
    r3 = await execute_claude("バックエンドはNode.js + Expressを使用します。")
    s3 = await get_current_session()
    commits['backend-node'] = s3['session_id']
    print(f"Commit ID: {commits['backend-node'][:8]}...")
    
    # 4. データベース選定（main branch）
    print("\n📝 Commit 4: データベース選定")
    r4 = await execute_claude("データベースはPostgreSQLを採用します。")
    s4 = await get_current_session()
    commits['db-postgres'] = s4['session_id']
    print(f"Commit ID: {commits['db-postgres'][:8]}...")
    
    # ブランチ1: Vue.jsの検討
    print("\n\n🌿 Branch: feature/vue-alternative")
    await reset_session()
    await set_current_session(commits['initial'])
    
    print("📝 Branch commit 1: Vue.jsでフロントエンド")
    r5 = await execute_claude("フロントエンドはVue.js 3 + TypeScriptで実装することにしました。")
    s5 = await get_current_session()
    commits['frontend-vue'] = s5['session_id']
    print(f"Commit ID: {commits['frontend-vue'][:8]}...")
    
    print("📝 Branch commit 2: Laravelバックエンド")
    r6 = await execute_claude("Vue.jsと相性の良いLaravel（PHP）をバックエンドに採用します。")
    s6 = await get_current_session()
    commits['backend-laravel'] = s6['session_id']
    print(f"Commit ID: {commits['backend-laravel'][:8]}...")
    
    # ブランチ2: マイクロサービス検討
    print("\n\n🌿 Branch: feature/microservices")
    await reset_session()
    await set_current_session(commits['frontend-react'])
    
    print("📝 Branch commit 1: マイクロサービスアーキテクチャ")
    r7 = await execute_claude("バックエンドはマイクロサービスアーキテクチャを採用。認証サービス、商品サービス、注文サービスに分割します。")
    s7 = await get_current_session()
    commits['architecture-microservices'] = s7['session_id']
    print(f"Commit ID: {commits['architecture-microservices'][:8]}...")
    
    # 各ブランチの確認
    print("\n\n=== ブランチの状態確認 ===")
    
    # main branch
    print("\n🎯 Main branch (backend-node)の状態:")
    await reset_session()
    await set_current_session(commits['backend-node'])
    r_main = await execute_claude("現在の技術スタックを教えてください。")
    print(f"Main: {r_main['response'][:150]}...")
    
    # vue branch
    print("\n🎯 Vue branch (backend-laravel)の状態:")
    await reset_session()
    await set_current_session(commits['backend-laravel'])
    r_vue = await execute_claude("現在の技術スタックを教えてください。")
    print(f"Vue: {r_vue['response'][:150]}...")
    
    # microservices branch
    print("\n🎯 Microservices branch の状態:")
    await reset_session()
    await set_current_session(commits['architecture-microservices'])
    r_micro = await execute_claude("アーキテクチャについて教えてください。")
    print(f"Micro: {r_micro['response'][:150]}...")
    
    # コミットグラフの表示
    print("\n\n=== コミットグラフ ===")
    print("initial")
    print("  ├─ frontend-react")
    print("  │    ├─ backend-node")
    print("  │    │    └─ db-postgres [main]")
    print("  │    └─ architecture-microservices [feature/microservices]")
    print("  └─ frontend-vue")
    print("       └─ backend-laravel [feature/vue-alternative]")
    
    # マージシミュレーション
    print("\n\n=== マージシミュレーション ===")
    print("main branchにmicroservicesの知識を統合...")
    await reset_session()
    await set_current_session(commits['db-postgres'])
    r_merge = await execute_claude(
        "実は先ほどマイクロサービスアーキテクチャも検討しました。"
        "認証、商品、注文の3つのサービスに分割する案です。"
        "現在の構成と比較してどう思いますか？"
    )
    print(f"統合後: {r_merge['response'][:200]}...")


if __name__ == "__main__":
    asyncio.run(main())