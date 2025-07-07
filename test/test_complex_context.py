#!/usr/bin/env python3
"""より複雑なファイルコンテキストのテスト"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_cli_server import execute_claude_with_context

async def test_complex_context():
    # より複雑なテスト用ファイル作成
    test_file = "/tmp/test_complex.py"
    with open(test_file, "w") as f:
        f.write('''class Calculator:
    """簡単な計算機クラス"""
    
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        """2つの数を足す"""
        self.result = x + y
        return self.result
    
    def multiply(self, x, y):
        """2つの数を掛ける"""
        self.result = x * y
        return self.result
    
    def get_result(self):
        """最後の計算結果を返す"""
        return self.result

# 使用例
calc = Calculator()
print(calc.add(5, 3))      # 8
print(calc.multiply(4, 7)) # 28
print(calc.get_result())   # 28
''')
    
    print("複雑なファイルコンテキストテスト")
    print(f"ファイル: {test_file}")
    
    result = await execute_claude_with_context(
        "このクラスの主な機能を3つ挙げてください。",
        test_file,
        timeout=30
    )
    
    if result["success"]:
        print(f"✅ 成功:")
        print(f"応答: {result['response']}")
        print(f"実行時間: {result['execution_time']:.2f}秒")
    else:
        print(f"❌ 失敗: {result['error']}")
    
    # セッションIDも確認
    print(f"\nセッション継続性も確認:")
    from claude_cli_server import get_current_session
    session_info = await get_current_session()
    print(f"セッションID: {session_info['session_id']}")

if __name__ == "__main__":
    asyncio.run(test_complex_context())