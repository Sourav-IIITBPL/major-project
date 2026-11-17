# Turnkey Prompt for Claude AI: Major Project Report Generation (Phase-1)

> **Instructions for the User:**  
> Copy and paste the entire prompt below into Claude AI (e.g., Claude 3.5 Sonnet / Claude Opus). This prompt contains all the academic constraints, project background, empirical numbers, mathematical formulas, and formatting guidelines established by the Department of ECE, IIIT Bhopal.

---

```markdown
You are an expert academic researcher, VLSI cryptographic engineer, and technical author specializing in applied cryptography, hardware-software co-design, and machine learning. 

I need you to generate/refine the complete, formal, publication-grade B.Tech Major Project (Phase-1) Report for our course EC-413 at the Indian Institute of Information Technology (IIIT) Bhopal.

Please strictly adhere to all guidelines, project metadata, mathematical models, empirical results, and structural specifications outlined below.

---

### 1. INSTITUTIONAL AND ACADEMIC METADATA
- **Project Title:** ML-Assisted Adaptive Cryptographic Engine: Workload-Aware Modular Exponentiation and Side-Channel Hardened Acceleration
- **Degree:** Bachelor of Technology (B.Tech) in Electronics and Communication Engineering (ECE)
- **Course Code & Title:** EC-413: Major Project (Phase-1)
- **Academic Year:** 2026 – 2027 (7th Semester)
- **Institution:** Indian Institute of Information Technology Bhopal (IIIT Bhopal), Madhya Pradesh, India
- **Department:** Department of Electronics and Communication Engineering
- **Student Authors:**
  1. Sourav Yadav (Scholar ID: 23U01074)
  2. Eric Dazzle George (Scholar ID: 23U01035)
- **Project Supervisor:** Dr. Aashish Parihar, Assistant Professor, Department of ECE, IIIT Bhopal
- **Major Project Coordinator:** Dr. Jogendra Singh Rana, Assistant Professor, Department of ECE, IIIT Bhopal
- **Evaluation Scheme (100 Marks Total):**
  - Continuous Evaluation: E1 (10) + E2 (10) + E3 (10) + E4 (10) = 40 Marks
  - End Term Viva: Coding & Results (20) + Project File (20) + Presentation (20) = 60 Marks

---

### 2. FORMATTING AND COMPLIANCE RULES
- **Page Size:** Standard A4 size.
- **Margins:** Exactly 1.0 inch (or 1.5 inches for binding edge if specified) on all four sides.
- **Typography:** Times New Roman throughout the document.
  - Normal Body Text: 12 pt, 1.5 line spacing, 6 pt space after paragraphs.
  - Heading 1 (Chapter Titles): 16 pt to 18 pt, Bold.
  - Heading 2 (Sections): 14 pt, Bold.
  - Heading 3 (Subsections): 12 pt, Bold/Italic.
- **Table and Figure Captions:**
  - Table captions placed ABOVE the table (e.g., "Table 3.1: Extracted Cryptographic Features").
  - Figure captions placed BELOW the figure (e.g., "Figure 5.4: Global Feature Importance from KernelSHAP").
- **Originality & Tone:** Academic, formal, rigorous, third-person passive/active engineering prose. Plagiarism must be strictly less than 15%. All diagrams, tables, and equations must be self-designed.

---

### 3. MANDATORY SECTIONS AND PAGE BUDGET
Ensure the generated report includes all required sections with appropriate technical depth:
1. **Title Page** (Conforming to IIIT Bhopal formatting)
2. **Candidate Declaration** (Signed by Sourav Yadav & Eric Dazzle George)
3. **Certificate of Approval** (Signed by Dr. Aashish Parihar & Dr. Jogendra Singh Rana)
4. **Abstract** (300–450 words summarizing the problem, adaptive ML scheduler, totient blinding, and 2048-bit benchmark results)
5. **List of Figures, List of Tables, and List of Abbreviations**
6. **Chapter 1: Introduction** [3–5 pages equivalent]
   - Problem definition and purpose of modular exponentiation ($M^e \pmod N$) in RSA, DH, and hybrid PQC.
   - Computational bottlenecks ($O(k^3)$ scaling) and side-channel vulnerabilities (SPA/timing attacks).
   - Value and novel contribution of adaptive ML-driven scheduling.
   - Paraphrased outline of the report, scope, and engineering limitations.
   - Individual contribution table (Sourav Yadav vs. Eric Dazzle George).
7. **Chapter 2: Literature Review and Background Details** [4–8 pages equivalent]
   - Mathematical review of modular exponentiation and binary square-and-multiply.
   - Montgomery modular multiplication algorithm and Montgomery domain conversions.
   - Sliding-window exponentiation ($w$-bit windows, odd powers precomputation).
   - Side-channel vulnerabilities: Simple Power Analysis (SPA), Differential Power Analysis (DPA), Kocher's timing attacks.
   - Countermeasures: Montgomery Powering Ladder vs. blinding techniques.
   - Literature gap: Lack of dynamic, real-time workload profiling and sub-microsecond ML dispatch in existing cryptographic libraries.
8. **Chapter 3: System Model and Architectural Framework** [4–8 pages equivalent]
   - End-to-end 4-stage architecture: Ingestion -> Bitwise Feature Extractor -> Compiled ML Dispatcher -> Side-Channel Hardened Execution Engine.
   - Mathematical definition of 6 extracted features:
     * Exponent bit-length $k = \lceil \log_2(e) \rceil$
     * Hamming weight $H(e) = \sum e_i$
     * Hamming weight ratio $\alpha = H(e)/k$
     * Maximum consecutive run of 1s $\text{Run}_{\max}(1)$
     * Maximum consecutive run of 0s $\text{Run}_{\max}(0)$
     * Modulus bit-length $k_{\text{mod}} = \lceil \log_2(N) \rceil$
   - Target hardware abstraction models: Intel AVX-512 SIMD, Xilinx UltraScale+ FPGA (DSP48E2), TSMC 28nm ASIC (Carry-Save Radix-4 Multipliers).
9. **Chapter 4: Methodology and Algorithmic Innovations** [4–8 pages equivalent]
   - **Dynamic Exponent Slicing:** Formulation $e = \sum_{j=0}^{m-1} e_j \cdot 2^{j \cdot L}$, concurrent execution, and Horner-style modular shift recombination.
   - **Euler Totient Blinding Countermeasure:** Formal proof using Euler's theorem:
     $e' = e + r \cdot \lambda(N)$ where $r \in_R [1, 2^{64}-1]$, demonstrating $M^{e'} \equiv M^e \pmod N$ with zero ciphertext distortion.
   - **Compiled Decision Tree Logic:** Direct mapping of scikit-learn tree branches to native C if-else routines for deterministic, sub-microsecond latency ($0.42\ \mu\text{s}$).
10. **Chapter 5: Implementation Details and Comparative Result Analysis** [5–10 pages equivalent]
    - Training methodology: 10,000 synthetic cryptographic workloads, 5 candidate models benchmarked (Decision Tree: 97.4% accuracy, 0.42 µs; Random Forest: 98.8%, 18.2 µs; XGBoost: 98.6%, 45.0 µs).
    - Explainable AI via KernelSHAP: Modulus and exponent bit-lengths contribute >68% global attribution; $\alpha$ drives sliding-window thresholds.
    - 2048-bit RSA benchmarks: Sliding window ($w=5$) reduces modular multiplications from 3,072 to 2,390 (22.2% reduction); ASIC Radix-4 reduces cycles from 4.19M to 1.05M (75.0% cycle reduction).
    - Full-stack demonstration platform: FastAPI asynchronous REST backend, React 19 web dashboard with BigInt string safety, 47 passing unit tests.
11. **Chapter 6: Conclusion and Future Scope** [2–3 pages equivalent]
    - Summary of Phase-1 achievements.
    - Phase-2 (8th Semester) Roadmap: FPGA RTL synthesis on Xilinx Zynq-7000, physical side-channel power capture using ChipWhisperer, post-quantum lattice polynomial multiplication (Kyber/Dilithium NTT).
12. **Chapter 7: References** [2–3 pages equivalent]
    - Complete, formal IEEE-style citations (Montgomery 1985, Joye & Yen 2002, Kocher 1996, Lundberg & Lee 2017, NIST SP 800-56B, etc.).

---

### 4. KEY METRICS AND EMPIRICAL DATA TO EMBED
- Decision Tree Accuracy: 97.4% | Inference Latency: 0.42 microseconds (420 nanoseconds).
- 2048-bit RSA Multiplications: Standard Binary = 3,072 ops; Sliding Window (w=5) = 2,390 ops (**22.2% reduction**).
- 2048-bit RSA Hardware Cycles: Standard Binary = 4.19M cycles; ASIC Carry-Save Radix-4 = 1.05M cycles (**75.0% cycle reduction**).
- Unit Tests: 47 automated tests covering mathematical correctness, totient invariance, and API endpoints.

Please generate the complete, beautifully formatted report text now.
```
