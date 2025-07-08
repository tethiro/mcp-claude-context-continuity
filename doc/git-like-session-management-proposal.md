# Git風セッション管理機能の提案

**作成日**: 2025-01-08  
**作成者**: Claude & Gemini（AI協働設計）

## 概要

Claude CLIのセッションIDが「会話のタイムスタンプ」として機能することを発見しました。この特性を活用し、Git風のブランチ管理機能を実装することで、複雑な会話フローを体系的に管理できるようになります。

## 背景と動機

### 発見された特性
- セッションIDは使い捨てだが、使用済みIDでもその時点の会話状態に復元可能
- 時系列の整合性が保たれる（未来の情報は知らない）
- これにより会話の「バージョン管理」が可能

### ユースケース
1. **複雑な問題解決**: 複数のアプローチを並行して試行
2. **クリエイティブな作業**: アイデアの分岐と統合
3. **教育・トレーニング**: 特定のステップからのやり直し
4. **開発作業**: 異なる実装方針の比較検討

## 提案する設計

### アーキテクチャ：ハイブリッドアプローチ

```
┌─────────────────────────────────────┐
│         ユーザーアプリケーション      │
├─────────────────────────────────────┤
│    SessionManager (クライアント)      │  ← Git風インターフェース
├─────────────────────────────────────┤
│         MCP プロトコル               │
├─────────────────────────────────────┤
│    Claude CLI MCP Server            │
│  ├─ 既存のツール群                   │
│  └─ 新規：Key-Valueストアツール      │  ← シンプルな永続化
└─────────────────────────────────────┘
```

### 1. MCPサーバー側の拡張

新しいツールを4つ追加：

```python
@mcp.tool()
async def save_named_session(name: str, session_id: str, metadata: dict = None):
    """セッションIDに名前を付けて保存"""
    
@mcp.tool()
async def get_named_session(name: str) -> dict:
    """名前からセッション情報を取得"""
    
@mcp.tool()
async def list_named_sessions() -> list:
    """保存されているセッション一覧を取得"""
    
@mcp.tool()
async def delete_named_session(name: str):
    """名前付きセッションを削除"""
```

### 2. データ保存構造

```
.claude-sessions/
├── sessions/
│   ├── 2025-01-08_12-30-45_abc123.json
│   ├── 2025-01-08_12-35-20_def456.json
│   └── ...
├── branches/
│   ├── main.json              # 最新のsession_idを指す
│   ├── feature_experiment-1.json
│   └── ...
└── config.json               # 設定ファイル
```

### 3. JSONデータフォーマット

```json
{
  "session_id": "abc123-def4-5678-9012",
  "parent_session_ids": ["parent1-session-id"],
  "timestamp": "2025-01-08T12:30:45.123Z",
  "name": "feature/error-handling",
  "message": "Implemented robust error handling for JSON parsing",
  "metadata": {
    "author": "user",
    "tags": ["error-handling", "bugfix"],
    "custom_fields": {}
  }
}
```

### 4. クライアントライブラリ（SessionManager）

```python
from claude_session_manager import SessionManager

# 初期化
sm = SessionManager()

# Git風の操作
sm.init()                              # .claude-sessions/ディレクトリを初期化
sm.branch("feature/new-approach")      # 新しいブランチを作成
sm.commit("Try different algorithm")   # 現在の状態をコミット
sm.checkout("main")                    # mainブランチに切り替え
sm.merge("feature/new-approach")       # ブランチをマージ（会話の統合）
sm.log()                              # コミット履歴を表示
sm.graph()                            # ブランチグラフを可視化
sm.status()                           # 現在のブランチと状態を表示
```

## 実装の段階

### フェーズ1：基本機能（MVP）
1. MCPサーバーにKey-Valueストアツールを追加
2. 基本的なSessionManagerクラスの実装
3. save/load/list機能の実装

### フェーズ2：Git風インターフェース
1. branch/checkout/commit機能の実装
2. 親子関係の管理
3. log/graph表示機能

### フェーズ3：高度な機能
1. merge機能（会話の統合）
2. diff機能（セッション間の差分表示）
3. タグ機能
4. リモートストレージ対応

## 利点

1. **直感的な操作**: 開発者に馴染み深いGitの概念を活用
2. **トレーサビリティ**: 会話の履歴と分岐を完全に追跡
3. **実験の自由度**: 安心して異なるアプローチを試せる
4. **協働作業**: セッション情報を共有して共同作業が可能

## 技術的な考慮事項

### なぜJSONファイルか？
- シンプルで実装が容易
- 人間が読めるフォーマット
- Gitでバージョン管理可能
- 必要に応じてSQLiteへの移行も容易

### なぜハイブリッドアプローチか？
- MCPサーバーの責務を最小限に保つ
- クライアント側で柔軟な操作を提供
- 既存のアーキテクチャを大きく変更しない

## オープンな質問

1. **ブランチ名の命名規則**: Git風（feature/, bugfix/等）を推奨すべきか？
2. **デフォルトブランチ**: "main"か"master"か？
3. **自動保存**: 各execute_claude実行後に自動的にセッションを保存すべきか？
4. **ガベージコレクション**: 古いセッション情報の自動削除は必要か？

## まとめ

この提案は、Claude CLIの隠れた機能を最大限に活用し、開発者にとって使いやすい形で提供するものです。Gitの概念を借りることで、学習コストを最小限に抑えながら、強力な会話管理機能を実現できます。

ご意見・ご要望をお聞かせください。