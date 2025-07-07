# WSL環境でのClaude Desktop設定

## 設定ファイルの場所

WSL環境でClaude Desktopを使用する場合、設定ファイルは以下の場所に配置します：

```
~/.config/Claude/claude_desktop_config.json
```

## Python起動版の設定

### 1. 基本設定（相対パス版）

現在のユーザーのホームディレクトリからの相対パスを使用：

```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python3",
      "args": [
        "./mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

### 2. 絶対パス版

フルパスを指定する場合：

```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python3",
      "args": [
        "/home/YOUR_USERNAME/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

### 3. 環境変数を使用する版

```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "python3",
      "args": [
        "${HOME}/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

### 4. venv（仮想環境）を使用する場合

```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "/home/YOUR_USERNAME/mcp-claude-context-continuity/venv/bin/python",
      "args": [
        "/home/YOUR_USERNAME/mcp-claude-context-continuity/src/claude_cli_server.py"
      ]
    }
  }
}
```

## 設定手順

1. 設定ディレクトリを作成：
```bash
mkdir -p ~/.config/Claude
```

2. 設定ファイルを作成または編集：
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

3. 上記の設定のいずれかをコピーして貼り付け

4. `YOUR_USERNAME`を実際のユーザー名に置き換え：
```bash
echo $USER  # 現在のユーザー名を確認
```

5. 設定を保存して、Claude Desktopを再起動

## パスの確認方法

プロジェクトの絶対パスを確認：
```bash
cd ~/mcp-claude-context-continuity
pwd
# 出力例: /home/tethiro/mcp-claude-context-continuity
```

Python3の場所を確認：
```bash
which python3
# 出力例: /usr/bin/python3
```

## トラブルシューティング

### 権限エラーの場合

実行権限を付与：
```bash
chmod +x ~/mcp-claude-context-continuity/src/claude_cli_server.py
```

### Pythonパッケージが見つからない場合

依存関係をインストール：
```bash
cd ~/mcp-claude-context-continuity
pip3 install -r requirements.txt
```

### ログの確認

デバッグログの場所：
```bash
tail -f ~/mcp-claude-context-continuity/claude_command_debug.log
```