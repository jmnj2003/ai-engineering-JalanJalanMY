# Builds notebooks/week4c_all_states.ipynb (JalanJalanMY).
# Usage: python3 -I build_nb_all.py <prep_lib_all.py> <output.ipynb>
import sys
import nbformat as nbf

lib = open(sys.argv[1], encoding="utf-8").read().split('if __name__ == "__main__":')[0].strip()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

cells = [
md("""# Week 4c — All-States Expansion: JalanJalanMY

**Why:** corpus v2 covered only Kuala Lumpur, Penang, Melaka and Sabah. JalanJalanMY plans trips anywhere in Malaysia, so every state and federal territory needs official attraction evidence.

**What this notebook does**
1. **Topic 3 steps** on the 12 remaining chapters of Tourism Malaysia's *Malaysia Travel Guide 2023* (S09–S20): Selangor, Putrajaya, Negeri Sembilan, Johor, Perak, Kedah, Perlis, Pahang, Terengganu, Kelantan, Sarawak and Labuan. It uses the same extraction, cleaning and **paragraph-aware 500-character** chunking, with page numbers kept.
2. **Topic 4 checks** with the same rules as Week 4b: approved source, non-empty text, length ≥ 100, garbled characters, ligatures, glyph-ID text, page reference, source age ≤ 36 months.
3. **Merge** with the reviewed corpus v2 (`data/prepared_chunks_clean_v2.jsonl`, 503 chunks) into **corpus v3**, deduplicate and measure coverage for all 16 states and federal territories.

**Kuala Lumpur chapter (pp. 7–20) not added:** KL already has its own 72-page official guide (S01) and holds 49% of corpus v2. Adding a second KL source would make the imbalance worse and repeat the same attractions.

**Upload to Colab:** `MTG_2023.pdf` and `data/prepared_chunks_clean_v2.jsonl` from the repo. Then use Runtime → Run all.

> The source PDF is © Tourism Malaysia (all rights reserved). Coursework use only — not committed to the repository."""),
md("## 1 — Setup and source check"),
code(r'''!pip install -q pypdf pandera langchain-core matplotlib
import os, re, json, shutil, pickle, hashlib
from pathlib import Path
from datetime import date
import pandas as pd

BASE = Path('/content') if Path('/content').is_dir() else Path.cwd()
RAW = BASE / 'states_raw'; RAW.mkdir(exist_ok=True)
(BASE / 'data' / 'processed').mkdir(parents=True, exist_ok=True)
(BASE / 'docs').mkdir(exist_ok=True)

NEEDED = ['MTG_2023.pdf']
for name in NEEDED:                                    # move uploads into states_raw
    if (BASE / name).is_file() and not (RAW / name).is_file():
        shutil.move(str(BASE / name), str(RAW / name))
missing = [n for n in NEEDED if not (RAW / n).is_file()]
assert not missing, f'Upload these PDFs first: {missing}'
V2 = BASE / 'data' / 'prepared_chunks_clean_v2.jsonl'
if not V2.exists() and (BASE / 'prepared_chunks_clean_v2.jsonl').exists():
    shutil.move(str(BASE / 'prepared_chunks_clean_v2.jsonl'), str(V2))
assert V2.exists(), 'Upload data/prepared_chunks_clean_v2.jsonl (Week 4b corpus v2) first.'
print('All inputs present:', NEEDED + [V2.name])
'''),
code(lib + r'''

# Source inspection: pages, readable text, glyph-ID and ligature artefacts, PDF date
from pypdf import PdfReader
inspect_rows = []
reader = PdfReader(str(RAW / 'MTG_2023.pdf'))
meta = reader.metadata or {}
for sid, fname, state, a, b, kind in SOURCES:
    text = '\n'.join(reader.pages[p - 1].extract_text() or '' for p in range(a, b + 1))
    inspect_rows.append({'source_id': sid, 'file': fname, 'state': state, 'pages': f'{a}-{b}', 'kind': kind,
                         'chars': len(text), 'glyph_id_codes': len(re.findall(r'/gid\d{5}', text)),
                         'ligature_artefacts': len(re.findall(r'/f_|[ﬀ-ﬆ]', text)),
                         'pdf_modified': str(meta.get('/ModDate', ''))[2:10],
                         'sha256': sha256(RAW / fname)[:12]})
inspection = pd.DataFrame(inspect_rows)
print(inspection.to_string(index=False))
'''),
md("""**Inspection findings:** all 12 chapters are readable prose with **no glyph-ID text**. Each page range starts on the state's own introduction page and ends on its last page (transport or contacts). Excluded on purpose: the full-page photo before each chapter (title caption only), the **regional introduction pages** (pp. 41, 77, 119, 159) that describe several states at once, and the Klang Valley transit map (p. 21), which is glyph-ID text."""),
md("## 2 — Topic 3 steps: extract, clean, chunk (page numbers kept)"),
code(r'''records, stats = prepare(RAW)
stats_df = pd.DataFrame(stats)[['source_id', 'state', 'pages', 'extracted_chars', 'chunks']]
print(stats_df.to_string(index=False))
print('\nNew prepared records:', len(records))

prepared_all = BASE / 'data' / 'processed' / 'prepared_text_all_states.jsonl'
with prepared_all.open('w', encoding='utf-8') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('Saved', prepared_all, prepared_all.stat().st_size, 'bytes')
'''),
md("## 3 — Topic 4 checks on the new chunks (same rules as Week 4b)"),
code(r'''import pandera.pandas as pa

APPROVED = {'MTG_2023.pdf'}
MODIFIED = {'MTG_2023.pdf': date(2025, 5, 28)}
LIGATURE = re.compile(r'/f_|[ﬀ-ﬆ]')
HOURS = re.compile(r'(?i)opening hours|\d{1,2}[.:]\d{2}\s?(?:am|pm)|\b\d{1,2}\s?(?:am|pm)\b')
PRICE = re.compile(r'RM ?\d')
months = lambda d: (date.today().year - d.year) * 12 + (date.today().month - d.month)

df = pd.DataFrame([{
    'chunk_id': i, 'record_id': r['record_id'], 'source': r['source'], 'state': r['state'], 'page': r['page'],
    'text': r['text'], 'char_count': len(r['text'].strip()),
    'has_bad_char': ('\x00' in r['text']) or ('�' in r['text']),
    'has_ligature_artefact': bool(LIGATURE.search(r['text'])),
    'glyph_id_garbage': bool(re.search(r'/gid\d{5}', r['text'])),
    'has_page_ref': r['page'] is not None,
    'source_age_months': months(MODIFIED[r['source']]),
} for i, r in enumerate(records)])

schema = pa.DataFrameSchema({
    'source': pa.Column(str, checks=pa.Check.isin(list(APPROVED), error='source not in approved inventory')),
    'text': pa.Column(str, checks=pa.Check(lambda s: s.str.strip().str.len() > 0, error='chunk text must not be empty')),
    'char_count': pa.Column(int, checks=pa.Check.ge(100, error='char_count >= 100 (shorter than one sentence)')),
    'has_bad_char': pa.Column(bool, checks=pa.Check(lambda s: ~s, error='garbled/replacement characters found')),
    'has_ligature_artefact': pa.Column(bool, checks=pa.Check(lambda s: ~s, error='PDF ligature artefact (/f_ or U+FB00-FB06)')),
    'glyph_id_garbage': pa.Column(bool, checks=pa.Check(lambda s: ~s, error='glyph-ID garbage (/gidNNNNN): unreadable map text')),
    'has_page_ref': pa.Column(bool, checks=pa.Check(lambda s: s, error='page reference missing (traceability)')),
    'source_age_months': pa.Column(int, checks=pa.Check.le(36, error='source older than 36 months')),
}, strict=False)

try:
    schema.validate(df, lazy=True); failures = pd.DataFrame()
except pa.errors.SchemaErrors as exc:
    failures = exc.failure_cases.copy()
failures.to_csv(BASE / 'docs' / 'week4c_validation_failures.csv', index=False)
print('Failures by rule:')
print(failures['check'].value_counts().to_string() if not failures.empty else 'none')
print('\nSource age (months):', df['source_age_months'].iloc[0])
for _, row in df[df['char_count'] < 100].iterrows():
    print(f"SHORT {row['record_id']:14} {row['char_count']:3} chars: {row['text'].strip()!r}")
'''),
md("""### Triage of the short chunks (same decision rules as Week 4b)
| Chunks | Evidence | Decision |
|---|---|---|
| `S12-p66-001` (`ysia`), `S15-p115-001` (`e.`), `S14-p106-002` (`EDAH MAINLAND`), `S12-p73-004`, `S15-p117-003`, `S18-p157-005`, `S19-p194-006` | End-of-page fragments or a cut-off heading | **Remove** — no usable content |
| `S11-p43-001`, `S13-p79-001`, `S16-p121-001` | Title-page slogans (e.g. *"PERAK — LAND of Grace"*) | **Remove** — page furniture |
| `S14-p111-005` (`077 / 1078`) | Tail of a phone number | **Remove** — no usable content |
| `S11-p47-002`, `S17-p136-001`, `S18-p154-002`, `S20-p200-003` | Social-media handles only | **Remove** — same rule as `S04-p93-002` in Week 4b |
| `S11-p46-003` | Broken, repeated link (`www.forestry.ns.gov.my.gov.my`) | **Remove** — the link does not work |
| `S10-p38-003`, `S14-p104-003`, `S20-p204-002` | Real attraction names from a list | **Retain** |
| `S09-p25-003`, `S11-p45-002`, `S16-p122-001`, `S17-p134-001`, `S18-p152-002`, `S19-p188-002` | Sentence endings plus **official website** links (frim.gov.my, jmm.gov.my, pahangtourism.org.my, beautifulterengganu.com, kesedar.gov.my, semenggoh.my) | **Retain** — useful source links |
| `S11-p44-001`, `S12-p72-003`, `S14-p107-003`, `S16-p126-004`, `S18-p153-001`, `S20-p205-006` | Complete sentence endings with attraction or transport facts | **Retain** |
| `S17-p145-003` | Sentence ending plus town labels (Marang, Dungun) | **Retain (review)** — low value |
| Ligature chunks | Same deterministic defect as Topic 4 | **Correct** |"""),
code(r'''import unicodedata
from langchain_core.documents import Document

REMOVE = {
    'S12-p66-001': 'removed: end-of-page fragment', 'S15-p115-001': 'removed: end-of-page fragment',
    'S14-p106-002': 'removed: cut-off heading', 'S12-p73-004': 'removed: end-of-page fragment',
    'S15-p117-003': 'removed: end-of-page fragment', 'S18-p157-005': 'removed: end-of-page fragment',
    'S19-p194-006': 'removed: end-of-page fragment',
    'S11-p43-001': 'removed: title-page slogan', 'S13-p79-001': 'removed: title-page slogan',
    'S16-p121-001': 'removed: title-page slogan',
    'S14-p111-005': 'removed: phone-number fragment',
    'S11-p47-002': 'removed: social-media handle fragment', 'S17-p136-001': 'removed: social-media handle fragment',
    'S18-p154-002': 'removed: social-media handle fragment', 'S20-p200-003': 'removed: social-media handle fragment',
    'S11-p46-003': 'removed: broken repeated link',
}
def repair_ligatures(text):
    text = text.replace('/f_', 'f')
    return re.sub(r'[ﬀ-ﬆ]', lambda m: unicodedata.normalize('NFKC', m.group(0)), text)

new_docs, removed, repaired_n = [], [], 0
for r in records:
    if r['record_id'] in REMOVE:
        removed.append({'record_id': r['record_id'], 'state': r['state'], 'decision': 'removed',
                        'reason': REMOVE[r['record_id']], 'preview': re.sub(r'\s+', ' ', r['text'])[:160]}); continue
    text = repair_ligatures(r['text']); repaired_n += text != r['text']
    meta = {k: r[k] for k in ('source', 'source_id', 'state', 'page', 'record_id', 'source_sha256', 'processing')}
    meta['topic4_ligatures_repaired'] = text != r['text']
    new_docs.append(Document(page_content=text, metadata=meta))
assert len(removed) == len(REMOVE), 'A REMOVE id was not found'
pd.DataFrame(removed).to_csv(BASE / 'docs' / 'week4c_quarantine_log.csv', index=False)
print('Removed:', len(removed), '| ligature-repaired:', repaired_n, '| new chunks kept:', len(new_docs))
print('Ligatures left:', sum(bool(LIGATURE.search(d.page_content)) for d in new_docs))
'''),
md("## 4 — Merge with corpus v2 → corpus v3"),
code(r'''v2_rows = [json.loads(l) for l in V2.open(encoding='utf-8') if l.strip()]
v2_docs = [Document(page_content=r['text'], metadata=dict(r['metadata'])) for r in v2_rows]
print('Corpus v2 chunks:', len(v2_docs))

all_docs = v2_docs + new_docs
seen, unique_docs, dup_rows = {}, [], []
for d in all_docs:
    h = hashlib.sha256(re.sub(r'\s+', ' ', d.page_content.strip()).encode('utf-8')).hexdigest()
    if h in seen:
        dup_rows.append({'hash': h, 'duplicate_source': d.metadata.get('record_id'), 'first_source': seen[h],
                         'preview': d.page_content[:160]}); continue
    seen[h] = d.metadata.get('record_id'); unique_docs.append(d)
print('Before dedup:', len(all_docs), '| after:', len(unique_docs), '| exact duplicates:', len(dup_rows))

def trigrams(t):
    w = re.findall(r'\w+', t.lower()); return set(zip(w, w[1:], w[2:]))
G = [trigrams(d.page_content) for d in unique_docs]
n_v2 = len([d for d in unique_docs if d.metadata.get('source_id') not in {s[0] for s in SOURCES}])
near = [(unique_docs[i].metadata.get('record_id'), unique_docs[j].metadata.get('record_id'), round(len(G[i] & G[j]) / len(G[i] | G[j]), 2))
        for i in range(len(G)) for j in range(max(i + 1, n_v2), len(G))       # new chunks vs everything
        if G[i] and G[j] and len(G[i] & G[j]) / len(G[i] | G[j]) >= 0.5]
print('Near-duplicate pairs involving new chunks (trigram Jaccard >= 0.5):', len(near), near[:10])
pd.DataFrame(dup_rows, columns=['hash', 'duplicate_source', 'first_source', 'preview']).to_csv(
    BASE / 'docs' / 'week4c_duplicate_review.csv', index=False)

with open(BASE / 'data' / 'chunks_clean_v3.pkl', 'wb') as f:
    pickle.dump(unique_docs, f)
with open(BASE / 'data' / 'prepared_chunks_clean_v3.jsonl', 'w', encoding='utf-8') as f:
    for i, d in enumerate(unique_docs):
        f.write(json.dumps({'chunk_id': i, 'text': d.page_content, 'metadata': d.metadata}, ensure_ascii=False) + '\n')
print('Saved corpus v3:', len(unique_docs), 'chunks')
'''),
md("## 5 — Coverage by state and by trip-planning need"),
code(r'''import matplotlib.pyplot as plt
STATES = ['Kuala Lumpur', 'Selangor', 'Putrajaya', 'Negeri Sembilan', 'Melaka', 'Johor', 'Perak', 'Penang',
          'Kedah', 'Perlis', 'Pahang', 'Terengganu', 'Kelantan', 'Sabah', 'Sarawak', 'Labuan']
TOPICS = {
    'Heritage & culture': r'(?i)\b(heritage|temple|mosque|church|colonial|historic|culture|cultural|museum|gallery)\b',
    'Food': r'(?i)\b(food|cuisine|dish|restaurant|hawker|nasi|satay|cafe|dining|eat)\b',
    'Nature & parks': r'(?i)\b(park|garden|forest|nature|lake|hill|waterfall|bird|island|beach|mount)\b',
    'Shopping': r'(?i)\b(shopping|mall|bazaar|market|boutique|retail)\b',
    'Opening hours stated': HOURS.pattern, 'Entry price stated': PRICE.pattern,
    'Disability access info': r'(?i)wheelchair|disabled|\boku\b|barrier-free|step-free',
}
rows = []
for s in STATES:
    docs = [d for d in unique_docs if d.metadata.get('state') == s]
    row = {'state': s, 'chunks': len(docs), 'share_%': round(len(docs) / len(unique_docs) * 100, 1),
           'with_page_ref': sum(d.metadata.get('page') is not None for d in docs)}
    for k, p in TOPICS.items():
        row[k] = sum(bool(re.search(p, d.page_content)) for d in docs)
    rows.append(row)
coverage = pd.DataFrame(rows)
assert coverage['chunks'].sum() == len(unique_docs), 'Some chunks have an unknown state'
assert (coverage['chunks'] > 0).all(), 'A state has no chunks'
print(coverage.to_string(index=False))
coverage.to_csv(BASE / 'docs' / 'week4c_coverage_by_state.csv', index=False)

SERIES, INK, MUTED, SURFACE = '#2a78d6', '#0b0b0b', '#52514e', '#fcfcfb'
order = coverage.sort_values('chunks')
fig, ax = plt.subplots(figsize=(8, 6.2), facecolor=SURFACE); ax.set_facecolor(SURFACE)
bars = ax.barh(order['state'], order['chunks'], height=0.6, color=SERIES)
for b, v, pct in zip(bars, order['chunks'], order['share_%']):
    ax.text(b.get_width() + 3, b.get_y() + b.get_height() / 2, f'{v}  ({pct}%)', va='center', fontsize=9, color=INK)
ax.set_xlabel('Reviewed chunks', color=MUTED)
ax.set_title(f'Corpus v3 coverage by state and federal territory ({len(unique_docs)} chunks)', loc='left', color=INK)
ax.grid(axis='x', color='#e6e5e1', linewidth=0.8); ax.set_axisbelow(True)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color('#c9c8c3'); ax.tick_params(colors=MUTED, length=0)
ax.set_xlim(0, coverage['chunks'].max() * 1.22)
plt.tight_layout(); plt.savefig(BASE / 'docs' / 'week4c_coverage_by_state.png', dpi=150); plt.show()
'''),
md("""**Reading the chart:** every state and federal territory now has official attraction evidence, so no state fails RAI2 outright. Kuala Lumpur still has the most chunks because it has its own 72-page guide, while each guide chapter gives the other states a similar, smaller amount. Coverage must therefore still be compared per state at evaluation time, and popular places from the place-data service help fill the gaps."""),
md("## 6 — Verify and download"),
code(r'''with open(BASE / 'data' / 'chunks_clean_v3.pkl', 'rb') as f:
    reloaded = pickle.load(f)
rows_v3 = [json.loads(l) for l in open(BASE / 'data' / 'prepared_chunks_clean_v3.jsonl', encoding='utf-8') if l.strip()]
assert len(reloaded) == len(rows_v3) and all(a['text'] == b.page_content for a, b in zip(rows_v3, reloaded))
print('PASS: corpus v3 PKL and JSONL match —', len(rows_v3), 'chunks')
print('Ligatures left:', sum(bool(LIGATURE.search(r['text'])) for r in rows_v3),
      '| glyph-ID left:', sum('/gid' in r['text'] for r in rows_v3))

manifest = {'created': str(date.today()), 'method': 'paragraph-aware-char-500, page numbers kept',
            'input_corpus_v2': {'path': 'data/prepared_chunks_clean_v2.jsonl', 'chunks': len(v2_docs),
                                'sha256': hashlib.sha256(V2.read_bytes()).hexdigest()},
            'sources': inspect_rows, 'removed': len(removed), 'new_chunks_kept': len(new_docs),
            'exact_duplicates': len(dup_rows), 'corpus_v3_chunks': len(unique_docs),
            'chunks_by_state': dict(zip(coverage['state'], coverage['chunks'].astype(int).tolist())),
            'outputs': {p: hashlib.sha256((BASE / p).read_bytes()).hexdigest()
                        for p in ['data/processed/prepared_text_all_states.jsonl', 'data/prepared_chunks_clean_v3.jsonl']}}
(BASE / 'data' / 'week4c_all_states_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Saved data/week4c_all_states_manifest.json')

OUT = ['data/processed/prepared_text_all_states.jsonl', 'data/prepared_chunks_clean_v3.jsonl', 'data/chunks_clean_v3.pkl',
       'data/week4c_all_states_manifest.json', 'docs/week4c_validation_failures.csv', 'docs/week4c_quarantine_log.csv',
       'docs/week4c_duplicate_review.csv', 'docs/week4c_coverage_by_state.csv', 'docs/week4c_coverage_by_state.png']
stage = BASE / 'week4c_download'
if stage.exists(): shutil.rmtree(stage)
for p in OUT:
    (stage / p).parent.mkdir(parents=True, exist_ok=True); shutil.copy(BASE / p, stage / p)
    print(f'{p:48} {os.path.getsize(BASE / p):>8} bytes')
archive = shutil.make_archive(str(BASE / 'week4c_outputs'), 'zip', stage)
try:
    from google.colab import files
    files.download(archive)
except ImportError:
    print('Not in Colab — download', archive, 'manually.')
'''),
]
nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}, "language_info": {"name": "python"}}
nbf.write(nb, sys.argv[2]); print("wrote", sys.argv[2], len(cells), "cells")
