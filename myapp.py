import streamlit as st
import pandas as pd
import os

st.title("📚 CA Study Tracker")

FILE_NAME = "study_data.csv"

# Load existing data
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])

# ---- Input Section ----
st.header("Add Study Entry")

with st.form("study_form"):
    date = st.date_input("Date")
    subject = st.selectbox("Subject", ["Accounts", "Law", "Tax", "Audit", "Other"])
    topic = st.text_input("Topic")
    hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_data = pd.DataFrame([[date, subject, topic, hours]],
                                columns=["Date", "Subject", "Topic", "Hours"])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)
        st.success("Entry Added!")

# ---- Show Data ----
st.header("Study Data")
st.dataframe(df)

# ---- Basic Stats ----
if not df.empty:
    st.header("Summary")

    total_hours = df["Hours"].sum()
    st.write(f"Total Hours Studied: {total_hours}")

    subject_hours = df.groupby("Subject")["Hours"].sum()
    st.bar_chart(subject_hours)

    daily_hours = df.groupby("Date")["Hours"].sum()
    st.line_chart(daily_hours)

    # Simple insight
    max_sub = subject_hours.idxmax()
    min_sub = subject_hours.idxmin()

    st.subheader("Insights")
    st.write(f"Most Studied Subject: {max_sub}")
    st.write(f"Least Studied Subject: {min_sub}")
else:
    st.info("No data yet. Add some entries.")