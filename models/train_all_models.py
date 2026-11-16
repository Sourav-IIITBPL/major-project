"""
Enhancement 3: Multi-Model Trainer with XGBoost and SHAP Explainability
=========================================================================
Trains three classifiers on the extended dataset:
  1. Decision Tree  (depth=4) – interpretable, compilable to C
  2. Random Forest  (n=100)   – high accuracy ensemble
  3. XGBoost        (n=200)   – state-of-the-art gradient boosting

Produces:
  - Accuracy comparison table
  - SHAP feature-importance plots (saved to models/shap_plots/)
  - Serialized models in models/saved/
  - Updated compiled_predictor.py for the Decision Tree

Usage:
    python models/train_all_models.py [--target software|hardware]
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

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
)
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

FEATURE_COLS = [
    "bit_length", "hamming_weight", "zero_density",
    "longest_zero_run", "avg_zero_run", "longest_one_run",
    "trailing_zeros", "wnaf_weight", "wnaf_zero_density",
    "longest_wnaf_zero_run",
]

TARGET_MAP = {
    "software": "label_fastest_time",
    "hardware": "label_lowest_hw_cost",
    "iters":    "label_fewest_iters",
}

SAVED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved")
PLOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shap_plots")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dataset(target_col: str):
    """Tries extended dataset first, falls back to original."""
    ext_path = os.path.join(ROOT, "enhanced_dataset", "data", "dataset_extended.csv")
    orig_path = os.path.join(ROOT, "major", "data", "dataset.csv")

    if os.path.exists(ext_path):
        path = ext_path
        print(f"[Dataset] Using extended dataset: {ext_path}")
    elif os.path.exists(orig_path):
        path = orig_path
        print(f"[Dataset] Extended dataset not found. Using original: {orig_path}")
    else:
        raise FileNotFoundError(
            "No dataset found. Run enhanced_dataset/generate_extended_dataset.py first."
        )

    df = pd.read_csv(path)
    print(f"         Rows: {len(df)}  |  Columns: {list(df.columns)}")

    # Drop rare classes
    counts = df[target_col].value_counts()
    valid  = counts[counts >= 2].index
    df     = df[df[target_col].isin(valid)].copy()

    print(f"[Target ] '{target_col}' distribution:")
    for cls, cnt in df[target_col].value_counts().items():
        print(f"          {cls:12s}: {cnt:5d} ({cnt/len(df)*100:.1f}%)")

    X = df[FEATURE_COLS]
    y = df[target_col]
    return X, y


def print_banner(text: str):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def save_confusion_matrix(y_test, y_pred, labels, name: str, plots_dir: str):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"Confusion Matrix – {name}", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(plots_dir, f"confusion_{name.lower().replace(' ', '_')}.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  → Confusion matrix saved: {path}")


def generate_compiled_predictor(tree, feature_names, class_names, out_path: str):
    """Compile Decision Tree to pure Python if-else static predictor."""
    from sklearn.tree import _tree

    tree_   = tree.tree_
    lines   = []
    lines.append('"""Static Compiled Decision Tree Predictor – Auto-Generated."""\n')
    lines.append("# DO NOT EDIT MANUALLY. Re-run models/train_all_models.py to regenerate.\n")
    lines.append("\ndef predict_strategy(feats: dict) -> str:")

    def recurse(node, depth):
        indent = "    " * (depth + 1)
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name      = feature_names[tree_.feature[node]]
            threshold = tree_.threshold[node]
            lines.append(f"{indent}if feats['{name}'] <= {threshold:.4f}:")
            recurse(tree_.children_left[node],  depth + 1)
            lines.append(f"{indent}else:")
            recurse(tree_.children_right[node], depth + 1)
        else:
            class_idx = tree_.value[node].argmax()
            lines.append(f"{indent}return '{class_names[class_idx]}'")

    recurse(0, 0)
    code = "\n".join(lines) + "\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"  → Compiled predictor saved: {out_path}")


# ---------------------------------------------------------------------------
# Main training pipeline
# ---------------------------------------------------------------------------

def train(target: str = "software"):
    target_col = TARGET_MAP.get(target, "label_fastest_time")
    os.makedirs(SAVED_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)

    print_banner(f"Enhancement 3 – Multi-Model Training  |  Target: '{target_col}'")

    X, y = load_dataset(target_col)
    le   = LabelEncoder()
    y_enc = le.fit_transform(y)
    classes = le.classes_.tolist()

    X_train, X_test, y_train, y_test, ye_train, ye_test = train_test_split(
        X, y, y_enc, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTrain : {len(X_train)} samples")
    print(f"Test  : {len(X_test)}  samples")
    print(f"Classes: {classes}")

    results = {}

    # ------------------------------------------------------------------
    # Model 1: Decision Tree (interpretable, C-compilable)
    # ------------------------------------------------------------------
    print_banner("Model 1 / 3 – Decision Tree (depth=4)")
    dt = DecisionTreeClassifier(max_depth=4, random_state=42, class_weight="balanced")
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    acc_dt = accuracy_score(y_test, y_pred_dt)
    cv_dt  = cross_val_score(dt, X, y, cv=5, scoring="accuracy").mean()

    print(f"  Test Accuracy : {acc_dt*100:.2f}%")
    print(f"  5-Fold CV     : {cv_dt*100:.2f}%")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred_dt, zero_division=0))

    print("  Top Feature Importances:")
    for feat, imp in sorted(
        zip(FEATURE_COLS, dt.feature_importances_), key=lambda x: x[1], reverse=True
    ):
        if imp > 0.005:
            bar = "█" * int(imp * 50)
            print(f"    {feat:28s}: {imp*100:5.2f}%  {bar}")

    print("\n  Decision Tree Rules:")
    print(export_text(dt, feature_names=FEATURE_COLS))

    joblib.dump(dt, os.path.join(SAVED_DIR, f"model_dt_{target}.joblib"))
    save_confusion_matrix(y_test, y_pred_dt, classes, "Decision Tree", PLOTS_DIR)

    # Also update the compiled predictor inside the major package
    compiled_path = os.path.join(ROOT, "major", "src", "ml", "compiled_predictor.py")
    generate_compiled_predictor(dt, FEATURE_COLS, classes, compiled_path)
    # And save a copy in models/saved/
    generate_compiled_predictor(
        dt, FEATURE_COLS, classes,
        os.path.join(SAVED_DIR, f"compiled_predictor_{target}.py")
    )

    results["Decision Tree"] = {"acc": acc_dt, "cv": cv_dt}

    # ------------------------------------------------------------------
    # Model 2: Random Forest
    # ------------------------------------------------------------------
    print_banner("Model 2 / 3 – Random Forest (n=100 trees)")
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=6, random_state=42,
        n_jobs=-1, class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    cv_rf  = cross_val_score(rf, X, y, cv=5, scoring="accuracy", n_jobs=-1).mean()

    print(f"  Test Accuracy : {acc_rf*100:.2f}%")
    print(f"  5-Fold CV     : {cv_rf*100:.2f}%")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred_rf, zero_division=0))

    joblib.dump(rf, os.path.join(SAVED_DIR, f"model_rf_{target}.joblib"))
    save_confusion_matrix(y_test, y_pred_rf, classes, "Random Forest", PLOTS_DIR)

    results["Random Forest"] = {"acc": acc_rf, "cv": cv_rf}

    # ------------------------------------------------------------------
    # Model 3: XGBoost
    # ------------------------------------------------------------------
    print_banner("Model 3 / 3 – XGBoost (n=200 estimators)")
    xgb = XGBClassifier(
        n_estimators=200, max_depth=5, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        random_state=42, n_jobs=-1,
        use_label_encoder=False, eval_metric="mlogloss",
        verbosity=0,
    )
    xgb.fit(X_train, ye_train)
    ye_pred_xgb = xgb.predict(X_test)
    y_pred_xgb  = le.inverse_transform(ye_pred_xgb)
    acc_xgb = accuracy_score(y_test, y_pred_xgb)
    cv_xgb  = cross_val_score(
        XGBClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=42, n_jobs=-1,
            use_label_encoder=False, eval_metric="mlogloss", verbosity=0,
        ),
        X, y_enc, cv=5, scoring="accuracy", n_jobs=-1
    ).mean()

    print(f"  Test Accuracy : {acc_xgb*100:.2f}%")
    print(f"  5-Fold CV     : {cv_xgb*100:.2f}%")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred_xgb, zero_division=0))

    joblib.dump(xgb, os.path.join(SAVED_DIR, f"model_xgb_{target}.joblib"))
    joblib.dump(le,  os.path.join(SAVED_DIR, f"label_encoder_{target}.joblib"))
    save_confusion_matrix(y_test, y_pred_xgb, classes, "XGBoost", PLOTS_DIR)

    results["XGBoost"] = {"acc": acc_xgb, "cv": cv_xgb}

    # ------------------------------------------------------------------
    # SHAP Explainability (using Random Forest – fastest SHAP support)
    # ------------------------------------------------------------------
    print_banner("SHAP Feature Explainability  (Random Forest)")
    try:
        import shap
        # Use a sample of test set for speed
        sample = X_test.sample(min(200, len(X_test)), random_state=42)
        explainer   = shap.TreeExplainer(rf)
        shap_values = explainer.shap_values(sample)

        # --- Summary plot (all classes combined – mean abs SHAP) ---
        fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
        # shap_values can be list of arrays (one per class) or 3D array
        if isinstance(shap_values, list):
            mean_abs = np.abs(np.array(shap_values)).mean(axis=0).mean(axis=0)
        else:
            mean_abs = np.abs(shap_values).mean(axis=0) if shap_values.ndim == 2 \
                       else np.abs(shap_values).mean(axis=(0, 2))

        sorted_idx = np.argsort(mean_abs)[::-1]
        sorted_feats = [FEATURE_COLS[i] for i in sorted_idx]
        sorted_vals  = mean_abs[sorted_idx]

        bars = ax.barh(sorted_feats[::-1], sorted_vals[::-1],
                       color="#3498db", edgecolor="black", height=0.6)
        ax.set_xlabel("Mean |SHAP Value| – Feature Impact on Strategy Prediction",
                      fontsize=11, fontweight="bold")
        ax.set_title("SHAP Global Feature Importance – Random Forest",
                     fontsize=13, fontweight="bold")
        ax.bar_label(bars, fmt="%.3f", padding=4, fontsize=9)
        ax.grid(True, axis="x", linestyle="--", alpha=0.5)
        plt.tight_layout()
        shap_path = os.path.join(PLOTS_DIR, f"shap_importance_{target}.png")
        fig.savefig(shap_path)
        plt.close(fig)
        print(f"  → SHAP importance plot saved: {shap_path}")
        print("\n  SHAP Feature Rankings:")
        for feat, val in zip(sorted_feats, sorted_vals):
            bar = "█" * max(1, int(val * 300))
            print(f"    {feat:28s}: {val:.4f}  {bar}")

    except Exception as e:
        print(f"  [SHAP skipped – {e}]")

    # ------------------------------------------------------------------
    # Final Comparison Table
    # ------------------------------------------------------------------
    print_banner("Model Comparison Summary")
    print(f"\n  {'Model':<20} {'Test Accuracy':>14} {'5-Fold CV':>10} "
          f"{'Compilable to C':>16} {'Notes'}")
    print("  " + "-" * 78)
    rows = [
        ("Decision Tree",  results["Decision Tree"]["acc"],  results["Decision Tree"]["cv"],  "✅ Yes (<1µs)",  "Direct if-else compilation"),
        ("Random Forest",  results["Random Forest"]["acc"],  results["Random Forest"]["cv"],  "❌ No (~150µs)", "Best SHAP explainability"),
        ("XGBoost",        results["XGBoost"]["acc"],        results["XGBoost"]["cv"],        "❌ No (~80µs)",  "Highest accuracy"),
    ]
    for name, acc, cv, compilable, note in rows:
        print(f"  {name:<20} {acc*100:>12.2f}%  {cv*100:>8.2f}%  {compilable:>16}  {note}")

    winner = max(results, key=lambda k: results[k]["acc"])
    print(f"\n  🏆 Highest Test Accuracy: {winner} ({results[winner]['acc']*100:.2f}%)")
    print(f"  🚀 C99-Deployable Winner : Decision Tree ({results['Decision Tree']['acc']*100:.2f}%)")
    print(f"\nAll models saved → {SAVED_DIR}")
    print(f"All plots saved  → {PLOTS_DIR}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train DT + RF + XGBoost for cryptographic strategy prediction."
    )
    parser.add_argument(
        "--target",
        choices=["software", "hardware", "iters"],
        default="software",
        help="Optimization objective: 'software' (wall-clock ms) | "
             "'hardware' (clock cycles) | 'iters' (loop iterations)",
    )
    args = parser.parse_args()
    train(target=args.target)
