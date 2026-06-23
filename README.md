# HERO Software — GTM Funnel Analysis

**Senior GTM Analyst Case Study** · by [Rodrigo Uehara Guskuma](https://www.linkedin.com/in/rodrigo-guskuma/)

A data-backed diagnosis of why Marketing's MQL growth didn't translate into proportional Bookings growth — and a prioritized, measurable action plan to fix it.

---

## The Question

> Marketing grew MQLs by **+38%**, but Bookings only grew **+9%** while CPL stayed flat.
> Sales blames lead quality. Marketing says Sales isn't converting.
> **Who is right, and what should we do about it?**

This repo contains the full analysis answering that question across the case's three tasks:

1. **Diagnose the funnel** — where does it break, what are the root causes, which to fix first.
2. **The creative lever** — turn the 20 disqualified-call transcripts into a repeatable intelligence loop.
3. **The action plan** — who to talk to, in what order, and how to measure success.

---

## TL;DR — The Findings

- **The funnel doesn't break uniformly — it breaks inside one segment.** Solar (PV) leads book at **1.6%**, while the core trades (SHK + Elektro) book at **~21%**.
- **PV quietly took over the pipeline.** PV grew from **34% → 58%** of MQLs. As that low-converting segment grew as a share of the pool, the overall booking rate fell from **11.4% → 6.4%** — a mix-shift effect, not a Sales-execution failure.
- **Both sides are right, about different segments.** Sales is correct that PV leads are unworkable; Marketing is correct that core-trade leads convert well. The real culprit is that **Marketing scaled PV without updating the ICP**, and no feedback loop existed to catch it.
- **The fix is to gate early-stage / sub-scale PV — not to abandon PV.** PV deals are actually the *largest* of any trade (ø €7,857), so the recommendation targets fit, not the whole segment.

Full reasoning, charts, and the action plan are in the analysis documents below.

---

## Repository Structure

```
hero-software-case/
├── README.md                          ← you are here
├── LICENSE                            ← MIT (code/analysis only; see IP note)
├── requirements.txt                   ← Python dependencies
│
├── Case_Study_Senior_GTM_Analyst.pdf  ← the original case brief (Hero Software)
├── project-blueprint.md                ← the planning blueprint written before analysis
│
├── csv_dateien/                       ← source datasets (Hero Software)
│   ├── leads.csv                      ← 820 leads: source, trade, size, score, region, date
│   ├── activities.csv                 ← 820 rows: calls, demos, time-to-first-touch
│   ├── bookings.csv                   ← 83 closed-won deals: date, deal size, trade, source
│   └── transcripts_sample.csv         ← 20 disqualified-call excerpts (German)
│
└── analysis/
    ├── funnel_analysis.py             ← main script: load, merge, metrics, 12 charts
    ├── review_checks.py               ← confounding/robustness checks (e.g. trade × speed)
    ├── audit.py                       ← data-integrity audit
    │
    ├── funnel_analysis.md             ← full written narrative (all 3 tasks)
    ├── rodrigo_uehara_guskuma_case_senior_data_analyst_gtm.md  ← 15-minute presentation version
    ├── rodrigo_uehara_guskuma_case_senior_data_analyst_gtm.pdf ← exported slides
    ├── data_questions.md              ← data inconsistencies + questions for the interviewer
    │
    └── charts/                        ← 12 generated PNG charts
```

### Where to start reading

| If you want… | Read |
|---|---|
| The full story, with all evidence | [`analysis/funnel_analysis.md`](analysis/funnel_analysis.md) |
| The 15-minute presentation version | [`analysis/rodrigo_uehara_guskuma_case_senior_data_analyst_gtm.md`](analysis/rodrigo_uehara_guskuma_case_senior_data_analyst_gtm.md) |
| How I planned the work before touching data | [`project-blueprint.md`](project-blueprint.md) |
| The sharp questions I'd ask the stakeholders | [`analysis/data_questions.md`](analysis/data_questions.md) |

---

## The Data

Four CSVs under `csv_dateien/`, covering **Nov 2025 – Apr 2026**:

| File | Rows | Key columns |
|---|---|---|
| `leads.csv` | 820 | `lead_id`, `created_at`, `trade`, `source`, `company_size`, `region`, `lead_score` |
| `activities.csv` | 820 | `lead_id`, `call_attempts`, `connected_calls`, `demos_completed`, `time_to_first_touch_hours` |
| `bookings.csv` | 83 | `lead_id`, `booking_date`, `deal_size_eur`, `trade`, `source` |
| `transcripts_sample.csv` | 20 | `transcript_id`, `lead_id`, `trade`, `date`, `dq_reason_freitext`, `transcript_excerpt` |

**Glossary** — `MQL` = Marketing Qualified Lead · `ICP` = Ideal Customer Profile · `DQ` = Disqualified ·
`SHK` = plumbing/heating · `Elektro` = electrical · `PV` = solar · `MA` = *Mitarbeiter* (employees) ·
`SDR` = Sales Development Rep · `AE` = Account Executive · `RevOps` = Revenue Operations.

---

## How to Run

**Requirements:** Python 3.11+ and the packages in `requirements.txt`.

```bash
# 1. (optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run the analysis (prints summary tables, regenerates all 12 charts)
python analysis/funnel_analysis.py
```

The script prints the funnel and segment tables to the console and writes all charts to `analysis/charts/`.
`review_checks.py` and `audit.py` are standalone and can be run the same way.

> **Note:** the scripts currently use an absolute `BASE` path at the top of each file. If you clone this
> elsewhere, update that path (or replace it with `os.path.dirname(__file__)`) so the CSVs resolve.

---

## Methodology Notes & Honest Caveats

These are stated up front because they affect how the numbers should be read:

1. **The +38% / +9% baseline can't be reproduced from this data.** Q3 2025 is missing and Q2 2026 is April-only, so the headline figures aren't verifiable here. Within the available window, MQL growth is **+61% QoQ** and cohort conversion fell **11.4% → 10.3%** — same directional story, different exact numbers.
2. **Q2 2026 is a partial quarter.** April leads hadn't finished converting at data-export time, so the 6.4% Q2 booking rate is understated. Treat it as a leading indicator.
3. **87.8% of leads (720) have no outcome label.** The 10.1% booking rate assumes "no booking = lost." How many are still in active pipeline is the first thing to confirm with RevOps.
4. **Three lead_ids appear as both booked and disqualified** with conflicting trades — flagged in `data_questions.md` as a CRM data-integrity issue.

The point of surfacing these is rigor: the diagnosis (PV dilution) holds regardless, but the exact rates carry these asterisks.

---

## License & IP

The **original analysis** — everything in `analysis/` plus this README and the blueprint — is released under the [MIT License](LICENSE).

The **case brief** (`Case_Study_Senior_GTM_Analyst.pdf`) and the **datasets** (`csv_dateien/`) are the property of **Hero Software GmbH**, provided for this interview case study only and **not** covered by the MIT license. They are included here solely to make the analysis reproducible.
