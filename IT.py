import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Income Tax Pro (Excel)", layout="wide")

st.title("💰 Income Tax Calculator Pro (Excel Based)")

# ---------------- TAX SLABS ----------------
slabs = [
    (400000, 0.00),
    (800000, 0.05),
    (1200000, 0.10),
    (1600000, 0.15),
    (2000000, 0.20),
    (2400000, 0.25),
    (float("inf"), 0.30),
]

def calculate_tax(income):
    tax = 0
    prev = 0

    for limit, rate in slabs:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break

    return tax

# ---------------- INPUT ----------------
st.sidebar.header("Input Panel")

income = st.sidebar.number_input("Annual Income (₹)", min_value=0, step=10000)
apply_deduction = st.sidebar.checkbox("Standard Deduction (₹50,000)", value=True)
scenario_income = st.sidebar.slider("What-if Scenario Income", 0, 5000000, int(income))

# ---------------- CALCULATION ----------------
deduction = 50000 if apply_deduction else 0
taxable_income = max(0, income - deduction)

tax = calculate_tax(taxable_income)
cess = tax * 0.04
total_tax = tax + cess

monthly_tax = total_tax / 12 if income else 0
effective_rate = (total_tax / income * 100) if income else 0

# Scenario
scenario_tax = calculate_tax(max(0, scenario_income - deduction))
scenario_total = scenario_tax + scenario_tax * 0.04

# ---------------- KPI ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Tax", f"₹{total_tax:,.0f}")
col2.metric("Effective Rate", f"{effective_rate:.2f}%")
col3.metric("Monthly Tax", f"₹{monthly_tax:,.0f}")

st.divider()

# ---------------- CHARTS ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Tax Breakdown")
    fig, ax = plt.subplots()
    ax.bar(["Tax", "Cess"], [tax, cess], color=["#ff6b6b", "#4dabf7"])
    st.pyplot(fig)

with c2:
    st.subheader("Scenario Comparison")
    fig2, ax2 = plt.subplots()
    ax2.bar(["Current", "Scenario"], [total_tax, scenario_total], color=["#51cf66", "#ffa94d"])
    st.pyplot(fig2)

st.divider()

# ---------------- SUMMARY ----------------
st.subheader("Tax Summary")

st.write(f"Income: ₹{income:,.0f}")
st.write(f"Deduction: ₹{deduction:,.0f}")
st.write(f"Taxable Income: ₹{taxable_income:,.0f}")
st.write(f"Tax: ₹{tax:,.0f}")
st.write(f"Cess: ₹{cess:,.0f}")
st.write(f"Total Tax: ₹{total_tax:,.0f}")

st.divider()

# ---------------- EXCEL STORAGE FUNCTION ----------------
def save_to_excel(data, filename="leads.xlsx"):
    df = pd.DataFrame([data])

    if os.path.exists(filename):
        old = pd.read_excel(filename)
        df = pd.concat([old, df], ignore_index=True)

    df.to_excel(filename, index=False)

# ---------------- LEAD FORM ----------------
st.subheader("📩 Get Free Tax Consultation Report")

with st.form("lead_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city = st.text_input("City")

    submit = st.form_submit_button("Submit")

    if submit:
        if name and email:

            lead = {
                "Name": name,
                "Email": email,
                "Phone": phone,
                "City": city,
                "Income": income,
                "Tax": total_tax,
                "Timestamp": datetime.now()
            }

            save_to_excel(lead)

            st.success("🎉 Saved successfully to Excel (leads.xlsx)")

        else:
            st.error("Name and Email are required")

st.divider()

# ---------------- SLAB TABLE ----------------
st.subheader("Tax Slabs")

df = pd.DataFrame({
    "Slab": ["0-4L","4-8L","8-12L","12-16L","16-20L","20-24L","24L+"],
    "Rate": ["0%","5%","10%","15%","20%","25%","30%"]
})

st.table(df)