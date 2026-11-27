# Shared preparation logic for the state-source expansion (same methods as Topic 3 / Topic 4).
# Usage: python3 -I prep_lib.py <src_dir> <out_jsonl>   (exploration run)
import re, json, hashlib, sys
from pathlib import Path
from pypdf import PdfReader

SOURCES = [  # (source_id, file, state, first_page, last_page, kind)
    ("S03", "MTG_2023.pdf", "Melaka", 53, 63, "guide-chapter"),
    ("S04", "MTG_2023.pdf", "Penang", 89, 99, "guide-chapter"),
    ("S05", "MTG_2023.pdf", "Sabah", 159, 179, "guide-chapter"),
    ("S06", "Map_Guide_PENANG_Eng.pdf", "Penang", 1, 2, "map-guide"),
    ("S07", "Melaka_Map_Guide_IDB_small.pdf", "Melaka", 1, 2, "map-guide"),
    ("S08", "Sabah Map & Guide.pdf", "Sabah", 1, 2, "map-guide"),
    ("S09", "MTG_2023.pdf", "Selangor", 23, 31, "guide-chapter"),
    ("S10", "MTG_2023.pdf", "Putrajaya", 33, 40, "guide-chapter"),
    ("S11", "MTG_2023.pdf", "Negeri Sembilan", 43, 51, "guide-chapter"),
    ("S12", "MTG_2023.pdf", "Johor", 65, 76, "guide-chapter"),
    ("S13", "MTG_2023.pdf", "Perak", 79, 87, "guide-chapter"),
    ("S14", "MTG_2023.pdf", "Kedah", 101, 111, "guide-chapter"),
    ("S15", "MTG_2023.pdf", "Perlis", 113, 118, "guide-chapter"),
    ("S16", "MTG_2023.pdf", "Pahang", 121, 131, "guide-chapter"),
    ("S17", "MTG_2023.pdf", "Terengganu", 133, 145, "guide-chapter"),
    ("S18", "MTG_2023.pdf", "Kelantan", 147, 158, "guide-chapter"),
    ("S19", "MTG_2023.pdf", "Sarawak", 181, 195, "guide-chapter"),
    ("S20", "MTG_2023.pdf", "Labuan", 197, 205, "guide-chapter"),
]
PHONE = re.compile(r'\+?6?0\d[\d\s-]{6,}')

def keep_line(line):
    """Map-label filter: keep sentence lines, phone lines and long upper-case headings."""
    l = line.strip()
    words = re.findall(r"[A-Za-z']+", l)
    return len(words) >= 4 or bool(PHONE.search(l)) or (len(words) >= 2 and l.isupper() and len(l) >= 8)

def fixed_chunks(s, size=500):          # Topic 3, unchanged
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    return [s[i:i + size] for i in range(0, len(s), size)]

def paragraph_chunks(s, size=500):      # Topic 3, unchanged
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    parts, current = [], ""
    for segment in re.split(r"\n\s*\n", s):
        segment = segment.strip()
        if not segment:
            continue
        if len(segment) > size:
            if current:
                parts.append(current); current = ""
            parts.extend(fixed_chunks(segment, size))
        elif len(current) + len(segment) + (2 if current else 0) <= size:
            current += ("\n\n" if current else "") + segment
        else:
            if current:
                parts.append(current)
            current = segment
    if current:
        parts.append(current)
    return parts

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare(src_dir):
    src_dir = Path(src_dir); records, stats = [], []
    for sid, fname, state, a, b, kind in SOURCES:
        path = src_dir / fname; reader = PdfReader(str(path)); digest = sha256(path)
        n_lines = n_kept = 0; chars = 0
        for p in range(a, b + 1):
            text = reader.pages[p - 1].extract_text() or ""
            chars += len(text)
            if kind == "map-guide":
                lines = [l for l in text.splitlines() if l.strip()]
                kept = [l for l in lines if keep_line(l)]
                n_lines += len(lines); n_kept += len(kept)
                text = "\n".join(kept)
            clean = re.sub(r"[ \t]+", " ", text).strip()
            for n, chunk in enumerate(paragraph_chunks(clean, 500)):
                records.append({
                    "record_id": f"{sid}-p{p}-{n:03d}", "text": chunk, "source": fname,
                    "source_id": sid, "state": state, "page": p, "source_sha256": digest,
                    "processing": "paragraph-aware-char-500" + ("+map-label-filter" if kind == "map-guide" else ""),
                })
        stats.append({"source_id": sid, "file": fname, "state": state, "pages": f"{a}-{b}", "kind": kind,
                      "extracted_chars": chars, "map_lines": n_lines, "map_lines_kept": n_kept,
                      "chunks": sum(1 for r in records if r["source_id"] == sid)})
    return records, stats

if __name__ == "__main__":
    recs, stats = prepare(sys.argv[1])
    for s in stats: print(s)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        for r in recs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    L = [len(r["text"].strip()) for r in recs]
    print("records", len(recs), "under100", sum(l < 100 for l in L))
    lig = sum(bool(re.search(r'/f_|[ﬀ-ﬆ]', r["text"])) for r in recs)
    gid = sum('/gid' in r["text"] for r in recs)
    print("ligature chunks", lig, "gid chunks", gid)
    for r in recs:
        if len(r["text"].strip()) < 100: print("SHORT", r["record_id"], repr(r["text"].strip()))
