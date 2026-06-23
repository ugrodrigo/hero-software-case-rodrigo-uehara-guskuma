import pandas as pd
import numpy as np

leads      = pd.read_csv(r"csv_dateien\leads.csv", parse_dates=["created_at"])
activities = pd.read_csv(r"csv_dateien\activities.csv")
bookings   = pd.read_csv(r"csv_dateien\bookings.csv", parse_dates=["booking_date"])

df = leads.merge(activities, on="lead_id", how="left")
df["converted"] = df["lead_id"].isin(bookings["lead_id"]).astype(int)

SEP = "=" * 64

# ─────────────────────────────────────────────────────────────────────
# CHECK A: Is time-to-touch CONFOUNDED with trade?
# If PV leads are systematically touched late, then "response time"
# is partly just "PV" restated.
# ─────────────────────────────────────────────────────────────────────
print(f"{SEP}\nA. Mean time_to_first_touch by trade\n{SEP}")
print(df.groupby("trade")["time_to_first_touch_hours"].agg(["mean","median","count"]).round(1).to_string())

touch_bins   = [0,2,4,8,24,48,999]
touch_labels = ["<=2h","2-4h","4-8h","8-24h","24-48h","48h+"]
df["touch_bucket"] = pd.cut(df["time_to_first_touch_hours"], bins=touch_bins, labels=touch_labels)

print(f"\n{SEP}\nA2. Touch-bucket distribution: PV vs non-PV (% within group)\n{SEP}")
ct = pd.crosstab(df["touch_bucket"], df["trade"]=="PV", normalize="columns")*100
ct.columns = ["non-PV %","PV %"]
print(ct.round(1).to_string())

# ─────────────────────────────────────────────────────────────────────
# CHECK B: Does response time still matter WITHIN core trades only?
# Strip out PV and small-co noise — look at SHK+Elektro only.
# ─────────────────────────────────────────────────────────────────────
core = df[df["trade"].isin(["SHK","Elektro"])]
print(f"\n{SEP}\nB. Booking rate by touch bucket — CORE TRADES ONLY (SHK+Elektro)\n{SEP}")
b = core.groupby("touch_bucket", observed=True).agg(
    MQLs=("lead_id","count"), Bk=("converted","sum"))
b["Booking %"] = (b["Bk"]/b["MQLs"]*100).round(1)
print(b.to_string())

# ─────────────────────────────────────────────────────────────────────
# CHECK C: The €262K counterfactual — how sound is it?
# Sonnet: 247 late-touch leads * (20% - their rate) ~ 46 lost bookings.
# Re-derive honestly and show how much is PV-confounded.
# ─────────────────────────────────────────────────────────────────────
late = df[df["time_to_first_touch_hours"] > 24]
print(f"\n{SEP}\nC. Late-touch (>24h) lead composition\n{SEP}")
print(f"Total late-touch leads: {len(late)}")
print(f"  of which PV:        {(late['trade']=='PV').sum()}  ({(late['trade']=='PV').mean()*100:.0f}%)")
print(f"  of which 1-2 MA:    {(late['company_size']=='1-2 MA').sum()}")
print("Late-touch booking rate:", round(late['converted'].mean()*100,1),"%")
fast = df[df["time_to_first_touch_hours"] <= 2]
print("Fast-touch (<=2h) PV share:", round((fast['trade']=='PV').mean()*100,1),"%")
print("Fast-touch booking rate:", round(fast['converted'].mean()*100,1),"%")

# ─────────────────────────────────────────────────────────────────────
# CHECK D: Two-way — booking rate by trade x touch (is effect real inside PV?)
# ─────────────────────────────────────────────────────────────────────
print(f"\n{SEP}\nD. Booking rate: trade x fast(<=2h)/slow(>24h)\n{SEP}")
df["speed"] = np.where(df["time_to_first_touch_hours"]<=2,"fast<=2h",
              np.where(df["time_to_first_touch_hours"]>24,"slow>24h","mid"))
piv = df.pivot_table(index="trade", columns="speed", values="converted",
                     aggfunc="mean")*100
print(piv.round(1).to_string())

# ─────────────────────────────────────────────────────────────────────
# CHECK E: call_attempts analysis (the gap Sonnet flagged as missing)
# ─────────────────────────────────────────────────────────────────────
print(f"\n{SEP}\nE. SDR effort (call_attempts) by trade & by outcome\n{SEP}")
print("Avg call_attempts by trade:")
print(df.groupby("trade")["call_attempts"].mean().round(2).to_string())
print("\nAvg call_attempts converted vs not:")
print(df.groupby("converted")[["call_attempts","connected_calls"]].mean().round(2).to_string())

# ─────────────────────────────────────────────────────────────────────
# CHECK F: Does score predict WITHIN trade? (is score useless, or just
# uncorrelated because trade dominates?)
# ─────────────────────────────────────────────────────────────────────
print(f"\n{SEP}\nF. Mean lead_score by trade (does PV just have low scores?)\n{SEP}")
print(df.groupby("trade")["lead_score"].agg(["mean","median"]).round(1).to_string())

# ─────────────────────────────────────────────────────────────────────
# CHECK G: deal size — revenue view, not just count. PV deals are big.
# ─────────────────────────────────────────────────────────────────────
print(f"\n{SEP}\nG. Revenue (booked EUR) by trade — count view undersells PV?\n{SEP}")
bk = bookings.groupby("trade")["deal_size_eur"].agg(["sum","mean","count"]).round(0)
print(bk.to_string())
print(f"\nTotal booked revenue: EUR {bookings['deal_size_eur'].sum():,.0f}")
