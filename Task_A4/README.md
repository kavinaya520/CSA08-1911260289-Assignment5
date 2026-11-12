# Task A4 - Plan Debugging and Profiling

Measurement script: `python a4_print_vs_logging.py` (output_a4_print_vs_logging.txt). The plan is applied to Task_B1/cleaning.py and Task_B3/compare.py.

## A4.1 Debugging plan for the cleaning code
| Tool | How it is used on the cleaning code |
|---|---|
| print | Quick look at a few suspicious rows, for example `print(repr(row))` just before the Fahrenheit conversion, to see the real text (` adyar `, `NA`, `''`). Removed afterwards. |
| assert | States what must be true: `assert 0 <= pm25 <= 999` after cleaning, `assert len(out) == len(seen)` (no duplicate left), `assert hi != lo` before min-max. A wrong result stops the program at the first broken rule instead of reaching the chart. |
| logging | `logging.debug` for every fixed value and `logging.warning` for every dropped row, written to a file with time and level. The level (DEBUG or WARNING) decides how much is written, without editing the code. |
| pdb / IDE debugger | `breakpoint()` (or a breakpoint in the IDE) inside `clean_rows` when the count of "values forward-filled" looks wrong; step with `n`, look at `row`, `last` with `p`, continue with `c`. Used for logic errors where it is not known in advance what to print. |

## A4.2 Profiling plan
1. `time.perf_counter()` around each stage (read, clean, load, query, chart) to find the slow stage; the difference of two readings is the time.
2. `timeit` for a small function that is called many times (for example `clean_name` or `to_number`), repeated several times so that one slow run does not mislead.
3. `cProfile` on the whole program, sorted by `tottime`, to find the function that takes the most time inside the slow stage. Example result (Task_B3): for the plain-Python daily mean, `csv.DictReader.__next__` has the largest own time (0.184 s of 0.652 s), and `statistics.mean` (`_sum`) uses 0.206 s in total, so reading the CSV and the exact `statistics` sum are the targets for improvement.
4. Change one thing, measure again, compare. `tracemalloc` is used for memory.

## Alternative concept: print statements only
Solution: put `print("row", i, value)` in the loop and delete or comment them out when the program works.

| 100,000 calls | Time (s) | Extra per call |
|---|---|---|
| no debugging | 0.0056 | - |
| print() to a file, every row | 0.0971 | 0.92 us |
| print() inside `if DEBUG:` with DEBUG = False | 0.0051 | about 0 |
| logging.debug at level DEBUG, to a file | 0.9156 | 9.10 us |
| logging.debug at level WARNING (switched off) | 0.0298 | 0.24 us |

Thousands of print or logging calls add real time: here logging to a file cost about 9 microseconds per call, so 1,000,000 messages add about 9 seconds (printing to a terminal is slower still). Both are O(n) in the number of messages. Switching off: prints must be edited out or guarded by a flag (easy to forget; the guard still costs one test per row); logging is switched off by raising the level (`logging.basicConfig(level=logging.WARNING)`), which needs no edit of the code and costs only 0.24 us per call. Logging also gives the time, the level and the file name, which print does not. A debugger needs no change in the code at all.
