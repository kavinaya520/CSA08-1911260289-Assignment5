"""Task A5 alternative concept: a trained Naive Bayes classifier instead of a word list (pure Python, leave-one-out on the 50 complaints)."""
import csv, math, os, sys, time, tracemalloc
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join("..", "Task_B4"))
from ai_tools import label, POS_BASE, NEG_BASE, POS_EXT, NEG_EXT, tokens

rows = list(csv.DictReader(open(os.path.join("..", "Task_B4", "complaints.csv"), encoding="utf-8")))
texts, mine = [r["complaint"] for r in rows], [r["my_label"] for r in rows]


def train(data):
    prior, counts, vocab = Counter(), defaultdict(Counter), set()
    for text, lab in data:
        prior[lab] += 1
        for w in tokens(text):
            counts[lab][w] += 1
            vocab.add(w)
    return prior, counts, vocab


def predict(model, text):
    prior, counts, vocab = model
    n = sum(prior.values())
    best, best_lp = None, -1e18
    for lab in prior:
        total = sum(counts[lab].values())
        lp = math.log(prior[lab] / n) + sum(math.log((counts[lab][w] + 1) / (total + len(vocab))) for w in tokens(text))
        if lp > best_lp:
            best, best_lp = lab, lp
    return best


data = list(zip(texts, mine))
hits = 0
for i in range(len(data)):
    model = train(data[:i] + data[i + 1:])
    hits += predict(model, data[i][0]) == data[i][1]
print(f"Naive Bayes, leave-one-out on 50 complaints: {hits} of 50 correct ({hits * 2}%)")
base = sum(label(t, POS_BASE, NEG_BASE) == m for t, m in zip(texts, mine))
ext = sum(label(t, POS_EXT, NEG_EXT) == m for t, m in zip(texts, mine))
print(f"Word list, base: {base} of 50 | word list, extended (tuned on the same 50, so optimistic): {ext} of 50")
print("Majority-class guess (always 'negative'):", Counter(mine).most_common(1)[0][1], "of 50")

tracemalloc.start()
model = train(data)
print(f"\nTraining on 50 complaints: model memory {tracemalloc.get_traced_memory()[1] / 1e3:.1f} KB, vocabulary {len(model[2])} words")
tracemalloc.stop()
big = texts * 1000
t = time.perf_counter()
for x in big:
    predict(model, x)
t_nb = time.perf_counter() - t
t = time.perf_counter()
for x in big:
    label(x, POS_EXT, NEG_EXT)
t_lex = time.perf_counter() - t
print(f"50,000 complaints: Naive Bayes {t_nb:.3f} s ({t_nb / 50:.4f} ms each) | word list {t_lex:.3f} s ({t_lex / 50:.4f} ms each)")
tracemalloc.start()
lexicon = {w: 1 for w in POS_EXT} | {w: -1 for w in NEG_EXT}
print(f"Word list memory: {len(lexicon)} words, {tracemalloc.get_traced_memory()[1] / 1e3:.1f} KB")
tracemalloc.stop()
