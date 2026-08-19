"""Book-Tax Difference Calculator for C-corporations — educational tool only, not tax advice."""

from calculations import get_difference_amount, get_signed_adjustment, get_deferred_tax
from differences import DIFFERENCES


def get_starting_inputs():
    """Ask for the starting book income and the tax rate used for every
    deferred tax calculation this run."""
    book_income = float(input("Starting book income(leave out commas): $ "))
    tax_rate = float(input("Combined effective tax rate (e.g. 0.25 for 25%): "))
    return book_income, tax_rate


def choose_item():
    """Print the numbered menu and return the item the user picks."""
    print("\nChoose a difference to add:")
    for i, item in enumerate(DIFFERENCES, 1):
        print(f"{i}. {item['name']}")
    choice = int(input("\nEnter number: ")) - 1
    return DIFFERENCES[choice]


def collect_values(item):
    """Prompt for each dollar amount item["inputs"] asks for."""
    return [float(input(label)) for label in item["inputs"]]


def print_categorization(item):
    """Print whether this item is permanent/temporary and favorable/unfavorable."""
    permanence = "Permanent" if item["permanent"] else "Temporary"
    favorability = "Favorable" if item["favorable"] else "Unfavorable"
    print(f"\n{item['name']}: {permanence}, {favorability}")


def collect_differences():
    """Loop letting the user add as many differences as they want. Returns
    a list of (item, amount) pairs, one entry per difference added."""
    added = []
    while True:
        item = choose_item()
        values = collect_values(item)
        amount = get_difference_amount(item, values)
        print_categorization(item)
        print(f"\nBook-tax difference amount: ${amount:,.2f}")

        added.append((item, amount))

        again = input("\nAdd another difference? (y/n): ").strip().lower()
        if again != "y":
            break
    return added


def print_deferred_tax_summary(added, tax_rate):
    """Print each temporary item's deferred tax entry, then separate totals
    for Deferred Tax Assets and Deferred Tax Liabilities (never netted --
    see get_deferred_tax)."""
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


def print_reconciliation(added, book_income):
    """Walk book income to taxable income by applying every item's signed
    adjustment in the order it was added (see get_signed_adjustment)."""
    print("\n--- Reconciliation ---")
    taxable_income = book_income
    print(f"Book income: ${book_income:,.2f}")
    for item, amount in added:
        signed = get_signed_adjustment(item, amount)
        taxable_income += signed
        sign_str = "+" if signed >= 0 else "-"
        print(f"{sign_str} {item['name']}: ${abs(signed):,.2f}")
    print(f"Taxable income: ${taxable_income:,.2f}")


def main():
    print("Book-Tax Difference Calculator for C-corporations — educational tool only, not tax advice.\n")
    book_income, tax_rate = get_starting_inputs()
    added = collect_differences()
    print_deferred_tax_summary(added, tax_rate)
    print_reconciliation(added, book_income)


if __name__ == "__main__":
    main()
