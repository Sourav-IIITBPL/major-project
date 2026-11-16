"""
Train Decision Tree & Random Forest Classifiers for Cryptographic Strategy Prediction.
Targeting Hardware Cost and Execution Efficiency.
"""

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train(target_col: str = "label_lowest_hw_cost"):
    data_path = "major/data/dataset.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing {data_path}. Run generate_dataset.py first.")
        
    df = pd.read_csv(data_path)
    
    feature_cols = [
        "bit_length", "hamming_weight", "zero_density",
        "longest_zero_run", "avg_zero_run", "longest_one_run",
        "trailing_zeros", "wnaf_weight", "wnaf_zero_density",
        "longest_wnaf_zero_run"
    ]
    
    print(f"Target column: {target_col}")
    class_counts = df[target_col].value_counts()
    print("Class distribution:\n", class_counts)
    
    # Filter out rare classes if any has < 2 samples
    valid_classes = class_counts[class_counts >= 2].index
    df_filtered = df[df[target_col].isin(valid_classes)]
    
    X = df_filtered[feature_cols]
    y = df_filtered[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    print(f"\nTrain size: {len(X_train)} | Test size: {len(X_test)}")
    
    # 1. Decision Tree (Interpretable, compilable to C/Python if-else)
    dt = DecisionTreeClassifier(max_depth=4, random_state=42)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    acc_dt = accuracy_score(y_test, y_pred_dt)
    
    print("=" * 60)
    print(f"Decision Tree Accuracy: {acc_dt * 100:.2f}%")
    print(classification_report(y_test, y_pred_dt))
    
    # Feature Importances
    importances = sorted(zip(feature_cols, dt.feature_importances_), key=lambda x: x[1], reverse=True)
    print("Top Feature Drivers:")
    for f_name, imp in importances:
        if imp > 0.005:
            print(f"  - {f_name:<25}: {imp * 100:.2f}%")
            
    # 2. Random Forest
    rf = RandomForestClassifier(n_estimators=40, max_depth=5, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    print("=" * 60)
    print(f"Random Forest Accuracy: {acc_rf * 100:.2f}%")
    
    # Save models
    os.makedirs("major/data", exist_ok=True)
    joblib.dump(rf, "major/data/model_rf.joblib")
    joblib.dump(dt, "major/data/model_dt.joblib")
    
    # 3. Export Tree Rules
    print("\nDecision Tree Rules Logic:")
    tree_rules = export_text(dt, feature_names=feature_cols)
    print(tree_rules)
    
    # 4. Generate Compiled Standalone Python Predictor
    generate_compiled_code(dt, feature_cols, list(dt.classes_))
    
    return dt, rf

def generate_compiled_code(tree, feature_names, class_names):
    """Compiles Decision Tree to static python if-else (0 microsecond latency)."""
    from sklearn.tree import _tree
    tree_ = tree.tree_
    
    lines = []
    lines.append('"""Static Compiled Decision Tree for Zero-Overhead Inference."""\n')
    lines.append("def predict_strategy(feats: dict) -> str:")
    
    def recurse(node, depth):
        indent = "    " * (depth + 1)
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_names[tree_.feature[node]]
            threshold = tree_.threshold[node]
            lines.append(f"{indent}if feats['{name}'] <= {threshold:.4f}:")
            recurse(tree_.children_left[node], depth + 1)
            lines.append(f"{indent}else:")
            recurse(tree_.children_right[node], depth + 1)
        else:
            class_idx = tree_.value[node].argmax()
            predicted = class_names[class_idx]
            lines.append(f"{indent}return '{predicted}'")
            
    recurse(0, 0)
    code = "\n".join(lines) + "\n"
    
    with open("major/src/ml/compiled_predictor.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Generated static predictor in: major/src/ml/compiled_predictor.py")

if __name__ == "__main__":
    train(target_col="label_lowest_hw_cost")
