#!/usr/bin/env python3
"""Claude CLI MCP Server - 即時デバッグ版"""

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
        """Claude実行コマンドを取得"""
        if self.claude_command is None:
            # WSL環境では直接パスを使用
            self.claude_command = "/home/tethiro/.nvm/versions/node/v22.17.0/bin/claude"
        return self.claude_command

# グローバルセッションマネージャー
session_manager = ClaudeSessionManager()

@mcp.tool()
async def execute_claude(prompt: str) -> Dict:
    """デバッグ版：コマンド文字列を即座に返す"""
    
    # Claude実行コマンドを取得
    claude_cmd = await session_manager.get_claude_command()
    
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
    
    # プロンプトを追加
    cmd.extend(["-p", prompt])
    
    # コマンド文字列を作成
    command_str = " ".join(cmd)
    
    # 即座に返す
    return {
        "tool_name": "execute_claude",
        "success": True,
        "prompt": prompt,
        "response": f"DEBUG: Command to execute: {command_str}",
        "execution_time": 0.001,
        "timestamp": datetime.now().isoformat(),
        "error": None,
        "debug_info": {
            "platform": platform.system(),
            "cmd_list": cmd,
            "cmd_string": command_str,
            "session_id": session_manager.before_session_id
        }
    }

@mcp.tool()
async def test_claude_cli() -> Dict:
    """Claude CLIが正しく設定されているかテスト"""
    
    claude_cmd = await session_manager.get_claude_command()
    
    if isinstance(claude_cmd, str):
        cmd = [claude_cmd, "--version"]
    else:
        cmd = claude_cmd.copy() + ["--version"]
    
    # コマンド実行（同期）
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
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

# 他のツールも定義（簡略版）
@mcp.tool()
async def get_execution_history(limit: int = 10) -> Dict:
    return {
        "tool_name": "get_execution_history",
        "success": True,
        "history": session_manager.history[-limit:] if limit > 0 else session_manager.history,
        "total_entries": len(session_manager.history),
        "current_session_id": session_manager.before_session_id
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
async def execute_claude_with_context(prompt: str, file_path: str) -> Dict:
    return {
        "tool_name": "execute_claude_with_context",
        "success": True,
        "prompt": prompt,
        "response": f"DEBUG: Would execute with file context: {file_path}",
        "execution_time": 0.001,
        "timestamp": datetime.now().isoformat(),
        "error": None,
        "context_file": file_path
    }

# メインエントリーポイント
if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())