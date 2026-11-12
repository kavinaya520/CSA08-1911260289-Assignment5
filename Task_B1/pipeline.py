"""Task B1.3: clean all 12 station files, load them into SQLite with executemany and answer the three board questions."""
import glob
import sqlite3
import time
from cleaning import clean_rows, read_csv

SCHEMA = """
CREATE TABLE stations (station_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, temp_unit_in_file TEXT);
CREATE TABLE readings (
    station_id INTEGER NOT NULL REFERENCES stations(station_id),
    day TEXT NOT NULL, hour INTEGER NOT NULL,
    pm25 REAL, pm10 REAL, no REAL, temp_c REAL, filled INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (station_id, day, hour));
"""


def build(db_path="airquality.db"):
    con = sqlite3.connect(db_path)
    con.executescript("DROP TABLE IF EXISTS readings; DROP TABLE IF EXISTS stations;" + SCHEMA)
    total_raw = total_clean = 0
    for path in sorted(glob.glob("data/*.csv")):
        raw = read_csv(path)
        rows, stats = clean_rows(raw)
        total_raw += len(raw)
        total_clean += len(rows)
        name = rows[0]["station"]
        unit = "F" if stats["Fahrenheit converted"] else "C"
        cur = con.execute("INSERT INTO stations (name, temp_unit_in_file) VALUES (?, ?)", (name, unit))
        sid = cur.lastrowid
        con.executemany(
            "INSERT INTO readings VALUES (?,?,?,?,?,?,?,?)",
            [(sid, r["date"], r["hour"], r["pm25"], r["pm10"], r["no"], r["temp"], r["filled"]) for r in rows])
        print(f"{name:13} raw rows {len(raw):4}  clean rows {len(rows):4}  "
              f"duplicates {stats['duplicate rows removed']}, impossible {stats['impossible values']}, "
              f"missing {stats['missing values']}, filled {stats['values forward-filled']}, unit {unit}")
    con.commit()
    print(f"\nTotal: {total_raw} raw rows -> {total_clean} clean rows loaded into {db_path}")
    return con


QUESTIONS = [
    ("Q1  Average PM2.5 of Adyar in October 2026",
     "SELECT ROUND(AVG(r.pm25), 2) FROM readings r JOIN stations s USING (station_id) "
     "WHERE s.name = ? AND r.day BETWEEN '2026-10-01' AND '2026-10-31'", ("Adyar",)),
    ("Q2  Stations ranked by average PM2.5 (worst three)",
     "SELECT s.name, ROUND(AVG(r.pm25), 1) AS avg_pm25 FROM readings r JOIN stations s USING (station_id) "
     "GROUP BY s.name ORDER BY avg_pm25 DESC LIMIT 3", ()),
    ("Q3  The three hours of the day with the worst air (network average)",
     "SELECT hour, ROUND(AVG(pm25), 1) AS avg_pm25 FROM readings GROUP BY hour ORDER BY avg_pm25 DESC LIMIT 3", ()),
]

if __name__ == "__main__":
    t = time.perf_counter()
    con = build()
    print(f"Cleaning and loading took {time.perf_counter() - t:.2f} s\n")
    for title, sql, params in QUESTIONS:
        print(title)
        print("   SQL:", sql)
        print("   ->", con.execute(sql, params).fetchall(), "\n")
    print("Share of stored readings that were forward-filled:",
          con.execute("SELECT ROUND(100.0 * SUM(filled) / COUNT(*), 2) FROM readings").fetchone()[0], "%")
    con.close()
