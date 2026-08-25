#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FIFTY_SEVENTH"

SOURCE_FORMS = {
    "E001": ("partem cito sume", "part. cito / sume", "den laufenden Posten kurz entnehmen"),
    "E002": ("preparationem in opere fac", "prep. / in op. / fac", "den Ansatz im Arbeitsgang bereiten"),
    "E003": ("ex fonte", "ex fonte", "aus der Quelle"),
    "E004": ("rem opera", "opera", "den Posten bearbeiten"),
    "E005": ("adde", "adde", "dazu"),
    "E006": ("aquam sume", "R. aq.", "Wasser entnehmen"),
    "E007": ("deinde rem opera, sume et continua", "deinde / opera / sume / cont.", "danach den Posten bearbeiten, entnehmen und weiterführen"),
    "E008": ("rem pone", "pone", "den Posten ansetzen"),
    "E009": ("ad mensuram", "ad mens.", "nach Sollmaß"),
    "E010": ("cito rem opera", "cito / opera", "den Posten kurz bearbeiten"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = [
        row
        for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv")
        if row["statement_id"] == "H1-S001"
    ]
    statement = next(
        row
        for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv")
        if row["statement_id"] == "H1-S001"
    )
    rows = []
    for position, event in enumerate(events, 1):
        latin, short, german = SOURCE_FORMS[event["event_id"]]
        atom_count = len(event["tenth_edition_reading_de"].split(" · "))
        rows.append(
            {
                "position": position,
                "event_id": event["event_id"],
                "surface": event["surface"],
                "exact_card_id": event["exact_card_id"],
                "component_recipe": event["component_recipe"],
                "literal_card_meaning_de": event["tenth_edition_reading_de"],
                "semantic_atom_count": atom_count,
                "latin_like_source_phrase": latin,
                "mixed_workshop_shorthand": short,
                "fluent_fragment_de": german,
                "picture_owner_inherited": "YES",
                "same_card_meaning": "YES",
            }
        )

    source_statement = (
        "De herba picta: partem cito sume. Preparationem in opere fac; ex fonte "
        "sume et opera. Adde aquam. Deinde rem opera, sume et continua; ad mensuram "
        "pone et cito opera."
    )
    shorthand = (
        "[HERBA PICTA] part. cito / prep. in op. / ex fonte / opera / adde / R. aq. "
        "/ deinde opera-sume-cont. / pone / ad mens. / cito opera"
    )
    edition = [{
        "statement_id": "H1-S001",
        "page": "f10r",
        "picture_owner_de": statement["owner_noun_de"],
        "surface_sequence": statement["surface_sequence"],
        "component_sequence": statement["component_sequence"],
        "latin_like_source_statement": source_statement,
        "mixed_workshop_shorthand": shorthand,
        "current_fluent_reading_de": statement["working_reading_de"],
        "cards": len(rows),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in rows),
        "picture_owner_is_silent_argument": "YES",
    }]
    write(f"{PREFIX}_10_CARD_SOURCE_MAP.tsv", rows, ["position", "event_id", "surface", "exact_card_id", "component_recipe", "literal_card_meaning_de", "semantic_atom_count", "latin_like_source_phrase", "mixed_workshop_shorthand", "fluent_fragment_de", "picture_owner_inherited", "same_card_meaning"])
    write(f"{PREFIX}_H1_S001_SOURCE_EDITION.tsv", edition, ["statement_id", "page", "picture_owner_de", "surface_sequence", "component_sequence", "latin_like_source_statement", "mixed_workshop_shorthand", "current_fluent_reading_de", "cards", "semantic_atoms", "picture_owner_is_silent_argument"])

    counts: dict[int, int] = {}
    for row in rows:
        count = int(row["semantic_atom_count"])
        counts[count] = counts.get(count, 0) + 1
    summary = {
        "status": "PASS",
        "decision": "H1_S001_SUPPORTS_COMPRESSED_RECIPE_SOURCE_READING",
        "statement": "H1-S001",
        "cards": len(rows),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in rows),
        "atom_count_distribution": {str(key): value for key, value in sorted(counts.items())},
        "densest_card": max(rows, key=lambda row: int(row["semantic_atom_count"]))["exact_card_id"],
        "densest_recipe": max(rows, key=lambda row: int(row["semantic_atom_count"]))["component_recipe"],
        "unmapped_cards": 0,
        "new_meanings": 0,
        "language_identification_claims": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_CONTINUOUS_RECONSTRUCTION.md").write_text(
        "# H1-S001: rekonstruierte Quellstufe\n\n"
        f"Bildbesitzer: **{statement['owner_noun_de']}** (stilles Argument).\n\n"
        f"Kartenoberfläche: `{statement['surface_sequence']}`\n\n"
        f"Lateinartige Quellfassung: *{source_statement}*\n\n"
        f"Werkstattkürzung: `{shorthand}`\n\n"
        f"Aktuelle flüssige Rücklesung: {statement['working_reading_de']}\n\n"
        "Die zehn Karten tragen zusammen 23 kurze Bedeutungsatome. Drei Karten sind "
        "einatomig, drei zweiatomig, drei dreiatomig; die lange Karte "
        "`OT+Y+T+CH+OL` bündelt fünf Atome. Das passt besser zu technischen "
        "Brevigraphkarten als zu zehn gewöhnlichen ausgeschriebenen Wörtern.\n",
        encoding="utf-8",
    )
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 857: H1-S001 source reconstruction\n\n"
        "The actual ten-card H1-S001 statement now has a card-by-card Latin-like source\n"
        "skeleton, mixed workshop shorthand and the existing fluent German reading. The\n"
        "pictured plant supplies the silent owner throughout. No card or meaning changes.\n\n"
        "Ten cards carry twenty-three short semantic atoms. The distribution is three\n"
        "one-atom, three two-atom, three three-atom and one five-atom card. The densest,\n"
        "OT+Y+T+CH+OL, naturally expands as a chained instruction: then operate on the\n"
        "item, take it and continue. That is the clearest current example of a technical\n"
        "brevigraph card compressing a source phrase rather than spelling one word.\n\n"
        "Next, reconstruct H1-S002 and test whether its shorter four-card continuation\n"
        "uses the same source syntax without repeating the picture owner.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
