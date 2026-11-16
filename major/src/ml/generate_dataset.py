"""
Dataset Generator for ML Strategy Prediction.
Generates diverse exponents (uniform, sparse, dense, bursty) across bit-lengths.
Calculates both software wall-clock time and standard hardware-cycle cost models.
"""

import sys
import os
import csv
import math
import random
import secrets
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from major.src.strategies.mod_exp_strategies import ModExpEngine
from major.src.features.feature_extractor import extract_features

def generate_custom_exponent(bit_length: int, profile: str) -> int:
    if profile == "uniform":
        return secrets.randbits(bit_length) | 1
        
    elif profile == "sparse":
        num_ones = max(2, int(bit_length * random.uniform(0.02, 0.15)))
        positions = random.sample(range(1, bit_length - 1), num_ones)
        val = (1 << (bit_length - 1)) | 1
        for pos in positions:
            val |= (1 << pos)
        return val
        
    elif profile == "dense":
        num_zeros = max(2, int(bit_length * random.uniform(0.02, 0.15)))
        positions = random.sample(range(1, bit_length - 1), num_zeros)
        val = (1 << bit_length) - 1
        for pos in positions:
            val &= ~(1 << pos)
        return val
        
    elif profile == "bursty":
        bits = []
        cur_bit = '1'
        while len(bits) < bit_length:
            run = random.randint(8, 64)
            bits.extend([cur_bit] * min(run, bit_length - len(bits)))
            cur_bit = '0' if cur_bit == '1' else '1'
        return int("".join(bits), 2)
        
    return secrets.randbits(bit_length) | 1

def compute_hw_cost(m: dict) -> float:
    """Hardware cost: (Sqrs * 1.0) + (Mults * 1.2) + (Iters * 0.15) + Precomputations."""
    return (m["sqrs"] * 1.0) + (m["mults"] * 1.2) + (m.get("precomp_mults", 0) * 1.2) + (m["iters"] * 0.15)

def generate_dataset(num_samples_per_config: int = 50, output_path: str = "major/data/dataset.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bit_lengths = [256, 512, 1024, 2048]
    profiles = ["uniform", "sparse", "dense", "bursty"]
    
    fieldnames = [
        "sample_id", "profile", "bit_length", "hamming_weight", "zero_density",
        "longest_zero_run", "avg_zero_run", "longest_one_run", "trailing_zeros",
        "wnaf_weight", "wnaf_zero_density", "longest_wnaf_zero_run",
        "feature_extract_time_us",
        # Strategy Metrics
        "bin_time_ms", "bin_iters", "bin_total_muls", "bin_hw_cost",
        "naf_time_ms", "naf_iters", "naf_total_muls", "naf_hw_cost",
        "wnaf_time_ms", "wnaf_iters", "wnaf_total_muls", "wnaf_hw_cost",
        "vlim_time_ms", "vlim_iters", "vlim_total_muls", "vlim_hw_cost",
        # Target Labels
        "label_fastest_time", "label_fewest_iters", "label_lowest_hw_cost"
    ]
    
    sample_id = 0
    total_runs = len(bit_lengths) * len(profiles) * num_samples_per_config
    print(f"Generating dataset: {total_runs} samples across bit-lengths {bit_lengths} -> {output_path}")
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for bit_len in bit_lengths:
            mod = secrets.randbits(bit_len) | 1
            base = secrets.randbits(bit_len) % mod
            while math.gcd(base, mod) != 1:
                mod = secrets.randbits(bit_len) | 1
                base = secrets.randbits(bit_len) % mod
                
            for prof in profiles:
                for _ in range(num_samples_per_config):
                    sample_id += 1
                    exp = generate_custom_exponent(bit_len, prof)
                    
                    feats = extract_features(exp, w=3)
                    
                    r_bin = ModExpEngine.binary_l2r(base, exp, mod)
                    r_naf = ModExpEngine.standard_naf(base, exp, mod)
                    r_wnaf = ModExpEngine.windowed_naf(base, exp, mod, w=3)
                    r_vlim = ModExpEngine.adaptive_vlim(base, exp, mod, w=3)
                    
                    cost_bin = compute_hw_cost(r_bin["metrics"])
                    cost_naf = compute_hw_cost(r_naf["metrics"])
                    cost_wnaf = compute_hw_cost(r_wnaf["metrics"])
                    cost_vlim = compute_hw_cost(r_vlim["metrics"])
                    
                    times = {
                        "Binary": r_bin["metrics"]["time_ms"],
                        "NAF": r_naf["metrics"]["time_ms"],
                        "wNAF": r_wnaf["metrics"]["time_ms"],
                        "VLIM": r_vlim["metrics"]["time_ms"]
                    }
                    iters = {
                        "Binary": r_bin["metrics"]["iters"],
                        "NAF": r_naf["metrics"]["iters"],
                        "wNAF": r_wnaf["metrics"]["iters"],
                        "VLIM": r_vlim["metrics"]["iters"]
                    }
                    costs = {
                        "Binary": cost_bin,
                        "NAF": cost_naf,
                        "wNAF": cost_wnaf,
                        "VLIM": cost_vlim
                    }
                    
                    best_time = min(times, key=times.get)
                    best_iters = min(iters, key=iters.get)
                    best_cost = min(costs, key=costs.get)
                    
                    row = {
                        "sample_id": sample_id,
                        "profile": prof,
                        "bit_length": feats["bit_length"],
                        "hamming_weight": feats["hamming_weight"],
                        "zero_density": round(feats["zero_density"], 4),
                        "longest_zero_run": feats["longest_zero_run"],
                        "avg_zero_run": round(feats["avg_zero_run"], 4),
                        "longest_one_run": feats["longest_one_run"],
                        "trailing_zeros": feats["trailing_zeros"],
                        "wnaf_weight": feats["wnaf_weight"],
                        "wnaf_zero_density": round(feats["wnaf_zero_density"], 4),
                        "longest_wnaf_zero_run": feats["longest_wnaf_zero_run"],
                        "feature_extract_time_us": round(feats["feature_extract_time_us"], 2),
                        
                        "bin_time_ms": round(r_bin["metrics"]["time_ms"], 4),
                        "bin_iters": r_bin["metrics"]["iters"],
                        "bin_total_muls": r_bin["metrics"]["total_muls"],
                        "bin_hw_cost": round(cost_bin, 2),
                        
                        "naf_time_ms": round(r_naf["metrics"]["time_ms"], 4),
                        "naf_iters": r_naf["metrics"]["iters"],
                        "naf_total_muls": r_naf["metrics"]["total_muls"],
                        "naf_hw_cost": round(cost_naf, 2),
                        
                        "wnaf_time_ms": round(r_wnaf["metrics"]["time_ms"], 4),
                        "wnaf_iters": r_wnaf["metrics"]["iters"],
                        "wnaf_total_muls": r_wnaf["metrics"]["total_muls"],
                        "wnaf_hw_cost": round(cost_wnaf, 2),
                        
                        "vlim_time_ms": round(r_vlim["metrics"]["time_ms"], 4),
                        "vlim_iters": r_vlim["metrics"]["iters"],
                        "vlim_total_muls": r_vlim["metrics"]["total_muls"],
                        "vlim_hw_cost": round(cost_vlim, 2),
                        
                        "label_fastest_time": best_time,
                        "label_fewest_iters": best_iters,
                        "label_lowest_hw_cost": best_cost
                    }
                    writer.writerow(row)
                    
                    if sample_id % 100 == 0 or sample_id == total_runs:
                        print(f"Progress: {sample_id}/{total_runs} samples...")

    print(f"Dataset generation complete: {output_path}")

if __name__ == "__main__":
    generate_dataset(num_samples_per_config=40)
