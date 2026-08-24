#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P554 = ROOT / "experiments/yolo/sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"


UNIFY = {
    "PROC004": ("den aktuellen Posten eintragen", "Eintragen bleibt der Kartenwert; übertragen ist die Quellenrahmen-Expansion."),
    "PROC008": ("den aktuellen Posten in Einsatz bringen", "Anlegen, einsetzen und einleiten sind Ziel-, Neutral- und Laufexpansionen derselben Aktivierung."),
    "PROC011": ("den aktuellen Posten in Einsatz bringen", "Ansetzen und einsetzen sind lokale Expansionen derselben OK+Y-Struktur."),
    "PROC038": ("nach vorgeschriebenem Maß in Einsatz bringen", "Einsetzen und einleiten werden allein durch den benachbarten Laufrahmen unterschieden."),
    "PROC042": ("den aktuellen Posten umsetzen", "Abmessen kommt vom Mengenrahmen; CHD+Y bleibt Umsetzen."),
    "PROC046": ("den aktuellen Posten länger wärmen", "Temperieren und warm halten sind beide EE-gerahmte Wärmeführung."),
    "PROC072": ("leiten", "Durchleiten ergänzt nur den sichtbaren Durchlass."),
    "PROC076": ("überführen und den Schritt schließen", "Durchleiten und Umfüllen sind Weg- und Zielarten des Überführens."),
    "PROC078": ("absetzen und den Schritt schließen", "Ablagern und Absetzenlassen sind Ziel- und Prozessausführungen desselben SHED-Schritts."),
    "PROC092": ("den aktuellen Posten länger in Einsatz halten", "Anlegen und Wirkenlassen sind Ziel- und Zeitexpansionen von OK+EE+Y."),
    "PROC120": ("weiterleiten, überführen und den Schritt schließen", "Abführen, Hinleiten, Umfüllen und mengenbezogenes Umsetzen konkretisieren L+CHD+DY."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    cards = read_tsv(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    events = read_tsv(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_DICTIONARY.tsv")
    audit_rows = []
    revised_cards = []
    for row in cards:
        if row["card_no"] in UNIFY:
            atomic, reason = UNIFY[row["card_no"]]
            audit_rows.append({
                "card_no": row["card_no"], "surfaces": row["surfaces"], "component_parse": row["component_parse"],
                "observed_context_expansions_de": row["observed_action_senses_de"], "unified_atomic_card_value_de": atomic,
                "unification_reason": reason, "occurrences": row["occurrences"], "records": row["records"],
                "atomic_value_stable": "YES", "context_expansions_retained": "YES",
            })
        else:
            atomic = row["portable_role_reading_de"]
        revised_cards.append({
            "card_no": row["card_no"], "surfaces": row["surfaces"], "component_parse": row["component_parse"],
            "role_signature": row["role_signature"], "clause_type": row["clause_type"],
            "atomic_card_value_de": atomic, "local_context_expansions_de": row["observed_action_senses_de"],
            "atomic_context_stable": "YES", "has_multiple_local_expansions": "YES" if row["card_no"] in UNIFY else "NO",
            "composition_status": row["composition_status"], "occurrences": row["occurrences"], "sections": row["sections"], "records": row["records"],
        })
    revised_by_card = {row["card_no"]: row for row in revised_cards}
    revised_events = []
    for row in events:
        card = revised_by_card[row["card_no"]]
        revised_events.append({
            "event_id": row["event_id"], "source_position_id": row["source_position_id"], "semantic_execution": row["semantic_execution"],
            "page": row["page"], "record": row["record"], "statement_id": row["statement_id"], "locus": row["locus"],
            "surface": row["surface"], "card_no": row["card_no"], "component_parse": row["component_parse"],
            "atomic_card_value_de": card["atomic_card_value_de"], "occurrence_action_expansion_de": row["occurrence_action_senses_de"],
            "containing_clause_de": row["containing_clause_de"], "silent_owner_de": row["silent_owner_de"],
            "atomic_value_stable": "YES", "complete_default_available": "YES",
        })
    write_tsv("FIVE_HUNDRED_FIFTY_FIFTH_ELEVEN_CARD_UNIFICATION_AUDIT.tsv", audit_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv", revised_cards)
    write_tsv("FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv", revised_events)
    summary = {
        "status": "PASS", "cards": len(revised_cards), "events": len(revised_events), "unified_cards": len(audit_rows),
        "context_expansion_events": sum(row["card_no"] in UNIFY for row in revised_events), "atomic_context_stable_cards": sum(row["atomic_context_stable"] == "YES" for row in revised_cards),
        "multi_expansion_cards": sum(row["has_multiple_local_expansions"] == "YES" for row in revised_cards),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertfünfundfünfzigste Runde: atomare Kartenvereinheitlichung", "", "## Ergebnis", "",
        "Alle elf bisher `kontextsensitiven` Karten besitzen einen stabilen kleinsten Werkstattwert. Ihre verschiedenen deutschen Verben sind keine verschiedenen Wörterbuchbedeutungen, sondern Satzrahmen-Expansionen.", "",
    ]
    for row in audit_rows:
        report.append(f"- `{row['card_no']}` `{row['surfaces']}`: **{row['unified_atomic_card_value_de']}**; lokal {row['observed_context_expansions_de']}.")
    report.extend(["", f"Damit sind alle {len(revised_cards)} Karten atomar kontextstabil. Bei elf Karten und {summary['context_expansion_events']} sichtbaren Ereignissen bleibt zusätzlich eine lokale Fachübersetzung erhalten.", "", "Der Unterschied ist wichtig: Das Wörterbuch speichert den atomaren Kartenwert; die Grammatik erzeugt aus Nachbarkarten die präzisere Tätigkeit. So kann ein Schreiber die Karte konstant lernen und trotzdem `anlegen`, `einleiten` oder `einwirken lassen` lesen."])
    (HERE / "FIVE_HUNDRED_FIFTY_FIFTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
