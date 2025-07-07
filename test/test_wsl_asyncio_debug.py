#!/usr/bin/env python3
"""WSL環境でのasyncio実行デバッグ"""

import asyncio
import subprocess
import json
import time

async def test_asyncio_execution():
    """asyncioでのClaude CLI実行テスト"""
    print("=== WSL asyncio Debug Test ===\n")
    
    cmd = [
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "こんにちは"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        # 非同期プロセス作成
        print("Creating subprocess...")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print(f"Process created: PID={proc.pid}")
        
        # タイムアウト付きで待機
        print("Waiting for process to complete...")
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), 
                timeout=30  # 30秒タイムアウト
            )
            elapsed = time.time() - start_time
            print(f"Process completed in {elapsed:.2f}s")
            
            # 結果を表示
            print(f"Return code: {proc.returncode}")
            
            if stdout:
                print("\nStdout:")
                output = stdout.decode().strip()
                print(f"Raw output length: {len(output)}")
                print(f"First 100 chars: {output[:100]}")
                
                try:
                    response = json.loads(output)
                    print("\nParsed JSON:")
                    print(json.dumps(response, indent=2, ensure_ascii=False))
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                    
            if stderr:
                print(f"\nStderr: {stderr.decode()}")
                
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"TIMEOUT after {elapsed:.2f}s")
            # プロセスを強制終了
            proc.kill()
            await proc.wait()
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def test_sync_vs_async():
    """同期と非同期の比較"""
    print("\n=== Sync vs Async Comparison ===\n")
    
    cmd = [
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
        "--dangerously-skip-permissions",
        "--output-format", "json",
        "-p", "test"
    ]
    
    # 同期実行
    print("1. Synchronous execution:")
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    sync_time = time.time() - start
    print(f"  Completed in {sync_time:.2f}s, return code: {result.returncode}")
    
    # 非同期実行
    print("\n2. Asynchronous execution:")
    start = time.time()
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    async_time = time.time() - start
    print(f"  Completed in {async_time:.2f}s, return code: {proc.returncode}")

async def main():
    await test_asyncio_execution()
    await test_sync_vs_async()

if __name__ == "__main__":
    # イベントループの詳細情報
    loop = asyncio.get_event_loop()
    print(f"Event loop: {type(loop).__name__}")
    
    asyncio.run(main())