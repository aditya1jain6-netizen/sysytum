import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="CA Study Dashboard", layout="wide")

st.title("📚 CA Study Performance Dashboard")

FILE_NAME = "study_data.csv"

# Load data
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
    df["Date"] = pd.to_datetime(df["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])

# ---- INPUT ----
st.header("➕ Add Study Entry")

with st.form("study_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date")
        subject_option = st.selectbox("Subject", ["Accounts", "Law", "Tax", "Audit", "Other"])
        
        if subject_option == "Other":
            subject = st.text_input("Enter Subject Name")
        else:
            subject = subject_option

    with col2:
        topic = st.text_input("Topic")
        hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if subject == "":
            st.error("Please enter subject name")
        else:
            new_data = pd.DataFrame([[date, subject, topic, hours]],
                                    columns=["Date", "Subject", "Topic", "Hours"])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            st.success("Entry Added!")

# ---- DASHBOARD ----
st.header("📊 Dashboard")

if not df.empty:

    df = df.sort_values("Date")

    total_hours = df["Hours"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hours", round(total_hours, 2))
    col2.metric("Total Days", df["Date"].nunique())

    # Productivity Score
    total_days = (df["Date"].max() - df["Date"].min()).days + 1
    studied_days = df["Date"].nunique()
    consistency = studied_days / total_days if total_days > 0 else 0
    productivity_score = total_hours * consistency

    col3.metric("Productivity Score", round(productivity_score, 2))

    # Charts
    st.subheader("Subject-wise Study")
    subject_hours = df.groupby("Subject")["Hours"].sum()
    st.bar_chart(subject_hours)

    st.subheader("Daily Trend")
    daily_hours = df.groupby("Date")["Hours"].sum()
    st.line_chart(daily_hours)

    # ---- Study Streak ----
    st.header("🔥 Study Streak")

    dates = df["Date"].drop_duplicates().sort_values()
    streak = 1

    for i in range(len(dates)-1, 0, -1):
        if (dates.iloc[i] - dates.iloc[i-1]).days == 1:
            streak += 1
        else:
            break

    st.metric("Current Streak (Days)", streak)

    # ---- Weekly Goal ----
    st.header("🎯 Weekly Goal")

    goal = st.number_input("Set Weekly Goal (Hours)", min_value=1.0, value=40.0)

    last_7_days = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=6))]
    weekly_hours = last_7_days["Hours"].sum()

    progress = min(weekly_hours / goal, 1.0)
    st.progress(progress)
    st.write(f"Weekly Hours: {weekly_hours} / {goal}")

    # ---- Improvement Trend ----
    st.header("📉 Improvement Trend")

    last_week = df[(df["Date"] >= df["Date"].max() - pd.Timedelta(days=6))]
    prev_week = df[(df["Date"] >= df["Date"].max() - pd.Timedelta(days=13)) &
                   (df["Date"] < df["Date"].max() - pd.Timedelta(days=6))]

    last_week_hours = last_week["Hours"].sum()
    prev_week_hours = prev_week["Hours"].sum()

    if last_week_hours > prev_week_hours:
        st.success("You are improving 📈")
    elif last_week_hours < prev_week_hours:
        st.warning("Study time decreased 📉")
    else:
        st.info("No change in study pattern")

    # ---- Exam Countdown ----
    st.header("📅 Exam Countdown")

    exam_date = st.date_input("Select Your Exam Date", datetime(2026, 11, 1))

    today = datetime.today().date()
    days_left = (exam_date - today).days

    if days_left > 0:
        st.metric("Days Left", days_left)
    else:
        st.error("Exam date has passed!")

    # ---- WOW FEATURE 1: Smart Recommendation ----
    st.header("🤖 Smart Recommendation")

    if not subject_hours.empty:
        least_subject = subject_hours.idxmin()
        st.write(f"👉 Focus more on: **{least_subject}**")

        if consistency < 0.5:
            st.warning("Low consistency. Try daily study.")
        else:
            st.success("Good consistency 👍")

    # ---- WOW FEATURE 2: Daily Study Plan ----
    st.subheader("📌 Required Daily Study Plan")

    target_total_hours = 300  # adjust if needed

    remaining_hours = max(target_total_hours - total_hours, 0)

    if days_left > 0:
        daily_required = remaining_hours / days_left

        st.write(f"🎯 Target: {target_total_hours} hours before exam")
        st.write(f"👉 You need **{round(daily_required, 2)} hours/day**")

        if daily_required > 8:
            st.error("Very high load! Start immediately.")
        elif daily_required > 5:
            st.warning("Moderate pressure. Stay consistent.")
        else:
            st.success("You're on track 👍")

else:
    st.info("No data yet. Add some entries.")