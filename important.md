# 重要な環境動作仕様

## Windows環境とWSL/Linux/macOS環境での動作の違い

### Windows環境
```
Windows Gemini → npm → Windows Python → claude_cli_server.py → WSL経由でClaude CLI
```

**重要ポイント**：
- **Pythonスクリプト（claude_cli_server.py）**: Windows Python で実行
- **Claude CLI**: WSL内にインストール、WSL経由で呼び出し
- **実行方法**: `subprocess.run(['wsl', '--', 'claude', ...])`

### WSL/Linux/macOS環境
```
Gemini → npm → ネイティブPython → claude_cli_server.py → 直接Claude CLI実行
```

**重要ポイント**：
- すべてネイティブ環境で完結
- **実行方法**: `subprocess.run(['claude', ...])`

## 実装の詳細

### bin/mcp-claude-context-continuity
```javascript
if (process.platform === 'win32') {
  // Windows: Windows Python を使用
  const child = spawn(pythonCmd, [scriptPath], {
    stdio: 'inherit'
  });
} else {
  // Unix系: ネイティブPython を使用
  const child = spawn(pythonCmd, [scriptPath], {
    stdio: 'inherit'
  });
}
```

### claude_cli_server.py での環境判定
```python
if platform.system() == "Windows":
    # Windows環境: WSL経由でClaude CLI実行
    # cmd = ['wsl', '--', '/path/to/claude', ...]
    encoding_kwargs = {'encoding': 'utf-8', 'errors': 'replace'}
else:
    # Unix系環境: 直接Claude CLI実行
    # cmd = ['/path/to/claude', ...]
    encoding_kwargs = {'encoding': 'utf-8'}
```

## 必要条件の違い

### Windows環境
- **Python**: Windows側にインストール必要
- **Claude CLI**: WSL内にインストール必要
- **WSL2**: 必須
- **NPM**: Windows側にインストール

### WSL/Linux/macOS環境
- **Python**: ネイティブ環境にインストール
- **Claude CLI**: ネイティブ環境にインストール
- **NPM**: ネイティブ環境にインストール

## 設定例

### Windows環境での設定
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "mcp-claude-context-continuity"
    }
  }
}
```

### WSL/Linux/macOS環境での設定
```json
{
  "mcpServers": {
    "claude-cli-server": {
      "command": "mcp-claude-context-continuity"
    }
  }
}
```

※設定は同じだが、内部動作が異なる

## トラブルシューティング

### Windows環境
1. Windows PythonでFastMCPがインストールされているか確認
2. WSL内にClaude CLIがインストールされているか確認
3. WSL2が正常に動作しているか確認

### WSL/Linux/macOS環境
1. ネイティブPythonでFastMCPがインストールされているか確認
2. Claude CLIがPATHに含まれているか確認

## 歴史的経緯

### 修正前（v1.0.0）
- Windows環境でもWSL内のPythonを使用していた
- 設計意図と異なる動作

### 修正後（v1.0.1）
- Windows環境でWindows Pythonを使用
- 設計意図通りの動作を実現

## 開発時の注意点

1. **環境の違いを意識する**: Windows環境とUnix系環境で動作が異なる
2. **テスト環境**: 両環境でのテストが必要
3. **依存関係**: 各環境で適切な依存関係をインストール
4. **パスの形式**: Windows→WSL間でのパス変換に注意

## 参考情報

- **プロジェクトルート**: `/mnt/c/prj/AI/prg/mcp-claude-context-continuity`
- **デバッグログ**: `claude_command_debug.log`
- **設定ファイル**: `~/.gemini/settings.json` (WSL) / `%USERPROFILE%\.gemini\settings.json` (Windows)

---

このファイルは、環境間の動作の違いを理解し、適切に設定・デバッグするための重要な資料です。