#!/usr/bin/env python3
"""Build the V18 R1 workshop reconstruction for the six frozen disputed cards.

The script materializes only the seven authorized prose pages through the
guarded GDT327 selector.  It never reads f84/f84r.  English expansions are
deliberately concrete sidequest defaults, not decipherment claims.
"""

from __future__ import annotations

import csv
import io
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEDGER = OUT.parent / "sidequest_theory_candidates_v17" / "V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
FORMAL = ROOT / "gdt327_joint_tuple_interlinear.tsv"
PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")

# Frozen rival order follows V18_SELECTION_PROTOCOL.md.  Repair tuples count
# (silent substance, vessel, body part, comparison, antecedent, sense change).
CARDS = {
    "0275fbf14e07935b0a45": {
        "surfaces": "okeey|qokeey", "selected": 0, "confidence": ".62",
        "rivals": [
            ("keep the preparation lukewarm", (0, 0, 0, 0, 7, 0), 91),
            ("mix the preparation thoroughly", (0, 0, 0, 0, 7, 2), 74),
            ("add warmed water to the preparation", (7, 3, 0, 0, 7, 0), 61),
        ],
        "rule": "After a heating/bath choice, preserve mild warmth until rinse or application.",
        "why": "All seven copies accept inherited preparation; MIX duplicates CHEDY and ADD-WARM-WATER duplicates explicit warm-water cards.",
    },
    "de7321bface5628e35d6": {
        "surfaces": "lchedy", "selected": 1, "confidence": ".61",
        "rivals": [
            ("leave the preparation standing in the lower vessel", (0, 8, 0, 0, 8, 1), 75),
            ("let the liquid drain into the lower receiving vessel", (8, 8, 0, 0, 8, 0), 92),
            ("let the preparation cool to its ordinary setting", (0, 0, 0, 0, 8, 4), 58),
        ],
        "rule": "After immersion or washing, let the working liquid run down into the lower receiver; this closes the local step.",
        "why": "Five copies touch an explicit outlet/basin/next lower route and the others follow bath, wash, or equal mixing; DRAIN stays distinct from SETTLE and RINSE.",
    },
    "259b2b3b0bf859882e2c": {
        "surfaces": "dchedy|schedy|tchedy", "selected": 0, "confidence": ".56",
        "rivals": [
            ("finish the foregoing treatment and close its instruction", (0, 0, 0, 0, 4, 0), 86),
            ("strain the foregoing preparation and set it aside", (4, 1, 0, 0, 4, 2), 67),
            ("wash the treated place through once", (4, 0, 4, 0, 4, 2), 62),
        ],
        "rule": "Close the carried instruction before the following preparation begins.",
        "why": "Three copies occur at physical-line entry and introduce a visibly new operation chain; the remaining copy follows passage through channels.",
    },
    "28ffbc88b97772a75f1e": {
        "surfaces": "olchedy|qolchedy", "selected": 0, "confidence": ".55",
        "rivals": [
            ("reserve the mixed liquid for the following step", (3, 1, 0, 0, 3, 0), 87),
            ("draw off the clear liquor", (3, 2, 0, 0, 3, 2), 64),
            ("retain the mixture together in the working vessel", (3, 3, 0, 0, 3, 1), 81),
        ],
        "rule": "Set aside the just-combined liquid without discarding it; retrieve or enlarge it in the next cell.",
        "why": "Every copy is followed by ADD or NEXT; none supplies the settling/clarity prerequisite expected by DRAW-OFF-CLEAR.",
    },
    "4d4559019a961b834aa1": {
        "surfaces": "char|dar|sar", "selected": 2, "confidence": ".54",
        "rivals": [
            ("take material from the same batch", (5, 0, 0, 0, 5, 1), 82),
            ("continue then with the following step", (0, 0, 0, 0, 5, 1), 73),
            ("repeat the foregoing preparation using the same batch", (5, 0, 0, 0, 5, 0), 88),
        ],
        "rule": "Repeat the immediately preceding preparation, retaining its batch as the inherited material.",
        "why": "The repeat expansion completes both line-final copies and explains OKAIN-CHAR-OKAIN; SAME-BATCH alone often dangles, while bare THEN loses the recurring material identity.",
    },
    "2cc054357a929df85f64": {
        "surfaces": "cho|sho", "selected": 2, "confidence": ".57",
        "rivals": [
            ("thereafter take the following detail", (0, 0, 0, 0, 4, 0), 78),
            ("resume the pictured plant topic", (0, 0, 0, 0, 4, 1), 72),
            ("take the upper flowering parts of the pictured plant", (4, 0, 0, 0, 4, 0), 89),
        ],
        "rule": "On f56r only, select the pictured plant's upper flowering parts; the following card supplies medium, companion part, or preparation.",
        "why": "The four copies precede lower root, wine, dried leaf, and fresh preparation, forming a repeated page-owned plant-part address rather than four different senses.",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def guarded_formal() -> list[dict[str, str]]:
    cols = ["page", "locus", "group_index", "record_ordinal", "field_ordinal",
            "within_field_position", "joint_tuple_id", "line_first", "prev_dy",
            "dy_closure", "b3"]
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(FORMAL), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--forbid-prefix", "f84", "--columns", ",".join(cols)]
    p = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return list(csv.DictReader(io.StringIO(p.stdout), delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def rep_text(rep: tuple[int, ...]) -> str:
    names = ("silent_substance", "vessel", "body_part", "comparison", "antecedent", "sense_change")
    return ";".join(f"{k}={v}" for k, v in zip(names, rep)) + f";total={sum(rep)}"


def gloss(row: dict[str, str]) -> str:
    card = CARDS.get(row["exact_tuple_id"])
    return card["rivals"][card["selected"]][0] if card else row["default_English"]


def main() -> None:
    prose = [r for r in read_tsv(LEDGER) if r["ledger_scope"] == "GDT327_PROSE"]
    formal = guarded_formal()
    if len(prose) != 381 or len(formal) != 381:
        raise SystemExit(f"sealed census mismatch prose={len(prose)} formal={len(formal)}")
    fidx = {(r["locus"], r["group_index"]): r for r in formal}
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    page_loci: dict[str, list[str]] = defaultdict(list)
    for row in prose:
        by_locus[row["locus"]].append(row)
        if row["locus"] not in page_loci[row["page"]]:
            page_loci[row["page"]].append(row["locus"])
    for rows in by_locus.values(): rows.sort(key=lambda r: int(r["event_index"]))
    by_record: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for page, loci in page_loci.items():
        for locus in loci:
            for event in by_locus[locus]:
                rec = fidx[(locus, event["event_index"])]["record_ordinal"]
                by_record[(page, rec)].append(event)

    decision_rows = []
    for tid, card in CARDS.items():
        occ = [r for r in prose if r["exact_tuple_id"] == tid]
        if len(occ) not in (3, 4, 5, 7, 8): raise SystemExit(f"bad target count {tid}={len(occ)}")
        rivals = card["rivals"]
        decision_rows.append({
            "exact_tuple_id": tid, "surface_examples": card["surfaces"],
            "occurrences": len(occ), "pages": "|".join(sorted({r["page"] for r in occ})),
            "rival_1": rivals[0][0], "rival_1_score_100": rivals[0][2], "rival_1_repairs": rep_text(rivals[0][1]),
            "rival_2": rivals[1][0], "rival_2_score_100": rivals[1][2], "rival_2_repairs": rep_text(rivals[1][1]),
            "rival_3": rivals[2][0], "rival_3_score_100": rivals[2][2], "rival_3_repairs": rep_text(rivals[2][1]),
            "selected_rival": card["selected"] + 1, "selected_meaning": rivals[card["selected"]][0],
            "confidence": card["confidence"], "workshop_rule": card["rule"], "selection_reason": card["why"],
        })

    occurrence_rows = []
    affected_loci = set()
    for row in prose:
        card = CARDS.get(row["exact_tuple_id"])
        if not card: continue
        affected_loci.add(row["locus"])
        locrows = by_locus[row["locus"]]
        j = next(i for i, x in enumerate(locrows) if x["source_event_serial"] == row["source_event_serial"])
        meta = fidx[(row["locus"], row["event_index"])]
        field = [x for x in locrows if fidx[(x["locus"], x["event_index"])]["field_ordinal"] == meta["field_ordinal"]]
        loci = page_loci[row["page"]]; li = loci.index(row["locus"])
        prev_line = by_locus[loci[li-1]] if li else []
        next_line = by_locus[loci[li+1]] if li + 1 < len(loci) else []
        prior = locrows[:j]
        after = locrows[j+1:]
        selected = card["rivals"][card["selected"]][0]
        record = by_record[(row["page"], meta["record_ordinal"])]
        # The graphs deliberately show the complete carried state on each side.
        before_state = " → ".join(gloss(x) for x in prior) or "pictured/page-owned preparation already active"
        after_state = " → ".join(gloss(x) for x in after) or "carry completed result into the following physical line"
        base = [gloss(x) for x in locrows]
        rivals_full = []
        for meaning, repairs, score in card["rivals"]:
            seq = base.copy(); seq[j] = meaning
            rivals_full.append("; ".join(seq))
        occurrence_rows.append({
            "exact_tuple_id": row["exact_tuple_id"], "surface": row["surface"], "page": row["page"],
            "locus": row["locus"], "event_index": row["event_index"], "record_ordinal": meta["record_ordinal"],
            "field_ordinal": meta["field_ordinal"], "within_field_position": meta["within_field_position"],
            "line_first": meta["line_first"], "prev_dy": meta["prev_dy"], "dy_closure": meta["dy_closure"], "b3": meta["b3"],
            "previous_physical_line_surface": " ".join(x["surface"] for x in prev_line) or "PAGE_START",
            "previous_physical_line_reading": "; ".join(gloss(x) for x in prev_line) or "PAGE_START",
            "complete_field_surface": " ".join(x["surface"] for x in field),
            "complete_field_reading": "; ".join(gloss(x) for x in field),
            "complete_physical_line_surface": " ".join(x["surface"] for x in locrows),
            "complete_record_surface": " ".join(x["surface"] for x in record),
            "complete_record_reading": "; ".join(gloss(x) for x in record),
            "process_state_before_target": before_state,
            "selected_meaning": selected,
            "process_state_after_target": after_state,
            "process_graph": f"{before_state} → [{selected}] → {after_state}",
            "next_physical_line_surface": " ".join(x["surface"] for x in next_line) or "PAGE_END",
            "next_physical_line_reading": "; ".join(gloss(x) for x in next_line) or "PAGE_END",
            "rival_1_complete_line": rivals_full[0], "rival_1_repairs": rep_text(card["rivals"][0][1]),
            "rival_2_complete_line": rivals_full[1], "rival_2_repairs": rep_text(card["rivals"][1][1]),
            "rival_3_complete_line": rivals_full[2], "rival_3_repairs": rep_text(card["rivals"][2][1]),
            "selected_complete_line": "; ".join(base),
        })

    if len(occurrence_rows) != 31:
        raise SystemExit(f"expected 31 target events, got {len(occurrence_rows)}")
    write_tsv(OUT / "V18_R1_SIX_CARD_DECISIONS.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(OUT / "V18_R1_31_OCCURRENCE_RECONSTRUCTIONS.tsv", occurrence_rows, list(occurrence_rows[0]))

    md = ["# V18 R1 — complete affected passages", "",
          "Every target is shown in its complete physical line, with the preceding and",
          "following physical line. Line breaks are copying/reflow opportunities, not",
          "automatic sentence ends. Bracketed arguments remain inherited from picture or",
          "prior step; no target is left semantically empty.", ""]
    seen = set()
    for occ in occurrence_rows:
        key = (occ["page"], occ["locus"])
        if key in seen: continue
        seen.add(key)
        md += [f"## {occ['locus']}", "",
               f"- Previous: `{occ['previous_physical_line_surface']}`",
               f"  — {occ['previous_physical_line_reading']}",
               f"- Target line: `{occ['complete_physical_line_surface']}`",
               f"  — {occ['selected_complete_line']}",
               f"- Following: `{occ['next_physical_line_surface']}`",
               f"  — {occ['next_physical_line_reading']}", ""]
        for same in [x for x in occurrence_rows if x["page"] == occ["page"] and x["locus"] == occ["locus"]]:
            md += [f"**{same['surface']} process graph:** `{same['process_graph']}`", ""]
    md += ["## Complete affected records/articles", ""]
    seen_records = set()
    for occ in occurrence_rows:
        key = (occ["page"], occ["record_ordinal"])
        if key in seen_records: continue
        seen_records.add(key)
        md += [f"### {occ['page']} record {occ['record_ordinal']}", "",
               f"`{occ['complete_record_surface']}`", "",
               occ["complete_record_reading"], ""]
    (OUT / "V18_R1_COMPLETE_AFFECTED_PASSAGES.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    report = [
        "# V18 R1 — workshop-master six-card reconstruction", "", "Date: 2026-08-21", "",
        "Status: **maximally abductive concrete workshop reading, not deciphered plaintext**.", "",
        "## Decision", "",
        "A novice can learn the six disputed cards as a compact set of non-overlapping instructions:", "",
        "```text",
        "OKEEY   preserve lukewarm working temperature",
        "LCHEDY  drain into the lower receiver and close the step",
        "DCHEDY  close the foregoing treatment before a new chain",
        "OLCHEDY reserve the mixed liquor for the following step",
        "CHAR    repeat the foregoing preparation with the same batch",
        "CHO     on f56r, take the pictured plant's upper flowering parts",
        "```", "",
        "The strongest revision is `LCHEDY`: **drain into the lower receiving vessel**.",
        "It repeatedly follows immersion, washing, or mixing and is repeatedly adjacent to",
        "a lower outlet, lower basin, or renewed lower route. Standing would overlap",
        "`OLKEEDY = settle`; cooling would overlap the already explicit COOL cards.", "",
        "The second revision is `CHAR`: **repeat the foregoing preparation using the same",
        "batch**. This retains the incumbent material continuity but turns the line-final",
        "copies and `OKAIN CHAR OKAIN` into executable apprentice instructions.", "",
        "The third revision is page-local `CHO`: **take the upper flowering parts of the",
        "pictured plant**. Its four positions now enumerate root/upper parts, upper parts in",
        "wine, upper parts with dried leaf, and fresh upper parts with honey. This is one",
        "page-owned sense, not four improvised plant parts.", "",
        "## Concrete process reading", "",
        "```text",
        "take/add measured portion",
        "→ mix evenly",
        "→ warm once or bathe",
        "→ OKEEY: maintain lukewarm condition",
        "→ rinse/apply",
        "→ LCHEDY: drain to lower receiver",
        "→ OLCHEDY: reserve the compounded liquor when it is to be reused",
        "→ DCHEDY: finish the carried treatment",
        "→ CHAR: repeat from the same batch where instructed",
        "```", "",
        "## Why this is teachable around 1420", "",
        "The apprentice memorizes six whole brevigraph cards, not a letterwise cipher.",
        "Objects remain active until replaced: the pictured simple in Herbal and the current",
        "liquor, vessel, opening, or treated place in Biological. A line break merely causes",
        "reflow. The four close-bearing cards are deliberately distinct: settle, reserve,",
        "drain, and finish. Such take–measure–heat–strain–apply sequences and mixed herbal,",
        "bath, and astrological material are ordinary in fifteenth-century medical",
        "miscellanies; that historical fit licenses the workflow, not any literal card value.", "",
        "Three period controls keep the reconstruction historically ordinary: British",
        "Library [Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567)",
        "contains a dated 1446 medical miscellany with recipe language of taking and",
        "seething-until; [Harley MS 2375](https://searcharchives.bl.uk/catalog/040-002048206)",
        "combines a Macer herbal, hot/humid baths, clysters, oils, recipes, and medical",
        "astrology; and [Harley MS 2381](https://searcharchives.bl.uk/catalog/040-002048212)",
        "combines hundreds of medical recipes with waters, plasters, distillation, and",
        "astrological tables. They support a teachable TAKE–HEAT–DRAIN–APPLY workflow and",
        "a mixed-volume ecology; they do not identify any Voynich form.", "",
        "## Costs and surviving rivals", "",
        "`OKEEY = MIX` remains locally readable but collides with `CHEDY` twice; warmed-water",
        "addition requires a silent water argument in every copy. `LCHEDY = STAND` remains",
        "the main rival but duplicates SETTLE and underuses the repeated lower-route context.",
        "`OLCHEDY = RETAIN IN WORKING VESSEL` is close to RESERVE but explains following NEXT",
        "less well. `DCHEDY = STRAIN/WASH` requires a new material or body argument and fails",
        "to explain three line-entry resets. Bare `CHAR = THEN` discards batch identity.",
        "`CHO = THEREAFTER` remains the strongest nonlexical rival but leaves f56r's repeated",
        "plant-part inventory needlessly implicit.", "",
        "## Coverage and seal", "",
        f"All {len(occurrence_rows)}/31 target occurrences are reconstructed with field, line,",
        "previous line, following line, three full-line rivals, repair counts, and an explicit",
        "before/target/after process graph. Only guarded f84-free GDT327 prose rows from the",
        "seven authorized pages were materialized. f84 and f84r were never opened.",
    ]
    (OUT / "CANDIDATE_V18_R1_WORKSHOP_MASTER.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"cards={len(decision_rows)} occurrences={len(occurrence_rows)} affected_lines={len(seen)}")


if __name__ == "__main__":
    main()
