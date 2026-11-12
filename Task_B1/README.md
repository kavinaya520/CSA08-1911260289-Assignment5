# Task B1 - Implement and Validate the Cleaning Pipeline

Run (from this folder): `python gen_data.py` (12 raw files in data/, synthetic, fixed seed), `python cleaning.py` (output_cleaning.txt), `python pipeline.py` (output_pipeline.txt, creates airquality.db), `python visualise.py` (output_visualise.txt, 4 charts), `python complete_code.py` (output_complete_code.txt), `python pandas_alt.py` (output_pandas_alt.txt).

## B1.1 Validate the implementation (sample_raw.csv, 13 lines, every problem of A1.1)
Before (13 rows) and after (12 rows) are printed in output_cleaning.txt. Examples: `Adyar,2026-10-01,3,52,...` twice -> one row; ` adyar ` -> `Adyar`; `-5` and `5000` -> None -> filled with 52; `abc` -> filled; `02/10/2026` -> `2026-10-02`; Alandur `82.4` F -> `28.0` C; `NA` and blank -> forward-filled (flag filled = 1).
What was fixed: 5 missing values, 2 impossible values, 1 duplicate, 2 Fahrenheit conversions, 7 values forward-filled. Normalisation of the 12 cleaned PM2.5 values: min-max 0.0 ... 1.0, z-score -0.799 ... 2.533.

## B1.2 Comparison with the design (A2)
The code follows the rules of A2.1 and the formats of A2.3. Changes made while coding: (1) a non-numeric text such as `abc` is handled like a missing value (the design listed only blank and NA); (2) a row with an unreadable date or an hour outside 0-23 is dropped and counted (not in the design); (3) the `filled` flag is set when any of the four columns of the row was filled, so the 14.17% in the output means "rows with at least one filled value", not 14% of the values; (4) the Fahrenheit rule uses the known station names (as designed), not the size of the value.

## B1.3 Store and query (output_pipeline.txt)
12 files, 9,012 raw rows -> 8,928 clean rows (7 duplicates per file removed), loaded with one `executemany` per station. The answers:

| Question | SQL result |
|---|---|
| Q1 average PM2.5 of Adyar in October | 49.99 ug/m3 |
| Q2 worst three stations | Manali 100.0, Royapuram 81.4, Guindy 74.5 |
| Q3 worst three hours of the day | 8:00 (88.6), 9:00 (87.1), 21:00 (83.7) |

## B1.4 Charts and interpretation (data are synthetic, made by gen_data.py with a built-in rush-hour pattern)
- `chart1_trend.png`: the network daily mean stays between 61.8 and 63.5 ug/m3 (month mean 62.5), so there is no trend in October, only small day-to-day changes. Adyar stays below the network line, because it is cleaner than the average station.
- `chart2_stations.png`: Manali (100.0) is the most polluted and Besant Nagar (36.5) the cleanest; 7 of the 12 stations are above the 60 ug/m3 line. The industrial and traffic areas (Manali, Royapuram, Guindy) lead.
- `chart3_scatter.png`: 2,549 measured readings (4 stations, filled values left out); Pearson r = -0.20, a weak negative relationship: the air is a little worse when it is cooler (night and early morning). The cloud is wide, so temperature alone does not explain PM2.5.
- `chart4_hours.png`: two peaks, in the morning (8:00 and 9:00) and in the evening (21:00), and the cleanest air at 15:00 (43.6 ug/m3). The board should issue warnings for the morning and evening rush hours.

## Complete the Code (complete_code.py)
TODO 1 reads with `csv.DictReader`, skips empty, `NA` and negative values and converts to float; TODO 2 is `round((v - lo) / (hi - lo), 3)`. Output equals the expected output: `[('Adyar', '2026-10-01', 48.0), ('Guindy', '2026-10-01', 95.0), ('Guindy', '2026-10-03', 121.0)]` and `[0.0, 0.644, 1.0]`. Added check: values above 999 are skipped; the test row `Guindy,2026-10-04,5000` is skipped (the assert `clean2 == clean` passes).

## Alternative concept: pandas instead of the csv module and loops (pandas_alt.py)
Solution: `pd.read_csv(..., na_values=["NA", ""])`, a boolean filter `(pm25 >= 0) & (pm25 <= 999)`, `dropna`, and vectorised `(s - s.min()) / (s.max() - s.min())`. Same result as the loops (checked).

| Rows | Loops time (s) | Loops peak memory (MB) | pandas time (s) | pandas peak memory (MB) |
|---|---|---|---|---|
| 1,000 | 0.0010 | 0.1 | 0.0034 | 0.2 |
| 100,000 | 0.1319 | 11.3 | 0.0594 | 14.8 |
| 1,000,000 | 1.4706 | 112.0 | 0.2529 | 148.1 |

Both are O(n). For a small file the loops are faster (pandas has a start-up cost); from 100,000 rows pandas is 2 to 6 times faster because the work is done in compiled code. Pandas uses about 30% more memory here (it keeps the full table, O(n) columns), while the loop keeps only the valid values. Time is measured without tracemalloc and memory in a second run.
