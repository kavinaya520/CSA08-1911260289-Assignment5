# Task B2 - Engineer Adversarial Data

Run: `python adversarial.py` (output_adversarial.txt, creates adversarial_files/), `python complete_code.py` (output_complete_code.txt).

## Bad files (adversarial.py, part 1)
| File | First program (trusts the file) | Checked program | What it reveals about the design |
|---|---|---|---|
| missing_column.csv | `KeyError: 'pm25'` (crash with no explanation) | `ValueError: missing column(s): ['pm25']` | the header must be validated against the required columns before reading rows |
| wrong_delimiter.csv (`;`) | `KeyError: 'station'` (the whole line became one column) | `wrong delimiter ';'; expected a comma` | the csv module does not guess; the delimiter must be checked (Sniffer) |
| utf16_encoding.csv | `UnicodeDecodeError` | "file is not UTF-8 ... re-save it as UTF-8" | the encoding must be fixed or detected; a clear message is needed |
| empty.csv | returns `[]` with no error, so an empty day looks like a normal day | `ValueError: file is empty` | silent success is dangerous; an empty file must be reported |

## Quote character in a station name (part 2)
| Search | SQL built with `+` | `?` placeholder |
|---|---|---|
| `St Thomas' Mount` | `OperationalError: near "Mount": syntax error` (the quote ends the string) | works, returns the row |
| `Adyar' OR '1'='1` | returns ALL 3 rows (the condition became true for every row: SQL injection) | returns no rows |
With `?` the value is sent to SQLite separately from the SQL text, so the quote is only data and never part of the command. A station name with an apostrophe is searched correctly, and the injection text is just a station name that does not exist.

## Sentiment scorer against difficult sentences (part 3): 5 of 9 wrong
| Kind | Sentence | Result |
|---|---|---|
| sarcasm | Oh great, another clean day of smoke and dust. | neutral (expected negative): "clean" +1 and "smoke" -1 cancel; the sarcasm is not understood |
| sarcasm | Wow, the helpful staff took three hours to answer. | positive (expected negative) |
| double negative | I cannot say the air is not dirty. | positive (expected negative): only the word directly before "dirty" is checked; "cannot say" is ignored |
| negator not next to the word | The river has never been clean. | positive (expected negative): the previous word is "been", not "never" |
| word not in the list | The air is terrible and I cannot breathe. | neutral (expected negative): "terrible" is not in the list |
Correct: "not bad, not slow at all" (positive), and the three mixed-opinion sentences happened to come out as expected, but only because the counts balanced (or one side had more words), not because the scorer understands "but".
What this reveals: a word list sees words, not meaning: it needs a bigger list, a longer negation window, and for sarcasm a trained model or a human check.

## Complete the Code (complete_code.py)
TODO 1: `con.executemany("INSERT INTO aq (station, day, pm25) VALUES (?, ?, ?)", readings)` then `con.commit()`. TODO 2: `SELECT AVG(pm25) FROM aq WHERE station = ?` with `(name,)`. Output `54.0 108.0` and `None`, equal to the expected output.
Why `None`: the whole text `Adyar' OR '1'='1` is passed as one value, so the query asks for a station with exactly that name; no row has it, there are no rows to average, and `AVG` of nothing is NULL, which Python shows as None.

## Alternative concept
String joining with f"... '{name}'": for `Adyar' OR '1'='1` the query becomes `WHERE station = 'Adyar' OR '1'='1'`, which is true for every row, and it returned 81.0, the average of ALL rows (not 54.0). The quote in `St Thomas' Mount` gave a syntax error. In a real program this could leak or delete data.

| Rows | executemany (s) | execute() in a loop (s) | loop / executemany |
|---|---|---|---|
| 1,000 | 0.0006 | 0.0010 | 1.63 |
| 100,000 | 0.0554 | 0.1321 | 2.38 |
| 500,000 | 0.3149 | 0.5386 | 1.71 |
Both are O(n); `executemany` is about 2 times faster because the statement is prepared once and the loop is run in C. If the loop also commits after every row on a file database, 2,000 rows took 1.550 s against 0.002 s: the commit (a disk write) dominates, so commit once at the end.
