import streamlit as st
import os
import csv
import json
import base64
import requests
from io import StringIO
from datetime import datetime, date, timedelta
import calendar

st.set_page_config(page_title="Adhyay Academy — Attendance", layout="centered")
st.title("Adhyay Academy — Daily Attendance Tracker")

# --- Config / options ---
CLASS_OPTIONS = ["8th CBSE", "9th CBSE", "10th CBSE"]
SUBJECT_OPTIONS = ["Mathematics", "SST", "Science", "English", "Others"]
FACULTY_OPTIONS = ["Pravin K", "Shubham K", "Sujata G", "Shubham S"]
START_TIMES = [f"{h:02d}:{m:02d}" for h in range(6, 23) for m in (0, 30)]

# GitHub repo settings from Streamlit secrets (recommended) or env
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN") if "GITHUB_TOKEN" in st.secrets else os.getenv("GITHUB_TOKEN")
GITHUB_REPO = st.secrets.get("GITHUB_REPO") if "GITHUB_REPO" in st.secrets else os.getenv("GITHUB_REPO")
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main") if "GITHUB_BRANCH" in st.secrets else os.getenv("GITHUB_BRANCH", "main")
DATA_DIR = st.secrets.get("DATA_DIR", "Attendance_tracking") if "DATA_DIR" in st.secrets else os.getenv("DATA_DIR", "Attendance_tracking")

HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# st.markdown(
#     "This app saves monthly attendance CSVs directly into the configured GitHub repository.\n\n"
#     "Make sure `GITHUB_TOKEN`, `GITHUB_REPO` and optionally `DATA_DIR` are set in Streamlit Secrets."
# )

def compute_end_time(start_str: str, hours: float) -> str:
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

def github_file_path_for_date(d: date) -> str:
    fname = f"attendance_{d.year}_{d.month:02d}.csv"
    return f"{DATA_DIR}/{fname}"

def get_repo_file(path: str):
    api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    params = {"ref": GITHUB_BRANCH}
    r = requests.get(api, headers=HEADERS, params=params, timeout=30)
    if r.status_code == 200:
        j = r.json()
        content = base64.b64decode(j["content"]).decode("utf-8")
        return content, j["sha"]
    if r.status_code == 404:
        return None, None
    r.raise_for_status()

def put_repo_file(path: str, content_text: str, sha: str = None, message: str = "Update attendance"):
    api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content_text.encode("utf-8")).decode("utf-8"),
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(api, headers=HEADERS, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()

def normalize_row_tuple(row):
    return tuple(str(x).strip().lower() for x in row)

# --- new: time slot parsing and overlap helpers ---
def parse_time_slot(slot: str):
    """Return (start_minutes, end_minutes) for a slot like '15:00-18:00'. 
    If end <= start, end is considered next day (adds 24*60)."""
    try:
        parts = slot.split("-", 1)
        s = parts[0].strip()
        e = parts[1].strip()
        t1 = datetime.strptime(s, "%H:%M")
        t2 = datetime.strptime(e, "%H:%M")
        m1 = t1.hour * 60 + t1.minute
        m2 = t2.hour * 60 + t2.minute
        if m2 <= m1:
            m2 += 24 * 60
        return m1, m2
    except Exception:
        return None

def intervals_overlap(a_start, a_end, b_start, b_end):
    return not (a_end <= b_start or b_end <= a_start)

def csv_text_to_rows(text):
    sio = StringIO(text)
    reader = csv.reader(sio)
    return list(reader)

def rows_to_csv_text(rows):
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerows(rows)
    return sio.getvalue()

# --- UI form ---
with st.form("attendance_form", clear_on_submit=True):
    att_date = st.date_input("Date", value=date.today())
    day_name = att_date.strftime("%A")
    st.write("Day:", day_name)

    start_time = st.selectbox("Start time (HH:MM)", START_TIMES, index=18)
    hours = st.number_input("Duration (hours, 0.5 steps)", min_value=0.5, max_value=12.0, step=0.5, value=1.0)
    end_time_display = compute_end_time(start_time, hours)
    # st.markdown(f"**End time:** {end_time_display if end_time_display else 'Invalid'}")
    end_time_24 = end_time_display.split()[0] if end_time_display else ""

    cls = st.selectbox("Class", CLASS_OPTIONS)
    subj = st.selectbox("Subject", SUBJECT_OPTIONS)
    faculty = st.selectbox("Faculty name", FACULTY_OPTIONS)

    submit = st.form_submit_button("Add Attendance")

if submit:
    if not GITHUB_TOKEN or not GITHUB_REPO:
        st.error("GitHub token or repo not configured. Set GITHUB_TOKEN and GITHUB_REPO in Streamlit secrets.")
    elif not (start_time and end_time_24 and cls and subj and faculty):
        st.warning("Please fill all fields.")
    else:
        date_str = att_date.strftime("%d-%m-%Y")
        time_slot = f"{start_time}-{end_time_24}"
        path = github_file_path_for_date(att_date)

        header = ["Day", "Date", "Time", "Class", "Subject", "Faculty"]
        new_row = [day_name, date_str, time_slot, cls, subj, faculty]
        new_tuple = normalize_row_tuple(new_row)

        try:
            existing_text, sha = get_repo_file(path)
            if existing_text:
                rows = csv_text_to_rows(existing_text)
                # If first row looks like header, keep it; else assume no header
                has_header = False
                if rows and [c.strip().lower() for c in rows[0]] == [h.lower() for h in header]:
                    has_header = True
                    data_rows = rows[1:]
                else:
                    data_rows = rows

                # check duplicate
                normalized_existing = [normalize_row_tuple(r) for r in data_rows if any(cell.strip() for cell in r)]
                if new_tuple in normalized_existing:
                    st.warning("Duplicate record detected in repository monthly file; not saved.")
                else:
                    # --- new: check time-overlap conflicts for same Date/Class (ignore subject) ---
                    conflict = False
                    try:
                        new_interval = parse_time_slot(time_slot)
                        for r in data_rows:
                            if len(r) < 6:
                                continue
                            existing_date = r[1].strip()
                            existing_time = r[2].strip()
                            existing_class = r[3].strip().lower()
                            existing_subj = r[4].strip().lower()
                            existing_faculty = r[5].strip()

                            # consider only same date and same class (ignore subject/faculty)
                            if existing_date == date_str and existing_class == cls.strip().lower():
                                existing_interval = parse_time_slot(existing_time)   # <-- parse before use
                                if new_interval and existing_interval and intervals_overlap(new_interval[0], new_interval[1], existing_interval[0], existing_interval[1]):
                                    st.error(f"Time overlap conflict: {faculty} ({time_slot}) overlaps with {existing_faculty} ({existing_time}) for class '{cls}' on {date_str}. Not saved.")
                                    conflict = True
                                    break
                    except Exception:
                        # if parsing fails, don't block save on overlap check; proceed to save or let duplicate detection handle it
                        conflict = False

                    if not conflict:
                        data_rows.append(new_row)
                        out_rows = ([header] if has_header else []) + data_rows
                        updated_text = rows_to_csv_text(out_rows)
                        # try put, handle rare race: retry once if conflict
                        try:
                            put_repo_file(path, updated_text, sha=sha, message=f"Add attendance {date_str} {time_slot} {faculty}")
                            st.success("Saved attendance to repository monthly file.")
                        except requests.HTTPError as e:
                            # fetch latest and retry once
                            st.info("Retrying due to concurrent update...")
                            existing_text2, sha2 = get_repo_file(path)
                            if existing_text2:
                                rows2 = csv_text_to_rows(existing_text2)
                                has_header2 = False
                                if rows2 and [c.strip().lower() for c in rows2[0]] == [h.lower() for h in header]:
                                    has_header2 = True
                                    data_rows2 = rows2[1:]
                                else:
                                    data_rows2 = rows2
                                normalized_existing2 = [normalize_row_tuple(r) for r in data_rows2 if any(cell.strip() for cell in r)]
                                if new_tuple in normalized_existing2:
                                    st.warning("Duplicate detected after retry; not saved.")
                                else:
                                    # re-run overlap check on latest data
                                    conflict2 = False
                                    try:
                                        new_interval = parse_time_slot(time_slot)
                                        for r in data_rows2:
                                            if len(r) < 6:
                                                continue
                                            existing_date = r[1].strip()
                                            existing_time = r[2].strip()
                                            existing_class = r[3].strip().lower()
                                            existing_subj = r[4].strip().lower()
                                            existing_faculty = r[5].strip()

                                            # consider only same date and same class (ignore subject/faculty)
                                            if existing_date == date_str and existing_class == cls.strip().lower():
                                                existing_interval = parse_time_slot(existing_time)  # <-- parse before use
                                                if new_interval and existing_interval and intervals_overlap(new_interval[0], new_interval[1], existing_interval[0], existing_interval[1]):
                                                    st.error(f"Time overlap conflict after retry: {faculty} ({time_slot}) overlaps with {existing_faculty} ({existing_time}) for class '{cls}' on {date_str}. Not saved.")
                                                    conflict2 = True
                                                    break
                                    except Exception:
                                        conflict2 = False

                                    if not conflict2:
                                        data_rows2.append(new_row)
                                        out_rows2 = ([header] if has_header2 else []) + data_rows2
                                        updated_text2 = rows_to_csv_text(out_rows2)
                                        put_repo_file(path, updated_text2, sha=sha2, message=f"Add attendance {date_str} {time_slot} {faculty}")
                                        st.success("Saved attendance to repository monthly file (after retry).")
                            else:
                                # file disappeared between calls; create new
                                put_repo_file(path, rows_to_csv_text([header, new_row]), message=f"Create attendance file {os.path.basename(path)}")
                                st.success("Created and saved monthly file in repository.")
            else:
                # create new file with header + row
                content = rows_to_csv_text([header, new_row])
                put_repo_file(path, content, message=f"Create attendance file {os.path.basename(path)}")
                st.success("Created and saved monthly file in repository.")
        except requests.HTTPError as e:
            st.error(f"GitHub API error: {e.response.status_code} {e.response.reason}")
        except Exception as e:
            st.error(f"Error saving attendance: {e}")

st.markdown("---")

# --- Download monthwise CSV ---

st.markdown("## Download monthly CSV")
col1, col2 = st.columns(2)
with col1:
    years = [datetime.now().year - 1, datetime.now().year, datetime.now().year + 1]
    sel_year = st.selectbox("Year", years, index=1)
with col2:
    sel_month = st.selectbox("Month", list(range(1, 13)), index=datetime.now().month - 1,
                             format_func=lambda m: calendar.month_name[m])

if st.button("Download CSV for selected month"):
    target_date = date(sel_year, sel_month, 1)
    path = github_file_path_for_date(target_date)
    try:
        content, sha = get_repo_file(path)
        if content:
            st.success(f"Found file: {os.path.basename(path)}")
            st.download_button("Download CSV", data=content.encode("utf-8"), file_name=os.path.basename(path), mime="text/csv")
        else:
            st.warning("No CSV found for the selected month.")
    except requests.HTTPError as e:
        body = ""
        try:
            body = e.response.text
        except Exception:
            pass
        st.error(f"GitHub API error: {e.response.status_code} {e.response.reason}\n{body}")
    except Exception as e:
        st.error(f"Error fetching file: {e}")

# --- Show current month's records ---

if st.button("Show current month's records"):
    target_date = date.today()
    path = github_file_path_for_date(target_date)
    try:
        content, sha = get_repo_file(path)
        if content:
            rows = csv_text_to_rows(content)
            if rows:
                header = rows[0]
                data_rows = rows[1:] if len(rows) > 1 else []
                st.info(f"{calendar.month_name[target_date.month]} {target_date.year} — {len(data_rows)} record(s)")
                # display as list of dicts for a nice table
                table_data = [dict(zip(header, r)) for r in data_rows]
                st.table(table_data)
            else:
                st.warning("CSV is empty.")
        else:
            st.warning("No CSV found for the current month.")
    except requests.HTTPError as e:
        body = ""
        try:
            body = e.response.text
        except Exception:
            pass
        st.error(f"GitHub API error: {e.response.status_code} {e.response.reason}\n{body}")
    except Exception as e:
        st.error(f"Error fetching current month's records: {e}")