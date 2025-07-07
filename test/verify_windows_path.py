#!/usr/bin/env python3
"""Windows環境のパス確認スクリプト"""

import os
import sys
import platform

print(f"Platform: {platform.system()}")
print(f"Python: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# スクリプトのパス
script_path = "C:\\prj\\AI\\prg\\mcp-claude-context-continuity\\src\\claude_cli_server.py"
print(f"\nChecking script path: {script_path}")

# WSL内のパスに変換
wsl_path = "/mnt/c/prj/AI/prg/mcp-claude-context-continuity/src/claude_cli_server.py"
print(f"WSL path: {wsl_path}")

# ファイルの存在確認
if os.path.exists(wsl_path):
    print(f"✅ File exists (WSL path)")
else:
    print(f"❌ File not found (WSL path)")
    
# 設定ファイルの例を出力
config = {
    "mcpServers": {
        "claude-context-continuity": {
            "command": "python",
            "args": [
                "C:\\\\prj\\\\AI\\\\prg\\\\mcp-claude-context-continuity\\\\src\\\\claude_cli_server.py"
            ]
        }
    }
}

import json
print(f"\nRecommended Windows config:")
print(json.dumps(config, indent=2))