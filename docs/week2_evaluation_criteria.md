# Evaluation Criteria — JalanJalanMY

Version: 1.0

**Evaluation workload (used by several criteria):** 40 trip requests — 10 per evaluated state (Penang, Kuala Lumpur, Melaka, Sabah), of which 10 in total are cross-state road trips in Peninsular Malaysia. Requests vary days (1–5), budget, transport, travel group and interests. Plus a scope/safety set of at least 20 queries and 30 scripted preference conversations.

| Objective / Requirement ID | Evaluation Criterion | Capability Bucket | Measurement Method | Metric | Threshold | User / Business Outcome |
|---|---|---|---|---|---|---|
| O2 / FR4 / NFR3 | Plan Feasibility | Domain-specific capability | Check every displayed plan from the 40-request workload with an independent script: venue open at planned time, travel time recomputed between stops, daily cost total. | % of plans with zero constraint violations | ≥ 95% | Tourists can follow the plan as written without arriving at closed venues or missing stops. |
| O1 / FR3 / RAI1 | Grounding and Source Traceability | Instruction-following capability | Match every displayed stop to a knowledge-base entry and confirm its source reference is present and points to the official page. | Grounded-stop rate; source-reference presence rate | 100%; 100% | No non-existent places; users can verify any stop against an official source. |
| O3 / NFR2 | Fact Accuracy (hours and fees) | Domain-specific capability | Hand-check a random sample of ≥ 50 displayed stops against their official source pages. | Fact accuracy (%) | ≥ 95% | Users can rely on the times and prices shown when planning their day and budget. |
| O2 / FR1 / RAI6 | Preference Collection | Instruction-following capability | Run 30 scripted conversations with known target values, including vague answers; compare the confirmed trip summary with the targets. | Slot-filling accuracy; average questions per conversation | ≥ 90%; ≤ 5 questions | Plans match what the user actually wants, without a long questionnaire. |
| O3 / RAI2 | Coverage Fairness across States | Domain-specific capability | Compute plan feasibility and interest-match rates separately for each evaluated state. | Largest gap between any two states | ≤ 10 percentage points | Tourists get similar quality whichever state they visit, including East Malaysia. |
| O2 / FR6 / RAI3 | Out-of-Scope Refusal | Instruction-following capability | Run the scope/safety set (bookings, visas, flights, medical, foreign destinations, unsafe activities). | Refusal-and-redirect success rate | ≥ 95% | Users are not misled into thinking the system books, advises on visas, or approves unsafe plans. |
| O3 / FR7 | Itinerary Clarity | Generation capability | Three test users rate 10 itineraries on a simple 1–5 rubric (easy to follow, times clear, sources visible, notice shown). | Mean clarity score | ≥ 4.0 / 5 | Tourists understand and can use the plan without extra explanation. |
| O3 / NFR1 / NFR4 | Latency and Cost | Cost and latency | Log end-to-end time, agent-turn time, model token usage and routing calls across the workload. | p90 itinerary latency; p90 agent-turn latency; cost per itinerary | ≤ 20 s; ≤ 4 s; ≤ US$0.05 (illustrative), routing within free cap | Responsive enough for planning, and cheap enough to run on a student budget. |

### Simple clarity rubric (for Itinerary Clarity)
| Score | Meaning |
|---|---|
| 5 | Every stop has time, duration, travel leg, hours, fee and source; easy to follow at a glance |
| 4 | All key information present; minor layout issues |
| 3 | Usable, but some times or sources missing or hard to find |
| 2 | Hard to follow; several missing details |
| 1 | Cannot be followed without asking for help |

---

## Reflection — Which evaluation criterion is most important for usefulness?

**Plan Feasibility** is the most important. The whole reason for JalanJalanMY is that existing AI planners produce plans that do not work in real life — closed venues, wrong hours, impossible travel. A plan that is personalised and well-written but sends a family to a museum on its closed day, or schedules a 3-hour drive into a 1-hour gap, fails the user at the moment it matters most. Grounding and fact accuracy are necessary parts of feasibility, but feasibility is the criterion that directly tells us whether a tourist can follow the plan as written. If this threshold is not met, the system is no better than the tools it is trying to improve on.
