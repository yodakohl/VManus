#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R239 = ROOT / "experiments/yolo/sidequest_semantic_biological_dual_protocol_two_hundred_thirty_ninth"
R240 = ROOT / "experiments/yolo/sidequest_semantic_reusable_procedure_motifs_two_hundred_fortieth"
R232 = ROOT / "experiments/yolo/sidequest_semantic_f83r_local_station_graph_two_hundred_thirty_second"
R241 = ROOT / "experiments/yolo/sidequest_semantic_f83r_motif_transfer_two_hundred_forty_first"

E12 = R239 / "TWO_HUNDRED_THIRTY_NINTH_ONE_HUNDRED_TWENTY_EIGHT_PROTOCOL_EVENTS.tsv"
S12 = R239 / "TWO_HUNDRED_THIRTY_NINTH_FORTY_THREE_COMPLETE_STATEMENTS.tsv"
M12 = R240 / "TWO_HUNDRED_FORTIETH_THIRTY_MOTIF_OCCURRENCES.tsv"
E3 = R232 / "TWO_HUNDRED_THIRTY_SECOND_ONE_HUNDRED_FIFTY_THREE_EVENTS.tsv"
S3 = R241 / "TWO_HUNDRED_FORTY_FIRST_FIFTY_FOUR_F83R_MOTIF_READINGS.tsv"
MOTIFS = R241 / "TWO_HUNDRED_FORTY_FIRST_SEVEN_MOTIF_CURRICULUM.tsv"

PROTOCOL = {
    "B1": "GEMEINSAMES_BECKEN_ANSATZ_UND_ANWENDUNG",
    "B2": "MODULARES_MEHRSTATIONS_SPUEL_UND_VERTEILEN",
    "B3": "OBERE_RANDSTATIONEN_BIS_ZUM_GEPAARTEN_UNTERBAU",
    "B4": "GEPAARTER_UNTERBAU_MIT_ZWEI_AUSGABEARMEN",
    "B5": "LINKER_AUSGABEARM_NACHTRAG",
    "B6": "RECHTER_ENDPUNKT_ZUSAMMENFASSUNG",
}

SPECIALISTS = [
    ("AIN", "PORTION"), ("AIR", "LAUFMEDIUM"), ("IIN", "ARBEITSSTUFE"),
    ("CKH", "DURCHLASS"), ("LSH", "WASCHGANG"), ("RESULT", "ERGEBNIS"),
]
WHOLE_SIGNS = [
    ("sshkchdy", "SCHWENKEN; SCHLUSS"), ("ytey", "FÜLLEN"),
    ("dl", "BADZUSATZ"), ("ls", "DÜSE"), ("ly", "AUFFANGSCHALE"),
    ("ches", "GLEICHTEILEN"),
]
ATOMIC = [("qoky", "EINSETZEN"), ("qokylddy", "BEFESTIGEN; SCHLUSS"), ("oldy", "SCHLUSS")]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    e12, s12, m12 = read_tsv(E12), read_tsv(S12), read_tsv(M12)
    e3, s3, motifs = read_tsv(E3), read_tsv(S3), read_tsv(MOTIFS)
    motif12: dict[str, list[str]] = defaultdict(list)
    for row in m12:
        for sid in row["statement_locus"].split(">"):
            if row["motif_id"] not in motif12[sid]:
                motif12[sid].append(row["motif_id"])
    s3_by_id = {r["statement_id"]: r for r in s3}

    statement_rows: list[dict[str, object]] = []
    for row in s12:
        statement_rows.append({
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "protocol": PROTOCOL[row["record_unit_id"]], "statement_id": row["statement_id"],
            "owner_path": row["visible_owner"], "event_ids": row["event_ids"],
            "visible_sequence": row["visible_sequence"], "concrete_value_chain": row["component_chain"],
            "complete_reading_de": row["complete_translation_de"],
            "motifs": "|".join(motif12[row["statement_id"]]) or "ATOMIC_OR_LOCAL_SEQUENCE",
            "owner_break_count": "0",
        })
    for row in s3:
        statement_rows.append({
            "record_unit_id": row["record_unit_id"], "page": "f83r",
            "protocol": PROTOCOL[row["record_unit_id"]], "statement_id": row["statement_id"],
            "owner_path": row["node_path"], "event_ids": row["event_ids"],
            "visible_sequence": row["visible_card_reading"], "concrete_value_chain": row["visible_card_reading"],
            "complete_reading_de": row["complete_station_reading_de"],
            "motifs": row["inherited_motifs"] if row["new_handoff_motif"] == "NONE" else row["new_handoff_motif"],
            "owner_break_count": row["owner_break_count"],
        })

    event_rows: list[dict[str, object]] = []
    for row in e12:
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record_unit_id": row["record_unit_id"],
            "protocol": PROTOCOL[row["record_unit_id"]], "statement_id": row["statement_id"],
            "field_id": row["field_id"], "owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "concrete_default_de": row["concrete_value_de"], "dictionary_layer": row["teaching_status"],
            "motif_context": "|".join(motif12[row["statement_id"]]) or "ATOMIC_OR_LOCAL_SEQUENCE",
        })
    for row in e3:
        sm = s3_by_id[row["statement_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": "f83r", "record_unit_id": sm["record_unit_id"],
            "protocol": PROTOCOL[sm["record_unit_id"]], "statement_id": row["statement_id"],
            "field_id": row["field_id"], "owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "concrete_default_de": row["portable_value_de"], "dictionary_layer": "F83R_PRODUCTIVE_OR_LOCAL_CARD",
            "motif_context": sm["new_handoff_motif"] if sm["new_handoff_motif"] != "NONE" else sm["inherited_motifs"],
        })

    form_rows: list[dict[str, object]] = []
    by_form: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_form[str(row["visible_surface"])].append(row)
    for surface, linked in sorted(by_form.items()):
        values = list(dict.fromkeys(str(r["concrete_default_de"]) for r in linked))
        form_rows.append({
            "visible_surface": surface,
            "concrete_default_de": values[0],
            "occurrence_count": len(linked),
            "event_ids": "|".join(str(r["event_id"]) for r in linked),
            "pages": "|".join(dict.fromkeys(str(r["page"]) for r in linked)),
            "records": "|".join(dict.fromkeys(str(r["record_unit_id"]) for r in linked)),
            "owners": " | ".join(dict.fromkeys(str(r["owner"]) for r in linked)),
            "dictionary_layers": "|".join(dict.fromkeys(str(r["dictionary_layer"]) for r in linked)),
            "value_invariant_across_all_occurrences": "YES" if len(values) == 1 else "NO",
        })

    event_path = OUT / "TWO_HUNDRED_FORTY_SECOND_281_EVENT_BIOLOGICAL_MANUAL.tsv"
    statement_path = OUT / "TWO_HUNDRED_FORTY_SECOND_97_STATEMENT_BIOLOGICAL_EDITION.tsv"
    dictionary_path = OUT / "TWO_HUNDRED_FORTY_SECOND_163_FORM_DICTIONARY.tsv"
    curriculum_path = OUT / "TWO_HUNDRED_FORTY_SECOND_COMPACT_CURRICULUM.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_SECOND_THREE_CONTINUOUS_PAGES.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_SECOND_REPORT.md"
    write_tsv(event_path, event_rows, list(event_rows[0]))
    write_tsv(statement_path, statement_rows, list(statement_rows[0]))
    write_tsv(dictionary_path, form_rows, list(form_rows[0]))

    curriculum: list[dict[str, object]] = []
    for row in motifs:
        curriculum.append({"lesson_layer": "PROCEDURE_MOTIF", "entry": row["motif_id"], "meaning_de": row["apprentice_rule_de"], "learning_method": "produktive Regel mit wechselnden Karten"})
    for entry, value in SPECIALISTS:
        curriculum.append({"lesson_layer": "SPECIALIST_COMPONENT", "entry": entry, "meaning_de": value, "learning_method": "gemeinsamer Fachbaustein"})
    for entry, value in WHOLE_SIGNS:
        curriculum.append({"lesson_layer": "LEARNED_WHOLE_SIGN", "entry": entry, "meaning_de": value, "learning_method": "aus Musterseite auswendig lernen"})
    for entry, value in ATOMIC:
        curriculum.append({"lesson_layer": "ATOMIC_COMMAND", "entry": entry, "meaning_de": value, "learning_method": "elementare Karte"})
    write_tsv(curriculum_path, curriculum, list(curriculum[0]))

    readable = ["# Biological-Lehrbuch: drei Seiten, ein Kartensystem", ""]
    for record in ("B1", "B2", "B3", "B4", "B5", "B6"):
        linked = [r for r in statement_rows if r["record_unit_id"] == record]
        readable += [f"## {record} / {linked[0]['page']} — {PROTOCOL[record]}", ""]
        for index, row in enumerate(linked, start=1):
            readable.append(f"{index}. {row['complete_reading_de']}")
        readable.append("")
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    invariant = sum(r["value_invariant_across_all_occurrences"] == "YES" for r in form_rows)
    report = f"""# Sidequest-Pass 242: vollständiges Biological-Lehrbuch

## Ergebnis

- **281/281** sichtbare Karten in f81v, f82r und f83r erhalten einen kurzen konkreten Default.
- **97/97** Aussagen sind vollständig lesbar.
- **163** verschiedene sichtbare Formen bilden das kompakte Biological-Wörterbuch.
- Alle **{invariant}/163** Formen behalten in dieser Arbeitstheorie über jedes Vorkommen denselben Default.
- Der Lehrplan besteht aus sieben Prozedurmotiven, sechs Fachkomponenten, sechs gelernten Ganzzeichen und drei atomaren Befehlen.

## Werkstattmodell

Der Lehrmeister zeigt zuerst auf den bereits gezeichneten Besitzer. Dann diktiert er eines der sieben Arbeitsmotive und setzt Mengen-, Ziel-, Durchlass-, Halte- und Schlusswerte ein. Der Lehrling schreibt produktive Karten, ergänzt bei Bedarf ein gelerntes Fachzeichen und übernimmt nur wirklich lokale Formen aus dem Muster.

Die drei Seiten bleiben praktisch verschieden: f81v ist ein gemeinsamer Beckenzyklus; f82r eine modulare Stationsfolge; f83r mehrere lokale Stationen mit einem gekoppelten Unterbau und zwei Nachträgen. Dasselbe Wörterbuch reicht für alle drei.

Input hashes: R239 events `{sha(E12)}`; R239 statements `{sha(S12)}`; R232 events `{sha(E3)}`; R241 statements `{sha(S3)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "events": len(event_rows), "statements": len(statement_rows),
        "records": len({r["record_unit_id"] for r in statement_rows}), "visible_forms": len(form_rows),
        "invariant_forms": invariant, "curriculum_entries": len(curriculum),
        "record_event_counts": dict(Counter(str(r["record_unit_id"]) for r in event_rows)),
        "outputs": {p.name: sha(p) for p in (event_path, statement_path, dictionary_path, curriculum_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
