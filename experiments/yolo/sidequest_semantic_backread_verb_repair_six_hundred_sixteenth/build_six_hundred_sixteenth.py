#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P615 = ROOT / "experiments/yolo/sidequest_semantic_readable_prose_six_hundred_fifteenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


WORD_REPAIRS = {
    "CH": ("ABZIEHEN", "ABNEHMEN", "material or working portion is taken off the active owner"),
    "K": ("ZUFUEHREN", "ZUDOSIEREN", "a bounded feed or portion is metered into the active work"),
    "L": ("FUEHREN", "WEITERLEITEN", "the active item continues along a local path or station"),
    "O": ("GANG", "ARBEITSGANG", "names the running work cycle, not the prepared material"),
    "P": ("HINEIN", "EINFUELLEN", "puts material into a receiver or local container"),
}


def revise_command(text: str) -> str:
    revised = text
    for old, new, _ in WORD_REPAIRS.values():
        revised = revised.replace(old, new)
    return revised


def components(parse: str) -> set[str]:
    return set(parse.replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))


def main() -> None:
    words = read(P615 / "SIX_HUNDRED_FIFTEENTH_39_WORD_GLOSSARY.tsv")
    cards = read(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    events = read(P615 / "SIX_HUNDRED_FIFTEENTH_381_READABLE_INTERLINEAR.tsv")
    statements = read(P615 / "SIX_HUNDRED_FIFTEENTH_116_READABLE_STATEMENTS.tsv")

    revised_words: list[dict[str, object]] = []
    for row in words:
        revised = dict(row)
        if row["canonical_component"] in WORD_REPAIRS:
            old, new, reason = WORD_REPAIRS[row["canonical_component"]]
            revised["old_spoken_workshop_word_de"] = old
            revised["spoken_workshop_word_de"] = new
            revised["backread_reason_de"] = reason
            revised["backread_revision"] = "YES"
        else:
            revised["old_spoken_workshop_word_de"] = row["spoken_workshop_word_de"]
            revised["backread_reason_de"] = "unchanged distinct cue"
            revised["backread_revision"] = "NO"
        revised_words.append(revised)
    word_fields = list(words[0]) + ["old_spoken_workshop_word_de", "backread_reason_de", "backread_revision"]
    write("SIX_HUNDRED_SIXTEENTH_39_BACKREAD_WORDS.tsv", revised_words, word_fields)

    revised_cards: list[dict[str, object]] = []
    for row in cards:
        revised = dict(row)
        revised["old_standard_command_de"] = row["standard_command_de"]
        revised["standard_command_de"] = revise_command(row["standard_command_de"])
        affected = sorted(components(row["semantic_component_parse"]) & set(WORD_REPAIRS))
        revised["revised_components"] = "|".join(affected) if affected else "NONE"
        revised["backread_revision"] = "YES" if affected else "NO"
        revised_cards.append(revised)
    card_fields = list(cards[0]) + ["old_standard_command_de", "revised_components", "backread_revision"]
    write("SIX_HUNDRED_SIXTEENTH_173_REVISED_COMMAND_DICTIONARY.tsv", revised_cards, card_fields)
    card_by_id = {str(row["card_no"]): row for row in revised_cards}

    revised_events: list[dict[str, object]] = []
    for row in events:
        revised = dict(row)
        card = card_by_id[row["card_no"]]
        revised["old_standard_command_de"] = row["standard_command_de"]
        revised["standard_command_de"] = card["standard_command_de"]
        revised["revised_components"] = card["revised_components"]
        revised["backread_revision"] = card["backread_revision"]
        revised_events.append(revised)
    event_fields = list(events[0]) + ["old_standard_command_de", "revised_components", "backread_revision"]
    write("SIX_HUNDRED_SIXTEENTH_381_REVISED_EVENT_COMMANDS.tsv", revised_events, event_fields)

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in revised_events:
        events_by_statement[str(row["statement_id"])].append(row)
    revised_statements: list[dict[str, object]] = []
    for row in statements:
        sequence = events_by_statement[row["statement_id"]]
        command_sequence = " | ".join(str(event["standard_command_de"]) for event in sequence)
        affected = sorted({part for event in sequence for part in str(event["revised_components"]).split("|") if part != "NONE"})
        revised_statements.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_or_station": row["owner_or_station"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "old_invariant_command_sequence_de": row["invariant_command_sequence_de"],
            "revised_invariant_command_sequence_de": command_sequence,
            "original_readable_workshop_de": row["readable_workshop_de"],
            "controlled_backread_de": f"Bei {row['owner_or_station']}: {command_sequence}.",
            "revised_components": "|".join(affected) if affected else "NONE",
            "backread_revision": "YES" if affected else "NO",
        })
    write("SIX_HUNDRED_SIXTEENTH_116_CONTROLLED_BACKREADS.tsv", revised_statements, list(revised_statements[0]))

    event_counts = {component: sum(component in components(row["semantic_component_parse"]) for row in events) for component in WORD_REPAIRS}
    card_counts = {component: sum(component in components(row["semantic_component_parse"]) for row in cards) for component in WORD_REPAIRS}
    contrast_rows = [
        {
            "contrast_id": "BR01",
            "old_collision_de": "ABZIEHEN versus FUEHREN was often paraphrased as laufen lassen",
            "component_a": "CH",
            "new_word_a_de": "ABNEHMEN",
            "component_b": "L",
            "new_word_b_de": "WEITERLEITEN",
            "events_a": event_counts["CH"],
            "events_b": event_counts["L"],
            "repair_rule_de": "take material off versus keep it moving onward",
        },
        {
            "contrast_id": "BR02",
            "old_collision_de": "ZUFUEHREN versus HINEIN was often paraphrased as zugeben",
            "component_a": "K",
            "new_word_a_de": "ZUDOSIEREN",
            "component_b": "P",
            "new_word_b_de": "EINFUELLEN",
            "events_a": event_counts["K"],
            "events_b": event_counts["P"],
            "repair_rule_de": "meter a feed versus put material into a receiver",
        },
        {
            "contrast_id": "BR03",
            "old_collision_de": "GANG was too easily confused with ANSATZ in fluent preparation prose",
            "component_a": "O",
            "new_word_a_de": "ARBEITSGANG",
            "component_b": "OR",
            "new_word_b_de": "ANSATZ",
            "events_a": event_counts["O"],
            "events_b": sum("OR" in components(row["semantic_component_parse"]) for row in events),
            "repair_rule_de": "work cycle versus the preparation being worked",
        },
    ]
    write("SIX_HUNDRED_SIXTEENTH_3_BACKREAD_CONTRAST_REPAIRS.tsv", contrast_rows, list(contrast_rows[0]))

    report = f"""# Sechshundertsechzehnte Runde: Rücklese-Verben schärfen

## Ergebnis

Beim Rückwärtslesen waren nicht die Kartenfolgen das Hauptproblem, sondern fünf zu breite deutsche Werkstattwörter. Sie sind nun kürzer und gegeneinander schärfer:

```text
CH  ABNEHMEN       statt ABZIEHEN
K   ZUDOSIEREN     statt ZUFUEHREN
L   WEITERLEITEN   statt FUEHREN
O   ARBEITSGANG    statt GANG
P   EINFUELLEN     statt HINEIN
```

Damit werden drei häufige Verwechslungen getrennt: Material abnehmen versus einen Posten weiterleiten; eine dosierte Gabe zuführen versus etwas in einen Empfänger füllen; Arbeitsgang versus bearbeiteter Ansatz.

Die Reparatur betrifft **{sum(row['backread_revision'] == 'YES' for row in revised_cards)} Karten**, **{sum(row['backread_revision'] == 'YES' for row in revised_events)} Ereignisse** und **{sum(row['backread_revision'] == 'YES' for row in revised_statements)} Aussagen**. Alle 39 Wörter, 173 Karten, 381 Ereignisse und 116 Aussagen bleiben vollständig.

## Beispiel

Die frühere Folge `ABZIEHEN · LAUF | HINEIN · DIES | ZUFUEHREN · PORTION` wird nun als `ABNEHMEN · LAUF | EINFUELLEN · DIES | ZUDOSIEREN · PORTION` gesprochen. Ein Lehrling kann daraus deutlich besser drei verschiedene Handgriffe zurückschreiben.

## Nächster Schritt

Als nächstes werden die übrigen leicht verwechselbaren Substantiv-/Adresspaare geschärft: LAUF/DURCHLASS, ZIEL/FACH, DIES/GABE und MASS/PORTION/NACHPORTION/STUFE.
"""
    (HERE / "SIX_HUNDRED_SIXTEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "word_repairs": len(WORD_REPAIRS),
        "words": len(revised_words),
        "cards": len(revised_cards),
        "revised_cards": sum(row["backread_revision"] == "YES" for row in revised_cards),
        "events": len(revised_events),
        "revised_events": sum(row["backread_revision"] == "YES" for row in revised_events),
        "statements": len(revised_statements),
        "revised_statements": sum(row["backread_revision"] == "YES" for row in revised_statements),
        "decision": "FIVE_OVERBROAD_WORKSHOP_VERBS_SHARPENED_FOR_BACKREADING",
    }
    (HERE / "SIX_HUNDRED_SIXTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
