# Claude CLI セッション管理の詳細仕様

このドキュメントは、Claude CLIのセッション管理機能の詳細な動作仕様をまとめたものです。

**最終更新**: 2025-01-08  
**検証済みバージョン**: Claude CLI 1.0.43

## セッションIDの基本概念

### 1. セッションIDは使い捨て
- 各セッションIDは`--resume`オプションで**1回だけ**使用可能
- 一度使用されたセッションIDを再度使用することはできない

### 2. JSONレスポンスの理解
```json
{
  "response": "こんにちは、太郎さん",
  "session_id": "abc123-def456"
}
```
- `session_id`は「**次回の会話で使うためのID**」
- 現在の会話を識別するIDではない

### 3. セッションIDはタイムスタンプ
セッションIDは会話の「タイムスタンプ」として機能し、その時点の会話状態を表します。

## セッションIDのライフサイクル

### 正常なフロー
```
1. 初回会話 → session_id: AAA を取得
2. --resume AAA で会話継続 → session_id: BBB を取得（AAAは消費済み）
3. --resume BBB で会話継続 → session_id: CCC を取得（BBBは消費済み）
```

### 分岐フロー（正しい使い方）
```
1. 会話A-1 → session_id: AAA
2. 会話A-2（--resume AAA） → session_id: BBB
3. get_current_session() → BBBを保存
4. reset_session() → BBBが使われないようにリセット【重要】
5. 会話B-1 → session_id: XXX
6. set_current_session(BBB) → 会話Aに戻る
7. 会話A-3（--resume BBB） → 会話Aが継続
```

## 重要な発見：セッションIDのタイムスタンプ性

### 実験結果
使用済みのセッションIDでも、その使用時点の会話状態に復元できることが判明しました。

#### 例：会話の流れ
```
1. 「私は太郎です」 → session_id: AAA
2. 「好きな食べ物はラーメン」（--resume AAA） → session_id: BBB
3. 「趣味は読書」（--resume BBB） → session_id: CCC
4. 「秘密の話」（--resume CCC） → session_id: DDD
```

#### 復元時の動作
```
set_current_session(AAA) + execute_claude("何を知っていますか？")
→ 「太郎さんですね」（ラーメン、読書、秘密は知らない）

set_current_session(BBB) + execute_claude("何を知っていますか？")
→ 「太郎さんで、ラーメンが好きですね」（読書、秘密は知らない）

set_current_session(CCC) + execute_claude("何を知っていますか？")
→ 「太郎さんで、ラーメンが好きで、趣味は読書ですね」（秘密は知らない）
```

### 時系列の整合性
- 過去のセッションIDで復元すると、その時点までの会話のみ記憶
- それ以降の会話内容は知らない（未来の情報は持たない）
- これにより、会話の任意の時点に戻って別の分岐を作ることが可能

## よくある誤解と正しい理解

### 誤解1：reset_sessionを忘れると復元不可能
**誤解**: `get_current_session`後に`reset_session`を忘れると、そのセッションIDは永久に失われる

**正解**: reset_sessionを忘れてセッションIDが使われても、そのIDで「使用時点」の状態に復元可能

### 誤解2：セッションIDは会話の識別子
**誤解**: セッションIDは現在進行中の会話を識別するID

**正解**: セッションIDは「次の会話で使うためのID」であり、会話のタイムスタンプとして機能

### 誤解3：使用済みセッションIDは無効
**誤解**: 一度使用されたセッションIDは完全に無効になる

**正解**: 使用済みセッションIDは、その使用時点の会話状態のスナップショットとして有効

## 実用的な使用例

### 1. 会話の分岐管理
```python
# メイン会話を進める
r1 = await execute_claude("プロジェクトの概要を説明して")
s1 = await get_current_session()
branch_point_1 = s1['session_id']

# さらに会話を続ける
r2 = await execute_claude("技術的な詳細を教えて")
s2 = await get_current_session()
branch_point_2 = s2['session_id']

# 後で branch_point_1 に戻って別の質問
await set_current_session(branch_point_1)
r3 = await execute_claude("ビジネス面での利点は？")
```

### 2. 会話履歴の探索
```python
# 各ポイントでセッションIDを記録しながら会話
sessions = []
topics = ["自己紹介", "趣味", "仕事", "将来の夢"]

for topic in topics:
    await execute_claude(f"{topic}について話します...")
    s = await get_current_session()
    sessions.append((topic, s['session_id']))

# 任意の時点に戻る
await set_current_session(sessions[1][1])  # 趣味の話の直後に戻る
```

## デバッグとテスト

### セッション動作確認用テストファイル
- `test_session_timeline.py`: セッションのタイムライン動作確認
- `test_session_id_reuse.py`: 使用済みセッションIDの復元テスト
- `test_session_simple_check.py`: 基本的なセッション復元確認
- `test_session_overrun_debug.py`: セッションオーバーランと時系列整合性の確認

### ログファイル
`claude_command_debug.log`には以下の情報が記録されます：
- セッションIDの更新履歴
- 手動設定されたセッションIDの使用
- コマンド実行時間とレスポンス

## まとめ

Claude CLIのセッション管理は、単なる会話の継続機能を超えて、会話の任意の時点に戻ることができる「タイムマシン」のような機能を提供します。これにより：

1. 複数の会話分岐を管理
2. 過去の任意の時点から会話を再開
3. 異なる文脈での質問を並行して進行

などが可能になり、より柔軟で強力な対話システムを構築できます。