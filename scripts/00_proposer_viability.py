#!/usr/bin/env python3
"""Proposer viability script (Phase 0).

Runs the full mock loop on toy program-induction tasks without GPU or network.
Uses a mock proposer and mock solver on deterministic toy tasks.

Prints PASS/FAIL per check and basic metrics at the end.

Usage:
    python scripts/00_proposer_viability.py
"""

from __future__ import annotations

import sys
import os

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from frontier_delta.tasks import generate_toy_tasks, Example, Task
from frontier_delta.sandbox import execute_candidate_on_example
from frontier_delta.verifier import PythonFunctionChecker, VerificationResult
from frontier_delta.rewards import VerifiedReward, RandomReward, FormatOnlyReward, PartialCreditReward
from frontier_delta.passk import pass_at_k, aggregate_pass_at_k
from frontier_delta.analysis import classify_task, classify_all, summary as analysis_summary
from frontier_delta.ledger import Ledger, LedgerRow
from frontier_delta.curriculum import LabelDecayMonitor, DEFAULT_BANDS
from frontier_delta.trainer import MockTrainer, TrainingExample


# ---------------------------------------------------------------------------
# Mock solver: generates candidate functions for toy tasks.
# In a real system this is a trained model; here it's a lookup table.
# ---------------------------------------------------------------------------

_MOCK_SOLUTIONS: dict[str, str] = {
    "add": "def solve(a, b):\n    return a + b\n",
    "sub": "def solve(a, b):\n    return a - b\n",
    "mul": "def solve(a, b):\n    return a * b\n",
    "div": "def solve(a, b):\n    return a // b if b != 0 else None\n",
    "rev": "def solve(s):\n    return s[::-1]\n",
    "repeat": "def solve(s, n):\n    return s * n\n",
    "max2": "def solve(a, b):\n    return a if a > b else b\n",
    "min2": "def solve(a, b):\n    return a if a < b else b\n",
    "sum3": "def solve(a, b, c):\n    return a + b + c\n",
    "mul_add": "def solve(a, b, c):\n    return (a * b) + c\n",
    "diff_of_sq": "def solve(a, b):\n    return (a + b) * (a - b)\n",
    "sum_sq": "def solve(a, b):\n    return a**2 + b**2\n",
    "is_even": "def solve(x):\n    return x % 2 == 0\n",
    "is_odd": "def solve(x):\n    return x % 2 != 0\n",
    "upper": "def solve(s):\n    return s.upper()\n",
    "lower": "def solve(s):\n    return s.lower()\n",
    "count": "def solve(s, c):\n    return s.count(c)\n",
    "eq_or_sum": "def solve(a, b):\n    return a if a == b else (a + b)\n",
    "evens": "def solve(n):\n    return [i for i in range(n) if i % 2 == 0]\n",
    "sum_range": "def solve(n):\n    return sum(range(n + 1))\n",
    "abs_diff": "def solve(a, b):\n    return abs(a - b)\n",
    "length": "def solve(s):\n    return len(s)\n",
    "concat_num": "def solve(a, b):\n    return int(str(a) + str(b))\n",
    "sort3": "def solve(a, b, c):\n    return sorted([a, b, c])\n",
    "range3": "def solve(a, b, c):\n    return max(a, b, c) - min(a, b, c)\n",
    "replace": "def solve(s, old, new):\n    return s.replace(old, new)\n",
    "safe_div": "def solve(a, b):\n    return a / b if b != 0 else 0.0\n",
    "square": "def solve(a):\n    return a * a\n",
    "avg": "def solve(a, b):\n    return (a + b) / 2\n",
    "strip": "def solve(s):\n    return s.strip()\n",
    "split": "def solve(s):\n    return s.split()\n",
    "split_sep": "def solve(s, sep):\n    return s.split(sep)\n",
    "sum_list": "def solve(lst):\n    return sum(lst) if lst else 0\n",
    "append": "def solve(lst, x):\n    return lst + [x]\n",
    "rev_list": "def solve(lst):\n    return lst[::-1]\n",
    "sorted_list": "def solve(lst):\n    return sorted(lst)\n",
    "dict_get": "def solve(d, k):\n    return d.get(k, None)\n",
    "repeat_list": "def solve(a, b):\n    return [a, b] * 3\n",
}

_MOCK_FUNC_NAMES = [
    "add", "sub", "mul", "div", "rev", "repeat", "max2", "min2", "sum3",
    "mul_add", "diff_of_sq", "sum_sq", "is_even", "is_odd", "upper", "lower",
    "count", "eq_or_sum", "evens", "sum_range", "abs_diff", "length",
    "concat_num", "sort3", "range3", "replace", "safe_div", "square", "avg",
    "strip", "split", "split_sep", "sum_list", "append", "rev_list",
    "sorted_list", "dict_get", "repeat_list",
]


def mock_solve(task: Task, correct: bool = True) -> str:
    """Generate a mock candidate for a task.

    If correct=True, returns the known correct solution (if available).
    Otherwise returns a deliberately wrong function.
    """
    func_name = task.meta.get("func_name", "")
    if correct and func_name in _MOCK_SOLUTIONS:
        return _MOCK_SOLUTIONS[func_name]
    # Return a wrong solution
    return "def solve(*args):\n    return None\n"


# ---------------------------------------------------------------------------
# Check harness
# ---------------------------------------------------------------------------

def run_checks() -> dict:
    """Run all viability checks.  Returns a dict with results."""
    results: dict[str, bool] = {}

    # --- 1. Task generation ---
    print("=" * 60)
    print("CHECK 1: Task generation")
    tasks = generate_toy_tasks(n=20, seed=42)
    assert len(tasks) == 20, f"Expected 20 tasks, got {len(tasks)}"
    for t in tasks:
        assert t.task_id, "Task has no ID"
        assert len(t.train_examples) == 5, f"Expected 5 train, got {len(t.train_examples)}"
        assert len(t.test_examples) == 5, f"Expected 5 test, got {len(t.test_examples)}"
    print(f"  PASS: generated {len(tasks)} tasks, each with 5 train + 5 test examples")
    results["task_generation"] = True

    # --- 2. Sandbox execution ---
    print("=" * 60)
    print("CHECK 2: Sandbox execution")
    from frontier_delta.sandbox import execute_candidate
    result = execute_candidate("def solve(a, b):\n    return a + b\n", (3, 4))
    assert result.success, f"Sandbox failed: {result.error}"
    assert result.output == "7", f"Expected '7', got {result.output}"
    print(f"  PASS: sandbox executed 3+4=7 in {result.elapsed_ms:.2f}ms")
    results["sandbox"] = True

    # --- 3. Verifier ---
    print("=" * 60)
    print("CHECK 3: Verifier (PythonFunctionChecker)")
    checker = PythonFunctionChecker()
    task0 = tasks[0]
    good_code = mock_solve(task0, correct=True)
    bad_code = mock_solve(task0, correct=False)

    good_result = checker.check(task0, good_code)
    good_train_result = checker.check(task0, good_code, split="train")
    print(f"  Correct solution: correct={good_result.correct}, passed={good_result.passed_examples}/{good_result.total_examples}")
    assert good_result.correct, "Correct solution should pass all tests"
    assert good_train_result.correct, "Correct solution should pass reward examples"

    bad_result = checker.check(task0, bad_code)
    print(f"  Wrong solution: correct={bad_result.correct}, passed={bad_result.passed_examples}/{bad_result.total_examples}")
    assert not bad_result.correct, "Wrong solution should fail"

    print("  PASS: verifier correctly distinguishes correct from incorrect")
    results["verifier"] = True

    # --- 4. Rewards ---
    print("=" * 60)
    print("CHECK 4: Rewards")
    vr = VerifiedReward()
    rr = RandomReward(seed=42)
    fr = FormatOnlyReward()
    pcr = PartialCreditReward()

    assert vr.compute(good_train_result) == 1.0, "VerifiedReward should give 1.0 for correct"
    assert vr.compute(bad_result) == 0.0, "VerifiedReward should give 0.0 for incorrect"
    print(f"  VerifiedReward: correct={vr.compute(good_train_result)}, incorrect={vr.compute(bad_result)}")

    rand_val = rr.compute(good_result)
    assert rand_val in (0.0, 1.0), "RandomReward should be 0 or 1"
    print(f"  RandomReward(seed=42): {rand_val}")

    fmt_val = fr.compute(good_result, candidate_code=good_code)
    assert fmt_val == 1.0, "FormatOnlyReward should give 1.0 for valid syntax"
    fmt_bad = fr.compute(good_result, candidate_code="def solve(:")
    assert fmt_bad == 0.0, "FormatOnlyReward should give 0.0 for syntax error"
    print(f"  FormatOnlyReward: valid={fmt_val}, syntax_error={fmt_bad}")

    print("  PASS: all reward functions behave as expected")
    results["rewards"] = True

    # --- 5. Mock trainer ---
    print("=" * 60)
    print("CHECK 5: Mock trainer")
    trainer = MockTrainer()
    step = trainer.step(
        [
            TrainingExample(task0.task_id, good_code, vr.compute(good_train_result)),
            TrainingExample(task0.task_id, bad_code, vr.compute(bad_result)),
        ]
    )
    assert step.model_version == 1, f"Expected version 1, got {step.model_version}"
    assert step.examples_seen == 2, f"Expected 2 examples, got {step.examples_seen}"
    assert step.mean_reward == 0.5, f"Expected mean reward 0.5, got {step.mean_reward}"
    print(f"  MockTrainer: version={step.model_version}, examples={step.examples_seen}, mean_reward={step.mean_reward:.2f}")
    print("  PASS: mock trainer records training-step summary")
    results["trainer"] = True

    # --- 6. pass@k ---
    print("=" * 60)
    print("CHECK 6: pass@k estimator")
    # 10 samples, 3 correct, k=1 -> 0.3; k=5 -> ?
    p1 = pass_at_k(10, 3, 1)
    p5 = pass_at_k(10, 3, 5)
    p10 = pass_at_k(10, 3, 10)
    print(f"  n=10, c=3: pass@1={p1:.4f}, pass@5={p5:.4f}, pass@10={p10:.4f}")
    assert abs(p1 - 0.3) < 0.01, f"pass@1 should be ~0.3, got {p1}"
    assert p10 == 1.0, "pass@10 should be 1.0 when c > 0"

    # n=10, c=10, k=1 -> 1.0
    p1_all_correct = pass_at_k(10, 10, 1)
    assert p1_all_correct == 1.0, f"All correct: pass@1 should be 1.0, got {p1_all_correct}"

    # n=10, c=0, k=1 -> 0.0
    p1_none = pass_at_k(10, 0, 1)
    assert p1_none == 0.0, f"No correct: pass@1 should be 0.0, got {p1_none}"

    print("  PASS: pass@k estimator correct")
    results["passk"] = True

    # --- 7. Analysis ---
    print("=" * 60)
    print("CHECK 7: Support-set classification")
    # Simulate: a task that was unsolvable (0/64) becomes solvable (60/64)
    gained = classify_task("t1", 64, 0, 64, 64)
    assert gained.label == "gained", f"Expected gained, got {gained.label}"

    # Solvable -> unsolvable
    lost = classify_task("t2", 64, 64, 64, 0)
    assert lost.label == "lost", f"Expected lost, got {lost.label}"

    # Solvable -> more solvable
    sharp = classify_task("t3", 64, 50, 64, 60, epsilon=0.25, delta_min=0.1)
    assert sharp.label == "sharpened", f"Expected sharpened, got {sharp.label}"

    # Stayed unsolvable
    unch = classify_task("t4", 64, 0, 64, 1)
    assert unch.label == "unchanged", f"Expected unchanged, got {unch.label}"

    print(f"  Classification: gained={gained.label}, lost={lost.label}, "
          f"sharpened={sharp.label}, unchanged={unch.label}")
    print("  PASS: support-set classification correct")
    results["analysis"] = True

    # --- 8. Ledger ---
    print("=" * 60)
    print("CHECK 8: Ledger")
    ledger = Ledger()
    for i, t in enumerate(tasks[:5]):
        n = 64
        c = 50 if i < 3 else 0
        row = LedgerRow(
            task_id=t.task_id,
            round_idx=0,
            arm="vanilla_rlvr",
            n_samples=n,
            c_correct=c,
            pass_at_1=pass_at_k(n, c, 1),
            pass_at_k={1: pass_at_k(n, c, 1), 8: pass_at_k(n, c, 8), 64: pass_at_k(n, c, 64)},
            p_solve=c / n,
            label="sharpened" if c > 0 else "unchanged",
        )
        ledger.add(row)
    assert len(ledger.all_rows()) == 5
    s = ledger.summary()
    print(f"  Ledger summary: {s}")
    print("  PASS: ledger records rows and produces summary")
    results["ledger"] = True

    # --- 9. Curriculum stubs ---
    print("=" * 60)
    print("CHECK 9: Curriculum stubs")
    monitor = LabelDecayMonitor()
    monitor.record(0, {t.task_id: 0.5 for t in tasks})
    s = monitor.summary()
    print(f"  Monitor summary: {s}")
    assert s["rounds_recorded"] == 1
    print("  PASS: curriculum stubs operational")
    results["curriculum"] = True

    # --- 10. Notebook ---
    print("=" * 60)
    print("CHECK 10: Notebook claims template")
    from frontier_delta.notebook import NotebookDB, Claim
    nb = NotebookDB(":memory:")
    nb.add_claim(Claim("c001", "Support expansion observed in arm X", "SELECT * FROM ledger WHERE label='gained'"))
    claims = nb.get_claims()
    assert len(claims) == 1
    md = nb.render_markdown()
    assert "Support expansion" in md
    print(f"  Claims in notebook: {len(claims)}")
    print("  PASS: notebook stores and renders claims")
    results["notebook"] = True

    # --- 11. Aggregate pass@k across tasks ---
    print("=" * 60)
    print("CHECK 11: Aggregate pass@k across multiple tasks")
    # Simulate 5 tasks, each with 64 samples, mixed correct counts
    correct_counts = [60, 50, 40, 2, 0]
    agg = aggregate_pass_at_k(64, correct_counts, 1)
    print(f"  Aggregate pass@1 across 5 tasks: {agg:.4f}")
    assert 0.0 < agg < 1.0, "Aggregate pass@1 should be between 0 and 1"
    print("  PASS: aggregate pass@k works")
    results["aggregate_passk"] = True

    # --- 12. Mock loop end-to-end ---
    print("=" * 60)
    print("CHECK 12: Mock loop end-to-end")
    checker = PythonFunctionChecker()
    correct_total = 0
    total = 0
    for t in tasks:
        code = mock_solve(t, correct=True)
        r = checker.check(t, code)
        total += r.total_examples
        if r.correct:
            correct_total += 1
    print(f"  Tasks solved: {correct_total}/{len(tasks)} "
          f"(total test examples checked: {total})")
    assert correct_total > 0, "At least some tasks should be solvable"
    results["mock_loop_e2e"] = True

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("Frontier Delta -- Proposer Viability (Phase 0)")
    print("Mock proposer + mock solver on toy tasks.  No GPU, no network.")
    print()

    try:
        results = run_checks()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFAIL: {e}")
        return 1

    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  {status}: {name}")

    print()
    if all_pass:
        print("ALL CHECKS PASSED")
        return 0
    else:
        print("SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
