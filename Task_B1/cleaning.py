"""Task B1: cleaning rules and normalisation for the station CSV files (csv module only)."""
import csv
import statistics
from collections import Counter
from datetime import datetime

FAHRENHEIT_STATIONS = {"Alandur", "Velachery"}      # the two stations that report in Fahrenheit
LIMITS = {"pm25": (0, 999), "pm10": (0, 999), "no": (0, 999), "temp": (-10, 60)}   # valid range (temp in Celsius)
FIELDS = ["pm25", "pm10", "no", "temp"]


def clean_name(text):
    return " ".join(text.split()).title()              # ' t nagar ' -> 'T Nagar'


def clean_date(text):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def to_number(text):
    text = (text or "").strip()
    if text == "" or text.upper() == "NA":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def clean_rows(rows):
    """rows: list of dicts read by csv.DictReader. Returns (cleaned rows, Counter of what was fixed)."""
    stats = Counter()
    seen, out = set(), []
    for r in rows:
        station, date = clean_name(r["station"]), clean_date(r["date"])
        try:
            hour = int(r["hour"])
        except ValueError:
            hour = -1
        if date is None or not 0 <= hour <= 23:
            stats["bad date/hour (row dropped)"] += 1
            continue
        key = (station, date, hour)
        if key in seen:
            stats["duplicate rows removed"] += 1
            continue
        seen.add(key)
        row = {"station": station, "date": date, "hour": hour, "filled": 0}
        for col in FIELDS:
            v = to_number(r[col])
            if v is None:
                stats["missing values"] += 1
            else:
                if col == "temp" and station in FAHRENHEIT_STATIONS:
                    v = round((v - 32) * 5 / 9, 1)
                    stats["Fahrenheit converted"] += 1
                lo, hi = LIMITS[col]
                if not lo <= v <= hi:
                    stats["impossible values"] += 1
                    v = None
            row[col] = v
        out.append(row)
    out.sort(key=lambda x: (x["station"], x["date"], x["hour"]))
    last = {}                                           # forward fill: previous valid value of the same station
    for row in out:
        for col in FIELDS:
            if row[col] is None:
                prev = last.get((row["station"], col))
                if prev is not None:
                    row[col] = prev
                    row["filled"] = 1
                    stats["values forward-filled"] += 1
                else:
                    stats["leading gaps left empty"] += 1
            else:
                last[(row["station"], col)] = row[col]
    return out, stats


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def min_max(values):
    lo, hi = min(values), max(values)
    return [0.0 if hi == lo else round((v - lo) / (hi - lo), 3) for v in values]


def z_score(values):
    m, s = statistics.mean(values), statistics.pstdev(values)
    return [0.0 if s == 0 else round((v - m) / s, 3) for v in values]


if __name__ == "__main__":
    raw = read_csv("sample_raw.csv")
    print("BEFORE cleaning (%d rows)" % len(raw))
    for r in raw:
        print("  ", list(r.values()))
    cleaned, stats = clean_rows(raw)
    print("\nAFTER cleaning (%d rows)" % len(cleaned))
    for r in cleaned:
        print("  ", [r[k] for k in ("station", "date", "hour", "pm25", "pm10", "no", "temp", "filled")])
    print("\nWhat was fixed:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    pm = [r["pm25"] for r in cleaned if r["pm25"] is not None]
    print("\nPM2.5 values:", pm)
    print("min-max :", min_max(pm))
    print("z-score :", z_score(pm))
