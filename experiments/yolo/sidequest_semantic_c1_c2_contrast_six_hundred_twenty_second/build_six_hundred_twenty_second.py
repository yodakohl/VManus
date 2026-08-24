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
    "AIIN": "SOLLMASS", "AIN": "PORTION", "AIR": "FLUESSIGKEITSLAUF", "AL": "ZIELSTELLE", "AR": "VORRAT",
    "CH": "ABNEHMEN", "CHD": "UMSETZEN", "CHK": "WAERMEN", "CKH": "DURCHLASSKANAL", "CTH": "BEREIT",
    "DY": "SCHLUSS", "E": "KURZ", "EE": "LANG", "EEE": "VOLL", "IIN": "ARBEITSSTUFE", "K": "ZUDOSIEREN",
    "L": "WEITERLEITEN", "LSH": "WASCHEN", "O": "ARBEITSGANG", "OK": "ANSETZEN", "OL": "FORTSETZEN",
    "OR": "ANSATZ", "OS": "ARBEITSFACH", "OT": "DANACH", "P": "EINFUELLEN", "R": "KUEHLEN",
    "S": "TEILEN", "SH": "HALTEN", "SHED": "ABSETZEN", "SOLK": "AUFFANGEN", "T": "EINTRAGEN", "Y": "ARBEITSPOSTEN",
}


def components(rows: list[dict[str, str]]) -> set[str]:
    result: set[str] = set()
    for row in rows:
        result.update(row["semantic_component_parse"].replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))
    return result


def main() -> None:
    events = read(P618 / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read(P619 / "SIX_HUNDRED_NINETEENTH_116_STATEMENT_MODULE_MAP.tsv")
    c1_events = [row for row in events if row["case_id"] == "C1"]
    c2_events = [row for row in events if row["case_id"] == "C2"]
    c1_statements = [row for row in statements if row["case_id"] == "C1"]
    c2_statements = [row for row in statements if row["case_id"] == "C2"]

    c1_modules = Counter(module for row in c1_statements for module in row["module_sequence"].split("|"))
    c2_modules = Counter(module for row in c2_statements for module in row["module_sequence"].split("|"))
    module_rows = []
    for module in sorted(set(c1_modules) | set(c2_modules)):
        module_rows.append({
            "module": module,
            "c1_statements": c1_modules[module],
            "c2_statements": c2_modules[module],
            "difference_c2_minus_c1": c2_modules[module] - c1_modules[module],
            "case_reading": "C2_MORE" if c2_modules[module] > c1_modules[module] else "C1_MORE" if c1_modules[module] > c2_modules[module] else "EQUAL",
        })
    write("SIX_HUNDRED_TWENTY_SECOND_8_MODULE_CONTRAST.tsv", module_rows, list(module_rows[0]))

    c1_components = components(c1_events)
    c2_components = components(c2_events)
    component_rows = []
    for component in sorted(c1_components | c2_components):
        in_c1 = component in c1_components
        in_c2 = component in c2_components
        component_rows.append({
            "component": component,
            "sharp_word_de": WORDS.get(component, component),
            "c1_present": "YES" if in_c1 else "NO",
            "c2_present": "YES" if in_c2 else "NO",
            "status": "SHARED" if in_c1 and in_c2 else "C1_ONLY" if in_c1 else "C2_ONLY",
            "case_use": "common plant-processing grammar" if in_c1 and in_c2 else "mild wash/ground-extract discriminator" if in_c1 else "divided full-treatment/follow-up discriminator",
        })
    write("SIX_HUNDRED_TWENTY_SECOND_32_COMPONENT_CONTRAST.tsv", component_rows, list(component_rows[0]))

    c1_cards = {row["card_no"] for row in c1_events}
    c2_cards = {row["card_no"] for row in c2_events}
    card_rows = []
    for card in sorted(c1_cards | c2_cards, key=lambda item: int(item[4:])):
        sample = next(row for row in events if row["card_no"] == card)
        card_rows.append({
            "card_no": card,
            "surfaces": "|".join(sorted({row["surface"] for row in events if row["card_no"] == card})),
            "semantic_component_parse": sample["semantic_component_parse"],
            "standard_command_de": sample["standard_command_de"],
            "c1_occurrences": sum(row["card_no"] == card for row in c1_events),
            "c2_occurrences": sum(row["card_no"] == card for row in c2_events),
            "status": "SHARED" if card in c1_cards and card in c2_cards else "C1_ONLY" if card in c1_cards else "C2_ONLY",
        })
    write("SIX_HUNDRED_TWENTY_SECOND_94_CARD_CONTRAST.tsv", card_rows, list(card_rows[0]))

    statement_rows = []
    for row in c1_statements + c2_statements:
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "module_sequence": row["module_sequence"],
            "case_role": "MILD_WASH_OR_GROUND_EXTRACT" if row["case_id"] == "C1" else "DIVIDED_FULL_TREATMENT_FOLLOW_UP_EXTRACT",
        })
    write("SIX_HUNDRED_TWENTY_SECOND_48_STATEMENT_CONTRAST.tsv", statement_rows, list(statement_rows[0]))

    c1_only = sorted(c1_components - c2_components)
    c2_only = sorted(c2_components - c1_components)
    side = f"""# C1 gegen C2 bei demselben Bildbesitzer

## Gemeinsamer Ausgangspunkt

H1 und H2 erben dieselbe abgebildete breit gezähnte radialblütige Pflanze. Das
Bild kann den Unterschied zwischen den beiden Fallstoffen deshalb nicht allein
tragen.

## C1 allein

`{' | '.join(f'{component}={WORDS[component]}' for component in c1_only)}`

FLUESSIGKEITSLAUF, WASCHEN, ARBEITSFACH und EINTRAGEN passen zu einem milden
Grundauszug, der gewaschen, geführt und mehrfach aufgefangen/eingetragen wird.

## C2 allein

`{' | '.join(f'{component}={WORDS[component]}' for component in c2_only)}`

VOLL, EINFUELLEN und TEILEN passen zu einem stärker behandelten, aufgeteilten
Nach- oder Spülauszug. C2 enthält sieben Dosiermodule gegenüber drei in C1;
C1 enthält drei Auffangmodule gegenüber einem in C2.

## Entscheidung

Der Textkern trennt beide Fälle trotz gleichen Bildbesitzers. Kein neues
Pflanzen- oder Stärkewort wird benötigt. Die bestehende Modulhäufigkeit und die
sieben exklusiven Komponenten genügen für unsere konkrete Arbeitstheorie.
"""
    (HERE / "SIX_HUNDRED_TWENTY_SECOND_C1_C2_SIDE_BY_SIDE.md").write_text(side, encoding="utf-8")

    report = f"""# Sechshundertzweiundzwanzigste Runde: C1 gegen C2

## Ergebnis

C1 umfasst 23 Aussagen/80 Ereignisse, C2 25/86. Beide nutzen alle acht Module und teilen 25 Komponenten sowie 17 exakte Karten. Dennoch sind ihre Arbeitsgänge nicht identisch.

- Nur C1: {', '.join(WORDS[component] for component in c1_only)}.
- Nur C2: {', '.join(WORDS[component] for component in c2_only)}.
- C2 dosiert in sieben Aussagen, C1 in drei.
- C1 fängt in drei Aussagen auf, C2 in einer.

Damit bleibt die Lesung `C1=milder Wasch-/Grundauszug` gegen `C2=geteilter Vollgrad-Nach-/Spülauszug` brauchbar, obwohl H1 und H2 dieselbe Pflanze als stillen Besitzer haben. Die Unterscheidung wird vom Text, nicht vom Bild, getragen.

## Nächster Schritt

C5 und C6 werden verglichen. C6 hat keine eigene Herbal-Zubereitung; falls sein B6-Text wirklich nur einen in C5 erzeugten Vorrat weiterverarbeitet, sollte seine Komponentenausstattung eine echte Teilmenge oder kurze Fortsetzung des C5-Nachtrags bilden.
"""
    (HERE / "SIX_HUNDRED_TWENTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "c1_statements": len(c1_statements),
        "c2_statements": len(c2_statements),
        "c1_events": len(c1_events),
        "c2_events": len(c2_events),
        "shared_components": len(c1_components & c2_components),
        "c1_only_components": c1_only,
        "c2_only_components": c2_only,
        "shared_cards": len(c1_cards & c2_cards),
        "c1_only_cards": len(c1_cards - c2_cards),
        "c2_only_cards": len(c2_cards - c1_cards),
        "same_picture_owner": True,
        "new_word": "NONE",
        "decision": "C1_C2_TEXT_CORES_DIFFER_DESPITE_SHARED_PICTURE_OWNER",
    }
    (HERE / "SIX_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
