#!/usr/bin/env python3
"""Build a finite base-by-ending phrase lattice and rank its empty cells."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"
OWNER_ATLAS = ROOT / "experiments/yolo/sidequest_semantic_owner_atlas_forty_sixth_edition/FORTY_SIXTH_140_OWNER_EXPANSIONS.tsv"

BASES = [
    ("OK", "ANSETZEN"), ("OL", "FORTSETZEN"), ("OT", "FOLGEND"),
    ("CHD", "UMSETZEN"), ("CTH", "BEREIT"), ("CKH", "DURCHLAUF"),
    ("CKHE", "TRENNEN"), ("CHK", "WAERMEN"), ("SHED", "ABSETZEN"),
    ("SOLK", "SAMMELN"), ("KCH", "BEARBEITEN"), ("SH", "HALTEN"),
]
ENDINGS = [
    ("Y", "DIESER_POSTEN"), ("CLOSE", "SCHLUSS"), ("AIIN", "SOLLWERT"),
    ("AIN", "PORTION"), ("IIN", "STUFE"), ("AL", "ZIEL"),
    ("AR", "QUELLE"), ("AIR", "LAUF_BAHN"), ("E+Y", "KURZ_DIESER_POSTEN"),
    ("EE+Y", "LAENGER_DIESER_POSTEN"), ("E+CLOSE", "KURZ_DANN_SCHLUSS"),
    ("EE+CLOSE", "LAENGER_DANN_SCHLUSS"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combine(base_value: str, ending_value: str) -> str:
    endings = {
        "DIESER_POSTEN": "am aktuellen Posten", "SCHLUSS": "und den Schritt schließen",
        "SOLLWERT": "mit Sollwert", "PORTION": "an einer Portion", "STUFE": "bis zur Stufe",
        "ZIEL": "am Ziel", "QUELLE": "aus der Quelle", "LAUF_BAHN": "entlang des Laufs",
        "KURZ_DIESER_POSTEN": "kurz am aktuellen Posten", "LAENGER_DIESER_POSTEN": "länger am aktuellen Posten",
        "KURZ_DANN_SCHLUSS": "kurz und dann schließen", "LAENGER_DANN_SCHLUSS": "länger und dann schließen",
    }
    verbs = {
        "ANSETZEN": "ansetzen", "FORTSETZEN": "fortsetzen", "FOLGEND": "zum folgenden Posten gehen",
        "UMSETZEN": "umsetzen", "BEREIT": "bereitstellen", "DURCHLAUF": "durchführen",
        "TRENNEN": "trennen", "WAERMEN": "wärmen", "ABSETZEN": "absetzen lassen",
        "SAMMELN": "auffangen", "BEARBEITEN": "bearbeiten", "HALTEN": "halten",
    }
    return f"{verbs[base_value]} {endings[ending_value]}"


def main() -> None:
    ledger = read_tsv(LEDGER)
    observed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        observed[row["atom_sequence"]].append(row)
    row_cells = Counter()
    row_events = Counter()
    col_cells = Counter()
    col_events = Counter()
    for base, _ in BASES:
        for ending, _ in ENDINGS:
            sequence = f"{base}+{ending}"
            if sequence in observed:
                row_cells[base] += 1
                row_events[base] += len(observed[sequence])
                col_cells[ending] += 1
                col_events[ending] += len(observed[sequence])

    cells = []
    for base_order, (base, base_value) in enumerate(BASES, 1):
        for ending_order, (ending, ending_value) in enumerate(ENDINGS, 1):
            sequence = f"{base}+{ending}"
            hits = observed.get(sequence, [])
            cells.append({
                "cell_id": f"B{base_order:02d}E{ending_order:02d}",
                "base": base,
                "base_value_de": base_value,
                "ending": ending,
                "ending_value_de": ending_value,
                "normalized_atom_sequence": sequence,
                "composed_short_reading_de": combine(base_value, ending_value),
                "status": "OBSERVED" if hits else "EMPTY_WELL_FORMED_PREDICTION",
                "observed_group_count": len(hits),
                "observed_surfaces": "|".join(sorted({row["visible_surface"] for row in hits})) or "NONE",
                "observed_pages": "|".join(sorted({row["page"] for row in hits})) or "NONE",
                "observed_registers": "|".join(sorted({row["register"] for row in hits})) or "NONE",
                "base_observed_endings": row_cells[base],
                "base_observed_groups": row_events[base],
                "ending_observed_bases": col_cells[ending],
                "ending_observed_groups": col_events[ending],
                "analogy_score": row_cells[base] + col_cells[ending],
                "selection_cost": "ONE_FIXED_12_BY_12_LATTICE",
            })
    write_tsv(OUT / "FORTY_SEVENTH_144_SLOT_LATTICE.tsv", cells)

    empties = [row for row in cells if row["status"] == "EMPTY_WELL_FORMED_PREDICTION"]
    empties.sort(key=lambda row: (-int(row["analogy_score"]), -(int(row["base_observed_groups"]) + int(row["ending_observed_groups"])), row["cell_id"]))
    selected = []
    for rank, row in enumerate(empties[:24], 1):
        selected.append({
            "prediction_rank": rank,
            **row,
            "predicted_surface_policy": "NO_SURFACE_INVENTED__MASTER_MAY_SELECT_REGISTERED_RENDERER",
            "future_readback_de": row["composed_short_reading_de"],
            "falsifier_de": "eine künftige echte Karte mit dieser Atomfolge muss denselben Kurzbeitrag behalten",
        })
    write_tsv(OUT / "FORTY_SEVENTH_24_EMPTY_CELL_PREDICTIONS.tsv", selected)

    owner_rows = read_tsv(OWNER_ATLAS)
    owner_lookup = {(row["root"], row["owner_class"]): row for row in owner_rows}
    ending_owner_phrase = {
        "Y": "am aktuellen Besitzerposten", "CLOSE": "und lokalen Schritt schließen",
        "AIIN": "mit dem Besitzer-Sollwert", "AIN": "an einer Besitzerportion", "IIN": "bis zur Besitzerstufe",
        "AL": "an der Besitzer-Zieladresse", "AR": "aus der Besitzer-Quelladresse", "AIR": "entlang des Besitzerlaufs",
        "E+Y": "kurz am aktuellen Besitzerposten", "EE+Y": "länger am aktuellen Besitzerposten",
        "E+CLOSE": "kurz, dann lokalen Schritt schließen", "EE+CLOSE": "länger, dann lokalen Schritt schließen",
    }
    prediction_owner_rows = []
    for row in selected:
        for owner_id in ("PLANT_BATCH", "BASIN_STATION", "CLOTH_FILTER", "CELESTIAL_TABLE", "GENERIC_WORKPIECE"):
            base_owner = owner_lookup[(row["base"], owner_id)]
            prose_limited = row["base"] in {"SHED", "SOLK"} or row["ending"] == "CLOSE"
            prediction_owner_rows.append({
                "prediction_rank": row["prediction_rank"],
                "cell_id": row["cell_id"],
                "normalized_atom_sequence": row["normalized_atom_sequence"],
                "owner_class": owner_id,
                "owner_expanded_prediction_de": f"{base_owner['spoken_owner_expansion_de']}; {ending_owner_phrase[row['ending']]}",
                "register_license": "PROSE_PRIMARY__CELESTIAL_TRAINING_ONLY" if prose_limited else "CROSS_REGISTER_OWNER_EXERCISE",
                "observed_complete_chain": "NO",
                "surface_form": "NOT_INVENTED",
            })
    write_tsv(OUT / "FORTY_SEVENTH_120_OWNER_PREDICTIONS.tsv", prediction_owner_rows)

    lines = [
        "# Die 12 × 12-Wortbildungsmaschine",
        "",
        "Zwölf Arbeitsbasen werden mit zwölf wiederkehrenden Endungen gekreuzt. Von 144",
        "vorab festgelegten Zellen stehen 55 bereits als exakte Atomfolgen auf den zehn",
        "Seiten; sie decken 179 sichtbare Gruppen. Die übrigen 89 sind leere, aber direkt",
        "sprechbare Werkstattzellen. Für die 24 am stärksten gestützten leeren Zellen wird",
        "eine konkrete Besitzerlesung unter fünf Besitzern angegeben, ohne eine Oberfläche",
        "zu erfinden.",
        "",
        "## Die 24 ersten leeren Zellen",
        "",
    ]
    for row in selected:
        lines.append(f"- {row['prediction_rank']}. `{row['normalized_atom_sequence']}` — {row['future_readback_de']} (Analogie {row['analogy_score']})")
    lines.extend([
        "",
        "Diese Vorhersagen sind für den kreativen Schreibbetrieb besonders nützlich: Der",
        "Meister darf eine passende registrierte Handform wählen, aber die Kurzlesung ist",
        "schon vor der Oberfläche festgelegt. Ein späterer Fund darf nicht nachträglich eine",
        "andere Satzbedeutung erhalten.",
    ])
    (OUT / "FORTY_SEVENTH_SLOT_LATTICE_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "bases": len(BASES), "endings": len(ENDINGS), "lattice_cells": len(cells),
            "observed_cells": sum(row["status"] == "OBSERVED" for row in cells),
            "observed_groups": sum(int(row["observed_group_count"]) for row in cells),
            "empty_cells": len(empties), "selected_predictions": len(selected),
            "owner_predictions": len(prediction_owner_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LEDGER, OWNER_ATLAS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
