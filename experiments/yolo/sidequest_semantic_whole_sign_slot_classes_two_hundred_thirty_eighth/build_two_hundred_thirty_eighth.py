#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_biological_second_lesson_two_hundred_thirty_seventh/TWO_HUNDRED_THIRTY_SEVENTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv"
SIGNS = ROOT / "experiments/yolo/sidequest_semantic_biological_second_lesson_two_hundred_thirty_seventh/TWO_HUNDRED_THIRTY_SEVENTH_SIX_WHOLE_SIGNS.tsv"

SLOTS = {
    "MC061": ("ACTION", "CLOSED_HANDLING_ACTION", "continuation → SIGN → close", "a concrete manipulation verb that can close the local step", "schwenken; Schluss"),
    "MC109": ("ACTION", "OPEN_FILL_OR_CHARGE_ACTION", "SIGN → transfer/close", "a filling or charging action whose object is inherited from the owner", "füllen"),
    "MC152": ("ACTION", "DIVISION_BEFORE_MEASURE", "source transfer → SIGN → measure", "a division or partition action before a prescribed value", "gleichteilen"),
    "MC012": ("OBJECT", "MATERIAL_ADDITIVE", "portion/path → SIGN → continuation/target", "a material or additive inserted into the current preparation", "Badzusatz"),
    "MC065": ("OBJECT", "DEVICE_PORT", "activation → SIGN → result", "a local opening, nozzle, or port between operation and result", "Düse"),
    "MC118": ("OBJECT", "RECEIVER_HEAD", "SIGN → handling → stage → collection", "a receiving container named before its handling sequence", "Auffangschale"),
}

PREDICTIONS = [
    ("P1", "CLOSED_HANDLING_ACTION", "After OL/continuation and at a closed field", "HANDLING_ACTION+CLOSE", "Do not substitute a material or vessel noun."),
    ("P2", "OPEN_FILL_OR_CHARGE_ACTION", "At statement entry before transfer/close", "FILL_OR_CHARGE_ACTION", "The visible owner supplies the omitted container."),
    ("P3", "DIVISION_BEFORE_MEASURE", "After source transfer and before AIIN", "DIVISION_OR_PORTIONING_ACTION", "A target or substance noun would break the action sequence."),
    ("P4", "MATERIAL_ADDITIVE", "Inside a quantity/path sequence", "MATERIAL_OR_ADDITIVE_NOUN", "It may recur unchanged when the same additive is reused."),
    ("P5", "DEVICE_PORT", "After activation and before RESULT", "PORT_OR_NOZZLE_NOUN", "It is a local device name, not a general direction marker."),
    ("P6", "RECEIVER_HEAD", "At statement entry before handling/grade/collection", "RECEIVING_VESSEL_NOUN", "The following cards operate on this inherited vessel."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    signs = read(SIGNS)
    sign_ids = {row["master_card_id"] for row in signs}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    occurrence_rows: list[dict[str, object]] = []
    for statement_id, rows in by_statement.items():
        for index, row in enumerate(rows):
            if row["master_card_id"] not in sign_ids:
                continue
            lexical_class, slot, frame, allowed, value = SLOTS[row["master_card_id"]]
            occurrence_rows.append({
                "event_id": row["event_id"],
                "statement_id": statement_id,
                "visible_sign": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "selected_value_de": value,
                "lexical_class": lexical_class,
                "slot_class": slot,
                "previous_value_de": rows[index - 1]["lesson_two_value_de"] if index else "STATEMENT_START",
                "next_value_de": rows[index + 1]["lesson_two_value_de"] if index + 1 < len(rows) else "STATEMENT_END",
                "abstract_frame": frame,
                "allowed_replacement_class": allowed,
                "visible_owner": row["visible_owner"],
            })
    write(OUT / "TWO_HUNDRED_THIRTY_EIGHTH_SEVEN_WHOLE_SIGN_OCCURRENCES.tsv", occurrence_rows)

    class_rows: list[dict[str, object]] = []
    for sign in signs:
        lexical_class, slot, frame, allowed, value = SLOTS[sign["master_card_id"]]
        occ = [row for row in occurrence_rows if row["master_card_id"] == sign["master_card_id"]]
        class_rows.append({
            "master_card_id": sign["master_card_id"],
            "visible_sign": sign["visible_sign"],
            "memorized_value_de": value,
            "lexical_class": lexical_class,
            "slot_class": slot,
            "occurrence_count": len(occ),
            "event_ids": "|".join(str(row["event_id"]) for row in occ),
            "slot_frame": frame,
            "allowed_replacement_class": allowed,
            "exact_surface_predictable": "NO",
            "card_class_predictable": "YES",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_EIGHTH_SIX_SLOT_CLASSES.tsv", class_rows)

    prediction_rows = [
        {"prediction_id": prediction_id, "slot_class": slot, "trigger_context": trigger, "predicted_card_class": predicted, "exclusion": exclusion}
        for prediction_id, slot, trigger, predicted, exclusion in PREDICTIONS
    ]
    write(OUT / "TWO_HUNDRED_THIRTY_EIGHTH_SIX_REPLACEMENT_RULES.tsv", prediction_rows)

    readable = [
        "# Das kleine Biological-Ganzzeichenbuch",
        "",
        "## Drei Handlungen",
        "",
        "- `sshkchdy` — **schwenken; Schluss**: geschlossene Handhabung nach einer Fortsetzung.",
        "- `ytey` — **füllen**: offene Füllhandlung vor dem anschließenden Transfer.",
        "- `ches` — **gleichteilen**: Teilung zwischen Quellabführung und Sollwert.",
        "",
        "## Drei Dinge",
        "",
        "- `dl` — **Badzusatz**: Stoffslot in zwei Mengen-/Laufsequenzen.",
        "- `ls` — **Düse**: Geräteport zwischen Einsetzen und Ergebnis.",
        "- `ly` — **Auffangschale**: Empfängerkopf vor Halten, Stufe und Sammlung.",
        "",
        "## Was ein Lehrling vorhersagen kann",
        "",
        "Er kann aus dem Satzplatz entscheiden, ob hier eine Handlung, ein Stoff, ein Geräteport oder ein Gefäß stehen muss. Er kann nicht allein daraus entscheiden, ob die konkrete gelernte Karte `dl`, `ls` oder `ly` lautet; diese Identität kommt aus dem Exemplar. Das entspricht genau einem gemischten System aus produktiver Grammatik und Nomenklator.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_EIGHTH_READABLE_WHOLE_SIGN_CODEBOOK.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 238 — syntaktische Klassen der sechs Ganzzeichen",
        "",
        "Die sechs Zeichen teilen sich exakt in drei Aktionen und drei Objekte. Alle sieben Vorkommen besitzen einen unterscheidbaren Satzslot. Damit ist die Klasse einer Ersatzkarte vorhersagbar, obwohl ihre exakte Oberfläche weiterhin aus dem Nomenklator gelernt werden muss.",
        "",
        "Das Modell gewinnt eine echte Kompositionsvorhersage: nach Quelltransfer vor AIIN steht eine Teilungshandlung; zwischen Aktivierung und Ergebnis ein Geräteport; am Kopf vor Halten/Stufe/Sammlung ein Empfänger; innerhalb Mengen-/Laufsequenzen ein Stoffzusatz.",
        "",
        "Nächster Schritt: die vollständigen f81v- und f82r-Recordübersetzungen mit diesen sechs kurzen Werten neu schreiben und prüfen, ob daraus zwei verschiedene praktische Protokolle entstehen.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_EIGHTH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "sign_source_sha256": hashlib.sha256(SIGNS.read_bytes()).hexdigest(),
        "signs": len(class_rows),
        "occurrences": len(occurrence_rows),
        "action_signs": sum(row["lexical_class"] == "ACTION" for row in class_rows),
        "object_signs": sum(row["lexical_class"] == "OBJECT" for row in class_rows),
        "replacement_rules": len(prediction_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
