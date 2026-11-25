# Data Quality, Bias, and Responsible Data Report — JalanJalanMY

Version: 1.0 (Topic 4)
Corpus reviewed: Topic 3 output `data/processed/prepared_text.jsonl` — 303 chunks from the Tourism Malaysia guide *Kuala Lumpur: The Dazzling Capital City* (`IDB_PDF_KLD_EN.pdf`, modified 18 Mar 2025)
Evidence: `notebooks/week4_quality.ipynb`, `docs/week4_validation_failures.csv`, `docs/week4_duplicate_review.csv`, `docs/week4_quarantine_log.csv`, `docs/week4_coverage_by_source.png`, `docs/week4_coverage_by_topic.png`
Reviewed corpus: `data/prepared_chunks_clean.jsonl` + `data/chunks_clean.pkl` — **247 chunks**

> Ratings use 1 (poor) to 5 (strong). **N.V. = Not Verified** — used where the evidence does not exist yet, instead of inventing a score.

## 1. Data Quality Scorecard

| Dimension | Rating (1–5 / N.V.) | Evidence | Action / limitation |
|---|---:|---|---|
| Completeness | **2** | No empty text or source (0/303). But **page reference missing in 303/303**; opening hours in **5** chunks and an RM price in **1** (of 247); **no source for Penang, Melaka or Sabah**; disability-access information in **0** chunks. | Add per-state sources and a structured hours/fee source; keep page numbers when re-chunking. |
| Consistency | **3** | One record format and one processing method (`paragraph-aware-char-500`) for all chunks. But **189/303** chunks start mid-word or mid-sentence, and some chunks mix two attraction entries (e.g. chunk 60). | Re-chunk by attraction heading in Topic 7. |
| Accuracy | **N.V.** | Extraction errors found and handled: **148** chunks with ligature artefacts repaired, **55** unreadable glyph-ID chunks quarantined. Whether the facts themselves (addresses, descriptions) are correct has **not** been checked against official attraction pages. | Hand-check a sample of ≥ 50 facts (NFR2) before Topic 8. |
| Timeliness | **3** | Source is **20 months** old — inside the 24-month rule (0 failures). Individual facts carry no dates; the text has no closure notices (all "temporar…" matches were "contemporary"). | Record edition dates; check the portal for a newer edition each semester; show "last checked" dates (RAI4). |
| Uniqueness | **4** | **0** exact duplicates (247 → 247) and **0** near-duplicate pairs at word-trigram Jaccard ≥ 0.5. | Single source only, so cross-source duplicates and contradictory versions cannot be tested yet. |

## 2. Validation and Data-Defect Findings

Rules run with Pandera (`schema.validate(df, lazy=True)`) on the 303 Topic 3 chunks. 514 failure rows are saved in `docs/week4_validation_failures.csv`.

| Rule | Quality concern | Observable condition | Failures (% of 303) | Examples | Decision |
|---|---|---|---|---|---|
| Text present | Completeness | `text.strip() != ""` | 0 (0%) | — | Hard fail |
| Source present and approved | Completeness / provenance | non-empty and in the Topic 3 inventory | 0 (0%) | — | Hard fail |
| No replacement characters | Accuracy | no `\x00` / `�` | 0 (0%) | — | Hard fail |
| Minimum useful length | Noise / completeness | `char_count >= 100` | 8 (2.6%) | chunk 165 `bibistro.my\n51`; chunk 37 `s a short walk from the station.` | Manual review |
| No PDF ligature artefacts | Accuracy (corruption) | no `/f_`, no U+FB00–FB06 | 148 (48.8%) — 276 artefacts | chunk 7 `magni/f_icent`; chunk 9 `/f_lagpole`, `/f_lies` | Correct |
| No glyph-ID garbage | Accuracy (corruption) | no `/gid` + 5 digits | 55 (18.2%) — chunks 228–282 | chunk 246 `/gid00078/gid00077/…` | Hard fail → quarantine |
| Page reference present | Completeness / traceability | `page is not None` | 303 (100%) | every chunk has `page: null` | Warning |
| Source age | Timeliness | `source_age_months <= 24` | 0 (0%) — age 20 months | — | Warning |

**Summary of defect types found**
- **Missing:** page references (all chunks); opening hours, fees and accessibility data (domain completeness).
- **Corrupted:** ligature artefacts (148 chunks, repaired); glyph-ID map text (55 chunks, quarantined). The template's corruption check (`\x00` / `�`) found **0** of these, so project-specific rules were essential.
- **Noisy:** page numbers and headings inside text (e.g. chunk 111 `…Sale. Sensational Shopping 38`), split words (`bu stling`, `dur ing`), short tail fragments.
- **Inconsistent:** chunk boundaries — 189 chunks start mid-word; chunk 60 holds the end of one attraction and the start of the next.
- **Stale:** none detected by the 24-month rule; fact-level currency is **uncertain**.

**Triage decisions (A5)**
| Case | Interpretation | Decision |
|---|---|---|
| Chunk 165 (14 chars, URL end + page number) | Defect — page furniture | Removed |
| Chunks 68, 96 (spa address and phone; KL Tower fact) | Valid short exceptions | Retained |
| Chunks 37, 105, 155, 176 (sentence endings; 176 ends the Melaka day-trip section) | Boundary fragments with real content | Retained, flagged for re-chunking |
| Chunk 193 (hotel website list) | Low-value directory text | Review further |
| 148 ligature chunks | Deterministic defect (every `/f_` is followed by `i` or `l`) | Corrected (`/f_`→`f`; NFKC for U+FB00–FB06) |
| 55 glyph-ID chunks | Defect, possibly recoverable: partial decoding (lowercase = gid+33, capitals = gid+31) gives "National Heart Institute", "Prince Court Medical Centre" | Quarantined; mapping not verified for digits/symbols, so not guessed |
| Missing page references | Known Topic 3 limitation | Retained with warning |

After correction, the same schema leaves only the page-reference warning (247) and 7 reviewed short chunks.

## 3. Duplicate and Anomaly Findings

- **Exact duplicates:** 0 (SHA-256 of whitespace-normalised text). `docs/week4_duplicate_review.csv` has its header only.
- **Near-duplicates:** 0 pairs at word-trigram Jaccard ≥ 0.5 (extra check in the notebook).
- **Anomalies:** a block of 55 consecutive chunks (228–282) of glyph-ID text from the city-map and legend pages — the largest extraction problem, quarantined. Map codes (`H1`, `H42`, `S7`) appear in the same block.
- **Contradictions / versions:** not testable with one source.
- **Provenance preserved:** every clean chunk keeps `source`, `source_sha256`, `record_id`, `processing`, and new fields `topic4_original_chunk_id` and `topic4_ligatures_repaired`. All 56 removed or quarantined chunks are recorded in `docs/week4_quarantine_log.csv` (55 quarantined, 1 removed), so nothing is dropped silently.

## 4. Representation, Coverage, and Bias Assessment

**Required areas vs evidence (247 clean chunks)**

| Required area | Expected evidence | Actual evidence | Gap? |
|---|---|---|---|
| Kuala Lumpur attractions | Official attraction list | 247 chunks (100%) | No |
| Penang, Melaka, Sabah attractions (RAI2) | Official list per state | No source. KL-guide mentions are incidental — Penang (5 chunks): a dish, a restaurant name, an airport; Sabah (6): handicrafts, geography, a tourist office address; Melaka (7): one short day-trip section, the rest transport/contacts | **Yes — genuine gap** |
| Opening hours / entry fees (FR4, NFR2) | Per attraction | 5 / 1 chunks | **Yes** |
| Interest categories (FR1), keyword **proxy** | Heritage, shopping, food, nature, family | 56 / 51 / 37 / 34 / 10 chunks | Weak for theme parks & family (not yet determinable) |
| Disability access (FR1, RAI2) | Wheelchair / step-free info | 0 chunks | **Yes** |

**Bias risks and propagation paths** (potential risks from data-level evidence — final system fairness is not claimed)

1. **Representation bias — state coverage.**
   *Evidence:* all chunks come from the KL guide; no source for the other three evaluated states.
   *Origin:* source selection (Topic 3 prepared one guide), amplified by a pipeline decision (the Penang map guide was not prepared because of its layout).
   *Path:* one-state source selection → prepared corpus without Penang/Melaka/Sabah attractions → retrieval finds nothing relevant, or only KL chunks → users planning those states get refusals or ungrounded stops.
2. **Measurement bias — missing hours, fees and accessibility, and proxy measures.**
   *Evidence:* hours in 5 chunks, price in 1, accessibility in 0; topic coverage is a keyword proxy; 55 map chunks (hospitals, tourist information centres, transit map) were lost to extraction.
   *Origin:* the source type (brochures rarely publish hours) and pipeline (extraction and chunking).
   *Path:* missing facts in the corpus → constraint checker has nothing to verify → plans pass or fail on missing data → users, especially elderly or wheelchair users, arrive at closed or unsuitable places.
3. **Historical bias — promotional curation.**
   *Evidence:* a national promotion guide emphasising malls (51 chunks) and international hotel brands.
   *Origin:* source — the publisher's choice of what to promote.
   *Path:* curated corpus → retrieval favours well-known commercial places → plans lean towards mainstream stops and away from small local businesses.

## 5. Privacy, Consent, Rights/Access, and Data Governance

| Question | Evidence | Status | Action / owner |
|---|---|---|---|
| Source owner, version and provenance | Tourism Malaysia; modified 18 Mar 2025; SHA-256 `1484ba6f…` in `data/week3_manifest.json`; page numbers missing | OK (document) / Gap (page) | Keep page numbers when re-chunking — Jessie, Topic 7 |
| Rights / access | "© Tourism Malaysia. All rights reserved." Publicly downloadable — but **publicly accessible ≠ public domain**. Used for coursework only. | **To verify** | Confirm with the lecturer; keep the repo private; seek permission before any public deployment — Jessie |
| Personal or sensitive data | Automated scan: 33 distinct e-mail addresses, all institutional tourism-office domains; 35 chunks with business/office phone numbers; 0 Malaysian IC-number patterns | **No** unnecessary personal data | Keep the scan for every new source — Jessie |
| Consent / collection basis | Published institutional document; no personal data collected. User conversation data is outside this corpus (covered by RAI5). | **N/A** | — |
| Update, superseded versions, retention | No defined process for new editions or removal of superseded guides | **Gap** | Record edition dates; check the portal each semester; replace and re-validate — Jessie, before Topic 7 |

## 6. Mitigation Plan and Residual Risk

| Issue | Evidence | Action | Owner / timing | Residual risk |
|---|---|---|---|---|
| No source for Penang, Melaka, Sabah | 0 state-source chunks; incidental mentions only | Add one official source per state; use a layout-aware loader for map-style guides; re-run Topic 4 rules | Jessie — before Topic 7 (Week 9) | Coverage still uneven between states until checked in Topic 8 |
| Opening hours and fees missing | 5 / 1 chunks of 247 | **Fees:** build the verified fee table with the fee-research agent (FR10) — official domains only, URL + quote + date, human spot-check. **Hours:** fetch live from a place-details service at checking time (only place IDs stored); treat "hours unknown" as a flagged condition in the checker | Jessie — Topic 7 | Hours and fees may still be out of date between refreshes (RAI4) |
| Glyph-ID map text | 55 chunks quarantined | Verify the glyph mapping against the PDF, or OCR the map pages; reintroduce only verified text | Jessie — Topic 7 | Map legend (hospitals, information centres, transit) missing meanwhile |
| Chunk boundaries split entries | 189 mid-word starts; chunk 60 mixes two entries | Re-chunk by attraction heading; keep page numbers | Jessie — Topic 7 | Some descriptions may still be separated from their names |
| Ligature corruption | 148 chunks | Repaired (deterministic) | Done — Topic 4 | Low |
| Disability access information absent | 0 chunks | Add accessibility sources (e.g. venue pages); mark accessibility as "unknown" in plans | Jessie — before Topic 8 | Accessibility needs cannot yet be met |
| Rights unclear | All rights reserved | Lecturer confirmation; private repo | Jessie — now | Public deployment not possible without permission |
| No update process | Gap in governance table | Edition date in manifest; semester check | Jessie — Topic 7 | Stale content between checks |

## 7. Impact on Topic 2 Requirements / Evaluation Criteria

| Requirement / criterion | How unresolved data issues could make it fail |
|---|---|
| **RAI2** — ≤ 10 pp quality gap between states | Fails outright while Penang, Melaka and Sabah have no attraction sources. |
| **NFR2** — ≥ 95% fact accuracy (hours, fees) | Cannot be measured or met: hours in 5 chunks, prices in 1. |
| **FR4 / NFR3** — ≥ 95% feasible plans | The constraint checker has almost no hours to check against. |
| **RAI4** — "last checked" date per stop | Only a document-level date exists; facts are undated. |
| **FR3 / RAI1** — 100% grounded stops with source reference | Grounding works at document level (source + SHA-256), but page-level references are missing; mixed-entry chunks risk wrong descriptions. |
| **FR1 / RAI6** — accessibility needs | Accessibility information is absent (0 chunks), so plans cannot yet respect a stated mobility need. |
| **FR8 / RAI7** — public-transport legs | The transit map pages are in the quarantined block; timetables must come from a separate structured source (already planned). |
| **FR10 / RAI9** — verified fee table (≥ 95% fee match; 100% URL + quote + date) | The fee table does not exist yet, so these thresholds cannot be measured until the fee-research agent runs in Topic 7. |

## 8. Topic 4 Quality Gate Decision

**GO WITH CONDITIONS**

The reviewed KL corpus (247 chunks) is sufficiently controlled to proceed: there are no empty, untraceable or duplicated chunks; the corruption that affected 48.8% of chunks was repaired; and the unreadable 18.2% is quarantined and logged. The remaining limitations are understood and documented. Proceeding is safe **only** with these conditions:

1. **Coverage:** add official sources for Penang, Melaka and Sabah and pass them through Topic 3 and Topic 4 checks before Topic 7 retrieval work — or formally narrow the evaluated scope to Kuala Lumpur and update RAI2. *Owner: Jessie, by Week 9.*
2. **Hours and fees:** add a structured hours/fee source before evaluating FR4/NFR2. *Owner: Jessie, Topic 7.*
3. **Rights:** confirm coursework use with the lecturer and keep the repository private. *Owner: Jessie, now.*
4. **Traceability:** keep page numbers and attraction boundaries when re-chunking. *Owner: Jessie, Topic 7.*

A **HOLD** would be appropriate if the scope must stay at four states and no further sources can be obtained, because RAI2 could not then be met.

## 9. Update — State Source Expansion (Week 4b, after the quality gate)

This section records work done **after** the Section 8 decision to meet **condition 1**. Sections 1–8 are kept unchanged as the original Topic 4 record.

**What was added:** six Tourism Malaysia sources for the three missing states (see `docs/week3_data_inventory.md`, S03–S08):
- *Malaysia Travel Guide 2023* state chapters (Melaka pp. 53–63, Penang pp. 89–99, Sabah pp. 159–179)
- the Penang, Melaka and Sabah *Map & Guide* leaflets

They were prepared with the same Topic 3 chunking (paragraph-aware, 500 characters), plus two additions: **page numbers kept**, and a **map-label filter** for the leaflets (dropped 2,854 of 4,370 lines — street and area labels). Evidence: `notebooks/week4_state_expansion.ipynb`.

**Topic 4 checks on the 270 new chunks**

| Rule | Failures | Decision |
|---|---|---|
| Glyph-ID garbage | 0 | — |
| PDF ligature artefacts | 5 | Corrected (same deterministic repair) |
| Minimum length (≥ 100 chars) | 13 | 8 removed (page headers, end-of-page fragments, Sarawak/Labuan captions on the Sabah title page); 5 retained (an attraction name, official website links) |
| Page reference present | 0 | — (page numbers now kept) |
| Source age | 0 at a 36-month limit | Limit raised from 24 to 36 months: the map guides are 32–33 months old, the travel guide 18 months |
| Exact duplicates (against KL corpus too) | 0 | — |
| Near-duplicates (trigram Jaccard ≥ 0.5) | 8 pairs | 6 removed (3 map-guide copies of guide-chapter text that add nothing; 3 copies of a generic "About Malaysia" introduction); 2 retained with a `near_duplicate_of` tag (they add phone numbers) |

Logs: `docs/week4_states_validation_failures.csv`, `docs/week4_states_quarantine_log.csv`, `docs/week4_states_duplicate_review.csv`.

**Corpus v2 — `data/prepared_chunks_clean_v2.jsonl` + `data/chunks_clean_v2.pkl` (503 chunks)**

| State | Chunks | Share | With page ref | Heritage & culture | Food | Nature & parks | Shopping | Hours stated | Price stated | Disability access |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Kuala Lumpur | 247 | 49.1% | 0 | 56 | 37 | 35 | 51 | 5 | 1 | 0 |
| Penang | 89 | 17.7% | 89 | 40 | 14 | 50 | 17 | 3 | 0 | 0 |
| Melaka | 75 | 14.9% | 75 | 43 | 12 | 22 | 15 | 1 | 0 | 0 |
| Sabah | 92 | 18.3% | 92 | 29 | 7 | 49 | 8 | 4 | 0 | 0 |

(Topic columns are keyword **proxies**, as in Section 4.)

**What changed in the assessment**
- **Representation bias (state coverage):** the main gap is closed — every evaluated state now has official attraction evidence. A **residual imbalance** remains: KL holds 49% of chunks against 15–18% for each other state, so retrieval quality per state still needs testing in Topic 8 (RAI2).
- **Completeness:** improved for states and for page references (256 of 503 chunks now have one; only the KL chunks lack it). **Hours, fees and accessibility are still almost absent** in every state. This confirms they must come from the fee-research agent (FR10) and a live place-details source, not from brochures.
- **Uniqueness:** a new cross-source near-duplicate risk appeared, because the same publisher reuses text across publications. It was handled by review, and the 2 tagged pairs must be de-duplicated at retrieval time.

**Updated gate status: GO WITH CONDITIONS**

| Condition (Section 8) | Status |
|---|---|
| 1. Official sources for Penang, Melaka, Sabah, checked before Topic 7 | **Met** — S03–S08 added and checked (this section) |
| 2. Structured hours and fee source | **Open** — planned: fee-research agent (FR10) + live hours, Topic 7 |
| 3. Rights confirmation, private repository | **Open** — confirm with the lecturer |
| 4. Page numbers and attraction boundaries when re-chunking | **Partly met** — page numbers kept for all new sources; KL chunks and heading-based re-chunking remain for Topic 7 |

**Topic 7 onwards uses corpus v2** (`data/prepared_chunks_clean_v2.jsonl` / `data/chunks_clean_v2.pkl`).
