"""Task B4.1: lexicon sentiment scorer and extractive summariser on 50 complaints, compared with my own labels."""
import csv
import re
import time
from collections import Counter

POS_BASE = {"good", "clean", "fast", "helpful", "improved"}
NEG_BASE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
POS_EXT = POS_BASE | {"great", "excellent", "thanks", "thank", "fresh", "better", "quick", "happy", "polite", "smooth", "easy", "stopped", "works", "well"}
NEG_EXT = NEG_BASE | {"terrible", "awful", "unbearable", "polluted", "pollution", "dust", "coughing", "cough", "choking", "ignored",
                      "late", "poor", "wrong", "crashes", "dizzy", "smells", "burning", "unacceptable", "nothing"}
NEGATORS = {"not", "never", "no"}
STOP = set("the a an and or but is are was were be been to of in on at for with it this that my we our i you your from by as near "
           "have has had do does did not no will would can cannot when which where what please there their they them so very much".split())


def tokens(text):
    return text.lower().replace(".", " ").replace(",", " ").replace("!", " ").replace("?", " ").split()


def score(text, pos, neg):
    words = tokens(text)
    total = 0
    for i, w in enumerate(words):
        v = 1 if w in pos else -1 if w in neg else 0
        if v and i > 0 and words[i - 1] in NEGATORS:
            v = -v
        total += v
    return total


def label(text, pos, neg):
    s = score(text, pos, neg)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def important_words(text):
    return [w for w in tokens(text) if w not in STOP and len(w) > 2]


def summarise(text, k=1, freq=None):
    """Extractive: the k sentences whose important words are the most frequent (in `freq`, or in the text itself)."""
    sents = sentences(text)
    if len(sents) <= k:
        return sents
    freq = freq or Counter(important_words(text))
    scored = [(sum(freq[w] for w in important_words(s)), i) for i, s in enumerate(sents)]
    best = sorted(sorted(scored, reverse=True)[:k], key=lambda x: x[1])      # keep original order
    return [sents[i] for _, i in best]


def first_k(text, k=1):
    return sentences(text)[:k]


if __name__ == "__main__":
    rows = list(csv.DictReader(open("complaints.csv", encoding="utf-8")))
    texts = [r["complaint"] for r in rows]
    mine = [r["my_label"] for r in rows]

    print("=== B4.1 Sentiment: agreement with my own labels (50 complaints) ===")
    for name, pos, neg in (("base word list (assignment's 5 + 6 words)", POS_BASE, NEG_BASE),
                           ("extended word list (19 positive + 25 negative words)", POS_EXT, NEG_EXT)):
        pred = [label(t, pos, neg) for t in texts]
        agree = sum(p == m for p, m in zip(pred, mine))
        print(f"{name}: agree on {agree} of 50 ({agree * 2}%)")
        conf = Counter(zip(mine, pred))
        print("   (my label -> scorer label):", {f"{a}->{b}": n for (a, b), n in sorted(conf.items())})
        if pos is POS_EXT:
            print("   Disagreements with the extended list:")
            for r, p in zip(rows, pred):
                if p != r["my_label"]:
                    print(f"     #{r['id']:>2} mine={r['my_label']:8} scorer={p:8} | {r['complaint']}")

    print("\n=== B4.1 Summariser: sentences chosen from the multi-sentence complaints ===")
    multi = [t for t in texts if len(sentences(t)) > 1]
    print(f"{len(multi)} of 50 complaints have more than one sentence")
    differ = 0
    for t in multi:
        a, b = summarise(t), first_k(t)
        differ += a != b
        print(f"  frequent-words: {a[0]!r:70} first-sentence: {b[0]!r}" if a != b else f"  (same sentence chosen) {a[0]!r}")
    print(f"The two methods choose a different sentence for {differ} of {len(multi)} complaints")

    print("\n=== Corpus summary: all 50 complaints joined, k = 3 ===")
    text = " ".join(texts)
    freq = Counter(important_words(text))
    top = [w for w, _ in freq.most_common(10)]
    print("Top 10 important words:", top)
    s_freq, s_first = summarise(text, 3), first_k(text, 3)
    cover = lambda sel: sum(w in important_words(" ".join(sel)) for w in top)
    print("Most-frequent-words summary:")
    for s in s_freq:
        print("   -", s)
    print("First-3-sentences summary:")
    for s in s_first:
        print("   -", s)
    print(f"Top-10 words covered: frequent-words {cover(s_freq)}/10, first-k {cover(s_first)}/10")

    print("\n=== Speed: 50,000 complaints (the monthly volume), the 50 repeated 1,000 times ===")
    big = texts * 1000
    t = time.perf_counter()
    for x in big:
        label(x, POS_EXT, NEG_EXT)
    t1 = time.perf_counter() - t
    t = time.perf_counter()
    for x in big:
        summarise(x)
    t2 = time.perf_counter() - t
    t = time.perf_counter()
    for x in big:
        first_k(x)
    t3 = time.perf_counter() - t
    print(f"sentiment scorer {t1:.3f} s ({t1 / 50:.4f} ms each) | frequent-words summary {t2:.3f} s ({t2 / 50:.4f} ms each) | first-k {t3:.3f} s ({t3 / 50:.4f} ms each)")
