"""Task A4 alternative concept: the time added by print() and by logging calls, and how each is switched off."""
import contextlib, io, logging, os, tempfile, time

N = 100_000
path = os.path.join(tempfile.gettempdir(), "a4.log")


def work(i):
    return i * 2.5


def plain():
    return sum(work(i) for i in range(N))


def with_print(out):
    total = 0
    with contextlib.redirect_stdout(out):
        for i in range(N):
            total += work(i)
            print("row", i, "value", total)
    return total


DEBUG = False


def with_print_flag():
    total = 0
    for i in range(N):
        total += work(i)
        if DEBUG:
            print("row", i, "value", total)
    return total


def with_logging(level):
    log = logging.getLogger(f"a4_{level}")
    log.handlers.clear()
    h = logging.FileHandler(path, mode="w")
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(h)
    log.setLevel(level)
    log.propagate = False
    total = 0
    for i in range(N):
        total += work(i)
        log.debug("row %d value %s", i, total)
    h.close()
    return total


def t(fn, *a):
    s = time.perf_counter()
    fn(*a)
    return time.perf_counter() - s


base = t(plain)
rows = [
    ("no debugging at all", base),
    ("print() to a file, every row", t(with_print, open(path, "w"))),
    ("print() guarded by if DEBUG (switched off)", t(with_print_flag)),
    ("logging.debug, level DEBUG, to a file", t(with_logging, logging.DEBUG)),
    ("logging.debug, level WARNING (switched off)", t(with_logging, logging.WARNING)),
]
print(f"{N:,} calls; time in seconds and extra time per call")
for name, sec in rows:
    print(f"{name:46} {sec:8.4f} s   extra per call {(sec - base) / N * 1e6:7.3f} us")
