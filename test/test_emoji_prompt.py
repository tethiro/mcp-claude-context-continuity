#!/usr/bin/env python3
"""絵文字を含むプロンプトのテスト"""

import asyncio
import sys
import os

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import claude_cli_server

async def test_emoji():
    """絵文字を含むプロンプトをテスト"""
    print("=== Emoji Prompt Test ===\n")
    
    # 絵文字を含むプロンプト
    prompt = "絵文字😊🎉と記号（♪♫♬）を使って楽しい新年の挨拶をしてください"
    
    print(f"Testing prompt: {prompt}")
    print("Prompt bytes:", prompt.encode('utf-8'))
    print()
    
    try:
        result = await claude_cli_server.execute_claude(prompt)
        print(f"Success: {result.get('success')}")
        print(f"Tool name: {result.get('tool_name')}")
        
        if result.get('success'):
            print(f"Response: {result.get('response')}")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_emoji()

if __name__ == "__main__":
    asyncio.run(main())