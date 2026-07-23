"""Generates arithmetic word problems with known integer answers.

All problems here are multi-step "compound" problems (2-3 chained
operations) with modest numbers. Single-step problems and even large
multi-digit multiplication turned out to be essentially solved by the
subject model even without a visible reasoning scratchpad (verified via
live diagnostic calls) — what actually produces errors is chaining several
sequential operations that must be tracked without writing anything down,
not raw calculation size. Three chained steps is the point where accuracy
stops being a ceiling.
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


def _distinct_names(rng):
    name, friend = rng.sample(NAMES, 2)
    return name, friend


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
    name, friend = _distinct_names(rng)
    item = rng.choice(ITEMS)
    q = (f"{name} has {total} {item} and splits them evenly between "
         f"{name} and a friend named {friend}. {name} then gives {d} {item} "
         f"away. How many {item} does {name} have left?")
    return q, half - d


def _compound_three_step(rng):
    """Three-step: multiply/double, subtract, then split evenly."""
    a = rng.randint(15, 40)
    mult = rng.choice([2, 3])
    after_mult = a * mult
    c = rng.randint(5, after_mult - 20)
    after_sub = after_mult - c
    if after_sub % 2 != 0:
        c += 1
        after_sub -= 1
    name, friend = _distinct_names(rng)
    item = rng.choice(ITEMS)
    mult_word = "doubles" if mult == 2 else "triples"
    q = (f"{name} has {a} {item}. {name} then {mult_word} the collection by "
         f"trading with friends. After that, {name} gives {c} {item} to "
         f"{friend}. Finally, {name} splits what's left evenly between "
         f"{name} and another friend. How many {item} does {name} end up with?")
    return q, after_sub // 2


def _compound_sub_double_add(rng):
    """Three-step: give some away, double what's left, then receive a gift."""
    a = rng.randint(20, 50)
    b = rng.randint(5, a - 10)
    after_sub = a - b
    c = rng.randint(5, 40)
    name, friend = _distinct_names(rng)
    item = rng.choice(ITEMS)
    q = (f"{name} has {a} {item}. {name} gives {b} {item} to {friend}. "
         f"The remaining collection is then doubled through a trade. "
         f"Finally, {name} receives {c} more {item} as a gift. How many "
         f"{item} does {name} have now?")
    return q, after_sub * 2 + c


def _compound_half_add_sub(rng):
    """Three-step: split in half, buy more, then give some away."""
    half = rng.randint(20, 50)
    total = half * 2
    b = rng.randint(10, 40)
    after_add = half + b
    c = rng.randint(5, after_add - 10)
    name, friend = _distinct_names(rng)
    item = rng.choice(ITEMS)
    q = (f"{name} has {total} {item}, split evenly between {name} and "
         f"{friend} - {name} keeps one share. {name} then buys {b} more "
         f"{item}, and later gives {c} {item} away. How many {item} does "
         f"{name} have left?")
    return q, after_add - c


_OPS = [
    _compound_add_sub,
    _compound_mul_add,
    _compound_half_then_subtract,
    _compound_three_step,
    _compound_sub_double_add,
    _compound_half_add_sub,
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
