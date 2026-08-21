#!/usr/bin/env python3
"""Build the independent V18 R3 technical-register reconstruction.

The source tuple is treated as an exact whole card.  Internal coordinates are
never used.  The guarded query materializes only the five permitted prose
pages that contain the six frozen target cards; f84/f84r are rejected before
row materialization.
"""

from __future__ import annotations

import csv
import io
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FORMAL = ROOT / "gdt327_joint_tuple_interlinear.tsv"
LEDGER = OUT.parent / "sidequest_theory_candidates_v17" / "V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ("f10r", "f56r", "f81v", "f82r", "f83r")

CARDS = {
    "0275fbf14e07935b0a45": {
        "surface": "OKEEY/QOKEEY",
        "selected": "add warmed water to the active vessel",
        "confidence": ".74",
        "transition": "WATER[warmed] enters VESSEL; MIXTURE becomes diluted and warm",
        "candidates": [
            ("keep the active preparation lukewarm", 78, "material=7;vessel=0;body=0;comparison=0;antecedent=7", 3,
             "collides with SOLSHEDY/heat cards and becomes immediate near-repetition on f82r.7"),
            ("mix the active preparation thoroughly", 64, "material=7;vessel=5;body=0;comparison=0;antecedent=7", 6,
             "duplicates CHEDY and follows/falls near explicit combining or stirring too often"),
            ("add warmed water to the active vessel", 94, "material=7;vessel=5;body=0;comparison=0;antecedent=0", 0,
             "supplies a missing input before straining, immersion, rinsing and application while preserving distinct heat cards"),
        ],
    },
    "de7321bface5628e35d6": {
        "surface": "LCHEDY",
        "selected": "drain the whole liquid into the lower receiving vessel",
        "confidence": ".71",
        "transition": "ACTIVE_VESSEL empties through LOWER_ROUTE into RECEIVER; whole liquid, not only clear upper fraction, moves",
        "candidates": [
            ("leave the preparation standing in the lower vessel", 82, "material=8;vessel=8;body=0;comparison=0;antecedent=0", 3,
             "fits immersion but duplicates OLKEEDY/SHEDY settling and is poor before LET_ENTER on f83r.37"),
            ("drain the whole liquid into the lower receiving vessel", 92, "material=8;vessel=7;body=0;comparison=0;antecedent=0", 0,
             "explains lower-outlet closures, upper-channel opening, wash cycles and empty-before-refill sequence"),
            ("let the preparation cool to the ordinary setting", 80, "material=8;vessel=0;body=0;comparison=0;antecedent=0", 4,
             "excellent before application on f83r.6 but does not explain outlet/channel ecology on f83r.11/.37/.41"),
        ],
    },
    "259b2b3b0bf859882e2c": {
        "surface": "DCHEDY/SCHEDY/TCHEDY",
        "selected": "wash the active vessel or route through once",
        "confidence": ".66",
        "transition": "one rinse charge traverses ACTIVE_ROUTE; route/vessel is clean and ready for the next charge",
        "candidates": [
            ("finish the preceding treatment", 69, "material=0;vessel=0;body=0;comparison=0;antecedent=4", 4,
             "can close a carried instruction but contributes no operation before decant/add/boil sequences"),
            ("strain the liquid once", 76, "material=4;vessel=4;body=0;comparison=0;antecedent=0", 3,
             "fits channel and decant contexts but duplicates the explicit SHCKHEDY cloth-straining card"),
            ("wash the active vessel or route through once", 89, "material=4;vessel=4;body=0;comparison=0;antecedent=0", 0,
             "one repeated apparatus-cleaning pass works field-only, after channels, and before loading a fresh batch"),
        ],
    },
    "28ffbc88b97772a75f1e": {
        "surface": "OLCHEDY/QOLCHEDY",
        "selected": "draw off the clear upper liquor into the receiver",
        "confidence": ".78",
        "transition": "CLEAR_SUPERNATANT transfers to RECEIVER; sediment/residue remains in source vessel",
        "candidates": [
            ("reserve the combined liquid in its vessel", 73, "material=3;vessel=3;body=0;comparison=0;antecedent=0", 2,
             "possible batch close but weak before immediate loading and channel routing"),
            ("draw off the clear upper liquor into the receiver", 94, "material=3;vessel=3;body=0;comparison=0;antecedent=0", 0,
             "completes stand-to-decant and wash-to-decant chains and remains distinct from whole-batch draining"),
            ("retain the mixture for later use", 70, "material=3;vessel=3;body=0;comparison=0;antecedent=3", 3,
             "does not explain why a new portion is loaded immediately after every occurrence"),
        ],
    },
    "4d4559019a961b834aa1": {
        "surface": "CHAR/DAR/SAR",
        "selected": "then proceed to the next act",
        "confidence": ".86",
        "transition": "SEQUENCE_CURSOR advances; active material and owner remain available",
        "candidates": [
            ("from the same batch", 72, "material=0;vessel=0;body=0;comparison=0;antecedent=5", 4,
             "works near mixtures but is awkward between jar storage and grinding and at line-final carry"),
            ("then proceed to the next act", 97, "material=0;vessel=0;body=0;comparison=0;antecedent=0", 0,
             "directly explains PUT IN--CARD--PUT IN and line-final continuation without changing content registers"),
            ("repeat the foregoing preparation", 68, "material=0;vessel=0;body=0;comparison=0;antecedent=5", 5,
             "would duplicate rather than advance the two consecutive additions on f82r.19"),
        ],
    },
    "2cc054357a929df85f64": {
        "surface": "CHO/SHO (f56r)",
        "selected": "as for the pictured plant itself",
        "confidence": ".59",
        "transition": "OWNER resets to the depicted f56r plant; following part/preparation attaches to that owner",
        "candidates": [
            ("thereafter take the following detail", 78, "material=0;vessel=0;body=0;comparison=0;antecedent=0", 2,
             "good sequence prose but poor inside ITS SEED IS--CARD--THE DRIED LEAF"),
            ("as for the pictured plant itself", 90, "material=0;vessel=0;body=0;comparison=0;antecedent=4", 0,
             "one page-owner reset works at field entry and medially before root, wine instruction, leaf and fresh remedy"),
            ("use the flowering tops of the plant", 51, "material=0;vessel=0;body=0;comparison=0;antecedent=4", 4,
             "contradicted by explicit lower-root, dried-leaf and honey/fresh-remedy continuations"),
        ],
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def guarded_formal() -> list[dict[str, str]]:
    cols = ["page", "locus", "group_index", "group_count", "record_ordinal",
            "field_ordinal", "within_field_position", "joint_tuple_id",
            "line_first", "prev_dy", "dy_closure", "b3"]
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(FORMAL), "--selector", "page"]
    for page in PAGES:
        cmd += ["--allow", page]
    cmd += ["--forbid-prefix", "f84", "--columns", ",".join(cols)]
    result = subprocess.run(cmd, cwd=ROOT, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def line_number(locus: str) -> int:
    return int(locus.split(".")[-1])


def joined(events: list[dict[str, str]], meanings: dict[tuple[str, str], str], fields: bool = False) -> str:
    parts: list[str] = []
    last_field = None
    for event in events:
        field = event.get("field_ordinal", "")
        if fields and last_field is not None and field != last_field:
            parts.append("/")
        parts.append(meanings[(event["locus"], event["group_index"])])
        last_field = field
    return " ".join(parts).replace(" / ", " / ")


def main() -> None:
    ledger = [r for r in read_tsv(LEDGER) if r["ledger_scope"] == "GDT327_PROSE" and r["page"] in PAGES]
    formal = guarded_formal()
    if any(r["page"].startswith("f84") for r in formal):
        raise SystemExit("sealed-page guard failure")
    meanings = {(r["locus"], r["event_index"]): r["default_English"] for r in ledger}
    surfaces = {(r["locus"], r["event_index"]): r["surface"] for r in ledger}
    formal_idx = {(r["locus"], r["group_index"]): r for r in formal}
    for key in meanings:
        if key not in formal_idx:
            raise SystemExit(f"missing formal row {key}")
    events = []
    for row in ledger:
        event = dict(row)
        event.update(formal_idx[(row["locus"], row["event_index"])])
        events.append(event)
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_locus[event["locus"]].append(event)
    for group in by_locus.values():
        group.sort(key=lambda r: int(r["group_index"]))
    by_page_loci: dict[str, list[str]] = defaultdict(list)
    for locus in by_locus:
        by_page_loci[locus.split(".")[0]].append(locus)
    for page in by_page_loci:
        by_page_loci[page].sort(key=line_number)

    decision_rows = []
    for tid, card in CARDS.items():
        count = sum(1 for r in events if r["joint_tuple_id"] == tid)
        for rank, (meaning, score, silent, repairs, rationale) in enumerate(card["candidates"], 1):
            decision_rows.append({
                "exact_tuple_id": tid, "surface_family": card["surface"], "occurrences": count,
                "candidate_rank": rank, "candidate_meaning": meaning, "process_fit_score_100": score,
                "required_silent_arguments": silent, "ad_hoc_repairs": repairs,
                "selected": int(meaning == card["selected"]), "selected_confidence": card["confidence"] if meaning == card["selected"] else "",
                "reason": rationale,
            })
    write_tsv(OUT / "V18_R3_SIX_CARD_DECISIONS.tsv", decision_rows,
              list(decision_rows[0]))

    target_events = [r for r in events if r["joint_tuple_id"] in CARDS]
    target_events.sort(key=lambda r: (PAGES.index(r["page"]), line_number(r["locus"]), int(r["group_index"])))
    if len(target_events) != 31:
        raise SystemExit(f"expected 31 target events, got {len(target_events)}")

    occurrence_rows = []
    passage_blocks = []
    for serial, event in enumerate(target_events, 1):
        card = CARDS[event["joint_tuple_id"]]
        line = by_locus[event["locus"]]
        loci = by_page_loci[event["page"]]
        li = loci.index(event["locus"])
        prev_line = by_locus[loci[li - 1]] if li else []
        next_line = by_locus[loci[li + 1]] if li + 1 < len(loci) else []
        pos = line.index(event)
        field = [r for r in line if r["field_ordinal"] == event["field_ordinal"]]
        effective_prev = (line[pos - 1] if pos else (prev_line[-1] if prev_line else None))
        effective_next = (line[pos + 1] if pos + 1 < len(line) else (next_line[0] if next_line else None))
        before_phrase = meanings[(effective_prev["locus"], effective_prev["group_index"])] if effective_prev else "new page-owned process"
        after_phrase = meanings[(effective_next["locus"], effective_next["group_index"])] if effective_next else "process remains open"
        local_meanings = dict(meanings)
        local_meanings[(event["locus"], event["group_index"])] = card["selected"]
        rival_graphs = []
        for candidate, _, _, _, _ in card["candidates"]:
            rival_graphs.append(f"{before_phrase} -> [{candidate}] -> {after_phrase}")
        selected_graph = f"BEFORE({before_phrase}) -> {card['transition']} -> NEXT({after_phrase})"
        row = {
            "occurrence_id": f"R3O{serial:02d}", "page": event["page"], "locus": event["locus"],
            "record": event["record_ordinal"], "field": event["field_ordinal"], "event_index": event["group_index"],
            "surface": surfaces[(event["locus"], event["group_index"])], "exact_tuple_id": event["joint_tuple_id"],
            "field_position": event["within_field_position"], "dy_closure": event["dy_closure"], "b3": event["b3"],
            "previous_physical_line": joined(prev_line, meanings) if prev_line else "<PAGE_START>",
            "complete_target_field": joined(field, local_meanings),
            "complete_physical_line": joined(line, local_meanings, fields=True),
            "following_physical_line": joined(next_line, meanings) if next_line else "<PAGE_END>",
            "state_immediately_before": before_phrase,
            "rival_1_graph": rival_graphs[0], "rival_2_graph": rival_graphs[1], "rival_3_graph": rival_graphs[2],
            "selected_meaning": card["selected"], "state_immediately_after": card["transition"],
            "selected_process_graph": selected_graph, "confidence": card["confidence"],
        }
        occurrence_rows.append(row)
        passage_blocks.append(
            f"### {row['occurrence_id']} — {event['locus']} `{row['surface']}`\n\n"
            f"- Vorzeile: {row['previous_physical_line']}\n"
            f"- Zielfeld: **{row['complete_target_field']}**\n"
            f"- Ganze Zeile: {row['complete_physical_line']}\n"
            f"- Folgezeile: {row['following_physical_line']}\n"
            f"- Prozess: `{selected_graph}`\n"
            f"- Rivalen: `{rival_graphs[0]}` / `{rival_graphs[1]}` / `{rival_graphs[2]}`\n"
        )
    write_tsv(OUT / "V18_R3_31_OCCURRENCE_RECONSTRUCTIONS.tsv", occurrence_rows,
              list(occurrence_rows[0]))

    # One selected reading is propagated through every affected complete record,
    # not merely through the attractive local windows.
    selected_meanings = dict(meanings)
    affected_records: set[tuple[str, str]] = set()
    for event in target_events:
        selected_meanings[(event["locus"], event["group_index"])] = CARDS[event["joint_tuple_id"]]["selected"]
        affected_records.add((event["page"], event["record_ordinal"]))
    record_blocks = []
    for page, record in sorted(affected_records, key=lambda x: (PAGES.index(x[0]), int(x[1]))):
        record_blocks.append(f"### {page}, vollständiger Record {record}\n")
        for locus in by_page_loci[page]:
            line_events = [e for e in by_locus[locus] if e["record_ordinal"] == record]
            if line_events:
                record_blocks.append(f"- `{locus}`: {joined(line_events, selected_meanings, fields=True)}")
        record_blocks.append("")

    header = "# V18 R3 — vollständige betroffene Passagen\n\n"
    header += "Alle 31 Zielvorkommen enthalten Zielfeld, ganze physische Zeile, Vor- und Folgezeile. "
    header += "Ein physischer Zeilenwechsel ist nicht automatisch ein Satzende; der Prozesszustand wird weitergetragen.\n\n"
    complete = header + "\n".join(passage_blocks)
    complete += "\n## Vollständig umgeschriebene betroffene Records/Artikel\n\n"
    complete += "\n".join(record_blocks)
    (OUT / "V18_R3_COMPLETE_AFFECTED_PASSAGES.md").write_text(complete, encoding="utf-8")


if __name__ == "__main__":
    main()
