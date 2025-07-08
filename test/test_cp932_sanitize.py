#!/usr/bin/env python3
"""cp932文字サニタイズ機能のテスト"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.claude_cli_server import ClaudeSessionManager

def test_sanitize():
    """cp932でエンコードできない文字の置換テスト"""
    manager = ClaudeSessionManager()
    
    # テストケース（新しい翻字ロジックに対応）
    test_cases = [
        ("通常の日本語テキスト", "通常の日本語テキスト"),  # 変更なし
        ("E=mc²の説明", "E=mc2の説明"),  # ²が2に置換
        ("α粒子とβ線について", "alpha粒子とbeta線について"),  # ギリシャ文字が英語名に
        ("音楽記号♪♫を使った表現", "音楽記号notenotes を使った表現"),  # 音符記号が説明的に
        ("1番目、2番目、3番目", "1番目、2番目、3番目"),  # 通常の数字は問題なし
        ("面積はπr²です", "面積はpir2です"),  # πと²が意味を保つ形で置換
        ("A ≤ B かつ C ≥ D", "A <= B かつ C >= D"),  # 不等号が適切に変換
        ("温度は25°Cです", "温度は25degCです"),  # 度記号も変換
        ("√2 ≈ 1.414", "sqrt2 ~= 1.414"),  # ルートと約等号
        ("x ∈ S, y ∉ S", "x in S, y not in S"),  # 集合記号
        ("Σ(i=1→n) = n(n+1)/2", "Sigma(i=1->n) = n(n+1)/2"),  # 大文字ギリシャと矢印
    ]
    
    print("=== cp932 サニタイズテスト ===\n")
    
    for original, expected in test_cases:
        result = manager.sanitize_prompt_for_cp932(original)
        status = "✓" if result == expected else "✗"
        print(f"{status} 入力: {original}")
        print(f"  期待: {expected}")
        print(f"  結果: {result}")
        print()
    
    # Windows環境でのコマンド構築テスト
    if sys.platform == "win32":
        print("=== Windows環境でのコマンド構築テスト ===\n")
        cmd = manager.build_claude_command(
            ["wsl", "--", "/path/to/claude"],
            "E=mc²について説明してください"
        )
        print(f"構築されたコマンド: {cmd}")
        print(f"プロンプト部分: {cmd[-1]}")

if __name__ == "__main__":
    test_sanitize()