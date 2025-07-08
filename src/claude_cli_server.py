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
        self.is_manually_set: bool = False  # 手動設定されたセッションかどうか
        
    def _add_history(self, entry: Dict):
        """履歴に操作を追加"""
        self.history.append(entry)
        # 最新100件のみ保持
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def build_claude_command(self, claude_cmd: Union[str, List[str]], prompt: str, include_resume: bool = True) -> List[str]:
        """Claude CLIコマンドを構築する共通関数
        
        Args:
            claude_cmd: Claude実行コマンド（文字列またはリスト）
            prompt: Claudeに送るプロンプト
            include_resume: --resumeオプションを含めるかどうか
            
        Returns:
            構築されたコマンドリスト
        """
        # 基本的な引数を構築
        base_args = [
            "--dangerously-skip-permissions",
            "--output-format", "json"
        ]
        
        # before_session_idがある場合は --resume オプションを追加
        if include_resume and self.before_session_id is not None:
            base_args.extend(["--resume", self.before_session_id])
            # デバッグ: resumeセッションIDをログに記録
            debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')
            with open(debug_log_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] Using --resume with session_id: {self.before_session_id}\n")
        
        # プロンプトを追加
        base_args.extend(["-p", prompt])
        
        # コマンドを構築
        if isinstance(claude_cmd, str):
            # Unix系: '/path/to/claude' -> ['/path/to/claude', '--arg1', '--arg2', ...]
            return [claude_cmd] + base_args
        else:
            # Windows: ['wsl', '--', '/path/to/claude'] -> ['wsl', '--', '/path/to/claude', '--arg1', '--arg2', ...]
            return claude_cmd + base_args
    
    def build_claude_version_command(self, claude_cmd: Union[str, List[str]]) -> List[str]:
        """Claude CLI --versionコマンドを構築する
        
        Args:
            claude_cmd: Claude実行コマンド（文字列またはリスト）
            
        Returns:
            構築されたコマンドリスト
        """
        if isinstance(claude_cmd, str):
            # Unix系: '/path/to/claude' -> ['/path/to/claude', '--version']
            return [claude_cmd, "--version"]
        else:
            # Windows: ['wsl', '--', '/path/to/claude'] -> ['wsl', '--', '/path/to/claude', '--version']
            return claude_cmd + ["--version"]
            
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
        """WindowsでWSL経由のClaude CLIを探す"""
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


async def _execute_claude_command(cmd: List[str], retry_count: int = 0) -> Dict:
    """Claude CLIコマンドを実行して結果を返す（内部は同期実行）
    
    MCPのasync関数として定義されているが、内部のCLI実行は同期的に行う。
    
    Args:
        cmd: 実行するコマンド
        retry_count: 現在のリトライ回数（内部使用）
    """
    start_time = time.time()
    
    # デバッグ: 実行コマンドをログファイルに記録
    debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')
    with open(debug_log_path, 'a') as f:
        f.write(f"\n[{datetime.now().isoformat()}] Executing command: {' '.join(cmd)}\n")
    
    # 全環境で同期実行を使用（MCPは1対1通信のため非同期の必要なし）
    try:
        # エンコーディング設定（Windows環境向け）
        if platform.system() == "Windows":
            # Windowsの場合、cmd は ['wsl', '--', '/path/to/claude', ...] の形式
            encoding_kwargs = {'encoding': 'utf-8', 'errors': 'replace'}
        else:
            # Unix系の場合、cmd は ['/path/to/claude', ...] の形式
            encoding_kwargs = {'encoding': 'utf-8'}
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=DEFAULT_TIMEOUT,
            stdin=subprocess.DEVNULL,
            **encoding_kwargs
        )
        
        execution_time = time.time() - start_time
        
        # デバッグ: 結果をログに記録
        with open(debug_log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Return code: {result.returncode}, Time: {execution_time:.2f}s\n")
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return {
                "success": False,
                "error": f"Command failed with code {result.returncode}: {error_msg}",
                "execution_time": execution_time
            }
        
        # 出力を処理
        output = result.stdout.strip()
        
        # デバッグ: 生の出力をログに記録（最初の500文字のみ）
        with open(debug_log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Raw output (first 500 chars): {output[:500]}\n")
        
        # JSON形式かチェック
        if output.startswith('{'):
            try:
                response_json = json.loads(output)
                
                # デバッグ: JSONの構造をログに記録
                with open(debug_log_path, 'a') as f:
                    f.write(f"[{datetime.now().isoformat()}] JSON keys: {list(response_json.keys())}\n")
                    if "result" in response_json:
                        f.write(f"[{datetime.now().isoformat()}] Result field: '{response_json['result']}'\n")
                
                # session_idがあれば保存
                if "session_id" in response_json:
                    new_session_id = response_json["session_id"]
                    old_session_id = session_manager.before_session_id
                    
                    # 手動設定されたセッションの場合
                    if session_manager.is_manually_set:
                        with open(debug_log_path, 'a') as f:
                            f.write(f"[{datetime.now().isoformat()}] Manual session kept: {old_session_id} (new would be: {new_session_id})\n")
                        # 手動設定フラグをリセット（次回からは通常モードに戻る）
                        session_manager.is_manually_set = False
                    else:
                        # 通常の自動更新
                        session_manager.before_session_id = new_session_id
                        with open(debug_log_path, 'a') as f:
                            f.write(f"[{datetime.now().isoformat()}] Session updated: {old_session_id} -> {new_session_id}\n")
                
                # resultフィールドの内容を確認
                result_content = response_json.get("result", "")
                
                # resultフィールドの型を確認してログに記録
                with open(debug_log_path, 'a') as f:
                    f.write(f"[{datetime.now().isoformat()}] Result type: {type(result_content).__name__}, value: {repr(result_content)[:200]}\n")
                
                # resultが文字列でない場合の処理
                if isinstance(result_content, (list, dict)):
                    # 配列やオブジェクトの場合はJSON文字列に変換
                    result_str = json.dumps(result_content, ensure_ascii=False)
                    with open(debug_log_path, 'a') as f:
                        f.write(f"[{datetime.now().isoformat()}] INFO: Result is {type(result_content).__name__}, converting to string: {result_str[:200]}\n")
                elif result_content is None:
                    # Noneの場合は空文字列にする
                    result_str = ""
                    with open(debug_log_path, 'a') as f:
                        f.write(f"[{datetime.now().isoformat()}] WARNING: Result is None, using empty string\n")
                else:
                    # 文字列の場合はそのまま使用
                    result_str = str(result_content)
                
                # 空の応答の場合は警告をログに記録
                if not result_str:
                    with open(debug_log_path, 'a') as f:
                        f.write(f"[{datetime.now().isoformat()}] WARNING: Empty result detected. Full JSON: {json.dumps(response_json, ensure_ascii=False)[:1000]}\n")
                        # エラーチェック
                        if response_json.get("is_error", False):
                            f.write(f"[{datetime.now().isoformat()}] ERROR: is_error=True, subtype={response_json.get('subtype', 'unknown')}\n")
                        # 実行時間情報
                        f.write(f"[{datetime.now().isoformat()}] Duration info: duration_ms={response_json.get('duration_ms', 'N/A')}, duration_api_ms={response_json.get('duration_api_ms', 'N/A')}\n")
                
                # 実行時間が長い場合も警告
                if execution_time > 30:
                    with open(debug_log_path, 'a') as f:
                        f.write(f"[{datetime.now().isoformat()}] WARNING: Long execution time: {execution_time:.2f}s\n")
                
                # 警告メッセージの構築
                warning = None
                if not result_str:
                    subtype = response_json.get("subtype", "unknown")
                    if response_json.get("is_error", False) or "error" in subtype:
                        warning = f"Claude CLI error: subtype={subtype}"
                        # error_during_executionの場合は特別な処理
                        if subtype == "error_during_execution":
                            output_tokens = response_json.get("usage", {}).get("output_tokens", 0)
                            if output_tokens > 0:
                                warning += f" (generated {output_tokens} tokens but no result returned)"
                    else:
                        warning = "Empty response from Claude CLI"
                elif execution_time > 30:
                    warning = f"Long execution time: {execution_time:.1f}s"
                
                # 手動設定セッションが見つからなかった場合の警告
                if session_manager.is_manually_set and "session_id" in response_json:
                    if session_manager.before_session_id != response_json["session_id"]:
                        if warning:
                            warning += "; "
                        else:
                            warning = ""
                        warning += f"Manual session not found, new session created"
                
                # 空の応答でerror_during_executionの場合の処理
                is_execution_error = not result_str and response_json.get("subtype") == "error_during_execution"
                
                if is_execution_error and retry_count < 1:
                    # 1回だけリトライ
                    with open(debug_log_path, 'a') as f:
                        f.write(f"[{datetime.now().isoformat()}] RETRY: error_during_execution detected, retrying... (attempt {retry_count + 1})\n")
                    
                    # 少し待機してからリトライ
                    time.sleep(2)
                    
                    # リトライ実行（再帰呼び出し）
                    return await _execute_claude_command(cmd, retry_count + 1)
                
                return {
                    "success": not is_execution_error,
                    "response": result_str,
                    "execution_time": execution_time,
                    "warning": warning,
                    "error": "Claude CLI execution error (retried once)" if is_execution_error and retry_count > 0 else "Claude CLI execution error" if is_execution_error else None
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
    
    # コマンドを構築（共通関数を使用）
    cmd = session_manager.build_claude_command(claude_cmd, prompt)
    
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
    
    # コマンドを構築（共通関数を使用）
    cmd = session_manager.build_claude_command(claude_cmd, prompt)
    
    # コマンド実行（ファイル内容を標準入力として渡す）
    start_time = time.time()
    
    # 全環境で同期実行を使用（MCPは1対1通信のため非同期の必要なし）
    try:
        # エンコーディング設定
        if platform.system() == "Windows":
            encoding_kwargs = {'encoding': 'utf-8', 'errors': 'replace'}
        else:
            encoding_kwargs = {'encoding': 'utf-8'}
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            **encoding_kwargs
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
            
            # デバッグ: 生の出力をログに記録（最初の500文字のみ）
            debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')
            with open(debug_log_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] execute_claude_with_context Raw output (first 500 chars): {output[:500]}\n")
            
            # JSON形式かチェック
            if output.startswith('{'):
                try:
                    response_json = json.loads(output)
                    
                    # デバッグ: JSONの構造をログに記録
                    with open(debug_log_path, 'a') as f:
                        f.write(f"[{datetime.now().isoformat()}] execute_claude_with_context JSON keys: {list(response_json.keys())}\n")
                        if "result" in response_json:
                            f.write(f"[{datetime.now().isoformat()}] execute_claude_with_context Result field: '{response_json['result']}'\n")
                    
                    # session_idがあれば保存
                    if "session_id" in response_json:
                        old_session_id = session_manager.before_session_id
                        session_manager.before_session_id = response_json["session_id"]
                        with open(debug_log_path, 'a') as f:
                            f.write(f"[{datetime.now().isoformat()}] Session updated: {old_session_id} -> {response_json['session_id']}\n")
                    
                    # resultフィールドの内容を確認
                    result_content = response_json.get("result", "")
                    
                    # 空の応答の場合は警告をログに記録
                    if not result_content:
                        with open(debug_log_path, 'a') as f:
                            f.write(f"[{datetime.now().isoformat()}] WARNING: execute_claude_with_context - Empty result field detected. Full JSON: {json.dumps(response_json)}\n")
                    
                    result = {
                        "success": True,
                        "response": result_content,
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
        cmd = session_manager.build_claude_version_command(claude_cmd)
        
        # 全環境で同期実行を使用（MCPは1対1通信のため非同期の必要なし）
        try:
            # エンコーディング設定
            if platform.system() == "Windows":
                encoding_kwargs = {'encoding': 'utf-8', 'errors': 'replace'}
            else:
                encoding_kwargs = {'encoding': 'utf-8'}
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,  # 短いタイムアウト
                stdin=subprocess.DEVNULL,
                **encoding_kwargs
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
    session_manager.is_manually_set = False  # 手動設定フラグもリセット
    
    return {
        "tool_name": "reset_session",
        "success": True,
        "message": "Session reset successfully",
        "old_session_id": old_session_id
    }


@mcp.tool()
async def set_current_session(session_id: str) -> Dict:
    """セッションIDを即座に設定（実行は一瞬で完了）
    
    単に内部変数を更新するだけの軽量な処理です。
    次回のexecute_claude実行時に、指定したセッションIDが使用されます。
    
    Args:
        session_id: 設定するセッションID（文字列）
        
    Returns:
        操作結果を含む辞書（即座に返される）
    """
    try:
        old_session_id = session_manager.before_session_id
        session_manager.before_session_id = session_id
        session_manager.is_manually_set = True  # 手動設定フラグを立てる
        
        # デバッグログに記録
        debug_log_path = os.path.join(os.path.dirname(__file__), '..', 'claude_command_debug.log')
        with open(debug_log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Session manually set: {old_session_id} -> {session_id} (manual flag ON)\n")
        
        return {
            "tool_name": "set_current_session",
            "success": True,
            "message": f"Session ID set to: {session_id}",
            "old_session_id": old_session_id,
            "new_session_id": session_id
        }
    except Exception as e:
        return {
            "tool_name": "set_current_session",
            "success": False,
            "error": f"Failed to set session: {str(e)}",
            "old_session_id": session_manager.before_session_id,
            "new_session_id": None
        }


# Windows環境用の設定
if platform.system() == "Windows":
    # WindowsでのProactorEventLoopポリシー設定
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# メインエントリーポイント
if __name__ == "__main__":
    # stdio経由でサーバーを起動
    asyncio.run(mcp.run_stdio_async())