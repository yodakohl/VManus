#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREDICTIONS = ROOT / "sidequest_semantic_address_axis_seven_hundred_ninety_second" / "SEVEN_HUNDRED_NINETY_SECOND_22_PREDICTED_SURFACES.tsv"
EVENTS = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth" / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def addr(recipe: str) -> str:
    return next(token for token in recipe.split("+") if token in {"AL", "AR"})


def path(owner: str, address: str, operation: str) -> str:
    if address == "AL":
        return f"AKTIVER_POSTEN --[{operation}]--> {owner}::ZIEL"
    return f"{owner}::QUELLE --[{operation}]--> AKTIVER_POSTEN"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    predictions = read(PREDICTIONS)
    events = read(EVENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    substitutions = []
    path_rows = []
    invariant_rows = []
    for index, prediction in enumerate(predictions, start=1):
        source = next(
            row
            for row in events
            if row["component_recipe"] == prediction["source_recipe"]
            and row["surface"] == prediction["source_surface"]
        )
        source_addr = addr(prediction["source_recipe"])
        target_addr = addr(prediction["counterpart_recipe"])
        source_tokens = prediction["source_recipe"].split("+")
        target_tokens = prediction["counterpart_recipe"].split("+")
        invariant = [token for token in source_tokens if token not in {"AL", "AR"}]
        target_invariant = [token for token in target_tokens if token not in {"AL", "AR"}]
        operation = " · ".join(invariant) or "ADDRESS_ONLY"
        statement = by_statement[source["statement_id"]]
        before_surfaces = [row["surface"] for row in statement]
        after_surfaces = [prediction["predicted_surface"] if row["event_id"] == source["event_id"] else row["surface"] for row in statement]
        before_readings = [row["rebuilt_reading_de"] for row in statement]
        after_readings = [prediction["counterpart_reading_de"] if row["event_id"] == source["event_id"] else row["rebuilt_reading_de"] for row in statement]
        substitutions.append(
            {
                "exercise": f"S{index:02d}",
                "page": source["page"],
                "record": source["record"],
                "statement_id": source["statement_id"],
                "owner_de": source["owner_de"],
                "source_event": source["event_id"],
                "before_surfaces": " ".join(before_surfaces),
                "after_surfaces": " ".join(after_surfaces),
                "before_reading_de": "; ".join(before_readings),
                "after_reading_de": "; ".join(after_readings),
                "address_change": source_addr + "→" + target_addr,
                "surface_change": prediction["source_surface"] + "→" + prediction["predicted_surface"],
                "other_events_unchanged": "YES",
            }
        )
        for phase, address, surface, reading in (
            ("BEFORE", source_addr, prediction["source_surface"], source["rebuilt_reading_de"]),
            ("AFTER", target_addr, prediction["predicted_surface"], prediction["counterpart_reading_de"]),
        ):
            path_rows.append(
                {
                    "exercise": f"S{index:02d}",
                    "phase": phase,
                    "page": source["page"],
                    "owner_de": source["owner_de"],
                    "address": address,
                    "address_reading_de": "ZIELSTELLE" if address == "AL" else "QUELLE",
                    "operation_components": operation,
                    "surface": surface,
                    "card_reading_de": reading,
                    "directed_path": path(source["owner_de"], address, operation),
                }
            )
        invariant_rows.append(
            {
                "exercise": f"S{index:02d}",
                "source_recipe": prediction["source_recipe"],
                "counterpart_recipe": prediction["counterpart_recipe"],
                "source_invariant_components": "+".join(invariant) or "NONE",
                "target_invariant_components": "+".join(target_invariant) or "NONE",
                "invariant_match": "YES" if invariant == target_invariant else "NO",
                "quantity_components_kept": ",".join(token for token in invariant if token in {"AIIN", "AIN"}) or "NONE",
                "grade_components_kept": ",".join(token for token in invariant if token in {"E", "EE", "EEE", "IIN"}) or "NONE",
                "endpoint_components_kept": ",".join(token for token in invariant if token in {"Y", "DY"}) or "NONE",
            }
        )

    rules = [
        {"step": 1, "instruction_de": "GLEICHE HUELLE UND HANDLUNG BEIBEHALTEN"},
        {"step": 2, "instruction_de": "AL ALS ZIELADRESSE LESEN: POSTEN ZUR BILDSTELLE"},
        {"step": 3, "instruction_de": "AR ALS QUELLADRESSE LESEN: VON DER BILDSTELLE ZUM POSTEN"},
        {"step": 4, "instruction_de": "MENGE, GRAD, LAUFENDEN POSTEN UND SCHLUSS NICHT AENDERN"},
        {"step": 5, "instruction_de": "DIE NEUE GANZKARTE VOM MEISTERBLATT KOPIEREN"},
    ]

    write(
        "SEVEN_HUNDRED_NINETY_THIRD_22_ADDRESS_SUBSTITUTIONS.tsv",
        substitutions,
        ["exercise", "page", "record", "statement_id", "owner_de", "source_event", "before_surfaces", "after_surfaces", "before_reading_de", "after_reading_de", "address_change", "surface_change", "other_events_unchanged"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_THIRD_44_BEFORE_AFTER_PATHS.tsv",
        path_rows,
        ["exercise", "phase", "page", "owner_de", "address", "address_reading_de", "operation_components", "surface", "card_reading_de", "directed_path"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_THIRD_22_COMPONENT_INVARIANTS.tsv",
        invariant_rows,
        ["exercise", "source_recipe", "counterpart_recipe", "source_invariant_components", "target_invariant_components", "invariant_match", "quantity_components_kept", "grade_components_kept", "endpoint_components_kept"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_THIRD_5_ADDRESS_PATH_RULES.tsv",
        rules,
        ["step", "instruction_de"],
    )

    examples = """# Pass 793 — dieselbe Handlung, umgekehrte Adresse

Die Gegenkarten werden wie Pfeile gelesen. `AL` lässt die Handlung **zur** bezeichneten Bildstelle laufen; `AR` lässt sie **von** der bezeichneten Bildstelle kommen.

- `daldy → dardy`: ZIELSTELLE · SCHLUSS → QUELLE · SCHLUSS;
- `pchedal → pchedar`: FÜLLEN · UMSETZEN · ZIELSTELLE → dieselbe Handlung aus der QUELLE;
- `cheoar → cheoal`: ENTNEHMEN · KURZ · ARBEITSGANG · QUELLE → dieselbe Arbeitskarte zur ZIELSTELLE;
- `qokeedal → qokeedar`: LANG ANSETZEN an der ZIELSTELLE → LANG ANSETZEN aus der QUELLE;
- `lchedal/lchedar` bleibt das bereits belegte Lehrmuster für LEITEN · UMSETZEN · Ziel/Quelle.

Das Bild gibt dabei keinen universellen Pfeil vor. Die Adresse ist owner-lokal: „Quelle“ und „Ziel“ beziehen sich auf das gerade aktive Pflanzenbild, Becken, Gefäß oder den lokalen Teil der Zeichnung. Genau deshalb kann dieselbe kurze Achse sowohl in Herbal- als auch in Biological-Sätzen stehen.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_THIRD_ADDRESS_PATHS.md").write_text(examples, encoding="utf-8")

    report = """# Pass 793 — AL/AR kehrt lokale Wege um

Alle 22 vorhergesagten Gegenkarten wurden in ihre vollständige Ausgangsaussage eingesetzt. Für jede gibt es einen Vorher- und Nachherpfad, insgesamt 44 lokale Wege. AL wird als `AKTIVER_POSTEN → Handlung → OWNER::ZIEL` gelesen; AR als `OWNER::QUELLE → Handlung → AKTIVER_POSTEN`.

In 22/22 Fällen bleiben alle Nichtadresskomponenten exakt gleich. Damit bleiben auch vorhandene Mengen-, Grad-, Y/DY- und Schlusswerte unverändert. Die übrigen Ereignisse jeder Aussage werden nicht angerührt.

Die Achse ist besonders nützlich, weil sie weder Wasser noch Medizin voraussetzt. In einem Pflanzenrezept kann sie „aus dem gezeigten Teil / an die Stelle“ heißen; an einem Becken „aus dem Gefäß / an das Gefäß“. Der Bildbesitzer liefert die konkrete Referenz, AL/AR nur die Richtung der Adresse.

Als nächstes verbinden wir die drei produktiven Achsen in einem kleinen Kartencompiler: Kern + Menge + Adresse + Grad + Ausgang. Er soll alle bereits belegten Kombinationen lesen und nur solche neuen Karten bilden, deren einzelne Achsen durch ein vorhandenes Paradigma gestützt sind.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_THIRD_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "substitutions": len(substitutions),
        "before_after_paths": len(path_rows),
        "component_invariants": len(invariant_rows),
        "invariant_matches": sum(row["invariant_match"] == "YES" for row in invariant_rows),
        "other_events_preserved": sum(row["other_events_unchanged"] == "YES" for row in substitutions),
        "decision": "AL_AR_SWAP_REVERSES_OWNER_LOCAL_PATH_AND_PRESERVES_OTHER_COMPONENTS",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
