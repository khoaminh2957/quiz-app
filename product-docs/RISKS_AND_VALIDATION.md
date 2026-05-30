# RISKS_AND_VALIDATION.md — quiz-app (Code-Review Skill Platform)

> **Phạm vi tài liệu**: Sổ rủi ro & kiểm chứng tổng hợp từ harness 20 vòng research (R01–R20). Mục tiêu: chuyển ý tưởng web học CODE-REVIEW từ pet project → sản phẩm end-to-end có thể đăng ký người dùng thật, thu tiền, vận hành ổn định.
> **Ngày**: 2026-05-30 · **Owner**: Senior Product Lead · **Trạng thái sản phẩm**: pre-revenue, no-DB, UI ~100% tiếng Việt, GTM/Trust/Security layer CHƯA build.
> **Nguyên tắc đọc**: Mọi số liệu thị trường gắn `[n]` là đã verify qua harness. Mọi con số KHÔNG có `[n]` là giả định nội bộ chưa kiểm chứng → xem Mục 5.

---

## 1. Tóm tắt điều hành (Executive Summary)

Sản phẩm có **một lợi thế định vị thật và hiếm**: dạy kỹ năng JUDGE code (đọc & phê bình, bắt lỗi theo 6 category) thay vì WRITE code — một "empty lane" mà LeetCode/Codewars (TDD, viết-và-chạy), Sourcery/CodeRabbit (AI tooling cho team B2B), Exercism (mentoring miễn phí) đều không chiếm. Thị trường nền đủ lớn (programming education ~$73B năm 2026 [1][11], CAGR 15%; 82% dev tự học online [2]) và có tín hiệu cầu định tính cho code-review-as-interview [19][20][21].

**Nhưng rủi ro lớn nhất KHÔNG phải thị trường — mà là chưa có một byte dữ liệu cầu thật nào.** Toàn bộ luận điểm bán hàng đứng trên số liệu thứ cấp + suy diễn. Codebase verify: 0 analytics tag, 0 dòng Stripe/billing, 0 lead capture (chỉ `logger.warning`), localStorage-only, no DB, no auth. Các con số conversion/retention/CAC trong các vòng sau đều là **giả định chưa test**.

**Ba mệnh lệnh kiểm chứng trước khi tiêu tiền infra:**
1. **Đo cầu thật** (waitlist durable + analytics funnel cookieless) — không có nó, mọi quyết định pricing/auth/DB là đánh bạc.
2. **Đóng rò đáp án + grading server-side** — điều kiện cấu trúc bắt buộc trước bất kỳ paywall nào (hiện `/api/questions` app.py:236–247 serialize cả `correct_idx`).
3. **Validate willingness-to-pay** qua fake-door pricing trước khi viết một dòng Stripe.

Rủi ro nền tảng của ngành (theo nguồn đã verify): >60% EdTech startup không đạt lợi nhuận vì revenue model không bền [34]; 42% startup chết vì thiếu market need [35]; CAC EdTech có thể >50% tổng chi [36]; conversion freemium EdTech chỉ 2.6% — dưới median SaaS 3.6% [25]; completion rate MOOC chỉ ~3% [32]. Đây là các "luật hấp dẫn" mà sản phẩm phải chủ động chống lại.

---

## 2. Sổ rủi ro (Risk Register)

Thang đánh giá: **Likelihood** (Thấp/TB/Cao) × **Impact** (Thấp/TB/Cao/Nghiêm trọng) → **Severity** (P0 chặn-launch / P1 / P2).

### 2.1 Rủi ro Thị trường (Market)

| ID | Rủi ro | L | I | Sev | Mitigation cụ thể |
|----|--------|---|---|-----|-------------------|
| M1 | **Không có cầu trả tiền thật** — toàn bộ TAM/định giá là số liệu thứ cấp + suy diễn; 0 lead, 0 analytics đã verify. 42% startup chết vì thiếu market need [35]. | Cao | Nghiêm trọng | **P0** | Waitlist durable (serverless POST → Formspree/Sheets/Resend, mirror pattern `/api/client_errors` + honeypot + throttle/IP). Fake-door `/pricing` 3 tier + bắt click "Subscribe" đo willingness-to-pay. Gate mọi infra spend vào ngưỡng lead tối thiểu (xem Mục 5, A1). |
| M2 | **Áp lực giá từ free/community** — Exercism 100% free + human mentoring [6]; Codewars free core ($5/th Red [5]). Người học code-review có thể không trả tiền khi free tier đối thủ đủ tốt. | Cao | Cao | P1 | Định vị wedge NGÁCH (security-review interview prep, R03) không trùng free tier đối thủ. Pricing anchored thị trường ($5–40/năm dưới LeetCode $159/yr [22], Educative $59/th [24]). Annual billing là đòn bẩy chính (50–60% saving [26]). |
| M3 | **Conversion freemium thấp hơn ngành** — EdTech freemium→paid chỉ 2.6%, dưới median SaaS 3.6% [25]. MVP có thể không đạt unit economics. | Cao | Cao | P1 | Ưu tiên opt-in trial (17.8% trial-to-paid) hoặc card-required (49.9%) thay vì freemium thuần [25]. Đo conversion thật qua fake-door trước khi build billing. |
| M4 | **Churn & completion thảm khốc kiểu MOOC** — completion MOOC ~3% [32]; returning-user rớt còn 7% [33]. Self-serve content churn nặng nếu thiếu retention loop. | Cao | Cao | P1 | Daily Code Review Challenge (date-hash) + streak/badge + (sau) SR Leitner. Share loop SSR `/q/<id>` + OG cards tạo re-entry. Đo D1/D7/D30 retention từ ngày đầu. |
| M5 | **Không khác biệt → bị nuốt** — >15,000 EdTech startup, phần lớn không scale vì thiếu differentiation → pricing pressure [37]. | TB | Cao | P1 | Giữ kỷ luật positioning "JUDGE không WRITE" (R02/R04); 6-category taxonomy làm product spine; badge SmartBear methodology làm "why this works". KHÔNG mở rộng 5 ngôn ngữ/feature creep cho đến khi có PMF tín hiệu. |
| M6 | **CAC nuốt lợi nhuận** — CAC EdTech có thể >50% tổng chi [36]. | TB | Cao | P1 | Growth loop hữu cơ (share permalink + daily challenge) thay paid acquisition sớm. EN-first top-funnel (PH/HN/SO kênh organic). Đo CAC blended ngay khi có kênh trả phí đầu tiên. |

### 2.2 Rủi ro Kỹ thuật (Technical)

| ID | Rủi ro | L | I | Sev | Mitigation cụ thể |
|----|--------|---|---|-----|-------------------|
| T1 | **Rò đáp án — paywall không thể enforce** — `/api/questions` (app.py:236–247) serialize toàn bộ `correct_idx` + `explanation` (VI 397KB LIVE); schema 20 keys KHÔNG có `tier`. Bất kỳ paywall nào đều bị bypass bằng đọc payload. | Cao | Nghiêm trọng | **P0** | Split `/api/round` (strip `correct_idx`/`explain`) + `/api/check` chấm server-side; thêm cột `tier`; filter CẢ 3 path serve câu hỏi (`/api/questions`, `/api/stage`, `/api/lang/.../stage`) để không leak paywall. **Blocker bắt buộc trước mọi monetization.** |
| T2 | **localStorage-only → mất tiến độ + không đồng bộ thiết bị** — không account/DB; lỗi kiểu freeCodeCamp #16147 (mất progress). | Cao | Cao | P1 | Cloud progress sync: nâng blob `schema_v:2` thành row per-user `progress(user_id PK, state_json JSONB, updated_at)`; GET/PUT `/api/progress`; field-merge (max xp/streak, union attempts/badges); giữ localStorage làm offline cache + anon fallback. |
| T3 | **Vercel serverless stateless → TCP pool exhaustion với Postgres** — connection pool cạn trên function ephemeral. | TB | Cao | P1 | Postgres serverless qua **HTTP-driver** (Neon/Supabase) né TCP-pool. Tách content store static (ETag/Cache-Control, load 7.3ms) khỏi user-state store (Postgres). Schema tối thiểu: `users` / `progress` JSONB / `processed_events`. |
| T4 | **Waitlist/lead mất sạch trên FS ephemeral** — Vercel FS không persist; `/api/client_errors` chỉ `logger.warning` (0 lead lưu). | Cao | Nghiêm trọng | **P0** | Mọi capture (waitlist/intent/pricing-click) PHẢI ghi ra external sink (Formspree/Sheets/Resend) — nguồn persist DUY NHẤT khi no-DB. Mirror pattern POST đã có ở `/api/client_errors`. |
| T5 | **OAuth/session sai trên stateless host** — in-process session vỡ trên Vercel. | TB | Cao | P1 | OAuth ĐƠN phương thức (GitHub, hợp dev audience như Exercism) + server-session cookie httpOnly **stateless** (JWT/signed, KHÔNG in-process); `provider_uid` UNIQUE chống duplicate-account. |
| T6 | **AI features đốt chi phí / hallucinate** — `/api/code_review` LLM call không gate → cost blowup; AI question gen hallucinate (đã đo 16.67% lỗi). | TB | Cao | P1 | `/api/code_review`: giới hạn ký tự + hash-cache KV + quota cookie/IP + timeout serverless. AI Question Generator chạy OFFLINE batch, gated bằng `validate.py` (schema + code-exec + dedup + pedagogy). AI Tutor có nhãn tin cậy. |
| T7 | **Nội dung mỏng/lệch ngôn ngữ** — chỉ 286 câu Python live; 1,141 EN là backup. Hard chỉ 198/1141; sources 273/286. | TB | TB | P2 | EN-first dùng dataset 1,141 đã có (không sinh mới gấp). AI gen offline gated bù cung dài hạn. Theo dõi sources coverage là metric trust thật. |

### 2.3 Rủi ro Pháp lý & Tuân thủ (Legal/Compliance)

| ID | Rủi ro | L | I | Sev | Mitigation cụ thể |
|----|--------|---|---|-----|-------------------|
| L1 | **Thu PII (email waitlist/account) không có privacy/consent** — chưa có privacy policy, GDPR, double-opt-in. | Cao | Cao | **P0** (khi bật capture) | Double-opt-in nhẹ cho waitlist; privacy notice tối thiểu + lawful basis trước khi thu email. Analytics cookieless (PostHog/Plausible) để né cookie-consent banner. |
| L2 | **Bản quyền nội dung & trích dẫn nguồn** — câu hỏi có code snippet + sources; cần dẫn nguồn đúng, tránh copy code có license. | TB | TB | P1 | `/trust` page từ research_refs + improvement_log (CHỈ metric thật 286/273/15). Citations static `sources_map.json` render `<a>`. Audit snippet có nguồn license rõ ràng. |
| L3 | **Thanh toán & thuế quốc tế** — Stripe thu tiền cross-border → VAT/tax, refund, chargeback. | TB | TB | P2 | Dùng Stripe-hosted Checkout (Stripe lo tax/compliance phần lớn) + signed entitlement token. Idempotent webhook scaffold. Hoãn đến khi demand verified. |
| L4 | **AI output sai gây thiệt hại học tập / trách nhiệm** — AI review/tutor đưa lời khuyên sai. | TB | TB | P2 | Nhãn tin cậy rõ ràng cho mọi AI output; disclaimer "AI-assisted, not authoritative"; ưu tiên citation nguồn người (SmartBear, academic refs). |

### 2.4 Rủi ro Tài chính (Financial)

| ID | Rủi ro | L | I | Sev | Mitigation cụ thể |
|----|--------|---|---|-----|-------------------|
| F1 | **Revenue model không bền** — >60% EdTech không đạt profitability vì model không rõ/không bền [34]. | Cao | Nghiêm trọng | **P0** (validate) | Validate willingness-to-pay qua fake-door TRƯỚC khi build billing. Wedge trả-tiền rõ: `code_review` tool ($5/th–$40/năm). Không build Stripe đến khi có tín hiệu intent. |
| F2 | **Infra burn trước doanh thu** — DB/auth/AI cost trước khi có user trả tiền. | TB | Cao | P1 | Stack chạy $0/MVP trên free tier (Supabase 50k MAU free [27]; Next/Supabase/Stripe <$200/th tới $1K MRR [28]). Stripe Billing 0.7% pay-as-you-go [29][30]. Gate spend vào milestone demand. |
| F3 | **Unit economics âm vì CAC > LTV** — CAC EdTech >50% chi [36]; conversion 2.6% [25] → LTV thấp nếu churn cao. | TB | Cao | P1 | Organic growth loop ưu tiên; annual billing nâng LTV (50–60% prepay [26]); đo LTV:CAC trước khi scale ad spend. |
| F4 | **Định giá sai (quá cao/thấp)** — anchor từ đối thủ nhưng ngách khác, chưa test giá thật. | TB | TB | P2 | Fake-door 3 tier đo điểm giá thật. Tham chiếu: Codewars $5/th–$40/yr [5], LeetCode $159/yr [22], Sourcery $12/seat [9], Educative $59/th [24]. Test 2–3 mức giá A/B. |

---

## 3. Quy trình Anti-Hallucination của Harness

Harness 20 vòng vận hành theo vòng lặp **generate → adversarial verify → quarantine**:

1. **Tách claim khỏi nguồn**: mỗi luận điểm phải gắn `source_url` thật, load được. Số liệu phải verify **verbatim** trên trang nguồn (vd "30% savings" Codewars, "1,468 reviews" Codecademy đều check tận chữ).
2. **Verify trên codebase thật, không tin mô tả**: mọi claim kỹ thuật grep thẳng vào `app.py` (vd xác nhận `/api/questions` app.py:236–247 lộ `correct_idx`; 0 dòng stripe; schema 20 keys không có `tier`). Tránh "đề xuất ảo" trên code không tồn tại.
3. **Đếm verified vs hallucination mỗi vòng**: mỗi R0x ghi `verified / hallu` (vd R01 43/29, R08 48/19). Tỷ lệ hallu cao → hạ readiness score, buộc re-verify.
4. **Phân loại lỗi 3 cấp**: (a) **fabrication cứng** (URL bịa / số bịa) → loại ngay; (b) **source attribution mismatch** (số thật nhưng gán sai publisher) → sửa nhãn; (c) **interpretation/suy diễn** (kết luận vượt dữ liệu) → đánh dấu "SUY DIỄN", không tính là fact.
5. **Phân biệt diễn giải vs dữ liệu**: kết luận kiểu "tiền thật ở B2B không ở learner" hay "xác nhận khoảng trống ngách" được gắn nhãn INTERPRETATION, không nâng lên thành bằng chứng.
6. **Live-page drift check**: số liệu thị trường được kiểm lại với trang LIVE; nếu trang đã đổi số → cờ ngay (vd Dataintelo live giờ báo $11.3B/2025→$37.44B/2034 thay vì $3.6B/2032 đã cite).
7. **Readiness score hội tụ**: điểm readiness (2.5→5.5/10 qua các vòng) phản ánh mức "đã verify đủ để hành động"; KHÔNG vòng nào đạt ngưỡng cho phép bỏ qua kiểm chứng cầu thật.

**Nguyên tắc rút ra**: *cite-or-decline* — không có nguồn load-được + verbatim thì không dùng làm cơ sở quyết định. Số nội bộ (conversion/retention/CAC kỳ vọng) KHÔNG được trộn lẫn với số đã verify.

---

## 4. Danh sách Ảo giác Đã loại (Quarantined Hallucinations)

| # | Loại lỗi | Mô tả | Xử lý |
|---|----------|-------|-------|
| H1 | Attribution mismatch | Số online-code-learning ($3.6B 2023→$12.2B 2032 @14.5%) gán cho "Dataintelo/Technavio" nhưng trang Dataintelo hiển thị số KHÁC. | Loại con số khỏi cơ sở định giá; chỉ giữ số bootcamp $3.77B/2025 (Mordor [12]) là named-source ổn định. |
| H2 | Attribution conflation | Số bootcamp ($1.9B 2025→$6.4B 2033 @16.5%) thực ra từ Market Mind Partners [4], KHÔNG phải Dataintelo/Technavio; Technavio bị nêu tên nhưng không có nguồn Technavio thật. | Sửa nhãn nguồn về Market Mind Partners; gỡ tên Technavio. |
| H3 | Live-page drift | Trang Dataintelo LIVE giờ báo $11.3B (2025)→$37.44B (2034) @14.2% — khác hẳn số đã cite. | Đánh dấu số cũ stale; không dùng làm anchor. |
| H4 | Driver mischaracterization (nhẹ) | Claim framing "Corporate Reskilling" là driver chính, nhưng nguồn liệt kê IT-sector growth / demand for software-dev specialists là driver hàng đầu. | Sửa diễn giải, không phải fabrication. |
| H5 | Interpretation vượt dữ liệu | "Tiền thật nằm ở B2B không ở learner subscription" + "xác nhận khoảng trống ngách / không player MCQ thống trị" là SUY DIỄN. | Gắn nhãn INTERPRETATION; không tính là fact đã verify. |
| H6 | Grouping nghi vấn | Gộp CodeRabbit/Sourcery (dev tooling) chung với PentesterLab (security training) vào "một nhánh phân mảnh" — hai loại sản phẩm khác bản chất. | Tách nhóm; phân loại đúng từng đối thủ. |
| H7 | Numeric discrepancy (nhẹ) | Codecademy Trustpilot cite ~1,458 reviews; live thực 1,468 (lệch 10). | Sửa số; hướng claim vẫn đúng. |
| H8 | Omitted detail | DataCamp Trustpilot nêu 4.6/5 không kèm count; live có ~800 reviews. | Bổ sung count; không mâu thuẫn. |
| H9 | Mis-weighted cause | Codecademy 2.4/5 — nguồn weight BILLING nặng hơn "shallow content", claim framing nghiêng content. | Cân lại: billing là nguyên nhân chính theo nguồn. |
| H10 | Garbled source text | Nhãn segment Business Research Insights bị paraphrase/máy-dịch lỗi ("Paid learning fashions", "get admission to"). | Đọc cẩn trọng; không trích nguyên văn nhãn lỗi. |
| H11 | False source attribution | (R01) một claim bị gắn sai nguồn (bị cắt trong log) — đã cờ FALSE SOURCE ATTRIBUTION. | Quarantine claim đến khi re-verify nguồn. |

**Pattern lặp lại cần cảnh giác**: phần lớn lỗi là **attribution mismatch / live-drift trên số liệu market-sizing** — đây là loại số DỄ stale và dễ gán sai publisher nhất. Quy tắc: với mọi số TAM/SAM, luôn ghi rõ publisher + năm + URL + ngày verify, và coi là tham chiếu tier chứ không phải sự thật tuyệt đối.

---

## 5. Giả định CHƯA kiểm chứng — cần test tiếp

> Đây là các con số/luận điểm KHÔNG có `[n]` chống lưng — toàn bộ là giả định nội bộ. Mỗi cái cần một thí nghiệm rẻ, có ngưỡng pass/fail rõ ràng. **Không tiêu tiền infra trước khi A1–A3 có kết quả.**

| ID | Giả định chưa kiểm chứng | Thí nghiệm kiểm chứng | Ngưỡng pass (đề xuất, cần user chốt) |
|----|--------------------------|------------------------|--------------------------------------|
| **A1** | Có cầu thật cho "luyện JUDGE code" (người sẵn sàng để lại email). | Waitlist durable + landing repositioned, đẩy 1–2 kênh organic (HN/Reddit/SO). Đo conversion visitor→email. | ≥ X% visitor→waitlist trong N tuần (X/N do user đặt; tham chiếu ngành để tránh ảo tưởng). |
| **A2** | Người dùng sẵn sàng TRẢ TIỀN (không chỉ thích ý tưởng). | Fake-door `/pricing` 3 tier + bắt click "Subscribe" → intent capture cookieless. | Tỷ lệ click-Subscribe / waitlist đủ cao để vượt threshold freemium ngành 2.6% [25]. |
| **A3** | Ngách "Security-Review Interview Prep" (ICP R03) là segment mua mạnh nhất. | Onboarding 2-bước route theo JTBD + waitlist phân-khúc theo ICP. So sánh conversion giữa các ICP. | Một ICP tách rõ về intent/conversion so với phần còn lại. |
| **A4** | Conversion/retention sẽ đạt mức nuôi được unit economics. | Đo D1/D7/D30 retention + freemium→paid thật sau khi có core loop + account. | Vượt baseline ngành (freemium 2.6% [25]; chống completion ~3% MOOC [32]). |
| **A5** | Growth loop hữu cơ (share `/q/<id>` + daily challenge) tạo viral/re-entry đủ giảm CAC. | Ship SSR permalink + OG cards + Daily Challenge; đo K-factor & share→visit→signup. | K-factor và re-entry rate đủ để CAC organic < ngưỡng (chống CAC >50% [36]). |
| **A6** | EN-first mở được top-funnel PH/HN/SO mà không loãng định vị. | i18n landing + `?lang` gating + load `questions_en_full.json`. So traffic/quality EN vs VI. | EN kênh organic mang lead chất lượng ≥ VI. |
| **A7** | `/api/code_review` AI tool là wedge trả-tiền thật (không chỉ nice-to-have). | Sau khi gate cost, đo usage + intent-to-pay cho tool này riêng. | Tool có retention/intent vượt phần content tĩnh. |
| **A8** | Giá $5/th–$40/năm là điểm tối ưu cho ngách (không phải anchor mù từ đối thủ). | A/B 2–3 mức giá trên fake-door. | Một điểm giá tối đa hoá (conversion × ARPU) rõ rệt. |
| **A9** | Định giá đối thủ tham chiếu vẫn đúng tại thời điểm launch. | Re-verify giá Codewars/LeetCode/Educative/Sourcery ngay trước GTM (giá DỄ drift — xem H3). | Giá khớp live; nếu drift → cập nhật anchor. |
| **A10** | Content 286 câu Python đủ depth giữ chân tới điểm trả tiền. | Đo hoàn thành stage + drop-off theo độ khó trên cohort thật. | Không có cliff drop-off trước paywall; hard 39 câu đủ cho Pro tier. |
| **A11** | AI question gen offline (gated `validate.py`) giải được bài toán cung nội dung ở chất lượng chấp nhận được. | Chạy batch + đo pass-rate qua validate (schema/exec/dedup/pedagogy) + human spot-check. | Pass-rate đủ cao + hallu < ngưỡng (baseline đã đo 16.67% lỗi cần hạ). |

---

## 6. Cổng kiểm chứng (Validation Gates) — thứ tự thực thi

> Nguyên tắc: **không nhảy gate**. Mỗi gate có blocker kỹ thuật + tín hiệu cầu phải đạt trước khi mở chi tiêu vòng sau.

1. **Gate 0 — Đo cầu (no infra spend)**: Waitlist durable (T4 fix) + analytics cookieless + landing repositioned + fake-door `/pricing`. → Pass A1, A2 mới qua.
2. **Gate 1 — Đóng lỗ cấu trúc**: Server-side grading `/api/round`+`/api/check`, đóng rò `correct_idx` (T1), thêm cột `tier`. *Bắt buộc trước mọi paywall.*
3. **Gate 2 — Account & sync** (chỉ khi A1/A2 pass): GitHub OAuth stateless + cloud progress sync (T2) + Postgres HTTP-driver (T3).
4. **Gate 3 — Monetization** (chỉ khi A2/A8 pass): Stripe-hosted Checkout + signed entitlement + idempotent webhook; privacy/GDPR (L1) bật cùng capture.
5. **Gate 4 — AI wedge & scale** (chỉ khi A7 pass): `/api/code_review` gated; AI gen offline; 4 Golden Signals + SLO.

---

## 7. Theo dõi (Cần đo từ ngày đầu)

- **Funnel**: page → quiz-start → waitlist → pricing-click (PostHog cookieless, REJECT pricing teaser/hero rewrite vì monetization premature).
- **Retention**: D1/D7/D30 (chống MOOC churn [32][33]).
- **Demand**: visitor→email conversion, click-Subscribe rate (vs freemium 2.6% [25]).
- **Growth**: K-factor share loop, re-entry từ daily challenge.
- **Trust (metric thật, KHÔNG phóng đại)**: 286 câu live / 273 có sources / 15 stage — render từ improvement_log thật.
- **Unit economics** (khi có billing): LTV:CAC, ARPU theo tier, churn (chống CAC >50% [36], EdTech profitability [34]).

---

## 8. Ghi chú kỷ luật sản phẩm

- **KHÔNG mở 5 ngôn ngữ / feature creep** trước PMF — chống "indistinguishable competitors" [37].
- **KHÔNG build Stripe/DB/auth** trước khi A1–A2 pass — chống infra burn trước doanh thu [34][36].
- **KHÔNG trộn số nội bộ với số đã verify** — mọi con số không `[n]` là giả định (Mục 5).
- **Monetization premature bị REJECT có chủ đích**: pricing teaser + hero rewrite hoãn; chỉ giữ fake-door để ĐO, không để BÁN.
- **Mọi số market-sizing phải re-verify trước GTM** — loại số DỄ drift nhất (H1–H3).