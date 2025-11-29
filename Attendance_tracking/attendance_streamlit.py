import streamlit as st
import os
import csv
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Adhyay Academy — Attendance", layout="centered")
st.title("Adhyay Academy — Daily Attendance Tracker")

# Where monthly attendance files are stored (directory)
DATA_DIR = r"C:\Users\DELL\Projects\python\Attendance_tracking"
os.makedirs(DATA_DIR, exist_ok=True)

st.markdown("Add today's attendance record. Records are saved to a CSV per month (no upload/download here).")

# fixed dropdown options
CLASS_OPTIONS = ["8th CBSE", "9th CBSE", "10th CBSE"]
SUBJECT_OPTIONS = ["Mathematics", "SST", "Science", "English", "Others"]
FACULTY_OPTIONS = ["Pravin K", "Shubham K", "Sujata G", "Shubham S"]

# generate start time options (every 30 minutes between 06:00 and 22:30)
START_TIMES = [f"{h:02d}:{m:02d}" for h in range(6, 23) for m in (0, 30)]

def compute_end_time(start_str: str, hours: float) -> str:
    """
    Compute end time given start_str "HH:MM" and duration in hours (e.g. 1.5).
    Returns "HH:MM (h:MM am/pm)" and adds " (+1 day)" if crossing midnight.
    """
    try:
        start_dt = datetime.strptime(start_str, "%H:%M")
        total_minutes = int(round(hours * 60))
        end_dt = start_dt + timedelta(minutes=total_minutes)

        end_24 = end_dt.strftime("%H:%M")
        end_ampm = end_dt.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        note = " (+1 day)" if end_dt.day != start_dt.day else ""
        return f"{end_24} ({end_ampm}){note}"
    except Exception:
        return ""

def month_file_for_date(d: date) -> str:
    """Return monthly CSV path for given date: attendance_YYYY_MM.csv"""
    fname = f"attendance_{d.year}_{d.month:02d}.csv"
    return os.path.join(DATA_DIR, fname)

def record_exists(path, day, date_str, time_slot, cls, subj, faculty):
    """Check CSV for an exact matching record (case-insensitive trim)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                # normalize fields
                def norm(x): 
                    return (str(x).strip().lower() if x is not None else "")
                if (norm(r.get("Day")) == norm(day) and
                    norm(r.get("Date")) == norm(date_str) and
                    norm(r.get("Time")) == norm(time_slot) and
                    norm(r.get("Class")) == norm(cls) and
                    norm(r.get("Subject")) == norm(subj) and
                    norm(r.get("Faculty")) == norm(faculty)):
                    return True
    except Exception:
        return False
    return False

with st.form("attendance_form", clear_on_submit=True):
    att_date = st.date_input("Date", value=date.today())
    # show day automatically
    day_name = att_date.strftime("%A")
    st.write("Day:", day_name)

    # Time: select start time and hours
    start_time = st.selectbox("Start time", START_TIMES, index=18)  # default ~15:00
    hours = st.number_input("Duration (hours, use 0.5 for 30 mins)", min_value=0.5, max_value=12.0, step=0.5, value=1.0)
    end_time_display = compute_end_time(start_time, hours)
    st.markdown(f"**End time:** {end_time_display if end_time_display else 'Invalid start/time'}")
    # use the 24-hour part for saving the time slot
    end_time_24 = end_time_display.split()[0] if end_time_display else ""

    # Class, Subject, Faculty dropdowns
    cls = st.selectbox("Class", CLASS_OPTIONS)
    subj = st.selectbox("Subject", SUBJECT_OPTIONS)
    faculty = st.selectbox("Faculty name", FACULTY_OPTIONS)

    submit = st.form_submit_button("Add Attendance")

if submit:
    if not (start_time and end_time_24 and cls and subj and faculty):
        st.warning("Please fill all fields.")
    else:
        date_str = att_date.strftime("%d-%m-%Y")
        time_slot = f"{start_time}-{end_time_24}"
        # determine monthly file path
        file_path = month_file_for_date(att_date)

        # duplicate check in monthly file
        if record_exists(file_path, day_name, date_str, time_slot, cls, subj, faculty):
            st.warning("Duplicate record detected — this attendance row already exists in the monthly file. Not saved.")
        else:
            row = [day_name, date_str, time_slot, cls, subj, faculty]
            header = ["Day", "Date", "Time", "Class", "Subject", "Faculty"]
            write_header = not os.path.exists(file_path)
            try:
                with open(file_path, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    if write_header:
                        writer.writerow(header)
                    writer.writerow(row)
                st.success(f"Attendance saved for {faculty} on {date_str} ({time_slot}) to {os.path.basename(file_path)}.")
            except Exception as e:
                st.error(f"Could not save attendance: {e}")

st.markdown("---")
st.caption("Records are saved per-month (attendance_YYYY_MM.csv). Hours / Hourly charge / Total columns are intentionally excluded.")