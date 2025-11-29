import streamlit as st
import pandas as pd
import os
import io
import zipfile
import tempfile
from faculty_salary_generation_invoice import generate_faculty_invoice, generate_combined_invoice

st.title("Adhyay Academy — Faculty Salary Generator (Minimal)")

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

        with tempfile.TemporaryDirectory() as tmpdir:
            out_paths = []
            if gen_ind:
                for faculty in df['Faculty'].unique():
                    fac_df = df[df['Faculty'] == faculty]
                    path = generate_faculty_invoice(fac_df, faculty, month, year)
                    if os.path.exists(path):
                        out_paths.append(path)
            if gen_comb:
                path = generate_combined_invoice(df, month, year)
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
                st.download_button("Download invoices ZIP", zip_buffer, file_name=f"invoices_{month}_{year}.zip")
                st.success(f"Generated {len(out_paths)} file(s).")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Upload CSV and click Generate.")