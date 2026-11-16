"""
Rigorous Multi-Dimensional Cryptographic Benchmarking Study.
Runs statistical evaluations across bit scales, exponent topologies, and memory bounds.
Outputs:
  - Mean Latency + Standard Deviation
  - Operation counts (Squarings, Multiplications, Iterations)
  - Peak Memory Overhead (tracemalloc)
  - Speedup and Reduction Percentages
"""

import sys
import os
import math
import secrets
import time
import tracemalloc
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from major.src.crypto_utils import generate_prime
from major.src.adaptive_engine import AdaptiveCryptoEngine
from major.src.ml.generate_dataset import generate_custom_exponent, compute_hw_cost

def generate_alternating_exponent(bit_length: int) -> int:
    """Pattern of 101010..."""
    val = 0
    for i in range(bit_length):
        if i % 2 == 0:
            val |= (1 << i)
    return val

def run_deep_study(samples_per_case: int = 12):
    print("=" * 125)
    print("STARTING RIGOROUS DEEP COMPARATIVE STUDY ACROSS CRYPTOGRAPHIC SCALES")
    print(f"Sample Count: {samples_per_case} iterations per configuration with True RSA Moduli")
    print("=" * 125)
    
    bit_scales = [256, 512, 1024, 2048]
    profiles = ["uniform", "sparse", "dense", "bursty", "alternating"]
    modes = [
        "fixed_binary",
        "fixed_naf",
        "fixed_wnaf",
        "fixed_vlim",
        "ml_adaptive",
        "hybrid_sliced",
        "blinded_adaptive"
    ]
    
    records = []
    
    for bit_len in bit_scales:
        print(f"\n[SCALE {bit_len}-BIT] Generating true primes and testing topologies...")
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
            for s_idx in range(samples_per_case):
                if prof == "alternating":
                    exp = generate_alternating_exponent(bit_len)
                else:
                    exp = generate_custom_exponent(bit_len, prof)
                    
                expected = pow(base, exp, mod)
                
                for mode in modes:
                    tracemalloc.start()
                    t0 = time.perf_counter()
                    res = AdaptiveCryptoEngine.execute(base, exp, mod, mode=mode, phi_m=phi_m, slice_bits=256)
                    t_elapsed_ms = (time.perf_counter() - t0) * 1000
                    _, peak_mem_bytes = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    assert res["result"] == expected, f"Mathematical divergence in {mode} at {bit_len}-bit {prof}"
                    
                    m = res["metrics"]
                    records.append({
                        "bit_length": bit_len,
                        "profile": prof,
                        "sample_idx": s_idx,
                        "mode": mode,
                        "strategy": res["selected_strategy"],
                        "time_ms": t_elapsed_ms,
                        "peak_mem_kb": peak_mem_bytes / 1024.0,
                        "dispatch_us": res["dispatch_time_us"],
                        "sqrs": m["sqrs"],
                        "mults": m["mults"],
                        "total_muls": m["sqrs"] + m["mults"],
                        "iters": m["iters"],
                        "hw_cost": compute_hw_cost(m)
                    })

    df = pd.DataFrame(records)
    os.makedirs("major/data", exist_ok=True)
    df.to_csv("major/data/deep_comparative_results.csv", index=False)
    print("\nDataset successfully generated: major/data/deep_comparative_results.csv")
    
    # -------------------------------------------------------------------------
    # Report 1: Global Statistical Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 125)
    print("GLOBAL STATISTICAL SUMMARY (All Bit-Lengths & Profiles Aggregated)")
    print("=" * 125)
    
    global_stats = df.groupby("mode").agg(
        mean_time=("time_ms", "mean"),
        std_time=("time_ms", "std"),
        mean_mults=("mults", "mean"),
        mean_iters=("iters", "mean"),
        mean_mem_kb=("peak_mem_kb", "mean"),
        mean_hw_cost=("hw_cost", "mean")
    ).reset_index()
    
    base_t = global_stats[global_stats["mode"] == "fixed_binary"]["mean_time"].values[0]
    base_m = global_stats[global_stats["mode"] == "fixed_binary"]["mean_mults"].values[0]
    base_it = global_stats[global_stats["mode"] == "fixed_binary"]["mean_iters"].values[0]
    
    global_stats["speedup_%"] = ((base_t - global_stats["mean_time"]) / base_t) * 100
    global_stats["mult_cut_%"] = ((base_m - global_stats["mean_mults"]) / base_m) * 100
    global_stats["iter_cut_%"] = ((base_it - global_stats["mean_iters"]) / base_it) * 100
    
    print(f"{'Strategy / Engine Mode':<24} | {'Mean Time(ms)':<14} | {'StdDev':<8} | {'Speedup':<9} | {'Mults':<8} | {'Mult Cut':<9} | {'Cycles/Iters':<12} | {'Peak Mem':<10}")
    print("-" * 125)
    for _, r in global_stats.iterrows():
        print(f"{r['mode']:<24} | {r['mean_time']:<14.3f} | {r['std_time']:<8.3f} | {r['speedup_%']:>+6.1f}%   | {r['mean_mults']:<8.1f} | {r['mult_cut_%']:>+6.1f}%   | {r['mean_iters']:<12.1f} | {r['mean_mem_kb']:<10.2f} KB")
    print("=" * 125)
    
    # -------------------------------------------------------------------------
    # Report 2: Per-Scale Granular Breakdown (256, 512, 1024, 2048)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 125)
    print("PER-SCALE PERFORMANCE GRANULAR MATRIX")
    print("=" * 125)
    print(f"{'Scale':<8} | {'Mode':<22} | {'Time (ms)':<12} | {'Speedup':<10} | {'Mults':<10} | {'Iters':<10} | {'HW Cost':<10}")
    print("-" * 125)
    
    for b_scale in bit_scales:
        sub = df[df["bit_length"] == b_scale].groupby("mode").agg(
            t_mean=("time_ms", "mean"),
            m_mean=("mults", "mean"),
            it_mean=("iters", "mean"),
            hw_mean=("hw_cost", "mean")
        ).reset_index()
        
        b_t = sub[sub["mode"] == "fixed_binary"]["t_mean"].values[0]
        sub["speedup_%"] = ((b_t - sub["t_mean"]) / b_t) * 100
        
        for _, r in sub.iterrows():
            print(f"{b_scale:<8} | {r['mode']:<22} | {r['t_mean']:<12.3f} | {r['speedup_%']:>+7.1f}%   | {r['m_mean']:<10.1f} | {r['it_mean']:<10.1f} | {r['hw_mean']:<10.1f}")
        print("-" * 125)
        
    # -------------------------------------------------------------------------
    # Report 3: Topology Profile Matrix (Sparse vs Dense vs Bursty vs Alternating)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 125)
    print("TOPOLOGY PERFORMANCE MATRIX (Impact of Exponent Geometry at 2048-Bit)")
    print("=" * 125)
    df_2048 = df[df["bit_length"] == 2048]
    topo = df_2048.groupby(["profile", "mode"]).agg(
        t_mean=("time_ms", "mean"),
        m_mean=("mults", "mean"),
        it_mean=("iters", "mean")
    ).reset_index()
    
    for p_name in profiles:
        print(f"\n[PROFILE: {p_name.upper()}] (2048-Bit Scale)")
        p_sub = topo[topo["profile"] == p_name]
        p_base_t = p_sub[p_sub["mode"] == "fixed_binary"]["t_mean"].values[0]
        p_sub = p_sub.copy()
        p_sub["speedup_%"] = ((p_base_t - p_sub["t_mean"]) / p_base_t) * 100
        
        print(f"  {'Mode':<22} | {'Time (ms)':<12} | {'Speedup':<10} | {'Multiplications':<16} | {'Iterations':<12}")
        print("  " + "-" * 85)
        for _, r in p_sub.iterrows():
            print(f"  {r['mode']:<22} | {r['t_mean']:<12.3f} | {r['speedup_%']:>+7.1f}%   | {r['m_mean']:<16.1f} | {r['it_mean']:<12.1f}")

    print("\n" + "=" * 125)
    print("ALL TESTS AND ASSERTIONS VALIDATED SUCCESSFULLY!")
    print("=" * 125)

if __name__ == "__main__":
    run_deep_study(samples_per_case=10)
