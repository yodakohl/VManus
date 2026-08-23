#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GRAPH_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_f83r_local_station_graph_two_hundred_thirty_second/TWO_HUNDRED_THIRTY_SECOND_ONE_HUNDRED_FIFTY_THREE_EVENTS.tsv"
GRAPH_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_f83r_local_station_graph_two_hundred_thirty_second/TWO_HUNDRED_THIRTY_SECOND_FIFTY_FOUR_STATEMENTS.tsv"

FUNCTIONS = {
    "N5": ("GEKOPPELTES DOPPELBECKEN FÜR EINWIRKUNG UND DURCHLASS", "hold/apply, transfer, pass twice, set value, settle", "central treatment and residence"),
    "N6": ("LINKER TEMPERIER- UND ERGEBNISARM", "warm, continue, add portion, transfer, take result, drain", "left finishing path"),
    "N7": ("RECHTER PORTIONS- UND VERTEILERARM", "add further portion, move to target, pour from source, settle", "right finishing path"),
}

MODELS = [
    ("M1", "GEKOPPELTES_DOPPELBECKEN_MIT_ZWEI_ABSCHLUSSPFADEN", 15, "Select", "Uses the visible pair, left/right contacts, repeated residence operations, and distinct branch vocabularies without inventing direction."),
    ("M2", "THERAPEUTISCHE_AUFLAGE_UND_SPUELBEHANDLUNG", 13, "Local expansion", "Human figures and hold/wash-like operations fit, but no body part, disease, or explicit treatment label is written."),
    ("M3", "EIN_GERICHTETER_GESCHLOSSENER_WASSERKREISLAUF", 7, "Reject", "No arrows, return edge, or connection to upper stations; open ends remain."),
    ("M4", "BLOSS_DEKORATIVES_FORMULAR_OHNE_APPARATUR", 8, "Reject", "Cannot exploit the three strong physical contacts or left/right operation split."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def operation_class(value: str) -> str:
    lower = value.lower()
    if any(term in lower for term in ("einwirk", "absetz", "halt", "befest", "durchlass")):
        return "RESIDENCE_OR_TREATMENT"
    if any(term in lower for term in ("überführ", "transfer", "dorthin", "ziel", "weiter", "lauf")):
        return "TRANSFER_OR_PATH"
    if any(term in lower for term in ("anteil", "portion", "sollwert", "maß", "bemess")):
        return "QUANTITY_OR_SETTING"
    if any(term in lower for term in ("abführ", "abzug", "ergebnis", "ausguss", "schluss")):
        return "OUTPUT_OR_CLOSE"
    if any(term in lower for term in ("wärm", "temper")):
        return "TEMPERATURE"
    if any(term in lower for term in ("sammel", "ansatz", "einsetz", "quelle", "davon", "dies")):
        return "INPUT_OR_REFERENT"
    return "LOCAL_SPECIALIST_ACTION"


def main() -> None:
    events = [row for row in read(GRAPH_EVENTS) if row["graph_node_id"] in FUNCTIONS]
    statement_source = read(GRAPH_STATEMENTS)
    statement_ids = {row["statement_id"] for row in events}
    statements = [row for row in statement_source if row["statement_id"] in statement_ids]

    event_rows: list[dict[str, object]] = []
    for row in events:
        function, _, role = FUNCTIONS[row["graph_node_id"]]
        event_rows.append({
            **row,
            "operation_class": operation_class(row["portable_value_de"]),
            "selected_apparatus_function": function,
            "apparatus_role": role,
        })
    write(OUT / "TWO_HUNDRED_THIRTY_THIRD_SEVENTY_ONE_EVENTS.tsv", event_rows)

    function_rows: list[dict[str, object]] = []
    for node_id, (function, chain, role) in FUNCTIONS.items():
        rows = [row for row in event_rows if row["graph_node_id"] == node_id]
        classes = Counter(row["operation_class"] for row in rows)
        function_rows.append({
            "node_id": node_id,
            "selected_function_de": function,
            "apparatus_role": role,
            "event_count": len(rows),
            "statement_count": len({row["statement_id"] for row in rows}),
            "short_operation_chain": chain,
            "operation_class_counts": "|".join(f"{key}:{classes[key]}" for key in sorted(classes)),
            "physical_relation": "two vessels joined by undirected arch" if node_id == "N5" else ("continuous left blue-lined open channel from N5" if node_id == "N6" else "continuous right S-conduit and multiended hub from N5"),
            "direction_claim": "NONE",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_THIRD_THREE_APPARATUS_FUNCTIONS.tsv", function_rows)

    statement_rows: list[dict[str, object]] = []
    for row in statements:
        owned_events = [event for event in event_rows if event["statement_id"] == row["statement_id"]]
        nodes = list(dict.fromkeys(event["graph_node_id"] for event in owned_events))
        statement_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "node_path": "→".join(nodes),
            "event_count": len(owned_events),
            "event_ids": "|".join(str(event["event_id"]) for event in owned_events),
            "literal_card_reading": row["literal_card_reading"],
            "apparatus_reading_de": row["graph_aware_reading_de"],
            "branch_interpretation": "LEFT_TO_RIGHT_OWNER_RESET_NOT_PHYSICAL_FLOW" if len(nodes) > 1 else FUNCTIONS[nodes[0]][2],
        })
    write(OUT / "TWO_HUNDRED_THIRTY_THIRD_TWENTY_FIVE_STATEMENTS.tsv", statement_rows)

    model_rows = [
        {"model_id": model_id, "model_de": model, "fit_score_out_of_16": score, "decision": decision, "reason": reason}
        for model_id, model, score, decision, reason in MODELS
    ]
    write(OUT / "TWO_HUNDRED_THIRTY_THIRD_MODEL_COMPETITION.tsv", model_rows)

    readable = [
        "# Die gekoppelte Unteranlage von f83r",
        "",
        "## Gewählte konkrete Lesung",
        "",
        "Ein **gekoppeltes Doppelbecken mit zwei Abschlusswegen**. Im Paar wird ein Posten eingesetzt, länger oder kurz einwirken gelassen, befestigt, zweimal durchgelassen, auf Sollwert gehalten und abgesetzt. Danach stehen zwei verschiedene Weiterbearbeitungen zur Verfügung:",
        "",
        "- **Linker Weg:** Sollwert setzen, kurz wärmen, länger weiterführen, Anteil zugeben, übertragen, Ergebnis nehmen und abführen.",
        "- **Rechter Weg:** weiteren Anteil nehmen, zum Ziel bringen, aus der Quelle ausgießen und kurz absetzen.",
        "",
        "B5 nimmt den linken Endposten noch einmal als Transferziel auf; B6 den rechten als Sammel- und Endverteilungsposten. Das sieht nach zwei auswählbaren Abschlussprotokollen aus, nicht nach einem zwingenden Kreisfluss.",
        "",
        "## Medizinische Expansion",
        "",
        "Wenn die Figuren als Patienten gelesen werden, ist die beste Expansion eine Auflage-/Spülbehandlung im Doppelbecken: Material anlegen und einwirken lassen; links temperieren und abnehmen, rechts eine weitere Portion verteilen. Das ist plausibler als eine bloße Industrieanlage, aber noch keine entschlüsselte Krankheitsanweisung.",
        "",
        "## Was die Zeichnung nicht sagt",
        "",
        "Sie nennt weder Einlass noch Auslass, weder warmes noch kaltes Wasser und keine Flussrichtung. Deshalb sind ›linker‹ und ›rechter Abschlussweg‹ robuste Namen; ›Zulauf‹ und ›Ablauf‹ wären zu früh.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_THIRD_READABLE_TWO_ARM_FUNCTION.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 233 — die einzige sichtbar gekoppelte f83r-Teilapparatur",
        "",
        "Die Analyse beschränkt sich auf N5–N7: 71 Karten in 25 Aussagen. Das zentrale Paar ist eine Einwirk-/Durchlasseinheit. Die beiden sichtbaren Fortsetzungen haben getrennte Textökologien: links Temperieren/Ergebnis/Abführen, rechts Portion/Quelle/Ausgießen/Absetzen.",
        "",
        "Die beste konkrete Funktion ist daher kein gerichteter Kreislauf, sondern ein gekoppeltes Doppelbecken mit zwei alternativen Abschlusswegen. Eine therapeutische Auflage-/Spülbehandlung ist die stärkste inhaltliche Expansion, während das formale Apparaturmodell auch ohne medizinische Nomen lesbar bleibt.",
        "",
        "Nächster Schritt: B5 und B6 als eigenständige Lehrlings-Nachträge prüfen. Wenn sie wirklich linke und rechte Abschlussprotokolle wiederaufnehmen, sollten ihre Karten die branchenspezifischen Verben fortsetzen.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_THIRD_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "graph_event_sha256": hashlib.sha256(GRAPH_EVENTS.read_bytes()).hexdigest(),
        "graph_statement_sha256": hashlib.sha256(GRAPH_STATEMENTS.read_bytes()).hexdigest(),
        "nodes": len(function_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "selected_model": MODELS[0][1],
        "direction_claims": 0,
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
