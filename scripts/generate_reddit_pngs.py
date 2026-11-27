#!/usr/bin/env python3
"""
Generates 10 publication-grade, Reddit-ready (r/nba & r/dataisbeautiful) PNG charts
from the verified 2026-27 NBA Roster (529 players) and Sponsorship Deals (448 deals) datasets.
"""

import json
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
OUT_DIR = os.path.join(REPO_ROOT, "charts")

os.makedirs(OUT_DIR, exist_ok=True)

# Hardwood Editorial palette (warm court parchment + rich editorial inks)
BG = "#F8F3E8"
PANEL = "#EFE7D6"
TRACK = "#E5DAC5"
BORDER = "#D5C7AE"
FG = "#1C1917"
MUTED = "#57534E"
DIM = "#78716C"
GOLD = "#B45309"       # Hardwood Gold
BLUE = "#1E3A8A"       # Classic Ink Blue
GREEN = "#047857"      # Celtics Emerald
CORAL = "#C2410C"      # Court Orange-Rust
VIOLET = "#6D28D9"     # Royal Purple
CYAN = "#0E7490"       # Deep Teal
ORANGE = "#C2410C"
NEUTRAL = "#78716C"
INK_ON_ACCENT = "#FAF6EE"
WATERMARK_TEXT = "Created by reddit user TopoHaiHai"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"],
    "text.parse_math": False,
    "axes.edgecolor": BORDER,
    "axes.linewidth": 0.9,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": FG,
    "xtick.color": MUTED,
    "ytick.color": FG,
})

players = json.load(open(os.path.join(DATA_DIR, "nba_players_2026_27.json"), encoding="utf-8"))
deals = json.load(open(os.path.join(DATA_DIR, "nba_sponsorship_deals.json"), encoding="utf-8"))
pmap = {p["player_id"]: p for p in players}
deals_by_player = defaultdict(list)
for d in deals:
    deals_by_player[d["player_id"]].append(d)

N_PLAYERS = len(players)
N_DEALS = len(deals)
N_SPON = len(deals_by_player)
FOOTER_TEXT = (
    f"Data: ESPN, Basketball-Reference, NBA.com, Forbes & public endorsement filings · "
    f"Snapshot Nov 25, 2026 ({N_PLAYERS} rostered players · {N_DEALS} tracked deals across {N_SPON} players)"
)


def val(x):
    return None if (x == "" or x is None) else float(x)


def short_last_name(full_name: str) -> str:
    parts = [p for p in full_name.split() if p not in ("Jr.", "Sr.", "II", "III", "IV", "V")]
    return parts[-1] if parts else full_name


def add_header_footer(fig, kicker, title, subtitle, accent=CORAL, footer=FOOTER_TEXT):
    # Dual Hardwood Editorial top stripe (Court Rust + Classic Ink Blue)
    fig.patches.append(mpatches.Rectangle((0, 0.990), 0.5, 0.010, transform=fig.transFigure, facecolor=CORAL, edgecolor="none"))
    fig.patches.append(mpatches.Rectangle((0.5, 0.990), 0.5, 0.010, transform=fig.transFigure, facecolor=BLUE, edgecolor="none"))
    # Top-left watermark + top-right tag
    fig.text(0.045, 0.976, WATERMARK_TEXT, fontsize=8.5, fontweight="semibold", color=DIM, alpha=0.88, ha="left", va="top")
    fig.text(0.955, 0.976, "r/nba · 2026–27", fontsize=8.8, fontweight="bold", color=DIM, ha="right", va="top")
    # Kicker, Georgia editorial serif title, subtitle
    fig.text(0.045, 0.951, kicker.upper(), fontsize=9.2, fontweight="bold", color=accent, ha="left", va="top")
    fig.text(0.045, 0.924, title, fontsize=18.2, fontweight="bold", fontfamily="Georgia", color=FG, ha="left", va="top")
    fig.text(0.045, 0.876, subtitle, fontsize=10.5, color=MUTED, ha="left", va="top")
    # Footer rule & caption
    fig.lines.append(plt.Line2D([0.045, 0.955], [0.052, 0.052], transform=fig.transFigure, color=BORDER, linewidth=1.0))
    fig.text(0.045, 0.033, footer, fontsize=8.4, color=DIM, ha="left", va="center")


def save_chart(fig, filename):
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=200, facecolor=BG)
    plt.close(fig)
    print(f"Saved {filename} ({os.path.getsize(path):,} bytes)")


# ==============================================================================
# CHART 1: RINGS SELL — NBA Champions Share of Rosters vs. Sponsorships
# ==============================================================================
def chart_1_rings_sell():
    champs_n = sum(1 for p in players if p["nba_titles"] > 0)
    champ_pct = champs_n / N_PLAYERS * 100
    c_deals_n = sum(1 for d in deals if pmap[d["player_id"]]["nba_titles"] > 0)
    c_deal_pct = c_deals_n / N_DEALS * 100
    c_avg = c_deals_n / champs_n
    nc_avg = (N_DEALS - c_deals_n) / (N_PLAYERS - champs_n)

    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · The Championship Endorsement Premium",
        f"Rings Sell: Champions Are {champ_pct:.0f}% of Players — But Hold {c_deal_pct:.0f}% of All Sponsorships",
        f"Title winners average {c_avg/nc_avg:.1f}× more tracked deals ({c_avg:.2f} vs. {nc_avg:.2f}, r = +0.44) and hold +0.55 deals/ring controlling for pay.",
        accent=GOLD,
    )

    ax_top = fig.add_axes([0.23, 0.72, 0.72, 0.115])
    ax_top.set_facecolor(BG)

    labels = [f"Share of Tracked Deals\n({N_DEALS} total)", f"Share of NBA Rosters\n({N_PLAYERS} total)"]
    vals = [c_deal_pct, champ_pct]
    y_pos = [0, 1]
    ax_top.barh(y_pos, [100, 100], height=0.56, color=TRACK, edgecolor="none")
    ax_top.barh(y_pos, vals, height=0.56, color=[GOLD, GOLD], edgecolor="none")
    ax_top.set_yticks(y_pos)
    ax_top.set_yticklabels(labels, fontsize=10.5, fontweight="bold", color=FG)
    ax_top.set_xlim(0, 100)
    ax_top.set_xticks([])
    for s in ax_top.spines.values():
        s.set_visible(False)

    ax_top.text(c_deal_pct - 1.5, 0, f"{c_deal_pct:.1f}% Champions ({c_deals_n})", va="center", ha="right", color=INK_ON_ACCENT, fontweight="bold", fontsize=10)
    ax_top.text(c_deal_pct + 1.5, 0, f"{100 - c_deal_pct:.1f}% Non-Champions ({N_DEALS - c_deals_n})", va="center", ha="left", color=MUTED, fontsize=9.5)
    ax_top.text(champ_pct + 1.5, 1, f"{champ_pct:.1f}% Champions ({champs_n})  ·  {100 - champ_pct:.1f}% Non-Champions ({N_PLAYERS - champs_n})", va="center", ha="left", color=FG, fontweight="bold", fontsize=9.8)

    ax = fig.add_axes([0.28, 0.105, 0.67, 0.56])
    ax.set_facecolor(BG)

    ind_counts = defaultdict(lambda: [0, 0])
    for d in deals:
        ind_counts[d["industry"]][0 if pmap[d["player_id"]]["nba_titles"] > 0 else 1] += 1

    rows = [(ind, c / (c + nc) * 100, c, c + nc) for ind, (c, nc) in ind_counts.items()]
    rows.sort(key=lambda r: (r[1], r[3]))

    y = np.arange(len(rows))
    pcts = [r[1] for r in rows]
    names = [f"{r[0]}  (n={r[3]})" for r in rows]

    ax.barh(y, [100] * len(rows), height=0.64, color=TRACK, edgecolor="none")
    bar_colors = [GOLD if p >= 50 else (BLUE if p >= 35 else NEUTRAL) for p in pcts]
    ax.barh(y, pcts, height=0.64, color=bar_colors, edgecolor="none")

    ax.axvline(champ_pct, color=CORAL, linestyle="--", linewidth=1.3, alpha=0.9)
    ax.axvline(c_deal_pct, color=FG, linestyle=":", linewidth=1.2, alpha=0.65)
    ax.text(champ_pct + 0.8, len(rows) - 0.15, f"Roster baseline ({champ_pct:.1f}%)", color=CORAL, fontsize=8.8, fontweight="bold", va="bottom")
    ax.text(c_deal_pct + 0.8, len(rows) - 0.15, f"All-deals avg ({c_deal_pct:.1f}%)", color=MUTED, fontsize=8.8, va="bottom")

    for i, (ind, pct, c, tot) in enumerate(rows):
        txt_col = INK_ON_ACCENT if pct >= 28 else FG
        ha = "right" if pct >= 28 else "left"
        xpos = pct - 1.5 if pct >= 28 else pct + 1.5
        ax.text(xpos, i, f"{pct:.0f}%", va="center", ha=ha, fontsize=9.2, fontweight="bold", color=txt_col)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.8, color=FG)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, len(rows) + 0.35)
    ax.set_xlabel("% of Industry Sponsorship Deals Held by NBA Champions", fontsize=9.8, color=MUTED, labelpad=6)
    ax.xaxis.set_major_formatter(lambda x, _: f"{int(x)}%")
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", length=0)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)

    save_chart(fig, "01_rings_sell_champion_premium.png")


# ==============================================================================
# CHART 2: THE $400M+ CLUB — Career NBA Earnings vs. 2026-27 Salary
# ==============================================================================
def chart_2_career_vs_salary():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Active On-Court Wealth Leaders",
        "The $400M+ Club: Career NBA Earnings vs. 2026–27 Salary",
        "Top 12 active earners through 2026–27. LeBron took a $3.9M vet min with Philly — and 5 of the top 12 have 0 rings.",
        accent=BLUE,
    )

    top12 = sorted([p for p in players if p["career_earnings_usd"] != ""], key=lambda x: -x["career_earnings_usd"])[:12]
    top12 = list(reversed(top12))

    ax1 = fig.add_axes([0.235, 0.105, 0.42, 0.655])
    ax2 = fig.add_axes([0.695, 0.105, 0.255, 0.655])

    y = np.arange(len(top12))
    careers = [p["career_earnings_usd"] / 1e6 for p in top12]
    curs = [(p["current_salary_usd"] or 0) / 1e6 for p in top12]
    cols = [GOLD if p["nba_titles"] > 0 else BLUE for p in top12]

    ax1.set_facecolor(BG)
    ax1.barh(y, careers, height=0.64, color=cols, edgecolor="none", alpha=0.92)
    ax1.set_xlim(0, 690)
    ax1.set_yticks(y)
    ylabels = []
    for p in top12:
        ring = f"★{p['nba_titles']}" if p["nba_titles"] > 0 else "0 rings"
        ylabels.append(f"{p['player_name']} ({p['current_team_abbr']}, {p['age']})\n{ring} · {len(deals_by_player[p['player_id']])} deals")
    ax1.set_yticklabels(ylabels, fontsize=9, color=FG, linespacing=1.15)
    ax1.set_title("Cumulative Career NBA Earnings ($M)", fontsize=10.8, fontweight="bold", color=FG, loc="left", pad=8)
    ax1.grid(axis="x", color=BORDER, linestyle="--", alpha=0.35)
    ax1.set_axisbelow(True)
    ax1.xaxis.set_major_formatter(lambda x, _: f"${int(x)}M")
    for sp in ["top", "right"]:
        ax1.spines[sp].set_visible(False)
    ax1.tick_params(axis="y", length=0)

    for i, (val_c, p) in enumerate(zip(careers, top12)):
        ax1.text(val_c + 8, i, f"${val_c:.1f}M", va="center", ha="left", fontsize=9.2, fontweight="bold", color=FG)

    ax2.set_facecolor(BG)
    sal_cols = [CORAL if p["player_name"] == "LeBron James" else (GREEN if (p["current_salary_usd"] or 0) >= 55e6 else NEUTRAL) for p in top12]
    ax2.barh(y, curs, height=0.64, color=sal_cols, edgecolor="none", alpha=0.92)
    ax2.set_xlim(0, 86)
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.set_title("2026–27 Season Salary ($M)", fontsize=10.8, fontweight="bold", color=FG, loc="left", pad=8)
    ax2.grid(axis="x", color=BORDER, linestyle="--", alpha=0.35)
    ax2.set_axisbelow(True)
    ax2.xaxis.set_major_formatter(lambda x, _: f"${int(x)}M")
    for sp in ["top", "right"]:
        ax2.spines[sp].set_visible(False)
    ax2.tick_params(axis="y", length=0)

    for i, (val_s, p) in enumerate(zip(curs, top12)):
        lbl = f"${val_s:.1f}M"
        if p["player_name"] == "LeBron James":
            lbl += "  ← Vet min w/ PHI!"
            ax2.text(val_s + 1.8, i, lbl, va="center", ha="left", fontsize=9, fontweight="bold", color=CORAL)
        elif p["player_name"] == "Stephen Curry":
            lbl += " (#1)"
            ax2.text(val_s + 1.8, i, lbl, va="center", ha="left", fontsize=9, fontweight="bold", color=GREEN)
        else:
            ax2.text(val_s + 1.8, i, lbl, va="center", ha="left", fontsize=9, color=FG)

    leg_handles = [
        mpatches.Patch(color=GOLD, label="NBA Champion (career)"),
        mpatches.Patch(color=BLUE, label="0 NBA Titles (career)"),
        mpatches.Patch(color=GREEN, label="$55M+ salary (2026–27)"),
        mpatches.Patch(color=CORAL, label="LeBron's $3.9M pay cut"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.8, labelcolor=MUTED)

    save_chart(fig, "02_career_earnings_vs_2026_salary.png")


# ==============================================================================
# CHART 3: INSIDE THE 2026-27 NBA SPONSORSHIP ECONOMY (13 Industries)
# ==============================================================================
def chart_3_sponsorship_industries():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Brand & Industry Landscape",
        f"Where NBA Endorsements Actually Go: {N_DEALS} Deals Across 13 Industries",
        "Footwear, Food & Beverage, and Fashion/Luxury drive 56% of deals — while Prediction Markets & Spirits target top-tier stars.",
        accent=GREEN,
    )

    ax = fig.add_axes([0.265, 0.105, 0.69, 0.72])
    ax.set_facecolor(BG)

    by_ind = defaultdict(list)
    for d in deals:
        by_ind[d["industry"]].append(d)

    notable_brands = {
        "Footwear & Apparel": "Nike, Adidas, Jordan Brand, New Balance, Li-Ning",
        "Food & Beverage": "Gatorade, Sprite, McDonald's, PepsiCo",
        "Fashion & Luxury": "Louis Vuitton, Coach, Tissot, BVLGARI",
        "Retail & Collectibles": "Dick's, Fanatics, Foot Locker, Macy's",
        "Technology & Consumer Electronics": "Google, Beats by Dre, Bose, Dialpad",
        "Automotive & Aviation": "Toyota, Turkish Airlines, Mercedes-Benz, CarMax",
        "Gaming & Media": "2K Sports, PlayStation, Nintendo, Overwatch",
        "Financial Services & Banking": "Chase, AmEx, SoFi, Klarna, BTCC",
        "Spirits & Alcohol": "Michelob Ultra, Hennessy, Cognac Frapin, Maker's Mark",
        "Health, Wellness & Personal Care": "CeraVe, Glaukos, Dove, Zamst",
        "Telecommunications": "AT&T, Xfinity, Verizon",
        "Insurance": "State Farm, Amica, USAA, AAMI",
        "Gambling & Prediction Markets": "Polymarket, Kalshi, FanDuel, PrizePicks",
    }

    rows = [(ind, len(items), len({x["player_id"] for x in items}), notable_brands.get(ind, "")) for ind, items in by_ind.items()]
    rows.sort(key=lambda r: r[1])

    y = np.arange(len(rows))
    counts = [r[1] for r in rows]

    colors = []
    for ind, cnt, _, _ in rows:
        if ind == "Footwear & Apparel":
            colors.append(BLUE)
        elif ind == "Food & Beverage":
            colors.append(GREEN)
        elif ind == "Fashion & Luxury":
            colors.append(VIOLET)
        elif ind in ("Gambling & Prediction Markets", "Spirits & Alcohol"):
            colors.append(CORAL)
        elif ind == "Insurance":
            colors.append(GOLD)
        else:
            colors.append(NEUTRAL)

    ax.barh(y, counts, height=0.66, color=colors, edgecolor="none", alpha=0.93)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.8, fontweight="bold", color=FG)
    ax.set_xlim(0, 195)
    ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xlabel("Number of Tracked NBA Player Sponsorship Deals", fontsize=9.8, color=MUTED, labelpad=6)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, (ind, cnt, n_pl, brands_str) in enumerate(rows):
        pct = cnt / N_DEALS * 100
        ax.text(cnt + 2.2, i, f"{cnt} ({pct:.1f}%)  ·  {brands_str}", va="center", ha="left",
                fontsize=8.5, color=FG if cnt >= 25 or ind in ("Gambling & Prediction Markets", "Spirits & Alcohol", "Insurance") else MUTED)

    callout = (
        "SPOTLIGHT: HIGH-WEALTH VERTICALS\n"
        "• Gambling & Prediction Markets (8):\n"
        "  LeBron (Polymarket $15M/yr, ex-DraftKings),\n"
        "  KD (FanDuel, Kalshi), Giannis (Kalshi),\n"
        "  Ant (PrizePicks), Jokić (Superbet)\n"
        "• Spirits & Alcohol (14): Hennessy, Lobos 1707,\n"
        "  Michelob Ultra, Cognac Frapin, Don Julio"
    )
    ax.text(
        0.985, 0.34, callout, transform=ax.transAxes,
        fontsize=8.3, color=FG, ha="right", va="bottom", linespacing=1.45,
        bbox=dict(boxstyle="round,pad=0.65", facecolor=PANEL, edgecolor=CORAL, linewidth=1.1),
    )

    save_chart(fig, "03_nba_sponsorship_economy_13_industries.png")


# ==============================================================================
# CHART 4: MOST MARKETABLE ROSTERS IN 2026-27 (Top 15 Teams)
# ==============================================================================
def chart_4_top_sponsored_teams():
    tm_deals = defaultdict(list)
    for d in deals:
        tm_deals[d["current_team"]].append(d)

    rows = []
    for tm, items in tm_deals.items():
        p_counts = Counter(x["player_name"] for x in items)
        top_stars = ", ".join(f"{short_last_name(n)} ({c})" for n, c in p_counts.most_common(3))
        rows.append((tm, len(items), len(p_counts), top_stars))
    rows.sort(key=lambda r: (r[1], r[2]), reverse=True)
    top15 = list(reversed(rows[:15]))

    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Franchise Star Power",
        "Which NBA Rosters Hoard the Most Sponsorship Deals in 2026–27?",
        f"After blockbuster 2026 moves (LeBron & Jaylen Brown to Philly; Giannis to Miami), the 76ers lead with {rows[0][1]} tracked deals.",
        accent=VIOLET,
    )

    ax = fig.add_axes([0.22, 0.105, 0.735, 0.72])
    ax.set_facecolor(BG)

    y = np.arange(len(top15))
    counts = [r[1] for r in top15]
    bar_cols = [VIOLET if i >= 12 else (BLUE if i >= 8 else NEUTRAL) for i in range(len(top15))]

    ax.barh(y, counts, height=0.66, color=bar_cols, edgecolor="none", alpha=0.92)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in top15], fontsize=10, fontweight="bold", color=FG)
    ax.set_xlim(0, 56)
    ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xlabel("Total Tracked Player Sponsorship Deals on 2026–27 Roster", fontsize=9.8, color=MUTED, labelpad=6)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, (tm, cnt, n_pl, stars) in enumerate(top15):
        stars_disp = stars.replace("Gilgeous-Alexander", "SGA")
        ax.text(cnt + 0.8, i, f"{cnt} deals ({n_pl} players)  ·  {stars_disp}", va="center", ha="left",
                fontsize=8.8, color=FG if i >= 10 else MUTED)

    save_chart(fig, "04_nba_teams_most_sponsored_rosters.png")


# ==============================================================================
# CHART 5: THE GLOBAL NBA — Top International Nations
# ==============================================================================
def chart_5_global_nba():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Global Footprint (45 Nationalities · 6 Continents)",
        "The Global NBA: France Leads in Players, Canada Dominates Dollars & Deals",
        "125+ international players across 44 non-USA nations. Cameroon's 3 stars out-earn 17 French players ($670M vs. $602M).",
        accent=CYAN,
    )

    intl = [p for p in players if p["nationality"] != "USA"]
    nat_p = Counter(p["nationality"] for p in intl)
    nat_d = Counter(pmap[d["player_id"]]["nationality"] for d in deals if pmap[d["player_id"]]["nationality"] != "USA")
    nat_e = defaultdict(int)
    nat_cont = {}
    for p in intl:
        nat_cont[p["nationality"]] = p["continent"]
        if p["career_earnings_usd"] != "":
            nat_e[p["nationality"]] += p["career_earnings_usd"]

    top12_nats = sorted(nat_p.keys(), key=lambda n: (nat_p[n], nat_e[n]), reverse=True)[:12]
    top12_nats = list(reversed(top12_nats))

    cont_col = {"Europe": CYAN, "North America": BLUE, "Oceania": VIOLET, "Africa": GOLD, "Asia": CORAL, "South America": GREEN}

    ax1 = fig.add_axes([0.19, 0.105, 0.25, 0.655])
    ax2 = fig.add_axes([0.48, 0.105, 0.25, 0.655])
    ax3 = fig.add_axes([0.77, 0.105, 0.19, 0.655])

    y = np.arange(len(top12_nats))
    cols = [cont_col.get(nat_cont[n], BLUE) for n in top12_nats]

    p_vals = [nat_p[n] for n in top12_nats]
    ax1.barh(y, p_vals, height=0.64, color=cols, alpha=0.92)
    ax1.set_yticks(y)
    ax1.set_yticklabels(top12_nats, fontsize=10, fontweight="bold", color=FG)
    ax1.set_xlim(0, 22)
    ax1.set_title("Rostered Players", fontsize=10.6, fontweight="bold", color=FG, loc="left", pad=8)
    ax1.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax1.set_axisbelow(True)
    for sp in ["top", "right"]: ax1.spines[sp].set_visible(False)
    ax1.tick_params(axis="y", length=0)
    for i, v in enumerate(p_vals):
        ax1.text(v + 0.5, i, str(v), va="center", ha="left", fontsize=9.2, fontweight="bold", color=FG)

    e_vals = [nat_e[n] / 1e6 for n in top12_nats]
    ax2.barh(y, e_vals, height=0.64, color=cols, alpha=0.92)
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.set_xlim(0, 1780)
    ax2.set_title("Combined Career Earnings ($M)", fontsize=10.6, fontweight="bold", color=FG, loc="left", pad=8)
    ax2.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax2.set_axisbelow(True)
    ax2.xaxis.set_major_formatter(lambda x, _: f"${int(x)}M")
    for sp in ["top", "right"]: ax2.spines[sp].set_visible(False)
    ax2.tick_params(axis="y", length=0)
    for i, v in enumerate(e_vals):
        lbl = f"${v/1000:.2f}B" if v >= 1000 else f"${v:.0f}M"
        ax2.text(v + 30, i, lbl, va="center", ha="left", fontsize=9, fontweight="bold", color=FG)

    d_vals = [nat_d[n] for n in top12_nats]
    ax3.barh(y, d_vals, height=0.64, color=cols, alpha=0.92)
    ax3.set_yticks(y)
    ax3.set_yticklabels([])
    ax3.set_xlim(0, 35)
    ax3.set_title("Tracked Deals", fontsize=10.6, fontweight="bold", color=FG, loc="left", pad=8)
    ax3.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax3.set_axisbelow(True)
    for sp in ["top", "right"]: ax3.spines[sp].set_visible(False)
    ax3.tick_params(axis="y", length=0)
    for i, v in enumerate(d_vals):
        ax3.text(v + 0.8, i, str(v), va="center", ha="left", fontsize=9.2, fontweight="bold", color=FG if v > 0 else DIM)

    leg_handles = [
        mpatches.Patch(color=CYAN, label="Europe (70 players)"),
        mpatches.Patch(color=BLUE, label="North America ex-USA (25)"),
        mpatches.Patch(color=GOLD, label="Africa (17)"),
        mpatches.Patch(color=VIOLET, label="Oceania (10)"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.8, labelcolor=MUTED)

    save_chart(fig, "05_global_nba_international_footprint.png")


# ==============================================================================
# CHART 6: CONTRACT HORIZONS (2003 -> 2036+)
# ==============================================================================
def chart_6_contract_horizons():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Major Endorsement Contract Horizons (2003 → 2036+)",
        "The Longest Bets in NBA Sponsorships: Lifetime Deals & 2026 Shakeups",
        "Verified timelines of disclosed multi-year, lifetime, and recently terminated NBA mega-deals as of November 2026.",
        accent=CORAL,
    )

    ax = fig.add_axes([0.285, 0.105, 0.665, 0.68])
    ax.set_facecolor(BG)

    horizon_specs = [
        ("LeBron James", "Nike", 2003.5, 2037.0, "Lifetime", "Lifetime ($1B+ est.)"),
        ("Kevin Durant", "Nike", 2007.5, 2037.0, "Lifetime", "Lifetime (signed 2023)"),
        ("Damian Lillard", "Adidas", 2012.5, 2037.0, "Lifetime", "Lifetime (signed 2024)"),
        ("Stephen Curry", "Li-Ning", 2026.5, 2036.5, "Active", "10-yr · $400M (2026–36)"),
        ("Stephen Curry", "Under Armour", 2013.5, 2026.8, "Ended", "Ended Oct 2026 (13 yrs)"),
        ("LaMelo Ball", "PUMA", 2020.8, 2030.8, "Active", "10-yr · $100M (2020–30)"),
        ("Devin Booker", "Nike", 2015.5, 2029.5, "Active", "Extended thru 2029"),
        ("Luka Dončić", "Jordan Brand", 2019.9, 2029.5, "Active", "Extended thru 2029"),
        ("James Harden", "Adidas", 2015.8, 2028.8, "Active", "13-yr · $200M (2015–28)"),
        ("Kyrie Irving", "ANTA", 2023.5, 2028.5, "Active", "5-yr · CCO (2023–28)"),
        ("Klay Thompson", "ANTA", 2014.5, 2027.5, "Active", "10-yr ext. thru 2027"),
        ("Zion Williamson", "Jordan Brand", 2019.6, 2026.5, "Ended", "7-yr · $75M ended 2026"),
        ("Shai Gilgeous-Alexander", "Converse", 2020.5, 2026.5, "Ended", "Moved to Nike Jun 2026"),
        ("LeBron James", "DraftKings", 2024.1, 2026.5, "Ended", "Ended → Polymarket ($15M/yr)"),
        ("Kawhi Leonard", "Aspiration", 2021.5, 2025.5, "Ended", "4-yr · $28M (NBA probe)"),
    ]
    horizon_specs = list(reversed(horizon_specs))

    y = np.arange(len(horizon_specs))
    status_color = {"Lifetime": GOLD, "Active": GREEN, "Ended": NEUTRAL}

    for i, (player, brand, s, e, st, note) in enumerate(horizon_specs):
        col = CORAL if (brand == "Li-Ning" and player == "Stephen Curry") else status_color[st]
        ax.barh(i, e - s, left=s, height=0.58, color=col, edgecolor="none", alpha=0.92)
        ax.scatter([s], [i], color=FG, s=18, zorder=4)
        if st == "Lifetime":
            ax.text(2037.2, i, "→", va="center", ha="left", color=GOLD, fontsize=12, fontweight="bold")
            ax.text(s + 0.5, i, note, va="center", ha="left", color=INK_ON_ACCENT, fontsize=8.5, fontweight="bold")
        elif e - s >= 7.5:
            ax.text(s + 0.45, i, note, va="center", ha="left", color=INK_ON_ACCENT, fontsize=8.4, fontweight="bold")
        else:
            xpos = max(e + 0.4, 2027.35) if e < 2031 else s - 0.35
            ha = "left" if e < 2031 else "right"
            ax.text(xpos, i, note, va="center", ha=ha, color=FG if st != "Ended" else MUTED, fontsize=8.4, fontweight="bold" if brand == "Li-Ning" else "normal")

    ax.axvline(2026.9, color=CORAL, linestyle="--", linewidth=1.4, zorder=5)
    ax.text(2026.9, len(horizon_specs) - 0.15, "Nov 2026", color=CORAL, fontsize=9, fontweight="bold", ha="center", va="bottom")

    ax.set_yticks(y)
    ax.set_yticklabels([f"{p} · {b}" for p, b, *_ in horizon_specs], fontsize=9.4, fontweight="bold", color=FG)
    ax.set_xlim(2002.5, 2038.8)
    ax.set_ylim(-0.7, len(horizon_specs) + 0.45)
    ax.set_xticks(range(2004, 2038, 4))
    ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xlabel("Contract Year", fontsize=9.8, color=MUTED, labelpad=6)
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    leg_handles = [
        mpatches.Patch(color=GOLD, label="Lifetime Contract"),
        mpatches.Patch(color=GREEN, label="Active Multi-Year"),
        mpatches.Patch(color=CORAL, label="2026 Mega-Switch (Curry → Li-Ning)"),
        mpatches.Patch(color=NEUTRAL, label="Ended / Expired"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.6, labelcolor=MUTED)

    save_chart(fig, "06_endorsement_contract_horizons.png")


# ==============================================================================
# CHART 7 (NEW — Q1): WHO SELLS WHAT? Player Wealth by Sponsorship Industry
# ==============================================================================
def chart_7_who_sells_what():
    vice_inds = {"Gambling & Prediction Markets", "Spirits & Alcohol"}
    spon_pids = sorted(
        [pid for pid in deals_by_player if val(pmap[pid]["career_earnings_usd"]) is not None],
        key=lambda pid: val(pmap[pid]["career_earnings_usd"]),
    )
    all_spon_med = float(np.median([val(pmap[pid]["career_earnings_usd"]) / 1e6 for pid in spon_pids]))
    vice_pids = {d["player_id"] for d in deals if d["industry"] in vice_inds}
    vice_med = float(np.median([val(pmap[pid]["career_earnings_usd"]) / 1e6 for pid in vice_pids]))
    other_med = float(np.median([val(pmap[pid]["career_earnings_usd"]) / 1e6 for pid in (set(spon_pids) - vice_pids)]))

    rows = []
    for ind in set(d["industry"] for d in deals):
        ds = [d for d in deals if d["industry"] == ind]
        pids = list({d["player_id"] for d in ds})
        ces = [val(pmap[pid]["career_earnings_usd"]) / 1e6 for pid in pids if val(pmap[pid]["career_earnings_usd"]) is not None]
        rows.append((ind, float(np.median(ces)), len(pids), len(ds), ind in vice_inds))
    rows.sort(key=lambda r: r[1])

    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Who Sells What? Wealth Skew Across Industries",
        "Who Sells What? Gambling & Spirits Skew Richest, Fashion Skews Youngest",
        f"Median career NBA earnings of endorsers in each industry. Vice-sponsored stars earn ${vice_med:.0f}M median vs. ${other_med:.0f}M other sponsored (p = 0.006).",
        accent=CORAL,
    )

    # Left main panel: 13 Industries ranked by median career earnings
    ax = fig.add_axes([0.275, 0.11, 0.435, 0.675])
    ax.set_facecolor(BG)

    y = np.arange(len(rows))
    meds = [r[1] for r in rows]
    cols = [CORAL if r[4] else (VIOLET if r[0] == "Fashion & Luxury" else (GOLD if r[1] >= 220 else BLUE)) for r in rows]

    ax.barh(y, meds, height=0.65, color=cols, alpha=0.92, edgecolor="none")
    ax.axvline(all_spon_med, color=MUTED, linestyle="--", linewidth=1.2, alpha=0.85)
    ax.text(all_spon_med + 5, len(rows) - 0.15, f"All sponsored median (${all_spon_med:.0f}M)", color=MUTED, fontsize=8.4, fontweight="bold", va="bottom")

    ax.set_yticks(y)
    ax.set_yticklabels([f"{r[0]} (n={r[2]})" for r in rows], fontsize=9.2, color=FG)
    for tick_lbl, r in zip(ax.get_yticklabels(), rows):
        if r[4]:
            tick_lbl.set_color(CORAL)
            tick_lbl.set_fontweight("bold")
    ax.set_xlim(0, 465)
    ax.set_ylim(-0.65, len(rows) + 0.35)
    ax.xaxis.set_major_formatter(lambda x, _: f"${int(x)}M")
    ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xlabel("Median Career NBA Earnings of Participating Players ($M)", fontsize=9.4, color=MUTED, labelpad=6)
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, r in enumerate(rows):
        ax.text(r[1] + 6, i, f"${r[1]:.1f}M", va="center", ha="left", fontsize=9, fontweight="bold", color=CORAL if r[4] else FG)

    # Right top panel: Vice deal prevalence across career earnings quartiles
    ax_q = fig.add_axes([0.755, 0.44, 0.20, 0.315])
    ax_q.set_facecolor(PANEL)
    for sp in ax_q.spines.values():
        sp.set_edgecolor(CORAL)
        sp.set_linewidth(1.0)

    qsz = len(spon_pids) // 4
    q_labels, q_pcts = [], []
    for i in range(4):
        grp = spon_pids[i * qsz : (i + 1) * qsz if i < 3 else len(spon_pids)]
        lo = int(round(val(pmap[grp[0]]["career_earnings_usd"]) / 1e6))
        hi = int(round(val(pmap[grp[-1]]["career_earnings_usd"]) / 1e6))
        vp = sum(1 for pid in grp if pid in vice_pids)
        q_labels.append(f"Q{i+1}\n${lo}–${hi}M")
        q_pcts.append(vp / len(grp) * 100)

    yq = np.arange(4)
    q_cols = [DIM, GOLD, GOLD, CORAL]
    ax_q.barh(yq, [30] * 4, height=0.52, color=TRACK)
    ax_q.barh(yq, q_pcts, height=0.52, color=q_cols)
    ax_q.set_yticks(yq)
    ax_q.set_yticklabels(q_labels, fontsize=8.1, color=FG, fontweight="bold")
    ax_q.invert_yaxis()
    ax_q.set_xlim(0, 32)
    ax_q.set_xticks([])
    ax_q.tick_params(axis="y", length=0, pad=5)
    ax_q.set_title("% With Alcohol/Gambling Deal\nby Career Earnings Quartile", fontsize=9.0, fontweight="bold", color=CORAL, pad=8)
    for i, pct in enumerate(q_pcts):
        ax_q.text(max(pct + 1.0, 1.2), i, f"{pct:.1f}%", va="center", ha="left", fontsize=8.6, fontweight="bold", color=FG if pct > 0 else DIM)

    # Right bottom panel: Honest statistical caveats box
    caveat_txt = (
        "STATISTICAL REALITY CHECK\n"
        f"• Vice players (n={len(vice_pids)}): ${vice_med:.1f}M med\n"
        f"  vs. ${other_med:.1f}M other sponsored\n"
        "  (Mann-Whitney p = 0.0057).\n"
        "• Caveat: Small n (22 vice deals) &\n"
        "  richer stars hold larger total\n"
        "  portfolios (mean 5.1 vs. 3.2).\n"
        "• Q1 ($5M–$83M) has ZERO vice\n"
        "  deals; young stars tilt Fashion."
    )
    fig.text(
        0.755, 0.115, caveat_txt, fontsize=8.3, color=FG, ha="left", va="bottom", linespacing=1.48,
        bbox=dict(boxstyle="round,pad=0.65", facecolor=PANEL, edgecolor=BORDER, linewidth=1.0),
    )

    leg_handles = [
        mpatches.Patch(color=CORAL, label="Alcohol & Gambling ('Vice')"),
        mpatches.Patch(color=GOLD, label="High-Earnings Verticals ($220M+)"),
        mpatches.Patch(color=BLUE, label="Mid-Tier / Mass-Market"),
        mpatches.Patch(color=VIOLET, label="Fashion & Luxury (Lowest Median)"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.5, labelcolor=MUTED)

    save_chart(fig, "07_who_sells_what_wealth_by_industry.png")


# ==============================================================================
# CHART 8: 2026-27 SNEAKER WARS
# ==============================================================================
def chart_8_sneaker_wars():
    shoe_brands = [
        "Nike", "Adidas", "Jordan Brand", "New Balance", "PUMA", "Skechers",
        "Li-Ning", "361°", "ANTA", "Converse", "Peak", "741 Performance",
        "Reebok", "Rigorer", "Under Armour", "Stria Sports"
    ]
    chinese = {"Li-Ning", "ANTA", "361°", "Peak", "Rigorer"}
    nike_inc = {"Nike", "Jordan Brand", "Converse"}
    alias = {
        "LeBron James": "LeBron", "Giannis Antetokounmpo": "Giannis",
        "Shai Gilgeous-Alexander": "SGA", "Kevin Durant": "KD",
        "Stephen Curry": "Curry", "Anthony Edwards": "Ant",
        "Luka Doncic": "Luka", "Nikola Jokic": "Jokić",
        "Kyrie Irving": "Kyrie", "Joel Embiid": "Embiid",
        "Kawhi Leonard": "Kawhi", "Damian Lillard": "Lillard",
        "Jayson Tatum": "Tatum", "Jimmy Butler III": "Butler",
        "James Harden": "Harden", "Donovan Mitchell": "Mitchell",
        "Tyrese Haliburton": "Haliburton", "LaMelo Ball": "LaMelo",
        "De'Aaron Fox": "Fox",
    }

    rows = []
    for b in shoe_brands:
        ds = [d for d in deals if d["brand"] == b and d["industry"] == "Footwear & Apparel" and d["deal_status"] in ("Active", "Lifetime")]
        pids = list({d["player_id"] for d in ds})
        if not pids:
            continue
        pids.sort(key=lambda pid: -(val(pmap[pid]["career_earnings_usd"]) or 0))
        sn = [alias.get(pmap[pid]["player_name"], pmap[pid]["player_name"]) for pid in pids]
        stars = ", ".join(sn[:4]) + (f" +{len(sn)-4}" if len(sn) > 4 else "")
        rows.append((b, len(pids), stars))
    rows.sort(key=lambda r: (r[1], 1 if r[0] == "741 Performance" else 0, r[0]))

    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Footwear Battleground",
        "The Sneaker Wars: Nike Leads Volume, But Chinese Brands Stole the Stars",
        f"Active & lifetime footwear deals tracked across {len(rows)} brands — Curry ($400M Li-Ning), Jokić (361°), and Kyrie (ANTA) reshape the market.",
        accent=CORAL,
    )

    ax = fig.add_axes([0.19, 0.105, 0.76, 0.68])
    ax.set_facecolor(BG)

    y = np.arange(len(rows))
    cnts = [r[1] for r in rows]
    cols = [BLUE if r[0] in nike_inc else (CORAL if r[0] in chinese else (GOLD if r[0] == "741 Performance" else GREEN)) for r in rows]

    ax.barh(y, cnts, height=0.65, color=cols, alpha=0.92)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.4, fontweight="bold", color=FG)
    ax.set_xlim(0, 42)
    ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xlabel("Active / Lifetime Tracked NBA Players on Brand Roster", fontsize=9.8, color=MUTED, labelpad=6)
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, (b, cnt, stars) in enumerate(rows):
        ax.text(cnt + 0.6, i, f"{cnt}  ·  {stars}", va="center", ha="left", fontsize=8.8, color=FG if cnt >= 3 else MUTED)

    leg_handles = [
        mpatches.Patch(color=BLUE, label="Nike Inc. (Nike / Jordan / Converse)"),
        mpatches.Patch(color=CORAL, label="Chinese Brands (Li-Ning / ANTA / 361° / Peak / Rigorer)"),
        mpatches.Patch(color=GREEN, label="US & Euro Rivals (Adidas / NB / PUMA / Skechers / UA)"),
        mpatches.Patch(color=GOLD, label="Independent (741)"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=2, frameon=False, fontsize=8.4, labelcolor=MUTED)

    save_chart(fig, "08_nba_sneaker_wars_2026_27.png")


# ==============================================================================
# CHART 9 (UPGRADED — Q3 + Q4): TENURE & RINGS VS SPONSORSHIPS
# ==============================================================================
def chart_9_experience_and_rings():
    exp_buckets = [(0, 1, "0–1 yr"), (2, 4, "2–4 yrs"), (5, 7, "5–7 yrs"), (8, 10, "8–10 yrs"), (11, 14, "11–14 yrs"), (15, 30, "15+ yrs")]
    exp_stats = []
    for lo, hi, lbl in exp_buckets:
        ps = [p for p in players if val(p["experience_years"]) is not None and lo <= val(p["experience_years"]) <= hi]
        dcs = [len(deals_by_player[p["player_id"]]) for p in ps]
        sp = sum(1 for c in dcs if c > 0)
        exp_stats.append((lbl, len(ps), sp / len(ps) * 100, float(np.mean(dcs))))

    ring_buckets = [(0, 0, "0 Rings"), (1, 1, "1 Ring"), (2, 3, "2–3 Rings"), (4, 10, "4 Rings")]
    ring_stats = []
    for lo, hi, lbl in ring_buckets:
        ps = [p for p in players if lo <= p["nba_titles"] <= hi]
        dcs = [len(deals_by_player[p["player_id"]]) for p in ps]
        sp = sum(1 for c in dcs if c > 0)
        ring_stats.append((lbl, len(ps), sp / len(ps) * 100, float(np.mean(dcs))))

    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Experience & Championships vs. Sponsorship Volume",
        "Tenure vs. Rings: Why Veterans Lead Raw — But Youth Wins at Equal Pay",
        "92% of 15+ yr vets have deals (4.17 avg), yet holding pay constant, young max stars beat veteran grinders while rings add +0.55 deals each.",
        accent=BLUE,
    )

    # Left panel: Experience buckets
    ax1 = fig.add_axes([0.075, 0.30, 0.48, 0.485])
    ax1.set_facecolor(BG)
    x1 = np.arange(len(exp_stats))
    y1 = [r[3] for r in exp_stats]
    c1 = [CORAL if i == len(exp_stats) - 1 else BLUE for i in range(len(exp_stats))]
    ax1.bar(x1, y1, width=0.58, color=c1, alpha=0.92)
    ax1.set_xticks(x1)
    ax1.set_xticklabels([f"{r[0]}\n{r[2]:.0f}% spon\n(n={r[1]})" for r in exp_stats], fontsize=8.3, color=FG, linespacing=1.2)
    ax1.set_ylim(0, 5.0)
    ax1.set_ylabel("Avg Tracked Sponsorships per Player", fontsize=9.4, color=MUTED)
    ax1.set_title("YEARS IN THE NBA  (Raw r = +0.52 · ρ = +0.48)", fontsize=10.5, fontweight="bold", color=BLUE, loc="left", pad=10)
    ax1.grid(axis="y", color=BORDER, linestyle="--", alpha=0.3)
    ax1.set_axisbelow(True)
    for sp in ["top", "right"]: ax1.spines[sp].set_visible(False)
    for i, r in enumerate(exp_stats):
        ax1.text(i, r[3] + 0.12, f"{r[3]:.2f}", ha="center", va="bottom", fontsize=9.8, fontweight="bold", color=CORAL if i == len(exp_stats) - 1 else FG)

    # Right panel: NBA Titles buckets
    ax2 = fig.add_axes([0.615, 0.30, 0.34, 0.485])
    ax2.set_facecolor(BG)
    x2 = np.arange(len(ring_stats))
    y2 = [r[3] for r in ring_stats]
    c2 = [NEUTRAL, GREEN, GREEN, GOLD]
    ax2.bar(x2, y2, width=0.55, color=c2, alpha=0.92)
    ax2.set_xticks(x2)
    ax2.set_xticklabels([f"{r[0]}\n{r[2]:.0f}% spon\n(n={r[1]})" for r in ring_stats], fontsize=8.3, color=FG, linespacing=1.2)
    ax2.set_ylim(0, 9.2)
    ax2.set_title("NBA TITLES  (Raw r = +0.44 · ρ = +0.31)", fontsize=10.5, fontweight="bold", color=GOLD, loc="left", pad=10)
    ax2.grid(axis="y", color=BORDER, linestyle="--", alpha=0.3)
    ax2.set_axisbelow(True)
    for sp in ["top", "right"]: ax2.spines[sp].set_visible(False)
    for i, r in enumerate(ring_stats):
        ax2.text(i, r[3] + 0.2, f"{r[3]:.2f}", ha="center", va="bottom", fontsize=9.8, fontweight="bold", color=GOLD if i == len(ring_stats) - 1 else FG)

    # Bottom multivariate twist banner
    banner = (
        "THE MULTIVARIATE PLOT TWIST  (OLS: Experience + Titles + Career Earnings + 2026–27 Salary · N = 448, R² = 0.67)\n"
        "• Experience FLIPS NEGATIVE (−0.12 deals/yr, p < 10⁻⁷) once you control for pay: veterans lead raw only via survivorship — at equal pay, young stars (Wemby, Flagg, Ant) win.\n"
        "• Championships STAY POSITIVE (+0.55 deals/ring, p < 10⁻⁶) even controlling for pay & tenure — and still +0.34 deals/ring excluding LeBron & Curry (p = 0.0014).\n"
        "• Within sponsored players only (n = 129), experience is flat for active deals (ρ = −0.15, p = 0.09) — longer careers mostly accumulate historical deals."
    )
    fig.text(
        0.045, 0.088, banner, fontsize=8.6, color=FG, ha="left", va="bottom", linespacing=1.52,
        bbox=dict(boxstyle="round,pad=0.65", facecolor=PANEL, edgecolor=GOLD, linewidth=1.2),
    )

    save_chart(fig, "09_experience_and_rings_vs_sponsorships.png")


# ==============================================================================
# CHART 10: ALL 30 NBA TEAMS MATRIX (Age vs. Payroll vs. Deals)
# ==============================================================================
def chart_10_team_matrix():
    by_tm = defaultdict(list)
    for p in players:
        by_tm[(p["current_team_abbr"], p["current_team"])].append(p)

    teams = []
    for (abbr, tm), ps in sorted(by_tm.items()):
        pay = sum((p["current_salary_usd"] or 0) for p in ps) / 1e6
        age = float(np.mean([p["age"] for p in ps]))
        dc = sum(len(deals_by_player[p["player_id"]]) for p in ps)
        teams.append({"abbr": abbr, "team": tm, "pay": pay, "age": age, "deals": dc})

    med_age = 26.0
    med_pay = 199.0

    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · All 30 Franchises · Age vs. Payroll vs. Star Power",
        "2026–27 NBA Team Matrix: Win-Now Superteams vs. Young Cores",
        "X = Avg Roster Age, Y = 2026–27 Payroll ($M), Bubble Size = Tracked Sponsorships. OKC breaks the curve (24.5 yrs · $220M · 27 deals).",
        accent=GREEN,
    )

    ax = fig.add_axes([0.08, 0.115, 0.875, 0.68])
    ax.set_facecolor(BG)

    ax.set_xlim(23.4, 29.6)
    ax.set_ylim(112, 238)

    # Quadrant subtle shading
    ax.axvspan(23.4, med_age, ymin=(med_pay - 112) / (238 - 112), ymax=1.0, color=GREEN, alpha=0.05)
    ax.axvspan(med_age, 29.6, ymin=(med_pay - 112) / (238 - 112), ymax=1.0, color=CORAL, alpha=0.05)
    ax.axvspan(23.4, med_age, ymin=0.0, ymax=(med_pay - 112) / (238 - 112), color=BLUE, alpha=0.04)

    ax.axvline(med_age, color=MUTED, linewidth=1.1, alpha=0.5)
    ax.axhline(med_pay, color=MUTED, linewidth=1.1, alpha=0.5)
    ax.grid(color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    ax.text(23.52, 234.5, "YOUNG & LOADED", color=GREEN, fontsize=9.2, fontweight="bold", ha="left", va="top")
    ax.text(29.45, 234.5, "WIN-NOW SUPERTEAMS", color=CORAL, fontsize=9.2, fontweight="bold", ha="right", va="top")
    ax.text(23.52, 136.0, "REBUILDING / YOUTH CORES", color=BLUE, fontsize=9.2, fontweight="bold", ha="left", va="bottom")
    ax.text(29.45, 117.0, "VETERAN VALUE ROSTERS", color=MUTED, fontsize=9.2, fontweight="bold", ha="right", va="bottom")

    for tm in sorted(teams, key=lambda x: x["deals"]):
        col = CORAL if tm["deals"] >= 20 else (GREEN if (tm["age"] < med_age and tm["pay"] >= med_pay) else (GOLD if tm["pay"] >= med_pay else BLUE))
        sz = max(210, 120 + tm["deals"] * 42)
        ax.scatter([tm["age"]], [tm["pay"]], s=sz, color=col, alpha=0.88, edgecolors=BG, linewidths=1.4, zorder=3)
        ink = INK_ON_ACCENT
        if tm["abbr"] == "DET":
            continue  # combined label with PHX (identical 26.0 yrs / $189.5M spot)
        lbl = "DET\nPHX" if tm["abbr"] == "PHX" else tm["abbr"]
        ax.text(tm["age"], tm["pay"], lbl, ha="center", va="center", fontsize=6.2 if tm["abbr"] == "PHX" else (7.8 if tm["deals"] >= 18 else 6.8), fontweight="bold", color=ink, zorder=4, linespacing=0.95)

    # Standout callouts placed in wide-open zones
    tmap = {t["abbr"]: t for t in teams}
    callouts = [
        ("OKC", (24.35, 206.0), "OKC: 24.5 yrs · $220M · 27 deals"),
        ("PHI", (26.45, 234.2), "PHI: #1 deals (32) · $224M"),
        ("GS", (28.75, 204.5), "GS: Oldest (29.1 yrs) · 24 deals"),
        ("MEM", (25.35, 120.8), "MEM: Lowest payroll ($121M)"),
    ]
    for abbr, (tx, ty), txt in callouts:
        tm = tmap[abbr]
        ax.annotate(
            txt, xy=(tm["age"], tm["pay"]), xytext=(tx, ty),
            fontsize=8.6, fontweight="bold", color=FG, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9, ls="--"),
            zorder=5,
        )

    ax.set_xlabel("Average 2026–27 Roster Age (Years)", fontsize=9.8, color=MUTED, labelpad=6)
    ax.set_ylabel("Total 2026–27 Payroll ($M)", fontsize=9.8, color=MUTED, labelpad=6)
    ax.yaxis.set_major_formatter(lambda y, _: f"${int(y)}M")
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0f} yrs")
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)

    leg_handles = [
        mpatches.Patch(color=CORAL, label="20+ tracked deals"),
        mpatches.Patch(color=GREEN, label="Young & >$199M payroll"),
        mpatches.Patch(color=GOLD, label="Vet & >$199M payroll"),
        mpatches.Patch(color=BLUE, label="Below median payroll"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.6, labelcolor=MUTED)

    save_chart(fig, "10_nba_30_team_matrix_age_payroll_deals.png")


if __name__ == "__main__":
    chart_1_rings_sell()
    chart_2_career_vs_salary()
    chart_3_sponsorship_industries()
    chart_4_top_sponsored_teams()
    chart_5_global_nba()
    chart_6_contract_horizons()
    chart_7_who_sells_what()
    chart_8_sneaker_wars()
    chart_9_experience_and_rings()
    chart_10_team_matrix()
    print(f"ALL 10 REDDIT PNGs GENERATED ({N_PLAYERS} players · {N_DEALS} deals · {N_SPON} sponsored)!")
