#!/usr/bin/env python3
"""Windows環境でのClaude CLI呼び出しの詳細デバッグ"""

import subprocess
import sys
import platform
import time
import os
import threading

def run_with_timeout_check(cmd, timeout=30):
    """タイムアウトをチェックしながら実行"""
    print(f"\nCommand: {' '.join(cmd)}")
    print(f"Timeout: {timeout}s")
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding='utf-8'
    )
    
    # 進行状況を表示するスレッド
    stop_event = threading.Event()
    def progress_indicator():
        elapsed = 0
        while not stop_event.is_set():
            print(f"\rRunning... {elapsed}s", end='', flush=True)
            time.sleep(1)
            elapsed += 1
    
    progress_thread = threading.Thread(target=progress_indicator)
    progress_thread.start()
    
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        stop_event.set()
        progress_thread.join()
        print(f"\nCompleted!")
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        stop_event.set()
        progress_thread.join()
        print(f"\nTIMEOUT after {timeout}s!")
        proc.kill()
        stdout, stderr = proc.communicate()
        return -1, stdout, stderr

def test_wsl_basic():
    """WSLの基本動作確認"""
    print("=== WSL Basic Test ===")
    
    # WSL自体の動作確認
    cmd = ["wsl", "--", "echo", "WSL is working"]
    returncode, stdout, stderr = run_with_timeout_check(cmd, timeout=5)
    print(f"Return code: {returncode}")
    print(f"Output: {stdout.strip()}")
    print(f"Error: {stderr.strip()}")
    print()

def test_claude_path():
    """Claude CLIのパス確認"""
    print("=== Claude Path Test ===")
    
    # which claude
    cmd = ["wsl", "--", "which", "claude"]
    returncode, stdout, stderr = run_with_timeout_check(cmd, timeout=5)
    print(f"which claude: {stdout.strip()}")
    
    # 直接パスでls
    cmd = ["wsl", "--", "ls", "-la", "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude"]
    returncode, stdout, stderr = run_with_timeout_check(cmd, timeout=5)
    print(f"ls result: {stdout.strip()}")
    print()

def test_claude_env():
    """環境変数の確認"""
    print("=== Environment Test ===")
    
    # 環境変数を確認
    cmd = ["wsl", "--", "bash", "-c", "echo PATH=$PATH"]
    returncode, stdout, stderr = run_with_timeout_check(cmd, timeout=5)
    print(f"PATH: {stdout.strip()}")
    
    # nodeとnpmの確認
    cmd = ["wsl", "--", "bash", "-lc", "which node && node --version"]
    returncode, stdout, stderr = run_with_timeout_check(cmd, timeout=5)
    print(f"Node: {stdout.strip()}")
    print()

def test_claude_variations():
    """異なる呼び出し方法のテスト"""
    print("=== Claude Call Variations ===")
    
    variations = [
        {
            "name": "Direct path",
            "cmd": ["wsl", "--", "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude", "--version"]
        },
        {
            "name": "Bash -c",
            "cmd": ["wsl", "--", "bash", "-c", "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude --version"]
        },
        {
            "name": "Bash -lc",
            "cmd": ["wsl", "--", "bash", "-lc", "claude --version"]
        },
        {
            "name": "Export PATH and run",
            "cmd": ["wsl", "--", "bash", "-c", "export PATH=/home/tethiro/.nvm/versions/node/v22.17.0/bin:$PATH && claude --version"]
        }
    ]
    
    for var in variations:
        print(f"\n--- {var['name']} ---")
        returncode, stdout, stderr = run_with_timeout_check(var['cmd'], timeout=10)
        print(f"Return code: {returncode}")
        print(f"Output: {stdout.strip()[:100]}")
        if stderr:
            print(f"Error: {stderr.strip()[:100]}")

def test_claude_minimal():
    """最小限のClaude呼び出し"""
    print("\n=== Minimal Claude Test ===")
    
    # 環境変数を設定してテスト
    cmd = [
        "wsl", "--",
        "bash", "-c",
        "export CLAUDE_NO_ANALYTICS=1 && /home/tethiro/.nvm/versions/node/v22.17.0/bin/claude --version"
    ]
    returncode, stdout, stderr = run_with_timeout_check(cmd, timeout=10)
    print(f"Return code: {returncode}")
    print(f"Output: {stdout}")
    print(f"Error: {stderr}")

def test_process_monitoring():
    """プロセスの監視"""
    print("\n=== Process Monitoring Test ===")
    
    # バックグラウンドでClaude実行
    cmd = [
        "wsl", "--",
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "-p", "echo test"
    ]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True
    )
    
    print("Process started, checking status...")
    for i in range(5):
        time.sleep(1)
        poll = proc.poll()
        if poll is not None:
            print(f"Process finished after {i+1}s with code: {poll}")
            stdout, stderr = proc.communicate()
            print(f"Output: {stdout[:200]}")
            break
        else:
            print(f"Still running after {i+1}s...")
    else:
        print("Process still running after 5s, terminating...")
        proc.terminate()
        stdout, stderr = proc.communicate()
        print(f"Terminated output: {stdout[:200]}")

def main():
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    # 各テストを順番に実行
    test_wsl_basic()
    test_claude_path()
    test_claude_env()
    test_claude_variations()
    test_claude_minimal()
    test_process_monitoring()
    
    print("\n=== Debug Summary ===")
    print("If Claude hangs or timeouts:")
    print("1. Check if it's waiting for input (use stdin=DEVNULL)")
    print("2. Try setting CLAUDE_NO_ANALYTICS=1")
    print("3. Check Windows Defender / Firewall")
    print("4. Try running directly in WSL terminal to compare")

if __name__ == "__main__":
    main()