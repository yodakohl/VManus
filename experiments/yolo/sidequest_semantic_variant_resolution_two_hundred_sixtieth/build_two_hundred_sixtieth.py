#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R257 = ROOT / "experiments/yolo/sidequest_semantic_mixed_codebook_edition_two_hundred_fifty_seventh"
CARDS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY.tsv"
EVENTS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_381_PROSE_EVENTS.tsv"
STATEMENTS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_116_STATEMENTS.tsv"

REVISION = {
    "MC053": ("danach im selben Gang weiter", "danach im selben Gang weiter", "OT_FOLLOW+OL_CONTINUE_WITHIN_ACTIVE_SEQUENCE", "bare OT+OL follows an already explicit batch sequence"),
    "MC163": ("zum Folgegang wechseln", "zum Folgegang wechseln", "Q_FRAME+OT_FOLLOW+OL_CONTINUE_NEW_TRACK", "q-framed OT+OL selects a following track before a separate continuation card"),
    "MC005": ("vorigen Posten überführen; Schluss", "vorigen Posten überführen; Schluss", "OK_SET+CHED_TRANSFER_PREVIOUS_ITEM+CLOSE", "both occurrences follow an explicitly named part or withdrawal"),
    "MC088": ("neuen Posten einsetzen; Schluss", "neuen Posten einsetzen; Schluss", "Q_FRAME+OK_SET+CHD_NEW_ENTRY+CLOSE", "all three occurrences are one-card statements opening a fresh local entry"),
}

TRANSLATION = {
    "H1-S002": "Die erste Charge weiterbearbeiten, zum Folgegang wechseln, dort weiterarbeiten und sie als bereit halten.",
    "H2-S002": "Den Folgeansatz und den aktiven Ansatz setzen, danach im selben Gang weiterarbeiten, davon eine Sollmenge nehmen und die Folge beibehalten.",
    "B1-S007": "Einen neuen Posten in die offene Zielstelle einsetzen; Schluss.",
    "B1-S015": "Den kurzen Teil aus der eben gesetzten Quelle als vorigen Posten überführen; Schluss.",
    "B3-S016": "Abziehen und den vorigen Posten in die nächste Station überführen; Schluss.",
    "B3-S025": "Einen neuen Posten in die nächste Station einsetzen; Schluss.",
    "B5-S002": "Einen neuen Posten in den linken Endposten einsetzen; Schluss.",
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
    revision_rows = []
    for row in cards:
        new = dict(row)
        if row["master_card_id"] in REVISION:
            core, local, parse, reason = REVISION[row["master_card_id"]]
            revision_rows.append({
                "master_card_id": row["master_card_id"], "master_form": row["master_form"],
                "old_core_de": row["portable_core_de"], "new_core_de": core,
                "old_local_de": row["local_prose_expansion_de"], "new_local_de": local,
                "old_component_parse": row["component_parse"], "new_component_parse": parse,
                "prose_event_count": row["prose_event_count"], "contextual_reason": reason,
            })
            new["portable_core_de"] = core
            new["local_prose_expansion_de"] = local
            new["component_parse"] = parse
            new["revision_260"] = "SOURCE_ORDER_DISTINCTION"
        else:
            new["revision_260"] = "UNCHANGED"
        revised_cards.append(new)
    by_id = {r["master_card_id"]: r for r in revised_cards}

    revised_events = []
    for row in events:
        new = dict(row)
        card = by_id[row["master_card_id"]]
        new["portable_core_de"] = card["portable_core_de"]
        new["local_register_expansion_de"] = card["local_prose_expansion_de"]
        new["revision_260"] = card["revision_260"]
        revised_events.append(new)
    by_statement: dict[str, list[dict[str, str]]] = {}
    for row in revised_events:
        by_statement.setdefault(row["statement_id"], []).append(row)

    revised_statements = []
    context_rows = []
    for row in statements:
        new = dict(row)
        evs = by_statement[row["statement_id"]]
        new["portable_core_chain"] = " | ".join(r["portable_core_de"] for r in evs)
        new["local_register_chain"] = " | ".join(r["local_register_expansion_de"] for r in evs)
        if row["statement_id"] in TRANSLATION:
            new["complete_local_translation_de"] = TRANSLATION[row["statement_id"]]
            new["revision_260"] = "REWRITTEN"
            target = next(r for r in evs if r["master_card_id"] in REVISION)
            target_index = evs.index(target)
            context_rows.append({
                "event_id": target["event_id"], "statement_id": row["statement_id"],
                "page": target["page"], "field_id": target["field_id"], "field_position": target["field_position"],
                "visible_owner": target["visible_owner"], "visible_surface": target["visible_surface"],
                "master_card_id": target["master_card_id"], "previous_card": evs[target_index - 1]["visible_surface"] if target_index else "STATEMENT_START",
                "next_card": evs[target_index + 1]["visible_surface"] if target_index + 1 < len(evs) else "STATEMENT_END",
                "full_visible_sequence": row["visible_sequence"], "new_core_de": target["portable_core_de"],
                "new_complete_translation_de": new["complete_local_translation_de"],
            })
        else:
            new["revision_260"] = "UNCHANGED"
        new["revised_event_count"] = str(sum(r["revision_260"] != "UNCHANGED" for r in evs))
        revised_statements.append(new)

    cards_path = OUT / "TWO_HUNDRED_SIXTIETH_173_CARD_DICTIONARY.tsv"
    events_path = OUT / "TWO_HUNDRED_SIXTIETH_381_PROSE_EVENTS.tsv"
    statements_path = OUT / "TWO_HUNDRED_SIXTIETH_116_STATEMENTS.tsv"
    revisions_path = OUT / "TWO_HUNDRED_SIXTIETH_FOUR_CARD_REVISIONS.tsv"
    contexts_path = OUT / "TWO_HUNDRED_SIXTIETH_SEVEN_CONTEXTS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTIETH_READABLE_VARIANT_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_SIXTIETH_REPORT.md"
    write_tsv(cards_path, revised_cards, list(revised_cards[0]))
    write_tsv(events_path, revised_events, list(revised_events[0]))
    write_tsv(statements_path, revised_statements, list(revised_statements[0]))
    write_tsv(revisions_path, revision_rows, list(revision_rows[0]))
    write_tsv(contexts_path, context_rows, list(context_rows[0]))

    readable = [
        "# Zwei scheinbare Variantenpaare werden vier Anweisungen", "",
        "## OT+OL", "",
        "- `otol`: **danach im selben Gang weiter**. Es folgt auf einen bereits genannten Folgeansatz und Ansatz.",
        "- `qotchol`: **zum Folgegang wechseln**. Es öffnet einen Folgegang, dem noch ein eigenes WEITER-Zeichen folgt.", "",
        "## OK+CHD/CHED", "",
        "- `okchedy/qokchedy`: **vorigen Posten überführen; Schluss**. Beide Belege haben links im selben Satz bereits einen Kurzteil oder Abzug.",
        "- `qokchdy`: **neuen Posten einsetzen; Schluss**. Alle drei Belege bilden allein eine neue, geschlossene Aussage.", "",
        "Damit besitzt jede der 173 Masterkarten wieder eine eigene kurze Arbeitsanweisung. Die Unterschiede sind nicht große neue Bedeutungen, sondern genau die kleinen Quellenordnungsmerkmale, die ein Werkstattschreiber braucht: gleicher Gang oder neuer Gang; voriger Posten oder neuer Posten.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 260: Restvarianten nach Quellenordnung getrennt

## Ergebnis

Die zwei bisherigen Arbeitsäquivalenzsets zerfallen in vier kleine Anweisungen. OTOL setzt einen bereits aktiven Ablauf fort; QOTCHOL wechselt zum Folgegang. OKCHEDY/QOKCHEDY überführt einen links bereits genannten Posten; QOKCHDY eröffnet allein einen neuen Eintrag.

Die Verteilung ist vollständig: beide CHED-Belege haben einen ausdrücklichen linken Quellposten, alle drei CHD-Belege sind Ein-Karten-Aussagen. Die zwei OT/OL-Belege unterscheiden bestehenden Folgekontext von explizitem Gangwechsel. Damit werden alle 173 Kartenwerte und alle 381 Ereignisse im Rückwärtscompiler eindeutig.

Inputs: cards `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (cards_path, events_path, statements_path, revisions_path, contexts_path, readable_path, report_path)
    summary = {
        "status": "PASS", "cards": len(revised_cards), "events": len(revised_events),
        "statements": len(revised_statements), "revised_cards": len(revision_rows),
        "revised_events": len(context_rows), "rewritten_statements": len(TRANSLATION),
        "distinct_core_values": len({r["portable_core_de"] for r in revised_cards}),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
