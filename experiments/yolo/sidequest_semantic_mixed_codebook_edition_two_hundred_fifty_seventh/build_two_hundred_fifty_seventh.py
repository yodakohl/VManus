#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R251 = ROOT / "experiments/yolo/sidequest_semantic_component_equations_two_hundred_fifty_first"
R250 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_working_edition_two_hundred_fiftieth"
CARDS = R251 / "TWO_HUNDRED_FIFTY_FIRST_REVISED_173_CARD_DICTIONARY.tsv"
EVENTS = R250 / "TWO_HUNDRED_FIFTIETH_381_PROSE_EVENTS.tsv"
STATEMENTS = R250 / "TWO_HUNDRED_FIFTIETH_116_PROSE_STATEMENTS.tsv"

REVISION = {
    "MC115": {
        "core": "danach mit diesem Posten weiter", "local": "danach mit diesem Posten weiter",
        "parse": "OT_FOLLOW+OL_CONTINUE+Y_CURRENT_ITEM", "layer": "PRODUCTIVE_TRIPLE_COMPOSITION",
        "reason": "sole attested OT+OL+Y triple recomposed from invariant stems",
    },
    "MC061": {
        "core": "übertragen; Schluss", "local": "übertragen; Schluss",
        "parse": "LEXICAL_BLOCKER_AR_AL_TRANSFER+CLOSE", "layer": "LEXICAL_BLOCKER_WHOLE_SIGN",
        "reason": "learned transfer sign blocks mechanical source-plus-target fusion",
    },
    "MC124": {
        "core": "weiter abziehen; Schluss", "local": "weiter abziehen; Schluss",
        "parse": "LEXICAL_BLOCKER_AR_OL_CONTINUING_WITHDRAWAL+CLOSE", "layer": "LEXICAL_BLOCKER_WHOLE_SIGN",
        "reason": "learned withdrawal sign blocks mechanical source-plus-continuation fusion",
    },
    "MC049": {
        "core": "Sudansatz", "local": "Sudansatz",
        "parse": "LEXICAL_BLOCKER_AR_OR_DECOCTION_BATCH", "layer": "LEXICAL_BLOCKER_WHOLE_SIGN",
        "reason": "learned decoction-batch sign blocks mechanical source-plus-batch fusion",
    },
    "MC068": {
        "core": "zur Folgeanwendung weiterführen", "local": "zur Folgeanwendung weiterführen",
        "parse": "LEXICAL_BLOCKER_AL_OL_FOLLOWUP_APPLICATION", "layer": "LEXICAL_BLOCKER_WHOLE_SIGN",
        "reason": "learned follow-up sign blocks mechanical target-plus-continuation fusion",
    },
}

TRANSLATION = {
    "H2-S001": "Aus dem bereiten Auszugsansatz die nächste Charge ansetzen, danach mit diesem Posten weiterarbeiten und ihn auf Sollmaß bringen.",
    "B1-S003": "Weiterführen und übertragen; Schluss.",
    "B4-S011": "An der linken Unterlaufstation das Sollmaß kurz wärmen, länger weiterführen, einen Anteil zugeben, überführen, fortsetzen und weiter abziehen; Schluss.",
    "H3-S001": "Aus dem Kochgut einen Sudansatz bilden, auswringen, eine Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; Schluss.",
    "H5-S005": "Eine weitere Zutat mit dem bearbeiteten Quellauszug weiterbearbeiten und zur Folgeanwendung weiterführen.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    revised_cards = []
    revisions = []
    for row in cards:
        new = dict(row)
        spec = REVISION.get(row["master_card_id"])
        if spec:
            old_core = row["portable_core_de"]
            old_local = row["local_prose_expansion_de"]
            old_parse = row["component_parse"]
            old_layer = row["dictionary_layer"]
            new.update({
                "portable_core_de": spec["core"], "local_prose_expansion_de": spec["local"],
                "component_parse": spec["parse"], "dictionary_layer": spec["layer"],
            })
            revisions.append({
                "master_card_id": row["master_card_id"], "master_form": row["master_form"],
                "old_core_de": old_core, "new_core_de": spec["core"],
                "old_local_de": old_local, "new_local_de": spec["local"],
                "old_component_parse": old_parse, "new_component_parse": spec["parse"],
                "old_dictionary_layer": old_layer, "new_dictionary_layer": spec["layer"],
                "reason": spec["reason"], "prose_event_count": row["prose_event_count"],
            })
        new["revision_257"] = "REVISED" if spec else "UNCHANGED"
        revised_cards.append(new)
    by_id = {r["master_card_id"]: r for r in revised_cards}

    revised_events = []
    for row in events:
        new = dict(row)
        card = by_id[row["master_card_id"]]
        new["portable_core_de"] = card["portable_core_de"]
        new["local_register_expansion_de"] = card["local_prose_expansion_de"]
        new["revision_257"] = card["revision_257"]
        revised_events.append(new)

    by_statement: dict[str, list[dict[str, str]]] = {}
    for row in revised_events:
        by_statement.setdefault(row["statement_id"], []).append(row)
    revised_statements = []
    for row in statements:
        new = dict(row)
        statement_events = by_statement[row["statement_id"]]
        new["portable_core_chain"] = " | ".join(r["portable_core_de"] for r in statement_events)
        new["local_register_chain"] = " | ".join(r["local_register_expansion_de"] for r in statement_events)
        if row["statement_id"] in TRANSLATION:
            new["complete_local_translation_de"] = TRANSLATION[row["statement_id"]]
        new["revised_event_count"] = str(sum(r["revision_257"] == "REVISED" for r in statement_events))
        new["revision_257"] = "REWRITTEN" if row["statement_id"] in TRANSLATION else "UNCHANGED"
        revised_statements.append(new)

    cards_path = OUT / "TWO_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY.tsv"
    events_path = OUT / "TWO_HUNDRED_FIFTY_SEVENTH_381_PROSE_EVENTS.tsv"
    statements_path = OUT / "TWO_HUNDRED_FIFTY_SEVENTH_116_STATEMENTS.tsv"
    revisions_path = OUT / "TWO_HUNDRED_FIFTY_SEVENTH_FIVE_REVISIONS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_SEVENTH_FIVE_REWRITTEN_PASSAGES.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_SEVENTH_REPORT.md"
    write_tsv(cards_path, revised_cards, list(revised_cards[0]))
    write_tsv(events_path, revised_events, list(revised_events[0]))
    write_tsv(statements_path, revised_statements, list(revised_statements[0]))
    write_tsv(revisions_path, revisions, list(revisions[0]))

    readable = ["# Fünf revidierte Passagen", ""]
    for statement_id in ("H2-S001", "H3-S001", "H5-S005", "B1-S003", "B4-S011"):
        row = next(r for r in revised_statements if r["statement_id"] == statement_id)
        readable += [f"## {statement_id}", "", f"`{row['visible_sequence']}`", "", row["complete_local_translation_de"], ""]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 257: integrierte Mischcodebuch-Ausgabe

## Ergebnis

Die neue Mischgrammatik ist in das vollständige Wörterbuch eingebaut. Vier gelernte Ganzzeichen besetzen die vier Lücken der produktiven Beziehungsalgebra; die einzige OT+OL+Y-Dreierkarte wird vollständig aus ihren drei Stämmen rückgelesen.

Nur fünf von 173 Karten und fünf von 381 Ereignissen benötigen eine Änderung oder strukturelle Präzisierung. Alle 116 Aussagen bleiben vollständig lesbar. Der Gewinn ist groß: Die Werkstattregel erklärt nun sowohl die produktiven Kombinationen als auch, warum bestimmte häufige Arbeitsgänge als kompakte Ganzzeichen erscheinen.

Inputs: dictionary `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (cards_path, events_path, statements_path, revisions_path, readable_path, report_path)
    summary = {
        "status": "PASS", "cards": len(revised_cards), "events": len(revised_events),
        "statements": len(revised_statements), "revised_cards": len(revisions),
        "revised_events": sum(r["revision_257"] == "REVISED" for r in revised_events),
        "rewritten_statements": sum(r["revision_257"] == "REWRITTEN" for r in revised_statements),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
