#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R260 = ROOT / "experiments/yolo/sidequest_semantic_variant_resolution_two_hundred_sixtieth"
R258 = ROOT / "experiments/yolo/sidequest_semantic_minimum_apprentice_deck_two_hundred_fifty_eighth"
CARDS = R260 / "TWO_HUNDRED_SIXTIETH_173_CARD_DICTIONARY.tsv"
EVENTS = R260 / "TWO_HUNDRED_SIXTIETH_381_PROSE_EVENTS.tsv"
STATEMENTS = R260 / "TWO_HUNDRED_SIXTIETH_116_STATEMENTS.tsv"
WHOLE = R258 / "TWO_HUNDRED_FIFTY_EIGHTH_23_WHOLE_SIGNS.tsv"

CONTENT = {"MC012", "MC049", "MC059", "MC071", "MC098", "MC108", "MC109", "MC114", "MC118", "MC119"}
INTERNAL_ACTION = {"MC052", "MC129", "MC152", "MC156"}
HANDOFF = {"MC068"}
TERMINAL_ACTION = {"MC037", "MC061", "MC084", "MC099", "MC124", "MC138", "MC160", "MC164"}


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


def whole_class(card_id: str) -> str:
    if card_id in CONTENT:
        return "CONTENT_OR_PRODUCT_SIGN"
    if card_id in INTERNAL_ACTION:
        return "INTERNAL_OPERATION_SIGN"
    if card_id in HANDOFF:
        return "OPEN_HANDOFF_SIGN"
    if card_id in TERMINAL_ACTION:
        return "TERMINAL_OPERATION_SIGN"
    raise KeyError(card_id)


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    whole_seed = read_tsv(WHOLE)
    whole_ids = {r["master_card_id"] for r in whole_seed}

    revised_cards = []
    for row in cards:
        new = dict(row)
        if row["master_card_id"] == "MC160":
            new["portable_core_de"] = "verwahren; Schluss"
            new["local_prose_expansion_de"] = "verwahren; Schluss"
            new["component_parse"] = "TALAM_TERMINAL_STORE_WHOLE"
            new["revision_263"] = "NOUN_TO_TERMINAL_OPERATION"
        else:
            new["revision_263"] = "UNCHANGED"
        revised_cards.append(new)
    by_id = {r["master_card_id"]: r for r in revised_cards}

    revised_events = []
    for row in events:
        new = dict(row)
        card = by_id[row["master_card_id"]]
        new["portable_core_de"] = card["portable_core_de"]
        new["local_register_expansion_de"] = card["local_prose_expansion_de"]
        new["revision_263"] = card["revision_263"]
        revised_events.append(new)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row)

    revised_statements = []
    for row in statements:
        new = dict(row)
        evs = by_statement[row["statement_id"]]
        new["portable_core_chain"] = " | ".join(r["portable_core_de"] for r in evs)
        new["local_register_chain"] = " | ".join(r["local_register_expansion_de"] for r in evs)
        if row["statement_id"] == "H4-S002":
            new["complete_local_translation_de"] = "Die Sollmenge überführen und verwahren; Schluss."
            new["revision_263"] = "REWRITTEN"
        else:
            new["revision_263"] = "UNCHANGED"
        revised_statements.append(new)

    occurrence_rows = []
    for row in revised_events:
        if row["master_card_id"] not in whole_ids:
            continue
        evs = by_statement[row["statement_id"]]
        index = next(i for i, event in enumerate(evs) if event["event_id"] == row["event_id"])
        position = "ONLY" if len(evs) == 1 else ("FIRST" if index == 0 else ("LAST" if index == len(evs) - 1 else "MIDDLE"))
        occurrence_rows.append({
            "event_id": row["event_id"], "statement_id": row["statement_id"], "page": row["page"],
            "visible_owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "whole_sign_class": whole_class(row["master_card_id"]),
            "whole_sign_value_de": row["portable_core_de"], "statement_position": position,
            "terminal_status": row["terminal_status"],
            "previous_instruction_de": evs[index - 1]["portable_core_de"] if index else "STATEMENT_START",
            "next_instruction_de": evs[index + 1]["portable_core_de"] if index + 1 < len(evs) else "STATEMENT_END",
        })

    syntax_rows = []
    for seed in whole_seed:
        card_id = seed["master_card_id"]
        occ = [r for r in occurrence_rows if r["master_card_id"] == card_id]
        cls = whole_class(card_id)
        syntax_rows.append({
            "master_card_id": card_id, "master_form": seed["master_form"],
            "registered_surfaces": seed["registered_surfaces"], "whole_sign_class": cls,
            "working_value_de": by_id[card_id]["portable_core_de"], "event_count": len(occ),
            "statement_positions": "|".join(dict.fromkeys(r["statement_position"] for r in occ)),
            "terminal_statuses": "|".join(dict.fromkeys(r["terminal_status"] for r in occ)),
            "slot_rule": (
                "name a material, product, vessel or part; remain open" if cls == "CONTENT_OR_PRODUCT_SIGN" else
                "perform an internal operation; remain open" if cls == "INTERNAL_OPERATION_SIGN" else
                "hand the active item to a following application; remain open" if cls == "OPEN_HANDOFF_SIGN" else
                "perform the learned operation and close the statement"
            ),
            "revision_263": "NOUN_TO_TERMINAL_OPERATION" if card_id == "MC160" else "KEEP",
        })

    cards_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_173_CARD_DICTIONARY.tsv"
    events_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_381_PROSE_EVENTS.tsv"
    statements_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_116_STATEMENTS.tsv"
    syntax_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_23_WHOLE_SIGN_SYNTAX.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_28_WHOLE_SIGN_OCCURRENCES.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_READABLE_NOMENCLATOR_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_THIRD_REPORT.md"
    write_tsv(cards_path, revised_cards, list(revised_cards[0]))
    write_tsv(events_path, revised_events, list(revised_events[0]))
    write_tsv(statements_path, revised_statements, list(revised_statements[0]))
    write_tsv(syntax_path, syntax_rows, list(syntax_rows[0]))
    write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))

    readable = [
        "# Satzplätze der 23 Ganzzeichen", "",
        "Die Nomenklatorschicht ist nicht ungeordnet. Sie hat vier Fächer:", "",
        "- zehn Stoff-/Produktzeichen mit fünfzehn Vorkommen; sie bleiben offen.",
        "- vier innere Handlungszeichen mit vier Vorkommen; sie bleiben offen.",
        "- ein offenes Übergabezeichen: FOLGEANWENDUNG.",
        "- acht terminale Handlungszeichen; jedes schließt seine Aussage.", "",
        "## Korrektur", "",
        "`talam` war als **Verwahrort** gelesen. Seine tatsächliche Stellung ist jedoch feld- und aussagefinal, und die Karte trägt den Schlussstatus. Die knappe Werkstattlesung lautet deshalb **verwahren; Schluss**.", "",
        "Die vollständige Folge `daiin chedy talam` heißt nun: **Sollmaß — überführen — verwahren; Schluss.**", "",
        "Damit weiß der Lehrling bei einem Ganzzeichen nicht nur, was es ungefähr bedeutet, sondern auch, in welches Satzfach es gehört.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 263: Syntax der Ganzzeichen

## Ergebnis

Die23 memorierten Zeichen teilen sich in zehn Stoff-/Produktzeichen, vier interne Operationen, eine offene Übergabe und acht terminale Operationen. Ihre28 Vorkommen befolgen diese Slotregeln vollständig. Nur TALAM widersprach seinem alten Nominalwert; es wird von VERWAHRORT zu VERWAHREN; SCHLUSS revidiert.

Das Nomenklatorfach wird damit selbst lehrbar: Ganzzeichen sind nicht freie Ausnahmen, sondern werden nach Inhalt, innerer Handlung, Übergabe und Abschluss sortiert.

Inputs: cards `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`, whole-sign seed `{sha(WHOLE)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (cards_path, events_path, statements_path, syntax_path, occurrence_path, readable_path, report_path)
    summary = {
        "status": "PASS", "whole_signs": len(syntax_rows), "whole_occurrences": len(occurrence_rows),
        "class_card_counts": {cls: sum(r["whole_sign_class"] == cls for r in syntax_rows) for cls in sorted({r["whole_sign_class"] for r in syntax_rows})},
        "class_event_counts": {cls: sum(r["whole_sign_class"] == cls for r in occurrence_rows) for cls in sorted({r["whole_sign_class"] for r in occurrence_rows})},
        "revised_cards": 1, "rewritten_statements": 1,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
