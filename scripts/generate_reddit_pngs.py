#!/usr/bin/env python3
"""
Generates 6 publication-grade, Reddit-ready (r/nba & r/dataisbeautiful) PNG charts
from the verified 2026-27 NBA Roster (529 players) and Sponsorship Deals (414 deals) datasets.
"""

import json
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
OUT_DIR = os.path.join(REPO_ROOT, "charts")

os.makedirs(OUT_DIR, exist_ok=True)

# Editorial dark-slate palette (high contrast in both Reddit dark & light feeds)
BG = "#0D1117"
PANEL = "#151B23"
BORDER = "#263041"
FG = "#F8FAFC"
MUTED = "#94A3B8"
DIM = "#64748B"
GOLD = "#F59E0B"
BLUE = "#38BDF8"
GREEN = "#10B981"
CORAL = "#F43F5E"
VIOLET = "#A855F7"
CYAN = "#06B6D4"
ORANGE = "#FB923C"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Liberation Sans", "Arial"],
    "text.parse_math": False,
    "axes.edgecolor": BORDER,
    "axes.linewidth": 0.8,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": FG,
    "xtick.color": MUTED,
    "ytick.color": FG,
})

FOOTER_TEXT = "Data: ESPN, Basketball-Reference, NBA.com, Forbes & public endorsement filings · Snapshot Nov 25, 2026 (529 rostered players · 414 tracked deals)"

players = json.load(open(os.path.join(DATA_DIR, "nba_players_2026_27.json"), encoding="utf-8"))
deals = json.load(open(os.path.join(DATA_DIR, "nba_sponsorship_deals.json"), encoding="utf-8"))
pmap = {p["player_id"]: p for p in players}
deals_by_player = defaultdict(list)
for d in deals:
    deals_by_player[d["player_id"]].append(d)


def add_header_footer(fig, kicker, title, subtitle, accent=GOLD, footer=FOOTER_TEXT):
    # Top accent bar
    fig.patches.append(mpatches.Rectangle((0, 0.992), 1.0, 0.008, transform=fig.transFigure, facecolor=accent, edgecolor="none"))
    fig.text(0.045, 0.952, kicker.upper(), fontsize=9.5, fontweight="bold", color=accent, ha="left", va="top")
    fig.text(0.045, 0.922, title, fontsize=19, fontweight="bold", color=FG, ha="left", va="top")
    fig.text(0.045, 0.875, subtitle, fontsize=11, color=MUTED, ha="left", va="top")
    # Footer line & caption
    fig.lines.append(plt.Line2D([0.045, 0.955], [0.052, 0.052], transform=fig.transFigure, color=BORDER, linewidth=0.9))
    fig.text(0.045, 0.033, footer, fontsize=8.5, color=DIM, ha="left", va="center")


def save_chart(fig, filename):
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=200, facecolor=BG)
    plt.close(fig)
    print(f"Saved {filename} ({os.path.getsize(path):,} bytes)")


# ==============================================================================
# CHART 1: RINGS SELL — NBA Champions Share of Rosters vs. Sponsorships by Industry
# ==============================================================================
def chart_1_rings_sell():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · The Championship Endorsement Premium",
        "Rings Sell: Champions Are 14% of Players — But Hold 41% of All Sponsorships",
        "NBA title winners average 4.2× more tracked deals per player (2.27 vs. 0.54) and dominate gambling, wellness, and spirits.",
        accent=GOLD,
    )

    # Top hero strip: 2 horizontal comparison bars (Roster Share vs Deal Share)
    ax_top = fig.add_axes([0.23, 0.72, 0.72, 0.115])
    ax_top.set_facecolor(BG)
    champs_n = sum(1 for p in players if p["nba_titles"] > 0)
    champ_pct = champs_n / len(players) * 100
    c_deals_n = sum(1 for d in deals if pmap[d["player_id"]]["nba_titles"] > 0)
    c_deal_pct = c_deals_n / len(deals) * 100

    labels = ["Share of Tracked Deals\n(414 total)", "Share of NBA Rosters\n(529 total)"]
    vals = [c_deal_pct, champ_pct]
    y_pos = [0, 1]
    ax_top.barh(y_pos, [100, 100], height=0.56, color="#1E293B", edgecolor="none")
    ax_top.barh(y_pos, vals, height=0.56, color=[GOLD, GOLD], edgecolor="none")
    ax_top.set_yticks(y_pos)
    ax_top.set_yticklabels(labels, fontsize=10.5, fontweight="bold", color=FG)
    ax_top.set_xlim(0, 100)
    ax_top.set_xticks([])
    for s in ax_top.spines.values():
        s.set_visible(False)

    ax_top.text(c_deal_pct - 1.5, 0, f"{c_deal_pct:.1f}% Champions ({c_deals_n})", va="center", ha="right", color="#0D1117", fontweight="bold", fontsize=10)
    ax_top.text(c_deal_pct + 1.5, 0, f"{100 - c_deal_pct:.1f}% Non-Champions ({len(deals) - c_deals_n})", va="center", ha="left", color=MUTED, fontsize=9.5)
    ax_top.text(champ_pct + 1.5, 1, f"{champ_pct:.1f}% Champions ({champs_n})  ·  {100 - champ_pct:.1f}% Non-Champions ({len(players) - champs_n})", va="center", ha="left", color=FG, fontweight="bold", fontsize=9.8)

    # Bottom panel: All 13 industries ranked by Champion share
    ax = fig.add_axes([0.28, 0.105, 0.67, 0.56])
    ax.set_facecolor(BG)

    ind_counts = defaultdict(lambda: [0, 0])
    for d in deals:
        ind_counts[d["industry"]][0 if pmap[d["player_id"]]["nba_titles"] > 0 else 1] += 1

    rows = []
    for ind, (c, nc) in ind_counts.items():
        tot = c + nc
        rows.append((ind, c / tot * 100, c, tot))
    rows.sort(key=lambda r: (r[1], r[3]))

    y = np.arange(len(rows))
    pcts = [r[1] for r in rows]
    names = [f"{r[0]}  (n={r[3]})" for r in rows]

    ax.barh(y, [100] * len(rows), height=0.64, color="#1E293B", edgecolor="none")
    bar_colors = [GOLD if p >= 50 else (BLUE if p >= 35 else "#64748B") for p in pcts]
    ax.barh(y, pcts, height=0.64, color=bar_colors, edgecolor="none")

    # Baseline vertical dashed lines: 14.2% roster share & 41.1% overall deal average
    ax.axvline(champ_pct, color=CORAL, linestyle="--", linewidth=1.3, alpha=0.9)
    ax.axvline(c_deal_pct, color=FG, linestyle=":", linewidth=1.2, alpha=0.65)
    ax.text(champ_pct + 0.8, len(rows) - 0.15, f"Roster baseline ({champ_pct:.1f}%)", color=CORAL, fontsize=8.8, fontweight="bold", va="bottom")
    ax.text(c_deal_pct + 0.8, len(rows) - 0.15, f"All-deals avg ({c_deal_pct:.1f}%)", color=MUTED, fontsize=8.8, va="bottom")

    for i, (ind, pct, c, tot) in enumerate(rows):
        txt_col = "#0D1117" if pct >= 28 else FG
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
# CHART 2: THE $400M+ CLUB — Career NBA Earnings vs. 2026-27 Salary (And LeBron's Pay Cut)
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

    # Two side-by-side aligned panels: Left = Career Earnings, Right = 2026-27 Salary
    ax1 = fig.add_axes([0.235, 0.105, 0.42, 0.655])
    ax2 = fig.add_axes([0.695, 0.105, 0.255, 0.655])

    y = np.arange(len(top12))
    careers = [p["career_earnings_usd"] / 1e6 for p in top12]
    curs = [(p["current_salary_usd"] or 0) / 1e6 for p in top12]
    cols = [GOLD if p["nba_titles"] > 0 else BLUE for p in top12]

    # Left panel: Career Earnings
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

    for i, (val, p) in enumerate(zip(careers, top12)):
        ax1.text(val + 8, i, f"${val:.1f}M", va="center", ha="left", fontsize=9.2, fontweight="bold", color=FG)

    # Right panel: 2026-27 Salary
    ax2.set_facecolor(BG)
    sal_cols = [CORAL if p["player_name"] == "LeBron James" else (GREEN if (p["current_salary_usd"] or 0) >= 55e6 else "#64748B") for p in top12]
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

    for i, (val, p) in enumerate(zip(curs, top12)):
        lbl = f"${val:.1f}M"
        if p["player_name"] == "LeBron James":
            lbl += "  ← Vet min w/ PHI!"
            ax2.text(val + 1.8, i, lbl, va="center", ha="left", fontsize=9, fontweight="bold", color=CORAL)
        elif p["player_name"] == "Stephen Curry":
            lbl += " (#1)"
            ax2.text(val + 1.8, i, lbl, va="center", ha="left", fontsize=9, fontweight="bold", color=GREEN)
        else:
            ax2.text(val + 1.8, i, lbl, va="center", ha="left", fontsize=9, color=FG)

    # Legend strip cleanly placed between subtitle and panel titles
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
# CHART 3: INSIDE THE 2026-27 NBA SPONSORSHIP ECONOMY (13 Industries + Top Brands)
# ==============================================================================
def chart_3_sponsorship_industries():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Brand & Industry Landscape",
        "Where NBA Endorsements Actually Go: 414 Deals Across 13 Industries",
        "Footwear, Food & Beverage, and Fashion/Luxury drive 56% of deals — while Prediction Markets & Insurance target top-tier stars.",
        accent=GREEN,
    )

    ax = fig.add_axes([0.265, 0.105, 0.69, 0.72])
    ax.set_facecolor(BG)

    by_ind = defaultdict(list)
    for d in deals:
        by_ind[d["industry"]].append(d)

    # Clean notable brands per industry (all verified present in Dataset 2)
    notable_brands = {
        "Footwear & Apparel": "Nike, Adidas, Jordan Brand, Li-Ning",
        "Food & Beverage": "Gatorade, Sprite, McDonald's, Chipotle",
        "Fashion & Luxury": "Louis Vuitton, Coach, Tissot, BVLGARI",
        "Retail & Collectibles": "Dick's, Fanatics, Foot Locker, Lowe's",
        "Technology & Consumer Electronics": "Google, Beats by Dre, Bose, Meta",
        "Gaming & Media": "2K Sports, PlayStation, Overwatch",
        "Automotive & Aviation": "Toyota, Turkish Airlines, Lucid, Chevy",
        "Financial Services & Banking": "JPMorgan Chase, AmEx, SoFi, Chime",
        "Spirits & Alcohol": "Michelob Ultra, Hennessy, Maker's Mark",
        "Health, Wellness & Personal Care": "CeraVe, Glaukos, Superpower, Journavx",
        "Telecommunications": "AT&T, Xfinity, Verizon",
        "Insurance": "State Farm, Amica, USAA, AAMI",
        "Gambling & Prediction Markets": "Polymarket, Kalshi, FanDuel, PrizePicks",
    }

    rows = []
    for ind, items in by_ind.items():
        n_players = len({x["player_id"] for x in items})
        rows.append((ind, len(items), n_players, notable_brands.get(ind, "")))
    rows.sort(key=lambda r: r[1])

    y = np.arange(len(rows))
    counts = [r[1] for r in rows]
    tot = len(deals)

    colors = []
    for ind, cnt, _, _ in rows:
        if ind == "Footwear & Apparel":
            colors.append(BLUE)
        elif ind == "Food & Beverage":
            colors.append(GREEN)
        elif ind == "Fashion & Luxury":
            colors.append(VIOLET)
        elif ind == "Gambling & Prediction Markets":
            colors.append(CORAL)
        elif ind == "Insurance":
            colors.append(GOLD)
        else:
            colors.append("#475569")

    ax.barh(y, counts, height=0.66, color=colors, edgecolor="none", alpha=0.93)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=10, fontweight="bold", color=FG)
    ax.set_xlim(0, 168)
    ax.grid(axis="x", color=BORDER, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xlabel("Number of Tracked NBA Player Sponsorship Deals", fontsize=9.8, color=MUTED, labelpad=6)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for i, (ind, cnt, n_pl, brands_str) in enumerate(rows):
        pct = cnt / tot * 100
        ax.text(cnt + 2.0, i, f"{cnt} ({pct:.1f}%)  ·  {brands_str}", va="center", ha="left",
                fontsize=8.8, color=FG if cnt >= 25 or ind in ("Gambling & Prediction Markets", "Insurance") else MUTED)

    # Callout box cleanly placed in the wide empty right zone above the bottom bars
    callout = (
        "SPOTLIGHT: EMERGING VERTICALS\n"
        "• Gambling & Prediction Markets (8):\n"
        "  LeBron (Polymarket $15M/yr, ex-DraftKings),\n"
        "  KD (FanDuel, Kalshi), Giannis (Kalshi),\n"
        "  Ant (PrizePicks), Jokić (Superbet)\n"
        "• Insurance (8): State Farm (Flagg, Cade,\n"
        "  Trae, Brook), Amica (Tatum), USAA (Castle)"
    )
    ax.text(
        0.985, 0.34, callout, transform=ax.transAxes,
        fontsize=8.4, color=FG, ha="right", va="bottom", linespacing=1.45,
        bbox=dict(boxstyle="round,pad=0.65", facecolor=PANEL, edgecolor=CORAL, linewidth=1.1),
    )

    save_chart(fig, "03_nba_sponsorship_economy_13_industries.png")


# ==============================================================================
# CHART 4: MOST MARKETABLE ROSTERS IN 2026-27 (Top 15 Teams by Player Sponsorships)
# ==============================================================================
def short_last_name(full_name: str) -> str:
    parts = [p for p in full_name.split() if p not in ("Jr.", "Sr.", "II", "III", "IV", "V")]
    return parts[-1] if parts else full_name


def chart_4_top_sponsored_teams():
    fig = plt.figure(figsize=(12.5, 8.2))
    add_header_footer(
        fig,
        "NBA 2026–27 · Franchise Star Power",
        "Which NBA Rosters Hoard the Most Sponsorship Deals in 2026–27?",
        "After blockbuster 2026 moves (LeBron & Jaylen Brown to Philly; Giannis to Miami), the 76ers top the league with 32 tracked deals.",
        accent=VIOLET,
    )

    ax = fig.add_axes([0.22, 0.105, 0.735, 0.72])
    ax.set_facecolor(BG)

    tm_deals = defaultdict(list)
    for d in deals:
        tm_deals[d["current_team"]].append(d)

    rows = []
    for tm, items in tm_deals.items():
        p_counts = Counter(x["player_name"] for x in items)
        top_stars = ", ".join(f"{short_last_name(n)} ({c})" for n, c in p_counts.most_common(3))
        n_pl = len(p_counts)
        rows.append((tm, len(items), n_pl, top_stars))
    rows.sort(key=lambda r: (r[1], r[2]), reverse=True)
    top15 = list(reversed(rows[:15]))

    y = np.arange(len(top15))
    counts = [r[1] for r in top15]
    bar_cols = [VIOLET if i >= 12 else (BLUE if i >= 8 else "#475569") for i in range(len(top15))]

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
        ax.text(cnt + 0.8, i, f"{cnt} deals ({n_pl} players)  ·  {stars}", va="center", ha="left",
                fontsize=8.8, color=FG if i >= 10 else MUTED)

    save_chart(fig, "04_nba_teams_most_sponsored_rosters.png")


# ==============================================================================
# CHART 5: THE GLOBAL NBA — Top International Nations (Players vs Career Earnings & Deals)
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

    # Top 12 nations by player count (tie-break by career earnings)
    top12_nats = sorted(nat_p.keys(), key=lambda n: (nat_p[n], nat_e[n]), reverse=True)[:12]
    top12_nats = list(reversed(top12_nats))

    cont_col = {"Europe": CYAN, "North America": BLUE, "Oceania": VIOLET, "Africa": GOLD, "Asia": CORAL, "South America": GREEN}

    ax1 = fig.add_axes([0.19, 0.105, 0.25, 0.655])
    ax2 = fig.add_axes([0.48, 0.105, 0.25, 0.655])
    ax3 = fig.add_axes([0.77, 0.105, 0.19, 0.655])

    y = np.arange(len(top12_nats))
    cols = [cont_col.get(nat_cont[n], BLUE) for n in top12_nats]

    # Panel 1: Rostered Players
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

    # Panel 2: Combined Career NBA Earnings ($M)
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

    # Panel 3: Tracked Sponsorship Deals
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
        mpatches.Patch(color=BLUE, label="North America ex-USA (24)"),
        mpatches.Patch(color=GOLD, label="Africa (17)"),
        mpatches.Patch(color=VIOLET, label="Oceania (10)"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.8, labelcolor=MUTED)

    save_chart(fig, "05_global_nba_international_footprint.png")


# ==============================================================================
# CHART 6: THE LONGEST BETS — Lifetime Deals, Mega-Contracts & 2026 Shakeups (Timeline)
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
    status_color = {"Lifetime": GOLD, "Active": GREEN, "Ended": "#64748B"}

    for i, (player, brand, s, e, st, note) in enumerate(horizon_specs):
        col = status_color[st]
        if brand == "Li-Ning" and player == "Stephen Curry":
            col = CORAL
        ax.barh(i, e - s, left=s, height=0.58, color=col, edgecolor="none", alpha=0.92)
        ax.scatter([s], [i], color=FG, s=18, zorder=4)
        if st == "Lifetime":
            ax.text(2037.2, i, "→", va="center", ha="left", color=GOLD, fontsize=12, fontweight="bold")
            ax.text(s + 0.5, i, note, va="center", ha="left", color="#0D1117", fontsize=8.5, fontweight="bold")
        elif e - s >= 7.5:
            ax.text(s + 0.45, i, note, va="center", ha="left", color="#0D1117" if st != "Ended" else FG, fontsize=8.4, fontweight="bold")
        else:
            # Clear the Nov 2026 vertical dashed line cleanly
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
        mpatches.Patch(color="#64748B", label="Ended / Expired"),
    ]
    fig.legend(handles=leg_handles, loc="upper left", bbox_to_anchor=(0.04, 0.848),
               ncol=4, frameon=False, fontsize=8.6, labelcolor=MUTED)

    save_chart(fig, "06_endorsement_contract_horizons.png")


if __name__ == "__main__":
    chart_1_rings_sell()
    chart_2_career_vs_salary()
    chart_3_sponsorship_industries()
    chart_4_top_sponsored_teams()
    chart_5_global_nba()
    chart_6_contract_horizons()
    print("ALL 6 REDDIT PNGs GENERATED!")
