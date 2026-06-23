# Hero Software – Senior GTM Analyst Case Study: Blueprint

## Context

The CRO and CEO need to understand why Marketing's +38% MQL growth only translated into +9% Bookings growth while CPL held flat. The core question is: **who is responsible — lead quality or Sales execution?** The answer must be data-backed and end in a concrete, measurable action plan.

We have 4 datasets:
- `leads.csv` — 820 leads (Nov 2025–Apr 2026): source, trade, company_size, lead_score, region, date
- `activities.csv` — 820 rows (1:1 with leads): call_attempts, connected_calls, demos_completed, time_to_first_touch_hours
- `bookings.csv` — 83 closed-won deals: booking_date, deal_size_eur, trade, source
- `transcripts_sample.csv` — 20 disqualified call excerpts: dq_reason_freitext, transcript_excerpt (German)

Overall conversion rate observed: **83 / 820 = ~10.1%** (but this includes all periods; the breakdown by period is critical).

---

## Deliverables

| # | File | Description |
|---|------|-------------|
| 1 | `analysis/funnel_analysis.py` | Full Python script: data loading, merging, all metrics |
| 2 | `analysis/funnel_analysis.md` | Written narrative: findings, hypotheses, action plan |
| 3 | `analysis/charts/` | PNG charts for the presentation (funnel by source, trade, score, time-to-touch) |

---

## Task 1 — Diagnose the Funnel (~60–90 min worth of thinking)

### Analytical Framework

**Step 1: Merge all datasets into a master table**
- LEFT JOIN leads ← activities on lead_id
- LEFT JOIN ← bookings on lead_id (flag as converted = 1/0)
- Add quarter/period dimension to leads.created_at (Q4 2025 vs Q1 2026 vs Q2 2026)

**Step 2: Compute funnel conversion rates by segment**

For each dimension, compute:
- MQL count
- Demo rate (demos_completed ≥ 1 / MQL count)
- Booking rate (converted / MQL count)
- Booking rate from demo (converted / demo ≥ 1)

Dimensions to cut by:
1. **Period** (month or quarter) → shows the degradation over time
2. **Lead source** (Google Ads, Meta Ads, Organic, Referral) → marketing quality signal
3. **Trade** (SHK, Elektro, PV, Maler, Dachdecker) → product-market fit signal
4. **Company size** (1-2 MA, 3-5 MA, 6-15 MA, 16-50 MA, 50+ MA) → ICP fit signal
5. **Lead score bucket** (0-39, 40-59, 60-79, 80-100) → scoring model validity signal

**Step 3: Sales effort analysis**
- Average call_attempts and connected_calls by conversion outcome
- Time-to-first-touch distribution: does fast follow-up predict conversion?
- Which segments get the MOST attempts vs. the LEAST? (SDR prioritization bias)

**Step 4: Identify the primary break point**
- Map where the biggest drop occurs: MQL → Connect → Demo → Booking
- Determine if the drop is uniform or concentrated in specific segments

### Hypotheses to Test

**H1: Lead quality degraded — Marketing filled the funnel with low-fit leads**
- Signal: MQL growth concentrated in low lead_score leads OR in trades/sizes with historically low conversion
- Test: Compare lead_score distribution and trade mix Q4 2025 vs Q1-Q2 2026
- Expected finding: PV and 1-5 MA segments grew disproportionately and have low booking rates

**H2: Sales execution bottleneck — SDRs aren't connecting or following up fast enough**
- Signal: Low connect rate (connected_calls / call_attempts), high time-to-first-touch on non-converted leads
- Test: Compare time_to_first_touch_hours for converted vs non-converted; look at demo rate by call_attempts
- Expected finding: Leads touched within 2h convert at 2-3x the rate of leads touched after 24h+

**H3: Demo-to-close rate dropped — qualification is weak, wrong leads reach demo stage**
- Signal: Demo rate may be fine, but close rate from demo fell
- Test: (bookings with demos) / (total demos completed) by period
- Expected finding: Demo quality degraded because SDRs pushed unqualified leads to demo to hit activity metrics

### Priority Hypothesis
Based on the transcript data, **H1 is the primary driver** (wrong-fit leads entering the funnel), with **H2 as a compounding factor** (slow follow-up wastes even the good leads that do enter).

---

## Task 2 — The Creative Lever (Transcript Analysis)

### Conceptual Sketch: Automated Disqualification Intelligence Loop

The 20 transcripts are currently an untapped qualitative signal. The approach:

**A. Structured tagging layer**
Classify each transcript on:
- `dq_category`: (Price | Timing | Fit | Competitor | Effort | Wrong Contact)
- `objection_type`: (Price sensitivity | Feature gap | Business stage | Incumbent | Product confusion)
- `company_size_signal`: extracted from transcript text
- `urgency_signal`: 1 (immediate), 2 (6 months), 3 (no timeline)

**B. Cross-reference with leads/activities data**
Join transcripts to leads.csv on lead_id → check if the dq_reason correlates with:
- Lead source (which channel brings the "Just comparing" crowd?)
- Lead score (are high-scored leads still being disqualified? → scoring model is broken)
- Trade (are PV leads disproportionately "Product confusion" DQ?)

**C. Two Concrete Example Outputs**

*Output 1 — For Marketing: Lead Source Contamination Map*
| Source | Primary DQ Reason | % of DQs | Action |
|--------|------------------|-----------|--------|
| Meta Ads | "Nur Info" / "Falsche Erwartung" | 40% | Tighten ad creative — show actual product screenshots |
| Google Ads | "Kein Bedarf jetzt" | 30% | Add negative keywords: "Was ist...", "Wie funktioniert..." |
| Organic | "Wettbewerber" | 20% | Create competitor comparison landing pages |

*Output 2 — For Sales: Objection-Specific Call Playbooks*
| Objection Pattern | Recommended Response | Example from Transcript |
|---|---|---|
| "I'm just comparing" | Trigger urgency with ROI calculator, offer free 30-day trial | T008: "Ich vergleiche gerade verschiedene Anbieter" |
| "We use Excel" | Anchor on time-cost of Excel: "How many hours/week on admin?" | T003: "Wir machen das noch mit Excel" |
| "PlanCraft is cheaper" | Reframe on total value, integration depth | T015: "PlanCraft kostet weniger pro Nutzer" |

**D. Scale path (beyond 20 transcripts)**
- Build a lightweight NLP tagger (keyword rules or LLM prompt) to classify ALL future call notes
- Feed weekly DQ breakdown back into lead scoring model as a negative signal
- Create a "DQ reason → Marketing insight" feedback loop (weekly digest to CMO)

---

## Task 3 — The Action Plan

### Who to talk to first (sequence matters)

1. **RevOps (Day 1-2)**: Validate data. Confirm lead_score model inputs, CRM field definitions. Are demos logged consistently? Is "connected_call" standardized across SDRs?
2. **Sales leadership (Day 3-4)**: Share the connect rate and time-to-touch findings. Not accusatory — frame as "where can we unlock capacity?" Walk them through H2.
3. **Marketing (Day 5-6)**: Share the source/trade conversion waterfall. Focus on which channels bring leads that actually close. Propose MQL re-definition with SQL criteria.
4. **CRO + CEO (Week 2)**: Present the full diagnosis with a prioritized 30/60/90-day plan.

### How to measure success

**Primary metric**: Lead-to-Booking conversion rate (target: recover from current ~10% toward ~14% within 60 days)

**Secondary metrics by hypothesis**:
| Metric | Baseline | 4-week target | Owner |
|--------|----------|---------------|-------|
| Demo rate (demos/MQLs) | TBD from analysis | +20% relative | Sales |
| Time-to-first-touch median | TBD | < 4 hours | SDR Manager |
| Booking rate from Referral+Organic | TBD | Hold or improve | Marketing |
| % of MQLs with lead_score ≥ 60 | TBD | +10pp | Marketing/RevOps |

**Threshold for hypothesis confirmation**: If conversion rate improves by ≥ 2pp within 4 weeks of implementing the primary fix, hypothesis is validated.

### Contingency if hypothesis doesn't hold after 4 weeks

- If H1 (lead quality) is wrong → pivot to H2 (Sales execution): implement SLA for time-to-touch, A/B test SDR assignment by lead score
- If H2 is wrong → test H3 (demo quality): add qualification checklist before demo, track demo-to-close separately
- Maintain a weekly metric review cadence so course corrections happen at 2-week intervals, not 4

---

## Execution Plan (What We'll Build)

### Phase 1: Python Analysis Script (`analysis/funnel_analysis.py`)
1. Load all 4 CSVs
2. Merge into master DataFrame
3. Compute period flags (Q4 2025, Q1 2026, Q2 2026)
4. Build funnel waterfall table (MQL → Connect → Demo → Booking) overall
5. Break down by: source, trade, company_size, lead_score_bucket, period
6. Sales activity analysis: conversion by time_to_first_touch bucket, call_attempts
7. Transcript analysis: frequency table of dq_reasons + cross-ref with lead attributes
8. Output: summary tables printed + charts saved to `analysis/charts/`

### Phase 2: Written Narrative (`analysis/funnel_analysis.md`)
Structure mirrors the 3 case tasks:
- Executive Summary (3 bullets — CRO/CEO-ready)
- Funnel Diagnosis (data tables + chart refs + hypothesis ranking)
- Creative Lever (transcript framework + 2 example outputs)
- Action Plan (stakeholder sequence + metrics + contingency)

### Phase 3: Charts (`analysis/charts/`)
- `funnel_waterfall_overall.png` — MQL → Connect → Demo → Booking overall
- `conversion_by_source.png` — booking rate per lead source
- `conversion_by_trade.png` — booking rate per trade
- `conversion_by_company_size.png` — booking rate per company size
- `lead_score_distribution_by_period.png` — score distribution Q4 vs Q1 vs Q2
- `time_to_touch_vs_conversion.png` — bar chart of conversion rate by time bucket
- `dq_reasons_breakdown.png` — horizontal bar of disqualification reason frequency

---

## Verification

1. Run `funnel_analysis.py` end-to-end — no errors, all charts generated
2. Confirm 820 leads + 83 bookings = ~10.1% overall conversion rate matches calculation
3. Validate that the MQL growth story is reproducible from the data (period-over-period counts)
4. Sanity check: booking counts per source in bookings.csv match bookings attributed via leads.csv join
5. Review the narrative for executive clarity — would a CEO understand it in 5 minutes?
