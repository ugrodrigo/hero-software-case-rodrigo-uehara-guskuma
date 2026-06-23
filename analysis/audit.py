import pandas as pd

leads       = pd.read_csv(r"csv_dateien\leads.csv",       parse_dates=["created_at"])
bookings    = pd.read_csv(r"csv_dateien\bookings.csv",    parse_dates=["booking_date"])
transcripts = pd.read_csv(r"csv_dateien\transcripts_sample.csv", parse_dates=["date"])
activities  = pd.read_csv(r"csv_dateien\activities.csv")

SEP = "=" * 60

# 1. lead_ids in BOTH bookings AND transcripts
overlap = set(bookings["lead_id"]) & set(transcripts["lead_id"])
print(f"\n{SEP}\n1. lead_ids in BOTH bookings AND transcripts: {len(overlap)}\n{SEP}")
for lid in overlap:
    b = bookings[bookings["lead_id"] == lid]
    t = transcripts[transcripts["lead_id"] == lid]
    l = leads[leads["lead_id"] == lid]
    print(f"lead_id: {lid}")
    print(f"  leads.csv   -> trade={l['trade'].values}  source={l['source'].values}")
    brow = b[["booking_date","deal_size_eur","trade","source"]].iloc[0]
    print(f"  bookings    -> date={brow['booking_date'].date()}  EUR={brow['deal_size_eur']}  trade={brow['trade']}  source={brow['source']}")
    trow = t[["date","trade","dq_reason_freitext"]].iloc[0]
    print(f"  transcripts -> date={trow['date'].date()}  trade={trow['trade']}  dq={trow['dq_reason_freitext']}")

# 2. Trade / source mismatches between bookings.csv and leads.csv
bk_leads = bookings.merge(leads[["lead_id","trade","source"]], on="lead_id", suffixes=("_bk","_lead"))
trade_mm  = bk_leads[bk_leads["trade_bk"]  != bk_leads["trade_lead"]]
source_mm = bk_leads[bk_leads["source_bk"] != bk_leads["source_lead"]]
print(f"\n{SEP}\n2a. Trade mismatches (bookings vs leads): {len(trade_mm)}\n{SEP}")
print(trade_mm[["lead_id","trade_bk","trade_lead"]].to_string())
print(f"\n{SEP}\n2b. Source mismatches (bookings vs leads): {len(source_mm)}\n{SEP}")
print(source_mm[["lead_id","source_bk","source_lead"]].to_string())

# 3. Date ranges
print(f"\n{SEP}\n3. Date ranges\n{SEP}")
print(f"leads:       {leads['created_at'].min().date()} to {leads['created_at'].max().date()}  ({len(leads)} rows)")
print(f"bookings:    {bookings['booking_date'].min().date()} to {bookings['booking_date'].max().date()}  ({len(bookings)} rows)")
print(f"transcripts: {transcripts['date'].min().date()} to {transcripts['date'].max().date()}  ({len(transcripts)} rows)")

# 4. MQL and bookings by month
print(f"\n{SEP}\n4. MQLs and Bookings by month\n{SEP}")
mql_m = leads.groupby(leads["created_at"].dt.to_period("M")).size().rename("MQLs")
bk_m  = bookings.groupby(bookings["booking_date"].dt.to_period("M")).size().rename("Bookings")
combined = pd.concat([mql_m, bk_m], axis=1).fillna(0).astype(int)
print(combined.to_string())

# 5. Is Q2 2026 partial?
q2 = leads[leads["created_at"].dt.to_period("Q") == "2026Q2"]
print(f"\n{SEP}\n5. Q2 2026 coverage in leads.csv\n{SEP}")
print(f"  {q2['created_at'].min().date()} to {q2['created_at'].max().date()}  ({len(q2)} leads, April only)")

# 6. Bookings with no matching lead_id
orphans = set(bookings["lead_id"]) - set(leads["lead_id"])
print(f"\n{SEP}\n6. Bookings with no matching lead_id: {len(orphans)}\n{SEP}")
print(orphans)

# 7. Logical impossibilities in activities
impossible_demo = activities[activities["demos_completed"] > activities["connected_calls"]]
impossible_conn = activities[activities["connected_calls"] > activities["call_attempts"]]
print(f"\n{SEP}\n7a. demos_completed > connected_calls (impossible): {len(impossible_demo)}\n{SEP}")
print(impossible_demo.head(10).to_string())
print(f"\n{SEP}\n7b. connected_calls > call_attempts (impossible): {len(impossible_conn)}\n{SEP}")
print(impossible_conn.head(10).to_string())

# 8. verify +38% MQL / +9% booking claim
print(f"\n{SEP}\n8. Quarter-over-quarter: verifying stated growth figures\n{SEP}")
leads["quarter"] = leads["created_at"].dt.to_period("Q")
bookings["quarter"] = bookings["booking_date"].dt.to_period("Q")
qmql = leads.groupby("quarter").size().rename("MQLs")
qbk  = bookings.groupby("quarter").size().rename("Bookings")
qtbl = pd.concat([qmql, qbk], axis=1).fillna(0).astype(int)
qtbl["MQL_growth_%"]     = qtbl["MQLs"].pct_change() * 100
qtbl["Booking_growth_%"] = qtbl["Bookings"].pct_change() * 100
print(qtbl.round(1).to_string())

# 9. Lead score: any leads with score 0 or > 100?
print(f"\n{SEP}\n9. Lead score out of 0-100 range\n{SEP}")
bad_score = leads[(leads["lead_score"] < 0) | (leads["lead_score"] > 100)]
print(f"  {len(bad_score)} leads with score outside 0-100")
print(f"  Min score: {leads['lead_score'].min()}  Max: {leads['lead_score'].max()}")

# 10. Leads with no booking AND no DQ transcript -- the silent majority
all_dq_leads = set(transcripts["lead_id"])
all_bk_leads = set(bookings["lead_id"])
silent = leads[~leads["lead_id"].isin(all_dq_leads | all_bk_leads)]
print(f"\n{SEP}\n10. Leads with neither booking nor DQ transcript: {len(silent)}\n{SEP}")
print(f"  These {len(silent)} leads ({len(silent)/len(leads)*100:.1f}% of pool) have no outcome label.")
