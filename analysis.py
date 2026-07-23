"""Aggregates per-response results into a comparison table."""


def summarize(results):
    """Groups results by condition and computes accuracy plus no-answer rate.

    no_answer_rate is purely mechanical (extracted_answer is None — the
    response never produced a parseable "Answer: <number>" line, usually
    because it started reasoning despite instructions not to and got cut
    off by MAX_TOKENS). Unlike the earlier keyword-based "give-up" detector
    (removed for being unreliable and always 0%), this is a direct,
    unambiguous signal, and it isn't 0% everywhere in practice — it's what
    first surfaced the hostile-feedback condition's format-breaking behavior.
    """
    by_condition = {}
    for r in results:
        by_condition.setdefault(r["condition"], []).append(r)

    summary = {}
    for condition, rows in by_condition.items():
        n = len(rows)
        n_correct = sum(1 for r in rows if r["is_correct"])
        n_no_answer = sum(1 for r in rows if r["extracted_answer"] is None)
        summary[condition] = {
            "n": n,
            "accuracy": n_correct / n if n else 0.0,
            "no_answer_rate": n_no_answer / n if n else 0.0,
        }
    return summary


def format_table(summary):
    lines = [
        "| Condition | N | Accuracy | No-answer rate |",
        "|---|---|---|---|",
    ]
    for condition, stats in summary.items():
        lines.append(
            f"| {condition} | {stats['n']} | {stats['accuracy']:.1%} | "
            f"{stats['no_answer_rate']:.1%} |"
        )
    return "\n".join(lines)
