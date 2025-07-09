# Claude CLI MCP Server 要件定義・仕様書

## 1. プロジェクト概要

### 1.1 目的
Claude CLIをプログラム内部から呼び出し、会話の継続性を保持するMCP（Model Context Protocol）サーバーを提供する。

### 1.2 主要機能
- Claude CLIの自動探索と実行
- セッション管理による会話の継続性
- ファイルコンテキストの提供
- 実行履歴の管理

## 2. 技術仕様

### 2.1 技術スタック
- **言語**: Python 3.8+
- **フレームワーク**: MCP (Model Context Protocol) - FastMCP
- **トランスポート**: stdio
- **外部依存**: Claude CLI

### 2.2 対応環境
- **Unix系OS**: Linux, macOS, WSL
- **Windows**: WSL経由でClaude CLIを実行

## 3. アーキテクチャ

### 3.1 ディレクトリ構造
```
mcp-claude-context-continuity/
├── doc/                    # ドキュメント
│   └── claude_cli_mcp_server_specification.md
├── src/                    # ソースコード
│   ├── server.py          # 旧カウンターサーバー（後で整理予定）
│   └── claude_cli_server.py  # Claude CLI MCPサーバー
├── test/                   # テストコード
│   ├── test_find_claude.py   # Claude CLI探索テスト
│   └── test_claude_cli_server.py  # MCPサーバーテスト
├── setting/                # 設定ファイル
│   └── claude_cli_mcp_config.json
├── tmp/                    # 一時ファイル
├── CLAUDE.md              # Claude Code用ガイド
├── README.md              # プロジェクト説明
└── requirements.txt       # Python依存関係
```

### 3.2 クラス構成

#### ClaudeSessionManager
セッション管理とClaude CLI探索を担当するクラス

**属性**:
- `before_session_id`: 前回のセッションID（永続保持）
- `history`: 実行履歴（最新100件）
- `claude_command`: Claude実行コマンドのキャッシュ

**メソッド**:
- `get_claude_command()`: Claude CLIの実行コマンドを取得
- `_find_claude_unix()`: Unix系OSでClaude CLIを探索
- `_find_claude_windows()`: WindowsでWSL経由のClaude CLIを探索
- `_add_history()`: 履歴に追加

## 4. 機能仕様

### 4.1 Claude CLI探索機能

#### Unix系OS（Linux/macOS/WSL）での探索順序
1. `which claude` コマンドで検索
2. 一般的なインストール場所をチェック
   - `/usr/local/bin/claude`
   - `/usr/bin/claude`
   - `~/.npm-global/bin/claude`
   - `~/.yarn/bin/claude`
   - `~/.volta/bin/claude`
   - `~/.nvm/versions/node/*/bin/claude`
   - `~/.asdf/installs/nodejs/*/bin/claude`
3. 環境変数 `CLAUDE_PATH` をチェック

#### Windowsでの探索順序
1. `wsl -- bash -lc "which claude"` で検索（bashログインシェル経由）
2. 既知のnvmパスをチェック
   - `/home/username/.nvm/versions/node/vXX.XX.X/bin/claude`
   - WSLユーザー名から動的に生成したパス

### 4.2 MCP提供ツール

#### execute_claude
基本的なClaude CLI実行ツール

**パラメータ**:
- `prompt` (str): Claudeに送るプロンプト
- `timeout` (int): タイムアウト時間（デフォルト: 300秒）

**返り値**:
```json
{
    "success": bool,
    "prompt": str,
    "response": str,  // Claude CLIの "result" フィールドの値のみ
    "execution_time": float,
    "timestamp": str,  // ISO形式
    "error": str | null
}
```

#### execute_claude_with_context
ファイルコンテキスト付きでClaude CLIを実行

**パラメータ**:
- `prompt` (str): Claudeに送るプロンプト
- `file_path` (str): コンテキストとして使用するファイルのパス
- `timeout` (int): タイムアウト時間（デフォルト: 300秒）

**返り値**:
上記に加えて `"context_file": str` を含む

#### get_execution_history
実行履歴を取得

**パラメータ**:
- `limit` (int): 取得する履歴数（デフォルト: 10）

**返り値**:
```json
{
    "success": true,
    "history": [...],
    "total_entries": int,
    "current_session_id": str | null
}
```

#### clear_execution_history
実行履歴をクリア

**返り値**:
```json
{
    "success": true,
    "message": str,
    "cleared_count": int
}
```

#### get_current_session
現在のセッションIDを取得

**返り値**:
```json
{
    "success": true,
    "session_id": str | null,
    "has_session": bool
}
```

#### reset_session
セッションをリセット

**返り値**:
```json
{
    "success": true,
    "message": str,
    "old_session_id": str | null
}
```

## 5. 重要な仕様

### 5.1 セッション継続機能（--resume）

**仕組み**:
1. Claude CLIの実行結果から `session_id` を取得して保存
2. 次回実行時、`before_session_id` が存在する場合は `--resume <session_id>` オプションを付加
3. これにより前回の会話コンテキストが引き継がれる

**実行フロー**:
- 初回: `claude --dangerously-skip-permissions --output-format json -p "質問"`
- 2回目以降: `claude --dangerously-skip-permissions --output-format json --resume <session_id> -p "質問"`

### 5.2 必須オプション
- `--dangerously-skip-permissions`: 権限確認をスキップ（必須）
- `--output-format json`: JSON形式で出力（構造化データ取得のため必須）

### 5.3 制約事項
- **並列実行は不可**: --resumeによるセッション継続性を保つため
- 履歴は最新100件まで保持
- タイムアウトはデフォルト300秒

## 6. エラーハンドリング

### 6.1 エラーケース
1. **Claude CLI未検出**: 適切なエラーメッセージと対処法を返す
2. **タイムアウト**: 指定時間を超えた場合
3. **JSON解析エラー**: Claude CLIの出力が不正な場合
4. **ファイル読み込みエラー**: コンテキストファイルが読めない場合
5. **コマンド実行エラー**: Claude CLIが異常終了した場合

### 6.2 エラー時の返り値
```json
{
    "success": false,
    "prompt": str,
    "response": null,
    "execution_time": float,
    "timestamp": str,
    "error": "エラーメッセージ"
}
```

## 7. 設定ファイル

### 7.1 MCP設定例（WSL/Linux/macOS）
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python",
      "args": ["/path/to/claude_cli_server.py"]
    }
  }
}
```

### 7.2 MCP設定例（Windows）
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "wsl",
      "args": [
        "-e",
        "python3",
        "/home/username/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

## 8. 今後の拡張予定

1. **Windows版の改良**
   - WSL経由の実行をより効率的に
   - パス変換の自動処理

2. **追加機能**
   - 実行履歴の永続化（ファイル保存）
   - 統計情報の提供（コスト、トークン使用量など）
   - カスタムオプションのサポート

3. **パフォーマンス最適化**
   - Claude CLI探索結果の永続キャッシュ
   - 起動時間の短縮

## 9. 開発メモ

### Windows版での実行方法（参考）
```bash
wsl -- /home/username/.nvm/versions/node/vXX.XX.X/bin/claude -p "こんにちは"
```

### 重要な発見
- Windows環境では `wsl -- bash -lc "which claude"` を使用することで、適切にPATHが設定された状態でClaude CLIを探索できる
- `--output-format stream-json` を使用する場合は `--verbose` フラグが必須（ただし、現在は使用していない）