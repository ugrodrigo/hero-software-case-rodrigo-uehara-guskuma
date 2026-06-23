# Data Inconsistencies & Questions for the Interviewer

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

## Questions for the Interviewer

### On data integrity

**Q1 — The three conflicting lead_ids (L10142, L10311, L10489)**
These appear as both Closed-Won and DQ'd, with the trade field conflicting between files (SHK/Elektro in leads and bookings; PV in transcripts). Is this a CRM data entry error, or do these companies have separate divisions that were approached independently?

**Q2 — The 720 leads with no outcome**
Are any of these still in active pipeline, or are they all resolved (ghosted, verbally DQ'd, or inactive)? If a large portion are pipeline, the current booking rate calculation is misleading.

### On timing and sales cycle

**Q3 — What is the typical sales cycle length from MQL creation to booking close?**
The data shows 13 bookings in May 2026 with no corresponding MQL created in May — these are April leads still closing. Without knowing the average cycle length, it's impossible to fairly compute Q2 conversion rates or know how long to wait before a lead is "lost."

**Q4 — Why does the leads dataset end April 29 while bookings continue to May 20?**
Is this a data export timing issue? If so, any analysis comparing conversion rates across months should account for this cutoff.

### On the case brief

**Q5 — Where do the +38% MQL and +9% Booking figures come from?**
The dataset covers November 2025 to April 2026. The Q4→Q1 MQL growth in the data is +61%, not +38%. What is the comparison baseline period, and is there prior data (Q2–Q3 2025) available to reproduce those figures?

**Q6 — Is there marketing spend data available anywhere?**
"CPL barely moved" is a key premise of the brief, but none of the four files contain spend or cost data. Without it, CPL claims cannot be verified or challenged with data.

### On data definitions

**Q7 — Is `demos_completed` logged consistently across all SDRs?**
If logging a demo in the CRM is optional or informal, the 23.9% demo rate and the 42% Demo→Booking rate could both be materially wrong — inflated if demos are under-logged, or deflated if reps log exploratory calls as demos.

**Q8 — What inputs feed the lead score model?**
The median lead score was identical across all three quarters (56–57) despite PV's share of MQLs growing from 34% to 58%. The model appears blind to the trade/segment shift. Knowing the inputs would reveal whether trade or company size are even features in the model — and whether a recalibration is feasible in the short term.
