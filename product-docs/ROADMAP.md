# ROADMAP — quiz-app: Nền tảng luyện CODE-REVIEW Skill

> **Tài liệu thực thi cho Product Lead.** Tổng hợp từ harness 20 vòng (R01–R20). Chuyển từ pet project demo (UI tiếng Việt, localStorage-only, no-DB, no-auth, no-payment) thành sản phẩm end-to-end có thể đăng ký người dùng thật, thu tiền và vận hành ổn định.
>
> **Positioning trục:** *"They make you WRITE code. We train you to JUDGE it."* — luyện kỹ năng đọc & phê bình code (bắt bug/style/perf/edge/concurrency/security), MCQ 1/4 theo 6 category, có explain + sources + misconception_map. Ngách empty-lane mà LeetCode / Codewars / Sourcery không chiếm.

---

## 0. Bối cảnh & Nguyên tắc dẫn đường

### 0.1. Trạng thái sản phẩm hiện tại (as-is)

| Hạng mục | Trạng thái |
|---|---|
| Content | 1.141 câu EN (backup) · 286 câu Python LIVE (39 hard, sources 273/286, 261 subtopics) |
| Sư phạm | 15 stage · 52 knowledge components · trích dẫn học thuật (Soloway/Sorva/Lister/Hermans) |
| Tech | Flask + Jinja · vanilla JS (Prism, copy) · Vercel serverless (api/index.py) |
| Persistence | localStorage ONLY — không DB, không tài khoản, không sync |
| Endpoints | /api/* read-only · /api/client_errors chỉ `logger.warning` (0 lead persist) |
| Monetization | 0 dòng Stripe/billing/webhook · không pricing · không tier |
| Analytics | 0 tag · không funnel · không event |
| i18n | UI ~100% tiếng Việt (cản kênh top-funnel quốc tế) |
| Pháp lý | Không privacy/GDPR/onboarding |

### 0.2. Ba lớp giá trị (định hình mọi phase)

- **GTM Layer** — waitlist durable, share/growth loop, EN-first top-funnel, analytics cookieless.
- **Trust Layer** — citations render được, trang /trust từ metric thật (286/273/15).
- **Security/Infra Layer** — server-side grading, Stripe/entitlement, OAuth+JWT, Postgres, Golden Signals/SLO/GDPR.

### 0.3. Nguyên tắc gate (rút từ 20 vòng)

1. **ĐO cầu TRƯỚC khi xây infra.** Stripe/DB/auth chỉ build sau khi waitlist + fake-door chứng minh willingness-to-pay (R01, R05, R10).
2. **Không leak đáp án = blocker cấu trúc của MỌI paywall.** `/api/questions` (app.py:236–247) hiện serialize cả `correct_idx`/`explain` → phải split `/api/round` + `/api/check` server-side TRƯỚC khi nghĩ tới tier (R06, R09).
3. **No-DB thì nguồn persist duy nhất là external sink.** Waitlist/lead phải POST ra Formspree/Sheets/Resend (Vercel FS ephemeral) (R01, R03).
4. **Chỉ dùng metric THẬT.** /trust và mọi badge neo vào con số kiểm chứng (286 câu, 273 sources, 15 stage), không phóng đại (R04 hallu 26).
5. **REJECT monetization premature.** Không hero rewrite quanh giá / pricing teaser cho tới khi có tín hiệu cầu (GTM P2 reject).

---

## PHASE 0 — MVP Market-Ready (Validate + Sellable Core)

**Mục tiêu:** Biến content browser thành *sản phẩm có thể bán* + dựng cơ chế ĐO cầu thật. Kết thúc Phase 0, ta biết **có nên** xây billing/DB hay không, và app đã **đủ điều kiện cấu trúc** để gắn paywall.

**Thời lượng ước tính:** 4–6 tuần (1–2 dev).

### Scope
1. Đóng rò đáp án (core mechanic sellable).
2. Dựng phễu đo cầu (analytics + waitlist durable + fake-door pricing).
3. Reposition landing quanh ngách "JUDGE not WRITE".
4. Growth loop nhẹ (share permalink).

### P0 items

| ID | Item | Nguồn | Ghi chú thực thi |
|---|---|---|---|
| P0-1 | **Scored "Review Round" loop** + result screen per-category (style/bug/security/concurrency/perf/edge) | R06 | Core mechanic còn thiếu khiến app chưa thành sản phẩm |
| P0-2 | **Server-side grading** — split `/api/round` (strip `correct_idx`/`explain`) + `/api/check` chấm điểm | R06, R09 | Bịt rò app.py:236–247; điều kiện bắt buộc trước mọi paywall |
| P0-3 | **Analytics cookieless** (PostHog/Plausible) — funnel page→quiz-start→waitlist | R01, GTM P2 | KHÔNG cookie, GDPR-safe; chỉ 3 event lõi |
| P0-4 | **Email waitlist durable** — serverless POST → external sink (Formspree/Sheets/Resend), mirror pattern `/api/client_errors` + honeypot + throttle/IP | R01, R03, GTM P0 | Nguồn persist DUY NHẤT khi no-DB |
| P0-5 | **Reposition landing** — hero theo Dunford: *"They make you WRITE code. We train you to JUDGE it."* | R02, R04 | Jinja/HTML zero-backend; 286 câu all-judge-format chống lưng |
| P0-6 | **Fake-door /pricing** — 3 tier market-anchored ($5/th–$40/năm) + cookieless intent capture (reuse POST waitlist) | R01, R05 | ZERO billing code; chỉ đo willingness-to-pay |

### P1 items
- **Surface 6-category flaw taxonomy** làm product spine (filter + per-category mastery grid) — R02.
- **Onboarding 2-bước chọn ICP** (Security-Review Interview Prep) → route theo JTBD, client-side reuse filter quiz.js — R03.
- **Waitlist phân-khúc theo ICP** qua field segment trong POST — R03.
- **Citations render được** — static `sources_map.json` + render `<a>` (lesson.js:100, lang_lesson.js:145) — Trust P0.

### P2 items
- Badge "Human skill AI won't replace" neo use-vs-want gap (SO 2024: 13.2% dùng / 40.9% muốn) — R04.
- Badge SmartBear review methodology ("why this works") — R02.
- Endpoint `/api/positioning` read-only cho comparison table — R04.

### Tiêu chí hoàn thành (Definition of Done)
- [ ] `/api/round` không trả `correct_idx`/`explain`; `/api/check` chấm server-side (xác minh bằng grep payload).
- [ ] Funnel 3 event chạy trên dashboard analytics, có số liệu ≥ 1 tuần.
- [ ] Waitlist lead lưu được ra external sink (test POST → thấy row), có honeypot + rate-limit/IP.
- [ ] Landing mới live với hero "JUDGE not WRITE"; /pricing fake-door bắt được click "Subscribe".
- [ ] **Gate quyết định:** đạt **ngưỡng cầu** (đề xuất: ≥ 100 waitlist signup HOẶC ≥ 30 fake-door "Subscribe" click trong 2–4 tuần) → mở khoá Phase 1. Nếu không đạt → pivot positioning/ICP, KHÔNG build billing.

---

## PHASE 1 — Launch (Accounts + Payments + AI Wedge)

**Mục tiêu:** Người dùng thật **đăng ký được**, **trả tiền được**, tiến độ **đồng bộ cloud**, và có **wedge AI dùng-thật** tạo lý do trả tiền. Chỉ khởi động sau khi Phase 0 gate PASS.

**Thời lượng ước tính:** 6–10 tuần (2 dev).

### Scope
1. Auth + cloud sync (chấm dứt mất tiến độ kiểu localStorage).
2. Free/Pro content split enforceable + Stripe Checkout thật.
3. Backend Postgres serverless + tách content store.
4. AI code-review wedge (sản phẩm dùng-thật, không còn quiz tĩnh).
5. EN-first top-funnel mở kênh quốc tế.

### P0 items

| ID | Item | Nguồn | Ghi chú thực thi |
|---|---|---|---|
| P1-A | **GitHub OAuth** (single method, hợp dev audience) + server session cookie httpOnly stateless (JWT/signed, KHÔNG in-process vì Vercel stateless), `provider_uid` UNIQUE | R08 | Không password; chống duplicate-account |
| P1-B | **Cloud progress sync** — lift localStorage blob (schema_v:2) → row `progress(user_id PK, state_json JSONB, updated_at)`; GET/PUT `/api/progress`; field-merge (max xp/streak, union attempts/badges); giữ localStorage làm offline cache + anon fallback | R08 | Vá lỗi mất tiến độ kiểu freeCodeCamp #16147 |
| P1-C | **Free/Pro content split server-side** — cột `tier`; tag 39 hard + security/concurrency = pro; filter CẢ 3 path (`/api/questions`, `/api/stage`, `/api/lang/.../stage`) để không leak paywall | R05, R09 | Phụ thuộc P0-2 đã đóng rò đáp án |
| P1-D | **Stripe-hosted Checkout** + signed entitlement token cho Pro + webhook idempotent (`processed_events`) | R05, R08, R10 | Hiện grep app.py = 0 dòng stripe; build mới hoàn toàn |
| P1-E | **`/api/code_review`** — dán code → AI review server-side; gate chi phí bằng char-limit + hash-cache KV + quota cookie/IP + timeout serverless | R07 | Wedge bán-được duy nhất; đánh gap 40.9% muốn vs 13.2% dùng |
| P1-F | **Postgres serverless qua HTTP-driver** (Neon/Supabase) né TCP-pool exhaustion trên Vercel stateless; schema tối thiểu `users` / `progress` JSONB / `processed_events` | R09 | Tách content store static (ETag/Cache-Control) khỏi user-state store |

### P1 items
- **EN-first top-funnel** — i18n landing + `?lang` gating; load `questions_en_full.json` (app.py:116/128 hiện chỉ `questions.json`) cho kênh PH/HN/SO — R06, GTM P1.
- **Billing-ready data model** + idempotent Stripe webhook scaffold — R08.
- **AI Question Generator** chạy OFFLINE batch, gated bằng `validate.py` (schema + code-exec + dedup + pedagogy) chống hallucination — R07.

### P2 items
- **Mode "Judge the AI's code"** — frame snippet là AI-generated (wedge khác biệt) — R06.
- **AI Tutor "Explain like a senior"** per-câu, có nhãn tin cậy — R07.

### Tiêu chí hoàn thành
- [ ] Đăng nhập GitHub OAuth thành công; session httpOnly stateless verify được.
- [ ] Tiến độ sync 2 chiều: đổi thiết bị thấy progress giống nhau; merge không mất data.
- [ ] Pro question KHÔNG leak qua bất kỳ path nào (test 3 endpoint với tài khoản free).
- [ ] Stripe Checkout thật charge được 1 giao dịch test→live; webhook idempotent (gửi trùng event → không double-grant).
- [ ] `/api/code_review` trả review thật trong timeout; quota chặn lạm dụng; cache hit giảm cost.
- [ ] Postgres qua HTTP-driver chạy ổn dưới tải Vercel (không pool exhaustion).
- [ ] Landing EN live; kênh top-funnel quốc tế bắt đầu có traffic.

---

## PHASE 2 — Scale (Reliability + Trust + Growth Engine)

**Mục tiêu:** Vận hành ổn định ở quy mô, dựng lòng tin (legal + trust page), và growth loop tự lan. Đây là pha "đáng tin cậy để mở rộng".

**Thời lượng ước tính:** liên tục sau launch (2+ dev).

### Scope
1. Observability + SLO (4 Golden Signals).
2. Pháp lý/bảo mật vận hành (GDPR, security headers).
3. Trust page từ metric thật.
4. Growth loop (Daily Challenge + share permalink + OG cards).
5. Spaced repetition (retention engine).

### P0/P1 items

| ID | Item | Nguồn | Ghi chú |
|---|---|---|---|
| S2-1 | **4 Golden Signals + SLO** (latency/traffic/errors/saturation) + structured logging mở rộng | Infra debt | Đo health vận hành |
| S2-2 | **Security headers + GDPR** (privacy policy, data export/delete, consent) | Infra debt | Điều kiện pháp lý để thu tiền hợp lệ |
| S2-3 | **`/api/code_review` gate + quota** cứng hoá (entitlement-aware) | R07, Infra debt | Liên kết với tier P1-C |
| S2-4 | **SHARE/GROWTH LOOP** — SSR permalink `/q/<id>` + OG/Twitter cards + nút Share (reuse `navigator.clipboard`) trên **Daily Code Review Challenge** (`/api/daily` date-hash) | GTM P0 | Viral loop top-funnel |
| S2-5 | **/trust page** từ `/api/research_refs` + `improvement_log` — CHỈ metric thật (286/273/15) | Trust P1 | Không phóng đại |
| S2-6 | **Spaced Repetition (Leitner)** — retention engine | Backlog "chưa build" | Tăng D7/D30 retention |

### Tiêu chí hoàn thành
- [ ] Dashboard 4 Golden Signals live; có SLO + alert.
- [ ] Privacy policy + data export/delete chạy được; consent banner đúng GDPR.
- [ ] `/q/<id>` SSR render OG card đúng khi share (test FB/Twitter/Slack unfurl).
- [ ] Daily Challenge ra câu mới theo date-hash; share loop đo được referral.
- [ ] /trust page chỉ hiển thị số kiểm chứng; spaced repetition tăng retention đo được.

---

## BẢNG TỔNG HỢP MỌI P0 TỪ 20 VÒNG

| Vòng | P0 item | Phase | Trạng thái blocker |
|---|---|---|---|
| R01 | Analytics funnel cookieless + fake-door pricing đo willingness-to-pay | 0 | Gate cầu |
| R01 | Email waitlist capture → managed store + double-opt-in nhẹ | 0 | Nguồn persist duy nhất |
| R02 | Reposition landing vs đối thủ: "WRITE vs JUDGE" | 0 | Positioning trục |
| R03 | Track "Security-Review Interview Prep" làm ICP mũi nhọn | 0 | Người-mua cụ thể |
| R03 | Persona-based question-pack endpoint từ taxonomy 6-category | 0 | Read-only, no new content |
| R04 | Hero landing theo Dunford: JUDGE không WRITE | 0 | Trục bán hàng |
| R05 | Fake-door /pricing + 3 tier + cookieless intent capture | 0 | Đo WTP, zero billing |
| R06 | Scored "Review Round" loop + per-category result screen | 0 | Core mechanic thiếu |
| R06 | Chấm điểm server-side + payload không lộ đáp án (`/api/check`) | 0 | **Blocker cấu trúc mọi paywall** |
| R07 | `/api/code_review` — AI review server-side + quota + cache | 1 | Wedge bán-được duy nhất |
| R08 | Cloud progress sync: lift localStorage blob → per-user row | 1 | Vá mất tiến độ |
| R08 | GitHub/Google OAuth single method + server session, no passwords | 1 | Nền auth |
| R09 | Đóng rò đáp án + enforce free/pro qua split round/check + cột tier | 1 | Enforce paywall |
| R10 | Stripe/billing/webhook xương sống doanh thu (grep = 0 dòng hiện tại) | 1 | Trục doanh thu |
| GTM | WAITLIST durable serverless → external sink + honeypot + throttle | 0 | Persist khi no-DB |
| GTM | SHARE/GROWTH LOOP: SSR `/q/<id>` + OG cards + Daily Challenge | 2 | Viral loop |
| Trust | Citations static `sources_map.json` + render `<a>` | 0 | Lòng tin nội dung |

> **Ghi chú thứ tự thực thi:** P0-2 (đóng rò đáp án, R06/R09) là **gốc phụ thuộc** — phải xong trước P1-C (tier split) và P1-D (Stripe), vì không có nó thì mọi paywall đều bị bypass qua `/api/questions`. Mọi P0 đo-cầu (R01/R03/R05) phải hoàn tất và PASS gate cầu trước khi tiêu một giờ vào billing/DB.

---

## RỦI RO & QUYẾT ĐỊNH ĐÃ CHỐT (rút từ harness)

| Quyết định | Lý do | Vòng |
|---|---|---|
| **REJECT** hero rewrite quanh giá / pricing teaser | Monetization premature khi chưa có tín hiệu cầu | GTM P2 |
| **REJECT** mở 5 ngôn ngữ ngay | Giữ focus ngách; chỉ reposition, không scope-creep content | R01 |
| GĐ đo cầu dùng external sink, KHÔNG dựng DB sớm | Vercel FS ephemeral; tránh infra phí trước khi có cầu | R01, R09 |
| Postgres qua HTTP-driver (Neon/Supabase), KHÔNG TCP-pool | Vercel stateless → TCP-pool exhaustion | R09 |
| OAuth single method (GitHub), no password | Audience là dev; giảm bề mặt bảo mật | R08 |
| Tách content store static khỏi user-state Postgres | Content read 7.3ms + ETag/CDN; tách concern | R09 |
| AI generator chạy OFFLINE batch + `validate.py` gate | Chống hallucination 16.67%; cung nội dung an toàn | R07 |

---

## METRIC THEO PHASE

| Phase | North-star metric | Ngưỡng PASS |
|---|---|---|
| 0 | Willingness-to-pay signal | ≥100 waitlist HOẶC ≥30 fake-door "Subscribe" click / 2–4 tuần |
| 1 | Trả tiền thật + retention | ≥1 paid conversion thật; cloud sync 0 data-loss; D7 retention đo được |
| 2 | Vận hành + viral | SLO đạt; referral từ share loop > 0; D30 retention tăng nhờ SR |

> Mọi ngưỡng cầu là đề xuất khởi điểm — Product Lead điều chỉnh theo baseline traffic thực tế sau tuần đầu của Phase 0.