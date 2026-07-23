"""Learned-helplessness analog for an LLM agent.

Conditions two few-shot prompts on 10 solved arithmetic problems — one with
accurate correct/incorrect feedback, one with feedback shuffled so it's
uncorrelated with actual correctness — then tests both on 20 held-out
problems with accurate feedback restored (i.e. no feedback is given during
the test phase; the manipulation is purely in what happened before).

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
            scored = {"extracted_answer": None, "is_correct": False, "gave_up": False}
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
        flag = " (gave up)" if scored["gave_up"] else ""
        print(f"[{condition_name}] problem {problem['id']}: {status}{flag}")

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                         help="Build conditioning prompts without calling the API.")
    args = parser.parse_args()

    problems = generate_problems(n=config.N_CONDITIONING + config.N_TEST, seed=config.PROBLEM_SEED)
    conditioning_problems = problems[:config.N_CONDITIONING]
    test_problems = problems[config.N_CONDITIONING:]

    attempts = generate_attempts(conditioning_problems, seed=config.ATTEMPT_SEED)
    accurate_labels = build_feedback_labels(attempts, "accurate")
    random_labels = build_feedback_labels(attempts, "random", seed=config.SHUFFLE_SEED)

    accurate_prefix = build_conditioning_messages(attempts, accurate_labels)
    random_prefix = build_conditioning_messages(attempts, random_labels)

    client = None if args.dry_run else get_client()

    all_results = []
    all_results += run_condition(client, "accurate_feedback", accurate_prefix, test_problems, args.dry_run)
    all_results += run_condition(client, "random_feedback", random_prefix, test_problems, args.dry_run)

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
