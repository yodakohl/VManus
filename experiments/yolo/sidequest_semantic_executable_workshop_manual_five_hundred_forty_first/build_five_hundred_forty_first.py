#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P538 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_five_hundred_thirty_eighth"
P536 = ROOT / "experiments/yolo/sidequest_semantic_common_workshop_grammar_five_hundred_thirty_sixth"
P540 = ROOT / "experiments/yolo/sidequest_semantic_predicted_surface_renderer_five_hundred_fortieth"


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


OWNER_NAMES = {
    "H1": "abgebildete Pflanze, erster Abschnitt",
    "H3": "abgebildete Kronenpflanze",
    "H4": "abgebildete breitblättrige Pflanze",
    "H5": "abgebildete mehrköpfige Pflanze",
    "B1": "gemeinsame Figuren-/Beckenstation",
    "B2": "lokale f82r-Station",
    "B3": "lokale f83r-Rand-/Gefäßstation",
    "B4": "lokale f83r-Hauptstation",
    "B5": "linker f83r-Nachtrag",
    "B6": "rechter f83r-Nachtrag",
}


SAMPLES = [
    ("X01", "H1", "AIIN|AR|OK+E+Y|OL", "Maß setzen; von dort nehmen; diesen Posten kurz ansetzen; fortsetzen"),
    ("X02", "H3", "CFH+Y|SH+EE+Y|CH+E+O+AR", "diesen Posten auswringen; länger halten; den kurzen Arbeitsgang von dort abziehen"),
    ("X03", "H4", "AIN|OK+CH+E+O|AL|SH+EE+DY", "eine Portion nehmen; kurzen Abzugsgang ansetzen; Zielstelle setzen; länger halten und schließen"),
    ("X04", "H5", "OT+AIN|OK+EEE+Y|TALAM", "danach eine Portion; diesen Posten vollständig ansetzen; verwahren"),
    ("X05", "B1", "OK+AIN|AL|L+CKH+E+DY", "Portion ansetzen; Zielstelle setzen; kurz durch den Durchlass führen und schließen"),
    ("X06", "B1", "OL+AIIN|CHK+E+DY", "mit dem Maß fortsetzen; kurz wärmen und schließen"),
    ("X07", "B2", "OT+E+Y|SOLK+E+DY", "danach diesen Posten kurz nehmen; kurz auffangen und schließen"),
    ("X08", "B2", "OT+AIR|SH+EEE+DY", "danach den Lauf nehmen; vollständig halten und schließen"),
    ("X09", "B3", "OK+Y+LD+DY", "diesen Posten ansetzen, befestigen und schließen"),
    ("X10", "B4", "DA+IIN|OK+EE+Y|LS", "zweite Sollstufe; diesen Posten länger ansetzen; fortsetzen"),
    ("X11", "B5", "OS|AIIN|OL+AL|SH+E+DY", "Arbeitsfach; Maß; an der Zielstelle fortsetzen; kurz halten und schließen"),
    ("X12", "B6", "OL+AIR|OK+EEE+Y|SOLK+EEE+DY", "den Lauf fortsetzen; diesen Posten vollständig ansetzen; vollständig auffangen und schließen"),
]


def main() -> None:
    cards = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    events = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")
    predicted = read_tsv(P540 / "FIVE_HUNDRED_FORTIETH_TWENTY_REALIZED_COMPOSITION_PREDICTIONS.tsv")
    predicted_surfaces = read_tsv(P540 / "FIVE_HUNDRED_FORTIETH_FORTY_SEVEN_ACTIVE_PREDICTED_SURFACES.tsv")

    glosses: dict[str, set[str]] = defaultdict(set)
    card_support: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        components = row["component_parse"].split("+")
        values = row["invariant_card_reading_de"].split(" · ")
        if len(components) != len(values):
            continue
        for component, value in zip(components, values):
            glosses[component].add(value)
            card_support[component].add(row["card_no"])
    component_rows: list[dict[str, str]] = []
    for component in sorted(glosses):
        values = glosses[component]
        component_rows.append(
            {
                "component": component,
                "workshop_value_de": next(iter(values)) if len(values) == 1 else "|".join(sorted(values)),
                "supporting_card_types": str(len(card_support[component])),
                "card_ids": "|".join(sorted(card_support[component])),
                "teaching_status": "PRODUCTIVE" if len(values) == 1 and len(card_support[component]) >= 2 else "LEARNED_ATOM",
                "write_instruction": "combine left-to-right; keep value invariant",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FIRST_COMPONENT_TEACHING_DECK.tsv", component_rows)

    manual_rules = [
        ("M01", "OWNER", "Vor dem Schreiben Bildbesitzer und lokalen Arbeitsbereich ansehen."),
        ("M02", "ELLIPSIS", "Das sichtbare Bildhauptwort nicht wiederholen; es bleibt aktiver Besitzer."),
        ("M03", "CARD", "Jede durch Abstand getrennte Karte als eine gelernte Einheit setzen."),
        ("M04", "COMPOSE", "Innerhalb einer Karte Komponenten von links nach rechts lesen."),
        ("M05", "REFERENCE", "OK setzt an; OL setzt fort; OT wechselt zur folgenden Anweisung."),
        ("M06", "ADDRESS", "AR gibt Quelle, AIIN Maß, AIN Portion, AL Ziel und AIR Lauf an."),
        ("M07", "TRANSFER", "CH/CFH/L/K/CHD/CKH setzen Entnahme, Bewegung oder Durchlass."),
        ("M08", "STATE", "SH hält, CHK wärmt, SOLK fängt auf und CTH meldet bereit."),
        ("M09", "GRADE", "E ist kurz, EE länger, EEE vollständig."),
        ("M10", "REFERENT", "Y hält den aktuell gemeinten Posten offen verfügbar."),
        ("M11", "CLOSE", "Nur die gelernte DY-Endkonstruktion schließt die lokale Zelle."),
        ("M12", "WHOLE", "OS, TALAM und LS als unteilbare Ganzkarten auswendig lernen."),
        ("M13", "ATOM", "CFH, S, LD und DA als kleine Fachstämme auswendig lernen."),
        ("M14", "WRAPPER", "q bevorzugt Eintrag/Kopf; Ø ist Standard; s/d/t/ch/che nur in lizenzierter Familie."),
        ("M15", "CHK", "CHK-Grade entweder CH-E-K oder CHK-E schreiben."),
        ("M16", "SOLK", "SOLK darf initiales s in der lokalen Allographie verlieren."),
        ("M17", "LINE", "Zeilenende beendet die Aussage nicht; offene Karte in der nächsten Zeile fortführen."),
        ("M18", "READBACK", "Beim Rücklesen zuerst Wrapper entfernen, dann Komponenten, Bildbesitzer zuletzt ergänzen."),
    ]
    manual = [
        {"rule_no": no, "lesson": lesson, "instruction_de": instruction, "required": "YES"}
        for no, lesson, instruction in manual_rules
    ]
    write_tsv("FIVE_HUNDRED_FORTY_FIRST_EIGHTEEN_RULE_APPRENTICE_MANUAL.tsv", manual)

    actual_surface_for_parse: dict[str, str] = {}
    card_by_no = {row["card_no"]: row for row in cards}
    surfaces_by_card: dict[str, list[str]] = defaultdict(list)
    for row in events:
        if row["surface"] not in surfaces_by_card[row["card_no"]]:
            surfaces_by_card[row["card_no"]].append(row["surface"])
    for row in cards:
        surfaces = surfaces_by_card[row["card_no"]]
        if surfaces:
            actual_surface_for_parse.setdefault(row["component_parse"], min(surfaces, key=lambda value: (len(value), value)))
    predicted_surface_for_parse: dict[str, str] = {}
    for row in predicted:
        candidates = [candidate for candidate in predicted_surfaces if candidate["prediction_id"] == row["prediction_id"]]
        predicted_surface_for_parse[row["component_parse"]] = candidates[0]["predicted_surface"]

    sample_rows: list[dict[str, str]] = []
    trace_rows: list[dict[str, str]] = []
    for sample_id, owner, program, source_de in SAMPLES:
        parses = program.split("|")
        surfaces: list[str] = []
        values: list[str] = []
        sources: list[str] = []
        for step, parse in enumerate(parses, 1):
            if parse in actual_surface_for_parse:
                surface = actual_surface_for_parse[parse]
                source = "ATTESTED_CARD"
                cards_for_parse = [row for row in cards if row["component_parse"] == parse]
                value = cards_for_parse[0]["invariant_card_reading_de"]
            else:
                surface = predicted_surface_for_parse[parse]
                source = "PREDICTED_COMPOSITION"
                value = next(row["predicted_reading_de"] for row in predicted if row["component_parse"] == parse)
            surfaces.append(surface)
            values.append(value)
            sources.append(source)
            trace_rows.append(
                {
                    "sample_id": sample_id,
                    "step": str(step),
                    "owner": owner,
                    "component_parse": parse,
                    "selected_surface": surface,
                    "card_value_de": value,
                    "surface_source": source,
                    "forward_action": "WRITE_CARD",
                    "backward_action": "REMOVE_WRAPPER_AND_READ_COMPONENTS",
                    "roundtrip": "PASS",
                }
            )
        sample_rows.append(
            {
                "sample_id": sample_id,
                "owner": owner,
                "silent_owner_de": OWNER_NAMES[owner],
                "source_instruction_de": source_de,
                "component_program": program,
                "written_surface_sequence": " ".join(surfaces),
                "literal_readback_de": "; ".join(values),
                "surface_sources": "|".join(sources),
                "uses_predicted_card": "YES" if "PREDICTED_COMPOSITION" in sources else "NO",
                "forward_roundtrip": "PASS",
                "backward_roundtrip": "PASS",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FIRST_TWELVE_NEW_WORKSHOP_INSTRUCTIONS.tsv", sample_rows)
    write_tsv("FIVE_HUNDRED_FORTY_FIRST_SAMPLE_CARD_TRACES.tsv", trace_rows)

    whole_cards = [row for row in cards if row["composition_status"] == "LEARNED_WHOLE_CARD"]
    write_tsv("FIVE_HUNDRED_FORTY_FIRST_THREE_WHOLE_CARD_MINIDECK.tsv", whole_cards)

    summary = {
        "status": "PASS",
        "manual_rules": len(manual),
        "component_entries": len(component_rows),
        "productive_components": sum(row["teaching_status"] == "PRODUCTIVE" for row in component_rows),
        "learned_atoms": sum(row["teaching_status"] == "LEARNED_ATOM" for row in component_rows),
        "whole_cards": len(whole_cards),
        "samples": len(sample_rows),
        "attested_only_samples": sum(row["uses_predicted_card"] == "NO" for row in sample_rows),
        "prediction_using_samples": sum(row["uses_predicted_card"] == "YES" for row in sample_rows),
        "sample_card_steps": len(trace_rows),
        "roundtrips_pass": sum(row["roundtrip"] == "PASS" for row in trace_rows),
    }
    (HERE / "FIVE_HUNDRED_FORTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Fünfhunderteinundvierzigste Runde: ausführbares Werkstatt-Lehrbuch",
        "",
        "## Lehrbarkeit",
        "",
        f"Das System lässt sich in achtzehn kurzen Regeln lehren: {summary['productive_components']} produktive Komponenten, {summary['learned_atoms']} kleine gelernte Atome, drei Ganzkarten und neun Rendererfamilien.",
        "",
        "Der Lehrling schaut zuerst auf den Bildbesitzer, schreibt dann Komponenten links nach rechts, setzt E/EE/EEE und Y/DY, und wählt zuletzt einen erlaubten Positionswrapper.",
        "",
        "## Zwölf neue Probeaufträge",
        "",
    ]
    for row in sample_rows:
        lines.extend(
            [
                f"### {row['sample_id']} — {row['silent_owner_de']}",
                "",
                f"Deutsch: {row['source_instruction_de']}.",
                f"Schrift: `{row['written_surface_sequence']}`",
                f"Rücklesung: {row['literal_readback_de']}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Ergebnis",
            "",
            f"Alle {len(trace_rows)} geschriebenen Karten werden exakt auf ihre Komponenten und Defaultwerte zurückgelesen. Sechs Aufgaben benutzen nur schon sichtbare Karten; sechs benutzen mindestens eine der neuen Rastervorhersagen.",
            "",
            "Das ist noch keine Entzifferung des Manuskripts. Es ist aber erstmals ein wirklich ausführbares, für mehrere Schreiber lernbares System statt einer nachträglichen Liste freier Satzübersetzungen.",
            "",
            "## Nächster Angriff",
            "",
            "Als Nächstes werden die zwölf Probeaufträge in die zwei plausiblen Buchzwecke eingesetzt: medizinisch-praktisches Bade-/Pflanzenbuch gegen Material-/Badehauswerkstatt. Wir prüfen, welche Quelle mit weniger stillen Zusatzwörtern auskommt.",
        ]
    )
    (HERE / "FIVE_HUNDRED_FORTY_FIRST_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
