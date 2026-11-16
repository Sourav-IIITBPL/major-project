"""
Unified Modular Exponentiation Strategies for Major Project.
All strategies return:
  - result: (base^exp) % mod
  - metrics: dictionary with detailed operation counts and timings.
"""

import time
import math

def generate_wnaf(k: int, w: int = 3):
    """
    Generate Windowed Non-Adjacent Form (wNAF) for positive integer k.
    w=2 is standard NAF.
    """
    if k <= 0:
        return [0]
    wnaf = []
    mod = 1 << w
    mid = 1 << (w - 1)
    while k > 0:
        if k % 2 == 1:
            z = k % mod
            if z >= mid:
                z -= mod
            wnaf.append(z)
            k -= z
        else:
            wnaf.append(0)
        k //= 2
    return wnaf

def _analytical_vlim_stride(zero_run: int, max_skip: int, cost_sq=1.0, cost_ctrl=2.0, route_penalty=0.1):
    """Analytical cost model for optimal zero-run batch stride."""
    if zero_run <= 0:
        return 0
    limit = min(zero_run, max_skip)
    optimal_stride = 1
    min_cost = float('inf')
    for s in range(1, limit + 1):
        cost = (s * cost_sq) + cost_ctrl + (route_penalty * (s ** 1.5))
        cost_per_bit = cost / s
        if cost_per_bit < min_cost:
            min_cost = cost_per_bit
            optimal_stride = s
    return optimal_stride

class ModExpEngine:
    @staticmethod
    def binary_l2r(base: int, exp: int, mod: int):
        """Standard Left-to-Right Binary Exponentiation (Baseline)."""
        start = time.perf_counter()
        if exp == 0:
            return {"result": 1 % mod, "metrics": {"time_ms": 0.0, "sqrs": 0, "mults": 0, "iters": 0, "precomp_mults": 0}}
        
        bits = bin(exp)[2:]
        res = 1
        sqrs = 0
        mults = 0
        iters = 0
        
        for bit in bits:
            iters += 1
            res = (res * res) % mod
            sqrs += 1
            if bit == '1':
                res = (res * base) % mod
                mults += 1
                
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "result": res,
            "metrics": {
                "time_ms": elapsed_ms,
                "sqrs": sqrs,
                "mults": mults,
                "iters": iters,
                "precomp_mults": 0,
                "total_muls": sqrs + mults
            }
        }

    @staticmethod
    def standard_naf(base: int, exp: int, mod: int):
        """Standard Non-Adjacent Form (w=2). Digits in {-1, 0, 1}."""
        start = time.perf_counter()
        if exp == 0:
            return {"result": 1 % mod, "metrics": {"time_ms": 0.0, "sqrs": 0, "mults": 0, "iters": 0, "precomp_mults": 0}}
        
        # Precompute base and inv_base
        inv_base = pow(base, -1, mod)
        precomp = {1: base % mod, -1: inv_base}
        precomp_mults = 0  # Inversion cost tracked separately if needed
        
        naf_digits = generate_wnaf(exp, w=2)
        naf_digits.reverse()
        
        res = 1
        sqrs = 0
        mults = 0
        iters = 0
        
        for digit in naf_digits:
            iters += 1
            res = (res * res) % mod
            sqrs += 1
            if digit != 0:
                res = (res * precomp[digit]) % mod
                mults += 1
                
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "result": res,
            "metrics": {
                "time_ms": elapsed_ms,
                "sqrs": sqrs,
                "mults": mults,
                "iters": iters,
                "precomp_mults": precomp_mults,
                "total_muls": sqrs + mults + precomp_mults
            }
        }

    @staticmethod
    def windowed_naf(base: int, exp: int, mod: int, w: int = 3):
        """Windowed NAF with precomputation table for odd digits up to 2^(w-1) - 1."""
        start = time.perf_counter()
        if exp == 0:
            return {"result": 1 % mod, "metrics": {"time_ms": 0.0, "sqrs": 0, "mults": 0, "iters": 0, "precomp_mults": 0}}
            
        inv_base = pow(base, -1, mod)
        base_mod = base % mod
        base_sq = (base_mod * base_mod) % mod
        inv_base_sq = (inv_base * inv_base) % mod
        
        precomp = {1: base_mod, -1: inv_base}
        precomp_mults = 2  # base_sq and inv_base_sq
        
        max_odd = (1 << (w - 1)) - 1
        curr_pos = base_mod
        curr_neg = inv_base
        for odd in range(3, max_odd + 1, 2):
            curr_pos = (curr_pos * base_sq) % mod
            curr_neg = (curr_neg * inv_base_sq) % mod
            precomp[odd] = curr_pos
            precomp[-odd] = curr_neg
            precomp_mults += 2
            
        wnaf_digits = generate_wnaf(exp, w=w)
        wnaf_digits.reverse()
        
        res = 1
        sqrs = 0
        mults = 0
        iters = 0
        
        for digit in wnaf_digits:
            iters += 1
            res = (res * res) % mod
            sqrs += 1
            if digit != 0:
                res = (res * precomp[digit]) % mod
                mults += 1
                
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "result": res,
            "metrics": {
                "time_ms": elapsed_ms,
                "sqrs": sqrs,
                "mults": mults,
                "iters": iters,
                "precomp_mults": precomp_mults,
                "total_muls": sqrs + mults + precomp_mults
            }
        }

    @staticmethod
    def adaptive_vlim(base: int, exp: int, mod: int, w: int = 3, segment_size: int = 512):
        """
        Adaptive Info-Density VLIM:
        wNAF + Zero-Run Detection + Analytical Stride Scheduling + Segment Boundary.
        """
        start = time.perf_counter()
        if exp == 0:
            return {"result": 1 % mod, "metrics": {"time_ms": 0.0, "sqrs": 0, "mults": 0, "iters": 0, "precomp_mults": 0}}
            
        inv_base = pow(base, -1, mod)
        base_mod = base % mod
        base_sq = (base_mod * base_mod) % mod
        inv_base_sq = (inv_base * inv_base) % mod
        
        precomp = {1: base_mod, -1: inv_base}
        precomp_mults = 2
        
        max_odd = (1 << (w - 1)) - 1
        curr_pos = base_mod
        curr_neg = inv_base
        for odd in range(3, max_odd + 1, 2):
            curr_pos = (curr_pos * base_sq) % mod
            curr_neg = (curr_neg * inv_base_sq) % mod
            precomp[odd] = curr_pos
            precomp[-odd] = curr_neg
            precomp_mults += 2
            
        digits = generate_wnaf(exp, w=w)
        digits.reverse()
        n = len(digits)
        
        res = 1
        sqrs = 0
        mults = 0
        iters = 0
        ctrl_overhead = 0
        
        i = 0
        while i < n:
            iters += 1
            d = digits[i]
            
            # Segment boundary limit
            in_seg = (n - i) % segment_size
            local_max_skip = in_seg if in_seg > 0 else segment_size
            
            # Trailing zeros fast exit
            if d == 0 and all(digits[k] == 0 for k in range(i, n)):
                rem = n - i
                for _ in range(rem):
                    res = (res * res) % mod
                sqrs += rem
                break
                
            # Active non-zero digit
            if d != 0:
                res = (res * res) % mod
                sqrs += 1
                res = (res * precomp[d]) % mod
                mults += 1
                i += 1
                continue
                
            # Zero-run adaptive stride
            run_len = 0
            j = i
            while j < n and digits[j] == 0:
                run_len += 1
                j += 1
                
            stride = _analytical_vlim_stride(run_len, local_max_skip)
            ctrl_overhead += 2
            
            for _ in range(stride):
                res = (res * res) % mod
            sqrs += stride
            i += stride
            
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "result": res,
            "metrics": {
                "time_ms": elapsed_ms,
                "sqrs": sqrs,
                "mults": mults,
                "iters": iters,
                "precomp_mults": precomp_mults,
                "ctrl_overhead": ctrl_overhead,
                "total_muls": sqrs + mults + precomp_mults
            }
        }
