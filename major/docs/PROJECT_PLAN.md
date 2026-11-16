# Major Project: ML-Assisted Adaptive Cryptographic Engine

## 1. Executive Summary & Research Question
* **Research Question**: *"Can machine learning accurately predict optimal modular exponentiation strategies from exponent morphology and target backend characteristics, enabling low-overhead workload-aware cryptographic acceleration?"*
* **Core Paradigm**: The ML model does **not** compute cryptographic results. It acts as an intelligent runtime dispatch layer (like an automatic transmission) that evaluates exponent structural features in $O(\text{bits})$ time and routes computation to the most efficient exponentiation strategy (Binary, NAF, wNAF, VLIM, or Fixed-Window).

---

## 2. Critical Crypto Defense & Mentor FAQ

### Trap 1: Side-Channel / Timing Attacks (Constant-Time Violation)
* **Risk**: In private-key RSA / ECC, variable execution time leaks private key bits.
* **Defense**: 
  1. Scope explicitly targets **public-key operations** (RSA signature verification with public $e$, certificate chains, client-side handshake verification) where timing leakage is harmless because $e$ is public.
  2. Server batch workloads: high-throughput TLS / PKI verification microservices processing millions of incoming public exponents.

### Trap 2: ML Inference Overhead vs. Exponentiation Latency
* **Risk**: If feature extraction + inference takes 0.1 ms, but 256-bit exponentiation takes 0.4 ms, ML overhead destroys performance gains.
* **Defense**:
  1. Primary target is **1024-bit, 2048-bit, and 4096-bit** cryptographic workloads (where exponentiation takes 10 ms to 100+ ms; a 5 µs decision tree inference is $< 0.05\%$ overhead).
  2. Features engineered using fast bitwise operations ($O(N)$ single-pass scan or hardware popcount).
  3. Pre-trained Decision Tree / Random Forest compiled into static C/Python `if-else` decision graphs (inference in $< 2\,\mu\text{s}$).

### Trap 3: Why ML Instead of a Hardcoded Rule (`if zeros > 60%`)?
* **Risk**: Mentor asks: "Why not write a 3-line heuristic?"
* **Defense**:
  1. **Cross-Architecture Divergence**: Crossover thresholds shift drastically across execution backends (pure Python vs C Montgomery vs FPGA Radix-2 vs Radix-4 vs CSA).
  2. **Multi-Feature Interaction**: Winner is not determined by zero-count alone, but non-linear interplay of: (Zero run length distribution) × (Hamming weight) × (Window precomputation cost) × (Multiplier latency ratio $C_{mult} / C_{sqr}$).
  3. ML captures non-linear multidimensional decision boundaries without manual tuning per hardware target.

---

## 3. System Architecture

```text
                  Inputs: Base (A), Exponent (B), Modulus (M), Target Backend
                                         │
                                         ▼
                            ┌────────────────────────┐
                            │ Fast Feature Extractor │ (Single pass O(N) bitwise)
                            └────────────┬───────────┘
                                         │ Features Vector
                                         ▼
                            ┌────────────────────────┐
                            │ Lightweight ML Model   │ (Decision Tree / Random Forest)
                            └────────────┬───────────┘
                                         │ Predicted Optimal Strategy
                                         ▼
                      ┌──────────────────┴──────────────────┐
                      ▼                  ▼                  ▼
             ┌─────────────────┐ ┌───────────────┐ ┌────────────────┐
             │   Binary L-to-R │ │  wNAF (w=3/4) │ │  Adaptive VLIM │
             └────────┬────────┘ └───────┬───────┘ └────────┬───────┘
                      └──────────────────┬──────────────────┘
                                         ▼
                            ┌────────────────────────┐
                            │ Target Hardware Engine │ (Python / C / Simulated HW)
                            └────────────┬───────────┘
                                         ▼
                                   Result A^B mod M
```

---

## 4. Phase-by-Phase Execution Roadmap (4–5 Weeks)

| Phase | Duration | Milestones |
| :--- | :--- | :--- |
| **Phase 1: Unified Strategy Framework** | Days 1–4 | Unify Binary, NAF, wNAF ($w=3,4,5$), and Adaptive VLIM into single modular interface in `major/src/strategies/`. |
| **Phase 2: Ultra-Fast Feature Extraction** | Days 5–7 | Build single-pass bitwise extractor in `major/src/features/` ($< 10\,\mu\text{s}$ for 1024-bit). |
| **Phase 3: Synthetic Dataset Generation** | Days 8–12 | Generate 10,000+ exponents across bit-lengths ($128, 256, 512, 1024, 2048$) and sparsity distributions (uniform random, dense, sparse, bursty). Label with ground-truth fastest strategy. |
| **Phase 4: ML Training & Model Compilation** | Days 13–18 | Train Decision Tree, Random Forest, XGBoost. Compare accuracy vs inference latency. Compile winning model to static fast decision code. |
| **Phase 5: Integrated Benchmark & Evaluation** | Days 19–25 | Compare: Fixed Binary vs Fixed wNAF vs Fixed VLIM vs Heuristic Rule vs ML-Adaptive. Measure wall-clock time, accuracy, overhead, HW operations. |
| **Phase 6: Final Paper & Defense Deck** | Days 26–30 | Thesis writeup, charts, tradeoff analysis, and viva deck. |
