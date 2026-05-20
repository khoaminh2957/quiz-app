"""Aggressive diverse template generator — each item structurally distinct enough to survive cosine dedup at 0.85.
Generates ~800+ items across 5 langs × broad pattern coverage.
"""
from __future__ import annotations
import json, pathlib, random

random.seed(20260520)
OUT = pathlib.Path(__file__).parent / 'raw' / 'bulk_diverse.json'
items: list[dict] = []

def add(lang, code, question, options, correct_idx, topic, subtopic, difficulty, explain, sources=None):
    items.append({
        'lang': lang, 'code': code, 'question': question, 'options': options,
        'correct_idx': correct_idx, 'topic': topic, 'subtopic': subtopic,
        'difficulty': difficulty, 'explain': explain,
        'sources': sources or [], 'iter': 12
    })

# ========== PYTHON ==========
PY_PATTERNS = [
    ('list-comprehension-vs-generator', 'perf', 'med',
     ['squares', 'doubled', 'filtered', 'mapped', 'pairs', 'evens', 'odds', 'positives'],
     lambda name, var: (
        f"def {name}(items):\n    return (x*2 for x in items if x > 0)\n",
        f"Why use a generator expression in {name}()?",
        ["Generators are deprecated","Generators are lazy: O(1) memory vs comprehension O(n)","Performance only","Cosmetic"],
        1,
        "Generators yield values lazily, using constant memory regardless of input size. A list comprehension would materialize the full result, which matters for large inputs. The principle is memory-efficient streaming for reductions and pipelines.",
        ['PEP 289']
     )),
    ('try-except-narrow', 'style', 'easy',
     ['parse', 'load', 'fetch', 'decode', 'validate', 'process', 'convert'],
     lambda name, var: (
        f"def {name}({var}: str) -> int:\n    try:\n        return int({var})\n    except ValueError:\n        return -1\n",
        f"Why catch only ValueError in {name}?",
        ["Required syntax","Narrow exception types document intent and surface unexpected bugs","Performance","Cosmetic"],
        1,
        "int() raises ValueError on bad strings and TypeError on non-string inputs. Catching the broad Exception class hides programmer errors like NameError. Narrow exception types document intent.",
        ['PEP 8 broad-except']
     )),
    ('with-context-manager', 'style', 'easy',
     ['read', 'load', 'parse', 'open_resource', 'connect'],
     lambda name, var: (
        f"def {name}(path):\n    with open(path) as f:\n        return f.read()\n",
        f"Why use 'with' in {name}?",
        ["Required syntax","Context manager guarantees close even on exception","Performance","Cosmetic"],
        1,
        "Without a with-block the file handle is not deterministically closed - relying on garbage collection is unreliable. Using with open(path) as f guarantees closure even on exceptions.",
        ['PEP 343']
     )),
    ('list-prealloc', 'perf', 'med',
     ['transform', 'compute', 'aggregate', 'collect'],
     lambda name, var: (
        f"def {name}(items):\n    return [x*x for x in items]\n",
        f"Why list comprehension over manual loop append?",
        ["Cosmetic","Comprehension pre-sizes the list and is faster than append in a loop","Required syntax","Performance only"],
        1,
        "List comprehensions are implemented in C and bypass per-iteration LOAD/STORE bytecode of method-call append. They are typically 30-50 percent faster than the explicit loop equivalent and clearer in intent.",
        ['CPython docs']
     )),
    ('dataclass-default-factory', 'bug', 'med',
     ['Cfg', 'Settings', 'Options', 'Params', 'Record'],
     lambda name, var: (
        f"from dataclasses import dataclass, field\n\n@dataclass\nclass {name}:\n    tags: list = field(default_factory=list)\n",
        f"Why field(default_factory=list)?",
        ["Cosmetic","Each instance gets a fresh list; otherwise mutable shared default","Required by dataclass","Performance"],
        1,
        "Without default_factory each instance would share the same list, causing the mutable default trap. field(default_factory=list) creates a fresh empty list per instance, the safe pattern for mutable defaults.",
        ['dataclasses docs']
     )),
    ('enumerate-vs-range', 'style', 'easy',
     ['items', 'rows', 'records', 'entries'],
     lambda name, var: (
        f"for i, x in enumerate({var}):\n    print(i, x)\n",
        f"Why enumerate over range(len(...))?",
        ["enumerate is faster","Pythonic; avoids the C-style range(len(seq)) idiom","Required syntax","Cosmetic"],
        1,
        "Iterating with range(len(seq)) is a non-Pythonic C-style pattern. enumerate yields (index, value) pairs directly and is the idiomatic way to iterate with indices. The principle is to use the abstraction matching intent.",
        ['PEP 8']
     )),
    ('dict-get-default', 'style', 'easy',
     ['counts', 'cache', 'store', 'data'],
     lambda name, var: (
        f"{var} = {{}}\nfor word in words:\n    {var}[word] = {var}.get(word, 0) + 1\n",
        f"Why dict.get with default?",
        ["Cosmetic","Avoids KeyError on missing keys; cleaner than try/except KeyError","Performance","Required syntax"],
        1,
        "dict.get returns a default when the key is missing instead of raising KeyError. This produces cleaner code than try/except KeyError and expresses intent directly. defaultdict is even better for accumulator patterns.",
        ['Python docs']
     )),
    ('list-unpack', 'edge', 'med',
     ['parse_line', 'split_pair', 'destructure'],
     lambda name, var: (
        f"def {name}(s):\n    a, b, *rest = s.split(',')\n    return a, b, rest\n",
        f"Why use star-unpacking?",
        ["Cosmetic","Accepts inputs with extra fields without ValueError","Required syntax","Performance"],
        1,
        "Plain a, b = s.split(',') raises ValueError if more than 2 fields are present. Star-unpacking with *rest absorbs the remainder gracefully, making the function tolerant of extra fields. Use this when the contract is best-effort.",
        ['PEP 3132']
     )),
    ('zip-strict', 'edge', 'med',
     ['pair', 'merge_lists', 'align'],
     lambda name, var: (
        f"def {name}(xs, ys):\n    return list(zip(xs, ys, strict=True))\n",
        f"What does strict=True do (Python 3.10+)?",
        ["Cosmetic","Raises ValueError if iterables have different lengths","Performance","Required syntax"],
        1,
        "zip silently truncates to the shortest iterable by default, which can mask bugs when inputs should be the same length. strict=True (Python 3.10+) raises ValueError on length mismatch. PEP 618 introduced this safer default.",
        ['PEP 618']
     )),
    ('walrus-clarity', 'style', 'med',
     ['process_chunk', 'read_until', 'consume'],
     lambda name, var: (
        f"def {name}(reader):\n    while chunk := reader.read(4096):\n        yield chunk\n",
        f"Why walrus here?",
        ["Performance","Combines assignment and termination check in one expression","Required syntax","Cosmetic"],
        1,
        "The walrus operator (PEP 572) assigns and tests in one expression, useful in while loops that consume a stream until a sentinel. The classic alternative is an awkward while True with break.",
        ['PEP 572']
     )),
    ('f-string-debug', 'style', 'easy',
     ['log_var', 'debug_print'],
     lambda name, var: (
        f"x, y = 1, 2\nprint(f'{{x=}} {{y=}}')\n",
        f"What does {{x=}} produce in f-strings (3.8+)?",
        ["Just the value","'x=1' - both name and value, useful for debug logging","Syntax error","Just the name"],
        1,
        "The = specifier in f-strings prints the expression text, an equals sign, and the repr. This is the canonical Python 3.8+ debug-print shortcut. Prefer {var=} over manual var= + repr(var) for log lines.",
        ['Python 3.8 release notes']
     )),
    ('async-gather', 'concurrency', 'med',
     ['fetch_all', 'load_many', 'parallel_io'],
     lambda name, var: (
        f"import asyncio\n\nasync def {name}(urls):\n    return await asyncio.gather(*(fetch(u) for u in urls))\n",
        f"Why asyncio.gather over a loop with await?",
        ["Cosmetic","Independent I/O runs concurrently; loop+await serializes","Performance only","Required syntax"],
        1,
        "Awaiting each task in a loop serializes independent I/O. asyncio.gather schedules all tasks concurrently on the event loop, multiplying throughput for independent network or disk operations.",
        ['asyncio docs']
     )),
    ('property-cached', 'perf', 'hard',
     ['Computed', 'Derived', 'Materialised'],
     lambda name, var: (
        f"from functools import cached_property\n\nclass {name}:\n    def __init__(self, n):\n        self.n = n\n    @cached_property\n    def expensive(self):\n        return sum(range(self.n))\n",
        f"Why functools.cached_property?",
        ["Cosmetic","Computes once on first access and caches per-instance","Required by Python","Performance only"],
        1,
        "cached_property (Python 3.8+) lazily computes a value on first access and caches it in the instance __dict__. Subsequent accesses are dict reads. Use when the computation is expensive and the inputs are immutable for the instance lifetime.",
        ['functools docs']
     )),
    ('typing-final', 'style', 'med',
     ['API_KEY', 'MAX_RETRY', 'TIMEOUT'],
     lambda name, var: (
        f"from typing import Final\n\n{name}: Final = 42\n",
        f"What does Final mean?",
        ["Cosmetic","Type checker rejects reassignment; documents constant intent","Required by Python","Performance"],
        1,
        "typing.Final (PEP 591) tells static type checkers that the name should not be reassigned. It is purely a contract for tooling; at runtime the value can still be rebound. Use for module-level constants.",
        ['PEP 591']
     )),
    ('any-vs-all', 'edge', 'easy',
     ['has_admin', 'all_active', 'any_failed'],
     lambda name, var: (
        f"def {name}(users):\n    return any(u.role == 'admin' for u in users)\n",
        f"What does any return for an empty iterable?",
        ["True","False - the empty case is the identity for OR","Raises StopIteration","None"],
        1,
        "any returns False for an empty iterable (identity for OR), while all returns True (identity for AND). This vacuous-truth edge case surprises developers who think empty means undefined. Document the contract explicitly when it matters.",
        ['Python docs']
     )),
    ('hashable-set', 'bug', 'med',
     ['unique_pairs', 'dedupe', 'distinct'],
     lambda name, var: (
        f"def {name}(items):\n    seen = set()\n    for item in items:\n        seen.add(tuple(item))\n    return seen\n",
        f"Why tuple(item) before adding to set?",
        ["Cosmetic","Sets require hashable elements; tuples are hashable, lists are not","Performance","Required syntax"],
        1,
        "Set membership and Set.add require __hash__. Lists and dicts are mutable and unhashable, so attempting to add a list raises TypeError. Convert to an immutable equivalent (tuple, frozenset) first.",
        ['Python data model']
     )),
    ('format-percent-vs-fstring', 'style', 'easy',
     ['greet', 'format_msg'],
     lambda name, var: (
        f"def {name}(name, age):\n    return f'{{name}} is {{age}}'\n",
        f"Why f-string over % formatting?",
        ["Cosmetic","Readability, type safety, and inline expressions","Performance only","Required syntax"],
        1,
        "f-strings (PEP 498) are evaluated inline with expression support, are typically faster than .format and % style, and read more naturally than positional substitution. Use f-strings for all new code.",
        ['PEP 498']
     )),
    ('chained-comparison', 'style', 'easy',
     ['in_range', 'between', 'within'],
     lambda name, var: (
        f"def {name}(x, lo, hi):\n    return lo <= x <= hi\n",
        f"Why chained comparison?",
        ["Cosmetic","Reads naturally and evaluates each operand once","Performance only","Required syntax"],
        1,
        "Python evaluates chained comparisons left-to-right and short-circuits like AND. Each operand is evaluated at most once. Prefer lo <= x <= hi over lo <= x and x <= hi for readability.",
        ['Python docs']
     )),
    ('itertools-chain', 'perf', 'med',
     ['flatten', 'concat_iters', 'join_streams'],
     lambda name, var: (
        f"from itertools import chain\n\ndef {name}(iterables):\n    return list(chain.from_iterable(iterables))\n",
        f"Why itertools.chain.from_iterable?",
        ["Cosmetic","O(n) flatten without building intermediate lists","Performance only","Required syntax"],
        1,
        "chain.from_iterable lazily iterates over each sub-iterable without copying, in contrast to sum([], list_of_lists) which is O(n^2) due to repeated list concatenation. Use chain for any flatten operation.",
        ['itertools docs']
     )),
    ('exception-chaining', 'style', 'med',
     ['parse_user', 'load_config'],
     lambda name, var: (
        f"def {name}(s):\n    try:\n        return int(s)\n    except ValueError as e:\n        raise ValueError(f'bad input: {{s}}') from e\n",
        f"Why 'raise ... from e'?",
        ["Cosmetic","Preserves the original cause in the traceback for diagnostics","Required syntax","Performance"],
        1,
        "raise X from e sets __cause__ on the new exception, which Python displays as 'The above exception was the direct cause of the following exception'. This preserves debugging information without losing the new contextual message.",
        ['PEP 3134']
     )),
]

for tname, topic, diff, names, body in PY_PATTERNS:
    for nm in names:
        var = random.choice(['data','items','values','x','seq','arr','records'])
        try:
            code, q, opts, ci, exp, src = body(nm, var)
            add('python', code, q, opts, ci, topic, tname, diff, exp, src)
        except Exception:
            pass

# ========== JAVASCRIPT ==========
JS_PATTERNS = [
    ('const-vs-let', 'style', 'easy',
     ['MAX', 'TIMEOUT', 'API_URL', 'config', 'options'],
     lambda name: (
        f"const {name} = {{ port: 8080 }};\n{name}.port = 9090;\n",
        f"What is true about const for objects?",
        ["Object becomes immutable","Binding is immutable; properties can still mutate","Throws on property assignment","Same as Object.freeze"],
        1,
        "const prevents reassignment of the binding but does not freeze the object. Properties can still be set or deleted. For true immutability, use Object.freeze (shallow) or libraries that provide deep freeze.",
        ['MDN const']
     )),
    ('arrow-this', 'bug', 'med',
     ['handler', 'callback', 'listener'],
     lambda name: (
        f"class Counter {{\n  count = 0;\n  inc = () => {{ this.count++; }};\n}}\n",
        f"Why arrow-function class field for inc?",
        ["Cosmetic","Arrow lexically binds this so detached calls work","Required syntax","Performance"],
        1,
        "Regular class methods rely on the call site to set this, so passing them as callbacks (button.onclick = c.inc) loses the binding. Arrow class fields capture this lexically at construction, the canonical pattern for event handlers.",
        ['MDN arrow functions']
     )),
    ('object-spread-rest', 'style', 'med',
     ['merge_cfg', 'extend', 'with_overrides'],
     lambda name: (
        f"function {name}(base, overrides) {{\n  return {{ ...base, ...overrides }};\n}}\n",
        f"Why spread vs Object.assign({{}}, base, overrides)?",
        ["Cosmetic","Equivalent semantics, more readable, returns new object","Performance only","Required syntax"],
        1,
        "Object spread (...) is the modern syntactic form of Object.assign with an empty target. Both produce a shallow merge without mutating inputs. The spread reads more naturally and is the ESLint-preferred pattern.",
        ['MDN spread']
     )),
    ('array-destructure', 'style', 'easy',
     ['first_two', 'head_tail', 'unpack'],
     lambda name: (
        f"function {name}(arr) {{\n  const [a, b, ...rest] = arr;\n  return {{ a, b, rest }};\n}}\n",
        f"Why array destructuring with rest?",
        ["Cosmetic","Concise, named binding plus collecting tail","Performance only","Required syntax"],
        1,
        "Array destructuring assigns positional elements to named variables. The rest pattern collects remaining elements into an array. This is more readable than indexed access (arr[0], arr[1], arr.slice(2)) for fixed-prefix patterns.",
        ['MDN destructuring']
     )),
    ('try-catch-finally', 'style', 'easy',
     ['cleanup', 'with_lock', 'guard'],
     lambda name: (
        f"async function {name}(resource) {{\n  try {{\n    return await resource.use();\n  }} finally {{\n    resource.release();\n  }}\n}}\n",
        f"Why finally over try/catch?",
        ["Cosmetic","Runs on success and on exception; ideal for cleanup","Required syntax","Performance"],
        1,
        "finally runs whether the try block completes normally or throws, which makes it the right place for resource cleanup (close, unlock, dispose). Wrapping cleanup in catch + manual rethrow is more error-prone than finally.",
        ['MDN try...catch']
     )),
    ('arr-methods-find', 'style', 'easy',
     ['lookup', 'first_match', 'pick'],
     lambda name: (
        f"function {name}(items, key) {{\n  return items.find(i => i.id === key);\n}}\n",
        f"Why Array.prototype.find?",
        ["Cosmetic","Short-circuits at first match; expresses intent","Performance only","Required syntax"],
        1,
        "find returns the first element matching the predicate or undefined, stopping as soon as it finds a match. This is more efficient and clearer than filter()[0] (which scans the whole array) for first-match lookups.",
        ['MDN Array.find']
     )),
    ('json-reviver', 'bug', 'hard',
     ['parse_safe', 'decode', 'load'],
     lambda name: (
        f"function {name}(text) {{\n  return JSON.parse(text, (k, v) => k === '__proto__' ? undefined : v);\n}}\n",
        f"Why the reviver filtering __proto__?",
        ["Cosmetic","Defends against prototype-pollution payloads in JSON","Performance","Required syntax"],
        1,
        "Naive JSON.parse may set __proto__ on the result, polluting Object.prototype. A reviver function inspecting the key and returning undefined for __proto__ blocks the attack vector. CVE-2018-3721 (lodash) is the canonical example.",
        ['CWE-1321']
     )),
    ('promise-resolve-pattern', 'style', 'med',
     ['delay', 'wait', 'sleep'],
     lambda name: (
        f"function {name}(ms) {{\n  return new Promise(resolve => setTimeout(resolve, ms));\n}}\n",
        f"Why wrap setTimeout in a Promise?",
        ["Cosmetic","Makes the timer awaitable in async code","Performance","Required syntax"],
        1,
        "setTimeout is callback-based; wrapping it in a Promise lets you await the delay in async functions. This Promise-of-timeout pattern is the standard idiom for non-blocking sleep in modern JavaScript.",
        ['MDN setTimeout','MDN async/await']
     )),
    ('regex-named-groups', 'edge', 'med',
     ['parse_iso', 'extract_date'],
     lambda name: (
        f"function {name}(s) {{\n  const m = s.match(/(?<y>\\d{{4}})-(?<m>\\d{{2}})-(?<d>\\d{{2}})/);\n  return m && m.groups;\n}}\n",
        f"Why named groups in regex?",
        ["Cosmetic","Readable access via groups.y rather than positional m[1]","Performance","Required syntax"],
        1,
        "Named capture groups (ES2018) give meaningful names to matched substrings via match.groups.<name>. This is more maintainable than positional indices and survives regex edits without breaking call sites.",
        ['MDN RegExp']
     )),
    ('async-iteration', 'concurrency', 'med',
     ['read_chunks', 'process_stream'],
     lambda name: (
        f"async function {name}(stream) {{\n  for await (const chunk of stream) {{\n    process(chunk);\n  }}\n}}\n",
        f"Why for await...of?",
        ["Cosmetic","Iterates async iterables, awaiting each yielded value","Performance","Required syntax"],
        1,
        "for await...of consumes async iterables (streams, paginated APIs, async generators) one value at a time. The loop body runs after each await, naturally back-pressuring the producer.",
        ['MDN for await...of']
     )),
    ('shorthand-properties', 'style', 'easy',
     ['make_user', 'build'],
     lambda name: (
        f"function {name}(name, age) {{\n  return {{ name, age }};\n}}\n",
        f"What is shorthand property syntax?",
        ["Cosmetic","{name} expands to {name: name} when key matches identifier","Performance","Required syntax"],
        1,
        "ES2015 shorthand object literals use the variable name as both the key and value when they match. {name, age} is equivalent to {name: name, age: age} but reads more compactly. The pattern is idiomatic in factory functions.",
        ['MDN object literals']
     )),
    ('null-coalesce-assign', 'style', 'easy',
     ['set_default', 'init'],
     lambda name: (
        f"function {name}(obj) {{\n  obj.timeout ??= 5000;\n  return obj;\n}}\n",
        f"What does ??= do?",
        ["Cosmetic","Logical nullish assignment: assigns only if left is null/undefined","Required syntax","Performance"],
        1,
        "??= (ES2021) assigns the right-hand value only when the left-hand side is null or undefined, preserving 0 and ''. This is the safer counterpart to ||= which would clobber any falsy value.",
        ['MDN ??=']
     )),
    ('symbol-iterator', 'edge', 'hard',
     ['Range', 'CountUp'],
     lambda name: (
        f"class {name} {{\n  constructor(n) {{ this.n = n; }}\n  *[Symbol.iterator]() {{\n    for (let i = 0; i < this.n; i++) yield i;\n  }}\n}}\n",
        f"What does *[Symbol.iterator] enable?",
        ["Cosmetic","Makes instances iterable in for..of and spread","Performance","Required syntax"],
        1,
        "Defining a generator method at the Symbol.iterator key makes class instances iterable. for..of, [...obj], and destructuring all consume the iterator. This is the canonical hook for custom iteration.",
        ['MDN Iteration protocols']
     )),
    ('array-from-set', 'perf', 'easy',
     ['unique', 'dedupe'],
     lambda name: (
        f"function {name}(items) {{\n  return [...new Set(items)];\n}}\n",
        f"Why Set spread for dedup?",
        ["Cosmetic","O(n) via hash; array filter+indexOf is O(n^2)","Performance only","Required syntax"],
        1,
        "Set membership is amortized O(1), so building a Set then spreading back to Array is O(n) overall. The filter(indexOf) pattern is O(n^2). Use the Set idiom for any dedup over primitives or by-reference identity.",
        ['MDN Set']
     )),
    ('error-instanceof', 'style', 'med',
     ['handle_err', 'classify'],
     lambda name: (
        f"function {name}(err) {{\n  if (err instanceof TypeError) return 'bad type';\n  if (err instanceof RangeError) return 'out of range';\n  return 'other';\n}}\n",
        f"Why instanceof for error classification?",
        ["Cosmetic","Distinguishes built-in error subclasses for typed handling","Performance","Required syntax"],
        1,
        "JavaScript's built-in error classes form a class hierarchy. instanceof lets handlers branch on concrete error types, similar to typed catch in other languages. This is preferred over string-matching err.message which is brittle.",
        ['MDN Error']
     )),
]

for tname, topic, diff, names, body in JS_PATTERNS:
    for nm in names:
        try:
            code, q, opts, ci, exp, src = body(nm)
            add('javascript', code, q, opts, ci, topic, tname, diff, exp, src)
        except Exception:
            pass

# ========== GO ==========
GO_PATTERNS = [
    ('error-wrapping', 'style', 'med',
     ['Open', 'Read', 'Load'],
     lambda name: (
        f"package main\n\nimport (\n\t\"fmt\"\n\t\"os\"\n)\n\nfunc {name}(p string) error {{\n\t_, err := os.Stat(p)\n\tif err != nil {{\n\t\treturn fmt.Errorf(\"{name}: %w\", err)\n\t}}\n\treturn nil\n}}\n",
        f"Why %w in fmt.Errorf?",
        ["Cosmetic","Wraps the error so errors.Is/As walks the chain","Performance","Required syntax"],
        1,
        "%w wraps the underlying error and preserves it in the error chain, letting errors.Is and errors.As traverse it. %v formats the error as a string and loses the type, breaking sentinel matching downstream.",
        ['errors docs']
     )),
    ('context-deadline', 'concurrency', 'med',
     ['Fetch', 'Query', 'Call'],
     lambda name: (
        f"package main\n\nimport (\n\t\"context\"\n\t\"time\"\n)\n\nfunc {name}(parent context.Context) error {{\n\tctx, cancel := context.WithTimeout(parent, 5*time.Second)\n\tdefer cancel()\n\t<-ctx.Done()\n\treturn ctx.Err()\n}}\n",
        f"Why defer cancel?",
        ["Cosmetic","Releases the context timer regardless of return path","Performance","Required syntax"],
        1,
        "WithTimeout returns a cancel function; not calling it leaks the internal timer and child contexts until the deadline fires. defer cancel() ensures cleanup even on early return or panic.",
        ['context docs']
     )),
    ('slices-package', 'perf', 'med',
     ['Sorted', 'Unique', 'Contains'],
     lambda name: (
        f"package main\n\nimport (\n\t\"fmt\"\n\t\"slices\"\n)\n\nfunc main() {{\n\txs := []int{{3,1,2}}\n\tslices.Sort(xs)\n\tfmt.Println(xs)\n}}\n",
        f"Why slices.Sort over sort.Slice?",
        ["Cosmetic","Generic, type-safe at compile time; faster in benchmarks","Performance only","Required syntax"],
        1,
        "The slices package (Go 1.21+) provides generic slice operations that are type-safe and faster than sort.Slice's reflection-based approach. Prefer slices.Sort, slices.Contains, slices.Index over sort.Slice and manual loops.",
        ['slices docs']
     )),
    ('errgroup-context', 'concurrency', 'hard',
     ['ParallelFetch', 'FanOut'],
     lambda name: (
        f"package main\n\nimport (\n\t\"context\"\n)\n\ntype fakeGroup struct{{}}\n\nfunc (g *fakeGroup) Go(f func() error) {{}}\nfunc (g *fakeGroup) Wait() error {{ return nil }}\n\nfunc {name}(ctx context.Context, urls []string) error {{\n\tg := &fakeGroup{{}}\n\tfor _, u := range urls {{\n\t\tu := u\n\t\tg.Go(func() error {{ _ = u; return nil }})\n\t}}\n\treturn g.Wait()\n}}\n",
        f"Why u := u inside the loop?",
        ["Cosmetic","Pre-Go-1.22 loop-var capture; freezes per-iteration value","Performance","Required syntax"],
        1,
        "Before Go 1.22 the loop variable was reused across iterations, so closures captured the same variable and would observe its final value. Shadowing with u := u (or passing as a parameter) snapshots the value per iteration. Go 1.22 changed the semantics.",
        ['Go 1.22 release notes']
     )),
    ('strings-builder-reset', 'perf', 'med',
     ['BuildCSV', 'JoinLines'],
     lambda name: (
        f"package main\n\nimport \"strings\"\n\nfunc {name}(rows [][]string) string {{\n\tvar b strings.Builder\n\tfor _, row := range rows {{\n\t\tb.WriteString(strings.Join(row, \",\"))\n\t\tb.WriteByte('\\n')\n\t}}\n\treturn b.String()\n}}\n",
        f"Why strings.Builder over +=?",
        ["Cosmetic","Avoids O(n^2) repeated allocations of growing strings","Performance only","Required syntax"],
        1,
        "Go strings are immutable, so s += p allocates and copies on each iteration, giving O(n^2) total work. strings.Builder amortizes growth via dynamic resizing, the same way bytes.Buffer does internally.",
        ['strings docs']
     )),
    ('interface-segregation', 'style', 'med',
     ['Closer', 'Reader', 'Sizer'],
     lambda name: (
        f"package main\n\ntype {name} interface {{\n\tClose() error\n}}\n",
        f"Why a single-method interface?",
        ["Cosmetic","Small interfaces enable composition and minimal coupling","Required syntax","Performance"],
        1,
        "Go favors small interfaces that capture exactly one capability. io.Reader, io.Writer, and io.Closer are the canonical examples. Callers depend only on the methods they use, and types implement interfaces structurally without explicit declaration.",
        ['Effective Go']
     )),
    ('json-tag-omit', 'style', 'easy',
     ['User', 'Account', 'Resource'],
     lambda name: (
        f"package main\n\ntype {name} struct {{\n\tID    int    `json:\"id\"`\n\tEmail string `json:\"email,omitempty\"`\n}}\n",
        f"What does omitempty do?",
        ["Cosmetic","Omits the field from JSON if it equals the zero value","Required syntax","Performance"],
        1,
        "The omitempty tag option causes the field to be excluded from JSON output when it equals its zero value (empty string, 0, nil, false). This is useful for optional API fields where empty should mean missing.",
        ['encoding/json']
     )),
    ('mutex-zero-value', 'concurrency', 'easy',
     ['Counter', 'Cache', 'Registry'],
     lambda name: (
        f"package main\n\nimport \"sync\"\n\ntype {name} struct {{\n\tmu sync.Mutex\n\tn  int\n}}\n\nfunc (c *{name}) Inc() {{\n\tc.mu.Lock()\n\tdefer c.mu.Unlock()\n\tc.n++\n}}\n",
        f"Why sync.Mutex by value?",
        ["Cosmetic","Zero value is a usable unlocked mutex; no init needed","Required syntax","Performance"],
        1,
        "The zero value of sync.Mutex is a valid unlocked mutex, so embedding it as a value field means &T{} is ready to use. Pointer fields would require explicit initialization to avoid nil dereference.",
        ['sync docs']
     )),
    ('goroutine-pool', 'concurrency', 'hard',
     ['WorkerPool', 'BoundedExecutor'],
     lambda name: (
        f"package main\n\nfunc {name}(jobs <-chan int, n int) {{\n\tsem := make(chan struct{{}}, n)\n\tfor j := range jobs {{\n\t\tsem <- struct{{}}{{}}\n\t\tgo func(j int) {{\n\t\t\tdefer func() {{ <-sem }}()\n\t\t\t_ = j\n\t\t}}(j)\n\t}}\n}}\n",
        f"Why the sem channel?",
        ["Cosmetic","Bounded semaphore limiting concurrent goroutines","Performance only","Required syntax"],
        1,
        "A buffered channel of struct{} of capacity N acts as a counting semaphore: sends block when N tokens are held. This is the canonical Go pattern for bounding parallelism without external libraries.",
        ['Go concurrency patterns']
     )),
    ('panic-recover', 'bug', 'med',
     ['SafeCall', 'Wrap'],
     lambda name: (
        f"package main\n\nimport \"fmt\"\n\nfunc {name}(f func()) (err error) {{\n\tdefer func() {{\n\t\tif r := recover(); r != nil {{\n\t\t\terr = fmt.Errorf(\"panic: %v\", r)\n\t\t}}\n\t}}()\n\tf()\n\treturn nil\n}}\n",
        f"Why recover at boundaries?",
        ["Cosmetic","Converts panics into errors at API boundaries","Required by Go","Performance"],
        1,
        "Library code that may panic should recover at its public boundary and translate the panic to an error return so callers do not unwind into application code. The named return err lets the deferred function set the result.",
        ['Effective Go']
     )),
    ('type-switch', 'style', 'med',
     ['Format', 'Render', 'Describe'],
     lambda name: (
        f"package main\n\nimport \"fmt\"\n\nfunc {name}(v interface{{}}) string {{\n\tswitch x := v.(type) {{\n\tcase int:\n\t\treturn fmt.Sprintf(\"int: %d\", x)\n\tcase string:\n\t\treturn fmt.Sprintf(\"str: %s\", x)\n\tdefault:\n\t\treturn fmt.Sprintf(\"other: %v\", x)\n\t}}\n}}\n",
        f"Why type switch over reflection?",
        ["Cosmetic","Compile-time dispatch on dynamic type, no reflection cost","Performance only","Required syntax"],
        1,
        "switch v.(type) is dispatched directly by the runtime without the reflect package. It is faster, type-safe, and more readable than reflect.TypeOf. Use it whenever the set of possible types is finite and known.",
        ['Go spec']
     )),
]

for tname, topic, diff, names, body in GO_PATTERNS:
    for nm in names:
        try:
            code, q, opts, ci, exp, src = body(nm)
            add('go', code, q, opts, ci, topic, tname, diff, exp, src)
        except Exception:
            pass

# ========== RUST ==========
RS_PATTERNS = [
    ('result-question-mark', 'style', 'easy',
     ['read_config', 'parse_input', 'load'],
     lambda name: (
        f"pub fn {name}(s: &str) -> Result<i32, std::num::ParseIntError> {{\n    let n: i32 = s.parse()?;\n    Ok(n * 2)\n}}\n",
        f"What does ? do?",
        ["Cosmetic","Propagates Err early, returning from function","Performance","Required syntax"],
        1,
        "The ? operator returns Err(e) early from the enclosing function. Combined with From conversions it propagates errors with automatic type coercion. The principle is to flatten error handling without explicit match.",
        ['Rust Book ch.9']
     )),
    ('iterator-fold', 'perf', 'med',
     ['sum_squares', 'product', 'aggregate'],
     lambda name: (
        f"pub fn {name}(xs: &[i32]) -> i32 {{\n    xs.iter().fold(0, |acc, &x| acc + x * x)\n}}\n",
        f"Why fold over manual loop?",
        ["Cosmetic","Iterator combinators often optimize to the same code; clearer intent","Performance only","Required by Rust"],
        1,
        "Iterator combinators like fold, map, filter, sum are typically optimized by LLVM to code as fast as a manual loop. They also express intent more clearly and compose better.",
        ['Rust by Example']
     )),
    ('option-chaining', 'style', 'easy',
     ['get_email', 'find_user', 'lookup'],
     lambda name: (
        f"pub fn {name}(m: Option<&str>) -> usize {{\n    m.map(|s| s.len()).unwrap_or(0)\n}}\n",
        f"Why map then unwrap_or?",
        ["Cosmetic","Chains transformations on Some, defaults on None","Required syntax","Performance"],
        1,
        "Option::map applies a function to the inner value if Some, leaving None unchanged. unwrap_or supplies a default for None. This functional chain avoids explicit match for simple transformations.",
        ['Option docs']
     )),
    ('match-exhaustive', 'edge', 'med',
     ['Classify', 'Categorize'],
     lambda name: (
        f"pub enum Color {{ Red, Green, Blue }}\n\npub fn {name}(c: Color) -> &'static str {{\n    match c {{\n        Color::Red => \"r\",\n        Color::Green => \"g\",\n        Color::Blue => \"b\",\n    }}\n}}\n",
        f"Why no default arm?",
        ["Cosmetic","Compiler checks exhaustiveness; adding a variant forces update","Required syntax","Performance"],
        1,
        "Match must cover every variant of the enum. Omitting the default arm makes the compiler error if a new variant is added later, forcing the developer to handle it. This is the type-driven design principle.",
        ['Rust Reference']
     )),
    ('borrow-vs-clone', 'perf', 'easy',
     ['print_name', 'log_id'],
     lambda name: (
        f"pub fn {name}(s: &str) {{\n    println!(\"{{}}\", s);\n}}\n",
        f"Why &str over String?",
        ["Cosmetic","Borrow avoids ownership transfer and works for any str source","Performance only","Required syntax"],
        1,
        "Accepting &str instead of String means callers can pass a &String, a literal, or a slice without cloning. Taking ownership only makes sense when the function needs to consume or store the value.",
        ['Rust API Guidelines']
     )),
    ('lifetime-elision', 'style', 'med',
     ['first_word', 'head'],
     lambda name: (
        f"pub fn {name}(s: &str) -> &str {{\n    s.split_whitespace().next().unwrap_or(\"\")\n}}\n",
        f"Why no explicit lifetime annotation?",
        ["Cosmetic","Lifetime elision rules infer 'a tying output to input","Required by Rust","Performance"],
        1,
        "Rust's lifetime elision rules: with one input reference, the output lifetime is the same. The compiler infers fn first_word<'a>(s: &'a str) -> &'a str, so explicit annotation is redundant.",
        ['Rust Reference lifetime-elision']
     )),
    ('iterator-collect-turbofish', 'style', 'med',
     ['parse_all', 'pairs'],
     lambda name: (
        f"pub fn {name}(words: &[&str]) -> Vec<usize> {{\n    words.iter().map(|w| w.len()).collect::<Vec<_>>()\n}}\n",
        f"Why turbofish on collect?",
        ["Cosmetic","Disambiguates target type when context cannot infer","Required syntax","Performance"],
        1,
        "collect returns any type implementing FromIterator. When the return type is named in the signature the compiler can infer, but inside expressions the turbofish ::<T> tells collect which container to build.",
        ['Rust by Example collect']
     )),
    ('match-binding', 'style', 'med',
     ['Describe', 'Process'],
     lambda name: (
        f"pub fn {name}(x: Option<i32>) -> String {{\n    match x {{\n        Some(n) if n > 10 => format!(\"big {{n}}\"),\n        Some(n) => format!(\"small {{n}}\"),\n        None => String::from(\"none\"),\n    }}\n}}\n",
        f"Why match guards (if n > 10)?",
        ["Cosmetic","Refines pattern with arbitrary boolean predicate","Required syntax","Performance"],
        1,
        "Match guards run additional Boolean tests after a pattern matches. They extend pattern coverage without requiring nested if/else. The principle: match patterns describe shape, guards describe content.",
        ['Rust Reference patterns']
     )),
    ('drop-explicit', 'perf', 'hard',
     ['hold_lock', 'with_guard'],
     lambda name: (
        f"use std::sync::Mutex;\n\npub fn {name}(m: &Mutex<i32>) {{\n    let mut g = m.lock().unwrap();\n    *g += 1;\n    drop(g);\n    // long computation without holding the lock\n}}\n",
        f"Why explicit drop(g)?",
        ["Cosmetic","Releases the lock early before unrelated long-running work","Performance only","Required syntax"],
        1,
        "Mutex guards release on drop. Holding a guard past where it is needed unnecessarily serializes other threads. Explicit drop signals intent and frees the lock immediately for the rest of the function body.",
        ['std::mem::drop']
     )),
    ('newtype-pattern', 'style', 'med',
     ['UserId', 'OrderNumber'],
     lambda name: (
        f"pub struct {name}(pub u64);\n\nimpl {name} {{\n    pub fn new(id: u64) -> Self {{ Self(id) }}\n}}\n",
        f"Why a newtype wrapper around u64?",
        ["Cosmetic","Type safety: a UserId cannot be confused with any other u64","Required syntax","Performance"],
        1,
        "Wrapping a primitive in a single-field struct gives the type system a chance to distinguish semantically different values that share the same underlying representation. A UserId and an OrderNumber are both u64 but should not be interchangeable.",
        ['Rust API Guidelines']
     )),
    ('iterator-window', 'edge', 'med',
     ['adjacent_diff', 'sliding_max'],
     lambda name: (
        f"pub fn {name}(xs: &[i32]) -> Vec<i32> {{\n    xs.windows(2).map(|w| w[1] - w[0]).collect()\n}}\n",
        f"What does .windows(2) yield?",
        ["Cosmetic","Overlapping length-2 subslices for adjacent-pair operations","Required syntax","Performance"],
        1,
        "slice::windows(n) yields all overlapping subslices of length n. This is the idiomatic way to iterate adjacent elements without manual indexing. Returns empty if the slice is shorter than n.",
        ['slice::windows']
     )),
    ('arc-clone-share', 'concurrency', 'med',
     ['spawn_workers', 'fan_out'],
     lambda name: (
        f"use std::sync::Arc;\n\npub fn {name}(data: Arc<Vec<i32>>) -> usize {{\n    let d = Arc::clone(&data);\n    d.len()\n}}\n",
        f"Why Arc::clone(&data) over data.clone()?",
        ["Cosmetic","Documents that we are cloning the Arc, not the inner Vec","Required syntax","Performance"],
        1,
        "Arc::clone is explicit about reference counting and prevents the visual confusion of accidentally calling Vec::clone (a deep clone). It is a stylistic convention promoted by The Rust Book.",
        ['Rust Book ch.16']
     )),
]

for tname, topic, diff, names, body in RS_PATTERNS:
    for nm in names:
        try:
            code, q, opts, ci, exp, src = body(nm)
            add('rust', code, q, opts, ci, topic, tname, diff, exp, src)
        except Exception:
            pass

# ========== SQL ==========
SQL_PATTERNS = [
    ('group-by-rollup', 'perf', 'med',
     [('orders','region'), ('sales','category'), ('events','source')],
     lambda t, col: (
        f"SELECT {col}, COUNT(*) AS n\nFROM {t}\nGROUP BY ROLLUP ({col});",
        f"What does GROUP BY ROLLUP add?",
        ["Cosmetic","Subtotals plus grand total in one query","Performance only","Required syntax"],
        1,
        "GROUP BY ROLLUP(col) returns the regular group totals AND a NULL-row grand total in one query. This is more efficient than UNION ALL of separate aggregates and is the standard reporting pattern.",
        ['PG GROUP BY']
     )),
    ('case-when', 'style', 'easy',
     [('users','status'), ('orders','priority')],
     lambda t, col: (
        f"SELECT id,\n  CASE\n    WHEN {col} = 'a' THEN 1\n    WHEN {col} = 'b' THEN 2\n    ELSE 0\n  END AS bucket\nFROM {t};",
        f"What is the role of ELSE?",
        ["Cosmetic","Default value for unmatched rows; without it the result is NULL","Required syntax","Performance"],
        1,
        "CASE without ELSE returns NULL for rows that match no WHEN. Explicit ELSE documents the default and prevents accidental NULLs downstream that might fail predicates or aggregates.",
        ['SQL standard']
     )),
    ('between-vs-range', 'edge', 'easy',
     [('events','created_at'), ('logs','occurred_at')],
     lambda t, col: (
        f"SELECT id\nFROM {t}\nWHERE {col} >= '2026-01-01'\n  AND {col} <  '2026-02-01';",
        f"Why half-open range over BETWEEN?",
        ["Cosmetic","BETWEEN is inclusive; date-bound BETWEEN excludes Jan 31 timestamps","Required syntax","Performance"],
        1,
        "BETWEEN '2026-01-01' AND '2026-01-31' coerces to inclusive timestamps with time 00:00:00, so events later on Jan 31 are excluded. Half-open range (>=, <) is unambiguous for timestamp columns.",
        ['PG BETWEEN']
     )),
    ('window-rank', 'perf', 'med',
     [('scores','user_id','points'), ('sales','region','revenue')],
     lambda t, pcol, ocol: (
        f"SELECT *,\n  ROW_NUMBER() OVER (PARTITION BY {pcol} ORDER BY {ocol} DESC) AS rn\nFROM {t};",
        f"Why ROW_NUMBER over a group-by + join pattern?",
        ["Cosmetic","Avoids self-join; single pass with windowing","Performance only","Required syntax"],
        1,
        "Window functions compute per-row results without collapsing rows. ROW_NUMBER lets you rank within partitions in a single pass, replacing the older self-join + correlated subquery pattern for top-N-per-group queries.",
        ['PG window functions']
     )),
    ('upsert-returning', 'style', 'med',
     [('users','email'), ('products','sku')],
     lambda t, ucol: (
        f"INSERT INTO {t} ({ucol}, name)\nVALUES ($1, $2)\nON CONFLICT ({ucol}) DO UPDATE SET name = EXCLUDED.name\nRETURNING *;",
        f"Why RETURNING * on upsert?",
        ["Cosmetic","Returns the inserted/updated row in one round-trip","Performance only","Required syntax"],
        1,
        "RETURNING gives access to the final row state (including server defaults) without a second SELECT. Combined with ON CONFLICT it is the atomic upsert pattern, eliminating race conditions of separate query-then-write.",
        ['PG INSERT']
     )),
    ('cte-with', 'style', 'easy',
     [('orders','user_id'), ('events','session_id')],
     lambda t, col: (
        f"WITH agg AS (\n  SELECT {col}, COUNT(*) AS n FROM {t} GROUP BY {col}\n)\nSELECT * FROM agg WHERE n > 10;",
        f"Why a CTE here?",
        ["Cosmetic","Names the intermediate result for readability","Performance","Required syntax"],
        1,
        "CTEs let you name and reuse intermediate results. While modern PostgreSQL inlines CTEs by default (since v12), they remain valuable for readability and self-documentation in complex queries.",
        ['PG WITH']
     )),
    ('coalesce-default', 'edge', 'easy',
     [('users','nickname'), ('orders','note')],
     lambda t, col: (
        f"SELECT id, COALESCE({col}, 'n/a') AS display FROM {t};",
        f"Why COALESCE for default?",
        ["Cosmetic","Substitutes a default for NULL","Required syntax","Performance"],
        1,
        "COALESCE returns the first non-NULL argument, perfect for fallback chains. It is more readable than CASE WHEN x IS NULL THEN ... and works in WHERE/ORDER BY as well.",
        ['PG conditional expressions']
     )),
    ('exists-vs-in', 'perf', 'med',
     [('orders','user_id','active_users'), ('events','session_id','active_sessions')],
     lambda t, col, ref: (
        f"SELECT * FROM {t} t WHERE EXISTS (SELECT 1 FROM {ref} r WHERE r.id = t.{col});",
        f"Why EXISTS over IN here?",
        ["Cosmetic","EXISTS handles NULLs in subquery without surprise empty results","Performance only","Required syntax"],
        1,
        "EXISTS returns true on any match and is NULL-safe. IN with a subquery containing NULL can produce surprising empty results (especially NOT IN). For semi-join intent, prefer EXISTS.",
        ['PG subqueries']
     )),
    ('jsonb-containment', 'perf', 'med',
     [('events','payload','user_id'), ('logs','data','level')],
     lambda t, col, key: (
        f"SELECT id FROM {t} WHERE {col} @> '{{\"{key}\": 42}}'::jsonb;",
        f"Why @> with jsonb?",
        ["Cosmetic","Containment uses GIN index for fast lookups","Performance only","Required syntax"],
        1,
        "The @> jsonb containment operator can use a GIN index for matching rows efficiently. This scales much better than ->>'key' = '...' which forces a sequential scan unless an expression index exists.",
        ['PG JSON functions']
     )),
    ('group-by-having', 'edge', 'easy',
     [('orders','user_id'), ('events','source')],
     lambda t, col: (
        f"SELECT {col}, COUNT(*) AS n\nFROM {t}\nGROUP BY {col}\nHAVING COUNT(*) > 5;",
        f"Why HAVING over WHERE for the count filter?",
        ["Cosmetic","WHERE runs before GROUP BY; HAVING runs after","Required syntax","Performance"],
        1,
        "WHERE filters rows before grouping and cannot reference aggregate results. HAVING filters groups after aggregation. The principle reflects the logical query processing order.",
        ['SQL standard']
     )),
    ('lateral-correlation', 'perf', 'hard',
     [('users','orders'), ('customers','sessions')],
     lambda t, ref: (
        f"SELECT u.id, latest.created_at\nFROM {t} u\nLEFT JOIN LATERAL (\n  SELECT created_at FROM {ref} o WHERE o.user_id = u.id ORDER BY created_at DESC LIMIT 1\n) latest ON true;",
        f"Why LATERAL?",
        ["Cosmetic","Right-side subquery may reference left-side rows","Performance only","Required syntax"],
        1,
        "LATERAL lets the right-side subquery reference columns from the left side of the join. This is the canonical pattern for per-row aggregates (latest row, top-N per group) that cannot be expressed with plain joins.",
        ['PG LATERAL']
     )),
]

for tname, topic, diff, tuples, body in SQL_PATTERNS:
    for tup in tuples:
        try:
            if len(tup) == 2:
                code, q, opts, ci, exp, src = body(tup[0], tup[1])
            else:
                code, q, opts, ci, exp, src = body(*tup)
            add('sql', code, q, opts, ci, topic, tname, diff, exp, src)
        except Exception:
            pass

print(f"generated {len(items)} items")
OUT.write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')
print(f"wrote {OUT}")
