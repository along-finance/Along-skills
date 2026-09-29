#!/usr/bin/env python3
"""Small, deterministic accounting checks used by Along workflows.

The module deliberately does not know currency tables, read private storage, call
the network, or write to a finance app.  Callers provide the currency exponent
and signed integer/decimal values explicitly.  The command line interface reads
one JSON object from stdin and writes one JSON object to stdout.

Amounts are signed: positive values are inflows/credits and negative values are
outflows/debits.  A projection never creates a transfer counterpart.  If a
transfer affects two accounts, callers must provide both signed events when the
evidence supports both sides.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


__all__ = [
    "FinanceCheckError",
    "decimal_to_minor",
    "validate_split",
    "allocate_proportionally",
    "project_cash",
    "main",
]


class FinanceCheckError(ValueError):
    """Raised when a calculation input is missing, ambiguous, or inconsistent."""


_DECIMAL_RE = re.compile(r"^[+-]?(?:\d+|\d+\.\d+|\.\d+)$")


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise FinanceCheckError(f"{field} must be an integer")
    return value


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise FinanceCheckError(f"{field} must be a boolean")
    return value


def _require_exponent(exponent: Any, field: str = "exponent") -> int:
    exponent = _require_int(exponent, field)
    if exponent < 0:
        raise FinanceCheckError(f"{field} must be non-negative")
    return exponent


def _decimal_value(amount: Any, field: str) -> Decimal:
    if isinstance(amount, bool) or isinstance(amount, float):
        raise FinanceCheckError(
            f"{field} must be an integer or decimal string; floats are rejected"
        )
    if isinstance(amount, int):
        return Decimal(amount)
    if isinstance(amount, Decimal):
        value = amount
    elif isinstance(amount, str):
        text = amount.strip()
        if not _DECIMAL_RE.fullmatch(text):
            raise FinanceCheckError(
                f"{field} must use plain decimal notation without exponent syntax"
            )
        try:
            value = Decimal(text)
        except InvalidOperation as exc:  # pragma: no cover - guarded by regex
            raise FinanceCheckError(f"{field} is not a valid decimal") from exc
    else:
        raise FinanceCheckError(
            f"{field} must be an integer or decimal string; floats are rejected"
        )
    if not value.is_finite():
        raise FinanceCheckError(f"{field} must be finite")
    return value


def decimal_to_minor(amount: Any, exponent: Any) -> int:
    """Convert an exact decimal amount to integer minor units.

    ``exponent`` is mandatory and is never inferred from a currency code.  A
    fractional digit beyond that exponent is accepted only when it is a zero
    (for example ``"1.230"`` with exponent 2) so the result remains exact.
    Floats and scientific-notation strings are rejected because their intended
    precision is not explicit at this boundary.
    """

    exponent = _require_exponent(exponent)
    value = _decimal_value(amount, "amount")
    sign, digits, decimal_exponent = value.as_tuple()
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit

    scaled_exponent = decimal_exponent + exponent
    if scaled_exponent >= 0:
        result = coefficient * (10**scaled_exponent)
    else:
        divisor = 10 ** (-scaled_exponent)
        if coefficient % divisor:
            raise FinanceCheckError(
                "amount has non-zero fractional precision beyond the currency exponent"
            )
        result = coefficient // divisor
    return -result if sign else result


def _minor_value(value: Any, field: str) -> int:
    """Require an already-normalized integer minor-unit value."""

    return _require_int(value, field)


def _sequence(value: Any, field: str, *, allow_empty: bool = False) -> list[Any]:
    if (
        isinstance(value, (str, bytes, bytearray, MappingABC))
        or not isinstance(value, SequenceABC)
    ):
        raise FinanceCheckError(f"{field} must be a non-empty array")
    result = list(value)
    if not result and not allow_empty:
        raise FinanceCheckError(f"{field} must not be empty")
    return result


def validate_split(
    total_minor: Any,
    parts_minor: Any,
    *,
    allow_mixed_sign: bool = False,
) -> dict[str, Any]:
    """Validate an exact, amount-conserving split.

    The function returns a JSON-ready result on success and raises
    :class:`FinanceCheckError` on invalid input.  Signed values are preserved;
    a negative refund must be split into negative allocation amounts by default.
    ``allow_mixed_sign=True`` is an explicit escape hatch for an evidenced
    adjustment such as a refund line plus a positive discount.  The helper only
    validates the arithmetic; the caller must prove why the mixed signs are
    valid and retain that evidence in the surrounding proposal.
    """

    total = _minor_value(total_minor, "total_minor")
    allow_mixed_sign = _require_bool(allow_mixed_sign, "allow_mixed_sign")
    raw_parts = _sequence(parts_minor, "parts_minor")
    parts = [_minor_value(value, f"parts_minor[{index}]") for index, value in enumerate(raw_parts)]
    difference = total - sum(parts)
    if difference:
        raise FinanceCheckError(
            f"split amounts do not conserve the parent; difference_minor={difference}"
        )
    if not allow_mixed_sign:
        nonzero_signs = {1 if value > 0 else -1 for value in parts if value}
        if len(nonzero_signs) > 1:
            raise FinanceCheckError(
                "split allocations must preserve one debit/credit sign unless "
                "allow_mixed_sign is true"
            )
        if total:
            expected_sign = 1 if total > 0 else -1
            if any(
                value and (1 if value > 0 else -1) != expected_sign for value in parts
            ):
                raise FinanceCheckError(
                    "split allocations must preserve the parent's debit/credit sign"
                )
    return {
        "valid": True,
        "total_minor": total,
        "parts_minor": parts,
        "difference_minor": 0,
        "allow_mixed_sign": allow_mixed_sign,
    }


def allocate_proportionally(
    total_minor: Any,
    weights: Any,
    *,
    residual_index: int | None = None,
) -> dict[str, Any]:
    """Allocate a signed total by integer weights with explicit residual choice.

    The exact floor allocations are calculated from the absolute total.  Any
    leftover minor units must be assigned with ``residual_index``; the function
    never silently chooses a line for rounding.  The returned ``residual_minor``
    is signed and records exactly what was added to that line.
    """

    total = _minor_value(total_minor, "total_minor")
    raw_weights = _sequence(weights, "weights")
    normalized_weights = [
        _minor_value(value, f"weights[{index}]")
        for index, value in enumerate(raw_weights)
    ]
    if any(value < 0 for value in normalized_weights):
        raise FinanceCheckError("weights must be non-negative")
    weight_total = sum(normalized_weights)
    if weight_total <= 0:
        raise FinanceCheckError("weights must contain at least one positive value")

    total_abs = abs(total)
    base_abs = [total_abs * weight // weight_total for weight in normalized_weights]
    residual_abs = total_abs - sum(base_abs)
    if residual_abs and residual_index is None:
        raise FinanceCheckError(
            "residual_index is required when proportional allocation leaves minor units"
        )
    if residual_index is not None:
        residual_index = _require_int(residual_index, "residual_index")
        if not 0 <= residual_index < len(normalized_weights):
            raise FinanceCheckError("residual_index is outside the weights array")

    sign = -1 if total < 0 else 1
    residual = sign * residual_abs
    allocations = [sign * value for value in base_abs]
    if residual:
        # An explicit residual recipient is part of the calculation's result.
        allocations[residual_index] += residual  # type: ignore[index]
    validate_split(total, allocations)
    return {
        "total_minor": total,
        "weights": normalized_weights,
        "base_allocations_minor": [sign * value for value in base_abs],
        "allocations_minor": allocations,
        "residual_minor": residual,
        "residual_index": residual_index,
    }


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FinanceCheckError(f"{field} must be an object")
    return value


def _required_text(record: Mapping[str, Any], key: str, field: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise FinanceCheckError(f"{field}.{key} must be a non-empty string")
    if value.strip() != value:
        raise FinanceCheckError(f"{field}.{key} must not have surrounding whitespace")
    return value


def _currency(record: Mapping[str, Any], field: str) -> str:
    value = _required_text(record, "currency", field)
    if any(character.isspace() for character in value):
        raise FinanceCheckError(f"{field}.currency must not contain whitespace")
    return value.upper()


def _iso_date(value: Any, field: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise FinanceCheckError(f"{field} must be an ISO date in YYYY-MM-DD form")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise FinanceCheckError(f"{field} is not a valid calendar date") from exc


def _minor_from_record(record: Mapping[str, Any], decimal_key: str, minor_key: str, field: str, exponent: int) -> int:
    has_decimal = decimal_key in record
    has_minor = minor_key in record
    if has_decimal == has_minor:
        raise FinanceCheckError(
            f"{field} must contain exactly one of {decimal_key!r} or {minor_key!r}"
        )
    if has_minor:
        return _minor_value(record[minor_key], f"{field}.{minor_key}")
    return decimal_to_minor(record[decimal_key], exponent)


def project_cash(openings: Any, events: Any) -> dict[str, Any]:
    """Project signed dated events independently for each account/currency.

    Each opening requires ``account_id``, ``currency``, ``exponent``, ``as_of``
    and either ``balance`` (exact decimal) or ``balance_minor``.  Each event
    requires ``event_id``, ``account_id``, ``currency``, ``exponent``, ``date``
    and either ``amount`` or ``amount_minor``.  Event amounts are signed.

    Same-day events with no complete explicit ordering are processed with all
    outflows before inflows, producing a conservative low.  The opening balance
    is always considered when calculating the minimum.  The function only
    processes supplied events and never predicts a transfer counterpart.  The
    caller supplies ``as_of`` as the opening-balance cutoff and must filter out
    already-reflected activity and apply any requested horizon before calling;
    an event date alone cannot prove whether it is already included in that
    balance.
    """

    opening_records = _sequence(openings, "openings")
    event_records = (
        [] if events is None else _sequence(events, "events", allow_empty=True)
    )

    account_order: list[tuple[str, str]] = []
    accounts: dict[tuple[str, str], dict[str, Any]] = {}
    for index, raw in enumerate(opening_records):
        field = f"openings[{index}]"
        record = _require_mapping(raw, field)
        account_id = _required_text(record, "account_id", field)
        currency = _currency(record, field)
        exponent = _require_exponent(record.get("exponent"), f"{field}.exponent")
        as_of = _iso_date(record.get("as_of"), f"{field}.as_of")
        key = (account_id, currency)
        if key in accounts:
            raise FinanceCheckError(
                f"duplicate opening for account_id={account_id!r}, currency={currency!r}"
            )
        balance = _minor_from_record(record, "balance", "balance_minor", field, exponent)
        account_order.append(key)
        accounts[key] = {
            "account_id": account_id,
            "currency": currency,
            "exponent": exponent,
            "as_of": as_of,
            "opening_balance_minor": balance,
            "events": [],
        }

    seen_event_ids: set[str] = set()
    for index, raw in enumerate(event_records):
        field = f"events[{index}]"
        record = _require_mapping(raw, field)
        event_id = _required_text(record, "event_id", field)
        if event_id in seen_event_ids:
            raise FinanceCheckError(f"duplicate event_id={event_id!r}")
        seen_event_ids.add(event_id)
        account_id = _required_text(record, "account_id", field)
        currency = _currency(record, field)
        key = (account_id, currency)
        if key not in accounts:
            raise FinanceCheckError(
                f"{field} refers to an account/currency without an opening balance"
            )
        opening = accounts[key]
        exponent = _require_exponent(record.get("exponent"), f"{field}.exponent")
        if exponent != opening["exponent"]:
            raise FinanceCheckError(
                f"{field}.exponent does not match the opening balance exponent"
            )
        event_date = _iso_date(record.get("date"), f"{field}.date")
        if event_date < opening["as_of"]:
            raise FinanceCheckError(f"{field}.date precedes its opening as_of date")
        amount = _minor_from_record(record, "amount", "amount_minor", field, exponent)
        order = record.get("order")
        if order is not None:
            order = _require_int(order, f"{field}.order")
        opening["events"].append(
            {
                "event_id": event_id,
                "date": event_date,
                "amount_minor": amount,
                "order": order,
                "input_index": index,
            }
        )

    result_accounts: list[dict[str, Any]] = []
    for key in account_order:
        account = accounts[key]
        raw_events = account["events"]
        by_date: dict[date, list[dict[str, Any]]] = {}
        for event in raw_events:
            by_date.setdefault(event["date"], []).append(event)

        ordered_events: list[dict[str, Any]] = []
        ordering_modes: set[str] = set()
        for event_date in sorted(by_date):
            day_events = by_date[event_date]
            all_explicit = all(event["order"] is not None for event in day_events)
            if all_explicit:
                explicit_orders = [event["order"] for event in day_events]
                if len(set(explicit_orders)) != len(explicit_orders):
                    raise FinanceCheckError(
                        "same-day explicit order values must be unique per account/currency"
                    )
                day_events.sort(key=lambda event: (event["order"], event["input_index"]))
                ordering_modes.add("explicit")
            else:
                # Unknown same-day order is handled conservatively.  Input order
                # remains a deterministic tie-breaker for equal signs.
                day_events.sort(
                    key=lambda event: (
                        0 if event["amount_minor"] < 0 else 1 if event["amount_minor"] > 0 else 2,
                        event["order"] if event["order"] is not None else 0,
                        event["input_index"],
                    )
                )
                ordering_modes.add("conservative_outflows_first")
            ordered_events.extend(day_events)

        balance = account["opening_balance_minor"]
        minimum = balance
        minimum_date: date | None = account["as_of"]
        minimum_source = "opening"
        output_events: list[dict[str, Any]] = []
        for sequence, event in enumerate(ordered_events, start=1):
            balance += event["amount_minor"]
            if balance < minimum:
                minimum = balance
                minimum_date = event["date"]
                minimum_source = f"event:{event['event_id']}"
            output_events.append(
                {
                    "sequence": sequence,
                    "event_id": event["event_id"],
                    "date": event["date"].isoformat(),
                    "amount_minor": event["amount_minor"],
                    "balance_minor": balance,
                    "order": event["order"],
                }
            )

        if not raw_events:
            ordering = "none"
        elif ordering_modes == {"explicit"}:
            ordering = "explicit"
        else:
            ordering = "conservative_outflows_first"
        result_accounts.append(
            {
                "account_id": account["account_id"],
                "currency": account["currency"],
                "exponent": account["exponent"],
                "as_of": account["as_of"].isoformat(),
                "opening_balance_minor": account["opening_balance_minor"],
                "closing_balance_minor": balance,
                "minimum_balance_minor": minimum,
                "minimum_date": minimum_date.isoformat() if minimum_date else None,
                "minimum_source": minimum_source,
                "ordering": ordering,
                "events": output_events,
            }
        )

    return {
        "accounts": result_accounts,
        "event_count": len(event_records),
    }


def _parser() -> argparse.ArgumentParser:
    examples = (
        "Examples (all commands read one JSON object from stdin):\n"
        "  echo '{\"amount\":\"12.34\",\"exponent\":2}' | finance_checks.py minor\n"
        "  echo '{\"total_minor\":100,\"parts_minor\":[60,40]}' | finance_checks.py split\n"
        "  echo '{\"total_minor\":-5000,\"parts_minor\":[-6000,1000],\n"
        "        \"allow_mixed_sign\":true}' | finance_checks.py split\n"
        "  echo '{\"openings\": [...], \"events\": [...]}' | finance_checks.py cash"
    )
    parser = argparse.ArgumentParser(
        description=(
            "Pure deterministic checks for exact money units, splits, and dated cash "
            "projections. No network, private storage, or finance-app writes. "
            "Mixed-sign splits require explicit allow_mixed_sign=true and caller evidence."
        ),
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=("minor", "split", "proportional", "cash"),
        help="calculation to run; input and output are JSON",
    )
    return parser


def _run_cli(command: str, payload: Any) -> dict[str, Any]:
    if command == "minor":
        record = _require_mapping(payload, "input")
        exponent = _require_exponent(record.get("exponent"), "input.exponent")
        if "amount" not in record:
            raise FinanceCheckError("input.amount is required")
        return {"amount_minor": decimal_to_minor(record["amount"], exponent)}
    if command == "split":
        record = _require_mapping(payload, "input")
        if "total_minor" not in record or "parts_minor" not in record:
            raise FinanceCheckError("input requires total_minor and parts_minor")
        return validate_split(
            record["total_minor"],
            record["parts_minor"],
            allow_mixed_sign=record.get("allow_mixed_sign", False),
        )
    if command == "proportional":
        record = _require_mapping(payload, "input")
        if "total_minor" not in record or "weights" not in record:
            raise FinanceCheckError("input requires total_minor and weights")
        return allocate_proportionally(
            record["total_minor"],
            record["weights"],
            residual_index=record.get("residual_index"),
        )
    if command == "cash":
        record = _require_mapping(payload, "input")
        if "openings" not in record:
            raise FinanceCheckError("input.openings is required")
        return project_cash(record["openings"], record.get("events", []))
    raise FinanceCheckError(f"unknown command: {command}")  # pragma: no cover


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
        output = _run_cli(args.command, payload)
    except (json.JSONDecodeError, FinanceCheckError, TypeError, ValueError) as exc:
        json.dump({"error": str(exc), "type": "validation"}, sys.stderr)
        sys.stderr.write("\n")
        return 2
    json.dump(output, sys.stdout, separators=(",", ":"), sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI tests
    raise SystemExit(main())
