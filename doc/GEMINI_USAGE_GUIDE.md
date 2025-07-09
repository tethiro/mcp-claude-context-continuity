# Gemini向け使用ガイド

このドキュメントは、GeminiからMCP Claude Context Continuityサーバーを使用する際のガイドです。

## セットアップ

### 1. 設定ファイルの場所

- **Windows**: `%APPDATA%\gemini-cli\config.json`
- **WSL/Linux/macOS**: `~/.config/gemini-cli/config.json`

### 2. 設定例

設定ファイルは`setting/`ディレクトリにサンプルがあります：
- `claude_cli_mcp_config_windows.json` - Windows用
- `claude_cli_mcp_config_wsl.json` - WSL/Linux/macOS用

## 重要な注意事項

### プロンプトは文字列として渡す

❌ **間違った例**（JSONオブジェクトとして渡す）:
```json
{
  "prompt": {"tool": "execute_claude", "prompt": "質問内容"}
}
```

✅ **正しい例**（文字列として渡す）:
```python
execute_claude(prompt="質問内容")
```

## 基本的な使い方

### 1. 単純な質問
```python
execute_claude(prompt="こんにちは")
```

### 2. 会話の継続
```python
# 初回
execute_claude(prompt="私は田中です")

# 2回目（前回の内容を覚えている）
execute_claude(prompt="私の名前を覚えていますか？")
# → "はい、田中さんですね"
```

### 3. ファイルを含む質問
```python
execute_claude_with_context(
    prompt="このコードを説明してください",
    file_path="/path/to/code.py"
)
```

## セッション管理

### 会話の保存と復元

```python
# 1. 現在の会話を保存
current = get_current_session()
saved_id = current["session_id"]

# 2. 必ずリセット（重要！）
reset_session()

# 3. 新しい会話を開始
execute_claude(prompt="別の話題について")

# 4. 保存した会話に戻る
set_current_session(session_id=saved_id)

# 5. 前の会話を継続
execute_claude(prompt="さっきの話の続きですが...")
```

### 複数の会話を管理

```python
# 会話A: 技術的な質問
execute_claude(prompt="Pythonについて教えて")
session_a = get_current_session()["session_id"]
reset_session()

# 会話B: 別の話題
execute_claude(prompt="料理について教えて")
session_b = get_current_session()["session_id"]
reset_session()

# 会話Aに戻る
set_current_session(session_id=session_a)
execute_claude(prompt="Pythonの続きですが...")

# 会話Bに戻る
set_current_session(session_id=session_b)
execute_claude(prompt="料理の続きですが...")
```

## パラメータの型

| ツール | パラメータ | 型 | 必須 |
|--------|-----------|-----|------|
| execute_claude | prompt | string | ✓ |
| execute_claude_with_context | prompt | string | ✓ |
| execute_claude_with_context | file_path | string | ✓ |
| get_execution_history | limit | integer | - |
| get_current_session | - | - | - |
| set_current_session | session_id | string | ✓ |
| reset_session | - | - | - |
| clear_execution_history | - | - | - |
| test_claude_cli | - | - | - |

## トラブルシューティング

### エラー: "Input should be a valid string"

このエラーは、プロンプトをJSONオブジェクトとして渡した場合に発生します。
必ず文字列として渡してください。

### セッションが混在する

`get_current_session()`の後は必ず`reset_session()`を実行してください。
そうしないと、保存したセッションIDが次の会話で使われてしまいます。

### Windows環境での文字化け

Windows環境では、一部の特殊文字（絵文字など）が表示できない場合があります。
これは正常な動作です。

## ベストプラクティス

1. **シンプルに使う**: 複雑なJSONを構築せず、シンプルな関数呼び出しとして使用
2. **型を守る**: promptは文字列、limitは整数
3. **セッション管理のルール**: get_current_session → reset_session の順序を守る
4. **エラーメッセージを読む**: 型の不一致エラーに注意

## 使用例：デバッグテストの実行

デバッグ用のテストプロンプトを実行する場合：

```python
execute_claude_with_context(
    prompt="ファイル内の指示に従ってテストを実行してください",
    file_path="/path/to/debug_test_prompts_simple.txt"
)
```