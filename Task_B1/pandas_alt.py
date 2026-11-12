"""Task B1 alternative concept: cleaning with the csv module and loops against pandas, for 1,000 / 100,000 / 1,000,000 rows."""
import csv, io, random, time, tracemalloc
import pandas as pd


def make_csv(n, seed=1):
    rnd = random.Random(seed)
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["station", "date", "pm25"])
    for i in range(n):
        x = rnd.random()
        v = "NA" if x < 0.03 else "" if x < 0.05 else str(-rnd.randint(1, 50)) if x < 0.06 else "5000" if x < 0.065 else f"{rnd.uniform(10, 200):.1f}"
        w.writerow([f"S{i % 12}", f"2026-10-{i % 28 + 1:02d}", v])
    return out.getvalue()


def loops(text):
    vals = []
    for r in csv.DictReader(io.StringIO(text)):
        raw = r["pm25"].strip()
        if raw == "" or raw.upper() == "NA":
            continue
        v = float(raw)
        if 0 <= v <= 999:
            vals.append(v)
    lo, hi = min(vals), max(vals)
    return [(v - lo) / (hi - lo) for v in vals]


def with_pandas(text):
    df = pd.read_csv(io.StringIO(text), na_values=["NA", ""])
    df = df[(df["pm25"] >= 0) & (df["pm25"] <= 999)].dropna(subset=["pm25"])
    return ((df["pm25"] - df["pm25"].min()) / (df["pm25"].max() - df["pm25"].min())).tolist()


if __name__ == "__main__":
    print(f"{'rows':>10} | {'loops time s':>12} {'loops peak MB':>14} | {'pandas time s':>13} {'pandas peak MB':>15} | same result")
    for n in (1_000, 100_000, 1_000_000):
        text = make_csv(n)
        res = {}
        for name, fn in (("loops", loops), ("pandas", with_pandas)):
            t = time.perf_counter()               # time measured without tracemalloc (it slows the program)
            out = fn(text)
            dt = time.perf_counter() - t
            tracemalloc.start()                   # memory measured in a second run
            fn(text)
            peak = tracemalloc.get_traced_memory()[1] / 1e6
            tracemalloc.stop()
            res[name] = (dt, peak, out)
        same = len(res["loops"][2]) == len(res["pandas"][2]) and all(abs(a - b) < 1e-9 for a, b in zip(res["loops"][2], res["pandas"][2]))
        print(f"{n:>10,} | {res['loops'][0]:>12.4f} {res['loops'][1]:>14.1f} | {res['pandas'][0]:>13.4f} {res['pandas'][1]:>15.1f} | {same}")
