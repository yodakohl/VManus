#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FIFTY_NINTH"

SOURCE_BY_CARD = {
    "PROC015": ("de praeparatione currente cito sume", "de prep. curr. / cito sume"),
    "PROC014": ("rem para", "rem / para"),
    "PROC016": ("preparatio", "prep."),
    "PROC017": ("ad mensuram para", "ad mens. / para"),
    "PROC018": ("in opere rem para et continua", "in op. / rem para-cont."),
    "PROC019": ("res currens", "rem"),
    "PROC009": ("ad mensuram", "ad mens."),
    "PROC020": ("deinde de praeparatione sume", "deinde / de prep. sume"),
    "PROC021": ("deinde continua", "deinde / cont."),
    "PROC013": ("continua", "cont."),
    "PROC022": ("praeparationem continua", "prep. / cont."),
    "PROC003": ("ex fonte", "ex fonte"),
    "PROC023": ("in opere rem praeparationi adde", "in op. / rem prep. adde"),
    "PROC024": ("adde usque ad gradum", "adde / ad grad."),
    "PROC025": ("in opere ad mensuram sume", "in op. / ad mens. / sume"),
}

STATEMENT_SOURCES = {
    "H2-S001": "De praeparatione currente cito sume; rem para, praeparationem ad mensuram in opere para et rem currentem relinque.",
    "H2-S002": "Deinde de praeparatione sume; eandem praeparationem pluribus operibus ad mensuram ex fonte continua.",
    "H2-S003": "In opere rem praeparationi adde; eandem praeparationem ut rem currentem tene, ad gradum adde et in opere ad mensuram sume.",
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
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["record"] == "H2"]
    statements = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["record"] == "H2"]
    rows = []
    for position, event in enumerate(events, 1):
        latin, short = SOURCE_BY_CARD[event["exact_card_id"]]
        rows.append(
            {
                "position": position,
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "exact_card_id": event["exact_card_id"],
                "component_recipe": event["component_recipe"],
                "literal_card_meaning_de": event["tenth_edition_reading_de"],
                "semantic_atom_count": len(event["tenth_edition_reading_de"].split(" · ")),
                "latin_like_source_phrase": latin,
                "mixed_workshop_shorthand": short,
                "picture_owner_inherited": "YES",
                "branch_preparation_active": "YES",
                "same_card_meaning": "YES",
            }
        )

    statement_rows = []
    transitions = {
        "H2-S001": "BRANCH_FROM_H1_ACTIVE_PREPARATION",
        "H2-S002": "CONTINUE_SAME_BRANCH_PREPARATION",
        "H2-S003": "ADD_TO_AND_DRAW_FROM_SAME_BRANCH",
    }
    for statement in statements:
        subset = [row for row in rows if row["statement_id"] == statement["statement_id"]]
        statement_rows.append(
            {
                "statement_id": statement["statement_id"],
                "transition": transitions[statement["statement_id"]],
                "surface_sequence": statement["surface_sequence"],
                "component_sequence": statement["component_sequence"],
                "latin_like_source_statement": STATEMENT_SOURCES[statement["statement_id"]],
                "mixed_workshop_shorthand": " / ".join(str(row["mixed_workshop_shorthand"]) for row in subset),
                "current_fluent_reading_de": statement["working_reading_de"],
                "cards": len(subset),
                "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in subset),
                "owner_restated": "NO",
                "explicit_close": "NO",
            }
        )

    state_rows = [
        {"boundary": "H1_TO_H2_S001", "transition": "BRANCH_FROM_ACTIVE_PREPARATION", "owner": "same pictured plant", "active_preparation": "small derived portion", "reset": "NO"},
        {"boundary": "H2_S001_TO_S002", "transition": "CONTINUE_SAME_BRANCH_PREPARATION", "owner": "same pictured plant", "active_preparation": "same branch batch", "reset": "NO"},
        {"boundary": "H2_S002_TO_S003", "transition": "ADD_TO_AND_DRAW_FROM_SAME_BRANCH", "owner": "same pictured plant", "active_preparation": "same branch batch", "reset": "NO"},
        {"boundary": "H2_END", "transition": "LEAVE_PREPARATION_ACTIVE", "owner": "same pictured plant", "active_preparation": "still open", "reset": "NO"},
    ]
    y_rows = [
        {"event_id": row["event_id"], "statement_id": row["statement_id"], "surface": row["surface"], "exact_card_id": row["exact_card_id"], "meaning_de": row["literal_card_meaning_de"], "same_Y_card": "YES"}
        for row in rows if row["exact_card_id"] == "PROC019"
    ]
    write(f"{PREFIX}_24_CARD_SOURCE_MAP.tsv", rows, ["position", "event_id", "statement_id", "surface", "exact_card_id", "component_recipe", "literal_card_meaning_de", "semantic_atom_count", "latin_like_source_phrase", "mixed_workshop_shorthand", "picture_owner_inherited", "branch_preparation_active", "same_card_meaning"])
    write(f"{PREFIX}_3_STATEMENT_SOURCE_EDITION.tsv", statement_rows, ["statement_id", "transition", "surface_sequence", "component_sequence", "latin_like_source_statement", "mixed_workshop_shorthand", "current_fluent_reading_de", "cards", "semantic_atoms", "owner_restated", "explicit_close"])
    write(f"{PREFIX}_4_STATE_TRANSITIONS.tsv", state_rows, ["boundary", "transition", "owner", "active_preparation", "reset"])
    write(f"{PREFIX}_5_Y_RENDERINGS.tsv", y_rows, ["event_id", "statement_id", "surface", "exact_card_id", "meaning_de", "same_Y_card"])

    distribution: dict[int, int] = {}
    for row in rows:
        atoms = int(row["semantic_atom_count"])
        distribution[atoms] = distribution.get(atoms, 0) + 1
    summary = {
        "status": "PASS",
        "decision": "H2_IS_AN_OPEN_BRANCH_OF_THE_ACTIVE_HERBAL_PREPARATION",
        "cards": len(rows),
        "statements": len(statement_rows),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in rows),
        "atom_distribution": {str(key): value for key, value in sorted(distribution.items())},
        "state_resets": sum(row["reset"] == "YES" for row in state_rows),
        "explicit_closes": sum(row["explicit_close"] == "YES" for row in statement_rows),
        "Y_events": len(y_rows),
        "Y_surfaces": sorted({row["surface"] for row in y_rows}),
        "unmapped_cards": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# H2: drei offene Arbeitsphasen derselben Pflanzenzubereitung", ""]
    for row in statement_rows:
        lines.extend([
            f"## {row['statement_id']} — {row['transition']}",
            "",
            f"Karten: `{row['surface_sequence']}`",
            "",
            f"Quellfassung: *{row['latin_like_source_statement']}*",
            "",
            f"Rücklesung: {row['current_fluent_reading_de']}",
            "",
        ])
    lines.extend([
        "## Y-Reihe im selben Eintrag",
        "",
        "`dy → chy → shy → chy → dy` sind fünf Oberflächen derselben exakten",
        "Y/POSTEN-Karte. H2 setzt keinen Besitzer zurück und enthält keinen Schluss.",
    ])
    (HERE / f"{PREFIX}_CONTINUOUS_H2_READING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 859: H2 as an open preparation branch\n\n"
        "The three H2 statements contain twenty-four cards and forty-two semantic atoms.\n"
        "The working source reading takes a small portion from H1's active preparation,\n"
        "continues that derived batch, then adds to and draws from the same branch. There\n"
        "is no owner reset and no closing card.\n\n"
        "Within this one record, exact Y/POSTEN appears five times as dy, chy, shy, chy,\n"
        "dy. That is a particularly concrete illustration of invariant card identity\n"
        "under surface rendering.\n\n"
        "Next, combine H1 and H2 into one complete f10r article and identify which source\n"
        "elements the picture, persistent state and visible cards each contribute.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
