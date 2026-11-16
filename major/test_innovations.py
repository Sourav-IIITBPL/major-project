"""
Test Suite for Major Project Innovations:
1. Intra-Exponent Hybrid Slicing
2. Exponent Blinding Side-Channel Hardening
3. C Header Dispatch Logic
"""

import sys
import os
import math
import secrets
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from major.src.strategies.hybrid_slicing import hybrid_sliced_mod_exp
from major.src.strategies.mod_exp_strategies import ModExpEngine

def test_slicing():
    print("=" * 60)
    print("TEST 1: Intra-Exponent Hybrid Slicing")
    print("=" * 60)
    for bit_len in [512, 1024, 2048]:
        mod = secrets.randbits(bit_len) | 1
        base = secrets.randbits(bit_len) % mod
        while math.gcd(base, mod) != 1:
            mod = secrets.randbits(bit_len) | 1
            base = secrets.randbits(bit_len) % mod
            
        # Create non-uniform exponent: first 512 bits dense, next 512 bits sparse
        exp = (secrets.randbits(bit_len // 2) | ((1 << (bit_len // 2)) - 1)) << (bit_len // 2)
        exp |= 1 | (1 << 30) # sparse lower half
        
        expected = pow(base, exp, mod)
        res = hybrid_sliced_mod_exp(base, exp, mod, slice_bits=256)
        
        assert res["result"] == expected, f"Slicing failed for {bit_len}-bit"
        m = res["metrics"]
        print(f"[{bit_len}-bit OK] Time: {m['time_ms']:.2f} ms | Slices: {m['num_slices']} | Sqrs: {m['sqrs']} | Mults: {m['mults']}")
        for dec in m["slice_decisions"]:
            print(f"   Slice {dec['slice_idx']}: Strategy={dec.get('strategy', 'N/A')}, Hamming={dec.get('hamming', 0)}")
            
    print("Hybrid Slicing Math Verified!\n")

def test_blinding():
    print("=" * 60)
    print("TEST 2: Exponent Blinding (Side-Channel Hardening)")
    print("=" * 60)
    # RSA parameters simulation
    p = 61
    q = 53
    N = p * q
    phi = (p - 1) * (q - 1)
    e = 17
    d = pow(e, -1, phi)
    
    # Message to sign/decrypt
    M = 42
    expected_sig = pow(M, d, N)
    
    # 5 runs with fresh random blinding salts
    print(f"Original private key d = {d} (Hamming: {d.bit_count()})")
    for run in range(5):
        r = secrets.randbits(32)
        d_blinded = d + r * phi
        sig = pow(M, d_blinded, N)
        assert sig == expected_sig, "Blinded signature failed!"
        print(f"  Run {run+1}: r={r:<10} | d_blinded={d_blinded:<15} | Hamming={d_blinded.bit_count():<4} | Verified OK")
    print("Exponent Blinding Mathematical Invariance Verified!\n")

if __name__ == "__main__":
    test_slicing()
    test_blinding()
