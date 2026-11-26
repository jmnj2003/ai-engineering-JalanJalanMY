# Architecture Decisions & Traceability — JalanJalanMY

Version: 1.1 (popular places added to grounding sources)
Diagram: `docs/week2_architecture_v1.png`
Builds on: `docs/week2_requirements.md`, `docs/week2_evaluation_criteria.md`

---

## Step C1 — Simplest architecture

```
User Query → AI Application → AI Capability (language model) → Response
```

**Main interaction:** a tourist describes a trip and receives a day-by-day itinerary.
**AI capability needed:** a language model that turns preferences into a plan.

**Can this support our requirements?** Only partly. A language model alone can write a personalised plan (FR2), but it cannot:
- guarantee every stop is real and verifiable, from an official guide or a place-data record (FR3, RAI1) — it plans from its own memory;
- know current opening hours and fees (NFR2);
- calculate real travel times, especially across states (FR4, NFR3);
- reliably refuse bookings, visas or unsafe requests (FR6, RAI3).

The TravelPlanner benchmark in our related work confirms this: a language model alone reached only a 0.6% success rate on multi-constraint travel planning. So components are added below, each justified by a requirement.

---

## Step C2 — Architecture needs from requirements

| Requirement ID | What does the requirement need? | Architecture Response |
|---|---|---|
| FR3 / RAI1 | Every stop must be verifiable — an official pick or a popular, highly rated place (proposed ≥ 4.2★ from ≥ 500 reviews) — with a source reference and label. | **Knowledge Source** of official attraction facts + external **Place-Data Service** for popular places (only the place ID stored) + **Knowledge Access** that retrieves only from these two |
| NFR2 / RAI4 / NFR5 | Hours and fees must match the source, carry a "last checked" date, and be easy to update per state. | **Source Ingestion & Fact Extraction** (offline) that turns official documents into structured facts with dates |
| FR4 / NFR3 | Plans must be checked for opening hours, travel time and budget before display. | **Constraint Checker** (rule-based) with a revise loop back to the generator |
| FR4 / NFR3 / RAI3 | Real travel times are needed, within and across states, plus a daily driving cap. | External **Routing Service** called by the Constraint Checker |
| FR1 / RAI6 | Missing trip details must be collected and confirmed before planning. | **Preference Agent** (language model service) in front of the planner |
| FR6 / RAI3 | Bookings, visas, flights, medical and non-Malaysia requests must be declined and redirected. | **Scope / Safety Control** before the Preference Agent |
| FR8 / RAI7 | Public-transport legs need official departure/arrival times and a link to the official ticketing site; no ticket checking or buying. | **Public Transport Timetables** (official open data) used by the generator and checker; output shows times + official ticketing link |
| FR9 / RAI8 | The user's booked flights, trains, buses, hotel, reservations and must-visit places must shape the plan, with buffers so no connection is missed. | **Preference Agent** collects and reads back fixed bookings; **Itinerary Generator** plans around them; **Constraint Checker** enforces them as hard constraints with buffers |
| FR10 / RAI9 | Entry fees for ticketed attractions must come from official sources with proof (URL, quote, date), and reseller prices must be rejected. | **Fee-Research Agent** (offline batch, language model + external **Web Search Service**) writes a **verified fee table** into the Knowledge Source after a human spot-check |
| NFR1 / NFR4 / RAI2 / RAI5 | Latency, cost and per-state quality must be measured, without storing personal data. | **Evaluation Point** that logs metrics only (no personal data) |

---

## Step C4 — Architecture Decision Record (ADR)

| Decision | Requirement / Constraint | Alternatives Considered | Selected Option | Trade-off Accepted |
|---|---|---|---|---|
| **AD1 — Ground plans in verified place data** | FR3, RAI1, NFR2: every stop must exist in a verifiable record with correct hours and fees; tourists also want popular places that brochures leave out | (a) Language model only; (b) live open web search at query time; (c) curated knowledge source from official documents only; (d) official knowledge source + popular places from a place-data service (e.g. Google Places) | (d) Official knowledge source + place-data service, both behind Knowledge Access; each stop labelled "Official guide" or "Popular" | Dependence on a third-party service, its free cap and terms (ratings and hours fetched live, only the place ID stored), and a popularity bias towards famous, crowded places (mitigated by ranking on interest match first and including at least one official or local pick per day); in exchange, much wider choice than brochures while keeping 100% grounding — no stop comes from model memory |
| **AD2 — Separate rule-based constraint checker** | FR4, NFR3: displayed plans must be feasible (≥ 95% with zero violations) | (a) Ask the language model to respect constraints in its instructions; (b) full constraint solver that builds the plan; (c) language model drafts, rule-based checker verifies and requests revisions | (c) Generate-then-verify with up to 3 revision attempts | Extra latency and model cost per revision, and a plan may still be shown with flagged violations after 3 attempts; but much more reliable than instructions alone and simpler to build than a full solver |
| **AD3 — External routing service for travel time** | FR4, NFR3, RAI3: real travel times within and across states; NFR4: low cost | (a) Straight-line distance × assumed speed; (b) open-source routing engine hosted ourselves; (c) external routing service | (c) External routing service, called only by the checker, results not stored long-term | Dependency on a third-party service, its usage cap and terms (results used live, not saved); in exchange for accurate road travel times without hosting our own routing |
| **AD4 — Preference agent before planning** | FR1, RAI6: collect and confirm missing details with ≤ 5 questions | (a) Fixed form with all fields; (b) free-text request passed straight to the planner; (c) conversational agent that asks only for missing details | (c) Preference agent with a confirmed trip summary | More complex to build and test, and an extra language-model call per turn (latency, cost); but fewer unnecessary questions than a form and fewer misread requests than free text |
| **AD5 — Explicit scope / safety control** | FR6, RAI3: ≥ 95% correct refusal of out-of-scope requests | (a) Instructions in the agent's prompt only; (b) explicit scope-control component before the agent | (b) Explicit scope / safety control | Possible false refusals of valid trip requests and an extra processing step; but scope behaviour can be tested and changed on its own |
| **AD6 — Timetables + official ticketing links for public transport** | FR8, RAI7: show real departure/arrival times; FR6: no booking; legal and terms-of-use constraints | (a) Scrape ticketing sites for prices and seat availability; (b) third-party paid ticketing/booking API; (c) official open timetable data for times + a link to the operator's official ticketing page | (c) Official timetables + ticketing link; the user buys the ticket themselves | Users must check prices and seat availability on the operator's site, and timetables may change without notice; in exchange, no scraping, no payment handling, no paid API, and the system stays within its "plan, don't book" scope |
| **AD7 — User bookings as hard constraints** | FR9, RAI8: never cause a missed flight, train or bus; respect must-visit places | (a) Mention bookings to the language model in its instructions only; (b) treat bookings as fixed time blocks that the generator plans around and the constraint checker enforces with minimum buffers | (b) Fixed time blocks + enforced buffers; bookings read back to the user for confirmation | Less flexibility — days with tight bookings get fewer stops, and when bookings and must-visit places cannot all fit, the system reports the conflict instead of producing a "complete" plan; in exchange, connections are protected by rules, not left to the model |
| **AD8 — Fee-research agent in a verified batch** | FR10, RAI9: official fees with proof; NFR4: low cost; brochures carry almost no prices (Week 3–4 evidence) | (a) Collect fees fully by hand; (b) search the web live for every user request; (c) an agent searches in a batch, accepts only allowlisted official domains, saves URL + quote + date, then a person spot-checks before use | (c) Batch fee-research agent + human spot-check | Fees can be out of date between refreshes (mitigated by the date shown), and the batch needs a search service with a paid or capped allowance; in exchange, prices are checkable, reseller and invented prices are blocked, and users wait for no live searches |

---

## Initial Requirements Traceability Matrix

| Objective | Requirement | Evaluation Criterion | Architecture Element | Later Evidence |
|---|---|---|---|---|
| O1 | FR3 / RAI1 | Grounding and Source Traceability (100% grounded, 100% source refs) | Knowledge Source + Place-Data Service + Knowledge Access + Constraint Checker (existence check) | Grounding check over all stops in the 40-request workload |
| O1 | NFR2 / RAI4 | Fact Accuracy (≥ 95%) + last-checked dates | Source Ingestion & Fact Extraction | Hand-check of ≥ 50 stops against official pages; date/freshness audit |
| O2 | FR4 / NFR3 | Plan Feasibility (≥ 95% zero-violation plans) | Constraint Checker + Routing Service | Independent feasibility script over the 40-request workload |
| O2 | FR1 / RAI6 | Preference Collection (≥ 90% slot accuracy, ≤ 5 questions) | Preference Agent | 30 scripted conversations with known targets |
| O2 | FR8 / RAI7 | Public Transport Leg Accuracy (≥ 95% timetable match; 100% notice + link) | Public Transport Timetables + Constraint Checker + Output | Sample check of ≥ 20 legs against operator timetables |
| O2 | FR9 / RAI8 | Fixed-Booking Handling (0 violated bookings/buffers; 100% impossible cases reported) | Preference Agent + Itinerary Generator + Constraint Checker | ≥ 15 workload requests with entered bookings, incl. tight and impossible cases |
| O1 | FR10 / RAI9 | Fee Research Accuracy (≥ 95% fee match; 100% URL + quote + date; 0 non-official domains) | Fee-Research Agent + Web Search Service + Knowledge Source (fee table) | Hand-check of ≥ 30 fees against official pages; audit of every fee row |
| O2 | FR6 / RAI3 | Out-of-Scope Refusal (≥ 95%) | Scope / Safety Control | Scope/safety test set of ≥ 20 queries |
| O3 | RAI2 | Coverage Fairness (≤ 10 pp gap between states) | Knowledge Source (per-state coverage) + Evaluation Point | Per-state feasibility and interest-match results |
| O3 | NFR1 / NFR4 | Latency and Cost (p90 ≤ 20 s; ≤ US$0.05 per itinerary) | Evaluation Point | Latency and cost logs from the evaluation workload |

---

## Final review checklist

| Question | Answer |
|---|---|
| Does each major component support a requirement or evaluation need? | Yes — every box in the diagram lists the requirement IDs that justify it (see Step C2). |
| Is any important data source, safety control or evaluation point missing? | Official sources, a place-data service for popular places, scope control, constraint checker and an evaluation point are all present. A user-feedback loop is not in V1; it can be added once the system is tested with users. |
| Have I added any technology or component that is not yet justified? | No specific technologies are named; components are labelled by function. Agentic re-planning during the trip is left out of V1 because no V1 requirement needs it. |
| Is there a simpler architecture that could still satisfy the requirements? | Removing the Preference Agent (using a fixed form) would still satisfy FR2–FR4, but not FR1/RAI6 as written. If time runs short, a form is the fallback, and FR1 would be revised. |

---

## Reflection — Which decision involved the most important trade-off?

**AD2 (generate-then-verify with a separate constraint checker)** involved the most important trade-off. It is driven by **FR4 and NFR3** — displayed plans must be feasible, with at least 95% having zero violations — which is also our most important evaluation criterion. Relying on instructions alone would be fast and cheap, but the TravelPlanner results show a language model on its own cannot keep track of many constraints. Adding a rule-based checker that sends violations back for revision makes feasibility checkable and enforceable. The trade-off we accept is **higher latency and cost** (each revision is another model call, which is why NFR1 allows up to 20 s), plus the possibility that, after 3 attempts, a plan is shown with a clearly flagged violation instead of a perfect one. We judged that a slower but trustworthy plan is more useful to a tourist than a fast plan that may send them to a closed venue.
