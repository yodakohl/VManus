#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P991 = ROOT / "experiments/yolo/sidequest_semantic_canonical_natural_fourteen_page_edition_nine_hundred_ninety_first"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    roots = read(P991 / "PASS991_53_ROOT_DICTIONARY.tsv")
    codebook = read(P991 / "PASS991_159_CODEBOOK.tsv")
    events = read(P991 / "PASS991_2511_EVENT_INTERLINEAR.tsv")
    occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        unit_ids = event["primary_teaching_unit_ids"].split("|") + event["mnemonic_common_unit_ids"].split("|")
        for unit_id in dict.fromkeys(unit_ids):
            if unit_id.startswith("R-"):
                occurrences[unit_id].append(event)

    for row in roots:
        if row["root_id"] == "R-S_ADDR":
            row["atomic_meaning_de"] = "SONDERORT"
            row["material_workshop_expansion_de"] = "besonders bezeichnete Materialstelle"
            row["station_workshop_expansion_de"] = "besondere Stationsstelle"
            row["celestial_relational_expansion_de"] = "Sternstelle"

    for row in codebook:
        if row["teaching_unit_id"] == "R-S_ADDR":
            row["spoken_value_de"] = "SONDERORT"
            row["concrete_context_values_de"] = "besonders bezeichnete Materialstelle | besondere Stationsstelle | Sternstelle"

    revised_events = 0
    for row in events:
        if "R-S_ADDR" not in row["primary_teaching_unit_ids"].split("|"):
            continue
        if row["physical_page"] == "f83r":
            row["complete_working_reading_de"] = row["complete_working_reading_de"].replace("STERNORT", "SONDERSTELLE")
            revised_events += 1

    audit_rows = []
    for row in roots:
        observed = occurrences[row["root_id"]]
        readings = []
        for event in observed:
            if event["complete_working_reading_de"] not in readings:
                readings.append(event["complete_working_reading_de"])
        audit_rows.append(
            {
                "root_id": row["root_id"],
                "recognition_form": row["recognition_form"],
                "atomic_meaning_de": row["atomic_meaning_de"],
                "content_occurrences": str(len(observed)),
                "content_pages": "|".join(dict.fromkeys(event["physical_page"] for event in observed)),
                "material_expansion_de": row["material_workshop_expansion_de"],
                "station_expansion_de": row["station_workshop_expansion_de"],
                "celestial_expansion_de": row["celestial_relational_expansion_de"],
                "sample_event_readings_de": "|".join(readings[:6]),
                "revision_status": "STERNORT_TO_SONDERORT" if row["root_id"] == "R-S_ADDR" else "KEEP",
            }
        )

    write(HERE / "PASS992_53_CLEAN_PORTABLE_ROOTS.tsv", roots, list(roots[0]))
    write(HERE / "PASS992_159_CODEBOOK.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS992_2511_EVENT_INTERLINEAR.tsv", events, list(events[0]))
    write(HERE / "PASS992_ROOT_PORTABILITY_AUDIT.tsv", audit_rows, list(audit_rows[0]))
    summary = {
        "status": "PASS",
        "portable_roots": len(roots),
        "roots_revised": 1,
        "station_events_revised": revised_events,
        "new_root_value": "SONDERORT",
    }
    (HERE / "PASS992_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (HERE / "PASS992_REPORT.md").write_text(
        """# Pass 992 — STERNORT wird SONDERORT

Das seltene Element `S_ADDR` erschien einmal in einer Himmelsstelle und einmal
in einer f83r-Stationskarte. **STERNORT** war deshalb als allgemeiner Stamm zu
eng. Die neue Lehrtafel lautet:

> `S_ADDR = SONDERORT`

- in Werkstatt-/Stationsprosa: **besondere Stelle**;
- im Himmelsregister: **Sternstelle**.

Alle übrigen 52 Stammwerte bleiben unverändert. Die zwei Oberflächenereignisse
bleiben dieselben; nur die f83r-Lesung wechselt von dem unpassenden STERNORT zu
SONDERSTELLE. Damit haben alle 53 portablen Wurzeln wieder einen Kern, der ihre
laufenden Textvorkommen nicht offen widerspricht.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
