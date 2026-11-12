"""Task A2 alternative concept: dropping missing readings against forward fill and median fill - effect on the daily mean and time."""
import random, statistics, time

rnd = random.Random(8)
# one station, 60 days x 24 hours; PM2.5 follows a daily pattern. The TRUE values are known, then readings are removed.
true = [[max(5, 50 + 35 * (1 if h in (8, 9, 20, 21) else 0) - (15 if 12 <= h <= 16 else 0) + rnd.gauss(0, 5)) for h in range(24)] for _ in range(60)]
print("Effect on the daily mean when 10% of readings are missing")
print(f"{'pattern of missing':34} {'drop':>8} {'forward fill':>13} {'median fill':>12}   (mean absolute error of the daily mean, ug/m3; lower is better)")
for pattern in ("random single hours", "rush hours 8-9 missing more often"):
    err = {"drop": [], "ffill": [], "median": []}
    for day in true:
        vals = list(day)
        if pattern.startswith("random"):
            miss = set(rnd.sample(range(24), 3))
        else:
            miss = {h for h in range(24) if rnd.random() < (0.5 if h in (8, 9) else 0.03)}
        obs = [None if h in miss else v for h, v in enumerate(vals)]
        valid = [v for v in obs if v is not None]
        if not valid:
            continue
        t_mean = statistics.mean(vals)
        med = statistics.median(valid)
        ff, last = [], None
        for v in obs:
            last = v if v is not None else last
            ff.append(last)
        ff = [v for v in ff if v is not None]
        err["drop"].append(abs(statistics.mean(valid) - t_mean))
        err["ffill"].append(abs(statistics.mean(ff) - t_mean))
        err["median"].append(abs(statistics.mean([v if v is not None else med for v in obs]) - t_mean))
    print(f"{pattern:34} {statistics.mean(err['drop']):>8.2f} {statistics.mean(err['ffill']):>13.2f} {statistics.mean(err['median']):>12.2f}")

print("\nTime for 1,000,000 values with 10% missing (seconds)")
vals = [None if rnd.random() < 0.1 else rnd.uniform(10, 200) for _ in range(1_000_000)]
t = time.perf_counter(); d = [v for v in vals if v is not None]; t_drop = time.perf_counter() - t
t = time.perf_counter()
out, last = [], None
for v in vals:
    last = v if v is not None else last
    out.append(last)
t_ff = time.perf_counter() - t
t = time.perf_counter(); m = statistics.median(d); out2 = [v if v is not None else m for v in vals]; t_med = time.perf_counter() - t
print(f"drop {t_drop:.3f} (O(n), result has {len(d):,} values) | forward fill {t_ff:.3f} (O(n), {len(out):,} values) | median fill {t_med:.3f} (O(n log n) sort, {len(out2):,} values)")
