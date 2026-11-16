"""
Intra-Exponent Entropy Slicing & Hybrid Execution Engine.
Partitions large exponents into localized bit-slices (e.g. 256-bit or 512-bit).
Dynamically selects the optimal algorithm per slice, sharing precomputed tables.
"""

import time
import math
from major.src.features.feature_extractor import extract_features
from major.src.strategies.mod_exp_strategies import ModExpEngine, generate_wnaf, _analytical_vlim_stride

def hybrid_sliced_mod_exp(base: int, exp: int, mod: int, slice_bits: int = 256):
    """
    Executes Intra-Exponent Slicing Modular Exponentiation.
    Accumulates slices using Horner-style bit shifting:
      R = (R^(2^k) * R_slice) % mod
    """
    start_time = time.perf_counter()
    if exp == 0:
        return {"result": 1 % mod, "metrics": {"time_ms": 0.0, "sqrs": 0, "mults": 0, "slices": 0}}
        
    total_bits = exp.bit_length()
    num_slices = (total_bits + slice_bits - 1) // slice_bits
    
    # 1. Extract slices from MSB to LSB
    slices = []
    for i in range(num_slices - 1, -1, -1):
        s_val = (exp >> (i * slice_bits)) & ((1 << slice_bits) - 1)
        slices.append((i, s_val))
        
    # 2. Shared Precomputation Table (w=3)
    # Computed once if any slice needs wNAF or VLIM
    inv_base = pow(base, -1, mod)
    base_mod = base % mod
    base_sq = (base_mod * base_mod) % mod
    inv_base_sq = (inv_base * inv_base) % mod
    precomp_table = {
        1: base_mod, -1: inv_base,
        3: (base_mod * base_sq) % mod,
        -3: (inv_base * inv_base_sq) % mod
    }
    
    total_sqrs = 0
    total_mults = 4  # Precomputation table cost
    total_iters = 0
    slice_decisions = []
    
    accumulator = 1
    first_slice = True
    
    for slice_idx, s_val in slices:
        if s_val == 0:
            slice_decisions.append({"slice_idx": slice_idx, "strategy": "ZeroSkip", "sqrs": slice_bits, "mults": 0})
            if not first_slice:
                for _ in range(slice_bits):
                    accumulator = (accumulator * accumulator) % mod
                total_sqrs += slice_bits
            continue
            
        s_bits = s_val.bit_length()
        s_hamming = s_val.bit_count()
        s_zero_density = (s_bits - s_hamming) / s_bits if s_bits > 0 else 0
        
        # Local Decision Heuristic / Model
        if s_hamming <= 3:
            strategy = "Binary"
        elif s_zero_density > 0.60:
            strategy = "VLIM"
        else:
            strategy = "wNAF"
            
        # Shift accumulator by slice_bits if not first slice
        if not first_slice:
            for _ in range(slice_bits):
                accumulator = (accumulator * accumulator) % mod
            total_sqrs += slice_bits
        first_slice = False
        
        # Execute selected strategy for this slice
        if strategy == "Binary":
            b_str = bin(s_val)[2:]
            r_slice = 1
            for b in b_str:
                r_slice = (r_slice * r_slice) % mod
                total_sqrs += 1
                if b == '1':
                    r_slice = (r_slice * base_mod) % mod
                    total_mults += 1
            total_iters += len(b_str)
            
        elif strategy == "wNAF":
            w_digits = generate_wnaf(s_val, w=3)
            w_digits.reverse()
            r_slice = 1
            for d in w_digits:
                r_slice = (r_slice * r_slice) % mod
                total_sqrs += 1
                if d != 0:
                    r_slice = (r_slice * precomp_table[d]) % mod
                    total_mults += 1
            total_iters += len(w_digits)
            
        elif strategy == "VLIM":
            digits = generate_wnaf(s_val, w=3)
            digits.reverse()
            n_d = len(digits)
            r_slice = 1
            idx = 0
            while idx < n_d:
                d = digits[idx]
                if d != 0:
                    r_slice = (r_slice * r_slice) % mod
                    total_sqrs += 1
                    r_slice = (r_slice * precomp_table[d]) % mod
                    total_mults += 1
                    idx += 1
                else:
                    run = 0
                    j = idx
                    while j < n_d and digits[j] == 0:
                        run += 1
                        j += 1
                    stride = _analytical_vlim_stride(run, 64)
                    for _ in range(stride):
                        r_slice = (r_slice * r_slice) % mod
                    total_sqrs += stride
                    idx += stride
                total_iters += 1
                
        # Multiply slice result into accumulator
        accumulator = (accumulator * r_slice) % mod
        total_mults += 1
        slice_decisions.append({"slice_idx": slice_idx, "strategy": strategy, "hamming": s_hamming, "bits": s_bits})
        
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    return {
        "result": accumulator,
        "metrics": {
            "time_ms": elapsed_ms,
            "sqrs": total_sqrs,
            "mults": total_mults,
            "iters": total_iters,
            "num_slices": num_slices,
            "slice_decisions": slice_decisions
        }
    }
