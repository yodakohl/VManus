#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
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


WORD = {
    "AIIN": "SOLLMASS", "AIN": "PORTION", "AIR": "FLUESSIGKEITSLAUF", "AL": "ZIELSTELLE", "AN": "NACHPORTION",
    "AR": "VORRAT", "CFH": "AUSWRINGEN", "CH": "ABNEHMEN", "CHD": "UMSETZEN", "CHK": "WAERMEN",
    "CKH": "DURCHLASSKANAL", "CTH": "BEREIT", "DY": "SCHLUSS", "E": "KURZ", "EE": "LANG",
    "EEE": "VOLL", "IIN": "ARBEITSSTUFE", "K": "ZUDOSIEREN", "L": "WEITERLEITEN", "LD": "BEFESTIGEN",
    "O": "ARBEITSGANG", "OK": "ANSETZEN", "OL": "FORTSETZEN", "OR": "ANSATZ", "OT": "DANACH",
    "P": "EINFUELLEN", "R": "KUEHLEN", "RESUME_CARD": "WIEDERAUFNEHMEN", "SH": "HALTEN", "SHED": "ABSETZEN",
    "SOLK": "AUFFANGEN", "T": "EINTRAGEN", "TALAM": "VERWAHREN", "Y": "ARBEITSPOSTEN",
}


def components(rows: list[dict[str, str]]) -> set[str]:
    result: set[str] = set()
    for row in rows:
        result.update(row["semantic_component_parse"].replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))
    return result


def main() -> None:
    events = read(P618 / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read(P619 / "SIX_HUNDRED_NINETEENTH_116_STATEMENT_MODULE_MAP.tsv")
    c3_events = [row for row in events if row["case_id"] == "C3"]
    c4_events = [row for row in events if row["case_id"] == "C4"]
    c3_statements = [row for row in statements if row["case_id"] == "C3"]
    c4_statements = [row for row in statements if row["case_id"] == "C4"]

    c3_modules = Counter(module for row in c3_statements for module in row["module_sequence"].split("|"))
    c4_modules = Counter(module for row in c4_statements for module in row["module_sequence"].split("|"))
    module_names = sorted(set(c3_modules) | set(c4_modules))
    module_rows = []
    for module in module_names:
        module_rows.append({
            "module": module,
            "c3_statements": c3_modules[module],
            "c4_statements": c4_modules[module],
            "difference_c3_minus_c4": c3_modules[module] - c4_modules[module],
            "reading": "SHARED_MODULE_DIFFERENT_FREQUENCY" if c3_modules[module] and c4_modules[module] else "CASE_SPECIFIC_MODULE",
        })
    write("SIX_HUNDRED_TWENTY_FIRST_8_MODULE_CONTRAST.tsv", module_rows, list(module_rows[0]))

    c3_components = components(c3_events)
    c4_components = components(c4_events)
    component_rows = []
    for component in sorted(c3_components | c4_components):
        in_c3 = component in c3_components
        in_c4 = component in c4_components
        component_rows.append({
            "component": component,
            "sharp_word_de": WORD.get(component, component),
            "c3_present": "YES" if in_c3 else "NO",
            "c4_present": "YES" if in_c4 else "NO",
            "status": "SHARED" if in_c3 and in_c4 else "C3_ONLY" if in_c3 else "C4_ONLY",
            "interpretive_use": "common workshop grammar" if in_c3 and in_c4 else "flower-extract/station discriminator" if in_c3 else "tempered-contact/poultice discriminator",
        })
    write("SIX_HUNDRED_TWENTY_FIRST_34_COMPONENT_CONTRAST.tsv", component_rows, list(component_rows[0]))

    c3_cards = {row["card_no"] for row in c3_events}
    c4_cards = {row["card_no"] for row in c4_events}
    card_rows = []
    for card in sorted(c3_cards | c4_cards, key=lambda item: int(item[4:])):
        sample = next(row for row in events if row["card_no"] == card)
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in events if row["card_no"] == card})),
            "semantic_component_parse": sample["semantic_component_parse"],
            "standard_command_de": sample["standard_command_de"],
            "c3_occurrences": sum(row["card_no"] == card for row in c3_events),
            "c4_occurrences": sum(row["card_no"] == card for row in c4_events),
            "status": "SHARED" if card in c3_cards and card in c4_cards else "C3_ONLY" if card in c3_cards else "C4_ONLY",
        })
    write("SIX_HUNDRED_TWENTY_FIRST_90_CARD_CONTRAST.tsv", card_rows, list(card_rows[0]))

    statement_rows = []
    for row in c3_statements + c4_statements:
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "module_sequence": row["module_sequence"],
            "case_role": "FLOWER_EXTRACT_OR_WASH_STATION" if row["case_id"] == "C3" else "TEMPERED_CONTACT_OR_POULTICE_STATION",
        })
    write("SIX_HUNDRED_TWENTY_FIRST_58_STATEMENT_CONTRAST.tsv", statement_rows, list(statement_rows[0]))

    c3_only = sorted(c3_components - c4_components)
    c4_only = sorted(c4_components - c3_components)
    markdown = f"""# C3 gegen C4: Warum die Fälle nicht dasselbe bedeuten

## Gemeinsame Grammatik

Beide Fälle benutzen DOSIEREN, ANSETZEN/BEHANDELN, ADRESSIEREN/WEITERLEITEN,
HALTEN/ABSETZEN, AUFFANGEN, FORTSETZEN und SCHLIESSEN. Diese Gemeinsamkeit ist
die Werkstattgrammatik, nicht der konkrete Inhalt.

## Nur C3

`{' | '.join(f'{component}={WORD.get(component, component)}' for component in c3_only)}`

Diese Folge trägt Auswringen, Bereitschaftsprüfung, Vollgrad, Arbeitsstufe,
Einfüllen, Kühlen und Wiederaufnehmen. Zusammen mit dem Blütenbild passt das
zu einem gewonnenen Auszug, der durch mehrere Wasch-/Eintauchstationen läuft.

## Nur C4

`{' | '.join(f'{component}={WORD.get(component, component)}' for component in c4_only)}`

Diese Folge trägt Nachportion, Durchlasskanal, Befestigen und Verwahren.
Zusammen mit Temperieren, Zielstelle und sichtbarem Figurenpaar passt das zu
einer portionierten Kontakt-/Auflagebehandlung mit lokalem Kanalweg.

## Entscheidung

Kein neues Anwendungswort ist nötig. Die vorhandenen produktiven Kerne tragen
bereits die Differenz; Bild und Fall konkretisieren sie. Ein zusätzliches
Wort BAD oder AUFLAGE würde dieselbe Information doppelt in Karte und Bild
schreiben und das System weniger elegant machen.
"""
    (HERE / "SIX_HUNDRED_TWENTY_FIRST_C3_C4_SIDE_BY_SIDE.md").write_text(markdown, encoding="utf-8")

    report = f"""# Sechshunderteinundzwanzigste Runde: C3 gegen C4

## Ergebnis

C3 hat 38 Aussagen/103 Ereignisse, C4 20 Aussagen/65 Ereignisse. Sie teilen 23 der insgesamt 34 verwendeten Komponenten und alle großen Arbeitsmodule außer der expliziten BEREITSCHAFTSPRÜFUNG, die nur C3 besitzt.

Die exklusiven Kerne entscheiden den Inhalt:

- C3: {', '.join(WORD.get(component, component) for component in c3_only)};
- C4: {', '.join(WORD.get(component, component) for component in c4_only)}.

C3 ist damit im jetzigen Modell ein Blütenauszug-/Waschstationsfall; C4 ein temperierter Portionier-/Kontakt-/Befestigungsfall. Die Differenz liegt nicht nur im Bildbesitzer. Sie ist bereits in elf exklusiven Komponenten und 72 nicht geteilten exakten Karten sichtbar.

## Nächster Schritt

Kein neues Wort wird eingeführt. Als nächstes werden C1 und C2 verglichen: Sie teilen sogar dieselbe abgebildete H1/H2-Pflanze und sind daher der härtere Test, ob die Textkerne einen milden Grundauszug von einem stärkeren Nach-/Spülauszug unterscheiden.
"""
    (HERE / "SIX_HUNDRED_TWENTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "c3_statements": len(c3_statements),
        "c4_statements": len(c4_statements),
        "c3_events": len(c3_events),
        "c4_events": len(c4_events),
        "shared_components": len(c3_components & c4_components),
        "c3_only_components": c3_only,
        "c4_only_components": c4_only,
        "shared_cards": len(c3_cards & c4_cards),
        "c3_only_cards": len(c3_cards - c4_cards),
        "c4_only_cards": len(c4_cards - c3_cards),
        "new_application_core": "NONE",
        "decision": "C3_C4_DISTINGUISHED_BY_EXISTING_COMPONENTS_AND_CASE_LAYER",
    }
    (HERE / "SIX_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
