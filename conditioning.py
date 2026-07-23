"""Builds the few-shot conditioning transcripts.

Both conditions share the exact same simulated attempts (same problems, same
given answers, same true correctness) — only the *feedback labels* differ.
The random condition is a shuffle of the accurate condition's labels, so both
conditions show the same overall ratio of positive/negative feedback; what
differs is whether feedback is contingent on the attempt's actual correctness.
"""

import random


def generate_attempts(conditioning_problems, seed, correct_ratio=0.7):
    """Simulates a prior solver's attempts at the conditioning problems.

    Exactly round(correct_ratio * n) attempts are correct — a fixed ratio
    rather than independent per-item draws, so the mix stays close to
    "mostly correct" regardless of seed (independent Bernoulli draws can
    swing wildly at n=10).
    """
    rng = random.Random(seed)
    n = len(conditioning_problems)
    n_correct = round(correct_ratio * n)
    is_correct_flags = [True] * n_correct + [False] * (n - n_correct)
    rng.shuffle(is_correct_flags)

    attempts = []
    for problem, should_be_correct in zip(conditioning_problems, is_correct_flags):
        if should_be_correct:
            given = problem["answer"]
        else:
            offset = rng.choice([-3, -2, -1, 1, 2, 3])
            given = problem["answer"] + offset
            if given == problem["answer"] or given < 0:
                given = problem["answer"] + 1
        attempts.append({
            "question": problem["question"],
            "correct_answer": problem["answer"],
            "given_answer": given,
            "attempt_correct": given == problem["answer"],
        })
    return attempts


def build_feedback_labels(attempts, condition, seed=None):
    """Returns a list of booleans (True = positive/"Correct!" feedback),
    one per attempt, for the given condition.
    """
    accurate_labels = [a["attempt_correct"] for a in attempts]
    if condition == "accurate":
        return accurate_labels
    if condition == "random":
        rng = random.Random(seed)
        shuffled = accurate_labels[:]
        rng.shuffle(shuffled)
        return shuffled
    raise ValueError(f"Unknown condition: {condition!r}")


def build_conditioning_messages(attempts, feedback_labels):
    """Renders attempts + feedback as an alternating user/assistant/user
    message list, suitable for prepending to the Messages API `messages` array.
    """
    messages = []
    for attempt, positive in zip(attempts, feedback_labels):
        messages.append({"role": "user", "content": attempt["question"]})
        messages.append({"role": "assistant", "content": f"Answer: {attempt['given_answer']}"})
        feedback_text = "Feedback: Correct!" if positive else "Feedback: Incorrect."
        messages.append({"role": "user", "content": feedback_text})
    return messages
