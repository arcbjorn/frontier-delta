import unittest

from frontier_delta.tasks import generate_toy_tasks
from frontier_delta.verifier import PythonFunctionChecker


class VerifierTests(unittest.TestCase):
    def test_checker_accepts_correct_program_on_heldout_examples(self):
        task = generate_toy_tasks(n=1, seed=1)[0]
        code = "def solve(a, b):\n    return a + b\n"
        result = PythonFunctionChecker(timeout_sec=2).check(task, code)
        self.assertTrue(result.correct)
        self.assertEqual(result.passed_examples, result.total_examples)
        self.assertEqual(result.split, "test")

    def test_checker_can_evaluate_training_examples_for_reward(self):
        task = generate_toy_tasks(n=1, seed=1)[0]
        code = "def solve(a, b):\n    return a + b\n"
        result = PythonFunctionChecker(timeout_sec=2).check(task, code, split="train")
        self.assertTrue(result.correct)
        self.assertEqual(result.passed_examples, len(task.train_examples))
        self.assertEqual(result.split, "train")

    def test_checker_rejects_wrong_program_on_heldout_examples(self):
        task = generate_toy_tasks(n=1, seed=1)[0]
        code = "def solve(a, b):\n    return None\n"
        result = PythonFunctionChecker(timeout_sec=2).check(task, code)
        self.assertFalse(result.correct)
        self.assertLess(result.passed_examples, result.total_examples)

    def test_checker_reports_timeout_as_sandbox_error(self):
        task = generate_toy_tasks(n=1, seed=1)[0]
        code = "def solve(a, b):\n    while True:\n        pass\n"
        result = PythonFunctionChecker(timeout_sec=0.1).check(task, code)
        self.assertFalse(result.correct)
        self.assertTrue(result.sandbox_error)


if __name__ == "__main__":
    unittest.main()
