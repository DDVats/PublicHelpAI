"""
PublicHelp AI - Chart Generator for Presentation and Reports
Generates publication-quality charts for model evaluation, metrics, and architecture.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = "reports/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0

def generate_benchmark_chart():
    models = ['Lexical (TF-IDF)', 'Dense (all-MiniLM)', 'Hybrid RRF', 'Hybrid RRF + MMR (Ours)']
    p5 = [0.1037, 0.0519, 0.0889, 0.0963]
    ndcg5 = [0.1331, 0.0780, 0.1128, 0.1220]
    mrr = [0.2107, 0.1576, 0.1866, 0.2000]

    x = np.arange(len(models))
    width = 0.26

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    rects1 = ax.bar(x - width, p5, width, label='Precision@5', color='#3B82F6', edgecolor='#1D4ED8', linewidth=1.2, zorder=3)
    rects2 = ax.bar(x, ndcg5, width, label='NDCG@5', color='#10B981', edgecolor='#047857', linewidth=1.2, zorder=3)
    rects3 = ax.bar(x + width, mrr, width, label='MRR', color='#F59E0B', edgecolor='#B45309', linewidth=1.2, zorder=3)

    ax.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=12, fontweight='bold', color='#1E293B', labelpad=10)
    ax.set_title('Recommender Retrieval & Ranking Benchmark (27 Test Queries)', fontsize=14, fontweight='bold', color='#0F172A', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10.5, fontweight='bold', color='#334155')
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#E2E8F0', fontsize=10.5, loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#94A3B8', zorder=0)
    ax.set_ylim(0, 0.25)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1E293B')

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "model_benchmark.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def generate_recsys_health_chart():
    metrics = ['Catalog Coverage', 'Intra-List Diversity', 'Persona Personalization']
    values = [100.0, 71.02, 31.63]
    colors = ['#10B981', '#6366F1', '#EC4899']

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    bars = ax.barh(metrics, values, color=colors, height=0.55, edgecolor='#334155', linewidth=1.2, zorder=3)
    ax.set_xlim(0, 115)
    ax.set_xlabel('Score / Percentage (%)', fontsize=12, fontweight='bold', color='#1E293B', labelpad=10)
    ax.set_title('RecSys Domain Health & Diversity Performance', fontsize=14, fontweight='bold', color='#0F172A', pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.5, color='#94A3B8', zorder=0)

    for bar, val in zip(bars, values):
        ax.text(val + 2, bar.get_y() + bar.get_height()/2, f"{val:.1f}%" if val != 71.02 else f"{val/100:.4f} (71.0%)",
                va='center', ha='left', fontsize=11, fontweight='bold', color='#0F172A')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "recsys_health.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

def generate_latency_chart():
    stages = ['Lexical TF-IDF', 'Sentence Transformer (GPU)', 'RRF + Eligibility Engine', 'Vectorized MMR Diversity', 'Total Response']
    latencies = [8.6, 13.3, 41.7, 0.8, 64.4] # Vectorized MMR is sub-millisecond

    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    bars = ax.bar(stages, latencies, color=['#38BDF8', '#818CF8', '#F472B6', '#34D399', '#F59E0B'], edgecolor='#1E293B', linewidth=1.1, zorder=3)
    ax.set_ylabel('Latency (milliseconds)', fontsize=11, fontweight='bold', color='#1E293B', labelpad=10)
    ax.set_title('End-to-End Pipeline Execution Latency Breakdown', fontsize=13, fontweight='bold', color='#0F172A', pad=15)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#94A3B8', zorder=0)
    ax.set_ylim(0, 80)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 1.5, f"{h:.1f} ms",
                ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0F172A')

    plt.xticks(rotation=12, ha='right', fontsize=9.5, fontweight='bold')
    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "latency_breakdown.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    generate_benchmark_chart()
    generate_recsys_health_chart()
    generate_latency_chart()
    print("All charts generated successfully.")
