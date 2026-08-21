#!/usr/bin/env python3
"""Build R3's complete V17 recurrent-card stress test.

This is a deliberately speculative sidequest instrument. It assigns concrete
technical meanings; it does not claim decipherment. Mixed GDT327 data is read
only through GuardedTSV with the seven authorized prose pages allow-listed.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV


OUT = Path(__file__).resolve().parent
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
GDT327 = ROOT / "gdt327_joint_tuple_interlinear.tsv"
V16 = ROOT / "experiments/yolo/sidequest_theory_candidates_v16/V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv"


# Exactly three concrete rivals per card. Score tuples are
# contextual / cross-page / Herbal-Bio portability / historical / repairs.
# Higher is better for the first four; lower is better for repairs.
DECISIONS = {
"2f1c5e56e8f0ff459065": ("in the stated or usual measure", [("in the stated or usual measure",5,5,5,5,0),("for the same duration",3,3,3,4,4),("let this portion remain",2,2,2,4,6)], .72, "RETAINED"),
"dcda95c81a5460feb191": ("with the foregoing liquid", [("with it; likewise under the same heading",4,5,5,5,1),("with the foregoing liquid",5,5,5,5,0),("add clean water",2,2,2,5,9)], .67, "IMPROVED"),
"b921a237be883a820352": ("this present charge", [("this portion",5,5,5,5,0),("this present charge",5,5,5,5,0),("this water",2,2,2,5,10)], .65, "IMPROVED"),
"bc4f1f5c006c74a4d26d": ("let it stand and settle", [("set ready in the usual manner; close the rubric",4,5,4,4,1),("let it stand and settle",5,5,5,5,0),("finish the application",3,4,3,5,4)], .61, "REVERSED"),
"6f7ff8287eddf4da9fdb": ("stir until evenly mixed", [("mix until even",5,5,5,5,0),("stir until evenly mixed",5,5,5,5,0),("heat until even",3,3,4,5,5)], .66, "IMPROVED"),
"276a7c2d74d1143446f4": ("apply or use the prepared substance", [("use the lesser portion",3,3,4,5,5),("apply or use the prepared substance",5,5,5,5,0),("take another portion",3,3,4,5,5)], .64, "REVERSED"),
"dd0ecaf5e27d81befffc": ("at the indicated place", [("at the indicated place",5,5,5,5,0),("with clean water",2,2,2,5,8),("then continue",3,3,3,5,5)], .66, "RETAINED"),
"7d25241b0e56c836372a": ("warm it to a tempered heat", [("use the tempered warm medium; close the rubric",4,5,4,5,1),("warm it to a tempered heat",5,5,5,5,0),("mix it thoroughly",3,3,4,5,5)], .62, "IMPROVED"),
"b5fcea1eaed06b2f2291": ("take up the next measured charge", [("take up the next entry",5,5,5,5,0),("take up the next measured charge",5,5,5,5,0),("pour in water",2,2,2,5,8)], .69, "IMPROVED"),
"7db18b2f0fb7ed0fcfd3": ("pour or rinse it over the indicated place", [("rinse or pour over the local place; close the rubric",5,5,5,5,0),("pour or rinse it over the indicated place",5,5,5,5,0),("let the vessel cool",3,3,3,5,6)], .63, "IMPROVED"),
"de7321bface5628e35d6": ("let it cool to the ordinary setting", [("leave at the ordinary base setting; close the rubric",4,5,5,4,1),("let it cool to the ordinary setting",5,5,5,5,0),("retain the residue",3,3,4,5,5)], .59, "IMPROVED"),
"e0b630cb1b5df5e7105b": ("when the preparation is ready", [("when prepared and ready",5,5,5,5,0),("when the preparation is ready",5,5,5,5,0),("while it remains warm",3,3,4,5,4)], .61, "IMPROVED"),
"7a4bb8136330ee4e6e56": ("the prepared liquid", [("the prepared liquid",5,5,5,5,0),("from the source vessel",3,3,3,5,5),("then continue",2,2,3,5,7)], .60, "RETAINED"),
"1645e612504fcef59ced": ("put the next measured charge into the vessel", [("then put it in",5,5,5,5,0),("put the next measured charge into the vessel",5,5,5,5,0),("add the dry ingredient",3,3,3,5,5)], .63, "IMPROVED"),
"0275fbf14e07935b0a45": ("add warmed water", [("keep gently warmed",4,4,5,5,3),("add warmed water",5,5,5,5,0),("mix thoroughly",3,3,4,5,5)], .57, "REVERSED"),
"308e8ea2d5d190c498e8": ("combine the two portions", [("combine the two portions",5,5,5,5,0),("work it in clean water",4,4,5,5,2),("add warmed oil",3,3,4,5,5)], .62, "RETAINED"),
"4d4559019a961b834aa1": ("then proceed", [("of the same",3,3,3,5,5),("then proceed",5,5,5,5,0),("with the same liquid",4,4,4,5,2)], .55, "REVERSED"),
"b5df9126607030b95175": ("until the liquid runs clear", [("until it becomes clear",5,5,5,5,0),("until the liquid runs clear",5,5,5,5,0),("until it becomes cool",3,3,4,5,5)], .56, "IMPROVED"),
"2cc054357a929df85f64": ("as for the pictured plant", [("thereafter",3,4,2,5,4),("as for the pictured plant",5,5,2,5,0),("take the pictured root",4,4,2,5,3)], .50, "REVERSED"),
"2cc8bb3c2af19607888f": ("through the joined channels", [("through the joined channels",5,5,4,5,0),("immerse the connected part",4,4,4,5,3),("strain it through cloth",3,3,3,5,5)], .60, "RETAINED"),
"259b2b3b0bf859882e2c": ("wash it through once", [("finish this application; close the rubric",3,4,4,5,4),("wash it through once",5,5,4,5,0),("close the lower outlet",4,4,4,5,3)], .55, "REVERSED"),
"9ad66e67803a12e745de": ("use the fresh preparation", [("use the fresh preparation",5,5,3,5,0),("gather the fresh herb",4,4,2,5,3),("add the fresh juice",4,4,3,5,3)], .55, "RETAINED"),
"9da1b6ac2c929daea697": ("one measured charge", [("one measured share",5,5,4,5,0),("one measured charge",5,5,4,5,0),("for one interval",3,3,3,5,5)], .54, "IMPROVED"),
"28ffbc88b97772a75f1e": ("draw off the clear liquor", [("retain the combined mixture; close the rubric",4,4,4,5,2),("draw off the clear liquor",5,5,4,5,0),("let the mixture settle",4,4,4,5,2)], .56, "REVERSED"),
"87411f84689b4f93a303": ("bring it once to the boil", [("heat once; close the rubric",5,5,4,5,0),("bring it once to the boil",5,5,4,5,0),("rinse the heated vessel",3,3,3,5,5)], .55, "IMPROVED"),
"d904bf7b044dd3922781": ("over a gentle heat", [("at gentle heat",5,5,4,5,0),("over a gentle heat",5,5,4,5,0),("with warmed water",3,3,4,5,4)], .54, "IMPROVED"),
"3b70942557b3a40e8030": ("let the liquid settle clear", [("let it settle; close the rubric",5,5,4,5,0),("let the liquid settle clear",5,5,4,5,0),("let it cool completely",4,4,4,5,3)], .55, "IMPROVED"),
"d68bc8de3bcee09db23c": ("strain it through cloth", [("strain completely; close the rubric",5,5,4,5,0),("strain it through cloth",5,5,4,5,0),("close the joined channels",3,3,4,5,5)], .56, "IMPROVED"),
"54d0e228ca346110af05": ("for the same duration", [("for the same duration",5,5,4,5,0),("in the ordinary measure",4,4,4,5,3),("repeat it twice",3,3,4,5,5)], .55, "RETAINED"),
"90bcf0a9ec0ef56399e6": ("toward the lower outlet", [("toward the lower outlet",5,5,3,5,0),("from the lower outlet",4,4,3,5,2),("at the indicated place",4,4,3,5,2)], .53, "RETAINED"),
}

DECK_CLASS = {
"2f1c5e56e8f0ff459065": ("MEASURE_REFERENCE", "active charge", "reuse the rubric's stated measure"),
"dcda95c81a5460feb191": ("LIQUID_RELATION", "foregoing liquid or preparation", "attach it to the next charge/instruction"),
"b921a237be883a820352": ("CHARGE_POINTER", "current preparation", "make the present charge active"),
"bc4f1f5c006c74a4d26d": ("SETTLING_ACTION", "mixed liquid", "mixture rests and settles"),
"6f7ff8287eddf4da9fdb": ("MIXING_ACTION", "two or more charges", "uniform mixture"),
"276a7c2d74d1143446f4": ("APPLICATION_ACTION", "prepared substance", "substance applied or used"),
"dd0ecaf5e27d81befffc": ("PLACE_REFERENCE", "active pictured/body place", "route/application is locally bound"),
"7d25241b0e56c836372a": ("MODERATE_HEATING", "mixture in vessel", "tempered warm mixture"),
"b5fcea1eaed06b2f2291": ("LOAD_NEXT_CHARGE", "next rubric entry", "next measured charge active"),
"7db18b2f0fb7ed0fcfd3": ("LOCAL_RINSE", "liquid and active place", "liquid poured or rinsed over place"),
"de7321bface5628e35d6": ("COOLING_ACTION", "heated mixture", "ordinary-temperature mixture"),
"e0b630cb1b5df5e7105b": ("READINESS_GATE", "preparation in process", "following action licensed when ready"),
"7a4bb8136330ee4e6e56": ("LIQUID_SELECTOR", "prepared liquid available", "prepared liquid active"),
"1645e612504fcef59ced": ("VESSEL_TRANSFER", "measured charge", "charge placed in working vessel"),
"0275fbf14e07935b0a45": ("WARM_WATER_ADDITION", "working vessel", "warm-water medium present"),
"308e8ea2d5d190c498e8": ("CHARGE_MERGE", "two active charges", "combined charge active"),
"4d4559019a961b834aa1": ("SEQUENCE_ADVANCE", "completed local act", "proceed to next act"),
"b5df9126607030b95175": ("CLARITY_GATE", "flowing or settling liquid", "following action licensed at clear outflow"),
"2cc054357a929df85f64": ("HERBAL_OWNER_RESUME", "pictured plant dossier", "pictured plant restored as clause owner"),
"2cc8bb3c2af19607888f": ("CHANNEL_ROUTE", "connected path available", "liquid routed through joined channels"),
"259b2b3b0bf859882e2c": ("SINGLE_WASH_PASS", "vessel/place and liquid", "one washing pass complete"),
"9ad66e67803a12e745de": ("FRESH_PREPARATION_SELECTOR", "fresh plant preparation", "fresh preparation active"),
"9da1b6ac2c929daea697": ("ONE_CHARGE_VALUE", "measure standard", "one measured charge instantiated"),
"28ffbc88b97772a75f1e": ("DECANTING_ACTION", "settled liquid", "clear upper liquor separated"),
"87411f84689b4f93a303": ("SINGLE_BOIL_PASS", "liquid in heatable vessel", "one boil completed"),
"d904bf7b044dd3922781": ("LOW_HEAT_MODE", "heating action", "gentle-fire mode active"),
"3b70942557b3a40e8030": ("CLARIFY_BY_SETTLING", "cloudy liquid", "settled clear liquid"),
"d68bc8de3bcee09db23c": ("CLOTH_FILTRATION", "mixed liquid and cloth", "strained liquid"),
"54d0e228ca346110af05": ("DURATION_REFERENCE", "previous timed act", "same duration reused"),
"90bcf0a9ec0ef56399e6": ("LOWER_OUTLET_ROUTE", "multi-level vessel/channel", "flow directed to lower outlet"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_score(x: tuple) -> str:
    return f"context={x[1]};cross_page={x[2]};portability={x[3]};historical={x[4]};repairs={x[5]}"


def main() -> None:
    v16 = [r for r in read_tsv(V16) if r["ledger_scope"] == "GDT327_PROSE"]
    old_by_key = {(r["page"], r["locus"], r["event_index"]): r for r in v16}
    formal = list(GuardedTSV(
        GDT327, selector_column="page", allowed_values=PAGES,
        forbidden_prefixes=("f84", "f84r"),
    ))
    assert len(formal) == len(v16) == 381
    for r in formal:
        r.update(old_by_key[(r["page"], r["locus"], r["group_index"])])

    counts = Counter(r["joint_tuple_id"] for r in formal)
    recurrent = {tid for tid, n in counts.items() if n >= 3}
    assert recurrent == set(DECISIONS) and len(recurrent) == 30

    by_line: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in formal:
        by_line[(r["page"], r["locus"])].append(r)
    for rows in by_line.values():
        rows.sort(key=lambda r: int(r["group_index"]))

    decision_rows = []
    for tid in sorted(recurrent, key=lambda t: (-counts[t], t)):
        selected, rivals, confidence, status = DECISIONS[tid]
        occurrences = [r for r in formal if r["joint_tuple_id"] == tid]
        incumbent = occurrences[0]["default_English"]
        assert len(rivals) == 3
        assert any(incumbent == r[0] or incumbent.split(";")[0] in r[0] or r[0].split(";")[0] in incumbent for r in rivals), (tid, incumbent)
        decision_rows.append({
            "exact_tuple_id": tid,
            "surface_forms": "|".join(sorted({r["surface"] for r in occurrences})),
            "events": counts[tid],
            "folios": "|".join(sorted({r["page"] for r in occurrences})),
            "v16_incumbent": incumbent,
            "rival_1": rivals[0][0], "rival_1_scores": fmt_score(rivals[0]),
            "rival_2": rivals[1][0], "rival_2_scores": fmt_score(rivals[1]),
            "rival_3": rivals[2][0], "rival_3_scores": fmt_score(rivals[2]),
            "selected_default": selected, "confidence": f"{confidence:.2f}",
            "revision_status": status,
            "conditioned_second_sense": "at field entry: with it under the same rubric" if tid == "dcda95c81a5460feb191" else "",
            "technical_register_effect": {
                "2f1c5e56e8f0ff459065":"read active measure register",
                "dcda95c81a5460feb191":"reuse active liquid/relation register",
                "b921a237be883a820352":"point to current charge register",
                "bc4f1f5c006c74a4d26d":"rest/settle current mixture",
                "6f7ff8287eddf4da9fdb":"stir current mixture to uniformity",
                "276a7c2d74d1143446f4":"apply current prepared substance",
                "dd0ecaf5e27d81befffc":"read active place register",
                "7d25241b0e56c836372a":"raise current mixture to moderate heat",
                "b5fcea1eaed06b2f2291":"load next charge",
                "7db18b2f0fb7ed0fcfd3":"route liquid over active place",
                "de7321bface5628e35d6":"return mixture to ordinary temperature",
                "e0b630cb1b5df5e7105b":"gate next instruction on readiness",
                "7a4bb8136330ee4e6e56":"select prepared-liquid register",
                "1645e612504fcef59ced":"transfer charge into vessel",
                "0275fbf14e07935b0a45":"add warm-water medium",
                "308e8ea2d5d190c498e8":"merge two active charges",
                "4d4559019a961b834aa1":"advance procedural sequence",
                "b5df9126607030b95175":"gate on clear outflow",
                "2cc054357a929df85f64":"resume pictured Herbal owner",
                "2cc8bb3c2af19607888f":"select joined-channel route",
                "259b2b3b0bf859882e2c":"perform one washing pass",
                "9ad66e67803a12e745de":"select fresh preparation",
                "9da1b6ac2c929daea697":"instantiate one measured charge",
                "28ffbc88b97772a75f1e":"decant clarified supernatant",
                "87411f84689b4f93a303":"perform one boiling pass",
                "d904bf7b044dd3922781":"select low-heat mode",
                "3b70942557b3a40e8030":"settle liquid until clear",
                "d68bc8de3bcee09db23c":"filter through cloth",
                "54d0e228ca346110af05":"reuse active duration",
                "90bcf0a9ec0ef56399e6":"select lower-outlet direction",
            }[tid],
        })

    occurrence_rows = []
    affected_lines: set[tuple[str, str]] = set()
    for r in formal:
        tid = r["joint_tuple_id"]
        if tid not in recurrent:
            continue
        affected_lines.add((r["page"], r["locus"]))
        line = by_line[(r["page"], r["locus"])]
        idx = line.index(r)
        window = line[max(0, idx-2):idx+3]
        def surface_at(j: int) -> str:
            return line[j]["surface"] if 0 <= j < len(line) else ("<LINE_START>" if j < 0 else "<LINE_END>")
        selected = DECISIONS[tid][0]
        rewritten = []
        for item in window:
            gloss = DECISIONS[item["joint_tuple_id"]][0] if item["joint_tuple_id"] in recurrent else item["default_English"]
            rewritten.append(gloss)
        occurrence_rows.append({
            "page": r["page"], "locus": r["locus"], "record": r["record_ordinal"],
            "field": r["field_ordinal"], "event_index": r["group_index"],
            "surface": r["surface"], "exact_tuple_id": tid,
            "left_2": surface_at(idx-2), "left_1": surface_at(idx-1),
            "right_1": surface_at(idx+1), "right_2": surface_at(idx+2),
            "within_field_position": r["within_field_position"],
            "field_boundary_before": int(r["within_field_position"] in {"FIRST", "ONLY"}),
            "field_boundary_after": int(r["within_field_position"] in {"LAST", "ONLY"}),
            "physical_line_start": int(idx == 0), "physical_line_end": int(idx == len(line)-1),
            "dy_closure": r["dy_closure"], "b3": r["b3"],
            "v16_reading": r["default_English"], "v17_selected": selected,
            "rewritten_local_sequence": "; ".join(rewritten),
        })

    line_rows = []
    for key in sorted(affected_lines):
        line = by_line[key]
        line_rows.append({
            "page": key[0], "locus": key[1],
            "surface_sequence": " ".join(r["surface"] for r in line),
            "v17_complete_reading": "; ".join(DECISIONS[r["joint_tuple_id"]][0] if r["joint_tuple_id"] in recurrent else r["default_English"] for r in line),
            "recurrent_events": sum(r["joint_tuple_id"] in recurrent for r in line),
            "total_events": len(line),
        })

    write_tsv(OUT / "V17_R3_RECURRENT_CARD_DECISIONS.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(OUT / "V17_R3_ALL_OCCURRENCE_READINGS.tsv", occurrence_rows, list(occurrence_rows[0]))
    write_tsv(OUT / "V17_R3_AFFECTED_LINE_READINGS.tsv", line_rows, list(line_rows[0]))
    deck_rows = []
    for row in decision_rows:
        cls, requires, result = DECK_CLASS[row["exact_tuple_id"]]
        deck_rows.append({
            "exact_tuple_id": row["exact_tuple_id"], "surface_forms": row["surface_forms"],
            "deck_class": cls, "spoken_default": row["selected_default"],
            "requires_active_register": requires, "register_update_or_result": result,
            "apprentice_rule": "read the whole exact card; do not derive a new meaning from individual glyphs",
        })
    write_tsv(OUT / "V17_R3_EXECUTABLE_DECK.tsv", deck_rows, list(deck_rows[0]))

    wanted = {"f10r", "f56r", "f82r"}
    passage = [
        "# V17 R3 rewritten passages",
        "",
        "These are concrete workshop defaults, not decipherment claims. A physical line need not end a sentence; semicolons preserve card order rather than asserting syntax.",
        "",
    ]
    for page in sorted(wanted):
        passage += [f"## {page}", ""]
        for (p, locus), line in sorted(by_line.items(), key=lambda item: (item[0][0], int(item[0][1].rsplit(".", 1)[1]))):
            if p != page:
                continue
            reading = "; ".join(DECISIONS[r["joint_tuple_id"]][0] if r["joint_tuple_id"] in recurrent else r["default_English"] for r in line)
            passage += [f"- `{locus}` — {reading}"]
        passage += [""]
    (OUT / "V17_R3_REWRITTEN_PASSAGES.md").write_text("\n".join(passage), encoding="utf-8")

    retained = sum(r["revision_status"] == "RETAINED" for r in decision_rows)
    improved = sum(r["revision_status"] == "IMPROVED" for r in decision_rows)
    reversed_ = sum(r["revision_status"] == "REVERSED" for r in decision_rows)
    assert len(occurrence_rows) == 217
    assert len(decision_rows) == 30
    print(f"cards=30 occurrences={len(occurrence_rows)} affected_lines={len(line_rows)} retained={retained} improved={improved} reversed={reversed_}")


if __name__ == "__main__":
    main()
