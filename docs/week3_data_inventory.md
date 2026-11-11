# Data Inventory — JalanJalanMY (Week 3)

Version: 1.0
Pathway: A (PDF/TXT)
Notebook: `notebooks/week3_pipeline.ipynb`

## Ingested sources

| Source ID | Filename / URL | Type and purpose | Version / date / owner | Access / rights | Inspection evidence |
|---|---|---|---|---|---|
| S01 | `IDB_PDF_KLD_EN.pdf` — *Kuala Lumpur: The Dazzling Capital City*, Tourism Malaysia e-brochure (portal: https://ebrochures.malaysia.travel) | Unstructured text (PDF brochure). Official list and descriptions of KL attractions — supports **FR3 / RAI1** (suggest only official attractions, with source reference). **Prepared in Part B and Part C.** | Owner: Tourism Malaysia. PDF modified 18 Mar 2025 (metadata; no creation date). SHA-256 `1484ba6f…65b76f7`. | © Tourism Malaysia, "all rights reserved". Coursework use only; PDF **not** committed to the public repo. Stored locally and uploaded to Colab `data/raw` for each run. | 72 pages, 0 empty pages, 143,605 characters extracted with pypdf. Readable prose by section (landmarks, heritage, parks, museums, food). Entry example: "KL Tower — Jalan Puncak, Off Jalan P.Ramlee — KL Tower is one of the most prominent…". Only 8 time mentions and 1 RM price in the whole guide. 303 very short lines (page numbers, headings). |
| S02 | `Map_Guide_PENANG_Eng.pdf` — *Penang Map & Guide*, Tourism Malaysia (portal: https://ebrochures.malaysia.travel) | Unstructured text + map layout (2-page fold-out). Penang attraction names, descriptions, phone numbers — supports **FR3**. **Inspected only** (not prepared this week). | Owner: Tourism Malaysia. PDF created 4 Jan 2024, modified 14 Mar 2024 (metadata). SHA-256 `1f956c18…2735491`. | © Tourism Malaysia, "all rights reserved". Coursework use only; not committed. | 2 pages, 39,446 characters. Descriptions are readable (e.g. "KEK LOK SI TEMPLE — Meaning 'Temple of Supreme Bliss'… Built in 1890…"), but mixed with map-label fragments: 1,765 non-empty lines, 159 of them ≤ 4 characters (grid numbers, "To", street fragments). 40 phone numbers; only 5 time mentions; no RM prices. |

> Confirm the exact download page for each PDF on the Tourism Malaysia e-brochure portal and add it here if it differs.

## Prepared outputs

| Output | Location | From | Records | Notes |
|---|---|---|---|---|
| Part B prepared chunks | `data/processed/prepared_text.jsonl` | S01 | 303 | Paragraph-aware, 500 characters; each record has `record_id`, `text`, `source`, `source_sha256`, `processing`, `page: null` |
| Part B lineage manifest | `data/week3_manifest.json` | S01 | 1 entry | Source and output SHA-256; lineage verification PASS |
| Part C pipeline output | `data/pipeline_v1/documents/prepared_text.jsonl` + `pipeline_manifest.json` | S01 | 303 | Same chunks, simpler record format (`id`, `source`, `text`, `page`); repeatability check PASS |

> **Rights note:** the prepared `.jsonl` files contain text copied from the brochures. Commit them only if the repository is **private**; otherwise commit the manifests and notebook as evidence and record that prepared data is stored locally.

## Known gaps (for Topic 4 quality review)

| Gap | Requirement affected | Planned response |
|---|---|---|
| Opening hours and fees are almost absent from the guides (S01: 8 time mentions, 1 price; S02: 5 time mentions, 0 prices) | **NFR2, FR4, RAI4** — correct hours and fees for feasibility checks | Add a structured hours source: attraction official pages, and the Selangor tourist-attraction list on data.gov.my (has an operating-hours field; CC BY licence). |
| Guides have publication dates, but individual facts are not dated | **RAI4** — "last checked" date per fact | Use the PDF modification date as the source date for now; record a check date when facts are verified. |
| Page numbers not kept in chunks (`page: null`) | **RAI1** — source traceability | Keep page boundaries in a later pipeline version. |
| Map-layout PDFs (S02 type) mix descriptions with map labels | **FR3** — clean attraction text | Not prepared in V1; handle with a layout-aware loader or filter short lines later. |
| Public transport timetables (FR8) not yet ingested | **FR8, RAI7** | Separate structured source (official open-data timetables) in a later week. |
