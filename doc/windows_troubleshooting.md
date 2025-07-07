# Windows環境でのトラブルシューティング

## 「No tools available」エラーの解決方法

### 1. Pythonパスの確認
Windows環境でPythonが正しくインストールされているか確認：
```bash
python --version
```

### 2. 設定ファイルの選択
以下の設定ファイルから環境に合わせて選択してください：

#### a) 標準的なPython環境
`setting/claude_cli_mcp_config_windows_final.json`
```json
{
  "mcpServers": {
    "claude-context-continuity": {
      "command": "python",
      "args": [
        "C:\\prj\\AI\\prg\\mcp-claude-context-continuity\\src\\claude_cli_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\prj\\AI\\prg\\mcp-claude-context-continuity\\src"
      }
    }
  }
}
```

#### b) Pythonのフルパスを指定
`setting/claude_cli_mcp_config_windows_fullpath.json`
- `C:\\Python312\\python.exe`の部分を実際のPythonインストールパスに変更してください

#### c) WSL経由で実行
`setting/claude_cli_mcp_config_windows.json`
- WSLがインストールされている環境で使用

### 3. デバッグ手順

1. **デバッグ版の実行**
   ```bash
   python C:\prj\AI\prg\mcp-claude-context-continuity\src\claude_cli_server_debug.py
   ```
   `debug_mcp_startup.log`ファイルを確認

2. **最小限のテスト**
   `setting/minimal_mcp_config_windows.json`を使用して、最小限のMCPサーバーが動作するか確認

3. **直接テスト**
   ```bash
   python test\test_windows_direct.py
   ```

### 4. 一般的な問題と解決策

#### 問題: Pythonモジュールが見つからない
**解決策**: 
- `pip install -r requirements.txt`を実行
- PYTHONPATHを設定ファイルで指定

#### 問題: タイムアウトエラー
**解決策**: 
- Windows Defenderやアンチウイルスソフトの例外設定にPythonを追加
- ファイアウォールの設定を確認

#### 問題: パスの問題
**解決策**: 
- バックスラッシュを二重にする（`\\`）
- 絶対パスを使用する

### 5. 推奨設定
最も安定して動作する設定：
1. `claude_cli_mcp_config_windows_final.json`を使用
2. Python 3.10以上をインストール
3. 必要なパッケージをインストール：
   ```bash
   pip install mcp
   ```

### 6. 確認コマンド
MCPサーバーが正しく起動しているか確認：
```bash
python test\test_mcp_stdio.py
```

成功すると以下のような出力が表示されます：
```
✅ Server initialized successfully!
Server name: claude-cli-server
Server version: 1.10.1
```