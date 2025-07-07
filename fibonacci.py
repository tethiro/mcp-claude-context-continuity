def fibonacci(n):
    """フィボナッチ数列の最初のn項を計算する"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib

# 最初の10項を計算
result = fibonacci(10)
print(f"フィボナッチ数列の最初の10項: {result}")