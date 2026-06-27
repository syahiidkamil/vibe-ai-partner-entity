"""Generate commanders.json provenance from the live localization (first-party).
Text is pulled exact by stringId (not transcribed). Curated commander->skill
groupings are by-id, justified by the skill name/description naming the commander,
or band adjacency. Roster characters + skin titles are extracted programmatically
from the 637xxx title band. Run with: uv run python3 gen_commanders.py
"""
import json, re, os

BASE = "vape/entity/storage/magic-chess-gogo"
LOC = f"{BASE}/game-client-from-bluestack/parsed/localization_en.json"
OUT = f"{BASE}/game-client-from-bluestack/parsed/strategy/commanders.json"
loc = json.load(open(LOC))


def T(sid):
    return loc[str(sid)]


# ---- resolved commanders: curated (name_id, desc_id) groups, each justified ----
# Each skill: [name_stringId|None, desc_stringId]. Text fetched exact below.
RESOLVED = {
    "Lancelot": {
        "roster_character": "Remy (title band clusters his skins; live UI shows Lancelot)",
        "archetype": "Economy / self-scaling",
        "strategy": ("Sacrifice interest for a guaranteed bonus-Gold drip, then sink all "
                     "Gold each round into upgrading Lancelot himself: gold-into-self "
                     "scaling rather than a board economy."),
        "skills": [
            ("Golden Legacy", 2212460314, 2212487225),   # live desc = the anchor
            ("Golden Blade", 2212494852, 2212494853),     # the anchor
        ],
        "related_skills": [  # alternate/secondary economy entries in the 2212460312 block
            ("Money-grubber", 2212460312, None),
            ("Finance Genius", 2212460313, 2212460315),   # [C7Active] gain gold randomly
            ("(interest passive)", None, 2212460316),
        ],
    },
    "Benny": {
        "roster_character": "Benny",
        "archetype": "Creep recruiter (PvE -> power)",
        "strategy": ("Turn the PvE creep rounds into army growth: each creep battle "
                     "recruits the opponent's strongest creep into Benny's faction."),
        "skills": [
            ("King of Beasts", 2212458396, 2212458397),
        ],
    },
    "Bersi": {
        "roster_character": "Bersi",
        "archetype": "Resurrection / durability",
        "strategy": ("Outlast: resurrect the first hero to die each round, buy team-wide "
                     "revive chances with Gold, and Bersi himself revives once with HP+Gold."),
        "skills": [
            ("Bersi's Blessing", 2212459263, 2212459266),
            ("Back from the Dead", 2212459264, 2212459267),
            ("Bersi's Obsession", 2212459265, 2212459289),
        ],
    },
    "Brown": {
        "roster_character": "Brown (skin 'Grandmaster Smith'; skill kit named 'Smith's Scorn')",
        "archetype": "Equipment denial + snowball execute",
        "strategy": ("Cripple the enemy carry by discarding its equipment, and snowball an "
                     "execute threshold that rises every win (Blazing Hammer artifact)."),
        "skills": [
            ("Smith's Scorn", 2212459329, 2212459353),
            ("Blazing Hammer", 2212459351, 2212459354),
            ("Reinforce", 2212459352, 2212459360),  # 'Play as Brown' obtain text
        ],
    },
    "Tharz": {
        "roster_character": "Tharz",
        "archetype": "Anti-3-star / 2-star stacking (Devil's Might)",
        "strategy": ("Forgo 3-stars entirely; instead every extra copy of a 2-star hero "
                     "enhances it (Devil's Might), a horizontal duplicate-fed power curve."),
        "skills": [
            ("Devil's Might", 2212459481, 2212459484),
            ("Petal Stars", 2212459475, None),
            ("Star Fall", 2212459476, None),
            ("Budding Blossom", 2212459477, None),
            ("Party Time!", 2212459482, None),
            ("Go, Tharz!", 2212459483, None),
        ],
    },
    "Austus": {
        "roster_character": "Austus",
        "archetype": "Shard/Totem value engine",
        "strategy": ("Collect shards (on wins and on ally deaths) to fire a Totem that "
                     "pays out Gold and free high-cost (5-Gold) heroes: an economy/value snowball."),
        "skills": [
            ("Power of Shadows", 2212459541, 2212459544),
            ("Blade of Resonance", 2212459542, 2212459545),
            ("Forest's Blessing", 2212459543, 2212459546),
        ],
    },
    "Harper": {
        "roster_character": "Harper",
        "archetype": "Damage-reduction / win-streak tank",
        "strategy": ("Survive on damage reduction and stacking win-streak shields; block a "
                     "whole round of damage on demand to protect a fragile HP lead."),
        "skills": [
            ("Warrior's Will", 2212460219, 2212460222),
            ("Shield of Blessing", 2212460220, 2212460223),
            ("Victory Contract", 2212460221, 2212460224),
        ],
    },
    "Dubi": {
        "roster_character": "Dubi",
        "archetype": "Fluffy mines (AoE control / zoning)",
        "strategy": ("Seed the board with Fluffy that explode and stun whole rows/columns; "
                     "scale the number of Fluffy with team Capacity."),
        "skills": [
            ("Dubi's Gift", 2212460225, 2212460228),
            ("Summon Fluffy", 2212460226, 2212461341),
            ("Awaken! Dubi's Wrath", 2212460227, 2212460250),
        ],
    },
    "Abe": {
        "roster_character": "Abe",
        "archetype": "Anti-commander aggression",
        "strategy": ("Accelerate the opponent's HP loss: deal extra damage to enemy "
                     "Commanders, and enhance Abe's attack after repeatedly hitting them."),
        "skills": [
            ("(post-win commander damage)", None, 2212461343),
            ("(enhanced attack vs commanders)", None, 2212461344),
        ],
    },
    "Johnson": {
        "roster_character": "Kaboom (the car commander; live UI shows Johnson, a hero-commander)",
        "archetype": "Exclusive-unit summoner (Johnny + Katoom) + charge tank",
        "strategy": ("Add commander-exclusive units to the shop (a 3-Gold Johnny, a Purple "
                     "Katoom) that charge the enemy; Johnson himself transforms into a car. "
                     "Has commander-exclusive Go Go cards."),
        "skills": [
            ("Johnny, Go!", 2212459418, 2212459421),
            ("Transform!", 2212459419, 2212459422),
            ("Go Katoom!", 2212459420, 2212459444),
            ("Spanner Spin", 2212459448, 2212459451),
            ("Shield Smash", 2212459449, 2212459452),
            ("Frenzy Rush", 2212459450, 2212459453),
            ("(Johnson hero-commander passive)", None, 2291825089),
        ],
    },
}

# ---- unattributed commander-skill pool (named, but no commander resolved) ----
UNATTRIBUTED = [
    # shared economy/utility selectable skills (group 0)
    ("Economize", 2212457559, 2212457560),
    ("Surging Morale", 2212457561, 2212457562),
    ("Alarm Chest", 2212457584, 2212457585),
    ("Boon to the Weak", 2212457589, 2212457590),
    ("Waste Not", 2212457591, 2212457592),
    ("Midas Touch!", 2212457593, 2212457615),
    # sacrifice / charm / gather-power kit (female commander, name unresolved)
    ("(sacrifice mana active)", None, 2212458523),
    ("Charming", 2212458549, 2212458545),
    ("(gather-power active)", None, 2212462240),
    # synergy manipulation
    ("(stun via synergy crystals)", None, 2212462391),
    ("(grant synergy crystal)", None, 2212463107),
    ("(grant Blessing)", None, 2212463108),
    # scavenger / inherit on elimination
    ("Astral Blessing - Gold", 2212460285, 2212460288),
    ("Astral Blessing - Hero", 2212460286, 2212460289),
    ("Astral Blessing - Equipment", 2212460287, 2212460290),
    # frost/copy traps (group 2, attribution soft)
    ("Frost Trap", 2212458390, 2212458366),
    ("Copy Trap", 2212458392, 2212458368),
]


def skill_obj(triple):
    name, name_id, desc_id = triple
    o = {"skill": name}
    if name_id:
        o["name_id"] = name_id
        o["name_text"] = T(name_id)
    if desc_id:
        o["desc_id"] = desc_id
        o["desc_text"] = T(desc_id)
    return o


# ---- roster characters + skin titles from the 637xxx band (programmatic) ----
def roster_clusters():
    items = sorted((int(k), v) for k, v in loc.items()
                   if 637068560 <= int(k) <= 637070700)
    # split on gaps > 12
    clusters, cur, prev = [], [], None
    for sid, v in items:
        if prev and sid - prev > 12:
            if cur:
                clusters.append(cur)
            cur = []
        cur.append((sid, v))
        prev = sid
    if cur:
        clusters.append(cur)
    return clusters


# known base character names (single given names) to label each cluster
BASE_NAMES = {"Harper", "Ragnar", "Remy", "Eva", "Abe", "Eggie", "Mavis", "Buss",
              "Benny", "Pao", "Yuki", "Connie", "Bersi", "Brown", "Saki", "Kaboom",
              "Rya", "Tharz", "Austus", "Dubi", "Asta"}
CJK = re.compile(r"[一-鿿]")
from collections import Counter
roster = []
for cl in roster_clusters():
    names = [v for _, v in cl if not CJK.search(v)]
    base = None
    # 1) a bare known given-name standing alone in the cluster
    for n in names:
        if n in BASE_NAMES:
            base = n
            break
    # 2) fallback: a known name recurring as the trailing token of skin titles
    if not base:
        trail = Counter(n.split()[-1] for n in names if " " in n)
        for cand, cnt in trail.most_common():
            if cand in BASE_NAMES and cnt >= 1:
                base = cand
                break
    if base:
        titles = [n for n in names if n != base]
        roster.append({"character": base, "skin_titles": titles,
                       "id_band": [cl[0][0], cl[-1][0]]})

out = {
    "_provenance": {
        "source": "live client v1.2.88.302.2 (BlueStacks), localization_en.json",
        "parser": "work_dir/saori/mcgg/mulong_parse.py (ver-6 localization)",
        "method": ("Commander names, titles, skill names and skill descriptions are "
                   "first-party verbatim from the EN localization (text pulled exact by "
                   "stringId). Commander->skill grouping is by the skill text naming the "
                   "commander (e.g. 'upgrade Lancelot', 'Play as Brown', possessive "
                   "'Bersi's', 'Harper', 'Austus', 'Abe', 'Tharz') and by localization "
                   "name-band adjacency. Roster characters + skin titles extracted from "
                   "the 637068560-637070700 title band by gap-clustering."),
        "not_resolved": ("Exact <Num> skill values: the data tables "
                         "(MCCommanderSkillValue, IndividualCommanderLevel, "
                         "CommanderRisingStar_MC2, MCCommanderInterestNum) hold the fills "
                         "but the localization is hash-keyed (no in-table stringId), so "
                         "per-skill <Num> keying is not deterministic from this dump "
                         "(same soft spot as synergy/item value prose). Templated "
                         "placeholders (<Num1>, <%Num1>, ####=line break) left intact."),
        "anchor": ("Commander Lancelot, Golden Legacy + Golden Blade, verified verbatim "
                   "against the live-UI anchor."),
    },
    "system": {
        "player_is_commander": "see ../../schemata.md (the Commander = the player)",
        "commander_hp": ("Each Commander has Commander HP; lost PvP rounds drain it, 0 = "
                         "eliminated. Many commander skills restore/protect HP "
                         "(e.g. on win, on defeating another Commander)."),
        "commander_level": ("Raised with Gold; gates Hero Capacity (board size). Some "
                            "skills reduce the Gold cap to upgrade, or the refresh cost."),
        "stars_and_skins": ("Up to 3 stars (per live UI). Star level scales skills "
                            "(Golden Legacy scales by stage/star I/II/III). Skins are "
                            "cosmetic titles (the 637xxx title band); many are MLBB-hero "
                            "crossover skins."),
        "commander_damage": ("Commander DMG scales with stage (per live UI). Supported by "
                            "post-win commander-damage skills (Abe) and gather-power "
                            "actives. Exact scaling not deterministically extracted."),
        "skill_tags": ("[C7Passive]/[C7Active] = commander passive/active; [C4Active] = an "
                       "active ability. Each commander has 2-3 signature skills."),
        "exclusive_gogo_cards": ("Some commanders have exclusive Go Go cards (Johnson, "
                                 "Lunox per live UI). See ../../gogo_cards/index.md."),
        "interest": ("Most commanders earn interest on saved Gold; a few forgo it "
                     "(Lancelot). MCCommanderInterestNum holds interest brackets."),
        "data_tables": ["CommanderSkillSelectConfig.bin", "MCCommanderSkillValue.bin",
                        "MCCommanderInterestNum.bin", "IndividualCommanderLevel.bin",
                        "CommanderRisingStar_MC2.bin", "IndividualCommandel.bin"],
    },
    "resolved_commanders": [],
    "unattributed_skill_pool": [skill_obj(t) for t in UNATTRIBUTED],
    "roster_characters": roster,
}

for name, d in RESOLVED.items():
    entry = {"name": name, "roster_character": d["roster_character"],
             "archetype": d["archetype"], "strategy": d["strategy"],
             "skills": [skill_obj(t) for t in d["skills"]]}
    if "related_skills" in d:
        entry["related_skills"] = [skill_obj(t) for t in d["related_skills"]]
    out["resolved_commanders"].append(entry)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w"), indent=2, ensure_ascii=False)
print("wrote", OUT)
print("resolved commanders:", len(out["resolved_commanders"]))
print("roster characters:", len(roster), [r["character"] for r in roster])
print("unattributed skills:", len(out["unattributed_skill_pool"]))
print()
print("ANCHOR CHECK:")
print(" Golden Legacy (live):", repr(T(2212487225)))
print(" Golden Blade:", repr(T(2212494852)), "::", repr(T(2212494853)))
