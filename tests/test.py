"""Tests for the book-tax difference calculator's formulas in calculations.py.

Run directly with: python tests/test.py
No pytest needed -- each test is a plain function that asserts; the runner
at the bottom calls them all and prints PASS/FAIL for each.
"""

import os
import sys

# calculations.py and differences.py live one directory up from this file,
# so add the repo root to the import path before importing them.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculations import get_difference_amount, get_signed_adjustment, get_deferred_tax
from src.differences import DIFFERENCES


def find_item(name):
    """Look up one of the real DIFFERENCES entries by name, so tests exercise
    the actual data the app uses instead of made-up copies of it."""
    return next(item for item in DIFFERENCES if item["name"] == name)


def test_direct_formula():
    # Fines & penalties: the entire book expense is nondeductible.
    item = find_item("Fines and penalties")
    amount = get_difference_amount(item, [1000])
    assert amount == 1000, f"expected 1000, got {amount}"


def test_subtract_formula():
    # Bad debt: difference is the gap between the book expense and tax deduction.
    item = find_item("Bad debt allowance (book) vs. write-off (tax)")
    amount = get_difference_amount(item, [800, 200])
    assert amount == 600, f"expected 600, got {amount}"


#def test_percentage_formula_fixed_rate():
    # Meals: 50% of book meals expense is nondeductible; the 0.5 rate is
    # stored on the item itself, not entered by the user.
   # item = find_item("Meals expense")
    #amount = get_difference_amount(item, [1000])
    #assert amount == 500, f"expected 500, got {amount}"


def test_percentage_formula_user_entered_rate():
    # DRD: book dividend income x a percentage that varies by ownership stake,
    # so the user enters it (50%, 65%, or 100%).
    item = find_item("Dividends received deduction")
    amount = get_difference_amount(item, [10000, 0.5])
    assert amount == 5000, f"expected 5000, got {amount}"


def test_signed_adjustment_unfavorable_adds_back():
    item = find_item("Fines and penalties")
    assert get_signed_adjustment(item, 100) == 100


def test_signed_adjustment_favorable_subtracts():
    item = find_item("Tax-exempt municipal bond interest")
    assert get_signed_adjustment(item, 100) == -100


def test_deferred_tax_permanent_item_is_none():
    item = find_item("Fines and penalties")
    assert get_deferred_tax(item, 100, 0.25) is None


def test_deferred_tax_unfavorable_temporary_is_asset():
    item = find_item("Bad debt allowance (book) vs. write-off (tax)")
    label, value = get_deferred_tax(item, 600, 0.25)
    assert label == "Deferred Tax Asset"
    assert value == 150, f"expected 150, got {value}"


def test_deferred_tax_favorable_temporary_is_liability():
    item = find_item("Tax depreciation exceeds book depreciation")
    label, value = get_deferred_tax(item, 3000, 0.25)
    assert label == "Deferred Tax Liability"
    assert value == 750, f"expected 750, got {value}"


TESTS = [
    test_direct_formula,
    test_subtract_formula,
    #test_percentage_formula_fixed_rate,
    test_percentage_formula_user_entered_rate,
    test_signed_adjustment_unfavorable_adds_back,
    test_signed_adjustment_favorable_subtracts,
    test_deferred_tax_permanent_item_is_none,
    test_deferred_tax_unfavorable_temporary_is_asset,
    test_deferred_tax_favorable_temporary_is_liability,
]


if __name__ == "__main__":
    passed = 0
    failed = 0
    for test in TESTS:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__} -- {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__} -- {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
