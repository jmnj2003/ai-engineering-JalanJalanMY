# Evaluation Criteria — JalanJalanMY

Version: 1.0
Builds on: `docs/week2_requirements.md`

**Evaluation workload (used by several criteria):** 40 trip requests — 10 per evaluated state (Penang, Kuala Lumpur, Melaka, Sabah), of which 10 in total are cross-state road trips in Peninsular Malaysia. Requests vary days (1–5), budget, transport, travel group and interests. Plus a scope/safety set of at least 20 queries and 30 scripted preference conversations. At least 10 workload requests use public transport, so the plans include KTM, rail or bus legs, and at least 15 include user-entered bookings (e.g. a flight landing at Kota Kinabalu at 10:00 am).

| Objective / Requirement ID | Evaluation Criterion | Capability Bucket | Measurement Method | Metric | Threshold | User / Business Outcome |
|---|---|---|---|---|---|---|
| O2 / FR4 / NFR3 | Plan Feasibility | Domain-specific capability | Check every displayed plan from the 40-request workload with an independent script: venue open at planned time, travel time recomputed between stops, daily cost total. | % of plans with zero constraint violations | ≥ 95% | Tourists can follow the plan as written without arriving at closed venues or missing stops. |
| O1 / FR3 / RAI1 | Grounding and Source Traceability | Instruction-following capability | Match every suggested stop to a knowledge-base entry or a place-data record and confirm its source reference and label ("Official guide" / "Popular") are present and correct; check user-named places found in neither source are labelled "not verified". | Grounded-stop rate; source-reference presence rate | 100%; 100% | No non-existent places; users can verify any stop against an official guide or its map listing. |
| O3 / NFR2 | Fact Accuracy (hours and fees) | Domain-specific capability | Hand-check a random sample of ≥ 50 displayed stops against their official source pages. | Fact accuracy (%) | ≥ 95% | Users can rely on the times and prices shown when planning their day and budget. |
| O2 / FR1 / RAI6 | Preference Collection | Instruction-following capability | Run 30 scripted conversations with known target values, including vague answers; compare the confirmed trip summary with the targets. | Slot-filling accuracy; average questions per conversation | ≥ 90%; ≤ 5 questions | Plans match what the user actually wants, without a long questionnaire. |
| O3 / RAI2 | Coverage Fairness across States | Domain-specific capability | Compute plan feasibility and interest-match rates separately for each evaluated state. | Largest gap between any two states | ≤ 10 percentage points | Tourists get similar quality whichever state they visit, including East Malaysia. |
| O2 / FR6 / RAI3 | Out-of-Scope Refusal | Instruction-following capability | Run the scope/safety set (bookings, visas, flights, medical, foreign destinations, unsafe activities). | Refusal-and-redirect success rate | ≥ 95% | Users are not misled into thinking the system books, advises on visas, or approves unsafe plans. |
| O2 / FR8 / RAI7 | Public Transport Leg Accuracy | Domain-specific capability | Check ≥ 20 public-transport legs from the workload against the operator's published timetable; inspect every leg for the "times may change" notice and a working official ticketing link. | Timetable match rate; legs with notice and working link | ≥ 95%; 100% | Users can catch the suggested train or bus, and buy tickets themselves on the official site. |
| O2 / FR9 / RAI8 | Fixed-Booking Handling | Domain-specific capability | Run ≥ 15 workload requests with user-entered bookings (flights, trains, buses, hotel, reservations, must-visit places), including tight and impossible cases; check each plan against the bookings and minimum buffers. | Plans violating a booking or buffer; must-visit places included or explained; impossible cases reported; free time filled with suggested stops that match interests | 0; 100%; 100%; ≥ 80% interest match | Users never miss a booked flight, train or bus, their own picks are respected, and the rest of the day is filled with relevant suggestions. |
| O1 / FR10 / RAI9 | Fee Research Accuracy | Domain-specific capability | Run the fee-research agent over the ticketed attractions in the 4 evaluated states; hand-check at least 30 extracted fees against the official pages; audit every row for source URL, quote, date and an allowlisted domain. | Fee match rate; rows with URL + quote + date; rows from non-official domains | ≥ 95%; 100%; 0 | Tourists see the real official price, with a source they can check, so the daily budget in the plan is trustworthy. |
| O3 / FR7 | Itinerary Clarity | Generation capability | Three test users rate 10 itineraries on a simple 1–5 rubric (easy to follow, times clear, sources visible, notice shown). | Mean clarity score | ≥ 4.0 / 5 | Tourists understand and can use the plan without extra explanation. |
| O3 / NFR1 / NFR4 | Latency and Cost | Cost and latency | Log end-to-end time, agent-turn time, model token usage and routing calls across the workload, and search requests per fee-table refresh. | p90 itinerary latency; p90 agent-turn latency; cost per itinerary | ≤ 20 s; ≤ 4 s; ≤ US$0.05 (illustrative), routing within free cap | Responsive enough for planning, and cheap enough to run on a student budget. |

### Simple clarity rubric (for Itinerary Clarity)
| Score | Meaning |
|---|---|
| 5 | Every stop has time, duration, travel leg, hours, fee and source; easy to follow at a glance |
| 4 | All key information present; minor layout issues |
| 3 | Usable, but some times or sources missing or hard to find |
| 2 | Hard to follow; several missing details |
| 1 | Cannot be followed without asking for help |

---

## 🤔 Reflection — Which evaluation criterion is most important for usefulness?

**Plan Feasibility** is the most important. The whole reason for JalanJalanMY is that existing AI planners produce plans that do not work in real life — closed venues, wrong hours, impossible travel. A plan that is personalised and well-written but sends a family to a museum on its closed day, or schedules a 3-hour drive into a 1-hour gap, fails the user at the moment it matters most. Grounding and fact accuracy are necessary parts of feasibility, but feasibility is the criterion that directly tells us whether a tourist can follow the plan as written. If this threshold is not met, the system is no better than the tools it is trying to improve on.
