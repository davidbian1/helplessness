"""Aggregates per-response results into a comparison table."""


def summarize(results):
    """Groups results by condition and computes accuracy."""
    by_condition = {}
    for r in results:
        by_condition.setdefault(r["condition"], []).append(r)

    summary = {}
    for condition, rows in by_condition.items():
        n = len(rows)
        n_correct = sum(1 for r in rows if r["is_correct"])
        summary[condition] = {
            "n": n,
            "accuracy": n_correct / n if n else 0.0,
        }
    return summary


def format_table(summary):
    lines = [
        "| Condition | N | Accuracy |",
        "|---|---|---|",
    ]
    for condition, stats in summary.items():
        lines.append(f"| {condition} | {stats['n']} | {stats['accuracy']:.1%} |")
    return "\n".join(lines)
