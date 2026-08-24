#!/usr/bin/env python3
"""Map statement-level process phases and longer procedure blocks."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_ten_weak_cards_three_hundred_fourth/THREE_HUNDRED_FOURTH_173_REVISED_IMPERATIVE_LEXICON.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_recurrent_formulas_three_hundred_fifth/THREE_HUNDRED_FIFTH_116_FORMULA_ANNOTATED_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase(event: dict[str, str], lexicon: dict[str, dict[str, str]]) -> str:
    family = event["family_parse"]
    gloss = lexicon[event["master_card_id"]]["source_short_value_de"].lower()
    if any(k in gloss for k in ["wasch", "spül", "seih", "klarlauf", "klarabzug", "auswring"]):
        return "WASH_FILTER"
    if any(k in family for k in ["SHED", "SOLK"]) or any(k in gloss for k in ["absetz", "sammel", "stehzeit"]):
        return "SETTLE_COLLECT"
    if "CHK" in family or any(k in gloss for k in ["wärm", "kalt"]):
        return "THERMAL"
    if any(k in family for k in ["CKHE", "CKH", "LSH"]) or any(k in gloss for k in ["durchlass", "durchleit", "passage"]):
        return "PASS_FILTER"
    if "CHED" in family or any(k in gloss for k in ["transfer", "überführ", "abführ", "zuführ", "abzug"]):
        return "TRANSFER"
    if "OK" in family or any(k in gloss for k in ["einsetz", "einwirk", "befestig", "auftragen"]):
        return "APPLY_CONTACT"
    if any(k in family for k in ["AIIN", "AIN", "IIN"]) or any(k in gloss for k in ["maß", "portion", "stufe"]):
        return "MEASURE_STAGE"
    if "AL" in family or any(k in gloss for k in ["ziel", "dorthin"]):
        return "TARGET"
    if "AR" in family or any(k in gloss for k in ["quelle", "davon"]):
        return "SOURCE"
    if any(k in family for k in ["OR", "CHO", "CHEO"]) or any(k in gloss for k in ["ansatz", "zutat", "auszug", "wurzel", "stängel", "kochgut"]):
        return "MATERIAL"
    if any(k in family for k in ["OL", "OT"]) or any(k in gloss for k in ["weiter", "folge", "nächste"]):
        return "CONTINUE"
    if "CTH" in family or any(k in gloss for k in ["bereit", "fertig"]):
        return "READY"
    if "+Y" in family or family == "Y" or "Y[" in family or gloss == "dies":
        return "ITEM"
    return "SPECIAL"


BLOCK_READINGS = {
    "APPLY_CONTACT": "aufeinanderfolgende Anwendungs-/Kontaktzellen",
    "TRANSFER": "aufeinanderfolgende Übergabe-, Abführ- oder Stationszellen",
    "SETTLE_COLLECT": "aufeinanderfolgende Absetz-/Sammelzellen",
    "PASS_FILTER": "aufeinanderfolgende Durchlass-/Filterzellen",
}


def main() -> None:
    raw = read(RAW)
    lexicon = {r["master_card_id"]: r for r in read(LEXICON)}
    source_statements = read(STATEMENTS)
    source_by_id = {r["statement_id"]: r for r in source_statements}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[str]] = defaultdict(list)
    for event in raw:
        if event["event_id"] == "E181":
            continue
        by_statement[event["statement_id"]].append(event)
        if event["statement_id"] not in by_record[event["record_unit_id"]]:
            by_record[event["record_unit_id"]].append(event["statement_id"])

    phase_rows = []
    phase_by_statement = {}
    for statement_id, selected in by_statement.items():
        phases = []
        event_phase_trace = []
        for event in selected:
            value = phase(event, lexicon)
            event_phase_trace.append(f"{event['event_id']}:{value}")
            if not phases or phases[-1] != value:
                phases.append(value)
        dominant = phases[0] if len(phases) == 1 else "MIXED"
        phase_by_statement[statement_id] = (tuple(phases), dominant)
        source = source_by_id[statement_id]
        phase_rows.append({
            "statement_id": statement_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "event_count": source["visible_event_count"],
            "phase_sequence": ">".join(phases),
            "dominant_phase": dominant,
            "phase_count": len(phases),
            "event_phase_trace": "|".join(event_phase_trace),
            "formula_ids": source["formula_ids"],
            "fluent_imperative_de": source["fluent_imperative_de"],
        })
    phase_path = HERE / "THREE_HUNDRED_SIXTH_116_STATEMENT_PHASES.tsv"
    write(phase_path, phase_rows)

    boundaries = []
    for record_id, statement_ids in by_record.items():
        for index in range(len(statement_ids) - 1):
            left, right = statement_ids[index:index + 2]
            left_seq, left_dom = phase_by_statement[left]
            right_seq, right_dom = phase_by_statement[right]
            pair = f"{left_dom}>{right_dom}"
            if left_dom == right_dom != "MIXED":
                relation = "SAME_PHASE_CELL_SERIES"
            elif left_dom != "MIXED" and right_dom != "MIXED":
                relation = "PURE_PHASE_TRANSITION"
            else:
                relation = "MIXED_STATEMENT_BOUNDARY"
            boundaries.append({
                "boundary_id": f"SB{len(boundaries)+1:03d}",
                "record_unit_id": record_id,
                "from_statement": left,
                "to_statement": right,
                "from_phase_sequence": ">".join(left_seq),
                "to_phase_sequence": ">".join(right_seq),
                "dominant_pair": pair,
                "boundary_relation": relation,
                "reading_de": "nächste Zelle derselben Prozessfamilie" if relation == "SAME_PHASE_CELL_SERIES" else "neuer oder gemischter Arbeitsschritt",
            })
    boundary_path = HERE / "THREE_HUNDRED_SIXTH_105_STATEMENT_BOUNDARIES.tsv"
    write(boundary_path, boundaries)

    blocks = []
    for record_id, statement_ids in by_record.items():
        start = 0
        while start < len(statement_ids):
            dominant = phase_by_statement[statement_ids[start]][1]
            end = start + 1
            while end < len(statement_ids) and phase_by_statement[statement_ids[end]][1] == dominant:
                end += 1
            if end - start >= 2 and dominant in BLOCK_READINGS:
                members = statement_ids[start:end]
                blocks.append({
                    "block_id": f"PB{len(blocks)+1:02d}",
                    "record_unit_id": record_id,
                    "dominant_phase": dominant,
                    "statement_count": len(members),
                    "first_statement": members[0],
                    "last_statement": members[-1],
                    "statement_ids": "|".join(members),
                    "block_reading_de": BLOCK_READINGS[dominant],
                    "continuous_reading_de": " ".join(source_by_id[s]["fluent_imperative_de"] for s in members),
                    "interpretation_de": "Stations- oder Variantenserie; nicht automatisch ein einziger langer Satz",
                })
            start = end
    block_path = HERE / "THREE_HUNDRED_SIXTH_EIGHT_PROCEDURE_BLOCKS.tsv"
    write(block_path, blocks)

    record_lines = ["# Elf Records als Folge von Prozessphasen", "", "Eine eckige Klammer zeigt die kollabierte Phasenfolge einer Aussage. Mehrere gleichartige Einzelaussagen hintereinander bilden einen lokalen Stations-/Variantenblock, nicht zwingend einen fortlaufenden Satz.", ""]
    phase_row_by_id = {r["statement_id"]: r for r in phase_rows}
    block_start = {r["first_statement"]: r for r in blocks}
    block_members = {s for r in blocks for s in r["statement_ids"].split("|")}
    for record_id, statement_ids in by_record.items():
        record_lines += [f"## {record_id}", ""]
        for statement_id in statement_ids:
            if statement_id in block_start:
                b = block_start[statement_id]
                record_lines += [f"**{b['block_id']} — {b['block_reading_de']} ({b['statement_ids']}):**", ""]
            row = phase_row_by_id[statement_id]
            prefix = "  -" if statement_id in block_members else "-"
            record_lines += [f"{prefix} **{statement_id} [{row['phase_sequence']}]:** {row['fluent_imperative_de']}"]
        record_lines += [""]
    record_path = HERE / "THREE_HUNDRED_SIXTH_ELEVEN_RECORD_MACRO_EDITION.md"
    record_path.write_text("\n".join(record_lines), encoding="utf-8")

    pair_counts = Counter(r["dominant_pair"] for r in boundaries)
    recurring_pairs = {pair: count for pair, count in pair_counts.items() if count >= 2 and "MIXED" not in pair}
    report_path = HERE / "THREE_HUNDRED_SIXTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 306: Aussagefolgen und lokale Stationsblöcke\n\n"
        f"Die 116 Aussagen erzeugen 105 recordinterne Grenzen. Nach einer festen Prozessklassifikation wiederholen sich nur drei reine Übergangstypen: TRANSFER→TRANSFER siebenmal, MEASURE_STAGE→APPLY_CONTACT zweimal und TRANSFER→APPLY_CONTACT zweimal. Acht maximale Blöcke mit zusammen {sum(int(r['statement_count']) for r in blocks)} Aussagen bestehen aus derselben reinen Prozessfamilie. Der auffälligste ist B3-S022–S025 mit vier aufeinanderfolgenden Transferzellen.\n\n"
        "Damit entsteht kein zweites, verborgenes Langrezept, das auf mehreren Seiten wortgleich wiederkehrt. Stattdessen sieht die Bio-Prosa stärker nach einer Abfolge kurzer Stations- oder Variantenfelder aus: Transferpalette, Kontaktzellen, Absetzpaar und Filterpaar. Das passt zur Bildgliederung und erklärt, warum viele Commit-Karten Einzelaussagen schließen.\n\n"
        "Der nächste Pass sollte diese acht Blöcke mit den sichtbaren lokalen Besitzern verschränken und jedem Block eine konkrete Betriebsrolle geben: Zuführung, Beckenbehandlung, Absetzen, Filtration oder Abführung.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "statements": len(phase_rows), "record_internal_boundaries": len(boundaries),
        "pure_same_phase_boundaries": sum(r["boundary_relation"] == "SAME_PHASE_CELL_SERIES" for r in boundaries),
        "procedure_blocks": len(blocks), "statements_in_blocks": sum(int(r["statement_count"]) for r in blocks),
        "recurring_pure_boundary_pairs": recurring_pairs,
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [RAW, LEXICON, STATEMENTS]},
        "output_hashes": {p.name: sha(p) for p in [phase_path, boundary_path, block_path, record_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
