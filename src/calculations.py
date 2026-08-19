"""Pure calculation functions -- no input()/print(), so these can be tested
in isolation from the interactive parts of the app."""


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
