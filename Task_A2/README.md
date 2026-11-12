# Task A2 - Design the Cleaning and Normalisation

Measurement script: `python a2_missing.py` (output_a2_missing.txt). The rules are implemented in Task_B1/cleaning.py.

## A2.1 Cleaning rules
| Problem | Rule | Justification |
|---|---|---|
| Missing value (blank, NA, non-number) | Forward fill: use the previous valid value of the same station and column; set `filled = 1`. A gap at the very start stays NULL. | Air pollution changes slowly from one hour to the next, so the previous hour is a better guess than a global median. The flag lets the summary count only measured readings. The measured error of the daily mean was 0.81 against 0.89 for dropping and 0.86 for the median (random gaps). |
| Impossible value (below 0 or above 999; temperature outside -10 to 60 C) | Treat it as missing (set to None) and then apply the missing-value rule. | A sensor fault is not information; keeping it would ruin the mean and the chart. |
| Duplicate rows | Keep the first row for each (station, date, hour) and count the removed ones. | An hour must be counted once; the same key is also the primary key in SQLite. |
| Fahrenheit temperature | For Alandur and Velachery: C = (F - 32) x 5/9, rounded to 1 decimal. | One unit in the database; the two stations are known from the case study, so no guessing from the value. |
| Station name and date format | Name: strip spaces, collapse spaces, Title Case. Date: accept `YYYY-MM-DD` and `DD/MM/YYYY`, store `YYYY-MM-DD`; a row with an unreadable date or an hour outside 0-23 is dropped and counted. | The same station must have one name; text dates must sort correctly. |

## A2.2 Normalisation of PM2.5
- Min-max: `x' = (x - min) / (max - min)`, result 0 to 1. Appropriate when a bounded range is needed (charts with different units side by side, distance-based methods). Weakness: one extreme value squeezes all others.
- Z-score: `z = (x - mean) / standard deviation`, mean 0 and spread 1. Appropriate when values are compared with the typical level ("2.5 standard deviations above normal") or when outliers must stand out; it has no fixed range.
Example (Task_B1/output_cleaning.txt): PM2.5 of 52 gives 0.055 by min-max and -0.616 by z-score; 121 gives 1.0 and 2.533. If the standard deviation or the range is 0 the result is 0.0 (no division by zero).

## A2.3 Standard formats
| Item | Format |
|---|---|
| Date | `YYYY-MM-DD` (text, ISO 8601) |
| Hour | integer 0 to 23 |
| Station name | Title Case, single spaces, no leading or trailing spaces (`T Nagar`) |
| Numbers | decimal point, float, one decimal; temperature in Celsius; units ug/m3 for PM and NO |
| Missing | NULL in the database (never 0, never the text NA) |

## Pseudocode
```
BEGIN clean_rows(rows)
  seen = empty set; out = empty list
  FOR EACH row IN rows
    station = TitleCase(strip(row.station))
    date = parse(row.date) using YYYY-MM-DD or DD/MM/YYYY
    hour = integer(row.hour)
    IF date is invalid OR hour is not in 0..23 THEN count it; skip the row
    IF (station, date, hour) is in seen THEN count a duplicate; skip the row
    add (station, date, hour) to seen
    FOR EACH column IN pm25, pm10, no, temp
      value = number(row.column), or empty if blank / NA / text
      IF value exists AND column is temp AND station reports Fahrenheit THEN value = (value - 32) * 5 / 9
      IF value exists AND value is outside the limits of column THEN value = empty
    add the row to out
  SORT out by station, date, hour
  FOR EACH row IN out, IN ORDER
    FOR EACH column
      IF value is empty AND a previous value of this station and column exists THEN
        value = previous value; row.filled = 1
      ELSE IF value is not empty THEN previous value = value
  RETURN out
END
```

## Alternative concept: drop the missing readings
Solution: `valid = [v for v in values if v is not None]` and average only `valid`.

| Case (60 days x 24 h, 10% missing, mean absolute error of the daily mean, ug/m3) | Drop | Forward fill | Median fill |
|---|---|---|---|
| Missing hours chosen at random | 0.89 | 0.81 | 0.86 |
| Rush hours 8-9 missing more often | 1.32 | 1.16 | 1.42 |

Dropping is unbiased when the gaps are random, but when the gaps are concentrated in the worst hours the daily average is too low (a bias). Time for 1,000,000 values with 10% missing: drop 0.020 s, forward fill 0.069 s (both O(n)), median fill 0.217 s (sorting, O(n log n)). Space: dropping makes a shorter list (900,152 values) and keeps no extra values; forward fill and median fill keep all 1,000,000 values (O(n)) and the median also needs a sorted copy.
