# PRODUCT_SPEC.md — quiz-app (codename: "JudgeCode")

> Tài liệu đặc tả sản phẩm end-to-end. Tổng hợp từ harness 20 vòng (R01–R20). Mọi con số content/codebase đều là **metric thật đã verify** (286 câu Python live, 273/286 có sources, 15 stage, 52 KC, 1.141 câu EN backup). Mọi tuyên bố thị trường giữ nguyên nguồn gốc từ vòng research và được đánh dấu là *assumption cần đo lại* khi chưa có dữ liệu nội bộ.

---

## 1. Tầm nhìn (Vision)

### 1.1. One-liner

> **"Họ bắt bạn VIẾT code. Chúng tôi luyện bạn JUDGE code."**
> Nền tảng luyện kỹ năng **code-review** (đọc, phê bình, bắt lỗi) qua các vòng trắc nghiệm 1/4 đáp án — kỹ năng con người mà AI chưa thay thế được.

### 1.2. Vấn đề (Problem)

- Mọi nền tảng coding-ed lớn (LeetCode, Codewars, HackerRank, Exercism, Codility) đều luyện **WRITE** (viết code, chạy test). Không ai luyện chuyên sâu kỹ năng **JUDGE** (đọc code người khác, bắt bug/style/perf/edge/concurrency/security).
- Trong thực tế làm việc, dev đọc code nhiều hơn viết. Vòng phỏng vấn ngày càng có khâu "review this PR".
- AI sinh code ngày càng nhiều → kỹ năng **đánh giá** code (kể cả code AI) trở thành kỹ năng khan hiếm. Khoảng cách use-vs-want trong khảo sát dev (muốn dùng AI cho code review nhiều hơn mức đang dùng) cho thấy nhu cầu về năng lực review.

### 1.3. Định vị (Positioning — empty lane)

| | Họ (đối thủ) | Chúng tôi |
|---|---|---|
| Hành vi luyện | WRITE & RUN | **JUDGE & EXPLAIN** |
| Format | viết hàm, pass test | đọc snippet, chọn 1/4 lỗi, đọc giải thích + nguồn |
| Wedge bán tiền | subscription chung | **AI Code Review tool** (dán code thật, nhận review) |
| Khác biệt AI | AI thay reviewer (Sourcery/CodeRabbit) | luyện *con người* judge code (kể cả code AI) |

Ngách "code-review skill" là **empty lane** — không đối thủ tham chiếu nào chiếm. Đây là trục định vị xuyên suốt mọi quyết định sản phẩm.

### 1.4. Tầm nhìn dài hạn

Từ "quiz tĩnh học code-review" → trở thành **công cụ review hằng ngày của dev** (luyện kỹ năng + dùng AI review code thật) → mở rộng B2B (team onboarding, đào tạo reviewer cho engineering org).

---

## 2. ICP & Personas

### 2.1. ICP mũi nhọn (đã khoá ở R03)

**"Security-Review Interview Prep"** — bootcamp grad / job seeker chuẩn bị vòng phỏng vấn có khâu code-review.

- **JTBD:** *"Giúp tôi pass vòng code-review/security-review trong phỏng vấn."*
- **Vì sao ngách này:** Codewars (TDD) và Sourcery/CodeRabbit (B2B AI reviewer) đều bỏ trống. Khả thi **ngay** trên content thật (46 câu security + 60 bug + 39 hard + misconception_map phủ 286 câu), không cần sinh content mới.

### 2.2. Bảng personas

| Persona | Mô tả | JTBD chính | Sẵn-sàng-trả-tiền | Ưu tiên |
|---|---|---|---|---|
| **P1 — Interview Prepper** (ICP mũi nhọn) | Bootcamp grad / job seeker, 0–2 năm KN | Pass vòng code-review phỏng vấn | Cao (deadline-driven) | **MVP** |
| **P2 — Junior dev đi làm** | Dev 0–3 năm, muốn lên trình review PR | Tự tin review PR đồng nghiệp; bớt bị reject review | Trung bình | v1 |
| **P3 — Self-learner / career-switcher** | Tự học, 82% dev học online | Xây nền tảng "đọc code" có phương pháp | Thấp–TB (price-sensitive) | v1 |
| **P4 — Eng manager / team lead** (tương lai) | Onboard reviewer cho team | Chuẩn hoá năng lực review trong team | Cao (B2B) | v2 |

### 2.3. Anti-persona (KHÔNG nhắm)

- Người muốn luyện **viết** thuật toán (đã có LeetCode).
- Người tìm AI **thay** reviewer cho production (đã có Sourcery/CodeRabbit) — ta luyện *con người*.

---

## 3. Value Proposition

### 3.1. Hero (theo April Dunford — đã chốt R04)

- **Hero headline:** "JUDGE code. Don't just WRITE it."
- **Sub:** "286 câu code-review thật, 6 loại lỗi, giải thích + nguồn cho từng câu. Luyện kỹ năng AI chưa thay được."
- **Proof points (chỉ metric thật):**
  - 286 câu Python all-judge-format, 39 câu hard.
  - 273/286 câu có **trích dẫn nguồn**.
  - Taxonomy **6 category lỗi**: bug / style / perf / edge / concurrency / security.
  - misconception_map cho mọi câu (giải thích *vì sao* sai).
  - Roadmap 15 stage, 52 knowledge components, có trích dẫn học thuật (Soloway, Sorva, Lister, Hermans...).

### 3.2. Badge khác biệt

- **"Human skill AI won't replace"** — neo vào gap use-vs-want trong khảo sát dev; **bắt buộc có footnote nguồn rõ** (tránh cherry-pick).
- **Phương pháp luận SmartBear code-review** làm "why this works" badge.

### 3.3. Điều KHÔNG làm (tránh phóng đại)

- KHÔNG hứa "AI review hoàn hảo".
- KHÔNG hero rewrite kiểu hype/monetization sớm (R-GTM reject "hero rewrite + pricing teaser" là premature).
- Mọi badge phải có nguồn; không tuyên bố vượt số liệu thật.

---

## 4. Feature Map (MVP / v1 / v2)

Ký hiệu: **[MH]** = must-have · **[NH]** = nice-to-have. Mỗi feature gắn vòng nguồn (Rxx).

### 4.1. MVP — "Bán được, vận hành được, đo được"

Mục tiêu MVP: biến content browser thành **sản phẩm có thể đăng ký + thu tiền + đo cầu**, đóng mọi lỗ bảo mật chặn paywall.

| Feature | MH/NH | Mô tả | Nguồn |
|---|---|---|---|
| **Review Round loop có chấm điểm** | MH | Vòng review N câu → màn result **per-category** (style/bug/security/concurrency/perf/edge). Đây là core mechanic còn thiếu khiến app chưa phải sản phẩm. | R06 |
| **Server-side grading** | MH | `/api/round` (strip `correct_idx`/explanation) + `/api/check` chấm phía server. Bịt rò đáp án ở `/api/questions` (app.py:236-247 đang serialize toàn bộ đáp án). **Blocker bán hàng.** | R06, R09 |
| **Cột `tier` + free/pro content split** | MH | Thêm field `tier`; filter CẢ 3 path serve câu (`/api/questions`, `/api/stage`, `/api/lang/.../stage`) để không leak paywall. | R05, R09 |
| **Fake-door /pricing** | MH | Jinja page + `pricing.json` config endpoint (clone pattern `_add_cache_headers(jsonify, 3600)` của `/api/roadmap`; thêm vào `vercel.json includeFiles`). 3 tier market-anchored. **Zero billing code** — chỉ đo willingness-to-pay. | R05 |
| **Email waitlist durable** | MH | Serverless POST → **external sink** (Formspree/Sheets/Resend), mirror pattern `/api/client_errors`; +honeypot +throttle/IP. Nguồn **duy nhất** persist khi no-DB. Phân-khúc theo ICP. | R01, R03, GTM |
| **Analytics funnel cookieless** | MH | PostHog/Plausible cookieless; funnel: page → quiz-start → waitlist. **Chỉ analytics**, không pricing teaser. | R01, GTM |
| **Reposition landing** | MH | Hero "JUDGE not WRITE" (Jinja/HTML, zero-backend) + comparison table vs đối thủ named. | R02, R04 |
| **6-category taxonomy là product spine** | MH | Grid 6 loại lỗi + filter + per-category mastery. | R02 |
| **Citations render thật** | MH | `static/sources_map.json` + render `<a>` (lesson.js:100, lang_lesson.js:145). Trust layer P0. | TRUST |
| **Persona pack endpoint** | NH | Read-only `/api/pack/<persona>` từ taxonomy 6-category (clone `/api/roadmap`, cache 3600s). | R03 |
| **Onboarding 2 bước (client-side)** | NH | Chọn ICP → route theo JTBD (reuse filter quiz.js, không DB). | R03 |
| **`/api/positioning` read-only** | NH | Comparison table + one-liner (dict tĩnh + cache 3600s). | R04 |

**Định nghĩa Done của MVP:** đáp án KHÔNG còn lộ trong payload; có waitlist persist được lead thật; có funnel đo được; landing đã reposition; có /pricing đo WTP.

### 4.2. v1 — "Có tài khoản, có thanh toán, có AI wedge"

Gate: chỉ build sau khi MVP cho tín hiệu cầu (waitlist + /pricing intent dương).

| Feature | MH/NH | Mô tả | Nguồn |
|---|---|---|---|
| **GitHub/Google OAuth (single method)** | MH | OAuth đơn phương thức (GitHub hợp dev audience như Exercism) + server session cookie httpOnly stateless (JWT/signed, KHÔNG in-process vì Vercel stateless); `provider_uid` UNIQUE. Không mật khẩu. | R08 |
| **Cloud progress sync** | MH | Nâng blob localStorage (schema_v:2) → row per-user `progress(user_id PK, state_json JSONB, updated_at)`; GET/PUT `/api/progress`; field-merge (max xp/streak, union attempts/badges); giữ localStorage làm offline cache + anon fallback. Vá lỗi mất tiến độ kiểu freeCodeCamp. | R08 |
| **Postgres serverless (HTTP-driver)** | MH | Neon/Supabase qua HTTP-driver né TCP-pool exhaustion trên Vercel stateless. Schema tối thiểu: `users` / `progress (JSONB)` / `processed_events`. Tách content store **static** (ETag/Cache-Control) khỏi user-state store. | R09 |
| **Stripe Checkout + entitlement** | MH | Stripe-hosted Checkout + signed entitlement token cho Pro tier; idempotent webhook scaffold; `processed_events` chống double-fire. (R10: hiện grep = 0 dòng stripe → đây là xương sống doanh thu cần xây.) | R05, R08, R10 |
| **AI Code Review `/api/code_review`** | MH | Dán code → AI review server-side. Gate chi phí: giới hạn ký tự + hash-cache KV + quota cookie/IP + timeout serverless. **Wedge bán-được duy nhất** biến app từ quiz tĩnh thành công cụ dùng thật. | R07 |
| **English-first content** | MH | Dùng dataset EN 1.141 câu có sẵn (load `questions_en_full.json`; app.py:116/128 hiện chỉ `questions.json`) cho kênh PH/HN/SO. i18n landing + `?lang` gating. | R06, GTM |
| **SR Leitner (spaced repetition)** | NH | Lịch ôn theo Leitner cho câu đã sai. Chưa build. | Giữ |
| **Share/growth loop** | NH | SSR permalink `/q/<id>` + OG/Twitter cards + nút Share (reuse navigator.clipboard) trên **Daily Code Review Challenge** (`/api/daily` date-hash). | GTM |
| **Gamification cloud** | NH | Badge/streak đồng bộ cloud (đang localStorage). | Giữ |

### 4.3. v2 — "Khác biệt sâu + B2B + mở rộng nội dung"

| Feature | MH/NH | Mô tả | Nguồn |
|---|---|---|---|
| **"Judge the AI's code" mode** | NH | Frame snippet là AI-generated → người học bắt lỗi code AI. Wedge khác biệt mạnh. | R06, R07 |
| **AI Question Generator (offline batch)** | NH | Chạy OFFLINE, gated bằng chính `validate.py` (schema + code-exec + dedup + pedagogy) chống hallucination. Giải bài toán cung nội dung. | R07 |
| **AI Tutor "Explain like a senior"** | NH | Giải thích per-câu, **có nhãn tin cậy**. | R07 |
| **Mở rộng đa ngôn ngữ live** | NH | Đưa JS/Go/SQL/Rust (đang EN backup) lên live như Python. | Content |
| **B2B team track** | NH | Onboard reviewer cho engineering org (persona P4). | R03 |
| **`/trust` page** | NH | Từ `/api/research_refs` + `improvement_log` (chỉ metric thật 286/273/15). | TRUST |
| **SLO / 4 Golden Signals / GDPR** | NH→MH (khi scale) | Latency/traffic/errors/saturation; security headers; privacy. | INFRA |

---

## 5. AI Features (chi tiết)

AI là **trục giá trị xếp trên** core loop, không thay thế nó.

| # | Feature | Vai trò | Cơ chế kiểm soát chi phí / chống hallucination | Ưu tiên |
|---|---|---|---|---|
| 1 | **AI Code Review** (`/api/code_review`) | Wedge bán-được duy nhất. Dán code thật → review server-side. Đánh đúng gap cầu lớn nhất (muốn dùng AI review > mức đang dùng). | Giới hạn ký tự + hash-cache KV + quota cookie/IP + timeout serverless. **Gate sau auth + tier.** | v1 (MH) |
| 2 | **AI Question Generator** | Giải bài toán **cung** nội dung. | Chạy OFFLINE batch, gated bằng `validate.py` (schema + code-exec + dedup + pedagogy). Không serve trực tiếp ra user. | v2 (NH) |
| 3 | **AI Tutor "Explain like a senior"** | Tăng độ sâu sư phạm per-câu. | Có **nhãn tin cậy**; fallback về explanation tĩnh sẵn có. | v2 (NH) |
| 4 | **"Judge the AI's code" mode** | Khác biệt định vị (luyện judge code AI). | Reuse content + framing layer; không gọi LLM realtime nếu dùng snippet tĩnh. | v2 (NH) |

**Nguyên tắc AI:** mọi output AI phải (a) gate chi phí, (b) có cache, (c) có fallback tĩnh, (d) có nhãn tin cậy / nguồn. KHÔNG để AI thành chi phí biến đổi không kiểm soát trên free tier.

---

## 6. User Flows chính

### 6.1. Flow A — Visitor → Lead (top-funnel, MVP)

```
Landing (JUDGE not WRITE)
  → click "Try a Review Round" (instant, no signup)
  → làm 1 Review Round (server-graded, /api/round + /api/check)
  → màn result per-category
  → CTA: "Save your progress" → Waitlist (email + ICP segment) → external sink
  [analytics: page → quiz-start → round-complete → waitlist]
```

### 6.2. Flow B — Đo willingness-to-pay (MVP, fake-door)

```
Bất kỳ điểm chạm Pro (hard questions / AI review teaser)
  → /pricing (3 tier market-anchored)
  → click "Subscribe" → capture intent (cookieless event + optional email)
  → "We'll notify you" (zero billing)
  [đo WTP TRƯỚC khi xây Stripe]
```

### 6.3. Flow C — Signup → Sync (v1)

```
CTA "Sign in with GitHub"
  → OAuth → server session (httpOnly, signed JWT stateless)
  → merge localStorage blob ↔ progress row (field-merge: max xp/streak, union attempts/badges)
  → progress đồng bộ đa thiết bị
```

### 6.4. Flow D — Free → Pro (v1)

```
Free user chạm nội dung tier=pro (39 hard / security / AI review)
  → /pricing thật → Stripe-hosted Checkout
  → webhook (idempotent, processed_events) → cấp signed entitlement token
  → server enforce tier ở /api/round, /api/stage, /api/lang/..., /api/code_review
```

### 6.5. Flow E — AI Code Review (v1, wedge)

```
Pro user → "Review my code" → dán snippet (giới hạn ký tự)
  → /api/code_review: check quota (cookie/IP) → hash-cache KV (hit→trả ngay)
  → miss → LLM review (timeout serverless) → cache → trả về review theo 6-category
```

### 6.6. Flow F — Daily Challenge / Share (v1, growth)

```
/api/daily (date-hash chọn câu) → Daily Code Review Challenge
  → user làm → nút Share → SSR permalink /q/<id> + OG card
  → bạn bè click permalink (SSR, index-able) → vào Flow A
```

---

## 7. Định nghĩa "Ra-thị-trường" (Go-to-Market readiness)

"Ra thị trường" = đăng ký được người dùng thật, thu tiền được, vận hành ổn định, có lợi thế cạnh tranh rõ ràng. Cụ thể hoá theo 4 trụ:

### 7.1. Acquire (đăng ký được người dùng thật)

- [ ] Landing đã reposition "JUDGE not WRITE" + comparison table.
- [ ] Waitlist **persist được lead thật** ra external sink (không mất khi serverless ephemeral).
- [ ] Analytics funnel cookieless chạy (page → round → waitlist đo được).
- [ ] OAuth GitHub hoạt động → có tài khoản thật.
- [ ] Share loop + Daily Challenge + SSR permalink index-able (top-funnel hữu cơ).

### 7.2. Monetize (thu tiền được)

- [ ] Server-side grading + content tier split (paywall **enforceable**, không leak đáp án).
- [ ] /pricing thật + Stripe-hosted Checkout + idempotent webhook + entitlement token.
- [ ] Ít nhất 1 wedge trả-tiền rõ: AI Code Review (gated) hoặc Pro content (39 hard/security).
- [ ] Có tín hiệu WTP dương từ fake-door TRƯỚC khi đầu tư billing đầy đủ.

### 7.3. Operate (vận hành ổn định)

- [ ] Postgres serverless HTTP-driver (không TCP-pool exhaustion).
- [ ] Cloud progress sync (không mất tiến độ kiểu freeCodeCamp).
- [ ] Content store tách static (ETag/Cache-Control) khỏi user-state store.
- [ ] 4 Golden Signals + structured logging + friendly 404/500 + health_check.
- [ ] Security headers, GDPR/privacy cơ bản, `/api/client_errors` mirror pattern cho durable writes.

### 7.4. Differentiate (lợi thế cạnh tranh rõ ràng)

- [ ] Định vị empty-lane "code-review skill" hiển thị rõ trên mọi điểm chạm.
- [ ] 6-category taxonomy là product spine (không đối thủ nào có grid này).
- [ ] Citations thật render (273/286) + badge "Human skill AI won't replace" có nguồn.
- [ ] "Judge the AI's code" mode (khác biệt sâu, v2).

### 7.5. Thứ tự gate (không nhảy bước)

```
MVP gate 1: Đóng rò đáp án + tier split (blocker bảo mật)   ← bắt buộc trước MỌI paywall
MVP gate 2: Waitlist durable + analytics funnel             ← đo cầu
MVP gate 3: Reposition landing + fake-door /pricing         ← đo WTP
─────────────────────────────────────────────────────────── (chỉ qua đây nếu cầu dương)
v1  gate 4: OAuth + Postgres + progress sync                ← hạ tầng tài khoản
v1  gate 5: Stripe Checkout + entitlement                   ← thu tiền thật
v1  gate 6: AI Code Review wedge + English-first            ← giá trị bán-được + top-funnel
─────────────────────────────────────────────────────────────
v2: Judge-the-AI mode, AI generator, B2B, multi-lang live, /trust, SLO/GDPR cứng
```

---

## 8. Rủi ro & nguyên tắc kỷ luật sản phẩm

| Rủi ro | Biểu hiện trong harness | Kỷ luật |
|---|---|---|
| **Monetization premature** | GTM reject "pricing teaser + hero rewrite" | Đo WTP bằng fake-door TRƯỚC khi xây Stripe/DB. |
| **Rò đáp án phá paywall** | `/api/questions` (app.py:236-247) serialize toàn bộ đáp án | Server-side grading là blocker hàng đầu, làm trước mọi tính năng trả tiền. |
| **Vercel stateless** | localStorage-only, FS ephemeral, 0 lead persist | External sink cho waitlist; HTTP-driver cho Postgres; JWT stateless session. |
| **AI = chi phí biến đổi** | `/api/code_review` có thể đốt tiền | Char-limit + KV cache + quota/IP + timeout + gate sau tier. |
| **Hallucination nội dung** | hallu rate cao trong nhiều vòng | AI generator chạy offline gated bằng `validate.py`; không serve trực tiếp. |
| **Phóng đại marketing** | cherry-pick số liệu | Mọi badge có footnote nguồn; chỉ dùng metric thật (286/273/15/52). |

---

## 9. Phụ lục — Trạng thái codebase hiện tại (đã verify)

- **Stack:** Flask (JSON + Jinja) · vanilla JS (Prism, copy buttons) · localStorage (no account/DB) · Vercel serverless (`api/index.py`).
- **Endpoints hiện có:** `/api/*`, friendly 404/500, `health_check`, structured logging.
- **Đã có:** dark mode, keyboard shortcuts (1-4 chọn / Enter nộp), `/review`, filter client-side (lang/topic/difficulty), lazy pagination 50 câu, gamification, mobile responsive.
- **CHƯA có (nợ để build):** auth/login, cloud save, đồng bộ thiết bị, payment, DB thật, AI features, analytics, leaderboard, onboarding, pháp lý/privacy.
- **Content live:** 286 câu Python (39 hard, 261 subtopics, sources 273/286). **Backup EN:** 1.141 câu (Python 286 / JS 237 / Go 222 / SQL 221 / Rust 175; easy 419 / med 524 / hard 198).
- **Lỗ cần vá ngay:** `app.py:236-247` lộ `correct_idx`; `app.py:116/128` chỉ load `questions.json` (chưa load `questions_en_full.json`); 0 dòng stripe/billing/webhook; schema thiếu cột `tier`.

---

*Mọi tuyên bố thị trường (TAM/SAM/CAGR/giá đối thủ) bắt nguồn từ vòng research R01–R10 và cần được kiểm chứng lại bằng dữ liệu nội bộ (waitlist + fake-door intent) trước khi đưa vào quyết định đầu tư lớn. Mọi metric content/codebase trong tài liệu này là số đã verify trên repo thật.*