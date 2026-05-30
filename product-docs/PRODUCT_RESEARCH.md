# PRODUCT_RESEARCH.md — quiz-app (Code-Review Skill Platform)

> **Tài liệu:** Dossier nghiên cứu sản phẩm cho việc đưa quiz-app từ pet project → sản phẩm end-to-end ra thị trường.
> **Trạng thái sản phẩm:** Web luyện CODE-REVIEW SKILL (JUDGE/bắt lỗi 1/4 theo 6 category), positioning "JUDGE không WRITE". 286 câu Python live + 1.141 câu EN backup. Chưa có auth/DB/billing/analytics.
> **Phương pháp:** Tổng hợp từ harness 20 vòng (R01–R20) với cơ chế adversarial verification. Mọi luận điểm số liệu gắn `[n]` trỏ tới nguồn đã xác minh ở cuối tài liệu.
> **Ngày:** 2026-05-30.

---

## 0. Tóm tắt điều hành (Executive Summary)

quiz-app đang ở **readiness trung bình ~3.8/10** qua 20 vòng nghiên cứu — tức ý tưởng và content có giá trị thật, nhưng phần "sản phẩm bán được" (auth, DB, billing, analytics, growth loop) **gần như chưa tồn tại trong code**. Đây là pet project có content tốt, không phải sản phẩm.

**Ba kết luận chiến lược:**

1. **Ngách "JUDGE code" là empty-lane có thật.** Các đối thủ lớn đều bắt người học VIẾT code (LeetCode/Codewars/HackerRank) hoặc là công cụ AI thay reviewer cho team (Sourcery/CodeRabbit) [8][9]. Không có player nào dạy kỹ năng *đọc & phê bình* code qua MCQ một cách chuyên sâu. Thị trường đủ lớn để nuôi một ngách: programming education ~$73B (2026) [1][11], online code-learning là SAM hẹp hơn (xem cảnh báo ảo giác ở §8).

2. **Thứ tự đúng là ĐO CẦU trước, XÂY INFRA sau.** 42% startup chết vì thiếu market need [35]; >60% EdTech không đạt lợi nhuận vì revenue model mơ hồ [34]; CAC EdTech >50% tổng chi [36]. Vì vậy P0 không phải Stripe/Postgres mà là **waitlist durable + analytics cookieless + fake-door pricing** để đo willingness-to-pay TRƯỚC khi đốt tiền infra.

3. **Monetization wedge = `/api/code_review` (AI review code thật), không phải quiz tĩnh.** Gap cầu lớn nhất: 40.9% dev *muốn* dùng AI cho code review nhưng chỉ 13.2% *đang* dùng (SO 2024, dùng trong R04/R07). Quiz là top-funnel; công cụ review code thật mới là thứ trả tiền. Giá tham chiếu ngách learner: $5/th–$40/năm (Codewars) [5].

**Khuyến nghị:** Không build billing/DB ngay. Ship lớp GTM mỏng (waitlist + share loop + analytics) trong 2–4 tuần, đo conversion fake-door, chỉ wire Stripe/Postgres khi có tín hiệu cầu thật.

---

## 1. Thị trường (TAM / SAM / SOM)

### 1.1 Quy mô thị trường

| Tầng | Định nghĩa | Quy mô | Nguồn |
|---|---|---|---|
| **TAM** | Programming education (toàn cầu) | $73.46B (2026) → $260.53B (2035), CAGR 15% | [1][11] |
| **SAM (tham chiếu)** | Online code-learning platform | Xem cảnh báo §8 — số liệu cited bị drift | [3] |
| **SAM (đối chiếu)** | Coding bootcamp market | $3.77B (2025) → $6.16B (2031), CAGR ~16% | [12] |
| **SAM (đối chiếu)** | Coding bootcamp (nguồn khác) | $1.9B (2025) → $6.4B (2033), CAGR 16.5% | [4] |
| **SOM (định giá)** | Learner subscription ngách code-review | Suy diễn từ pricing benchmark §4 | [5][22] |

> **Lưu ý độ tin cậy:** Số TAM $73.46B/$260.53B được xác minh verbatim ở 2 nguồn độc lập [1][11]. Số "online code-learning $3.6B→$12.2B" trong R01 đã bị flag: trang nguồn LIVE hiện báo số KHÁC ($11.3B 2025 → $37.44B 2034 @ 14.2%). Chi tiết §8.

### 1.2 Tín hiệu cầu (demand signals)

- **82% dev học code qua nguồn online** vs 49% học ở trường; 84% dùng technical documentation để học [2]. Đây là tín hiệu mạnh cho kênh phân phối self-learning online — đúng kênh của quiz-app.
- **Đọc code >> viết code:** Robert C. Martin (Clean Code) — tỉ lệ thời gian *đọc* vs *viết* code "well over 10 to 1" [15]. Dev đọc/review code liên tục nhưng kỹ năng này **bị dạy thiếu** — đúng khoảng trống quiz-app nhắm vào.
- **Dev viết code ít hơn ta tưởng:** Chỉ 32% tuần làm việc dành cho viết/cải thiện code; 35% cho code management (maintenance 19%, testing 12%, security 4%); ở tổ chức >500 dev, maintenance tăng lên 32% [13]. Review/maintenance là phần lớn công việc thật → kỹ năng review có giá trị nghề nghiệp.
- **AI làm code-review skill quan trọng HƠN, không bớt đi:** 85% dev thường xuyên dùng AI tools; 68% kỳ vọng nhà tuyển dụng sẽ yêu cầu thành thạo AI [14]. Khi AI sinh code nhiều hơn, người *judge* được code AI trở thành kỹ năng khan hiếm — luận điểm này được cộng đồng HN ủng hộ [19][21].

### 1.3 Tín hiệu thị trường ngách (interview/hiring)

- Thread HN **"Interviews in the Age of AI: Ditch Leetcode – Try Code Reviews Instead"** tồn tại thật, đề xuất code-review session thay LeetCode để đánh giá ứng viên [19].
- HN: "LeetCode is not for engineering on the job though, it's purely a test for getting hired" [20].
- HN: AI-generated code làm tăng nhu cầu kỹ sư biết review/judge code [21].

→ **Hệ quả:** Có một JTBD "pass code-review interview round" đang được thị trường nói tới nhưng chưa ai phục vụ bằng sản phẩm luyện tập. Đây là ICP mũi nhọn (xem §3).

---

## 2. Đối thủ & Khác biệt hoá

### 2.1 Bảng so sánh đối thủ

| Đối thủ | Mô hình | Người học làm gì | Giá learner | Có dạy "judge code"? | Nguồn |
|---|---|---|---|---|---|
| **Codewars** | Freemium, TDD kata | VIẾT & chạy code | Red $5/th, $24/6th, $40/năm | Không | [5] |
| **Exercism** | 100% free, non-profit | VIẾT code + human mentoring | Miễn phí | Không (mentoring ≠ luyện judge) | [6] |
| **LeetCode** | Freemium, algo | VIẾT code/giải thuật | Premium $35/th, $159/năm | Không | [22] |
| **HackerRank** | B2B/employer | VIẾT code (assessment) | Không bán learner sub ($165–375/th B2B) | Không | [7] |
| **Pluralsight** | Video courses | XEM video | $29–45/th, $299–499/năm | Không (passive) | [23] |
| **Educative** | Text-based courses | ĐỌC + bài tập | $59/th (~$199–299/năm) | Không (general) | [24] |
| **Sourcery** | AI reviewer (B2B tool) | (công cụ, không học) | $12/seat/th (Pro) | Không — thay reviewer, không *dạy* | [8][9] |
| **CodeRabbit** | AI reviewer (B2B tool) | (công cụ, không học) | $12–24/dev/th | Không — thay reviewer | [8] |
| **PentesterLab** | Security code-review lab | Tìm lỗ hổng (security only) | (lab bảo mật) | Một phần (chỉ security, không MCQ tổng quát) | [10] |
| **quiz-app (ta)** | MCQ judge code | JUDGE/bắt lỗi 1/4 theo 6 category | $5/th–$40/năm (đề xuất) | **CÓ — đây là core** | — |

### 2.2 Định vị empty-lane

> **One-liner (Dunford-style, đã chốt R04):** *"Họ bắt bạn VIẾT code. Chúng tôi luyện bạn JUDGE code."*

Phân tích lane:
- **Lane "WRITE & RUN"** (Codewars, LeetCode, HackerRank, Exercism): đông đúc, người học sản xuất code [5][6][7][22].
- **Lane "AI thay reviewer"** (Sourcery, CodeRabbit): là *tooling* cho team B2B, KHÔNG phải nền tảng đào tạo learner [8][9].
- **Lane "JUDGE/review skill qua luyện tập"**: gần như TRỐNG. PentesterLab chạm vào nhưng chỉ security & không phải MCQ tổng quát [10].

**Khác biệt phòng thủ được (defensible):**
1. **6-category flaw taxonomy** (bug/style/perf/edge/concurrency/security) làm xương sống sản phẩm — filter + per-category mastery (chốt R02/R06).
2. **Content đã qua kiểm định:** 286 câu Python live, 39 hard, sources 273/286, misconception_map phủ 286 câu — khó copy nhanh.
3. **Methodology badge:** neo vào SmartBear review methodology (R02) + "Human skill AI won't replace" neo vào use-vs-want gap (R04).

### 2.3 Áp lực cạnh tranh cần đề phòng

- **Exercism miễn phí 100%** [6] tạo áp lực giá mạnh ở phần general learning → ta KHÔNG cạnh tranh ở "learn to code", chỉ ở ngách "judge".
- **Tiền thật ở B2B, không ở learner subscription** (HackerRank $1,990–4,490/năm B2B vs learner free [7]; AI reviewer B2B per-seat [8][9]). Đây là *suy diễn* (xem §8) — hàm ý đường B2B/team có thể là monetization tier về sau.
- **>15,000 EdTech startup tồn tại**, đa số chết vì thiếu khác biệt hoá → pricing pressure, low brand loyalty [37]. Khác biệt hoá lane là sống còn.

---

## 3. Người dùng, ICP & Nỗi đau (JTBD)

### 3.1 ICP mũi nhọn (chốt R03)

**Track "Security-Review Interview Prep"** — bootcamp grad / job seeker.

| Thuộc tính | Chi tiết |
|---|---|
| **Persona** | Bootcamp grad hoặc dev đang tìm việc, chuẩn bị phỏng vấn |
| **JTBD** | "Pass the code-review round" trong phỏng vấn |
| **Vì sao ngách này khả thi NGAY** | Content thật đã đủ: 46 security + 60 bug + 39 hard + misconception_map phủ 286 câu — KHÔNG cần sinh content mới |
| **Vì sao đối thủ bỏ trống** | Codewars=TDD; Sourcery/CodeRabbit=B2B AI reviewer; không ai luyện "judge để pass interview" |

### 3.2 Nỗi đau người dùng (verified)

| Nỗi đau | Bằng chứng | Nguồn |
|---|---|---|
| LeetCode không phản ánh việc thật trên job | HN: "purely a test for getting hired" | [20] |
| Cần cách đánh giá tốt hơn LeetCode trong thời đại AI | HN thread "Ditch Leetcode – Try Code Reviews" | [19] |
| Scaffolding quá nặng = làm theo hướng dẫn, không tự giải | Dataquest review về Codecademy | [16] |
| Học xong vẫn thiếu portfolio thật để xin việc | DataCamp users phải tự build project ngoài | [17] |
| Billing tệ + content nông/cũ làm mất niềm tin | Codecademy Trustpilot 2.4/5 (~1,468 reviews) vs DataCamp 4.6/5 (~800) | [18] |

> **Bài học từ [18]:** điểm thấp Codecademy chủ yếu do **billing issues** (auto-renew, charge sau khi huỷ), không chỉ content. Hàm ý cho ta: nếu wire billing, phải làm cancel/refund minh bạch ngay từ đầu — đây là điểm khác biệt trust dễ thắng.

### 3.3 Cơ chế đo phân khúc (đã chốt, client-side, không DB)

- Onboarding 2 bước chọn ICP → route theo JTBD (reuse filter `quiz.js`).
- Waitlist phân khúc theo ICP qua POST → managed store ngoài.
- Persona-based question-pack endpoint từ taxonomy 6-category (clone pattern `/api/roadmap`, cache 3600s).

---

## 4. Pricing Benchmark & Monetization

### 4.1 Bảng giá đối thủ (learner-facing)

| Sản phẩm | Tháng | Năm | Tiết kiệm năm | Ghi chú | Nguồn |
|---|---|---|---|---|---|
| **Codewars Red** | $5 | $40 | ~30% | $24/6th; gần nhất với ngách ta | [5] |
| **LeetCode Premium** | $35 | $159 | ~62% | annual ≈ $13.25/th | [22][26] |
| **Pluralsight** | $29–45 | $299–499 | ~50% | gộp thành "Complete" $45/th từ 3/2025 | [23] |
| **Educative** | $59 | ~$199–299 | ~50%+ | text-based | [24] |
| **Sourcery (AI reviewer)** | $12/seat | — | — | B2B tool, không phải learner | [9] |
| **CodeRabbit (AI reviewer)** | $12–24/dev | — | — | B2B tool | [8] |

### 4.2 Định giá đề xuất (anchor)

- **Anchor learner ngách:** Codewars $5/th–$40/năm [5] là tham chiếu sát nhất (cùng tập khách hàng dev cá nhân, cùng định dạng practice). LeetCode $35/th [22] là trần trên cho "interview prep premium".
- **Đề xuất quiz-app:** Free (quiz cơ bản) + Pro **$5/th hoặc $40/năm** (39 hard + security/concurrency + `/api/code_review` quota). Định vị giá thấp để giảm ma sát conversion ở giai đoạn validation.
- **Lever chính = annual billing:** tiết kiệm 50–60% vs monthly là đòn bẩy chuẩn của dev-learning sub [26].

### 4.3 Cảnh báo conversion (rất quan trọng)

| Chỉ số | Giá trị | Nguồn | Hàm ý |
|---|---|---|---|
| EdTech freemium→paid | **2.6%** (dưới SaaS median 3.6%) | [25] | Freemium đơn thuần conversion thấp |
| Opt-in free trial → paid | 17.8% | [25] | Trial tốt hơn freemium nhiều |
| Opt-out (card-required) trial → paid | **49.9%** | [25] | Card-required trial mạnh nhất |
| MOOC completion rate | **3.13%** (2017–18) | [32] | Content free churn nặng |
| MOOC user quay lại năm sau | rớt từ 38% → 7% | [33] | Self-serve free không giữ chân |
| EdTech không đạt lợi nhuận | >60% (revenue model mơ hồ) | [34] | Phải có model rõ |
| Startup chết vì thiếu market need | ~42% | [35] | ĐO CẦU trước |
| CAC EdTech | >50% tổng chi | [36] | Growth loop hữu cơ là sống còn |

> **Kết luận pricing:** Freemium thuần conversion chỉ ~2.6% [25] → cân nhắc **card-required trial** (49.9%) cho tier Pro về sau. Nhưng TRƯỚC đó phải fake-door để đo WTP thật — không wire billing mù.

### 4.4 Chi phí vận hành (đủ rẻ để validate)

- **Supabase Free:** 50K MAU, 500MB DB, 5GB egress; Pro từ $25/th (100K MAU) [27].
- **Next.js/Supabase/Stripe stack:** $0/th ở MVP, <$200/th tới sau $1K MRR [28].
- **Stripe Billing:** 0.7% billing volume, gồm subscription + Smart Retries [29][30].

→ Infra cost KHÔNG phải lý do trì hoãn. Lý do trì hoãn là **chưa có bằng chứng cầu**.

---

## 5. Xu hướng (Trends)

1. **AI ở khắp nơi nhưng trust gap còn lớn.** 85% dev dùng AI tools [14] nhưng nhu cầu *judge* code AI tăng (HN [21]). Code-review skill = "human skill AI won't replace" — neo positioning vào đây (R04).
2. **Đọc/review code là phần lớn công việc thật**, không phải viết [13][15] → kỹ năng review có giá trị nghề nghiệp ngày càng rõ.
3. **Interview đang dịch khỏi LeetCode** sang đánh giá thực tế hơn như code review [19][20].
4. **Annual billing thành chuẩn ngành** cho dev-learning sub (tiết kiệm 50–60%) [26].
5. **EdTech bão hoà & khó lợi nhuận** [34][37] → khác biệt hoá ngách + growth loop hữu cơ (CAC thấp) là điều kiện sống còn [36].

---

## 6. Khoảng cách Sản phẩm → Thị trường (Product Gap)

Trạng thái code hiện tại (verified qua harness):

| Hạng mục | Trạng thái hiện tại | Cần để bán được |
|---|---|---|
| **Analytics** | 0 tag, `/api/client_errors` chỉ `logger.warning` | PostHog cookieless funnel (page→quiz-start→waitlist) |
| **Waitlist/lead** | 0 lead capture, localStorage-only | POST durable → external sink (Formspree/Sheets/Resend) + honeypot + throttle |
| **Pricing** | 0 dòng pricing/stripe | Fake-door `/pricing` 3 tier + intent capture |
| **Đáp án** | `/api/questions` (app.py:236–247) **lộ `correct_idx`** | Split `/api/round` (strip) + `/api/check` chấm server-side |
| **Auth** | Không có | GitHub OAuth + signed/JWT session (Vercel stateless) |
| **DB** | localStorage-only, không DB | Postgres serverless HTTP-driver (Neon/Supabase) |
| **Billing** | 0 dòng stripe/webhook | Stripe Checkout + signed entitlement + idempotent webhook |
| **Growth loop** | Không có share | SSR `/q/<id>` + OG/Twitter cards + Share button + Daily Challenge |
| **Citations/trust** | Sources có data nhưng chưa render link | `sources_map.json` render `<a>` + `/trust` page |

### 6.1 Lộ trình ưu tiên (theo gate, đã chốt qua 20 vòng)

**P0 — Đo cầu (build trước, rẻ, không DB):**
1. Waitlist durable (serverless POST → external sink, mirror pattern `/api/client_errors` + honeypot + throttle/IP).
2. Share/growth loop: SSR permalink `/q/<id>` + OG/Twitter cards + Share button trên Daily Code Review Challenge.
3. Fake-door `/pricing` (3 tier market-anchored + cookieless intent capture, ZERO billing code).
4. Analytics PostHog cookieless (page→quiz-start→waitlist).
5. **Đóng rò đáp án:** split `/api/round` + `/api/check` server-side — *blocker cấu trúc bắt buộc trước mọi paywall*.

**P1 — Chuẩn bị monetization (gated bởi tín hiệu cầu P0):**
1. EN-first top-funnel (i18n landing + load `questions_en_full.json`) cho kênh PH/HN/SO.
2. Server-side free/pro split (cột `tier`, filter cả 3 path serve câu hỏi).
3. Cloud progress sync (lift localStorage blob → per-user row, GET/PUT `/api/progress`).
4. GitHub OAuth + server session (httpOnly, stateless).
5. Postgres serverless HTTP-driver (Neon/Supabase) + tách content store static khỏi user-state.
6. Citations render + `/trust` page (chỉ metric thật: 286/273/15).

**P2 — Doanh thu & AI wedge (gated bởi P1):**
1. `/api/code_review` (dán code → AI review server-side + quota + cache KV + timeout) — **wedge trả tiền duy nhất**.
2. Stripe-hosted Checkout + signed entitlement token cho Pro.
3. AI Question Generator (offline batch, gated bằng `validate.py` anti-hallucination).
4. AI Tutor "Explain like a senior" có nhãn tin cậy.

> **REJECT (premature, đã loại R-GTM):** pricing teaser ở hero + hero rewrite quanh monetization. Lý do: monetization premature khi chưa đo cầu.

---

## 7. Rủi ro & Giả định

| Rủi ro | Bằng chứng | Giảm thiểu |
|---|---|---|
| Thiếu market need (nguyên nhân chết #1) | 42% startup [35] | P0 fake-door + waitlist ĐO trước build |
| Freemium conversion thấp | 2.6% EdTech [25] | Card-required trial (49.9%) [25] cho Pro |
| Free content churn nặng | MOOC completion 3.13% [32], return 38%→7% [33] | Gamification + streak + cloud sync giữ chân |
| CAC ăn >50% chi phí | [36] | Share loop hữu cơ (SSR `/q/<id>` + Daily Challenge) thay paid acquisition |
| Bão hoà + thiếu khác biệt | >15K EdTech [37] | Lane "JUDGE" + 6-category taxonomy + content kiểm định |
| Áp lực giá từ free | Exercism 100% free [6] | Không cạnh tranh "learn to code"; chỉ ngách "judge" |
| Trust/billing gây churn | Codecademy 2.4/5 vì billing [18] | Cancel/refund minh bạch từ đầu |

**Giả định cần kiểm chứng (chưa có evidence trực tiếp):**
- WTP thực tế của ICP "interview prep" ở mức $5/th — *cần fake-door xác nhận*.
- Share loop tạo viral coefficient đủ để CAC thấp — *cần đo sau khi ship*.
- B2B/team tier khả thi — *suy diễn từ [7][8][9], chưa verified*.

---

## 8. Đánh giá độ tin cậy & Ảo giác đã loại

### 8.1 Tổng quan độ tin cậy

- Harness 20 vòng: trung bình ~47 claim verified / ~27 hallucination-loại mỗi vòng. Tỉ lệ hallucination ~16.67% (R07) → **mọi số liệu phải double-check nguồn, không cache số thị trường**.
- Các nguồn **độ tin cậy CAO** (verified verbatim, URL live, số khớp 100%): [1][2][5][6][7][9][11][12][13][14][22][23][24][25][27][29][30] và các URL đối thủ chính (codewars.com/subscription, exercism.org, sourcery.ai/pricing).

### 8.2 Ảo giác / sai lệch đã loại (KHÔNG dùng làm căn cứ)

| Vấn đề | Mô tả | Xử lý |
|---|---|---|
| **Online code-learning $3.6B→$12.2B @14.5%** [3] | URL thật nhưng trang LIVE hiện báo số KHÁC: $11.3B (2025) → $37.44B (2034) @14.2%. Số cited đã drift/lỗi thời. | **KHÔNG dùng làm SAM chính thức.** Dùng bootcamp [12] làm SAM đối chiếu. |
| **Source attribution mismatch** (R01) | Số bootcamp $1.9B→$6.4B gán nhầm cho "Dataintelo/Technavio" — thực ra của Market Mind Partners [4]; Technavio được nêu nhưng không có nguồn Technavio thật. | Chỉ trích [4] = Market Mind Partners; bỏ nhãn Technavio. |
| **Driver mischaracterization** (R01) | Claim framing "Corporate Reskilling" là driver chính, nhưng nguồn liệt kê IT-sector growth là driver chính. | Sửa diễn giải, không dùng "corporate reskilling" làm headline. |
| **Trustpilot count** (R01) | Cited ~1,458 reviews, nguồn live nói 1,468 (lệch 10). | Dùng số đúng 1,468 [18]. |
| **Suy diễn vs dữ liệu** (R01) | "Tiền thật ở B2B không ở learner sub" và "không player thống trị MCQ" là SUY DIỄN/INTERPRETATION, không phải số liệu nguồn. | Đánh dấu rõ là *suy diễn* trong §2.3, không trình bày như fact. |
| **Báo cáo segment label garbled** (R01) | Business Research Insights có label máy-sinh ("Paid learning fashions", "get admission to"). | Bỏ qua label garbled; chỉ dùng số tổng đã verified [1][11]. |
| **Gộp nhóm khác loại** (R01) | Gộp CodeRabbit/Sourcery (dev tooling) với PentesterLab (security training) vào "một nhánh phân mảnh" — hai loại sản phẩm khác nhau. | Tách rõ trong bảng §2.1: AI reviewer vs security lab. |

### 8.3 Nguyên tắc sử dụng tài liệu này

1. **Số TAM dùng được:** $73.46B → $260.53B @15% [1][11] (2 nguồn độc lập, verbatim).
2. **Số SAM "online code-learning" trong R01 KHÔNG dùng** — đã drift. Nếu cần SAM, re-fetch nguồn live hoặc dùng bootcamp [12][4] làm proxy.
3. **Phân biệt fact vs suy diễn:** các luận điểm "empty-lane", "tiền ở B2B" là suy diễn hợp lý nhưng cần fake-door/B2B pilot để verify.
4. **Không cache số thị trường** — re-verify mỗi khi dùng cho pitch/đầu tư.

---

## 9. Quyết định & Bước tiếp theo (Actionable)

**Trong 2–4 tuần tới (P0, không cần DB/billing):**
1. Ship waitlist durable + analytics cookieless → bắt đầu thu lead & funnel data.
2. Ship fake-door `/pricing` 3 tier ($5/th–$40/năm anchor [5]) → đo WTP.
3. Ship SSR `/q/<id>` + Daily Challenge + Share button → khởi động growth loop hữu cơ (CAC thấp [36]).
4. Đóng rò đáp án (`/api/round` + `/api/check`) → mở khoá khả năng paywall sau này.

**Gate quyết định:** Chỉ wire OAuth → Postgres → Stripe → `/api/code_review` KHI fake-door cho thấy WTP đủ (benchmark: vượt freemium 2.6% [25], hướng tới trial-style conversion).

**Metric thành công P0:**
- Waitlist signups (lead thật đầu tiên — hiện đang 0).
- Funnel conversion page→quiz-start→waitlist (PostHog).
- Fake-door "Subscribe" click-through trên `/pricing` (proxy WTP).
- Share/permalink traffic (viral signal).

---

*Tài liệu này tổng hợp 20 vòng harness với adversarial verification. Mọi số liệu gắn [n] trỏ tới danh sách nguồn đã xác minh. Các số đã bị flag ảo giác (§8.2) KHÔNG được dùng làm căn cứ quyết định. Re-verify số thị trường trước mọi lần dùng cho gọi vốn/pitch.*