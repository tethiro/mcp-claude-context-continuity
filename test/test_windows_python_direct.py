#!/usr/bin/env python3
"""Windows版Pythonから直接実行するテスト"""

import asyncio
import sys
import os
import platform

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claude_cli_server import session_manager, execute_claude

async def test_windows_execution():
    print("=" * 60)
    print("Windows Python Direct Execution Test")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"OS: {platform.system()}")
    print("=" * 60)
    
    # 1. Claude CLIの探索
    print("\n1. Finding Claude CLI...")
    try:
        claude_cmd = await session_manager.get_claude_command()
        print(f"✅ Found: {claude_cmd}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. WSLの確認
    print("\n2. Checking WSL...")
    if platform.system() == "Windows":
        import subprocess
        try:
            result = subprocess.run(["wsl", "--", "echo", "WSL is working"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ WSL: {result.stdout.strip()}")
            else:
                print(f"❌ WSL Error: {result.stderr}")
        except Exception as e:
            print(f"❌ WSL not available: {e}")
    
    # 3. 簡単なテスト実行
    print("\n3. Testing execute_claude...")
    print("Prompt: 'こんにちは'")
    
    try:
        result = await execute_claude("こんにちは", timeout=30)
        
        if result["success"]:
            print(f"✅ Success")
            print(f"Response: {result['response']}")
            print(f"Execution time: {result['execution_time']:.2f}s")
        else:
            print(f"❌ Failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Windowsでのasyncioイベントループポリシー設定
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(test_windows_execution())