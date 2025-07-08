#!/usr/bin/env python3
"""セッションブランチの可視化ツール"""

import asyncio
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.claude_cli_server import (
    execute_claude, 
    get_current_session, 
    reset_session,
    set_current_session,
    get_execution_history
)


class SessionBranchVisualizer:
    def __init__(self):
        self.branches = {}
        self.current_branch = "main"
        
    async def commit(self, message, content):
        """新しいコミット（会話）を作成"""
        print(f"\n💬 {message}")
        result = await execute_claude(content)
        session = await get_current_session()
        
        commit_id = session['session_id'][:8]
        
        if self.current_branch not in self.branches:
            self.branches[self.current_branch] = []
        
        self.branches[self.current_branch].append({
            'id': commit_id,
            'full_id': session['session_id'],
            'message': message,
            'response': result['response'][:100] + "..."
        })
        
        print(f"📌 Commit: {commit_id} on branch '{self.current_branch}'")
        return session['session_id']
    
    async def checkout(self, branch_name, from_commit=None):
        """ブランチの切り替えまたは作成"""
        await reset_session()
        
        if from_commit:
            # 特定のコミットから新しいブランチを作成
            await set_current_session(from_commit)
            print(f"\n🌿 Creating new branch '{branch_name}' from {from_commit[:8]}")
        else:
            # 既存のブランチに切り替え
            if branch_name in self.branches and self.branches[branch_name]:
                last_commit = self.branches[branch_name][-1]['full_id']
                await set_current_session(last_commit)
                print(f"\n🔄 Switching to branch '{branch_name}'")
        
        self.current_branch = branch_name
    
    async def log(self, branch_name=None):
        """ブランチのコミット履歴を表示"""
        branch = branch_name or self.current_branch
        
        if branch not in self.branches:
            print(f"Branch '{branch}' not found")
            return
        
        print(f"\n📜 Log for branch '{branch}':")
        for commit in self.branches[branch]:
            print(f"  {commit['id']} - {commit['message']}")
            print(f"    └─ {commit['response']}")
    
    async def diff(self, branch1, branch2):
        """2つのブランチの違いを確認"""
        print(f"\n🔍 Diff between '{branch1}' and '{branch2}':")
        
        if branch1 in self.branches and self.branches[branch1]:
            await reset_session()
            await set_current_session(self.branches[branch1][-1]['full_id'])
            r1 = await execute_claude("これまでの内容を3行でまとめて")
            print(f"\n{branch1}:\n{r1['response']}")
        
        if branch2 in self.branches and self.branches[branch2]:
            await reset_session()
            await set_current_session(self.branches[branch2][-1]['full_id'])
            r2 = await execute_claude("これまでの内容を3行でまとめて")
            print(f"\n{branch2}:\n{r2['response']}")
    
    def visualize(self):
        """ブランチ構造を視覚化"""
        print("\n🌳 Branch Structure:")
        print("main")
        
        # 簡易的な可視化
        for branch, commits in self.branches.items():
            if branch != "main":
                print(f"  └─ {branch}")
                for i, commit in enumerate(commits):
                    prefix = "     └─" if i == len(commits) - 1 else "     ├─"
                    print(f"{prefix} {commit['id']}: {commit['message']}")


async def demo():
    """Git風ブランチ管理のデモンストレーション"""
    viz = SessionBranchVisualizer()
    
    print("=== セッションブランチ管理デモ ===")
    
    # Main branchでの開発
    commit1 = await viz.commit(
        "Initial commit", 
        "新しいブログシステムを開発します。プロジェクト名は『FastBlog』です。"
    )
    
    commit2 = await viz.commit(
        "Add user requirements",
        "ユーザー要件：記事投稿、コメント機能、タグ付け、検索機能が必要です。"
    )
    
    commit3 = await viz.commit(
        "Choose frontend tech",
        "フロントエンドはNext.js 14を使用します。"
    )
    
    # Feature branchの作成
    await viz.checkout("feature/api-design", from_commit=commit2)
    
    await viz.commit(
        "Design REST API",
        "REST APIの設計：/api/posts, /api/comments, /api/tags のエンドポイントを作成します。"
    )
    
    await viz.commit(
        "Add GraphQL consideration",
        "GraphQLの採用も検討中です。より柔軟なデータ取得が可能になります。"
    )
    
    # 別のfeature branchの作成
    await viz.checkout("feature/mobile-app", from_commit=commit2)
    
    await viz.commit(
        "Mobile app planning",
        "React Nativeを使用してモバイルアプリも開発します。"
    )
    
    await viz.commit(
        "Choose Flutter instead",
        "パフォーマンスを考慮して、FlutterでのモバイルApp開発に変更します。"
    )
    
    # Main branchに戻る
    await viz.checkout("main")
    
    await viz.commit(
        "Add backend decision",
        "バックエンドはPython FastAPIを採用します。"
    )
    
    # ログとビジュアライゼーション
    await viz.log("main")
    await viz.log("feature/api-design")
    await viz.log("feature/mobile-app")
    
    viz.visualize()
    
    # ブランチ間の差分確認
    await viz.diff("feature/api-design", "feature/mobile-app")
    
    # 実行履歴の確認
    print("\n\n📊 実行統計:")
    history = await get_execution_history(limit=20)
    print(f"Total executions: {len(history['history'])}")
    print(f"Total branches created: {len(viz.branches)}")
    print(f"Commits per branch:")
    for branch, commits in viz.branches.items():
        print(f"  - {branch}: {len(commits)} commits")


if __name__ == "__main__":
    asyncio.run(demo())