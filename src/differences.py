"""The static list of book-tax differences the calculator knows about."""

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
