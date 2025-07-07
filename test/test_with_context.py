#!/usr/bin/env python3
"""execute_claude_with_contextのテスト"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_cli_server import execute_claude_with_context

async def test_context():
    # テスト用ファイル作成
    test_file = "/tmp/test_code.py"
    with open(test_file, "w") as f:
        f.write("""def hello():
    return "Hello, World!"
""")
    
    print("ファイルコンテキストテスト")
    print(f"ファイル: {test_file}")
    
    result = await execute_claude_with_context(
        "このコードは何をしていますか？簡潔に説明してください。",
        test_file,
        timeout=30
    )
    
    if result["success"]:
        print(f"✅ 成功: {result['response']}")
    else:
        print(f"❌ 失敗: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_context())