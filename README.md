# MCP Claude Context Continuity

An MCP (Model Context Protocol) server that maintains conversation context for Claude CLI across multiple invocations.

## Features

- 🔄 **Conversation Continuity**: Leverages Claude CLI's `--resume` feature to maintain conversation context across multiple calls
- 📝 **Session Management**: Save, restore, and branch conversations
- 🖥️ **Cross-platform**: Supports Windows (via WSL), Linux, and macOS
- ⚡ **Simple Implementation**: All functionality in a single Python file

## Requirements

- Python 3.8+
- Claude CLI (must be installed)
- FastMCP (`pip install fastmcp`)
- WSL2 for Windows environments

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tethiro/mcp-claude-context-continuity.git
cd mcp-claude-context-continuity
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Gemini CLI (Recommended)

Add the following to your Gemini configuration file:

**Windows** (`%USERPROFILE%\.gemini\settings.json`):
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "wsl",
      "args": [
        "-e",
        "python3",
        "/mnt/c/path/to/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

**WSL/Linux/macOS** (`~/.gemini/settings.json`):
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

### Claude Desktop

Add similar configuration to your Claude Desktop settings file.

## Usage

### Basic Usage

1. **Simple conversation**:
```
execute_claude(prompt="Hello, I'm John")
```

2. **Continue conversation**:
```
execute_claude(prompt="Do you remember my name?")
→ "Yes, you're John"
```

### Session Management

1. **Save current session**:
```
session_id = get_current_session()
```

2. **Start new session**:
```
reset_session()
```

3. **Restore saved session**:
```
set_current_session(session_id="saved_id")
```

### Available Tools

| Tool | Description |
|------|-------------|
| `execute_claude` | Execute Claude CLI with conversation continuity |
| `execute_claude_with_context` | Execute with file context |
| `get_execution_history` | Get execution history |
| `get_current_session` | Get current session ID |
| `set_current_session` | Set session ID |
| `reset_session` | Reset session |
| `clear_execution_history` | Clear history |
| `test_claude_cli` | Test functionality |

## How Session Management Works

Using Claude CLI's `--resume` feature, you can return to any point in a conversation using session IDs:

```
Conversation 1: "I'm Alice" → session_id: AAA
Conversation 2: "I like reading" (--resume AAA) → session_id: BBB
Conversation 3: "My favorite book is..." (--resume BBB) → session_id: CCC

Later:
set_current_session("AAA") → State where only "Alice" is known
set_current_session("BBB") → State where "Alice" and "reading" are known
```

## Troubleshooting

### Claude CLI Not Found

Set the `CLAUDE_PATH` environment variable:
```bash
export CLAUDE_PATH=/path/to/claude
```

### Windows Environment Notes

- WSL2 is required
- Install Claude CLI inside WSL
- Use WSL format paths (`/mnt/c/...`)

## License

MIT License

---

# MCP Claude Context Continuity

Claude CLIの会話コンテキストを保持するMCP（Model Context Protocol）サーバーです。

## 特徴

- 🔄 **会話の継続性**: Claude CLIの`--resume`機能を活用し、複数の呼び出し間で会話コンテキストを保持
- 📝 **セッション管理**: 会話の保存、復元、分岐が可能
- 🖥️ **クロスプラットフォーム**: Windows（WSL経由）、Linux、macOS対応
- ⚡ **シンプルな実装**: 単一のPythonファイルで全機能を提供

## 必要条件

- Python 3.8以上
- Claude CLI（インストール済み）
- FastMCP（`pip install fastmcp`）
- Windows環境の場合はWSL2

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/tethiro/mcp-claude-context-continuity.git
cd mcp-claude-context-continuity
```

2. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

## 設定

### Gemini CLI（推奨）

Geminiの設定ファイルに以下を追加：

**Windows環境** (`%USERPROFILE%\.gemini\settings.json`):
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "wsl",
      "args": [
        "-e",
        "python3",
        "/mnt/c/path/to/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

**WSL/Linux/macOS** (`~/.gemini/settings.json`):
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

### Claude Desktop

Claude Desktopの設定ファイルに同様の設定を追加します。

## 使用方法

### 基本的な使い方

1. **通常の会話**:
```
execute_claude(prompt="こんにちは、私は山田です")
```

2. **会話の継続**:
```
execute_claude(prompt="私の名前を覚えていますか？")
→ "はい、山田さんですね"
```

### セッション管理

1. **現在のセッションを保存**:
```
session_id = get_current_session()
```

2. **新しいセッションを開始**:
```
reset_session()
```

3. **保存したセッションに戻る**:
```
set_current_session(session_id="保存したID")
```

### 利用可能なツール

| ツール | 説明 |
|--------|------|
| `execute_claude` | Claude CLIを実行（会話継続） |
| `execute_claude_with_context` | ファイルコンテキスト付きで実行 |
| `get_execution_history` | 実行履歴を取得 |
| `get_current_session` | 現在のセッションIDを取得 |
| `set_current_session` | セッションIDを設定 |
| `reset_session` | セッションをリセット |
| `clear_execution_history` | 履歴をクリア |
| `test_claude_cli` | 動作確認 |

## セッション管理の仕組み

Claude CLIの`--resume`機能を活用し、セッションIDによって会話の任意の時点に戻ることができます：

```
会話1「私は太郎です」 → session_id: AAA
会話2「趣味は読書です」（--resume AAA） → session_id: BBB
会話3「好きな本は...」（--resume BBB） → session_id: CCC

後から：
set_current_session("AAA") → "太郎"のみ知っている状態
set_current_session("BBB") → "太郎"と"読書"を知っている状態
```

## トラブルシューティング

### Claude CLIが見つからない場合

環境変数`CLAUDE_PATH`を設定：
```bash
export CLAUDE_PATH=/path/to/claude
```

### Windows環境での注意点

- WSL2が必要です
- Claude CLIはWSL内にインストールしてください
- ファイルパスはWSL形式（`/mnt/c/...`）で指定

## ライセンス

MIT License