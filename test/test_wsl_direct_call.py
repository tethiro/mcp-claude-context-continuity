#!/usr/bin/env python3
"""WSL環境から直接Claude CLIを呼び出すテスト"""

import subprocess
import json
import time

def test_direct_call():
    """WSL環境からの直接呼び出し"""
    print("=== WSL Direct Call Test ===\n")
    
    cmd = [
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "こんにちは"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("Executing...")
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        elapsed = time.time() - start
        
        print(f"\nElapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("\nStdout:")
            try:
                response = json.loads(result.stdout)
                print(json.dumps(response, indent=2, ensure_ascii=False))
            except:
                print(result.stdout[:500])
                
        if result.stderr:
            print(f"\nStderr: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT after 30 seconds!")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_direct_call()