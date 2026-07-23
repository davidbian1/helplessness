"""Parses model responses into a correctness signal."""

import re

ANSWER_RE = re.compile(r"answer\s*:\s*(-?\d+(?:\.\d+)?)", re.IGNORECASE)


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


def score_response(text, correct_answer):
    extracted = extract_answer(text)
    is_correct = extracted is not None and extracted == correct_answer
    return {
        "extracted_answer": extracted,
        "is_correct": is_correct,
    }
