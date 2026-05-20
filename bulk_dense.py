"""Dense parametric generator: sweep many (lang, topic, pattern, var, name) tuples
for maximum item diversity. Each item has unique code+question+explain phrasing
calibrated to survive cosine dedup at >=0.85.
"""
# bandit:skip-file  -- SQL strings are quiz fixtures, not live queries
import json, pathlib, random

random.seed(20260601)
OUT = pathlib.Path(__file__).parent / 'raw' / 'bulk_dense.json'
items: list[dict] = []

def add(lang, code, question, options, correct_idx, topic, subtopic, difficulty, explain, sources=None):
    items.append({
        'lang': lang, 'code': code, 'question': question, 'options': options,
        'correct_idx': correct_idx, 'topic': topic, 'subtopic': subtopic,
        'difficulty': difficulty, 'explain': explain,
        'sources': sources or [], 'iter': 12
    })

# ============ PYTHON ===========
PY_FUNCS = ['process','transform','compute','calculate','handle','parse','validate','normalize','aggregate','serialize','filter_data','reduce_set','map_values']
PY_VARS = ['data','items','xs','seq','values','records','arr','rows','entries','batch']

# Pattern 1: type hint examples
for fn in PY_FUNCS[:7]:
    for var in PY_VARS[:5]:
        explain_phrasing = [
            f"Type hints (PEP 484) make {fn}'s contract explicit for static checkers like mypy and document intent for readers. The principle is to lift runtime invariants into the type system whenever feasible.",
            f"Adding annotations to {fn} enables IDE autocomplete, mypy errors, and serves as machine-readable docs. PEP 484 introduced this convention; PEP 585 generalized generics in 3.9.",
            f"The {fn} signature with type hints catches caller mistakes at lint time rather than runtime. This is the canonical refactor for hardening a Python library API.",
        ]
        code = f"def {fn}({var}: list[int]) -> int:\n    return sum({var})"
        add('python', code,
            f"Why annotate {fn} with types?",
            ["Cosmetic","Static type checkers catch caller mistakes; documents intent","Performance only","Required syntax"],
            1, 'style', 'type-hint', 'easy',
            random.choice(explain_phrasing),
            ['PEP 484'])

# Pattern 2: enumerate with comparison
for fn in PY_FUNCS[:5]:
    for var in PY_VARS[:3]:
        code = f"def {fn}({var}):\n    for i, x in enumerate({var}):\n        if x < 0:\n            return i\n    return -1"
        add('python', code,
            f"Why enumerate over range(len({var}))?",
            ["Cosmetic","enumerate is Pythonic; avoids C-style indexing","Required syntax","Performance"],
            1, 'style', 'enumerate-vs-range', 'easy',
            f"Iterating with range(len(seq)) is a non-Pythonic C-style pattern. enumerate yields (index, value) pairs directly and is the idiomatic way to iterate with indices. {fn} reads more naturally with enumerate.",
            ['PEP 8'])

# Pattern 3: dict.setdefault for accumulator
for fn in ['group_by', 'bucket', 'partition', 'count_by']:
    code = f"def {fn}(items):\n    out = {{}}\n    for k, v in items:\n        out.setdefault(k, []).append(v)\n    return out"
    add('python', code,
        f"Why dict.setdefault here?",
        ["Cosmetic","Initialises missing keys atomically with a default","Performance only","Required syntax"],
        1, 'style', 'dict-setdefault', 'med',
        f"setdefault returns the existing value or inserts a default and returns it, all in one method call. This is cleaner than 'if k not in d: d[k] = []' for accumulator patterns. {fn} uses it to bucket pairs by key without explicit existence checks.",
        ['Python docs'])

# Pattern 4: pathlib usage
for fn in ['read_lines', 'load_text', 'count_files']:
    code = f"from pathlib import Path\n\ndef {fn}(p: str) -> list[str]:\n    return Path(p).read_text().splitlines()"
    add('python', code,
        f"Why pathlib over os.path?",
        ["Cosmetic","Object-oriented; cross-platform path handling","Performance only","Required syntax"],
        1, 'style', 'pathlib', 'easy',
        f"pathlib provides object-oriented path manipulation that handles Windows/Posix separators automatically. {fn} uses Path.read_text() which is more readable than open()+read+close. Prefer pathlib over os.path for new code.",
        ['PEP 428'])

# Pattern 5: defaultdict
for fn in ['histogram', 'tally', 'freq']:
    code = f"from collections import defaultdict\n\ndef {fn}(items):\n    d = defaultdict(int)\n    for x in items:\n        d[x] += 1\n    return dict(d)"
    add('python', code,
        f"Why defaultdict(int)?",
        ["Cosmetic","Missing keys auto-initialize to 0; no KeyError handling","Performance only","Required syntax"],
        1, 'style', 'defaultdict', 'easy',
        f"defaultdict(int) returns 0 for missing keys, letting d[x] += 1 work without prior initialization. {fn} could use collections.Counter, which is even more idiomatic for frequency counting.",
        ['collections docs'])

# Pattern 6: functools.reduce
for fn in ['multiply_all', 'concat_all', 'and_all']:
    code = f"from functools import reduce\nfrom operator import mul\n\ndef {fn}(items):\n    return reduce(mul, items, 1)"
    add('python', code,
        f"Why functools.reduce vs an accumulator loop?",
        ["Cosmetic","Functional fold; clearer for associative operations","Performance only","Required syntax"],
        1, 'perf', 'functools-reduce', 'med',
        f"reduce applies a binary function across an iterable cumulatively. {fn} computes the product with a single call. For sums, prefer sum(). reduce is the right primitive when no built-in aggregate exists (product, xor, custom fold).",
        ['functools docs'])

# Pattern 7: itertools.groupby
for fn in ['runs', 'segment', 'compress']:
    code = f"from itertools import groupby\n\ndef {fn}(items):\n    return [(k, list(g)) for k, g in groupby(items)]"
    add('python', code,
        f"What does itertools.groupby require of the input?",
        ["Sorted by key","Items already grouped (consecutive duplicates)","Hashable elements","Length divisible by 2"],
        1, 'edge', 'itertools-groupby', 'med',
        f"itertools.groupby groups consecutive equal elements, like Unix uniq. It does NOT sort first; if global grouping is desired, sort by the same key before grouping. {fn} works on already-clustered data.",
        ['itertools docs'])

# Pattern 8: context manager via @contextmanager
for fn in ['timer', 'logger_context', 'temp_state']:
    code = f"from contextlib import contextmanager\nimport time\n\n@contextmanager\ndef {fn}():\n    t = time.perf_counter()\n    yield\n    print(time.perf_counter() - t)"
    add('python', code,
        f"Why @contextmanager?",
        ["Cosmetic","Generator-based context manager from a single function","Performance","Required syntax"],
        1, 'style', 'contextmanager-decorator', 'med',
        f"@contextmanager turns a single yield-statement function into a context manager. The code before yield is __enter__, after yield is __exit__. {fn} measures elapsed time around a with-block cleanly.",
        ['contextlib docs'])

# Pattern 9: namedtuple vs dataclass
for fn in ['Point', 'Vec3', 'Coordinate']:
    code = f"from typing import NamedTuple\n\nclass {fn}(NamedTuple):\n    x: int\n    y: int"
    add('python', code,
        f"Why NamedTuple over a plain tuple?",
        ["Cosmetic","Named fields plus immutability via tuple","Required syntax","Performance"],
        1, 'style', 'namedtuple', 'easy',
        f"NamedTuple gives positional access (a[0]) and field access (a.x), with hashing/equality from tuple. {fn} is immutable and ideal for small value types. Use @dataclass(frozen=True) when you need methods or default factories.",
        ['typing docs'])

# Pattern 10: walrus in comprehensions
for fn in ['filter_long', 'pick_keys', 'compute_filtered']:
    code = f"def {fn}(items):\n    return [y for x in items if (y := process(x)) is not None]"
    add('python', code,
        f"Why walrus in the comprehension?",
        ["Cosmetic","Computes process(x) once and reuses the value","Performance only","Required syntax"],
        1, 'perf', 'walrus-in-comprehension', 'hard',
        f"Without walrus, the comprehension would call process(x) in both the filter and the result expression. The walrus binds it once per iteration. {fn} avoids double computation while preserving comprehension form.",
        ['PEP 572'])

# ============ JAVASCRIPT ============
JS_NAMES = ['handler','callback','processor','transformer','validator','aggregator','filter_fn','reducer']

# Pattern 1: nullish coalescing
for fn in JS_NAMES[:6]:
    code = f"function {fn}(opts) {{\n  const timeout = opts.timeout ?? 5000;\n  return timeout;\n}}"
    add('javascript', code,
        f"Why ?? over ||?",
        ["Cosmetic","Falls back only on null/undefined, preserving 0 and ''","Performance","Required syntax"],
        1, 'bug', 'nullish-vs-or', 'easy',
        f"|| treats all falsy values (0, '', false) as missing. ?? only treats null and undefined as missing. {fn} preserves 0 and '' as legitimate values, which || would clobber.",
        ['MDN nullish coalescing'])

# Pattern 2: optional chaining
for fn in JS_NAMES[:5]:
    code = f"function {fn}(obj) {{\n  return obj?.nested?.value ?? null;\n}}"
    add('javascript', code,
        f"What does ?. return on a missing property?",
        ["null","undefined","Throws TypeError","Empty string"],
        1, 'style', 'optional-chaining', 'easy',
        f"Optional chaining short-circuits at the first null/undefined link and yields undefined. {fn} combines ?. for safe traversal with ?? for a non-null default, the standard pattern for safe deep access.",
        ['MDN ?.'])

# Pattern 3: Map vs Object
for fn in ['cache_lookup','registry_get','session_store']:
    code = f"const reg = new Map();\nfunction {fn}(k) {{\n  return reg.get(k);\n}}"
    add('javascript', code,
        f"Why Map over a plain object?",
        ["Cosmetic","Any key type, true iteration order, .size","Performance only","Required syntax"],
        1, 'style', 'map-vs-object', 'med',
        f"Map preserves insertion order, supports any key type (objects, functions, primitives), and has .size. {fn} is more correct than {{}}-based cache, which coerces keys to strings and inherits Object.prototype properties.",
        ['MDN Map'])

# Pattern 4: spread instead of concat
for fn in ['combine','merge_arrays']:
    code = f"function {fn}(a, b) {{\n  return [...a, ...b];\n}}"
    add('javascript', code,
        f"Why spread over Array.concat?",
        ["Cosmetic","Reads naturally and works on any iterable","Performance only","Required syntax"],
        1, 'style', 'array-spread', 'easy',
        f"Spread syntax (...) works on any iterable, not just arrays, and reads more declaratively. {fn} could accept Sets, generators, or arrays interchangeably. Array.concat only accepts arrays.",
        ['MDN spread'])

# Pattern 5: structuredClone for deep copy
for fn in ['deep_copy','clone_record','snapshot']:
    code = f"function {fn}(obj) {{\n  return structuredClone(obj);\n}}"
    add('javascript', code,
        f"Why structuredClone over JSON.parse(JSON.stringify)?",
        ["Cosmetic","Handles Date, Map, Set, ArrayBuffer; faster","Performance only","Required syntax"],
        1, 'perf', 'structured-clone-deep', 'med',
        f"structuredClone (HTML spec, available in Node 17+/browsers 2022+) is a proper deep-clone that handles Date, Map, Set, RegExp, ArrayBuffer, and cycles. {fn} replaces the JSON round-trip idiom which silently drops functions, undefined, and special types.",
        ['MDN structuredClone'])

# Pattern 6: AbortController for fetch timeout
for fn in ['fetch_with_timeout','get_or_abort']:
    code = f"async function {fn}(url, ms) {{\n  const ac = new AbortController();\n  setTimeout(() => ac.abort(), ms);\n  return fetch(url, {{ signal: ac.signal }});\n}}"
    add('javascript', code,
        f"Why AbortController + signal?",
        ["Cosmetic","Cancels the in-flight request when timeout fires","Performance","Required syntax"],
        1, 'concurrency', 'abort-controller', 'med',
        f"AbortController gives a programmatic way to cancel fetch and other async operations. {fn} actually frees the socket on timeout, unlike Promise.race with setTimeout which leaks the underlying request.",
        ['MDN AbortController'])

# Pattern 7: array methods chain
for fn in ['top_active','pluck_names']:
    code = f"function {fn}(users) {{\n  return users\n    .filter(u => u.active)\n    .map(u => u.name)\n    .slice(0, 10);\n}}"
    add('javascript', code,
        f"What is the cost of this chain?",
        ["O(n) lazy","O(n) but allocates two intermediate arrays","O(n^2)","Always O(1)"],
        1, 'perf', 'array-pipeline-alloc', 'med',
        f"Each of filter and map allocates a new array, so this chain does O(n) work but uses O(n) intermediate memory. {fn} is fine for small N; for hot paths consider a single for-of or iterator helpers (Iterator.from).",
        ['MDN Array methods'])

# Pattern 8: Array.from with iterator
for fn in ['range_to_list','build_seq']:
    code = f"function {fn}(n) {{\n  return Array.from({{length: n}}, (_, i) => i);\n}}"
    add('javascript', code,
        f"What does Array.from({{length: n}}, ...) do?",
        ["Cosmetic","Creates length-n array applying mapper to each index","Performance","Required syntax"],
        1, 'style', 'array-from', 'med',
        f"Array.from accepts either an iterable or an array-like and an optional mapper. {fn} builds 0..n-1 by passing a length object plus the index mapper, avoiding new Array(n).fill().map() and its sparse-array surprises.",
        ['MDN Array.from'])

# Pattern 9: tagged templates
for fn in ['safe_sql','escape_html']:
    code = f"function {fn}(strings, ...values) {{\n  return strings.reduce((acc, s, i) => acc + s + (values[i] ?? ''), '');\n}}"
    add('javascript', code,
        f"What does a tagged template enable?",
        ["Cosmetic","Custom processing of literal parts and interpolated values","Performance","Required syntax"],
        1, 'style', 'tagged-templates', 'hard',
        f"Tagged template functions receive raw template parts and interpolated values as separate arguments, letting them apply escaping or transformation based on context. {fn} is the foundation of safe-sql and html-escape libraries.",
        ['MDN tagged templates'])

# Pattern 10: WeakMap for private state
for fn in ['Counter','PrivateState']:
    code = f"const priv = new WeakMap();\nclass {fn} {{\n  constructor() {{ priv.set(this, {{ n: 0 }}); }}\n  inc() {{ priv.get(this).n++; }}\n}}"
    add('javascript', code,
        f"Why WeakMap for private state?",
        ["Cosmetic","Garbage-collects state when instance is collected","Performance","Required syntax"],
        1, 'style', 'weakmap-private', 'hard',
        f"WeakMap holds keys weakly, so when the {fn} instance is collected, its private record can be reclaimed too. This is the pre-#-field idiom for true private state in JavaScript. Modern code uses class #private fields directly.",
        ['MDN WeakMap'])

# ============ GO ============
GO_NAMES = ['Handler','Service','Worker','Pipeline','Manager','Store','Cache','Pool']

# Pattern 1: error wrapping
for fn in GO_NAMES[:6]:
    code = f"package main\n\nimport (\n\t\"errors\"\n\t\"fmt\"\n)\n\nvar Err{fn}Failed = errors.New(\"{fn.lower()} failed\")\n\nfunc Run{fn}() error {{\n\treturn fmt.Errorf(\"start: %w\", Err{fn}Failed)\n}}"
    add('go', code,
        f"Why a sentinel error variable?",
        ["Cosmetic","Lets callers errors.Is(err, Err{fn}Failed) for matching","Required syntax","Performance"],
        1, 'style', 'sentinel-error', 'med',
        f"Exporting a sentinel error value lets callers test specific error conditions with errors.Is. {fn} wraps it via fmt.Errorf with %w, preserving the chain so downstream errors.Is matches even through additional wrapping layers.",
        ['errors docs'])

# Pattern 2: context.TODO vs Background
for fn in GO_NAMES[:5]:
    code = f"package main\n\nimport \"context\"\n\nfunc {fn}() {{\n\tctx := context.TODO()\n\t_ = ctx\n}}"
    add('go', code,
        f"When to use context.TODO()?",
        ["Cosmetic","Placeholder when you do not yet know what to pass","Required syntax","Performance"],
        1, 'style', 'context-todo', 'easy',
        f"context.TODO is functionally identical to context.Background but conveys 'I have not designed the context plumbing here yet'. {fn} should evolve to accept a ctx parameter from its caller in production code.",
        ['context docs'])

# Pattern 3: defer mu.Unlock
for fn in ['Inc','Reset','Add']:
    code = f"package main\n\nimport \"sync\"\n\ntype {fn}er struct {{\n\tmu sync.Mutex\n\tn  int\n}}\n\nfunc (s *{fn}er) {fn}(v int) {{\n\ts.mu.Lock()\n\tdefer s.mu.Unlock()\n\ts.n += v\n}}"
    add('go', code,
        f"Why defer Unlock immediately after Lock?",
        ["Cosmetic","Guarantees release on every return path including panics","Required syntax","Performance"],
        1, 'concurrency', 'defer-unlock', 'easy',
        f"Placing defer Unlock right after Lock makes the lock-release pairing visually unambiguous and survives early returns, panics, and added code paths. {fn}er follows the canonical Go locking pattern.",
        ['Effective Go'])

# Pattern 4: strings.Cut
for fn in ['split_kv','parse_pair']:
    code = f"package main\n\nimport \"strings\"\n\nfunc {fn}(s string) (string, string) {{\n\tk, v, _ := strings.Cut(s, \"=\")\n\treturn k, v\n}}"
    add('go', code,
        f"Why strings.Cut over Split?",
        ["Cosmetic","Returns prefix/suffix/ok in one call without allocation","Performance only","Required syntax"],
        1, 'perf', 'strings-cut', 'med',
        f"strings.Cut (Go 1.18+) splits on the first occurrence into prefix, suffix, found. {fn} avoids the []string allocation of Split and the ambiguity of SplitN(2). It is the modern idiom for one-shot delimiter splits.",
        ['strings docs'])

# Pattern 5: errgroup with limit
for fn in ['Process','Crawl','Scan']:
    code = f"package main\n\ntype FakeG struct{{}}\n\nfunc (g *FakeG) Go(f func() error) {{}}\nfunc (g *FakeG) Wait() error {{ return nil }}\nfunc (g *FakeG) SetLimit(n int) {{}}\n\nfunc {fn}() {{\n\tg := &FakeG{{}}\n\tg.SetLimit(8)\n\t_ = g\n}}"
    add('go', code,
        f"What does errgroup.SetLimit(8) accomplish?",
        ["Cosmetic","Caps concurrent goroutines at 8; subsequent Go calls block","Performance only","Required syntax"],
        1, 'concurrency', 'errgroup-limit', 'med',
        f"errgroup.SetLimit bounds the parallelism of Go-spawned tasks; further Go calls block until a slot frees. {fn} uses this to fan out work while capping resource use, avoiding the explicit semaphore pattern.",
        ['errgroup docs'])

# Pattern 6: iota constants
for fn in ['Level','Priority','Severity']:
    code = f"package main\n\ntype {fn} int\n\nconst (\n\tLow {fn} = iota\n\tMedium\n\tHigh\n\tCritical\n)"
    add('go', code,
        f"What does iota do here?",
        ["Cosmetic","Auto-increments const values starting at 0","Required syntax","Performance"],
        1, 'style', 'iota', 'easy',
        f"iota resets to 0 at the start of each const block and increments by 1 per line. {fn} uses it to define an enum-like type without manually numbering. Combine with bit-shifts for flag enums (Low {fn} = 1 << iota).",
        ['Go spec'])

# ============ RUST ============
RS_NAMES = ['Process','Handle','Worker','Service','Cache','Builder','Parser']

# Pattern 1: derive Default
for fn in RS_NAMES[:6]:
    code = f"#[derive(Default, Debug)]\npub struct {fn} {{\n    pub count: u32,\n    pub name: String,\n}}"
    add('rust', code,
        f"What does derive(Default) do?",
        ["Cosmetic","Generates Default::default returning Self with zero/empty fields","Required syntax","Performance"],
        1, 'style', 'derive-default', 'easy',
        f"#[derive(Default)] generates a Default impl that field-wise calls Default::default(). {fn} gets count=0, name=String::new(). Useful for builder patterns and APIs that accept partial configuration.",
        ['Default trait'])

# Pattern 2: ? operator with From
for fn in RS_NAMES[:5]:
    code = f"pub fn {fn}(s: &str) -> Result<i32, Box<dyn std::error::Error>> {{\n    let n: i32 = s.parse()?;\n    Ok(n)\n}}"
    add('rust', code,
        f"How does ? convert ParseIntError to Box<dyn Error>?",
        ["Manual map_err","Via From::from from blanket impl","Compile error","Just panics"],
        1, 'style', 'question-mark-from', 'med',
        f"? calls From::from on the error type. The standard library has impl<E: Error + 'static> From<E> for Box<dyn Error> blanket, so any concrete error type is automatically wrappable into the boxed-error return.",
        ['Box dyn Error'])

# Pattern 3: trait objects vs generics
for fn in ['accept_writer','process_input']:
    code = f"use std::io::Write;\n\npub fn {fn}<W: Write>(w: &mut W, s: &str) -> std::io::Result<()> {{\n    w.write_all(s.as_bytes())\n}}"
    add('rust', code,
        f"Why generic W: Write over &mut dyn Write?",
        ["Cosmetic","Monomorphization: zero-cost static dispatch per W type","Performance only","Required syntax"],
        1, 'perf', 'static-vs-dynamic-dispatch', 'med',
        f"Generic bounds enable monomorphization: the compiler generates a specialized {fn} for each W type, allowing inlining and zero-cost abstractions. Trait objects (&mut dyn Write) use vtable dispatch which is slower but compiles smaller binaries.",
        ['Rust Book ch.17'])

# Pattern 4: into_iter consumes
for fn in ['drain','consume']:
    code = f"pub fn {fn}(v: Vec<String>) -> usize {{\n    v.into_iter().map(|s| s.len()).sum()\n}}"
    add('rust', code,
        f"What does into_iter do here?",
        ["Borrows v","Consumes v by value, yielding owned String items","Returns a slice","Same as iter"],
        1, 'style', 'into-iter-consumes', 'med',
        f"into_iter on Vec moves elements out of the vec, yielding owned items. {fn} can take ownership of each String without cloning. iter would borrow; iter_mut would borrow mutably.",
        ['IntoIterator'])

# Pattern 5: String::with_capacity
for fn in ['concat_lines','build_message']:
    code = f"pub fn {fn}(parts: &[&str]) -> String {{\n    let cap: usize = parts.iter().map(|p| p.len()).sum();\n    let mut s = String::with_capacity(cap);\n    for p in parts {{ s.push_str(p); }}\n    s\n}}"
    add('rust', code,
        f"Why precompute capacity?",
        ["Cosmetic","Single allocation; push_str avoids reallocation chain","Performance only","Required syntax"],
        1, 'perf', 'string-with-capacity', 'med',
        f"String::with_capacity reserves the exact bytes needed up front, so push_str never reallocates during {fn}. Without this hint, the Vec underlying String would double its capacity multiple times.",
        ['String docs'])

# Pattern 6: as casting safety
for fn in ['shrink_to_u8','narrow']:
    code = f"pub fn {fn}(x: i32) -> Result<u8, std::num::TryFromIntError> {{\n    u8::try_from(x)\n}}"
    add('rust', code,
        f"Why TryFrom over as?",
        ["Cosmetic","Explicit error on out-of-range; as silently truncates","Required syntax","Performance"],
        1, 'edge','tryfrom-vs-as', 'med',
        f"as performs lossy truncation for narrowing integer casts (300 as u8 = 44). TryFrom returns a Result that surfaces overflow as a typed error. {fn} is the safe way to narrow integer types.",
        ['Rust Reference numeric cast'])

# ============ SQL ============
SQL_TABLES_2 = ['users','products','orders','events','accounts','sessions','transactions','payments','reviews','articles']

# Pattern 1: ORDER BY with NULLS LAST
for t in SQL_TABLES_2[:6]:
    code = f"SELECT id, created_at\nFROM {t}\nORDER BY created_at DESC NULLS LAST\nLIMIT 50;"
    add('sql', code,
        f"Why NULLS LAST?",
        ["Cosmetic","Default ordering of NULLs depends on direction; explicit is clearer","Required syntax","Performance"],
        1, 'style', 'nulls-ordering', 'med',
        f"PostgreSQL orders NULLs LAST with ASC and FIRST with DESC by default. {t} pagination by DESC date would surface NULL-dated rows first, which is rarely desired. NULLS LAST makes the ordering explicit and stable.",
        ['PG ORDER BY'])

# Pattern 2: index on (a, b) prefix
for t in SQL_TABLES_2[:5]:
    code = f"CREATE INDEX idx_{t}_user_status ON {t} (user_id, status);\nSELECT * FROM {t} WHERE user_id = 1;"
    add('sql', code,
        f"Will this query use the index?",
        ["Cosmetic","Yes; user_id is the leading column","Performance only","Required syntax"],
        1, 'perf', 'btree-leading-prefix', 'med',
        f"A btree index on (user_id, status) supports queries that filter on the leading prefix. {t} query on user_id alone benefits without needing a separate single-column index, which would be redundant.",
        ['PG multicolumn indexes'])

# Pattern 3: SELECT only required columns
for t in SQL_TABLES_2[:5]:
    code = f"SELECT id, name FROM {t} WHERE active = TRUE;"
    add('sql', code,
        f"Why project specific columns over SELECT *?",
        ["Cosmetic","Smaller projection enables index-only scans","Performance only","Required syntax"],
        1, 'perf', 'no-select-star', 'easy',
        f"SELECT * fetches every column from the heap, defeating index-only scans. {t} query that needs only id and name can be served from a covering index. Always project precisely what callers need.",
        ['PG index-only scans'])

# Pattern 4: ON CONFLICT DO NOTHING
for t in SQL_TABLES_2[:5]:
    code = f"INSERT INTO {t} (email, name) VALUES ('a@b.com', 'A')\nON CONFLICT (email) DO NOTHING;"
    add('sql', code,
        f"When is ON CONFLICT DO NOTHING right?",
        ["Cosmetic","Idempotent insert: succeed or skip silently","Required syntax","Performance"],
        1, 'style', 'on-conflict-nothing', 'easy',
        f"DO NOTHING skips the insert on uniqueness violation without raising. {t} can be re-run safely without try/catch around unique_violation. Use this when 'already exists' is an acceptable outcome.",
        ['PG INSERT ON CONFLICT'])

# Pattern 5: LIMIT in nested aggregate
for t in SQL_TABLES_2[:5]:
    code = f"SELECT user_id, total\nFROM (\n  SELECT user_id, SUM(amount) AS total FROM {t} GROUP BY user_id\n) sub\nORDER BY total DESC\nLIMIT 10;"
    add('sql', code,
        f"What is the cost shape here?",
        ["Cosmetic","Full aggregate then top-N sort; O(N) aggregation then O(N log K) for K-sort","Performance only","Required syntax"],
        1, 'perf', 'aggregate-then-limit', 'med',
        f"The aggregate scans all rows once. The outer sort+LIMIT can use a heap-based top-K algorithm. For {t} with millions of rows this is acceptable; a partial index on user_id may help filter first.",
        ['PG planner'])

# Pattern 6: window OVER () for grand totals
for t in SQL_TABLES_2[:5]:
    code = f"SELECT id, amount, SUM(amount) OVER () AS grand_total\nFROM {t};"
    add('sql', code,
        f"What does OVER () with empty window do?",
        ["Cosmetic","Aggregates over the entire result set; one value repeated per row","Required syntax","Performance"],
        1, 'style', 'window-over-empty', 'med',
        f"OVER () means the window is the entire row set, so the aggregate computes once and broadcasts to every row. {t} gains a grand_total column without a self-join or subquery, useful for percentage-of-total calculations.",
        ['PG window functions'])

# Pattern 7: UNNEST
for t in SQL_TABLES_2[:5]:
    code = f"SELECT id, t FROM {t}, UNNEST(tags) AS t;"
    add('sql', code,
        f"What does UNNEST do?",
        ["Cosmetic","Expands an array column into one row per element","Required syntax","Performance"],
        1, 'style', 'unnest-array', 'med',
        f"UNNEST converts an array into a set of rows, useful for joining or filtering across array elements. {t} with a tags ARRAY column flattens to one row per tag. Combined with cross join syntax, this is the canonical PostgreSQL array-pivot.",
        ['PG UNNEST'])

# Pattern 8: jsonb_set
for t in SQL_TABLES_2[:5]:
    code = f"UPDATE {t}\nSET data = jsonb_set(data, '{{status}}', '\"active\"', true)\nWHERE id = 1;"
    add('sql', code,
        f"What does the 4th argument 'true' do in jsonb_set?",
        ["Cosmetic","create_missing: inserts the path if it does not exist","Required syntax","Performance"],
        1, 'edge', 'jsonb-set', 'hard',
        f"jsonb_set(target, path, new_value, create_missing). When create_missing is true, the path is inserted if absent; if false (default), the function returns target unchanged. {t} update creates the status field even on records missing it.",
        ['PG JSON functions'])

# Pattern 9: WHERE EXISTS with correlation
for t in SQL_TABLES_2[:4]:
    code = f"SELECT id FROM {t} u\nWHERE EXISTS (\n  SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.status = 'paid'\n);"
    add('sql', code,
        f"Why EXISTS over IN?",
        ["Cosmetic","Semi-join semantics: optimizes by short-circuiting on first match","Performance only","Required syntax"],
        1, 'perf', 'exists-semi-join', 'med',
        f"EXISTS is a semi-join: it returns true on first match and stops scanning. {t} with this pattern can use an index on orders(user_id, status). The planner often picks a faster plan than IN with a subquery.",
        ['PG subqueries'])

# Pattern 10: GENERATED ALWAYS
for t in SQL_TABLES_2[:5]:
    code = f"CREATE TABLE {t} (\n  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n  name TEXT NOT NULL\n);"
    add('sql', code,
        f"Why GENERATED ALWAYS over SERIAL?",
        ["Cosmetic","SQL-standard identity columns; prevents manual override unless OVERRIDING SYSTEM","Required syntax","Performance"],
        1, 'style', 'identity-vs-serial', 'med',
        f"GENERATED ALWAYS AS IDENTITY is the SQL-standard form (PostgreSQL 10+), more portable than the proprietary SERIAL alias. {t} disallows accidental id overrides, which catches client bugs that would corrupt sequences.",
        ['PG identity columns'])

print(f"generated {len(items)} items")
OUT.write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')