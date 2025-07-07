#!/usr/bin/env python3
"""Claude CLIの場所を探すテストプログラム"""

import asyncio
import os
import platform
import subprocess
import glob
from typing import Optional, List, Union

async def run_command(cmd: List[str], timeout: int = 5) -> subprocess.CompletedProcess:
    """コマンドを実行して結果を返す"""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout=stdout.decode() if stdout else "",
            stderr=stderr.decode() if stderr else ""
        )
    except asyncio.TimeoutError:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=-1,
            stdout="",
            stderr="Timeout"
        )
    except Exception as e:
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=-1,
            stdout="",
            stderr=str(e)
        )

async def find_claude_unix() -> Optional[str]:
    """Unix系OS（Linux/macOS/WSL）でClaude CLIを探す"""
    print("🔍 Unix系OSでClaude CLIを探しています...")
    
    # 1. whichコマンドで探す
    print("\n1. whichコマンドで検索:")
    result = await run_command(["which", "claude"])
    if result.returncode == 0 and result.stdout.strip():
        path = result.stdout.strip()
        print(f"   ✅ 見つかりました: {path}")
        return path
    else:
        print("   ❌ whichコマンドでは見つかりませんでした")
    
    # 2. よくある場所をチェック
    print("\n2. よくある場所をチェック:")
    common_paths = [
        "/usr/local/bin/claude",
        "/usr/bin/claude",
        os.path.expanduser("~/.npm-global/bin/claude"),
        os.path.expanduser("~/.yarn/bin/claude"),
        os.path.expanduser("~/.volta/bin/claude"),
    ]
    
    # nvmのパスを追加
    nvm_patterns = [
        os.path.expanduser("~/.nvm/versions/node/*/bin/claude"),
    ]
    for pattern in nvm_patterns:
        common_paths.extend(glob.glob(pattern))
    
    # asdfのパスを追加
    asdf_patterns = [
        os.path.expanduser("~/.asdf/installs/nodejs/*/bin/claude"),
    ]
    for pattern in asdf_patterns:
        common_paths.extend(glob.glob(pattern))
    
    for path in common_paths:
        if os.path.exists(path):
            if os.access(path, os.X_OK):
                print(f"   ✅ 見つかりました: {path}")
                return path
            else:
                print(f"   ⚠️  ファイルは存在しますが実行権限がありません: {path}")
        else:
            print(f"   ❌ 存在しません: {path}")
    
    # 3. 環境変数をチェック
    print("\n3. 環境変数CLAUDE_PATHをチェック:")
    if "CLAUDE_PATH" in os.environ:
        path = os.environ["CLAUDE_PATH"]
        print(f"   📝 CLAUDE_PATH = {path}")
        if os.path.exists(path) and os.access(path, os.X_OK):
            print(f"   ✅ 有効なパスです")
            return path
        else:
            print(f"   ❌ 無効なパスです")
    else:
        print("   ❌ CLAUDE_PATHは設定されていません")
    
    return None

async def find_claude_windows() -> Optional[List[str]]:
    """WindowsでWSL経由のClaude CLIを探す"""
    print("🔍 WindowsからWSL経由でClaude CLIを探しています...")
    
    # 1. WSL内でbashを起動してwhichコマンドを実行
    print("\n1. WSL内でbashを起動してwhichコマンドを実行:")
    # bashの-lcオプションでログインシェルとして起動し、環境変数をロード
    result = await run_command(["wsl", "--", "bash", "-lc", "which claude"])
    if result.returncode == 0 and result.stdout.strip():
        path = result.stdout.strip()
        print(f"   ✅ 見つかりました: {path}")
        return ["wsl", "--", path]
    else:
        print("   ❌ whichコマンドでは見つかりませんでした")
    
    # 2. よくあるnvmのパスを試す
    print("\n2. nvmの一般的なパスをチェック:")
    nvm_paths = [
        "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude",
    ]
    
    # WSL内のユーザー名を取得
    user_result = await run_command(["wsl", "--", "whoami"])
    if user_result.returncode == 0:
        username = user_result.stdout.strip()
        print(f"   WSLユーザー名: {username}")
        
        # 動的にパスを生成
        nvm_paths.extend([
            f"/home/{username}/.nvm/versions/node/v22.17.0/bin/claude",
        ])
    
    for path in nvm_paths:
        print(f"   チェック中: {path}")
        result = await run_command(["wsl", "--", "test", "-x", path])
        if result.returncode == 0:
            print(f"   ✅ 実行可能ファイルが見つかりました")
            return ["wsl", "--", path]
        else:
            print(f"   ❌ 見つかりませんでした")
    
    return None

async def test_claude_execution(cmd: Union[str, List[str]]) -> bool:
    """見つかったClaude CLIが実際に動作するかテスト"""
    print("\n📋 Claude CLIの動作テスト:")
    
    if isinstance(cmd, str):
        test_cmd = [cmd, "--version"]
    else:
        test_cmd = cmd + ["--version"]
    
    print(f"   実行コマンド: {' '.join(test_cmd)}")
    result = await run_command(test_cmd)
    
    if result.returncode == 0:
        print(f"   ✅ 正常に動作しています")
        print(f"   バージョン情報: {result.stdout.strip()}")
        return True
    else:
        print(f"   ❌ エラーが発生しました")
        print(f"   エラー: {result.stderr}")
        return False

async def main():
    """メイン処理"""
    print("=" * 60)
    print("Claude CLI 探索テスト")
    print(f"OS: {platform.system()}")
    print(f"Platform: {platform.platform()}")
    print("=" * 60)
    
    claude_cmd = None
    
    if platform.system() == "Windows":
        claude_cmd = await find_claude_windows()
    else:
        claude_path = await find_claude_unix()
        if claude_path:
            claude_cmd = claude_path
    
    print("\n" + "=" * 60)
    print("結果:")
    
    if claude_cmd:
        print(f"✅ Claude CLIが見つかりました")
        if isinstance(claude_cmd, list):
            print(f"   コマンド: {' '.join(claude_cmd)}")
        else:
            print(f"   パス: {claude_cmd}")
        
        # 動作テスト
        success = await test_claude_execution(claude_cmd)
        if success:
            print("\n🎉 Claude CLIは正常に使用できます！")
        else:
            print("\n⚠️  Claude CLIは見つかりましたが、実行に問題があります")
    else:
        print("❌ Claude CLIが見つかりませんでした")
        print("\n対処法:")
        print("1. Claude CLIがインストールされているか確認してください")
        print("2. PATHに追加されているか確認してください")
        print("3. 環境変数CLAUDE_PATHに絶対パスを設定してください")

if __name__ == "__main__":
    asyncio.run(main())