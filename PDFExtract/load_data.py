import csv
from pathlib import Path
from datetime import datetime
import sys
from transform_data import get_data_list

# Prepare header rows (matching the CSV structure) without Source column
header1 = ['', 'Rainfall', '', '', 'Depth', '', 'Flow', '', 'Velocity', '']
header2 = ['', 'Depth (mm)', 'Peak (mm/hr)', 'Average (mm/hr)',
           'Min (m)', 'Max (m)',
           'Min (m3/s)', 'Volume (m3)', 'Min (m/s)', 'Max (m/s)']

def process_file(path: Path) -> list:
    """Process a single file with get_data_list and return CSV rows for that file."""
    rows = [header1, header2]
    try:
        data = get_data_list(path)
    except Exception as e:
        print(f"Skipping {path.name}: error calling get_data_list: {e}")
        return rows

    for item in data:
        name = list(item.keys())[0]
        block = item[name]

        def get(dct, key):
            return dct.get(key, '') if isinstance(dct, dict) else ''

        rainfall = block.get('Rainfall', {})
        r_depth = get(rainfall, 'Depth (mm)')
        r_peak = get(rainfall, 'Peak (mm/hr)')
        r_avg = get(rainfall, 'Average (mm/hr)')

        depth = block.get('Depth', {})
        d_min = get(depth, 'Min (m)')
        d_max = get(depth, 'Max (m)')

        flow = block.get('Flow', {})
        f_min = get(flow, 'Min (m3/s)')
        f_vol = get(flow, 'Volume (m3)')
        f_max = get(flow, 'Max (m3/s)')

        vel = block.get('Velocity', {})
        v_min = get(vel, 'Min (m/s)')
        v_max = get(vel, 'Max (m/s)')

        row = [
            name,                # Row label (e.g. Rain, Observed)
            r_depth, r_peak, r_avg,
            d_min, d_max,
            f_min, f_vol, v_min, v_max
        ]
        rows.append(row)
    return rows

if __name__ == "__main__":
    # folder can be passed as first CLI arg, otherwise use default folder
    folder_arg = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\DELL\Projects\python\extracted_pages"
    folder = Path(folder_arg)
    if not folder.exists() or not folder.is_dir():
        print(f"Folder not found: {folder}")
        sys.exit(1)

    out_dir = Path(__file__).resolve().parent / "extracted_csv"
    out_dir.mkdir(parents=True, exist_ok=True)

    date = datetime.now().strftime("%Y%m%d_%H%M%S")

    processed_count = 0
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        rows = process_file(path)
        # write one CSV per input file
        out_fname = out_dir / f"{path.stem}_table_{date}.csv"
        with out_fname.open("w", newline='', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        processed_count += 1
        print(f"Wrote {len(rows)-2} data rows for {path.name} to {out_fname}")

    print(f"Processed {processed_count} files. Output folder: {out_dir}")