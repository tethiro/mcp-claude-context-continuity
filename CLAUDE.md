# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要
Counter MCP Server - シンプルなカウンター機能を提供するMCP（Model Context Protocol）サーバー

## 技術スタック
- Python 3.8+
- MCP (Model Context Protocol) - stdio トランスポート

## 開発コマンド

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### サーバーの起動
```bash
python server.py
```

### テストの実行
```bash
python -m pytest test_server.py
```

## アーキテクチャ

### コア機能
5つの基本機能を実装：
- `count_up`: カウンターを増加（ステップ値指定可能）
- `count_down`: カウンターを減少（ステップ値指定可能）
- `get_count`: 現在のカウント値を取得
- `reset_count`: カウンターをリセット（デフォルト0）
- `get_history`: カウント操作の履歴を取得

### 重要な仕様
- カウンター値の範囲: -1000 〜 1000
- 履歴は最新100件まで保持
- セッションごとに独立したカウンター管理
- エラー時はデフォルト値で処理

### ファイル構造
```
counter-mcp-server/
├── server.py          # メインサーバー実装
├── requirements.txt   # 依存関係
├── README.md         # 使用方法
└── test_server.py    # テストコード
```

## 開発時の注意点
- MCP仕様に準拠したツール定義を実装
- stdio経由でのJSON-RPC通信
- 非同期処理（async/await）を使用
- 範囲チェックと適切なエラーハンドリング