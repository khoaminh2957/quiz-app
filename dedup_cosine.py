"""Real §3.6 dedup pass: sentence-transformers all-MiniLM-L6-v2 cosine ≥0.85 → reject.
Lang-sharded. Runs as a post-pass over questions.jsonl, rewrites questions.json with kept items.
"""
import json, pathlib, sys
from sentence_transformers import SentenceTransformer, util

ROOT = pathlib.Path(__file__).parent
JSONL = ROOT / 'questions.jsonl'
JSON_OUT = ROOT / 'questions.json'

print("loading all-MiniLM-L6-v2 (~80MB first time)...", flush=True)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("model loaded.", flush=True)

items = []
for line in JSONL.read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if line:
        items.append(json.loads(line))
print(f"loaded {len(items)} items", flush=True)

# encode by lang shard
by_lang = {}
for i, it in enumerate(items):
    by_lang.setdefault(it['lang'], []).append(i)

kept_mask = [True] * len(items)
THRESHOLD = 0.85
total_rejected = 0
for lang, idxs in by_lang.items():
    texts = [items[i]['question'] + ' ' + items[i]['code'] for i in idxs]
    embs = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    # cosine similarity matrix
    sim = util.cos_sim(embs, embs)
    # greedy keep-first: walk in order, reject any later item with sim>=threshold to a kept earlier item
    n = len(idxs)
    local_keep = [True] * n
    for j in range(n):
        if not local_keep[j]:
            continue
        for k in range(j+1, n):
            if local_keep[k] and float(sim[j][k]) >= THRESHOLD:
                local_keep[k] = False
    for local_i, gi in enumerate(idxs):
        if not local_keep[local_i]:
            kept_mask[gi] = False
            total_rejected += 1
    kept_lang = sum(local_keep)
    print(f"  lang={lang}: candidates={n} kept={kept_lang} rejected={n-kept_lang}", flush=True)

kept = [it for it, m in zip(items, kept_mask) if m]
print(f"\nFinal: kept {len(kept)} / {len(items)} items (rejected {total_rejected} for cosine>={THRESHOLD})", flush=True)

# atomically rewrite jsonl + json
tmp = ROOT / 'questions.jsonl.dedup_tmp'
with tmp.open('w', encoding='utf-8') as f:
    for it in kept:
        f.write(json.dumps(it, ensure_ascii=False) + '\n')
        f.flush()
import os
os.replace(tmp, JSONL)
JSON_OUT.write_text(json.dumps(kept, ensure_ascii=False, indent=0), encoding='utf-8')
print("rewrote questions.jsonl and questions.json")
