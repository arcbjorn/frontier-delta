"""Task definitions and a deterministic toy program-induction generator.

Each Task has a natural-language description, training input-output examples,
and held-out test examples. The hidden function is a pure Python callable.
"""

from __future__ import annotations

import dataclasses
import hashlib
import random
from typing import Callable, List, Tuple


@dataclasses.dataclass(frozen=True)
class Example:
    """A single input-output pair.

    Args:
        args: positional arguments to the hidden function.
        kwargs: keyword arguments to the hidden function.
        output: expected return value.
    """

    args: Tuple[object, ...]
    kwargs: Tuple[Tuple[str, object], ...]
    output: object


@dataclasses.dataclass(frozen=True)
class Task:
    """A program-induction task.

    Attributes:
        task_id: unique identifier.
        description: natural-language description of the hidden function.
        train_examples: examples the solver may use for training/reward.
        test_examples: held-out examples used only for evaluation.
        difficulty_band: proposer-estimated difficulty label.
        meta: arbitrary metadata (e.g., proposer model, generation seed).
    """

    task_id: str
    description: str
    train_examples: List[Example]
    test_examples: List[Example]
    difficulty_band: str = "medium"
    meta: dict = dataclasses.field(default_factory=dict)


# ---------------------------------------------------------------------------
# Toy program-induction generator
# ---------------------------------------------------------------------------

_TOY_SPECS: List[tuple[str, Callable[..., object]]] = [
    ("add", lambda a, b: a + b),
    ("sub", lambda a, b: a - b),
    ("mul", lambda a, b: a * b),
    ("div", lambda a, b: a // b if b != 0 else None),
    ("rev", lambda s: s[::-1]),
    ("repeat", lambda s, n: s * n),
    ("max2", lambda a, b: a if a > b else b),
    ("min2", lambda a, b: a if a < b else b),
    ("sum3", lambda a, b, c: a + b + c),
    ("mul_add", lambda a, b, c: (a * b) + c),
    ("diff_of_sq", lambda a, b: (a + b) * (a - b)),
    ("sum_sq", lambda a, b: a**2 + b**2),
    ("is_even", lambda x: x % 2 == 0),
    ("is_odd", lambda x: x % 2 != 0),
    ("upper", lambda s: s.upper()),
    ("lower", lambda s: s.lower()),
    ("count", lambda s, c: s.count(c)),
    ("eq_or_sum", lambda a, b: a if a == b else (a + b)),
    ("evens", lambda n: [i for i in range(n) if i % 2 == 0]),
    ("sum_range", lambda n: sum(range(n + 1))),
    ("abs_diff", lambda a, b: abs(a - b)),
    ("length", lambda s: len(s)),
    ("concat_num", lambda a, b: int(str(a) + str(b))),
    ("sort3", lambda a, b, c: sorted([a, b, c])),
    ("range3", lambda a, b, c: max(a, b, c) - min(a, b, c)),
    ("replace", lambda s, old, new: s.replace(old, new)),
    ("safe_div", lambda a, b: a / b if b != 0 else 0.0),
    ("square", lambda a: a * a),
    ("avg", lambda a, b: (a + b) / 2),
    ("strip", lambda s: s.strip()),
    ("split", lambda s: s.split()),
    ("split_sep", lambda s, sep: s.split(sep)),
    ("sum_list", lambda lst: sum(lst) if lst else 0),
    ("append", lambda lst, x: lst + [x]),
    ("rev_list", lambda lst: lst[::-1]),
    ("sorted_list", lambda lst: sorted(lst)),
    ("dict_get", lambda d, k: d.get(k, None)),
    ("repeat_list", lambda a, b: [a, b] * 3),
]


def _hash_id(func: Callable[..., object], idx: int) -> str:
    """Deterministic task-id from function source and index."""
    try:
        src = func.__code__.co_code
    except AttributeError:
        src = str(func).encode()
    digest = hashlib.sha256(src + bytes([idx])).hexdigest()[:12]
    return f"toy-{digest}"


def generate_toy_task(
    func: Callable[..., object],
    idx: int = 0,
    n_train: int = 5,
    n_test: int = 5,
    rng: random.Random | None = None,
    name: str | None = None,
) -> Task:
    """Generate a single Task for a toy function.

    Args:
        func: the hidden Python function.
        idx: variant index (changes the seed for examples).
        n_train: number of training examples.
        n_test: number of held-out test examples.
        rng: seeded Random instance; if None, uses a fresh Random(idx).

    Returns:
        Task with train and test examples.
    """
    if rng is None:
        rng = random.Random(idx)

    # Build a plausible description for the toy functions
    # (In real use the proposer writes this.)
    description = f"Implement a function that matches the provided examples."

    def _random_arg(arg_name: str) -> object:
        """Return a random argument value appropriate for toy functions."""
        if arg_name.startswith("n") or arg_name == "x":
            return rng.randint(0, 20)
        if arg_name in ("s", "old", "new", "sep"):
            choices = ["hello", "world", "abc", "xyz", "test", "foo", "bar", ""]
            return rng.choice(choices)
        if arg_name == "c":
            return rng.choice("abcdefgh")
        if arg_name in ("a", "b", "c"):
            return rng.randint(-10, 10)
        if arg_name == "lst":
            return [rng.randint(0, 5) for _ in range(rng.randint(1, 5))]
        if arg_name == "d":
            return {rng.choice(["x", "y", "z"]): rng.randint(0, 10) for _ in range(rng.randint(1, 3))}
        return rng.randint(0, 10)

    # Inspect function signature
    import inspect

    try:
        sig = inspect.signature(func)
        arg_names = list(sig.parameters.keys())
    except (ValueError, TypeError):
        # Fallback for lambdas: guess arity from error or use generic names
        # We use a simple heuristic: try calling with increasing args until it works
        arg_names = []
        for arity in range(1, 5):
            try:
                func(*([0] * arity))
                arg_names = [chr(97 + i) for i in range(arity)]  # a, b, c, ...
                break
            except (TypeError, ZeroDivisionError):
                continue
        if not arg_names:
            arg_names = ["a", "b"]

    def make_example() -> Example:
        args = tuple(_random_arg(name) for name in arg_names)
        try:
            output = func(*args)
        except (TypeError, ValueError, ZeroDivisionError):
            output = None
        return Example(args=args, kwargs=(), output=output)

    train_examples = [make_example() for _ in range(n_train)]
    test_examples = [make_example() for _ in range(n_test)]

    return Task(
        task_id=_hash_id(func, idx),
        description=description,
        train_examples=train_examples,
        test_examples=test_examples,
        difficulty_band="medium",
        meta={
            "func_name": name or getattr(func, "__name__", "lambda"),
            "arg_names": arg_names,
            "seed": idx,
        },
    )


def generate_toy_tasks(
    n: int = 20,
    seed: int = 42,
    n_train: int = 5,
    n_test: int = 5,
) -> List[Task]:
    """Generate n toy program-induction tasks.

    Args:
        n: number of tasks to generate.  Cycles through _TOY_FUNCTIONS if n > len.
        seed: random seed for reproducibility.
        n_train: number of training examples per task.
        n_test: number of held-out test examples per task.

    Returns:
        List of Task objects.
    """
    rng = random.Random(seed)
    tasks: List[Task] = []
    for i in range(n):
        name, func = _TOY_SPECS[i % len(_TOY_SPECS)]
        tasks.append(
            generate_toy_task(
                func,
                idx=i,
                n_train=n_train,
                n_test=n_test,
                rng=rng,
                name=name,
            )
        )
    return tasks
