#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P618 = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
P619 = ROOT / "experiments/yolo/sidequest_semantic_case_modules_six_hundred_nineteenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


WORDS = {
    "AIIN": "SOLLMASS", "AIN": "PORTION", "AL": "ZIELSTELLE", "AR": "VORRAT", "CH": "ABNEHMEN",
    "CHD": "UMSETZEN", "CKH": "DURCHLASSKANAL", "DA": "ZWEITMARKER", "DY": "SCHLUSS", "E": "KURZ",
    "EE": "LANG", "HO": "ZUTAT", "IIN": "ARBEITSSTUFE", "K": "ZUDOSIEREN", "L": "WEITERLEITEN",
    "O": "ARBEITSGANG", "OK": "ANSETZEN", "OL": "FORTSETZEN", "OR": "ANSATZ", "OT": "DANACH",
    "R": "KUEHLEN", "RESUME_CARD": "WIEDERAUFNEHMEN", "SH": "HALTEN", "SHED": "ABSETZEN",
    "SOLK": "AUFFANGEN", "Y": "ARBEITSPOSTEN",
}


def components(rows: list[dict[str, str]]) -> set[str]:
    result: set[str] = set()
    for row in rows:
        result.update(row["semantic_component_parse"].replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))
    return result


def main() -> None:
    events = read(P618 / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read(P619 / "SIX_HUNDRED_NINETEENTH_116_STATEMENT_MODULE_MAP.tsv")
    cases = read(P618 / "SIX_HUNDRED_EIGHTEENTH_6_CASE_NOUN_LEDGER.tsv")
    c5_events = [row for row in events if row["case_id"] == "C5"]
    c6_events = [row for row in events if row["case_id"] == "C6"]
    c5_statements = [row for row in statements if row["case_id"] == "C5"]
    c6_statements = [row for row in statements if row["case_id"] == "C6"]

    c5_modules = Counter(module for row in c5_statements for module in row["module_sequence"].split("|"))
    c6_modules = Counter(module for row in c6_statements for module in row["module_sequence"].split("|"))
    module_rows = []
    for module in sorted(set(c5_modules) | set(c6_modules)):
        module_rows.append({
            "module": module,
            "c5_statements": c5_modules[module],
            "c6_statements": c6_modules[module],
            "status": "SHARED" if c5_modules[module] and c6_modules[module] else "C5_ONLY" if c5_modules[module] else "C6_ONLY",
            "reading": "shared stock-handling grammar" if c5_modules[module] and c6_modules[module] else "preparation/transfer function" if c5_modules[module] else "receiver-side stock function",
        })
    write("SIX_HUNDRED_TWENTY_THIRD_7_MODULE_CONTRAST.tsv", module_rows, list(module_rows[0]))

    c5_components = components(c5_events)
    c6_components = components(c6_events)
    component_rows = []
    for component in sorted(c5_components | c6_components):
        in_c5 = component in c5_components
        in_c6 = component in c6_components
        component_rows.append({
            "component": component,
            "sharp_word_de": WORDS.get(component, component),
            "c5_present": "YES" if in_c5 else "NO",
            "c6_present": "YES" if in_c6 else "NO",
            "status": "SHARED" if in_c5 and in_c6 else "C5_ONLY" if in_c5 else "C6_ONLY",
            "functional_reading": "shared stock handling" if in_c5 and in_c6 else "C5 preparation/transfer" if in_c5 else "C6 cooling/collection",
        })
    write("SIX_HUNDRED_TWENTY_THIRD_26_COMPONENT_CONTRAST.tsv", component_rows, list(component_rows[0]))

    c5_cards = {row["card_no"] for row in c5_events}
    c6_cards = {row["card_no"] for row in c6_events}
    card_rows = []
    for card in sorted(c5_cards | c6_cards, key=lambda item: int(item[4:])):
        sample = next(row for row in events if row["card_no"] == card)
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in events if row["card_no"] == card})),
            "semantic_component_parse": sample["semantic_component_parse"],
            "standard_command_de": sample["standard_command_de"],
            "c5_occurrences": sum(row["card_no"] == card for row in c5_events),
            "c6_occurrences": sum(row["card_no"] == card for row in c6_events),
            "status": "SHARED" if card in c5_cards and card in c6_cards else "C5_ONLY" if card in c5_cards else "C6_ONLY",
        })
    write("SIX_HUNDRED_TWENTY_THIRD_35_CARD_CONTRAST.tsv", card_rows, list(card_rows[0]))

    statement_rows = []
    for row in c5_statements + c6_statements:
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "module_sequence": row["module_sequence"],
            "case_role": "PREPARE_TRANSFER_HOLD_STOCK" if row["case_id"] == "C5" else "COOL_COLLECT_DOSE_OPTIONAL_STOCK",
        })
    write("SIX_HUNDRED_TWENTY_THIRD_10_STATEMENT_CONTRAST.tsv", statement_rows, list(statement_rows[0]))

    revised_cases = []
    for row in cases:
        revised = dict(row)
        revised["pre_623_case_material_de"] = row["case_material_de"]
        revised["pre_623_application_de"] = row["application_de"]
        revised["c5_link_status"] = "NOT_APPLICABLE"
        if row["case_id"] == "C6":
            revised["case_material_de"] = "separater oder uebernommener gekuehlter Auffangvorrat ohne eigene Herbal-Seite"
            revised["application_de"] = "optionales offenes Kuehl-/Auffang-/Dosierformular am rechten B6-Lauf"
            revised["c5_link_status"] = "C5_PRODUCT_COMPATIBLE_BUT_NOT_EXPLICITLY_BOUND"
        revised_cases.append(revised)
    case_fields = list(cases[0]) + ["pre_623_case_material_de", "pre_623_application_de", "c5_link_status"]
    write("SIX_HUNDRED_TWENTY_THIRD_6_REVISED_CASE_NOUN_LEDGER.tsv", revised_cases, case_fields)

    c5_only = sorted(c5_components - c6_components)
    c6_only = sorted(c6_components - c5_components)
    side = f"""# C5 gegen C6: Übergabe oder unabhängiger Nachtrag?

## C5

C5 bereitet aus der H5-Bildpflanze einen konzentrierten Ansatz, adressiert und
überträgt ihn, hält/setzt ihn ab und schließt drei lokale Schritte. Exklusive
Kerne: `{' | '.join(f'{item}={WORDS[item]}' for item in c5_only)}`.

## C6

C6 besteht aus nur einer offenen B6-Aussage. Sie dosiert, adressiert,
fortsetzt und fängt auf; exklusiv sind `R=KUEHLEN` und `SOLK=AUFFANGEN`.

## Verbindung

C6 kann logisch das Produkt von C5 übernehmen: C5 erzeugt und überträgt,
C6 kühlt und fängt auf. Aber nur zwei exakte Karten werden geteilt, B5/B6 sind
bildlich getrennt, und kein sichtbarer Verweis bindet beide. Daher bleibt C6
ein optionaler Vorrats-/Auffangnachtrag, nicht das sichere Schlussfeld von C5.
"""
    (HERE / "SIX_HUNDRED_TWENTY_THIRD_C5_C6_SIDE_BY_SIDE.md").write_text(side, encoding="utf-8")

    report = f"""# Sechshundertdreiundzwanzigste Runde: C5 gegen C6

## Ergebnis

C5 hat neun Aussagen/38 Ereignisse; C6 nur eine Aussage/neun Ereignisse. Sie teilen zehn Komponenten, aber nur zwei exakte Karten. C6 ist weder Komponenten- noch Karten-Teilmenge von C5.

C5 besitzt vierzehn exklusive Kerne für Vorrat, Abnehmen, Umsetzen, Kanal, Abschluss, Zutat, Stufe, Arbeitsgang, Ansetzen, Danach/Wiederaufnehmen und Halten/Absetzen. C6 fügt KUEHLEN und AUFFANGEN hinzu und hat keinen Schluss.

Die beste Arbeitslesung wird daher korrigiert: C6 ist ein **offenes optionales Kuehl-/Auffang-/Dosierformular**. Es kann C5-Material übernehmen, ist aber nicht sichtbar daran gebunden. Der frühere feste `C6=geerbter C5-Vorrat`-Eindruck war zu eng.

## Nächster Schritt

Die sechs korrigierten Fälle werden nun zu einem gemeinsamen Werkstattablauf geordnet: welche sind vollständige Vorbereitung+Anwendung, welche Varianten und welche optionalen Anhänge? Danach wird Astro als separate Wahl-/Adressschicht wieder angefügt, ohne seine Labels zu übersetzen.
"""
    (HERE / "SIX_HUNDRED_TWENTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "c5_statements": len(c5_statements),
        "c6_statements": len(c6_statements),
        "c5_events": len(c5_events),
        "c6_events": len(c6_events),
        "shared_components": len(c5_components & c6_components),
        "c5_only_components": c5_only,
        "c6_only_components": c6_only,
        "shared_cards": len(c5_cards & c6_cards),
        "c6_component_subset_of_c5": c6_components <= c5_components,
        "c6_card_subset_of_c5": c6_cards <= c5_cards,
        "decision": "C6_OPTIONAL_STOCK_HANDLING_APPENDIX__NOT_PROVEN_C5_CONTINUATION",
    }
    (HERE / "SIX_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
