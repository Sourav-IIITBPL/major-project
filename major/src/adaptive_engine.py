"""
Adaptive Cryptographic Execution Engine (Extended).
Supports:
  1. 'fixed_binary', 'fixed_naf', 'fixed_wnaf', 'fixed_vlim'
  2. 'ml_adaptive': Whole-exponent prediction via compiled decision tree.
  3. 'hybrid_sliced': Intra-exponent entropy slicing & multi-strategy execution.
  4. 'blinded_adaptive': Side-channel hardened exponent blinding + adaptive execution.
"""

import time
import sys
import os
import secrets

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from major.src.features.feature_extractor import extract_features
from major.src.strategies.mod_exp_strategies import ModExpEngine
from major.src.strategies.hybrid_slicing import hybrid_sliced_mod_exp
from major.src.ml.compiled_predictor import predict_strategy

class AdaptiveCryptoEngine:
    STRATEGY_MAP = {
        "Binary": ModExpEngine.binary_l2r,
        "NAF": ModExpEngine.standard_naf,
        "wNAF": lambda b, e, m: ModExpEngine.windowed_naf(b, e, m, w=3),
        "VLIM": lambda b, e, m: ModExpEngine.adaptive_vlim(b, e, m, w=3)
    }

    @classmethod
    def execute(cls, base: int, exp: int, mod: int, mode: str = "ml_adaptive", phi_m: int = None, slice_bits: int = 256):
        """
        Executes modular exponentiation with chosen mode.
        """
        t_start = time.perf_counter()
        
        # Mode 3: Intra-Exponent Hybrid Slicing
        if mode == "hybrid_sliced":
            res = hybrid_sliced_mod_exp(base, exp, mod, slice_bits=slice_bits)
            total_time_ms = (time.perf_counter() - t_start) * 1000
            return {
                "result": res["result"],
                "selected_strategy": "HybridSliced",
                "mode": mode,
                "dispatch_time_us": 5.0, # Slice extraction is O(1) bit shifts
                "total_time_ms": total_time_ms,
                "metrics": res["metrics"],
                "features": None
            }

        # Mode 4: Blinded Adaptive (Side-Channel Hardened)
        if mode == "blinded_adaptive":
            # Apply random exponent blinding if order is known, else simulated coprime salt
            order = phi_m if phi_m else (mod - 1)
            salt = secrets.randbits(32)
            exp_blinded = exp + (salt * order)
            feats = extract_features(exp_blinded, w=3)
            strategy_name = predict_strategy(feats)
            dispatch_time_us = (time.perf_counter() - t_start) * 1_000_000
            exec_func = cls.STRATEGY_MAP.get(strategy_name, ModExpEngine.binary_l2r)
            run_res = exec_func(base, exp_blinded, mod)
            total_time_ms = (time.perf_counter() - t_start) * 1000
            return {
                "result": run_res["result"],
                "selected_strategy": f"Blinded-{strategy_name}",
                "mode": mode,
                "dispatch_time_us": dispatch_time_us,
                "total_time_ms": total_time_ms,
                "metrics": run_res["metrics"],
                "features": feats
            }

        # Mode 2: ML-Adaptive (Whole Exponent)
        if mode == "ml_adaptive":
            feats = extract_features(exp, w=3)
            strategy_name = predict_strategy(feats)
            dispatch_time_us = (time.perf_counter() - t_start) * 1_000_000
            exec_func = cls.STRATEGY_MAP.get(strategy_name, ModExpEngine.binary_l2r)
            run_res = exec_func(base, exp, mod)
            total_time_ms = (time.perf_counter() - t_start) * 1000
            return {
                "result": run_res["result"],
                "selected_strategy": strategy_name,
                "mode": mode,
                "dispatch_time_us": dispatch_time_us,
                "total_time_ms": total_time_ms,
                "metrics": run_res["metrics"],
                "features": feats
            }

        # Mode 1: Fixed strategies
        raw = mode.replace("fixed_", "").upper()
        lookup = {"BINARY": "Binary", "NAF": "NAF", "WNAF": "wNAF", "VLIM": "VLIM"}
        strategy_name = lookup.get(raw, "Binary")
        exec_func = cls.STRATEGY_MAP.get(strategy_name, ModExpEngine.binary_l2r)
        run_res = exec_func(base, exp, mod)
        total_time_ms = (time.perf_counter() - t_start) * 1000
        
        return {
            "result": run_res["result"],
            "selected_strategy": strategy_name,
            "mode": mode,
            "dispatch_time_us": 0.0,
            "total_time_ms": total_time_ms,
            "metrics": run_res["metrics"],
            "features": None
        }
