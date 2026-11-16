"""
Enhancement 1: Extended Multi-Profile Dataset Generator
========================================================
Extends the original dataset with:
  - 4096-bit scale (real-world RSA-4096)
  - 'alternating' profile (worst-case 101010... pattern)
  - 'ecc_random'   profile (256-bit / 384-bit ECC scalar multiplications)
  - 5000+ samples  (100 samples per configuration)
Saves to: enhanced_dataset/data/dataset_extended.csv
"""

import sys
import os
import csv
import math
import random
import secrets
import time

# ---------------------------------------------------------------------------
# Root path so we can import the core major package
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from major.src.strategies.mod_exp_strategies import ModExpEngine
from major.src.features.feature_extractor import extract_features

# ---------------------------------------------------------------------------
# Exponent profile generators
# ---------------------------------------------------------------------------

def gen_uniform(bit_length: int) -> int:
    """Standard cryptographic random key."""
    return secrets.randbits(bit_length) | (1 << (bit_length - 1)) | 1


def gen_sparse(bit_length: int) -> int:
    """Low Hamming weight (2%-15% ones)."""
    num_ones = max(2, int(bit_length * random.uniform(0.02, 0.15)))
    positions = random.sample(range(1, bit_length - 1), min(num_ones, bit_length - 2))
    val = (1 << (bit_length - 1)) | 1
    for pos in positions:
        val |= (1 << pos)
    return val


def gen_dense(bit_length: int) -> int:
    """High Hamming weight (85%-98% ones)."""
    num_zeros = max(2, int(bit_length * random.uniform(0.02, 0.15)))
    positions = random.sample(range(1, bit_length - 1), min(num_zeros, bit_length - 2))
    val = (1 << bit_length) - 1
    for pos in positions:
        val &= ~(1 << pos)
    return val | 1


def gen_bursty(bit_length: int) -> int:
    """Alternating clustered runs of 0s and 1s (8-64 bits each)."""
    bits = []
    cur_bit = '1'
    while len(bits) < bit_length:
        run = random.randint(8, 64)
        bits.extend([cur_bit] * min(run, bit_length - len(bits)))
        cur_bit = '0' if cur_bit == '1' else '1'
    val = int("".join(bits), 2)
    return val | 1


def gen_alternating(bit_length: int) -> int:
    """Worst-case 101010... pattern for wNAF."""
    val = 0
    for i in range(bit_length):
        if i % 2 == 0:
            val |= (1 << i)
    return val


def gen_ecc_random(bit_length: int) -> int:
    """
    ECC-style scalar: typically a full-width random integer (256/384-bit).
    Resamples at the given bit_length regardless (project stretches this up
    to 1024-bit to keep timings comparable).
    """
    return secrets.randbits(bit_length) | (1 << (bit_length - 1)) | 1


PROFILE_GENERATORS = {
    "uniform":     gen_uniform,
    "sparse":      gen_sparse,
    "dense":       gen_dense,
    "bursty":      gen_bursty,
    "alternating": gen_alternating,
    "ecc_random":  gen_ecc_random,
}

# ---------------------------------------------------------------------------
# Hardware cost model (identical to original project)
# ---------------------------------------------------------------------------

def compute_hw_cost(m: dict) -> float:
    return (
        m["sqrs"] * 1.0
        + m["mults"] * 1.2
        + m.get("precomp_mults", 0) * 1.2
        + m["iters"] * 0.15
    )

# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------

def generate_extended_dataset(
    num_samples_per_config: int = 100,
    output_path: str = None,
):
    if output_path is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "dataset_extended.csv")

    bit_lengths = [256, 512, 1024, 2048, 4096]
    profiles    = list(PROFILE_GENERATORS.keys())          # 6 profiles

    fieldnames = [
        "sample_id", "profile", "bit_length",
        "hamming_weight", "zero_density",
        "longest_zero_run", "avg_zero_run", "longest_one_run",
        "trailing_zeros", "wnaf_weight", "wnaf_zero_density",
        "longest_wnaf_zero_run", "feature_extract_time_us",
        # Per-strategy metrics
        "bin_time_ms",  "bin_iters",  "bin_total_muls",  "bin_hw_cost",
        "naf_time_ms",  "naf_iters",  "naf_total_muls",  "naf_hw_cost",
        "wnaf_time_ms", "wnaf_iters", "wnaf_total_muls", "wnaf_hw_cost",
        "vlim_time_ms", "vlim_iters", "vlim_total_muls", "vlim_hw_cost",
        # Labels
        "label_fastest_time", "label_fewest_iters", "label_lowest_hw_cost",
    ]

    total_runs = len(bit_lengths) * len(profiles) * num_samples_per_config
    print("=" * 70)
    print("Enhancement 1: Extended Multi-Profile Dataset Generation")
    print(f"  Bit-lengths   : {bit_lengths}")
    print(f"  Profiles      : {profiles}")
    print(f"  Samples/config: {num_samples_per_config}")
    print(f"  Total samples : {total_runs}")
    print(f"  Output        : {output_path}")
    print("=" * 70)

    sample_id = 0
    t_global_start = time.time()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for bit_len in bit_lengths:
            # Generate a fresh RSA-style modulus for this scale
            mod  = secrets.randbits(bit_len) | 1
            base = secrets.randbits(bit_len) % mod
            while math.gcd(base, mod) != 1:
                mod  = secrets.randbits(bit_len) | 1
                base = secrets.randbits(bit_len) % mod

            print(f"\n[{bit_len}-bit] Running {len(profiles) * num_samples_per_config} samples …")

            for prof in profiles:
                gen_fn = PROFILE_GENERATORS[prof]
                for _ in range(num_samples_per_config):
                    sample_id += 1
                    exp = gen_fn(bit_len)

                    feats  = extract_features(exp, w=3)
                    r_bin  = ModExpEngine.binary_l2r(base, exp, mod)
                    r_naf  = ModExpEngine.standard_naf(base, exp, mod)
                    r_wnaf = ModExpEngine.windowed_naf(base, exp, mod, w=3)
                    r_vlim = ModExpEngine.adaptive_vlim(base, exp, mod, w=3)

                    cost_bin  = compute_hw_cost(r_bin["metrics"])
                    cost_naf  = compute_hw_cost(r_naf["metrics"])
                    cost_wnaf = compute_hw_cost(r_wnaf["metrics"])
                    cost_vlim = compute_hw_cost(r_vlim["metrics"])

                    times = {
                        "Binary": r_bin["metrics"]["time_ms"],
                        "NAF":    r_naf["metrics"]["time_ms"],
                        "wNAF":   r_wnaf["metrics"]["time_ms"],
                        "VLIM":   r_vlim["metrics"]["time_ms"],
                    }
                    iters = {
                        "Binary": r_bin["metrics"]["iters"],
                        "NAF":    r_naf["metrics"]["iters"],
                        "wNAF":   r_wnaf["metrics"]["iters"],
                        "VLIM":   r_vlim["metrics"]["iters"],
                    }
                    costs = {
                        "Binary": cost_bin,
                        "NAF":    cost_naf,
                        "wNAF":   cost_wnaf,
                        "VLIM":   cost_vlim,
                    }

                    writer.writerow({
                        "sample_id":   sample_id,
                        "profile":     prof,
                        "bit_length":  feats["bit_length"],
                        "hamming_weight":       feats["hamming_weight"],
                        "zero_density":         round(feats["zero_density"], 4),
                        "longest_zero_run":     feats["longest_zero_run"],
                        "avg_zero_run":         round(feats["avg_zero_run"], 4),
                        "longest_one_run":      feats["longest_one_run"],
                        "trailing_zeros":       feats["trailing_zeros"],
                        "wnaf_weight":          feats["wnaf_weight"],
                        "wnaf_zero_density":    round(feats["wnaf_zero_density"], 4),
                        "longest_wnaf_zero_run":feats["longest_wnaf_zero_run"],
                        "feature_extract_time_us": round(feats["feature_extract_time_us"], 2),

                        "bin_time_ms":   round(r_bin["metrics"]["time_ms"], 4),
                        "bin_iters":     r_bin["metrics"]["iters"],
                        "bin_total_muls":r_bin["metrics"]["total_muls"],
                        "bin_hw_cost":   round(cost_bin, 2),

                        "naf_time_ms":   round(r_naf["metrics"]["time_ms"], 4),
                        "naf_iters":     r_naf["metrics"]["iters"],
                        "naf_total_muls":r_naf["metrics"]["total_muls"],
                        "naf_hw_cost":   round(cost_naf, 2),

                        "wnaf_time_ms":   round(r_wnaf["metrics"]["time_ms"], 4),
                        "wnaf_iters":     r_wnaf["metrics"]["iters"],
                        "wnaf_total_muls":r_wnaf["metrics"]["total_muls"],
                        "wnaf_hw_cost":   round(cost_wnaf, 2),

                        "vlim_time_ms":   round(r_vlim["metrics"]["time_ms"], 4),
                        "vlim_iters":     r_vlim["metrics"]["iters"],
                        "vlim_total_muls":r_vlim["metrics"]["total_muls"],
                        "vlim_hw_cost":   round(cost_vlim, 2),

                        "label_fastest_time":  min(times,  key=times.get),
                        "label_fewest_iters":  min(iters,  key=iters.get),
                        "label_lowest_hw_cost":min(costs,  key=costs.get),
                    })

                    if sample_id % 500 == 0 or sample_id == total_runs:
                        elapsed = time.time() - t_global_start
                        print(f"  Progress: {sample_id}/{total_runs} samples  "
                              f"({elapsed:.0f}s elapsed)")

    print(f"\nDataset saved  → {output_path}")
    print(f"Total rows     : {sample_id}")
    print(f"Time taken     : {time.time() - t_global_start:.1f}s")
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate extended cryptographic dataset.")
    parser.add_argument("--samples", type=int, default=25, help="Samples per configuration (default: 25)")
    args = parser.parse_args()
    generate_extended_dataset(num_samples_per_config=args.samples)
