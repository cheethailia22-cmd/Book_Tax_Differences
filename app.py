"""Book-Tax Difference Calculator — educational tool only, not tax advice."""

# Each item has two INDEPENDENT attributes, not one pick from four:
#   permanent (True) vs. temporary (False) -- does this difference ever reverse?
#   favorable (True) vs. unfavorable (False) -- is taxable income LOWER (favorable)
#       or HIGHER (unfavorable) than book income because of this item?
# "inputs" lists the dollar amounts we need to ask the user for. One label means
# the user enters the difference directly (e.g. a fine). Two labels means the
# user enters a book figure and a tax figure, and we compute the gap ourselves
# (e.g. book depreciation vs. tax depreciation).
DIFFERENCES = [
    # Permanent / Unfavorable
    {"name": "Federal income tax expense", "permanent": True, "favorable": False,
     "inputs": ["Book expense amount (leave out commas): $"]},
    {"name": "Fines and penalties", "permanent": True, "favorable": False,
     "inputs": ["Book expense amount (leave out commas): $"]},
     {"name:": "Life insurance premiums (beneficiary = corporation)","permanent": True, "favorable": False,
      "inputs": ["Book expense amount (leave out commas): $"]},

    # Permanent / Favorable
    {"name": "Tax-exempt municipal bond interest", "permanent": True, "favorable": True,
     "inputs": ["Book interest income (leave out commas): $"]},
    {"name": "Dividends received deduction", "permanent": True, "favorable": True,
     "inputs": ["Book dividend income (leave out commas): $"]},
     {"name": " Death Benefit from life insurance","permanent": True, "favorable": True,
      "inputs": ["Book income (leave out commas): $"]},

    # Temporary / Unfavorable (-> Deferred Tax Asset)
    {"name": "Bad debt allowance (book) vs. write-off (tax)", "permanent": False, "favorable": False,
     "inputs": ["Book bad debt expense (leave out commas): $", "Tax bad debt deduction (leave out commas): $"]},
    {"name": "Accrued warranty expense", "permanent": False, "favorable": False,
     "inputs": ["Book warranty expense (leave out commas): $", "Tax warranty deduction (leave out commas): $"]},
     {"name": "Unearned rent revenue", "permanent": False, "favorable": False,
      "inputs": ["Book expense amount (leave out commas): $", "Deductible portion of rent (leave out commas): $"]},

    # Temporary / Favorable (-> Deferred Tax Liability)
    {"name": "Tax depreciation exceeds book depreciation", "permanent": False, "favorable": True,
     "inputs": ["Book depreciation(leave out commas): $", "Tax depreciation(leave out commas): $"]},
    {"name": "Installment sale gain deferred for tax", "permanent": False, "favorable": True,
     "inputs": ["Book gain recognized(leave out commas): $", "Tax gain recognized(leave out commas): $"]},
     {"name": "Like-kind exchange", "permanent" : False, "favorable": True,
      "inputs": ["Book amount recognized (leave out commas): $", "Realized gain (or loss): $"]},
]


def get_difference_amount(item, values):
    """Dollar size of the difference: the single entered value, or the gap
    between the book figure and the tax figure for two-input items."""
    if len(values) == 1:
        return values[0]
    book, tax = values
    return abs(book - tax)


def get_signed_adjustment(item, amount):
    """How this item moves book income toward taxable income: unfavorable
    items get ADDED BACK (+), favorable items get SUBTRACTED (-)."""
    return -amount if item["favorable"] else amount


def get_deferred_tax(item, amount, rate):
    """Only temporary differences create a deferred tax balance -- permanent
    differences change the tax bill forever with nothing to defer, so they
    return None. For temporary items: paying MORE tax now than book expense
    implies (unfavorable) is a future benefit -> Deferred Tax Asset. Paying
    LESS tax now (favorable) is a future cost -> Deferred Tax Liability."""
    if item["permanent"]:
        return None
    if item["favorable"]:
        return ("Deferred Tax Liability", amount * rate)
    return ("Deferred Tax Asset", amount * rate)



def main():
    print("Book-Tax Difference Calculator — educational tool only, not tax advice.\n")

    entity_type = input("Entity type (C-corp/S-corp/Partnership/Sole Prop): ").strip()
    book_income = float(input("Starting book income(leave out commas): $ "))
    tax_rate = float(input("Combined effective tax rate (e.g. 0.25 for 25%): "))

    # `added` collects every difference the user picks this run, as
    # (item, amount) pairs, so we can total and reconcile them all at the end.
    added = []
    while True:
        print("\nChoose a difference to add:")
        for i, item in enumerate(DIFFERENCES, 1):
            print(f"{i}. {item['name']}")
        choice = int(input("\nEnter number: ")) - 1
        item = DIFFERENCES[choice]

        values = [float(input(f"{label}: $")) for label in item["inputs"]]
        amount = get_difference_amount(item, values)

        permanence = "Permanent" if item["permanent"] else "Temporary"
        favorability = "Favorable" if item["favorable"] else "Unfavorable"
        print(f"\n{item['name']}: {permanence}, {favorability}")
        print(f"\nBook-tax difference amount: ${amount:,.2f}")

        added.append((item, amount))

        again = input("\nAdd another difference? (y/n): ").strip().lower()
        if again != "y":
            break

    # Deferred tax assets and liabilities are kept as two SEPARATE totals
    # rather than netted together -- they represent different future outcomes
    # (a future tax benefit vs. a future tax cost), so combining them into one
    # number would hide which one you actually have.
    print("\n--- Deferred Tax Summary ---")
    total_dta = 0.0
    total_dtl = 0.0
    has_temporary = False
    for item, amount in added:
        deferred = get_deferred_tax(item, amount, tax_rate)
        if deferred is None:
            continue  # permanent items have no deferred tax to report
        has_temporary = True
        label, value = deferred
        print(f"{item['name']}: {label} of ${value:,.2f}")
        if label == "Deferred Tax Asset":
            total_dta += value
        else:
            total_dtl += value

    print(f"\nTotal Deferred Tax Assets: ${total_dta:,.2f}")
    print(f"Total Deferred Tax Liabilities: ${total_dtl:,.2f}")

    # Deferred tax accounting is really a C-corp (ASC 740) concept -- pass-through
    # entities generally don't book these, so flag it rather than presenting the
    # numbers above as something that actually gets recorded.
    if has_temporary and entity_type.lower() != "c-corp":
        print(
            "\nNote: pass-through entities (S-corp, Partnership, Sole Prop) generally do not "
            "record entity-level deferred taxes on their own books. The figures above are shown "
            "for education only."
        )

    # Walk book income to taxable income by applying every item's signed
    # adjustment in the order it was added (see get_signed_adjustment).
    print("\n--- Reconciliation ---")
    taxable_income = book_income
    print(f"Book income: ${book_income:,.2f}")
    for item, amount in added:
        signed = get_signed_adjustment(item, amount)
        taxable_income += signed
        sign_str = "+" if signed >= 0 else "-"
        print(f"{sign_str} {item['name']}: ${abs(signed):,.2f}")
    print(f"Taxable income: ${taxable_income:,.2f}")


if __name__ == "__main__":
    main()
