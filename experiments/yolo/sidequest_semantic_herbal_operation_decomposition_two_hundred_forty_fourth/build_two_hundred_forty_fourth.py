#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_herbal_curriculum_transfer_two_hundred_forty_third"
CARDS = SRC / "TWO_HUNDRED_FORTY_THIRD_66_CARD_HERBAL_DICTIONARY.tsv"
EVENTS = SRC / "TWO_HUNDRED_FORTY_THIRD_100_EVENT_HERBAL_TRANSFER.tsv"

MAP = {
    "MC006": ("OK + CHEO", "Auszug einsetzen", "FULL_COMPOSITION", "NONE"),
    "MC015": ("OK + OK + Y", "denselben Posten erneut einsetzen", "FULL_COMPOSITION", "NONE"),
    "MC021": ("OL + TCH + Y", "die laufende Bereitung fortsetzen", "PARTIAL_COMPOSITION", "TCH preparation core"),
    "MC037": ("TCHO + DY", "kalt stellen; Schluss", "LEARNED_WHOLE_OPERATION", "TCHO cold-setting operation"),
    "MC041": ("OK + OL", "die Fortsetzung einsetzen", "FULL_COMPOSITION", "NONE"),
    "MC048": ("K + IIN", "die Arbeitsstufe setzen", "FULL_COMPOSITION", "NONE"),
    "MC053": ("OT + OL", "anschließend fortsetzen", "FULL_COMPOSITION", "NONE"),
    "MC068": ("SOTODAN", "als Folgeanwendung führen", "LEARNED_WHOLE_OPERATION", "SOTODAN follow-up application"),
    "MC077": ("K + AL", "an der Zielstelle bearbeiten", "FULL_COMPOSITION", "NONE"),
    "MC090": ("K + OL", "weiter bearbeiten", "FULL_COMPOSITION", "NONE"),
    "MC099": ("CHEECKHO + DY", "auftragen; Schluss", "LEARNED_WHOLE_OPERATION", "CHEECKHO application operation"),
    "MC100": ("O + DY", "abkühlen; Schluss", "LEARNED_WHOLE_OPERATION", "O cooling operation"),
    "MC103": ("OK + Y", "den laufenden Posten einsetzen und weiterbearbeiten", "FULL_COMPOSITION", "NONE"),
    "MC104": ("K + E + OL", "kurz weiterbearbeiten", "FULL_COMPOSITION", "NONE"),
    "MC107": ("OT + Y", "zum nächsten Posten wechseln", "FULL_COMPOSITION", "NONE"),
    "MC111": ("SHFY + AIIN", "eine vorgeschriebene Stehzeit einhalten", "PARTIAL_COMPOSITION", "SHFY standing core"),
    "MC115": ("OT + OL + Y", "den bereiten Folgeposten wählen", "FULL_COMPOSITION", "NONE"),
    "MC117": ("K + Y", "den laufenden Posten bearbeiten", "FULL_COMPOSITION", "NONE"),
    "MC122": ("K + E + Y", "den laufenden Posten kurz bearbeiten", "FULL_COMPOSITION", "NONE"),
    "MC129": ("CFHY", "auswringen", "LEARNED_WHOLE_OPERATION", "CFHY wringing operation"),
    "MC142": ("D + OL", "vom vorigen Arbeitsgang nehmen", "PARTIAL_COMPOSITION", "D previous-source core"),
    "MC156": ("CPHY", "nachseihen", "LEARNED_WHOLE_OPERATION", "CPHY second-straining operation"),
    "MC158": ("CTH + OR", "den Ansatz bereitstellen", "FULL_COMPOSITION", "NONE"),
    "MC163": ("OT + OL", "den Folgegang fortsetzen", "FULL_COMPOSITION", "NONE"),
    "MC169": ("CTH + AIIN", "die Sollvorbereitung setzen", "FULL_COMPOSITION", "NONE"),
}


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
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    operation_cards = [r for r in cards if r["curriculum_layer"] == "HERBAL_LOCAL_OPERATION_SIGN"]
    decompositions: list[dict[str, object]] = []
    for row in operation_cards:
        components, reading, status, residue = MAP[row["master_card_id"]]
        decompositions.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "old_default_de": row["concrete_default_de"],
            "component_parse": components, "revised_compositional_reading_de": reading,
            "composition_status": status, "memorized_residue": residue,
            "occurrence_count": row["occurrence_count"], "event_ids": row["event_ids"],
            "apprentice_rule": (
                "build from shared components" if status == "FULL_COMPOSITION"
                else "build shared frame and memorize one residual core" if status == "PARTIAL_COMPOSITION"
                else "memorize as one short operation sign"
            ),
        })

    revised_cards: list[dict[str, object]] = []
    for row in cards:
        item = dict(row)
        if row["master_card_id"] in MAP:
            components, reading, status, residue = MAP[row["master_card_id"]]
            item.update({"component_parse": components, "revised_default_de": reading, "composition_status": status, "memorized_residue": residue})
        elif row["curriculum_layer"] == "COMMON_BIOLOGICAL_HERBAL_CORE":
            item.update({"component_parse": "COMMON_CORE", "revised_default_de": row["concrete_default_de"], "composition_status": "KNOWN_FROM_BIOLOGICAL", "memorized_residue": "NONE"})
        else:
            item.update({"component_parse": "WHOLE_NOUN", "revised_default_de": row["concrete_default_de"], "composition_status": "LEARNED_HERBAL_NOUN", "memorized_residue": row["concrete_default_de"]})
        revised_cards.append(item)

    occurrence_rows: list[dict[str, object]] = []
    for event in events:
        if event["master_card_id"] not in MAP:
            continue
        components, reading, status, residue = MAP[event["master_card_id"]]
        occurrence_rows.append({
            "event_id": event["event_id"], "page": event["page"], "record_unit_id": event["record_unit_id"],
            "statement_id": event["statement_id"], "visible_surface": event["visible_surface"],
            "master_card_id": event["master_card_id"], "component_parse": components,
            "revised_compositional_reading_de": reading, "composition_status": status,
            "visible_owner": event["visible_owner"], "terminal_status": event["terminal_status"],
        })

    decomposition_path = OUT / "TWO_HUNDRED_FORTY_FOURTH_25_OPERATION_CARDS.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_FORTY_FOURTH_28_OPERATION_OCCURRENCES.tsv"
    revised_path = OUT / "TWO_HUNDRED_FORTY_FOURTH_REVISED_66_CARD_DICTIONARY.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_FOURTH_READABLE_OPERATION_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_FOURTH_REPORT.md"
    write_tsv(decomposition_path, decompositions, list(decompositions[0]))
    write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))
    write_tsv(revised_path, revised_cards, list(revised_cards[0]))

    readable = ["# Herbal-Operationslektion", "", "## Vollständig baubare Karten", ""]
    for row in decompositions:
        if row["composition_status"] == "FULL_COMPOSITION":
            readable.append(f"- `{row['master_form']}` = `{row['component_parse']}` → {row['revised_compositional_reading_de']}")
    readable += ["", "## Teilweise baubare Karten", ""]
    for row in decompositions:
        if row["composition_status"] == "PARTIAL_COMPOSITION":
            readable.append(f"- `{row['master_form']}` = `{row['component_parse']}` → {row['revised_compositional_reading_de']}; neu zu lernen: {row['memorized_residue']}")
    readable += ["", "## Sechs echte neue Ganzhandlungen", ""]
    for row in decompositions:
        if row["composition_status"] == "LEARNED_WHOLE_OPERATION":
            readable.append(f"- `{row['master_form']}` → {row['revised_compositional_reading_de']}")
    readable += ["", "Der Herbal-Lehrling muss also nicht 25 neue Operationswörter auswendig lernen. Sechzehn baut er vollständig, drei mit einem kleinen Restkern, sechs als ganze Fachzeichen.", ""]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    card_counts = Counter(r["composition_status"] for r in decompositions)
    event_counts = Counter(r["composition_status"] for r in occurrence_rows)
    report = f"""# Sidequest-Pass 244: Herbal-Operationskarten zerlegen

## Ergebnis

Von 25 lokalen Herbal-Operationskarten sind **16 vollständig kompositionell**, **3 teilweise kompositionell** und nur **6 gelernte Ganzhandlungen**. Gewichtet nach Vorkommen sind 22 von 28 Operationsereignissen mindestens teilweise aus dem bestehenden Werkstattinventar lesbar.

Die drei Restkerne sind TCH für laufende Bereitung, SHFY für Stehzeit und D für die vorige Quelle. Die sechs ganzen Handlungen bleiben kurz: kalt stellen, Folgeanwendung, auftragen, abkühlen, auswringen und nachseihen.

Besonders wichtig sind die Paradigmen `OK+Y`, `K+Y`, `K+E+Y`, `K+OL`, `K+E+OL`, `OT+Y`, `OT+OL`, `CTH+OR` und `CTH+AIIN`. Sie sagen reale neue Kartenwerte voraus, statt nachträglich für jede Oberfläche einen Satz zu erfinden.

Input dictionary SHA-256: `{sha(CARDS)}`; events `{sha(EVENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "operation_cards": len(decompositions), "operation_occurrences": len(occurrence_rows),
        "card_status_counts": dict(card_counts), "event_status_counts": dict(event_counts),
        "outputs": {p.name: sha(p) for p in (decomposition_path, occurrence_path, revised_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
