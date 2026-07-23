"""Renders a static whiteboard-style summary of the experiment design as a PNG.
Doesn't depend on any run results — just documents the fixed methodology.

Usage:
    python make_design_diagram.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUTPUT_PATH = Path(__file__).parent / "results" / "design_diagram.png"


def _box(ax, center, width, height, title, subtitle=None, facecolor="#eef2ff", edgecolor="#4338ca"):
    x, y = center[0] - width / 2, center[1] - height / 2
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.3, edgecolor=edgecolor, facecolor=facecolor,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(center[0], center[1] + height * 0.16, title, ha="center", va="center",
                 fontsize=10, fontweight="bold", color="#111827")
        ax.text(center[0], center[1] - height * 0.22, subtitle, ha="center", va="center",
                 fontsize=8.5, color="#374151")
    else:
        ax.text(center[0], center[1], title, ha="center", va="center",
                 fontsize=10, fontweight="bold", color="#111827")


def _arrow(ax, start, end, color="#6b7280"):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=13,
        color=color, linewidth=1.3, shrinkA=0, shrinkB=0,
    ))


def plot_design_diagram(output_path=OUTPUT_PATH):
    fig, ax = plt.subplots(figsize=(8, 6.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(3.2, 10.6)
    ax.axis("off")
    ax.set_title("Learned-helplessness analog: experiment design", fontsize=13, fontweight="bold", pad=12)

    # Row 1
    _box(ax, (5, 9.6), 4.2, 0.9, "30 word problems", "10 conditioning + 20 test")
    _arrow(ax, (5, 9.15), (5, 8.65))

    # Row 2
    _box(ax, (5, 8.2), 3.6, 0.9, "Simulated attempts", "70% correct (fixed)")
    _arrow(ax, (5, 7.75), (3.4, 7.25))
    _arrow(ax, (5, 7.75), (6.6, 7.25))

    # Row 3 (fork)
    _box(ax, (3.4, 6.8), 3.2, 0.9, "Accurate feedback", "matches correctness",
         facecolor="#dcfce7", edgecolor="#15803d")
    _box(ax, (6.6, 6.8), 3.2, 0.9, "Random feedback", "shuffled, uncorrelated",
         facecolor="#fee2e2", edgecolor="#b91c1c")
    _arrow(ax, (3.4, 6.35), (3.4, 5.85))
    _arrow(ax, (6.6, 6.35), (6.6, 5.85))

    # Row 4
    _box(ax, (3.4, 5.4), 3.2, 0.9, "20 test problems", "no feedback given",
         facecolor="#dcfce7", edgecolor="#15803d")
    _box(ax, (6.6, 5.4), 3.2, 0.9, "20 test problems", "no feedback given",
         facecolor="#fee2e2", edgecolor="#b91c1c")
    _arrow(ax, (3.4, 4.95), (4.3, 4.45))
    _arrow(ax, (6.6, 4.95), (5.7, 4.45))

    # Row 5 (merge)
    _box(ax, (5, 4.0), 4.2, 0.9, "Compare results", "accuracy vs give-up rate",
         facecolor="#fef9c3", edgecolor="#a16207")

    fig.tight_layout()
    output_path.parent.mkdir(exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    path = plot_design_diagram()
    print(f"Saved to {path}")
