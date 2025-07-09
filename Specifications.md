# Specifications.md

MCP Claude Context Continuity プロジェクトの技術仕様書

## プロジェクト概要
Claude CLIの会話コンテキストを保持するMCP（Model Context Protocol）サーバー

## 技術スタック
- Python 3.8+
- FastMCP 0.1.0+
- Claude CLI (WSL内にインストール)
- 非同期処理 (asyncio) - MCPフレームワークで使用

## アーキテクチャ

### コア実装
単一ファイル `src/claude_cli_server.py` にすべての機能を実装

### 提供する8つのツール
1. `execute_claude` - Claude CLIを実行（会話継続）
2. `execute_claude_with_context` - ファイルコンテキスト付き実行
3. `get_execution_history` - 実行履歴を取得（デフォルト10件、最大100件）
4. `clear_execution_history` - 実行履歴をクリア
5. `get_current_session` - 現在の未使用セッションIDを取得
6. `set_current_session` - セッションIDを設定して会話を復元
7. `reset_session` - セッションをリセット
8. `test_claude_cli` - 動作確認

## セッション管理仕様

### 基本原理
- Claude CLIの`--resume`オプションを使用して会話の継続性を実現
- セッションIDは使い捨て（1回の`--resume`でのみ使用可能）
- セッションIDはタイムスタンプとして機能（過去の任意の時点に復元可能）

### コマンド実行パターン
```bash
# 初回実行
claude --dangerously-skip-permissions --output-format json -p "質問"

# 継続実行
claude --dangerously-skip-permissions --output-format json --resume <session_id> -p "質問"
```

### セッションフロー
```
1. 会話1「太郎です」 → 返却: session_id=AAA
2. 会話2「趣味は読書」（--resume AAA） → 返却: session_id=BBB
3. get_current_session() → BBBを取得（未使用）
4. reset_session() → 新規セッション開始
5. set_current_session(BBB) → 会話2の直後に復元
```

## 環境対応

### プラットフォーム別実装
- **Windows**: WSL経由で実行 (`["wsl", "--", "/path/to/claude"]`)
- **WSL/Linux/macOS**: 直接実行 (`"/path/to/claude"`)

### Claude CLI探索順序
1. `which claude` コマンド
2. 一般的なインストールパス
3. 環境変数 `CLAUDE_PATH`

## エンコーディング仕様
- すべてUTF-8で統一
- ファイルI/O時に`encoding='utf-8'`を明示
- Windows環境のcp932問題は解決済み

## エラーハンドリング
- タイムアウト: 300秒（DEFAULT_TIMEOUT）
- すべてのエラーレスポンスに`tool_name`フィールドを含む
- 空の結果が返った場合の自動リトライ機能

## ファイル構造（リリース版）
```
mcp-claude-context-continuity/
├── src/
│   └── claude_cli_server.py      # すべての実装
├── doc/
│   ├── GEMINI_USAGE_GUIDE.md
│   ├── claude_cli_mcp_server_specification.md
│   └── session_management_detailed_spec.md
├── setting/
│   ├── README.md
│   ├── claude_cli_mcp_config_windows.json
│   └── claude_cli_mcp_config_wsl.json
├── README.md
├── Specifications.md
├── requirements.txt
└── .gitignore
```

## パフォーマンス特性
- 通常のクエリ: 8-12秒
- 複雑なクエリ: 15-30秒
- ファイルコンテキスト付き: 12-15秒
- 即時応答（履歴取得等）: 1秒未満

## 制限事項
1. 並列実行は不可（セッション継続性保持のため）
2. 履歴は最新100件まで（メモリ内保持）
3. Windows環境では一部の特殊文字（絵文字等）に制限

## 設定例

### Windows環境
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "wsl",
      "args": [
        "-e",
        "python3",
        "/mnt/c/path/to/src/claude_cli_server.py"
      ]
    }
  }
}
```

### WSL/Linux/macOS環境
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python3",
      "args": [
        "/path/to/src/claude_cli_server.py"
      ]
    }
  }
}
```