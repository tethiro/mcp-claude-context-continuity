# 同期実行への統一

記録日: 2025年1月8日

## 概要

Claude CLI MCP Serverの実装を、全環境（Windows/WSL/Linux/macOS）で同期実行（subprocess.run）に統一しました。

## 統一の理由

1. **MCPの特性**
   - MCPサーバーは1対1通信モデル
   - 1つのサーバープロセスは1つのクライアントとのみ通信
   - 並行処理の必要性がない

2. **パフォーマンス問題**
   - Windows環境で非同期実行時に極端な遅延（10-30倍）
   - 同期実行では安定して高速（8-10秒）

3. **コードの簡潔性**
   - プラットフォーム別の分岐コードを削減
   - 保守性の向上
   - Geminiが指摘した「コードの重複」問題を解決

## 実装の変更点

### 変更前
```python
# Windows環境
if platform.system() == "Windows":
    # 同期実行
    result = subprocess.run(cmd, ...)
else:
    # Unix系環境では非同期実行
    proc = await asyncio.create_subprocess_exec(...)
```

### 変更後
```python
# 全環境で同期実行
# エンコーディング設定のみ環境別
if platform.system() == "Windows":
    encoding_kwargs = {'encoding': 'utf-8', 'errors': 'replace'}
else:
    encoding_kwargs = {'encoding': 'utf-8'}

result = subprocess.run(cmd, ..., **encoding_kwargs)
```

## 環境別の違い（呼び出し方）

統一後も、Claude CLIの呼び出し方は環境によって異なります：

- **Windows**: `['wsl', '--', '/path/to/claude', ...]`（WSL経由）
- **WSL/Unix**: `['/path/to/claude', ...]`（直接実行）

## 影響を受けた関数

1. `_execute_claude_command()` - メインの実行関数
2. `execute_claude_with_context()` - ファイルコンテキスト付き実行
3. `test_claude_cli()` - Claude CLI動作確認

## メリット

1. **コードの簡潔性**: 約100行のコード削減
2. **保守性の向上**: プラットフォーム分岐が最小限
3. **安定性**: 全環境で同じ実行方式
4. **パフォーマンス**: Windows環境での問題を回避

## テスト結果

- Windows環境: 正常動作（8-10秒）
- WSL環境: 正常動作
- Linux/macOS: 理論上問題なし（同期実行は標準的）

## 今後の課題

特になし。MCPの1対1通信モデルには同期実行が最適。

## 追加の最適化（2025年1月8日）

### コマンド構築ロジックの共通化

Windows版とUnix版でコマンド構築ロジックを共通化しました：

1. **共通メソッドの追加**:
   - `build_claude_command()`: 通常のClaude実行コマンド構築
   - `build_claude_version_command()`: --versionコマンド構築

2. **実装の詳細**:
```python
def build_claude_command(self, claude_cmd, prompt):
    base_args = ["--dangerously-skip-permissions", "--output-format", "json"]
    # --resumeやプロンプトを追加
    
    if isinstance(claude_cmd, str):
        # Unix系: ['/path/to/claude'] + args
        return [claude_cmd] + base_args
    else:
        # Windows: ['wsl', '--', '/path/to/claude'] + args
        return claude_cmd + base_args
```

3. **メリット**:
   - コード重複の削除（約40行削減）
   - 保守性の向上
   - Windows/Unix系の違いを1箇所で管理