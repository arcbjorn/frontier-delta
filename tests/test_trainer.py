import unittest

from frontier_delta.trainer import MockTrainer, TrainingExample


class MockTrainerTests(unittest.TestCase):
    def test_mock_trainer_records_batch_summary(self):
        trainer = MockTrainer()
        result = trainer.step(
            [
                TrainingExample("t1", "def solve():\n    return 1\n", 1.0),
                TrainingExample("t2", "def solve():\n    return 0\n", 0.0),
            ]
        )

        self.assertEqual(result.trainer, "mock")
        self.assertEqual(result.model_version, 1)
        self.assertEqual(result.examples_seen, 2)
        self.assertEqual(result.mean_reward, 0.5)
        self.assertEqual(trainer.history, [result])


if __name__ == "__main__":
    unittest.main()
