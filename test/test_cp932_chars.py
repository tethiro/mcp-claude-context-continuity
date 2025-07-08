#!/usr/bin/env python3
"""cp932でサポートされている文字の確認"""

def check_cp932_support():
    """各種文字のcp932サポート状況を確認"""
    
    test_chars = [
        ("²", "上付き2"),
        ("³", "上付き3"),
        ("α", "アルファ"),
        ("β", "ベータ"),
        ("γ", "ガンマ"),
        ("π", "パイ"),
        ("♪", "8分音符"),
        ("♫", "連桁8分音符"),
        ("√", "ルート"),
        ("∞", "無限大"),
        ("°", "度記号"),
        ("±", "プラスマイナス"),
        ("×", "乗算記号"),
        ("÷", "除算記号"),
        ("≠", "不等号"),
        ("≤", "以下"),
        ("≥", "以上"),
        ("∈", "属する"),
        ("∉", "属さない"),
        ("⊂", "部分集合"),
    ]
    
    print("=== cp932 文字サポート状況 ===\n")
    print("文字 | 名前         | cp932サポート")
    print("-" * 40)
    
    for char, name in test_chars:
        try:
            char.encode('cp932')
            supported = "○"
        except UnicodeEncodeError:
            supported = "×"
        
        print(f"{char:>3} | {name:<12} | {supported}")

if __name__ == "__main__":
    check_cp932_support()