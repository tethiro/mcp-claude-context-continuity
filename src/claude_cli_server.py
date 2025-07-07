#!/usr/bin/env python3
"""Claude CLI MCP Server - Claude CLIをプログラム内部から呼び出すMCPサーバー"""

import asyncio
import json
import os
import platform
import glob
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP

# 定数
DEFAULT_TIMEOUT = 300  # デフォルトタイムアウト（秒）

# FastMCPインスタンスの作成
mcp = FastMCP("claude-cli-server")


class ClaudeSessionManager:
    """Claude CLIのセッション管理クラス"""
    
    def __init__(self):
        self.before_session_id: Optional[str] = None  # 前回のセッションID
        self.history: List[Dict] = []
        self.claude_command: Optional[Union[str, List[str]]] = None  # キャッシュ
        
    def _add_history(self, entry: Dict):
        """履歴に操作を追加"""
        self.history.append(entry)
        # 最新100件のみ保持
        if len(self.history) > 100:
            self.history = self.history[-100:]
            
    async def get_claude_command(self) -> Union[str, List[str]]:
        """Claude実行コマンドを取得（キャッシュ付き）"""
        if self.claude_command is None:
            if platform.system() == "Windows":
                self.claude_command = await self._find_claude_windows()
            else:
                self.claude_command = await self._find_claude_unix()
                
            if self.claude_command is None:
                raise FileNotFoundError("Claude CLI not found. Please install Claude CLI or set CLAUDE_PATH environment variable.")
                
        return self.claude_command
    
    async def _find_claude_unix(self) -> Optional[str]:
        """Unix系OS（Linux/macOS/WSL）でClaude CLIを探す"""
        # 1. whichコマンドで探す
        try:
            proc = await asyncio.create_subprocess_exec(
                "which", "claude",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0 and stdout:
                return stdout.decode().strip()
        except:
            pass
        
        # 2. よくある場所をチェック
        common_paths = [
            "/usr/local/bin/claude",
            "/usr/bin/claude",
            os.path.expanduser("~/.npm-global/bin/claude"),
            os.path.expanduser("~/.yarn/bin/claude"),
            os.path.expanduser("~/.volta/bin/claude"),
        ]
        
        # nvmのパスを追加
        common_paths.extend(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/claude")))
        # asdfのパスを追加
        common_paths.extend(glob.glob(os.path.expanduser("~/.asdf/installs/nodejs/*/bin/claude")))
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # 3. 環境変数をチェック
        if "CLAUDE_PATH" in os.environ:
            path = os.environ["CLAUDE_PATH"]
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    async def _find_claude_windows(self) -> Optional[List[str]]:
        """WindowsでWSL経由のClaude CLIを探す（同期版を使用）"""
        # 1. WSL内でbashを起動してwhichコマンドを実行
        try:
            result = subprocess.run(
                ["wsl", "--", "bash", "-lc", "which claude"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                path = result.stdout.strip()
                return ["wsl", "--", path]
        except:
            pass
        
        # 2. よくあるnvmのパスを試す
        nvm_paths = ["/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude"]
        
        # WSL内のユーザー名を取得して動的にパスを生成
        try:
            result = subprocess.run(
                ["wsl", "--", "whoami"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                username = result.stdout.strip()
                nvm_paths.append(f"/home/{username}/.nvm/versions/node/v22.17.0/bin/claude")
        except:
            pass
        
        for path in nvm_paths:
            try:
                result = subprocess.run(
                    ["wsl", "--", "test", "-x", path],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return ["wsl", "--", path]
            except:
                pass
        
        return None


# グローバルセッションマネージャー
session_manager = ClaudeSessionManager()


async def _execute_claude_command(cmd: List[str]) -> Dict:
    """Claude CLIコマンドを実行して結果を返す"""
    start_time = time.time()
    
    # デバッグ: 実行コマンドをログファイルに記録
    debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')
    with open(debug_log_path, 'a') as f:
        f.write(f"\n[{datetime.now().isoformat()}] Executing command: {' '.join(cmd)}\n")
    
    # Windows環境では同期実行を使用
    if platform.system() == "Windows":
        try:
            # Windows/WSL環境では、標準入力を閉じて対話モードを避ける
            # エンコーディングエラーを回避するため、errors='replace'を追加
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
                stdin=subprocess.DEVNULL,  # 標準入力を閉じる
                encoding='utf-8',  # 文字エンコーディングを明示的に指定
                errors='replace'  # デコードエラーを?に置換
            )
            
            execution_time = time.time() - start_time
            
            # デバッグ: 結果をログに記録
            with open(debug_log_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] Return code: {result.returncode}, Time: {execution_time:.2f}s\n")
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                return {
                    "success": False,
                    "error": f"Command failed with code {result.returncode}: {error_msg}",
                    "execution_time": execution_time
                }
            
            # 出力を処理（JSONではない場合もある）
            output = result.stdout.strip()
            
            # JSON形式かチェック
            if output.startswith('{'):
                try:
                    response_json = json.loads(output)
                    
                    # session_idがあれば保存
                    if "session_id" in response_json:
                        old_session_id = session_manager.before_session_id
                        session_manager.before_session_id = response_json["session_id"]
                        with open(debug_log_path, 'a') as f:
                            f.write(f"[{datetime.now().isoformat()}] Session updated: {old_session_id} -> {response_json['session_id']}\n")
                    
                    return {
                        "success": True,
                        "response": response_json.get("result", ""),
                        "execution_time": execution_time
                    }
                    
                except json.JSONDecodeError:
                    # JSONパースに失敗した場合は生の出力を返す
                    pass
            
            # JSON形式でない場合は生の出力を返す
            return {
                "success": True,
                "response": output,
                "execution_time": execution_time
            }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Timeout after {DEFAULT_TIMEOUT} seconds",
                "execution_time": DEFAULT_TIMEOUT
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    # Unix系OSでは非同期実行
    else:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), 
                timeout=DEFAULT_TIMEOUT
            )
            
            execution_time = time.time() - start_time
            
            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return {
                    "success": False,
                    "error": f"Command failed with code {proc.returncode}: {error_msg}",
                    "execution_time": execution_time
                }
            
            # 出力を処理（JSONではない場合もある）
            output = stdout.decode().strip() if stdout else ""
            
            # JSON形式かチェック
            if output.startswith('{'):
                try:
                    response_json = json.loads(output)
                    
                    # session_idがあれば保存
                    if "session_id" in response_json:
                        old_session_id = session_manager.before_session_id
                        session_manager.before_session_id = response_json["session_id"]
                        with open(debug_log_path, 'a') as f:
                            f.write(f"[{datetime.now().isoformat()}] Session updated: {old_session_id} -> {response_json['session_id']}\n")
                    
                    return {
                        "success": True,
                        "response": response_json.get("result", ""),
                        "execution_time": execution_time
                    }
                    
                except json.JSONDecodeError:
                    # JSONパースに失敗した場合は生の出力を返す
                    pass
            
            # JSON形式でない場合は生の出力を返す
            return {
                "success": True,
                "response": output,
                "execution_time": execution_time
            }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Timeout after {DEFAULT_TIMEOUT} seconds",
                "execution_time": DEFAULT_TIMEOUT
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": time.time() - start_time
            }


@mcp.tool()
async def execute_claude(prompt: str) -> Dict:
    """Claude CLIを実行して結果を返す
    
    Args:
        prompt: Claudeに送るプロンプト
        timeout: タイムアウト時間（秒）
        
    Returns:
        実行結果を含む辞書
    """
    # Claude実行コマンドを取得
    try:
        claude_cmd = await session_manager.get_claude_command()
    except FileNotFoundError as e:
        return {
            "tool_name": "execute_claude_with_context",
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
    
    # コマンドを構築
    if isinstance(claude_cmd, str):
        cmd = [claude_cmd]
    else:
        cmd = claude_cmd.copy()
    
    cmd.extend([
        "--dangerously-skip-permissions",
        "--output-format", "json"
    ])
    
    # before_session_idがある場合は --resume オプションを追加
    if session_manager.before_session_id is not None:
        cmd.extend(["--resume", session_manager.before_session_id])
        # デバッグ: resumeセッションIDをログに記録
        with open(os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log'), 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Using --resume with session_id: {session_manager.before_session_id}\n")
    
    # プロンプトを追加
    cmd.extend(["-p", prompt])
    
    # コマンド実行
    result = await _execute_claude_command(cmd)
    
    # 完全な返り値を構築
    full_result = {
        "tool_name": "execute_claude",
        "success": result["success"],
        "prompt": prompt,
        "response": result.get("response"),
        "execution_time": result["execution_time"],
        "timestamp": datetime.now().isoformat(),
        "error": result.get("error")
    }
    
    # 履歴に追加
    session_manager._add_history(full_result)
    
    return full_result


@mcp.tool()
async def execute_claude_with_context(prompt: str, file_path: str) -> Dict:
    """ファイルコンテキスト付きでClaude CLIを実行
    
    ファイルの内容を読み込んで、その内容についてClaudeに質問できます。
    例: README.mdについて質問する、コードファイルの説明を求める等
    
    Args:
        prompt: Claudeに送るプロンプト（例: "このファイルの目的を説明して"）
        file_path: コンテキストとして使用するファイルのパス（例: "README.md"）
        
    Returns:
        実行結果を含む辞書
    """
    # ファイルの存在確認
    if not os.path.exists(file_path):
        return {
            "tool_name": "execute_claude_with_context",
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": f"File not found: {file_path}"
        }
    
    # ファイル内容を読み込む
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        return {
            "tool_name": "execute_claude_with_context",
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": f"Failed to read file: {str(e)}"
        }
    
    # Claude実行コマンドを取得
    try:
        claude_cmd = await session_manager.get_claude_command()
    except FileNotFoundError as e:
        return {
            "tool_name": "execute_claude_with_context",
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
    
    # コマンドを構築
    if isinstance(claude_cmd, str):
        cmd = [claude_cmd]
    else:
        cmd = claude_cmd.copy()
    
    cmd.extend([
        "--dangerously-skip-permissions",
        "--output-format", "json"
    ])
    
    # before_session_idがある場合は --resume オプションを追加
    if session_manager.before_session_id is not None:
        cmd.extend(["--resume", session_manager.before_session_id])
        # デバッグ: resumeセッションIDをログに記録
        with open(os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log'), 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Using --resume with session_id: {session_manager.before_session_id}\n")
    
    # プロンプトを追加
    cmd.extend(["-p", prompt])
    
    # コマンド実行（ファイル内容を標準入力として渡す）
    start_time = time.time()
    
    # Windows環境では同期実行を使用
    if platform.system() == "Windows":
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            stdout, stderr = proc.communicate(input=file_content, timeout=DEFAULT_TIMEOUT)
            
            execution_time = time.time() - start_time
            
            if proc.returncode != 0:
                error_msg = stderr if stderr else "Unknown error"
                result = {
                    "success": False,
                    "error": f"Command failed with code {proc.returncode}: {error_msg}",
                    "execution_time": execution_time
                }
            else:
                # 出力を処理（JSONではない場合もある）
                output = stdout.strip()
                
                # JSON形式かチェック
                if output.startswith('{'):
                    try:
                        response_json = json.loads(output)
                        
                        # session_idがあれば保存
                        if "session_id" in response_json:
                            session_manager.before_session_id = response_json["session_id"]
                        
                        result = {
                            "success": True,
                            "response": response_json.get("result", ""),
                            "execution_time": execution_time
                        }
                        
                    except json.JSONDecodeError:
                        # JSONパースに失敗した場合は生の出力を返す
                        result = {
                            "success": True,
                            "response": output,
                            "execution_time": execution_time
                        }
                else:
                    # JSON形式でない場合は生の出力を返す
                    result = {
                        "success": True,
                        "response": output,
                        "execution_time": execution_time
                    }
                    
        except subprocess.TimeoutExpired:
            result = {
                "success": False,
                "error": f"Timeout after {DEFAULT_TIMEOUT} seconds",
                "execution_time": DEFAULT_TIMEOUT
            }
        except Exception as e:
            result = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    # Unix系OSでは非同期実行
    else:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=file_content.encode()), 
                timeout=DEFAULT_TIMEOUT
            )
            
            execution_time = time.time() - start_time
            
            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                result = {
                    "success": False,
                    "error": f"Command failed with code {proc.returncode}: {error_msg}",
                    "execution_time": execution_time
                }
            else:
                # 出力を処理（JSONではない場合もある）
                output = stdout.decode().strip() if stdout else ""
                
                # JSON形式かチェック
                if output.startswith('{'):
                    try:
                        response_json = json.loads(output)
                        
                        # session_idがあれば保存
                        if "session_id" in response_json:
                            old_session_id = session_manager.before_session_id
                            session_manager.before_session_id = response_json["session_id"]
                            debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')
                            with open(debug_log_path, 'a') as f:
                                f.write(f"[{datetime.now().isoformat()}] Session updated: {old_session_id} -> {response_json['session_id']}\n")
                        
                        result = {
                            "success": True,
                            "response": response_json.get("result", ""),
                            "execution_time": execution_time
                        }
                        
                    except json.JSONDecodeError:
                        # JSONパースに失敗した場合は生の出力を返す
                        result = {
                            "success": True,
                            "response": output,
                            "execution_time": execution_time
                        }
                else:
                    # JSON形式でない場合は生の出力を返す
                    result = {
                        "success": True,
                        "response": output,
                        "execution_time": execution_time
                    }
                    
        except asyncio.TimeoutError:
            result = {
                "success": False,
                "error": f"Timeout after {DEFAULT_TIMEOUT} seconds",
                "execution_time": DEFAULT_TIMEOUT
            }
        except Exception as e:
            result = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    # 完全な返り値を構築
    full_result = {
        "tool_name": "execute_claude_with_context",
        "success": result["success"],
        "prompt": prompt,
        "response": result.get("response"),
        "execution_time": result["execution_time"],
        "timestamp": datetime.now().isoformat(),
        "error": result.get("error"),
        "context_file": file_path
    }
    
    # 履歴に追加
    session_manager._add_history(full_result)
    
    return full_result


@mcp.tool()
async def get_execution_history(limit: int = 10) -> Dict:
    """実行履歴を取得
    
    Args:
        limit: 取得する履歴数（デフォルト: 10）
        
    Returns:
        履歴情報を含む辞書
    """
    # 最新のlimit件を取得
    history_slice = session_manager.history[-limit:] if limit > 0 else session_manager.history
    
    return {
        "tool_name": "get_execution_history",
        "success": True,
        "history": history_slice,
        "total_entries": len(session_manager.history),
        "current_session_id": session_manager.before_session_id
    }


@mcp.tool()
async def clear_execution_history() -> Dict:
    """実行履歴をクリア
    
    Returns:
        操作結果を含む辞書
    """
    cleared_count = len(session_manager.history)
    session_manager.history = []
    
    return {
        "tool_name": "clear_execution_history",
        "success": True,
        "message": f"Cleared {cleared_count} history entries",
        "cleared_count": cleared_count
    }


@mcp.tool()
async def get_current_session() -> Dict:
    """現在のセッションIDを取得
    
    Returns:
        セッション情報を含む辞書
    """
    return {
        "tool_name": "get_current_session",
        "success": True,
        "session_id": session_manager.before_session_id,
        "has_session": session_manager.before_session_id is not None
    }


@mcp.tool()
async def test_claude_cli() -> Dict:
    """Claude CLIが正しく設定されているかテスト
    
    Returns:
        テスト結果を含む辞書
    """
    try:
        # Claude実行コマンドを取得
        claude_cmd = await session_manager.get_claude_command()
        
        # コマンドを構築（--versionオプションで簡単なテスト）
        if isinstance(claude_cmd, str):
            cmd = [claude_cmd, "--version"]
        else:
            cmd = claude_cmd.copy() + ["--version"]
        
        # Windows環境では同期実行を使用
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,  # 短いタイムアウト
                    stdin=subprocess.DEVNULL,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode == 0:
                    return {
                        "tool_name": "test_claude_cli",
                        "success": True,
                        "command": " ".join(cmd),
                        "output": result.stdout.strip(),
                        "message": "Claude CLI found and working!"
                    }
                else:
                    return {
                        "tool_name": "test_claude_cli",
                        "success": False,
                        "command": " ".join(cmd),
                        "error": result.stderr.strip() if result.stderr else "Command failed",
                        "message": "Claude CLI found but not working properly"
                    }
                    
            except subprocess.TimeoutExpired:
                return {
                    "tool_name": "test_claude_cli",
                    "success": False,
                    "command": " ".join(cmd),
                    "error": "Timeout",
                    "message": "Claude CLI command timed out"
                }
            except Exception as e:
                return {
                    "tool_name": "test_claude_cli",
                    "success": False,
                    "command": " ".join(cmd),
                    "error": str(e),
                    "message": "Error executing Claude CLI"
                }
        
        # Unix系OSでは非同期実行
        else:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=5
                )
                
                if proc.returncode == 0:
                    return {
                        "tool_name": "test_claude_cli",
                        "success": True,
                        "command": " ".join(cmd),
                        "output": stdout.decode().strip(),
                        "message": "Claude CLI found and working!"
                    }
                else:
                    return {
                        "tool_name": "test_claude_cli",
                        "success": False,
                        "command": " ".join(cmd),
                        "error": stderr.decode().strip() if stderr else "Command failed",
                        "message": "Claude CLI found but not working properly"
                    }
                    
            except asyncio.TimeoutError:
                return {
                    "tool_name": "test_claude_cli",
                    "success": False,
                    "command": " ".join(cmd),
                    "error": "Timeout",
                    "message": "Claude CLI command timed out"
                }
            except Exception as e:
                return {
                    "tool_name": "test_claude_cli",
                    "success": False,
                    "command": " ".join(cmd),
                    "error": str(e),
                    "message": "Error executing Claude CLI"
                }
                
    except FileNotFoundError as e:
        return {
            "tool_name": "test_claude_cli",
            "success": False,
            "command": None,
            "error": str(e),
            "message": "Claude CLI not found"
        }
    except Exception as e:
        return {
            "tool_name": "test_claude_cli",
            "success": False,
            "command": None,
            "error": str(e),
            "message": "Unexpected error"
        }


@mcp.tool()
async def reset_session() -> Dict:
    """セッションをリセット
    
    Returns:
        操作結果を含む辞書
    """
    old_session_id = session_manager.before_session_id
    session_manager.before_session_id = None
    
    return {
        "tool_name": "reset_session",
        "success": True,
        "message": "Session reset successfully",
        "old_session_id": old_session_id
    }


# Windows環境用の設定
if platform.system() == "Windows":
    # WindowsでのProactorEventLoopポリシー設定
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# メインエントリーポイント
if __name__ == "__main__":
    # stdio経由でサーバーを起動
    asyncio.run(mcp.run_stdio_async())