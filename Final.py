import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tax + Lead Gen App", layout="wide")

# ---------------- UI THEME ----------------
st.markdown("""
<style>
body { background-color: #0e1117; }
h1, h2, h3, p { color: white; }

.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    border: none;
}

.sidebar .sidebar-content {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Smart Tax Calculator + Lead System (FY 2025-26)")
st.caption("New Regime | Tax Calculation + Client Capture System")

# ---------------- SIDEBAR CLIENT DETAILS ----------------
st.sidebar.header("👤 Client Details")

client_name = st.sidebar.text_input("Full Name")
pan = st.sidebar.text_input("PAN Number")
phone = st.sidebar.text_input("Phone Number")
email = st.sidebar.text_input("Email ID")

st.sidebar.divider()

st.sidebar.subheader("📞 Quick Lead Form")

interest = st.sidebar.selectbox(
    "Service Interested In",
    ["Tax Filing", "Investment Planning", "Loan Assistance", "Insurance", "Other"]
)

submit_lead = st.sidebar.button("🚀 Submit Lead")

if "leads" not in st.session_state:
    st.session_state.leads = []

if submit_lead:
    if client_name and phone:
        st.session_state.leads.append({
            "Name": client_name,
            "PAN": pan,
            "Phone": phone,
            "Email": email,
            "Interest": interest
        })
        st.sidebar.success("Lead Saved Successfully ✅")
    else:
        st.sidebar.error("Name & Phone are required")

# ---------------- MAIN INPUT ----------------
income = st.number_input("Enter your taxable income (₹)", min_value=0, step=50000)

# ---------------- TAX CALC ----------------
def calculate_tax_slabs(income):
    slabs = [
        (400000, 0.0),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float('inf'), 0.30)
    ]

    prev = 0
    tax = 0
    breakdown = []

    for limit, rate in slabs:
        if income > prev:
            taxable = min(income, limit) - prev
            slab_tax = taxable * rate
            tax += slab_tax

            breakdown.append({
                "Slab": f"₹{prev:,.0f} - ₹{limit if limit != float('inf') else '∞'}",
                "Tax": slab_tax
            })

            prev = limit
        else:
            break

    return tax, breakdown

# ---------------- BUTTON ----------------
if st.button("🚀 Calculate Tax"):
    tax, breakdown = calculate_tax_slabs(income)

    rebate = min(tax, 60000) if income <= 1200000 else 0
    tax_after_rebate = tax - rebate
    cess = tax_after_rebate * 0.04
    final_tax = tax_after_rebate + cess

    # METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("💼 Income", f"₹{income:,.0f}")
    col2.metric("🧾 Tax After Rebate", f"₹{tax_after_rebate:,.0f}")
    col3.metric("💸 Final Tax", f"₹{final_tax:,.0f}")

    st.divider()

    # ---------------- CHART ----------------
    df = pd.DataFrame(breakdown)

    if not df.empty:
        fig = px.bar(
            df,
            y="Slab",
            x="Tax",
            orientation="h",
            text="Tax",
            color="Tax",
            color_continuous_scale="Blues"
        )

        fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")

        fig.update_layout(
            title="📊 Tax Contribution by Income Slab",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font_color="white",
            xaxis_title="Tax Amount (₹)",
            yaxis_title="Income Slab",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- EXPLANATION ----------------
    with st.expander("📘 How this works"):
        st.write("""
        - Tax is calculated slab by slab
        - Rebate u/s 87A applies if income ≤ ₹12 lakh
        - 4% cess is added after rebate
        - Chart shows how much tax each slab contributes
        """)

    with st.expander("📄 Detailed Calculation"):
        st.write(f"Tax before rebate: ₹{tax:,.0f}")
        st.write(f"Rebate: ₹{rebate:,.0f}")
        st.write(f"Cess (4%): ₹{cess:,.0f}")

# ---------------- LEADS DASHBOARD ----------------
if st.session_state.leads:
    st.subheader("📋 Collected Leads")

    lead_df = pd.DataFrame(st.session_state.leads)
    st.dataframe(lead_df, use_container_width=True)