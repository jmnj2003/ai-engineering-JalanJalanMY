# JalanJalanMY — Grounded Itinerary Planner for Malaysia

> Generates personalised day-by-day trip plans across Malaysia, using RAG over official national and state tourism sources and the Google Maps Routes API to check that every day — including cross-state travel — is actually possible.

## Problem Statement
Malaysian tourism information is split across Tourism Malaysia, state tourism boards and attraction websites, while general AI trip planners often suggest places that are closed, wrongly described or non-existent, and never check travel time between states. JalanJalanMY retrieves stops only from official sources, uses an LLM to personalise the plan, and verifies hours, budget and real travel times before showing it.

## Evidence of the Problem
- 16% of travellers who used AI for travel were recommended a place, tour or activity that did not exist; incorrect prices, hours or details was the most common problem (27%) — Greetwell survey via Stacker/KEYT, Sept 2026: https://keyt.com/lifestyle/travel/stacker-travel/2026/09/16/survey-ai-hallucinated-travel-destinations-for-1-in-6-users/
- Malaysia recorded 42.2 million visitor arrivals in 2025 (+11.2%), and Visit Malaysia 2026 targets about 45 million visitors — https://says.com/my/news/malaysia-records-42-2-million-visitors-in-2025 ; https://www.ipohecho.com.my/2025/04/30/malaysia-sets-sights-on-45-million-tourists-rm270-billion-in-revenue-for-vm2026/

## Initial Related Work / Existing Approaches
- **TravelPlanner benchmark** (Xie et al., ICML 2024) — https://proceedings.mlr.press/v235/xie24j.html. Limitation: GPT-4 reached only a 0.6% success rate; LLMs alone fail multi-constraint planning.
- **LLM + formal verification planning** (Hao et al., arXiv:2404.11891) — https://arxiv.org/abs/2404.11891v3. Limitation: 93.9% on TravelPlanner, but on synthetic U.S. data, not real official sources or road travel times.
- **Official portals and itinerary apps** (Tourism Malaysia e-brochures, state boards, Wanderlog). Limitation: portals are fragmented by state and not personalised; apps do not verify plans against official hours.

## Engineering Gap / Limitation
No Malaysian planner combines RAG over official national and state tourism sources with real routing data to produce personalised, verified itineraries — including cross-state trips.

## Project Objectives
- O1: To design a RAG-based itinerary planner using official Malaysian tourism sources and the Google Maps Routes API.
- O2: To develop it with a conversational preference agent, fact extraction, preference-based retrieval, an LLM planner and a constraint checker (hours, travel time, budget).
- O3: To evaluate constraint violations, grounding, fact accuracy, travel feasibility, interest match, fairness across states and latency.

## Target Users
Tourists planning a 1–5 day leisure trip in Malaysia, within one state or across neighbouring states, including users with budget or accessibility needs.

## Scope
- Evaluated on 4 states: Penang, Kuala Lumpur, Melaka, Sabah.
- Cross-state trips by road within Peninsular Malaysia; Sabah trips stay within Sabah. No flights, no booking.

## System Overview
```
Preference Agent asks only for missing details
   (state(s), days, budget, transport, interests, group, pace, accessibility/food needs)
   → confirms trip summary with the user
   → Retrieve attractions from official sources (RAG / vector store)
   → LLM drafts day-by-day plan
   → Constraint checker: opening hours + budget + Google Maps travel time
   → Invalid? regenerate  |  Valid? show itinerary with sources + "last checked" dates
   → User asks for a change ("add Ipoh") → Preference Agent updates request → re-plan
```

## Data Sources
- Tourism Malaysia official e-brochures — https://ebrochures.malaysia.travel
- Penang Global Tourism — http://www.mypenang.gov.my
- Penang Hill Corporation — https://www.penanghill.gov.my/index.php/en/tickets
- Sabah Tourism Board — https://tourism.sabah.gov.my
- Kuala Lumpur and Melaka official tourism sources — [add URLs]
- Google Maps Platform Routes API — travel time and distance (live, not stored)

> Source documents are collected for local use only and are **not** committed to this repository.
> **API keys are stored in environment variables / Colab secrets and are never committed.**

## Repository Structure
```
docs/        observation sheet, system map, project scope
data/        (local only — see note above)
src/         application code
notebooks/   Colab notebooks (from Week 3)
evaluation/  test trip requests and results
prompts/     system prompts and templates
```

## Weekly Progress
| Week | Focus | Deliverable | Status |
|------|-------|-------------|--------|
| W1 | System map + project scope | README + docs | ✅ |
