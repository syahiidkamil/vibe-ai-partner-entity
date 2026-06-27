#!/usr/bin/env python3
"""Generate domain-organized hero markdown for the magic_chess_gogo schema,
straight from dataset_s6.json so every stat is exact (no transcription)."""
import json, collections, os

ROOT = "vape/entity/storage/magic-chess-gogo/game-client-from-friend/dataset_s6.json"
OUT = "vape/entity/memory/schemata/magic_chess_gogo/concrete_things/heroes"
# NOTE: heroes/ moved under concrete_things/ (2026-06-28). After regenerating here, re-run
# gen_skills.py + inject_skills.py to re-add the active-skill bullets (this base gen omits them).
os.makedirs(OUT, exist_ok=True)

d = json.load(open(ROOT))
heroes = d["heroes"]

# synergy id -> display name, confirmed first-party 2026-06-28 from the live client v302.2
# (localization name-bands + FX_Fetter pinyin + m_Sort membership; corrects plan.md: 51=Exorcist,
# 54=Dragoncaller).
KNOWN = {1: "Bruiser", 2: "Dauntless", 3: "Defender", 4: "Weapon Master", 5: "Marksman",
         6: "Mage", 7: "Stargazer", 8: "Assassin", 9: "Scavenger", 10: "Phasewarper",
         50: "Emberlord", 51: "Exorcist", 52: "Heartbond", 53: "Astro Power", 54: "Dragoncaller",
         55: "Neobeasts", 56: "Kishin", 57: "Enchanted Tales", 58: "Mystic Meow",
         59: "Northern Vale"}
synname = {}
synaxis = {}
for s in d.get("synergies", []):
    sid = s["id"]
    synname[sid] = KNOWN.get(sid) or s.get("name") or None
    synaxis[sid] = s.get("axis")

def syn_label(sid):
    n = synname.get(sid)
    return f"{n} (r{sid})" if n else f"r{sid} (unnamed)"

def split_syn(syns):
    cls = [s for s in syns if s < 50]
    fac = [s for s in syns if s >= 50]
    return cls, fac

def star_table(stars):
    head = ("| Star | HP | PhyAtk | MagAtk | PhyDef | MagDef | AtkSpd | MoveSpd "
            "| Crit | DPS | EHP | MP |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|"
    rows = [head, sep]
    for st in stars:
        rows.append("| {star} | {hp} | {phyAtk} | {magAtk} | {phyDef} | {magDef} "
                    "| {atkSpeed} | {moveSpeed} | {crit} | {dps} | {ehp} | {mp} |".format(**st))
    return "\n".join(rows)

def hero_block(h):
    cls, fac = split_syn(h["synergies"])
    cls_s = ", ".join(syn_label(s) for s in cls) or "none"
    fac_s = ", ".join(syn_label(s) for s in fac) or "none"
    role = "Tank" if h.get("isTank") else "non-tank"
    if h.get("isSummon"):
        role += ", SUMMON"
    lines = []
    lines.append(f"### {h['name']}  (id {h['id']}, cost {h['cost']})")
    lines.append("")
    lines.append(f"- **Class synergy:** {cls_s}  ·  **Faction synergy:** {fac_s}")
    lines.append(f"- **Skills:** {h['skills']}  ·  **Role:** {role}  ·  "
                 f"**Equip priority (slot order):** {h['equipPriority']}")
    lines.append(f"- **Meta signals:** compCount {h.get('compCount')} (in recommended comps)  ·  "
                 f"carryCount {h.get('carryCount')} (as carry)")
    lines.append(f"- **codename:** `{h['codename']}`  ·  **nameSource:** {h['nameSource']}  ·  "
                 f"**icon:** `{h['headIconFile']}`")
    lines.append("")
    lines.append(star_table(h["stars"]))
    lines.append("")
    return "\n".join(lines)

HEADER = (
    "<!-- GENERATED from storage/magic-chess-gogo/game-client/dataset_s6.json by "
    "work_dir/saori/mcgg/gen_heroes.py. Stats are exact; do not hand-edit. "
    "Regenerate on a season patch. -->\n"
)

COST_NOTE = {
    1: "Cheapest tier: many copies in the shared pool, the early-game backbone.",
    2: "Low tier: still common, the bridge into mid-game synergy.",
    3: "Mid tier: the contested workhorses, common 3-star targets.",
    4: "High tier: strong carries, scarce in the pool.",
    5: "Top tier: the legendaries, rarest pulls, game-deciding when starred.",
}

specials = [h for h in heroes if h.get("isSummon") or not h["synergies"]]
normal = [h for h in heroes if h not in specials]
by_cost = collections.defaultdict(list)
for h in normal:
    by_cost[h["cost"]].append(h)
for c in by_cost:
    by_cost[c].sort(key=lambda x: x["name"])

# --- cost files ---
for c in range(1, 6):
    hs = by_cost.get(c, [])
    body = [HEADER, f"# Cost {c} Heroes (MCGG S6)", ""]
    body.append(f"{COST_NOTE[c]}  {len(hs)} heroes at this cost.")
    body.append("")
    body.append("Synergy ids: class = r1-r10, faction = r50-r59 (all 20 named from the in-game "
                "UI; see ../concrete_things/synergies.md for rosters, tiers, and icons). Stats are "
                "per star level (1/2/3). See ../schemata.md for the loop.")
    body.append("")
    for h in hs:
        body.append(hero_block(h))
    open(f"{OUT}/cost_{c}.md", "w").write("\n".join(body).rstrip() + "\n")

# --- special units ---
body = [HEADER, "# Special / Non-Shop Units (MCGG S6)", ""]
body.append("Units outside the normal shop roster: summons and special entries. They have no "
            "synergies of their own and are not bought from the shop.")
body.append("")
for h in specials:
    body.append(hero_block(h))
    if h["id"] == 179:
        body.append("> Summoned by the Dragoncaller faction (r54); scales with that synergy's "
                    "tier. Note: 4 star tiers, not 3.\n")
open(f"{OUT}/special_units.md", "w").write("\n".join(body).rstrip() + "\n")

# --- index ---
dist = {c: len(by_cost.get(c, [])) for c in range(1, 6)}
idx = [HEADER, "# Heroes (MCGG S6): the full roster, organized by domain", ""]
idx.append("The complete S6 hero data, generated exact from Kamil's datamined "
           "`dataset_s6.json` (the flat client export, re-organized here by the domain's own "
           "axis: cost tier). Per-cost detail files carry every field including full per-star "
           "stat tables; this index is the map. Governed by ../disclaimer.md (regenerate on a "
           "season patch).")
idx.append("")
idx.append("## Cost distribution (shop heroes)")
idx.append("")
idx.append("| Cost | Heroes | Detail |")
idx.append("|---|---|---|")
for c in range(1, 6):
    idx.append(f"| {c} | {dist[c]} | [cost_{c}.md](cost_{c}.md) |")
idx.append(f"| special | {len(specials)} | [special_units.md](special_units.md) |")
total = sum(dist.values()) + len(specials)
idx.append(f"| **total** | **{total}** | |")
idx.append("")
idx.append("## Per-star mechanic")
idx.append("")
idx.append("Each hero has 3 star tiers (the Dragon summon has 4). Merge 3 copies of a hero to "
           "raise its star (1->2->3); nine 1-stars make a 3-star. HP roughly 1.8x per step, so "
           "a 3-star is a large power spike. Every per-star stat block is in the cost files.")
idx.append("")
idx.append("## Stat legend")
idx.append("")
idx.append("HP, PhyAtk/MagAtk (physical/magic attack), PhyDef/MagDef, AtkSpd (attacks/sec), "
           "MoveSpd, Crit, DPS (the client's damage-per-second figure), EHP (effective HP vs "
           "the modeled defense), MP (mana to cast the skill). compCount/carryCount come from "
           "the client's recommended-comp data (how often a hero appears, and as a carry): "
           "the tier-list seed.")
idx.append("")
idx.append("## Roster at a glance  (`name (class / faction)`)")
idx.append("")
for c in range(1, 6):
    idx.append(f"**Cost {c}:** " + " · ".join(
        f"{h['name']} ({', '.join(syn_label(s) for s in split_syn(h['synergies'])[0]) or '-'}"
        f" / {', '.join(syn_label(s) for s in split_syn(h['synergies'])[1]) or '-'})"
        for h in by_cost.get(c, [])))
    idx.append("")
idx.append("**Special:** " + " · ".join(f"{h['name']} (id {h['id']})" for h in specials))
idx.append("")
open(f"{OUT}/index.md", "w").write("\n".join(idx).rstrip() + "\n")

print("wrote:", sorted(os.listdir(OUT)))
print("normal:", len(normal), "specials:", len(specials), "total:", len(heroes))
print("dist:", dist)
