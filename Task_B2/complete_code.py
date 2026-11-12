"""Task B2 - Complete the Code (TODO 1 and TODO 2 done) and the alternative-concept experiments."""
import sqlite3
import time

readings = [("Adyar", "2026-10-01", 48.0), ("Guindy", "2026-10-01", 95.0),
            ("Guindy", "2026-10-03", 121.0), ("Adyar", "2026-10-04", 60.0)]
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
# TODO 1: one executemany call with ? placeholders, then commit
con.executemany("INSERT INTO aq (station, day, pm25) VALUES (?, ?, ?)", readings)
con.commit()


def station_average(name):
    # TODO 2: parameterised SELECT (AVG of no rows is NULL, which Python returns as None)
    return con.execute("SELECT AVG(pm25) FROM aq WHERE station = ?", (name,)).fetchone()[0]


print(station_average("Adyar"), station_average("Guindy"))
print(station_average("Adyar' OR '1'='1"))   # an injection attempt finds nothing

# ---- Alternative concept 1: the SQL built by joining strings ----
def station_average_fstring(name):
    return con.execute(f"SELECT AVG(pm25) FROM aq WHERE station = '{name}'").fetchone()[0]

print("\nAlternative: SQL built with an f-string")
print("  Adyar                 ->", station_average_fstring("Adyar"))
print("  Adyar' OR '1'='1      ->", station_average_fstring("Adyar' OR '1'='1"),
      "(the condition became: station = 'Adyar' OR '1'='1', which is true for every row -> average of ALL rows)")
try:
    station_average_fstring("St Thomas' Mount")
except sqlite3.OperationalError as e:
    print("  St Thomas' Mount      -> OperationalError:", e)
con.close()

# ---- Alternative concept 2: executemany against execute in a loop ----
print("\nAlternative: executemany() against execute() in a loop (time for n rows, in-memory database)")
print(f"{'n rows':>10} {'executemany s':>14} {'execute loop s':>15} {'loop / many':>12}")
for n in (1_000, 100_000, 500_000):
    data = [(f"S{i % 12}", "2026-10-01", float(i % 200)) for i in range(n)]
    res = []
    for mode in ("many", "loop"):
        c = sqlite3.connect(":memory:")
        c.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
        t = time.perf_counter()
        if mode == "many":
            c.executemany("INSERT INTO aq VALUES (?,?,?)", data)
        else:
            for row in data:
                c.execute("INSERT INTO aq VALUES (?,?,?)", row)
        c.commit()
        res.append(time.perf_counter() - t)
        c.close()
    print(f"{n:>10,} {res[0]:>14.4f} {res[1]:>15.4f} {res[1] / res[0]:>11.2f}x")

# ---- same comparison when the database is a FILE and each execute is committed (what a careless loop does) ----
import os, tempfile
path = os.path.join(tempfile.gettempdir(), "b2_commit_test.db")
n = 2_000
data = [(f"S{i % 12}", "2026-10-01", float(i % 200)) for i in range(n)]
for mode in ("many", "loop + commit every row"):
    if os.path.exists(path):
        os.remove(path)
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
    t = time.perf_counter()
    if mode == "many":
        c.executemany("INSERT INTO aq VALUES (?,?,?)", data)
        c.commit()
    else:
        for row in data:
            c.execute("INSERT INTO aq VALUES (?,?,?)", row)
            c.commit()
    print(f"file database, {n:,} rows, {mode:24}: {time.perf_counter() - t:.3f} s")
    c.close()
os.remove(path)
