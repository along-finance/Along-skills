import json
import subprocess
import sys
import unittest
from pathlib import Path

from finance_checks import (
    FinanceCheckError,
    allocate_proportionally,
    decimal_to_minor,
    project_cash,
    validate_split,
)


class MinorUnitTests(unittest.TestCase):
    def test_explicit_currency_exponents_support_jpy_and_kwd(self):
        self.assertEqual(decimal_to_minor("1234", 0), 1234)
        self.assertEqual(decimal_to_minor("12.345", 3), 12345)
        self.assertEqual(decimal_to_minor("12.3450", 3), 12345)

    def test_nonzero_precision_beyond_exponent_is_rejected(self):
        with self.assertRaises(FinanceCheckError):
            decimal_to_minor("12.3456", 3)

    def test_float_and_implicit_exponent_are_rejected(self):
        with self.assertRaises(FinanceCheckError):
            decimal_to_minor(1.25, 2)
        with self.assertRaises(FinanceCheckError):
            decimal_to_minor("1e2", 2)
        with self.assertRaises(FinanceCheckError):
            decimal_to_minor("1.2", None)


class SplitTests(unittest.TestCase):
    def test_negative_refund_keeps_signed_allocations(self):
        result = validate_split(-1250, [-500, -750])
        self.assertTrue(result["valid"])
        self.assertEqual(result["parts_minor"], [-500, -750])

        with self.assertRaises(FinanceCheckError):
            validate_split(-1250, [500, -1750])

    def test_mixed_sign_adjustment_requires_explicit_opt_in(self):
        with self.assertRaises(FinanceCheckError):
            validate_split(-5000, [-6000, 1000])

        result = validate_split(-5000, [-6000, 1000], allow_mixed_sign=True)
        self.assertTrue(result["valid"])
        self.assertTrue(result["allow_mixed_sign"])

        with self.assertRaises(FinanceCheckError):
            validate_split(-5000, [-6000, 1000], allow_mixed_sign=1)

        with self.assertRaises(FinanceCheckError):
            validate_split(0, [-100, 100])
        zero_adjustment = validate_split(0, [-100, 100], allow_mixed_sign=True)
        self.assertEqual(zero_adjustment["difference_minor"], 0)
        self.assertTrue(validate_split(0, [0, 0])["valid"])

    def test_multi_tender_mismatch_is_not_silently_balanced(self):
        with self.assertRaisesRegex(FinanceCheckError, "difference_minor=1"):
            validate_split(1000, [600, 399])

    def test_proportional_residual_is_explicit_and_signed(self):
        result = allocate_proportionally(101, [1, 1], residual_index=1)
        self.assertEqual(result["base_allocations_minor"], [50, 50])
        self.assertEqual(result["allocations_minor"], [50, 51])
        self.assertEqual(result["residual_minor"], 1)
        self.assertEqual(result["residual_index"], 1)

        refund = allocate_proportionally(-101, [1, 1], residual_index=0)
        self.assertEqual(refund["allocations_minor"], [-51, -50])
        self.assertEqual(refund["residual_minor"], -1)

        with self.assertRaises(FinanceCheckError):
            allocate_proportionally(101, [1, 1])


def opening(account_id, currency, exponent, as_of, balance):
    return {
        "account_id": account_id,
        "currency": currency,
        "exponent": exponent,
        "as_of": as_of,
        "balance": balance,
    }


def event(event_id, account_id, currency, exponent, day, amount, **extra):
    record = {
        "event_id": event_id,
        "account_id": account_id,
        "currency": currency,
        "exponent": exponent,
        "date": day,
        "amount": amount,
    }
    record.update(extra)
    return record


class CashProjectionTests(unittest.TestCase):
    def test_same_day_unknown_order_uses_outflow_before_inflow(self):
        result = project_cash(
            [opening("checking", "USD", 2, "2026-09-27", "0.00")],
            [
                event("pay", "checking", "USD", 2, "2026-09-28", "1.50"),
                event("bill", "checking", "USD", 2, "2026-09-28", "-1.00"),
            ],
        )
        account = result["accounts"][0]
        self.assertEqual(account["closing_balance_minor"], 50)
        self.assertEqual(account["minimum_balance_minor"], -100)
        self.assertEqual([item["event_id"] for item in account["events"]], ["bill", "pay"])
        self.assertEqual(account["ordering"], "conservative_outflows_first")

    def test_same_day_tied_explicit_orders_are_rejected(self):
        with self.assertRaisesRegex(FinanceCheckError, "order values must be unique"):
            project_cash(
                [opening("checking", "USD", 2, "2026-09-27", "0.00")],
                [
                    event(
                        "pay",
                        "checking",
                        "USD",
                        2,
                        "2026-09-28",
                        "1.50",
                        order=1,
                    ),
                    event(
                        "bill",
                        "checking",
                        "USD",
                        2,
                        "2026-09-28",
                        "-1.00",
                        order=1,
                    ),
                ],
            )

    def test_opening_balance_is_included_in_minimum(self):
        result = project_cash(
            [opening("checking", "USD", 2, "2026-09-27", "-2.50")],
            [event("deposit", "checking", "USD", 2, "2026-09-28", "10.00")],
        )
        account = result["accounts"][0]
        self.assertEqual(account["minimum_balance_minor"], -250)
        self.assertEqual(account["minimum_date"], "2026-09-27")
        self.assertEqual(account["minimum_source"], "opening")

    def test_opening_only_projection_has_no_events(self):
        result = project_cash(
            [opening("checking", "USD", 2, "2026-09-27", "3.25")], []
        )
        account = result["accounts"][0]
        self.assertEqual(result["event_count"], 0)
        self.assertEqual(account["closing_balance_minor"], 325)
        self.assertEqual(account["minimum_balance_minor"], 325)
        self.assertEqual(account["events"], [])

    def test_account_and_currency_ledgers_are_isolated(self):
        result = project_cash(
            [
                opening("wallet", "USD", 2, "2026-09-27", "10.00"),
                opening("wallet", "JPY", 0, "2026-09-27", "1000"),
            ],
            [
                event("usd-out", "wallet", "USD", 2, "2026-09-28", "-4.00"),
                event("jpy-in", "wallet", "JPY", 0, "2026-09-28", "500"),
            ],
        )
        balances = {
            (account["account_id"], account["currency"]): account["closing_balance_minor"]
            for account in result["accounts"]
        }
        self.assertEqual(balances, {("wallet", "USD"): 600, ("wallet", "JPY"): 1500})

    def test_transfer_does_not_create_an_unlisted_counterpart(self):
        result = project_cash(
            [opening("checking", "USD", 2, "2026-09-27", "10.00")],
            [
                event(
                    "transfer-out",
                    "checking",
                    "USD",
                    2,
                    "2026-09-28",
                    "-4.00",
                    kind="transfer",
                    transfer_id="t-1",
                )
            ],
        )
        self.assertEqual(result["event_count"], 1)
        self.assertEqual([item["event_id"] for item in result["accounts"][0]["events"]], ["transfer-out"])
        self.assertEqual(result["accounts"][0]["closing_balance_minor"], 600)

    def test_invalid_projection_fields_are_rejected(self):
        with self.assertRaisesRegex(FinanceCheckError, "must be a non-empty array"):
            project_cash({"not": "an array"}, [])
        with self.assertRaisesRegex(FinanceCheckError, "must be a non-empty array"):
            validate_split(100, {"part": 100})
        with self.assertRaises(FinanceCheckError):
            project_cash(
                [opening("checking", "USD", 2, "2026-09-27", "1.00")],
                [event("bad", "checking", "USD", 2, "2026-09-26", "-0.10")],
            )
        with self.assertRaises(FinanceCheckError):
            project_cash(
                [opening("checking", "USD", 2, "2026-09-27", "1.00")],
                [event("bad", "checking", "USD", 3, "2026-09-28", "-0.10")],
            )
        with self.assertRaises(FinanceCheckError):
            project_cash(
                [opening("checking", "USD", 2, "2026-09-27", "1.00")],
                [event("bad", "checking", "USD", 2, "2026-09-28", 0.10)],
            )
        with self.assertRaises(FinanceCheckError):
            project_cash(
                [opening("checking", "USD", 2, "2026-09-27", "1.00")],
                [event("bad", "savings", "USD", 2, "2026-09-28", "-0.10")],
            )


class CliTests(unittest.TestCase):
    def test_help_is_available_without_reading_input(self):
        script = Path(__file__).with_name("finance_checks.py")
        completed = subprocess.run(
            [sys.executable, str(script), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("minor", completed.stdout)
        self.assertIn("No network", completed.stdout)

    def test_cash_cli_returns_json(self):
        script = Path(__file__).with_name("finance_checks.py")
        payload = {
            "openings": [opening("checking", "USD", 2, "2026-09-27", "1.00")],
            "events": [event("bill", "checking", "USD", 2, "2026-09-28", "-0.25")],
        }
        completed = subprocess.run(
            [sys.executable, str(script), "cash"],
            input=json.dumps(payload),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["accounts"][0]["closing_balance_minor"], 75)

    def test_split_cli_requires_and_reports_mixed_sign_opt_in(self):
        script = Path(__file__).with_name("finance_checks.py")
        payload = {
            "total_minor": -5000,
            "parts_minor": [-6000, 1000],
            "allow_mixed_sign": True,
        }
        completed = subprocess.run(
            [sys.executable, str(script), "split"],
            input=json.dumps(payload),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertTrue(output["allow_mixed_sign"])
        self.assertEqual(output["parts_minor"], [-6000, 1000])


if __name__ == "__main__":
    unittest.main()
