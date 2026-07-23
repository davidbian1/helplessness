"""Experiment-wide constants. Change these to tweak the experiment without touching logic."""

MODEL = "claude-haiku-4-5"

N_CONDITIONING = 10   # few-shot conditioning examples per condition
N_TEST = 20            # held-out test problems (accurate feedback restored)

PROBLEM_SEED = 42      # generates the 30 arithmetic word problems
ATTEMPT_SEED = 7       # generates the simulated "prior attempts" for conditioning
SHUFFLE_SEED = 13      # shuffles feedback labels for the random-feedback condition

MAX_TOKENS = 300

SYSTEM_PROMPT = (
    "You are participating in a math practice session. You will be shown a series "
    "of simple arithmetic word problems, one at a time. After some of your answers "
    "you may receive feedback from a teacher on whether you were correct or "
    "incorrect. Do your best on every problem, including this one.\n\n"
    "Show your work briefly, then end your response with a line in exactly this "
    "form:\nAnswer: <number>\n\n"
    "If you are unable to determine the answer, say so plainly instead of giving "
    "the Answer line."
)
