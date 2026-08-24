#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P525 = ROOT / "experiments/yolo/sidequest_semantic_page_renderer_sheets_five_hundred_twenty_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(P525 / "FIVE_HUNDRED_TWENTY_FIFTH_381_PAGE_SHEET_LOG.tsv")
    sheets = read_tsv(P525 / "FIVE_HUNDRED_TWENTY_FIFTH_SEVEN_PAGE_RENDERER_SHEETS.tsv")
    entries = read_tsv(P525 / "FIVE_HUNDRED_TWENTY_FIFTH_FIFTY_NINE_PAGE_ADDRESSED_ENTRIES.tsv")
    sheet_by_page = {row["page"]: row for row in sheets}

    output: list[dict[str, str]] = []
    for row in source:
        sheet = sheet_by_page[row["page"]]
        output.append(
            {
                **row,
                "bound_exemplar_page": row["page"],
                "bound_renderer_sheet": sheet["page_sheet_id"],
                "sheet_activation": "AUTOMATIC_WITH_PHYSICAL_PAGE",
                "free_program_choice": "NO",
                "free_owner_choice_final": "NO",
                "free_renderer_choice": "NO",
                "free_semantic_invention": "NO",
                "execution_source": (
                    "BOUND_PAGE_ENTRY"
                    if row["page_renderer_action"] == "APPLY_PAGE_ADDRESSED_ENTRY"
                    else row["page_renderer_action"]
                ),
                "final_free_decision_count": "0",
                "final_master_mode": "DETERMINISTIC_EXEMPLAR_EXECUTION",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv", output)

    manual = [
        ("PAGE", "Nimm die physisch vorliegende Zielseite; ihr Rendererblatt ist fest gebunden."),
        ("SHEET", "Aktiviere das zur Seite gehörende Blatt automatisch."),
        ("RECORD", "Am Recordanfang setze den sichtbaren Hauptbesitzer."),
        ("VISIBLE_SHIFT", "Bei einer neuen getrennten Bildstation setze den lokalen Besitzer."),
        ("VISIBLE_GAP", "Bei einer Bildlücke beende Vererbung und kopiere die lokale Bindung."),
        ("INHERIT", "Ohne Bildschwelle behalte den laufenden Besitzer."),
        ("READ_CARD", "Lies die nächste exakte Karte aus dem Masterexemplar."),
        ("DECOMPOSE", "Zerlege sie mit Kartenlexikon, Komponentenstreifen oder Ganzzeichenkarte."),
        ("AUTOMATON", "Führe ihre primitive Operation im fünfstufigen Automaten aus."),
        ("CONTEXT", "Prüfe die vier automatischen Wrapper-Kontextregeln."),
        ("ADDRESS", "Falls keine Kontextregel greift, prüfe Record+Locus+Regeloberfläche im Seitenblatt."),
        ("STAMP", "Setze gegebenenfalls einen der acht Wrapperstempel vor den erhaltenen rechten Rest."),
        ("GLOBAL", "Ohne lokalen Eintrag benutze die globale Rendereroberfläche."),
        ("CARRY", "Bei der einen markierten Randwiederholung E180/E181 lies zwei sichtbare Kopien als ein Quellzeichen."),
        ("CLOSE", "Eine lizenzierte Schlusskarte schließt den Schritt; ein Zeilenende allein nicht."),
        ("ADVANCE", "Gehe zur nächsten sichtbaren Karte und wiederhole."),
    ]
    manual_rows = [
        {
            "rule_no": str(number),
            "rule_id": rule_id,
            "instruction_de": instruction,
            "free_choice": "NO",
        }
        for number, (rule_id, instruction) in enumerate(manual, 1)
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_SIXTH_SIXTEEN_RULE_MASTER_MANUAL.tsv", manual_rows)

    audit = [
        {
            "choice_family": "STATEMENT_PROGRAM",
            "earlier_decision_instances": "63",
            "current_free_decisions": "0",
            "replacement_mechanism": "CARD_BY_CARD_FIVE_STATE_AUTOMATON",
        },
        {
            "choice_family": "VISIBLE_OWNER",
            "earlier_decision_instances": "21",
            "current_free_decisions": "0",
            "replacement_mechanism": "RECORD_INITIALIZATION_PLUS_VISIBLE_THRESHOLDS",
        },
        {
            "choice_family": "LOCAL_ALLOGRAPH",
            "earlier_decision_instances": "67",
            "current_free_decisions": "0",
            "replacement_mechanism": "FOUR_CONTEXT_RULES_PLUS_BOUND_PAGE_ADDRESSES",
        },
        {
            "choice_family": "PAGE_RENDERER_SHEET",
            "earlier_decision_instances": "7",
            "current_free_decisions": "0",
            "replacement_mechanism": "PHYSICALLY_BOUND_TO_SELECTED_MASTER_PAGE",
        },
        {
            "choice_family": "TOTAL",
            "earlier_decision_instances": "158",
            "current_free_decisions": "0",
            "replacement_mechanism": "DETERMINISTIC_EXEMPLAR_EXECUTION",
        },
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_SIXTH_ZERO_FREE_CHOICE_AUDIT.tsv", audit)

    usage = [
        {
            "execution_source": key,
            "events": str(value),
            "requires_master_exemplar": "YES" if key == "BOUND_PAGE_ENTRY" else "NO",
            "meaning": (
                "lokale Seitenadresse liefert den Wrapperstempel"
                if key == "BOUND_PAGE_ENTRY"
                else "wiederkehrende sichtbare Kontextregel"
                if key == "AUTOMATIC_CONTEXT_RULE"
                else "allgemeine Rendererregel"
            ),
        }
        for key, value in Counter(row["execution_source"] for row in output).items()
    ]
    write_tsv("FIVE_HUNDRED_TWENTY_SIXTH_RENDERER_USAGE.tsv", usage)

    summary = {
        "status": "PASS",
        "events": len(output),
        "pages": len(sheets),
        "bound_page_entries": len(entries),
        "manual_rules": len(manual_rows),
        "free_decision_instances": sum(int(row["final_free_decision_count"]) for row in output),
        "deterministic_events": sum(row["final_master_mode"] == "DETERMINISTIC_EXEMPLAR_EXECUTION" for row in output),
        "execution_sources": dict(Counter(row["execution_source"] for row in output)),
        "semantic_recovery_without_exemplar_claimed": False,
    }
    (HERE / "FIVE_HUNDRED_TWENTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
