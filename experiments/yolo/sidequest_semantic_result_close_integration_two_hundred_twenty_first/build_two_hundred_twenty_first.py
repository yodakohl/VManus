#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R213 = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
R216 = ROOT / "experiments/yolo/sidequest_semantic_776_layered_edition_two_hundred_sixteenth"
R218 = ROOT / "experiments/yolo/sidequest_semantic_owner_expansion_debt_two_hundred_eighteenth"
DICTIONARY = R213 / "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv"
EVENTS = R213 / "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv"
STATEMENTS = R218 / "TWO_HUNDRED_EIGHTEENTH_116_TIGHTENED_STATEMENTS.tsv"
LAYERED = R216 / "TWO_HUNDRED_SIXTEENTH_776_LAYERED_LEDGER.tsv"

REVISED = {"MC019": "Schluss", "MC119": "Ergebnis"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = read(DICTIONARY)
    events = read(EVENTS)
    statements = read(STATEMENTS)
    layered = read(LAYERED)

    dictionary_out: list[dict[str, object]] = []
    for row in dictionary:
        dictionary_out.append({
            **row,
            "previous_current_value_de": row["current_value_de"],
            "current_value_de": REVISED.get(row["master_card_id"], row["current_value_de"]),
            "r221_revision": "THREE_OWNER_SIMPLIFICATION" if row["master_card_id"] in REVISED else "UNCHANGED",
        })
    write(OUT / "TWO_HUNDRED_TWENTY_FIRST_173_CARD_DICTIONARY.tsv", dictionary_out)

    events_out: list[dict[str, object]] = []
    by_statement: dict[str, list[dict[str, object]]] = {}
    for row in events:
        updated = {
            **row,
            "previous_portable_value_de": row["portable_value_de"],
            "portable_value_de": REVISED.get(row["master_card_id"], row["portable_value_de"]),
            "r221_revision": "THREE_OWNER_SIMPLIFICATION" if row["master_card_id"] in REVISED else "UNCHANGED",
        }
        events_out.append(updated)
        by_statement.setdefault(row["statement_id"], []).append(updated)
    write(OUT / "TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv", events_out)

    statement_overrides = {
        "H3-S001": "Kochgut zum Sud ansetzen, auswringen, Stehzeit abwarten, nachseihen, Ergebnis abnehmen und kalt stellen; Schluss.",
        "H4-S003": "Sollportion aus dem Quellauszug nehmen und länger bearbeiten; Schluss.",
        "B2-S012": "Abführgut auf Ergebnis kurz vorbereiten, länger einwirken, klar abziehen, auf Sollwert bringen und vollständig einsetzen; Schluss.",
        "B4-S010": "Schluss.",
        "B4-S015": "Anteil zum Ergebnis geben, Portion durch die Zielpassage führen, kurz sammeln und abführen; Schluss.",
    }
    statements_out: list[dict[str, object]] = []
    for row in statements:
        literal = " | ".join(str(item["portable_value_de"]) for item in by_statement[row["statement_id"]])
        layered_reading = row["layered_card_reading"].replace("[KERN:fertig]", "[KERN:Schluss]").replace("[KERN:Freigabewert]", "[KERN:Ergebnis]")
        statements_out.append({
            **row,
            "layered_card_reading": layered_reading,
            "r221_literal_card_reading": literal,
            "r221_owner_expansion_de": statement_overrides.get(row["statement_id"], row["r218_owner_expansion_de"]),
            "r221_revision": "RESULT_OR_CLOSE_REVISED" if row["statement_id"] in statement_overrides else "UNCHANGED",
        })
    write(OUT / "TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv", statements_out)

    layered_out: list[dict[str, object]] = []
    affected_rows: list[dict[str, object]] = []
    for row in layered:
        updated = dict(row)
        if row["normalized_id"] in REVISED:
            updated["portable_core_value_de"] = REVISED[row["normalized_id"]]
            if row["normalized_id"] == "MC019" and row["source_kind"] == "PROSE_EVENT":
                updated["local_expansion_de"] = "Schluss"
            if row["normalized_id"] == "MC119" and row["source_kind"] == "ASTRO_GROUP":
                prefix = row["local_expansion_de"].split(":", 1)[0]
                updated["local_expansion_de"] = f"{prefix}: Ergebnis oder abgelesener Diagrammwert."
            updated["r221_revision"] = "THREE_OWNER_SIMPLIFICATION"
            affected_rows.append(updated)
        else:
            updated["r221_revision"] = "UNCHANGED"
        layered_out.append(updated)
    write(OUT / "TWO_HUNDRED_TWENTY_FIRST_776_LAYERED_LEDGER.tsv", layered_out)
    write(OUT / "TWO_HUNDRED_TWENTY_FIRST_TEN_AFFECTED_OCCURRENCES.tsv", affected_rows)

    formula = [
        {"field": 1, "visible_cards": "chey aiin choky", "core_reading": "dies · Sollwert · einsetzen", "plant": "Diesen Pflanzenposten auf Sollwert bringen und einsetzen.", "bio": "Diesen Stationsposten auf Sollwert bringen und einsetzen.", "astro": "Diesen Diagrammposten auf Sollwert bringen und setzen."},
        {"field": 2, "visible_cards": "dar daiin dal", "core_reading": "davon · Sollwert · dorthin", "plant": "Davon den Sollwert nehmen und zur Zielzubereitung bringen.", "bio": "Davon den Sollwert nehmen und zur Zielstation bringen.", "astro": "Vom Bezugssektor den Sollwert zum Zielsektor führen."},
        {"field": 3, "visible_cards": "aiin okal oldy", "core_reading": "Sollwert · dorthin einsetzen · Schluss", "plant": "Sollwert an der Zielzubereitung einsetzen; Schluss.", "bio": "Sollwert an der Zielstation einsetzen; Schluss.", "astro": "Sollwert im Zielfeld setzen; Schluss."},
        {"field": 4, "visible_cards": "cheey", "core_reading": "Ergebnis", "plant": "Ergebnis: lokaler Pflanzenauszug.", "bio": "Ergebnis: lokaler Stationsablauf.", "astro": "Ergebnis: abgelesener Diagrammwert."},
    ]
    write(OUT / "TWO_HUNDRED_TWENTY_FIRST_REVISED_COMMON_FORMULA.tsv", formula)
    lines = [
        "# Revidierte gemeinsame Formel",
        "",
        "**dies – Sollwert – einsetzen; davon – Sollwert – dorthin; Sollwert – Ziel – Schluss; Ergebnis.**",
        "",
    ]
    for row in formula:
        lines.extend([
            f"## Feld {row['field']}: `{row['visible_cards']}`",
            "",
            f"Kern: **{row['core_reading']}**",
            "",
            f"- Pflanze: {row['plant']}",
            f"- Bio: {row['bio']}",
            f"- Astro: {row['astro']}",
            "",
        ])
    (OUT / "TWO_HUNDRED_TWENTY_FIRST_REVISED_COMMON_FORMULA.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "layered_source_sha256": hashlib.sha256(LAYERED.read_bytes()).hexdigest(),
        "dictionary_cards": len(dictionary_out),
        "prose_events": len(events_out),
        "statements": len(statements_out),
        "layered_groups": len(layered_out),
        "affected_occurrences": len(affected_rows),
        "affected_prose": sum(row["source_kind"] == "PROSE_EVENT" for row in affected_rows),
        "affected_astro": sum(row["source_kind"] == "ASTRO_GROUP" for row in affected_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
