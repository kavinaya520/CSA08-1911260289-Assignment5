# Python Programming - Assignment 5 (CO5)

Data acquisition, cleaning, analysis and AI applications (city air-quality monitoring network).

- Name: Kavinaya A
- Register number: 1911260289
- Python version: 3.12.3
- Libraries: pandas 3.0.6, matplotlib 3.11.2 (see requirements.txt); everything else is the standard library (csv, sqlite3, statistics, re, logging, cProfile, tracemalloc)
- GitHub: https://github.com/kavinaya520/CSA08-1911260289-Assignment5.git

## How to run
Run each program from inside its folder (`cd Task_B1` and so on). Saved output: `output_<program>.txt` (and `.png` pictures of them); charts are in Task_B1. The data are synthetic and made by the programs (fixed random seed), so the counts are repeatable; timings depend on the computer.

| Task | Folder | Commands | Result note |
|---|---|---|---|
| A1 | Task_A1 | `python a1_csv_vs_sql.py` | CSV problems listed, 2-table SQLite design; CSV+pandas 0.035 s against 0.0001 s for an indexed SQL question |
| A2 | Task_A2 | `python a2_missing.py` | Cleaning rules, normalisation, formats; forward fill gave the smallest daily-mean error (0.81 vs 0.89 for dropping) |
| A3 | Task_A3 | (design only; timings in Task_B3) | 4 charts chosen, daily summary table by SQL GROUP BY |
| A4 | Task_A4 | `python a4_print_vs_logging.py` | Debug and profile plan; logging costs 9.1 us per call when on, 0.24 us when off |
| A5 | Task_A5 | `python a5_naive_bayes.py` | Sentiment, summariser, chatbot designs; Naive Bayes on 50 complaints 46% (word list 74% / 90%) |
| B1 | Task_B1 | `python gen_data.py`, `python cleaning.py`, `python pipeline.py`, `python visualise.py`, `python complete_code.py`, `python pandas_alt.py` | 9,012 raw rows -> 8,928 clean rows in SQLite; 4 charts; Complete the Code output matched; pandas 5.8 times faster at 1,000,000 rows |
| B2 | Task_B2 | `python adversarial.py`, `python complete_code.py` | 4 bad files caught; `+` SQL breaks (injection returns all rows), `?` is safe; scorer wrong on 5 of 9 difficult sentences |
| B3 | Task_B3 | `python compare.py` | Loops, pandas and SQL agree; at 1,051,200 rows 2.365 s, 0.483 s and 0.451 s; cProfile: `csv.DictReader.__next__` is the slowest function |
| B4 | Task_B4 | `python complete_code.py`, `python ai_tools.py`, `python index_test.py` | Agreement with my labels 37/50 (basic list) and 45/50 (extended list); index made the query 1,800 times faster |

Each task folder has a README.md with the design, the measurements and the alternative-concept analysis. Part A answers (designs, rules, pseudocode, reasoning) are in Task_A1 to Task_A5; Part B has the code and evidence.
