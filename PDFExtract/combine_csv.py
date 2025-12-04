import csv
from pathlib import Path
from datetime import datetime

IN_DIR = Path(__file__).resolve().parent / "extracted_csv"
OUT_DIR = IN_DIR / "combined"
OUT_DIR.mkdir(parents=True, exist_ok=True)
date = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_FILE = OUT_DIR / f"combined_tables_{date}.csv"

def combine_csvs(input_dir=IN_DIR, out_file=OUT_FILE, add_blank_after: bool = True) -> int:
    """Combine all .csv files in input_dir into out_file.
    Writes a single blank row after each appended file when add_blank_after=True.
    Returns total number of rows written (excluding blank separator rows)."""
    input_dir = Path(input_dir)
    out_file = Path(out_file)
    
    # ensure out_file parent directory exists
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    files = sorted([p for p in input_dir.glob("*.csv") if p.is_file()])
    if not files:
        print("No CSV files found in", input_dir)
        return 0

    total_rows = 0
    with out_file.open("w", newline="", encoding="utf-8-sig") as fout:
        writer = csv.writer(fout)
        for fpath in files:
            with fpath.open("r", encoding="utf-8-sig", newline="") as fin:
                reader = csv.reader(fin)
                written_for_file = 0
                for row in reader:
                    writer.writerow(row)
                    written_for_file += 1
                total_rows += written_for_file
            if add_blank_after:
                writer.writerow([])  # blank separator row

    print(f"Combined {len(files)} files into {out_file} (data rows: {total_rows})")
    return total_rows

if __name__ == "__main__":
    combine_csvs(IN_DIR, OUT_FILE)