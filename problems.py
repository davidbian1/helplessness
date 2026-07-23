"""Generates arithmetic word problems with known integer answers.

Includes both single-step problems (larger numbers than a first pass) and
two-step "compound" problems that require carrying an intermediate result.
The compound problems are what create room for genuine mistakes — a single
easy operation tends to hit a ceiling (100% accuracy) that can't show a
conditioning effect either way.
"""

import random

NAMES = [
    "Maya", "Liam", "Sofia", "Noah", "Aisha", "Ethan",
    "Priya", "Lucas", "Zoe", "Omar", "Ava", "Kenji",
]

ITEMS = [
    "apples", "stickers", "marbles", "books", "pencils",
    "cookies", "balloons", "coins", "cards", "seashells",
]


def _addition(rng):
    a = rng.randint(40, 95)
    b = rng.randint(15, 80)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {a} {item}. Then {name} buys {b} more {item}. "
         f"How many {item} does {name} have in total?")
    return q, a + b


def _subtraction(rng):
    a = rng.randint(50, 130)
    b = rng.randint(15, a - 10)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {a} {item}. {name} gives away {b} {item} to a friend. "
         f"How many {item} does {name} have left?")
    return q, a - b


def _multiplication(rng):
    a = rng.randint(11, 29)
    b = rng.randint(11, 29)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} buys {a} bags of {item}, with {b} {item} in each bag. "
         f"How many {item} does {name} have in total?")
    return q, a * b


def _division(rng):
    quotient = rng.randint(11, 29)
    divisor = rng.randint(6, 19)
    total = quotient * divisor
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {total} {item} and wants to share them equally among "
         f"{divisor} friends. How many {item} does each friend get?")
    return q, quotient


def _compound_add_sub(rng):
    """Two-step: buy some, then give some away."""
    a = rng.randint(30, 70)
    b = rng.randint(15, 50)
    c = rng.randint(10, a + b - 5)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {a} {item}. Then {name} buys {b} more {item}, and "
         f"later gives {c} {item} away to a friend. How many {item} does "
         f"{name} have now?")
    return q, a + b - c


def _compound_mul_add(rng):
    """Two-step: multiply, then add a leftover amount."""
    a = rng.randint(8, 19)
    b = rng.randint(8, 16)
    c = rng.randint(10, 60)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} buys {a} bags of {item}, with {b} {item} in each bag. "
         f"{name} already had {c} {item} at home. How many {item} does "
         f"{name} have in total now?")
    return q, a * b + c


def _compound_half_then_subtract(rng):
    """Two-step: split evenly between two people, then one gives some away."""
    half = rng.randint(15, 60)
    total = half * 2
    d = rng.randint(3, half - 3)
    name, friend, item = rng.choice(NAMES), rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {total} {item} and splits them evenly between "
         f"{name} and a friend named {friend}. {name} then gives {d} {item} "
         f"away. How many {item} does {name} have left?")
    return q, half - d


_OPS = [
    _addition,
    _subtraction,
    _multiplication,
    _division,
    _compound_add_sub,
    _compound_mul_add,
    _compound_half_then_subtract,
]


def generate_problems(n=30, seed=42):
    """Returns a deterministic list of n problems, roughly balanced across
    the operation types above. Each item is
    {"id": int, "question": str, "answer": int}.
    """
    rng = random.Random(seed)

    sequence = []
    while len(sequence) < n:
        batch = _OPS[:]
        rng.shuffle(batch)
        sequence.extend(batch)
    sequence = sequence[:n]

    problems = []
    for i, op in enumerate(sequence):
        question, answer = op(rng)
        problems.append({"id": i, "question": question, "answer": answer})
    return problems
