import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tax Calculator FY 2025-26", layout="wide")

# Elegant styling
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1, h2, h3, p {
    color: #ffffff;
}
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Income Tax Calculator (FY 2025-26)")
st.caption("New Regime | Includes Rebate u/s 87A + 4% Cess")

income = st.number_input("Enter your taxable income (₹)", min_value=0, step=50000)

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
    total_tax = 0
    breakdown = []

    for limit, rate in slabs:
        if income > prev:
            taxable = min(income, limit) - prev
            slab_tax = taxable * rate
            total_tax += slab_tax

            breakdown.append({
                "Income Slab": f"₹{prev:,.0f} - ₹{limit if limit != float('inf') else '∞'}",
                "Tax in ₹": slab_tax
            })

            prev = limit
        else:
            break

    return total_tax, breakdown

if st.button("🚀 Calculate Tax"):
    tax, breakdown = calculate_tax_slabs(income)

    rebate = min(tax, 60000) if income <= 1200000 else 0
    tax_after_rebate = tax - rebate
    cess = tax_after_rebate * 0.04
    final_tax = tax_after_rebate + cess

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("💼 Income", f"₹{income:,.0f}")
    col2.metric("🧾 Tax After Rebate", f"₹{tax_after_rebate:,.0f}")
    col3.metric("💸 Final Tax (incl. cess)", f"₹{final_tax:,.0f}")

    st.divider()

    df = pd.DataFrame(breakdown)

    if not df.empty:
        # Horizontal bar chart
        fig = px.bar(
            df,
            y="Income Slab",
            x="Tax in ₹",
            orientation="h",
            text="Tax in ₹",
            color="Tax in ₹",
            color_continuous_scale="Blues"
        )

        # Format labels
        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            title="📊 Tax Contribution from Each Income Slab",
            xaxis_title="Tax Amount (₹)",
            yaxis_title="Income Slabs",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font_color="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Explanation section
    with st.expander("📘 How to read this chart"):
        st.write("""
        - Each bar represents a **tax slab**
        - Length of the bar = **tax paid in that slab**
        - Higher slabs contribute more tax due to higher rates
        - If your income is low, fewer slabs will appear
        """)

    # Breakdown
    with st.expander("📄 Detailed Breakdown"):
        st.write(f"Tax before rebate: ₹{tax:,.0f}")
        st.write(f"Rebate (87A): ₹{rebate:,.0f}")
        st.write(f"Cess (4%): ₹{cess:,.0f}")