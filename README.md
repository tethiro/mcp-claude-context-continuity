# Claude CLI MCP Server

Claude CLIをプログラム内部から呼び出し、会話の継続性を保持するMCP（Model Context Protocol）サーバーです。

## 特徴

- 🔍 **自動探索**: Claude CLIのインストール場所を自動的に検出
- 💬 **会話継続**: `--resume` オプションによるセッション管理で会話コンテキストを保持
- 🖥️ **クロスプラットフォーム**: Windows（WSL経由）、Linux、macOS対応
- 📄 **ファイルコンテキスト**: ファイル内容を含めた質問が可能
- 📊 **履歴管理**: 実行履歴の保存と参照

## 必要条件

- Python 3.8以上
- Claude CLI（インストール済み）
- Windows環境の場合はWSL2

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
# 探索テスト
python test/test_find_claude.py

# MCPサーバー動作テスト
python test/test_claude_cli_server_simple.py
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
基本的なClaude CLI実行：
```
ツール: execute_claude
プロンプト: "What is 2+2?"
タイムアウト: 300（オプション）
```

### execute_claude_with_context
ファイルコンテキスト付き実行：
```
ツール: execute_claude_with_context
プロンプト: "このコードを説明してください"
ファイルパス: "/path/to/code.py"
```

### get_execution_history
実行履歴の取得（最新10件）：
```
ツール: get_execution_history
件数: 10（オプション）
```

### get_current_session
現在のセッション情報：
```
ツール: get_current_session
```

### reset_session
セッションのリセット：
```
ツール: reset_session
```

## 仕組み

### セッション管理

1. 初回実行時：Claude CLIから `session_id` を取得
2. 2回目以降：`--resume <session_id>` オプションで会話を継続
3. これにより、前の会話内容を記憶した状態で対話が可能

### Claude CLI探索

**Unix系（Linux/macOS/WSL）:**
1. `which claude` コマンド
2. 一般的なインストールパス（npm、yarn、nvm、volta、asdf）
3. 環境変数 `CLAUDE_PATH`

**Windows:**
1. `wsl -- bash -lc "which claude"` でWSL内を探索
2. 既知のnvmパス

## トラブルシューティング

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

## 開発

### テスト実行

```bash
# Claude CLI探索テスト
python test/test_find_claude.py

# MCPサーバー動作テスト  
python test/test_claude_cli_server_simple.py
```

### プロジェクト構造

```
mcp-claude-context-continuity/
├── src/
│   └── claude_cli_server.py    # MCPサーバー本体
├── test/
│   ├── test_find_claude.py     # 探索テスト
│   └── test_claude_cli_server_simple.py  # 動作テスト
├── setting/
│   ├── claude_cli_mcp_config_windows.json
│   └── claude_cli_mcp_config_wsl.json
├── doc/
│   └── claude_cli_mcp_server_specification.md  # 詳細仕様
├── CLAUDE.md                   # Claude Code用ガイド
├── README.md                   # このファイル
└── requirements.txt            # Python依存関係
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを作成して変更内容を議論してください。