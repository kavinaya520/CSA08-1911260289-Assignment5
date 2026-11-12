"""Task A1 alternative concept: answer the board's questions by loading CSV into pandas every time, or by SQL (indexed)."""
import csv, os, random, sqlite3, tempfile, time
import pandas as pd

path = os.path.join(tempfile.gettempdir(), "a1_all.csv")
rnd = random.Random(2)
days = [f"2026-{m:02d}-{d:02d}" for m in range(1, 13) for d in range(1, 29)]
with open(path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["station", "day", "hour", "pm25"])
    for s in range(12):
        base = rnd.uniform(40, 110)
        for day in days:
            for h in range(24):
                w.writerow([f"S{s:02d}", day, h, round(max(1, rnd.gauss(base, 15)), 1)])
rows = 12 * len(days) * 24
print(f"data: 12 stations x {len(days)} days x 24 hours = {rows:,} readings; CSV file {os.path.getsize(path) / 1e6:.1f} MB")

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT, day TEXT, hour INTEGER, pm25 REAL)")
df0 = pd.read_csv(path)
con.executemany("INSERT INTO aq VALUES (?,?,?,?)", df0.itertuples(index=False, name=None))
con.execute("CREATE INDEX idx ON aq (station, day)")
print(f"pandas DataFrame in memory: {df0.memory_usage(deep=True).sum() / 1e6:.1f} MB")

Q = {
    "Q1 average PM2.5 of S03 in month 10": (
        lambda d: d[(d.station == "S03") & d.day.str.startswith("2026-10")].pm25.mean(),
        "SELECT AVG(pm25) FROM aq WHERE station='S03' AND day BETWEEN '2026-10-01' AND '2026-10-31'"),
    "Q2 worst station (highest mean)": (
        lambda d: d.groupby("station").pm25.mean().idxmax(),
        "SELECT station FROM aq GROUP BY station ORDER BY AVG(pm25) DESC LIMIT 1"),
    "Q3 worst hour of the day": (
        lambda d: d.groupby("hour").pm25.mean().idxmax(),
        "SELECT hour FROM aq GROUP BY hour ORDER BY AVG(pm25) DESC LIMIT 1"),
}
print(f"\n{'question':40} {'CSV + pandas (read every time) s':>34} {'SQL query s':>12}")
for name, (fn, sql) in Q.items():
    t = time.perf_counter(); a = fn(pd.read_csv(path)); t_csv = time.perf_counter() - t
    t = time.perf_counter(); b = con.execute(sql).fetchone()[0]; t_sql = time.perf_counter() - t
    print(f"{name:40} {t_csv:>34.4f} {t_sql:>12.4f}")
print("\nQ1 again, a short question that can use the index (one station, one day):")
t = time.perf_counter(); pd.read_csv(path).query("station == 'S03' and day == '2026-10-05'").pm25.mean(); t_csv = time.perf_counter() - t
t = time.perf_counter(); con.execute("SELECT AVG(pm25) FROM aq WHERE station='S03' AND day='2026-10-05'").fetchone(); t_sql = time.perf_counter() - t
print(f"CSV + pandas {t_csv:.4f} s | SQL with index {t_sql:.6f} s | ratio {t_csv / t_sql:.0f} times")
