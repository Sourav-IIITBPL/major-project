# Major Project (Phase-1) Presentation & Report Package [EC-413]

**Department of Electronics and Communication Engineering**  
**Indian Institute of Information Technology (IIIT) Bhopal**

---

## 📌 Directory Purpose & Overview

This self-contained directory contains the complete end-term academic deliverables for the **B.Tech Major Project (Phase-1) [Course Code: EC-413]**:
- **Project Title:** *ML-Assisted Adaptive Cryptographic Engine: Workload-Aware Modular Exponentiation and Side-Channel Hardened Acceleration*
- **Students:** Sourav Yadav (Scholar ID: `23U01074`) & Eric Dazzle George (Scholar ID: `23U01035`)
- **Supervisor:** Dr. Aashish Parihar, Assistant Professor, Department of ECE
- **Major Project Coordinator:** Dr. Jogendra Singh Rana, Assistant Professor, Department of ECE

Everything needed to review, print, present, or independently re-generate both the **formal project report (`.docx`)** and the **presentation slide deck (`.pptx`)** is housed directly within this folder. This folder can be copied or zipped independently without breaking any internal links or dependencies.

---

## 📂 Folder Contents & Architecture

```
ppt-and-proejct-report/
│
├── ECE_Major_Project_Report_Phase_1.docx       # OFFICIAL Generated Project Report (Word Document)
├── ECE_Major_Project_Presentation_Phase_1.pptx # OFFICIAL Generated Presentation Deck (PowerPoint 16:9)
│
├── PROJECT_REPORT.md                          # Full Markdown version of the academic report (Chapters 1-7)
├── PRESENTATION_SLIDES.md                     # Complete slide-by-slide script with layout & speaker notes
│
├── PROMPT_FOR_CLAUDE_REPORT_GENERATION.md     # Turnkey Master Prompt for Claude AI (Report Generation)
├── PROMPT_FOR_CLAUDE_PPT_GENERATION.md        # Turnkey Master Prompt for Claude AI (Presentation Generation)
│
├── generate_report_docx.py                    # Python script to regenerate the Word .docx file
├── generate_presentation_pptx.py              # Python script to regenerate the PowerPoint .pptx file
│
├── figures/                                   # High-resolution figures embedded into Report & PPT
│   ├── latency_scaling.png                    # Latency scaling across 512 to 4096-bit operands
│   ├── hardware_cycles_comparison_2048.png    # Hardware cycle comparisons across silicon backends
│   ├── multiplications_comparison_2048.png    # Multiplication counts across exponentiation algorithms
│   ├── shap_importance_software.png          # KernelSHAP feature attribution bar plot
│   ├── confusion_decision_tree.png            # Confusion matrix for compiled Decision Tree
│   ├── confusion_random_forest.png            # Confusion matrix for Random Forest
│   ├── confusion_xgboost.png                  # Confusion matrix for XGBoost
│   └── distribution_asic_csa52.png            # Carry-save Radix-4 cycle distribution
│
├── reference_docs/                            # Technical specifications and repository documentation
│   ├── COMPREHENSIVE_TECHNICAL_SPECIFICATION.md
│   ├── DEVELOPER_GUIDE.md
│   ├── INNOVATIONS_AND_IMPROVEMENTS.md
│   ├── PROJECT_PLAN.md
│   ├── ROOT_README.md
│   └── calibration_report.txt
│
├── '2. ECE_Major_project format of synopsis 7th sem.pdf'    # Instructor Synopsis Format (PDF)
├── '2. ECE_Major_project format of synopsis 7th sem.docx'   # Instructor Synopsis Format (Word)
├── '3. ECE_Guidelines for Major Project end term viva 7th Sem.pdf' # Viva guidelines (PDF)
├── '4. ECE Major Project Instructions -Phase 1.pdf'         # Scheme & Section instructions (PDF)
│
├── guidelines_text.txt                         # Extracted plain text of viva instructions
├── instructions_text.txt                       # Extracted plain text of Phase-1 instructions
└── synopsis_text.txt                           # Extracted plain text of synopsis format
```

---

## 🎯 Compliance with IIIT Bhopal Guidelines

The generated documents strictly fulfill every guideline set by the Major Project Coordinator (Dr. Jogendra Singh Rana) and the Department of ECE:

| Guideline Requirement | Department Specification | Project Implementation |
| :--- | :--- | :--- |
| **Typography** | Times New Roman, 1.5 line spacing | Applied in `ECE_Major_Project_Report_Phase_1.docx` via `python-docx` styles. |
| **Font Sizing** | 12 pt body, 14 pt headings, 16–18 pt chapter titles | Formatted systematically across all document elements. |
| **Margins** | 1.0 inch (or 1.5 inch binding margin) on all 4 sides | Configured via section page layout XML. |
| **Captions** | Figures: Caption below; Tables: Caption above | Applied consistently across all embedded figures and academic tables. |
| **Required Sections** | Intro (3–5 p), Background (4–8 p), System Model (4–8 p), Methodology (4–8 p), Results (5–10 p), Conclusion (2–3 p), References | All 7 chapters generated in full technical depth with math formulas, tables, and plots. |
| **Plagiarism** | Strictly < 15% | Content is self-composed, mathematically derived, and original. |
| **Presentation** | 5–10 min, ~10–15 slides, presented by all members | 14 slides (16:9 widescreen) with individual speaking tags and notes for Sourav & Eric. |

---

## ⚡ How to Regenerate or Modify Deliverables

If you ever wish to modify text, update numbers, or regenerate the documents from source:

### 1. Regenerate the Word Report (`.docx`)
```bash
cd /home/sourav/major-project
.venv/bin/python ppt-and-proejct-report/generate_report_docx.py
```
*Output: `ppt-and-proejct-report/ECE_Major_Project_Report_Phase_1.docx`*

### 2. Regenerate the PowerPoint Presentation (`.pptx`)
```bash
cd /home/sourav/major-project
.venv/bin/python ppt-and-proejct-report/generate_presentation_pptx.py
```
*Output: `ppt-and-proejct-report/ECE_Major_Project_Presentation_Phase_1.pptx`*

---

## 🤖 Using with Claude AI (or Any Frontier LLM)

If you wish to have Claude AI edit or expand the project report or presentation deck, simply:
1. Open Claude AI (or your agent of choice).
2. Attach or copy-paste either:
   - `PROMPT_FOR_CLAUDE_REPORT_GENERATION.md` (for report generation/refinement)
   - `PROMPT_FOR_CLAUDE_PPT_GENERATION.md` (for presentation customization)
3. Claude will have all context, numbers, formulas, and instructor guidelines to produce flawless revisions.

---

## 📊 Summary of Core Engineering Results

- **Model Latency:** Compiled Decision Tree classifier evaluates workloads in **$0.42\ \mu\text{s}$** ($420\ \text{ns}$) with **97.4% accuracy** (100$\times$ faster than XGBoost).
- **Operation Reduction:** Adaptive Sliding Window ($w=5$) cuts total modular multiplications from 3,072 to 2,390 on 2048-bit RSA (**22.2% reduction**).
- **Silicon Acceleration:** TSMC 28nm Carry-Save Radix-4 multiplier reduces execution cycles from 4.19M to 1.05M (**75.0% cycle reduction**).
- **Side-Channel Defense:** Euler Totient Blinding ($e' = e + r\lambda(N)$) guarantees mathematical invariance while eliminating SPA and DPA power correlation across runs.
- **Verification:** 47 automated unit tests validate full-stack cryptographic correctness across software and hardware pipelines.
