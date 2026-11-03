# Requirements Specification — JalanJalanMY

Version: 1.0
Project: JalanJalanMY — Grounded Itinerary Planner for Malaysia
Builds on: `docs/week1_project_scope.md`

---

## Section 0 — Project Framing & Application Scope Checkpoint

| Framing element | JalanJalanMY |
|---|---|
| **Problem Evidence** | **1. AI travel tools give wrong or non-existent recommendations.** In an August 2026 survey of U.S. leisure travellers, 16% of those who used AI for travel were recommended a place, tour or activity that did not exist, and 55% received at least one bad recommendation. Incorrect prices, hours or details was the most common problem (27%). Source: Greetwell survey via Stacker/KEYT, 16 Sept 2026 — https://keyt.com/lifestyle/travel/stacker-travel/2026/09/16/survey-ai-hallucinated-travel-destinations-for-1-in-6-users/ (note: run by a travel concierge company). <br>**2. Malaysia's visitor market is large and growing.** 42.2 million visitor arrivals in 2025 (+11.2% from 38 million in 2024); Visit Malaysia 2026 targets about 45 million visitors. Sources: https://says.com/my/news/malaysia-records-42-2-million-visitors-in-2025 ; https://www.ipohecho.com.my/2025/04/30/malaysia-sets-sights-on-45-million-tourists-rm270-billion-in-revenue-for-vm2026/ <br>Together: many people plan Malaysian trips, and the AI tools they increasingly use are unreliable on exactly the facts a plan depends on (hours, prices, existence). |
| **Existing Approaches** | **1. TravelPlanner benchmark** (Xie et al., ICML 2024) — evaluates LLM agents on multi-constraint travel planning; shows GPT-4 reached only a 0.6% success rate. <br>**2. LLM + formal verification** (Hao et al., arXiv:2404.11891) — the LLM converts the request into a constraint problem for a solver; 93.9% success on TravelPlanner, but on synthetic U.S. data. <br>**3. Official tourism portals** (Tourism Malaysia e-brochures, state tourism boards) — authoritative attraction information, but static, split by state and not personalised. <br>**4. Itinerary apps** (e.g. Wanderlog) — help users arrange chosen places, but rely on the user or generic web data and do not verify plans against official opening hours. |
| **Project / Engineering Gap** | LLMs can personalise trips but cannot reliably satisfy hard constraints; official Malaysian tourism information is reliable but fragmented across national and state sources and not personalised; existing planners do not check whether a day — especially a cross-state day — is physically possible. The practical gap is **poor grounding and missing feasibility checking** for personalised Malaysian itineraries. (This is an engineering gap, not a claim of scientific novelty.) |
| **Objective O1** | To design a grounded itinerary planner for Malaysia that uses official national and state tourism sources as its knowledge base and an external routing service for travel times within and across states. |
| **Objective O2** | To develop the planner with a conversational preference agent that collects missing trip details, structured fact extraction (hours, closed days, fees, visit duration, location), preference-based retrieval, a language-model itinerary generator, and a constraint checker that rejects plans with closed venues, impossible travel times or over-budget days. |
| **Objective O3** | To evaluate the planner on constraint-violation rate, grounding, fact accuracy, preference-collection accuracy, coverage fairness across states, latency and cost. |
| **Intended Users** | Domestic and international leisure tourists planning a 1–5 day trip in Malaysia (one state, or neighbouring states by road), including families, elderly travellers and users with budget, accessibility or dietary needs. |
| **Supported Tasks** | 1. Collect trip preferences through a short conversation (destination, days, budget, transport, interests, group, pace, accessibility/food needs). <br>2. Generate a day-by-day itinerary with times, stops and travel legs. <br>3. Show each stop's opening hours, fee and official source with a "last checked" date. <br>4. Check and report feasibility (opening hours, travel time, budget). <br>5. Revise the plan when the user changes a preference (e.g. "add Ipoh", "make it cheaper"). |
| **Information / Knowledge Domain** | Official Malaysian tourism information: attractions, opening hours, closed days, entry fees, typical visit duration, location and category, from Tourism Malaysia and state tourism bodies. Travel time and distance from a routing service. Full evaluation on 4 states: Penang, Kuala Lumpur, Melaka, Sabah. |
| **Operating Context** | A web application used before a trip (planning at home) and occasionally during the trip on a phone. Single user per session; no account required. |
| **Important Constraints** | **Data:** official sources differ in format and detail by state; hours and fees change over time. **Access:** the routing service has a monthly free usage cap (10,000 requests per SKU per month for route computation); routing results may not be stored long-term under the provider's terms. **Budget:** student project — near-zero running cost. **Time:** one semester. **Policy:** source documents not redistributed in the public repo; API keys never committed. **Technical:** cross-state routing by road only within Peninsular Malaysia. |
| **Explicit Out-of-Scope Tasks** | Booking or paying for hotels, transport, tickets or tours. Flights, including Peninsular ↔ East Malaysia. Trips outside Malaysia. Visa, immigration or legal advice. Medical or safety-critical advice (e.g. whether a hike is safe for a heart condition). Recommending places that are not in the official knowledge base. Guaranteeing that hours or prices are current. |
| **Evaluation Focus** | Does JalanJalanMY produce personalised itineraries that are **grounded** (every stop comes from an official source), **feasible** (no closed venues, achievable travel times, within budget) and **accurate** (correct hours and fees) — consistently across states — at acceptable latency and cost? |
| **Traceability** | O1 → FR3, FR4, NFR2, RAI1 (grounding, sources). O2 → FR1, FR2, FR5, FR6, NFR1, NFR3 (agent, planning, checking). O3 → all NFR and RAI thresholds, evaluated in `week2_evaluation_criteria.md`. |

---

## Section 1 — Functional Requirements

| # | Requirement — The system SHALL | Scope Boundary — SHALL NOT (where relevant) |
|---|---|---|
| FR1 | Ask the user for any missing trip details (destination state(s), number of days, daily budget, transport mode, interests, travel group, pace, accessibility and dietary needs), and confirm a trip summary before generating a plan. | Generate a plan without confirming the trip summary, or ask again for details the user has already given. |
| FR2 | Generate a day-by-day itinerary for 1–5 days showing, for each stop, the planned arrival time, visit duration and travel time from the previous stop. | Plan trips longer than 5 days, trips outside Malaysia, or trips requiring flights. |
| FR3 | Include only attractions that exist in the official-source knowledge base, and show each stop's opening hours, entry fee, source reference and "last checked" date. | Recommend or invent places, events or details not supported by an official source. |
| FR4 | Check every plan before display for: venue open at the planned time, achievable travel time between consecutive stops, and total daily cost within the user's budget; and revise or flag any plan that fails a check. | Show a plan containing a known violation without clearly marking it. |
| FR5 | Update the itinerary when the user changes a preference (e.g. adds a state, lowers the budget, changes the pace), and re-run the feasibility checks. | Silently drop previously confirmed preferences when updating. |
| FR6 | Decline requests outside the defined trip-planning scope (bookings, payments, visas, flights, medical or legal questions, non-Malaysian destinations) and redirect the user to an appropriate official channel. | Perform bookings or payments, or give visa, legal or medical advice. |
| FR7 | Present itineraries in clear English suitable for domestic and international tourists, including a "verify before visiting" notice. | — |

---

## Section 2 — Non-Functional Requirements

| # | Quality Attribute | Requirement | Measurement Method | Metric | Threshold |
|---|---|---|---|---|---|
| NFR1 | Performance | The system shall return a complete verified itinerary within an acceptable waiting time, and respond to each preference question quickly. | Run the 40-request evaluation workload (10 per evaluated state, including 10 cross-state trips) and log end-to-end time; separately log time per preference-agent turn. | p90 itinerary latency; p90 agent-turn latency | Itinerary ≤ 20 s; agent turn ≤ 4 s |
| NFR2 | Correctness | Opening hours and entry fees shown in itineraries shall match the official source. | Hand-check a random sample of at least 50 displayed stops against their official source pages. | Fact accuracy (%) | ≥ 95% |
| NFR3 | Reliability | Displayed itineraries shall be feasible: no closed venues, achievable travel times, within budget. | Run the 40-request workload; check each displayed plan with an independent script (opening hours + recomputed travel times + cost total). | % of plans with zero constraint violations | ≥ 95% |
| NFR4 | Cost | Running cost shall fit a student budget. | Record language-model token usage and routing-service calls across the evaluation workload. | Model cost per itinerary; routing calls per month | ≤ US$0.05 per itinerary (illustrative); routing calls within the provider's monthly free cap |
| NFR5 | Maintainability | Updated or newly added official source documents (e.g. a new state) shall be incorporated without code changes to other components. | Controlled update test: replace one state's source document and add one new state's sources; time the process. | Update time; code files changed | ≤ 15 min; 0 code files changed |

---

## Section 3 — Responsible AI Requirements

| # | Responsible AI Risk | Requirement | Measurement Method | Metric | Threshold |
|---|---|---|---|---|---|
| RAI1 | Hallucination / Grounding | Every stop shall be traceable to an official source in the knowledge base, with a working source reference. | For all displayed stops in the evaluation workload, match each stop to a knowledge-base entry and check the source reference. | Grounded-stop rate; source-reference presence rate | 100% grounded; 100% presence |
| RAI2 | Fairness / Coverage across states | Plan quality shall not differ beyond an agreed tolerance between evaluated states. | Compute NFR3 feasibility rate and preference-match rate separately for Penang, Kuala Lumpur, Melaka and Sabah. | Largest gap between any two states | ≤ 10 percentage points |
| RAI3 | Safety / Scope | The system shall decline out-of-scope or unsafe requests and redirect appropriately, and shall cap daily driving time. | Run a scope/safety test set of at least 20 queries (bookings, visas, medical, flights, foreign destinations, unsafe activities); check all cross-state plans for driving time. | Refusal-and-redirect success rate; plans exceeding the driving cap | ≥ 95% refusal success; 0 plans with > 5 h driving per day |
| RAI4 | Outdated information / Transparency | Every stop shall show a "last checked" date, and stops whose source is older than the freshness limit shall be flagged. | Inspect all displayed stops; compare source dates against the freshness limit. | Date-shown rate; unflagged stale stops | 100% shown; 0 unflagged stops older than 6 months |
| RAI5 | Privacy & Security | The system shall not store personal data from conversations, and API keys shall never appear in the repository or client. | Inspect logs after the test workload for names/phone numbers/emails; run a secret scan on the repository history. | PII items found in logs; secrets found in repo | 0; 0 |
| RAI6 | Misread preferences | The preference agent shall correctly capture the user's stated trip details. | Run 30 scripted conversations with known target values (including vague answers like "not too expensive"); compare the confirmed summary to the targets. | Slot-filling accuracy; average questions per conversation | ≥ 90% accuracy; ≤ 5 questions |

---

## 🤔 Reflection — Which Responsible AI requirement is most difficult to measure or enforce?

**RAI4 (outdated information)** is the hardest to enforce. RAI1 can be enforced in code because a stop either exists in the knowledge base or it does not. RAI4 depends on facts that change in the real world without telling us: a museum can change its hours or close permanently the day after we collect the data, and the official page itself may be out of date. The system can only show the date we last checked and flag old entries — it cannot know the true current state. Measuring it is also costly, because checking whether the information is still correct needs manual re-verification of each source. This means RAI4 reduces the harm (users are warned) rather than removing it, which is why the "verify before visiting" notice is part of FR7.
