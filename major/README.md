# ML-Assisted Adaptive Cryptographic Engine

A complete, standalone research framework for workload-aware modular exponentiation ($A^B \pmod M$) acceleration.

---

## Quick Start (Standalone Execution)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Mathematical Correctness:**
   ```bash
   python test_sanity.py
   ```

3. **Run Multi-Scale Benchmark (256-bit to 2048-bit):**
   ```bash
   python benchmarks/evaluate_all.py
   ```

4. **Run Statistical Comparative Study (1,400 runs across topologies):**
   ```bash
   python benchmarks/deep_comparative_study.py
   ```

5. **Generate Presentation Figures:**
   ```bash
   python benchmarks/plot_results.py
   ```
   *(Charts saved to `docs/figures/`)*

---

## Project Structure

```
major/
├── requirements.txt                 <- Environment dependencies
├── test_sanity.py                   <- Mathematical verification against pow()
├── test_innovations.py              <- Verification for Slicing & Exponent Blinding
├── src/
│   ├── strategies/
│   │   ├── mod_exp_strategies.py    <- Binary, NAF, wNAF, and Adaptive VLIM engines
│   │   ├── hybrid_slicing.py        <- Intra-Exponent 256-bit entropy slicing
│   │   └── addition_chain_mcts.py   <- AlphaExponent beam search addition chain optimizer
│   ├── features/
│   │   └── feature_extractor.py     <- Ultra-fast single-pass O(N) bitwise feature extractor
│   ├── ml/
│   │   ├── generate_dataset.py      <- Multi-topology dataset generator with true primes
│   │   ├── train_model.py           <- Decision Tree & Random Forest training pipeline
│   │   ├── compiled_predictor.py    <- Zero-overhead static decision code (< 1 µs)
│   │   └── crypto_dispatch.h        <- Static C99 dispatch header (< 15 ns)
│   ├── crypto_utils.py              <- Miller-Rabin probabilistic prime generator
│   └── adaptive_engine.py           <- Master runtime dispatch engine
├── benchmarks/
│   ├── evaluate_all.py              <- Multi-scale benchmark suite (256 to 2048 bits)
│   ├── deep_comparative_study.py    <- 1,400-run deep topology benchmark
│   └── plot_results.py              <- High-resolution chart generator
├── data/
│   ├── dataset.csv                  <- 640 training workloads
│   ├── deep_comparative_results.csv <- 1,400-run comprehensive study dataset
│   ├── model_dt.joblib              <- Serialized Decision Tree
│   └── model_rf.joblib              <- Serialized Random Forest
└── docs/
    ├── figures/                     <- Publication-grade 300-DPI charts
    ├── PROJECT_PLAN.md              <- Phase-by-phase execution plan & roadmap
    ├── INNOVATIONS_AND_IMPROVEMENTS.md <- Live running log of all breakthroughs
    └── COMPREHENSIVE_TECHNICAL_SPECIFICATION.md <- Master thesis document & mentor defense
```
