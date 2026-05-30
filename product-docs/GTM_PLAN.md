# GTM Plan — quiz-app (CodeJudge)

## TL;DR (cho người bận)

Sản phẩm là nền tảng web luyện kỹ năng **CODE-REVIEW / JUDGE code** qua MCQ (đọc đoạn code → chọn 1/4 lỗi theo 6 category → nhận explain + nguồn). Đây là **empty lane**: tất cả đối thủ lớn dạy bạn VIẾT code, gần như không ai dạy bạn ĐỌC & PHÊ BÌNH code chuyên sâu.

GTM này chọn chiến lược **demand-first, build-after**: không xây Stripe/DB/auth ngay, mà ship 3 thứ rẻ-nhất-có-thể (waitlist durable, share loop, fake-door pricing) để **đo willingness-to-pay** trước, rồi mới chi infra. North-star = **Weekly Review Rounds Completed**. Mục tiêu 90 ngày: 2.000 waitlist, 30 lượt click "Subscribe" trên fake-door, 5 khách trả tiền thật đầu tiên.

---

## 1. Positioning (1 câu)

> **"Họ bắt bạn VIẾT code. CodeJudge luyện bạn ĐỌC và bắt lỗi code — kỹ năng review mà AI chưa thay được."**

- **Category**: Code-review / code-judgment skill trainer (không phải LeetCode-style "write & run").
- **Đối thủ định danh rõ**: Codewars/HackerRank = TDD viết-và-chạy; Sourcery/CodeRabbit = AI thay reviewer (tool B2B, không phải đào tạo). Không ai chiếm lane "train human to judge code".
- **Chống lưng bằng dữ liệu thật** (không phóng đại):
  - 286 câu Python LIVE, 100% format judge, 6 category (bug/style/perf/edge/concurrency/security), 39 hard, sources 273/286, 261 subtopics; 1.141 câu EN backup.
  - Trust-gap AI có thật: SO 2024 *use-vs-want* gap (13.2% dùng AI code-review / 40.9% muốn) → kỹ năng judge của con người vẫn là wedge.
- **Wedge bán-tiền**: tính năng `/api/code_review` (dán code → AI review) là thứ "dùng thật" duy nhất biến app từ quiz tĩnh thành công cụ.

---

## 2. ICP & JTBD (ai trả tiền, vì sao)

| ICP | JTBD ("job to be done") | Vì sao chọn |
|---|---|---|
| **#1 mũi nhọn — Bootcamp grad / job seeker** | "Pass vòng code-review / security-review trong phỏng vấn" | Có content phủ ngay (46 security + 60 bug + 39 hard + misconception_map/286), nỗi đau cấp tính, sẵn-sàng-trả |
| #2 — Junior dev (0–2 năm) đang onboarding | "Đọc PR của team mà không lạc, bắt được bug trước khi senior bắt" | Đau hằng ngày, retention cao |
| #3 — Self-taught dev (82% dev tự học online) | "Lấp lỗ hổng kỹ năng review mà khóa 'write code' không dạy" | Top-funnel rộng, EN-first |

**Đi với #1 trước** (track *Security-Review Interview Prep*): nỗi đau rõ, deadline thật (lịch phỏng vấn), content sẵn sàng — không cần generate mới.

---

## 3. Pricing & Gói

### Triết lý
- Định giá neo theo đối thủ đã verify: **Codewars Red $5/th**, **Sourcery $12/seat**. Đặt giá trong dải này.
- **Wedge trả tiền = `code_review` + content hard/security**, không phải toàn bộ quiz (quiz free để hút funnel).
- **Giai đoạn 0–90 ngày: KHÔNG viết billing code.** Chỉ chạy **fake-door /pricing** để đo intent. Stripe thật chỉ bật khi đạt gate demand (mục 8).

### Bảng giá (3 tier — anchor cho fake-door, kích hoạt thật ở Phase 2)

| Gói | Giá | Cho ai | Gồm gì |
|---|---|---|---|
| **Free** | $0 | Top-funnel, mọi người | Toàn bộ quiz easy/med, roadmap 15 stage, Daily Challenge, progress localStorage |
| **Pro** | **$5/tháng** hoặc **$40/năm** (tiết kiệm 33%) | ICP #1, #2 | Mở khóa 39 hard + security/concurrency, cloud progress sync, `/api/code_review` (quota), per-category mastery, SR Leitner |
| **Teams** (fake-door only Phase 0) | "Contact us" | Bootcamp / eng manager | Seat-based, cohort dashboard, custom security pack — **chỉ thu intent, chưa định giá cứng** |

> Lý do $5/$40: đủ thấp để impulse-buy của job seeker, đủ neo giá trị so với Codewars Red. Annual $40 (=$3.33/th) để kéo LTV và giảm churn tháng.

### Free → Pro gate (kỹ thuật, đã chốt qua harness)
- Tách `/api/round` (strip `correct_idx`/explain) + `/api/check` chấm server-side → **bịt rò đáp án** ở `/api/questions` (hiện lộ `correct_idx`).
- Thêm cột `tier` ở schema; filter cả 3 path serve câu hỏi để paywall không leak.
- **Đây là điều kiện CẤU TRÚC bắt buộc trước mọi paywall** — không có nó thì gói Pro không enforce được.

---

## 4. Kênh Acquisition & CAC

### Nguyên tắc
Giai đoạn đầu **ưu tiên kênh CAC ≈ $0** (content/community/loop), chỉ test paid sau khi có baseline conversion. Bật **EN-first** cho mọi kênh quốc tế (load `questions_en_full.json`, hiện app.py:116/128 mới chỉ `questions.json`).

### Bảng kênh

| # | Kênh | Cơ chế | CAC dự kiến | Ưu tiên |
|---|---|---|---|---|
| 1 | **Daily Code Review Challenge** (viral loop) | SSR permalink `/q/<id>` + OG/Twitter card + nút Share; 1 câu/ngày (date-hash `/api/daily`) | ~$0 | **P0** |
| 2 | **Dev community** (r/learnprogramming, r/cscareerquestions, Hacker News "Show HN", Dev.to, Lobsters) | Post góc "I built a trainer to JUDGE code, not write it" + link Daily Challenge | ~$0 | **P0** |
| 3 | **SEO long-tail** | Mỗi `/q/<id>` là 1 landing index được ("Spot the bug in this Python snippet…"); 286 trang → tăng dần | ~$0 (vốn thời gian) | P1 |
| 4 | **EN top-funnel (PH/SO/HN)** | i18n landing + `?lang` gating, dataset EN 1.141 câu | ~$0 | P1 |
| 5 | **Bootcamp partnership** (mục 6) | B2B2C, đưa track Security-Review vào curriculum | thấp/lead | P1 |
| 6 | **Paid acquisition** (Reddit/Google "code review interview prep") | Chỉ bật khi có conversion baseline | mục tiêu **CAC < 1/3 LTV** | P2 |

### Toán CAC/LTV (làm rõ ngưỡng paid)
- LTV thô (Pro $5/th, churn giả định 8%/th, gross margin ~85%): `LTV ≈ 5 × (1/0.08) × 0.85 ≈ $53`. Annual nâng con số này lên.
- **Trần CAC paid an toàn = LTV/3 ≈ $17/khách trả tiền.** Trên ngưỡng này thì tắt kênh paid, dồn về loop/SEO.
- Phase 0 **không tiêu tiền paid** — mục tiêu là đo *organic conversion rate* (visitor → waitlist → fake-door click) để biết kênh nào đáng scale.

---

## 5. Retention & Engagement

**Vấn đề lớn nhất hiện tại**: progress chỉ ở `localStorage` → mất tiến độ khi đổi máy/xóa cache (đúng lỗi kiểu freeCodeCamp #16147). Đây là **rò rỉ retention số 1** cần vá khi có auth.

| Cơ chế | Mô tả | Trạng thái |
|---|---|---|
| **Daily Code Review Challenge** | 1 câu/ngày, streak + badge → lý do quay lại hằng ngày | Build P0 (cũng là acquisition loop) |
| **Cloud progress sync** | Lift localStorage blob → row per-user (`progress(user_id, state_json JSONB)`), field-merge max(xp/streak), union(attempts/badges); giữ localStorage làm offline cache | Build khi có auth (P1) |
| **Per-category mastery** | 6-category taxonomy thành xương sống: thấy mình yếu "concurrency" → quay lại luyện | P1 |
| **SR Leitner (spaced repetition)** | Lịch ôn câu sai → kéo D7/D30 retention | Chưa build, P2 |
| **Streak/badge gamification** | Đã có sẵn, giữ | Live |

**Auth chốt**: OAuth **GitHub đơn phương thức** (hợp dev audience như Exercism), server-session cookie httpOnly + JWT signed (stateless cho Vercel), `provider_uid UNIQUE`. Không password.

---

## 6. Partnerships

| Đối tác | Mô hình | Giá trị | Khi nào |
|---|---|---|---|
| **Coding bootcamps** (VN + SEA) | B2B2C: nhúng track *Security-Review Interview Prep* vào curriculum cuối khóa | Lead chất lượng, doanh thu Teams, social proof | Sau khi có 1 track polished |
| **Dev influencer / YouTube CS-career** | Affiliate / sponsor Daily Challenge | Top-funnel rẻ, credibility | Phase 1 |
| **Open-source / Dev.to & Hashnode** | Cross-post + canonical link về `/q/<id>` | SEO + reach | Phase 1 |
| **SmartBear review methodology** | Anchor credibility (badge "why this works") — không phải đối tác thương mại, là academic/methodology anchor | Trust | Live (mục 7) |

---

## 7. Trust Layer (lợi thế cạnh tranh "khó sao chép")

Khác biệt bền vững không nằm ở UI mà ở **độ tin cậy nội dung** — đây là moat khi đối thủ AI sinh content rác.

- **Citations hiển thị**: render `<a>` từ `static/sources_map.json` (lesson.js:100, lang_lesson.js:145) — 273/286 câu có nguồn.
- **Trang `/trust`**: build từ `/api/research_refs` + `improvement_log`, **chỉ metric thật** (286 câu / 273 nguồn / 15 stage) — không bịa số.
- **Nền sư phạm**: roadmap 15 stage, 52 KC, trích dẫn học thuật (Soloway 1984, Sorva 2013, Robins 2003, Lister 2004, Hermans 2021) — chống lưng cho positioning "có phương pháp", không phải quiz vui.
- **Anti-hallucination content pipeline**: AI Question Generator chạy **offline batch**, gated bằng chính `validate.py` (schema + code-exec + dedup + pedagogy) → nguồn cung content tin cậy mà đối thủ generate-on-the-fly không có.

---

## 8. Metrics & North-Star

### North-Star Metric
> **Weekly Review Rounds Completed** (số "Review Round" có chấm điểm hoàn thành / tuần).

Vì sao: đo đúng giá trị cốt lõi (người dùng thực sự *luyện judge*), không gameable bằng pageview, và tương quan trực tiếp với retention + willingness-to-pay.

### Funnel & analytics
- **PostHog cookieless**, đúng 3 event: `page_view → quiz_start → waitlist_signup` (Phase 0 thêm `fake_door_subscribe_click`). **REJECT** tracking nặng — giữ privacy-first, không cần GDPR consent banner sớm.

### Bảng chỉ số theo phase

| Metric | Phase 0 (90 ngày) | Phase 1 | Phase 2 |
|---|---|---|---|
| Waitlist signups | **2.000** | 8.000 | — |
| Visitor → waitlist CVR | ≥ 5% | ≥ 7% | — |
| Fake-door "Subscribe" clicks | **30** (đo WTP) | — | — |
| Weekly Review Rounds (NSM) | 500/tuần | 3.000/tuần | 10.000/tuần |
| Paying customers | — | **5 đầu tiên** | 100 |
| Free→Pro CVR | — | ≥ 2% | ≥ 4% |
| D7 retention | baseline | ≥ 20% | ≥ 30% |
| Monthly churn (Pro) | — | < 10% | < 7% |

**Gate kích hoạt build infra (anti-premature)**:
- Bật **Stripe + DB + auth** CHỈ KHI fake-door đạt **≥ 30 subscribe-click** *hoặc* **≥ 2.000 waitlist với CVR ≥ 5%**. Dưới ngưỡng → tiếp tục đo, không xây.

---

## 9. Launch Sequence

Sắp theo đúng thứ tự gate đã chốt qua 20 vòng harness — mỗi phase mở khóa phase sau bằng **dữ liệu cầu thật**, không build trước nhu cầu.

### Phase 0 — Measure Demand (Tuần 1–4) — KHÔNG billing, KHÔNG DB
**Mục tiêu: chứng minh có cầu trước khi tốn infra.**
- **[P0] Waitlist durable**: serverless POST → external sink (Formspree/Google Sheets/Resend), mirror pattern `/api/client_errors`, + honeypot + throttle/IP. Đây là nguồn persist duy nhất khi chưa có DB.
- **[P0] Share/Growth loop**: SSR `/q/<id>` + OG/Twitter card + nút Share trên **Daily Code Review Challenge**.
- **[P0] Reposition landing** theo Dunford: "JUDGE code, không WRITE code" — đối chiếu đối thủ định danh.
- **[P0] Scored Review Round loop** + result theo category + chấm **server-side `/api/check`** (bịt rò đáp án — điều kiện cấu trúc).
- **[P0] Fake-door /pricing** (3 tier + cookieless intent capture, **zero billing code**).
- **[P0] Analytics PostHog cookieless** (3 event funnel).
- **[P0] Trust layer cơ bản**: render citations từ `sources_map.json`.

### Phase 1 — Top-Funnel & Light Build (Tuần 5–10) — *gated bởi Phase 0 demand*
- **[P1] EN-first**: i18n landing + `?lang`, load `questions_en_full.json` → mở kênh PH/HN/SO.
- **[P1] OAuth GitHub + cloud progress sync** (vá rò rỉ retention #1).
- **[P1] Server-side free/pro content split** (cột `tier`, filter cả 3 path).
- **[P1] /api/code_review wedge**: gate chi phí bằng char-limit + hash-cache KV + quota cookie/IP + timeout serverless.
- **[P1] Postgres serverless** qua HTTP-driver (Neon/Supabase) + tách content store static khỏi user-state store.
- **[P1] Trang /trust** đầy đủ.

### Phase 2 — Monetize & Scale (Tuần 11+) — *gated bởi demand gate (mục 8)*
- **[P2] Stripe-hosted Checkout** + signed entitlement token cho Pro; idempotent webhook.
- **[P2] "Judge the AI's code" mode** (wedge khác biệt).
- **[P2] AI Tutor "Explain like a senior"** (nhãn tin cậy).
- **[P2] SR Leitner** + per-category mastery nâng cao.
- **[P2] Bootcamp B2B partnerships** + Teams tier định giá thật.
- **[P2] Paid acquisition** (chỉ khi CAC < LTV/3) + 4 Golden Signals / SLO / GDPR / security headers.

---

## 10. Rủi ro & Câu hỏi mở

| Rủi ro | Giảm thiểu |
|---|---|
| **Cầu không đủ** (fake-door < 30 click) | Đã thiết kế gate để *fail cheap* — chưa tốn infra; pivot ICP hoặc positioning |
| **Content mới 286 câu Python LIVE** | EN backup 1.141 câu + AI generator gated `validate.py`; ưu tiên depth Security-Review pack trước breadth |
| **Rò đáp án `/api/questions`** (lộ `correct_idx`) | P0 bắt buộc: split round/check trước mọi paywall |
| **Vercel stateless** (FS ephemeral, không session in-process) | External sink + Neon HTTP-driver + JWT stateless — đã chốt kiến trúc |
| **No legal/privacy** | PostHog cookieless né GDPR sớm; thêm privacy page ở Phase 2 trước khi thu tiền |
| **AI commoditize content** | Moat = trust layer (citations thật + pedagogy + offline-validated pipeline), không phải UI |

**Câu hỏi mở cần dữ liệu Phase 0 trả lời**: (1) ICP nào convert tốt nhất — job seeker hay junior dev? (2) WTP thật ở $5/th hay cần $3? (3) `code_review` wedge hay content hard mới là lý do trả tiền? (4) Kênh nào (Daily loop vs Show HN vs SEO) cho CVR cao nhất để dồn lực?