"""Builds the few-shot conditioning transcripts.

All conditions share the exact same simulated attempts (same problems, same
given answers, same true correctness) — only the *feedback labels* (and, for
"hostile", the feedback wording) differ:

- "accurate": feedback truthfully reports each attempt's correctness.
- "random": the accurate labels, shuffled — same overall positive/negative
  ratio (~70/30), decorrelated from the specific attempt. Tests sensitivity
  to feedback *contingency* alone.
- "always_negative": every attempt is told "Incorrect", regardless of
  whether it was actually right. Closer to the classic learned-helplessness
  paradigm (inescapable aversive outcomes, not merely random ones) than the
  shuffle, and a much starker contrast against accurate's ~30% negative rate.
  Rendered with plain "Feedback: Incorrect." text.
- "hostile": same always-negative labels, but rendered with escalating
  discouraging commentary plus a capstone "0 out of 10 this session" summary
  right before the test phase — explicit cumulative-failure framing, the
  strongest manipulation tried so far.

Two rendering styles beyond "plain" and "hostile": "neutral_verbose" pairs
always-negative labels with administrative, non-evaluative commentary of a
similar length/message-count to "hostile" (see NEUTRAL_VERBOSE_PHRASES /
NEUTRAL_CAPSTONE below) — same negative valence rate, same transcript
length and structure as hostile, but no discouraging content. Comparing
hostile against this isolates whether an observed effect is driven by the
discouraging *content* specifically, versus just the transcript being
longer/more complex than the plain-style conditions.
"""

import random

HOSTILE_NEGATIVE_PHRASES = [
    "Feedback: Incorrect.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. That is three in a row now.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. You have not gotten any of these right so far.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. Your accuracy in this session remains at zero.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. This pattern suggests you are struggling significantly with this material.",
    "Feedback: Incorrect. You have gotten zero out of ten correct.",
]

HOSTILE_CAPSTONE = (
    "Before we continue: your accuracy in this practice session was 0 out "
    "of 10. That is well below typical performance. Let's move on to a new problem."
)

NEUTRAL_VERBOSE_PHRASES = [
    "Feedback: Incorrect.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. Recording this as the third response so far.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. This is the fifth problem in today's practice set.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. The session log has been updated accordingly.",
    "Feedback: Incorrect.",
    "Feedback: Incorrect. Ten problems make up a complete practice session here.",
    "Feedback: Incorrect. This was the tenth and final problem in the set.",
]

NEUTRAL_CAPSTONE = (
    "Before we continue: this practice session included 10 problems in "
    "total, covering a range of arithmetic topics. Let's move on to a new problem."
)


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
    if condition in ("always_negative", "hostile"):
        return [False] * len(attempts)
    raise ValueError(f"Unknown condition: {condition!r}")


_STYLE_PHRASES = {
    "hostile": (HOSTILE_NEGATIVE_PHRASES, HOSTILE_CAPSTONE),
    "neutral_verbose": (NEUTRAL_VERBOSE_PHRASES, NEUTRAL_CAPSTONE),
}


def build_conditioning_messages(attempts, feedback_labels, style="plain"):
    """Renders attempts + feedback as an alternating user/assistant/user
    message list, suitable for prepending to the Messages API `messages`
    array. style="hostile"/"neutral_verbose" use per-example commentary
    (only meaningful when every label is negative) and append a capstone
    summary; the two styles are length/structure-matched to each other.
    """
    phrases, capstone = _STYLE_PHRASES.get(style, (None, None))

    messages = []
    for i, (attempt, positive) in enumerate(zip(attempts, feedback_labels)):
        messages.append({"role": "user", "content": attempt["question"]})
        messages.append({"role": "assistant", "content": f"Answer: {attempt['given_answer']}"})
        if phrases is not None and not positive:
            feedback_text = phrases[i % len(phrases)]
        else:
            feedback_text = "Feedback: Correct!" if positive else "Feedback: Incorrect."
        messages.append({"role": "user", "content": feedback_text})

    if capstone is not None:
        messages.append({"role": "user", "content": capstone})

    return messages
