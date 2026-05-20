"""More diverse code-review snippets via realistic, structurally distinct templates."""
import json, pathlib, random

random.seed(20260615)
OUT = pathlib.Path(__file__).parent / 'raw' / 'bulk_v3.json'
items: list[dict] = []

def add(lang, code, q, opts, ci, t, st, d, e, s=None):
    items.append({'lang':lang,'code':code,'question':q,'options':opts,'correct_idx':ci,
                  'topic':t,'subtopic':st,'difficulty':d,'explain':e,'sources':s or [],'iter':12})

# Python - varied patterns
PY = [
    ("def shuffle_in_place(arr):\n    import random\n    random.shuffle(arr)",
     "Why random.shuffle in-place?", "perf", "in-place-mutation", "easy",
     "random.shuffle modifies the list in place and returns None. This is more memory-efficient than producing a shuffled copy. The convention 'return None' on mutating functions is consistent across the stdlib."),
    ("def safe_int(x, default=0):\n    try:\n        return int(x)\n    except (ValueError, TypeError):\n        return default",
     "Why catch both ValueError and TypeError?", "style", "exception-tuple", "med",
     "int() raises ValueError on bad strings and TypeError on non-string/non-numeric inputs. A tuple of exception types captures both in one clause. Documenting the specific exceptions caught makes intent clear."),
    ("from typing import TypeVar, Generic\n\nT = TypeVar('T')\n\nclass Stack(Generic[T]):\n    def __init__(self):\n        self._items: list[T] = []\n    def push(self, x: T) -> None:\n        self._items.append(x)",
     "Why Generic[T]?", "style", "typing-generic", "med",
     "TypeVar + Generic let type checkers track the element type through Stack methods. Stack[int]() vs Stack[str]() are distinct in mypy's view. This is the PEP 484 generic-class idiom for typed containers."),
    ("import secrets\n\ndef token(n=32):\n    return secrets.token_urlsafe(n)",
     "Why secrets.token_urlsafe?", "security", "secrets-urlsafe", "easy",
     "secrets.token_urlsafe is the high-level CSPRNG-backed function for URL/cookie-safe tokens. It returns base64url without padding. Use this for any user-facing identifier that must be unguessable."),
    ("import logging\n\nlog = logging.getLogger(__name__)\n\ndef handle(x):\n    log.info('handling %s', x)",
     "Why %s formatting in logger?", "perf", "logging-deferred-format", "med",
     "Passing %s placeholders defers string formatting until the handler actually needs the message. If the log level filters this record out, no formatting cost is paid. f-strings would evaluate eagerly."),
    ("from typing import Iterator\n\ndef batch(items: list, n: int) -> Iterator[list]:\n    for i in range(0, len(items), n):\n        yield items[i:i+n]",
     "Why yield slices?", "perf", "yield-batches", "easy",
     "Generator yields each batch lazily, so consumers can process and discard without holding all batches in memory. items[i:i+n] is a shallow slice, sharing the underlying list backing."),
    ("def median(nums):\n    s = sorted(nums)\n    n = len(s)\n    if n == 0:\n        return None\n    mid = n // 2\n    return s[mid] if n % 2 else (s[mid-1] + s[mid]) / 2",
     "Why average two middle values for even length?", "edge", "median-even", "med",
     "Statistical median for even-count samples is the mean of the two central order statistics. Returning a single middle element biases the result. Edge case: empty input must be handled explicitly (None or raise)."),
    ("def is_palindrome(s):\n    s = s.lower()\n    return s == s[::-1]",
     "What edge case is mishandled?", "edge", "case-fold-vs-lower", "med",
     "str.lower handles ASCII but not all Unicode (e.g., German ß becomes ss with casefold but not lower). For Unicode-aware comparison use s.casefold() == s[::-1].casefold() and also strip non-alphanumerics if needed."),
    ("import asyncio\n\nasync def with_timeout(coro, sec):\n    return await asyncio.wait_for(coro, timeout=sec)",
     "What does asyncio.wait_for raise on timeout?", "concurrency", "asyncio-wait-for", "easy",
     "asyncio.wait_for cancels the inner coroutine and raises asyncio.TimeoutError if the deadline expires. The cancelled coroutine should propagate CancelledError so structured cleanup runs."),
    ("from dataclasses import dataclass, field\n\n@dataclass(slots=True)\nclass Point:\n    x: float\n    y: float",
     "What does slots=True do (3.10+)?", "perf", "dataclass-slots", "med",
     "@dataclass(slots=True) generates __slots__ along with the data fields. Instances skip __dict__, saving memory (~40-50%) and slightly speeding attribute access. Trade-off: dynamic attributes are forbidden."),
    ("def find_max_index(nums):\n    if not nums:\n        return -1\n    return max(range(len(nums)), key=nums.__getitem__)",
     "Why pass nums.__getitem__ as key?", "perf", "max-with-key", "hard",
     "max with key=fn applies fn to each element and selects by the result. nums.__getitem__ is the bound-method form of nums[i], providing the value at index i. Cleaner than max(enumerate(nums), key=lambda p: p[1])[0]."),
    ("def cumsum(xs):\n    total = 0\n    for x in xs:\n        total += x\n        yield total",
     "What does this generator produce?", "style", "cumulative-yield", "easy",
     "Each iteration yields the running total. itertools.accumulate is the stdlib equivalent. Use this pattern for cumulative aggregates over large or infinite streams without materializing intermediates."),
    ("def deep_get(d, *keys, default=None):\n    for k in keys:\n        if not isinstance(d, dict) or k not in d:\n            return default\n        d = d[k]\n    return d",
     "Why isinstance check inside the loop?", "edge", "deep-get-safety", "med",
     "Without the type guard, encountering a non-dict mid-path (e.g., a list or None) would raise TypeError or AttributeError. The check returns the default on type mismatches, making deep_get total over malformed inputs."),
    ("import functools\n\n@functools.singledispatch\ndef render(x):\n    return str(x)\n\n@render.register\ndef _(x: list):\n    return '[' + ','.join(render(i) for i in x) + ']'",
     "What does @functools.singledispatch do?", "style", "singledispatch", "hard",
     "singledispatch dispatches to a different implementation based on the first argument's type. It is type-based polymorphism for functions, the Python analogue of overloading or multimethods, allowing extension without modifying the original function."),
]
for code, q, t, st, d, e in PY:
    opts = ["Cosmetic", e.split('.')[0].strip(), "Performance only", "Required syntax"]
    add('python', code, q, opts, 1, t, st, d, e)

# JavaScript - varied
JS = [
    ("function debounce(fn, ms) {\n  let t;\n  return function(...args) {\n    clearTimeout(t);\n    t = setTimeout(() => fn.apply(this, args), ms);\n  };\n}",
     "How does debounce help?", "perf", "debounce", "med",
     "Debounce collapses bursts of calls into one trailing invocation after ms quiet. Useful for resize, scroll, and keystroke handlers. Throttle is the complementary pattern that caps frequency rather than collapsing."),
    ("function once(fn) {\n  let called = false, val;\n  return function(...a) {\n    if (called) return val;\n    called = true;\n    return val = fn.apply(this, a);\n  };\n}",
     "What does once() guarantee?", "style", "once-wrapper", "easy",
     "once returns a wrapped function that runs at most one time and caches the first return value. Subsequent calls return the cached value without re-invoking. Useful for initialization that must not repeat."),
    ("const get = (obj, path) => path.split('.').reduce((a, k) => a?.[k], obj);",
     "Why use ?. inside reduce?", "edge", "safe-path-traversal", "med",
     "Optional chaining at each step short-circuits on null/undefined, returning undefined for missing paths. Without it, accessing a property on undefined would throw TypeError. The pattern lets get('a.b.c.d') safely traverse any depth."),
    ("async function* paginate(fetcher) {\n  let cursor = null;\n  do {\n    const page = await fetcher(cursor);\n    yield* page.items;\n    cursor = page.nextCursor;\n  } while (cursor);\n}",
     "What does an async generator enable?", "concurrency", "async-paginate", "hard",
     "Async generators expose paginated APIs as for-await-of streams. The consumer treats it as a flat iterator while the producer manages cursor state. This is the canonical pattern for streaming paginated REST/GraphQL APIs."),
    ("const memoize = (fn) => {\n  const cache = new Map();\n  return (k) => cache.has(k) ? cache.get(k) : cache.set(k, fn(k)).get(k);\n};",
     "Why Map for memoize cache?", "perf", "memoize-map", "med",
     "Map supports any key type and has efficient .has, .get, .set in O(1) average. The chained .set().get() returns the value while updating the cache in one expression. Plain objects coerce keys to strings and inherit prototype properties."),
    ("Array.prototype.last = function() { return this[this.length - 1]; };",
     "What is wrong with extending Array.prototype?", "style", "no-prototype-extension", "easy",
     "Modifying built-in prototypes pollutes the global namespace and can collide with future ECMAScript additions or third-party libraries. Use a utility function or a class wrapper instead. This is the 'don't extend built-ins' rule."),
    ("function createLogger(prefix) {\n  return Object.freeze({\n    info: (msg) => console.log(prefix, msg),\n    warn: (msg) => console.warn(prefix, msg),\n  });\n}",
     "Why Object.freeze on the returned API?", "security", "freeze-api", "med",
     "Object.freeze prevents accidental or malicious mutation of the returned API. Callers cannot replace logger.info with their own function. This is defensive immutability for module exports."),
    ("const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);",
     "What does pipe compose?", "style", "function-composition", "med",
     "pipe takes N functions and returns a single function that applies them left to right. pipe(f, g, h)(x) is h(g(f(x))). The dual compose applies right to left. These are functional-programming primitives common in Ramda and lodash/fp."),
    ("const groupBy = (arr, fn) => arr.reduce((acc, x) => {\n  const k = fn(x);\n  (acc[k] = acc[k] || []).push(x);\n  return acc;\n}, {});",
     "What does groupBy return?", "style", "group-by-reduce", "easy",
     "groupBy returns an object mapping keys to arrays of matching elements. The key function fn computes the bucket label. Common shape for analytical reduction. lodash.groupBy is the canonical reference."),
    ("function isPlainObject(v) {\n  return v !== null && typeof v === 'object' && Object.getPrototypeOf(v) === Object.prototype;\n}",
     "Why check Object.getPrototypeOf?", "edge", "plain-object-check", "hard",
     "typeof null === 'object' is the classic gotcha; explicit null check rules it out. Checking prototype identifies plain {} objects distinct from class instances, arrays, Date, Map, etc. instanceof Object would accept those."),
    ("const sleep = (ms) => new Promise(r => setTimeout(r, ms));\n\nasync function retry(fn, attempts = 3) {\n  for (let i = 0; i < attempts; i++) {\n    try { return await fn(); } catch (e) {\n      if (i === attempts - 1) throw e;\n      await sleep(2 ** i * 100);\n    }\n  }\n}",
     "What backoff strategy does this use?", "style", "exponential-backoff", "med",
     "Exponential backoff with base 100ms doubles between retries: 100, 200, 400ms. Adding jitter (random ms) prevents thundering herd. This is the standard cloud-client retry pattern (AWS, Google docs)."),
    ("function* range(start, end, step = 1) {\n  for (let i = start; i < end; i += step) yield i;\n}",
     "Why generator over array?", "perf", "lazy-range", "easy",
     "A generator yields values on demand without materializing the full range. range(0, 1e9) does not allocate a billion-element array; consumers can break early. This is the lazy-iteration idiom."),
    ("class Observable {\n  constructor() { this.subs = new Set(); }\n  subscribe(fn) { this.subs.add(fn); return () => this.subs.delete(fn); }\n  emit(v) { for (const s of this.subs) s(v); }\n}",
     "Why does subscribe return an unsubscribe function?", "style", "subscribe-returns-unsub", "med",
     "Returning the cleanup function as the subscription handle is the rxjs and React useEffect convention. The caller stores it and invokes to detach the listener. This pattern composes cleanly through forwarding."),
]
for code, q, t, st, d, e in JS:
    opts = ["Cosmetic", e.split('.')[0].strip(), "Performance only", "Required syntax"]
    add('javascript', code, q, opts, 1, t, st, d, e)

# Go - varied
GO = [
    ("package main\n\nimport \"fmt\"\n\nfunc main() {\n\tdefer fmt.Println(\"world\")\n\tfmt.Println(\"hello\")\n}",
     "What is printed first?", "edge", "defer-order", "easy",
     "Deferred calls run in LIFO order at function return, so 'hello' prints first then 'world' on return. Use defer for cleanup that should happen after the main work, e.g., closing files or releasing locks."),
    ("package main\n\nimport (\n\t\"fmt\"\n\t\"strings\"\n)\n\nfunc main() {\n\ts := strings.Builder{}\n\tfor i := 0; i < 100; i++ {\n\t\tfmt.Fprintf(&s, \"%d,\", i)\n\t}\n}",
     "Why fmt.Fprintf with &s?", "perf", "fprintf-builder", "med",
     "fmt.Fprintf writes formatted output directly to any io.Writer. strings.Builder implements io.Writer, so we avoid an intermediate string allocation per iteration. Faster than s += fmt.Sprintf which builds a new string each time."),
    ("package main\n\nimport \"fmt\"\n\nfunc main() {\n\tm := map[string]int{\"a\": 1, \"b\": 2}\n\tfor k, v := range m {\n\t\tfmt.Println(k, v)\n\t}\n}",
     "What is true about map iteration order?", "edge", "map-iteration-order", "easy",
     "Go intentionally randomizes map iteration order to discourage code that depends on it. The randomization is per-run and per-map. To iterate in a stable order, collect keys, sort, and iterate by index."),
    ("package main\n\nimport \"fmt\"\n\ntype S struct{ N int }\n\nfunc main() {\n\ts := S{N: 1}\n\tdefer fmt.Println(s.N)\n\ts.N = 2\n}",
     "What does the deferred print show?", "edge", "defer-arg-eval", "med",
     "Arguments to deferred calls are evaluated immediately, so s.N is captured as 1 even though we mutate s.N to 2 before return. This snapshot semantic prevents accidental late-binding bugs. Wrap in a closure to defer evaluation."),
    ("package main\n\nimport (\n\t\"fmt\"\n\t\"runtime\"\n)\n\nfunc main() {\n\truntime.GC()\n\tfmt.Println(runtime.NumCPU())\n}",
     "Why call runtime.GC() explicitly?", "perf", "manual-gc", "hard",
     "Forcing a GC cycle is sometimes useful in benchmarks to start with a clean heap, but in normal code it harms performance. The runtime tunes GC pacing automatically; manual calls usually indicate a benchmarking artifact or misguided optimization."),
    ("package main\n\nimport \"sort\"\n\ntype byLen []string\n\nfunc (a byLen) Len() int           { return len(a) }\nfunc (a byLen) Less(i, j int) bool { return len(a[i]) < len(a[j]) }\nfunc (a byLen) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }",
     "Why three methods for sort.Interface?", "style", "sort-interface", "med",
     "sort.Sort works on any type that implements Len, Less, Swap. This pre-generics pattern lets you reuse the sort algorithm with custom orderings. With Go 1.21+, sort.Slice and slices.SortFunc are more concise."),
    ("package main\n\nimport \"context\"\n\nfunc Do(ctx context.Context, work func(context.Context) error) error {\n\treturn work(ctx)\n}",
     "Why pass context as first parameter?", "style", "context-first-arg", "easy",
     "Go convention places context.Context as the first parameter and conventionally names it ctx. This makes context plumbing obvious at every API boundary and supports cancellation/deadline propagation through the call stack."),
    ("package main\n\nimport \"fmt\"\n\nfunc main() {\n\tch := make(chan int, 3)\n\tch <- 1\n\tch <- 2\n\tch <- 3\n\tclose(ch)\n\tfor v := range ch {\n\t\tfmt.Println(v)\n\t}\n}",
     "Why close the channel before ranging?", "concurrency", "close-channel-range", "easy",
     "Range over a channel exits when the channel is closed and drained. Without close, range blocks forever waiting for more values. Closing signals 'no more sends'; the receiver drains pending values then exits."),
    ("package main\n\nimport (\n\t\"sync\"\n)\n\nvar pool = sync.Pool{New: func() any { return make([]byte, 0, 1024) }}\n\nfunc getBuf() []byte {\n\tb := pool.Get().([]byte)\n\treturn b[:0]\n}",
     "Why b[:0] after Get?", "perf", "sync-pool-reset", "med",
     "sync.Pool returns objects that may carry state from previous users. b[:0] truncates the slice to zero length while preserving capacity, so the caller starts with an empty but pre-allocated buffer. Forget to reset and you get leftover data."),
    ("package main\n\nimport \"errors\"\n\nvar ErrNotFound = errors.New(\"not found\")\n\nfunc Lookup(k string) error {\n\treturn ErrNotFound\n}",
     "Why a package-level sentinel error?", "style", "sentinel-error-var", "easy",
     "Exporting ErrNotFound as a package-level var lets callers test specific error conditions via errors.Is. The sentinel pattern is canonical for stable error matching, complementing the typed errors.As pattern."),
    ("package main\n\nimport (\n\t\"context\"\n\t\"time\"\n)\n\nfunc Tick(ctx context.Context) {\n\tt := time.NewTicker(time.Second)\n\tdefer t.Stop()\n\tfor {\n\t\tselect {\n\t\tcase <-ctx.Done():\n\t\t\treturn\n\t\tcase <-t.C:\n\t\t}\n\t}\n}",
     "Why defer t.Stop?", "concurrency", "ticker-stop", "med",
     "Ticker keeps an internal goroutine alive until Stop is called. Without defer t.Stop(), Tick can leak the ticker when ctx is cancelled. The pattern: create ticker, defer Stop, then loop on select."),
]
for code, q, t, st, d, e in GO:
    opts = ["Cosmetic", e.split('.')[0].strip(), "Performance only", "Required syntax"]
    add('go', code, q, opts, 1, t, st, d, e)

# Rust - varied
RS = [
    ("pub fn safe_div(a: i32, b: i32) -> Option<i32> {\n    a.checked_div(b)\n}",
     "Why checked_div over a / b?", "edge", "checked-div", "easy",
     "checked_div returns None for division by zero or overflow (i32::MIN / -1) instead of panicking. Use checked_* for any arithmetic over untrusted or wide-range inputs where panics are unacceptable."),
    ("pub fn maybe_first(s: &str) -> Option<char> {\n    s.chars().next()\n}",
     "Why return Option<char>?", "style", "option-return", "easy",
     "Empty strings have no first character. Returning Option<char> makes the empty case explicit in the type, forcing callers to handle it. Panicking with .chars().next().unwrap() defers the issue to a runtime error."),
    ("use std::collections::BTreeMap;\n\npub fn ordered(pairs: Vec<(String, i32)>) -> BTreeMap<String, i32> {\n    pairs.into_iter().collect()\n}",
     "Why BTreeMap over HashMap?", "style", "btreemap-ordered", "med",
     "BTreeMap maintains keys in sorted order, so iteration yields entries lexicographically. Use BTreeMap when you need ordered traversal or range queries; HashMap is faster for lookups but has random order."),
    ("pub fn split_first<T>(v: &[T]) -> Option<(&T, &[T])> {\n    v.split_first()\n}",
     "What does slice::split_first return?", "style", "split-first", "easy",
     "split_first returns Some((&head, &tail)) for non-empty slices and None for empty ones. This is the canonical way to destructure a slice without panicking, useful in recursive algorithms on lists."),
    ("pub fn parse_pair(s: &str) -> Option<(i32, i32)> {\n    let (a, b) = s.split_once(',')?;\n    Some((a.parse().ok()?, b.parse().ok()?))\n}",
     "Why ? chained with Option?", "style", "option-chain-question", "med",
     "? on Option propagates None as the function's None. Combined with split_once and ok(), this expresses 'all parts must succeed or return None' concisely without explicit match."),
    ("use std::time::Instant;\n\npub fn time<F: FnOnce() -> R, R>(f: F) -> (R, std::time::Duration) {\n    let t = Instant::now();\n    let r = f();\n    (r, t.elapsed())\n}",
     "Why FnOnce bound?", "style", "fnonce-bound", "med",
     "FnOnce is the most permissive of the Fn family: it allows closures that consume captured state. Since time() calls the closure exactly once, FnOnce admits the widest set of closures while still permitting Fn and FnMut at call sites."),
    ("pub fn parse_or_default(s: &str, default: i32) -> i32 {\n    s.parse().unwrap_or(default)\n}",
     "Why unwrap_or over unwrap_or_else?", "perf", "unwrap-or-vs-else", "easy",
     "unwrap_or always evaluates its argument; unwrap_or_else takes a closure invoked only on Err. For cheap defaults (literals, computed values), unwrap_or is fine. For expensive computations, prefer unwrap_or_else to avoid wasted work."),
    ("pub fn clamp_u32(x: u32) -> u32 {\n    x.clamp(10, 100)\n}",
     "What does clamp guarantee?", "style", "clamp", "easy",
     "clamp(min, max) returns min if x < min, max if x > max, x otherwise. Panics if min > max. The single call replaces a max(min(x, max), min) chain that is harder to read and less amenable to optimization."),
    ("pub fn vec_to_set<T: std::hash::Hash + Eq>(v: Vec<T>) -> std::collections::HashSet<T> {\n    v.into_iter().collect()\n}",
     "Why generic <T: Hash + Eq>?", "style", "generic-bounds", "med",
     "HashSet requires keys to be hashable and equality-comparable. The where clause states this contract. Callers who pass a T missing these bounds get a clear compile error rather than failing inside the function."),
    ("pub fn vec_to_box<T>(v: Vec<T>) -> Box<[T]> {\n    v.into_boxed_slice()\n}",
     "Why Box<[T]> over Vec<T>?", "perf", "boxed-slice", "med",
     "Box<[T]> stores only the data pointer and length (16 bytes on 64-bit). Vec<T> additionally stores capacity. When you know the size is fixed, into_boxed_slice trims excess capacity and saves a usize per value."),
    ("use std::sync::atomic::{AtomicBool, Ordering};\n\npub fn cas_init(flag: &AtomicBool) -> bool {\n    flag.compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire).is_ok()\n}",
     "Why AcqRel for success?", "concurrency", "acqrel-ordering", "hard",
     "AcqRel combines Acquire (for the load) and Release (for the store) semantics, providing the happens-before guarantee needed for one-shot initialization. The failure ordering only needs Acquire since no store happens on failure."),
    ("use std::path::{Path, PathBuf};\n\npub fn join_paths(base: &Path, name: &str) -> PathBuf {\n    base.join(name)\n}",
     "Why Path vs PathBuf in the signature?", "style", "path-vs-pathbuf", "easy",
     "Path is the borrowed form (like &str); PathBuf is owned (like String). Accept &Path in arguments for flexibility; return PathBuf when ownership is needed. base.join(name) returns a new PathBuf without modifying base."),
]
for code, q, t, st, d, e in RS:
    opts = ["Cosmetic", e.split('.')[0].strip(), "Performance only", "Required syntax"]
    add('rust', code, q, opts, 1, t, st, d, e)

# SQL - varied
SQL = [
    ("WITH ranked AS (\n  SELECT id, score, RANK() OVER (ORDER BY score DESC) AS r\n  FROM games\n)\nSELECT * FROM ranked WHERE r <= 10;",
     "Why RANK over ROW_NUMBER?", "style", "rank-vs-row-number", "med",
     "RANK assigns the same rank to ties and skips subsequent ranks (1,2,2,4). ROW_NUMBER assigns unique sequential numbers regardless of ties. Use RANK when tied rows should be reported together; DENSE_RANK avoids gaps."),
    ("SELECT FIRST_VALUE(name) OVER (PARTITION BY dept ORDER BY hired_at) AS pioneer\nFROM employees;",
     "What does FIRST_VALUE return?", "style", "first-value", "med",
     "FIRST_VALUE returns the value from the first row of the window frame. With PARTITION BY dept ORDER BY hired_at, it returns the longest-tenured employee's name in each department. LAST_VALUE needs explicit frame to behave intuitively."),
    ("SELECT id, json_agg(tag) AS tags\nFROM items\nGROUP BY id;",
     "What does json_agg do?", "style", "json-agg", "med",
     "json_agg collects values into a JSON array per group. Useful for denormalizing one-to-many relationships into a single row per parent. Combined with json_build_object for nested structures."),
    ("WITH RECURSIVE n(i) AS (\n  SELECT 1\n  UNION ALL\n  SELECT i+1 FROM n WHERE i < 10\n)\nSELECT i FROM n;",
     "What does this recursive CTE produce?", "style", "recursive-cte", "med",
     "The base case starts with i=1, the recursive part increments while i<10. Result is 1..10. Recursive CTEs are useful for hierarchies (trees), sequences, and graph traversals. Always include a terminating predicate."),
    ("SELECT GENERATE_SERIES(\n  '2026-01-01'::date,\n  '2026-12-31'::date,\n  '1 month'::interval\n) AS month_start;",
     "What does generate_series do for dates?", "style", "generate-series-date", "med",
     "generate_series(start, stop, step) emits a row per increment. For dates, it builds a calendar. Useful for left-joining against actual data to fill gaps (zero rows where no events occurred)."),
    ("SELECT id\nFROM users\nWHERE created_at >= NOW() - INTERVAL '7 days'\nFOR SHARE;",
     "What does FOR SHARE do?", "concurrency", "for-share", "hard",
     "FOR SHARE acquires shared row locks on selected rows, preventing concurrent transactions from updating or deleting them until the current transaction commits. Use when you read rows that must remain stable through later writes."),
    ("CREATE TYPE user_role AS ENUM ('admin', 'user', 'guest');\n\nCREATE TABLE users (\n  id BIGSERIAL PRIMARY KEY,\n  role user_role NOT NULL DEFAULT 'user'\n);",
     "Why ENUM type?", "style", "enum-type", "easy",
     "PostgreSQL ENUM constrains a column to a fixed set of values, enforced by the database. Indexed comparison is fast (internal int representation). Note: adding a value requires ALTER TYPE; some teams prefer a lookup table for flexibility."),
    ("SELECT a.id, ARRAY_AGG(b.tag) AS tags\nFROM articles a\nLEFT JOIN article_tags b ON b.article_id = a.id\nGROUP BY a.id;",
     "What is the role of LEFT JOIN here?", "edge", "array-agg-left-join", "med",
     "LEFT JOIN ensures articles with no tags still appear with an array of {NULL}. To get an empty array instead, use ARRAY_AGG(b.tag) FILTER (WHERE b.tag IS NOT NULL) or COALESCE."),
    ("CREATE INDEX idx_active_emails\nON users (email)\nWHERE deleted_at IS NULL;",
     "Why a WHERE clause on the index?", "perf", "partial-index", "med",
     "Partial indexes only cover rows matching the predicate. The index is smaller and faster, and only relevant queries (those with deleted_at IS NULL in their WHERE) can use it. Common for soft-delete patterns."),
    ("SELECT pg_advisory_lock(hashtext('migration:v42'));\n-- do migration work\nSELECT pg_advisory_unlock(hashtext('migration:v42'));",
     "Why advisory locks for migrations?", "concurrency", "advisory-lock-migration", "hard",
     "Advisory locks are application-managed; PostgreSQL holds the lock without affecting any tables. Migration tools use them to serialize concurrent deploy attempts: only one process can hold the well-known key at a time."),
    ("EXPLAIN ANALYZE SELECT id FROM events WHERE user_id = 42 AND status = 'open';",
     "What does EXPLAIN ANALYZE add over EXPLAIN?", "perf", "explain-analyze", "easy",
     "EXPLAIN shows the planner's chosen plan; ANALYZE actually executes the query and records timing/row counts per node. This reveals planner estimate errors versus reality and is essential for query tuning."),
    ("UPDATE inventory SET qty = qty - 1\nWHERE sku = 'X' AND qty > 0\nRETURNING qty;",
     "Why include qty > 0 in WHERE?", "edge", "qty-guard", "med",
     "Without the guard, qty could decrement below zero. The atomic check-and-update in one statement avoids the classic read-decrement-write race. RETURNING gives the new value for the caller to see."),
]
for code, q, t, st, d, e in SQL:
    opts = ["Cosmetic", e.split('.')[0].strip(), "Performance only", "Required syntax"]
    add('sql', code, q, opts, 1, t, st, d, e)

print(f"generated {len(items)} items")
OUT.write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')
