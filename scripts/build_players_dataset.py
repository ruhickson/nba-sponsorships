#!/usr/bin/env python3
"""
Builds Dataset 1: All currently-rostered NBA players (2026-27 season) as of 2026-11-25.

Sources reconciled:
  1. Live ESPN 2026-27 team rosters API (all 30 teams, 529 players)
  2. Live ESPN athlete bio API (career teamHistory for all 529 players)
  3. Basketball-Reference 2026-27 player contracts table (488 standard contracts)
  4. Basketball-Reference 2011-2026 NBA championship playoff rosters (+ official injured champs)
  5. Basketball-Reference individual career salary histories for top 25 veterans & ESPN gap players
  6. Official NBA 2026-27 Opening-Night International Players list (pr.nba.com, 125 players / 43 countries)
"""

import csv
import html as htmllib
import json
import os
import re
import unicodedata
from datetime import date

AS_OF_DATE = date(2026, 11, 25)
RAW_DIR = "/home/antigravity/nba_datasets/raw"
OUT_DIR = "/home/antigravity/nba_datasets"

# Franchise relocation/rename normalization so teams_count reflects distinct NBA franchises
FRANCHISE_NORMALIZE = {
    "Seattle SuperSonics": "Oklahoma City Thunder",
    "New Jersey Nets": "Brooklyn Nets",
    "New Orleans Hornets": "New Orleans Pelicans",
    "Charlotte Bobcats": "Charlotte Hornets",
}

# Official injured NBA champions who remained on the active 15-man championship roster
# without logging playoff minutes (verified against NBA/Wikipedia championship records)
INJURED_OFFICIAL_CHAMPS = {
    "kevon looney": [2017],
    "og anunoby": [2019],
    "nikola topic": [2025],
}

# Verified birth countries / nationalities for the 10 players missing ESPN birthPlace
MISSING_BIRTHPLACE_PATCH = {
    "5242502": ("Israel", "Israel"),           # Ben Saraf
    "4711294": ("Lithuania", "USA"),           # Matas Buzelis (born Chicago, represents Lithuania)
    "4871145": ("Australia", "Australia"),     # Josh Giddey
    "4997528": ("Serbia", "United Kingdom"),   # Nikola Jovic (born Leicester, UK; represents Serbia)
    "5214989": ("Serbia", "Serbia"),           # Bogoljub Markovic
    "5157587": ("Australia", "Australia"),     # Rocco Zikarsky
    "4997538": ("Croatia", "Bosnia & Herzegovina"),  # Karlo Matkovic (born Livno, BiH; represents Croatia)
    "5159925": ("Serbia", "Serbia"),           # Nikola Topic
    "4870562": ("USA", "USA"),                 # Dominick Barlow
    "5217746": ("China", "China"),             # Yang Hansen
}

# Country name standardization
COUNTRY_STANDARDIZE = {
    "United States": "USA",
    "U.S.A.": "USA",
    "England": "United Kingdom",
    "Great Britain": "United Kingdom",
    "Scotland": "United Kingdom",
    "Wales": "United Kingdom",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
    "Republic of the Congo": "Congo",
    "Democratic Republic of the Congo": "Democratic Republic of Congo",
    "DR Congo": "Democratic Republic of Congo",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Czechia": "Czech Republic",
    "The Bahamas": "Bahamas",
    "Saint Lucia": "St. Lucia",
}

# Continent mapping (geographic continent; Turkey & Georgia & Russia & Israel mapped transparently)
CONTINENT_MAP = {
    # North America
    "USA": "North America",
    "Canada": "North America",
    "Bahamas": "North America",
    "Dominican Republic": "North America",
    "Jamaica": "North America",
    "Mexico": "North America",
    "Nicaragua": "North America",
    "Haiti": "North America",
    "Puerto Rico": "North America",
    "St. Lucia": "North America",
    "Antigua and Barbuda": "North America",
    "U.S. Virgin Islands": "North America",
    "Belize": "North America",
    "Cuba": "North America",
    # South America
    "Brazil": "South America",
    "Argentina": "South America",
    "Colombia": "South America",
    "Venezuela": "South America",
    "Uruguay": "South America",
    # Europe
    "France": "Europe",
    "Spain": "Europe",
    "Germany": "Europe",
    "Serbia": "Europe",
    "Slovenia": "Europe",
    "Greece": "Europe",
    "Croatia": "Europe",
    "Bosnia & Herzegovina": "Europe",
    "Lithuania": "Europe",
    "Latvia": "Europe",
    "Estonia": "Europe",
    "Italy": "Europe",
    "Switzerland": "Europe",
    "United Kingdom": "Europe",
    "Netherlands": "Europe",
    "Belgium": "Europe",
    "Russia": "Europe",
    "Ukraine": "Europe",
    "Czech Republic": "Europe",
    "Poland": "Europe",
    "Finland": "Europe",
    "Sweden": "Europe",
    "Austria": "Europe",
    "Portugal": "Europe",
    "Montenegro": "Europe",
    "Georgia": "Europe",
    "Turkey": "Europe",
    "Denmark": "Europe",
    "Hungary": "Europe",
    "Bulgaria": "Europe",
    "Romania": "Europe",
    "North Macedonia": "Europe",
    "Iceland": "Europe",
    "Ireland": "Europe",
    # Africa
    "Nigeria": "Africa",
    "Cameroon": "Africa",
    "Senegal": "Africa",
    "South Sudan": "Africa",
    "Sudan": "Africa",
    "Congo": "Africa",
    "Democratic Republic of Congo": "Africa",
    "Guinea": "Africa",
    "Mali": "Africa",
    "Angola": "Africa",
    "Ivory Coast": "Africa",
    "Cote d'Ivoire": "Africa",
    "Egypt": "Africa",
    "South Africa": "Africa",
    "Ghana": "Africa",
    "Tunisia": "Africa",
    "Cape Verde": "Africa",
    "Central African Republic": "Africa",
    # Asia
    "China": "Asia",
    "Japan": "Asia",
    "Israel": "Asia",
    "South Korea": "Asia",
    "Philippines": "Asia",
    "India": "Asia",
    "Lebanon": "Asia",
    "Taiwan": "Asia",
    "Iran": "Asia",
    # Oceania
    "Australia": "Oceania",
    "New Zealand": "Oceania",
    "Papua New Guinea": "Oceania",
}


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def norm_base(name: str) -> str:
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", norm(name)).strip()
    return re.sub(r"\s+", " ", s)


def std_country(c: str) -> str:
    if not c:
        return ""
    c = c.strip()
    return COUNTRY_STANDARDIZE.get(c, c)


def compute_age(dob_str: str, espn_age):
    if dob_str:
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", dob_str)
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            bday = date(y, mo, d)
            age = AS_OF_DATE.year - bday.year - ((AS_OF_DATE.month, AS_OF_DATE.day) < (bday.month, bday.day))
            return age, f"{y:04d}-{mo:02d}-{d:02d}"
    return espn_age, ""


def load_bref_contracts():
    with open(os.path.join(RAW_DIR, "bref_contracts.html")) as f:
        chtml = f.read()
    m = re.search(r'<table[^>]*id="player-contracts"[^>]*>(.*?)</table>', chtml, re.S)
    by_exact = {}
    by_base = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S):
        if 'data-stat="player"' not in tr or '<th scope="col"' in tr:
            continue
        cells = [
            htmllib.unescape(re.sub(r"<[^>]+>", "", c).strip())
            for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)
        ]
        if len(cells) < 4:
            continue
        pname = cells[1]
        tm = cells[2]
        sal_str = cells[3].replace("$", "").replace(",", "").strip()
        sal = int(sal_str) if sal_str.isdigit() else None
        if sal is None:
            continue
        by_exact.setdefault(norm(pname), []).append((tm, sal))
        by_base.setdefault(norm_base(pname), []).append((tm, sal))
    return by_exact, by_base


def load_nba_intl():
    with open(os.path.join(RAW_DIR, "nba_intl_2026_27.html")) as f:
        ihtml = f.read()
    by_exact = {}
    by_base = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", ihtml, re.S):
        cells = [
            htmllib.unescape(re.sub(r"<[^>]+>", "", c).strip())
            for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)
        ]
        if len(cells) >= 3 and cells[0] != "Country":
            country = std_country(cells[0])
            pname = cells[1].replace("*", "").strip()
            by_exact[norm(pname)] = country
            by_base[norm_base(pname)] = country
    return by_exact, by_base


def load_champions():
    with open(os.path.join(RAW_DIR, "bref_champions.json")) as f:
        champs = json.load(f)
    champ_years = {}
    for yr, info in champs.items():
        for pl in info["playoffs"]:
            champ_years.setdefault(norm_base(pl["name"]), set()).add(int(yr))
    for k, yrs in INJURED_OFFICIAL_CHAMPS.items():
        champ_years.setdefault(k, set()).update(yrs)
    return {k: sorted(v) for k, v in champ_years.items()}


def load_career_patch():
    path = os.path.join(RAW_DIR, "bref_career_salaries_patch.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        data = json.load(f)
    return {norm_base(k): v for k, v in data.items()}


def main():
    with open(os.path.join(RAW_DIR, "espn_rosters.json")) as f:
        rosters = json.load(f)
    with open(os.path.join(RAW_DIR, "espn_bios.json")) as f:
        bios = json.load(f)

    bref_sal_exact, bref_sal_base = load_bref_contracts()
    intl_exact, intl_base = load_nba_intl()
    champ_map = load_champions()
    career_patch = load_career_patch()

    rows = []
    missing_continent = set()

    for p in rosters:
        pid = str(p["id"])
        name = p["fullName"].strip()
        k = norm(name)
        kb = norm_base(name)

        age, dob = compute_age(p.get("dateOfBirth"), p.get("age"))
        pos = (p.get("position") or {}).get("abbreviation") or ""
        cur_team = FRANCHISE_NORMALIZE.get(p["_team_name"], p["_team_name"])
        cur_abbr = p["_team_abbr"]

        # NBA Titles
        title_yrs = champ_map.get(kb, [])
        nba_titles = len(title_yrs)
        nba_title_years = "; ".join(str(y) for y in title_yrs)

        # Teams played for (chronological, distinct NBA franchises)
        th = (bios.get(pid) or {}).get("teamHistory") or []
        # ESPN returns most-recent first; reverse for chronological order
        teams_ordered = []
        for t in reversed(th):
            tname = FRANCHISE_NORMALIZE.get(t["displayName"], t["displayName"])
            if tname not in teams_ordered:
                teams_ordered.append(tname)
        if cur_team not in teams_ordered:
            teams_ordered.append(cur_team)
        teams_played_for = "; ".join(teams_ordered)
        teams_count = len(teams_ordered)

        # Current 2026-27 salary
        bref_entries = bref_sal_exact.get(k) or bref_sal_base.get(kb)
        bref_cur = None
        if bref_entries:
            # Prefer entry matching current team if multiple, else max
            team_matches = [sal for tm, sal in bref_entries if tm.upper() == cur_abbr.upper()]
            bref_cur = max(team_matches) if team_matches else max(sal for _, sal in bref_entries)

        espn_cur = (p.get("contract") or {}).get("salary")
        current_salary = bref_cur if bref_cur else (int(espn_cur) if espn_cur else None)
        contract_type = "Standard" if current_salary else "Two-Way / Undisclosed"

        # Career earnings to date (inclusive of 2026-27 contract)
        patch = career_patch.get(kb)
        if patch and patch.get("career_thru_2026"):
            career_earnings = int(patch["career_thru_2026"]) + (current_salary or 0)
            earnings_source = "Basketball-Reference"
        else:
            # Sum ESPN seasons <= 2026 (deduplicated by season year) + reconciled 2026-27 salary
            espn_by_yr = {}
            for c in p.get("contracts") or []:
                yr = (c.get("season") or {}).get("year")
                sal = c.get("salary")
                if yr and sal and int(yr) <= 2026:
                    espn_by_yr[int(yr)] = max(espn_by_yr.get(int(yr), 0), int(sal))
            pre_2027 = sum(espn_by_yr.values())
            if pre_2027 > 0 or current_salary:
                career_earnings = pre_2027 + (current_salary or 0)
                earnings_source = "ESPN + Basketball-Reference"
            else:
                career_earnings = None
                earnings_source = "Undisclosed (Two-Way / Rookie)"

        # Nationality & Birth Country
        bp_country = std_country((p.get("birthPlace") or {}).get("country") or "")
        espn_cit = std_country(p.get("citizenship") or "")
        nba_intl_country = intl_exact.get(k) or intl_base.get(kb) or ""

        if pid in MISSING_BIRTHPLACE_PATCH:
            patch_nat, patch_bp = MISSING_BIRTHPLACE_PATCH[pid]
            if not bp_country:
                bp_country = patch_bp
            nationality = nba_intl_country or patch_nat
        else:
            # Official NBA 2026-27 international list is authoritative for sporting nationality;
            # otherwise fall back to ESPN citizenship, then birthplace country
            nationality = nba_intl_country or espn_cit or bp_country or "USA"

        nationality = std_country(nationality)
        birth_country = std_country(bp_country or nationality)

        continent = CONTINENT_MAP.get(nationality, "")
        if not continent:
            missing_continent.add(nationality)

        exp_years = (p.get("experience") or {}).get("years")
        debut_year = p.get("debutYear") or ""

        rows.append({
            "player_id": pid,
            "player_name": name,
            "age": age,
            "date_of_birth": dob,
            "position": pos,
            "current_team": cur_team,
            "current_team_abbr": cur_abbr,
            "nba_titles": nba_titles,
            "nba_title_years": nba_title_years,
            "teams_played_for": teams_played_for,
            "teams_count": teams_count,
            "current_salary_usd": current_salary if current_salary is not None else "",
            "salary_contract_type": contract_type,
            "career_earnings_usd": career_earnings if career_earnings is not None else "",
            "nationality": nationality,
            "birth_country": birth_country,
            "continent": continent,
            "experience_years": exp_years if exp_years is not None else "",
            "debut_year": debut_year,
            "earnings_source": earnings_source,
        })

    # Sort by current_salary_usd descending, then career_earnings_usd descending, then name
    rows.sort(
        key=lambda r: (
            -(r["current_salary_usd"] if isinstance(r["current_salary_usd"], int) else -1),
            -(r["career_earnings_usd"] if isinstance(r["career_earnings_usd"], int) else -1),
            r["player_name"],
        )
    )

    csv_path = os.path.join(OUT_DIR, "nba_players_2026_27.csv")
    json_path = os.path.join(OUT_DIR, "nba_players_2026_27.json")

    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(rows)} players to {csv_path} and {json_path}")
    if missing_continent:
        print("WARNING: Unmapped continents for:", missing_continent)

    # Print summary stats
    champs_count = sum(1 for r in rows if r["nba_titles"] > 0)
    with_sal = sum(1 for r in rows if isinstance(r["current_salary_usd"], int))
    with_career = sum(1 for r in rows if isinstance(r["career_earnings_usd"], int))
    conts = {}
    for r in rows:
        conts[r["continent"]] = conts.get(r["continent"], 0) + 1
    nats = len({r["nationality"] for r in rows})
    print(f"Champions: {champs_count} | Standard salaries: {with_sal}/{len(rows)} | Career earnings: {with_career}/{len(rows)} | Distinct nationalities: {nats}")
    print("Continents:", sorted(conts.items(), key=lambda x: -x[1]))
    print("\nTop 10 by Career Earnings:")
    for r in sorted(rows, key=lambda x: -(x["career_earnings_usd"] if isinstance(x["career_earnings_usd"], int) else -1))[:10]:
        print(f"  {r['player_name']:24s} ({r['current_team_abbr']:3s}) age={r['age']} titles={r['nba_titles']} teams={r['teams_count']} cur=${r['current_salary_usd'] or 0:>11,} career=${r['career_earnings_usd'] or 0:>12,} [{r['nationality']} / {r['continent']}]")


if __name__ == "__main__":
    main()
