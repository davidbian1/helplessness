"""Aggregates per-response results into a comparison table."""


def summarize(results):
    """Groups results by condition and computes accuracy / give-up rate."""
    by_condition = {}
    for r in results:
        by_condition.setdefault(r["condition"], []).append(r)

    summary = {}
    for condition, rows in by_condition.items():
        n = len(rows)
        n_correct = sum(1 for r in rows if r["is_correct"])
        n_gaveup = sum(1 for r in rows if r["gave_up"])
        summary[condition] = {
            "n": n,
            "accuracy": n_correct / n if n else 0.0,
            "giveup_rate": n_gaveup / n if n else 0.0,
        }
    return summary


def format_table(summary):
    lines = [
        "| Condition | N | Accuracy | Give-up / Refusal Rate |",
        "|---|---|---|---|",
    ]
    for condition, stats in summary.items():
        lines.append(
            f"| {condition} | {stats['n']} | {stats['accuracy']:.1%} | "
            f"{stats['giveup_rate']:.1%} |"
        )
    return "\n".join(lines)
