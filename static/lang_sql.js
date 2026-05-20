/* lang_sql.js — SQL-specific hints (pg_query, Schwartz HPM, awesome-sql, Exercism). */
(function(){
const HINTS = {
  "index_planner_stat":      "Planner uses pg_statistic histograms; stale stats → bad row estimates → seq scan over index. Run ANALYZE after bulk writes. (pg_query, Schwartz HPM)",
  "null_three_valued_logic": "NULL = NULL is NULL, not TRUE. Use IS NULL / IS NOT DISTINCT FROM. WHERE clauses treat NULL as 'not true' (skip the row). (Exercism SQL)",
  "windowed_aggregate":      "Window functions compute per-row over a frame; aggregate-only functions collapse the row set. Use SUM(x) OVER (...) vs SUM(x) GROUP BY. (awesome-sql)",
  "cte_materialization":     "Postgres 12+ inlines simple CTEs; force materialization with `WITH x AS MATERIALIZED (...)` when reuse is expensive. (pg_query)",
  "row_estimate_skew":       "When one bucket has 10× others, planner picks a strategy by avg, blowing up the outlier. EXPLAIN ANALYZE shows estimate vs actual rows. (Schwartz HPM)",
};
const PATTERN_HINTS = [
  [/\bEXPLAIN\b|\bANALYZE\b|\bINDEX\b/i, "index_planner_stat"],
  [/\bIS\s+(NOT\s+)?NULL\b|=\s*NULL|<>\s*NULL/i, "null_three_valued_logic"],
  [/\bOVER\s*\(|PARTITION\s+BY|ROW_NUMBER|RANK\(\)/i, "windowed_aggregate"],
  [/\bWITH\b.+\bAS\b\s*\(/i, "cte_materialization"],
  [/\bGROUP\s+BY\b|\bHAVING\b/i, "row_estimate_skew"],
];
function fire(hintIds){
  const ul = document.getElementById('lang-hint-active');
  if (!ul) return;
  if (!hintIds.length){ ul.innerHTML = '<li class="hint">No SQL-specific hint for this question.</li>'; return; }
  ul.innerHTML = hintIds.map(id => `<li><strong>${id}</strong>: ${HINTS[id] || ''}</li>`).join('');
}
window.LANG_HINTS_SQL = function(q){
  if (q.lang !== 'sql') return;
  const ids = new Set();
  if (HINTS[q.kc_tag]) ids.add(q.kc_tag);
  for (const [pat, id] of PATTERN_HINTS){
    if (pat.test(q.code)) ids.add(id);
  }
  fire(Array.from(ids));
};
})();
