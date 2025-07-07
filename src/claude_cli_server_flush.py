#!/usr/bin/env python3
"""Claude CLI MCP Server - フラッシュ版"""

import sys

# 標準出力のバッファリングを無効化
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

# 元のサーバーをインポート
from claude_cli_server import *

# メインエントリーポイント
if __name__ == "__main__":
    # バッファリングを完全に無効化
    import os
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # stdio経由でサーバーを起動
    asyncio.run(mcp.run_stdio_async())