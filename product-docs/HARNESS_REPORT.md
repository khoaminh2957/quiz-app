# HARNESS REPORT — Product Evolution (20 vòng × 21 agent)

> Tự động sinh bởi `harness/product_evolution_harness.js`. **426 agent**, **920 phát hiện verified**, **581 cờ ảo giác bị loại**.

## Phương pháp
Mỗi vòng = 8 research agent (WebSearch/WebFetch nguồn thật) → 8 verify agent (kiểm chứng độc lập, anti-hallucination) → 3 improve agent (3 góc product/eng/business) → 1 judge (P0/P1/P2) → 1 synth (cập nhật trạng thái tích luỹ). 6 agent cuối dựng tài liệu end-to-end.

## Quỹ đạo readiness theo vòng

| Vòng | Trục | Verified | Ảo giác bắt | Round score | Readiness |
|---|---|---|---|---|---|
| 01 | Market & Demand Validation | 43 | 29 | 3.5 | 2.5/10 |
| 02 | Competitor Landscape & Differentiation | 44 | 28 | 5 | 3.5/10 |
| 03 | Target Users, ICP & JTBD | 52 | 30 | 4 | 3.5/10 |
| 04 | Value Proposition & Positioning | 36 | 26 | 5.5 | 4/10 |
| 05 | Pricing & Monetization Model | 47 | 27 | 3 | 3.5/10 |
| 06 | Core Feature Set for Market Fit | 53 | 29 | 4 | 4/10 |
| 07 | AI-Powered Features | 45 | 26 | 4 | 5.5/10 |
| 08 | Accounts, Auth & Data Model | 48 | 19 | 3 | 3.5/10 |
| 09 | Backend Architecture & Database | 48 | 26 | 3 | 4.5/10 |
| 10 | Payments & Billing | 52 | 33 | 2 | 2.5/10 |
| 11 | Content Strategy & Question-Bank Scaling | 42 | 33 | 3 | 3.5/10 |
| 12 | Pedagogy & Learning Efficacy | 48 | 27 | 4 | 3.5/10 |
| 13 | UX/UI & Onboarding Redesign | 52 | 30 | 4.5 | 3.5/10 |
| 14 | Growth, SEO & Acquisition | 49 | 31 | 4 | 4/10 |
| 15 | Retention, Engagement & Gamification | 49 | 35 | 6 | 3.5/10 |
| 16 | Analytics, Metrics & Experimentation | 41 | 27 | 4 | 2.5/10 |
| 17 | Security, Privacy & Compliance | 47 | 30 | 4 | 3.5/10 |
| 18 | Scalability, Reliability & Infra | 44 | 33 | 3.5 | 3.5/10 |
| 19 | Brand, Trust & Social Proof | 35 | 29 | 4 | 3.5/10 |
| 20 | Launch Plan & GTM Execution | 45 | 33 | 4 | 4.5/10 |

## Backlog hợp nhất (mọi đề xuất được JUDGE chấp nhận)

### P0 (27)
- **(R01)** Analytics funnel nhẹ + fake-door pricing để đo mức sẵn-sàng-trả tiền (PHẦN ANALYTICS: gắn Plausible/PostHog cookieless)
- **(R01)** Email waitlist capture lưu vào managed store + double-opt-in nhẹ
- **(R02)** Reposition landing against named competitors: "They make you WRITE code. We train you to JUDGE it."
- **(R03)** Track 'Security-Review Interview Prep' làm ICP mũi nhọn
- **(R03)** Persona-based question-pack endpoint từ taxonomy 6-category sẵn có
- **(R04)** Viet lai hero landing theo Dunford: JUDGE code khong WRITE code
- **(R05)** Fake-door /pricing page + 3 market-anchored tiers + cookieless intent capture (waitlist/event log, zero billing code)
- **(R06)** Ship a scored "Review Round" loop with a per-category result screen (the missing core mechanic)
- **(R06)** Cham diem server-side + payload khong lo dap an (/api/check)
- **(R07)** Endpoint /api/code_review: dán code, AI review server-side có quota + cache
- **(R08)** Cloud progress sync: lift the existing localStorage blob to a per-user row
- **(R08)** GitHub/Google OAuth (single method) + server session, no passwords
- **(R09)** Đóng rò đáp án + enforce free/pro phía server bằng split round/check + cột tier
- **(R10)** Stripe Checkout + signature-verified webhook làm xương sống doanh thu (P0)
- **(R10)** Cột `tier` trong schema + entitlement check server-side khoá nội dung Pro (P0)
- **(R11)** Khử rò rỉ vị trí + độ dài đáp án (answer-key debias) trên toàn bank
- **(R12)** Nối nốt Spaced Repetition: biến due-list thành phiên luyện chạy được (/review?mode=due)
- **(R13)** Instant first-question onboarding on landing (time-to-value <10s, no account) — merge of the two zero-click variants
- **(R14)** Programmatic SEO: per-question route /q/<id> server-rendered + sitemap.xml + robots.txt + canonical/OG/JSON-LD (QAPage)
- **(R15)** Achievement/badge engine kích hoạt ngay ngày-1 + confetti milestone
- **(R16)** Tích hợp PostHog cookieless làm event pipeline P0 (1 snippet, anonymous client-ID)
- **(R17)** Bịt rò đáp án: /api/questions ngừng ship correct_idx + explain (server-side grading)
- **(R18)** Observability thật: stream log + Four Golden Signals ra sink durable
- **(R18)** Edge-cache /api/questions qua CDN + gzip/brotli + tách correct_idx server-side
- **(R19)** Biến source tag thành link kiểm chứng được (verifiable citations) — clickable citations + normalize tag variants
- **(R20)** Durable waitlist capture via serverless POST → external sink (Formspree/Sheets/Resend)
- **(R20)** Daily Code Review Challenge: SSR permalink /q/<id> + OG/Twitter cards + nút Share

### P1 (22)
- **(R01)** Fake-door pricing test: trang /pricing 3 tier + bắt click 'Subscribe' để đo willingness-to-pay
- **(R01)** Định vị lại landing quanh ngách 'Code-Review Skill' (CHỈ phần repositioning, KHÔNG mở 5 ngôn ngữ)
- **(R02)** Surface the 6-category flaw taxonomy as the product spine (filter + per-category mastery)
- **(R03)** Onboarding 2-bước chọn ICP → route theo JTBD (client-side, không DB)
- **(R03)** Waitlist phân-khúc theo ICP qua endpoint POST + managed store ngoài
- **(R04)** Endpoint /api/positioning read-only cho comparison table + one-liner
- **(R05)** Server-side free/premium content split (tier field + filtered question endpoints) to make any paywall enforceable
- **(R06)** Make the product English-first using the already-built EN dataset
- **(R07)** AI Question Generator gated bằng chính validate.py (anti-hallucination)
- **(R08)** Billing-ready data model + idempotent Stripe webhook scaffold
- **(R09)** Postgres serverless qua HTTP-driver (Neon/Supabase) + tách content store khỏi DB
- **(R10)** Webhook + bảng entitlement Postgres làm nguồn-sự-thật cho quyền Pro (không dùng localStorage)
- **(R11)** Chuyển 'sources' từ tag trần sang link nguồn thật (đúng value-prop)
- **(R12)** Đo learning gain: pre/post diagnostic + lưu confidence để chấm calibration
- **(R13)** Wire the already-built English content + EN/VI UI toggle (i18n) via ?lang=en -> questions_en_full.json
- **(R14)** Lightweight cookieless analytics (Plausible/Umami) to measure traffic source, landing, and conversion to a practice session
- **(R15)** Streak-freeze (đóng băng streak) client-side + cảnh báo nguy cơ mất streak
- **(R16)** Định nghĩa North-star + funnel activation D7 và dashboard cohort
- **(R17)** Dựng nền HTTP-security: CSP nonce + HSTS/X-Frame-Options/X-Content-Type + đóng /api/learners
- **(R18)** Công bố SLO uptime + error budget làm release control loop
- **(R19)** Trang /trust công khai: 'Vì sao tin đáp án đúng' + Cách kiểm định nội dung
- **(R20)** Localize top-of-funnel sang EN-first cho kênh launch quốc tế (i18n landing + ?lang)

### P2 (15)
- **(R02)** Anchor credibility on the SmartBear review methodology as a unique "why this works" badge
- **(R04)** Badge "Human skill AI won't replace" — neo vao use-vs-want gap
- **(R05)** Wire real Stripe-hosted Checkout + signed entitlement token for the Pro tier
- **(R06)** Add a "Judge the AI's code" mode that frames snippets as AI-generated
- **(R07)** AI Tutor 'Explain like a senior' theo từng câu — có nhãn tin cậy
- **(R09)** Tách content store (static, không DB) khỏi user-state store (Postgres)
- **(R10)** Pricing tier + thanh toán nội địa VN (Momo/VNPay) và Smart Retries chống rớt thu
- **(R11)** Calibration thực nghiệm P/D + provenance freshness để scale ngân hàng có kiểm soát
- **(R12)** Adaptive sequencing dùng est_difficulty đã có sẵn (Elo nhẹ trong localStorage)
- **(R13)** WCAG 2.2 tap-target sizing + visible keyboard-shortcut affordance (CSS-only + small '?' overlay)
- **(R14)** Daily code-review challenge with a stable dated URL /daily/<date> (index-able + OG), built on existing /api/daily
- **(R14)** Shareable scorecard: session/daily result page /result with dynamic OG image + native share to a play-now link
- **(R16)** A/B testing infra qua PostHog feature flags để thử nghiệm activation lever
- **(R17)** Khung pháp lý go-live tối thiểu: Privacy Policy + ToS + quyền access/delete (GDPR/CCPA/Nghị định 13 VN)
- **(R20)** Launch funnel instrumentation (cookieless PostHog) — analytics half only

## Chi tiết từng vòng

### R01 — Market & Demand Validation
*Verified 43 · Ảo giác bắt 29 · Readiness 2.5/10*

Vòng Market & Demand Validation chốt hướng: trước khi xây Stripe/DB/auth, phải ĐO cầu thật. Bằng chứng thị trường lớn (programming education $73B, online code-learning SAM $3.6B→$12.2B, CAGR ~14.5%; 82% dev tự học online) + benchmark giá đối thủ (Codewars Red $5/th, Sourcery $12/seat) đủ chứng minh TAM/định giá tham chiếu. Verify codebase: 0 analytics tag, 0 pricing/stripe, /api/client_errors chỉ logger.warning (0 lead), localStorage-only, không DB. 4 cải tiến được nhận: P0 analytics cookieless (Plausible/PostHog), P0 email waitlist lưu managed store ngoài (Vercel FS ephemeral), P1 fake-door /pricing 3 tier đo willingness-to-pay, P1 repositioning landing quanh ngách "Code-Review Skill". Loại phần mở 5 ngôn ngữ/EN. Lưu ý: /api/event CHƯA tồn tại — P0 analytics phải tạo route này để P1 pricing bắt event.

**Quyết định chính:**
- Chiến lược measure-before-build: cấm xây Stripe/DB/auth cho tới khi funnel + lead capture chứng minh cầu thật
- P0 — Gắn analytics cookieless (Plausible hoặc PostHog) + TẠO MỚI route /api/event (hiện chưa tồn tại) để đo funnel landing→quiz→Q5→complete; verified 0 analytics tag trong codebase
- P0 — Email waitlist ghi vào managed store NGOÀI (Supabase/Airtable/Sheet webhook) vì Vercel FS ephemeral; kèm source/UTM/lang để đo conversion theo kênh; verified hiện 0 lead (chỉ logger.warning)
- P1 — Fake-door /pricing 3 tier đo willingness-to-pay, khung giá bám benchmark thật (Codewars Red $5/th, Sourcery $12/seat); phụ thuộc P0 (cần /api/event + email trước)
- P1 — Repositioning landing quanh ngách 'Code-Review Skill' (chỉ sửa copy hero/why), nhấn 'đọc & bắt bug như reviewer'
- LOẠI BỎ: mở /en + 5 ngôn ngữ — giữ Python-only có chủ đích, EN content chưa deployable
- TAM/định giá đã xác minh: programming education $73B (2026), online code-learning SAM $3.6B→$12.2B (CAGR ~14.5%), 82% dev tự học online; ngách code-review chưa bị LeetCode/HackerRank đánh trực diện

### R02 — Competitor Landscape & Differentiation
*Verified 44 · Ảo giác bắt 28 · Readiness 3.5/10*

Vòng Competitor Landscape chốt định vị empty-lane: "Họ bắt bạn VIẾT code. Chúng tôi luyện bạn JUDGE code." Thị trường coding-ed ~14.7B (2024)→61.4B (2033, CAGR 18.2%) đủ lớn cho ngách; trust-gap AI có thật (chỉ 43% dev tin AI, 45% chê AI ở task khó) ủng hộ skill review thủ công. Đối thủ được định danh rõ: Codewars=TDD viết-và-chạy, Sourcery=AI thay reviewer (không phải nền tảng đào tạo) — đều không chiếm lane "judge code". 3 việc nhận: P0 reposition landing (Jinja/HTML, zero-backend), P1 lộ 6-category flaw taxonomy thành xương sống (grid + per-category mastery + filter), P2 badge phương pháp SmartBear. CẢNH BÁO: copy phải dùng số thật 286 câu (KHÔNG 1.141) nếu không thành overclaim phá vỡ trust.

**Quyết định chính:**
- P0 — Reposition landing với frame 'Họ bắt bạn VIẾT code, chúng tôi luyện bạn JUDGE code'; named comparison table (Codewars=TDD viết-và-chạy, Sourcery=AI thay reviewer). Pure Jinja/HTML, zero-backend, là storefront ship trước tiên.
- RÀNG BUỘC BẮT BUỘC — Mọi copy/marketing dùng số THẬT 286 câu Python; cấm tái dùng '1.141' (overclaim phá trust, đã xác minh questions.json=286).
- P1 — Đưa 6-category flaw taxonomy (style/bug/security/perf/concurrency/edge, đã verify cân bằng) thành xương sống sản phẩm: category grid + per-category mastery + /quiz filter; biến slogan P0 thành feature click được. Chỉ template+localStorage tally, no DB.
- P2 — /method page tĩnh anchor credibility trên SmartBear methodology (200-400 LOC/60-90min/70-90% defect-discovery); là nội dung MỚI phải author (chưa có trong research_refs.json), tận dụng infra citation sẵn có.
- Giữ ngách empty-lane 'judge code' được hậu thuẫn bằng evidence: thị trường lớn+tăng nhanh (CAGR 18.2%), AI trust-gap thật (43% tin / 45% chê task khó), đối thủ không chiếm lane này.
- Thứ tự: storefront message (P0) trước, rồi taxonomy grid (P1) mới có nghĩa, rồi method badge (P2) như trust-reinforcer tăng close-rate.

### R03 — Target Users, ICP & JTBD
*Verified 52 · Ảo giác bắt 30 · Readiness 3.5/10*

Vòng ICP & JTBD khoá được MỘT người-mua cụ thể: track "Security-Review Interview Prep" cho bootcamp grad / job seeker với JTBD rõ "pass code-review round". Ngách này Codewars (TDD) và Sourcery/CodeRabbit (B2B AI reviewer) đều bỏ trống, khả thi NGAY trên content thật (46 security + 60 bug + 39 hard + misconception_map phủ cả 286 câu, không sinh content mới). Backbone kỹ thuật là persona→pack endpoint read-only từ taxonomy 6-category sẵn có (clone pattern /api/roadmap cache 3600s). Hai cơ chế đo phân-khúc: onboarding 2-bước client-side route theo JTBD (reuse filter quiz.js) và waitlist phân-khúc qua POST + managed store ngoài (clone api_client_errors, Vercel ephemeral). Sản phẩm chuyển từ "nền tảng vô danh tính ICP" sang "có 1 ICP trả-tiền-được + đường đo nhu cầu". Vẫn chưa có auth/DB/payment/AI; UI tiếng Việt.

**Quyết định chính:**
- ICP mũi nhọn KHOÁ vào 'Security-Review Interview Prep' cho bootcamp grad/job seeker, JTBD đơn 'pass code-review round' — biến nền tảng vô danh tính thành sản phẩm có 1 người-mua cụ thể (P0, impact high/effort low, content thật đủ phủ)
- Persona→question-pack endpoint là backbone kỹ thuật bắt buộc cho mọi track ICP: dict Python tĩnh map persona→filter(topic/difficulty/stage_id), read-only, cache 3600s theo pattern /api/roadmap — dependency của track lẫn onboarding (P0)
- Onboarding 2-bước CLIENT-SIDE (không DB): chọn bản effort=low reuse filter quiz.js + query-param, ship SAU khi pack endpoint sống để routing có đích (P1)
- Waitlist PHÂN-KHÚC theo ICP (B2C learner vs B2B team-lead) qua POST + managed store ngoài (Formspree/Sheets, vì Vercel filesystem ephemeral) — bằng chứng thị trường rẻ nhất, cần persona prefill + track sống (P1)
- Định vị cạnh tranh xác nhận: Codewars=TDD freemium, Sourcery/CodeRabbit/Greptile=B2B per-seat AI reviewer — không ai có learner/educational code-judging angle; Python #1 trong segment 'Learning to Code' (66.4%) củng cố Python-only

### R04 — Value Proposition & Positioning
*Verified 36 · Ảo giác bắt 26 · Readiness 4/10*

Vòng này khoá positioning làm trục bán hàng. JUDGE chấp nhận 3 cải tiến: (P0) viết lại hero landing.html theo Dunford — "JUDGE code KHÔNG WRITE code" thay câu chung-chung hiện tại, có 286 câu all-judge-format + 6 loại flaw chống lưng (không phóng đại); (P1) endpoint /api/positioning read-only phục vụ comparison table + one-liner, clone pattern /api/roadmap (dict tĩnh + cache 3600s), tách data khỏi template, dễ CDN trên Vercel; (P2) badge "Human skill AI won't replace" neo vào SO 2024 use-vs-want gap (13.2% dùng / 40.9% muốn), reuse research_refs.json citation, cần footnote nguồn rõ tránh cherry-pick. Thứ tự thực thi cứng: hero → comparison → badge. Các định hướng ICP/onboarding/waitlist từ vòng trước vẫn treo, chưa ưu tiên vòng này.

**Quyết định chính:**
- P0 — Viết lại hero landing.html theo Dunford: thông điệp canonical 'JUDGE code KHÔNG WRITE code', thay câu chung-chung dòng 31; gộp 3 đề xuất hero trùng lặp thành 1; chỉ sửa Jinja template, 0 endpoint/DB (high-impact/low-effort).
- P1 — Thêm endpoint /api/positioning read-only (dict tĩnh + _add_cache_headers 3600s, clone /api/roadmap) phục vụ comparison table + one-liner; chọn kiến trúc endpoint thay vì Jinja static dict để nhất quán codebase, dễ cache/CDN Vercel, tách data khỏi template.
- P2 — Badge 'Human skill AI won't replace' neo vào SO 2024 use-vs-want gap (13.2% dùng / 40.9% muốn), reuse research_refs.json citation pattern; là message bổ-trợ, cần footnote nguồn rõ để tránh cherry-pick stat.
- Thứ tự thực thi cứng: hero (positioning gốc) → comparison table → badge; comparison/badge vô nghĩa nếu hero chưa định positioning.
- Các định hướng ICP/onboarding/waitlist/analytics/fake-door từ vòng trước vẫn treo, KHÔNG ưu tiên trong vòng positioning này.
- Không thay đổi ranh giới phạm vi: vẫn chưa làm auth/DB/payment/AI; tất cả cải tiến vòng này là frontend + 1 read-only endpoint, không động tới scope lớn.

### R05 — Pricing & Monetization Model
*Verified 47 · Ảo giác bắt 27 · Readiness 3.5/10*

Vòng Pricing & Monetization chốt một track 3 bước theo thứ tự gate. P0: dựng fake-door /pricing (Jinja page + pricing.json config endpoint clone pattern _add_cache_headers(jsonify,3600) của /api/roadmap, thêm vào vercel.json includeFiles) cùng intent/waitlist capture cookieless tái dùng POST /api/client_errors — đo willingness-to-pay TRƯỚC khi tốn infra. P1 (gated bởi demand): server-side free/premium split, tag 39 hard + security/concurrency = tier=pro, filter CẢ 3 path serve câu hỏi (/api/questions, /api/stage, /api/lang/.../stage) để không leak paywall, giữ quiz/roadmap chạy cho free. P2 (gated bởi P0+P1): Stripe-hosted Checkout + signed JWT entitlement trong localStorage. Tier anchor: Free $0 / Pro $12-mo hoặc $99-yr / Team ~$15-19/seat, nằm trong market band đã verify.

**Quyết định chính:**
- Áp dụng monetization theo 3 gate tuần tự: P0 fake-door validate → P1 content split → P2 Stripe; cấm xây bước sau khi bước trước chưa pass (tránh tốn infra/leak access).
- P0: gộp 3 đề xuất fake-door/pricing trùng lặp thành MỘT deliverable — /pricing Jinja page + pricing.json config endpoint (clone _add_cache_headers(jsonify,3600) của /api/roadmap, thêm vào vercel.json includeFiles) + intent/waitlist capture reuse POST /api/client_errors structured-logger, không PII/cookie, không billing.
- Tier anchor đặt trong market band đã verify: Free $0 / Pro $12/mo hoặc $99/yr / Team ~$15-19/seat (tham chiếu Sourcery $12-24, LeetCode $35/mo·$159/yr, Educative ~$134-200/yr), tôn trọng guidance 2-4 tier.
- P1 hạ xuống P1 và CONDITIONAL theo demand: phải filter CẢ 3 path serve câu hỏi (/api/questions, /api/stage/<id>, /api/lang/<lang>/stage/<id>) để paywall không leak; tag 39 hard + security/concurrency = tier=pro; giữ quiz.js và lang_roadmap.js chạy cho item free.
- P2 Stripe-hosted Checkout + signed JWT-in-localStorage làm proof-of-purchase, tránh cần user DB cho v1; nhưng đây là bề mặt secrets/webhook đầu tiên nên strictly gated bởi cả P0 (proven WTP) lẫn P1 (boundary enforceable).
- Market-size macro ($14.7B→$61.4B, EdTech $36.1B→$120.4B) chỉ là color, KHÔNG load-bearing cho quyết định gate.
- Chưa viết bất kỳ code monetization nào vòng này — toàn bộ vẫn là plan có scope rõ; trạng thái thực tế vẫn KHÔNG auth/DB/payment/pháp lý.

### R06 — Core Feature Set for Market Fit
*Verified 53 · Ảo giác bắt 29 · Readiness 4/10*

Vòng "Core Feature Set" chốt 4 cải tiến đã được JUDGE xác minh trên codebase thật. Hai P0 nền tảng: (1) một "Review Round" loop có chấm điểm và màn result theo từng category (style/bug/security/concurrency/perf/edge) — mechanic còn THIẾU khiến content browser chưa thành sản phẩm bán được; (2) chấm điểm server-side qua /api/round + /api/check, KHÔNG trả đáp án trong payload — bịt lỗ rò /api/questions lộ correct_idx, điều kiện cấu trúc bắt buộc trước mọi paywall. P1: English-first dùng dataset EN 1141 câu đã có sẵn để mở rộng thị trường. P2: mode "Judge the AI's code" làm wedge khác biệt. Build round dựa trên LIVE path lang_lesson.html/.js, KHÔNG phải quiz.js.

**Quyết định chính:**
- P0 — Ship 'Review Round' loop có scoring + per-category result screen (mechanic CORE còn thiếu), build trên LIVE path lang_lesson.html/.js chứ KHÔNG phải quiz.js
- P0 — Chấm điểm server-side: /api/round trả payload KHÔNG đáp án + /api/check scores; bịt lỗ rò /api/questions (app.py:238) lộ correct_idx/explain/misconception_map. Điều kiện cấu trúc BẮT BUỘC trước mọi paywall
- Hai P0 phải land cùng nhau (round loop vô nghĩa nếu scoring vẫn ở browser); free/pro split đã schema-ready 183 free/103 pro
- P1 — English-first: tận dụng dataset EN 1141 câu đã có (questions_en_full.json), thêm ?lang switch + includeFiles + dịch chrome ~13 template; sequenced SAU 2 P0 để tránh churn
- P2 — Mode 'Judge the AI's code' frame snippet là AI-generated, dùng misconception_map sẵn có làm wedge khác biệt; là re-skin chỉ có giá trị sau khi loop+server-scoring tồn tại
- Giữ stateless trên Vercel, không thêm DB/auth trong vòng này; monetization vẫn theo gate P0 fake-door → P1 split → P2 Stripe

### R07 — AI-Powered Features
*Verified 45 · Ảo giác bắt 26 · Readiness 5.5/10*

Vòng AI-Powered Features bổ sung trục AI thực sự lên trên core loop Review Round đã có. Chốt 3 tính năng: (P0) /api/code_review — dán code, AI review server-side, gate chi phí bằng giới hạn ký tự + hash-cache KV + quota cookie/IP + timeout serverless; đây là wedge bán-được duy nhất, biến app từ quiz tĩnh thành công cụ dùng thật, đánh đúng gap cầu lớn nhất (40.9% muốn vs 13.2% dùng AI cho code review). (P1) AI Question Generator chạy OFFLINE batch, gated bằng validate.py (schema + code-exec + dedup + pedagogy) chống hallucination 16.67% gần-free, giải bài toán cung nội dung. (P2) AI Tutor "Explain like a senior" per-câu có nhãn tin cậy, dựa misconception_map/explain/sources đã verify 286/286, làm retention layer pro-gate thứ 2. Thứ tự ship: code_review trước, hai cái sau theo sau khi wedge có user.

**Quyết định chính:**
- P0: build /api/code_review — endpoint AI review server-side, là wedge bán-được duy nhất biến app từ quiz tĩnh thành công cụ dùng thật, đánh gap cầu 40.9% muốn vs 13.2% dùng AI
- Kiến trúc chi phí cho code_review: giới hạn ký tự input + hash-cache KV (dedup request giống nhau) + quota theo cookie/IP + timeout serverless — khả thi trên Vercel stateless
- Route code_review TÁCH RIÊNG, KHÔNG dùng lại pattern /api/questions (đã rò correct_idx tại app.py:238 do json.dumps cả đáp án)
- Monetization của code_review: free 3 review/ngày, pro unlimited — feature trả-tiền trực tiếp đầu tiên của app
- P1: AI Question Generator chạy OFFLINE batch (không đụng timeout/chi phí runtime Vercel), gated bằng validate.py có sẵn (schema Draft2020 + code-exec đa-ngôn-ngữ + jaccard dedup + pedagogy) để chặn hallucination 16.67% gần-free; giải bài toán cung nội dung (hiện 286 câu 100% Python)
- P2: AI Tutor 'Explain like a senior' per-câu có NHÃN TIN CẬY, dựa context đã verify (286/286 misconception_map+explain, 273 sources) để giảm rủi ro hallucination; là pro-gate retention layer thứ 2, KHÔNG phải wedge
- Thứ tự ship cứng: code_review (P0) phải có user trước, rồi mới Question Generator (P1, content backstage), cuối là AI Tutor (P2, retention)
- Chấp nhận harness dedup dùng jaccard thay vì cosine như mô tả — vẫn đủ tốt làm gate anti-hallucination

### R08 — Accounts, Auth & Data Model
*Verified 48 · Ảo giác bắt 19 · Readiness 3.5/10*

Vòng "Accounts, Auth & Data Model" chốt 3 quyết định nền tảng cho monetization. P0: Cloud progress sync — nâng blob localStorage hiện có (schema_v:2) thành row per-user qua progress(user_id PK, state_json JSONB, updated_at), GET/PUT /api/progress, field-merge (max xp/streak, union attempts/badges), giữ localStorage làm offline cache + anon fallback; vá đúng lỗi mất tiến độ kiểu freeCodeCamp #16147. P0: OAuth ĐƠN phương thức (GitHub, hợp dev audience như Exercism) + server-session cookie httpOnly stateless (JWT/signed, KHÔNG in-process vì Vercel stateless), provider_uid UNIQUE chống duplicate-account, né hoàn toàn OWASP password liability. P1: data model billing-ready + Stripe webhook idempotent (processed_events event_id PK, provision invoice.paid, revoke canceled/payment_failed, gate qua users.plan server-side) — chưa phải launch blocker vì chưa có premium content/tier field.

**Quyết định chính:**
- P0 Cloud progress sync: nâng blob localStorage (schema_v:2) thành row progress(user_id PK, state_json JSONB, updated_at) với GET/PUT /api/progress, field-merge (max xp/streak, union attempts/badges); giữ localStorage làm offline cache + anon fallback — vá lỗi mất tiến độ kiểu freeCodeCamp #16147; là keystone của cả trục vì không có durable progress thì account không đáng trả tiền.
- P0 OAuth ĐƠN phương thức (GitHub, hợp dev audience như Exercism) với provider_uid UNIQUE chống duplicate-account; identity là tiền đề bắt buộc cho sync + billing (cần user_id để key row).
- P0 Session: server-session cookie httpOnly STATELESS (JWT hoặc signed cookie, KHÔNG in-process session vì Vercel functions stateless); né hoàn toàn OWASP password-storage liability.
- P1 (không phải launch blocker) Billing-ready data model + Stripe webhook idempotent: processed_events(event_id PK) chống double-provision, provision trên invoice.paid, revoke trên canceled/payment_failed, gate pro qua users.plan server-side thay vì client state.
- Sequencing: ship auth + sync trước để retain user, dựng premium surface thật (hiện ZERO premium content/tier field trong questions.json), rồi mới bật billing; scaffold billing land sớm để model billing-ready nhưng chưa launch-blocking.

### R09 — Backend Architecture & Database
*Verified 48 · Ảo giác bắt 26 · Readiness 4.5/10*

Vòng Backend & Database chốt 3 quyết định, gộp cụm 4 đề DB trùng lặp thành 1. P0 (blocker bán-hàng): đóng rò đáp án — split /api/round (strip correct_idx/explain) + /api/check chấm server-side + thêm cột tier để enforce paywall; verified /api/questions (app.py:236-247) đang serialize toàn bộ đáp án (VI 397KB LIVE) và schema 20 keys KHÔNG có tier. P1: chốt Postgres serverless qua HTTP-driver (Neon/Supabase Pro) né TCP-pool exhaustion trên Vercel stateless, schema tối thiểu users/progress JSONB/processed_events. P2 (ADR design-principle): tách content store static (load 7.3ms, ETag/Cache-Control sẵn) khỏi user-state Postgres — cấm nhồi content 1.8MB vào DB. Readiness nhích nhờ chốt provisioning + integrity path, nhưng code chưa wiring.

**Quyết định chính:**
- P0 INTEGRITY/PAYWALL: split /api/round (strip correct_idx/explain) + /api/check chấm server-side + thêm cột tier — điều kiện cần tối thiểu để monetize; verified rò đáp án tại /api/questions app.py:236-247 (VI 397KB LIVE) và schema 20 keys không có tier
- P1 DB: chốt Postgres serverless qua HTTP-driver (Neon hoặc Supabase Pro) né TCP-pool exhaustion trên Vercel stateless; schema tối thiểu users/progress JSONB/processed_events cho idempotent webhook — đại diện cụm DB, reject 3 đề DB trùng lặp
- P2 ADR (design-principle, không effort riêng): content store static (load 7.3ms verified, ETag/Cache-Control sẵn) TÁCH khỏi user-state Postgres; cấm đưa content 1.8MB vào DB
- Reject: gộp 4 đề DB thành 1 quyết định provisioning cụ thể thay vì để các đề DB đứng riêng trùng lặp
- Xác nhận hiện trạng: app stateless, state chỉ ở localStorage → cần backend trước khi bán cross-device + gắn billing

### R10 — Payments & Billing
*Verified 52 · Ảo giác bắt 33 · Readiness 2.5/10*

Vòng Payments & Billing chốt xương sống doanh thu: hiện grep app.py = 0 dòng stripe/billing/webhook, không có secret_key, schema không có cột tier, và route duy nhất nhận POST là /api/client_errors (không verify chữ ký). Hai P0 đồng-trục: (1) Stripe Hosted Checkout + webhook verify construct_event + processed_events PK idempotency; (2) thêm cột tier + ký session (set secret_key) + entitlement check server-side. CẢNH BÁO thực thi đã xác minh: /api/round, /api/check, /api/code_review, /api/progress, OAuth ĐỀU KHÔNG TỒN TẠI; điểm gate đọc thật là /api/questions (app.py:236) đang dump full QUESTIONS gồm đáp án+explain — phải vá leak này cùng lúc nếu không paywall bị scrape bypass. Entitlement nguồn-sự-thật ở Postgres (P1), không localStorage. Pricing $5/th–$40/năm quyết sớm; Momo/VNPay hoãn P2.

**Quyết định chính:**
- P0: Stripe Hosted Checkout (PCI ra ngoài scope) + webhook verify construct_event + processed_events(event_id PK) idempotency — xương sống thu tiền, hiện app.py có 0 dòng stripe/webhook, chỉ /api/client_errors nhận POST không verify chữ ký
- P0 đồng-trục: thêm cột tier vào schema + set secret_key để ký session (cả hai hiện THIẾU) + entitlement check server-side; không có hai thứ này thì không phân biệt free/pro server-side, paywall vô nghĩa
- P0 BẮT BUỘC cùng hạng mục paywall: vá leak /api/questions (app.py:236 dump full QUESTIONS gồm đáp án+explain) — nếu không, paywall bị bypass bằng scrape; các route gate trong đề xuất (/api/round, /api/check, /api/code_review) ĐÃ XÁC MINH KHÔNG TỒN TẠI
- P1: Postgres serverless HTTP-driver (Neon/Supabase) là nguồn-sự-thật cho entitlements + processed_events; localStorage (client-controlled) KHÔNG được làm nguồn quyền Pro; nội dung kỹ thuật chồng lấn 2 P0 nên coi là lớp hạ tầng củng cố, không phải hạng mục độc lập
- Pricing quyết sớm: Pro $5/tháng–$40/năm (benchmark Codewars Red $40/năm, LeetCode $159/năm, tránh bẫy donation kiểu Exercism); Smart Retries chỉ bật-flag nên gộp vào P0 Stripe
- P2 hoãn: Momo/VNPay là mở rộng thị trường, KHÔNG phải đường thu tối thiểu để launch; với team 1 người pre-revenue, dựng cổng nội địa trước khi có khách quốc tế đầu tiên là lệch ưu tiên — làm sau khi xương sống quốc tế chạy + có tín hiệu cầu VN

### R11 — Content Strategy & Question-Bank Scaling
*Verified 42 · Ảo giác bắt 33 · Readiness 3.5/10*

Vòng Content Strategy chốt 3 việc bán-được tự-chứa, không phụ thuộc endpoint phantom. P0 (#4): debias.py offline khử CỘNG HƯỞNG hai rò rỉ ground-truth — vị trí (B=66.9%, SQL=74.2%) và length-leak (đáp án đúng dài nhất 88.1%, EN 1005/1141); rebalance ~25%/option seed cố định + gate length vào validate.py. Học viên đang đoán đúng 67-88% mà không đọc code → phá construct validity của sản phẩm bán code-review; phải làm TRƯỚC mọi scaling. P1: sources_map.json biến 1552 tag trần (0 URL, 74 rỗng) thành link canonical bấm-được, cứu value-prop "explain+nguồn". P2: bỏ trần iter=12 (1019/1427 đang kẹt, khóa scaling), thêm provenance (created_at/content_version), cross-bank dedup VI∪EN cosine>=0.85; P/D thực hoãn tới khi có /api/check + traffic.

**Quyết định chính:**
- P0 BLOCKER bán-được #1: chạy debias.py offline khử ĐỒNG THỜI rò rỉ vị trí (B=66.9%, SQL=74.2%) và length-leak (đáp án đúng dài nhất 88.1%, EN 1005/1141) — rebalance ~25%/option seed cố định + viết lại distractor; chọn superset #4 thay #1 vì #1 chỉ xử lý vị trí.
- Thêm 2 gate vào validate.py: (a) phân phối vị trí đáp án ~đều, (b) đáp án đúng KHÔNG được là option dài nhất một cách hệ thống — chặn tái-nhiễm rò rỉ khi scale.
- KHÔNG scale bank trước khi debias: scale một bank rò rỉ chỉ nhân rò rỉ; debias + gate là tiền-điều-kiện cho mọi việc thêm câu.
- P1: sources_map.json (tag→canonical URL) + build-step làm giàu + gate chặn tag ngoài map — biến 1552 source-string (0 URL, 74 rỗng) thành link thật, cứu value-prop 'explain+nguồn'; xếp sau P0 vì bank vẫn usable khi đáp án đã debiased.
- P2: gỡ khóa scaling pipeline — bỏ trần schema iter=12 (1019/1427 câu đang kẹt), thêm provenance (created_at/content_version), cross-bank dedup VI∪EN cosine>=0.85 (thay dedup per-file).
- Hoãn P/D calibration thực nghiệm: phụ thuộc /api/check (chưa tồn tại) + cần response learner thật → chỉ có giá trị SAU khi có traffic, không phải đòn bán-được tức thì.
- Chọn #3 (superset) và loại #5: #3 thêm freshness/version/retire/cross-bank dedup ngoài phần P/D-from-/api/check chung.

### R12 — Pedagogy & Learning Efficacy
*Verified 48 · Ảo giác bắt 27 · Readiness 3.5/10*

Vòng Pedagogy chốt đóng "last-mile" của vòng học DUY NHẤT đã có đủ data: Spaced Repetition. P0 — biến due-list chết (mastery_perlang.js:44-59 chỉ render <li>) thành phiên luyện chạy được qua route MỚI /review-session (KHÔNG tái dùng /review ở app.py:154 vì nó render index.html flat), reuse runner + /api/questions cache, 0 DB, 0 phantom. P1 — truyền confidence vào recordAttempt (fix 1 dòng, state_migrate.js:95 hiện vứt data calibration) + pre/post diagnostic đo learning-gain (điểm-bán sư phạm). P2 — adaptive sequencing dùng est_difficulty IRT có sẵn, hoãn vì rủi ro pedagogy cao + xung đột mastery_gate. Nợ P0 hạ tầng (Stripe/leak/OAuth/Postgres/phantom endpoints) vẫn nguyên, chưa build.

**Quyết định chính:**
- P0: Đóng last-mile Spaced Repetition — tạo route MỚI /review-session render due-queue thành phiên luyện chạy được (reuse runner + /api/questions cache, 0 DB, 0 phantom endpoint); TUYỆT ĐỐI không tái dùng /review (app.py:154) vì nó render index.html flat quiz vô-pedagogy.
- Refactor bắt buộc cho P0: tách renderQ/submit khỏi runner IIFE (đang bind chặt STAGE_ID + stageData.mastery_gate ở lang_lesson.js:12,68,156) thành hàm tái dùng + stub gate logic + scaffold DOM IDs; effort thực là LOW-MEDIUM, không phải low.
- P1 quick win: thêm tham số confidence vào recordAttempt (state_migrate.js:95 hiện bỏ data calibration); fix 1 dòng để bật đo overconfidence/calibration.
- P1: pre/post diagnostic (8-10 câu/stage baseline + lặp sau gate, hiển thị Δ accuracy) là điểm-bán 'learning-gain hữu hình' nhưng không chặn ra mắt — đứng sau đóng vòng SRS.
- P2 HOÃN adaptive sequencing: dù 286 câu có est_difficulty IRT sẵn (lang_lesson.js:104 chỉ hiển thị), rủi ro theta Elo ad-hoc + xung đột mastery_gate (đo acc 20 câu gần nhất → bơm-phồng accuracy giả) → cần learning-gain (P1) trước để có tín hiệu.
- Pedagogy vòng này độc lập với hạ tầng phantom; toàn bộ nợ P0 (Stripe, leak /api/questions, OAuth, Postgres, /api/round//check//code_review) vẫn chưa build và là rào chính cho monetization/ra-mắt.
- debias.py + 2 leak-gate (vị trí B=66.9%, length-leak 88.1%) vẫn là tiền-đề bắt buộc TRƯỚC mọi scaling content.

### R13 — UX/UI & Onboarding Redesign
*Verified 52 · Ảo giác bắt 30 · Readiness 3.5/10*

Vòng UX/UI & Onboarding xác lập 3 cải tiến JUDGE chấp nhận, ưu tiên giảm bounce trước khi mở rộng thị trường. P0: instant first-question onboarding ngay trên landing (time-to-value <10s, no account) — swap landing.html:47-55 (4-step text wall) bằng phiên fetch /api/daily reuse quiz.js runner, localStorage 'seen_intro' + CTA 'Luyện tiếp', 0 route/0 DB; fold coachmark roadmap/mastery/review nếu rẻ. P1: wire EN content đã trả-tiền-nhưng-chưa-bán (questions_en_full.json 1141Q + 4 track JS/Go/SQL/Rust) qua ?lang/Accept-Language — phase 1 swap content (rẻ), phase 2 trích ~115 chuỗi Jinja qua t(). P2: WCAG 2.2 tap-target 44px + '?' shortcut overlay + fix html lang='en' sai (lesson/mastery/roadmap), CSS-only. Pedagogy/hạ tầng nợ giữ nguyên.

**Quyết định chính:**
- P0: Instant first-question onboarding ngay trên landing — bỏ 4-step text wall (landing.html:47-55), fetch /api/daily reuse quiz.js runner, localStorage 'seen_intro' + CTA 'Luyện tiếp', 0 route/0 DB; coachmark 3-step (roadmap/mastery/review) chỉ fold nếu rẻ
- P1: Wire EN content đã có sẵn (questions_en_full.json 1141Q, xác minh real EN khớp 286 VI id) + 4 track JS/Go/SQL/Rust qua ?lang/Accept-Language; split delivery — phase 1 swap question content theo lang (rẻ, unlock tracks), phase 2 trích ~115 chuỗi Jinja qua t()
- P1 sau P0: i18n mở rộng thị trường 82.1% self-taught EN nhưng phải fix bounce (onboarding) trước khi đáng dịch; defensible vì Exercism/Codecademy không ship UI i18n
- P2: WCAG 2.2 tap-target 44px (.copy-btn 20px→44px, .page-btn/.qmeta, @media max-width:600px) + '?' shortcut overlay, CSS-only, giữ :focus-visible + aria-live
- P2 fold: fix html lang='en' khai sai trên VI (lesson.html:2/mastery.html:2/roadmap.html:2 = SC 3.1.1 fail), 1 dòng/file bundle vào CSS pass
- Thứ tự ưu tiên vòng: giảm bounce (P0) → mở rộng market-reach (P1) → polish/a11y (P2); P0 cao nhất vì time-to-value là conversion bottleneck cho no-signup self-learn
- KHÔNG đụng /review (app.py:154 flat quiz) và giữ nguyên pedagogy SR + hạ tầng nợ (Stripe/OAuth/Postgres/leak fix) — vòng này thuần UX/UI content-tự-chứa trên stack hiện tại

### R14 — Growth, SEO & Acquisition
*Verified 49 · Ảo giác bắt 31 · Readiness 4/10*

Vòng Growth/SEO chốt: trục acquisition số 1 cho thương hiệu mới = Programmatic SEO. JUDGE chấp nhận 4 cải tiến, ưu tiên P0: per-question route /q/<id> server-rendered + sitemap.xml + robots.txt + canonical/OG/JSON-LD (QAPage) — codebase hiện 0 SEO surface, content nằm khoá trong /api/questions blob client-side, vô hình với crawler. P1: analytics cookieless (Plausible/Umami) làm backbone đo lường traffic/conversion. P2: /daily/<date> URL ổn định (crawl-freshness + return hook) và /result shareable scorecard + dynamic OG image (viral loop). CAVEAT quan trọng: chỉ ship SEO cho 286 câu Python mà app live thực load; 1,141 câu EN trong questions_en_full.json là backup chưa wire, KHÔNG free URL. Sequencing: SEO → analytics → daily/share.

**Quyết định chính:**
- P0 Programmatic SEO: ship /q/<id> server-rendered + sitemap.xml + robots.txt + canonical/OG/JSON-LD (QAPage) làm lever acquisition số 1 cho newcomer không thương hiệu — feasible ~1 Jinja route + 2 dynamic routes, 0 DB
- SCOPE CỨNG: SEO chỉ cho 286 câu Python app live thực load; KHÔNG claim 1,427 — 1,141 câu EN là backup chưa wire, treat re-wiring corpus như prerequisite riêng
- Consolidate proposals #1+#4 (near-duplicate) thành 1 ACCEPT SEO route; tách analytics ra khỏi #3
- P1 Analytics cookieless (Plausible/Umami) land ngay sau/cùng SEO làm measurement backbone — không có thì bay mù về CAC/conversion
- P2 /daily/<date> URL ổn định: multiplier trên P0/P1, build trên /api/daily đã có, KHÔNG phải prerequisite
- P2 /result shareable scorecard + dynamic OG image: ship SAU cùng — OG render Pillow/SVG-to-PNG là item fragile nhất trên Vercel Python (cold-start risk), và share loop chỉ compound khi đã có traffic đo được + landing index-able
- Sequencing bắt buộc: SEO (P0) → analytics (P1) → daily URL + share (P2); content đang khoá trong /api/questions blob client-side là rào cản crawler cần phá đầu tiên

### R15 — Retention, Engagement & Gamification
*Verified 49 · Ảo giác bắt 35 · Readiness 3.5/10*

Vòng Retention/Gamification chốt 2 cải tiến dựa-trên-bằng-chứng và verified-trong-code, zero infra. (P0) Achievement/badge engine kích hoạt ngày-1 + confetti milestone: vá dead code badges_earned (state_migrate.js:57 khai báo nhưng không bao giờ ghi), tái dùng spawnConfetti/modal của celebration.js; đảm bảo ≥1 badge dễ ngay session đầu. Đòn bẩy: day-1 achievement → 33.42% vs 20.36% retention (~64% lift). (P1) Streak-freeze client-side + banner cảnh báo nguy cơ mất streak: sửa hard-reset streak (state_migrate.js:123-136), thuần localStorage ~25 dòng; bằng chứng 17.19 vs 11.62 ngày (+48%), không dark pattern. P1 vì chỉ phát huy sau khi đã có cohort có-streak (badge day-1 lên kệ trước). Đều là item bán-được-hàng, củng cố loop onboarding→retention.

**Quyết định chính:**
- P0: Build Achievement/badge engine kích hoạt ngày-1 — vá dead code badges_earned (state_migrate.js:57), bộ badge cụ thể, đảm bảo ≥1 badge dễ trong session đầu; tái dùng spawnConfetti+modal của celebration.js cho confetti milestone streak/XP. Đòn bẩy day-1 achievement → 33.42% vs 20.36% retention.
- P1: Streak-freeze client-side + banner cảnh báo nguy cơ mất streak — sửa hard-reset streak (state_migrate.js:123-136), thuần localStorage ~25 dòng; +48% retention (17.19 vs 11.62 ngày), không dark pattern.
- Sequencing: badge day-1 (P0) phải lên kệ TRƯỚC streak-freeze (P1) vì freeze chỉ phát huy sau khi user đã có cohort có-streak nhiều ngày.
- Cả hai chọn zero infra, client-side, dựa trên gap đã verify trong code — ưu tiên impact-to-effort và tính 'bán-được-hàng' cho onboarding→retention loop.
- Không nâng readiness đáng kể: gamification cải thiện engagement nhưng hạ tầng P0 phantom (Stripe/gate/OAuth/Postgres) + corpus EN chưa loaded + SEO/UX nợ vẫn chặn ra thị trường trả-tiền.

### R16 — Analytics, Metrics & Experimentation
*Verified 41 · Ảo giác bắt 27 · Readiness 2.5/10*

Vòng Analytics chốt một sự thật cốt lõi đã verify: codebase quiz-app có ZERO instrumentation (không match posthog/ga4/amplitude trong bất kỳ .py/.js/.html nào — chỉ harness prompt nhắc tên). Không đo thì mọi quyết định feature/pricing/retention đều mù, nên đây là blocker của cả trục. JUDGE chấp nhận 3 đề xuất theo thứ tự cứng: (P0) tích hợp PostHog cookieless qua đúng pattern beacon đã có sẵn (fetch '/api/client_errors' keepalive:true, app.py:414), hook tại quiz.js:29 init + quiz.js:150 submit, dùng streak/xp/daily_completed (state_migrate.js:54-57) làm nguyên liệu activation; (P1) North-star "JUDGE đúng >=10 câu code-review trong 7 ngày đầu" + funnel D7 + cohort dashboard; (P2) A/B qua feature flags — hoãn tới khi đủ traffic. PostHog free 1M events/tháng khớp ràng buộc serverless no-DB.

**Quyết định chính:**
- P0 — Dựng PostHog cookieless làm event pipeline nền của cả trục: tái dùng pattern beacon đã verify tồn tại (fetch '/api/client_errors' keepalive:true tại app.py:414), instrument 2 hook quiz.js:29 (init) + quiz.js:150 (submit) với anonymous client-ID; lý do P0: ZERO instrumentation hiện tại (verified) khiến mọi quyết định feature/pricing/retention mù — đây là blocker chặn tất cả.
- P1 — Định nghĩa North-star 'JUDGE đúng >=10 câu code-review trong 7 ngày đầu' + funnel activation D7 + cohort dashboard; gần zero code app (chỉ config PostHog), nhưng phụ thuộc cứng vào P0 phải chảy đủ event trước nên xếp sau, không P0.
- P2 — A/B testing infra qua PostHog feature flags (cùng snippet P0, free tier, no backend mới): hoãn vì pre-revenue chưa đủ traffic đạt significance; cần baseline (P0) + North-star (P1) + user thực trước.
- Stack & chi phí: PostHog free 1M product-analytics events/tháng + 1M feature-flag requests/tháng + 5k session replays — khớp ràng buộc serverless no-DB, không phát sinh chi phí ở quy mô hiện tại; D7 retention là leading indicator đã được Amplitude xác nhận (69% top-D7 cũng top 3-tháng).
- Sequencing bắt buộc: P0 (pipeline) → P1 (North-star/funnel) → P2 (A/B); KHÔNG đảo, vì định nghĩa funnel khi chưa có event = chỉ là tài liệu, và A/B khi chưa có traffic = vô nghĩa.

### R17 — Security, Privacy & Compliance
*Verified 47 · Ảo giác bắt 30 · Readiness 3.5/10*

Vòng Security/Privacy/Compliance xác định 1 blocker P0 thật: /api/questions (app.py:238) ship trọn correct_idx+explain+misconception_map+sources → ai cũng GET-scrape full đáp án, làm paywall code_review ($5/th) vô nghĩa = lỗ trực tiếp; fix = server-side grading (/api/grade), client bỏ phụ thuộc q.correct_idx. P1: dựng nền HTTP-security (CSP nonce cho 4 inline bootstrap, HSTS/X-Frame/X-Content-Type, đóng gate /api/learners + /api/cohort_progress + throttle /api/client_errors) — effort thấp, không thêm dep. P2: khung pháp lý go-live (Privacy Policy + ToS + access/delete GDPR/CCPA/Nghị định 13 VN, nêu rõ retention 30 ngày để vượt điểm yếu 'vague' của Codecademy) — forward-looking vì hiện chỉ 25 agent tổng hợp + localStorage, PII gần-zero. Đính chính: questions_en_full.json KHÔNG trong includeFiles; learner_registry chỉ rò qua /api/learners.

**Quyết định chính:**
- P0: Triển khai server-side grading (/api/grade hoặc /api/answer/<id>); /api/questions ngừng ship correct_idx+explain+misconception_map+sources — chống scrape full đáp án bảo vệ paywall code_review
- P0-scoping: Đây là blocker security thực sự DUY NHẤT của vòng; không nâng các header/legal lên P0 vì chúng không trực tiếp chặn việc bán
- P1: Dựng baseline HTTP-security trên Flask/Vercel — CSP nonce cho 4 inline bootstrap, HSTS/X-Frame-Options/X-Content-Type-Options, gate /api/learners + /api/cohort_progress sau auth, throttle /api/client_errors; gộp #2+#4 chọn bản nonce cụ thể
- P2: Khung pháp lý go-live tối thiểu (Privacy Policy + ToS + quyền access/delete GDPR/CCPA/Nghị định 13 VN) bằng Jinja tĩnh; nêu rõ retention + mốc 30 ngày để vượt điểm yếu 'vague' của Codecademy
- Đính chính trạng thái: questions_en_full.json KHÔNG nằm trong includeFiles (bỏ phần xoá file đó); learner_registry CÓ trong includeFiles nhưng chỉ web-reachable qua /api/learners → fix là gate endpoint, không xoá file
- Hoãn compliance đầy đủ: hiện chỉ 25 agent tổng hợp + localStorage (PII gần-zero), kích hoạt full GDPR/retention khi account/Stripe thật landing

### R18 — Scalability, Reliability & Infra
*Verified 44 · Ảo giác bắt 33 · Readiness 3.5/10*

Vòng infra xác nhận 1 P0 hạ-tầng-thật MỚI ngoài security: production hiện CÓ 0 observability (app.py:48-56 chỉ RotatingFileHandler ghi logs/app.log, FS Vercel ephemeral → mất log). Fix rẻ: StreamHandler(sys.stdout) + log sink $0; after_request (app.py:64-73) đã emit latency_ms/status/path nên 4 Golden Signals gần free. Gộp P0 security cũ: tách correct_idx/explain/sources/misconception_map khỏi /api/questions sang /api/grade server-side (chống scrape đáp án = blocker bán B2B). Edge-cache (thiếu s-maxage/CDN-Cache-Control) + brotli hạ xuống P1. Công bố SLO 99.5% + error budget + UptimeRobot/BetterStack cắm vào /debug/health là P1, làm SAU observability. Thứ tự đúng: observability → grade server-side → monitor+SLO.

**Quyết định chính:**
- Nâng Observability lên P0 hạ-tầng-THẬT: app.py:48-56 chỉ RotatingFileHandler → logs/app.log, FS Vercel ephemeral nên prod đang 0 observability; fix low-effort StreamHandler(sys.stdout) + log sink $0, tận dụng after_request 64-73 đã emit latency_ms/status/path cho 4 Golden Signals
- Giữ tách correct_idx/explain/sources/misconception_map ra server-side /api/grade là P0 security THẬT (scrape 1 request lộ toàn bộ đáp án = vô giá trị cho khách B2B/assessment)
- Hạ edge-cache /api/questions + brotli xuống P1 (đòn bẩy scale rẻ, không phải blocker bán hàng): hiện chỉ max-age=3600, thiếu s-maxage/CDN-Cache-Control nên Vercel chưa serve từ edge
- SLO 99.5% + error budget + UptimeRobot/BetterStack (cắm /debug/health đã có) là P1 làm SAU observability — công bố SLO khi chưa đo được là cam kết rỗng
- Thứ tự thực thi infra: observability (đo) → grade server-side (chống gian lận) → uptime monitor + SLO (cam kết khách B2B)
- Reject các bản dup: chọn observability bản #4 (low effort, line refs) thay #1; chọn grade bản #3 nêu rõ /api/grade

### R19 — Brand, Trust & Social Proof
*Verified 35 · Ảo giác bắt 29 · Readiness 3.5/10*

Vòng Brand/Trust khoá 2 đòn niềm tin rẻ-mà-load-bearing, đã verify trong code thật. P0: biến source tag thành CITATION BẤM ĐƯỢC — 273/286 câu có nguồn chuẩn (PEP/CWE/OWASP/python-docs) nhưng render text trần (.join ' · ') ở lesson.js:100 + lang_lesson.js:145, 0/207 tag clickable; thêm static/sources_map.json + build-time normalize biến thể (PEP-8=32, PEP 8=11) rồi sửa 2 dòng thành <a target=_blank>. P1: trang /trust công khai render tĩnh từ /api/research_refs (DOI thật: Soloway, Sorva, Robins, Lister, Hermans) + improvement_log + 12 iter review = '12 vòng kiểm định'; CHỈ metric thật (286/273/15 stage), KHÔNG đụng learner_registry (25 agent Monte Carlo). Trust align NN/G + Google E-E-A-T (Trust tối quan trọng nhất). P0 security/infra cũ vẫn nợ.

**Quyết định chính:**
- P0: Biến source tag thành CITATION BẤM ĐƯỢC — chọn proposal #4 (không #1) vì #4 nêu đúng cả 2 file render thật (lesson.js:99/100 + lang_lesson.js:144/145) và bắt buộc build-time normalize tag variants; chỉ thêm static/sources_map.json + sửa 2 dòng <a target=_blank>; wedge niềm tin rẻ nhất + chặn-bán-hàng số 1.
- Bắt buộc normalize biến thể tag tại build-time (confirmed PEP-8=32, PEP 8=11 trong questions.json) — không normalize thì map URL miss hàng loạt, citation chết.
- P1: /trust page công khai — chọn proposal #5 (low effort, render template tĩnh từ /api/research_refs đã có endpoint) thay vì #2 (medium); phơi tài sản E-E-A-T đang bị chôn (DOI thật Soloway/Sorva/Robins/Lister/Hermans + improvement_log + 12 iter review).
- /trust CHỈ dùng metric thật (286 câu/273 nguồn/15 stage); TUYỆT ĐỐI không đụng learner_registry vì honest_note xác nhận 25 agent Monte Carlo, không phải user thật — bịa social proof = vi phạm E-E-A-T/Trust.
- Grounding niềm tin theo NN/G Trustworthy Design (testimonial bên ngoài > tự-host; design quality + comprehensive/correct/current content) và Google E-E-A-T (Trust là thành phần quan trọng nhất).
- Trust improvements KHÔNG override P0 security (server-side grading) — citation/trust là wedge bán hàng nhưng grading lộ đáp án vẫn là blocker kỹ thuật phải fix trước khi monetize.

### R20 — Launch Plan & GTM Execution
*Verified 45 · Ảo giác bắt 33 · Readiness 4.5/10*

Vòng "Launch Plan & GTM Execution" chốt 4 quyết định bịt blocker 0→1. P0: (1) waitlist capture bền vững qua serverless POST → external sink (Formspree/Sheets/Resend) + honeypot + throttle/IP, vì codebase hiện convert 0 visitor → 0 contact (/api/client_errors chỉ log stdout ephemeral trên Vercel); (2) Daily Code Review Challenge có SSR permalink /q/<id> + OG/Twitter cards + nút Share, biến daily mechanic sẵn có thành growth loop (hiện ZERO og:/twitter: tag → share ra link chết). P1: localize top-of-funnel EN-first (i18n landing + ?lang), kích hoạt 1,141 câu EN dark inventory cho kênh PH/HN/SO. P2: chỉ nhận instrumentation PostHog cookieless (page→quiz-start→waitlist); TỪ CHỐI pricing teaser + hero rewrite vì monetization positioning premature khi chưa giữ được lead nào.

**Quyết định chính:**
- P0 — Build waitlist capture: serverless POST route → external durable sink (Formspree/Google Sheets/Resend), mirror /api/client_errors POST pattern, thêm honeypot + per-IP throttle; KHÔNG dựng KV/Upstash stateful infra trước khi validate demand
- P0 — Daily Code Review Challenge thành growth loop: SSR permalink /q/<id> + OG/Twitter preview cards + nút Share (reuse navigator.clipboard); biến /api/daily JSON-only thành shareable distribution primitive
- P1 — EN-first top-of-funnel: i18n landing.html (đang lang=vi) + ?lang gating, load questions_en_full.json (1,141 câu dark inventory) khớp kênh PH/HN/SO; xếp sau P0 vì capture phải tồn tại trước
- P2 — Chỉ nhận instrumentation PostHog cookieless (page→quiz-start→waitlist events) để đo channel conversion
- REJECT — Pricing teaser ($5/mo–$40/yr Reviewer tier) + hero copy rewrite: monetization positioning premature khi chưa giữ được 1 lead retained nào, out-of-scope cho unblock 0→1
- Giữ nguyên Trust Layer + Security/Infra debt ở backlog; vòng này ưu tiên GTM 0→1 capture+distribution trước khi đụng monetization/grading hardening
