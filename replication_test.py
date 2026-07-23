"""Direct replication of confirmatory_test.py's result.

Identical hypothesis, identical test, identical design (same conditions,
same N, same power target) -- the only thing that differs is the seed
offset, which is fresh and disjoint from every prior run in this project
(exploratory: 0-250; original confirmatory: 5000-7019). If the original
effect is real rather than a one-off false positive, it should reproduce
here in the same direction.

Pre-registration (fixed before this script is run):
  H1: accuracy(hostile_feedback) < accuracy(accurate_feedback)
  Test: one-sided Fisher's exact test, alpha = 0.05
  N: 1000 per condition
  Seeds: offset 9000+

Usage:
    python replication_test.py            # ~2000 API calls, ~40-65 min
    python replication_test.py --dry-run
"""

import argparse

from confirmatory import run_confirmatory

SEED_OFFSET = 9000
REPLICATES = 20
TEST_PER_REPLICATE = 50

CONDITIONS = [
    ("accurate_feedback", "accurate", "plain"),
    ("hostile_feedback", "hostile", "hostile"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_confirmatory(
        label="replication",
        hypothesis="accuracy(hostile_feedback) < accuracy(accurate_feedback) -- independent replication",
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
