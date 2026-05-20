"""Migrate to Python-only + Vietnamese UI.

- Backs up original questions.json -> questions_en_full.json (preserve audit trail).
- Filters to Python only (286 Qs).
- Translates per-Q fields (question/options/explain/learning_objective/metacog_pre/metacog_post/misconception_map)
  via a curated pattern-translation table; leaves `code` and technical identifiers untouched.
- Filters roadmap_perlang.json to Python only.
- Writes vi_translations.json (UI strings) and updates question fields in place.
"""
import json, re, os, tempfile, pathlib, hashlib, shutil
from collections import Counter

ROOT = pathlib.Path(__file__).parent

def atomic_write(path, content):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try: os.unlink(tmp)
            except: pass

# ---- Q-text translation tables (deterministic) ----
# Mapping common question stems / option phrases / explain framings to Vietnamese.

QUESTION_PHRASES = [
    (r"^What does this code output\??$", "Đoạn code này in ra gì?"),
    (r"^What does this code do\??$", "Đoạn code này làm gì?"),
    (r"^What does this code print\??$", "Đoạn code này in ra gì?"),
    (r"^What is the output\??$", "Output là gì?"),
    (r"^What does the (?:final |last )?print output\??$", "Lệnh print cuối cùng in ra gì?"),
    (r"^What will (?:this|the code) print\??$", "Code này sẽ in ra gì?"),
    (r"^What is printed\??$", "Cái gì được in ra?"),
    (r"^What happens when (?:this code|the code) (?:is run|runs)\??$", "Chuyện gì xảy ra khi chạy đoạn code này?"),
    (r"^What error does this raise\??$", "Đoạn code này raise lỗi gì?"),
    (r"^What error is raised\??$", "Lỗi nào được raise?"),
    (r"^What exception is raised\??$", "Exception nào được raise?"),
    (r"^Which option is correct\??$", "Đáp án nào đúng?"),
    (r"^Which (?:line|option|statement) (?:contains|has) the bug\??$", "Dòng/lệnh nào chứa lỗi?"),
    (r"^Where is the bug\??$", "Lỗi nằm ở đâu?"),
    (r"^What is the bug\??$", "Bug là gì?"),
    (r"^What is wrong with this code\??$", "Đoạn code này sai chỗ nào?"),
    (r"^Which (?:option|choice) (?:correctly )?(?:fixes|fix) the bug\??$", "Lựa chọn nào sửa được bug?"),
    (r"^Which is the most idiomatic (?:Python )?(?:version|way)\??$", "Cách viết nào idiomatic nhất trong Python?"),
    (r"^Which is the most Pythonic (?:way|version)\??$", "Cách viết nào Pythonic nhất?"),
    (r"^Which (?:option )?has the (?:best|lowest|highest) (?:time )?complexity\??$", "Lựa chọn nào có độ phức tạp tốt nhất?"),
    (r"^What is the time complexity\??$", "Độ phức tạp thời gian là bao nhiêu?"),
    (r"^What is the space complexity\??$", "Độ phức tạp bộ nhớ là bao nhiêu?"),
    (r"^Which (?:is|option is) the security (?:flaw|issue|vulnerability)\??$", "Lỗ hổng bảo mật ở đâu?"),
    (r"^What security (?:flaw|issue) (?:does this code have|is present)\??$", "Đoạn code này có lỗ hổng bảo mật gì?"),
    (r"^What concurrency (?:issue|bug|hazard) (?:is present|does this have)\??$", "Đoạn code này có vấn đề concurrency gì?"),
    (r"^What style (?:violation|issue) is present\??$", "Vi phạm style nào ở đây?"),
    (r"^Which PEP 8 (?:violation|rule) (?:appears|is violated)\??$", "Vi phạm PEP 8 nào xuất hiện?"),
    (r"^What PEP 8 violation appears in this function definition\??$", "Định nghĩa function này vi phạm PEP 8 ở đâu?"),
    (r"^Which (?:test case|input) (?:will|would) (?:trigger|cause) the (?:bug|error|edge case)\??$", "Test case nào sẽ trigger bug?"),
    (r"^What happens with empty input\??$", "Chuyện gì xảy ra với input rỗng?"),
    (r"^What is the value of `?(\w+)`? after the code runs\??$", r"Giá trị của `\1` sau khi chạy là gì?"),
    (r"^What is returned\??$", "Cái gì được return?"),
    (r"^What does (\w+)\(\) return\??$", r"Hàm \1() return gì?"),
    (r"^What is the result\??$", "Kết quả là gì?"),
    (r"^Which is the correct fix\??$", "Sửa thế nào là đúng?"),
]

# Common option phrases — translate the common Python-output / error patterns
OPTION_PHRASES = [
    (r"^Raises (\w+Error)$", r"Raises \1"),  # keep error class English
    (r"^Raises (\w+Error): (.+)$", r"Raises \1: \2"),
    (r"^Returns (.+)$", r"Trả về \1"),
    (r"^Prints (.+)$", r"In ra \1"),
    (r"^No output$", "Không có output"),
    (r"^Nothing$", "Không in gì"),
    (r"^Empty (?:list|string|dict|set)$", "Rỗng"),
    (r"^True$", "True"),
    (r"^False$", "False"),
    (r"^None$", "None"),
    (r"^Crashes$", "Crash"),
    (r"^Infinite loop$", "Vòng lặp vô hạn"),
    (r"^Hangs$", "Treo"),
    (r"^Undefined behavior$", "Hành vi không xác định"),
    (r"^Implementation defined$", "Tuỳ implementation"),
    (r"^Missing type hints on parameters$", "Thiếu type hints cho tham số"),
    (r"^Missing docstring$", "Thiếu docstring"),
    (r"^Function name not in snake_case$", "Tên function không theo snake_case"),
    (r"^Function name not snake_case$", "Tên function không phải snake_case"),
    (r"^Line too long$", "Dòng quá dài"),
    (r"^Inconsistent indentation$", "Indentation không nhất quán"),
    (r"^Use of mutable default argument$", "Dùng mutable default argument"),
    (r"^Mutable default argument$", "Mutable default argument"),
    (r"^Late-binding closure$", "Late-binding closure"),
    (r"^Off-by-one error$", "Off-by-one error"),
]

# Explain field — translate common framings (sentence-level)
EXPLAIN_PATTERNS = [
    (r"\bThis code\b", "Đoạn code này"),
    (r"\bThe code\b", "Đoạn code"),
    (r"\bThe correct answer is\b", "Đáp án đúng là"),
    (r"\bThe issue is\b", "Vấn đề là"),
    (r"\bThe bug is\b", "Bug là"),
    (r"\bNote that\b", "Lưu ý rằng"),
    (r"\bRemember that\b", "Nhớ rằng"),
    (r"\bBecause\b", "Bởi vì"),
    (r"\bbecause\b", "bởi vì"),
    (r"\bIn Python\b", "Trong Python"),
    (r"\bin Python\b", "trong Python"),
    (r"\bThis is a (?:known )?(\w+) (?:bug|issue|pattern)\b", r"Đây là pattern \1"),
    (r"\bThis violates\b", "Điều này vi phạm"),
    (r"\bThe function\b", "Function"),
    (r"\bThe variable\b", "Biến"),
    (r"\bA review skill\b", "Kỹ năng review"),
    (r"\bbug fix review skill\b", "kỹ năng review sửa bug"),
    (r"\bsecurity review skill\b", "kỹ năng review bảo mật"),
    (r"\bperformance review skill\b", "kỹ năng review performance"),
    (r"\bstyle review skill\b", "kỹ năng review style"),
    (r"\bedge case review skill\b", "kỹ năng review edge case"),
    (r"\bconcurrency review skill\b", "kỹ năng review concurrency"),
    (r"\bshould be\b", "nên là"),
    (r"\bmust be\b", "phải là"),
    (r"\bis used to\b", "được dùng để"),
    (r"\bis evaluated\b", "được đánh giá"),
    (r"\bspecifies that\b", "quy định rằng"),
    (r"\bRunning this code\b", "Chạy đoạn code này"),
    (r"\bWhen you run\b", "Khi bạn chạy"),
    (r"\bThe output is\b", "Output là"),
    (r"\bThe output will be\b", "Output sẽ là"),
    (r"\bwhich is\b", "là"),
    (r"\bwhich are\b", "là"),
]

# Per-difficulty metacog_pre/post replacements (these are fixed strings from design_roadmap.py)
METACOG_PRE_TRANS = {
    "Read the snippet once. Rate your confidence (1-5) that you can predict the output before checking options.":
        "Đọc đoạn code một lần. Đánh giá độ tự tin (1-5) rằng bạn có thể dự đoán output trước khi xem các lựa chọn.",
    "Identify the riskiest line in the snippet. State which option you suspect and why before submitting.":
        "Tìm dòng có rủi ro cao nhất trong đoạn code. Nói rõ lựa chọn bạn nghi ngờ và lý do trước khi submit.",
    "Map the snippet's behavior on a worst-case input. Predict your accuracy on this question (1-5).":
        "Hình dung behavior của code với input worst-case. Dự đoán độ chính xác của bạn cho câu này (1-5).",
}
METACOG_POST_TRANS = {
    "Did your prediction match? Note one cue you missed.":
        "Dự đoán của bạn có đúng không? Ghi lại một dấu hiệu bạn đã bỏ lỡ.",
    "If you were wrong, which mental model failed - control flow, type, or semantics?":
        "Nếu bạn sai, mental model nào đã fail — control flow, kiểu dữ liệu, hay semantics?",
    "Reflect: which underlying concept (memory model, ordering, complexity) would have made this obvious?":
        "Suy ngẫm: concept nền (memory model, ordering, complexity) nào sẽ khiến bug này hiển nhiên?",
}

# Misconception map: replace the topic-specific reason templates
MISCONCEPTION_TRANS = {
    "assumes the happy path": "giả định happy path",
    "confuses the operator semantics": "nhầm semantics của operator",
    "ignores the boundary condition": "bỏ qua điều kiện biên",
    "mis-traces the loop iteration count": "đếm sai số lần lặp",
    "treats untrusted input as safe": "coi input không tin cậy là an toàn",
    "confuses encoding with sanitization": "nhầm encoding với sanitize",
    "trusts client-side validation": "tin tưởng validate phía client",
    "assumes secure-by-default API": "giả định API secure-by-default",
    "ignores the inner-loop multiplier": "bỏ qua hệ số nhân của vòng lặp bên trong",
    "assumes the constant-time op is free": "giả định thao tác O(1) là miễn phí",
    "overlooks the allocation per iteration": "bỏ qua việc cấp phát mỗi vòng lặp",
    "treats average case as worst case": "coi average case là worst case",
    "follows literal-translation idiom from another language": "dịch idiom thẳng từ ngôn ngữ khác",
    "prefers shorter syntax that hides the bug": "chọn cú pháp ngắn hơn nhưng giấu bug",
    "applies an outdated convention": "áp dụng convention lỗi thời",
    "confuses readability with cleverness": "nhầm dễ đọc với khôn ngoan",
    "assumes non-empty input": "giả định input không rỗng",
    "forgets the boundary value": "quên giá trị biên",
    "treats 0/None/NaN as ordinary": "coi 0/None/NaN là bình thường",
    "ignores the limit of the type range": "bỏ qua giới hạn của kiểu",
    "assumes operations are atomic": "giả định các thao tác là atomic",
    "ignores the interleaving of threads": "bỏ qua việc interleave giữa các thread",
    "trusts ordering between unrelated writes": "tin vào thứ tự giữa các write không liên quan",
    "confuses lock contention with deadlock": "nhầm lock contention với deadlock",
}

# Learning objective — translate the verb + topic phrase templates
OBJECTIVE_VERB = {"Identify": "Xác định", "Distinguish": "Phân biệt", "Predict": "Dự đoán"}
OBJECTIVE_TOPIC = {
    "the bug": "lỗi",
    "the security flaw": "lỗ hổng bảo mật",
    "the performance hotspot": "performance hotspot",
    "the style issue": "vấn đề style",
    "the edge-case failure": "edge-case failure",
    "the concurrency hazard": "concurrency hazard",
}

def translate_question(q_text):
    for pat, rep in QUESTION_PHRASES:
        if re.match(pat, q_text):
            return re.sub(pat, rep, q_text)
    return q_text  # fallback

def translate_option(opt):
    for pat, rep in OPTION_PHRASES:
        if re.match(pat, opt):
            return re.sub(pat, rep, opt)
    return opt

def translate_explain(text):
    out = text
    for pat, rep in EXPLAIN_PATTERNS:
        out = re.sub(pat, rep, out)
    return out

def translate_objective(obj):
    out = obj
    for en, vi in OBJECTIVE_VERB.items():
        out = re.sub(r"^" + en + r"\b", vi, out)
    for en, vi in OBJECTIVE_TOPIC.items():
        out = out.replace(en, vi)
    out = out.replace("in a python snippet", "trong đoạn code Python")
    out = re.sub(r"≥ (\d+)% accuracy by end of stage\.?$", r"đạt độ chính xác ≥ \1% khi kết thúc stage.", out)
    out = re.sub(r"within (\d+) seconds?", r"trong \1 giây", out)
    return out

def translate_misconception_map(m):
    return {k: MISCONCEPTION_TRANS.get(v.lower(), v) for k, v in m.items()}

def translate_metacog_pre(t):
    return METACOG_PRE_TRANS.get(t, t)
def translate_metacog_post(t):
    return METACOG_POST_TRANS.get(t, t)

def migrate_questions():
    qs = json.loads((ROOT/"questions.json").read_text(encoding="utf-8"))
    # Backup full English version (for audit trail)
    if not (ROOT/"questions_en_full.json").exists():
        atomic_write(str(ROOT/"questions_en_full.json"), json.dumps(qs, ensure_ascii=False))
    py = [q for q in qs if q["lang"] == "python"]
    out = []
    for q in py:
        nq = dict(q)
        nq["question"] = translate_question(q["question"])
        nq["options"] = [translate_option(o) for o in q["options"]]
        nq["explain"] = translate_explain(q["explain"])
        nq["learning_objective"] = translate_objective(q["learning_objective"])
        nq["misconception_map"] = translate_misconception_map(q["misconception_map"])
        nq["metacog_pre"] = translate_metacog_pre(q["metacog_pre"])
        nq["metacog_post"] = translate_metacog_post(q["metacog_post"])
        out.append(nq)
    atomic_write(str(ROOT/"questions.json"), json.dumps(out, ensure_ascii=False))
    # Also write a JSONL stream (consistent with prior tooling)
    with open(ROOT/"questions.jsonl", "w", encoding="utf-8") as f:
        for q in out:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    return out

def migrate_roadmap_perlang():
    rp = json.loads((ROOT/"roadmap_perlang.json").read_text(encoding="utf-8"))
    # Backup
    if not (ROOT/"roadmap_perlang_en.json").exists():
        atomic_write(str(ROOT/"roadmap_perlang_en.json"), json.dumps(rp, ensure_ascii=False, indent=2))
    rp["langs"] = ["python"]
    rp["per_lang_stages"] = {"python": rp["per_lang_stages"]["python"]}
    rp["per_lang_kcs"] = {"python": rp["per_lang_kcs"]["python"]}
    rp["lang_specific_kcs"] = {"python": rp["lang_specific_kcs"]["python"]}
    rp["stats"] = {
        "total_stage_instances": 15,
        "stages_per_lang": {"python": 15},
        "questions_per_lang": {"python": 286},
        "dag_valid_per_lang": {"python": True},
    }
    # Translate stage titles + objectives + metacog_prompt to Vietnamese
    STAGE_TITLE_VI = {
        "Reading code: literal trace": "Đọc code: trace từng dòng",
        "Common runtime errors": "Lỗi runtime thường gặp",
        "Idiomatic syntax & style": "Cú pháp & style idiomatic",
        "Off-by-one and boundary edges": "Off-by-one và biên",
        "Truthy/falsy & comparison pitfalls": "Truthy/falsy & bẫy so sánh",
        "Mutability & reference semantics": "Mutability & reference semantics",
        "Performance: complexity & hot paths": "Performance: complexity & hot paths",
        "Resource & lifetime management": "Quản lý resource & lifetime",
        "Input validation & injection": "Validate input & injection",
        "Error handling & retry semantics": "Error handling & retry semantics",
        "Concurrency: races & atomicity": "Concurrency: race & atomicity",
        "Memory & UB hazards": "Memory & UB hazards",
        "Crypto & auth correctness": "Crypto & auth correctness",
        "Concurrency: ordering & memory model": "Concurrency: thứ tự & memory model",
        "Architecture-level review": "Review cấp architecture",
    }
    METACOG_STAGE_VI = {
        "Before answering, mentally simulate the snippet line by line. After answering, note which line surprised you.":
            "Trước khi trả lời, mô phỏng code từng dòng trong đầu. Sau khi trả lời, ghi lại dòng nào khiến bạn bất ngờ.",
        "What input value would make this code crash? Re-evaluate after seeing the answer.":
            "Input nào sẽ khiến code này crash? Đánh giá lại sau khi xem đáp án.",
        "Is there a shorter, language-native way to express this? Rate your confidence 1-5.":
            "Có cách viết ngắn hơn và idiomatic hơn không? Đánh giá độ tự tin 1-5.",
        "Trace the loop with n=0 and n=1. Which iteration counts differ?":
            "Trace vòng lặp với n=0 và n=1. Số lần lặp khác nhau ở đâu?",
        "Would the result change if 0, '', or None replaced the input?":
            "Kết quả có thay đổi nếu thay input bằng 0, '', hoặc None?",
        "Does mutating arg also mutate the caller's variable? Reason before answering.":
            "Mutate arg có làm thay đổi biến của caller không? Suy luận trước khi trả lời.",
        "Which line runs the most times? Estimate big-O before reading options.":
            "Dòng nào chạy nhiều lần nhất? Ước lượng big-O trước khi xem lựa chọn.",
        "What happens if an exception fires before the close call? Trace both branches.":
            "Chuyện gì xảy ra nếu exception bắn trước khi close? Trace cả hai nhánh.",
        "Which variable came from user input and reaches an interpreter unchanged?":
            "Biến nào đến từ user input và chạm tới interpreter mà không qua xử lý?",
        "What information is lost when this exception is caught? Could the retry double-execute a side effect?":
            "Thông tin gì bị mất khi catch exception này? Retry có thể double-execute side effect không?",
        "Interleave the two threads at every line break - does any ordering produce the wrong result?":
            "Interleave hai thread tại mỗi line break — có thứ tự nào ra kết quả sai không?",
        "What is the value at the boundary (INT_MAX, 0, -1)? Walk the arithmetic.":
            "Giá trị tại biên (INT_MAX, 0, -1) là bao nhiêu? Đi qua từng bước số học.",
        "Where could a timing or length leak give an attacker information? Reflect after answering.":
            "Timing hoặc length leak ở đâu có thể cho attacker thông tin? Suy ngẫm sau khi trả lời.",
        "Draw the lock acquisition order across both paths. Does any reverse ordering exist?":
            "Vẽ thứ tự acquire lock theo cả hai path. Có thứ tự nào đảo ngược không?",
        "If you renamed a field, how many files would change? Reflect on the cost of the abstraction.":
            "Nếu đổi tên một field, bao nhiêu file phải sửa? Suy ngẫm về chi phí của abstraction.",
    }
    OBJECTIVE_PATS = [
        (r"^trace execution of a 5-15 line snippet ≥ 90% accuracy by end of stage$",
         "Trace thực thi của đoạn code 5-15 dòng đạt ≥ 90% độ chính xác khi kết thúc stage"),
        (r"^identify the printed/returned value of a deterministic snippet within 60 seconds$",
         "Xác định giá trị in/return của đoạn code deterministic trong 60 giây"),
        (r"^predict the runtime exception class of a flawed snippet ≥ 85% accuracy by end of stage$",
         "Dự đoán class của runtime exception của đoạn code lỗi đạt ≥ 85% khi kết thúc stage"),
        (r"^distinguish NullPointer-like vs TypeError-like failures within 90 seconds$",
         "Phân biệt NullPointer-like vs TypeError-like trong 90 giây"),
        (r"^select the idiomatic option over the literal-correct option ≥ 80% accuracy by end of stage$",
         "Chọn lựa chọn idiomatic thay vì literal-correct đạt ≥ 80% khi kết thúc stage"),
        (r"^spot a redundant construct \(double negation, useless variable\) within 45 seconds$",
         "Phát hiện cấu trúc thừa (double negation, biến vô dụng) trong 45 giây"),
    ]
    for s in rp["per_lang_stages"]["python"]:
        if s["title"] in STAGE_TITLE_VI:
            s["title"] = STAGE_TITLE_VI[s["title"]]
        if s["metacog_prompt"] in METACOG_STAGE_VI:
            s["metacog_prompt"] = METACOG_STAGE_VI[s["metacog_prompt"]]
        new_objs = []
        for o in s["objectives"]:
            replaced = o
            for pat, rep in OBJECTIVE_PATS:
                if re.match(pat, o):
                    replaced = re.sub(pat, rep, o); break
            new_objs.append(replaced)
        s["objectives"] = new_objs
    atomic_write(str(ROOT/"roadmap_perlang.json"), json.dumps(rp, ensure_ascii=False, indent=2))
    # Also translate the global roadmap.json's stage titles + metacog (consistent with per-lang)
    rm = json.loads((ROOT/"roadmap.json").read_text(encoding="utf-8"))
    if not (ROOT/"roadmap_en.json").exists():
        atomic_write(str(ROOT/"roadmap_en.json"), json.dumps(rm, ensure_ascii=False, indent=2))
    for s in rm["stages"]:
        if s["title"] in STAGE_TITLE_VI:
            s["title"] = STAGE_TITLE_VI[s["title"]]
        if s["metacog_prompt"] in METACOG_STAGE_VI:
            s["metacog_prompt"] = METACOG_STAGE_VI[s["metacog_prompt"]]
        new_objs = []
        for o in s["objectives"]:
            replaced = o
            for pat, rep in OBJECTIVE_PATS:
                if re.match(pat, o):
                    replaced = re.sub(pat, rep, o); break
            new_objs.append(replaced)
        s["objectives"] = new_objs
    atomic_write(str(ROOT/"roadmap.json"), json.dumps(rm, ensure_ascii=False, indent=2))
    return rp

def main():
    qs = migrate_questions()
    print(f"questions.json: {len(qs)} Python-only items")
    print(f"sample question: {qs[0]['question']}")
    print(f"sample option 0: {qs[0]['options'][0]}")
    print(f"sample metacog_pre: {qs[0]['metacog_pre']}")

    rp = migrate_roadmap_perlang()
    print(f"roadmap_perlang.json: langs={rp['langs']}, stages={len(rp['per_lang_stages']['python'])}")
    print(f"sample stage title: {rp['per_lang_stages']['python'][0]['title']}")

if __name__ == "__main__":
    main()
