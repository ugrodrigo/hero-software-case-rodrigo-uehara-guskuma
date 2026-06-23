# Data Inconsistencies & Questions

Findings from a data integrity audit across all four datasets.

---

## Inconsistencies Found in the Data

### 1. Three lead_ids appear as both Closed-Won and Disqualified

The same lead_id exists simultaneously in `bookings.csv` and `transcripts_sample.csv`, with contradictory trades and impossible timelines:

| lead_id | leads.csv | bookings.csv | transcripts_sample.csv | Issue |
|---|---|---|---|---|
| **L10142** | Elektro / Organic Search | Booked Jan 18, 2026 | DQ'd Dec 8, 2025 as **PV** / "Nicht kaufbereit" | DQ before booking — possible but suspicious |
| **L10311** | Elektro / Referral | Booked Jan 7, 2026 | DQ'd Jan 22, 2026 as **PV** / "Nur Info" | DQ **after** booking — logically impossible for the same engagement |
| **L10489** | SHK / Google Ads | Booked Jan 3, 2026 | DQ'd Mar 22, 2026 as **PV** / "Bauchgefühl" | DQ 79 days after close — impossible |

All three were booked as SHK/Elektro but the transcripts label them as PV. Either a CRM data entry error (wrong lead_id typed into the transcript), or these companies have separate SHK and PV divisions that received two separate sales motions. Either way, these records are unreliable and slightly inflate the PV DQ count in the transcript sample.

---

### 2. April MQLs haven't had time to convert — Q2 conversion rate is artificially low

The leads dataset stops at April 29 but bookings continue through May 20:

| Month | MQLs | Bookings (by close date) |
|---|---|---|
| Nov 2025 | 118 | 2 |
| Dec 2025 | 154 | 8 |
| Jan 2026 | 151 | 17 |
| Feb 2026 | 123 | 14 |
| Mar 2026 | 165 | 11 |
| Apr 2026 | 109 | 18 |
| **May 2026** | **0 MQLs** | **13 bookings** |

13 May bookings have no corresponding MQL in the dataset — they are almost certainly April leads still closing. The 6.4% Q2 booking rate is therefore understated. April MQLs cannot be fairly compared to prior quarters without knowing the full conversion window.

---

### 3. The stated "+38% MQL / +9% Booking" growth figures don't match the data

Using the dataset as-is:

| Quarter | MQLs | QoQ growth | Bookings (by close date) | QoQ growth |
|---|---|---|---|---|
| Q4 2025 | 272 | — | 10 | — |
| Q1 2026 | 439 | **+61%** | 42 | +320% |
| Q2 2026 | 109 | — | 31 | — |

The brief states "+38% MQL growth" and "+9% Booking growth." Neither figure is reproducible from the provided dataset. The comparison baseline (likely Q2–Q3 2025) is not included.

---

### 4. 87.8% of leads have no outcome label

| Outcome | Count | % of pool |
|---|---|---|
| Booked | 83 | 10.1% |
| DQ'd with transcript | 20 | 2.4% |
| **No label at all** | **720** | **87.8%** |

The 10.1% booking rate assumes all 820 leads are fully resolved (i.e., "no booking = lost"). If a meaningful portion of those 720 are still in active pipeline, the real conversion rate and the SDR activity metrics are both distorted.

---

## Questions

Ordered by impact — the strategic questions come first, because they decide whether the recommendation is "gate PV" or something else entirely. The data-hygiene questions come last.

### On strategy and ICP (ask these first)

**Q1 — Is there a documented, current ICP, and when was it last updated?**
The whole diagnosis is that *Marketing scaled PV without updating the ICP.* That only holds if I know what the ICP actually is. Does a written ICP exist? Does it set explicit thresholds for trade and company size (e.g. "6+ employees, core trades")? If it was last updated before the PV surge, that's the root cause in one sentence — and a fast fix.

**Q2 — Was the PV surge a deliberate strategic bet, or did it happen unmanaged?**
This is the one I most want to be wrong about. If leadership intentionally chased the solar boom with product investment on the roadmap, then "gate PV" is the wrong call — the right call is "set realistic timeline expectations and protect core-trade conversion *while* PV matures." If it happened unmanaged, my recommendation stands. I won't know which until I ask, and I'd rather challenge my own conclusion than bulldoze Marketing with it.

### On the case-brief premises

**Q3 — Where do the +38% MQL and +9% Booking figures come from?**
The dataset covers November 2025 to April 2026. The Q4→Q1 MQL growth in the data is +61%, not +38%. What is the comparison baseline period, and is there prior data (Q2–Q3 2025) available to reproduce those figures? Without it, I can confirm the *direction* of the story but not the headline numbers.

**Q4 — CPL is likely the wrong metric for us right now — can we get spend by channel?**
"CPL barely moved" is a stated premise, but none of the four files contain spend data, and the analysis suggests CPL is the wrong lens anyway: Meta Ads leads book at ~3% vs Referral/Organic far higher. With spend by channel I can compute **Cost-per-Booking**, which would likely show that "flat CPL" is hiding a real rise in the cost of an *actual* customer. Is that data available?

### On data definitions and the scoring model

**Q5 — Does the lead-score model include trade and company size as features?**
The median lead score was flat at 56–57 across all three quarters despite PV's share of MQLs growing from 34% to 58% — the model was blind to the single biggest mix shift in the data. I want to know whether trade/size are even inputs, and whether a short-term recalibration (or a negative weight on early-stage PV) is feasible.

**Q6 — Is `demos_completed` logged consistently across all SDRs?**
If logging a demo in the CRM is optional or informal, the 23.9% demo rate and the 42% Demo→Booking rate could both be materially wrong — inflated if demos are under-logged, or deflated if reps log exploratory calls as demos.

**Q7 — Are sales calls recorded or transcribed, or are these 20 excerpts the only qualitative record?**
The strongest version of the Task 2 feedback loop — retroactively classifying the 720 leads that currently have no outcome label — only works if call recordings or notes exist at scale. If they do, that's a one-time backfill that could re-light a chunk of "invisible" pipeline. If the 20 excerpts are all we have, the loop starts manual from today forward.

### On timing and sales cycle

**Q8 — What is the typical sales cycle length, and why does the leads export end April 29 while bookings run to May 20?**
The data shows 13 bookings in May 2026 with no MQL created in May — April leads still closing. Without the average cycle length I can't fairly compute Q2 conversion or know how long to wait before calling a lead "lost," and the leads/bookings cutoff mismatch means any month-over-month conversion comparison needs to account for the truncation.

### On data integrity

**Q9 — The 720 leads with no outcome**
Are any of these still in active pipeline, or are they all resolved (ghosted, verbally DQ'd, or inactive)? If a large portion are pipeline, the 10.1% booking rate — and every segment rate derived from it — is understated. This is the single assumption the whole diagnosis rests on.

**Q10 — The three conflicting lead_ids (L10142, L10311, L10489)**
These appear as both Closed-Won and DQ'd, with the trade field conflicting between files (SHK/Elektro in leads and bookings; PV in transcripts). Is this a CRM data entry error, or do these companies have separate divisions that were approached independently? Minor in volume, but it's a flag on CRM data hygiene.
