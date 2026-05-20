// Minimal syntax-highlight shim — Prism replacement that escapes-only.
// Real Prism would highlight; this keeps the same API surface (Prism.highlightElement) without external deps.
window.Prism = (function () {
  function escape(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function highlightElement(el) {
    // Apply simple keyword coloring for visual distinction without external dep.
    const lang = (el.className.match(/language-(\w+)/) || [,''])[1];
    let html = escape(el.textContent || '');
    const keywords = {
      python: /\b(def|class|return|import|from|if|elif|else|for|while|try|except|finally|with|as|in|not|and|or|is|None|True|False|lambda|yield|async|await|global|nonlocal|pass|raise|break|continue)\b/g,
      js: /\b(function|var|let|const|return|if|else|for|while|try|catch|finally|class|extends|new|this|super|throw|async|await|of|in|typeof|instanceof|null|undefined|true|false|import|export|from|default)\b/g,
      javascript: /\b(function|var|let|const|return|if|else|for|while|try|catch|finally|class|extends|new|this|super|throw|async|await|of|in|typeof|instanceof|null|undefined|true|false|import|export|from|default)\b/g,
      go: /\b(package|import|func|return|if|else|for|range|switch|case|default|var|const|type|struct|interface|map|chan|go|defer|select|break|continue|fallthrough|nil|true|false)\b/g,
      rust: /\b(fn|let|mut|const|static|if|else|for|while|loop|match|return|use|mod|pub|struct|enum|impl|trait|where|as|in|self|Self|crate|true|false|None|Some|Ok|Err|move|ref|async|await)\b/g,
      sql: /\b(SELECT|FROM|WHERE|GROUP|BY|HAVING|ORDER|LIMIT|OFFSET|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|INDEX|ALTER|DROP|JOIN|INNER|LEFT|RIGHT|OUTER|ON|AS|AND|OR|NOT|NULL|IS|IN|BETWEEN|LIKE|ILIKE|EXISTS|CASE|WHEN|THEN|ELSE|END|UNION|ALL|DISTINCT|COUNT|SUM|AVG|MIN|MAX|COALESCE|NULLIF|BEGIN|COMMIT|ROLLBACK|LATERAL|WITH|RETURNING|CONFLICT|DO|EXCLUDED|FOR|UPDATE)\b/gi,
    };
    const rx = keywords[lang];
    if (rx) html = html.replace(rx, '<span style="color:#60a5fa">$1</span>');
    html = html.replace(/("|')(?:\\.|(?!\1).)*\1/g, m => `<span style="color:#a3e635">${m}</span>`);
    html = html.replace(/\/\/[^\n]*|#[^\n]*|--[^\n]*/g, m => `<span style="color:#94a3b8;font-style:italic">${m}</span>`);
    el.innerHTML = html;
  }
  return { highlightElement };
})();
