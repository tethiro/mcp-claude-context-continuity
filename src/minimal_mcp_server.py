#!/usr/bin/env python3
"""最小限のMCPサーバー（動作確認用）"""

import asyncio
from mcp.server.fastmcp import FastMCP

# FastMCPインスタンスの作成
mcp = FastMCP("minimal-test-server")

@mcp.tool()
async def hello(name: str = "World") -> str:
    """シンプルな挨拶を返す
    
    Args:
        name: 挨拶する相手の名前
        
    Returns:
        挨拶メッセージ
    """
    return f"Hello, {name}!"

@mcp.tool()
async def echo(message: str) -> str:
    """メッセージをそのまま返す
    
    Args:
        message: エコーバックするメッセージ
        
    Returns:
        入力されたメッセージ
    """
    return message

# メインエントリーポイント
if __name__ == "__main__":
    # stdio経由でサーバーを起動
    asyncio.run(mcp.run_stdio_async())