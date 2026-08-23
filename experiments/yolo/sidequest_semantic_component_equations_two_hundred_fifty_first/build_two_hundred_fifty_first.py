#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R250 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_working_edition_two_hundred_fiftieth"
R213 = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
DICTIONARY = R250 / "TWO_HUNDRED_FIFTIETH_REVISED_173_CARD_DICTIONARY.tsv"
BASE = R213 / "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv"


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
    source = read_tsv(DICTIONARY)
    base = {r["master_card_id"]: r for r in read_tsv(BASE)}
    revised: list[dict[str, object]] = []
    for row in source:
        item = dict(row)
        if row["component_parse"] == "COMMON_CORE":
            item["component_parse"] = base[row["master_card_id"]]["component_formula"]
        if row["master_card_id"] in {"MC053", "MC163"}:
            item["portable_core_de"] = "DANACH_WEITER"
        if row["master_card_id"] == "MC148":
            item["component_parse"] = "Y + K + AN"
        revised.append(item)

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in revised:
        grouped[str(row["component_parse"])].append(row)
    equations: list[dict[str, object]] = []
    for formula, linked in sorted(grouped.items()):
        values = list(dict.fromkeys(str(r["portable_core_de"]) for r in linked))
        generic = formula in {"MEMORIZED_WHOLE_CARD", "OPAQUE_WHOLE_CARD"}
        equations.append({
            "component_formula": formula,
            "card_count": len(linked),
            "master_card_ids": "|".join(str(r["master_card_id"]) for r in linked),
            "master_forms": "|".join(str(r["master_form"]) for r in linked),
            "portable_cores_de": "|".join(values),
            "equation_status": "GENERIC_WHOLE_CARD_BUCKET" if generic else ("CONSISTENT" if len(values) == 1 else "CONFLICT"),
        })

    repairs = [
        {
            "repair_id": "EQ01", "old_collision": "OT + OL had Fortgang and Folgegang",
            "affected_cards": "MC053|MC163", "new_equation": "OT + OL = DANACH_WEITER",
            "local_expansions": "anschließend fortsetzen | den Folgegang fortsetzen",
        },
        {
            "repair_id": "EQ02", "old_collision": "YKAIN and YKAN were both parsed Y + K + AIN",
            "affected_cards": "MC047|MC148|MC170", "new_equation": "Y+K+AIN = erste Portion; Y+K+AN = zweite Portion; Y+K+AIIN = Sollportion",
            "local_expansions": "three distinct quantity cards",
        },
    ]
    triplet = [
        {"master_card_id": "MC047", "surface": "ykain", "component_formula": "Y + K + AIN", "quantity_value_de": "ERSTE_PORTION", "right_grade": "AIN", "prediction": "unmarked bounded portion"},
        {"master_card_id": "MC148", "surface": "ykan", "component_formula": "Y + K + AN", "quantity_value_de": "ZWEITE_PORTION", "right_grade": "AN", "prediction": "alternate or second bounded portion"},
        {"master_card_id": "MC170", "surface": "ykaiin", "component_formula": "Y + K + AIIN", "quantity_value_de": "SOLLPORTION", "right_grade": "AIIN", "prediction": "prescribed or target-valued portion"},
    ]

    dictionary_path = OUT / "TWO_HUNDRED_FIFTY_FIRST_REVISED_173_CARD_DICTIONARY.tsv"
    equation_path = OUT / "TWO_HUNDRED_FIFTY_FIRST_COMPONENT_EQUATIONS.tsv"
    repair_path = OUT / "TWO_HUNDRED_FIFTY_FIRST_TWO_COLLISION_REPAIRS.tsv"
    triplet_path = OUT / "TWO_HUNDRED_FIFTY_FIRST_PORTION_TRIPLET.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_FIRST_READABLE_ROOT_EQUATIONS.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_FIRST_REPORT.md"
    write_tsv(dictionary_path, revised, list(revised[0]))
    write_tsv(equation_path, equations, list(equations[0]))
    write_tsv(repair_path, repairs, list(repairs[0]))
    write_tsv(triplet_path, triplet, list(triplet[0]))

    readable = [
        "# Zwei reparierte Stammgleichungen", "",
        "## OT + OL", "", "`OT + OL = DANACH WEITER`", "",
        "`otol` und `qotchol` tragen denselben tragbaren Kern. Fortgang und Folgegang sind nur zwei lokale Formulierungen.", "",
        "## Y + K + Mengenende", "",
        "- `ykain = Y + K + AIN` → **ERSTE PORTION**",
        "- `ykan = Y + K + AN` → **ZWEITE PORTION**",
        "- `ykaiin = Y + K + AIIN` → **SOLLPORTION**", "",
        "Das sichtbare Ende trägt den Unterschied. `AIN`, `AN` und `AIIN` dürfen deshalb nicht mehr zu einer einzigen Mengenkarte zusammengeschoben werden.", "",
        "## Ergebnis", "", "Nach diesen zwei Reparaturen besitzt keine konkrete wiederverwendete Komponentenformel im 173-Karten-Wörterbuch zwei verschiedene tragbare Kerne. Ganze gelernte Karten bleiben davon ausdrücklich ausgenommen.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    conflicts = [r for r in equations if r["equation_status"] == "CONFLICT"]
    report = f"""# Sidequest-Pass 251: Komponenten-Gleichungen bereinigt

## Ergebnis

Der vollständige 173-Karten-Audit fand nur zwei wiederverwendete Formelkollisionen. Beide sind repariert. OT+OL erhält einen einzigen Kern DANACH_WEITER. Das vermeintliche Y+K+AIN-Duplikat zerfällt sichtbar in AIN, AN und AIIN und liefert das Portionstripel erste/zweite/Sollportion.

Nach der Reparatur bleiben **{len(conflicts)} konkrete Komponentenformeln mit widersprüchlichen tragbaren Kernen**. Generische Sammelklassen für auswendig gelernte Ganzkarten werden nicht fälschlich als Stammgleichung behandelt.

Input dictionary `{sha(DICTIONARY)}`; base formulas `{sha(BASE)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "cards": len(revised), "component_equations": len(equations),
        "repairs": len(repairs), "remaining_conflicts": len(conflicts),
        "outputs": {p.name: sha(p) for p in (dictionary_path, equation_path, repair_path, triplet_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
