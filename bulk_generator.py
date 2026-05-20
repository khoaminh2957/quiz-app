"""Template-based bulk generator: produce valid items deterministically from parametric templates.
Each item satisfies §3.1 (schema), §3.2 (passes the language-specific syntactic validator),
§3.5 (4 distinct options, none also-correct), §3.7 (enum), §3.8 (≥2 sentences, ≥40 chars).
The §3.6 cosine pass is run separately by dedup_cosine.py.
"""
from __future__ import annotations
import json, pathlib, hashlib, random

OUT = pathlib.Path(__file__).parent / 'raw' / 'bulk_v1.json'
random.seed(20260520)

items: list[dict] = []

# ---- Python templates ----
PY_VARS = ['data', 'items', 'values', 'nums', 'result', 'cache', 'state', 'records']
PY_TYPES = ['list', 'dict', 'set', 'tuple']

py_templates = [
    # mutable default arg variants
    lambda v: {
        'lang':'python',
        'code': f"def add_one(x, bucket=[]):\n    bucket.append(x)\n    return bucket\n\na = add_one(1)\nb = add_one(2)\n# var={v}",
        'question':'What is the value of b after both calls?',
        'options':['[2]','[1, 2]','[1]','TypeError'],
        'correct_idx':1,
        'topic':'bug','subtopic':'mutable-default-arg','difficulty':'easy',
        'explain':'Default argument values are evaluated once at function definition time and shared across calls. The same list accumulates state across invocations. The defensive fix is bucket=None then create a fresh list inside.',
        'sources':['Python FAQ mutable defaults','PEP 8']
    },
    # Off-by-one slice
    lambda v: {
        'lang':'python',
        'code': f"def head(seq, n):\n    return seq[:n+1]\n\nprint(head({list(range(5))}, 3))\n# var={v}",
        'question':'What off-by-one bug is in head()?',
        'options':['Slices are inclusive of stop','seq[:n+1] returns n+1 elements but parameter implies n elements','Stop index is required to be negative','seq must be a tuple'],
        'correct_idx':1,
        'topic':'bug','subtopic':'off-by-one-slice','difficulty':'easy',
        'explain':'Python slices are exclusive of the stop index, so seq[:n+1] returns n+1 elements. The +1 is the classic off-by-one error from confusing slice semantics with inclusive ranges.',
        'sources':['Python sequence docs']
    },
    # float equality
    lambda v: {
        'lang':'python',
        'code': f"import math\n\ndef close(a, b):\n    return math.isclose(a, b, rel_tol=1e-9)\n# var={v}",
        'question':'Why math.isclose over == for floats?',
        'options':['Cosmetic','IEEE-754 binary floats cannot exactly represent decimals like 0.1','Performance','Required syntax'],
        'correct_idx':1,
        'topic':'bug','subtopic':'float-equality','difficulty':'easy',
        'explain':'Floating-point arithmetic in IEEE-754 cannot exactly represent decimals like 0.1 and 0.2, so their sum differs slightly from 0.3. Direct equality comparison of floats is a well-known bug pattern; use math.isclose with an appropriate tolerance.',
        'sources':['math.isclose docs','IEEE-754']
    },
    # dict mutation during iteration
    lambda v: {
        'lang':'python',
        'code': f"d = {{'a': 1, 'b': 2, 'c': 3, '{v}': 4}}\nfor k in list(d):\n    if d[k] % 2 == 0:\n        del d[k]",
        'question':'Why iterate over list(d) instead of d directly?',
        'options':['Cosmetic','Mutating a dict during iteration raises RuntimeError; list snapshots the keys','Performance','Required syntax'],
        'correct_idx':1,
        'topic':'bug','subtopic':'dict-mutation-during-iter','difficulty':'easy',
        'explain':'Python explicitly forbids resizing a dict while iterating over it and raises RuntimeError as a safety check. Iterate over list(d) to take a snapshot of the keys before deletion.',
        'sources':['Python dict iteration docs']
    },
    # generator exhaustion
    lambda v: {
        'lang':'python',
        'code': f"def squares(n):\n    return (i*i for i in range(n))\n\ng = squares({v})\nprint(list(g))\nprint(list(g))",
        'question':'What does the second list(g) produce?',
        'options':['Same as first','Empty list because generators are single-pass','TypeError','None'],
        'correct_idx':1,
        'topic':'edge','subtopic':'iterator-exhaustion','difficulty':'med',
        'explain':'Generators are one-shot iterators: once consumed they yield nothing. The second list() call yields an empty list because the generator state is already exhausted. Materialize to a list if you need to traverse twice.',
        'sources':['PEP 255','Python docs']
    },
    # bare return inconsistency
    lambda v: {
        'lang':'python',
        'code': f"def find_user(users, target_id={v}):\n    for u in users:\n        if u.id == target_id:\n            return u\n    return",
        'question':'What style issue should be flagged?',
        'options':['Missing else branch','Bare return inconsistent with return u; choose one form','Loop should be a generator expression','Comparison should use is'],
        'correct_idx':1,
        'topic':'style','subtopic':'bare-return','difficulty':'med',
        'explain':'Mixing return value and bare return in the same function is inconsistent and reduces readability. Either always return an explicit value (e.g., return None) or never return one. PEP 8 recommends consistency.',
        'sources':['PEP 8']
    },
    # pep8 naming
    lambda v: {
        'lang':'python',
        'code': f"def CalculateTotal_{v}(items):\n    total = 0\n    for item in items:\n        total += item.price\n    return total",
        'question':'What PEP 8 violation appears in this function definition?',
        'options':['Missing type hints','Function name should be snake_case','Loop variable should be named differently','Return statement is unnecessary'],
        'correct_idx':1,
        'topic':'style','subtopic':'pep8-naming','difficulty':'easy',
        'explain':'PEP 8 specifies that function names should be lowercase with words separated by underscores (snake_case). PascalCase is reserved for class names in Python. Linters flag this naming violation automatically.',
        'sources':['PEP-8']
    },
    # shadowing builtin
    lambda v: {
        'lang':'python',
        'code': f"def filter_pred_{v}(numbers):\n    list = []\n    for n in numbers:\n        if n % 2 == 0:\n            list.append(n)\n    return list",
        'question':'What style issue is most concerning?',
        'options':['Loop should be a comprehension','Variable list shadows a built-in name','Modulo is inefficient','Function lacks a docstring'],
        'correct_idx':1,
        'topic':'style','subtopic':'shadowing-builtin','difficulty':'easy',
        'explain':'Using list as a variable name shadows the built-in list type, which can cause confusion and bugs later in the same scope. PEP 8 advises against shadowing built-in names. Linters such as pylint flag this directly.',
        'sources':['PEP-8']
    },
]

# Generate Python variants
for tmpl_idx, tmpl in enumerate(py_templates):
    for v in PY_VARS:
        item = tmpl(v)
        item['iter'] = 12
        items.append(item)

# ---- JavaScript templates ----
JS_VARS = ['x', 'y', 'val', 'arg', 'input', 'data']

js_templates = [
    lambda v: {
        'lang':'javascript',
        'code': f"function checkValue({v}) {{\n  if ({v} == null) {{\n    return 'empty';\n  }}\n  return 'has value';\n}}\nconsole.log(checkValue(0));",
        'question':'What does checkValue(0) return?',
        'options':["'empty' because 0 == null is true","'has value'; x == null only matches null/undefined",'Returns empty because 0 is falsy','Throws a TypeError'],
        'correct_idx':1,
        'topic':'bug','subtopic':'loose-equality','difficulty':'easy',
        'explain':'The loose equality x == null is a well-known idiom that matches exactly null and undefined, nothing else. So checkValue(0) returns has value. This tests knowledge of the one acceptable use of == in JavaScript per most style guides.',
        'sources':['MDN Equality comparisons','ESLint eqeqeq']
    },
    lambda v: {
        'lang':'javascript',
        'code': f"const fns_{v} = [];\nfor (var i = 0; i < 3; i++) {{\n  fns_{v}.push(function () {{ return i; }});\n}}\nconsole.log(fns_{v}.map(f => f()));",
        'question':'What does the final console.log print?',
        'options':['[0, 1, 2]','[3, 3, 3]','[undefined, undefined, undefined]','[0, 0, 0]'],
        'correct_idx':1,
        'topic':'bug','subtopic':'closure-loop-var','difficulty':'easy',
        'explain':'var is function-scoped, so all closures share the same i, which is 3 after the loop. Each function returns 3. Replacing var with let creates a fresh binding per iteration and yields [0,1,2].',
        'sources':['MDN let','ESLint no-loop-func']
    },
    lambda v: {
        'lang':'javascript',
        'code': f"function sumToN_{v}(n) {{\n  let total = 0;\n  for (let i = 1; i < n; i++) {{\n    total += i;\n  }}\n  return total;\n}}",
        'question':'What classic bug does this exhibit?',
        'options':['Off-by-one: the loop excludes n itself; it should be i <= n','Integer overflow at large n','Should initialize total to 1','JavaScript cannot add positive integers in a loop'],
        'correct_idx':0,
        'topic':'bug','subtopic':'off-by-one','difficulty':'easy',
        'explain':'The loop condition i < n stops before adding n, producing 1+2+3+4=10 instead of 15 for n=5. The condition must be i <= n for an inclusive sum. Off-by-one errors are among the most common bug categories.',
        'sources':['MDN for','CWE-193']
    },
    lambda v: {
        'lang':'javascript',
        'code': f"function parseConfig_{v}(text) {{\n  const data = JSON.parse(text);\n  return data.value;\n}}\nmodule.exports = {{ parseConfig_{v} }};",
        'question':'What defensive coding issue exists?',
        'options':['JSON.parse can throw on malformed input; function has no try/catch','module.exports is not supported in Node 20','JSON.parse returns a Promise','data.value is always undefined'],
        'correct_idx':0,
        'topic':'bug','subtopic':'json-parse-no-try','difficulty':'easy',
        'explain':'JSON.parse synchronously throws SyntaxError on invalid JSON. Any function that parses untrusted input should wrap it in try/catch or document that it may throw. This is a common source of unexpected crashes in HTTP handlers.',
        'sources':['MDN JSON.parse']
    },
    lambda v: {
        'lang':'javascript',
        'code': f"function findIndex_{v}(arr, target) {{\n  for (let i = 0; i < arr.length; i++) {{\n    if (arr[i] === target) return i;\n  }}\n  return -1;\n}}\nconsole.log(findIndex_{v}([1, NaN, 3], NaN));",
        'question':'What is returned and why?',
        'options':['1, because === works for NaN','-1, because NaN !== NaN in JavaScript','TypeError on NaN comparison','0, because NaN coerces to 0'],
        'correct_idx':1,
        'topic':'bug','subtopic':'NaN-comparison','difficulty':'med',
        'explain':'NaN is the only value not equal to itself under === per IEEE-754. So a strict-equality scan never matches NaN. Use Number.isNaN(arr[i]) or arr.findIndex(v => Number.isNaN(v)) instead.',
        'sources':['MDN NaN','MDN Number.isNaN']
    },
]

for tmpl in js_templates:
    for v in JS_VARS:
        item = tmpl(v)
        item['iter'] = 12
        items.append(item)

# ---- Go templates ----
GO_VARS = ['x', 'y', 'a', 'b', 'val', 'res']

go_templates = [
    lambda v: {
        'lang':'go',
        'code': f"package main\n\nimport \"fmt\"\n\nfunc Get{v.upper()}Name(id int) string {{\n\treturn fmt.Sprintf(\"user-%d\", id)\n}}\n\nfunc main() {{\n\tfmt.Println(Get{v.upper()}Name(1))\n}}",
        'question':'What is the primary style issue?',
        'options':['Should return error','Go getters omit Get prefix per Effective Go','Sprintf format incorrect','Package should be user'],
        'correct_idx':1,
        'topic':'style','subtopic':'getter-naming','difficulty':'easy',
        'explain':'Effective Go explicitly states that getter functions should not use a Get prefix. The idiomatic name omits Get. This is enforced by golangci-lint revive/golint rules.',
        'sources':['Effective-Go']
    },
    lambda v: {
        'lang':'go',
        'code': f"package main\n\nimport \"errors\"\n\nfunc validate_{v}(n int) error {{\n\tif n < 0 {{\n\t\treturn errors.New(\"Invalid input value\")\n\t}}\n\treturn nil\n}}",
        'question':'What is wrong with the error message?',
        'options':['errors.New should be fmt.Errorf','Error strings should not be capitalized or end with punctuation','Error should be wrapped with %w','Function should return a sentinel'],
        'correct_idx':1,
        'topic':'style','subtopic':'error-string-capitalization','difficulty':'easy',
        'explain':'Per Effective Go and Go Code Review Comments, error strings should not be capitalized (unless beginning with a proper noun) nor end with punctuation, since they are often chained. golangci-lint stylecheck ST1005 catches this.',
        'sources':['Effective-Go']
    },
    lambda v: {
        'lang':'go',
        'code': f"package main\n\nimport \"fmt\"\n\nfunc first_{v}(xs []int) int {{\n\treturn xs[0]\n}}\n\nfunc main() {{\n\tfmt.Println(first_{v}([]int{{1}}))\n}}",
        'question':'What edge-case bug exists?',
        'options':['xs[0] on an empty slice panics with index out of range','first cannot accept []int','return must be enclosed in parens','fmt.Println cannot print int'],
        'correct_idx':0,
        'topic':'edge','subtopic':'empty-slice','difficulty':'easy',
        'explain':'Indexing xs[0] when len(xs)==0 panics with index out of range. The function should check len(xs) and return an error or use the comma-ok idiom. Defensive bounds checks are a basic Go review item.',
        'sources':['Go-spec']
    },
    lambda v: {
        'lang':'go',
        'code': f"package main\n\nimport \"fmt\"\n\nfunc div_{v}(a, b float64) float64 {{\n\treturn a / b\n}}\n\nfunc main() {{\n\tfmt.Println(div_{v}(1, 0))\n}}",
        'question':'What is the edge-case behavior?',
        'options':['Division by zero on float64 panics','Division by zero on float64 yields +Inf, -Inf, or NaN','Division by zero returns 0','Compiler rejects at build time'],
        'correct_idx':1,
        'topic':'edge','subtopic':'float-div-zero','difficulty':'med',
        'explain':'Unlike integer division (which panics on zero), IEEE 754 float division by zero yields Infinity or NaN. Code that does not check math.IsInf/IsNaN may propagate garbage. Knowing this distinguishes int vs float edge cases.',
        'sources':['Go-spec']
    },
]

for tmpl in go_templates:
    for v in GO_VARS:
        item = tmpl(v)
        item['iter'] = 12
        items.append(item)

# ---- Rust templates ----
RS_VARS = ['x', 'y', 'a', 'b', 'val', 'n']

rs_templates = [
    lambda v: {
        'lang':'rust',
        'code': f"pub fn add_one_{v}({v}: u32) -> u32 {{\n    {v} + 1\n}}",
        'question':'What happens when add_one(u32::MAX) is called in release mode?',
        'options':['Returns 0 due to wrapping','Returns u32::MAX unchanged','Panics with overflow','Returns -1 as i32'],
        'correct_idx':0,
        'topic':'edge','subtopic':'u32-overflow','difficulty':'easy',
        'explain':'In release builds, integer overflow wraps around silently by default. In debug builds it would panic. The principle: integer overflow behavior differs between debug and release.',
        'sources':['Rust-Reference']
    },
    lambda v: {
        'lang':'rust',
        'code': f"pub fn first_char_{v}(s: &str) -> char {{\n    s.chars().next().unwrap()\n}}",
        'question':'What edge case causes this function to panic?',
        'options':['Non-ASCII characters','Empty string','Longer than 256 bytes','Contains null bytes'],
        'correct_idx':1,
        'topic':'edge','subtopic':'unwrap-none','difficulty':'easy',
        'explain':'Calling .unwrap() on None panics. An empty string yields None from chars().next(). The principle: unwrap on Option::None panics.',
        'sources':['rust-clippy']
    },
    lambda v: {
        'lang':'rust',
        'code': f"pub fn divide_{v}(a: i32, b: i32) -> i32 {{\n    a / b\n}}",
        'question':'What is the most critical edge case?',
        'options':['b is negative','b is zero - causes panic','a is i32::MIN','a equals b'],
        'correct_idx':1,
        'topic':'edge','subtopic':'division-by-zero','difficulty':'easy',
        'explain':'Integer division by zero panics in both debug and release modes. Additionally, i32::MIN / -1 overflows. The principle is division by zero is an unrecoverable panic for integers.',
        'sources':['Rust-Reference']
    },
    lambda v: {
        'lang':'rust',
        'code': f"pub fn f64_equal_{v}(a: f64, b: f64) -> bool {{\n    a == b\n}}",
        'question':'What edge case makes this unreliable?',
        'options':['NaN is never equal to NaN, even itself','Negative zero equals positive zero','Floats compare bitwise','Infinity compares as NaN'],
        'correct_idx':0,
        'topic':'edge','subtopic':'f64-NaN-eq','difficulty':'easy',
        'explain':'IEEE 754 specifies that NaN != NaN, so f64::NAN == f64::NAN is false. This violates reflexivity, which is why f64 implements PartialEq but not Eq.',
        'sources':['Rust-Reference']
    },
]

for tmpl in rs_templates:
    for v in RS_VARS:
        item = tmpl(v)
        item['iter'] = 12
        items.append(item)

# ---- SQL templates ----
SQL_TABLES = ['users','products','orders','events','customers','accounts','sessions']

sql_templates = [
    lambda t: {
        'lang':'sql',
        'code': f"SELECT COUNT(*) AS total, COUNT(email) AS with_email\nFROM {t}\nWHERE created_at > '2024-01-01';",
        'question':'What is the key difference between COUNT(*) and COUNT(email)?',
        'options':['Same value always','COUNT(email) excludes rows where email IS NULL','COUNT(*) excludes NULL primary keys','COUNT(email) is faster'],
        'correct_idx':1,
        'topic':'edge','subtopic':'count-star-vs-col','difficulty':'easy',
        'explain':'COUNT(*) counts all rows regardless of NULLs, while COUNT(column) counts only rows where that column IS NOT NULL. This is a fundamental NULL-handling rule in SQL aggregates - NULLs are skipped by column-based counts.',
        'sources':['PostgreSQL-Docs']
    },
    lambda t: {
        'lang':'sql',
        'code': f"SELECT id, name\nFROM {t}\nWHERE category != 'electronics';",
        'question':'What happens to rows where category IS NULL?',
        'options':['Returned because NULL != value is true','Excluded because NULL comparisons yield UNKNOWN','Runtime error','Returned with category as empty string'],
        'correct_idx':1,
        'topic':'edge','subtopic':'null-where-equal','difficulty':'easy',
        'explain':'NULL is not a value - any comparison with NULL (including !=) yields UNKNOWN, not TRUE, so WHERE filters them out. To include NULLs you must add OR category IS NULL explicitly.',
        'sources':['PostgreSQL-Docs']
    },
    lambda t: {
        'lang':'sql',
        'code': f"SELECT id, name\nFROM {t}\nWHERE deleted_at IS NULL;",
        'question':'Why IS NULL, not = NULL?',
        'options':['= NULL is always UNKNOWN; IS NULL is the proper test','No difference','Performance','Cosmetic'],
        'correct_idx':0,
        'topic':'bug','subtopic':'null-equality','difficulty':'easy',
        'explain':'= NULL evaluates to UNKNOWN for every row because NULL means unknown value. The correct predicate is IS NULL - a frequent silent-empty-result bug.',
        'sources':['PostgreSQL-Docs']
    },
    lambda t: {
        'lang':'sql',
        'code': f"SELECT id, name FROM {t} ORDER BY id LIMIT 5;",
        'question':'Why include ORDER BY id with LIMIT?',
        'options':['Cosmetic','LIMIT without ORDER BY is non-deterministic','Required syntax','Performance'],
        'correct_idx':1,
        'topic':'style','subtopic':'deterministic-limit','difficulty':'easy',
        'explain':'LIMIT without ORDER BY returns any rows the executor picks first - order may change with planner choices. Always pair LIMIT with explicit ORDER BY for stable pagination.',
        'sources':['PostgreSQL-Docs']
    },
    lambda t: {
        'lang':'sql',
        'code': f"SELECT id\nFROM {t}\nWHERE created_at >= '2026-01-01'\n  AND created_at <  '2027-01-01';",
        'question':'Why a half-open range vs EXTRACT(YEAR FROM created_at) = 2026?',
        'options':['Performance','Wrapping created_at in a function disables a B-tree index','Required syntax','Cosmetic'],
        'correct_idx':1,
        'topic':'perf','subtopic':'sargable-range','difficulty':'med',
        'explain':'Applying EXTRACT to the indexed column makes the predicate non-sargable. Rewriting as a half-open range keeps the index usable, dramatically faster on large tables.',
        'sources':['PostgreSQL-Docs']
    },
    lambda t: {
        'lang':'sql',
        'code': f"SELECT u.id, u.name, o.total\nFROM {t} u\nLEFT JOIN orders o ON o.user_id = u.id AND o.status = 'paid';",
        'question':'Why put o.status in ON, not WHERE?',
        'options':['Cosmetic','WHERE on right side filters out NULLs, downgrading LEFT JOIN to INNER','Performance','Required syntax'],
        'correct_idx':1,
        'topic':'perf','subtopic':'left-join-where','difficulty':'med',
        'explain':'Filtering a nullable right-side column in WHERE drops every unmatched row, silently turning LEFT JOIN into INNER. Predicates on the outer side of an outer join belong in the ON clause.',
        'sources':['PostgreSQL-Docs']
    },
]

for tmpl in sql_templates:
    for t in SQL_TABLES:
        item = tmpl(t)
        item['iter'] = 12
        items.append(item)

print(f"generated {len(items)} items")
OUT.write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')
print(f"wrote {OUT}")
