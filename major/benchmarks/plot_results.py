"""
Publication-Quality Benchmark Visualizer for Major Project.
Generates charts for mentor presentation and research paper:
  1. Latency Scaling Curve (256-bit to 2048-bit)
  2. Multiplications Cut Comparison
  3. Hardware Iterations / Clock Cycles Reduction (VLIM vs Binary)
  4. Security vs Latency Tradeoff (Baseline vs Blinded-Adaptive)
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_plots():
    csv_path = "major/data/comprehensive_benchmark_results.csv"
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found. Run evaluate_all.py first.")
        return
        
    df = pd.read_csv(csv_path)
    output_dir = "major/docs/figures"
    os.makedirs(output_dir, exist_ok=True)
    
    # Aggregated averages
    summary = df.groupby(["bit_length", "mode"]).agg({
        "total_time_ms": "mean",
        "mults": "mean",
        "sqrs": "mean",
        "iters": "mean",
        "hw_cost": "mean"
    }).reset_index()
    
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    colors = {
        "fixed_binary": "#e74c3c",    # Red (Baseline)
        "fixed_naf": "#e67e22",       # Orange
        "fixed_wnaf": "#3498db",      # Blue
        "fixed_vlim": "#9b59b6",      # Purple
        "ml_adaptive": "#2ecc71",     # Green (Winner)
        "blinded_adaptive": "#1abc9c" # Teal (Secure)
    }
    labels = {
        "fixed_binary": "Binary (Baseline)",
        "fixed_naf": "Standard NAF",
        "fixed_wnaf": "Windowed NAF (w=3)",
        "fixed_vlim": "Adaptive VLIM",
        "ml_adaptive": "ML-Adaptive (Ours)",
        "blinded_adaptive": "Blinded-Adaptive (Secure)"
    }
    
    # -------------------------------------------------------------
    # Plot 1: Execution Time Scaling Across Bit Lengths
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    for mode in colors.keys():
        mode_data = summary[summary["mode"] == mode]
        if not mode_data.empty:
            ax.plot(
                mode_data["bit_length"], mode_data["total_time_ms"],
                marker='o', linewidth=2.2, label=labels[mode], color=colors[mode]
            )
            
    ax.set_title("Modular Exponentiation Latency Across Cryptographic Scales", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Cryptographic Exponent Scale (Bits)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Execution Latency (ms)", fontsize=11, fontweight='bold')
    ax.set_xticks([256, 512, 1024, 2048])
    ax.legend(frameon=True, fontsize=10, loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.6)
    
    fig.tight_layout()
    p1 = os.path.join(output_dir, "latency_scaling.png")
    fig.savefig(p1)
    plt.close(fig)
    print(f"Saved: {p1}")
    
    # -------------------------------------------------------------
    # Plot 2: 2048-Bit Multiplications Reduction (Bar Chart)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    data_2048 = summary[summary["bit_length"] == 2048].sort_values("mults", ascending=False)
    
    bar_modes = [m for m in data_2048["mode"] if m in colors]
    bar_vals = [data_2048[data_2048["mode"] == m]["mults"].values[0] for m in bar_modes]
    bar_colors = [colors[m] for m in bar_modes]
    bar_labels = [labels[m] for m in bar_modes]
    
    bars = ax.barh(bar_labels, bar_vals, color=bar_colors, edgecolor="black", height=0.6)
    ax.bar_label(bars, fmt='%.0f', padding=4, fontsize=9.5, fontweight='bold')
    
    ax.set_title("2048-Bit RSA: Total Multiplication Count by Strategy", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Number of Modular Multiplications (Lower is Better)", fontsize=11, fontweight='bold')
    ax.grid(True, linestyle="--", alpha=0.6, axis="x")
    
    fig.tight_layout()
    p2 = os.path.join(output_dir, "multiplications_comparison_2048.png")
    fig.savefig(p2)
    plt.close(fig)
    print(f"Saved: {p2}")
    
    # -------------------------------------------------------------
    # Plot 3: Hardware State-Machine Clock Cycles / Iterations
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    iter_vals = [data_2048[data_2048["mode"] == m]["iters"].values[0] for m in bar_modes]
    
    bars = ax.bar(bar_labels, iter_vals, color=bar_colors, edgecolor="black", width=0.55)
    ax.bar_label(bars, fmt='%.0f', padding=3, fontsize=9, fontweight='bold')
    
    ax.set_title("2048-Bit Hardware Loop Iterations / State-Machine Cycles", fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel("Loop Control Transitions (Lower is Better)", fontsize=11, fontweight='bold')
    plt.xticks(rotation=15, ha="right", fontsize=9.5, fontweight='bold')
    ax.grid(True, linestyle="--", alpha=0.6, axis="y")
    
    fig.tight_layout()
    p3 = os.path.join(output_dir, "hardware_cycles_comparison_2048.png")
    fig.savefig(p3)
    plt.close(fig)
    print(f"Saved: {p3}")
    
    print("\nAll presentation figures successfully generated in major/docs/figures/")

if __name__ == "__main__":
    generate_plots()
