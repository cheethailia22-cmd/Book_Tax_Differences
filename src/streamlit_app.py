"""Book-Tax Difference Calculator -- Streamlit UI.

Lets you add as many differences as you want, one at a time (like the
console app's "Add another difference?" loop), then shows a grand total
summary: Deferred Tax Asset/Liability totals and a book-to-taxable-income
reconciliation across everything added.

Streamlit reruns this whole script top to bottom on every click, so a plain
Python list wouldn't survive between clicks -- that's what st.session_state
is for: it's a dict that Streamlit keeps alive across reruns.

Run with: streamlit run src/streamlit_app.py
"""

import streamlit as st

from calculations import get_difference_amount, get_signed_adjustment, get_deferred_tax
from differences import DIFFERENCES

st.title("Book-Tax Difference Calculator")
st.caption("For C-corporations -- educational tool only, not tax advice.")

if "added" not in st.session_state:
    st.session_state.added = []  # list of (item, amount) pairs, grows as differences are added

book_income = st.number_input("Starting book income ($)", value=0.0, step=1000.0)
tax_rate = st.number_input("Combined effective tax rate (e.g. 0.25 for 25%)", value=0.25, step=0.01)

st.header("Add a difference")
names = [item["name"] for item in DIFFERENCES]
selected_name = st.selectbox("Choose a difference", names)
item = next(i for i in DIFFERENCES if i["name"] == selected_name)

values = [st.number_input(label, value=0.0, step=100.0, key=label) for label in item["inputs"]]

col1, col2 = st.columns(2)
if col1.button("Add difference"):
    amount = get_difference_amount(item, values)
    st.session_state.added.append((item, amount))
    permanence = "Permanent" if item["permanent"] else "Temporary"
    favorability = "Favorable" if item["favorable"] else "Unfavorable"
    st.success(f"Added: {item['name']} -- {permanence}, {favorability} -- ${amount:,.2f}")

if col2.button("Start over"):
    st.session_state.added = []

added = st.session_state.added

if added:
    st.header("Differences added")
    for item, amount in added:
        permanence = "Permanent" if item["permanent"] else "Temporary"
        favorability = "Favorable" if item["favorable"] else "Unfavorable"
        st.write(f"- {item['name']}: {permanence}, {favorability} -- ${amount:,.2f}")

    # Deferred tax assets and liabilities are kept as two SEPARATE totals
    # rather than netted together -- same reasoning as the console app.
    st.header("Deferred Tax Summary")
    total_dta = 0.0
    total_dtl = 0.0
    for item, amount in added:
        deferred = get_deferred_tax(item, amount, tax_rate)
        if deferred is None:
            continue  # permanent items have no deferred tax to report
        label, value = deferred
        st.write(f"{item['name']}: {label} of ${value:,.2f}")
        if label == "Deferred Tax Asset":
            total_dta += value
        else:
            total_dtl += value
    st.write(f"**Total Deferred Tax Assets:** ${total_dta:,.2f}")
    st.write(f"**Total Deferred Tax Liabilities:** ${total_dtl:,.2f}")

    st.header("Reconciliation")
    taxable_income = book_income
    st.write(f"Book income: ${book_income:,.2f}")
    for item, amount in added:
        signed = get_signed_adjustment(item, amount)
        taxable_income += signed
        sign_str = "+" if signed >= 0 else "-"
        st.write(f"{sign_str} {item['name']}: ${abs(signed):,.2f}")
    st.write(f"**Taxable income:** ${taxable_income:,.2f}")
