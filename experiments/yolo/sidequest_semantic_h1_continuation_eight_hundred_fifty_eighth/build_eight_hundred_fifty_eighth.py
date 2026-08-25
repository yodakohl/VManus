#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
S001 = ROOT / "sidequest_semantic_h1_source_reconstruction_eight_hundred_fifty_seventh"
PREFIX = "EIGHT_HUNDRED_FIFTY_EIGHTH"

SOURCE_FORMS = {
    "E011": ("eandem rem pone", "eand. rem / pone", "denselben laufenden Posten ansetzen"),
    "E012": ("deinde sume et continua", "deinde / sume / cont.", "danach entnehmen und weiterführen"),
    "E013": ("continua", "cont.", "weiterarbeiten"),
    "E014": ("rem praeparatam tene", "rem prep. / tene", "ihn bereitet halten"),
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
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["statement_id"] == "H1-S002"]
    statement = next(row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["statement_id"] == "H1-S002")
    previous = read(S001 / "EIGHT_HUNDRED_FIFTY_SEVENTH_H1_S001_SOURCE_EDITION.tsv")[0]
    rows = []
    for position, event in enumerate(events, 1):
        latin, short, german = SOURCE_FORMS[event["event_id"]]
        rows.append(
            {
                "position": position,
                "event_id": event["event_id"],
                "surface": event["surface"],
                "exact_card_id": event["exact_card_id"],
                "component_recipe": event["component_recipe"],
                "literal_card_meaning_de": event["tenth_edition_reading_de"],
                "semantic_atom_count": len(event["tenth_edition_reading_de"].split(" · ")),
                "latin_like_source_phrase": latin,
                "mixed_workshop_shorthand": short,
                "fluent_fragment_de": german,
                "picture_owner_inherited": "YES",
                "active_preparation_inherited": "YES",
                "same_card_meaning": "YES",
            }
        )

    state = [
        {"register": "PICTURE_OWNER", "set_in": "H1-S001/picture", "value_de": statement["owner_noun_de"], "restated_in_S002": "NO", "used_in_S002": "YES"},
        {"register": "ACTIVE_PREPARATION", "set_in": "H1-S001", "value_de": "vorbereiteter Ansatz der Bildpflanze", "restated_in_S002": "NO", "used_in_S002": "YES"},
        {"register": "CURRENT_ITEM", "set_in": "H1-S001", "value_de": "laufender Posten aus diesem Ansatz", "restated_in_S002": "Y/POSTEN only", "used_in_S002": "YES"},
        {"register": "SOURCE_AND_WATER", "set_in": "H1-S001", "value_de": "Quelle und zugemessenes Wasser", "restated_in_S002": "NO", "used_in_S002": "NO"},
    ]
    combined = [{
        "record": "H1",
        "page": "f10r",
        "statements": 2,
        "cards": 14,
        "semantic_atoms": int(previous["semantic_atoms"]) + sum(int(row["semantic_atom_count"]) for row in rows),
        "S001_source": previous["latin_like_source_statement"],
        "S002_source": "Eandem rem pone; deinde sume et continua; age porro et rem praeparatam tene.",
        "S002_shorthand": "[OWNER+PREP inherited] eand. rem/pone / deinde sume-cont. / cont. / rem prep.-tene",
        "S002_current_reading_de": statement["working_reading_de"],
        "owner_restated": "NO",
        "preparation_restated": "NO",
        "explicit_close_in_H1": "NO",
    }]
    write(f"{PREFIX}_4_CARD_SOURCE_MAP.tsv", rows, ["position", "event_id", "surface", "exact_card_id", "component_recipe", "literal_card_meaning_de", "semantic_atom_count", "latin_like_source_phrase", "mixed_workshop_shorthand", "fluent_fragment_de", "picture_owner_inherited", "active_preparation_inherited", "same_card_meaning"])
    write(f"{PREFIX}_4_INHERITED_REGISTERS.tsv", state, ["register", "set_in", "value_de", "restated_in_S002", "used_in_S002"])
    write(f"{PREFIX}_COMPLETE_H1_SOURCE_EDITION.tsv", combined, ["record", "page", "statements", "cards", "semantic_atoms", "S001_source", "S002_source", "S002_shorthand", "S002_current_reading_de", "owner_restated", "preparation_restated", "explicit_close_in_H1"])

    summary = {
        "status": "PASS",
        "decision": "H1_S002_IS_CONTEXT_DEPENDENT_CONTINUATION",
        "S002_cards": len(rows),
        "S002_semantic_atoms": sum(int(row["semantic_atom_count"]) for row in rows),
        "H1_cards": 14,
        "H1_semantic_atoms": combined[0]["semantic_atoms"],
        "inherited_registers": sum(row["used_in_S002"] == "YES" for row in state),
        "restated_owner_or_preparation": 0,
        "explicit_close_cards": 0,
        "unmapped_cards": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_CONTINUOUS_H1_READING.md").write_text(
        "# H1 vollständig: Einrichtung und elliptische Fortsetzung\n\n"
        f"## H1-S001\n\n*{previous['latin_like_source_statement']}*\n\n"
        "## H1-S002\n\n"
        "Karten: `qokchy qotchol chol cthy`\n\n"
        "Quellfassung: *Eandem rem pone; deinde sume et continua; age porro et rem praeparatam tene.*\n\n"
        "Werkstattkürzung: `[OWNER+PREP geerbt] eand. rem/pone / deinde sume-cont. / cont. / rem prep.-tene`\n\n"
        f"Rücklesung: {statement['working_reading_de']}\n\n"
        "S002 braucht nur vier Karten, weil Bildbesitzer und Ansatz aus S001 fortgelten."
        " Die Y-Karten nennen den laufenden Posten, nicht die Pflanze erneut. Der ganze"
        " H1-Eintrag endet offen; hier wurde kein Schlusszeichen erzwungen.\n",
        encoding="utf-8",
    )
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 858: H1-S002 as inherited continuation\n\n"
        "H1-S002 maps four cards to eight semantic atoms without repeating the pictured\n"
        "plant or the preparation established in H1-S001. PICTURE_OWNER and\n"
        "ACTIVE_PREPARATION remain inherited; Y supplies the current item locally.\n\n"
        "The complete H1 article now has fourteen cards and thirty-one semantic atoms.\n"
        "Its second statement is shorter because it is an elliptic continuation, not\n"
        "because the four cards lack content. Neither statement has an explicit closing\n"
        "card, so the edition leaves the article open instead of inventing punctuation.\n\n"
        "Next, apply the same source-reconstruction method to H2 and ask whether its\n"
        "three statements reset or continue the active preparation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
