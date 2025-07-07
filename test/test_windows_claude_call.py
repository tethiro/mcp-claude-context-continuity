#!/usr/bin/env python3
"""Windows環境からClaude CLIを呼び出すテストプログラム"""

import subprocess
import sys
import platform
import time
import json

def test_simple_version():
    """シンプルな--versionテスト"""
    print("=== Test 1: Simple --version ===")
    cmd = ["wsl", "--", "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude", "--version"]
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        print(f"Success: {result.returncode == 0}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_echo():
    """echoコマンドでテスト（JSON出力なし）"""
    print("=== Test 2: Echo without JSON ===")
    cmd = [
        "wsl", "--", 
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "-p", "echo test"
    ]
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)} chars")
        if len(result.stdout) < 500:
            print(f"Stdout: {result.stdout}")
        else:
            print(f"Stdout (first 500 chars): {result.stdout[:500]}...")
        print(f"Stderr: {result.stderr}")
        print(f"Success: {result.returncode == 0}")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after 30 seconds!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_json():
    """JSON出力でテスト"""
    print("=== Test 3: With JSON output ===")
    cmd = [
        "wsl", "--", 
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "Say just 'Hello' and nothing else"
    ]
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                print(f"JSON parsed successfully!")
                print(f"Result: {data.get('result', 'No result field')}")
                print(f"Session ID: {data.get('session_id', 'No session_id field')}")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
        
        print(f"Success: {result.returncode == 0}")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after 30 seconds!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_japanese():
    """日本語でテスト"""
    print("=== Test 4: Japanese prompt ===")
    cmd = [
        "wsl", "--", 
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "こんにちは"
    ]
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL, encoding='utf-8')
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Success: {result.returncode == 0}")
        
        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                print(f"JSON parsed successfully!")
                print(f"Result preview: {data.get('result', '')[:100]}...")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                print(f"Raw output: {result.stdout[:200]}...")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after 30 seconds!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_popen():
    """Popenを使ったテスト（より細かい制御）"""
    print("=== Test 5: Using Popen ===")
    cmd = [
        "wsl", "--", 
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "Say hello"
    ]
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding='utf-8'
        )
        
        print("Process started, waiting for completion...")
        stdout, stderr = proc.communicate(timeout=30)
        elapsed = time.time() - start
        
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {proc.returncode}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        print(f"Success: {proc.returncode == 0}")
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after 30 seconds!")
        proc.kill()
        stdout, stderr = proc.communicate()
        print(f"Killed process output: {stdout}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def main():
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print()
    
    # 各テストを実行
    test_simple_version()
    test_with_echo()
    test_with_json()
    test_with_japanese()
    test_with_popen()
    
    print("\n=== Test Summary ===")
    print("Check the results above to see which method works best.")
    print("If all tests timeout, there might be an issue with:")
    print("1. WSL configuration")
    print("2. Claude CLI installation")
    print("3. Network/firewall settings")
    print("4. Windows Defender or antivirus software")

if __name__ == "__main__":
    main()