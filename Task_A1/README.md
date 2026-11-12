# Task A1 - Design the Data Acquisition

Measurement script: `python a1_csv_vs_sql.py` (output_a1_csv_vs_sql.txt). All designs below are implemented in Task_B1.

## A1.1 Structure of a station CSV file and expected problems
One file per station per day (or month), one line per hourly reading, header line first:
`station,date,hour,pm25,pm10,no,temp` (text, text, integer 0-23, and four decimal readings; temp in Celsius, but in Fahrenheit for two stations).

| # | Problem | Example (see Task_B1/sample_raw.csv) | Why it matters |
|---|---|---|---|
| 1 | Missing value (blank or NA) | `Adyar,2026-10-01,1,NA,82,16,27.1` and a blank pm25 | an average over NA fails or is wrong |
| 2 | Negative reading (sensor fault) | `-5` for pm25 | concentration cannot be below 0 |
| 3 | Impossibly large reading | `5000` for pm25 (a day above 999 ug/m3 is not realistic) | one value spoils the mean and the chart scale |
| 4 | Non-numeric text | `abc` in pm25 | float() raises ValueError |
| 5 | Duplicate row | the line `Adyar,2026-10-01,3,52,...` twice | the hour is counted twice |
| 6 | Temperature in Fahrenheit | Alandur `82.4` (really 28 C) | mixes units; a scatter plot against PM2.5 is wrong |
| 7 | Inconsistent station name | ` adyar ` and `Adyar` | one station becomes two groups |
| 8 | Inconsistent date format | `02/10/2026` and `2026-10-02` | wrong sorting, wrong GROUP BY |
| 9 | Missing column, wrong delimiter, wrong encoding, empty file | tested in Task_B2 | the whole file is unusable |

## A1.2 Storage design (SQLite)
```
stations(station_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, temp_unit_in_file TEXT)
readings(station_id INTEGER NOT NULL REFERENCES stations,
         day TEXT NOT NULL, hour INTEGER NOT NULL,
         pm25 REAL, pm10 REAL, no REAL, temp_c REAL, filled INTEGER NOT NULL DEFAULT 0,
         PRIMARY KEY (station_id, day, hour))
```
| CSV column | Goes to | Rule |
|---|---|---|
| station | stations.name -> readings.station_id | cleaned name; one row per station, id given by SQLite |
| date | readings.day | text `YYYY-MM-DD` (sorts correctly) |
| hour | readings.hour | integer 0-23 |
| pm25, pm10, no | readings.pm25, pm10, no | REAL, NULL when missing and not fillable |
| temp | readings.temp_c | REAL in Celsius (Fahrenheit converted) |
| (new) | readings.filled | 1 if any value of the row was forward-filled, so that fake values can be excluded |

The composite primary key (station_id, day, hour) forbids duplicate readings and also gives an index for "one station, one day" queries. The station name is stored once (no repetition in 100,000 rows).

## A1.3 CSV or SQL? Three questions of the board
| Question | By reading CSV files | By SQL |
|---|---|---|
| Q1 average PM2.5 of one station in October | read the station file, filter by date, average (or read all files and filter) | `SELECT AVG(pm25) ... WHERE s.name=? AND day BETWEEN ...` |
| Q2 which station is worst | read all 12 files, group in Python | `GROUP BY station ORDER BY AVG(pm25) DESC LIMIT 1` |
| Q3 which hours are worst | read everything, group by hour | `GROUP BY hour ORDER BY AVG(pm25) DESC LIMIT 3` |

CSV: no set-up, easy to open in Excel, but every question reads and parses all the text again and every program repeats the cleaning. SQL: the data is cleaned once and checked by the table definition (primary key); questions are short, and indexes make them fast; the cost is the one-time load. Answers from SQL are in Task_B1/output_pipeline.txt.

## Alternative concept: CSV loaded into a DataFrame for every question
Solution: `df = pd.read_csv(path)` at the start of each question, then a boolean filter or `groupby`. Measured on 96,768 readings (12 stations, 336 days, CSV 2.3 MB):

| Question | CSV + pandas, read every time (s) | SQL (s) |
|---|---|---|
| Q1 average of one station in a month | 0.0524 | 0.0002 |
| Q2 worst station | 0.0402 | 0.0103 |
| Q3 worst hour | 0.0276 | 0.0192 |
| one station, one day | 0.0346 | 0.000107 (with index, 324 times faster) |

Time: CSV + pandas is a full scan, O(n), for every question (parsing included). SQL does a full scan too for a `GROUP BY` over everything (Q2, Q3: O(n)), but a question on one station and one day uses the index and is O(log n). Space: the CSV needs 2.3 MB on disk but the DataFrame needed 12.3 MB of memory (about 5 times more) and it is rebuilt for each question; SQLite keeps the data on disk and loads only the pages it needs.
