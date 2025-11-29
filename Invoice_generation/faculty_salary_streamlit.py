import streamlit as st
import pandas as pd
import os
import io
import zipfile
import tempfile
from datetime import datetime

# faculty generators
from faculty_salary_generation_invoice import generate_faculty_invoice, generate_combined_invoice as faculty_combined

# student generators
from Fee_completion_invoice import read_student_data, generate_combined_invoice as student_combined, generate_detailed_invoice as student_detailed

st.set_page_config(page_title="Adhyay Academy — Invoice Generator", layout="centered")
st.title("Adhyay Academy — Invoice Generator (Faculty / Student)")

mode = st.radio("Select mode", ("Faculty Salary", "Student Fees"))

if mode == "Faculty Salary":
    uploaded = st.file_uploader("Upload CSV (Date dd-mm-yyyy)", type="csv")
    gen_ind = st.checkbox("Generate Individual Invoices", True)
    gen_comb = st.checkbox("Generate Combined Invoice", True)

    if st.button("Generate") and uploaded:
        try:
            df = pd.read_csv(uploaded)
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            first_date = df['Date'].dropna().iloc[0] if not df['Date'].dropna().empty else pd.Timestamp.now()
            month = first_date.strftime("%B")
            year = first_date.year

            out_paths = []
            with tempfile.TemporaryDirectory() as tmpdir:
                if gen_ind:
                    for faculty in df['Faculty'].unique():
                        fac_df = df[df['Faculty'] == faculty]
                        path = generate_faculty_invoice(fac_df, faculty, month, year)
                        if os.path.exists(path):
                            out_paths.append(path)
                if gen_comb:
                    path = faculty_combined(df, month, year)
                    if os.path.exists(path):
                        out_paths.append(path)

                if not out_paths:
                    st.warning("No files generated.")
                else:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        for p in out_paths:
                            zf.write(p, arcname=os.path.basename(p))
                    zip_buffer.seek(0)
                    st.download_button("Download invoices ZIP", zip_buffer, file_name=f"invoices_faculty_{month}_{year}.zip")
                    st.success(f"Generated {len(out_paths)} file(s).")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Upload CSV and click Generate.")

else:  # Student Fees
    uploaded = st.file_uploader("Upload Excel (.xls/.xlsx) — all sheets will be processed", type=["xls", "xlsx"])
    gen_comb = st.checkbox("Generate combined admin report", value=True)
    gen_detailed = st.checkbox("Generate detailed invoices for each student", value=False)

    if st.button("Generate Student Invoices"):

        if not uploaded:
            st.warning("Please upload an Excel file first.")
        else:
            tmp_path = None
            try:
                # save uploaded to a temp file because read_student_data expects a path
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                    tmp.write(uploaded.getbuffer())
                    tmp_path = tmp.name

                st.info("Reading student data...")
                students_fees = read_student_data(tmp_path, detailed_report=gen_detailed)

                if not students_fees:
                    st.warning("No student records found in the uploaded file.")
                else:
                    out_paths = []

                    if gen_detailed:
                        st.info("Generating detailed student invoices...")
                        for idx, (student_name, fees_data) in enumerate(students_fees.items(), 1):
                            st.write(f"{idx}. {student_name} ({fees_data.get('class_name','')})")
                            path = student_detailed(student_name, fees_data)
                            if os.path.exists(path):
                                out_paths.append(path)

                    if gen_comb:
                        st.info("Generating combined student report...")
                        combined_path = student_combined(students_fees)
                        if os.path.exists(combined_path):
                            out_paths.append(combined_path)

                    if out_paths:
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                            for p in out_paths:
                                zf.write(p, arcname=os.path.basename(p))
                        zip_buffer.seek(0)
                        fname = f"student_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                        st.download_button("Download all invoices (ZIP)", data=zip_buffer, file_name=fname, mime="application/zip")
                        st.success(f"Generated {len(out_paths)} file(s).")
                    else:
                        st.warning("No PDF files were generated.")

            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)