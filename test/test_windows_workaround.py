#!/usr/bin/env python3
"""Windows環境でのClaude CLI呼び出しの回避策テスト"""

import subprocess
import sys
import platform
import time
import tempfile
import os

def test_with_script_file():
    """スクリプトファイル経由で実行"""
    print("=== Test with Script File ===")
    
    # 一時的なスクリプトファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        script_path = f.name
        f.write("""#!/bin/bash
export PATH="/home/tethiro/.nvm/versions/node/v22.17.0/bin:$PATH"
claude --dangerously-skip-permissions --output-format json -p "Hello from script"
""")
    
    try:
        # WSLパスに変換
        wsl_script_path = script_path.replace('\\', '/').replace('C:', '/mnt/c')
        
        # スクリプトに実行権限を付与
        subprocess.run(["wsl", "--", "chmod", "+x", wsl_script_path], capture_output=True)
        
        # スクリプトを実行
        cmd = ["wsl", "--", "bash", wsl_script_path]
        print(f"Running script: {wsl_script_path}")
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        elapsed = time.time() - start
        
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:500]}")
        print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.unlink(script_path)
    print()

def test_with_input_file():
    """入力ファイル経由で実行"""
    print("=== Test with Input File ===")
    
    # 一時的な入力ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        input_path = f.name
        f.write("Hello from input file")
    
    try:
        # WSLパスに変換
        wsl_input_path = input_path.replace('\\', '/').replace('C:', '/mnt/c')
        
        # catでファイルを読み込んでパイプ
        cmd = [
            "wsl", "--", "bash", "-c",
            f"cat {wsl_input_path} | /home/tethiro/.nvm/versions/node/v22.17.0/bin/claude --dangerously-skip-permissions --output-format json -p"
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        elapsed = time.time() - start
        
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:500]}")
        print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.unlink(input_path)
    print()

def test_with_nohup():
    """nohupを使用してバックグラウンド実行"""
    print("=== Test with nohup ===")
    
    cmd = [
        "wsl", "--", "bash", "-c",
        "nohup /home/tethiro/.nvm/versions/node/v22.17.0/bin/claude --dangerously-skip-permissions --output-format json -p 'Hello nohup' > /tmp/claude_output.txt 2>&1 && cat /tmp/claude_output.txt"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        elapsed = time.time() - start
        
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:500]}")
        print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_timeout_command():
    """Linux timeoutコマンドを使用"""
    print("=== Test with timeout command ===")
    
    cmd = [
        "wsl", "--", "bash", "-c",
        "timeout 20 /home/tethiro/.nvm/versions/node/v22.17.0/bin/claude --dangerously-skip-permissions --output-format json -p 'Hello timeout'"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        elapsed = time.time() - start
        
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:500]}")
        print(f"Error: {result.stderr}")
        if result.returncode == 124:
            print("Note: Return code 124 means the timeout command killed the process")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_env_vars():
    """環境変数を設定して実行"""
    print("=== Test with Environment Variables ===")
    
    env_vars = [
        "CLAUDE_NO_ANALYTICS=1",
        "NODE_ENV=production",
        "CI=true",
        "CLAUDE_DISABLE_TELEMETRY=1"
    ]
    
    cmd = [
        "wsl", "--", "bash", "-c",
        f"{' '.join(env_vars)} /home/tethiro/.nvm/versions/node/v22.17.0/bin/claude --dangerously-skip-permissions --output-format json -p 'Hello env'"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        elapsed = time.time() - start
        
        print(f"Elapsed time: {elapsed:.2f}s")
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout[:500]}")
        print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_direct_node():
    """Node.js経由で直接実行"""
    print("=== Test Direct Node Execution ===")
    
    # Claudeの実行ファイルの内容を確認
    cmd = ["wsl", "--", "head", "-n", "1", "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Claude shebang: {result.stdout.strip()}")
    
    # nodeで直接実行を試みる
    cmd = [
        "wsl", "--", 
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/node",
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--version"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("TIMEOUT!")
    except Exception as e:
        print(f"Error: {e}")
    print()

def main():
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print()
    
    # 各回避策をテスト
    test_with_script_file()
    test_with_input_file()
    test_with_nohup()
    test_with_timeout_command()
    test_with_env_vars()
    test_direct_node()
    
    print("\n=== Workaround Summary ===")
    print("Check which methods work without timeout.")
    print("The successful method can be integrated into claude_cli_server.py")

if __name__ == "__main__":
    main()