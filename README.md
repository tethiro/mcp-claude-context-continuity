# Claude CLI MCP Server

Claude CLIをプログラム内部から呼び出し、会話の継続性を保持するMCP（Model Context Protocol）サーバーです。

## 特徴

- 🔍 **自動探索**: Claude CLIのインストール場所を自動的に検出
- 💬 **会話継続**: `--resume` オプションによるセッション管理で会話コンテキストを保持
- 🖥️ **クロスプラットフォーム**: Windows（WSL経由）、Linux、macOS対応
- 📄 **ファイルコンテキスト**: ファイル内容を含めた質問が可能
- 📊 **履歴管理**: 実行履歴の保存と参照
- 🔧 **一貫性のあるAPI**: すべてのツールが`tool_name`フィールドを含む統一された応答形式
- ⚡ **高速実行**: 全環境で同期実行を採用し、安定した10秒前後の応答時間を実現

## 必要条件

- Python 3.8以上
- Claude CLI（インストール済み）
- Windows環境の場合はWSL2
- FastMCP 0.8.0以上

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/mcp-claude-context-continuity.git
cd mcp-claude-context-continuity
```

2. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

3. Claude CLIの動作確認：
```bash
# MCPサーバー動作テスト
python test/test_claude_cli_server_simple.py

# デバッグテスト（各ツールを直接実行）
python test/test_mcp_server_debug.py
```

## 設定

### Claude Desktop（Windows）

`%APPDATA%\Claude\claude_desktop_config.json` に以下を追加：

```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "wsl",
      "args": [
        "-e",
        "python3",
        "/mnt/c/prj/AI/prg/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

### Claude Desktop（WSL/Linux/macOS）

`~/.config/Claude/claude_desktop_config.json` に以下を追加：

```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python3",
      "args": [
        "/path/to/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

## 使用方法

Claude Desktop内で以下のツールが利用可能になります：

### execute_claude
基本的なClaude CLI実行。会話の継続性が保たれます：
```json
{
  "tool": "execute_claude",
  "prompt": "こんにちは、私は山田太郎です"
}
```

### execute_claude_with_context
ファイルコンテキスト付き実行：
```json
{
  "tool": "execute_claude_with_context",
  "prompt": "このコードを説明してください",
  "file_path": "/path/to/code.py"
}
```

### get_execution_history
実行履歴の取得（デフォルト10件、最大100件）：
```json
{
  "tool": "get_execution_history",
  "limit": 10
}
```

### get_current_session
現在のセッション情報を取得：
```json
{
  "tool": "get_current_session"
}
```

### reset_session
セッションをリセット（会話履歴をクリア）：
```json
{
  "tool": "reset_session"
}
```

### clear_execution_history
実行履歴をクリア：
```json
{
  "tool": "clear_execution_history"
}
```

### test_claude_cli
Claude CLIの動作確認：
```json
{
  "tool": "test_claude_cli"
}
```

## 仕組み

### セッション管理

1. 初回実行時：Claude CLIから `session_id` を取得
2. 2回目以降：`--resume <session_id>` オプションで会話を継続
3. これにより、前の会話内容を記憶した状態で対話が可能

例：
```
1回目: "こんにちは、私は山田太郎です" → session_id: abc123を取得
2回目: --resume abc123 "私の名前を覚えていますか？" → "はい、山田太郎さんですね"
```

### Claude CLI探索

**Unix系（Linux/macOS/WSL）:**
1. `which claude` コマンド
2. 一般的なインストールパス（npm、yarn、nvm、volta、asdf）
3. 環境変数 `CLAUDE_PATH`

**Windows:**
1. `wsl -- bash -lc "which claude"` でWSL内を探索
2. 既知のnvmパス

### 応答形式

すべてのツールは統一された形式で応答を返します：
```json
{
  "tool_name": "execute_claude",
  "success": true,
  "prompt": "質問内容",
  "response": "Claudeからの応答",
  "execution_time": 5.123,
  "timestamp": "2025-01-08T12:34:56",
  "error": null
}
```

## トラブルシューティング

### 実装の特徴
- 全環境で同期実行（subprocess.run）を使用
- MCPの1対1通信モデルに最適化
- Windows、WSL、Linux、macOSで動作確認済み
- すべての7つのツールが正常に動作することをテスト済み
- Windows環境での非同期実行問題（10-30倍の遅延）を解決

### Claude CLIが見つからない場合

1. Claude CLIがインストールされているか確認：
```bash
claude --version
```

2. 環境変数 `CLAUDE_PATH` を設定：
```bash
export CLAUDE_PATH=/path/to/claude
```

### Windows環境での注意点

- WSL2が必要です
- Claude CLIはWSL内にインストールする必要があります
- ファイルパスはWSL形式（`/mnt/c/...`）で指定

### エンコーディングの問題

Windows環境では、以下の文字がcp932でサポートされていません：
- 絵文字（😊、🎉など）
- 一部の音符記号（♫、♬）

回避策：
- 「絵文字を使って」のような説明的な指示を使用
- 基本的な日本語と英数字、一般的な記号のみを使用

## 開発

### テスト実行

```bash
# MCPサーバー動作テスト  
python test/test_claude_cli_server_simple.py

# デバッグテスト（各ツールを直接実行）
python test/test_mcp_server_debug.py

# Windows環境テスト
python test/test_windows_claude_call.py

# エンコーディングテスト
python test/test_emoji_prompt.py

# 統合テスト（両環境対応）
# test/unified_test_prompts.txt の内容を実行
```

### プロジェクト構造

```
mcp-claude-context-continuity/
├── src/
│   └── claude_cli_server.py              # MCPサーバー本体
├── test/
│   ├── test_claude_cli_server_simple.py  # 基本動作テスト
│   ├── test_mcp_server_debug.py          # デバッグテスト
│   ├── test_windows_*.py                 # Windows環境テスト
│   ├── test_emoji_prompt.py              # エンコーディングテスト
│   └── *_test_prompts.txt                # テストプロンプト集
├── setting/
│   ├── claude_cli_mcp_config_windows.json
│   └── claude_cli_mcp_config_wsl.json
├── claude_command_debug.log              # デバッグログ
├── CLAUDE.md                             # Claude Code用ガイド
├── README.md                             # このファイル
└── requirements.txt                      # Python依存関係
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを作成して変更内容を議論してください。