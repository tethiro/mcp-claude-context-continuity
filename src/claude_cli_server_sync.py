#!/usr/bin/env python3
"""Claude CLI MCP Server - 同期実行版"""

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
DEFAULT_TIMEOUT = 300

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
        """Claude実行コマンドを取得"""
        if self.claude_command is None:
            # WSL環境では直接パスを使用
            self.claude_command = "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude"
        return self.claude_command

# グローバルセッションマネージャー
session_manager = ClaudeSessionManager()

# デバッグログ
debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')

def _execute_claude_command_sync(cmd: List[str]) -> Dict:
    """Claude CLIコマンドを同期的に実行"""
    start_time = time.time()
    
    # デバッグ: 実行コマンドをログに記録
    with open(debug_log_path, 'a') as f:
        f.write(f"\n[{datetime.now().isoformat()}] Executing command (SYNC): {' '.join(cmd)}\n")
    
    try:
        # 同期実行
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            stdin=subprocess.DEVNULL,
            encoding='utf-8',
            errors='replace'
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
        
        # 出力を処理
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

@mcp.tool()
async def execute_claude(prompt: str) -> Dict:
    """Claude CLIを実行して結果を返す（同期版）"""
    
    # Claude実行コマンドを取得
    try:
        claude_cmd = await session_manager.get_claude_command()
    except FileNotFoundError as e:
        return {
            "tool_name": "execute_claude",
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
        with open(debug_log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Using --resume with session_id: {session_manager.before_session_id}\n")
    
    # プロンプトを追加
    cmd.extend(["-p", prompt])
    
    # コマンド実行（同期）
    result = _execute_claude_command_sync(cmd)
    
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
async def test_claude_cli() -> Dict:
    """Claude CLIが正しく設定されているかテスト"""
    
    claude_cmd = await session_manager.get_claude_command()
    
    if isinstance(claude_cmd, str):
        cmd = [claude_cmd, "--version"]
    else:
        cmd = claude_cmd.copy() + ["--version"]
    
    # 同期実行
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
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
            
    except Exception as e:
        return {
            "tool_name": "test_claude_cli",
            "success": False,
            "command": " ".join(cmd),
            "error": str(e),
            "message": "Error executing Claude CLI"
        }

# 他のツールも定義（元のまま）
@mcp.tool()
async def get_execution_history(limit: int = 10) -> Dict:
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
    return {
        "tool_name": "get_current_session",
        "success": True,
        "session_id": session_manager.before_session_id,
        "has_session": session_manager.before_session_id is not None
    }

@mcp.tool()
async def reset_session() -> Dict:
    old_session_id = session_manager.before_session_id
    session_manager.before_session_id = None
    return {
        "tool_name": "reset_session",
        "success": True,
        "message": "Session reset successfully",
        "old_session_id": old_session_id
    }

@mcp.tool()
async def execute_claude_with_context(prompt: str, file_path: str) -> Dict:
    # 簡略版
    return {
        "tool_name": "execute_claude_with_context",
        "success": False,
        "prompt": prompt,
        "response": None,
        "execution_time": 0,
        "timestamp": datetime.now().isoformat(),
        "error": "Not implemented in sync version",
        "context_file": file_path
    }

# メインエントリーポイント
if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())