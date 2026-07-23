"""Runs the accurate-vs-random feedback comparison across several independent
seed triples and pools the results.

A single seed run (run_experiment.py) is one draw of problems/attempts/
shuffle — its result could be idiosyncratic to that draw. This replicates
the whole experiment across N_REPLICATES seeds and reports both the pooled
comparison (bigger n) and the per-replicate breakdown (does the direction
hold up across draws, or does it bounce around?).

Usage:
    python run_multi_seed.py                  # 6 replicates, config.N_TEST each
    python run_multi_seed.py --replicates 10
    python run_multi_seed.py --dry-run
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import config
from analysis import format_table, summarize
from run_experiment import get_client, run_replicate

RESULTS_DIR = Path(__file__).parent / "results"

N_REPLICATES_DEFAULT = 6


def per_replicate_table(results):
    by_key = {}
    for r in results:
        key = (r["replicate_id"], r["condition"])
        by_key.setdefault(key, []).append(r)

    replicate_ids = sorted({r["replicate_id"] for r in results})
    lines = ["| Replicate | accurate_feedback | random_feedback |", "|---|---|---|"]
    for rid in replicate_ids:
        acc_rows = by_key.get((rid, "accurate_feedback"), [])
        rand_rows = by_key.get((rid, "random_feedback"), [])
        acc_pct = sum(r["is_correct"] for r in acc_rows) / len(acc_rows) if acc_rows else 0
        rand_pct = sum(r["is_correct"] for r in rand_rows) / len(rand_rows) if rand_rows else 0
        lines.append(f"| {rid} | {acc_pct:.0%} | {rand_pct:.0%} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=N_REPLICATES_DEFAULT,
                         help=f"Number of independent seed triples to run (default {N_REPLICATES_DEFAULT}).")
    parser.add_argument("--dry-run", action="store_true",
                         help="Build conditioning prompts without calling the API.")
    args = parser.parse_args()

    client = None if args.dry_run else get_client()

    all_results = []
    for i in range(args.replicates):
        # Distinct, deterministic seed triple per replicate.
        problem_seed = config.PROBLEM_SEED + i
        attempt_seed = config.ATTEMPT_SEED + 100 + i
        shuffle_seed = config.SHUFFLE_SEED + 200 + i
        print(f"\n=== Replicate {i} (seeds {problem_seed}/{attempt_seed}/{shuffle_seed}) ===")
        all_results += run_replicate(
            client, problem_seed, attempt_seed, shuffle_seed,
            dry_run=args.dry_run, replicate_id=i,
        )

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_path = RESULTS_DIR / f"raw_multiseed_{timestamp}.json"
    raw_path.write_text(json.dumps(all_results, indent=2))

    pooled_summary = summarize(all_results)
    pooled_table = format_table(pooled_summary)
    per_seed_table = per_replicate_table(all_results)

    report = (
        f"## Pooled across {args.replicates} replicates "
        f"(n={pooled_summary['accurate_feedback']['n']} per condition)\n\n"
        f"{pooled_table}\n\n"
        f"## Per-replicate breakdown\n\n{per_seed_table}\n"
    )
    table_path = RESULTS_DIR / f"comparison_multiseed_{timestamp}.md"
    table_path.write_text(report)

    print("\n" + report)
    print(f"Raw results:   {raw_path}")
    print(f"Summary table: {table_path}")

    if not args.dry_run:
        from visualize_results import plot_replicate_variance
        chart_path = plot_replicate_variance(raw_path)
        print(f"Variance chart: {chart_path}")


if __name__ == "__main__":
    main()
