"""
Enhancement 7: Cross-Architecture Backend Configuration
=========================================================
Defines hardware cost coefficients for 4 real-world computational backends.
Used by train_per_backend.py to train one model per backend target.
"""

# Each backend: (C_sqr, C_mult, C_ctrl)
# C_sqr  = cost per modular squaring          (normalized baseline = 1.0)
# C_mult = cost per modular multiplication    (relative to squaring)
# C_ctrl = cost per loop control transition   (relative to squaring)

BACKEND_CONFIGS = {
    "python_bigint": {
        "cost_sqr":  1.0,
        "cost_mult": 1.2,
        "cost_ctrl": 2.0,
        "description": (
            "Pure CPython BigInt arithmetic. Loop dispatch bytecode is relatively "
            "expensive (C_ctrl high). Multiplication slightly heavier than squaring."
        ),
    },
    "c_montgomery": {
        "cost_sqr":  1.0,
        "cost_mult": 2.5,
        "cost_ctrl": 0.5,
        "description": (
            "C-level Montgomery Radix-2 multiplier. Multiplication latency is 2.5× "
            "squaring (Montgomery reduction overhead). Loop control is fast (C loop)."
        ),
    },
    "fpga_radix4": {
        "cost_sqr":  1.0,
        "cost_mult": 4.0,
        "cost_ctrl": 0.1,
        "description": (
            "FPGA Radix-4 CSA multiplier pipeline. Multiplication is 4× squaring "
            "(full 4-word carry-save accumulation). FSM transitions are near-free "
            "(single clock edge). VLIM zero-skipping dominates here."
        ),
    },
    "asic_csa52": {
        "cost_sqr":  1.0,
        "cost_mult": 5.0,
        "cost_ctrl": 0.05,
        "description": (
            "ASIC Carry-Save Adder (52-bit word) Montgomery multiplier. Multiply is "
            "5× squaring. FSM clock transitions nearly free. VLIM provides maximum "
            "energy and latency savings."
        ),
    },
}

DEFAULT_BACKEND = "python_bigint"
ALL_BACKEND_NAMES = list(BACKEND_CONFIGS.keys())


def get_backend(name: str) -> dict:
    if name not in BACKEND_CONFIGS:
        raise ValueError(
            f"Unknown backend '{name}'. "
            f"Choose from: {ALL_BACKEND_NAMES}"
        )
    return BACKEND_CONFIGS[name]


def compute_hw_cost_backend(m: dict, backend_name: str) -> float:
    """
    Compute hardware cost using backend-specific coefficients.

    hw_cost = sqrs * C_sqr
            + mults * C_mult
            + precomp_mults * C_mult
            + iters * C_ctrl
    """
    cfg = get_backend(backend_name)
    return (
        m["sqrs"]                * cfg["cost_sqr"]
        + m["mults"]             * cfg["cost_mult"]
        + m.get("precomp_mults", 0) * cfg["cost_mult"]
        + m["iters"]             * cfg["cost_ctrl"]
    )


if __name__ == "__main__":
    print("Available Backend Configurations:")
    print("=" * 70)
    for name, cfg in BACKEND_CONFIGS.items():
        print(f"\n  [{name}]")
        print(f"    C_sqr  = {cfg['cost_sqr']}")
        print(f"    C_mult = {cfg['cost_mult']}")
        print(f"    C_ctrl = {cfg['cost_ctrl']}")
        print(f"    {cfg['description']}")
