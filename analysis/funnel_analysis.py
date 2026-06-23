import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

BASE = r"c:\Users\Rodrigo Guskuma\Documents\vscode\personal-projects\hero-software-case"
CSV_DIR = os.path.join(BASE, "csv_dateien")
CHART_DIR = os.path.join(BASE, "analysis", "charts")
os.makedirs(CHART_DIR, exist_ok=True)

# --- HERO brand colours ---
DARK_BG   = "#0B1F3A"
PANEL_BG  = "#0F2040"
TEAL      = "#00B9A0"
ORANGE    = "#FF6B35"
YELLOW    = "#FFD166"
BLUE_LT   = "#8ECAE6"
MINT      = "#06D6A0"
RED_LT    = "#EF476F"
WHITE     = "#FFFFFF"
GREY      = "#AAB8C2"

plt.rcParams.update({
    "figure.facecolor":  DARK_BG,
    "axes.facecolor":    PANEL_BG,
    "axes.edgecolor":    "#1E3A5F",
    "text.color":        WHITE,
    "axes.labelcolor":   WHITE,
    "xtick.color":       WHITE,
    "ytick.color":       WHITE,
    "grid.color":        "#1E3A5F",
    "grid.alpha":        0.6,
    "font.family":       "sans-serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ── LOAD ────────────────────────────────────────────────────────────────────
leads       = pd.read_csv(os.path.join(CSV_DIR, "leads.csv"),       parse_dates=["created_at"])
activities  = pd.read_csv(os.path.join(CSV_DIR, "activities.csv"))
bookings    = pd.read_csv(os.path.join(CSV_DIR, "bookings.csv"),    parse_dates=["booking_date"])
transcripts = pd.read_csv(os.path.join(CSV_DIR, "transcripts_sample.csv"), parse_dates=["date"])

# ── MASTER TABLE ─────────────────────────────────────────────────────────────
df = leads.merge(activities, on="lead_id", how="left")
df["converted"]    = df["lead_id"].isin(bookings["lead_id"]).astype(int)
df["has_connect"]  = (df["connected_calls"] >= 1).astype(int)
df["has_demo"]     = (df["demos_completed"]  >= 1).astype(int)

df["month"]        = df["created_at"].dt.to_period("M")
df["quarter"]      = df["created_at"].dt.to_period("Q")
df["period_label"] = df["quarter"].astype(str).map(
    {"2025Q4": "Q4 2025", "2026Q1": "Q1 2026", "2026Q2": "Q2 2026"}
)

size_order = ["1-2 MA", "3-5 MA", "6-15 MA", "16-50 MA", "50+ MA"]
df["company_size"] = pd.Categorical(df["company_size"], categories=size_order, ordered=True)

df["score_bucket"] = pd.cut(
    df["lead_score"],
    bins=[0, 39, 59, 79, 100],
    labels=["0-39", "40-59", "60-79", "80-100"]
)

# time-to-touch bucket
touch_bins   = [0, 2, 4, 8, 24, 48, 999]
touch_labels = ["≤2h", "2-4h", "4-8h", "8-24h", "24-48h", "48h+"]
df["touch_bucket"] = pd.cut(
    df["time_to_first_touch_hours"],
    bins=touch_bins,
    labels=touch_labels
)

# ── HELPER ──────────────────────────────────────────────────────────────────
def funnel_table(data, group_col=None):
    if group_col:
        g = data.groupby(group_col, observed=True)
        t = pd.DataFrame({
            "MQLs":     g["lead_id"].count(),
            "Connects": g["has_connect"].sum(),
            "Demos":    g["has_demo"].sum(),
            "Bookings": g["converted"].sum(),
        })
    else:
        t = pd.DataFrame([{
            "MQLs":     len(data),
            "Connects": data["has_connect"].sum(),
            "Demos":    data["has_demo"].sum(),
            "Bookings": data["converted"].sum(),
        }])
    t["Connect %"] = (t["Connects"] / t["MQLs"] * 100).round(1)
    t["Demo %"]    = (t["Demos"]    / t["MQLs"] * 100).round(1)
    t["Booking %"] = (t["Bookings"] / t["MQLs"] * 100).round(1)
    t["Demo→Bk %"] = (t["Bookings"] / t["Demos"].replace(0, np.nan) * 100).round(1)
    return t


# ═══════════════════════════════════════════════════════════════════════════
# CHART 1 — Overall Funnel Waterfall
# ═══════════════════════════════════════════════════════════════════════════
ov   = funnel_table(df)
stgs = ["MQLs", "Connects", "Demos", "Bookings"]
vals = [int(ov[s].values[0]) for s in stgs]
cols = [TEAL, "#00CDB0", ORANGE, YELLOW]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(stgs, vals, color=cols, width=0.5, zorder=3)

for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 6,
            str(v), ha="center", va="bottom", fontsize=15, fontweight="bold")

for i in range(1, len(vals)):
    pct = vals[i] / vals[i - 1] * 100
    x   = i
    y   = vals[i] + vals[0] * 0.07
    ax.annotate(f"{pct:.0f}% of prev",
                xy=(x, vals[i]), xytext=(x, y),
                ha="center", fontsize=9, color=GREY,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8))

ax.set_title("Overall Funnel — Nov 2025 to Apr 2026", fontsize=14, fontweight="bold", pad=16)
ax.set_ylabel("Leads")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(axis="y", zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "01_funnel_waterfall.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 1: funnel_waterfall")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 2 — MQL Volume vs. Bookings by Month
# ═══════════════════════════════════════════════════════════════════════════
monthly = (
    df.groupby("month")
    .agg(MQLs=("lead_id", "count"), Bookings=("converted", "sum"))
    .reset_index()
)
monthly["month_str"] = monthly["month"].astype(str)

fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()
ax2.set_facecolor(PANEL_BG)

ax1.bar(monthly["month_str"], monthly["MQLs"], color=TEAL, alpha=0.65, label="MQLs", zorder=3, width=0.5)
ax2.plot(monthly["month_str"], monthly["Bookings"], color=ORANGE, lw=2.5,
         marker="o", ms=8, label="Bookings", zorder=4)

ax1.set_ylabel("MQL Count", color=TEAL, fontsize=11)
ax2.set_ylabel("Bookings", color=ORANGE, fontsize=11)
ax1.tick_params(axis="y", colors=TEAL)
ax2.tick_params(axis="y", colors=ORANGE)
ax2.set_facecolor(PANEL_BG)

for spine in ax2.spines.values():
    spine.set_visible(False)

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", facecolor="#132540", labelcolor=WHITE)

ax1.set_title("MQL Volume vs. Bookings by Month\nMQLs accelerating — Bookings not keeping pace",
              fontsize=13, fontweight="bold", pad=12)
ax1.grid(axis="y", alpha=0.2, zorder=0)
ax1.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "02_mql_vs_bookings_monthly.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 2: mql_vs_bookings_monthly")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 3 — Booking Rate by Source
# ═══════════════════════════════════════════════════════════════════════════
by_src = funnel_table(df, "source").sort_values("Booking %")
median_bk = by_src["Booking %"].median()

fig, ax = plt.subplots(figsize=(10, 5))
c = [TEAL if v >= median_bk else ORANGE for v in by_src["Booking %"]]
ax.barh(by_src.index, by_src["Booking %"], color=c, height=0.45, zorder=3)

for idx, (bk, n, cr) in enumerate(zip(by_src["Booking %"], by_src["MQLs"], by_src["Connect %"])):
    ax.text(bk + 0.15, idx, f"{bk:.1f}%  |  n={int(n)}  |  connect {cr:.0f}%",
            va="center", fontsize=10.5, color=WHITE)

ax.set_xlabel("Lead-to-Booking Rate (%)")
ax.set_title("Lead-to-Booking Rate by Source", fontsize=13, fontweight="bold", pad=12)
ax.set_xlim(0, by_src["Booking %"].max() * 1.75)
ax.grid(axis="x", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "03_conversion_by_source.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 3: conversion_by_source")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 4 — Booking Rate by Trade
# ═══════════════════════════════════════════════════════════════════════════
by_trade = funnel_table(df, "trade").sort_values("Booking %")
median_t = by_trade["Booking %"].median()

fig, ax = plt.subplots(figsize=(10, 5))
c = [TEAL if v >= median_t else ORANGE for v in by_trade["Booking %"]]
ax.barh(by_trade.index, by_trade["Booking %"], color=c, height=0.45, zorder=3)

for idx, (bk, n, dr) in enumerate(zip(by_trade["Booking %"], by_trade["MQLs"], by_trade["Demo %"])):
    ax.text(bk + 0.1, idx, f"{bk:.1f}%  |  n={int(n)}  |  demo {dr:.0f}%",
            va="center", fontsize=10.5, color=WHITE)

ax.set_xlabel("Lead-to-Booking Rate (%)")
ax.set_title("Lead-to-Booking Rate by Trade\nPV conversion rate is the critical outlier",
             fontsize=13, fontweight="bold", pad=12)
ax.set_xlim(0, by_trade["Booking %"].max() * 1.75)
ax.grid(axis="x", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "04_conversion_by_trade.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 4: conversion_by_trade")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 5 — Booking Rate by Company Size
# ═══════════════════════════════════════════════════════════════════════════
by_size = funnel_table(df, "company_size")
median_s = by_size["Booking %"].median()

fig, ax = plt.subplots(figsize=(10, 5))
c = [TEAL if v >= median_s else ORANGE for v in by_size["Booking %"]]
bars = ax.bar(by_size.index.astype(str), by_size["Booking %"], color=c, width=0.5, zorder=3)

for bar, bk, n in zip(bars, by_size["Booking %"], by_size["MQLs"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            f"{bk:.1f}%\nn={int(n)}", ha="center", va="bottom", fontsize=9.5, color=WHITE)

ax.set_ylabel("Lead-to-Booking Rate (%)")
ax.set_title("Lead-to-Booking Rate by Company Size\n1-5 employee firms are uneconomical to convert",
             fontsize=13, fontweight="bold", pad=12)
ax.set_ylim(0, by_size["Booking %"].max() * 1.5)
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "05_conversion_by_company_size.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 5: conversion_by_company_size")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 6 — Lead Score Distribution by Quarter
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
palette = [TEAL, ORANGE, YELLOW]
for period, col in zip(["Q4 2025", "Q1 2026", "Q2 2026"], palette):
    sub = df[df["period_label"] == period]["lead_score"]
    if len(sub):
        ax.hist(sub, bins=20, alpha=0.55, color=col, label=f"{period}  (n={len(sub)})",
                density=True, zorder=3)
        ax.axvline(sub.median(), color=col, lw=1.5, linestyle="--", alpha=0.8)

ax.set_xlabel("Lead Score")
ax.set_ylabel("Density")
ax.set_title("Lead Score Distribution by Quarter\n(dashed = median per period)",
             fontsize=13, fontweight="bold", pad=12)
ax.legend(facecolor="#132540", labelcolor=WHITE)
ax.grid(alpha=0.2, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "06_lead_score_by_quarter.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 6: lead_score_by_quarter")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 7 — Booking Rate by Lead Score Bucket
# ═══════════════════════════════════════════════════════════════════════════
by_score = funnel_table(df, "score_bucket")

fig, ax = plt.subplots(figsize=(10, 5))
c_score = [ORANGE, "#FFD166", BLUE_LT, TEAL]
bars = ax.bar(by_score.index.astype(str), by_score["Booking %"],
              color=c_score[: len(by_score)], width=0.5, zorder=3)

for bar, bk, n in zip(bars, by_score["Booking %"], by_score["MQLs"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            f"{bk:.1f}%\nn={int(n)}", ha="center", va="bottom", fontsize=10, color=WHITE)

ax.set_ylabel("Lead-to-Booking Rate (%)")
ax.set_title("Booking Rate by Lead Score Bucket\nDoes scoring predict conversion?",
             fontsize=13, fontweight="bold", pad=12)
ax.set_ylim(0, by_score["Booking %"].max() * 1.5)
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "07_booking_rate_by_score.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 7: booking_rate_by_score")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 8 — Time-to-First-Touch vs. Booking Rate
# ═══════════════════════════════════════════════════════════════════════════
by_touch = (
    df.groupby("touch_bucket", observed=True)
    .agg(MQLs=("lead_id", "count"), Bookings=("converted", "sum"))
    .reset_index()
)
by_touch["Booking %"] = (by_touch["Bookings"] / by_touch["MQLs"] * 100).round(1)

fig, ax = plt.subplots(figsize=(11, 6))
c_touch = [TEAL, TEAL, BLUE_LT, "#FFD166", ORANGE, RED_LT]
bars = ax.bar(by_touch["touch_bucket"].astype(str), by_touch["Booking %"],
              color=c_touch[: len(by_touch)], width=0.55, zorder=3)

for bar, bk, n in zip(bars, by_touch["Booking %"], by_touch["MQLs"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
            f"{bk:.1f}%\nn={int(n)}", ha="center", va="bottom", fontsize=9.5, color=WHITE)

ax.set_xlabel("Time to First Sales Touch")
ax.set_ylabel("Lead-to-Booking Rate (%)")
ax.set_title("Booking Rate by Time-to-First-Touch\nEvery hour of delay costs conversions",
             fontsize=13, fontweight="bold", pad=12)
ax.set_ylim(0, by_touch["Booking %"].max() * 1.5)
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "08_time_to_touch_vs_conversion.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 8: time_to_touch_vs_conversion")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 9 — DQ Reasons (transcripts)
# ═══════════════════════════════════════════════════════════════════════════
dq_cat_map = {
    "Nicht kaufbereit":  "Timing / Not Ready",
    "Will nur vergleichen": "Timing / Not Ready",
    "Kein Bedarf jetzt": "Timing / Not Ready",
    "Andere Priorität":  "Timing / Not Ready",
    "Recherche":         "Timing / Not Ready",
    "Nur Info":          "Wrong-Fit Lead",
    "Falsche Erwartung": "Wrong-Fit Lead",
    "Nicht passend":     "Wrong-Fit Lead",
    "Zu klein":          "Wrong-Fit Lead",
    "Einzelunternehmer": "Wrong-Fit Lead",
    "Bauchgefühl":       "Wrong-Fit Lead",
    "Wettbewerber":      "Competitor Lock-in",
    "Preis":             "Price Objection",
    "Funktionslücke":    "Product Gap",
    "Nicht erreicht":    "Sales Process",
    "Falsche Person":    "Sales Process",
}
transcripts["dq_category"] = transcripts["dq_reason_freitext"].map(dq_cat_map).fillna("Other")
cat_counts = transcripts["dq_category"].value_counts()
raw_counts  = transcripts["dq_reason_freitext"].value_counts()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Left: raw reasons
ax1.barh(raw_counts.index, raw_counts.values, color=TEAL, height=0.6, zorder=3)
for i, (v, lbl) in enumerate(zip(raw_counts.values, raw_counts.index)):
    ax1.text(v + 0.04, i, str(int(v)), va="center", fontsize=9.5, color=WHITE)
ax1.set_title("Raw DQ Reason (20 transcript sample)", fontsize=11, fontweight="bold", pad=10)
ax1.tick_params(labelsize=9)
ax1.grid(axis="x", alpha=0.25, zorder=0)
ax1.set_axisbelow(True)

# Right: category pie
pie_cols = [ORANGE, TEAL, RED_LT, YELLOW, BLUE_LT, MINT]
wedges, texts, autotexts = ax2.pie(
    cat_counts.values,
    labels=cat_counts.index,
    autopct="%1.0f%%",
    colors=pie_cols[: len(cat_counts)],
    startangle=90,
    textprops={"color": WHITE, "fontsize": 9.5},
    pctdistance=0.75,
)
for at in autotexts:
    at.set_fontsize(9)
ax2.set_title("DQ Category Rollup", fontsize=11, fontweight="bold", pad=10)

fig.suptitle("Why Leads Get Disqualified — Transcript Analysis",
             fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "09_dq_reasons.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 9: dq_reasons")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 10 — Trade Mix by Quarter (shows the MQL quality shift)
# ═══════════════════════════════════════════════════════════════════════════
period_order = ["Q4 2025", "Q1 2026", "Q2 2026"]
trade_period = (
    df.groupby(["period_label", "trade"], observed=True)
    .size()
    .unstack(fill_value=0)
)
trade_period = trade_period.reindex(period_order)
trade_period_pct = trade_period.div(trade_period.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(11, 6))
trade_cols = [TEAL, ORANGE, YELLOW, BLUE_LT, MINT]
trade_period_pct.plot(kind="bar", ax=ax,
                      color=trade_cols[: len(trade_period_pct.columns)],
                      width=0.65, zorder=3, edgecolor="none")

ax.set_title("Trade Mix by Quarter\nPV share growing = lower-converting segment dominates MQL pool",
             fontsize=12, fontweight="bold", pad=12)
ax.set_ylabel("% of MQLs")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="Trade", facecolor="#132540", labelcolor=WHITE, title_fontsize=9)
ax.grid(axis="y", alpha=0.2, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "10_trade_mix_by_quarter.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 10: trade_mix_by_quarter")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 11 — SDR Effort by Trade (call_attempts) — the triage evidence
# ═══════════════════════════════════════════════════════════════════════════
effort = df.groupby("trade")["call_attempts"].mean().sort_values()

fig, ax = plt.subplots(figsize=(10, 5))
c_eff = [ORANGE if t == "PV" else TEAL for t in effort.index]
bars = ax.barh(effort.index, effort.values, color=c_eff, height=0.5, zorder=3)
for bar, v in zip(bars, effort.values):
    ax.text(v + 0.05, bar.get_y() + bar.get_height() / 2, f"{v:.2f}",
            va="center", fontsize=11, color=WHITE)

ax.set_xlabel("Avg. Call Attempts per Lead")
ax.set_title("SDR Effort by Trade\nSDRs already give PV half the attempts — they're triaging, not neglecting",
             fontsize=12, fontweight="bold", pad=12)
ax.set_xlim(0, effort.max() * 1.25)
ax.grid(axis="x", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "11_sdr_effort_by_trade.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 11: sdr_effort_by_trade")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 12 — Booked Revenue by Trade (the revenue-weighted view)
# ═══════════════════════════════════════════════════════════════════════════
rev = bookings.groupby("trade")["deal_size_eur"].agg(["sum", "mean", "count"])
rev = rev.sort_values("sum")

fig, ax = plt.subplots(figsize=(10, 5.5))
c_rev = [ORANGE if t == "PV" else TEAL for t in rev.index]
bars = ax.barh(rev.index, rev["sum"] / 1000, color=c_rev, height=0.5, zorder=3)
for bar, (tr, row) in zip(bars, rev.iterrows()):
    ax.text(row["sum"] / 1000 + 3, bar.get_y() + bar.get_height() / 2,
            f"€{row['sum']/1000:.0f}k  |  {int(row['count'])} deals  |  ø €{row['mean']/1000:.1f}k",
            va="center", fontsize=10, color=WHITE)

ax.set_xlabel("Booked Revenue (€ thousands)")
ax.set_title("Booked Revenue by Trade\nPV closes rarely — but its few deals are the LARGEST (ø €7.9k)",
             fontsize=12, fontweight="bold", pad=12)
ax.set_xlim(0, rev["sum"].max() / 1000 * 1.5)
ax.grid(axis="x", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(os.path.join(CHART_DIR, "12_revenue_by_trade.png"), dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 12: revenue_by_trade")

# ═══════════════════════════════════════════════════════════════════════════
# CONFOUND / ROBUSTNESS — time-to-touch is endogenous with trade
# ═══════════════════════════════════════════════════════════════════════════
df["speed"] = np.where(df["time_to_first_touch_hours"] <= 2, "fast ≤2h",
              np.where(df["time_to_first_touch_hours"] > 24, "slow >24h", "mid 2-24h"))

# Booking rate: trade × speed
speed_piv = (df.pivot_table(index="trade", columns="speed",
                            values="converted", aggfunc="mean") * 100).round(1)
speed_piv = speed_piv[["fast ≤2h", "mid 2-24h", "slow >24h"]]

# Late-touch composition
late = df[df["time_to_first_touch_hours"] > 24]
pv_share_late = (late["trade"] == "PV").mean() * 100

# Honest recoverable estimate — CORE TRADES ONLY (SHK + Elektro)
core = df[df["trade"].isin(["SHK", "Elektro"])]
core_fast_rate = core[core["time_to_first_touch_hours"] <= 2]["converted"].mean()
core_late = core[core["time_to_first_touch_hours"] > 24]
core_late_n = len(core_late)
core_late_booked = core_late["converted"].sum()
core_recoverable = core_late_n * core_fast_rate - core_late_booked
core_avg_deal = bookings[bookings["trade"].isin(["SHK", "Elektro"])]["deal_size_eur"].mean()
core_recoverable_eur = core_recoverable * core_avg_deal

# ═══════════════════════════════════════════════════════════════════════════
# PRINT SUMMARY TABLES (captured for the narrative)
# ═══════════════════════════════════════════════════════════════════════════
SEP = "=" * 70

print(f"\n{SEP}\nOVERALL FUNNEL\n{SEP}")
print(funnel_table(df).to_string(index=False))

print(f"\n{SEP}\nFUNNEL BY SOURCE\n{SEP}")
print(funnel_table(df, "source").to_string())

print(f"\n{SEP}\nFUNNEL BY TRADE\n{SEP}")
print(funnel_table(df, "trade").to_string())

print(f"\n{SEP}\nFUNNEL BY COMPANY SIZE\n{SEP}")
print(funnel_table(df, "company_size").to_string())

print(f"\n{SEP}\nFUNNEL BY LEAD SCORE BUCKET\n{SEP}")
print(funnel_table(df, "score_bucket").to_string())

print(f"\n{SEP}\nFUNNEL BY QUARTER\n{SEP}")
print(funnel_table(df, "period_label").to_string())

print(f"\n{SEP}\nTRADE MIX % BY QUARTER\n{SEP}")
print(trade_period_pct.round(1).to_string())

print(f"\n{SEP}\nTIME-TO-TOUCH ANALYSIS\n{SEP}")
print(by_touch.to_string(index=False))

print(f"\n{SEP}\nDQ CATEGORIES (transcript sample, n=20)\n{SEP}")
print(cat_counts.to_string())

print(f"\n{SEP}\nBOOKINGS — AVG DEAL SIZE BY SOURCE\n{SEP}")
print(bookings.groupby("source")["deal_size_eur"].agg(["mean", "count"]).round(0).to_string())

print(f"\n{SEP}\nBOOKINGS — AVG DEAL SIZE BY TRADE\n{SEP}")
print(bookings.groupby("trade")["deal_size_eur"].agg(["mean", "count"]).round(0).to_string())

print(f"\n{SEP}\nLEAD SCORE STATS BY QUARTER\n{SEP}")
print(df.groupby("period_label")["lead_score"].describe().round(1).to_string())

print(f"\n{SEP}\nPV SHARE BY QUARTER (%)\n{SEP}")
pv_share = df.groupby("period_label", group_keys=False).apply(
    lambda x: (x["trade"] == "PV").mean() * 100, include_groups=False
).round(1)
print(pv_share.to_string())

print(f"\n{SEP}\nSMALL CO (1-5 MA) SHARE BY QUARTER (%)\n{SEP}")
small_share = df.groupby("period_label", group_keys=False).apply(
    lambda x: (x["company_size"].isin(["1-2 MA", "3-5 MA"])).mean() * 100, include_groups=False
).round(1)
print(small_share.to_string())

print(f"\n{SEP}\nMEAN TIME-TO-TOUCH BY TRADE (confound check)\n{SEP}")
print(df.groupby("trade")["time_to_first_touch_hours"].agg(["mean", "median"]).round(1).to_string())

print(f"\n{SEP}\nBOOKING RATE: TRADE x SPEED (two-way robustness)\n{SEP}")
print(speed_piv.to_string())

print(f"\n{SEP}\nLATE-TOUCH (>24h) COMPOSITION\n{SEP}")
print(f"Total late-touch leads: {len(late)}  |  PV share: {pv_share_late:.0f}%")

print(f"\n{SEP}\nHONEST RECOVERABLE OPPORTUNITY (core trades only)\n{SEP}")
print(f"Core (SHK+Elektro) fast ≤2h booking rate: {core_fast_rate*100:.1f}%")
print(f"Core late-touch (>24h) leads: {core_late_n}  (booked: {core_late_booked})")
print(f"Recoverable bookings: ~{core_recoverable:.0f}")
print(f"Avg core deal size: €{core_avg_deal:,.0f}")
print(f"=> Recoverable ARR: ~€{core_recoverable_eur:,.0f}  (vs naive €262k estimate)")

print(f"\n{SEP}\nSDR EFFORT (call_attempts) BY TRADE\n{SEP}")
print(df.groupby("trade")["call_attempts"].mean().round(2).to_string())

print(f"\n{SEP}\nBOOKED REVENUE BY TRADE\n{SEP}")
print(rev.sort_values("sum", ascending=False).round(0).to_string())
print(f"Total booked revenue: €{bookings['deal_size_eur'].sum():,.0f}")

print(f"\n\n✅  All 12 charts written to: {CHART_DIR}")
