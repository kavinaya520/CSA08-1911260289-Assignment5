"""Task B2: adversarial inputs - bad files, SQL quote characters and difficult sentences."""
import csv
import io
import os
import sqlite3

os.makedirs("adversarial_files", exist_ok=True)
REQUIRED = ["station", "date", "hour", "pm25"]

# ---------- 1. the four bad files ----------
files = {
    "missing_column.csv": "station,date,hour\nAdyar,2026-10-01,0\n".encode("utf-8"),
    "wrong_delimiter.csv": "station;date;hour;pm25\nAdyar;2026-10-01;0;48\n".encode("utf-8"),
    "utf16_encoding.csv": "station,date,hour,pm25\nAdyar,2026-10-01,0,48\n".encode("utf-16"),
    "empty.csv": b"",
}
for name, data in files.items():
    with open(os.path.join("adversarial_files", name), "wb") as f:
        f.write(data)


def naive_load(path):
    """Version 1 (what a first program does): trusts the file."""
    with open(path, newline="") as f:
        return [(r["station"], r["date"], int(r["hour"]), float(r["pm25"])) for r in csv.DictReader(f)]


def safe_load(path):
    """Version 2: checks the file and says exactly what is wrong."""
    raw = open(path, "rb").read()
    if not raw.strip():
        raise ValueError("file is empty")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("file is not UTF-8 (probably UTF-16 or Latin-1); re-save it as UTF-8")
    try:
        dialect = csv.Sniffer().sniff(text.splitlines()[0], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    if dialect.delimiter != ",":
        raise ValueError(f"wrong delimiter {dialect.delimiter!r}; expected a comma")
    reader = csv.DictReader(io.StringIO(text))
    missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"missing column(s): {missing}")
    return [(r["station"], r["date"], int(r["hour"]), float(r["pm25"])) for r in reader]


print("=== 1. Bad files: first program against the checked program ===")
for name in files:
    path = os.path.join("adversarial_files", name)
    for label, fn in (("naive", naive_load), ("checked", safe_load)):
        try:
            result = fn(path)
            print(f"{name:20} {label:8} -> returned {result}")
        except Exception as e:
            print(f"{name:20} {label:8} -> {type(e).__name__}: {e}")

# ---------- 2. quote character in a station name ----------
print("\n=== 2. Station name with a quote character ===")
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
con.executemany("INSERT INTO aq VALUES (?,?,?)", [
    ("Adyar", "2026-10-01", 48.0), ("Guindy", "2026-10-01", 95.0), ("St Thomas' Mount", "2026-10-01", 77.0)])


def search_plus(name):
    return con.execute("SELECT * FROM aq WHERE station = '" + name + "'").fetchall()


def search_placeholder(name):
    return con.execute("SELECT * FROM aq WHERE station = ?", (name,)).fetchall()


for name in ("St Thomas' Mount", "Adyar' OR '1'='1"):
    for label, fn in (("string with +", search_plus), ("? placeholder", search_placeholder)):
        try:
            print(f"{name!r:22} {label:14} -> {fn(name)}")
        except Exception as e:
            print(f"{name!r:22} {label:14} -> {type(e).__name__}: {e}")

# ---------- 3. difficult sentences for the sentiment scorer ----------
print("\n=== 3. Sentiment scorer against difficult sentences ===")
POSITIVE = {"good", "clean", "fast", "helpful", "improved"}
NEGATIVE = {"bad", "dirty", "slow", "rude", "smoke", "broken"}
NEGATORS = {"not", "never", "no"}


def score(text):
    words = text.lower().replace(".", " ").replace(",", " ").replace("!", " ").split()
    total = 0
    for i, w in enumerate(words):
        v = 1 if w in POSITIVE else -1 if w in NEGATIVE else 0
        if v and i > 0 and words[i - 1] in NEGATORS:
            v = -v
        total += v
    return total


def label(text):
    s = score(text)
    return "positive" if s > 0 else "negative" if s < 0 else "neutral"


tests = [
    ("sarcasm", "Oh great, another clean day of smoke and dust.", "negative"),
    ("sarcasm", "Wow, the helpful staff took three hours to answer.", "negative"),
    ("double negative", "The service is not bad, not slow at all.", "positive"),
    ("double negative", "I cannot say the air is not dirty.", "negative"),
    ("negator not next to word", "The river has never been clean.", "negative"),
    ("mixed opinion", "The bus was fast but the station is dirty and the staff are rude.", "negative"),
    ("mixed opinion", "Roads are clean but the factory smoke is bad.", "negative"),
    ("mixed opinion", "Good work on the roads, bad work on the drains.", "neutral"),
    ("word not in list", "The air is terrible and I cannot breathe.", "negative"),
]
wrong = 0
for kind, text, expected in tests:
    got = label(text)
    ok = got == expected
    wrong += not ok
    print(f"{'OK ' if ok else 'WRONG'} | {kind:24} | expected {expected:8} got {got:8} (score {score(text):+d}) | {text}")
print(f"\n{wrong} of {len(tests)} difficult sentences labelled wrongly")
