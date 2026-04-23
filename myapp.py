import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CA Study Dashboard", layout="wide")
st.title("📚 CA Study Performance Dashboard")

FILE_NAME = "study_data.csv"

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])

        if "Hours" in df.columns:
            df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce").fillna(0)

        return df
    else:
        return pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])

df = load_data()

# ---------------- SAVE DATA ----------------
def save_data(dataframe):
    dataframe.to_csv(FILE_NAME, index=False)

# ---------------- INPUT ----------------
st.header("➕ Add Study Entry")

with st.form("study_form"):
    col1, col2 = st.columns(2)

    with col1:
        date_input = st.date_input("Date")
        subject_option = st.selectbox("Subject", ["Accounts", "Law", "Tax", "Audit", "Other"])

        subject = ""
        if subject_option == "Other":
            subject = st.text_input("Enter Subject Name")
        else:
            subject = subject_option

    with col2:
        topic = st.text_input("Topic")
        hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if subject.strip() == "":
            st.error("Subject cannot be empty")
        else:
            # ✅ FIX: normalize date here (MOST IMPORTANT FIX)
            date = pd.to_datetime(date_input)

            new_row = pd.DataFrame([[date, subject, topic, hours]],
                                   columns=["Date", "Subject", "Topic", "Hours"])

            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Entry Added Successfully!")

# ---------------- STOP IF EMPTY ----------------
if df.empty:
    st.info("No data yet. Add your study entries.")
    st.stop()

# ---------------- SORT (SAFE NOW) ----------------
df = df.sort_values("Date")

# ---------------- METRICS ----------------
total_hours = float(df["Hours"].sum())
unique_days = df["Date"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Hours", round(total_hours, 2))
col2.metric("Active Days", int(unique_days))

# ---------------- PRODUCTIVITY ----------------
try:
    total_days = (df["Date"].max() - df["Date"].min()).days + 1

    if total_days > 0:
        consistency = unique_days / total_days
    else:
        consistency = 0

    productivity_score = total_hours * consistency
except:
    consistency = 0
    productivity_score = 0

col3.metric("Productivity Score", round(productivity_score, 2))

# ---------------- CHARTS ----------------
st.subheader("📊 Subject-wise Study")
subject_hours = df.groupby("Subject")["Hours"].sum()
st.bar_chart(subject_hours)

st.subheader("📈 Daily Trend")
daily_hours = df.groupby("Date")["Hours"].sum()
st.line_chart(daily_hours)

# ---------------- STREAK ----------------
st.header("🔥 Study Streak")

streak = 0
dates = df["Date"].drop_duplicates().sort_values()

if len(dates) > 0:
    streak = 1
    for i in range(len(dates)-1, 0, -1):
        if (dates.iloc[i] - dates.iloc[i-1]).days == 1:
            streak += 1
        else:
            break

st.metric("Current Streak", streak)

# ---------------- WEEKLY GOAL ----------------
st.header("🎯 Weekly Goal")

goal = st.number_input("Set Weekly Goal (Hours)", min_value=1.0, value=40.0)

last_7_days = df[df["Date"] >= (df["Date"].max() - pd.Timedelta(days=6))]
weekly_hours = float(last_7_days["Hours"].sum())

progress = min(weekly_hours / goal, 1.0)
st.progress(progress)

st.write(f"Weekly Progress: {round(weekly_hours,2)} / {goal}")

# ---------------- IMPROVEMENT ----------------
st.header("📉 Improvement Trend")

last_week = df[df["Date"] >= df["Date"].max() - pd.Timedelta(days=6)]
prev_week = df[(df["Date"] >= df["Date"].max() - pd.Timedelta(days=13)) &
               (df["Date"] < df["Date"].max() - pd.Timedelta(days=6))]

last_sum = float(last_week["Hours"].sum())
prev_sum = float(prev_week["Hours"].sum())

if last_sum > prev_sum:
    st.success("Improving 📈")
elif last_sum < prev_sum:
    st.warning("Declining 📉")
else:
    st.info("Stable performance")

# ---------------- EXAM COUNTDOWN ----------------
st.header("📅 Exam Countdown")

exam_date = st.date_input("Select Exam Date", datetime(2026, 11, 1))
exam_date = pd.to_datetime(exam_date)

today = pd.to_datetime(datetime.today().date())
days_left = (exam_date - today).days

if days_left > 0:
    st.metric("Days Left", days_left)
else:
    st.error("Exam date passed")

# ---------------- SMART RECOMMENDATION ----------------
st.header("🤖 Smart Recommendation")

if not subject_hours.empty:
    least_subject = subject_hours.idxmin()
    st.write(f"Focus more on: **{least_subject}**")

    if consistency < 0.5:
        st.warning("Low consistency. Study daily.")
    else:
        st.success("Good consistency 👍")

# ---------------- DAILY PLAN ----------------
st.subheader("📌 Daily Study Plan")

target_hours = 300
remaining = max(target_hours - total_hours, 0)

if days_left > 0:
    daily_required = remaining / days_left
else:
    daily_required = 0

st.write(f"Required Daily Hours: **{round(daily_required,2)}**")

if daily_required > 8:
    st.error("Very high load")
elif daily_required > 5:
    st.warning("Moderate load")
else:
    st.success("Manageable plan")