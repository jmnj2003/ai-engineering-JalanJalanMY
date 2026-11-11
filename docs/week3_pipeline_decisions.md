# Pipeline Decisions — JalanJalanMY (Week 3)

Version: 1.0
Diagram: `docs/week3_pipeline_diagram.png`
Builds on: `docs/week2_requirements.md`, `docs/week2_architecture_v1.png` (expands the **Source Ingestion & Fact Extraction** component)

## Summary

| Item | Decision |
|---|---|
| **Requirement IDs** | **FR3 / RAI1** (suggest only official attractions, traceable to a source) — main driver. **NFR2 / RAI4** (correct hours and fees, dated) — only partly supported; gap recorded in the data inventory. **NFR5** (update a source without code changes) — supported by the configurable source path. |
| **Selected source** | S01 `IDB_PDF_KLD_EN.pdf` (Tourism Malaysia, KL guide, 72 pages). S02 Penang Map & Guide was inspected but not prepared, because its map layout mixes attraction text with map labels. |
| **Pathway** | A — PDF/TXT (pypdf extraction) |
| **Chosen configuration** | Whitespace cleanup, then **paragraph-aware chunking, 500 characters** |
| **Output location** | Part B: `data/processed/prepared_text.jsonl` + `data/week3_manifest.json`. Part C: `data/pipeline_v1/documents/prepared_text.jsonl` + `pipeline_manifest.json` |

## Part B comparison and evidence

| Configuration A | Configuration B | Observed evidence | Selected approach and trade-off |
|---|---|---|---|
| Fixed-size, 500 characters | Paragraph-aware, 500 characters | Fixed: **287** chunks, **159** cut mid-word, **6** end at a sentence. Paragraph-aware: **303** chunks, **133** cut mid-word, **22** end at a sentence. The extracted text has only 29 blank-line segments, and **all 29 are longer than 500 characters** (longest 37,115), so both methods slice inside attraction entries — the "KL Tower" chunk starts mid-word ("th attractions that…") in both. | **Paragraph-aware.** It respects the guide's section breaks and breaks fewer words, which keeps attraction text together better for FR3/RAI1. |

**Accepted limitation:** because the PDF has few paragraph breaks, most chunks are still 500-character slices, so one attraction (name, address and description) can be split across two chunks, and page numbers are not kept (`page: null`). This is acceptable for V1 because the goal this week is a working, traceable pipeline. Splitting on attraction headings and keeping page numbers is planned for a later version.

## ETL or ELT?

**ETL.** Text is extracted, cleaned and chunked *before* it is stored as the prepared dataset. The planner only ever needs the prepared chunks, the guides are small (one 72-page PDF ≈ 300 chunks), and chunking is a required step before retrieval, so there is no benefit in loading raw text into storage first. The raw PDF is kept unchanged in `data/raw` (with its SHA-256), so the transform can be re-run with a different configuration if needed.

## Batch or streaming?

**Batch.** Tourism Malaysia guides change rarely (S01 modified March 2025, S02 March 2024), so the pipeline runs on demand when a new or updated guide is added (NFR5: ≤ 15 min, no code changes — only the source path changes). Streaming would add complexity for no benefit. Live data the planner needs at trip time — routing travel times and timetables (FR4, FR8) — is fetched through API calls when a plan is checked, **not** through this pipeline.

## Stage contracts

| Stage | Contract / evidence | Failure response |
|---|---|---|
| **Ingest** | `select_source()` / `resolve_source()` finds exactly `IDB_PDF_KLD_EN.pdf` in `data/raw`; SHA-256 recorded (`1484ba6f…`). Use is permitted for coursework. | Stop: `FileNotFoundError` if the file is missing; never pick "the first PDF" automatically. |
| **Inspect** | pypdf returns readable text: 72 pages, 0 empty pages, 143,605 characters. | Stop with "No extractable text — scanned PDFs may require OCR" if text is empty. Map-layout PDFs (S02) are flagged and left out of preparation. |
| **Prepare** | Whitespace cleaned; paragraph-aware chunks of ≤ 500 characters; 303 chunks produced. | Stop with "No text chunks produced" or an invalid-method error; report the failure in the notebook. |
| **Validate** | Output file exists, is non-empty (214,867 bytes Part B; 178,399 bytes Part C), record count matches (303), no empty chunks; output SHA-256 recorded. Two representative records inspected by eye. | Stop for missing or empty output, or a record-count mismatch. |
| **Record lineage** | `week3_manifest.json` links S01 → `data/processed/prepared_text.jsonl` with both checksums (verification PASS). `pipeline_manifest.json` records configuration, source, output and mapping; Cell 9 rerun gives identical fingerprints (PASS). | Stop and report if the source or output is missing, a checksum does not match, or the mapping changes between runs. |

## Difference between Part B and Part C outputs

Both runs produce the **same 303 chunks** with the same configuration. The Part C file is smaller (178,399 vs 214,867 bytes) because the Cell 8A record format is simpler: it stores `id`, `source`, `text` and `page`, while Part B also stores `record_id`, `source_sha256` and `processing` per record. In Part C, the checksum and method are kept once in `pipeline_manifest.json` instead of in every record.

## Provenance and access caveats

- **Copyright:** S01 and S02 are © Tourism Malaysia, "all rights reserved". The PDFs are not committed. The prepared `.jsonl` files contain brochure text, so they are committed only if the repository is private; otherwise only the notebook and manifests are committed and the prepared data stays in local storage.
- **Manifest fields:** the lab code records `source_version` and `access_rights` as "Not verified". The version (PDF modification date) and rights are recorded manually in `docs/week3_data_inventory.md`.
- **Paths:** `pipeline_manifest.json` stores absolute Colab paths (`/content/week3_project/...`), which only exist during a Colab session.
- **Hours and fees gap:** the guides alone cannot support NFR2/FR4. A structured hours source is needed and is listed in the data inventory.
