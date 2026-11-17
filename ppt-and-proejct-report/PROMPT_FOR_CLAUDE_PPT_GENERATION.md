# Turnkey Prompt for Claude AI: Presentation PPT Generation (Phase-1)

> **Instructions for the User:**  
> Copy and paste the entire prompt below into Claude AI (e.g., Claude 3.5 Sonnet / Claude Opus). This prompt contains all presentation guidelines, slide structures, image references, and speaker notes required for the 5-10 minute presentation at IIIT Bhopal.

---

```markdown
You are an expert presentation designer, academic speaker coach, and VLSI cryptographic engineer.

I need you to generate/refine the complete slide-by-slide presentation deck and accompanying speaker script for our B.Tech Major Project (Phase-1) End-Term Viva for course EC-413 at the Indian Institute of Information Technology (IIIT) Bhopal.

Please strictly follow the institutional presentation rules, timing guidelines, visual aesthetics, and slide breakdown provided below.

---

### 1. PRESENTATION REQUIREMENTS & CONSTRAINTS
- **Course & Institution:** EC-413: Major Project (Phase-1), Department of Electronics and Communication Engineering, IIIT Bhopal.
- **Project Title:** ML-Assisted Adaptive Cryptographic Engine: Workload-Aware Modular Exponentiation and Side-Channel Hardened Acceleration
- **Group Presenters:**
  - Sourav Yadav (Scholar ID: 23U01074)
  - Eric Dazzle George (Scholar ID: 23U01035)
- **Project Mentors:**
  - Supervisor: Dr. Aashish Parihar, Assistant Professor (ECE)
  - Coordinator: Dr. Jogendra Singh Rana, Major Project Coordinator (ECE)
- **Presentation Timing:** Exactly 5 to 10 minutes total (shared equally between Sourav and Eric), followed by a faculty Q&A session.
- **Slide Count:** Exactly 12 to 14 slides (conforming to the guideline of ~10-15 slides).
- **Slide Ratio & Theme:** 16:9 Widescreen. Academic dark/slate navy theme with electric blue and teal accents. High visual contrast, structured cards, clear bullet hierarchy, zero text clutter.

---

### 2. SLIDE-BY-SLIDE CONTENT & TIME ALLOCATION

#### Slide 1: Title Slide [0:00 - 0:45]
- **Visuals:** Formal university title layout, Department of ECE, IIIT Bhopal, course code EC-413.
- **Details:** Full project title, student names and scholar IDs, supervisor Dr. Aashish Parihar, coordinator Dr. Jogendra Singh Rana.
- **Speaker:** Sourav / Eric (Introduction of the project).

#### Slide 2: Problem Statement & Motivation [0:45 - 1:30]
- **Visuals:** Split two-column card (Computational Bottleneck vs. Security Vulnerability).
- **Points:** $O(k^3)$ cubic complexity of Montgomery multiplication; static algorithms waste up to 40% performance; Left-to-Right square-and-multiply leaks secret keys via Simple Power Analysis (SPA) and timing attacks.
- **Speaker:** Sourav.

#### Slide 3: System Architecture & End-to-End Pipeline [1:30 - 2:15]
- **Visuals:** 4-stage pipeline flowchart:
  1. Input Ingestion (Modulus 512-4096b, Exponent, HW context)
  2. Zero-Overhead Bitwise Feature Extractor ($O(\log k)$)
  3. Compiled Decision Tree Dispatcher (<0.5 µs latency)
  4. Side-Channel Hardened Backend (Euler Blinding + Hardware Core)
- **Speaker:** Sourav.

#### Slide 4: Cryptographic Workload Profiling & Feature Space [2:15 - 3:00]
- **Visuals:** Table of 6 extracted bitwise features ($k$, $H(e)$, $\alpha = H(e)/k$, Max Run 1s, Max Run 0s, Modulus bits).
- **Highlights:** $O(1)$ SWAR / popcnt bit counting in <15 ns; zero floating-point BigInt overhead; natural workload clustering.
- **Speaker:** Sourav.

#### Slide 5: Algorithmic Suite & Dynamic Exponent Slicing [3:00 - 3:45]
- **Visuals:** Decomposition math: $e = \sum e_j \cdot 2^{jL}$, parallel exponentiation terms, Horner modular shift recombination.
- **Highlights:** Binary L-to-R, Montgomery Ladder, Sliding Window ($w=2..6$), Dynamic Exponent Slicing for multi-core SIMD and FPGA DSP blocks.
- **Speaker:** Eric.

#### Slide 6: Side-Channel Hardening via Euler Totient Blinding [3:45 - 4:30]
- **Visuals:** Proof of invariance: $e' = e + r \cdot \lambda(N) \implies M^{e'} \equiv M^e \pmod N$.
- **Highlights:** Refreshed 64-bit random salt $r$ completely decorrelates power traces and execution time across runs with zero plaintext distortion; defeats SPA, DPA, and timing attacks.
- **Speaker:** Eric.

#### Slide 7: Machine Learning Model Benchmarking & Selection [4:30 - 5:15]
- **Visuals:** Embed `confusion_decision_tree.png` and comparative table (Decision Tree vs Random Forest vs XGBoost vs MLP vs LogReg).
- **Key Insight:** Decision Tree achieves 97.4% accuracy with **0.42 µs latency** (100x faster than XGBoost) and zero external runtime libraries, compiling directly into C/Verilog `if-else` logic.
- **Speaker:** Sourav.

#### Slide 8: Explainable AI & SHAP Interpretability [5:15 - 6:00]
- **Visuals:** Embed `shap_importance_software.png` bar plot.
- **Highlights:** Modulus and exponent bit-lengths account for >68% global importance; Hamming weight ratio $\alpha$ defines sliding window threshold ($\alpha > 0.48$); aligns with BigInt complexity theory.
- **Speaker:** Sourav.

#### Slide 9: Experimental Results: 2048-bit RSA Benchmarking [6:00 - 6:45]
- **Visuals:** Embed `multiplications_comparison_2048.png` and `hardware_cycles_comparison_2048.png`.
- **Key Numbers:** Sliding Window ($w=5$) reduces modular multiplications from 3,072 to 2,390 (**22.2% reduction**); TSMC 28nm CSA Radix-4 cuts hardware cycles from 4.19M to 1.05M (**75.0% cycle reduction**).
- **Speaker:** Eric.

#### Slide 10: Hardware Backend Acceleration & Scaling [6:45 - 7:30]
- **Visuals:** Embed `latency_scaling.png` plot across key sizes 512 to 4096-bit.
- **Targets:** Intel AVX-512 SIMD (8 parallel lanes), Xilinx UltraScale+ FPGA (systolic DSP48E2 array), TSMC 28nm ASIC (Carry-Save Radix-4 multiplier eliminating carry-propagation delay).
- **Speaker:** Eric.

#### Slide 11: Full-Stack Implementation & Interactive Platform [7:30 - 8:15]
- **Visuals:** 3-column breakdown:
  1. FastAPI asynchronous REST server
  2. React 19 responsive dashboard with string-safe BigInt IEEE-754 handling
  3. 47 automated unit tests asserting mathematical correctness and totient invariance.
- **Speaker:** Sourav.

#### Slide 12: Work Distribution & Team Contributions [8:15 - 8:45]
- **Visuals:** Clear two-box split:
  - **Sourav Yadav (23U01074):** ML pipeline, model training, sub-microsecond Decision Tree compilation, SHAP interpretability, FastAPI backend, React 19 frontend.
  - **Eric Dazzle George (23U01035):** Exponentiation algorithms, Montgomery ladder, Euler totient blinding mathematical proofs, hardware cycle modeling, comparative benchmarking suite.
- **Speaker:** Sourav & Eric.

#### Slide 13: Summary of Phase-1 & Roadmap for Phase-2 [8:45 - 9:30]
- **Visuals:** Achievements summary vs. 8th semester milestones:
  - Jan–Feb 2027: FPGA RTL synthesis on Xilinx Zynq-7000 (measuring LUTs, DSPs, BRAMs).
  - Mar 2027: Physical electromagnetic/power trace capture using ChipWhisperer-Lite.
  - Apr 2027: Post-quantum lattice Number Theoretic Transform (NTT) acceleration (Kyber/Dilithium).
  - May 2027: Final B.Tech thesis and IEEE journal manuscript submission.
- **Speaker:** Eric.

#### Slide 14: References & Acknowledgments [9:30 - 10:00]
- **Visuals:** Core academic citations (Montgomery 1985, Joye & Yen 2002, Kocher 1996, Lundberg 2017) and sincere gratitude to Supervisor Dr. Aashish Parihar and Coordinator Dr. Jogendra Singh Rana.
- **Speaker:** Sourav & Eric (Opening floor for viva Q&A).

---

### 3. VIVA DEFENCE PREPARATION: COMMON FACULTY QUESTIONS & MODEL ANSWERS
Generate succinct, high-impact model answers for the following likely viva questions:
1. *Why did you choose a Decision Tree over more accurate models like XGBoost or Neural Networks?*
   - **Answer:** Decision Tree delivers 97.4% accuracy with an inference latency of only 0.42 µs, whereas XGBoost takes 45 µs and requires a heavyweight runtime. In hardware, a decision tree compiles into trivial hardwired comparator logic with zero execution jitter.
2. *How does Euler Totient Blinding guarantee that the decrypted plaintext is not altered?*
   - **Answer:** By Euler's Totient Theorem, for any message $M$ coprime to $N$, $M^{\lambda(N)} \equiv 1 \pmod N$. Therefore, $M^{e + r\lambda(N)} = M^e \cdot (M^{\lambda(N)})^r \equiv M^e \cdot (1)^r = M^e \pmod N$. The ciphertext is mathematically invariant.
3. *Why is dynamic slicing superior to standard multi-threading for BigInt modular exponentiation?*
   - **Answer:** Modular reduction is inherently sequential because each step depends on the previous reduction modulus. Dynamic slicing decomposes the exponent into independent sub-exponents that can be computed simultaneously on separate DSP cores, recombining results with minimal modular shifts.

Please generate the complete, production-ready presentation script and slides now.
```
