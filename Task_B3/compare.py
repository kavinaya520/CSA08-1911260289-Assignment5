"""Task B3: daily mean PM2.5 per station - plain Python loops, pandas groupby and SQL GROUP BY."""
import cProfile, csv, io, os, pstats, random, sqlite3, statistics, tempfile, time
from collections import defaultdict
from datetime import date, timedelta
import pandas as pd

TMP = tempfile.gettempdir()


def generate(path, stations, seed=3):
    """One CSV with `stations` stations x 8,760 hourly readings (a year): station,day,hour,pm25"""
    rnd = random.Random(seed)
    start = date(2026, 1, 1)
    days = [(start + timedelta(d)).isoformat() for d in range(365)]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "day", "hour", "pm25"])
        for s in range(stations):
            base = rnd.uniform(40, 110)
            for day in days:
                for h in range(24):
                    w.writerow([f"S{s:03d}", day, h, round(max(1, rnd.gauss(base, 15)), 1)])


def by_loops(path):                       # stores all readings first, then statistics.mean
    groups = defaultdict(list)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            groups[(r["station"], r["day"])].append(float(r["pm25"]))
    return {k: statistics.mean(v) for k, v in groups.items()}


def by_running_sum(path):                 # alternative: one pass, running sum and count
    sums = defaultdict(lambda: [0.0, 0])
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            acc = sums[(r["station"], r["day"])]
            acc[0] += float(r["pm25"])
            acc[1] += 1
    return {k: s / n for k, (s, n) in sums.items()}


def by_pandas(path):
    df = pd.read_csv(path)
    g = df.groupby(["station", "day"])["pm25"].mean()
    return g.to_dict()


def load_sql(path, con):
    con.execute("DROP TABLE IF EXISTS aq")
    con.execute("CREATE TABLE aq (station TEXT, day TEXT, hour INTEGER, pm25 REAL)")
    with open(path, newline="") as f:
        rd = csv.reader(f)
        next(rd)
        con.executemany("INSERT INTO aq VALUES (?,?,?,?)", ((a, b, int(c), float(d)) for a, b, c, d in rd))
    con.commit()


def by_sql(con):
    return {(s, d): m for s, d, m in con.execute("SELECT station, day, AVG(pm25) FROM aq GROUP BY station, day")}


def timed(fn, *a):
    t = time.perf_counter()
    out = fn(*a)
    return out, time.perf_counter() - t


if __name__ == "__main__":
    # ---------- B3.1 correctness on small data ----------
    small = os.path.join(TMP, "b3_small.csv")
    generate(small, 2)
    con = sqlite3.connect(":memory:")
    load_sql(small, con)
    a, b, c, d = by_loops(small), by_pandas(small), by_sql(con), by_running_sum(small)
    same = lambda x, y: x.keys() == y.keys() and all(abs(x[k] - y[k]) < 1e-9 for k in x)
    print("B3.1 correctness: 2 stations x 365 days =", len(a), "daily means")
    print("  loops == pandas:", same(a, b), "| loops == SQL:", same(a, c), "| loops == running sum:", same(a, d))
    k = ("S000", "2026-01-01")
    print(f"  example {k}: loops {a[k]:.4f}  pandas {b[k]:.4f}  SQL {c[k]:.4f}  running sum {d[k]:.4f}")
    con.close()

    # ---------- B3.2 increasing the data size ----------
    print("\nB3.2 time in seconds (file read included for loops and pandas; SQL load and SQL query shown separately)")
    print(f"{'stations':>8} {'rows':>10} {'loops':>8} {'running sum':>12} {'pandas':>8} {'SQL load':>9} {'SQL query':>10}")
    results = {}
    for n in (1, 12, 120):
        path = os.path.join(TMP, f"b3_{n}.csv")
        generate(path, n)
        rows = n * 8760
        _, t_loop = timed(by_loops, path)
        _, t_run = timed(by_running_sum, path)
        _, t_pd = timed(by_pandas, path)
        con = sqlite3.connect(":memory:")
        _, t_load = timed(load_sql, path, con)
        _, t_sql = timed(by_sql, con)
        con.close()
        results[n] = (t_loop, t_run, t_pd, t_load, t_sql)
        print(f"{n:>8} {rows:>10,} {t_loop:>8.3f} {t_run:>12.3f} {t_pd:>8.3f} {t_load:>9.3f} {t_sql:>10.3f}")

    # ---------- B3.3 profile of the plain-Python version ----------
    print("\nB3.3 cProfile of by_loops on the 12-station file (sorted by time inside each function)")
    path = os.path.join(TMP, "b3_12.csv")
    pr = cProfile.Profile()
    pr.enable()
    by_loops(path)
    pr.disable()
    buf = io.StringIO()
    pstats.Stats(pr, stream=buf).sort_stats("tottime").print_stats(6)
    print("\n".join(l for l in buf.getvalue().splitlines() if l.strip())[:2500])

    # ---------- space: memory of the two plain-Python versions ----------
    import tracemalloc
    path = os.path.join(TMP, "b3_12.csv")
    print("\nPeak memory on the 12-station file (tracemalloc):")
    for name, fn in (("store all readings (by_loops)", by_loops), ("running sum (by_running_sum)", by_running_sum)):
        tracemalloc.start()
        fn(path)
        print(f"  {name:32} {tracemalloc.get_traced_memory()[1] / 1e6:6.2f} MB")
        tracemalloc.stop()
