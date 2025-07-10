# Specifications.md

MCP Claude Context Continuity プロジェクトの技術仕様書

## 重要な動作原理

### MCPサーバーの実行環境
**最重要**: MCPサーバーは常にホストOSのPythonで実行されます
- Windows環境: Windows版Python（`python.exe`）で実行
- WSL/Linux/macOS環境: ネイティブPythonで実行

### Claude CLIの実行環境
- Windows環境: WSL経由で実行（MCPサーバーから`wsl --`経由で呼び出し）
- WSL/Linux/macOS環境: 直接実行

この違いを理解することは、正しい設定と動作のために極めて重要です。

## プロジェクト概要
Claude CLIの会話コンテキストを保持するMCP（Model Context Protocol）サーバー

## 技術スタック
- Python 3.8+
- FastMCP 0.1.0+
- Claude CLI (WSL内にインストール)
- 非同期処理 (asyncio) - MCPフレームワークで使用

## アーキテクチャ

### MCPサーバープロセスモデル
MCPサーバーの実行環境とプロセス管理に関する重要な仕様：

#### プロセスライフサイクル
- **常駐プロセス**: MCPサーバーはGeminiセッション中は常駐プロセスとして動作
- **独立性**: 各Geminiインスタンスが独自のMCPサーバープロセスを起動
- **状態管理**: セッション状態は各プロセスのメモリ内で保持
- **並行実行**: 複数のGeminiインスタンスが同時に実行可能（相互干渉なし）

#### 実行環境の重要な違い
- **MCPサーバー自体の実行環境**:
  - Windows: Windows版Pythonで直接実行
  - WSL/Linux/macOS: ネイティブPythonで直接実行
  - **重要**: MCPサーバーは常にホストOSのPythonインタープリターで実行される

- **Claude CLIの実行環境**:
  - Windows: WSL経由で実行（`["wsl", "--", "/path/to/claude"]`）
  - WSL/Linux/macOS: 直接実行（`"/path/to/claude"`）
  - **重要**: Claude CLIは常にWSL/Linux環境内で実行される

#### プロセス間の関係
```
Windows環境の例:
Gemini → Windows Python → MCP Server Process
                         ↓
                    subprocess.run()
                         ↓
                    WSL → Claude CLI

WSL/Linux環境の例:
Gemini → Native Python → MCP Server Process
                        ↓
                   subprocess.run()
                        ↓
                   Claude CLI (直接)
```

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

## メモリ内状態管理

### 保持される状態
MCPサーバープロセスは以下の状態をメモリ内で管理：

1. **現在のセッションID** (`current_session_id`)
   - 未使用のセッションID（次回の`--resume`で使用可能）
   - `reset_session()`で新規生成

2. **実行履歴** (`execution_history`)
   - 最大100件の実行ログを保持
   - 各エントリには実行時刻、プロンプト、レスポンス、セッションIDを記録

3. **Claude CLIパス** (`claude_cli_path`)
   - 初回検出時にキャッシュ
   - プロセス終了まで再利用

### 状態の永続性
- **プロセス内**: すべての状態はプロセス存続中は保持される
- **プロセス間**: 各Geminiインスタンスは独立した状態を持つ
- **永続化なし**: プロセス終了時にすべての状態は失われる

## 制限事項
1. 並列実行は不可（セッション継続性保持のため）
2. 履歴は最新100件まで（メモリ内保持）
3. Windows環境では一部の特殊文字（絵文字等）に制限
4. プロセス終了時にセッション状態は失われる（永続化なし）

## 設定例

### Windows環境
**重要**: Windows環境では、MCPサーバーはWindows版Pythonで実行されます。以下は誤った設定例です。

```json
// ❌ 誤った設定 - WSL経由でMCPサーバーを起動しようとしている
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

**正しい設定**:
```json
// ✅ 正しい設定 - Windows版Pythonで直接実行
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python",
      "args": [
        "C:\\path\\to\\src\\claude_cli_server.py"
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