"""Task B4.2: effect of an index on (station, day) on the slowest query; B4.3 scale arithmetic."""
import os, random, sqlite3, tempfile, time

path = os.path.join(tempfile.gettempdir(), "b4_index.db")
if os.path.exists(path):
    os.remove(path)
con = sqlite3.connect(path)
con.execute("CREATE TABLE aq (station TEXT, day TEXT, hour INTEGER, pm25 REAL)")
rnd = random.Random(4)
days = [f"2026-{m:02d}-{d:02d}" for m, d in ((m, d) for m in range(1, 13) for d in range(1, 29))][:336]
rows = ((f"S{s:03d}", day, h, round(rnd.uniform(10, 200), 1)) for s in range(120) for day in days for h in range(24))
con.executemany("INSERT INTO aq VALUES (?,?,?,?)", rows)
con.commit()
n = con.execute("SELECT COUNT(*) FROM aq").fetchone()[0]
print(f"table aq: {n:,} rows (120 stations x 336 days x 24 hours), file {os.path.getsize(path) / 1e6:.1f} MB")

QUERY = "SELECT AVG(pm25), MIN(pm25), MAX(pm25) FROM aq WHERE station = ? AND day = ?"
queries = [(f"S{rnd.randrange(120):03d}", rnd.choice(days)) for _ in range(200)]


def run():
    t = time.perf_counter()
    for q in queries:
        con.execute(QUERY, q).fetchone()
    return time.perf_counter() - t


print("\nQuery:", QUERY)
print("Plan without index:", con.execute("EXPLAIN QUERY PLAN " + QUERY, queries[0]).fetchall()[0][-1])
before = run()
t = time.perf_counter()
con.execute("CREATE INDEX idx_station_day ON aq (station, day)")
con.commit()
build = time.perf_counter() - t
print("Plan with index   :", con.execute("EXPLAIN QUERY PLAN " + QUERY, queries[0]).fetchall()[0][-1])
after = run()
print(f"\n200 queries without index: {before:.3f} s ({before / 200 * 1000:.2f} ms each)")
print(f"200 queries with index   : {after:.4f} s ({after / 200 * 1000:.3f} ms each)")
print(f"speed-up: {before / after:.0f} times; building the index took {build:.2f} s; file now {os.path.getsize(path) / 1e6:.1f} MB")
con.close()
os.remove(path)

print("\nB4.3 scale arithmetic")
old, new = 12, 12 + 100
per_year = new * 4 * 24 * 365
print(f"{new} stations x 4 readings/hour x 24 x 365 = {per_year:,} readings per year ({per_year // 12:,} per month, {new * 96:,} per day)")
print(f"Current network: 12 x 24 x 365 = {12 * 24 * 365:,} readings per year; growth {per_year / (12 * 24 * 365):.0f} times")
print(f"Complaints: 50,000 per month = {50000 / 30:,.0f} per day = {50000 / 30 / 86400:.3f} per second on average")
