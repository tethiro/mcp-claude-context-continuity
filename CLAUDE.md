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
# Claude CLI探索テスト
python test/test_find_claude.py

# MCPサーバー動作テスト
python test/test_claude_cli_server_simple.py
```

## アーキテクチャ

### コア機能
7つのMCPツールを提供：
- `execute_claude`: Claude CLIを実行して結果を返す
- `execute_claude_with_context`: ファイルコンテキスト付きでClaude CLIを実行
- `get_execution_history`: 実行履歴を取得（最新10件）
- `clear_execution_history`: 実行履歴をクリア
- `get_current_session`: 現在のセッションIDを取得
- `reset_session`: セッションをリセット
- `test_claude_cli`: Claude CLIの動作確認（デバッグ用）

### 重要な仕様
- **セッション継続機能（最重要）**: 
  - `--resume`オプションでClaude CLIの会話コンテキストを保持
  - 初回: `claude --dangerously-skip-permissions --output-format json -p "質問"`
  - 2回目以降: `claude --dangerously-skip-permissions --output-format json --resume <session_id> -p "質問"`
  - これにより前回の会話内容を記憶した状態で対話が可能
- **必須オプション**: 
  - `--dangerously-skip-permissions`: 権限確認をスキップ（必須）
  - `--output-format json`: JSON形式で出力（session_id取得のため必須）
- **タイムアウト**: 
  - DEFAULT_TIMEOUT = 30秒（実装）
  - 仕様書では300秒だが、現在の実装は30秒に設定
- **制約事項**:
  - 並列実行は不可（--resumeによるセッション継続性を保つため）
  - 履歴は最新100件まで保持（メモリ内のみ）
- **クロスプラットフォーム**: Windows（WSL経由）、Linux、macOS対応

### ファイル構造
```
mcp-claude-context-continuity/
├── src/
│   ├── claude_cli_server.py         # メインMCPサーバー実装
│   ├── claude_cli_server_debug.py   # デバッグ版
│   ├── claude_cli_server_windows_fix.py  # Windows対応テスト版（非推奨）
│   └── minimal_mcp_server.py        # 最小限のテストサーバー
├── test/
│   ├── test_find_claude.py          # Claude CLI探索テスト
│   ├── test_claude_cli_server_simple.py  # 動作テスト
│   └── test_mcp_stdio.py            # MCP通信テスト
├── setting/
│   ├── claude_cli_mcp_config_windows.json  # Windows設定例
│   └── claude_cli_mcp_config_wsl.json      # WSL/Unix設定例
├── doc/
│   └── claude_cli_mcp_server_specification.md  # 詳細仕様書
├── requirements.txt                  # Python依存関係
├── package.json                      # npm package設定
└── README.md                         # 使用方法
```

## 開発時の注意点
- **Windows環境**: WSL経由でClaude CLIを実行するため、`subprocess.run()`にstdin=subprocess.DEVNULLを指定
- **エラーハンドリング**: タイムアウト、JSON解析エラー、ファイル読み込みエラーを適切に処理
- **デバッグ**: `claude_command_debug.log`にコマンド実行ログを記録
- **セッション管理**: ClaudeSessionManagerクラスでsession_idを永続的に保持
- **Claude CLI探索**: 
  - Unix系: which, 一般的なパス、環境変数の順で探索
  - Windows: WSL内のbash -lcでPATHを適切に設定して探索

## 現在の問題点
- **Windows環境でのタイムアウト問題**: 
  - WSL経由でClaude CLIを実行すると30秒でタイムアウトする
  - `stdin=subprocess.DEVNULL`を指定しても解決していない
  - 実行コマンドは`claude_command_debug.log`で確認可能

## 今後の課題
- Windows環境でのタイムアウト問題の根本的解決
- npmパッケージとしての公開準備（@local/claude-context-continuity）
- 実行履歴の永続化（現在はメモリ内のみ）
- タイムアウト値の統一（実装:30秒 vs 仕様書:300秒）
- Claude CLI探索結果の永続キャッシュ