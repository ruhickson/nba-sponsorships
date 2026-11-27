# NBA 2026–27 Roster & Sponsorship Datasets

Snapshot date: **November 25, 2026** (2026–27 NBA Regular Season).

Two relational datasets joined via `player_id` (ESPN Athlete ID), exported in both CSV and JSON formats under `data/`, paired with a standalone interactive analytics dashboard in `index.html` (open locally or enable GitHub Pages to view).

---

## Interactive Dashboard: `index.html`

Self-contained HTML/Tailwind/Canvas/SVG dashboard with all 529 players and 448 sponsorship deals embedded:
- Global cross-filtering (search, continent, team, industry, championship status, tracked deals)
- Overview & Earnings scatter explorer, Top-15 leaderboards, global geography, age cohorts, and team mobility
- Sponsorship Intelligence (13 industries, top brands, champion/international splits, launch timeline, and contract horizons)
- Sortable, exportable Players & Deals tables + slide-over Player Profile drawer

## r/nba 10-Chart Prototype Studio: `prototype-studio.html`

Standalone browser-ready prototype dashboard for testing `/r/nba` visual themes across **10 NBA data stories** before batch-rendering final PNGs:
- **4 live visual presets:** `r/nba Dark Mode`, `r/nba Classic Light`, `Hardwood Editorial`, and `Broadcast Neon`
- **10 data stories:** Rings Sell (#1), The $400M+ Club (#2), 13 Sponsorship Industries (#3), Most-Sponsored Rosters (#4), Global NBA (#5), Endorsement Contract Horizons (#6), Who Sells What? Wealth by Industry (#7), 2026–27 Sneaker Wars (#8), Tenure vs. Rings & The Survivorship Flip (#9), and the 30-Team Age/Payroll/Deals Matrix (#10)
- **Reddit workflow tools:** Toggleable `/r/nba` `[OC]` post-card frame, 1-col Feed vs. 2-col Studio Grid layout, one-click Reddit title copy, selection spec copy, and instant client-side `Test PNG ↓` exports

## Reddit-Ready PNG Charts: `charts/`

High-DPI (2500×1640, 200 DPI) Matplotlib PNGs generated via `scripts/generate_reddit_pngs.py` (`01_rings_sell_champion_premium.png` through `10_nba_30_team_matrix_age_payroll_deals.png`).

---

## Dataset 1: `data/nba_players_2026_27.csv` / `.json`

Covers **all 529 currently-rostered NBA players** across all 30 franchises.

### Schema (20 columns)

| Column | Type | Description |
|---|---|---|
| `player_id` | string | Unique primary key (ESPN Athlete ID) for joining to Dataset 2 |
| `player_name` | string | Player full name |
| `age` | integer | Exact age as of 2026-11-25 |
| `date_of_birth` | string | `YYYY-MM-DD` |
| `position` | string | Position abbreviation (`PG`, `SG`, `SF`, `PF`, `C`) |
| `current_team` | string | Current 2026–27 NBA franchise |
| `current_team_abbr` | string | Current team abbreviation |
| `nba_titles` | integer | Official NBA Championships won (75 active champions across the league) |
| `nba_title_years` | string | Semicolon-separated championship years (e.g., `2012; 2013; 2016; 2020`) |
| `teams_played_for` | string | Chronological, semicolon-separated list of distinct NBA franchises played for (relocated/renamed franchises normalized, e.g., Seattle SuperSonics → Oklahoma City Thunder) |
| `teams_count` | integer | Count of distinct NBA franchises played for |
| `current_salary_usd` | integer | 2026–27 NBA salary in USD (449/529 standard contracts; blank for Two-Way/undisclosed contracts) |
| `salary_contract_type` | string | `Standard` or `Two-Way / Undisclosed` |
| `career_earnings_usd` | integer | Cumulative NBA salary earned to date, inclusive of 2026–27 (464/529 players) |
| `nationality` | string | Sporting nationality (authoritative NBA 2026–27 opening-night international roster list + verified citizenship/birthplace) |
| `birth_country` | string | Country of birth (retained separately where birthplace differs from sporting nationality) |
| `continent` | string | Geographic continent (`North America`, `Europe`, `Africa`, `Oceania`, `Asia`, `South America`) |
| `experience_years` | integer | Seasons of NBA experience |
| `debut_year` | integer | First NBA season year (where recorded by ESPN) |
| `earnings_source` | string | Provenance of career earnings calculation |

### Sources & Methodology
- **Rosters & Bios**: Live ESPN NBA Team Rosters API & Athlete Bio API (all 30 teams, 529 players).
- **2026–27 Salaries**: Basketball-Reference `contracts/players.html` (prioritized for live 2026–27 signed contracts and combined waived/stretched + active pay), with ESPN contract fallback.
- **Career Earnings**: Basketball-Reference individual career salary histories verified for top 25 veterans and all players with ESPN interior-year gaps; reconciled ESPN historical contracts + 2026–27 contract for the remainder. (Early Two-Way / G-League seasons are typically excluded from standard contract ledgers.)
- **NBA Titles**: Basketball-Reference 2011–2026 championship playoff rosters plus official injured-on-active-roster champions (Kevon Looney 2017, OG Anunoby 2019, Nikola Topić 2025).
- **Nationalities**: Official NBA 2026–27 Opening-Night International Players release (`pr.nba.com`, 125 international players across 43 countries) reconciled with ESPN birthplace/citizenship records.

---

## Dataset 2: `data/nba_sponsorship_deals.csv` / `.json`

Covers **448 verified sponsorship & endorsement deals** across **129 currently-rostered NBA players** and **282 distinct brands**, categorized into **13 standardized industries**.

### Schema (14 columns)

| Column | Type | Description |
|---|---|---|
| `deal_id` | string | Unique deal identifier (`DEAL-0001` – `DEAL-0448`) |
| `player_id` | string | Foreign key joining cleanly to `nba_players_2026_27.csv` (100% referential integrity) |
| `player_name` | string | Player full name |
| `current_team` | string | Current 2026–27 NBA franchise |
| `brand` | string | Sponsor / partner brand name (deduplicated & standardized) |
| `industry` | string | One of 13 standardized industries (see below) |
| `sub_industry` | string | Granular vertical (e.g., `Signature Sneakers`, `Prediction Market`, `Home & Auto Insurance`) |
| `deal_type` | string | Partnership structure (`Signature Shoe Deal`, `Brand Ambassador`, `Equity Partner / Endorsement`, `Ad Campaign`, `Founder / Own Brand`, etc.) |
| `start_date` | string | Start year or month (`YYYY` or `YYYY-MM`, populated for 380/414 deals) |
| `end_date` | string | Known end date, `Lifetime`, or honestly marked `Undisclosed (Ongoing)` / `Undisclosed` where contract term is private |
| `deal_status` | string | `Active`, `Lifetime`, `Ended / Former`, or `Historical / Status Unconfirmed` |
| `reported_value_notes` | string | Publicly reported financial terms, equity stakes, or campaign context |
| `source` | string | Verifiable source URL |
| `data_tier` | string | `Curated / Multi-Source Verified` vs `Public Endorsement Directory` |

### Standardized Industries (13)
1. `Footwear & Apparel` (90)
2. `Food & Beverage` (80)
3. `Fashion & Luxury` (64)
4. `Retail & Collectibles` (43)
5. `Technology & Consumer Electronics` (30)
6. `Gaming & Media` (21)
7. `Automotive & Aviation` (20)
8. `Financial Services & Banking` (17)
9. `Spirits & Alcohol` (13)
10. `Health, Wellness & Personal Care` (11)
11. `Telecommunications` (9)
12. `Gambling & Prediction Markets` (8)
13. `Insurance` (8)

### Reproducibility
Rebuild & chart scripts are stored in `scripts/`:
- `scripts/build_players_dataset.py`
- `scripts/curated_sponsorships.py`
- `scripts/build_sponsorships_dataset.py`
- `scripts/generate_reddit_pngs.py`
