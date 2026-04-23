import streamlit as st

st.set_page_config(page_title="Income Tax Calculator (New Regime)", page_icon="💰")

st.title("💰 Income Tax Calculator - New Regime (India)")
st.write("FY 2023-24 / AY 2024-25")

# Input
income = st.number_input("Enter your Annual Income (₹)", min_value=0.0, step=50000.0)

def calculate_tax(income):
    tax = 0
    breakdown = []

    if income > 1500000:
        tax += (income - 1500000) * 0.30
        breakdown.append(("Above ₹15L (30%)", (income - 1500000) * 0.30))
        income = 1500000

    if income > 1200000:
        tax += (income - 1200000) * 0.20
        breakdown.append(("₹12L - ₹15L (20%)", (income - 1200000) * 0.20))
        income = 1200000

    if income > 900000:
        tax += (income - 900000) * 0.15
        breakdown.append(("₹9L - ₹12L (15%)", (income - 900000) * 0.15))
        income = 900000

    if income > 600000:
        tax += (income - 600000) * 0.10
        breakdown.append(("₹6L - ₹9L (10%)", (income - 600000) * 0.10))
        income = 600000

    if income > 300000:
        tax += (income - 300000) * 0.05
        breakdown.append(("₹3L - ₹6L (5%)", (income - 300000) * 0.05))

    return tax, breakdown


if st.button("Calculate Tax"):
    tax, breakdown = calculate_tax(income)

    # Section 87A Rebate
    if income <= 700000:
        rebate = tax
        tax = 0
    else:
        rebate = 0

    cess = tax * 0.04
    total_tax = tax + cess

    st.subheader("📊 Tax Breakdown")

    for slab, amount in breakdown:
        st.write(f"{slab}: ₹{amount:,.2f}")

    st.write("---")
    st.write(f"Tax before rebate: ₹{tax + rebate:,.2f}")
    st.write(f"Rebate (87A): ₹{rebate:,.2f}")
    st.write(f"Tax after rebate: ₹{tax:,.2f}")
    st.write(f"Cess (4%): ₹{cess:,.2f}")

    st.success(f"✅ Total Tax Payable: ₹{total_tax:,.2f}")