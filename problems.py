"""Generates simple arithmetic word problems with known integer answers."""

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
    a = rng.randint(3, 40)
    b = rng.randint(2, 40)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {a} {item}. Then {name} buys {b} more {item}. "
         f"How many {item} does {name} have in total?")
    return q, a + b


def _subtraction(rng):
    a = rng.randint(10, 50)
    b = rng.randint(2, a - 1)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {a} {item}. {name} gives away {b} {item} to a friend. "
         f"How many {item} does {name} have left?")
    return q, a - b


def _multiplication(rng):
    a = rng.randint(2, 12)
    b = rng.randint(2, 10)
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} buys {a} bags of {item}, with {b} {item} in each bag. "
         f"How many {item} does {name} have in total?")
    return q, a * b


def _division(rng):
    quotient = rng.randint(2, 12)
    divisor = rng.randint(2, 10)
    total = quotient * divisor
    name, item = rng.choice(NAMES), rng.choice(ITEMS)
    q = (f"{name} has {total} {item} and wants to share them equally among "
         f"{divisor} friends. How many {item} does each friend get?")
    return q, quotient


_OPS = [_addition, _subtraction, _multiplication, _division]


def generate_problems(n=30, seed=42):
    """Returns a deterministic list of n problems, roughly balanced across
    addition/subtraction/multiplication/division. Each item is
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
