"""
Ultra-Fast Exponent Feature Extractor.
Extracts structural features in O(N) single-pass.
"""

import time

def extract_features(exp: int, w: int = 3) -> dict:
    start = time.perf_counter_ns()
    
    bit_length = exp.bit_length()
    if bit_length == 0:
        return {
            "bit_length": 0, "hamming_weight": 0, "zero_density": 0.0,
            "longest_zero_run": 0, "avg_zero_run": 0.0, "longest_one_run": 0,
            "trailing_zeros": 0, "wnaf_weight": 0, "wnaf_zero_density": 0.0,
            "longest_wnaf_zero_run": 0, "feature_extract_time_us": 0.0
        }
    
    # 1. Native CPU popcount
    hamming_weight = exp.bit_count()
    zero_count = bit_length - hamming_weight
    zero_density = zero_count / bit_length
    
    # 2. Fast trailing zeros
    trailing_zeros = (exp & -exp).bit_length() - 1 if exp > 0 else 0
    
    # 3. Fast binary runs scan
    b_str = bin(exp)[2:]
    max_zero_run = 0
    max_one_run = 0
    zero_run_count = 0
    zero_run_sum = 0
    
    cur_char = b_str[0]
    cur_len = 0
    for ch in b_str:
        if ch == cur_char:
            cur_len += 1
        else:
            if cur_char == '0':
                zero_run_count += 1
                zero_run_sum += cur_len
                if cur_len > max_zero_run:
                    max_zero_run = cur_len
            else:
                if cur_len > max_one_run:
                    max_one_run = cur_len
            cur_char = ch
            cur_len = 1
            
    if cur_char == '0':
        zero_run_count += 1
        zero_run_sum += cur_len
        if cur_len > max_zero_run:
            max_zero_run = cur_len
    else:
        if cur_len > max_one_run:
            max_one_run = cur_len
            
    avg_zero_run = (zero_run_sum / zero_run_count) if zero_run_count > 0 else 0.0
    
    # 4. Streamlined wNAF scan (no extra list copies)
    mod = 1 << w
    mid = 1 << (w - 1)
    k = exp
    wnaf_len = 0
    wnaf_nonzero = 0
    max_wnaf_zero_run = 0
    cur_w_zero_run = 0
    
    while k > 0:
        wnaf_len += 1
        if k & 1:
            z = k & (mod - 1)
            if z >= mid:
                z -= mod
            wnaf_nonzero += 1
            cur_w_zero_run = 0
            k -= z
        else:
            cur_w_zero_run += 1
            if cur_w_zero_run > max_wnaf_zero_run:
                max_wnaf_zero_run = cur_w_zero_run
        k >>= 1
        
    wnaf_zero_density = (wnaf_len - wnaf_nonzero) / wnaf_len if wnaf_len > 0 else 0.0
    extract_time_us = (time.perf_counter_ns() - start) / 1000.0
    
    return {
        "bit_length": bit_length,
        "hamming_weight": hamming_weight,
        "zero_density": zero_density,
        "longest_zero_run": max_zero_run,
        "avg_zero_run": avg_zero_run,
        "longest_one_run": max_one_run,
        "trailing_zeros": trailing_zeros,
        "wnaf_weight": wnaf_nonzero,
        "wnaf_zero_density": wnaf_zero_density,
        "longest_wnaf_zero_run": max_wnaf_zero_run,
        "feature_extract_time_us": extract_time_us
    }
