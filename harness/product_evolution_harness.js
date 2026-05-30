export const meta = {
  name: 'product-evolution-harness',
  description: 'Harness 20 vòng × 21 agent: research (nguồn đáng tin cậy) → kiểm tra hallucination → cải tiến → đánh giá → tổng hợp, biến quiz-app thành sản phẩm end-to-end sẵn sàng ra thị trường',
  whenToUse: 'Khi muốn tiến hóa ý tưởng web quiz-app thành một sản phẩm thương mại hoàn chỉnh, có kiểm chứng nguồn và chống ảo giác.',
  phases: [
    { title: 'Rounds', detail: '20 vòng × 21 agent: research→verify(anti-hallucination)→improve→judge→synth' },
    { title: 'Synthesis', detail: '6 agent dựng tài liệu sản phẩm end-to-end (research/spec/arch/GTM/roadmap/risks)' },
  ],
}

// ----------------------------------------------------------------------------
// 0. Hiện trạng sản phẩm (snapshot tĩnh, nhúng vào mọi prompt để agent có nền)
// ----------------------------------------------------------------------------
const PRODUCT_SNAPSHOT = `
SẢN PHẨM HIỆN TẠI — "quiz-app" (tên tạm):
- Bản chất: nền tảng web học CODE-REVIEW qua câu hỏi trắc nghiệm (MCQ). Người học đọc 1 đoạn code, chọn 1/4 đáp án (bug/style/perf/edge/concurrency/security), nhận giải thích + link nguồn.
- Nội dung: 1.141 câu hỏi đã qua 12 vòng generate + kiểm định. Ngôn ngữ: Python 286, JavaScript 237, Go 222, SQL 221, Rust 175. Độ khó: easy 419 / med 524 / hard 198.
- Sư phạm: roadmap 15 stage, 52 knowledge components, có trích dẫn học thuật (Soloway 1984, Sorva 2013, Robins 2003, Lister 2004, Hermans 2021...). Mastery tracking, cohort simulation, per-language tracks.
- Tech stack: Flask (Python) phục vụ JSON + Jinja templates; frontend vanilla JS (Prism highlight, copy buttons); tiến độ lưu localStorage (KHÔNG có tài khoản/DB). Deploy Vercel (serverless, api/index.py). Có /api/* endpoints, friendly 404/500, health_check, structured logging.
- Tính năng: dark mode, keyboard shortcuts (1-4 chọn, Enter nộp), /review, filter client-side theo lang/topic/difficulty, lazy pagination 50 câu, gamification, mobile responsive.
- Trạng thái thị trường: hiện UI gần như 100% tiếng Việt, mới chỉ là pet project / demo. CHƯA có: đăng ký/đăng nhập, lưu cloud, đồng bộ thiết bị, thanh toán/monetization, DB thật, AI features, analytics, leaderboard xã hội, funnel marketing, onboarding, pháp lý/privacy.
- Đối thủ tham chiếu: LeetCode, Codewars, Exercism, Educative, DataCamp, Coursera, Codecademy, HackerRank, Pluralsight, Codility — NHƯNG góc "học CODE-REVIEW skill" (đọc & phê bình code, bắt bug) là ngách ít ai làm chuyên sâu.

MỤC TIÊU CUỐI: biến ý tưởng web này thành một SẢN PHẨM END-TO-END có thể đưa ra thị trường (đăng ký được người dùng thật, thu tiền được, vận hành ổn định, có lợi thế cạnh tranh rõ ràng).
`.trim()

// ----------------------------------------------------------------------------
// 1. Chương trình 20 vòng (mỗi vòng 1 trục phát triển sản phẩm)
// ----------------------------------------------------------------------------
const ROUNDS = [
  { id: '01', title: 'Market & Demand Validation', focus: 'Kích thước thị trường (TAM/SAM/SOM) cho học lập trình / code-review / upskilling dev; bằng chứng nhu cầu thực (số liệu, báo cáo ngành); ai sẵn sàng trả tiền.' },
  { id: '02', title: 'Competitor Landscape & Differentiation', focus: 'So sánh trực diện LeetCode/Codewars/Exercism/Educative/HackerRank...; điểm yếu của họ; khoảng trống "code-review skill" để mình chiếm.' },
  { id: '03', title: 'Target Users, ICP & JTBD', focus: 'Chân dung người dùng lý tưởng (sinh viên CS, dev junior/mid, team lead, bootcamp, doanh nghiệp tuyển dụng); jobs-to-be-done; phân khúc trả tiền.' },
  { id: '04', title: 'Value Proposition & Positioning', focus: 'Tuyên ngôn giá trị khác biệt; định vị 1 câu; vì sao chọn ta thay vì đối thủ; thông điệp cốt lõi.' },
  { id: '05', title: 'Pricing & Monetization Model', focus: 'Mô hình doanh thu (freemium, subscription, B2B/team, marketplace, certification); benchmark giá thị trường edtech/dev-tool; price points & gói.' },
  { id: '06', title: 'Core Feature Set for Market Fit', focus: 'Tập tính năng tối thiểu để bán được (must-have); tính năng làm nên "wow"; ưu tiên theo impact/effort.' },
  { id: '07', title: 'AI-Powered Features', focus: 'LLM tạo câu hỏi/giải thích tự động, gia sư cá nhân hoá, AI review code người dùng dán vào, adaptive difficulty; chi phí & rủi ro AI; chống ảo giác trong nội dung AI.' },
  { id: '08', title: 'Accounts, Auth & Data Model', focus: 'Chuyển từ localStorage sang tài khoản thật: đăng ký/đăng nhập (OAuth, email), đồng bộ tiến độ đa thiết bị; mô hình dữ liệu người dùng/tiến độ/thanh toán.' },
  { id: '09', title: 'Backend Architecture & Database', focus: 'Kiến trúc backend market-ready: chọn DB (Postgres/SQLite/serverless), API layer, tách content store, migration từ Flask hiện tại; chi phí vận hành.' },
  { id: '10', title: 'Payments & Billing', focus: 'Tích hợp thanh toán (Stripe/Paddle/LemonSqueezy): subscription, trial, dunning, hoá đơn, thuế (VAT/GST), thanh toán nội địa VN (Momo/VNPay) nếu phục vụ VN.' },
  { id: '11', title: 'Content Strategy & Question-Bank Scaling', focus: 'Mở rộng & giữ chất lượng ngân hàng câu hỏi: coverage ngôn ngữ/topic, độ tươi mới, pipeline kiểm định, chống trùng lặp, đóng góp cộng đồng, bản quyền nội dung.' },
  { id: '12', title: 'Pedagogy & Learning Efficacy', focus: 'Tối ưu hiệu quả học: spaced repetition, mastery learning, adaptive sequencing, đo learning gain; bằng chứng học thuật cho từng cơ chế.' },
  { id: '13', title: 'UX/UI & Onboarding Redesign', focus: 'Trải nghiệm & onboarding chuyển đổi: first-run experience, time-to-value, accessibility (WCAG), mobile, i18n (đa ngôn ngữ giao diện) vì hiện đang 100% tiếng Việt.' },
  { id: '14', title: 'Growth, SEO & Acquisition', focus: 'Kênh kéo người dùng: SEO nội dung (mỗi câu hỏi là 1 trang index được?), content marketing, community, referral, partnerships với trường/bootcamp; CAC benchmark.' },
  { id: '15', title: 'Retention, Engagement & Gamification', focus: 'Giữ chân: streaks, daily goals, leaderboard, badges, email/push nudges, habit loops; bằng chứng cơ chế nào thực sự tăng retention (tránh dark pattern).' },
  { id: '16', title: 'Analytics, Metrics & Experimentation', focus: 'North-star metric, activation/retention/revenue funnel, event tracking, A/B testing infra, cohort analysis; công cụ (PostHog/Amplitude/GA4) & chi phí.' },
  { id: '17', title: 'Security, Privacy & Compliance', focus: 'Bảo mật & tuân thủ: auth security, OWASP, lưu trữ dữ liệu người dùng, GDPR/CCPA/Nghị định 13 VN, privacy policy & ToS, data retention.' },
  { id: '18', title: 'Scalability, Reliability & Infra', focus: 'Vận hành quy mô: vượt giới hạn Vercel hobby, CDN/cache, rate limiting, observability (logs/metrics/alerts), uptime/SLA, chi phí hạ tầng theo quy mô.' },
  { id: '19', title: 'Brand, Trust & Social Proof', focus: 'Thương hiệu & niềm tin: tên/định danh, landing page chuyển đổi, testimonials, case study, chứng chỉ hoàn thành, độ tin cậy nội dung (vì sao tin câu trả lời đúng).' },
  { id: '20', title: 'Launch Plan & GTM Execution', focus: 'Kế hoạch ra mắt: MVP scope, beta/waitlist, launch channels (ProductHunt, HN, communities), pricing launch, sequencing 0→1; risk register & điều kiện thành công.' },
]

// ----------------------------------------------------------------------------
// 2. 8 lăng kính research (× mỗi vòng = 8 research + 8 verify agent)
// ----------------------------------------------------------------------------
const LENSES = [
  { key: 'market_data', prompt: 'Số liệu thị trường & nhu cầu định lượng (market size, growth rate, số liệu khảo sát developer như StackOverflow Survey, JetBrains, báo cáo edtech). Trích nguồn có thẩm quyền.' },
  { key: 'competitor', prompt: 'Đối thủ trực tiếp làm gì cho trục này: tính năng, giá, mô hình; điểm mạnh/yếu cụ thể có thể kiểm chứng (trang pricing, docs, review người dùng).' },
  { key: 'authoritative', prompt: 'Best-practice từ nguồn có thẩm quyền (paper học thuật, tài liệu chính thức của vendor như Stripe/Postgres/OWASP/WCAG, sách chuẩn ngành).' },
  { key: 'user_pain', prompt: 'Nỗi đau & nhu cầu người dùng thật: review/ phàn nàn trên Reddit/HN/G2/Trustpilot/app store, forum dev; trích dẫn cụ thể (có thể paraphrase nhưng phải có URL nguồn).' },
  { key: 'pricing_bench', prompt: 'Benchmark giá & monetization cho trục này trong edtech/dev-tools: con số price point thật, gói, conversion rate freemium nếu công bố.' },
  { key: 'tech_bestpractice', prompt: 'Best-practice kỹ thuật & triển khai cho trục này: kiến trúc tham chiếu, thư viện/dịch vụ chuẩn, chi phí, cạm bẫy triển khai; ưu tiên docs chính thức.' },
  { key: 'pitfalls', prompt: 'Cạm bẫy, anti-pattern, thất bại thường gặp ở trục này (post-mortem, bài học startup, cảnh báo bảo mật). Vì sao thất bại.' },
  { key: 'trends_opportunity', prompt: 'Xu hướng mới & cơ hội khác biệt hoá 2025-2026 cho trục này (AI, ngách chưa ai chiếm, hành vi người học mới). Cơ hội cụ thể cho sản phẩm này.' },
]

const PERSPECTIVES = [
  { key: 'product', prompt: 'Góc PRODUCT: tính năng, UX, luồng người dùng, định vị giá trị.' },
  { key: 'engineering', prompt: 'Góc ENGINEERING: kiến trúc, data model, tích hợp, chi phí kỹ thuật, khả thi triển khai trên stack Flask/Vercel hiện tại hoặc nâng cấp.' },
  { key: 'business', prompt: 'Góc BUSINESS/GTM: doanh thu, pricing, kênh, đối tượng trả tiền, lợi thế cạnh tranh, rủi ro thị trường.' },
]

// ----------------------------------------------------------------------------
// 3. Schemas (structured output — không cần parse)
// ----------------------------------------------------------------------------
const FINDING_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    searched_queries: { type: 'array', items: { type: 'string' } },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string', description: 'Phát hiện ngắn gọn, định lượng nếu có' },
          evidence: { type: 'string', description: 'Bằng chứng/ trích dẫn ngắn từ nguồn' },
          source_url: { type: 'string', description: 'URL THẬT đã truy cập. Nếu không tìm được nguồn thật thì để rỗng và đặt confidence=low.' },
          source_name: { type: 'string' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['claim', 'source_url', 'confidence'],
      },
    },
  },
  required: ['lens', 'findings'],
}

// Đơn giản hoá: bỏ tầng lồng 'checked' (gây schema-mismatch cao). Verify vẫn
// kiểm tra từng claim trong reasoning, chỉ output các claim đã xác minh + cờ ảo giác.
const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    verified_findings: {
      type: 'array',
      description: 'CHỈ các claim được nguồn THẬT ủng hộ (verdict=supported). Bỏ claim không kiểm chứng được.',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          source_url: { type: 'string' },
        },
        required: ['claim'],
      },
    },
    hallucination_flags: { type: 'array', items: { type: 'string' }, description: 'Claim/URL bịa, phóng đại, hoặc không kiểm chứng được — mô tả ngắn' },
  },
  required: ['lens', 'verified_findings', 'hallucination_flags'],
}

const IMPROVE_SCHEMA = {
  type: 'object',
  properties: {
    perspective: { type: 'string' },
    improvements: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          description: { type: 'string', description: 'Thay đổi cụ thể, khả thi, mô tả đủ để implement' },
          rationale: { type: 'string', description: 'Dựa trên verified finding nào' },
          category: { type: 'string', enum: ['product', 'tech', 'business', 'growth', 'ux', 'content', 'security', 'pedagogy'] },
          impact: { type: 'string', enum: ['high', 'medium', 'low'] },
          effort: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['title', 'description', 'impact', 'effort', 'category'],
      },
    },
  },
  required: ['perspective', 'improvements'],
}

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    accepted: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          why: { type: 'string' },
          priority: { type: 'string', enum: ['P0', 'P1', 'P2'] },
        },
        required: ['title', 'priority'],
      },
    },
    rejected: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, why: { type: 'string' } }, required: ['title'] } },
    round_score: { type: 'number', description: '0-10: mức sẵn sàng ra thị trường của TRỤC này sau vòng' },
  },
  required: ['accepted', 'round_score'],
}

const SYNTH_ROUND_SCHEMA = {
  type: 'object',
  properties: {
    round_summary: { type: 'string', description: '<=120 từ: kết luận của vòng' },
    updated_product_state: { type: 'string', description: '<=220 từ: định nghĩa sản phẩm TÍCH LUỸ tới hiện tại (vòng sau sẽ đọc cái này)' },
    key_decisions: { type: 'array', items: { type: 'string' } },
    readiness_score: { type: 'number', description: '0-10: tổng mức sẵn sàng ra thị trường tích luỹ' },
  },
  required: ['round_summary', 'updated_product_state', 'readiness_score'],
}

const DOC_SCHEMA = {
  type: 'object',
  properties: {
    filename: { type: 'string' },
    markdown: { type: 'string', description: 'Nội dung tài liệu Markdown đầy đủ, tiếng Việt (giữ thuật ngữ kỹ thuật tiếng Anh), có trích dẫn nguồn dạng [n].' },
  },
  required: ['filename', 'markdown'],
}

// ----------------------------------------------------------------------------
// 4. Helpers
// ----------------------------------------------------------------------------
function clip(s, n) { s = String(s == null ? '' : s); return s.length > n ? s.slice(0, n) + '…' : s }
function compactVerified(vArr) {
  return vArr.flatMap(v => (v && v.verified_findings ? v.verified_findings : []))
    .map(f => `- ${clip(f.claim, 200)}${f.source_url ? ` [${clip(f.source_url, 90)}]` : ''}`)
    .join('\n')
}

const RANGE_START = (args && Number.isInteger(args.startRound)) ? args.startRound : 0
const RANGE_END = (args && Number.isInteger(args.endRound)) ? args.endRound : ROUNDS.length - 1
const FAST = !!(args && args.fast)
const SKIP_DOCS = !!(args && args.skipDocs)            // batch trung gian: bỏ qua dựng tài liệu
const PRIOR_STATE = (args && typeof args.priorState === 'string' && args.priorState) ? args.priorState : null
const PRIOR_VERIFIED = (args && Array.isArray(args.priorVerified)) ? args.priorVerified : []
const PRIOR_HALLU = (args && Array.isArray(args.priorHallu)) ? args.priorHallu : []

log(`🚀 Harness khởi động — vòng ${RANGE_START + 1}…${RANGE_END + 1} / ${ROUNDS.length}${FAST ? ' (FAST/smoke)' : ''}${SKIP_DOCS ? ' (batch, skipDocs)' : ''}${PRIOR_STATE ? ' [resume state]' : ''}`)

// ----------------------------------------------------------------------------
// 5. Vòng lặp 20 vòng — mỗi vòng 21 agent
// ----------------------------------------------------------------------------
const rounds = []
let productState = PRIOR_STATE || PRODUCT_SNAPSHOT
let allVerified = PRIOR_VERIFIED.slice()        // {r, lens, claim, url}
let allHallucinations = PRIOR_HALLU.slice()      // {r, flag}

for (let r = RANGE_START; r <= RANGE_END; r++) {
  const R = ROUNDS[r]
  const ph = `R${R.id} ${R.title}`
  phase(ph)
  log(`▶ Vòng ${R.id}: ${R.title}`)

  const baseCtx = `${PRODUCT_SNAPSHOT}\n\n### TRẠNG THÁI SẢN PHẨM TÍCH LUỸ (từ các vòng trước):\n${clip(productState, 2200)}\n\n### TRỤC CỦA VÒNG NÀY — ${R.title}:\n${R.focus}`

  // --- Stage 1+2: research → verify, pipeline theo từng lăng kính (16 agent) ---
  const lensResults = await pipeline(
    LENSES,
    (lens, _l, i) => agent(
      `Bạn là RESEARCH AGENT. Bạn CÓ WebSearch và WebFetch — hãy DÙNG chúng thật (${FAST ? '1' : '2'} truy vấn).\n\n${baseCtx}\n\n### NHIỆM VỤ — lăng kính "${lens.key}":\n${lens.prompt}\n\nTìm ${FAST ? '1-2' : '2-3'} phát hiện CỤ THỂ NHẤT, định lượng nếu được, mỗi cái kèm URL THẬT bạn đã truy cập. Mỗi claim/evidence NGẮN GỌN (1-2 câu). TUYỆT ĐỐI KHÔNG bịa URL hay số liệu. Nếu không tìm được nguồn thật cho 1 claim, để source_url rỗng và confidence=low. Tiếng Việt, giữ thuật ngữ EN.`,
      { label: `research:${R.id}:${lens.key}`, phase: ph, schema: FINDING_SCHEMA, agentType: 'general-purpose' }
    ),
    (research, lens, i) => agent(
      `Bạn là VERIFICATION / HALLUCINATION-CHECK AGENT. Bạn CÓ WebSearch + WebFetch.\n\nDưới đây là các phát hiện của một research agent cho lăng kính "${lens.key}" (trục: ${R.title}). Với MỖI phát hiện, kiểm tra độc lập (trong đầu): (a) URL có TỒN TẠI THẬT không (WebFetch/Search thử — 403/chặn-bot KHÁC với bịa URL), (b) nguồn có THỰC SỰ ủng hộ claim không, (c) số liệu có khớp không.\n\nOUTPUT (ngắn gọn):\n- verified_findings: CHỈ những claim được nguồn THẬT ủng hộ (kèm source_url). Bỏ claim không kiểm chứng được.\n- hallucination_flags: liệt kê ngắn mọi URL bịa / số liệu phóng đại / claim không có nguồn.\n\nPHÁT HIỆN CẦN KIỂM TRA:\n${JSON.stringify((research && research.findings) || [], null, 1).slice(0, 5000)}`,
      { label: `verify:${R.id}:${lens.key}`, phase: ph, schema: VERIFY_SCHEMA, agentType: 'general-purpose' }
    )
  )

  const verified = lensResults.filter(Boolean)
  for (const v of verified) {
    for (const f of (v.verified_findings || [])) allVerified.push({ r: R.id, lens: v.lens, claim: clip(f.claim, 240), url: f.source_url || '' })
    for (const h of (v.hallucination_flags || [])) allHallucinations.push({ r: R.id, flag: clip(h, 240) })
  }
  const verifiedDigest = compactVerified(verified) || '(không có finding nào được xác minh ở vòng này)'

  // --- Stage 3: improve (3 agent, 3 góc nhìn) ---
  const improveResults = (await parallel(PERSPECTIVES.map(p => () => agent(
    `Bạn là IMPROVEMENT AGENT — ${p.prompt}\n\n${baseCtx}\n\n### BẰNG CHỨNG ĐÃ XÁC MINH ở vòng này (chỉ dùng cái đã verified, đừng bịa thêm):\n${clip(verifiedDigest, 3500)}\n\n### NHIỆM VỤ:\nĐề xuất ĐÚNG 3 cải tiến CỤ THỂ, KHẢ THI nhất cho trục "${R.title}" để đẩy sản phẩm tới mức ra-thị-trường. Mỗi cải tiến: title ngắn, description <=60 từ (đủ để implement), rationale 1 câu gắn bằng chứng. Cân nhắc khả thi trên stack Flask/Vercel/JSON hiện tại hoặc nêu rõ nâng cấp cần thiết.`,
    { label: `improve:${R.id}:${p.key}`, phase: ph, schema: IMPROVE_SCHEMA, agentType: 'general-purpose' }
  )))).filter(Boolean)

  const allImprovements = improveResults.flatMap(ir => (ir.improvements || []).map(im => ({ ...im, perspective: ir.perspective })))

  // --- Stage 4: judge (1 agent) ---
  const judged = await agent(
    `Bạn là PRODUCT JUDGE khắt khe, ưu tiên ra-thị-trường. Dưới đây là các đề xuất cải tiến cho trục "${R.title}". Chấm & chọn: accept cái nào (gán priority P0/P1/P2 theo impact-vs-effort & mức cấp thiết cho việc bán được sản phẩm), reject cái nào (vì sao). Cho round_score 0-10 mức sẵn sàng ra thị trường của TRỤC này.\n\nĐỀ XUẤT:\n${JSON.stringify(allImprovements, null, 1).slice(0, 8000)}`,
    { label: `judge:${R.id}`, phase: ph, schema: JUDGE_SCHEMA }
  )

  // --- Stage 5: synth (1 agent) — cập nhật trạng thái tích luỹ ---
  const synth = await agent(
    `Bạn là SYNTHESIS AGENT. Tổng hợp vòng "${R.title}".\n\n### Trạng thái sản phẩm trước vòng:\n${clip(productState, 2000)}\n\n### Bằng chứng đã xác minh:\n${clip(verifiedDigest, 2500)}\n\n### Cải tiến được JUDGE chấp nhận:\n${JSON.stringify((judged && judged.accepted) || [], null, 1).slice(0, 3500)}\n\nViết: (1) round_summary <=120 từ; (2) updated_product_state <=220 từ — định nghĩa sản phẩm TÍCH LUỸ MỚI (gộp quyết định vòng này vào trạng thái cũ, đây là cái vòng sau đọc); (3) key_decisions; (4) readiness_score 0-10 tổng thể. Tiếng Việt, giữ thuật ngữ EN.`,
    { label: `synth:${R.id}`, phase: ph, schema: SYNTH_ROUND_SCHEMA }
  )

  if (synth && synth.updated_product_state) productState = synth.updated_product_state

  rounds.push({
    id: R.id,
    title: R.title,
    verified_count: verified.reduce((a, v) => a + (v.verified_findings ? v.verified_findings.length : 0), 0),
    hallucination_count: verified.reduce((a, v) => a + (v.hallucination_flags ? v.hallucination_flags.length : 0), 0),
    accepted: (judged && judged.accepted) || [],
    round_score: (judged && judged.round_score) || 0,
    readiness_score: (synth && synth.readiness_score) || 0,
    summary: (synth && synth.round_summary) || '',
    key_decisions: (synth && synth.key_decisions) || [],
  })
  log(`✓ Vòng ${R.id} xong — verified=${rounds[rounds.length - 1].verified_count}, hallu=${rounds[rounds.length - 1].hallucination_count}, readiness=${rounds[rounds.length - 1].readiness_score}/10`)
}

// ----------------------------------------------------------------------------
// 5b. Batch trung gian: trả state tích luỹ, KHÔNG dựng tài liệu (để batch cuối làm)
// ----------------------------------------------------------------------------
if (SKIP_DOCS) {
  log(`⏸ Batch xong (vòng ${RANGE_START + 1}…${RANGE_END + 1}) — bàn giao state cho batch sau.`)
  return {
    meta: { rounds_run: rounds.length, verified_total: allVerified.length, hallucination_total: allHallucinations.length, batch: true },
    rounds,
    finalProductState: productState,
    allVerified,
    allHallucinations,
    trajectory: rounds.map(r => ({ id: r.id, readiness: r.readiness_score })),
  }
}

// ----------------------------------------------------------------------------
// 6. Tổng hợp cuối — 6 agent dựng tài liệu sản phẩm end-to-end
// ----------------------------------------------------------------------------
phase('Synthesis')
log('🧩 Dựng tài liệu sản phẩm end-to-end…')

const roundDigest = rounds.map(r =>
  `## R${r.id} ${r.title} (readiness ${r.readiness_score}/10, verified ${r.verified_count}, hallu ${r.hallucination_count})\n${clip(r.summary, 600)}\nĐã chấp nhận: ${r.accepted.map(a => `[${a.priority}] ${a.title}`).join('; ') || '—'}`
).join('\n\n')

const verifiedDossier = allVerified.map((f, i) => `[${i + 1}] (R${f.r}/${f.lens}) ${f.claim}${f.url ? ` — ${f.url}` : ''}`).join('\n')
const halluSummary = allHallucinations.map((h, i) => `- (R${h.r}) ${h.flag}`).join('\n') || '(không phát hiện ảo giác đáng kể)'

const DOCS = [
  { file: 'PRODUCT_RESEARCH.md', brief: 'DOSSIER NGHIÊN CỨU có trích dẫn: thị trường (TAM/SAM/SOM), đối thủ (bảng so sánh), người dùng & nỗi đau, pricing benchmark, xu hướng. MỌI luận điểm phải gắn [n] trỏ tới nguồn trong danh sách verified dưới đây. Có mục "Đánh giá độ tin cậy & ảo giác đã loại".', useDossier: true },
  { file: 'PRODUCT_SPEC.md', brief: 'ĐẶC TẢ SẢN PHẨM END-TO-END: tầm nhìn, ICP & personas, value proposition, feature map (MVP / v1 / v2) với must-have vs nice-to-have, AI features, user flows chính, định nghĩa "ra-thị-trường".', useDossier: false },
  { file: 'TECH_ARCHITECTURE.md', brief: 'KIẾN TRÚC KỸ THUẬT để market-ready: sơ đồ hệ thống, lựa chọn DB & lý do, auth, payments, content store, API, hosting/scale, migration từ Flask/Vercel hiện tại, bảo mật, chi phí hạ tầng theo quy mô. Có code-level migration steps.', useDossier: false },
  { file: 'GTM_PLAN.md', brief: 'KẾ HOẠCH RA THỊ TRƯỜNG: positioning 1 câu, pricing & gói (bảng giá cụ thể), kênh acquisition + CAC, retention/engagement, partnerships, metrics/north-star, launch sequence.', useDossier: false },
  { file: 'ROADMAP.md', brief: 'LỘ TRÌNH THỰC THI phân pha: Phase 0 (MVP market-ready), Phase 1 (launch), Phase 2 (scale). Mỗi pha: scope, P0/P1 items (lấy từ các vòng), tiêu chí hoàn thành, ước lượng. Bảng tổng hợp mọi P0 từ 20 vòng.', useDossier: false },
  { file: 'RISKS_AND_VALIDATION.md', brief: 'SỔ RỦI RO & KIỂM CHỨNG: risk register (rủi ro thị trường/kỹ thuật/pháp lý/tài chính + mitigation), tóm tắt quy trình anti-hallucination của harness, danh sách ảo giác đã loại, các giả định CHƯA kiểm chứng cần test tiếp.', useDossier: true },
]

// QUAN TRỌNG: KHÔNG dùng schema cho doc — markdown đầy đủ qua StructuredOutput
// hay bị truncate/schema-mismatch → retry vô tận. Trả về PLAIN TEXT (final message).
const docOut = (await parallel(DOCS.map(d => () => agent(
  `Bạn là SENIOR ${d.file.includes('TECH') ? 'STAFF ENGINEER' : d.file.includes('GTM') ? 'HEAD OF GROWTH' : 'PRODUCT LEAD'}. Viết tài liệu \`${d.file}\` cho sản phẩm, dựa trên kết quả harness 20 vòng.\n\n${PRODUCT_SNAPSHOT}\n\n### TRẠNG THÁI SẢN PHẨM CUỐI (tích luỹ 20 vòng):\n${clip(productState, 2500)}\n\n### TÓM TẮT 20 VÒNG:\n${clip(roundDigest, 9000)}\n${d.useDossier ? `\n### NGUỒN ĐÃ XÁC MINH (trích dẫn bằng [n]):\n${clip(verifiedDossier, 12000)}\n\n### ẢO GIÁC ĐÃ LOẠI:\n${clip(halluSummary, 3000)}\n` : ''}\n### YÊU CẦU TÀI LIỆU:\n${d.brief}\n\nViết Markdown đầy đủ, có cấu trúc heading rõ, bảng khi cần, tiếng Việt (giữ thuật ngữ kỹ thuật EN). Cụ thể & khả thi, KHÔNG sáo rỗng.\n\nQUAN TRỌNG: Trả lời của bạn là TOÀN BỘ nội dung file Markdown (bắt đầu bằng "# ..."). KHÔNG kèm lời dẫn, KHÔNG bọc trong code fence. Chỉ markdown thuần.`,
  { label: `doc:${d.file}`, phase: 'Synthesis' }
).then(md => (md && String(md).trim()) ? { filename: d.file, markdown: String(md).trim() } : null)))).filter(Boolean)

log(`✅ Hoàn tất — ${rounds.length} vòng, ${allVerified.length} nguồn verified, ${allHallucinations.length} cờ ảo giác, ${docOut.length} tài liệu.`)

return {
  meta: { rounds_run: rounds.length, verified_total: allVerified.length, hallucination_total: allHallucinations.length },
  rounds,
  finalProductState: productState,
  allVerified,
  allHallucinations,
  trajectory: rounds.map(r => ({ id: r.id, readiness: r.readiness_score })),
  docs: docOut,
  verifiedDossier,
  halluSummary,
}
