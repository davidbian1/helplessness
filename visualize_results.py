"""Renders a bar chart comparing accuracy across conditions.

Usage:
    python visualize_results.py                  # uses the most recent results/raw_*.json
    python visualize_results.py results/raw_20260722_231000.json
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from analysis import summarize

RESULTS_DIR = Path(__file__).parent / "results"


def _latest_raw_file():
    candidates = sorted(RESULTS_DIR.glob("raw_*.json"))
    if not candidates:
        return None
    return candidates[-1]


def plot_comparison(raw_path, output_path=None):
    results = json.loads(Path(raw_path).read_text())
    summary = summarize(results)

    conditions = list(summary.keys())
    accuracy = [summary[c]["accuracy"] * 100 for c in conditions]

    x = range(len(conditions))

    fig, ax = plt.subplots(figsize=(6, 4.5))
    bars = ax.bar(list(x), accuracy, width=0.5, color="#2563eb")

    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 110)
    ax.set_title("Accuracy by conditioning")
    ax.set_xticks(list(x))
    ax.set_xticklabels(conditions)
    ax.bar_label(bars, fmt="%.0f%%", padding=3)
    fig.tight_layout()

    output_path = output_path or Path(raw_path).with_name(
        Path(raw_path).name.replace("raw_", "chart_").replace(".json", ".png")
    )
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_json", nargs="?", help="Path to a results/raw_*.json file (default: most recent).")
    args = parser.parse_args()

    raw_path = Path(args.raw_json) if args.raw_json else _latest_raw_file()
    if raw_path is None or not raw_path.exists():
        sys.exit("No results file found. Run run_experiment.py first, or pass a path explicitly.")

    output_path = plot_comparison(raw_path)
    print(f"Chart saved to {output_path}")


if __name__ == "__main__":
    main()
