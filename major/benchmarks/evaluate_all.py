"""
Comprehensive Benchmarking Suite for Major Project (Including All Innovations).
Evaluates:
  1. Fixed Binary L-to-R (Baseline)
  2. Fixed Standard NAF
  3. Fixed Windowed NAF (w=3)
  4. Fixed Adaptive VLIM
  5. ML-Adaptive Engine (Whole Exponent)
  6. Hybrid-Sliced Engine (Intra-Exponent Multi-Strategy)
  7. Blinded-Adaptive Engine (Side-Channel Hardened)
"""

import sys
import os
import math
import secrets
import time
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from major.src.crypto_utils import generate_prime
from major.src.adaptive_engine import AdaptiveCryptoEngine
from major.src.ml.generate_dataset import generate_custom_exponent, compute_hw_cost

def run_evaluation(num_trials_per_bit: int = 5):
    print("=" * 115)
    print("MAJOR PROJECT: COMPREHENSIVE BENCHMARK EVALUATION (INNOVATIONS INCLUDED)")
    print("=" * 115)
    
    bit_lengths = [256, 512, 1024, 2048]
    profiles = ["uniform", "sparse", "dense", "bursty"]
    modes = [
        "fixed_binary",
        "fixed_naf",
        "fixed_wnaf",
        "fixed_vlim",
        "ml_adaptive",
        "hybrid_sliced",
        "blinded_adaptive"
    ]
    
    results = []
    
    for bit_len in bit_lengths:
        print(f"Generating true RSA primes and profiling {bit_len}-bit cryptographic scale...")
        # True RSA modulus: N = p * q
        p = generate_prime(bit_len // 2)
        q = generate_prime(bit_len // 2)
        while p == q:
            q = generate_prime(bit_len // 2)
        mod = p * q
        phi_m = (p - 1) * (q - 1)
        
        base = secrets.randbits(bit_len) % mod
        while math.gcd(base, mod) != 1:
            base = secrets.randbits(bit_len) % mod
            
        for prof in profiles:
            for _ in range(num_trials_per_bit):
                exp = generate_custom_exponent(bit_len, prof)
                expected_val = pow(base, exp, mod)
                
                for mode in modes:
                    res = AdaptiveCryptoEngine.execute(base, exp, mod, mode=mode, phi_m=phi_m, slice_bits=256)
                    assert res["result"] == expected_val, f"Correctness failed for {mode} on {bit_len}-bit {prof}"
                    
                    m = res["metrics"]
                    hw_cost = compute_hw_cost(m)
                    
                    results.append({
                        "bit_length": bit_len,
                        "profile": prof,
                        "mode": mode,
                        "strategy_used": res["selected_strategy"],
                        "total_time_ms": res["total_time_ms"],
                        "dispatch_us": res["dispatch_time_us"],
                        "iters": m["iters"],
                        "sqrs": m["sqrs"],
                        "mults": m["mults"],
                        "hw_cost": hw_cost
                    })

    df = pd.DataFrame(results)
    
    print("\n" + "=" * 115)
    print("OVERALL PERFORMANCE SUMMARY ACROSS ALL WORKLOADS (256-bit to 2048-bit)")
    print("=" * 115)
    summary = df.groupby("mode").agg({
        "total_time_ms": "mean",
        "dispatch_us": "mean",
        "iters": "mean",
        "mults": "mean",
        "sqrs": "mean",
        "hw_cost": "mean"
    }).reset_index()
    
    base_time = summary[summary["mode"] == "fixed_binary"]["total_time_ms"].values[0]
    base_mults = summary[summary["mode"] == "fixed_binary"]["mults"].values[0]
    
    summary["speedup_%"] = ((base_time - summary["total_time_ms"]) / base_time) * 100
    summary["mult_reduction_%"] = ((base_mults - summary["mults"]) / base_mults) * 100
    
    print(f"{'Strategy / Engine Mode':<24} | {'Time(ms)':<10} | {'Speedup':<10} | {'Mults':<8} | {'Mult Cut':<10} | {'Iters':<8} | {'HW Cost':<10}")
    print("-" * 115)
    for _, r in summary.iterrows():
        print(f"{r['mode']:<24} | {r['total_time_ms']:<10.3f} | {r['speedup_%']:>+7.1f}%   | {r['mults']:<8.1f} | {r['mult_reduction_%']:>+7.1f}%   | {r['iters']:<8.1f} | {r['hw_cost']:<10.1f}")
    print("=" * 115)
    
    # 2048-bit scale
    print("\n" + "=" * 115)
    print("2048-BIT HIGH-SECURITY RSA WORKLOAD BREAKDOWN")
    print("=" * 115)
    df_2048 = df[df["bit_length"] == 2048].groupby("mode").agg({
        "total_time_ms": "mean",
        "mults": "mean",
        "sqrs": "mean",
        "iters": "mean"
    }).reset_index()
    t_2048_base = df_2048[df_2048["mode"] == "fixed_binary"]["total_time_ms"].values[0]
    df_2048["speedup_%"] = ((t_2048_base - df_2048["total_time_ms"]) / t_2048_base) * 100
    
    print(f"{'Strategy / Engine Mode':<24} | {'Time (ms)':<12} | {'Speedup vs Binary':<18} | {'Multiplications':<16} | {'Iterations':<12}")
    print("-" * 115)
    for _, r in df_2048.iterrows():
        print(f"{r['mode']:<24} | {r['total_time_ms']:<12.3f} | {r['speedup_%']:>+12.1f}%     | {r['mults']:<16.1f} | {r['iters']:<12.1f}")
    print("=" * 115)
    
    os.makedirs("major/data", exist_ok=True)
    df.to_csv("major/data/comprehensive_benchmark_results.csv", index=False)
    print("\nDetailed benchmark data saved to major/data/comprehensive_benchmark_results.csv")

if __name__ == "__main__":
    run_evaluation(num_trials_per_bit=5)
