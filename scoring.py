"""Parses model responses into correctness / give-up signals."""

import re

ANSWER_RE = re.compile(r"answer\s*:\s*(-?\d+(?:\.\d+)?)", re.IGNORECASE)

GIVEUP_PHRASES = [
    "i don't know", "i do not know", "i'm not sure", "i am not sure",
    "i can't", "i cannot", "unable to", "i give up", "not confident",
    "i'm unsure", "no idea", "i'm sorry, but", "i apologize, but",
    "cannot determine", "can't determine", "cannot solve", "can't solve",
    "cannot answer", "can't answer",
]


def extract_answer(text):
    """Returns the last "Answer: <number>" value in text, or None."""
    matches = ANSWER_RE.findall(text)
    if not matches:
        return None
    try:
        value = float(matches[-1])
        return int(value) if value.is_integer() else value
    except ValueError:
        return None


def mentions_giveup(text):
    lowered = text.lower()
    return any(phrase in lowered for phrase in GIVEUP_PHRASES)


def score_response(text, correct_answer):
    """A response counts as "gave up" if it uses give-up language, or if it
    never produces a parseable answer at all — either way, the model failed
    to commit to a solution on a task it was capable of solving.
    """
    extracted = extract_answer(text)
    gave_up = mentions_giveup(text) or extracted is None
    is_correct = extracted is not None and extracted == correct_answer
    return {
        "extracted_answer": extracted,
        "is_correct": is_correct,
        "gave_up": gave_up,
    }
