import unittest

from frontier_delta.ledger import COLOR_MAP, Ledger, LedgerRow


class LedgerTests(unittest.TestCase):
    def test_color_map_contains_expected_labels(self):
        self.assertEqual(COLOR_MAP["gained"].symbol, "+")
        self.assertEqual(COLOR_MAP["lost"].symbol, "-")
        self.assertEqual(COLOR_MAP["sharpened"].symbol, "~")
        self.assertEqual(COLOR_MAP["unchanged"].symbol, ".")

    def test_ledger_adds_and_filters_rows(self):
        ledger = Ledger()
        row = LedgerRow(
            task_id="t1",
            round_idx=0,
            arm="main_selfplay",
            n_samples=64,
            c_correct=10,
            pass_at_1=0.1,
            pass_at_k={1: 0.1, 8: 0.8},
            p_solve=0.2,
            label="sharpened",
        )
        ledger.add(row)
        self.assertEqual(ledger.rows_for_arm("main_selfplay"), [row])
        self.assertEqual(ledger.rows_for_task("t1"), [row])
        self.assertEqual(ledger.summary()["total_rows"], 1)


if __name__ == "__main__":
    unittest.main()
