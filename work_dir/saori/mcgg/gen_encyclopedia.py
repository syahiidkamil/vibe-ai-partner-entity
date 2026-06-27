"""
Extract the Magic Chess: GO GO in-app Encyclopedia (and the round/gold economy
numbers) from the live BlueStacks client, EXACT from source -- not transcribed.

Two sources, both first-party (client v1.2.88.302.2):
  1. localization_en.json  -- the encyclopedia PROSE (one stringId per panel; the
     guide text lives as contiguous id-bands).
  2. MCClassicsBattleConfig_S6.txt -- the decoded round/economy XML (the NUMBERS:
     stage ranges, base salary, extra salary, victory/streak bonus, commander DMG).

Output: storage/.../parsed/strategy/encyclopedia.json  (provenance for the
schema markdown). Re-run on a client re-pull / new season.

Run:  uv run python3 work_dir/saori/mcgg/gen_encyclopedia.py
"""
import json, re, os

ROOT = "vape/entity/storage/magic-chess-gogo/game-client-from-bluestack"
LOC = f"{ROOT}/parsed/localization_en.json"
CFG = f"{ROOT}/readable/decoded/MCClassicsBattleConfig_S6.txt"
OUT = f"{ROOT}/parsed/strategy/encyclopedia.json"

# --- the encyclopedia panels, by stringId (live S6, the 3003 band; a few from the
#     2912 band where it carries detail the 3003 band omits) ---
PANELS = {
    "game_rules":              3003306606,  # shared pool / fixed counts / rounds / champion
    "round.battle_stage":      3003306607,  # four stages I-IV, Go Go Box, stage DMG
    "round.battle_round":      3003307280,  # shop auto-refresh, 2 EXP, phases, Battle Accel
    "round.battle_complete":   3003307281,  # +1 on defense, commander DMG by units/star/round
    "round.creep_round":       3003307282,  # creep round, 3 equip drop, pick 1
    "hero.star_quality":       3003307283,  # 3 stars, combine 3, five quality tiers
    "hero.faction_role":       3003307284,  # faction + role -> synergy
    "hero.summoned":           2912711922,  # summoned heroes traits
    "hero.blessing":           2912711175,  # blessing system (synergy +1)
    "commander.level_exp":     3003307285,  # 2 EXP/round, gold->EXP, level gates capacity
    "commander.skills":        3003307286,  # 3 unique skills, unlocks
    "commander.dmg_formula":   2912711205,  # Commander DMG = Round Base + Total Star Levels
    "commander.dmg_base":      2912711204,  # winner deals DMG to loser; Arena -25 HP
    "commander.dmg_special":   2912711203,  # non-Hero unit +1; draw -> both deal DMG
    "gold":                    3003307287,  # base/interest/streak/victory/commander
    "gold.shop_actions":       3003307288,  # recruit / refresh / level up
    "advanced.economy":        3003308431,  # save for interest, all-in when low HP
    "advanced.synergy_pos":    3003308432,  # activate synergy; melee front / ranged back
    "advanced.counter_pool":   3003308433,  # counter foes; deny shared-pool heroes
    "season.dawnlight":        3275246170,  # current-season banner (Dawnlight Celebration)
}

# extra MCGG-specific guides that live in the localization but NOT on the 8-tab Encyclopedia
# bar. Each entry: list of stringIds (title first, then body parts). MCGG-only; the main MLBB
# MOBA tutorials are excluded on purpose.
GUIDES = {
    "mode.go_go_auction":      [2912711047, 2912711048],
    "mode.draft_pick":         [2078505105, 1080434174, 1144011998],
    "feature.commander_power_card": [2912711086, 2912711108, 1629673760],
    "feature.crystal_dice":    [2078505135, 1082709494, 2312887464],
    "feature.magic_crystal_rune": [2078505133, 1662170372, 1662170373, 1662170374, 3007059187],
    "feature.auto_buy":        [1079666900, 1079666901],
    "feature.lock_shop":       [1146073352],            # the "Advanced Shop" mechanic
    "feature.collection_points": [1083363810, 1083363811, 1083363812, 1083363813, 1083363845],
    "synergy_tutorial.heartbond": [1083367870, 1083367871, 1083367872, 1083367873],
}

# tab labels (UI), for the index
TAB_LABELS = {
    "main_tabs": [1982040849, 1982040850, 1982040851, 1982040852, 1982040853,
                  1982040854, 1982040857, 1982040879],            # GameRules..SeasonInfo
    "round_subtabs": [2912711232, 2912711233, 2912711234, 2912711235, 2912711236],
    "hero_subtabs": [2912711237, 2912711238, 2912711239, 2912711240],  # incl ShopRefreshProb
}


def clean(s):
    """Strip Moonton markup: [color]..[-] tags and ## line breaks."""
    s = re.sub(r"\[[#0-9A-Za-z_\-]+\]", "", s)   # [FFC262] [#d9e0ff] [b] [-] ...
    s = s.replace("##", "\n").replace("　", " ")
    return s.strip()


def xml_attrs(txt, tag):
    out = []
    for m in re.findall(rf"<{tag}\b([^>]*?)/?>", txt):
        d = dict(re.findall(r'(\w+)="([^"]*)"', m))
        out.append(d)
    return out


def main():
    loc = json.load(open(LOC))
    cfg = open(CFG, encoding="utf-8", errors="replace").read()

    panels = {}
    for key, sid in PANELS.items():
        raw = loc.get(str(sid))
        panels[key] = {"id": sid, "text": clean(raw) if raw else None,
                       "raw": raw}

    guides = {}
    for key, ids in GUIDES.items():
        parts = [{"id": sid, "text": clean(loc[str(sid)])}
                 for sid in ids if str(sid) in loc]
        guides[key] = {"title": parts[0]["text"] if parts else None,
                       "ids": ids,
                       "body": [p for p in parts[1:]]}

    labels = {grp: {sid: loc.get(str(sid)) for sid in ids}
              for grp, ids in TAB_LABELS.items()}

    # --- economy NUMBERS from the S6 config XML ---
    res_init = xml_attrs(cfg, "AResourceInit")
    base_sal = xml_attrs(cfg, "ABaseSalary")
    extra_sal = xml_attrs(cfg, "SExtraSalary")
    victory = xml_attrs(cfg, "AVictoryReward")
    win_streak = xml_attrs(cfg, "AContinueVictoryReward")
    lose_streak = xml_attrs(cfg, "AContinueFailureReward")
    stage_range = xml_attrs(cfg, "SMCRoundRange")
    round_dmg = xml_attrs(cfg, "SRoundExtraDamage")

    economy = {
        "starting_resources": res_init[0] if res_init else None,
        "base_salary": {k: v for k, v in (base_sal[0].items() if base_sal else [])},
        "extra_salary_by_round": {int(d["iRoundIndex"]): int(d["iExtraValue"])
                                  for d in extra_sal},
        "victory_reward": victory[0] if victory else None,
        "win_streak_bonus": win_streak[0] if win_streak else None,
        "lose_streak_bonus": lose_streak[0] if lose_streak else None,
        "interest": {"per_10_gold": 2, "max": 4, "source": "loc 3003307287 / Interest=4"},
    }
    stages = [{"stage": int(d["iStage"]), "start": int(d["iStartRound"]),
               "end": int(d["iEndRound"])} for d in stage_range]
    commander_dmg = {"round_base_dmg": {int(d["iRound"]): int(d["iValue"])
                                        for d in round_dmg},
                     "formula": "Round Base DMG + Total Star Levels of Surviving Units"}

    doc = {
        "meta": {
            "source": "MCGG live client v1.2.88.302.2 (BlueStacks pull, 2026-06-27)",
            "loc_file": "parsed/localization_en.json",
            "cfg_file": "readable/decoded/MCClassicsBattleConfig_S6.txt",
            "generator": "work_dir/saori/mcgg/gen_encyclopedia.py",
            "season": "S6 (Dawnlight Celebration)",
        },
        "tab_labels": labels,
        "panels": panels,
        "guides": guides,
        "economy": economy,
        "stage_ranges": stages,
        "commander_dmg": commander_dmg,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {OUT}")
    print(f"  {len([p for p in panels.values() if p['text']])}/{len(panels)} panels resolved")
    print(f"  guides: {len(guides)} ({sum(1 for g in guides.values() if g['body'])} with body)")
    print(f"  stages: {stages}")
    print(f"  base_salary: {economy['base_salary']}")
    print(f"  extra_salary: {economy['extra_salary_by_round']}")
    print(f"  victory: {economy['victory_reward']}")
    print(f"  win_streak: {economy['win_streak_bonus']}  lose_streak: {economy['lose_streak_bonus']}")
    print(f"  round_base_dmg: {commander_dmg['round_base_dmg']}")


if __name__ == "__main__":
    main()
