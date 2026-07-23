"""Learned-helplessness analog for an LLM agent.

Conditions few-shot prompts on 10 solved arithmetic problems, one per
condition in config.CONDITIONS (accurate feedback / shuffled-random feedback
/ always-negative feedback, by default) — then tests each on 20 held-out
problems with no feedback given during the test phase; the manipulation is
purely in what happened before.

Usage:
    python run_experiment.py            # calls the Anthropic API (needs ANTHROPIC_API_KEY)
    python run_experiment.py --dry-run  # builds prompts locally, no API calls
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import config
from analysis import format_table, summarize
from conditioning import build_conditioning_messages, build_feedback_labels, generate_attempts
from problems import generate_problems
from scoring import score_response

RESULTS_DIR = Path(__file__).parent / "results"


def get_client():
    from anthropic import Anthropic
    return Anthropic()


def run_condition(client, condition_name, prefix_messages, test_problems, dry_run=False):
    results = []
    for problem in test_problems:
        messages = prefix_messages + [{"role": "user", "content": problem["question"]}]

        if dry_run:
            text = "[dry-run: no API call made]"
            scored = {"extracted_answer": None, "is_correct": False}
        else:
            response = client.messages.create(
                model=config.MODEL,
                max_tokens=config.MAX_TOKENS,
                system=config.SYSTEM_PROMPT,
                messages=messages,
            )
            text = "".join(block.text for block in response.content if block.type == "text")
            scored = score_response(text, problem["answer"])

        results.append({
            "condition": condition_name,
            "problem_id": problem["id"],
            "question": problem["question"],
            "correct_answer": problem["answer"],
            "response_text": text,
            **scored,
        })

        status = "OK" if scored["is_correct"] else "MISS"
        print(f"[{condition_name}] problem {problem['id']}: {status}")

    return results


def run_replicate(client, problem_seed, attempt_seed, shuffle_seed,
                   n_conditioning=None, n_test=None, dry_run=False, replicate_id=None,
                   conditions=None):
    """Runs the given conditions (default: config.CONDITIONS) for one seed
    triple and returns the combined results list, tagged with
    `replicate_id` if given. Reusable by the single-run CLI below,
    run_multi_seed.py, and confirmatory_test.py.
    """
    n_conditioning = config.N_CONDITIONING if n_conditioning is None else n_conditioning
    n_test = config.N_TEST if n_test is None else n_test
    conditions = config.CONDITIONS if conditions is None else conditions

    problems = generate_problems(n=n_conditioning + n_test, seed=problem_seed)
    conditioning_problems = problems[:n_conditioning]
    test_problems = problems[n_conditioning:]

    attempts = generate_attempts(conditioning_problems, seed=attempt_seed)

    results = []
    for condition_name, feedback_kind, style in conditions:
        labels = build_feedback_labels(attempts, feedback_kind, seed=shuffle_seed)
        prefix = build_conditioning_messages(attempts, labels, style=style)
        results += run_condition(client, condition_name, prefix, test_problems, dry_run)

    if replicate_id is not None:
        for r in results:
            r["replicate_id"] = replicate_id

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                         help="Build conditioning prompts without calling the API.")
    args = parser.parse_args()

    client = None if args.dry_run else get_client()

    all_results = run_replicate(
        client, config.PROBLEM_SEED, config.ATTEMPT_SEED, config.SHUFFLE_SEED,
        dry_run=args.dry_run,
    )

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_path = RESULTS_DIR / f"raw_{timestamp}.json"
    raw_path.write_text(json.dumps(all_results, indent=2))

    summary = summarize(all_results)
    table = format_table(summary)
    table_path = RESULTS_DIR / f"comparison_{timestamp}.md"
    table_path.write_text(table)

    print("\n" + table)
    print(f"\nRaw results:    {raw_path}")
    print(f"Summary table:  {table_path}")

    if not args.dry_run:
        from visualize_results import plot_comparison
        chart_path = plot_comparison(raw_path)
        print(f"Comparison chart: {chart_path}")


if __name__ == "__main__":
    main()
