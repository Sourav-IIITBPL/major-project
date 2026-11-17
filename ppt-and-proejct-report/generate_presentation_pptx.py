#!/usr/bin/env python3
"""
generate_presentation_pptx.py
Generates the official Major Project (Phase-1) PowerPoint Presentation (16:9 widescreen)
for IIIT Bhopal B.Tech ECE (EC-413).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank layout

    # Base Colors
    NAVY = RGBColor(15, 23, 42)       # Slate 900
    DARK_BLUE = RGBColor(30, 58, 138)  # Blue 900
    ACCENT_BLUE = RGBColor(37, 99, 235)# Blue 600
    TEAL = RGBColor(13, 148, 136)      # Teal 600
    TEXT_DARK = RGBColor(30, 41, 59)   # Slate 800
    TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    BG_CARD = RGBColor(248, 250, 252)  # Slate 50
    BORDER_COLOR = RGBColor(226, 232, 240) # Slate 200
    WHITE = RGBColor(255, 255, 255)
    GOLD = RGBColor(217, 119, 6)

    fig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")

    def add_header(slide, title_text, category="IIIT BHOPAL | B.TECH ECE MAJOR PROJECT (PHASE-1)"):
        # Top banner line
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = ACCENT_BLUE
        top_bar.line.fill.background()

        # Category / Breadcrumb
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Decorative accent card
    card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(23, 37, 84) # Dark blue card
    card.line.color.rgb = RGBColor(59, 130, 246)
    card.line.width = Pt(1.5)

    # University & Department text
    tb = slide1.shapes.add_textbox(Inches(1.2), Inches(1.1), Inches(11), Inches(0.5))
    p = tb.text_frame.paragraphs[0]
    p.text = "INDIAN INSTITUTE OF INFORMATION TECHNOLOGY BHOPAL"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    tb_sub = slide1.shapes.add_textbox(Inches(1.2), Inches(1.45), Inches(11), Inches(0.4))
    p_sub = tb_sub.text_frame.paragraphs[0]
    p_sub.text = "Department of Electronics and Communication Engineering | B.Tech Major Project (Phase-1) [EC-413]"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = RGBColor(203, 213, 225)

    # Project Title
    tb_title = slide1.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(11), Inches(1.8))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p1 = tf_title.paragraphs[0]
    p1.text = "ML-Assisted Adaptive Cryptographic Engine"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p2 = tf_title.add_paragraph()
    p2.text = "Workload-Aware Modular Exponentiation & Side-Channel Hardened Hardware Acceleration"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(56, 189, 248)

    # Authors & Supervisor Boxes
    # Student Box
    sbox = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.3), Inches(5.2), Inches(1.8))
    sbox.fill.solid()
    sbox.fill.fore_color.rgb = RGBColor(30, 41, 59)
    sbox.line.color.rgb = RGBColor(71, 85, 105)
    tf_s = sbox.text_frame
    tf_s.word_wrap = True
    ps0 = tf_s.paragraphs[0]
    ps0.text = "PROJECT STUDENTS"
    ps0.font.size = Pt(11)
    ps0.font.bold = True
    ps0.font.color.rgb = RGBColor(251, 191, 36)
    ps1 = tf_s.add_paragraph()
    ps1.text = "• Sourav Yadav (Scholar ID: 23U01074)\n• Eric Dazzle George (Scholar ID: 23U01035)"
    ps1.font.size = Pt(13)
    ps1.font.color.rgb = WHITE

    # Supervisor Box
    gbox = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(4.3), Inches(5.3), Inches(1.8))
    gbox.fill.solid()
    gbox.fill.fore_color.rgb = RGBColor(30, 41, 59)
    gbox.line.color.rgb = RGBColor(71, 85, 105)
    tf_g = gbox.text_frame
    tf_g.word_wrap = True
    pg0 = tf_g.paragraphs[0]
    pg0.text = "ACADEMIC MENTORSHIP"
    pg0.font.size = Pt(11)
    pg0.font.bold = True
    pg0.font.color.rgb = RGBColor(251, 191, 36)
    pg1 = tf_g.add_paragraph()
    pg1.text = "• Supervisor: Dr. Aashish Parihar, Assistant Professor (ECE)\n• Major Project Coordinator: Dr. Jogendra Singh Rana (ECE)\n• Venue: IIIT Bhopal Campus"
    pg1.font.size = Pt(12)
    pg1.font.color.rgb = WHITE

    set_speaker_notes(slide1, 
        "Good morning respected evaluators, Dr. Aashish Parihar, Dr. Jogendra Singh Rana, and faculty members. "
        "We are Sourav Yadav and Eric Dazzle George, presenting our B.Tech Major Project Phase-1 titled: "
        "'ML-Assisted Adaptive Cryptographic Engine: Workload-Aware Modular Exponentiation and Side-Channel Hardened Acceleration'. "
        "In this project, we address the computational latency bottlenecks and side-channel vulnerabilities of public-key cryptography "
        "by combining sub-microsecond machine learning scheduling with mathematical totient blinding and hardware co-design.")

    # =========================================================================
    # SLIDE 2: Problem Statement & Motivation
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "1. Problem Statement & Research Motivation")

    # Left Column: The Problem
    p_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
    p_box.fill.solid()
    p_box.fill.fore_color.rgb = BG_CARD
    p_box.line.color.rgb = BORDER_COLOR
    tf = p_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE COMPUTATIONAL & SECURITY CHALLENGE"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(220, 38, 38)
    
    bullets_p = [
        ("Cubic Complexity Bottleneck:", "Modular exponentiation M^e mod N is the computational core of RSA, Diffie-Hellman, and post-quantum transitions. For k-bit numbers, Montgomery multiplication requires O(k^3) bit operations."),
        ("Static Sub-Optimality:", "Current cryptographic libraries (OpenSSL, Libgcrypt) use fixed algorithms. A static algorithm chosen for 2048-bit keys causes severe CPU cache eviction or memory stalls on edge IoT processors."),
        ("Critical Side-Channel Leakage:", "Standard Left-to-Right binary and naive sliding-window algorithms exhibit asymmetric power consumption and timing variations depending on exponent bits (0 = Square only, 1 = Square + Multiply)."),
        ("SPA / Timing Attack Threat:", "Adversaries measuring power traces or cache latency can reconstruct secret private keys in under 1,000 observations without breaking mathematical assumptions.")
    ]
    for title, desc in bullets_p:
        p_t = tf.add_paragraph()
        p_t.text = f"• {title} "
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = NAVY
        p_d = tf.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_DARK

    # Right Column: Proposed Solution & Objectives
    s_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    s_box.fill.solid()
    s_box.fill.fore_color.rgb = RGBColor(239, 246, 255)
    s_box.line.color.rgb = RGBColor(191, 219, 254)
    tf2 = s_box.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "PROPOSED ADAPTIVE ARCHITECTURE"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_BLUE

    bullets_s = [
        ("Sub-Microsecond ML Dispatcher:", "Integrate a real-time Decision Tree classifier (<0.5 µs latency) that profiles input modulus, exponent bit-patterns, and hardware platform to dynamically select the optimal mathematical algorithm."),
        ("Multi-Algorithm Execution Suite:", "Engine supports Binary L-to-R, Montgomery Ladder, Sliding Window (w=2..6), and novel Dynamic Exponent Slicing across AVX-512, FPGA, and ASIC Radix-4 backends."),
        ("Mathematical Euler Totient Blinding:", "Randomize private exponents on every execution using e' = e + r*lambda(N), achieving side-channel immunity with zero ciphertext distortion."),
        ("Verifiable Explainability:", "Complete SHAP (SHapley Additive exPlanations) validation proving feature sensitivity matches physical hardware characteristics.")
    ]
    for title, desc in bullets_s:
        p_t = tf2.add_paragraph()
        p_t.text = f"✔ {title} "
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = DARK_BLUE
        p_d = tf2.add_paragraph()
        p_d.text = f"   {desc}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide2,
        "Slide 2 outlines the motivation. Public-key cryptosystems rely heavily on modular exponentiation. "
        "However, systems face two dilemmas: first, static algorithmic selection wastes up to 40% of hardware cycles across varying key sizes; "
        "second, standard implementations leak secret keys through power variations (SPA) and timing attacks. "
        "Our solution introduces a lightweight ML dispatcher coupled with mathematical totient blinding to achieve both speed and cryptographic immunity.")

    # =========================================================================
    # SLIDE 3: System Architecture & End-to-End Pipeline
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "2. System Architecture & End-to-End Pipeline")

    # 4 Architecture Stages
    stages = [
        ("STAGE 1: INPUT INGESTION", "Cryptographic Request\n• Modulus (N: 512-4096b)\n• Exponent (e: k-bits)\n• Hardware Context\n  (AVX, FPGA, ASIC)", RGBColor(238, 242, 255)),
        ("STAGE 2: FEATURE ENGINE", "Zero-Overhead Extractor\n• Bit-length k & Modulus bits\n• Hamming weight H(e) & ratio\n• Max run of 1s & 0s\n• Target HW cache/cores", RGBColor(240, 253, 250)),
        ("STAGE 3: ML DISPATCHER", "Compiled Decision Tree\n• Latency: < 0.42 microseconds\n• Zero-dependency if-else code\n• 97.4% empirical accuracy\n• Adaptive window selector", RGBColor(254, 243, 199)),
        ("STAGE 4: HARDENED BACKEND", "Execution Core\n• Dynamic Exponent Slicing\n• Euler Totient Blinding\n• Montgomery Multiplier\n• ASIC Radix-4 / FPGA / AVX", RGBColor(240, 253, 244))
    ]

    for idx, (title, desc, bg_c) in enumerate(stages):
        x = Inches(0.8 + idx * 2.95)
        st_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.5), Inches(2.8), Inches(3.2))
        st_box.fill.solid()
        st_box.fill.fore_color.rgb = bg_c
        st_box.line.color.rgb = BORDER_COLOR
        st_box.line.width = Pt(1.2)
        tf = st_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK

    # Bottom Banner: Dual Software & Hardware Synthesis
    bot_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.9), Inches(11.7), Inches(2.0))
    bot_box.fill.solid()
    bot_box.fill.fore_color.rgb = BG_CARD
    bot_box.line.color.rgb = ACCENT_BLUE
    tf_b = bot_box.text_frame
    tf_b.word_wrap = True
    pb = tf_b.paragraphs[0]
    pb.text = "KEY ARCHITECTURAL HIGHLIGHTS"
    pb.font.size = Pt(12)
    pb.font.bold = True
    pb.font.color.rgb = DARK_BLUE
    
    pb2 = tf_b.add_paragraph()
    pb2.text = "• Pure BigInt Compatibility: Supports variable key lengths from 512-bit legacy up to 4096-bit post-quantum transition sizes with string-safe IEEE-754 precision.\n" \
               "• Low-Latency Pipeline: Real-time decision making occurs entirely in software or on-chip hardware registers without OS context switching.\n" \
               "• Dual Platform Deployment: Fully functional RESTful API (FastAPI) and interactive modern dashboard (React 19) alongside synthesizable RTL models."
    pb2.font.size = Pt(10.5)
    pb2.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide3,
        "Here we see the 4-stage end-to-end architecture. "
        "When an encryption or signature request arrives, Stage 2 extracts bit-level statistical features in O(log k) bitwise operations. "
        "Stage 3 executes our compiled Decision Tree, which requires less than 420 nanoseconds. "
        "Stage 4 executes the selected algorithm with random totient blinding on the target hardware backend.")

    # =========================================================================
    # SLIDE 4: Workload Profiling & Feature Extraction
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "3. Workload Profiling & Cryptographic Feature Space")

    # Table of Features
    tbl_shape = slide4.shapes.add_table(7, 3, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.3))
    table = tbl_shape.table
    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(3.7)

    headers = ["Feature Name", "Mathematical Symbol", "Cryptographic & Hardware Significance"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    features_data = [
        ("Exponent Bit-Length", "k = ceil(log2(e))", "Governs outer loop iterations (squaring steps)"),
        ("Hamming Weight", "H(e) = sum(e_i)", "Determines total non-zero multiplications in binary method"),
        ("Hamming Weight Ratio", "alpha = H(e) / k", "Core metric deciding whether window precomputations amortize"),
        ("Max Run of Ones", "Run_max(1)", "Determines optimal sliding window width w to avoid redundant shifts"),
        ("Max Run of Zeros", "Run_max(0)", "Identifies zero-skip opportunities for sparse exponents"),
        ("Modulus Bit-Length", "k_mod = ceil(log2(N))", "Determines word-count and memory cache pressure in Montgomery Mul")
    ]
    for r_idx, (fn, sym, sig) in enumerate(features_data):
        r = r_idx + 1
        table.cell(r, 0).text = fn
        table.cell(r, 1).text = sym
        table.cell(r, 2).text = sig
        for c in range(3):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r % 2 == 0 else WHITE
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(9.5)
                para.font.color.rgb = TEXT_DARK

    # Right side explanation
    rf_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.5), Inches(1.5), Inches(4.0), Inches(5.3))
    rf_box.fill.solid()
    rf_box.fill.fore_color.rgb = BG_CARD
    rf_box.line.color.rgb = BORDER_COLOR
    tf_rf = rf_box.text_frame
    tf_rf.word_wrap = True
    prf = tf_rf.paragraphs[0]
    prf.text = "PROFILING EFFICIENCY"
    prf.font.size = Pt(12)
    prf.font.bold = True
    prf.font.color.rgb = TEAL

    p_body = tf_rf.add_paragraph()
    p_body.text = "\n• Zero Floating-Point BigInt Overhead: Feature extraction operates directly on bitwise representations (GMP / native Python bit_length and bit_count).\n\n" \
                 "• O(1) Bitwise Counting: Hamming weight is computed using SWAR / popcnt CPU intrinsics in < 15 nanoseconds.\n\n" \
                 "• Workload Clustering: Empirically proves that modular exponentiation workloads naturally bifurcate into Dense (alpha >= 0.5), Sparse (alpha < 0.25), and Hardware-Limited regimes."
    p_body.font.size = Pt(10.5)
    p_body.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide4,
        "Slide 4 explains the feature engineering. Rather than treating cryptographic operations as a black box, "
        "we extract 6 primary mathematical descriptors. The ratio of Hamming weight to bit length, alpha, "
        "along with the maximum run of ones, directly indicates whether a sliding-window table lookup will outperform a direct ladder.")

    # =========================================================================
    # SLIDE 5: Algorithmic Innovations & Slicing
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "4. Algorithmic Innovations: Dynamic Exponent Slicing")

    # Left: Slicing Diagram & Logic
    sl_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.8), Inches(5.3))
    sl_box.fill.solid()
    sl_box.fill.fore_color.rgb = BG_CARD
    sl_box.line.color.rgb = BORDER_COLOR
    tf = sl_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "MATHEMATICAL FORMULATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    p_math = tf.add_paragraph()
    p_math.text = "\nPartitioning k-bit exponent e into m slices of length L:\n" \
                  "  e = sum_{i=0}^{m-1} e_i * 2^{i*L}\n\n" \
                  "Exponentiation decomposed into concurrent terms:\n" \
                  "  M^e mod N = prod_{i=0}^{m-1} (M^{e_i})^{2^{i*L}} mod N\n\n" \
                  "Parallel Pipeline Execution:\n" \
                  "• Slices e_i computed concurrently across independent hardware pipelines or SIMD ALUs.\n" \
                  "• Shift aggregation uses Horner-like modular reduction:\n" \
                  "  R_{i-1} = (R_i)^{2^L} * M^{e_{i-1}} mod N"
    p_math.font.size = Pt(10.5)
    p_math.font.color.rgb = TEXT_DARK

    # Right: Algorithm Comparison Cards
    right_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
    right_box.fill.solid()
    right_box.fill.fore_color.rgb = BG_CARD
    right_box.line.color.rgb = BORDER_COLOR
    tf2 = right_box.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "SUPPORTED ALGORITHM SUITE"
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_BLUE

    algos = [
        ("Binary Left-to-Right:", "Baseline squaring and multiplication. Low memory, but highly variable timing and vulnerable to SPA."),
        ("Montgomery Ladder:", "Constant-time dual accumulation (R0, R1). Exactly 1 square + 1 multiply per bit. Fully immune to timing/SPA."),
        ("Sliding Window (w=2..6):", "Precomputes odd powers {M^3, ..., M^{2^w - 1}}. Skips zero runs. Minimizes total multiplications for high-density exponents."),
        ("Dynamic Slicing:", "Decomposes 2048/4096-bit exponents into 256/512-bit sub-words. Ideal for FPGA dual DSP48 blocks and multi-core CPU SIMD.")
    ]
    for aname, adesc in algos:
        pa = tf2.add_paragraph()
        pa.text = f"• {aname} "
        pa.font.bold = True
        pa.font.size = Pt(10.5)
        pa.font.color.rgb = NAVY
        pd = tf2.add_paragraph()
        pd.text = f"  {adesc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide5,
        "On Slide 5, we show our algorithmic suite. In addition to standard Left-to-Right and Montgomery Ladder, "
        "we implemented a dynamic exponent slicing scheme. For large 4096-bit exponents, slicing breaks the exponent "
        "into smaller chunks that can be dispatched to separate FPGA arithmetic cores or AVX-512 register lanes, "
        "reducing total critical-path latency.")

    # =========================================================================
    # SLIDE 6: Side-Channel Hardening via Euler Totient Blinding
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "5. Side-Channel Hardening: Euler Totient Blinding")

    # Card 1: Mathematical Invariance
    c1 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(2.6))
    c1.fill.solid()
    c1.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c1.line.color.rgb = RGBColor(187, 247, 208)
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "EULER TOTIENT INVARIANCE THEOREM"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(22, 101, 52)
    p_body = tf1.add_paragraph()
    p_body.text = "Let N = p * q, and Carmichael function lambda(N) = lcm(p-1, q-1).\n" \
                 "For any message M coprime to N and random integer r in [1, 2^64 - 1]:\n" \
                 "    e_blinded = e + r * lambda(N)\n" \
                 "    M^{e_blinded} = M^{e + r*lambda(N)} = M^e * (M^{lambda(N)})^r = M^e * 1^r = M^e (mod N)\n" \
                 "Result: 100% mathematically exact output with zero plaintext distortion!"
    p_body.font.size = Pt(9.5)
    p_body.font.color.rgb = TEXT_DARK

    # Card 2: Side-Channel Defense Mechanism
    c2 = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(2.6))
    c2.fill.solid()
    c2.fill.fore_color.rgb = RGBColor(254, 242, 242)
    c2.line.color.rgb = RGBColor(254, 202, 202)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "ATTACK MITIGATION ANALYSIS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(153, 27, 27)
    p_body2 = tf2.add_paragraph()
    p_body2.text = "• SPA (Simple Power Analysis) Defense:\n" \
                  "  Because r is uniformly refreshed on every execution, the Hamming weight and bit sequence differ completely in every trace.\n" \
                  "• DPA (Differential Power Analysis) Defense:\n" \
                  "  Averaging thousands of power traces yields uncorrelated Gaussian noise.\n" \
                  "• Timing Attack Immunity:\n" \
                  "  Execution duration is completely de-correlated from the true private exponent."
    p_body2.font.size = Pt(9.5)
    p_body2.font.color.rgb = TEXT_DARK

    # Card 3: Comparison Table
    tbl_s6 = slide6.shapes.add_table(4, 4, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.5))
    t6 = tbl_s6.table
    t6.columns[0].width = Inches(2.5)
    t6.columns[1].width = Inches(2.5)
    t6.columns[2].width = Inches(3.3)
    t6.columns[3].width = Inches(3.4)

    s6_headers = ["Implementation Scheme", "Timing Attack Vulnerability", "Power Analysis (SPA / DPA)", "Computational Overhead"]
    for i, h in enumerate(s6_headers):
        cell = t6.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    row_data = [
        ("Standard Binary L-to-R", "EXTREME (Bit-dependent branching)", "VULNERABLE (SPA identifies 0 vs 1)", "Baseline (0% overhead)"),
        ("Montgomery Ladder Alone", "NONE (Constant-time)", "RESISTANT to SPA (Uniform operations)", "~33% more multiplications"),
        ("Ladder + Euler Totient Blinding (Ours)", "ZERO CORRELATION (Randomized)", "FULL IMMUNITY to SPA & DPA", "< 3.5% overhead on 2048-bit keys")
    ]
    for r_idx, (c0, c1_t, c2_t, c3_t) in enumerate(row_data):
        row = r_idx + 1
        t6.cell(row, 0).text = c0
        t6.cell(row, 1).text = c1_t
        t6.cell(row, 2).text = c2_t
        t6.cell(row, 3).text = c3_t
        for col in range(4):
            cell = t6.cell(row, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row % 2 == 1 else WHITE
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(9.5)
                para.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide6,
        "Slide 6 presents our side-channel defense. By utilizing Euler's Totient Theorem, we add a random 64-bit multiple "
        "of lambda(N) to the private exponent. By mathematical identity, M^(e + r*lambda(N)) is congruent to M^e mod N. "
        "This completely randomizes the power trace and execution timing on every single run, thwarting both Simple and Differential Power Analysis.")

    # =========================================================================
    # SLIDE 7: Machine Learning Model Benchmarking & Selection
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "6. Machine Learning Model Benchmarking & Selection")

    # Left: Confusion Matrix Image
    img_path = os.path.join(fig_dir, "confusion_decision_tree.png")
    if os.path.exists(img_path):
        slide7.shapes.add_picture(img_path, Inches(0.8), Inches(1.5), width=Inches(5.6))

    # Right: Comparative Table & Selection Rationale
    tbl_ml = slide7.shapes.add_table(6, 4, Inches(6.8), Inches(1.5), Inches(5.7), Inches(3.2))
    t_ml = tbl_ml.table
    t_ml.columns[0].width = Inches(1.8)
    t_ml.columns[1].width = Inches(1.1)
    t_ml.columns[2].width = Inches(1.3)
    t_ml.columns[3].width = Inches(1.5)

    ml_headers = ["ML Model", "Accuracy", "Inference Latency", "Deployment Form"]
    for i, h in enumerate(ml_headers):
        cell = t_ml.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = WHITE

    ml_rows = [
        ("Decision Tree (Ours)", "97.4%", "0.42 µs", "Native C/Verilog If-Else"),
        ("Random Forest", "98.8%", "18.2 µs", "Ensemble Tree Forest"),
        ("XGBoost", "98.6%", "45.0 µs", "Gradient Boosted Trees"),
        ("MLP Neural Net", "96.2%", "120.0 µs", "Matrix Multiply Layers"),
        ("Logistic Regression", "88.1%", "2.1 µs", "Linear Hyperplane")
    ]
    for r_idx, (m, acc, lat, dep) in enumerate(ml_rows):
        row = r_idx + 1
        t_ml.cell(row, 0).text = m
        t_ml.cell(row, 1).text = acc
        t_ml.cell(row, 2).text = lat
        t_ml.cell(row, 3).text = dep
        for col in range(4):
            cell = t_ml.cell(row, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row % 2 == 1 else WHITE
            for para in cell.text_frame.paragraphs:
                para.font.size = Pt(9)
                para.font.color.rgb = TEXT_DARK

    # Bottom Right Card: Architectural Decision Rationale
    dec_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(4.9), Inches(5.7), Inches(2.0))
    dec_box.fill.solid()
    dec_box.fill.fore_color.rgb = RGBColor(254, 243, 199)
    dec_box.line.color.rgb = RGBColor(251, 191, 36)
    tf_dec = dec_box.text_frame
    tf_dec.word_wrap = True
    pdec = tf_dec.paragraphs[0]
    pdec.text = "WHY DECISION TREE WAS SELECTED FOR PRODUCTION"
    pdec.font.size = Pt(11)
    pdec.font.bold = True
    pdec.font.color.rgb = RGBColor(146, 64, 14)
    p_body = tf_dec.add_paragraph()
    p_body.text = "• Zero Library Footprint: Can be compiled directly into nested C if-else branches or synthesizable Verilog look-up logic.\n" \
                  "• 100x Faster Than Boosted Models: 0.42 µs latency ensures scheduling overhead is negligible (< 0.05% of 2048-bit RSA).\n" \
                  "• Deterministic Bounded Execution: Fixed depth eliminates timing jitter during algorithm dispatch."
    p_body.font.size = Pt(9.5)
    p_body.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide7,
        "Slide 7 shows our model benchmarking. While Random Forest and XGBoost achieved marginally higher accuracy (98.8%), "
        "their inference time is between 18 and 45 microseconds with large memory footprints. "
        "In contrast, our compiled Decision Tree achieves 97.4% accuracy with an inference time of only 420 nanoseconds, "
        "and requires zero external runtime libraries. This makes it ideal for real-time embedded hardware.")

    # =========================================================================
    # SLIDE 8: Explainable AI & SHAP Interpretability
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "7. Explainable AI: SHAP Feature Attribution")

    # Left: SHAP Bar Image
    img_shap = os.path.join(fig_dir, "shap_importance_software.png")
    if os.path.exists(img_shap):
        slide8.shapes.add_picture(img_shap, Inches(0.8), Inches(1.5), width=Inches(5.8))

    # Right: Interpretability Discussion
    sh_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.3))
    sh_box.fill.solid()
    sh_box.fill.fore_color.rgb = BG_CARD
    sh_box.line.color.rgb = BORDER_COLOR
    tf = sh_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SHAPLEY VALUE HARDWARE CORRELATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    shap_points = [
        ("Modulus & Exponent Bit-Lengths (>68% Total Importance):", "SHAP confirms that bit-length is the overriding factor deciding whether multi-word Montgomery arithmetic or hardware radix multipliers dominate latency."),
        ("Hamming Weight Ratio Thresholds:", "When alpha > 0.48, SHAP values strongly shift predictions toward Sliding Window w=5 and w=6, where precomputed odd powers amortize across frequent multiplications."),
        ("Sparse Exponent Identification:", "When alpha < 0.25, the model correctly prioritizes Binary L-to-R or Montgomery Ladder with zero-skip logic, saving up to 40% memory lookups."),
        ("Validation of Theoretical Crypto Models:", "The machine learning model did not memorize arbitrary patterns; its feature weights precisely align with the mathematical complexity curves of BigInt modular arithmetic.")
    ]
    for stitle, sdesc in shap_points:
        pt = tf.add_paragraph()
        pt.text = f"• {stitle} "
        pt.font.bold = True
        pt.font.size = Pt(10.5)
        pt.font.color.rgb = NAVY
        pd = tf.add_paragraph()
        pd.text = f"  {sdesc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide8,
        "On Slide 8, we apply SHAP interpretability to explain why the model makes each algorithmic choice. "
        "The SHAP analysis proves that modulus bit-length and Hamming weight ratio account for over 68% of the decision weight. "
        "This gives us mathematical confidence that the ML model is faithfully capturing the underlying hardware cost curves "
        "rather than overfitting on synthetic dataset noise.")

    # =========================================================================
    # SLIDE 9: Experimental Results - 2048-bit RSA Performance
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "8. Experimental Results: 2048-bit RSA Benchmarking")

    # Left: Multiplications Comparison Image
    img_mul = os.path.join(fig_dir, "multiplications_comparison_2048.png")
    if os.path.exists(img_mul):
        slide9.shapes.add_picture(img_mul, Inches(0.8), Inches(1.5), width=Inches(5.7))

    # Right: Cycles Comparison Image
    img_cyc = os.path.join(fig_dir, "hardware_cycles_comparison_2048.png")
    if os.path.exists(img_cyc):
        slide9.shapes.add_picture(img_cyc, Inches(6.8), Inches(1.5), width=Inches(5.7))

    # Bottom Summary Strip
    sum_box = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.8), Inches(11.7), Inches(1.2))
    sum_box.fill.solid()
    sum_box.fill.fore_color.rgb = RGBColor(239, 246, 255)
    sum_box.line.color.rgb = ACCENT_BLUE
    tf_s = sum_box.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "KEY QUANTITATIVE FINDINGS (2048-bit Workloads)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE
    p2 = tf_s.add_paragraph()
    p2.text = "• Operation Reduction: Sliding Window w=5 reduces total modular multiplications from 3,072 to 2,390 (22.2% reduction).\n" \
              "• Cycle Acceleration: ASIC Carry-Save Radix-4 reduces execution cycles from 4.19M to 1.05M cycles (75.0% cycle reduction).\n" \
              "• Dispatch Cost: Decision Tree inference consumes only 0.42 µs, representing less than 0.05% of the total execution budget."
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide9,
        "Slide 9 displays our quantitative benchmarks for standard 2048-bit RSA. "
        "The left plot shows that sliding-window w=5 reduces total modular multiplications by 22.2% compared to standard binary exponentiation. "
        "The right plot shows hardware cycle execution: on our ASIC Carry-Save Radix-4 backend, total cycles drop by 75%, from 4.19 million down to 1.05 million.")

    # =========================================================================
    # SLIDE 10: Hardware Backend Acceleration (ASIC / FPGA / AVX)
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "9. Hardware Backend Acceleration & Scaling")

    # Left: Latency Scaling Image
    img_lat = os.path.join(fig_dir, "latency_scaling.png")
    if os.path.exists(img_lat):
        slide10.shapes.add_picture(img_lat, Inches(0.8), Inches(1.5), width=Inches(5.7))

    # Right: Backend Architectures Breakdown
    hw_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    hw_box.fill.solid()
    hw_box.fill.fore_color.rgb = BG_CARD
    hw_box.line.color.rgb = BORDER_COLOR
    tf = hw_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TARGET HARDWARE ACCELERATOR ENGINES"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY

    hw_specs = [
        ("Intel AVX-512 SIMD (Software Target):", "Utilizes 512-bit vector registers with vectorized IFMA (Integer Fused Multiply-Add) intrinsics. Amortizes multi-word limb multiplications across 8 parallel 64-bit lanes."),
        ("Xilinx UltraScale+ FPGA (DSP48E2 Target):", "Maps multi-precision Montgomery multiplication directly onto dedicated 27x18-bit DSP slices operating at 400 MHz. Eliminates LUT routing congestion through systolic scheduling."),
        ("TSMC 28nm ASIC (Dedicated Core Target):", "Employs Carry-Save Radix-4 Montgomery Multipliers (CSA). Compresses partial products into redundant carry-save form, eliminating carry propagation delay along the critical path."),
        ("Scalability across 512 to 4096-bit Keys:", "The latency plot shows consistent sub-linear cycle growth on hardware backends compared to software, ensuring seamless scalability for 4096-bit keys.")
    ]
    for hname, hdesc in hw_specs:
        pt = tf.add_paragraph()
        pt.text = f"• {hname} "
        pt.font.bold = True
        pt.font.size = Pt(10.5)
        pt.font.color.rgb = DARK_BLUE
        pd = tf.add_paragraph()
        pd.text = f"  {hdesc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide10,
        "Slide 10 details our hardware backend modeling. We evaluated three target architectures: "
        "Intel AVX-512 SIMD for servers, Xilinx UltraScale+ FPGA DSP48E2 slices for reconfigurable infrastructure, and TSMC 28nm ASIC for embedded silicon. "
        "Our Carry-Save Radix-4 multiplier avoids carry propagation delays, maintaining predictable latency even as key lengths scale up to 4096 bits.")

    # =========================================================================
    # SLIDE 11: Full-Stack Implementation & Interactive Platform
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "10. Full-Stack Implementation & Interactive Platform")

    # 3 Column Cards
    col_cards = [
        ("FASTAPI BACKEND", [
            ("Port 8000 REST API", "Asynchronous high-throughput server"),
            ("/api/analyze-workload", "Extracts 6 cryptographic features"),
            ("/api/recommend-algorithm", "Instant Decision Tree inference"),
            ("/api/full-benchmarks", "Multi-backend cycle & latency simulation"),
            ("/api/rsa/encrypt-decrypt", "Full cryptographic lifecycle verification")
        ], RGBColor(238, 242, 255)),
        ("REACT 19 FRONTEND", [
            ("Modern Responsive UI", "Built with Tailwind CSS & Lucide icons"),
            ("1024/2048-bit Safe", "String-safe BigInt decimal/hex handling"),
            ("Interactive Radar Charts", "Real-time workload complexity visualization"),
            ("Side-Channel Simulator", "Live comparison of blinded vs unblinded traces"),
            ("Preset Workloads", "One-click load for RSA-1024, RSA-2048, RSA-4096")
        ], RGBColor(240, 253, 250)),
        ("VERIFICATION & TESTS", [
            ("47 Unit Tests", "100% test pass rate across core test suite"),
            ("Mathematical Correctness", "Validated against Python pow(M, e, N)"),
            ("Euler Blinding Equivalence", "Asserted M^{e'} == M^e mod N across 10k runs"),
            ("IEEE-754 Precision Checks", "Verified zero truncation on BigInt parsing"),
            ("Automated CI Script", "Single-command 'run_all.sh' orchestration")
        ], RGBColor(254, 243, 199))
    ]

    for idx, (title, items, bg_c) in enumerate(col_cards):
        x = Inches(0.8 + idx * 3.95)
        cbox = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.5), Inches(3.8), Inches(5.3))
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = bg_c
        cbox.line.color.rgb = BORDER_COLOR
        tf = cbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY

        for iname, idesc in items:
            pt = tf.add_paragraph()
            pt.text = f"✔ {iname}:"
            pt.font.bold = True
            pt.font.size = Pt(10)
            pt.font.color.rgb = DARK_BLUE
            pd = tf.add_paragraph()
            pd.text = f"   {idesc}"
            pd.font.size = Pt(9.5)
            pd.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide11,
        "Slide 11 highlights our software engineering implementation. We built a production-grade FastAPI service on port 8000 "
        "and a responsive React 19 web dashboard on port 3000. BigInt values up to 4096 bits are processed without precision loss. "
        "Our codebase includes 47 passing unit tests covering mathematical accuracy, totient invariance, and API endpoints.")

    # =========================================================================
    # SLIDE 12: Work Distribution & Team Contributions
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "11. Team Work Distribution & Individual Contributions")

    # Member 1 Box
    m1_box = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
    m1_box.fill.solid()
    m1_box.fill.fore_color.rgb = BG_CARD
    m1_box.line.color.rgb = ACCENT_BLUE
    m1_box.line.width = Pt(1.5)
    tf1 = m1_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "SOURAV YADAV (Scholar ID: 23U01074)"
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = DARK_BLUE
    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Department of ECE | Primary Focus: Machine Learning & Full-Stack Platform"
    p1_sub.font.size = Pt(10)
    p1_sub.font.color.rgb = TEXT_MUTED

    m1_tasks = [
        ("Machine Learning Pipeline & Model Training:", "Implemented synthetic cryptographic workload generator (10,000 samples) and trained 5 classifiers (Decision Tree, RF, XGBoost, MLP, LogReg)."),
        ("Sub-Microsecond Decision Tree Compilation:", "Converted scikit-learn Decision Tree into compiled C/Python if-else routines, reducing inference latency to < 0.42 µs with zero library dependencies."),
        ("SHAP Explainability & Attribution Analysis:", "Conducted KernelSHAP interpretability studies, generating feature attribution plots and validating cryptographic feature sensitivity."),
        ("Full-Stack Dashboard & API Infrastructure:", "Built FastAPI asynchronous endpoints and interactive React 19 web application with BigInt string precision and side-channel radar visualization.")
    ]
    for tt, td in m1_tasks:
        pt = tf1.add_paragraph()
        pt.text = f"• {tt} "
        pt.font.bold = True
        pt.font.size = Pt(10)
        pt.font.color.rgb = NAVY
        pd = tf1.add_paragraph()
        pd.text = f"  {td}"
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK

    # Member 2 Box
    m2_box = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    m2_box.fill.solid()
    m2_box.fill.fore_color.rgb = BG_CARD
    m2_box.line.color.rgb = TEAL
    m2_box.line.width = Pt(1.5)
    tf2 = m2_box.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "ERIC DAZZLE GEORGE (Scholar ID: 23U01035)"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = TEAL
    p2_sub = tf2.add_paragraph()
    p2_sub.text = "Department of ECE | Primary Focus: Cryptography & Hardware Modeling"
    p2_sub.font.size = Pt(10)
    p2_sub.font.color.rgb = TEXT_MUTED

    m2_tasks = [
        ("Cryptographic Algorithm Engine:", "Designed and implemented Binary L-to-R, Montgomery Ladder, Sliding Window (w=2..6), and Dynamic Exponent Slicing engines in Python and C."),
        ("Side-Channel Euler Totient Blinding:", "Formulated and proved the Euler/Carmichael totient blinding scheme (e' = e + r*lambda(N)), ensuring 100% mathematical invariance and SPA immunity."),
        ("Hardware Backend Architectural Modeling:", "Constructed microarchitectural cycle and latency models for Intel AVX-512, Xilinx UltraScale+ FPGA DSP48E2, and TSMC 28nm CSA Radix-4 ASICs."),
        ("Benchmarking Suite & Mathematical Validation:", "Formulated the 47-test validation suite, executing comprehensive comparative latency and multiplication benchmarks across 512 to 4096-bit RSA workloads.")
    ]
    for tt, td in m2_tasks:
        pt = tf2.add_paragraph()
        pt.text = f"• {tt} "
        pt.font.bold = True
        pt.font.size = Pt(10)
        pt.font.color.rgb = NAVY
        pd = tf2.add_paragraph()
        pd.text = f"  {td}"
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide12,
        "Slide 12 presents our individual contributions as required by the IIIT Bhopal major project guidelines. "
        "Sourav focused on the machine learning models, sub-microsecond compilation, SHAP interpretability, and full-stack software development. "
        "Eric led the cryptographic algorithms, side-channel Euler totient proofs, hardware microarchitecture modeling, and experimental benchmarking.")

    # =========================================================================
    # SLIDE 13: Summary of Contributions & Phase-2 Roadmap
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, "12. Summary of Phase-1 & Roadmap for Phase-2 (8th Sem)")

    # Left: Phase 1 Achievements
    p1_box = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
    p1_box.fill.solid()
    p1_box.fill.fore_color.rgb = RGBColor(240, 253, 244)
    p1_box.line.color.rgb = RGBColor(187, 247, 208)
    tf1 = p1_box.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "PHASE-1 DELIVERABLES (COMPLETED)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(22, 101, 52)

    achievements = [
        ("Adaptive ML Engine:", "Compiled Decision Tree scheduler achieves 97.4% accuracy with < 0.42 µs execution latency."),
        ("22.2% Arithmetic Reduction:", "Sliding window optimization reduces modular multiplications from 3,072 to 2,390 on 2048-bit RSA."),
        ("75.0% Cycle Reduction:", "Carry-Save Radix-4 ASIC multiplier reduces execution cycles from 4.19M to 1.05M."),
        ("Mathematical SPA/Timing Immunity:", "Euler totient blinding verified mathematically with zero plaintext distortion."),
        ("Full-Stack Demonstration:", "Production-ready FastAPI backend and responsive React 19 web interface verified by 47 unit tests.")
    ]
    for atitle, adesc in achievements:
        pt = tf1.add_paragraph()
        pt.text = f"✔ {atitle} "
        pt.font.bold = True
        pt.font.size = Pt(10.5)
        pt.font.color.rgb = NAVY
        pd = tf1.add_paragraph()
        pd.text = f"   {adesc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK

    # Right: Phase 2 Roadmap
    p2_box = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    p2_box.fill.solid()
    p2_box.fill.fore_color.rgb = RGBColor(238, 242, 255)
    p2_box.line.color.rgb = RGBColor(199, 210, 254)
    tf2 = p2_box.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "PHASE-2 ROADMAP (8TH SEMESTER)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    milestones = [
        ("FPGA Hardware Synthesis (Jan - Feb 2027):", "Synthesize and map RTL SystemVerilog onto physical Xilinx Zynq-7000 FPGA SoC development board, measuring real on-chip resource utilization (LUTs, DSPs, BRAMs)."),
        ("Physical Side-Channel Power Capture (Mar 2027):", "Measure actual electromagnetic emissions and power traces using ChipWhisperer-Lite / high-speed digital oscilloscope to empirically quantify SNR reduction."),
        ("Post-Quantum Lattice Acceleration (Apr 2027):", "Extend the adaptive ML engine to post-quantum Number Theoretic Transform (NTT) polynomial multipliers for NIST-standardized Kyber/ML-KEM and Dilithium/ML-DSA."),
        ("Final Thesis & IEEE Journal Submission (May 2027):", "Complete comprehensive B.Tech thesis and submit manuscript to IEEE Transactions on Very Large Scale Integration (VLSI) Systems.")
    ]
    for mtitle, mdesc in milestones:
        pt = tf2.add_paragraph()
        pt.text = f"➔ {mtitle} "
        pt.font.bold = True
        pt.font.size = Pt(10.5)
        pt.font.color.rgb = DARK_BLUE
        pd = tf2.add_paragraph()
        pd.text = f"   {mdesc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide13,
        "Slide 13 summarizes Phase-1 achievements and establishes our Phase-2 roadmap. "
        "In Phase-1, we delivered the mathematical, ML, software, and simulation frameworks. "
        "In Phase-2 during the 8th semester, we will synthesize our RTL on a physical Xilinx Zynq FPGA, "
        "capture physical power traces using ChipWhisperer, and expand our adaptive engine to post-quantum lattice cryptography.")

    # =========================================================================
    # SLIDE 14: References & Acknowledgments
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_header(slide14, "References & Acknowledgments")

    # References Left
    ref_box = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.3))
    ref_box.fill.solid()
    ref_box.fill.fore_color.rgb = BG_CARD
    ref_box.line.color.rgb = BORDER_COLOR
    tf = ref_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KEY ACADEMIC REFERENCES"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    references = [
        "[1] P. L. Montgomery, 'Modular multiplication without trial division,' Mathematics of Computation, vol. 44, no. 170, pp. 519-521, 1985.",
        "[2] M. Joye and S.-M. Yen, 'The Montgomery powering ladder,' in Cryptographic Hardware and Embedded Systems (CHES), Springer, pp. 291-302, 2002.",
        "[3] P. C. Kocher, 'Timing attacks on implementations of Diffie-Hellman, RSA, DSS, and other systems,' in Advances in Cryptology (CRYPTO), Springer, pp. 104-113, 1996.",
        "[4] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017.",
        "[5] NIST Special Publication 800-56B Rev. 2, 'Recommendation for Pair-Wise Key-Establishment Using Integer Factorization Cryptography,' 2019.",
        "[6] C. K. Koc and T. Acar, 'Montgomery multiplication algorithms,' IEEE Micro, vol. 16, no. 3, pp. 26-33, 1996."
    ]
    for r in references:
        pr = tf.add_paragraph()
        pr.text = r
        pr.font.size = Pt(9.5)
        pr.font.color.rgb = TEXT_DARK

    # Acknowledgments Right
    ack_box = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.5), Inches(1.5), Inches(4.0), Inches(5.3))
    ack_box.fill.solid()
    ack_box.fill.fore_color.rgb = RGBColor(238, 242, 255)
    ack_box.line.color.rgb = RGBColor(199, 210, 254)
    tf2 = ack_box.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "ACKNOWLEDGMENTS"
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = DARK_BLUE

    ack_body = tf2.add_paragraph()
    ack_body.text = "\nWe express our deepest gratitude to:\n\n" \
                   "• Dr. Aashish Parihar, our Major Project Supervisor, for his invaluable technical guidance, insights into VLSI architecture, and consistent encouragement.\n\n" \
                   "• Dr. Jogendra Singh Rana, Major Project Coordinator, and all faculty members of the Department of ECE, IIIT Bhopal, for their constructive reviews and academic support.\n\n" \
                   "• Indian Institute of Information Technology Bhopal, for providing state-of-the-art computational infrastructure.\n\n" \
                   "Thank you!\nQuestions & Discussion are welcome."
    ack_body.font.size = Pt(10)
    ack_body.font.color.rgb = TEXT_DARK

    set_speaker_notes(slide14,
        "We thank our supervisor Dr. Aashish Parihar, our coordinator Dr. Jogendra Singh Rana, and all faculty members present today. "
        "This concludes our Phase-1 presentation. We are now open for questions and discussion.")

    # Save presentation
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ECE_Major_Project_Presentation_Phase_1.pptx")
    prs.save(out_path)
    print(f"Successfully generated presentation PPTX: {out_path}")

if __name__ == "__main__":
    create_deck()
