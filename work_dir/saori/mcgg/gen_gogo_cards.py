"""Extract the MCGG Go Go Card data from the live-client localization.

Writes  .../game-client-from-bluestack/parsed/strategy/gogo_cards.json

WHY localization-driven (not table-driven): the card name/desc are NOT stored in
any skill table as a stringId. In the mulong format a localized name/desc column
"consumes ZERO bytes" (runtime lookup), so no decoded table references the card
strings. The card text therefore lives only in the localization pool
(AllLanguageEN -> localization_en.json), where names and effects are interleaved
with hero skills in column-major blocks (names band, then descs band). There is
no clean per-card band and no stored rarity column, so this extractor resolves
what is first-party verifiable and marks the rest unresolved (never fabricates).

Confident name<->effect pairings are those where the effect SELF-IDENTIFIES its
commander: an "(Exclusive to Commander X)" tag, a "Commander X" mention, the
hero's signature mechanic, or a previously UI-captured match. The numbers stay as
<Num*> template placeholders except the four UI-anchor cards, whose filled values
are confirmed from the game UI.

Run:  uv run python3 work_dir/saori/mcgg/gen_gogo_cards.py
"""
import os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BASE = os.path.join(ROOT, "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack")
LOC = os.path.join(BASE, "parsed/localization_en.json")
OUT = os.path.join(BASE, "parsed/strategy/gogo_cards.json")
VERSION = "1.2.88.302.2"

loc = {int(k): v for k, v in json.load(open(LOC)).items()}


def g(sid):
    return loc.get(sid)


# ---- the card SYSTEM (verified strings) ----
system = {
    "categories": {  # UI filter tabs; rarity colors ascend Blue < Purple < Orange
        "Power Cards": 1082708441,
        "Orange Cards": 1079733340,
        "Purple Cards": 1079733339,
        "Blue Cards": 1079733338,
    },
    "power_card_stage": {  # Round I-2 replaces the first Go Go Card round
        "intro": g(2912711108),
        "first_stage": g(1629673760),
    },
    "quality_upgrade": {  # cards can be bumped a tier; max -> Black Dragon Treasures
        "subsequent": g(2212550713),
        "round_II_3": g(2212545908),
        "yu_zhong_variant": g(2212550714),
    },
    "labels": {
        "go_go_cards": g(309298004),
        "select_commander_power_card": g(562798238),
        "commander_power_cards": g(1578577778),
    },
}

# ---- the 36 Commander Power Card names (first-party) ----
power_names = sorted({t for t in loc.values()
                      if re.search(r"'s Power$", t) and len(t) < 24})

# ---- confident commander pairings (effect self-identifies the commander) ----
# (commander, effect_sid, source, filled?) ; filled text only for UI anchors
resolved = [
    {"commander": "Minotaur", "effect_sid": 2212524886, "rarity": "Power",
     "exclusive": False, "source": "UI anchor (verbatim)",
     "ui": "Select an Equipment to enhance. Can be used 2 time(s). "
           "Obtain random Equipment x2."},
    {"commander": "Kagura", "effect_sid": 2212524701, "rarity": "Power",
     "exclusive": False, "source": "UI anchor (verbatim)",
     "ui": "Select a Hero. When battle starts, they gain 20% Hybrid Lifesteal "
           "and 30% Hybrid ATK. Gain 9 Gold."},
    {"commander": "Johnson", "effect_sid": 2212545969, "rarity": "Power",
     "exclusive": True, "source": "UI anchor (verbatim) + Exclusive tag",
     "ui": "Increases the number of Johnnies in the Hero Pool by 5. Johnny gains "
           "25% Hybrid ATK and 20% Max HP. (Exclusive to Commander Johnson)"},
    {"commander": "Lunox", "effect_sid": 2212545841, "rarity": "Power",
     "exclusive": True, "source": "UI anchor (verbatim) + Exclusive tag",
     "ui": "Gain 4 Gold. When you first activate a Synergy to 6, gain 24 more "
           "Gold. (Exclusive to Commander Lunox)"},
    {"commander": "Karina", "effect_sid": 2212524826, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag"},
    {"commander": "Lukas", "effect_sid": 2212549629, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag"},
    {"commander": "Alice", "effect_sid": 2212550646, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag + UI capture"},
    {"commander": "Yu Zhong", "effect_sid": 2212550714, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag"},
    {"commander": "Ruby", "effect_sid": 2212575670, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag"},
    {"commander": "Diggie", "effect_sid": 2212551762, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag + Alarm Chest signature"},
    {"commander": "Popol and Kupa", "effect_sid": 2212551733, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag (capture variant)"},
    {"commander": "Popol and Kupa", "effect_sid": 2212546034, "rarity": "Power",
     "exclusive": False, "source": "Copy Trap signature + UI capture"},
    {"commander": "Zilong", "effect_sid": 2212549625, "rarity": "Power",
     "exclusive": True, "source": "Exclusive tag (Great Dragon Spear)"},
    {"commander": "Harley", "effect_sid": 2212524730, "rarity": "Power",
     "exclusive": False, "source": "UI capture"},
    {"commander": "Lancelot", "effect_sid": 2212548917, "rarity": "Power",
     "exclusive": False, "source": "UI capture"},
    {"commander": "Dyrroth", "effect_sid": None, "rarity": "Power",
     "exclusive": True, "source": "Exclusive label 2212545881; effect text unresolved"},
]
for c in resolved:
    c["effect_template"] = g(c["effect_sid"]) if c["effect_sid"] else None

resolved_commanders = {c["commander"] for c in resolved}
unpaired = [n for n in power_names
            if n[:-len("'s Power")] not in {c.replace(" and ", " and ") for c in resolved_commanders}]

# ---- generic (non-commander) Go Go card effects, verified; rarity per-card UNRESOLVED ----
generic = {
    "gold": g(2212551740),
    "free_refresh": g(2212551738),
    "equipment_chest": g(2212551795),
    "magic_crystal_chest": g(2212550677),
    "copy_trick_name": g(2212550621),
    "copy_trick_effect": g(2212550622),
    "black_dragon_treasures": [g(2212550616), g(2212550617), g(2212550618), g(2212550619)],
}

out = {
    "meta": {
        "season": "S6", "status": "live", "version": VERSION,
        "source": "Magic Chess GoGo client (BlueStacks pull), localization_en.json",
        "method": "localization-driven; card name/desc are runtime lookups absent "
                  "from every decoded table, so no stored stringId or rarity column "
                  "exists. Names/effects interleaved with hero skills in column-major "
                  "blocks. Confident pairings self-identify the commander; the rest "
                  "are name-resolved, effect-unpaired. Never fabricated.",
        "power_card_names_found": len(power_names),
        "power_cards_effect_resolved": len([c for c in resolved if c["effect_sid"]]),
        "anchors_verbatim_confirmed": 4,
    },
    "system": system,
    "power_card_names": power_names,
    "power_cards_resolved": resolved,
    "power_cards_name_only": unpaired,
    "generic_cards": generic,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
print("wrote", OUT)
print("power names:", len(power_names), "| effects resolved:", out["meta"]["power_cards_effect_resolved"])
print("name-only:", len(unpaired))
