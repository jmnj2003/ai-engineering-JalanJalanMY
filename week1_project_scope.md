# Week 1 Project Scope — JalanJalanMY

**Project Name**
JalanJalanMY — Grounded Itinerary Planner for Malaysia (RAG + Google Maps)

**Domain**
Tourism / Travel Planning

**Problem Statement**
Tourists planning a trip in Malaysia must combine information from Tourism Malaysia, separate state tourism boards and individual attraction websites, then work out opening hours, fees and travel time between places, including across states (e.g. Penang → Ipoh → Cameron Highlands). General-purpose AI trip planners are fast but often recommend places that are closed, wrongly described or do not exist, and they do not check whether a day's plan is physically possible. AI engineering makes it possible to build a system that generates a personalised day-by-day itinerary in which every stop is retrieved from official sources (RAG) and every leg of travel is checked with real routing data (Google Maps API).

**Evidence of the Problem**
Evidence 1: Current AI travel tools frequently give wrong or non-existent recommendations. In an August 2026 survey of U.S. leisure travellers, 16% of those who used AI for travel were recommended a place, tour or activity that did not exist, and 55% received at least one bad recommendation; incorrect prices, hours or details was the most common problem (27%). (Note: survey run by a travel concierge company.)
Source / citation: Greetwell (2026), reported by Stacker/KEYT, 16 Sept 2026. https://keyt.com/lifestyle/travel/stacker-travel/2026/09/16/survey-ai-hallucinated-travel-destinations-for-1-in-6-users/

Evidence 2: Malaysia has a very large and growing visitor market, so reliable trip planning affects millions of people. Malaysia recorded 42.2 million visitor arrivals in 2025, up 11.2% from 38 million in 2024, and the Visit Malaysia 2026 campaign targets about 45 million visitors and RM270 billion in tourism receipts.
Source / citation: SAYS (citing Bernama), *Malaysia Records 42.2 Million Visitors In 2025*, 27 Jan 2026 — https://says.com/my/news/malaysia-records-42-2-million-visitors-in-2025 ; Ipoh Echo, *Malaysia sets sights on 45 million tourists, RM270 billion in revenue for VM2026*, 30 Apr 2025 — https://www.ipohecho.com.my/2025/04/30/malaysia-sets-sights-on-45-million-tourists-rm270-billion-in-revenue-for-vm2026/

**Initial Related Work (at least 3)**

Study / solution 1: TravelPlanner benchmark — tests LLM agents on realistic multi-constraint travel planning with tools, about four million data records and 1,225 planning tasks.
Source / citation: Xie, J., Zhang, K., Chen, J., Zhu, T., Lou, R., Tian, Y., Xiao, Y., & Su, Y. (2024). TravelPlanner: A Benchmark for Real-World Planning with Language Agents. *ICML 2024*, PMLR 235. https://proceedings.mlr.press/v235/xie24j.html
Key limitation: Shows LLMs alone are unreliable planners — GPT-4 achieved only a 0.6% success rate because agents fail to keep track of multiple constraints.

Study / solution 2: LLM + formal verification for travel planning — the LLM converts the request into a constraint-satisfaction problem that a solver solves, reaching a 93.9% success rate on TravelPlanner.
Source / citation: Hao, Y., Chen, Y., Zhang, Y., & Fan, C. (2024). Large Language Models Can Solve Real-World Planning Rigorously with Formal Verification Tools. arXiv:2404.11891. https://arxiv.org/abs/2404.11891v3
Key limitation: Evaluated on synthetic U.S. benchmark data; not grounded in a real country's official, changing tourism information or real road travel times.

Study / solution 3: Official tourism portals and consumer itinerary apps — Tourism Malaysia publishes official e-brochures and state boards (e.g. Penang Global Tourism, Sabah Tourism Board) publish attraction information; apps such as Wanderlog help users arrange places into a trip.
Source / citation: Tourism Malaysia e-brochures — https://ebrochures.malaysia.travel ; Wanderlog — https://wanderlog.com
Key limitation: Official portals are authoritative but static, split by state and not personalised; itinerary apps rely on the user or generic web data and do not verify plans against official hours.

**Engineering Gap / Limitation**
Gap / Limitation: LLMs can personalise trips but cannot reliably satisfy hard constraints; official Malaysian tourism information is reliable but fragmented across national and state sources and not personalised; and existing planners do not check whether multi-state days are physically possible. There is no Malaysian system that combines RAG over official national and state tourism sources with real routing data to generate personalised, verified itineraries, including cross-state trips.

**Initial Project Objectives (2–3)**
O1: To design a RAG-based itinerary planner that uses official Malaysian tourism sources (Tourism Malaysia and state tourism boards) as its knowledge base, and the Google Maps Routes API for travel times within and across states.
O2: To develop the system with a conversational preference agent that asks the user only for missing trip details (destination, days, budget, transport, interests, travel group, pace, accessibility and food needs), structured fact extraction (hours, closed days, fees, visit duration, location), preference-based retrieval, an LLM itinerary generator and a constraint checker that rejects plans with closed venues, impossible travel times or over-budget days.
O3: To evaluate itineraries on constraint-violation rate, grounding (every stop exists in an official source), fact accuracy, travel-time feasibility, interest match, coverage fairness across states and latency, and the preference agent on slot-filling accuracy and number of questions asked.

**Target Users**
Domestic and international tourists planning a 1–5 day leisure trip in Malaysia, either within one state or across neighbouring states, including users with budget or accessibility needs.

**Scope**
- Knowledge base designed to cover all states; **full evaluation on 4 states**: Penang, Kuala Lumpur, Melaka and Sabah (to include East Malaysia).
- Cross-state trips by **road** (car / bus) within Peninsular Malaysia; Sabah trips stay within Sabah. Flights between Peninsular and East Malaysia are out of scope.
- The system plans only; it does not book or pay for anything.

**Data Sources (at least 2)**
Source 1: Tourism Malaysia official e-brochures (national + per-state guides) — URL: https://ebrochures.malaysia.travel
Source 2: Penang Global Tourism (official state tourism bureau) — URL: http://www.mypenang.gov.my ; Penang Hill Corporation (hours and tickets) — https://www.penanghill.gov.my/index.php/en/tickets
Source 3: Sabah Tourism Board — URL: https://tourism.sabah.gov.my ; Kuala Lumpur and Melaka official tourism sources — [add official URLs after checking]
Routing data: Google Maps Platform Routes API (Compute Routes / Compute Route Matrix) — live travel time and distance between stops. Pricing page lists a free monthly usage cap per SKU (10,000 requests/month for Routes Essentials): https://developers.google.com/maps/billing-and-pricing/pricing

**Similar to EduAdvisor**
- RAG over official, authoritative documents.
- Same pipeline idea: load → clean → extract/chunk → embed → vector store → LLM → guardrails → UI.
- Same evaluation focus: accuracy, groundedness, latency and safety.

**Different from EduAdvisor**
- A **preference agent** gathers requirements through short conversation, then the output is a **structured day-by-day plan**, not a free-form chat answer.
- Combines RAG with an **external API (Google Maps)** for real travel times, including **across states**.
- Needs a **constraint checker**: the LLM proposes, rules and routing data verify.
- Uses **time-sensitive data** (hours, fees) that needs "last checked" dates.
- Sources are split across **national and state** bodies with uneven coverage.

**Responsible AI Risks (at least 2)**
Risk 1 — Hallucination: the model invents an attraction or event not in the sources → tourists travel to a place that does not exist. Mitigation: grounding check rejects any stop not in the knowledge base.
Risk 2 — Outdated information: hours or fees change after collection → tourists arrive at a closed venue or face unexpected costs. Mitigation: "last checked" dates and a "verify before visiting" notice.
Risk 3 — Coverage fairness across states: states with less official content (e.g. smaller or East Malaysian destinations) get weaker plans → unequal benefit for local tourism and tourists. Mitigation: measure plan quality per state and report gaps.
Risk 4 — Safety: long cross-state driving days or outdoor activities in monsoon/flood season → fatigue or danger. Mitigation: cap daily driving time and add seasonal warnings from official advisories.
Risk 5 — Misread preferences: the agent misinterprets a vague answer (e.g. "not too expensive") or skips an accessibility need → the plan is unaffordable or unusable for the user. Mitigation: convert vague answers into explicit values and confirm the full trip summary before planning.
Risk 6 — Security and privacy: Google Maps API key leaked in the public repository → misuse and unexpected charges; user trip details logged unnecessarily. Mitigation: keep keys in environment variables / secrets (never committed), restrict the key, and store no personal data.
