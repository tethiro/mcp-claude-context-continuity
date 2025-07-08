# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要
Claude CLI MCP Server - Claude CLIをプログラム内部から呼び出し、会話の継続性を保持するMCP（Model Context Protocol）サーバー

## 技術スタック
- Python 3.8+
- MCP (Model Context Protocol) - FastMCP
- Claude CLI (外部依存)
- 非同期処理 (asyncio)

## 開発コマンド

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### サーバーの起動
```bash
# Unix系OS
python src/claude_cli_server.py

# Windows (WSL経由)
wsl -e python3 /mnt/c/prj/AI/prg/mcp-claude-context-continuity/src/claude_cli_server.py
```

### テストの実行
```bash
# 基本的な動作テスト
python test/test_claude_cli_server_simple.py

# MCPサーバーデバッグテスト（ツール直接実行）
python test/test_mcp_server_debug.py

# Windows環境テスト
python test/test_windows_claude_call.py
python test/test_windows_claude_debug.py

# エンコーディングテスト
python test/test_emoji_prompt.py
```

## アーキテクチャ

### コア機能
8つのMCPツールを提供：
- `execute_claude`: Claude CLIを実行して結果を返す
- `execute_claude_with_context`: ファイルコンテキスト付きでClaude CLIを実行
- `get_execution_history`: 実行履歴を取得（デフォルト10件、最大100件）
- `clear_execution_history`: 実行履歴をクリア
- `get_current_session`: 現在のセッションIDを取得
- `set_current_session`: 次回使用するセッションIDを設定
- `reset_session`: セッションをリセット
- `test_claude_cli`: Claude CLIの動作確認

### 重要な仕様
- **セッション継続機能（最重要）**: 
  - `--resume`オプションでClaude CLIの会話コンテキストを保持
  - 初回: `claude --dangerously-skip-permissions --output-format json -p "質問"`
  - 2回目以降: `claude --dangerously-skip-permissions --output-format json --resume <session_id> -p "質問"`
  - これにより前回の会話内容を記憶した状態で対話が可能
  - **重要**: `set_current_session`で過去のセッションIDを設定すると、その時点の会話内容に戻ることができる
- **環境別の呼び出し方法（重要）**:
  - **WSL上のGeminiからClaudeを呼ぶ場合**: 直接実行（`/path/to/claude`）
  - **Windows上のGeminiからClaudeを呼ぶ場合**: WSL経由（`wsl -- /path/to/claude`）
  - これはMCPサーバーがWSL上で動作し、Claude CLIもWSL内にインストールされているため
- **必須オプション**: 
  - `--dangerously-skip-permissions`: 権限確認をスキップ（必須）
  - `--output-format json`: JSON形式で出力（session_id取得のため必須）
- **タイムアウト**: 
  - DEFAULT_TIMEOUT = 300秒
- **エンコーディング対応**:
  - `encoding='utf-8', errors='replace'`により、Windows環境でのcp932エンコーディング問題に対応
  - 絵文字や特殊文字は環境により制限あり
- **制約事項**:
  - 並列実行は不可（--resumeによるセッション継続性を保つため）
  - 履歴は最新100件まで保持（メモリ内のみ）
- **クロスプラットフォーム**: Windows（WSL経由）、Linux、macOS対応
- **返り値の一貫性**: すべてのツールが`tool_name`フィールドを含む

### ファイル構造
```
mcp-claude-context-continuity/
├── src/
│   └── claude_cli_server.py                 # メインMCPサーバー実装（同期実行統一版）
├── test/
│   ├── test_claude_cli_server_simple.py    # 基本動作テスト
│   ├── test_mcp_server_debug.py            # ツール直接テスト
│   ├── test_windows_claude_call.py         # Windows環境テスト
│   ├── test_windows_claude_debug.py        # Windowsデバッグテスト
│   ├── test_emoji_prompt.py                # エンコーディングテスト
│   ├── unified_test_prompts.txt            # 統合テストプロンプト（両環境対応）
│   ├── mcp_tools_test_prompts.txt          # テストプロンプト集
│   ├── encoding_test_prompts.txt           # エンコーディングテスト用
│   └── encoding_debug_prompts.txt          # cp932デバッグ用
├── setting/
│   ├── claude_cli_mcp_config_windows.json  # Windows設定例
│   └── claude_cli_mcp_config_wsl.json      # WSL/Unix設定例
├── doc/
│   ├── sync_execution_unification.md       # 同期実行統一の記録
│   ├── windows_async_performance_issue.md  # Windows非同期問題の記録
│   └── gemini_code_review_20250108.md      # Geminiコードレビュー
├── claude_command_debug.log         # コマンド実行ログ
├── requirements.txt                 # Python依存関係
├── CLAUDE.md                        # このファイル
└── README.md                        # 使用方法
```

## 開発時の注意点
- **全環境共通**:
  - 同期実行（subprocess.run）で統一
  - MCPは1対1通信のため非同期処理は不要
  - `stdin=subprocess.DEVNULL`で対話モードを回避
- **Windows環境**: 
  - WSL経由でClaude CLIを実行（`['wsl', '--', '/path/to/claude']`）
  - `encoding='utf-8', errors='replace'`でcp932エンコーディング問題に対応
- **Unix系環境（WSL/Linux/macOS）**:
  - Claude CLIを直接実行（`['/path/to/claude']`）
  - `encoding='utf-8'`を使用
- **エラーハンドリング**: 
  - タイムアウト、JSON解析エラー、ファイル読み込みエラーを適切に処理
  - すべてのエラーケースで`tool_name`を含む
- **デバッグ**: 
  - `claude_command_debug.log`にコマンド実行ログを記録
  - セッションID更新も記録
- **セッション管理**: ClaudeSessionManagerクラスでsession_idをメモリ内に保持
- **Claude CLI探索**: 
  - Unix系: which → 一般的なパス → 環境変数の順で探索
  - Windows: WSL内でwhich → nvmパスの順で探索

## 既知の制限事項
- **Windows環境での文字エンコーディング**:
  - cp932でサポートされない文字（一部の絵文字、音符記号♫♬など）は使用不可
  - 基本的な日本語、英数字、一般的な記号は問題なし
  - 回避策：「絵文字を使って」のような説明的な指示を使用
- **Windows環境での非同期実行パフォーマンス**:
  - asyncio + WSL経由の実行で極端な遅延（10-30倍）が発生
  - 同期実行（subprocess.run）を使用することで回避
  - 詳細：`doc/windows_async_performance_issue.md`参照

## デバッグ時の注意点
- **難しい問題に遭遇した場合**：
  - Geminiに相談することを推奨（`mcp__gemini-cli__geminiChat`ツールを使用）
  - 特に非同期処理、プロセス間通信、エンコーディング問題など
  - 例：今回のasyncio stdin継承問題はGeminiの分析により解決
  - Geminiは1会話しか記憶が続かないため、問題の詳細を一度に説明すること

## テスト済み環境
- Windows 11 + WSL2 + Ubuntu
- Claude CLI 1.0.43
- Python 3.8+
- FastMCP 0.8.0
- Windows環境：同期実行で全7機能動作確認済み（平均10秒）
- WSL環境：同期実行で全7機能動作確認済み（平均10秒）
- 非同期版からの改善：Windows環境で93%（136秒→10秒）

## パフォーマンス特性

### 実行時間の目安
- **通常のクエリ**: 8-12秒
- **複雑なクエリ**: 15-30秒
- **ファイルコンテキスト付き**: 12-15秒
- **即時応答（履歴取得等）**: 1秒未満

### 環境別の安定性
- Windows（WSL経由）: 安定動作、cp932エンコーディング制約あり
- WSL/Linux/macOS: 安定動作、エンコーディング制約なし

## MCP設定例（Gemini用）

### Windows上のGemini設定
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

### WSL上のGemini設定
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python3",
      "args": [
        "/mnt/c/prj/AI/prg/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

**注意**: 両環境とも、MCPサーバー自体はWSL上で動作し、Claude CLIもWSL内にインストールされている必要があります。違いはGeminiからMCPサーバーへの接続方法のみです。