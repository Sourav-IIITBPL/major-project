"""
Enhancement 6: Hardware Cost Auto-Profiler
============================================
Runs micro-benchmarks on the current machine to empirically measure the
actual cost ratios between:
  - Modular Squaring   (C_sqr)
  - Modular Multiply   (C_mult)
  - Loop Control       (C_ctrl)

These measured ratios replace the hardcoded constants (1.0, 1.2, 0.15)
in the original project's compute_hw_cost() formula, making the ML model
training more accurate for the actual target hardware.

Outputs:
  - profiler/calibration_results.json  (machine-specific coefficients)
  - profiler/calibration_report.txt    (human-readable report)

Usage:
    python profiler/hardware_profiler.py [--iterations 5000]
"""

import sys
import os
import json
import time
import math
import secrets
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PROFILER_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH    = os.path.join(PROFILER_DIR, "calibration_results.json")
REPORT_PATH  = os.path.join(PROFILER_DIR, "calibration_report.txt")


# ---------------------------------------------------------------------------
# Micro-benchmark helpers
# ---------------------------------------------------------------------------

def _timeit(fn, iters: int) -> float:
    """Return mean time per call in nanoseconds."""
    # Warm-up
    for _ in range(max(10, iters // 100)):
        fn()
    # Actual measurement
    t0 = time.perf_counter_ns()
    for _ in range(iters):
        fn()
    return (time.perf_counter_ns() - t0) / iters   # ns/call


def benchmark_squaring(bit_len: int, iterations: int) -> float:
    """Benchmark a single modular squaring: R = R*R % mod."""
    mod  = secrets.randbits(bit_len) | 1
    base = secrets.randbits(bit_len) % mod
    r    = [base]  # list to avoid Python constant-folding
    return _timeit(lambda: r.__setitem__(0, (r[0] * r[0]) % mod), iterations)


def benchmark_multiply(bit_len: int, iterations: int) -> float:
    """Benchmark a single modular multiplication: R = R*A % mod."""
    mod  = secrets.randbits(bit_len) | 1
    base = secrets.randbits(bit_len) % mod
    r    = [secrets.randbits(bit_len) % mod]
    return _timeit(lambda: r.__setitem__(0, (r[0] * base) % mod), iterations)


def benchmark_loop_ctrl(iterations: int) -> float:
    """Benchmark pure Python loop-control overhead (no arithmetic)."""
    counter = [0]

    def _loop_body():
        counter[0] += 1
        if counter[0] > 0:
            pass

    return _timeit(_loop_body, iterations)


def benchmark_bit_scan(bit_len: int, iterations: int) -> float:
    """Benchmark bit-string scan (feature extractor proxy)."""
    exp = secrets.randbits(bit_len)
    bits_str = bin(exp)[2:]

    def _scan():
        _ = sum(1 for c in bits_str if c == '1')

    return _timeit(_scan, iterations)


# ---------------------------------------------------------------------------
# Full profiling run
# ---------------------------------------------------------------------------

def run_profiler(iterations: int = 5000) -> dict:
    bit_scales = [256, 512, 1024, 2048]

    print("=" * 65)
    print("  Enhancement 6 – Hardware Cost Auto-Profiler")
    print(f"  Iterations per test : {iterations:,}")
    print("=" * 65)

    results = {
        "meta": {
            "iterations": iterations,
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
        },
        "per_bit_length": {},
        "calibrated_coefficients": {},
        "summary": {},
    }

    all_sqr_ns   = []
    all_mult_ns  = []
    all_ctrl_ns  = []

    for bit_len in bit_scales:
        print(f"\n[{bit_len}-bit] Running micro-benchmarks …")

        sqr_ns  = benchmark_squaring(bit_len, iterations)
        mult_ns = benchmark_multiply(bit_len, iterations)
        ctrl_ns = benchmark_loop_ctrl(iterations)
        scan_ns = benchmark_bit_scan(bit_len, iterations)

        # Relative cost ratios (squaring = 1.0 baseline)
        ratio_mult = mult_ns / sqr_ns if sqr_ns > 0 else 1.2
        ratio_ctrl = ctrl_ns / sqr_ns if sqr_ns > 0 else 0.15

        all_sqr_ns.append(sqr_ns)
        all_mult_ns.append(mult_ns)
        all_ctrl_ns.append(ctrl_ns)

        entry = {
            "sqr_ns":    round(sqr_ns,  2),
            "mult_ns":   round(mult_ns, 2),
            "ctrl_ns":   round(ctrl_ns, 2),
            "scan_ns":   round(scan_ns, 2),
            "ratio_mult_to_sqr": round(ratio_mult, 4),
            "ratio_ctrl_to_sqr": round(ratio_ctrl, 4),
        }
        results["per_bit_length"][str(bit_len)] = entry

        print(f"  Squaring  (C_sqr)  : {sqr_ns:>8.1f} ns/op")
        print(f"  Multiply  (C_mult) : {mult_ns:>8.1f} ns/op  "
              f"(ratio = {ratio_mult:.3f}×)")
        print(f"  Loop ctrl (C_ctrl) : {ctrl_ns:>8.1f} ns/op  "
              f"(ratio = {ratio_ctrl:.3f}×)")
        print(f"  Bit scan  (feature): {scan_ns:>8.1f} ns/op")

    # ------------------------------------------------------------------
    # Aggregate calibrated coefficients (average across all bit scales)
    # ------------------------------------------------------------------
    avg_sqr_ns  = sum(all_sqr_ns)  / len(all_sqr_ns)
    avg_mult_ns = sum(all_mult_ns) / len(all_mult_ns)
    avg_ctrl_ns = sum(all_ctrl_ns) / len(all_ctrl_ns)

    cost_sqr  = 1.0
    cost_mult = round(avg_mult_ns / avg_sqr_ns, 4) if avg_sqr_ns > 0 else 1.2
    cost_ctrl = round(avg_ctrl_ns / avg_sqr_ns, 4) if avg_sqr_ns > 0 else 0.15

    results["calibrated_coefficients"] = {
        "cost_sqr":  cost_sqr,
        "cost_mult": cost_mult,
        "cost_ctrl": cost_ctrl,
        "description": (
            "hw_cost = sqrs*cost_sqr + mults*cost_mult "
            "+ precomp_mults*cost_mult + iters*cost_ctrl"
        ),
    }

    # ------------------------------------------------------------------
    # Comparison vs. original hardcoded values
    # ------------------------------------------------------------------
    orig = {"cost_sqr": 1.0, "cost_mult": 1.2, "cost_ctrl": 0.15}
    results["summary"] = {
        "original_hardcoded": orig,
        "measured_on_this_machine": results["calibrated_coefficients"],
        "mult_ratio_change_pct": round(
            (cost_mult - 1.2) / 1.2 * 100, 2
        ),
        "ctrl_ratio_change_pct": round(
            (cost_ctrl - 0.15) / 0.15 * 100, 2
        ),
    }

    print("\n" + "=" * 65)
    print("  Calibration Results")
    print("=" * 65)
    print(f"  Hardcoded (original) : sqr=1.0 | mult=1.20 | ctrl=0.150")
    print(f"  Measured  (this CPU) : sqr=1.0 | mult={cost_mult:.3f} | ctrl={cost_ctrl:.3f}")
    print(f"  Multiply ratio shift : {results['summary']['mult_ratio_change_pct']:+.1f}%")
    print(f"  Ctrl    ratio shift  : {results['summary']['ctrl_ratio_change_pct']:+.1f}%")

    return results


# ---------------------------------------------------------------------------
# Save outputs
# ---------------------------------------------------------------------------

def save_results(results: dict):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n  → JSON saved  : {JSON_PATH}")

    # Human-readable text report
    coeff = results["calibrated_coefficients"]
    report_lines = [
        "Hardware Cost Auto-Profiler – Calibration Report",
        "=" * 65,
        f"Python     : {results['meta']['python_version']}",
        f"Platform   : {results['meta']['platform']}",
        f"Iterations : {results['meta']['iterations']:,}",
        "",
        "Calibrated Cost Coefficients (use these in generate_dataset.py):",
        f"  cost_sqr  = {coeff['cost_sqr']}",
        f"  cost_mult = {coeff['cost_mult']}",
        f"  cost_ctrl = {coeff['cost_ctrl']}",
        "",
        "Per Bit-Length Results:",
    ]
    for bl, entry in results["per_bit_length"].items():
        report_lines.append(
            f"  {bl:>5}-bit: sqr={entry['sqr_ns']:.1f}ns  "
            f"mult={entry['mult_ns']:.1f}ns  "
            f"ctrl={entry['ctrl_ns']:.1f}ns  "
            f"(mult/sqr={entry['ratio_mult_to_sqr']:.3f}, "
            f"ctrl/sqr={entry['ratio_ctrl_to_sqr']:.3f})"
        )
    report_lines += [
        "",
        "compute_hw_cost formula:",
        f"  {coeff['description']}",
    ]

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  → Report saved: {REPORT_PATH}")


def load_calibration() -> dict:
    """
    Load the calibrated coefficients from the saved JSON.
    Returns default values if the file does not exist yet.
    """
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["calibrated_coefficients"]
    # Fallback: original hardcoded values
    return {"cost_sqr": 1.0, "cost_mult": 1.2, "cost_ctrl": 0.15}


def compute_hw_cost_calibrated(m: dict, coeffs: dict = None) -> float:
    """
    Drop-in replacement for major.src.ml.generate_dataset.compute_hw_cost()
    that uses machine-specific calibrated coefficients.
    """
    if coeffs is None:
        coeffs = load_calibration()
    return (
        m["sqrs"]  * coeffs["cost_sqr"]
        + m["mults"] * coeffs["cost_mult"]
        + m.get("precomp_mults", 0) * coeffs["cost_mult"]
        + m["iters"] * coeffs["cost_ctrl"]
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Profile hardware cost ratios for the ML-Assisted Crypto Engine."
    )
    parser.add_argument(
        "--iterations", type=int, default=5000,
        help="Number of timing iterations per micro-benchmark (default: 5000)."
    )
    args = parser.parse_args()

    results = run_profiler(iterations=args.iterations)
    save_results(results)
    print("\n  Enhancement 6 complete – calibration data ready.")
