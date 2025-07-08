#!/usr/bin/env python3
"""空のresultフィールド処理のテスト"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.claude_cli_server import execute_claude


async def test_empty_result_handling():
    """長い処理で空のresultが返った場合の動作確認"""
    
    print("=== 空のresultフィールド処理テスト ===\n")
    
    # ファイル出力を要求するプロンプト（長い処理になりやすい）
    prompt = """
    以下の内容で test_output.md というファイルを作成してください：
    
    # テストドキュメント
    
    このドキュメントは、Claude CLI MCP Serverのテスト用です。
    
    ## セクション1
    長い内容を含むドキュメントを生成して、
    error_during_executionが発生するかテストします。
    
    ## セクション2
    - 項目1
    - 項目2
    - 項目3
    
    （これを20セクションまで続けてください）
    """
    
    print("1. 長い処理を要求するプロンプトを送信...")
    print(f"プロンプト: {prompt[:100]}...")
    
    result = await execute_claude(prompt)
    
    print("\n2. 結果:")
    print(f"成功: {result['success']}")
    print(f"実行時間: {result['execution_time']:.1f}秒")
    
    if result.get('warning'):
        print(f"警告: {result['warning']}")
    
    if result.get('error'):
        print(f"エラー: {result['error']}")
    
    print(f"\n3. レスポンス:")
    print("-" * 50)
    print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])
    print("-" * 50)
    
    # ファイルが作成されたか確認
    if os.path.exists("test_output.md"):
        print("\n4. ファイル確認: test_output.md が作成されました")
        with open("test_output.md", "r") as f:
            content = f.read()
            print(f"   ファイルサイズ: {len(content)} バイト")
        os.remove("test_output.md")  # クリーンアップ
    else:
        print("\n4. ファイル確認: test_output.md は作成されませんでした")


if __name__ == "__main__":
    asyncio.run(test_empty_result_handling())