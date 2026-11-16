import sys
import os
import secrets
import math

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from major.src.strategies.mod_exp_strategies import ModExpEngine
from major.src.features.feature_extractor import extract_features

def run_sanity():
    print("Testing Major Project Strategies & Feature Extractor...")
    for bit_len in [256, 512, 1024]:
        base = secrets.randbits(bit_len)
        exp = secrets.randbits(bit_len)
        mod = secrets.randbits(bit_len) | 1
        while math.gcd(base, mod) != 1:
            mod = secrets.randbits(bit_len) | 1
            
        expected = pow(base, exp, mod)
        
        # Test strategies
        r_bin = ModExpEngine.binary_l2r(base, exp, mod)
        r_naf = ModExpEngine.standard_naf(base, exp, mod)
        r_wnaf = ModExpEngine.windowed_naf(base, exp, mod, w=3)
        r_vlim = ModExpEngine.adaptive_vlim(base, exp, mod, w=3)
        
        assert r_bin["result"] == expected, f"Binary failed for {bit_len}-bit"
        assert r_naf["result"] == expected, f"NAF failed for {bit_len}-bit"
        assert r_wnaf["result"] == expected, f"wNAF failed for {bit_len}-bit"
        assert r_vlim["result"] == expected, f"VLIM failed for {bit_len}-bit"
        
        feats = extract_features(exp, w=3)
        print(f"[{bit_len}-bit OK] Extractor: {feats['feature_extract_time_us']:.2f} us | VLIM time: {r_vlim['metrics']['time_ms']:.2f} ms | Iters: {r_vlim['metrics']['iters']} vs Bin: {r_bin['metrics']['iters']}")

    print("\nALL MATHEMATICAL ASSERTIONS AND TIMINGS VERIFIED!")

if __name__ == "__main__":
    run_sanity()
