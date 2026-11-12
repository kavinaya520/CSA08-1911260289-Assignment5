# Task B4 - Final Engineering Decision

Run: `python complete_code.py` (output_complete_code.txt), `python ai_tools.py` (output_ai_tools.txt), `python index_test.py` (output_index_test.txt). Input: complaints.csv (50 complaints written by me for this assignment, each with my own label).

## B4.1 Sentiment scorer and summariser on 50 complaints (25 negative, 16 positive, 9 neutral by my reading)
| Word list | Labels that agree with mine |
|---|---|
| The assignment's list (5 positive, 6 negative words) | 37 of 50 (74%); 8 negative complaints were called neutral because their words are not in the list |
| Extended list (19 positive, 25 negative words), chosen after reading the same 50, so optimistic | 45 of 50 (90%) |
The 5 disagreements with the extended list: `The river has never been clean.` (negator is not the previous word), `No action was taken on my earlier complaint.` (no sentiment word), `Oh great, another clean day of smoke and dust.` (sarcasm), `The new sprinklers work well and the dust is less.` (the list has "works", not "work"), `The helpline staff were helpful but the wait was long.` (mixed opinion; I labelled it neutral, the scorer says positive).
Summariser: 13 of the 50 complaints have more than one sentence; the frequent-words method picks a different sentence than "the first sentence" for 5 of them (for example "The helpline is slow and the staff were rude." instead of "Nobody answers my calls."). On all 50 complaints joined (k = 3) the frequent-words summary contains 8 of the 10 most frequent important words (air, clean, smoke, bad, fast, dust, station, factory, staff, road), the first-3-sentences summary only 4.

## B4.2 Index on (station, day) (index_test.py)
Table of 967,680 readings (120 stations x 336 days x 24 hours). Slowest query: `SELECT AVG, MIN, MAX ... WHERE station = ? AND day = ?`, 200 different queries.
| | Plan | Time for 200 queries | Per query |
|---|---|---|---|
| Without index | `SCAN aq` | 7.329 s | 36.64 ms |
| With `CREATE INDEX idx_station_day ON aq (station, day)` | `SEARCH ... USING INDEX` | 0.0041 s | 0.020 ms |
The query is about 1,800 times faster (a scan is O(n), the index search O(log n)). Cost: 0.42 s to build the index and the file grew from 32.4 MB to 55.8 MB, and each new insert has to update the index.

## B4.3 Production decision
Scale: 112 stations x 4 readings an hour x 24 x 365 = 3,924,480 readings a year (10,752 a day, 37 times today's 105,120), and 50,000 complaints a month = 0.019 a second on average.
- Store: keep SQLite (or a server database such as PostgreSQL if many people write at the same time), table `readings` with the primary key and the extra index on (station, day). A few million rows is small for it: a million-row GROUP BY took 0.45 s and an indexed single-day question 0.02 ms.
- Clean: clean each day's new files (about 10,752 rows) in a small batch job and add them with one `executemany`; pandas is the better tool if a full year is cleaned again (1,000,000 rows in 0.25 s against 1.47 s with loops).
- Analyse: SQL for the daily and monthly summaries; pandas and matplotlib for charts.
- AI: the word-list scorer is fast enough (0.0016 ms a complaint, 50,000 in 0.08 s), so speed is not a problem; accuracy is: 74% for the basic list and 90% for the extended list on my 50 complaints, which is optimistic because I tuned it on them, and it fails on sarcasm, negation not next to the word, and mixed opinions. My decision: use the extended word list now as a first filter and flag complaints that contain "but", sarcasm words or no sentiment word for a person to read; at the same time keep the human labels, and train a model (Naive Bayes or a pre-trained language model) when several thousand labelled complaints exist, because a Naive Bayes trained on only 50 gave 46%, worse than always guessing the majority (50%) (Task_A5). Then test the model on complaints it has not seen before it replaces the word list.

## Complete the Code (complete_code.py)
TODO 1: for each word the value is +1 (in POSITIVE), -1 (in NEGATIVE) or 0; if the previous word is in NEGATORS the sign is flipped; the values are added to `total`. Output equals the expected output (positive, negative, negative, positive). A complaint labelled wrongly: `The river has never been clean.` is labelled positive (score +1): the word before "clean" is "been", not "never", so the negation is not seen. `Oh great, another clean day of smoke and dust.` is labelled neutral (+1 and -1 cancel) because the sarcasm is not understood.

## Alternative concept: first k sentences instead of the most frequent words
Solution: `first_k(text, k)` returns `sentences(text)[:k]`. Quality (output_ai_tools.txt): it is wrong when the first sentence is only a greeting ("Excellent service.", "Thank you for the fast response.") and it covered 4 of the 10 key words of the 50 complaints against 8 of 10 for the frequent-words method; but it is simple and always keeps the author's first (often main) point. Time: O(1) after the sentences are split, against O(words) for counting words and scoring every sentence; measured for 50,000 complaints: 0.079 s (0.0016 ms each) against 0.143 s (0.0029 ms each). Space: first-k keeps k sentences; the frequent-words method also keeps a word-count dictionary, O(distinct words).
