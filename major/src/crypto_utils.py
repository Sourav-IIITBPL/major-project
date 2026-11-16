"""
Fast Miller-Rabin Probabilistic Prime Generator for Cryptographic Workloads.
"""

import secrets

def is_prime(n: int, k: int = 20) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
        
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
        
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits: int) -> int:
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate
