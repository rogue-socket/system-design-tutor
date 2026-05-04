"""SM-2 lite scheduler tests.

Mirrors the algorithm specified in references/spaced-repetition.md (the
``update_card`` pseudocode block). If you change the algorithm there,
update this file in the same commit — the spec_parity test will fail
loudly otherwise.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "references" / "spaced-repetition.md"


def update_card(card: dict, rating: int, today: date) -> dict:
    """Mirror of the spec block in references/spaced-repetition.md."""
    if rating < 3:
        card["interval_days"] = 1
        card["ease"] = max(1.3, card["ease"] - 0.2)
    else:
        if card["interval_days"] == 0:
            card["interval_days"] = 1
        elif card["interval_days"] == 1:
            card["interval_days"] = 6
        else:
            card["interval_days"] = round(card["interval_days"] * card["ease"])
        card["ease"] = max(
            1.3,
            card["ease"] + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)),
        )

    card["next_review"] = today + timedelta(days=card["interval_days"])
    card["review_history"].append({"date": today.isoformat(), "rating": rating})
    return card


def _new_card() -> dict:
    return {"ease": 2.5, "interval_days": 0, "review_history": []}


# ------- Tests -------

def test_new_card_first_pass_promotes_to_one_day():
    today = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=4, today=today)
    assert card["interval_days"] == 1, card
    assert card["next_review"] == today + timedelta(days=1)
    assert card["review_history"][-1]["rating"] == 4


def test_second_pass_promotes_to_six_days():
    today = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=4, today=today)
    update_card(card, rating=4, today=today + timedelta(days=1))
    assert card["interval_days"] == 6, card


def test_third_pass_uses_ease_multiplier():
    """interval=6, ease starts 2.5; rating=4 keeps ease at ~2.5
    (per the formula: 0.1 - 1*(0.08+1*0.02) = 0.1 - 0.10 = 0.0).
    Next interval = round(6 * 2.5) = 15."""
    today = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=4, today=today)
    update_card(card, rating=4, today=today + timedelta(days=1))
    update_card(card, rating=4, today=today + timedelta(days=7))
    assert abs(card["ease"] - 2.5) < 1e-9, card["ease"]
    assert card["interval_days"] == 15, card["interval_days"]


def test_fail_resets_interval_and_drops_ease():
    today = date(2026, 5, 4)
    card = {"ease": 2.5, "interval_days": 30, "review_history": []}
    update_card(card, rating=1, today=today)
    assert card["interval_days"] == 1
    assert abs(card["ease"] - 2.3) < 1e-9, card["ease"]
    assert card["next_review"] == today + timedelta(days=1)


def test_ease_floors_at_1_3_after_repeated_fails():
    today = date(2026, 5, 4)
    card = _new_card()
    for i in range(20):
        update_card(card, rating=0, today=today + timedelta(days=i))
    assert abs(card["ease"] - 1.3) < 1e-9, card["ease"]


def test_perfect_rating_increases_ease():
    """rating=5: 0.1 - 0*(0.08+0*0.02) = +0.10 to ease."""
    today = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=5, today=today)
    assert abs(card["ease"] - 2.6) < 1e-9, card["ease"]


def test_rating_three_decreases_ease():
    """rating=3 (correct with effort): 0.1 - 2*(0.08+2*0.02) = 0.1 - 0.24 = -0.14."""
    today = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=3, today=today)
    assert abs(card["ease"] - 2.36) < 1e-9, card["ease"]


def test_review_history_is_append_only():
    today = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=4, today=today)
    update_card(card, rating=2, today=today + timedelta(days=1))
    update_card(card, rating=4, today=today + timedelta(days=2))
    assert len(card["review_history"]) == 3
    assert [h["rating"] for h in card["review_history"]] == [4, 2, 4]


def test_failure_then_recovery_sequence():
    """Realistic learning curve: pass, pass, fail (resets), then re-promote."""
    d0 = date(2026, 5, 4)
    card = _new_card()
    update_card(card, rating=4, today=d0)                          # 1d
    update_card(card, rating=4, today=d0 + timedelta(days=1))      # 6d
    update_card(card, rating=1, today=d0 + timedelta(days=7))      # reset to 1d, ease 2.3
    assert card["interval_days"] == 1
    assert abs(card["ease"] - 2.3) < 1e-9
    update_card(card, rating=4, today=d0 + timedelta(days=8))      # 6d
    assert card["interval_days"] == 6


def test_spec_parity_with_markdown():
    """Detect drift: the formulas in the spec must match what's tested here."""
    text = SPEC.read_text()
    must_contain = [
        'card["interval_days"] = 1',
        'card["ease"] = max(1.3, card["ease"] - 0.2)',
        'card["interval_days"] = 6',
        'round(card["interval_days"] * card["ease"])',
        'max(1.3, card["ease"] + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)))',
    ]
    for needle in must_contain:
        assert needle in text, f"spec drift: spaced-repetition.md no longer contains: {needle!r}"


TESTS_LIST = [
    ("SR: new card first pass → 1d", test_new_card_first_pass_promotes_to_one_day),
    ("SR: second pass → 6d", test_second_pass_promotes_to_six_days),
    ("SR: third pass uses ease multiplier", test_third_pass_uses_ease_multiplier),
    ("SR: fail resets interval, drops ease 0.2", test_fail_resets_interval_and_drops_ease),
    ("SR: ease floors at 1.3", test_ease_floors_at_1_3_after_repeated_fails),
    ("SR: rating 5 raises ease by 0.10", test_perfect_rating_increases_ease),
    ("SR: rating 3 lowers ease by 0.14", test_rating_three_decreases_ease),
    ("SR: review_history is append-only", test_review_history_is_append_only),
    ("SR: pass-pass-fail-pass recovery", test_failure_then_recovery_sequence),
    ("SR: spec parity with markdown", test_spec_parity_with_markdown),
]


def main():
    failed = 0
    for name, fn in TESTS_LIST:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            failed += 1
    print(f"\n{len(TESTS_LIST) - failed}/{len(TESTS_LIST)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
