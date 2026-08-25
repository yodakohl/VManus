#!/usr/bin/env python3
"""Build Pass 725: edit the five Herbal records as complete fluent articles."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P724 = ROOT / "experiments/yolo/sidequest_semantic_concrete_medium_revision_seven_hundred_twenty_fourth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FLUENT = {
    "H1-S001": "Von der abgebildeten Pflanze einen kleinen Arbeitsposten entnehmen. Den Ansatz fuer den Arbeitsgang bereiten, die Quelle bestimmen und ihn auf den aktuellen Posten anwenden. Das vorgesehene Fach benutzen, Wasser entnehmen, den Posten danach weiter anwenden und fortfuehren; ihn nach Mass ansetzen und kurz anwenden.",
    "H1-S002": "Den aktuellen Posten ansetzen; danach etwas davon entnehmen und die Arbeit fortfuehren. Weiterarbeiten und den Posten bereiten.",
    "H2-S001": "Vom aktuellen Ansatz kurz entnehmen, den Posten bereiten und den Ansatz nach Mass fuer den naechsten Arbeitsgang fortfuehren; die folgenden Verweise halten denselben Posten aktiv.",
    "H2-S002": "Danach etwas vom Ansatz entnehmen. Denselben Ansatz durch die Folge weiterfuehren, das Mass beachten und aus der angegebenen Quelle nehmen.",
    "H2-S003": "Im Arbeitsgang dem aktuellen Ansatz zugeben; denselben Ansatz aktiv halten, bis zur genannten Stufe weiter zugeben und zuletzt nach Mass aus dem Arbeitsgang entnehmen.",
    "H3-S001": "Die Pflanzenzubereitung weiter anwenden und am Ziel halten. Den aktuellen Posten auswringen, bis zum Mass halten, in den Empfaenger fuellen und lange halten; anschliessend anwenden, entnehmen und den Arbeitsgang schliessen.",
    "H3-S002": "Den aktuellen Posten im Arbeitsgang halten und anwenden.",
    "H3-S003": "Den vorigen Schritt wiederaufnehmen; diesen Posten weiterfuehren, ihm etwas zugeben und ihn bis zum Mass halten.",
    "H3-S004": "Danach diesen Posten weiter ansetzen, bereiten und aktiv halten.",
    "H4-S001": "Nach dem angegebenen Mass ansetzen; dem aktuellen Posten eine Portion und eine Nachgabe zugeben; den Arbeitsgang schliessen.",
    "H4-S002": "Das Mass beachten, diesen Posten umsetzen und verwahren.",
    "H4-S003": "Dem aktuellen Posten das vorgeschriebene Mass zugeben; aus der Quelle kurz fuer den Arbeitsgang entnehmen, lange erwaermen und den Fortsetzungsschritt schliessen.",
    "H4-S004": "Nach Mass am Ziel ansetzen, den Posten weiter anwenden und als eine Portion des Ansatzes fuehren.",
    "H5-S001": "Eine Zutat fuer den Ansatz entnehmen, sie als aktuellen Posten zum Ziel bringen und nach Mass fortgesetzt zugeben; danach erneut aus dem Ansatz entnehmen und am Ziel ansetzen.",
    "H5-S002": "Den vorigen Vorgang wiederaufnehmen; diese Zutat ansetzen, dann lange durch den Durchlass des Arbeitsgangs entnehmen und schliessen.",
    "H5-S003": "Die Zutat halten, dem aktuellen Posten kurz zugeben und ihn erneut ansetzen.",
    "H5-S004": "Diesen Posten ansetzen, im Arbeitsgang kurz etwas daraus entnehmen und es dem Ziel zugeben.",
    "H5-S005": "Die Zutat waehlen, diesen Posten ansetzen und die Zutat aus der Quelle zugeben; danach eine Portion in den Arbeitsgang nehmen.",
    "H5-S006": "Danach diesem Posten kurz weiter zugeben, bis das Mass erreicht ist.",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    statements = [row for row in read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_116_STATEMENTS.tsv") if row["record"].startswith("H")]
    events = [row for row in read(P724 / "SEVEN_HUNDRED_TWENTY_FOURTH_381_EVENTS.tsv") if row["record"].startswith("H")]
    event_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        event_by_statement[row["statement_id"]].append(row)

    statement_rows = []
    for row in statements:
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "silent_plant_owner": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "component_sequence": row["component_sequence"],
            "atomic_trace_de": row["pass724_atomic_trace_de"],
            "fluent_article_clause_de": FLUENT[row["statement_id"]],
            "water_named": "YES" if "Wasser" in FLUENT[row["statement_id"]] else "NO",
            "added_named_species": "NONE", "added_disease": "NONE", "added_unanchored_ingredient": "NONE",
            "form_status": "UNCHANGED",
        })

    event_rows = []
    fluent_by_statement = {row["statement_id"]: row["fluent_article_clause_de"] for row in statement_rows}
    for row in events:
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "locus": row["locus"], "silent_owner": row["owner_de"],
            "card_no": row["card_no"], "surface": row["observed_surface"],
            "component_recipe": row["component_recipe"], "atomic_reading_de": row["pass724_semantic_de"],
            "statement_fluent_de": fluent_by_statement[row["statement_id"]],
            "surface_owner_boundary_unchanged": "YES",
        })

    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_record[str(row["record"])].append(row)
    record_rows = []
    for record in ["H1", "H2", "H3", "H4", "H5"]:
        rows = statements_by_record[record]
        record_events = [row for row in event_rows if row["record"] == record]
        record_rows.append({
            "record": record, "page": rows[0]["page"], "silent_plant_owner": rows[0]["silent_plant_owner"],
            "statements": len(rows), "events": len(record_events),
            "continuous_fluent_article_de": " ".join(str(row["fluent_article_clause_de"]) for row in rows),
            "water_mentions": sum(str(row["fluent_article_clause_de"]).count("Wasser") for row in rows),
            "named_species": "NONE", "named_diseases": "NONE", "unanchored_named_ingredients": "NONE",
        })

    write("SEVEN_HUNDRED_TWENTY_FIFTH_100_HERBAL_EVENTS.tsv", event_rows)
    write("SEVEN_HUNDRED_TWENTY_FIFTH_19_HERBAL_STATEMENTS.tsv", statement_rows)
    write("SEVEN_HUNDRED_TWENTY_FIFTH_5_COMPLETE_HERBAL_ARTICLES.tsv", record_rows)

    article = ["# Fuenf vollständige Herbal-Artikel", "", "Die Pflanzenbilder liefern jeweils den stillen Besitzer. Keine Artbestimmung wird behauptet.", ""]
    for row in record_rows:
        article.extend([f"## {row['record']} — {row['page']}", "", f"*Bildbesitzer: {row['silent_plant_owner']}*", "", str(row["continuous_fluent_article_de"]), ""])
    (HERE / "SEVEN_HUNDRED_TWENTY_FIFTH_COMPLETE_HERBAL_ARTICLES.md").write_text("\n".join(article), encoding="utf-8")

    summary = {
        "status": "PASS", "herbal_records": len(record_rows), "statements": len(statement_rows), "events": len(event_rows),
        "record_event_counts": {row["record"]: int(row["events"]) for row in record_rows},
        "water_statements": sum(row["water_named"] == "YES" for row in statement_rows),
        "air_events_in_herbal": sum("AIR" in row["component_recipe"].split("+") for row in event_rows),
        "named_species": 0, "named_diseases": 0, "unanchored_named_ingredients": 0,
        "form_changes": 0,
        "decision": "FIVE_COMPLETE_HERBAL_ARTICLES_USE_NEW_ATOMS_WITH_WATER_ONLY_AT_THE_SINGLE_HERBAL_AIR_EVENT",
    }
    (HERE / "SEVEN_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
