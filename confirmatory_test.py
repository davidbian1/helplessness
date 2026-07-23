"""Pre-registered confirmatory test: hostile feedback vs. accurate feedback.
This is the ORIGINAL confirmatory test (already run; result documented in
README.md). Re-running this file reruns the identical design on the same
seed offset -- for an independent replication with fresh seeds, use
replication_test.py instead.

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

Result (already obtained): 76.1% accurate vs 68.2% hostile, p=4.9e-05,
significant. See README.md for full writeup.

Usage:
    python confirmatory_test.py            # ~2000 API calls, ~40-65 min
    python confirmatory_test.py --dry-run
"""

import argparse

from confirmatory import run_confirmatory

SEED_OFFSET = 5000
REPLICATES = 20
TEST_PER_REPLICATE = 50  # 20 x 50 = 1000 per condition

CONDITIONS = [
    ("accurate_feedback", "accurate", "plain"),
    ("hostile_feedback", "hostile", "hostile"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_confirmatory(
        label="confirmatory",
        hypothesis="accuracy(hostile_feedback) < accuracy(accurate_feedback)",
        conditions=CONDITIONS,
        primary="hostile_feedback",
        secondary="accurate_feedback",
        seed_offset=SEED_OFFSET,
        replicates=REPLICATES,
        test_per_replicate=TEST_PER_REPLICATE,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
