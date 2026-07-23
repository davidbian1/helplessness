"""Shared runner for pre-registered confirmatory tests.

The discipline every caller of run_confirmatory() must follow: one
hypothesis, one one-sided Fisher's exact test, one pre-committed sample
size decided before running (not after seeing partial results), on seeds
disjoint from every other run in this project, executed once, reported
regardless of outcome. See confirmatory_test.py for the original
worked example and rationale.
"""

import json
from datetime import datetime
from pathlib import Path

from scipy.stats import fisher_exact

from run_experiment import get_client, run_replicate

RESULTS_DIR = Path(__file__).parent / "results"


def run_confirmatory(label, hypothesis, conditions, primary, secondary,
                      seed_offset, replicates=20, test_per_replicate=50,
                      dry_run=False):
    """Runs `replicates` independent seed triples (base seed_offset, disjoint
    ranges for problem/attempt/shuffle seeds), pools results, and performs
    the single pre-specified test: accuracy(primary) < accuracy(secondary),
    one-sided Fisher's exact, alpha=0.05.

    conditions: full (name, feedback_kind, style) list to run per replicate
      (usually just [primary_spec, secondary_spec], but can include a third
      condition run alongside for descriptive purposes -- only primary vs
      secondary is tested).
    primary/secondary: condition_name strings identifying which of the run
      conditions are being compared. Hypothesis is primary < secondary.
    """
    client = None if dry_run else get_client()

    all_results = []
    for i in range(replicates):
        problem_seed = seed_offset + i
        attempt_seed = seed_offset + 1000 + i
        shuffle_seed = seed_offset + 2000 + i
        print(f"\n=== [{label}] Replicate {i+1}/{replicates} "
              f"(seeds {problem_seed}/{attempt_seed}/{shuffle_seed}) ===")
        all_results += run_replicate(
            client, problem_seed, attempt_seed, shuffle_seed,
            n_test=test_per_replicate, dry_run=dry_run, replicate_id=i,
            conditions=conditions,
        )

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = RESULTS_DIR / f"raw_{label}_{timestamp}.json"
    raw_path.write_text(json.dumps(all_results, indent=2))

    a_rows = [r for r in all_results if r["condition"] == secondary]
    b_rows = [r for r in all_results if r["condition"] == primary]
    a_correct, a_total = sum(r["is_correct"] for r in a_rows), len(a_rows)
    b_correct, b_total = sum(r["is_correct"] for r in b_rows), len(b_rows)

    # table row 0 = secondary (expected better), row 1 = primary (expected worse)
    # alternative="greater" tests row0's odds of correct > row1's -- i.e.
    # secondary accuracy > primary accuracy, exactly the pre-registered H.
    table = [[a_correct, a_total - a_correct], [b_correct, b_total - b_correct]]
    odds_ratio, p_value = fisher_exact(table, alternative="greater")

    verdict = "SIGNIFICANT" if p_value < 0.05 else "NOT significant"
    n_per_condition = test_per_replicate * replicates

    report = f"""# {label}: confirmatory result

H: {hypothesis}
Test: one-sided Fisher's exact test, alpha = 0.05
Pre-committed N: {n_per_condition} per condition
Seed offset: {seed_offset}

## Result

{secondary}: {a_correct}/{a_total} ({a_correct/a_total:.1%})
{primary}: {b_correct}/{b_total} ({b_correct/b_total:.1%})

p-value (one-sided): {p_value:.6f}
odds ratio: {odds_ratio:.3f}

## Verdict: {verdict} at alpha=0.05

This is the sole pre-registered analysis for this comparison. No further
tests, conditions, or seeds should be added to try to change this result --
if it's null, that is the answer this experiment produced.
"""
    report_path = RESULTS_DIR / f"result_{label}_{timestamp}.md"
    report_path.write_text(report)

    print("\n" + report)
    print(f"Raw results: {raw_path}")
    print(f"Report:      {report_path}")

    return {
        "p_value": p_value, "odds_ratio": odds_ratio, "verdict": verdict,
        "raw_path": raw_path, "report_path": report_path,
    }
