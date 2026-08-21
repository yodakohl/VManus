#!/usr/bin/env python3
"""Build R1's complete recurrent-card teaching deck for sidequest V17.

This is deliberately abductive translation play, not a decipherment result.
Only the seven authorized f84-free prose pages are loaded.  Mixed formal data
is materialized through the repository's guarded TSV command.
"""

from __future__ import annotations

import csv
import io
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V16 = ROOT / "experiments/yolo/sidequest_theory_candidates_v16"
PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
LEDGER = V16 / "V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv"
FORMAL = ROOT / "gdt327_joint_tuple_interlinear.tsv"


# tuple_id: incumbent, rival 2, rival 3, selected, optional conditioned sense,
# confidence, status, three score vectors (fit, consistency, portability,
# historical plausibility, silent/special repairs).  Totals are the first four
# fields minus repairs.
DECISIONS = {
"2f1c5e56e8f0ff459065": ("in the stated or usual measure", "for the stated interval", "in equal portions", "by the stated or usual measure", "", ".62", "RETAINED_REPHRASED", (5,5,5,5,1),(3,3,4,5,3),(4,3,4,5,2)),
"dcda95c81a5460feb191": ("with it; likewise under the same heading", "with the preceding preparation", "continue the same procedure", "with the preceding preparation", "At physical entry: likewise with the same preparation.", ".65", "IMPROVED", (4,5,5,5,1),(5,5,5,5,0),(4,4,5,5,1)),
"b921a237be883a820352": ("this portion", "this liquid", "repeat this step", "this portion", "", ".58", "RETAINED", (5,5,5,5,0),(4,3,4,5,2),(3,3,4,4,3)),
"bc4f1f5c006c74a4d26d": ("set ready in the usual manner; close the rubric", "let it stand and end the instruction", "the preparation is finished", "set it ready, then end this instruction", "", ".51", "RETAINED_REPHRASED", (5,5,5,5,0),(5,4,5,5,1),(4,5,5,5,1)),
"6f7ff8287eddf4da9fdb": ("mix until even", "stir it thoroughly", "perform the usual preparation", "mix until even", "", ".55", "RETAINED", (5,5,5,5,0),(5,5,5,5,0),(3,4,5,4,1)),
"276a7c2d74d1143446f4": ("use the lesser portion", "apply or use this portion", "take the second portion", "apply or use this portion", "After an explicit measure: use the measured portion.", ".54", "REVERSED", (3,3,4,4,3),(5,5,5,5,1),(3,3,4,4,3)),
"dd0ecaf5e27d81befffc": ("at the indicated place", "into the lower vessel", "at that same place", "at the indicated place", "", ".49", "RETAINED", (5,5,5,5,0),(4,3,3,5,2),(5,4,5,5,1)),
"7d25241b0e56c836372a": ("use the tempered warm medium; close the rubric", "immerse in warm water, then stop", "add warm liquid, then stop", "bathe or immerse in the tempered warm liquid, then stop", "", ".47", "IMPROVED", (5,5,5,5,1),(5,4,5,5,1),(4,4,5,5,2)),
"b5fcea1eaed06b2f2291": ("take up the next entry", "take the next portion", "add the usual liquid", "take up the next portion or instruction", "After a committed cell: take up the next instruction.", ".69", "RETAINED_REPHRASED", (5,5,5,5,0),(5,5,5,5,0),(3,3,5,4,3)),
"7db18b2f0fb7ed0fcfd3": ("rinse or pour over the local place; close the rubric", "wash the part once, then stop", "draw off the liquid, then stop", "rinse or pour over the local place, then stop", "", ".48", "RETAINED_REPHRASED", (5,5,5,5,0),(5,4,5,5,1),(4,3,5,5,2)),
"de7321bface5628e35d6": ("leave at the ordinary base setting; close the rubric", "leave it to stand, then stop", "return it to the lower basin, then stop", "leave it to stand in its place, then stop", "", ".46", "IMPROVED", (3,4,5,3,2),(5,5,5,5,0),(4,3,5,5,2)),
"e0b630cb1b5df5e7105b": ("when prepared and ready", "when it has warmed", "when the mixture is complete", "when the preparation is ready", "", ".52", "RETAINED_REPHRASED", (5,5,5,5,0),(3,3,4,5,2),(5,4,5,5,1)),
"7a4bb8136330ee4e6e56": ("the prepared liquid", "from the foregoing material", "the decoction", "the prepared liquid", "In an inherited relation: liquid from the foregoing batch.", ".44", "RETAINED", (5,4,5,5,1),(4,4,5,5,1),(4,3,4,5,2)),
"1645e612504fcef59ced": ("then put it in", "add one measured ingredient", "pour it into the vessel", "put or add it into the vessel", "", ".50", "IMPROVED", (5,5,5,5,0),(4,4,5,5,2),(5,4,5,5,1)),
"0275fbf14e07935b0a45": ("keep gently warmed", "mix thoroughly", "keep the vessel in motion", "keep gently warmed", "", ".56", "RETAINED", (5,5,5,5,0),(4,4,5,5,1),(3,3,5,4,2)),
"308e8ea2d5d190c498e8": ("combine the two portions", "work it in warm clean water", "join it to the preceding mixture", "combine the two portions", "", ".50", "RETAINED", (5,5,5,5,0),(4,3,5,5,2),(5,4,5,5,1)),
"4d4559019a961b834aa1": ("of the same", "then continue", "from the same batch", "from the same batch", "", ".50", "IMPROVED", (4,4,5,5,1),(3,3,5,5,2),(5,5,5,5,0)),
"b5df9126607030b95175": ("until it becomes clear", "until it cools", "until the opening clears", "until the liquid runs clear", "In Herbal: until the expressed liquid runs clear.", ".51", "RETAINED_REPHRASED", (5,5,5,5,0),(3,3,5,5,2),(4,4,5,5,1)),
"2cc054357a929df85f64": ("thereafter", "take the same plant part again", "resume the foregoing topic", "then, thereafter", "", ".48", "RETAINED_REPHRASED", (5,5,4,5,0),(3,3,3,4,3),(4,4,4,5,1)),
"2cc8bb3c2af19607888f": ("through the joined channels", "immerse it in the conduit", "with the connected apparatus", "through the connected channels", "", ".47", "RETAINED_REPHRASED", (5,5,5,5,0),(4,4,5,5,1),(5,4,5,5,1)),
"259b2b3b0bf859882e2c": ("finish this application; close the rubric", "remove the person and stop", "let the liquid drain and stop", "finish this application, then stop", "", ".45", "RETAINED_REPHRASED", (5,5,5,5,0),(3,3,5,5,2),(4,3,5,5,2)),
"9ad66e67803a12e745de": ("use the fresh preparation", "take the fresh plant part", "apply the fresh juice", "use the fresh preparation", "", ".48", "RETAINED", (5,5,4,5,0),(4,4,4,5,1),(4,4,4,5,1)),
"9da1b6ac2c929daea697": ("one measured share", "one vesselful", "the first portion", "one measured portion", "", ".46", "RETAINED_REPHRASED", (5,5,5,5,0),(4,3,5,5,2),(4,4,5,5,1)),
"28ffbc88b97772a75f1e": ("retain the combined mixture; close the rubric", "cover the joined mixture, then stop", "leave both portions together, then stop", "keep the combined mixture together, then stop", "", ".47", "RETAINED_REPHRASED", (5,5,5,5,0),(4,4,5,5,1),(5,5,5,5,0)),
"87411f84689b4f93a303": ("heat once; close the rubric", "stir once, then stop", "warm for one interval, then stop", "heat it once, then stop", "", ".43", "RETAINED_REPHRASED", (5,5,5,5,0),(3,3,5,5,2),(4,4,5,5,1)),
"d904bf7b044dd3922781": ("at gentle heat", "with a small portion", "at the lower basin", "over gentle heat", "", ".45", "RETAINED_REPHRASED", (5,5,5,5,0),(3,3,5,4,2),(3,3,5,5,2)),
"3b70942557b3a40e8030": ("let it settle; close the rubric", "let it cool, then stop", "draw off the clear part, then stop", "let it settle, then stop", "", ".47", "RETAINED_REPHRASED", (5,5,5,5,0),(4,3,5,5,2),(4,4,5,5,1)),
"d68bc8de3bcee09db23c": ("strain completely; close the rubric", "rinse twice, then stop", "empty both channels, then stop", "strain it completely, then stop", "", ".49", "RETAINED_REPHRASED", (5,5,5,5,0),(3,3,5,5,2),(3,3,5,5,2)),
"54d0e228ca346110af05": ("for the same duration", "in the same measure", "for one further interval", "for the same interval", "", ".46", "RETAINED_REPHRASED", (5,5,5,5,0),(4,3,5,5,2),(4,4,5,5,1)),
"90bcf0a9ec0ef56399e6": ("toward the lower outlet", "at the lower vessel", "through the next opening", "toward the lower outlet", "", ".43", "RETAINED", (5,5,5,5,0),(4,4,5,5,1),(4,4,5,5,1)),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_formal() -> list[dict[str, str]]:
    cols = ["page", "locus", "group_index", "group_count", "record_ordinal",
            "field_ordinal", "within_field_position", "joint_tuple_id",
            "line_first", "prev_dy", "dy_closure", "b3"]
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(FORMAL),
           "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--forbid-prefix", "f84", "--columns", ",".join(cols)]
    result = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def score_text(v: tuple[int, int, int, int, int]) -> str:
    return (f"fit={v[0]};cross_page={v[1]};portability={v[2]};"
            f"historical={v[3]};repairs={v[4]};total={sum(v[:4])-v[4]}")


def main() -> None:
    prose = [r for r in read_tsv(LEDGER) if r["ledger_scope"] == "GDT327_PROSE"]
    formal = guarded_formal()
    fidx = {(r["locus"], r["group_index"]): r for r in formal}
    if len(prose) != 381 or len(formal) != 381:
        raise SystemExit(f"expected 381 events, got prose={len(prose)} formal={len(formal)}")
    counts = Counter(r["exact_tuple_id"] for r in prose)
    recurrent = {tid for tid, n in counts.items() if n >= 3}
    if recurrent != set(DECISIONS) or len(recurrent) != 30:
        raise SystemExit(f"decision census mismatch: recurrent={len(recurrent)} decisions={len(DECISIONS)}")

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in prose:
        by_locus[r["locus"]].append(r)
    for group in by_locus.values():
        group.sort(key=lambda r: int(r["event_index"]))

    decision_rows = []
    occurrence_rows = []
    for tid in sorted(recurrent, key=lambda x: (-counts[x], x)):
        inc, r2, r3, selected, second, conf, status, s1, s2, s3 = DECISIONS[tid]
        occ = [r for r in prose if r["exact_tuple_id"] == tid]
        surfaces = sorted({r["surface"] for r in occ})
        pages = sorted({r["page"] for r in occ})
        decision_rows.append({
            "exact_tuple_id": tid, "surface_examples": "|".join(surfaces),
            "events": len(occ), "pages": "|".join(pages),
            "rival_1_v16_incumbent": inc, "rival_1_score": score_text(s1),
            "rival_2": r2, "rival_2_score": score_text(s2),
            "rival_3": r3, "rival_3_score": score_text(s3),
            "selected_default": selected, "conditioned_second_sense": second,
            "confidence": conf, "revision_status": status,
            "workshop_rule": "Learn the exact card as one whole brevigraph; wrappers do not alter this deck meaning.",
        })
        for r in occ:
            group = by_locus[r["locus"]]
            j = next(i for i, x in enumerate(group) if x["source_event_serial"] == r["source_event_serial"])
            window = group[max(0, j-2): j+3]
            rewritten = []
            for x in group:
                d = DECISIONS.get(x["exact_tuple_id"])
                gloss = d[3] if d else x["default_English"]
                rewritten.append(gloss)
            meta = fidx[(r["locus"], r["event_index"])]
            occurrence_rows.append({
                "exact_tuple_id": tid, "surface": r["surface"], "page": r["page"],
                "locus": r["locus"], "event_index": r["event_index"],
                "record_ordinal": meta["record_ordinal"],
                "field_ordinal": meta["field_ordinal"],
                "within_field_position": meta["within_field_position"],
                "line_first": meta["line_first"], "prev_dy": meta["prev_dy"],
                "dy_closure": meta["dy_closure"], "b3": meta["b3"],
                "left_2_to_right_2_surfaces": " | ".join(x["surface"] for x in window),
                "v16_local_readings": " | ".join(x["default_English"] for x in window),
                "selected_default": selected,
                "rewritten_complete_physical_line": "; ".join(rewritten),
                "occurrence_fit": "FITS" if s1[0] >= 4 or selected != inc else "FITS_WITH_INHERITED_ARGUMENT",
            })

    write_tsv(OUT / "V17_R1_RECURRENT_CARD_DECISIONS.tsv", decision_rows,
              ["exact_tuple_id", "surface_examples", "events", "pages",
               "rival_1_v16_incumbent", "rival_1_score", "rival_2", "rival_2_score",
               "rival_3", "rival_3_score", "selected_default",
               "conditioned_second_sense", "confidence", "revision_status", "workshop_rule"])
    write_tsv(OUT / "V17_R1_ALL_OCCURRENCE_READINGS.tsv", occurrence_rows,
              ["exact_tuple_id", "surface", "page", "locus", "event_index", "record_ordinal",
               "field_ordinal", "within_field_position", "line_first", "prev_dy",
               "dy_closure", "b3", "left_2_to_right_2_surfaces",
               "v16_local_readings", "selected_default",
               "rewritten_complete_physical_line", "occurrence_fit"])

    affected = sorted({r["locus"] for r in occurrence_rows})
    out = ["# V17 R1 — rewritten passages", "",
           "These are concrete workshop readings, not decipherment claims. A physical",
           "line ending is treated as reflow unless a card itself closes the instruction.", ""]
    for page in ("f10r", "f56r", "f82r"):
        out += [f"## Complete {page}", ""]
        for locus in sorted((x for x in by_locus if x.startswith(page + ".")),
                            key=lambda x: int(x.rsplit(".", 1)[1])):
            group = by_locus[locus]
            surface = " ".join(x["surface"] for x in group)
            reading = "; ".join(DECISIONS.get(x["exact_tuple_id"], (None,None,None,x["default_English"]))[3] for x in group)
            out += [f"- `{locus}` — `{surface}`", f"  — {reading}", ""]
        kind = "illustrated simple article" if page != "f82r" else "bath/application record page"
        out += [f"**Whole-page reading:** {page} is a continuous {kind}; its physical lines",
                "carry clauses across available spaces rather than delimiting every statement.", ""]
    out += ["## Every other affected physical line", ""]
    for locus in affected:
        if locus.startswith(("f10r.", "f56r.", "f82r.")):
            continue
        group = by_locus[locus]
        surface = " ".join(x["surface"] for x in group)
        reading = "; ".join(DECISIONS.get(x["exact_tuple_id"], (None,None,None,x["default_English"]))[3] for x in group)
        out += [f"- `{locus}` — `{surface}`", f"  — {reading}", ""]
    (OUT / "V17_R1_REWRITTEN_PASSAGES.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    retained = [r for r in decision_rows if r["revision_status"].startswith("RETAINED")]
    improved = [r for r in decision_rows if r["revision_status"] == "IMPROVED"]
    reversed_ = [r for r in decision_rows if r["revision_status"] == "REVERSED"]
    report = [
        "# V17 R1 — common teaching deck candidate", "",
        "Date: 2026-08-21", "",
        "Status: **maximally abductive sidequest candidate, not decipherment**.", "",
        "## Result", "",
        f"The deck contains all 30 recurrent exact cards and all {len(occurrence_rows)} occurrences.",
        "Each card has exactly three concrete rival expansions. The selected reading is",
        "a whole-card workshop expansion: a novice memorizes the card, sees its inherited",
        "picture/rubric argument, and reads through physical line breaks until a close.", "",
        "The strongest correction is `OKY/QOKY`: **apply or use this portion** replaces",
        "V16's needlessly specific *lesser portion*. The contexts license use/application",
        "but do not repeatedly furnish a comparison that would make it lesser. `OR` remains",
        "**prepared liquid**, `OKEEY/QOKEEY` remains **keep gently warmed**, `CHEDY` remains",
        "**mix until even**, and `CKHY` remains **through the connected channels**.", "",
        "## Teachable production rule", "",
        "1. Copy the picture or page rubric first; it supplies the silent subject.",
        "2. Choose an open article card in Herbal or a short action cell in Biological.",
        "3. Read common cards as whole brevigraphs, never letter by letter.",
        "4. Inherit preparation, vessel, body-place and measure until explicitly changed.",
        "5. Treat a physical line end as available-space reflow; a close-bearing card ends",
        "   only its local instruction.", "",
        "## Priority decisions", "",
        "| family | selected concrete reading |", "|---|---|",
        "| OKEEY/QOKEEY | keep gently warmed |",
        "| CHEDY | mix until even |",
        "| OKY/QOKY | apply or use this portion |",
        "| OR | the prepared liquid |",
        "| OKAIN/QOKAIN | put or add it into the vessel |",
        "| OKAL/QOKAL | combine the two portions |",
        "| VAL-Q | leave it to stand in its place, then stop |",
        "| VAL-QE | bathe/immerse in tempered warm liquid, then stop |",
        "| VAL-S | set ready, then end this instruction |",
        "| VAL-L | rinse/pour over the local place, then stop |",
        "| CHAR/DAR/SAR | from the same batch |",
        "| CHO/SHO | then, thereafter |",
        "| CKHY | through the connected channels |", "",
        "## V16 disposition", "",
        f"- retained or concretely rephrased: {len(retained)} cards",
        f"- improved without reversing the action family: {len(improved)} cards",
        f"- reversed: {len(reversed_)} card (`OKY/QOKY`)", "",
        "Retained/rephrased: " + ", ".join(r["surface_examples"] for r in retained) + ".", "",
        "Improved: " + ", ".join(r["surface_examples"] for r in improved) + ".", "",
        "Reversed: " + ", ".join(r["surface_examples"] for r in reversed_) + ".", "",
        "## Remaining concrete weaknesses", "",
        "The four close-bearing value cards remain an action-plus-close deck rather than",
        "four externally identified processes. `OR` still needs its conditioned *from the",
        "foregoing batch* sense in some inherited relations. These are explicit rival",
        "meanings, not empty placeholders. No card is withdrawn from concrete reading.", "",
        "## Seal", "",
        "Only f10r, f11r, f55v, f56r, f81v, f82r and f83r were loaded through",
        "the guarded f84-free page selection. The Astro readings were not used to infer",
        "prose identities. f84 and f84r were not opened.",
    ]
    (OUT / "CANDIDATE_V17_R1_WORKSHOP_TEACHING_DECK.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"cards={len(decision_rows)} occurrences={len(occurrence_rows)} affected_lines={len(affected)}")


if __name__ == "__main__":
    main()
