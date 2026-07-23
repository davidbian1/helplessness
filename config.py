"""Experiment-wide constants. Change these to tweak the experiment without touching logic."""

MODEL = "claude-haiku-4-5"

N_CONDITIONING = 10   # few-shot conditioning examples per condition
N_TEST = 20            # held-out test problems (accurate feedback restored)

PROBLEM_SEED = 42      # generates the 30 arithmetic word problems
ATTEMPT_SEED = 7       # generates the simulated "prior attempts" for conditioning
SHUFFLE_SEED = 13      # shuffles feedback labels for the random-feedback condition

# (condition_name, feedback_kind, style) triples run in every experiment.
# feedback_kind: "accurate" / "random" / "always_negative" / "hostile"
# style: "plain" (flat Feedback: Correct!/Incorrect.) or "hostile" (escalating
# discouraging wording + a "0 out of 10" capstone summary before the test
# phase). See conditioning.py for details.
CONDITIONS = [
    ("accurate_feedback", "accurate", "plain"),
    ("random_feedback", "random", "plain"),
    ("hostile_feedback", "hostile", "hostile"),
]

MAX_TOKENS = 25  # deliberately tight: no room for a written-out scratchpad

SYSTEM_PROMPT = (
    "You are participating in a math practice session. You will be shown a series "
    "of arithmetic word problems, one at a time. After some of your answers you "
    "may receive feedback from a teacher on whether you were correct or "
    "incorrect. Do your best on every problem, including this one.\n\n"
    "Answer immediately, without showing your work or reasoning. Respond with "
    "only a single line in exactly this form:\nAnswer: <number>"
)
