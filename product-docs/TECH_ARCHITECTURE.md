Đây là tài liệu kiến trúc. Tôi sẽ viết trực tiếp dựa trên thông tin sản phẩm đã cung cấp — không cần truy cập codebase vì các tham chiếu file (app.py:236-247, lesson.js:100, v.v.) đã được nêu rõ trong context.

# TECH_ARCHITECTURE.md — quiz-app (CodeJudge)

> Tài liệu kiến trúc kỹ thuật để đưa quiz-app từ **pet project (Flask + Vercel, localStorage-only)** lên **sản phẩm end-to-end market-ready** (đăng ký, thu tiền, vận hành ổn định). Viết theo kết quả harness 20 vòng. Mọi quyết định bám trạng thái codebase thật: Flask serve JSON + Jinja, frontend vanilla JS, `api/index.py` serverless, `/api/questions` (app.py:236-247) đang lộ `correct_idx`, không DB, không auth, không billing.

---

## 0. TL;DR cho người vội

| Hạng mục | Quyết định | Lý do 1 dòng |
|---|---|---|
| **Hosting** | Giữ Vercel serverless (Python runtime), không đổi nền | Migration chi phí ~0, vẫn đủ cho 0→50k MAU |
| **DB user-state** | **Neon Postgres** (HTTP/serverless driver) | Né TCP-pool exhaustion trên Vercel stateless; free tier đủ MVP |
| **Content store** | Giữ **static JSON** (không nhét vào DB) | Load 7.3ms, ETag/Cache-Control, immutable, CDN-able |
| **Auth** | **GitHub OAuth** (single method) + JWT cookie httpOnly | Đúng dev audience (như Exercism); stateless hợp Vercel |
| **Payments** | **Stripe Checkout hosted** + signed entitlement + idempotent webhook | Không tự xử lý thẻ; PCI ngoài scope |
| **Đáp án** | Split `/api/round` (strip) + `/api/check` (chấm server-side) | **Blocker #1**: hiện FE biết đáp án → không thể bán/grade tin được |
| **Waitlist (P0 ngay)** | POST serverless → external sink (Sheets/Resend) | Nguồn persist DUY NHẤT khi chưa có DB |
| **Analytics** | PostHog cookieless (page→quiz-start→waitlist) | Đo cầu trước khi xây paywall; không cần cookie banner |

**Thứ tự build (gated):** Phase 0 (waitlist + analytics + đóng rò đáp án) → Phase 1 (auth + Postgres + cloud sync) → Phase 2 (Stripe + tier enforcement) → Phase 3 (AI code_review wedge).

---

## 1. Bối cảnh & nguyên tắc kiến trúc

### 1.1 Hiện trạng (as-is)

```
┌─────────────────────────────────────────────┐
│  Browser (vanilla JS + Prism + localStorage) │
│  quiz.js / lesson.js / lang_lesson.js        │
└───────────────┬─────────────────────────────┘
                │ HTTP (JSON + Jinja HTML)
                ▼
┌─────────────────────────────────────────────┐
│  Vercel Serverless  —  api/index.py → Flask  │
│  /api/questions  (LỘ correct_idx, 397KB VI)  │
│  /api/roadmap /api/stage /api/lang/...        │
│  /api/client_errors (chỉ logger.warning)      │
│  health_check, 404/500, structured logging    │
└───────────────┬─────────────────────────────┘
                │ đọc file
                ▼
   static JSON: questions.json (VI live, 286 Python)
               questions_en_full.json (1141 EN, BACKUP)
               roadmap / KC / research_refs
   ❌ KHÔNG DB · ❌ KHÔNG auth · ❌ KHÔNG billing · ❌ state = localStorage
```

**3 khiếm khuyết chặn monetization (theo harness R06/R09/R10):**

1. **Rò đáp án** — `/api/questions` (app.py:236-247) serialize toàn bộ payload gồm `correct_idx` + `explanation`. Bất kỳ paywall/grading nào cũng vô nghĩa khi client tự biết đáp án.
2. **Không có danh tính** — state nằm trong localStorage; mất máy = mất tiến độ (lỗi kiểu freeCodeCamp #16147), không thể gắn entitlement trả tiền vào ai.
3. **Không có nơi persist** — 0 dòng `stripe`/`billing`/`webhook`; `/api/client_errors` chỉ log, 0 lead được lưu.

### 1.2 Nguyên tắc thiết kế (ADR cấp principle)

- **P1 — Tách 2 store theo vòng đời dữ liệu.** *Content* (câu hỏi, roadmap, KC) là **immutable, đọc-nhiều, không-PII** → static + CDN. *User-state* (progress, entitlement, account) là **mutable, ghi, PII** → Postgres. KHÔNG nhồi content vào DB (mất ETag/cache, tốn read, khó CDN).
- **P2 — Stateless function, state ngoài process.** Vercel function chết sau mỗi request → không session in-process, không connection pool dài hạn. Dùng JWT cookie + HTTP DB driver.
- **P3 — Server là nguồn chân lý cho grading & entitlement.** FE không bao giờ nhận đáp án hay tier-decision chưa enforce.
- **P4 — Gated build.** Mỗi tầng infra chỉ build khi tầng đo-cầu phía trước cho tín hiệu dương. Không xây Stripe trước khi waitlist có lead; không xây Postgres trước khi auth cần.
- **P5 — Degrade an toàn.** Anonymous vẫn chơi được (localStorage fallback). DB down ⇒ vẫn serve content tĩnh.

---

## 2. Kiến trúc mục tiêu (to-be)

```
                         ┌──────────────────────────────────────┐
                         │            Browser (SPA-lite)         │
                         │  quiz.js · round.js · lesson.js       │
                         │  JWT cookie (httpOnly) · localStorage  │
                         │  (offline cache + anon fallback)       │
                         └───┬───────────────┬──────────────┬────┘
            content (GET)    │   user-state  │   auth/pay   │
                             │   (GET/PUT)   │              │
        ┌────────────────────▼───┐  ┌────────▼────────┐  ┌──▼────────────────┐
        │ Vercel Edge / CDN       │  │ Vercel Function │  │ Vercel Function   │
        │ static JSON (ETag,      │  │ Flask (api/)    │  │ /api/auth/*       │
        │ immutable, Cache-Control)│  │ /api/round      │  │ /api/stripe/*     │
        │  questions_*.json        │  │ /api/check      │  │ /api/webhook      │
        │  roadmap/KC/refs         │  │ /api/progress   │  │                   │
        └─────────────────────────┘  │ /api/code_review│  └──┬──────────────┬─┘
                                      └───┬─────────────┘     │              │
                                          │ HTTP driver        │ OAuth        │ HTTPS
                                          ▼                    ▼              ▼
                                ┌──────────────────┐   ┌─────────────┐  ┌──────────┐
                                │ Neon Postgres     │   │ GitHub      │  │ Stripe   │
                                │ users · progress  │   │ OAuth       │  │ Checkout │
                                │ entitlements      │   └─────────────┘  │ +Webhook │
                                │ processed_events  │                    └──────────┘
                                └──────────────────┘
        ┌─────────────────────────────────────────────────────────────────┐
        │ Cross-cutting: PostHog (cookieless) · Resend (email) ·           │
        │ Upstash Redis/KV (quota + AI cache) · external waitlist sink     │
        └─────────────────────────────────────────────────────────────────┘
```

**Đường dữ liệu chính:**
- **Đọc nội dung:** Browser → CDN (static JSON), không chạm function, không chạm DB.
- **Chơi 1 round:** `GET /api/round?ids=...` (đã strip đáp án) → người dùng chọn → `POST /api/check` (chấm server-side, trả đúng/sai + explanation + sources).
- **Đồng bộ tiến độ:** `GET/PUT /api/progress` (cần JWT) → merge vào Postgres.
- **Trả tiền:** `/api/stripe/checkout` → Stripe hosted → `/api/webhook` (idempotent) → cập nhật `entitlements`.

---

## 3. Lựa chọn Database & lý do

### 3.1 Quyết định: **Neon Postgres (serverless, HTTP driver)**

| Tiêu chí | Neon Postgres | Supabase | Vercel KV (Redis) | Lý do chọn/loại |
|---|---|---|---|---|
| Driver hợp Vercel stateless | ✅ HTTP (`@neondatabase/serverless` / psycopg over HTTP) | ✅ (PgBouncer/HTTP) | ✅ | TCP-pool dài hạn **chết** trên function ephemeral |
| Quan hệ + JSONB | ✅ | ✅ | ❌ (KV) | Cần JOIN entitlement, JSONB cho progress blob |
| Free tier MVP | ✅ (0.5GB, scale-to-zero) | ✅ | ✅ | Đủ 0→~5k user |
| Branching (preview/migration) | ✅ (db-branch theo PR) | ⚠️ | — | Test migration không đụng prod |
| Latency cold | ⚠️ ~vài trăm ms khi scale-to-zero | ⚠️ | ✅ | Chấp nhận được; mitigate bằng warmup hoặc keep-alive |

**Kết luận:** Neon cho store quan hệ (user-state), **Upstash Redis (KV)** cho cache phù du (AI code_review hash-cache, quota cookie/IP). KV không thay được Postgres vì cần quan hệ + bền entitlement.

> **Tránh bẫy:** KHÔNG dùng driver Postgres TCP truyền thống (psycopg2 socket) trên Vercel — mỗi cold start mở connection mới, pool cạn nhanh (đã ghi nhận pattern này ở các deploy serverless). Bắt buộc HTTP-based driver hoặc PgBouncer transaction-mode.

### 3.2 Schema tối thiểu (DDL)

```sql
-- 3.2.1 Người dùng (OAuth-only, không password)
CREATE TABLE users (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider      TEXT NOT NULL DEFAULT 'github',
    provider_uid  TEXT NOT NULL,
    email         TEXT,
    display_name  TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, provider_uid)   -- chống duplicate-account
);

-- 3.2.2 Tiến độ (nâng từ localStorage blob schema_v:2)
CREATE TABLE progress (
    user_id     BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    state_json  JSONB NOT NULL DEFAULT '{}'::jsonb,  -- xp, streak, attempts, badges, mastery
    schema_v    INT NOT NULL DEFAULT 2,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3.2.3 Entitlement (quyết định free/pro phía server)
CREATE TABLE entitlements (
    user_id       BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    tier          TEXT NOT NULL DEFAULT 'free',     -- 'free' | 'pro'
    status        TEXT NOT NULL DEFAULT 'inactive', -- active|past_due|canceled
    stripe_customer_id     TEXT,
    stripe_subscription_id TEXT,
    current_period_end     TIMESTAMPTZ,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3.2.4 Idempotency cho Stripe webhook (chống xử lý trùng event)
CREATE TABLE processed_events (
    event_id    TEXT PRIMARY KEY,        -- Stripe event.id
    type        TEXT NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3.2.5 Waitlist (nếu muốn nội-bộ-hoá sau khi có DB; Phase 0 dùng sink ngoài)
CREATE TABLE waitlist (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       TEXT NOT NULL,
    segment     TEXT,                    -- ICP: 'security-interview' | ...
    intent      TEXT,                    -- 'pricing-pro' | 'pricing-team' (fake-door)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (email, intent)
);
```

**Merge rule cho progress** (khi sync localStorage ↔ DB, tránh ghi đè mất tiến độ): `max(xp)`, `max(streak)`, **union** `attempts` + `badges`, lấy `mastery` theo `max` per-KC. Đây là field-merge, không phải last-write-wins.

---

## 4. Authentication & Authorization

### 4.1 Quyết định: **GitHub OAuth (single method) + JWT cookie stateless**

- **Vì sao 1 method, vì sao GitHub:** audience là dev/job-seeker (đúng ICP R03 "Security-Review Interview Prep"). GitHub login là chuẩn-mực với dev (như Exercism). Một method = ít bề mặt tấn công, ít UX phân nhánh. Google có thể thêm sau nếu kênh non-dev mở.
- **Không password** → loại bỏ toàn bộ rủi ro lưu/hash/reset mật khẩu.
- **Session = JWT signed, cookie httpOnly + Secure + SameSite=Lax**, KHÔNG session in-process (Vercel stateless). Payload tối thiểu: `sub=user_id`, `tier`, `exp`. `tier` trong JWT chỉ để render UI nhanh — **mọi enforce vẫn check DB/entitlement** (P3).

### 4.2 Luồng OAuth (code-level)

```
1. GET  /api/auth/github         → 302 tới GitHub authorize (state = CSRF nonce, lưu cookie httpOnly ngắn hạn)
2. GitHub → GET /api/auth/callback?code=...&state=...
3. Function: verify state → exchange code lấy access_token
              → GET https://api.github.com/user  (provider_uid, email, name)
              → UPSERT users (provider, provider_uid)   -- ON CONFLICT DO UPDATE
              → SELECT/INIT entitlements (tier='free')
              → ký JWT {sub, tier, exp=+30d}
              → Set-Cookie: session=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/
              → 302 về /
4. Mọi /api/* cần auth: đọc cookie → verify chữ ký JWT → g.user_id
```

**Authorization (entitlement gate):**

```python
def require_pro(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        uid = current_user_id()           # từ JWT
        if uid is None:
            return jsonify(error="auth_required"), 401
        ent = db_entitlement(uid)         # SELECT tier,status FROM entitlements
        if not (ent.tier == "pro" and ent.status == "active"):
            return jsonify(error="upgrade_required"), 402  # Payment Required
        return fn(*a, **kw)
    return wrapper
```

---

## 5. Đóng rò đáp án + Server-side grading (blocker #1)

Đây là thay đổi **bắt buộc trước mọi paywall** (R06/R09). Hiện `/api/questions` trả cả `correct_idx` + `explanation`.

### 5.1 Split endpoint

| Endpoint | Trả về | KHÔNG trả |
|---|---|---|
| `GET /api/round?ids=q1,q2,...` (hoặc `?n=10&lang=python`) | `id`, `code`, `lang`, 4 `options`, `category`, `difficulty` | `correct_idx`, `explanation`, `sources`, `misconception_map` |
| `POST /api/check` body `{id, choice}` | `{correct: bool, correct_idx, explanation, sources, misconception}` | — (chỉ trả sau khi đã nộp) |

### 5.2 Code-level migration cho app.py

```python
# TRƯỚC (app.py:236-247) — LỘ đáp án
@app.route("/api/questions")
def api_questions():
    return _add_cache_headers(jsonify(ALL_QUESTIONS), 3600)  # gồm correct_idx ❌

# SAU — round (strip) + check (server grade)
PUBLIC_FIELDS = ("id", "code", "lang", "options", "category", "difficulty", "tier")

def _strip(q):
    return {k: q[k] for k in PUBLIC_FIELDS if k in q}

@app.route("/api/round")
def api_round():
    qs = select_questions(request.args)          # lọc theo lang/topic/difficulty/ids
    qs = enforce_tier(qs, current_user_id())     # ẩn câu pro nếu free (xem §6)
    return _add_cache_headers(jsonify([_strip(q) for q in qs]), 3600)

@app.route("/api/check", methods=["POST"])
def api_check():
    body = request.get_json(force=True)
    q = QUESTION_INDEX.get(body.get("id"))
    if q is None:
        return jsonify(error="not_found"), 404
    # gate câu pro
    if q.get("tier") == "pro" and not is_pro(current_user_id()):
        return jsonify(error="upgrade_required"), 402
    correct = (body.get("choice") == q["correct_idx"])
    return jsonify(
        correct=correct,
        correct_idx=q["correct_idx"],
        explanation=q["explanation"],
        sources=q.get("sources", []),
        misconception=q.get("misconception_map", {}).get(str(body.get("choice"))),
    )
```

### 5.3 Frontend đổi tương ứng

- `quiz.js`: load câu từ `/api/round` (không có `correct_idx`); khi nộp gọi `POST /api/check`, render result/explanation từ response.
- `lesson.js:100` & `lang_lesson.js:145`: render `sources` thành `<a>` từ response của `/api/check` (cũng là chỗ Trust Layer P0 cắm citation link).
- Giữ keyboard shortcut (1-4 chọn, Enter nộp) — chỉ đổi nguồn dữ liệu.

> **Lưu ý:** Vì `/api/round` strip đáp án nhưng vẫn cache 3600s an toàn (không PII, không đáp án). `/api/check` **không cache** (POST, per-user).

---

## 6. Content store & Tier enforcement

### 6.1 Content giữ STATIC (không vào DB)

- File: `questions.json` (VI live 286 Python), `questions_en_full.json` (1141 EN — bật cho EN-first top-funnel, sửa `app.py:116/128` để load thêm), `roadmap`, `KC`, `research_refs`, `sources_map.json`.
- Phục vụ qua CDN với `ETag` + `Cache-Control: public, max-age=3600, immutable` (theo nội dung versioned). Load đo được ~7.3ms.
- Khi cập nhật content: deploy mới (immutable URL theo hash) → cache-bust tự nhiên. Không cần migration DB.

### 6.2 Tier field & enforce 3 đường

Thêm `tier` vào mỗi câu trong JSON: gắn `pro` cho **39 hard + security/concurrency** (theo R05), còn lại `free`. Enforce phải áp **cả 3 path** kẻo leak paywall:

```python
def enforce_tier(questions, uid):
    if is_pro(uid):
        return questions
    return [q for q in questions if q.get("tier", "free") == "free"]
# áp cho: /api/round, /api/stage, /api/lang/<lang>/stage
```

Vì grading đã ở `/api/check` (§5) và `/api/check` tự gate câu `pro` → free user không thể "đoán mò rồi xem đáp án" câu pro. **Paywall giờ mới thật sự enforceable.**

---

## 7. Payments & Billing

### 7.1 Quyết định: **Stripe Checkout (hosted) + signed entitlement + idempotent webhook**

- **Hosted Checkout** → Stripe giữ trang thẻ, PCI-DSS nằm ngoài scope của ta (không bao giờ chạm số thẻ).
- Giá theo positioning R-final: **$5/tháng – $40/năm** (Pro), neo vào benchmark (Codewars Red $5/th, Sourcery $12/seat).
- Webhook là **nguồn chân lý** cập nhật `entitlements`; client redirect chỉ để UX, không tin được.

### 7.2 Luồng (code-level)

```python
# 1. Tạo Checkout Session
@app.route("/api/stripe/checkout", methods=["POST"])
@require_login
def create_checkout():
    uid = current_user_id()
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": PRICE_PRO_MONTHLY, "quantity": 1}],
        success_url=f"{BASE}/welcome?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{BASE}/pricing",
        client_reference_id=str(uid),       # map về user của ta
        customer_email=user_email(uid),
    )
    return jsonify(url=session.url)          # FE redirect

# 2. Webhook — idempotent, verify signature
@app.route("/api/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return "", 400

    # idempotency: chèn event.id, nếu trùng → đã xử lý
    if not insert_processed_event(event["id"], event["type"]):  # False nếu conflict
        return "", 200

    if event["type"] in ("checkout.session.completed",
                         "customer.subscription.updated",
                         "customer.subscription.deleted"):
        obj = event["data"]["object"]
        uid = int(obj.get("client_reference_id") or lookup_uid_by_customer(obj["customer"]))
        upsert_entitlement(
            uid,
            tier="pro" if obj.get("status") in ("active", "trialing") else "free",
            status=obj.get("status", "canceled"),
            stripe_customer_id=obj.get("customer"),
            stripe_subscription_id=obj.get("subscription") or obj.get("id"),
            current_period_end=obj.get("current_period_end"),
        )
    return "", 200
```

**Idempotency insert:**

```python
def insert_processed_event(event_id, etype):
    try:
        db.execute("INSERT INTO processed_events(event_id,type) VALUES(%s,%s)", (event_id, etype))
        return True
    except UniqueViolation:
        return False    # đã xử lý → bỏ qua an toàn
```

### 7.3 Phase fake-door trước (R05 P0)

Trước khi viết code Stripe thật: dựng `/pricing` (Jinja) + `pricing.json` (clone `_add_cache_headers(jsonify, 3600)`), thêm vào `vercel.json includeFiles`; nút "Subscribe" → `POST` capture intent vào **waitlist sink ngoài** (cookieless, 0 dòng billing). Chỉ khi click-rate đủ mới build §7.2.

---

## 8. API surface (to-be)

| Method | Endpoint | Auth | Cache | Mô tả |
|---|---|---|---|---|
| GET | `/api/round` | optional | 3600s | Câu đã strip đáp án + tier-filtered |
| POST | `/api/check` | optional | no | Chấm server-side, trả explanation/sources |
| GET | `/api/roadmap` `/api/stage` `/api/lang/<l>/stage` | optional | 3600s | Tier-filtered |
| GET/PUT | `/api/progress` | **JWT** | no | Cloud sync, field-merge |
| GET | `/api/auth/github` · `/api/auth/callback` | — | no | OAuth |
| POST | `/api/stripe/checkout` | **JWT** | no | Tạo Checkout |
| POST | `/api/webhook` | Stripe sig | no | Cập nhật entitlement (idempotent) |
| POST | `/api/code_review` | **JWT + quota** | hash-cache | AI wedge (Phase 3) |
| POST | `/api/waitlist` | — (honeypot+throttle) | no | Lead → sink ngoài |
| POST | `/api/client_errors` | — | no | Đã có (giữ pattern làm mirror cho waitlist) |
| GET | `/api/positioning` `/api/research_refs` `/api/daily` | — | 3600s | Static-ish (positioning, /trust, daily challenge) |
| GET | `/q/<id>` | — | SSR | Permalink + OG/Twitter card (growth loop) |

**Convention:** mọi GET content dùng `_add_cache_headers(..., 3600)`; mọi endpoint per-user/POST = no-cache; lỗi trả JSON `{error: code}` + HTTP status đúng (401 auth, 402 upgrade, 404 not_found, 429 quota).

---

## 9. AI code_review wedge (Phase 3 — endpoint duy nhất bán-được "dùng thật")

```python
@app.route("/api/code_review", methods=["POST"])
@require_pro                                   # gate tier
def code_review():
    code = (request.json or {}).get("code", "")
    if len(code) > MAX_CHARS:                  # 1. giới hạn ký tự (cap cost)
        return jsonify(error="too_long"), 413
    if not quota_ok(quota_key()):              # 2. quota cookie/IP → 429
        return jsonify(error="quota_exceeded"), 429
    h = sha256(code.encode()).hexdigest()
    cached = kv.get(h)                          # 3. hash-cache KV
    if cached:
        return jsonify(cached)
    result = call_llm(code, timeout=SERVERLESS_TIMEOUT - 2)   # 4. timeout < limit function
    kv.setex(h, 86400, result)
    return jsonify(result)
```

4 van kiểm soát chi phí: **char-limit → quota → hash-cache → timeout**. Đây là tính năng đánh đúng gap cầu lớn nhất (40.9% muốn AI code review vs 13.2% đang dùng). **AI Question Generator** chạy OFFLINE batch, gate bằng `validate.py` (schema + code-exec + dedup + pedagogy) — không phải runtime endpoint, không rủi ro hallucination trên prod.

---

## 10. Migration plan từ Flask/Vercel hiện tại

Mỗi phase độc lập deploy được, gated bởi tín hiệu phase trước (P4).

### Phase 0 — Đo cầu + đóng rò (1 sprint, 0 infra mới)
1. `POST /api/waitlist` → external sink (Resend/Sheets/Formspree) + honeypot + throttle/IP. Mirror đúng pattern `/api/client_errors`.
2. PostHog cookieless: tag `page → quiz-start → waitlist`.
3. **Split `/api/round` + `/api/check`** (§5) — đóng rò đáp án. (Có thể làm ngay, không phụ thuộc DB.)
4. SSR `/q/<id>` + OG card + nút Share trên `/api/daily`.
5. Render `sources` `<a>` từ `sources_map.json` (Trust P0).
6. **Reject** hero pricing rewrite / monetization teaser (premature).

> *Acceptance:* có lead thật trong sink + funnel PostHog hiển thị drop-off; `/api/round` không còn `correct_idx` (grep payload).

### Phase 1 — Identity + Cloud sync (gated bởi lead > 0)
1. Provision **Neon** (free), chạy DDL §3.2.
2. `/api/auth/github` + callback + JWT cookie (§4).
3. `GET/PUT /api/progress` field-merge (§3.2), giữ localStorage làm cache + anon fallback.
4. Thêm cột/bảng `entitlements` (mặc định free) — chưa bán, chỉ sẵn sàng.

> *Acceptance:* login GitHub, đổi máy thấy progress giữ nguyên; anon vẫn chơi được.

### Phase 2 — Monetization thật (gated bởi fake-door click-rate)
1. Thêm `tier` vào content JSON (39 hard + security/concurrency = pro).
2. `enforce_tier` áp cả 3 path (§6.2); `/api/check` gate pro.
3. Stripe Checkout + webhook idempotent (§7).
4. `require_pro` decorator áp cho endpoint pro.

> *Acceptance:* free user không xem được đáp án câu pro; thanh toán test-mode → webhook bật `tier='pro'`; refund/cancel → hạ về free.

### Phase 3 — AI wedge + scale hardening (gated bởi paying users > 0)
1. `/api/code_review` (§9) + Upstash KV cache/quota.
2. 4 Golden Signals (latency/traffic/errors/saturation), SLO, security headers, GDPR/privacy page, `/trust`.
3. EN-first i18n landing + `?lang` gating (kênh PH/HN/SO).

---

## 11. Bảo mật

| Lớp | Biện pháp |
|---|---|
| **Đáp án** | Server-side grade; payload `/api/round` strip `correct_idx` (đóng lỗ R06/R09) |
| **Auth** | JWT signed (HS256/RS256), cookie `HttpOnly; Secure; SameSite=Lax`; CSRF state nonce ở OAuth |
| **Authz** | Entitlement check ở DB, KHÔNG tin `tier` trong JWT để enforce (chỉ render UI) |
| **Payments** | `stripe.Webhook.construct_event` verify chữ ký; idempotency qua `processed_events`; không lưu thẻ |
| **AI endpoint** | char-limit + quota cookie/IP + timeout; chặn abuse cost |
| **Waitlist** | honeypot field + throttle/IP; validate email server-side |
| **Secrets** | Vercel env vars (`STRIPE_SECRET`, `WEBHOOK_SECRET`, `JWT_SECRET`, `GH_CLIENT_*`, `DATABASE_URL`); không commit |
| **Transport/Headers** | HTTPS bắt buộc; `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Strict-Transport-Security` |
| **PII/GDPR** | Chỉ lưu email + provider_uid; cookieless analytics; trang privacy + export/delete progress |
| **Input** | `request.get_json(force=True)` bọc try; validate `id ∈ QUESTION_INDEX`; giới hạn body size |

---

## 12. Hosting, Scale & Chi phí hạ tầng

### 12.1 Quyết định hosting: **giữ Vercel**

Migration cost ~0, đủ tải 0→50k MAU. Function ephemeral đã định hình mọi lựa chọn (HTTP DB driver, JWT stateless, KV quota). Cảnh báo scale: **cold start** Neon scale-to-zero + Vercel function → mitigate bằng keep-warm/cron ping hoặc Neon "always-on" khi có doanh thu.

### 12.2 Chi phí theo quy mô (ước tính, USD/tháng)

| Quy mô | Vercel | Neon (Postgres) | Upstash KV | Stripe | PostHog | Email (Resend) | **Tổng ~** |
|---|---|---|---|---|---|---|---|
| **MVP** (< 5k MAU, free tier) | $0 (Hobby) | $0 (free) | $0 (free) | 2.9%+30¢/giao dịch | $0 (<1M ev) | $0 (3k mail) | **~$0** |
| **Traction** (5k–50k MAU) | $20 (Pro) | $19 (Launch) | $10 | % doanh thu | $0–$50 | $20 | **~$70–120** |
| **Growth** (50k–500k MAU) | $20–$200 (usage) | $69+ (Scale) | $50 | % doanh thu | $50–$200 | $90 | **~$300–600** |

**Ghi chú chi phí:**
- AI `/api/code_review` là biến phí lớn nhất khi scale → hash-cache KV + quota giữ trần. Chỉ bật cho **pro** nên cost gắn với doanh thu.
- Stripe ăn theo giao dịch (~3%) — không phải fixed; ở $5/th biên vẫn dương.
- Content tĩnh phục vụ qua CDN → gần như miễn phí bandwidth, không tốn function-invocation.
- Đòn bẩy chi phí #1: **giữ content khỏi DB** (P1) → DB chỉ chứa user-state nhỏ (vài KB/user), free tier Neon kéo được hàng nghìn user.

### 12.3 Khi nào phải rời Vercel

Chỉ cân nhắc container (Fly.io/Railway) khi: (a) cần WebSocket/long-running, (b) AI workload cần GPU/streaming dài quá timeout serverless, hoặc (c) function-invocation cost vượt chi phí container tương đương. Hiện chưa chạm ngưỡng nào.

---

## 13. Phụ lục — ADR ngắn (quyết định & bị loại)

| ADR | Quyết định | Bị loại | Lý do |
|---|---|---|---|
| Hosting | Giữ Vercel serverless | Tự host container | Migration cost 0, chưa cần long-running |
| DB | Neon Postgres HTTP | psycopg2 TCP / Mongo / KV-only | TCP-pool chết trên ephemeral; cần quan hệ + JSONB |
| Content | Static JSON + CDN | Nhồi vào Postgres | Giữ ETag/cache, giảm read, CDN, đòn bẩy chi phí |
| Auth | GitHub OAuth + JWT | Email/password; session in-process | Đúng dev audience; stateless hợp Vercel; bỏ rủi ro password |
| Payments | Stripe hosted + webhook | Tự xử lý thẻ; tin client redirect | PCI ngoài scope; webhook là nguồn chân lý |
| Grading | Server-side `/api/check` | Trả `correct_idx` cho FE | Blocker monetization; chống rò đáp án |
| Pricing UI | Fake-door trước, Stripe sau | Build billing ngay | Đo willingness-to-pay trước khi tốn infra (P4) |
| AI | `/api/code_review` gated pro + offline gen | AI runtime cho free / gen on-the-fly | Trần chi phí; chống hallucination trên prod |

---

*Tài liệu này phản ánh trạng thái tích luỹ 20 vòng harness. Mọi tham chiếu file (app.py:236-247, lesson.js:100, lang_lesson.js:145, app.py:116/128) là điểm cắm migration thật trong codebase hiện tại.*