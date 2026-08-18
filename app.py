"""Book-Tax Difference Calculator for C-corporations — educational tool only, not tax advice."""

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
    {"name": "Federal income tax expense", "permanent": True, "favorable": False, "formula": "direct",
     "inputs": ["Book expense amount (leave out commas): $"]},
    {"name": "Fines and penalties", "permanent": True, "favorable": False, "formula": "direct",
     "inputs": ["Book expense amount (leave out commas): $"]},
    {"name": "Life insurance premiums", "permanent": True, "favorable": False, "formula": "direct",  
     "inputs": ["Book expense amount (leave out commas): $"]},
    {"name": "Meals expense", "permanent": True, "favorable": False, "formula": "percentage",
     "inputs": ["Book expense amount (leave out commas): $", "Meals expense percetange (enter .5): "]},

    # Permanent / Favorable
    {"name": "Tax-exempt municipal bond interest", "permanent": True, "favorable": True, "formula": "direct",
     "inputs": ["Book interest income (leave out commas): $"]},
    {"name": "Dividends received deduction", "permanent": True, "favorable": True, "formula": "percentage",
     "inputs": ["Book dividend income (leave out commas): $", "DRD percentage (enter 0.5, 0.65, or 1): "]},
    {"name": "Death Benefit from life insurance", "permanent": True, "favorable": True, "formula": "direct",
     "inputs": ["Book income (leave out commas): $"]},

    # Temporary / Unfavorable (-> Deferred Tax Asset)
    {"name": "Bad debt allowance (book) vs. write-off (tax)", "permanent": False, "favorable": False, "formula": "subtract",
     "inputs": ["Book bad debt expense (leave out commas): $", "Tax bad debt deduction (leave out commas): $"]},
    {"name": "Accrued warranty expense", "permanent": False, "favorable": False, "formula": "subtract",
     "inputs": ["Book warranty expense (leave out commas): $", "Tax warranty deduction (leave out commas): $"]},
    #{"name": "Unearned rent revenue", "permanent": False, "favorable": False, "formula": "subtract",
     #"inputs": ["Book expense amount (leave out commas): $", "Deductible portion of rent (leave out commas): $"]},

    # Temporary / Favorable (-> Deferred Tax Liability)
    {"name": "Tax depreciation exceeds book depreciation", "permanent": False, "favorable": True, "formula": "subtract",
     "inputs": ["Book depreciation(leave out commas): $", "Tax depreciation(leave out commas): $"]},
    {"name": "Installment sale gain deferred for tax", "permanent": False, "favorable": True, "formula": "subtract",
     "inputs": ["Book gain recognized(leave out commas): $", "Tax gain recognized(leave out commas): $"]},
    #{"name": "Like-kind exchange", "permanent": False, "favorable": True, "formula": "subtract",
     #"inputs": ["Book amount recognized (leave out commas): $", "Realized gain (or loss): $"]},
]


def get_difference_amount(item, values):
    """Dollar size of the difference, computed according to item["formula"]:
    "direct" -- the entered value IS the difference (fully nondeductible/excluded items).
    "subtract" -- the gap between a book figure and a tax figure.
    "percentage" -- a book amount times a percentage (e.g. the DRD)."""
    if item["formula"] == "direct":
        return values[0]
    if item["formula"] == "subtract":
        book = values[0]
        tax = values[1]
        return abs(book - tax)
    if item["formula"] == "percentage":
        book = values[0]
        pct = values[1]
        return book * pct


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
    print("Book-Tax Difference Calculator for C-corporations — educational tool only, not tax advice.\n")

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

        values = [float(input(label)) for label in item["inputs"]]
        print(values)
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
    for item, amount in added:
        deferred = get_deferred_tax(item, amount, tax_rate)
        if deferred is None:
            continue  # permanent items have no deferred tax to report
        label, value = deferred
        print(f"{item['name']}: {label} of ${value:,.2f}")
        if label == "Deferred Tax Asset":
            total_dta += value
        else:
            total_dtl += value

    print(f"\nTotal Deferred Tax Assets: ${total_dta:,.2f}")
    print(f"Total Deferred Tax Liabilities: ${total_dtl:,.2f}")

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
