#!/usr/bin/env python3
"""Windows対応版 Claude CLI MCP Server"""

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

# FastMCPインスタンスの作成
mcp = FastMCP("claude-cli-server")


class ClaudeSessionManager:
    """Claude CLIのセッション管理クラス"""
    
    def __init__(self):
        self.before_session_id: Optional[str] = None
        self.history: List[Dict] = []
        self.claude_command: Optional[Union[str, List[str]]] = None
        
    def _add_history(self, entry: Dict):
        """履歴に操作を追加"""
        self.history.append(entry)
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
        
        common_paths = [
            "/usr/local/bin/claude",
            "/usr/bin/claude",
            os.path.expanduser("~/.npm-global/bin/claude"),
            os.path.expanduser("~/.yarn/bin/claude"),
            os.path.expanduser("~/.volta/bin/claude"),
        ]
        
        common_paths.extend(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/claude")))
        common_paths.extend(glob.glob(os.path.expanduser("~/.asdf/installs/nodejs/*/bin/claude")))
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        if "CLAUDE_PATH" in os.environ:
            path = os.environ["CLAUDE_PATH"]
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    async def _find_claude_windows(self) -> Optional[List[str]]:
        """WindowsでWSL経由のClaude CLIを探す（同期版を使用）"""
        # WSL内でbashを起動してwhichコマンドを実行
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
        
        # よくあるnvmのパスを試す
        nvm_paths = ["/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude"]
        
        # WSL内のユーザー名を取得
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


async def _execute_claude_command_windows(cmd: List[str]) -> Dict:
    """Windows用: 同期的にClaude CLIコマンドを実行"""
    start_time = time.time()
    
    try:
        # Windows環境では同期的に実行
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "Unknown error"
            return {
                "success": False,
                "error": f"Command failed with code {result.returncode}: {error_msg}",
                "execution_time": execution_time
            }
        
        # JSON解析
        try:
            response_json = json.loads(result.stdout)
            
            # session_idがあれば保存
            if "session_id" in response_json:
                session_manager.before_session_id = response_json["session_id"]
            
            return {
                "success": True,
                "response": response_json.get("result", ""),
                "execution_time": execution_time
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parse error: {str(e)}",
                "raw_output": result.stdout,
                "execution_time": execution_time
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout after 30 seconds",
            "execution_time": 30
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "execution_time": time.time() - start_time
        }


async def _execute_claude_command_unix(cmd: List[str]) -> Dict:
    """Unix系OS用: 非同期でClaude CLIコマンドを実行"""
    start_time = time.time()
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), 
            timeout=30
        )
        
        execution_time = time.time() - start_time
        
        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            return {
                "success": False,
                "error": f"Command failed with code {proc.returncode}: {error_msg}",
                "execution_time": execution_time
            }
        
        # JSON解析
        try:
            response_json = json.loads(stdout.decode())
            
            if "session_id" in response_json:
                session_manager.before_session_id = response_json["session_id"]
            
            return {
                "success": True,
                "response": response_json.get("result", ""),
                "execution_time": execution_time
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parse error: {str(e)}",
                "raw_output": stdout.decode() if stdout else "",
                "execution_time": execution_time
            }
            
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Timeout after 30 seconds",
            "execution_time": 30
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "execution_time": time.time() - start_time
        }


@mcp.tool()
async def execute_claude(prompt: str) -> Dict:
    """Claude CLIを実行して結果を返す"""
    try:
        claude_cmd = await session_manager.get_claude_command()
    except FileNotFoundError as e:
        return {
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
    
    if session_manager.before_session_id is not None:
        cmd.extend(["--resume", session_manager.before_session_id])
    
    cmd.extend(["-p", prompt])
    
    # OS別にコマンド実行
    if platform.system() == "Windows":
        result = await _execute_claude_command_windows(cmd)
    else:
        result = await _execute_claude_command_unix(cmd)
    
    # 完全な返り値を構築
    full_result = {
        "success": result["success"],
        "prompt": prompt,
        "response": result.get("response"),
        "execution_time": result["execution_time"],
        "timestamp": datetime.now().isoformat(),
        "error": result.get("error")
    }
    
    session_manager._add_history(full_result)
    
    return full_result


@mcp.tool()
async def execute_claude_with_context(prompt: str, file_path: str) -> Dict:
    """ファイルコンテキスト付きでClaude CLIを実行"""
    if not os.path.exists(file_path):
        return {
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": f"File not found: {file_path}"
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        return {
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": f"Failed to read file: {str(e)}"
        }
    
    try:
        claude_cmd = await session_manager.get_claude_command()
    except FileNotFoundError as e:
        return {
            "success": False,
            "prompt": prompt,
            "response": None,
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
    
    if isinstance(claude_cmd, str):
        cmd = [claude_cmd]
    else:
        cmd = claude_cmd.copy()
    
    cmd.extend([
        "--dangerously-skip-permissions",
        "--output-format", "json"
    ])
    
    if session_manager.before_session_id is not None:
        cmd.extend(["--resume", session_manager.before_session_id])
    
    cmd.extend(["-p", prompt])
    
    start_time = time.time()
    
    # Windows環境では同期版を使用
    if platform.system() == "Windows":
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = proc.communicate(input=file_content, timeout=30)
            execution_time = time.time() - start_time
            
            if proc.returncode != 0:
                error_msg = stderr if stderr else "Unknown error"
                result = {
                    "success": False,
                    "error": f"Command failed with code {proc.returncode}: {error_msg}",
                    "execution_time": execution_time
                }
            else:
                try:
                    response_json = json.loads(stdout)
                    
                    if "session_id" in response_json:
                        session_manager.before_session_id = response_json["session_id"]
                    
                    result = {
                        "success": True,
                        "response": response_json.get("result", ""),
                        "execution_time": execution_time
                    }
                    
                except json.JSONDecodeError as e:
                    result = {
                        "success": False,
                        "error": f"JSON parse error: {str(e)}",
                        "raw_output": stdout,
                        "execution_time": execution_time
                    }
                    
        except subprocess.TimeoutExpired:
            result = {
                "success": False,
                "error": f"Timeout after {timeout} seconds",
                "execution_time": timeout
            }
        except Exception as e:
            result = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    else:
        # Unix系は既存の非同期版を使用
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=file_content.encode()), 
                timeout=30
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
                try:
                    response_json = json.loads(stdout.decode())
                    
                    if "session_id" in response_json:
                        session_manager.before_session_id = response_json["session_id"]
                    
                    result = {
                        "success": True,
                        "response": response_json.get("result", ""),
                        "execution_time": execution_time
                    }
                    
                except json.JSONDecodeError as e:
                    result = {
                        "success": False,
                        "error": f"JSON parse error: {str(e)}",
                        "raw_output": stdout.decode() if stdout else "",
                        "execution_time": execution_time
                    }
                    
        except asyncio.TimeoutError:
            result = {
                "success": False,
                "error": f"Timeout after {timeout} seconds",
                "execution_time": timeout
            }
        except Exception as e:
            result = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    # 完全な返り値を構築
    full_result = {
        "success": result["success"],
        "prompt": prompt,
        "response": result.get("response"),
        "execution_time": result["execution_time"],
        "timestamp": datetime.now().isoformat(),
        "error": result.get("error"),
        "context_file": file_path
    }
    
    session_manager._add_history(full_result)
    
    return full_result


@mcp.tool()
async def get_execution_history(limit: int = 10) -> Dict:
    """実行履歴を取得"""
    history_slice = session_manager.history[-limit:] if limit > 0 else session_manager.history
    
    return {
        "success": True,
        "history": history_slice,
        "total_entries": len(session_manager.history),
        "current_session_id": session_manager.before_session_id
    }


@mcp.tool()
async def clear_execution_history() -> Dict:
    """実行履歴をクリア"""
    cleared_count = len(session_manager.history)
    session_manager.history = []
    
    return {
        "success": True,
        "message": f"Cleared {cleared_count} history entries",
        "cleared_count": cleared_count
    }


@mcp.tool()
async def get_current_session() -> Dict:
    """現在のセッションIDを取得"""
    return {
        "success": True,
        "session_id": session_manager.before_session_id,
        "has_session": session_manager.before_session_id is not None
    }


@mcp.tool()
async def reset_session() -> Dict:
    """セッションをリセット"""
    old_session_id = session_manager.before_session_id
    session_manager.before_session_id = None
    
    return {
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
    asyncio.run(mcp.run_stdio_async())