#!/usr/bin/env python3
"""WSL環境でのプラットフォーム検出テスト"""

import platform
import sys
import os

print("=== WSL Platform Detection ===")
print(f"platform.system(): {platform.system()}")
print(f"sys.platform: {sys.platform}")
print(f"os.name: {os.name}")
print(f"platform.release(): {platform.release()}")
print(f"platform.version(): {platform.version()}")

# WSL検出
is_wsl = False
if os.path.exists("/proc/version"):
    with open("/proc/version", "r") as f:
        if "microsoft" in f.read().lower():
            is_wsl = True

print(f"\nIs WSL: {is_wsl}")
print(f"Is Windows: {platform.system() == 'Windows'}")
print(f"Is Linux: {platform.system() == 'Linux'}")