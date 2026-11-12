"""Generates the raw station CSV files for October 2026 (synthetic data, seed fixed) with the faults of the case study."""
import csv, math, os, random

STATIONS = {  # name: (base PM2.5, reports Fahrenheit?)
    "Adyar": (55, False), "Guindy": (82, False), "Alandur": (70, True), "Velachery": (60, True),
    "T Nagar": (75, False), "Anna Nagar": (58, False), "Besant Nagar": (40, False), "Perungudi": (68, False),
    "Manali": (110, False), "Royapuram": (90, False), "Kodambakkam": (72, False), "Tambaram": (45, False)}


def generate(folder="data", seed=5):
    rnd = random.Random(seed)
    os.makedirs(folder, exist_ok=True)
    for name, (base, fahrenheit) in STATIONS.items():
        rows = []
        for day in range(1, 32):
            for hour in range(24):
                rush = math.exp(-((hour - 8.5) / 2.0) ** 2) + 0.9 * math.exp(-((hour - 20.5) / 2.2) ** 2)
                temp_c = 28 + 5 * math.sin((hour - 9) / 24 * 2 * math.pi) + rnd.gauss(0, 0.8)
                pm25 = max(5, base * (0.75 + 0.55 * rush) - 1.6 * (temp_c - 28) + rnd.gauss(0, 6))
                pm10 = pm25 * 1.7 + rnd.gauss(0, 8)
                no = 12 + 0.25 * pm25 + rnd.gauss(0, 3)
                temp = temp_c * 9 / 5 + 32 if fahrenheit else temp_c
                date = f"2026-10-{day:02d}"
                if name == "Tambaram":
                    date = f"{day:02d}/10/2026"          # a different date format
                shown = {"T Nagar": " t nagar "}.get(name, name)  # untidy station name
                rows.append([shown, date, hour] + [f"{v:.1f}" for v in (pm25, pm10, no, temp)])
        for r in rows:                                   # inject faults
            for col in (3, 4, 5, 6):
                x = rnd.random()
                if x < 0.02:
                    r[col] = ""
                elif x < 0.035:
                    r[col] = "NA"
            x = rnd.random()
            if x < 0.01:
                r[3] = f"-{rnd.randint(1, 50)}"           # negative sensor fault
            elif x < 0.015:
                r[3] = str(rnd.choice([5000, 9999]))      # impossibly large
        for i in sorted(rnd.sample(range(len(rows)), 7), reverse=True):
            rows.insert(i + 1, list(rows[i]))              # duplicate rows
        with open(os.path.join(folder, f"{name.replace(' ', '_').lower()}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["station", "date", "hour", "pm25", "pm10", "no", "temp"])
            w.writerows(rows)


if __name__ == "__main__":
    generate()
    print("12 station files written to data/")
