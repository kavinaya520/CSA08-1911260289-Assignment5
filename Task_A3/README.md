# Task A3 - Design the Analysis and Visualisation

The charts are drawn in Task_B1/visualise.py; the timing evidence for the alternative is in Task_B3.

## A3.1 Choice of charts
| Question of the board | Chart | Why this chart |
|---|---|---|
| Trend of PM2.5 over a month | Line chart (day on x, daily mean on y) | the x axis is ordered time; a line shows rise and fall and several lines (network, one station) can be compared |
| Comparison of stations | Bar chart, sorted, with the 60 ug/m3 limit as a line | categories with one value each; the bar length is easy to compare; sorting gives the ranking |
| Relationship between temperature and PM2.5 | Scatter plot (+ correlation r) | two numeric variables; each point is one reading and the cloud shows direction and strength |
| Hours with the worst air | Bar chart of the mean for each hour 0-23, worst three highlighted | 24 categories in a clock order; the peaks (rush hours) are clear. A box plot per hour would also show the spread, a histogram of PM2.5 would show the distribution but not the hour. |

Other uses: a histogram for the distribution of all PM2.5 values and a box plot per station to compare the spread and the outliers.

## A3.2 Daily summary table per station
Columns: `station, day, min_pm25, max_pm25, mean_pm25, valid_readings`. Produced by one SQL statement on the cleaned table:
```
SELECT s.name, r.day, MIN(r.pm25), MAX(r.pm25), AVG(r.pm25),
       COUNT(CASE WHEN r.filled = 0 AND r.pm25 IS NOT NULL THEN 1 END) AS valid_readings
FROM readings r JOIN stations s USING (station_id)
GROUP BY s.name, r.day
```
`valid_readings` counts only measured values (not forward-filled, not NULL), so a day with 10 valid readings is visibly less reliable than a day with 24. The same table can be made with pandas `groupby(["station","day"]).agg(...)`.

Pseudocode:
```
BEGIN summary
  FOR EACH (station, day) group in the readings table
    min = smallest pm25; max = largest pm25; mean = sum / count of pm25
    valid = number of rows with filled = 0 and pm25 not empty
    WRITE one row (station, day, min, max, mean, valid)
END
```

## Alternative concept: daily summary with Python loops
Solution: read all rows, keep a dictionary `groups[(station, day)] = [values]`, then compute min, max and `statistics.mean` for each group (this is `by_loops` in Task_B3/compare.py). Measured for the daily mean (Task_B3):

| Rows | Python loops (s) | SQL GROUP BY query (s) |
|---|---|---|
| 8,760 | 0.017 | 0.004 |
| 105,120 | 0.256 | 0.044 |
| 1,051,200 | 2.365 | 0.451 |

Time: both are O(n) (every row is visited once), but SQL runs in compiled code and is about 5 times faster here. Memory: the loop version keeps every reading in lists, O(n) (4.60 MB for 105,120 rows); a SQL GROUP BY keeps only one running aggregate per group, O(number of groups), and works through the file on disk.
