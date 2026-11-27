# Week 4c — All-States Expansion (JalanJalanMY)

Adds the 12 remaining chapters of Tourism Malaysia's *Malaysia Travel Guide 2023* (S09–S20) so the
knowledge base covers all 13 states and 3 federal territories. Same method as Week 4b
(paragraph-aware 500-character chunks, page numbers kept, Topic 4 checks).

| ID | State / FT | Pages | Chunks |
|---|---|---|---|
| S09 | Selangor | 23–31 | 33 |
| S10 | Putrajaya | 33–40 | 29 |
| S11 | Negeri Sembilan | 43–51 | 26 (29 − 3 removed) |
| S12 | Johor | 65–76 | 40 (42 − 2) |
| S13 | Perak | 79–87 | 31 (32 − 1) |
| S14 | Kedah | 101–111 | 38 (40 − 2) |
| S15 | Perlis | 113–118 | 19 (21 − 2) |
| S16 | Pahang | 121–131 | 35 (36 − 1) |
| S17 | Terengganu | 133–145 | 36 (37 − 1) |
| S18 | Kelantan | 147–158 | 37 (39 − 2) |
| S19 | Sarawak | 181–195 | 44 (45 − 1) |
| S20 | Labuan | 197–205 | 24 (25 − 1) |

408 new chunks → 16 removed (fragments, slogans, handle-only text, one broken link), 10 ligatures repaired,
0 duplicates → 392 kept. Corpus v3 = 503 (v2) + 392 = **895 chunks**.

The guide's KL chapter (pp. 7–20) is not added: KL already has its own 72-page guide (S01).

## How to run (Colab)
1. Upload `MTG_2023.pdf` and `data/prepared_chunks_clean_v2.jsonl`.
2. Open `notebooks/week4c_all_states.ipynb` → Runtime → Run all.
3. Download `week4c_outputs.zip` and copy its `data/` and `docs/` folders into the repo.
   It contains `prepared_chunks_clean_v3.jsonl`, `chunks_clean_v3.pkl` and `week4c_all_states_manifest.json`,
   which are made from your real corpus v2 and so are not included here.

The files in `docs/` and `data/processed/` here come from a test run on the same guide; the new-state
chunks are identical to what the notebook produces.
