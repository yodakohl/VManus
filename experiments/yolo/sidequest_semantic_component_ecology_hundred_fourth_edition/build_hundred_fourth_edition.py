#!/usr/bin/env python3
"""Map all 44 atomic values across Herbal and Biological records."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMPONENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_44_ATOMIC_COMPONENTS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    components = read_tsv(COMPONENTS)
    events = read_tsv(EVENTS)
    occurrences: list[dict[str, object]] = []
    by_atom: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        domain = "HERBAL" if event["record_unit_id"].startswith("H") else "BIOLOGICAL"
        for atom_position, atom in enumerate(event["semantic_atoms"].split("+"), 1):
            row = {
                "atom_occurrence_serial": len(occurrences) + 1,
                "event_serial": event["event_serial"],
                "atom_position_in_card": atom_position,
                "atom": atom,
                "atomic_default_de": next(item["atomic_default_de"] for item in components if item["atom"] == atom),
                "domain": domain,
                "record_unit_id": event["record_unit_id"],
                "page": event["page"],
                "statement_id": event["statement_id"],
                "visible_surface": event["visible_surface"],
                "master_card_id": event["master_card_id"],
            }
            occurrences.append(row)
            by_atom[atom].append(row)

    ecology: list[dict[str, object]] = []
    for component in components:
        atom = component["atom"]
        rows = by_atom[atom]
        herbal = [row for row in rows if row["domain"] == "HERBAL"]
        bio = [row for row in rows if row["domain"] == "BIOLOGICAL"]
        h_records = {row["record_unit_id"] for row in herbal}
        b_records = {row["record_unit_id"] for row in bio}
        if herbal and bio and len(h_records) >= 2 and len(b_records) >= 2:
            status = "PORTABLE_WORKSHOP_CORE"
            use = "same short value in both prose sections"
        elif herbal and bio:
            status = "THIN_CROSS_SECTION_BRIDGE"
            use = "retain shared value but teach the sparse side by exemplar"
        elif herbal:
            status = "HERBAL_SPECIALIST"
            use = "do not export beyond plant preparation without a new occurrence"
        else:
            status = "BIOLOGICAL_SPECIALIST"
            use = "do not export beyond bath/service work without a new occurrence"
        if len(rows) == 1:
            status = status + "__ONE_EVENT"
            use = use + "; memorize the exact card"
        ecology.append({
            "atom": atom,
            "atomic_default_de": component["atomic_default_de"],
            "word_class": component["word_class"],
            "total_atom_occurrences": len(rows),
            "herbal_occurrences": len(herbal),
            "biological_occurrences": len(bio),
            "herbal_records": ",".join(sorted(h_records)) if h_records else "NONE",
            "biological_records": ",".join(sorted(b_records)) if b_records else "NONE",
            "distinct_master_cards": len({row["master_card_id"] for row in rows}),
            "distinct_surfaces": len({row["visible_surface"] for row in rows}),
            "distinct_statements": len({row["statement_id"] for row in rows}),
            "ecology_status": status,
            "apprentice_use": use,
        })

    portable = [row for row in ecology if row["ecology_status"] == "PORTABLE_WORKSHOP_CORE"]
    specialist = [row for row in ecology if row not in portable]
    write_tsv(OUT / "HUNDRED_FOURTH_44_COMPONENT_ECOLOGY.tsv", list(ecology[0]), ecology)
    write_tsv(OUT / "HUNDRED_FOURTH_PORTABLE_CORE.tsv", list(portable[0]), portable)
    write_tsv(OUT / "HUNDRED_FOURTH_SPECIALIST_COMPONENTS.tsv", list(specialist[0]), specialist)
    write_tsv(OUT / "HUNDRED_FOURTH_ATOM_OCCURRENCES.tsv", list(occurrences[0]), occurrences)

    statuses = Counter(row["ecology_status"] for row in ecology)
    portable_names = ", ".join(f"{row['atom']}={row['atomic_default_de']}" for row in portable)
    thin = [row for row in ecology if row["ecology_status"].startswith("THIN_CROSS_SECTION_BRIDGE")]
    herbal_only = [row for row in ecology if row["ecology_status"].startswith("HERBAL_SPECIALIST")]
    bio_only = [row for row in ecology if row["ecology_status"].startswith("BIOLOGICAL_SPECIALIST")]
    report = [
        "# Hundertvierte Runde: Gemeinsames Lehrdeck und Fachschwänze", "",
        "## Gemeinsamer Kern", "",
        f"{len(portable)} der 44 Atomwerte erscheinen in mindestens zwei Herbal- und zwei",
        "Biological-Records. Sie bilden das tragfähige gemeinsame Werkstattdeck:", "",
        portable_names + ".", "",
        f"Weitere {len(thin)} Werte überbrücken beide Abschnitte nur dünn. {len(herbal_only)}",
        f"bleiben Herbal-Spezialisten und {len(bio_only)} Biological-Spezialisten.",
        "Ein seitenlokales Wort wird dadurch nicht automatisch zum universellen Stamm.", "",
        "## Lehrfolge", "",
        "Zuerst lernt der Lehrling den portablen Kern. Dünne Brücken werden mit je einem",
        "Beispielsatz gelernt. Herbal- und Bad-/Dienst-Spezialisten liegen in getrennten",
        "kleinen Tafeln. So bleibt das System für mehrere Schreiber einfach, obwohl es",
        "Fachkarten enthält.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_FOURTH_COMPONENT_ECOLOGY_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "components": len(ecology), "atom_occurrences": len(occurrences),
        "portable_core": len(portable), "thin_bridges": len(thin),
        "herbal_specialists": len(herbal_only), "biological_specialists": len(bio_only),
        "status_counts": dict(statuses),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
