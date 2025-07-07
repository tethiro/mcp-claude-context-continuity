#!/usr/bin/env python3
"""Windows PythonからWSL経由でClaude CLIを直接テスト"""

import subprocess
import platform
import json
import time

def test_wsl_claude():
    print("=" * 60)
    print("WSL Claude CLI Direct Test")
    print(f"Platform: {platform.system()}")
    print("=" * 60)
    
    if platform.system() != "Windows":
        print("This test is for Windows only")
        return
    
    # 1. WSLの動作確認
    print("\n1. Testing WSL...")
    try:
        result = subprocess.run(["wsl", "--", "echo", "Hello from WSL"], 
                              capture_output=True, text=True, timeout=5)
        print(f"✅ WSL works: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ WSL error: {e}")
        return
    
    # 2. WSL内のClaude CLIを確認
    print("\n2. Finding Claude in WSL...")
    try:
        result = subprocess.run(["wsl", "--", "bash", "-lc", "which claude"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            claude_path = result.stdout.strip()
            print(f"✅ Claude found: {claude_path}")
        else:
            print(f"❌ Claude not found")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Claude CLIのバージョン確認
    print("\n3. Testing Claude CLI version...")
    try:
        result = subprocess.run(["wsl", "--", claude_path, "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Claude version: {result.stdout.strip()}")
        else:
            print(f"❌ Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 4. 簡単なClaude CLI実行テスト（短いタイムアウト）
    print("\n4. Testing simple Claude execution...")
    cmd = [
        "wsl", "--", claude_path,
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "Say just 'Hi'"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"Return code: {result.returncode}")
        print(f"Elapsed time: {elapsed:.2f}s")
        
        if result.returncode == 0:
            print("✅ Success")
            print(f"stdout length: {len(result.stdout)} chars")
            try:
                response = json.loads(result.stdout)
                print(f"Result: {response.get('result', 'No result field')}")
            except json.JSONDecodeError:
                print(f"Raw output: {result.stdout[:200]}...")
        else:
            print(f"❌ Failed")
            print(f"stderr: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout after 30 seconds")
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_wsl_claude()