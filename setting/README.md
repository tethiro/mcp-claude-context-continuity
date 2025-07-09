# 設定ファイルサンプル

このディレクトリには、各環境用のMCP設定ファイルのサンプルが含まれています。

## ファイル一覧

- `claude_cli_mcp_config_windows.json` - Windows環境用
- `claude_cli_mcp_config_wsl.json` - WSL/Linux/macOS環境用

## 使い方

1. お使いの環境に合ったファイルをコピー
2. パスを実際のインストール場所に変更
3. Geminiの設定ディレクトリに配置

### Windows環境
```
copy claude_cli_mcp_config_windows.json %APPDATA%\gemini-cli\config.json
```

### WSL/Linux/macOS環境
```bash
cp claude_cli_mcp_config_wsl.json ~/.config/gemini-cli/config.json
```

## 注意事項

- パスは絶対パスで指定してください
- Windows環境では`wsl -e`を使用してWSL内のPythonを実行します
- Claude CLIはWSL内にインストールされている必要があります