"""
Enhancement 7: Per-Backend Model Trainer
==========================================
Trains a Decision Tree classifier for EACH hardware backend target
using backend-specific cost coefficients.

For each backend:
  - Re-labels the dataset using backend cost model (not generic formula)
  - Trains a Decision Tree (compilable to C)
  - Saves serialized model and compiled predictor

Usage:
    python multi_backend/train_per_backend.py
    python multi_backend/train_per_backend.py --backend fpga_radix4
"""

import sys
import os
import argparse
import warnings
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, classification_report

from multi_backend.backend_configs import BACKEND_CONFIGS, ALL_BACKEND_NAMES

FEATURE_COLS = [
    "bit_length", "hamming_weight", "zero_density",
    "longest_zero_run", "avg_zero_run", "longest_one_run",
    "trailing_zeros", "wnaf_weight", "wnaf_zero_density",
    "longest_wnaf_zero_run",
]

MODELS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
PLOTS_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")

STRATEGY_METRIC_COLS = {
    "Binary": ("bin_sqrs",  "bin_mults",  "bin_total_muls",  "bin_iters"),
    "NAF":    ("naf_sqrs",  "naf_mults",  "naf_total_muls",  "naf_iters"),
    "wNAF":   ("wnaf_sqrs", "wnaf_mults", "wnaf_total_muls", "wnaf_iters"),
    "VLIM":   ("vlim_sqrs", "vlim_mults", "vlim_total_muls", "vlim_iters"),
}


def _load_dataset():
    """Load extended or original dataset."""
    ext  = os.path.join(ROOT, "enhanced_dataset", "data", "dataset_extended.csv")
    orig = os.path.join(ROOT, "major", "data", "dataset.csv")
    path = ext if os.path.exists(ext) else orig
    print(f"[Dataset] {path}")
    return pd.read_csv(path)


def _derive_per_backend_labels(df: pd.DataFrame, backend_name: str) -> pd.Series:
    """
    Re-compute the optimal strategy label using backend-specific cost model.
    Strategy columns that must exist in the CSV (from generate_extended_dataset.py):
      bin_total_muls, bin_iters, bin_sqrs, bin_mults
      naf_total_muls, naf_iters, naf_sqrs, naf_mults   (etc.)

    If the per-strategy sqrs/mults are not separately stored, we approximate
    using the total_muls breakdown from the existing dataset structure.
    """
    cfg = BACKEND_CONFIGS[backend_name]
    cs  = cfg["cost_sqr"]
    cm  = cfg["cost_mult"]
    cc  = cfg["cost_ctrl"]

    # --- Check which columns are available ---
    # The original dataset stores per-strategy hw_cost columns;
    # we recompute using backend coefficients.
    # Available: bin_total_muls, bin_iters, bin_hw_cost ... etc.

    costs = {}

    # Binary: sqrs ≈ bit_length, mults ≈ hamming_weight, iters = bit_length
    costs["Binary"] = (
        df["bit_length"] * cs             # squarings
        + df["bin_total_muls"].sub(df["bit_length"], fill_value=0).clip(lower=0) * cm
        + df["bin_iters"] * cc
    )
    # Approximate: bin_mults = bin_total_muls - bin_iters (iters ≈ sqrs for binary)
    # Use original hw_cost ratios scaled by backend coefficients
    # Simple: scale the original hw_cost by (new coefficients / original coefficients)
    orig_cs, orig_cm, orig_cc = 1.0, 1.2, 0.15

    for strat, col_prefix in [("Binary", "bin"), ("NAF", "naf"), ("wNAF", "wnaf"), ("VLIM", "vlim")]:
        if f"{col_prefix}_hw_cost" in df.columns and f"{col_prefix}_iters" in df.columns:
            # Reconstruct: original hw_cost = sqrs*1.0 + mults*1.2 + precomp*1.2 + iters*0.15
            # We know iters; use hw_cost to back-calculate sqrs+mults portion
            orig_hw   = df[f"{col_prefix}_hw_cost"]
            orig_iter_contrib = df[f"{col_prefix}_iters"] * orig_cc
            sqr_mult_contrib  = (orig_hw - orig_iter_contrib).clip(lower=0)

            # Re-weight
            new_iter_contrib = df[f"{col_prefix}_iters"] * cc
            # For squarings vs multiplications breakdown we use total_muls:
            total_ops = df[f"{col_prefix}_total_muls"].clip(lower=1)
            sqrs_frac = df["bit_length"] / total_ops   # approximate sqrs fraction

            new_hw = (
                sqrs_frac * total_ops * cs               # squarings
                + (1 - sqrs_frac) * total_ops * cm       # multiplications
                + new_iter_contrib
            )
            costs[strat] = new_hw
        else:
            # Fallback: uniform scaling
            if f"{col_prefix}_hw_cost" in df.columns:
                scale = (cs + cm) / (orig_cs + orig_cm)
                costs[strat] = df[f"{col_prefix}_hw_cost"] * scale

    # Build label series
    cost_df = pd.DataFrame(costs)
    labels  = cost_df.idxmin(axis=1)
    return labels


def _generate_compiled_predictor(tree, feature_names, class_names, out_path):
    from sklearn.tree import _tree
    tree_  = tree.tree_
    lines  = [f'"""Compiled Decision Tree for {os.path.basename(out_path)}."""\n']
    lines.append("\ndef predict_strategy(feats: dict) -> str:")

    def recurse(node, depth):
        indent = "    " * (depth + 1)
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_names[tree_.feature[node]]
            thr  = tree_.threshold[node]
            lines.append(f"{indent}if feats['{name}'] <= {thr:.4f}:")
            recurse(tree_.children_left[node],  depth + 1)
            lines.append(f"{indent}else:")
            recurse(tree_.children_right[node], depth + 1)
        else:
            cls_idx = tree_.value[node].argmax()
            lines.append(f"{indent}return '{class_names[cls_idx]}'")

    recurse(0, 0)
    code = "\n".join(lines) + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)


def train_for_backend(backend_name: str, df: pd.DataFrame):
    cfg = BACKEND_CONFIGS[backend_name]
    print(f"\n{'='*65}")
    print(f"  Training for backend: [{backend_name}]")
    print(f"  C_sqr={cfg['cost_sqr']}  C_mult={cfg['cost_mult']}  C_ctrl={cfg['cost_ctrl']}")
    print(f"  {cfg['description'][:60]}…")
    print(f"{'='*65}")

    # Re-derive labels
    labels = _derive_per_backend_labels(df, backend_name)
    df     = df.copy()
    df["backend_label"] = labels

    counts = df["backend_label"].value_counts()
    print(f"\n  Label distribution for [{backend_name}]:")
    for cls, cnt in counts.items():
        print(f"    {cls:12s}: {cnt:5d} ({cnt/len(df)*100:.1f}%)")

    # Filter rare
    valid = counts[counts >= 2].index
    df    = df[df["backend_label"].isin(valid)].copy()
    classes = sorted(df["backend_label"].unique().tolist())

    X = df[FEATURE_COLS]
    y = df["backend_label"]

    if len(classes) < 2:
        print(f"  [Skip] Only one class for backend '{backend_name}' – skipping.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    dt = DecisionTreeClassifier(max_depth=5, random_state=42, class_weight="balanced")
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)

    print(f"\n  Test Accuracy : {acc*100:.2f}%")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\n  Top Feature Importances:")
    for feat, imp in sorted(
        zip(FEATURE_COLS, dt.feature_importances_), key=lambda x: x[1], reverse=True
    ):
        if imp > 0.005:
            bar = "█" * int(imp * 50)
            print(f"    {feat:28s}: {imp*100:5.2f}%  {bar}")

    print("\n  Decision Tree Rules:")
    print(export_text(dt, feature_names=FEATURE_COLS))

    # Save model
    os.makedirs(MODELS_DIR, exist_ok=True)
    model_path = os.path.join(MODELS_DIR, f"model_{backend_name}.joblib")
    joblib.dump(dt, model_path)
    print(f"  → Model saved: {model_path}")

    # Save compiled predictor
    pred_path = os.path.join(MODELS_DIR, f"compiled_predictor_{backend_name}.py")
    _generate_compiled_predictor(dt, FEATURE_COLS, classes, pred_path)
    print(f"  → Compiled predictor: {pred_path}")

    # Save label distribution bar chart
    os.makedirs(PLOTS_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=120)
    bars = ax.bar(counts.index, counts.values, color=["#e74c3c","#3498db","#2ecc71","#9b59b6"],
                  edgecolor="black")
    ax.bar_label(bars, padding=3, fontsize=10, fontweight="bold")
    ax.set_title(f"Strategy Distribution – [{backend_name}]", fontsize=12, fontweight="bold")
    ax.set_ylabel("Sample Count")
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    chart_path = os.path.join(PLOTS_DIR, f"distribution_{backend_name}.png")
    fig.savefig(chart_path)
    plt.close(fig)
    print(f"  → Distribution chart: {chart_path}")

    return {"backend": backend_name, "accuracy": acc, "classes": classes}


def dispatch_for_backend(feats: dict, backend_name: str) -> str:
    """
    Runtime dispatch: load the model for the target backend and predict.
    Falls back to the default compiled predictor if model not found.
    """
    model_path = os.path.join(MODELS_DIR, f"model_{backend_name}.joblib")
    if not os.path.exists(model_path):
        # Fallback: load original compiled predictor
        from major.src.ml.compiled_predictor import predict_strategy
        return predict_strategy(feats)

    dt = joblib.load(model_path)
    row = [[feats[c] for c in FEATURE_COLS]]
    return dt.predict(row)[0]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train per-backend strategy classifiers."
    )
    parser.add_argument(
        "--backend", choices=ALL_BACKEND_NAMES + ["all"], default="all",
        help="Which backend to train for (default: all)."
    )
    args = parser.parse_args()

    df = _load_dataset()
    summary = []

    targets = ALL_BACKEND_NAMES if args.backend == "all" else [args.backend]
    for backend in targets:
        res = train_for_backend(backend, df)
        if res:
            summary.append(res)

    if summary:
        print("\n" + "="*65)
        print("  MULTI-BACKEND TRAINING SUMMARY")
        print("="*65)
        print(f"  {'Backend':<22} {'Accuracy':>10}  {'Classes'}")
        print("  " + "-"*55)
        for s in summary:
            print(f"  {s['backend']:<22} {s['accuracy']*100:>9.2f}%  {s['classes']}")
        print(f"\n  Models saved → {MODELS_DIR}")
        print(f"  Plots  saved → {PLOTS_DIR}")
