"""Task B1 - Complete the Code (TODO 1 and TODO 2 done) plus the extra check for readings above 999."""
import csv
import io

RAW = """station,date,pm25
Adyar,2026-10-01,48
Adyar,2026-10-02,NA
Adyar,2026-10-03,
Guindy,2026-10-01,95
Guindy,2026-10-02,-5
Guindy,2026-10-03,121
"""

# the same data with one extra test row for the new check (a sensor fault of 5000)
RAW_TEST = RAW + "Guindy,2026-10-04,5000\n"


def load_clean(text):
    """Returns (station, date, pm25) tuples for valid, non-negative readings only."""
    rows = []
    # TODO 1: read with csv.DictReader; skip empty, 'NA' or negative pm25; convert to float
    for r in csv.DictReader(io.StringIO(text)):
        raw = r["pm25"].strip()
        if raw == "" or raw.upper() == "NA":
            continue
        value = float(raw)
        if value < 0 or value > 999:          # added check: negative or above 999 is a sensor fault
            continue
        rows.append((r["station"], r["date"], value))
    return rows


def min_max(values):
    # TODO 2: scale each value to 0-1 using (v - min) / (max - min), rounded to 3 decimals
    lo, hi = min(values), max(values)
    return [round((v - lo) / (hi - lo), 3) for v in values]


clean = load_clean(RAW)
print(clean)
print(min_max([pm for _, _, pm in clean]))

print("\nWith the extra test row (Guindy, 2026-10-04, 5000):")
clean2 = load_clean(RAW_TEST)
print(clean2)
assert clean2 == clean, "the 5000 reading must be skipped"
print("5000 skipped: True")
