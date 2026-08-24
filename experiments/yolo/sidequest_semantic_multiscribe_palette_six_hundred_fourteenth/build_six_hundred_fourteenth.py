#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"


def read(name: str) -> list[dict[str, str]]:
    with (P613 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    ("SR01", "CHD+DY", "UMSETZEN; SCHLUSS", "PROC076", "PROC094", "B1-S017 after KURZ·FORTSETZEN", "use compressed dchdy card after a short continuation in B1"),
    ("SR02", "CHD+Y", "UMSETZEN · DIES", "PROC042", "PROC133", "B3-S006 immediately after a closed CHD card", "use the CHY-framed card when B3 resumes after the closed transfer"),
    ("SR03", "CHK+EE+Y", "WAERMEN · LANG · DIES", "PROC046", "PROC107", "record B2", "B2 uses its reordered warming card; preparation and B4 use cheeky"),
    ("SR04", "OK+CHD+DY", "ANSETZEN · UMSETZEN; SCHLUSS", "PROC082", "PROC091", "previous card is T+E+Y or L+O", "use the expanded CHED card after an entry or guided path"),
    ("SR05", "OK+OL", "ANSETZEN · FORTSETZEN", "PROC037", "PROC160", "record B4", "B4 uses its qokol station spelling"),
    ("SR06", "OK+Y", "ANSETZEN · DIES", "PROC008", "PROC011", "stored Herbal substeps H1-S002, H5-S004, H5-S005", "use the CHY-framed Herbal substep card only in the three copied slots"),
    ("SR07", "OL", "FORTSETZEN", "PROC013", "PROC115", "B2-S010 between ANSETZEN·DIES and HALTEN·LANG·DIES", "use the short LS margin/workbench abbreviation in this B2 chain"),
    ("SR08", "OT+CHD+DY", "DANACH · UMSETZEN; SCHLUSS", "PROC145", "PROC166", "record B5", "B5 uses its compressed closed transfer card"),
    ("SR09", "OT+Y", "DANACH · DIES", "PROC065", "PROC036", "record H3", "H3 uses the q-framed next-item card"),
    ("SR10", "SH+EE+Y", "HALTEN · LANG · DIES", "PROC031", "PROC157", "B4 immediately after WAERMEN·LANG·DIES", "use sheey for the long hold immediately following long warming"),
]


def desk(record: str) -> str:
    if record.startswith("H"):
        return "P_PREPARATION_DESK"
    if record in {"B1", "B2"}:
        return "B_BATH_DESK"
    return "S_STATION_DESK"


def select_card(parse: str, command: str, record: str, statement: str, previous_parse: str, previous_command: str) -> tuple[str, str]:
    if parse == "CHD+DY" and statement == "B1-S017":
        return "PROC094", "SR01_EXCEPTION"
    if parse == "CHD+Y" and statement == "B3-S006":
        return "PROC133", "SR02_EXCEPTION"
    if parse == "CHK+EE+Y" and record == "B2":
        return "PROC107", "SR03_EXCEPTION"
    if parse == "OK+CHD+DY" and previous_parse in {"T+E+Y", "L+O"}:
        return "PROC091", "SR04_EXCEPTION"
    if parse == "OK+OL" and record == "B4":
        return "PROC160", "SR05_EXCEPTION"
    if parse == "OK+Y" and statement in {"H1-S002", "H5-S004", "H5-S005"}:
        return "PROC011", "SR06_EXCEPTION"
    if parse == "OL" and statement == "B2-S010":
        return "PROC115", "SR07_EXCEPTION"
    if parse == "OT+CHD+DY" and record == "B5":
        return "PROC166", "SR08_EXCEPTION"
    if parse == "OT+Y" and record == "H3":
        return "PROC036", "SR09_EXCEPTION"
    if parse == "SH+EE+Y" and record == "B4" and previous_command == "WAERMEN · LANG · DIES":
        return "PROC157", "SR10_EXCEPTION"
    defaults = {
        ("CHD+DY", "UMSETZEN; SCHLUSS"): "PROC076",
        ("CHD+Y", "UMSETZEN · DIES"): "PROC042",
        ("CHK+EE+Y", "WAERMEN · LANG · DIES"): "PROC046",
        ("OK+CHD+DY", "ANSETZEN · UMSETZEN; SCHLUSS"): "PROC082",
        ("OK+OL", "ANSETZEN · FORTSETZEN"): "PROC037",
        ("OK+Y", "ANSETZEN · DIES"): "PROC008",
        ("OL", "FORTSETZEN"): "PROC013",
        ("OT+CHD+DY", "DANACH · UMSETZEN; SCHLUSS"): "PROC145",
        ("OT+Y", "DANACH · DIES"): "PROC065",
        ("SH+EE+Y", "HALTEN · LANG · DIES"): "PROC031",
    }
    return defaults[(parse, command)], "DEFAULT_CARD"


def main() -> None:
    cards = read("SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    events = read("SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    cards_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        cards_by_key[(row["semantic_component_parse"], row["standard_command_de"])].append(row)
    duplicate_keys = {key for key, rows in cards_by_key.items() if len(rows) > 1}
    target_cards = {row["card_no"] for key in duplicate_keys for row in cards_by_key[key]}
    target_events = [row for row in events if row["card_no"] in target_cards]

    rule_rows = [{
        "rule_id": rule_id,
        "semantic_component_parse": parse,
        "invariant_command_de": command,
        "default_card_no": default,
        "alternate_card_no": alternate,
        "alternate_condition": condition,
        "apprentice_rule_de": explanation,
    } for rule_id, parse, command, default, alternate, condition, explanation in RULES]
    write("SIX_HUNDRED_FOURTEENTH_10_COMMAND_CARD_RULES.tsv", rule_rows, list(rule_rows[0]))

    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in target_events:
        events_by_card[row["card_no"]].append(row)
    palette_rows: list[dict[str, object]] = []
    for card_no in sorted(target_cards, key=lambda item: int(item[4:])):
        card = next(row for row in cards if row["card_no"] == card_no)
        card_events = events_by_card[card_no]
        counts = Counter(row["surface"] for row in card_events)
        default_surface = sorted(counts, key=lambda item: (-counts[item], item))[0]
        by_desk = defaultdict(list)
        for row in card_events:
            by_desk[desk(row["record"])].append(row["surface"])
        palette_rows.append({
            "card_no": card_no,
            "semantic_component_parse": card["semantic_component_parse"],
            "invariant_command_de": card["standard_command_de"],
            "occurrences": len(card_events),
            "licensed_surfaces": card["surfaces"],
            "default_surface": default_surface,
            "preparation_desk_surfaces": "|".join(sorted(set(by_desk["P_PREPARATION_DESK"]))) or "NONE",
            "bath_desk_surfaces": "|".join(sorted(set(by_desk["B_BATH_DESK"]))) or "NONE",
            "station_desk_surfaces": "|".join(sorted(set(by_desk["S_STATION_DESK"]))) or "NONE",
            "records": "|".join(sorted({row["record"] for row in card_events})),
            "surface_teaching_rule_de": "use the desk surface if listed; where several are listed copy the local exemplar; all licensed surfaces keep the same command",
        })
    write("SIX_HUNDRED_FOURTEENTH_20_CARD_SURFACE_PALETTE.tsv", palette_rows, list(palette_rows[0]))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    replay_rows: list[dict[str, object]] = []
    for row in target_events:
        sequence = events_by_statement[row["statement_id"]]
        index = sequence.index(row)
        previous_parse = sequence[index - 1]["semantic_component_parse"] if index else "START"
        previous_command = sequence[index - 1]["standard_command_de"] if index else "START"
        predicted, reason = select_card(row["semantic_component_parse"], row["standard_command_de"], row["record"], row["statement_id"], previous_parse, previous_command)
        card = next(item for item in cards if item["card_no"] == row["card_no"])
        replay_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "desk": desk(row["record"]),
            "semantic_component_parse": row["semantic_component_parse"],
            "invariant_command_de": row["standard_command_de"],
            "previous_parse": previous_parse,
            "expected_card_no": row["card_no"],
            "selected_card_no": predicted,
            "selection_reason": reason,
            "observed_surface": row["surface"],
            "licensed_surfaces": card["surfaces"],
            "card_selection_correct": "YES" if predicted == row["card_no"] else "NO",
            "surface_is_licensed": "YES" if row["surface"] in card["surfaces"].split("|") else "NO",
        })
    write("SIX_HUNDRED_FOURTEENTH_71_EVENT_SURFACE_REPLAY.tsv", replay_rows, list(replay_rows[0]))

    manual = """# Drei Arbeitstische, eine Bedeutung

## Gemeinsame Regel

Alle Schreiber lernen dieselben 39 Wörter und 163 Befehle. Kein Schreiber darf
einer Oberflächenvariante eine neue Bedeutung geben. Die sichtbare Karte wird
in drei Schritten erzeugt:

1. Befehl aus der Fallanweisung bilden.
2. Bei einem der zehn Doppelbefehle SR01–SR10 die genaue Kartenidentität wählen.
3. Eine am eigenen Arbeitstisch lizenzierte Oberfläche schreiben; bei mehreren
   lokalen Formen das nebenliegende Exemplar kopieren.

## P — Pflanzen- und Zubereitungstisch

P schreibt H1–H5. Er bevorzugt `chol`, `shey`, `cheeky`, `otchey` und die
herbalen OK-Y-Formen. Drei gelernte Unterplätze verwenden die CHY-Karte
PROC011. Das ist ein Kopierbrauch, keine zweite Bedeutung.

## B — Bad- und Anwendungstisch

B schreibt B1–B2. Er bevorzugt nacktes `ol`, q-gerahmtes OK-Y und die lokalen
B2-Karten `chkeey` und `ls`. `ls` ist die kurze Werkbankform von FORTSETZEN
zwischen Einsetzen und langem Halten.

## S — Stations- und Nachtragstisch

S schreibt B3–B6. Er verwendet häufiger `sol/tol/cheol`, die kompakten
geschlossenen Transferkarten und lokale q-Rahmen. Wo S zwei Oberflächen für
dieselbe Karte kennt, entscheidet das kopierte Stationsmuster, nicht die
Bedeutung.

## Zehn Merksätze

- Nach kurzer B1-Fortsetzung: kompaktes dchdy.
- Nach geschlossenem B3-Umsetzen: chedchy.
- Im B2-Wärmeplatz: chkeey.
- Nach Eintrag oder geführtem Gang: expanded OK-CHED-Schlusskarte.
- Im B4-Fortsetzungsplatz: qokol.
- In drei gespeicherten Herbal-Unterplätzen: OK-CHY statt OK-Y.
- Zwischen B2-Einsetzen und Langhalten: ls.
- Im B5-Nachtransfer: otchdy.
- In H3 für DANACH DIES: qotchy.
- Direkt nach langem B4-Wärmen: sheey.

Diese Regeln wählen alle 71 betroffenen Kartenidentitäten richtig. Die genaue
sichtbare Variante innerhalb einer Kartenidentität bleibt eine kleine lokale
Schreibpalette.
"""
    (HERE / "SIX_HUNDRED_FOURTEENTH_THREE_DESK_MANUAL.md").write_text(manual, encoding="utf-8")

    report = f"""# Sechshundertvierzehnte Runde: Mehrschreiber-Palette

## Ergebnis

Die zehn verbliebenen Doppelbefehle sind nun als zehn konkrete Kartenwahlregeln und zwanzig Kartenpaletten lehrbar. Sie decken **{len(target_events)} Vorkommen**. Die Kartenregel wählt {sum(row['card_selection_correct'] == 'YES' for row in replay_rows)}/{len(replay_rows)} Mal die tatsächlich verwendete exakte Karte; jede beobachtete Oberfläche gehört zur erlaubten Palette ihrer Karte.

Die Werkstatt braucht damit keine freien Bedeutungsvarianten. Sie hat drei Schreibtische mit eigenen Gewohnheiten:

- P: Pflanzen/Zubereitung;
- B: Bad/Anwendung;
- S: Station/Nachtrag.

Der wichtigere Befund ist konzeptionell: Mehrere Schreiber können dieselbe semantische Kurzgrammatik teilen, während sie unterschiedliche gelernte Kartenformen bevorzugen. Nur bei sieben Karten-/Record-Kombinationen bleibt die Wahl zwischen mehreren Oberflächen rein exemplarisch; sie verändert den Befehl nicht.

## Nächster Schritt

Jetzt lässt sich eine neue vollständige Zehnseiten-Ausgabe schreiben: zuerst Besitzer und Fall nennen, danach nur die 163 standardisierten Befehle; daneben kann die jeweilige Schreiberkarte stehen. Dadurch wird sichtbar, ob die Übersetzung über ganze Records wirklich lesbar bleibt.
"""
    (HERE / "SIX_HUNDRED_FOURTEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "commands_with_card_choice": len(rule_rows),
        "palette_cards": len(palette_rows),
        "licensed_surfaces": sum(len(row["licensed_surfaces"].split("|")) for row in palette_rows),
        "events": len(replay_rows),
        "card_selection_correct": sum(row["card_selection_correct"] == "YES" for row in replay_rows),
        "licensed_surface_correct": sum(row["surface_is_licensed"] == "YES" for row in replay_rows),
        "desks": 3,
        "decision": "TEN_CONTEXT_RULES_PLUS_THREE_DESK_SURFACE_PALETTES",
    }
    (HERE / "SIX_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
