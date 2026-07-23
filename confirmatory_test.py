"""Pre-registered confirmatory test: hostile feedback vs. accurate feedback.

Everything before this script (single n=20 runs, the random-feedback
condition, the always_negative pilot, the hostile pilot, all the pooled
6-replicate multi-seed runs) was exploratory. Multiple manipulations and
multiple pairwise comparisons were tried without correction, across
overlapping data, with the analysis effectively chosen after looking at
results each time -- classic p-hacking, even though every individual number
reported was accurate. None of it constitutes evidence for or against the
hypothesis.

This script is the fix: ONE pre-specified hypothesis, ONE pre-specified
test, ONE pre-committed sample size decided by power analysis (not by what
looked promising), run ONCE on seeds that have never been touched by any
prior run in this project, analyzed with no further tweaking after seeing
the result.

Pre-registration (fixed before this script is run):
  H1: accuracy(hostile_feedback) < accuracy(accurate_feedback)
  Test: one-sided Fisher's exact test, alpha = 0.05
  N: 1000 problems per condition (REPLICATES x TEST_PER_REPLICATE below),
     chosen for ~81% power to detect a 6-percentage-point true gap around
     a ~70% baseline (see the power calculation in the conversation this
     script came from) -- not because it guarantees significance.
  Seeds: offset 5000+, disjoint from every seed used in every prior
     exploratory run in this project (which used seeds in the 0-250 range).
  The random_feedback condition is excluded entirely: it was already
     conclusively null (240 pooled calls, p=1.0) and including it here
     would just reopen a multiple-comparisons problem.

Usage:
    python confirmatory_test.py            # ~2000 API calls, ~40-65 min
    python confirmatory_test.py --dry-run
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from scipy.stats import fisher_exact

import config
from run_experiment import get_client, run_replicate

RESULTS_DIR = Path(__file__).parent / "results"

SEED_OFFSET = 5000
REPLICATES = 20
TEST_PER_REPLICATE = 50  # 20 x 50 = 1000 per condition

CONFIRMATORY_CONDITIONS = [
    ("accurate_feedback", "accurate", "plain"),
    ("hostile_feedback", "hostile", "hostile"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = None if args.dry_run else get_client()

    all_results = []
    for i in range(REPLICATES):
        problem_seed = SEED_OFFSET + i
        attempt_seed = SEED_OFFSET + 1000 + i
        shuffle_seed = SEED_OFFSET + 2000 + i
        print(f"\n=== Replicate {i+1}/{REPLICATES} (seeds {problem_seed}/{attempt_seed}/{shuffle_seed}) ===")
        all_results += run_replicate(
            client, problem_seed, attempt_seed, shuffle_seed,
            n_test=TEST_PER_REPLICATE, dry_run=args.dry_run, replicate_id=i,
            conditions=CONFIRMATORY_CONDITIONS,
        )

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = RESULTS_DIR / f"raw_confirmatory_{timestamp}.json"
    raw_path.write_text(json.dumps(all_results, indent=2))

    accurate = [r for r in all_results if r["condition"] == "accurate_feedback"]
    hostile = [r for r in all_results if r["condition"] == "hostile_feedback"]

    acc_correct = sum(r["is_correct"] for r in accurate)
    acc_total = len(accurate)
    hos_correct = sum(r["is_correct"] for r in hostile)
    hos_total = len(hostile)

    table = [
        [acc_correct, acc_total - acc_correct],
        [hos_correct, hos_total - hos_correct],
    ]
    odds_ratio, p_value = fisher_exact(table, alternative="greater")
    # alternative="greater" on [accurate, hostile] tests
    # odds_ratio(accurate correct : incorrect) > odds_ratio(hostile correct : incorrect),
    # i.e. accurate accuracy > hostile accuracy -- exactly H1.

    verdict = "SIGNIFICANT" if p_value < 0.05 else "NOT significant"

    report = f"""# Confirmatory test result

H1: accuracy(hostile_feedback) < accuracy(accurate_feedback)
Test: one-sided Fisher's exact test, alpha = 0.05
Pre-committed N: {TEST_PER_REPLICATE * REPLICATES} per condition

## Result

accurate_feedback: {acc_correct}/{acc_total} ({acc_correct/acc_total:.1%})
hostile_feedback:  {hos_correct}/{hos_total} ({hos_correct/hos_total:.1%})

p-value (one-sided): {p_value:.4f}
odds ratio: {odds_ratio:.3f}

## Verdict: {verdict} at alpha=0.05

This is the sole pre-registered analysis. No further tests, conditions, or
seeds should be added to try to change this result -- if it's null, that is
the answer this experiment produced.
"""
    report_path = RESULTS_DIR / f"confirmatory_result_{timestamp}.md"
    report_path.write_text(report)

    print("\n" + report)
    print(f"Raw results: {raw_path}")
    print(f"Report:      {report_path}")


if __name__ == "__main__":
    main()
