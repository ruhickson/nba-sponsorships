#!/usr/bin/env python3
"""
Builds Dataset 2: NBA Player Sponsorship & Endorsement Deals (joined to Dataset 1 via player_id).

Merges:
  1. Curated, source-verified 2024-2026 deals from curated_sponsorships.py (Forbes 2026,
     Sole Retriever 2026-27 signature shoe directory, The Guardian, Marketing Dive/Brew,
     Adweek, LA Times, official press releases)
  2. Publicly rendered endorsement records from BookingAgentInfo (bai_public_endorsements.json)
     covering 100+ rostered NBA players, deduplicated cleanly against curated deals.
"""

import csv
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(__file__))
from curated_sponsorships import CURATED_DEALS

RAW_DIR = "/home/antigravity/nba_datasets/raw"
OUT_DIR = "/home/antigravity/nba_datasets"

MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}

BRAND_NORMALIZE_DISPLAY = {
    "google": "Google",
    "nike": "Nike",
    "adidas": "Adidas",
    "puma": "PUMA",
    "anta": "ANTA",
    "li-ning": "Li-Ning",
    "under armour": "Under Armour",
    "new balance": "New Balance",
    "jordan": "Jordan Brand",
    "jordan brand": "Jordan Brand",
    "air jordan": "Jordan Brand",
    "skechers": "Skechers",
    "reebok": "Reebok",
    "converse": "Converse",
    "361": "361°",
    "361 degrees": "361°",
    "361°": "361°",
    "at&t": "AT&T",
    "gatorade": "Gatorade",
    "sprite": "Sprite",
    "pepsi": "PepsiCo",
    "pepsico": "PepsiCo",
    "mcdonalds": "McDonald's",
    "mcdonald's": "McDonald's",
    "tissot": "Tissot",
    "louis vuitton": "Louis Vuitton",
    "beats": "Beats by Dre",
    "beats by dre": "Beats by Dre",
    "beats electronics": "Beats by Dre",
    "draftkings": "DraftKings",
    "fanduel": "FanDuel",
    "prizepicks": "PrizePicks",
    "polymarket": "Polymarket",
    "kalshi": "Kalshi",
    "betmgm": "BetMGM",
    "state farm": "State Farm",
    "state farm insurance": "State Farm",
    "amica": "Amica Mutual Insurance",
    "amica mutual insurance": "Amica Mutual Insurance",
    "stanley": "Stanley",
    "stanley 1913": "Stanley",
    "adidas originals": "Adidas",
    "kristapsporzingis.myshopify.com": "Kristaps Porzingis Official Merch",
    "chase": "JPMorgan Chase",
    "jpmorgan chase": "JPMorgan Chase",
    "sofi": "SoFi",
    "skims": "SKIMS",
    "h-e-b": "H-E-B",
    "heb": "H-E-B",
    "fanatics": "Fanatics",
    "2k": "2K Sports",
    "2k sports": "2K Sports",
    "nba 2k": "2K Sports",
    "playstation": "PlayStation",
    "sony playstation": "PlayStation",
    "chipotle": "Chipotle",
    "chipotle mexican grill": "Chipotle",
    "lowe's": "Lowe's",
    "lowes": "Lowe's",
    "foot locker": "Foot Locker",
    "dick's sporting goods": "Dick's Sporting Goods",
    "dicks sporting goods": "Dick's Sporting Goods",
    "subway": "Subway",
    "wingstop": "Wingstop",
    "raising cane's": "Raising Cane's",
    "taco bell": "Taco Bell",
    "carmax": "CarMax",
    "toyota": "Toyota",
    "hyundai": "Hyundai",
    "kia": "Kia",
    "cerave": "CeraVe",
    "hennessy": "Hennessy",
    "michelob ultra": "Michelob Ultra",
    "bape": "BAPE (A Bathing Ape)",
    "bape (a bathing ape)": "BAPE (A Bathing Ape)",
    "overwatch": "Overwatch (Blizzard Entertainment)",
    "overwatch (blizzard entertainment)": "Overwatch (Blizzard Entertainment)",
    "just salad": "Just Salad",
    "gopuff": "Gopuff",
    "rakuten": "Rakuten",
    "coach": "Coach",
    "levi's": "Levi's",
    "levis": "Levi's",
    "rimowa": "Rimowa",
    "canada goose": "Canada Goose",
    "ysl beauty": "YSL Beauty",
    "stanley": "Stanley",
    "ruffles": "Ruffles",
    "powerade": "Powerade",
    "panini": "Panini",
    "panini america": "Panini",
    "tissot": "Tissot",
    "oakley": "Oakley",
    "crocs": "Crocs",
    "new era": "New Era",
    "t-mobile": "T-Mobile",
    "verizon": "Verizon",
    "samsung": "Samsung",
    "jbl": "JBL",
    "bose": "Bose",
    "hyperice": "Hyperice",
    "therabody": "Therabody",
    "whoop": "WHOOP",
    "cash app": "Cash App",
    "coinbase": "Coinbase",
    "chime": "Chime",
    "american express": "American Express",
    "visa": "Visa",
    "mastercard": "Mastercard",
    "uber eats": "Uber Eats",
    "doordash": "DoorDash",
    "popeyes": "Popeyes",
    "starbucks": "Starbucks",
    "red bull": "Red Bull",
    "monster energy": "Monster Energy",
    "bodyarmor": "BODYARMOR",
    "celsius": "CELSIUS",
    "oreo": "Oreo",
    "trolli": "Trolli",
    "pringles": "Pringles",
    "mountain dew": "Mountain Dew",
    "starry": "Starry",
    "doritos": "Doritos",
    "little caesars": "Little Caesars",
    "papa john's": "Papa John's",
    "wendy's": "Wendy's",
    "burger king": "Burger King",
    "kfc": "KFC",
    "shake shack": "Shake Shack",
    "dunkin'": "Dunkin'",
    "dunkin": "Dunkin'",
    "gucci": "Gucci",
    "dior": "Dior",
    "prada": "Prada",
    "balenciaga": "Balenciaga",
    "burberry": "Burberry",
    "ralph lauren": "Ralph Lauren",
    "tommy hilfiger": "Tommy Hilfiger",
    "hugo boss": "Hugo Boss",
    "boss": "Hugo Boss",
    "calvin klein": "Calvin Klein",
    "tag heuer": "TAG Heuer",
    "hublot": "Hublot",
    "audemars piguet": "Audemars Piguet",
    "tiffany & co.": "Tiffany & Co.",
    "cartier": "Cartier",
    "breitling": "Breitling",
    "old spice": "Old Spice",
    "degree": "Degree",
    "gillette": "Gillette",
    "dove": "Dove",
    "dove men+care": "Dove Men+Care",
    "manscaped": "MANSCAPED",
    "call of duty": "Call of Duty",
    "ea sports": "EA Sports",
    "fortnite": "Fortnite",
    "xbox": "Xbox",
    "nintendo": "Nintendo",
    "espn": "ESPN",
    "amazon": "Amazon",
    "walmart": "Walmart",
    "target": "Target",
    "best buy": "Best Buy",
    "home depot": "The Home Depot",
    "the home depot": "The Home Depot",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def norm_base(s: str) -> str:
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", norm(s)).strip()
    return re.sub(r"\s+", " ", s)


def brand_key(b: str) -> str:
    b_clean = b.strip()
    b_low = b_clean.lower()
    if b_low in BRAND_NORMALIZE_DISPLAY:
        b_clean = BRAND_NORMALIZE_DISPLAY[b_low]
    return norm(b_clean)


def clean_brand_name(b: str) -> str:
    b = b.strip()
    if b.lower() in BRAND_NORMALIZE_DISPLAY:
        return BRAND_NORMALIZE_DISPLAY[b.lower()]
    # Fix ALL CAPS brand names if longer than 4 chars and not an acronym
    if b.isupper() and len(b) > 4 and " " in b:
        return b.title()
    return b


def parse_bai_date(date_str: str) -> str:
    if not date_str:
        return ""
    s = date_str.strip()
    # e.g. "April, 2026" or "April 2026"
    m = re.match(r"([A-Za-z]+),?\s*(\d{4})", s)
    if m:
        mo = MONTHS.get(m.group(1).lower())
        if mo:
            return f"{m.group(2)}-{mo}"
        return m.group(2)
    m2 = re.search(r"(\d{4})", s)
    return m2.group(1) if m2 else ""


def map_industry(brand: str, cat_path: str):
    """Map BookingAgentInfo category_path & brand name into standardized 13-industry taxonomy."""
    b = brand.lower()
    c = (cat_path or "").lower()

    # Brand-specific overrides for precision
    if any(k in b for k in ["nike", "jordan", "adidas", "puma", "new balance", "under armour",
                            "anta", "li-ning", "skechers", "reebok", "converse", "361",
                            "peak", "rigorer", "741", "stria", "hoka", "asics", "salomon",
                            "vans", "brooks", "on running", "athletic propulsion", "apl",
                            "crossover culture", "fabletics", "alo yoga", "lululemon",
                            "mitchell & ness", "champion", "starter", "gymshark"]) or b == "fvv":
        return "Footwear & Apparel", (cat_path.split(">")[-1].strip() if cat_path else "Athletic Footwear & Apparel")

    if any(k in b for k in ["draftkings", "fanduel", "prizepicks", "betmgm", "polymarket",
                            "kalshi", "superbet", "underdog", "sleeper", "caesars sportsbook",
                            "espn bet", "betrivers", "bet365", "stake", "hard rock bet"]):
        return "Gambling & Prediction Markets", "Sports Betting / Fantasy"

    if any(k in b for k in ["state farm", "amica", "geico", "progressive", "allstate",
                            "nationwide", "liberty mutual", "usaa", "travelers", "aflac",
                            "metlife", "massmutual", "new york life", "prudential",
                            "kaiser permanente", "aami"]):
        return "Insurance", (cat_path.split(">")[-1].strip() if cat_path else "Insurance")

    if any(k in b for k in ["chase", "jpmorgan", "sofi", "cash app", "coinbase", "crypto.com",
                            "chime", "american express", "amex", "visa", "mastercard",
                            "bank of america", "wells fargo", "citi", "capital one",
                            "robinhood", "venmo", "paypal", "klarna", "affirm", "aspiration",
                            "goldman sachs", "charles schwab", "fidelity", "webull", "credit karma",
                            "experian", "turbotax", "intuit", "discover", "ally", "us bank", "pnc",
                            "wellby financial", "square", "bmo", "frost bank", "amerant bank"]):
        return "Financial Services & Banking", (cat_path.split(">")[-1].strip() if cat_path else "Financial Services")

    if any(k in b for k in ["hennessy", "cognac", "frapin", "michelob", "bud light", "budweiser", "coors", "corona",
                            "modelo", "heineken", "stella artois", "patron", "casamigos",
                            "lobos", "cincoro", "don julio", "clase azul", "absolut", "grey goose",
                            "ciroc", "jameson", "jack daniel", "johnnie walker", "crown royal",
                            "moet", "veuve clicquot", "maker's mark", "silver oak", "wine", "vodka",
                            "tequila", "whiskey", "bourbon", "beer", "brewing", "brewery", "seltzer",
                            "white claw", "high noon", "1800 tequila", "espolon"]) or re.search(r"\b(gin|rum)\b", b):
        return "Spirits & Alcohol", (cat_path.split(">")[-1].strip() if cat_path else "Alcoholic Beverages")

    if any(k in b for k in ["at&t", "verizon", "t-mobile", "xfinity", "comcast", "boost mobile",
                            "cricket wireless", "mint mobile", "spectrum", "cox communications"]):
        return "Telecommunications", "Telecom & Wireless"

    if any(k in b for k in ["2k", "playstation", "xbox", "nintendo", "ea sports", "overwatch",
                            "blizzard", "activision", "call of duty", "fortnite", "epic games",
                            "riot games", "twitch", "youtube", "netflix", "disney", "hulu",
                            "espn", "wondery", "spotify", "siriusxm", "paramount", "peacock",
                            "max", "hbo", "audible", "faze", "100 thieves", "logitech g",
                            "razer", "hyperx", "scuf", "gamestop", "roblox", "minecraft",
                            "ballislife", "boxed.gg"]):
        return "Gaming & Media", (cat_path.split(">")[-1].strip() if cat_path else "Gaming & Entertainment")

    if any(k in b for k in ["louis vuitton", "dior", "gucci", "prada", "coach", "rimowa",
                            "tissot", "tag heuer", "hublot", "audemars piguet", "rolex",
                            "omega", "breitling", "panerai", "cartier", "tiffany", "bulgari", "bvlgari",
                            "burberry", "balenciaga", "versace", "armani", "fendi", "givenchy",
                            "saint laurent", "ysl", "moncler", "canada goose", "skims", "levi",
                            "ralph lauren", "tommy hilfiger", "hugo boss", "calvin klein",
                            "bape", "kith", "fear of god", "off-white", "supreme", "rhude",
                            "amiri", "oakley", "ray-ban", "warby parker", "new era", "crocs",
                            "ugg", "timberland", "true religion", "american eagle", "hollister",
                            "abercrombie", "gap", "old navy", "express", "mens wearhouse",
                            "indochino", "untuckit", "vuori", "rhone", "stance", "psd",
                            "ethika", "hanes", "fruit of the loom", "jockey", "meundies",
                            "bath & body", "sephora", "valentino", "dolce", "bottega", "celine",
                            "black samurai", "porzingis official merch", "american tall", "kenzo"]):
        return "Fashion & Luxury", (cat_path.split(">")[-1].strip() if cat_path else "Fashion & Luxury")

    # Category path rules (NOTE: check non-alcoholic BEFORE alcoholic!)
    if any(k in c for k in ["insurance"]):
        return "Insurance", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["gambling", "betting", "casino", "fantasy sports", "lottery"]):
        return "Gambling & Prediction Markets", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["footwear", "sneaker", "sportswear", "athletic apparel", "sporting goods"]):
        if "retail" in c or "store" in c:
            return "Retail & Collectibles", cat_path.split(">")[-1].strip()
        return "Footwear & Apparel", cat_path.split(">")[-1].strip()
    if "non-alcoholic" in c or any(k in c for k in ["food", "beverage", "drink", "restaurant", "snack", "coffee",
                            "candy", "grocery", "fast food", "dining", "pizza", "burger",
                            "nutrition", "protein", "water", "soda", "tea", "ice cream",
                            "cereal", "chocolate", "delivery", "supermarket", "milk", "juice"]):
        if "alcoholic beverages" not in c:
            return "Food & Beverage", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["alcoholic beverages", "beer", "wine", "spirits", "liquor"]):
        return "Spirits & Alcohol", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["fashion", "apparel", "clothing", "luxury", "watch", "jewelry",
                            "eyewear", "sunglasses", "accessories", "luggage", "handbag",
                            "fragrance", "beauty", "cosmetics", "underwear", "streetwear"]):
        return "Fashion & Luxury", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["finance", "banking", "credit", "fintech", "crypto", "investment",
                            "payment", "accounting", "tax", "bank"]):
        return "Financial Services & Banking", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["telecom", "wireless", "mobile carrier", "internet service"]):
        return "Telecommunications", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["gaming", "video game", "media", "streaming", "entertainment",
                            "music", "podcast", "publishing", "broadcast", "film", "tv"]):
        return "Gaming & Media", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["auto", "car", "vehicle", "tire", "airline", "aviation", "motors", "mobility"]):
        return "Automotive & Aviation", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["health", "wellness", "medical", "pharma", "personal care",
                            "skincare", "skin care", "mens skin", "grooming", "hygiene", "deodorant", "shaving",
                            "fitness", "supplement", "vitamin", "dental", "oral care", "sleep", "medication"]):
        return "Health, Wellness & Personal Care", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["tech", "electronic", "software", "computer", "audio", "headphone",
                            "speaker", "phone", "online service", "gadget", "wearable",
                            "hardware", "cloud"]) or re.search(r"\b(ai|app|apps)\b", c):
        return "Technology & Consumer Electronics", cat_path.split(">")[-1].strip()
    if any(k in c for k in ["retail", "e-commerce", "collectible", "trading card", "memorabilia",
                            "furniture", "home", "mattress", "appliance", "store", "shopping",
                            "travel", "hotel", "hospitality", "marketplace", "office and school"]):
        return "Retail & Collectibles", cat_path.split(">")[-1].strip()

    # Secondary brand heuristics if category path was generic
    if any(k in b for k in ["gatorade", "sprite", "pepsi", "coca-cola", "coke", "mcdonald",
                            "chipotle", "subway", "wingstop", "wendy", "taco bell", "popeyes",
                            "raising cane", "little caesars", "papa john", "domino", "starbucks",
                            "dunkin", "red bull", "monster", "bodyarmor", "celsius", "barcode",
                            "coco5", "ruffles", "doritos", "lays", "pringles", "oreo", "trolli",
                            "hershey", "reeses", "snickers", "skittles", "kellogg", "general mills",
                            "wheaties", "quaker", "kind", "clif", "muscle milk", "optimum",
                            "uber eats", "doordash", "grubhub", "instacart", "gopuff", "salad",
                            "coffee", "tea", "water", "juice", "soda", "pizza", "burger", "grill",
                            "chicken", "steak", "kitchen", "bakery", "foods", "snacks", "candy",
                            "drinks", "beverage", "hydration", "electrolyte", "protein", "bar"]) or b == "x2":
        return "Food & Beverage", (cat_path.split(">")[-1].strip() if cat_path else "Food & Beverage")

    if any(k in b for k in ["toyota", "honda", "ford", "chevy", "chevrolet", "gmc", "kia",
                            "hyundai", "nissan", "mercedes", "bmw", "audi", "porsche", "lexus",
                            "jeep", "dodge", "ram", "subaru", "volkswagen", "tesla", "rivian",
                            "lucid", "michelin", "goodyear", "bridgestone", "carmax", "autozone",
                            "delta", "united", "american airlines", "southwest", "jetblue", "airways",
                            "airlines", "wheels up", "netjets", "easterns automotive", "neste"]):
        return "Automotive & Aviation", (cat_path.split(">")[-1].strip() if cat_path else "Automotive & Mobility")

    if any(k in b for k in ["panini", "topps", "fanatics", "upper deck", "stockx", "goat",
                            "ebay", "foot locker", "champs", "hibbett", "dick's", "walmart",
                            "target", "amazon", "lowe's", "home depot", "ikea", "wayfair",
                            "airbnb", "marriott", "hilton", "expedia", "booking", "stanley",
                            "yeti", "wilson", "spalding", "rakuten", "momento", "infinite objects",
                            "flexispot"]):
        return "Retail & Collectibles", (cat_path.split(">")[-1].strip() if cat_path else "Retail & Collectibles")

    if any(k in b for k in ["beats", "apple", "google", "samsung", "sony", "bose", "jbl",
                            "skullcandy", "sonos", "hyperice", "therabody", "whoop", "oura",
                            "garmin", "fitbit", "meta", "microsoft", "intel", "nvidia", "hp",
                            "dell", "lenovo", "lg", "tcl", "hisense", "vizio", "roku", "ring",
                            "gopro", "canon", "nikon", "linkedin", "trufan", "paycom"]):
        return "Technology & Consumer Electronics", (cat_path.split(">")[-1].strip() if cat_path else "Tech & Software")

    if any(k in b for k in ["cerave", "dove", "degree", "old spice", "gillette", "harry's",
                            "nivea", "neutrogena", "cetaphil", "axe", "secret", "colgate",
                            "crest", "oral-b", "listerine", "invisalign", "calm", "headspace",
                            "peloton", "tonal", "mirror", "equinox", "planet fitness", "la fitness",
                            "gnc", "vitamin", "athletic greens", "ag1", "liquid i.v.", "pedialyte",
                            "icy hot", "biofreeze", "aleve", "advil", "tylenol", "theragun",
                            "leef brands"]):
        return "Health, Wellness & Personal Care", (cat_path.split(">")[-1].strip() if cat_path else "Health & Personal Care")

    sub = cat_path.split(">")[-1].strip() if cat_path else "General Sponsorship"
    return "Other / Sports & Lifestyle", sub


def main():
    with open(os.path.join(OUT_DIR, "nba_players_2026_27.json"), encoding="utf-8") as f:
        players = json.load(f)

    # Index players by normalized name and base name
    p_by_exact = {norm(p["player_name"]): p for p in players}
    p_by_base = {norm_base(p["player_name"]): p for p in players}
    p_by_id = {str(p["player_id"]): p for p in players}

    def find_player(name: str):
        return p_by_exact.get(norm(name)) or p_by_base.get(norm_base(name))

    deals = []
    seen = set()  # (player_id, brand_key, deal_status_group) -> allow Ended + Active for same brand if needed? Usually distinct brand per player, except e.g. none

    # 1. Ingest curated deals first (highest richness & precision)
    skipped_curated = []
    for row in CURATED_DEALS:
        (pname, brand, industry, sub_ind, deal_type, start_date, end_date,
         status, notes, source) = row
        p = find_player(pname)
        if not p:
            skipped_curated.append((pname, brand))
            continue
        pid = str(p["player_id"])
        bdisp = clean_brand_name(brand)
        bkey = brand_key(bdisp)
        dedup_key = (pid, bkey)
        seen.add(dedup_key)
        deals.append({
            "player_id": pid,
            "player_name": p["player_name"],
            "current_team": p["current_team"],
            "brand": bdisp,
            "industry": industry,
            "sub_industry": sub_ind,
            "deal_type": deal_type,
            "start_date": start_date,
            "end_date": end_date,
            "deal_status": status,
            "reported_value_notes": notes,
            "source": source,
            "data_tier": "Curated / Multi-Source Verified",
        })

    if skipped_curated:
        print("Skipped curated (not currently rostered):", skipped_curated)

    # 2. Ingest publicly rendered BookingAgentInfo records for 111 NBA players
    def extract_summary_brands(summary: str):
        brands = []
        if not summary:
            return brands
        # Pattern 1: "most recent brand deal, with X (Month YYYY), was covered" OR "'s deal with X (Month YYYY) was covered"
        m1 = re.search(
            r"(?:most recent brand deal,\s+with|'s deal with)\s+(.+?)\s*(?:\(([A-Za-z]+ \d{4}|\d{4})\))?(?:,\s*was covered|\s+was covered)",
            summary,
        )
        if m1:
            brands.append((m1.group(1).strip(), m1.group(2) or ""))

        # Pattern 2: "has one brand deal on record, with X(, from Month YYYY)?"
        m_one = re.search(
            r"has one brand deal on record,\s+with\s+(.+?)(?:,\s+from\s+([A-Za-z]+ \d{4}|\d{4}))?(?:\.\s|\.$)",
            summary,
        )
        if m_one:
            brands.append((m_one.group(1).strip(), m_one.group(2) or ""))
            return brands

        # Pattern 3: "Other deals on record include ..." / "The most recent deals include ..." / "Deals on record include ..." / "The deals are with ..."
        m2 = re.search(
            r"(?:Other deals on record include|The most recent deals include|Deals on record include|Their deals on record include|The deals are with)\s+(.+?)(?:\.\s|\.$)",
            summary,
        )
        if m2:
            part = m2.group(1).strip()
            # Protect brand names containing " and " or " & " only when preceded by comma or standard split
            # Split on ", " and final " and " (avoid splitting inside e.g. "BAPE (A Bathing Ape)")
            items = re.split(r",\s+(?![^()]*\))|\s+and\s+(?![^()]*\))", part)
            for it in items:
                it = it.strip()
                if not it:
                    continue
                bm = re.match(r"^(.+?)\s*\(([A-Za-z]+ \d{4}|\d{4})\)$", it)
                if bm:
                    brands.append((bm.group(1).strip(), bm.group(2)))
                else:
                    brands.append((it, ""))
        return brands

    bai_path = os.path.join(RAW_DIR, "bai_public_endorsements.json")
    bai_added = 0
    if os.path.exists(bai_path):
        with open(bai_path, encoding="utf-8") as f:
            bai_data = json.load(f)

        for pid, info in bai_data.items():
            p = p_by_id.get(str(pid)) or find_player(info.get("player_name", ""))
            if not p:
                continue
            pid_str = str(p["player_id"])
            src_url = info.get("url", "")
            tiles = info.get("tiles", [])
            summary_brands = extract_summary_brands(info.get("summary", ""))

            # Align summary_brands with tiles by matching start_date first, then positional fallback
            used_tile_idx = set()
            for idx_b, (raw_brand, sum_date) in enumerate(summary_brands):
                if not raw_brand:
                    continue
                bdisp = clean_brand_name(raw_brand)
                bkey = brand_key(bdisp)
                if (pid_str, bkey) in seen:
                    continue
                seen.add((pid_str, bkey))

                # Find matching tile
                sum_dt_iso = parse_bai_date(sum_date)
                matched_tile = None
                for ti, tile in enumerate(tiles):
                    if ti in used_tile_idx:
                        continue
                    t_dt_iso = parse_bai_date(tile.get("start_date", ""))
                    if sum_dt_iso and t_dt_iso and sum_dt_iso == t_dt_iso:
                        matched_tile = tile
                        used_tile_idx.add(ti)
                        break
                if matched_tile is None:
                    for ti, tile in enumerate(tiles):
                        if ti not in used_tile_idx:
                            matched_tile = tile
                            used_tile_idx.add(ti)
                            break

                cat_path = matched_tile.get("category_path", "") if matched_tile else ""
                industry, sub_ind = map_industry(bdisp, cat_path)
                start_dt = sum_dt_iso or (parse_bai_date(matched_tile.get("start_date", "")) if matched_tile else "")
                dtypes = (matched_tile.get("deal_types") or []) if matched_tile else []
                deal_type = "; ".join(dtypes) if dtypes else "Brand Endorsement"

                yr_m = re.match(r"^(\d{4})", start_dt)
                yr_int = int(yr_m.group(1)) if yr_m else None
                if yr_int and yr_int >= 2023:
                    status = "Active"
                    end_dt = "Undisclosed (Ongoing)"
                elif yr_int:
                    status = "Historical / Status Unconfirmed"
                    end_dt = "Undisclosed"
                else:
                    status = "Status Unconfirmed"
                    end_dt = "Undisclosed"

                deals.append({
                    "player_id": pid_str,
                    "player_name": p["player_name"],
                    "current_team": p["current_team"],
                    "brand": bdisp,
                    "industry": industry,
                    "sub_industry": sub_ind,
                    "deal_type": deal_type,
                    "start_date": start_dt,
                    "end_date": end_dt,
                    "deal_status": status,
                    "reported_value_notes": f"Public endorsement record ({cat_path})" if cat_path else "Public endorsement record",
                    "source": src_url,
                    "data_tier": "Public Endorsement Directory",
                })
                bai_added += 1

    # Sort cleanly by player_name, then Active/Lifetime first, then start_date descending
    status_rank = {"Lifetime": 0, "Active": 1, "Historical / Status Unconfirmed": 2, "Status Unconfirmed": 3, "Ended / Former": 4}
    deals.sort(key=lambda d: (d["player_name"], status_rank.get(d["deal_status"], 9), -(int(d["start_date"][:4]) if d["start_date"][:4].isdigit() else 0), d["brand"]))

    # Assign clean deal_ids
    final_deals = []
    for idx, d in enumerate(deals, 1):
        rec = {"deal_id": f"DEAL-{idx:04d}"}
        rec.update(d)
        final_deals.append(rec)

    csv_path = os.path.join(OUT_DIR, "nba_sponsorship_deals.csv")
    json_path = os.path.join(OUT_DIR, "nba_sponsorship_deals.json")

    fieldnames = list(final_deals[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(final_deals)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_deals, f, indent=2, ensure_ascii=False)

    # Verify 100% referential integrity
    orphans = [d for d in final_deals if d["player_id"] not in p_by_id]
    assert len(orphans) == 0, f"Found {len(orphans)} orphan player_ids!"

    unique_players = len({d["player_id"] for d in final_deals})
    unique_brands = len({d["brand"] for d in final_deals})
    with_start = sum(1 for d in final_deals if d["start_date"])
    with_explicit_end = sum(1 for d in final_deals if d["end_date"] and not d["end_date"].startswith("Undisclosed"))

    by_ind = {}
    for d in final_deals:
        by_ind[d["industry"]] = by_ind.get(d["industry"], 0) + 1

    print(f"Wrote {len(final_deals)} sponsorship deals ({bai_added} added from BAI public records) to {csv_path} & {json_path}")
    print(f"Unique NBA players covered: {unique_players} | Unique brands: {unique_brands}")
    print(f"With start_date: {with_start}/{len(final_deals)} | With explicit end_date/Lifetime: {with_explicit_end}/{len(final_deals)}")
    print("\nDeals by Industry:")
    for ind, cnt in sorted(by_ind.items(), key=lambda x: -x[1]):
        print(f"  {ind:35s}: {cnt}")

    # Inspect any "Other / Sports & Lifestyle" so we can refine categorization if needed
    others = [(d["player_name"], d["brand"], d["sub_industry"]) for d in final_deals if d["industry"] == "Other / Sports & Lifestyle"]
    if others:
        print(f"\nSample 'Other / Sports & Lifestyle' ({len(others)}):")
        for o in others[:25]:
            print(" ", o)


if __name__ == "__main__":
    main()
