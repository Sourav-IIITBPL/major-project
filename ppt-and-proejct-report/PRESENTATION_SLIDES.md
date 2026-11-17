# Major Project (Phase-1) Presentation Deck & Speaker Script [EC-413]

**Institution:** Indian Institute of Information Technology (IIIT) Bhopal  
**Department:** Electronics and Communication Engineering  
**Project Title:** ML-Assisted Adaptive Cryptographic Engine: Workload-Aware Modular Exponentiation and Side-Channel Hardened Acceleration  
**Presenters:** Sourav Yadav (23U01074) & Eric Dazzle George (23U01035)  
**Supervisor:** Dr. Aashish Parihar, Assistant Professor (ECE)  
**Major Project Coordinator:** Dr. Jogendra Singh Rana, Assistant Professor (ECE)  
**Format:** 14 Slides (16:9 Widescreen) | Presentation Duration: 7–10 Minutes  

---

## SLIDE 1: TITLE SLIDE

### Visual Layout:
- Background: Deep Navy (`#0F172A`) with Electric Blue accent frame.
- Institution Header: `INDIAN INSTITUTE OF INFORMATION TECHNOLOGY BHOPAL`
- Department: `Department of Electronics and Communication Engineering | B.Tech Major Project (Phase-1) [EC-413]`
- Title: **ML-Assisted Adaptive Cryptographic Engine**
- Subtitle: *Workload-Aware Modular Exponentiation & Side-Channel Hardened Hardware Acceleration*
- Presenters Box (Left):
  - Sourav Yadav (Scholar ID: 23U01074)
  - Eric Dazzle George (Scholar ID: 23U01035)
- Supervision Box (Right):
  - Supervisor: Dr. Aashish Parihar, Assistant Professor (ECE)
  - Major Project Coordinator: Dr. Jogendra Singh Rana (ECE)

### Speaker Notes (Sourav / Eric):
> "Good morning respected evaluators, Dr. Aashish Parihar, Dr. Jogendra Singh Rana, and faculty members. We are Sourav Yadav and Eric Dazzle George. Today, we are presenting our Major Project Phase-1 on the 'ML-Assisted Adaptive Cryptographic Engine: Workload-Aware Modular Exponentiation and Side-Channel Hardened Acceleration'. In this project, we address the critical performance bottlenecks and physical side-channel vulnerabilities of asymmetric cryptography through real-time machine learning dispatch, dynamic exponent slicing, and mathematical Euler totient blinding."

---

## SLIDE 2: PROBLEM STATEMENT & MOTIVATION

### Visual Layout:
- Split Two-Column Layout (Problem on Left, Proposed Solution on Right).
- Left Box (The Challenge):
  - **Cubic Complexity Bottleneck:** Large-integer modular exponentiation ($M^e \pmod N$) scales cubically ($O(k^3)$) with Montgomery multiplication, consuming high latency and energy.
  - **Static Sub-Optimality:** Standard cryptographic libraries (OpenSSL, Libgcrypt) use fixed algorithms. A static choice either underutilizes SIMD/FPGA multipliers or causes severe cache thrashing on microcontrollers.
  - **Side-Channel Vulnerability:** Standard Left-to-Right binary square-and-multiply leaks secret exponent bits via Simple Power Analysis (SPA) and timing variations.
  - **Threat Reality:** Adversaries can recover private keys in under 1,000 power trace measurements.
- Right Box (Proposed Solution):
  - **Sub-Microsecond ML Dispatcher:** Decision Tree (<0.5 µs latency) dynamically matches workload bit patterns to the best execution pipeline.
  - **Multi-Algorithm Acceleration Suite:** Binary, Montgomery Ladder, Sliding Window ($w=2..6$), Dynamic Exponent Slicing.
  - **Mathematical Euler Totient Blinding:** $e' = e + r \cdot \lambda(N)$ ensures complete side-channel immunity with zero ciphertext distortion.
  - **Explainable Verification:** Full SHAP attribution proving hardware-consistent feature sensitivity.

### Speaker Notes (Sourav):
> "Public-key cryptosystems like RSA and Diffie-Hellman depend on computing $M^e \pmod N$ for 2048-bit to 4096-bit numbers. This faces two critical problems: First, existing implementations use rigid, static algorithms that waste up to 40% of hardware throughput across different key lengths. Second, naive exponentiation leaks private keys directly through power consumption traces and timing discrepancies. Our goal is to create an adaptive engine that dynamically chooses the fastest algorithm while guaranteeing mathematical immunity against physical side-channel attacks."

---

## SLIDE 3: SYSTEM ARCHITECTURE & HIGH-LEVEL PIPELINE

### Visual Layout:
- 4-Stage Horizontal Flow Cards:
  1. **Stage 1: Input Ingestion:** Cryptographic Request (Modulus $N \in [512, 4096]$, Exponent $e$, Hardware Context).
  2. **Stage 2: Bitwise Feature Extractor:** Zero-overhead metrics ($k$, $H(e)$, $\alpha = H(e)/k$, max runs of 1s and 0s).
  3. **Stage 3: Compiled ML Dispatcher:** Direct C/Python if-else logic (<0.42 µs latency, 97.4% accuracy).
  4. **Stage 4: Execution & Countermeasure Core:** Euler Totient Blinding + Selected Backend (AVX-512, FPGA DSP48E2, ASIC Carry-Save Radix-4).
- Bottom Banner: Full-stack integration with FastAPI REST server and responsive React 19 dashboard.

### Speaker Notes (Sourav):
> "Slide 3 presents our end-to-end architecture. When a request arrives, Stage 2 extracts bit-level statistical features in $O(\log k)$ bitwise steps without floating-point conversion. Stage 3 evaluates these features using our compiled Decision Tree in less than 420 nanoseconds. Finally, Stage 4 applies totient blinding and executes the chosen exponentiation algorithm on the selected hardware backend."

---

## SLIDE 4: WORKLOAD PROFILING & FEATURE SPACE

### Visual Layout:
- Left: Feature Specification Table (6 Primary Descriptors).
  - Exponent Bit-Length: $k = \lceil \log_2(e) \rceil$ (Governs squarings)
  - Hamming Weight: $H(e) = \sum e_i$ (Governs multiplications)
  - Hamming Weight Ratio: $\alpha = H(e)/k$ (Window amortization threshold)
  - Max Run of Ones: $\text{Run}_{\max}(1)$ (Optimal window width $w$)
  - Max Run of Zeros: $\text{Run}_{\max}(0)$ (Zero-skipping indicator)
  - Modulus Bit-Length: $k_{\text{mod}} = \lceil \log_2(N) \rceil$ (Multi-word limb memory footprint)
- Right: Profiling Efficiency Box.
  - Zero BigInt float conversion overhead.
  - SWAR / popcnt CPU intrinsics run in < 15 nanoseconds.
  - Workload clustering: Dense ($\alpha \ge 0.5$), Sparse ($\alpha < 0.25$), and Hardware-limited regimes.

### Speaker Notes (Sourav):
> "To classify workloads without adding overhead, we extract six bitwise features directly from BigInt representations. The Hamming weight ratio, alpha, alongside the maximum run of ones, directly informs the dispatcher whether precomputing a sliding-window lookup table will be mathematically amortized over the exponentiation."

---

## SLIDE 5: ALGORITHMIC SUITE & DYNAMIC EXPONENT SLICING

### Visual Layout:
- Left Column: Mathematical Formulation of Exponent Slicing.
  - Decomposition: $e = \sum_{j=0}^{m-1} e_j \cdot 2^{j \cdot L}$
  - Parallel Expansion: $M^e \equiv \prod_{j=0}^{m-1} (M^{e_j})^{2^{j \cdot L}} \pmod N$
  - Horner Modular Shift Recombination: $R_{j-1} = (R_j)^{2^L} \cdot M^{e_{j-1}} \pmod N$
- Right Column: Supported Algorithms.
  - Binary Left-to-Right: Baseline square-and-multiply.
  - Montgomery Ladder: Constant-time dual register $(R_0, R_1)$, SPA-immune.
  - Sliding Window ($w=2..6$): Skips zero sequences, amortizes odd power lookups.
  - Dynamic Slicing: Concurrent sub-word evaluation across multi-core SIMD and FPGA DSP blocks.

### Speaker Notes (Eric):
> "On Slide 5, we show our algorithmic suite. In addition to binary and Montgomery ladder methods, we developed Dynamic Exponent Slicing. For 4096-bit exponents, slicing partitions the exponent into balanced chunks that are processed concurrently across parallel hardware arithmetic units and recombined via Horner-style shifts, reducing critical path latency."

---

## SLIDE 6: SIDE-CHANNEL HARDENING VIA EULER TOTIENT BLINDING

### Visual Layout:
- Top Left Card: Mathematical Invariance.
  - $N = p \cdot q$, $\lambda(N) = \text{lcm}(p-1, q-1)$.
  - Random 64-bit integer $r \in_R [1, 2^{64}-1]$ refreshed per execution.
  - $e' = e + r \cdot \lambda(N)$
  - $M^{e'} = M^e \cdot (M^{\lambda(N)})^r \equiv M^e \cdot 1^r \equiv M^e \pmod N$
- Top Right Card: Attack Resistance Analysis.
  - SPA: Hamming weight and bit patterns are completely randomized on each run.
  - DPA: Power traces across runs have zero statistical correlation (noise level).
  - Timing Attacks: Random extra bits decouple execution time from original private key.
- Bottom: Comparative Security Table (Standard Binary vs Montgomery Ladder vs Our Euler Blinding).

### Speaker Notes (Eric):
> "Slide 6 presents our side-channel countermeasure. Using Euler's Totient Theorem, we add a random 64-bit multiple of lambda(N) to the private exponent. Because $M^{\lambda(N)} \equiv 1 \pmod N$, the computed ciphertext is 100% mathematically identical to the unblinded result. However, the physical power trace and execution time change completely every time, defeating Simple and Differential Power Analysis with less than 3.5% overhead."

---

## SLIDE 7: MACHINE LEARNING MODEL BENCHMARKING & SELECTION

### Visual Layout:
- Left: Embedded Confusion Matrix Plot (`confusion_decision_tree.png`).
- Right Top: Comparative Accuracy and Latency Table.
  - Decision Tree (Selected): 97.4% accuracy, **0.42 µs latency**, compiled if-else branches.
  - Random Forest: 98.8% accuracy, 18.2 µs latency, 2.4 MB memory.
  - XGBoost: 98.6% accuracy, 45.0 µs latency, 1.8 MB memory.
  - MLP Neural Net: 96.2% accuracy, 120.0 µs latency, heavy float operations.
  - Logistic Regression: 88.1% accuracy, 2.1 µs latency, poor non-linear boundary fit.
- Right Bottom: Architectural Decision Box.
  - Compiled Decision Tree achieves sub-microsecond evaluation ($0.42\ \mu\text{s}$) with zero external runtime libraries, making it directly synthesizable in C or Verilog.

### Speaker Notes (Sourav):
> "Slide 7 compares the five machine learning models we trained on 10,000 cryptographic workloads. Although ensemble methods like Random Forest and XGBoost achieved 98.8% accuracy, their inference latency is up to 45 microseconds with large memory footprints. In contrast, our compiled Decision Tree achieves 97.4% accuracy in only 420 nanoseconds with zero external library dependencies, making it ideal for real-time hardware dispatch."

---

## SLIDE 8: EXPLAINABLE AI & SHAP ATTRIBUTION

### Visual Layout:
- Left: Embedded Global Feature Importance Plot (`shap_importance_software.png`).
- Right: SHAP Interpretability Takeaways.
  - **Modulus and Exponent Bit-Lengths (>68% Total Weight):** Accurately captures where multi-word Montgomery arithmetic and cache-line boundaries dominate.
  - **Hamming Weight Ratio Threshold:** Strong activation toward Sliding Window ($w=5$) when $\alpha > 0.48$.
  - **Run Length Metrics:** Determines window width boundaries to avoid redundant shifts.
  - **Validation:** Proves that the ML model aligns with mathematical complexity theory rather than memorizing synthetic noise.

### Speaker Notes (Sourav):
> "To verify that our model's predictions reflect true hardware behavior, we applied KernelSHAP attribution. As shown in the bar chart, modulus bit-length and Hamming weight ratio account for over 68% of the model's decisions. This confirms that the model's decision logic closely matches theoretical BigInt complexity curves."

---

## SLIDE 9: EXPERIMENTAL RESULTS: 2048-BIT RSA BENCHMARKING

### Visual Layout:
- Side-by-Side Plots:
  - Left Plot: `multiplications_comparison_2048.png` (Total multiplications across algorithms).
  - Right Plot: `hardware_cycles_comparison_2048.png` (Hardware cycles across backends).
- Bottom Summary Strip:
  - Operation Reduction: Sliding Window ($w=5$) reduces modular multiplications from 3,072 to 2,390 (**22.2% reduction**).
  - Cycle Acceleration: ASIC Carry-Save Radix-4 reduces execution cycles from 4.19M to 1.05M (**75.0% cycle reduction**).
  - Dispatch Overhead: ML inference takes 0.42 µs (< 0.05% of 2048-bit RSA execution time).

### Speaker Notes (Eric):
> "Slide 9 highlights our experimental results on standard 2048-bit RSA. The left chart shows that the ML-selected sliding window ($w=5$) cuts modular multiplications by 22.2% over standard binary exponentiation. The right chart shows hardware execution cycles: our TSMC 28nm Carry-Save Radix-4 multiplier achieves a 75% reduction in cycles, dropping from 4.19 million down to 1.05 million cycles."

---

## SLIDE 10: HARDWARE BACKEND ACCELERATION & SCALING

### Visual Layout:
- Left: Embedded Latency Scaling Plot across key sizes 512 to 4096-bit (`latency_scaling.png`).
- Right: Target Architecture Specifications.
  - **Intel AVX-512 SIMD:** 512-bit vector registers with vectorized IFMA intrinsics, 8 parallel 64-bit limbs.
  - **Xilinx UltraScale+ FPGA:** Systolic Montgomery array mapped onto dedicated DSP48E2 slices at 400 MHz.
  - **TSMC 28nm ASIC:** Carry-Save Adder (CSA) Radix-4 multiplier eliminates carry-propagation critical path.
  - **Scalability:** Sub-linear cycle scaling enables predictable execution even at 4096-bit key sizes.

### Speaker Notes (Eric):
> "Slide 10 details our hardware backend models. We modeled three distinct targets: Intel AVX-512 SIMD for servers, Xilinx UltraScale+ FPGA for reconfigurable systems, and TSMC 28nm ASIC for dedicated silicon. By using carry-save redundant arithmetic, the ASIC multiplier eliminates carry-propagation delay, maintaining high clock frequencies and predictable scaling up to 4096 bits."

---

## SLIDE 11: FULL-STACK IMPLEMENTATION & INTERACTIVE PLATFORM

### Visual Layout:
- 3 Implementation Pillar Cards:
  - **FastAPI REST Backend:** Asynchronous microservices (`/api/analyze-workload`, `/api/recommend-algorithm`, `/api/full-benchmarks`, `/api/rsa/encrypt-decrypt`).
  - **React 19 Web Dashboard:** Tailwind CSS, responsive cards, string-safe BigInt IEEE-754 precision, live radar complexity charts, side-channel simulation.
  - **Automated Verification:** 47 unit and integration tests asserting mathematical equivalence ($M^{e'} \equiv M^e \pmod N$) and API reliability.

### Speaker Notes (Sourav):
> "Slide 11 highlights our end-to-end platform. We deployed a production-grade FastAPI server and an interactive React 19 dashboard. The platform handles arbitrary-length BigInt integers without precision loss, visualizes workload complexity via radar charts, and provides interactive side-channel power trace comparisons. The entire codebase is validated by 47 automated tests."

---

## SLIDE 12: WORK DISTRIBUTION & TEAM CONTRIBUTIONS

### Visual Layout:
- Two Distinct Member Cards:
  - **Sourav Yadav (23U01074):**
    - Machine learning synthetic data generation (10,000 workloads) and model training.
    - Compiled Decision Tree native branch generator (<0.42 µs latency).
    - KernelSHAP feature attribution and interpretability analysis.
    - FastAPI asynchronous REST API and React 19 interactive web dashboard.
  - **Eric Dazzle George (23U01035):**
    - Modular exponentiation algorithms (Binary, Montgomery ladder, Sliding window, Dynamic slicing).
    - Euler totient blinding mathematical formulations and proofs ($e' = e + r\lambda(N)$).
    - Hardware cycle and microarchitectural modeling for AVX-512, FPGA, and ASIC.
    - 47-test validation test suite and comparative benchmark execution.

### Speaker Notes (Sourav / Eric):
> "As outlined in Slide 12, Sourav led the machine learning pipeline, sub-microsecond compilation, SHAP interpretability, and full-stack software development. Eric led the cryptographic algorithm suite, Euler totient blinding proofs, hardware cycle modeling, and experimental benchmarking."

---

## SLIDE 13: SUMMARY OF PHASE-1 & PHASE-2 ROADMAP

### Visual Layout:
- Left Box: Phase-1 Achievements (Completed).
  - Adaptive ML engine with 97.4% accuracy and 0.42 µs latency.
  - 22.2% multiplication reduction on 2048-bit RSA.
  - 75.0% cycle reduction on Carry-Save Radix-4 ASIC.
  - Provable side-channel immunity via Euler totient blinding.
  - Full-stack web platform validated by 47 unit tests.
- Right Box: Phase-2 Milestones (8th Semester).
  - Jan – Feb 2027: Synthesize SystemVerilog RTL on Xilinx Zynq-7000 FPGA board; measure physical LUTs, DSPs, and power.
  - Mar 2027: Capture physical electromagnetic/power traces via ChipWhisperer-Lite to quantify SNR suppression.
  - Apr 2027: Extend adaptive engine to post-quantum Number Theoretic Transform (NTT) for Kyber/Dilithium.
  - May 2027: Final B.Tech Thesis and submission to IEEE Transactions on VLSI Systems.

### Speaker Notes (Eric):
> "To conclude, Phase-1 successfully delivered the mathematical foundations, machine learning dispatch, and verified software models. In Phase-2 during our 8th semester, we will synthesize our RTL on a physical Xilinx Zynq FPGA, capture real power traces using a ChipWhisperer, and extend our adaptive framework to post-quantum lattice cryptography."

---

## SLIDE 14: REFERENCES & ACKNOWLEDGMENTS

### Visual Layout:
- Left Column: Academic References (Montgomery 1985, Joye & Yen 2002, Kocher 1996, Lundberg & Lee 2017 SHAP, NIST SP 800-56B).
- Right Column: Acknowledgments.
  - Sincere gratitude to Project Supervisor **Dr. Aashish Parihar** for technical mentorship in VLSI and embedded cryptography.
  - Gratitude to Major Project Coordinator **Dr. Jogendra Singh Rana** and the Department of ECE, IIIT Bhopal.
  - Open for questions and discussion.

### Speaker Notes (Sourav / Eric):
> "We would like to express our deepest gratitude to our supervisor, Dr. Aashish Parihar, and our coordinator, Dr. Jogendra Singh Rana, for their continuous guidance and support. Thank you, respected evaluators. We are now happy to take any questions."

---
*End of Presentation Deck Script.*
