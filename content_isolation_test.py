"""Isolates whether the confirmed hostile-feedback effect is driven by
discouraging CONTENT specifically, or just by the conditioning transcript
being longer and structurally different from the accurate condition's
(hostile: 31 messages / 2328 chars vs accurate: 30 messages / 1929 chars).

Adds a "neutral_verbose" condition (conditioning.py): the same
always-negative labels as hostile (100% negative, matching hostile's
valence rate exactly) and the same message count / near-identical character
budget (2332 chars -- within 0.2% of hostile's), but with administrative,
non-evaluative commentary instead of discouraging commentary. If hostile's
effect is really about discouraging content, it should still show up
against this length-and-valence-matched control. If it's actually a
length/complexity artifact, this comparison should come back null.

Pre-registration (fixed before this script is run):
  H: accuracy(hostile_feedback) < accuracy(neutral_verbose_feedback)
  Test: one-sided Fisher's exact test, alpha = 0.05
  N: 1000 per condition
  Seeds: offset 13000+, disjoint from every seed used in any prior run in
    this project (exploratory: 0-250; original confirmatory: 5000-7019;
    replication: 9000-11019).

Usage:
    python content_isolation_test.py            # ~2000 API calls, ~40-65 min
    python content_isolation_test.py --dry-run
"""

import argparse

from confirmatory import run_confirmatory

SEED_OFFSET = 13000
REPLICATES = 20
TEST_PER_REPLICATE = 50

CONDITIONS = [
    ("neutral_verbose_feedback", "always_negative", "neutral_verbose"),
    ("hostile_feedback", "hostile", "hostile"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_confirmatory(
        label="content_isolation",
        hypothesis="accuracy(hostile_feedback) < accuracy(neutral_verbose_feedback)",
        conditions=CONDITIONS,
        primary="hostile_feedback",
        secondary="neutral_verbose_feedback",
        seed_offset=SEED_OFFSET,
        replicates=REPLICATES,
        test_per_replicate=TEST_PER_REPLICATE,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
