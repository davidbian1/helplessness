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


def plot_replicate_variance(raw_path, output_path=None):
    """For multi-seed runs: accuracy per replicate per condition, as a line
    chart, to show whether the direction of any gap is consistent across
    independent seed draws or just bounces around.
    """
    results = json.loads(Path(raw_path).read_text())
    by_key = {}
    for r in results:
        by_key.setdefault((r["replicate_id"], r["condition"]), []).append(r)

    replicate_ids = sorted({r["replicate_id"] for r in results})
    conditions = ["accurate_feedback", "random_feedback"]
    colors = {"accurate_feedback": "#15803d", "random_feedback": "#b91c1c"}

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for condition in conditions:
        accs = []
        for rid in replicate_ids:
            rows = by_key.get((rid, condition), [])
            accs.append(100 * sum(r["is_correct"] for r in rows) / len(rows) if rows else 0)
        ax.plot(replicate_ids, accs, marker="o", label=condition, color=colors[condition])

    ax.set_xlabel("Replicate (independent seed draw)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 105)
    ax.set_xticks(replicate_ids)
    ax.set_title("Accuracy per replicate, by condition")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    fig.tight_layout()

    output_path = output_path or Path(raw_path).with_name(
        Path(raw_path).name.replace("raw_multiseed_", "variance_").replace(".json", ".png")
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
