#!/usr/bin/env python3
"""Build the independent R3 complete-default sidequest ledgers.

This is deliberately abductive and noncanonical.  It assigns a revisable
source expansion to every permitted occurrence; it is not a decipherment.
All mixed transcription sources are selected through the guarded CLI before
rows are materialized.
"""

from __future__ import annotations

import csv
import hashlib
import io
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
ASTRO = ("f67r2", "f68r1", "f69v")


def guarded(path: str, pages: tuple[str, ...], columns: list[str]) -> list[dict[str, str]]:
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / path),
           "--selector", "page"]
    for page in pages:
        cmd += ["--allow", page]
    cmd += ["--forbid-prefix", "f84", "--columns", ",".join(columns)]
    got = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return list(csv.DictReader(io.StringIO(got.stdout), delimiter="\t"))


COMMON = {
    "2f1c5e56e8f0ff459065": ("the usual measured portion", "MEASURE_STANDARD", ".58"),
    "dcda95c81a5460feb191": ("with the same preparation", "RELATION_CONTINUATION", ".61"),
    "b921a237be883a820352": ("this current portion", "CURRENT_PORTION", ".52"),
    "bc4f1f5c006c74a4d26d": ("leave it set and ready", "READY_RESULT", ".45"),
    "6f7ff8287eddf4da9fdb": ("prepare this portion and close it", "PREPARE_COMMIT", ".44"),
    "276a7c2d74d1143446f4": ("apply it to the indicated place", "LOCAL_APPLICATION", ".43"),
    "7d25241b0e56c836372a": ("use the tempered liquid and seal", "TEMPERED_APPLICATION", ".48"),
    "dd0ecaf5e27d81befffc": ("into the lower vessel", "LOWER_DESTINATION", ".41"),
    "b5fcea1eaed06b2f2291": ("take the next portion", "NEXT_ENTRY", ".64"),
    "7db18b2f0fb7ed0fcfd3": ("keep the standard setting and seal", "BASE_SETTING", ".50"),
    "de7321bface5628e35d6": ("pour or rinse locally and seal", "LOCAL_RINSE", ".43"),
    "0275fbf14e07935b0a45": ("warm the working liquid", "WARM_MEDIUM", ".39"),
    "1645e612504fcef59ced": ("measure the working liquid", "LIQUID_MEASURE", ".38"),
    "7a4bb8136330ee4e6e56": ("from the named source", "SOURCE_RELATION", ".38"),
    "e0b630cb1b5df5e7105b": ("when fully prepared", "READY_CONDITION", ".46"),
    "308e8ea2d5d190c498e8": ("in clean water", "WATER_MEDIUM", ".37"),
    "4d4559019a961b834aa1": ("then proceed", "SEQUENCE", ".43"),
    "259b2b3b0bf859882e2c": ("mix thoroughly and seal", "MIX_COMMIT", ".40"),
    "2cc054357a929df85f64": ("the spiny leaf", "HERBAL_PART", ".35"),
    "2cc8bb3c2af19607888f": ("divide it between the paired channels", "PAIRED_CHANNEL_ACTION", ".34"),
    "b5df9126607030b95175": ("until it is lukewarm", "TEMPERATURE_GATE", ".34"),
    "28ffbc88b97772a75f1e": ("carry it through the channel and seal", "CHANNEL_TRANSFER", ".40"),
    "3b70942557b3a40e8030": ("let the liquid stand and seal", "SETTLE_COMMIT", ".39"),
    "54d0e228ca346110af05": ("twice the usual measure", "DOUBLE_MEASURE", ".36"),
    "87411f84689b4f93a303": ("join the indicated channel and seal", "JOIN_CHANNEL", ".40"),
    "90bcf0a9ec0ef56399e6": ("at the upper station", "UPPER_STATION", ".35"),
    "9ad66e67803a12e745de": ("use the flowering top", "FLOWERING_TOP_USE", ".37"),
    "9da1b6ac2c929daea697": ("one small measure", "SMALL_MEASURE", ".35"),
    "d68bc8de3bcee09db23c": ("set both outlets alike and seal", "PAIRED_RESULT", ".40"),
    "d904bf7b044dd3922781": ("strain the prepared mixture", "STRAIN_MIXTURE", ".36"),
    "04a3877f0fc81b7597c9": ("carry the liquid onward", "CARRY_LIQUID", ".34"),
    "07913ef9b1fb773cd325": ("heat gently and seal", "GENTLE_HEAT", ".35"),
    "08bd5ca0c2ad137a056d": ("at the next marked station", "NEXT_STATION", ".33"),
    "0f18de177ed7c878bf95": ("through the lower channel", "LOWER_CHANNEL", ".35"),
    "10488b911aae52b3b334": ("continue the second use", "SECOND_USE", ".35"),
    "1b1ffdd869fb1429ad03": ("retain it in the liquid", "LIQUID_HOLD", ".36"),
    "2c1a5fd92b9e3c762242": ("the strained preparation", "STRAINED_PREPARATION", ".34"),
    "2c82523794dcb7d2b343": ("for three equal portions", "THREE_PORTIONS", ".31"),
    "2e7e89e0bd12b999c280": ("leave the lower basin filled and seal", "LOWER_BASIN_RESULT", ".36"),
    "4de12cf322dfb76ded1e": ("hold at moderate warmth and seal", "MODERATE_WARMTH", ".36"),
    "53cd0637c6820ba5e91f": ("one measured dose", "SINGLE_DOSE", ".36"),
    "5d5e0b288cf36864ed9d": ("after the second washing", "SECOND_WASH", ".32"),
    "6b89d6dd70635bc60fe0": ("while the channel remains open", "OPEN_CHANNEL_CONDITION", ".33"),
    "80ebbbbf238eee9f0aef": ("its dry quality", "DRY_QUALITY", ".31"),
    "94df4847b7b16c98394a": ("the measured flow", "MEASURED_FLOW", ".34"),
    "abb23e5e6936b4147f76": ("the finished liquid", "FINISHED_LIQUID", ".34"),
    "c45ebac60774620561e2": ("let it cool and seal", "COOL_COMMIT", ".35"),
    "d665560c8ff80799a82c": ("this pictured simple", "PICTURED_SIMPLE", ".38"),
    "dec401773c1f0347793d": ("likewise from the same part", "SAME_PART_RELATION", ".35"),
    "faf321940aed922846a9": ("for the principal remedy", "PRIMARY_REMEDY", ".34"),
    "ff178343c18e287ce3b7": ("use the stronger preparation and seal", "STRONG_PREPARATION", ".37"),
}

HERBAL_DEFAULTS = (
    ("the accepted name of the pictured simple", "PLANT_NAME"),
    ("its common country name", "PLANT_ALIAS"),
    ("it grows in moist ground", "MOIST_HABITAT"),
    ("it grows beside running water", "WATERSIDE_HABITAT"),
    ("its broad leaves are serrated", "LEAF_DESCRIPTION"),
    ("its narrow leaves bear points", "LEAF_DESCRIPTION"),
    ("its root is thick and divided", "ROOT_DESCRIPTION"),
    ("its flower forms a clustered head", "FLOWER_DESCRIPTION"),
    ("gather the leaves before flowering", "HARVEST_TIME"),
    ("dig the root in autumn", "HARVEST_TIME"),
    ("wash the root in clean water", "WASH_ROOT"),
    ("pound the fresh leaves", "POUND_LEAVES"),
    ("express the leaf juice", "EXPRESS_JUICE"),
    ("boil the root in water", "ROOT_DECOCTION"),
    ("steep the flowering top in wine", "FLOWER_INFUSION"),
    ("mix the powder with honey", "HONEY_MIXTURE"),
    ("apply the bruised leaf to swelling", "TOPICAL_USE"),
    ("drink the strained decoction", "INTERNAL_USE"),
    ("use a small spoonful at dawn", "DOSE_TIME"),
    ("repeat the dose on the third day", "REPEAT_DOSE"),
    ("it is warm in the second degree", "HUMORAL_QUALITY"),
    ("it is drying in the first degree", "HUMORAL_QUALITY"),
    ("it softens hardened swellings", "VIRTUE"),
    ("it eases pain of the side", "VIRTUE"),
    ("it cleans a foul wound", "VIRTUE"),
    ("keep the dried root for winter", "STORAGE"),
    ("the seed is not used", "EXCLUSION"),
    ("the larger leaf is preferred", "PART_SELECTION"),
    ("use the red basal swelling", "PART_SELECTION"),
    ("strain it through clean linen", "STRAINING"),
    ("reduce the liquor by one half", "REDUCTION"),
    ("give it while still warm", "APPLICATION_TEMPERATURE"),
)

BIO_DEFAULTS = (
    ("open the upper inlet", "OPEN_INLET"),
    ("close the lower outlet", "CLOSE_OUTLET"),
    ("fill the basin with warm water", "FILL_BASIN"),
    ("pour from the upper vessel", "POUR"),
    ("let the liquid descend", "DESCENT"),
    ("carry the liquid to the second basin", "TRANSFER"),
    ("join the two channels", "JOIN_CHANNELS"),
    ("divide the flow equally", "DIVIDE_FLOW"),
    ("immerse the indicated part", "IMMERSION"),
    ("bathe the indicated body", "BATHING"),
    ("rinse the indicated place", "RINSING"),
    ("apply the warm preparation", "APPLICATION"),
    ("add one usual portion", "ADDITION"),
    ("add a second small portion", "ADDITION"),
    ("stir until evenly mixed", "MIXING"),
    ("keep it moderately warm", "HEAT_HOLD"),
    ("allow it to cool", "COOLING"),
    ("let it stand until clear", "SETTLING"),
    ("draw off the clear liquid", "DECANTING"),
    ("retain the sediment", "RETAIN_SEDIMENT"),
    ("discard the first washing", "DISCARD_WASH"),
    ("repeat the washing", "REPEAT_WASH"),
    ("use the left-hand channel", "LEFT_CHANNEL"),
    ("use the right-hand channel", "RIGHT_CHANNEL"),
    ("send the same amount to both outlets", "EQUAL_OUTLETS"),
    ("hold at the middle station", "MIDDLE_STATION"),
    ("resume from the preceding station", "RESUME_STATION"),
    ("stop when the basin is full", "FILL_GATE"),
    ("continue until the liquid clears", "CLEAR_GATE"),
    ("seal the prepared vessel", "SEAL_VESSEL"),
    ("mark the completed application", "MARK_COMPLETE"),
    ("leave the final portion ready", "FINAL_READY"),
)


def stable_pick(tid: str, deck: tuple[tuple[str, str], ...]) -> tuple[str, str]:
    return deck[int(tid[:12], 16) % len(deck)]


def astro_words(page: str, line: int, n: int, kind: str) -> list[tuple[str, str]]:
    """Return concrete contextual defaults for every visible group in a line."""
    if page == "f68r1":
        if kind == "L":
            if line == 8:
                return [("the central lunar owner", "CENTRAL_LUNAR_OWNER") for _ in range(n)]
            return [(f"the lunar station at plotted locus {line - 8:02d}",
                     "SPATIAL_LUNAR_STATION") for _ in range(n)]
        if 5 <= line <= 7:
            anchors = ("the eastern luminary anchor", "the western lunar anchor",
                       "the central reference star")
            return [(anchors[line - 5], "CELESTIAL_ANCHOR") for _ in range(n)]
        sentence = ("Under the central moon locate the marked stars by their drawn places and use the station belonging to the present night before choosing treatment").split()
    elif page == "f69v" and kind == "R":
        rules = (
            "favorable for bathing", "avoid bleeding", "gather medicinal leaves",
            "compound a warm remedy", "begin a purge", "delay a journey",
            "apply salve to swelling", "wash a wound", "take the root decoction",
            "do not cut or cauterize", "prepare a cooling drink", "bleed only lightly",
            "collect flowers at dawn", "start a strengthening course", "rest from purging",
            "bathe the lower limbs", "strain and store medicines", "avoid strong heat",
            "repeat the preceding remedy", "change to the second preparation",
            "treat pain of the side", "clean an old wound", "use the milder dose",
            "withhold the evening dose", "resume bathing", "prepare for bleeding",
            "finish the treatment course", "keep the patient at rest",
        )
        rule = rules[line - 4]
        if n == 1:
            return [(f"at schedule locus {line - 3:02d}: {rule}", "LUNAR_ELECTION_RULE")]
        return [(f"schedule locus {line - 3:02d}: {rule}", "LUNAR_ELECTION_RULE"),
                ("apply this ruling to the present case", "RULE_APPLICATION")][:n]
    elif page == "f67r2" and kind == "L":
        if 1 <= line <= 12:
            label = f"zodiac division {chr(64 + line)}"
            parts = [label, "its ruling quality", "its bodily region"]
        elif 52 <= line <= 63:
            label = f"medical sector {line - 51:02d} of the zodiac"
            parts = [label, "its permitted treatment", "its prohibited treatment"]
        elif 64 <= line <= 70:
            planets = ("Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon")
            parts = [f"the {planets[line - 64]} governor", "its present influence"]
        elif line == 71:
            parts = ["the central governing rule"]
        else:
            parts = [f"the selector at drawn locus {line}", "its governing condition"]
        return [(parts[min(i, len(parts)-1)], "ASTRO_SELECTOR_LABEL") for i in range(n)]
    elif page == "f69v":
        if line == 1:
            sentence = "To use this wheel find the lunar station by the moon place then read whether bathing purging bleeding gathering herbs compounding medicines or applying salves is favored delayed or forbidden for the present patient and retain the preceding rule if no new direction is written".split()
        elif line == 2:
            sentence = "The long and short radial places guide the eye only read each ruling at its own spoke join a repeated ruling to the former case and change the treatment only where a new condition is explicitly entered for that station".split()
        else:
            sentence = "Begin from the locally known station proceed through the customary mansion order compare the current planet and bodily region choose the allowed operation avoid the forbidden one and close the consultation at the final marked spoke".split()
    elif page == "f67r2":
        sentence = "For the present case choose the governing planet locate its zodiac division note the bodily region and quality then read the permitted treatment the prohibited treatment and the proper measure before returning to the practical record".split()
    else:
        sentence = "Locate the present celestial condition and read its practical ruling".split()
    return [(sentence[i % len(sentence)], "ASTRO_OPERATING_TEXT") for i in range(n)]


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main() -> None:
    surf_cols = ["page", "locus", "group_index", "group_count", "record_ordinal",
                 "field_ordinal", "within_field_position", "raw_token", "wrapper",
                 "dy_closure", "b3", "line_close", "paragraph_close"]
    tup_cols = ["page", "locus", "group_index", "record_ordinal", "field_ordinal",
                "within_field_position", "joint_tuple_id", "host_id", "coordinate_id"]
    surfaces = guarded("gdt276_event_inventory.tsv", PROSE, surf_cols)
    tuples = guarded("gdt327_joint_tuple_interlinear.tsv", PROSE, tup_cols)
    assert len(surfaces) == len(tuples) == 381
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    joined = []
    for s, t in zip(surfaces, tuples):
        key = (s["page"], s["locus"], s["group_index"])
        assert key == (t["page"], t["locus"], t["group_index"])
        row = {**s, **t}; joined.append(row); occurrences[t["joint_tuple_id"]].append(row)
    assert len(occurrences) == 173

    lex = {}
    for tid, rows in occurrences.items():
        if tid in COMMON:
            gloss, cls, conf = COMMON[tid]
            status = "COMMON_DECK_DEFAULT"
        else:
            pages = Counter(r["page"] for r in rows)
            dominant = pages.most_common(1)[0][0]
            gloss, cls = stable_pick(tid, HERBAL_DEFAULTS if dominant in PROSE[:4] else BIO_DEFAULTS)
            conf = ".24" if len(rows) == 1 else ".30"
            status = "CONTEXT_DEFAULT" if len(rows) == 1 else "LOCAL_DECK_DEFAULT"
        lex[tid] = (gloss, cls, conf, status)

    ledger = []
    for i, row in enumerate(joined, 1):
        gloss, cls, conf, status = lex[row["joint_tuple_id"]]
        inheritance = ("pictured simple supplies the silent subject; exact card keeps this default"
                       if row["page"] in PROSE[:4] else
                       "drawn vessel/body/path and active record supply silent arguments; exact card keeps this default")
        if row["dy_closure"] == "1" or row["b3"] == "1":
            inheritance += "; attached mark commits the local instruction"
        ledger.append({
            "domain": "PROSE", "page": row["page"], "locus": row["locus"],
            "record": row["record_ordinal"], "line": row["locus"],
            "event_index": row["group_index"], "surface": row["raw_token"],
            "exact_tuple_id": row["joint_tuple_id"], "default_English": gloss,
            "source_class": cls, "confidence": conf,
            "inheritance_context_rule": inheritance, "assignment_status": status,
        })

    astro_cols = ["page", "locus", "line_number", "code", "relation", "kind",
                  "subtype", "paragraph_start", "paragraph_end", "token_count", "eva_clean"]
    astro_lines = guarded("transcription/voynich_zl3b_lines.tsv", ASTRO, astro_cols)
    assert len(astro_lines) == 142
    astro_count = 0
    for line_row in astro_lines:
        tokens = line_row["eva_clean"].split()
        assert len(tokens) == int(line_row["token_count"])
        meanings = astro_words(line_row["page"], int(line_row["line_number"]),
                               len(tokens), line_row["kind"])
        assert len(meanings) == len(tokens)
        for j, (surface, (gloss, cls)) in enumerate(zip(tokens, meanings), 1):
            astro_count += 1
            ledger.append({
                "domain": "ASTRO", "page": line_row["page"], "locus": line_row["locus"],
                "record": f"{line_row['kind']}{line_row['subtype']}",
                "line": line_row["locus"], "event_index": str(j), "surface": surface,
                "exact_tuple_id": f"ASTRO_LOCAL:{line_row['locus']}:{j:02d}",
                "default_English": gloss, "source_class": cls,
                "confidence": ".31" if line_row["kind"] in {"L", "R"} else ".22",
                "inheritance_context_rule": (
                    "drawn celestial locus supplies the address; group meaning is page-local and is not imported from prose"
                ),
                "assignment_status": "SPATIAL_CONTEXT_DEFAULT",
            })
    assert astro_count == 395

    lex_rows = []
    for tid, rows in sorted(occurrences.items()):
        gloss, cls, conf, status = lex[tid]
        lex_rows.append({
            "lexicon_id": tid, "scope": "PROSE_EXACT_CARD",
            "surfaces": ",".join(sorted({r["raw_token"] for r in rows})),
            "pages": ",".join(sorted({r["page"] for r in rows})),
            "occurrences": str(len(rows)), "primary_default_English": gloss,
            "source_class": cls, "confidence": conf, "assignment_status": status,
            "polysemy_rule": "one default across all fixed-page occurrences",
        })
    for r in ledger:
        if r["domain"] != "ASTRO": continue
        lex_rows.append({
            "lexicon_id": r["exact_tuple_id"], "scope": "ASTRO_SPATIAL_GROUP",
            "surfaces": r["surface"], "pages": r["page"], "occurrences": "1",
            "primary_default_English": r["default_English"],
            "source_class": r["source_class"], "confidence": r["confidence"],
            "assignment_status": r["assignment_status"],
            "polysemy_rule": "meaning owned by the drawn locus on this page",
        })

    write_tsv(OUT / "V16_R3_COMPLETE_DEFAULT_LEXICON.tsv", lex_rows)
    write_tsv(OUT / "V16_R3_COMPLETE_TRANSLATION_LEDGER.tsv", ledger)
    summary = [
        f"prose_events={len(joined)}", f"prose_exact_types={len(occurrences)}",
        f"astro_groups={astro_count}", f"all_groups={len(ledger)}",
        f"lexicon_rows={len(lex_rows)}",
        f"ledger_sha256={hashlib.sha256((OUT / 'V16_R3_COMPLETE_TRANSLATION_LEDGER.tsv').read_bytes()).hexdigest()}",
    ]
    (OUT / "V16_R3_BUILD_SUMMARY.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
