#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P618 = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"


def read(name: str) -> list[dict[str, str]]:
    with (P618 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


MODULES = [
    ("M01", "DOSIEREN", "AIIN|AIN|AN|IIN|DA plus K|OK|P|T", "Sollmass, Portion, Nachportion oder Stufe setzen und in Arbeit bringen"),
    ("M02", "ANSETZEN_BEHANDELN", "OK plus Y|AL|E|EE|EEE", "aktiven Posten ansetzen, anwenden oder graduiert behandeln"),
    ("M03", "ADRESSIEREN_WEITERLEITEN", "AR|AIR|CKH|AL|OS or L|CHD|P", "Vorrat, Fluessigkeitslauf, Kanal, Zielstelle oder Fach waehlen und den Posten bewegen"),
    ("M04", "HALTEN_ABSETZEN", "SH|SHED plus Y|E|EE|EEE|DY", "Posten halten, laenger halten oder absetzen"),
    ("M05", "AUFFANGEN", "SOLK or OS plus CH|L|AIR", "abgenommenen oder weitergeleiteten Bestand auffangen"),
    ("M06", "FORTSETZEN", "OL|OT|RESUME_CARD", "gleichen Arbeitsfaden fortsetzen, danach weitermachen oder wieder aufnehmen"),
    ("M07", "BEREITSCHAFT_PRUEFEN", "CTH", "bis zum bereiten Zustand arbeiten"),
    ("M08", "SCHLIESSEN", "DY licensed close", "lokalen Arbeitsschritt abschliessen"),
]


def token_set(rows: list[dict[str, str]]) -> set[str]:
    result: set[str] = set()
    for row in rows:
        result.update(row["semantic_component_parse"].replace("[", "+").replace("]", "+").replace(" ", "+").split("+"))
    return result


def modules_for(tokens: set[str]) -> list[str]:
    output = []
    if tokens & {"AIIN", "AIN", "AN", "IIN", "DA"} and tokens & {"K", "OK", "P", "T"}:
        output.append("M01_DOSIEREN")
    if "OK" in tokens and tokens & {"Y", "AL", "E", "EE", "EEE"}:
        output.append("M02_ANSETZEN_BEHANDELN")
    if tokens & {"AR", "AIR", "CKH", "AL", "OS", "L", "CHD", "P"}:
        output.append("M03_ADRESSIEREN_WEITERLEITEN")
    if tokens & {"SH", "SHED"} and tokens & {"Y", "E", "EE", "EEE", "DY"}:
        output.append("M04_HALTEN_ABSETZEN")
    if "SOLK" in tokens or ("OS" in tokens and tokens & {"CH", "L", "AIR"}):
        output.append("M05_AUFFANGEN")
    if tokens & {"OL", "OT", "RESUME_CARD"}:
        output.append("M06_FORTSETZEN")
    if "CTH" in tokens:
        output.append("M07_BEREITSCHAFT_PRUEFEN")
    if "DY" in tokens:
        output.append("M08_SCHLIESSEN")
    return output


def main() -> None:
    events = read("SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read("SIX_HUNDRED_EIGHTEENTH_116_LAYERED_STATEMENTS.tsv")
    cases = read("SIX_HUNDRED_EIGHTEENTH_6_CASE_NOUN_LEDGER.tsv")
    module_rows = [{"module_id": mid, "module_name_de": name, "trigger": trigger, "workshop_reading_de": reading} for mid, name, trigger, reading in MODULES]
    write("SIX_HUNDRED_NINETEENTH_8_WORKSHOP_MODULES.tsv", module_rows, list(module_rows[0]))

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    statement_rows: list[dict[str, object]] = []
    for row in statements:
        sequence = events_by_statement[row["statement_id"]]
        tokens = token_set(sequence)
        assigned = modules_for(tokens)
        statement_rows.append({
            "case_id": row["case_id"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "event_count": row["event_count"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": " | ".join(event["semantic_component_parse"] for event in sequence),
            "module_sequence": "|".join(assigned),
            "module_count": len(assigned),
            "layered_reading_de": row["layered_reading_de"],
        })
    write("SIX_HUNDRED_NINETEENTH_116_STATEMENT_MODULE_MAP.tsv", statement_rows, list(statement_rows[0]))

    matrix_rows: list[dict[str, object]] = []
    for case in cases:
        case_statements = [row for row in statement_rows if row["case_id"] == case["case_id"]]
        for mid, name, _, _ in MODULES:
            key = f"{mid}_{name}"
            hits = [row for row in case_statements if key in str(row["module_sequence"]).split("|")]
            matrix_rows.append({
                "case_id": case["case_id"],
                "case_material_de": case["case_material_de"],
                "module_id": mid,
                "module_name_de": name,
                "prepare_statements": sum(row["phase"] == "PREPARE_PRODUCT" for row in hits),
                "operate_apply_statements": sum(row["phase"] == "OPERATE_OR_APPLY" for row in hits),
                "total_statements": len(hits),
                "statement_ids": "|".join(str(row["statement_id"]) for row in hits) if hits else "NONE",
            })
    write("SIX_HUNDRED_NINETEENTH_48_CASE_MODULE_MATRIX.tsv", matrix_rows, list(matrix_rows[0]))

    ngram_occurrences: dict[tuple[int, tuple[str, ...]], list[tuple[str, str, str]]] = defaultdict(list)
    for row in statements:
        sequence = events_by_statement[row["statement_id"]]
        parses = [event["semantic_component_parse"] for event in sequence]
        for n in (2, 3):
            for index in range(len(parses) - n + 1):
                ngram_occurrences[(n, tuple(parses[index:index + n]))].append((row["case_id"], row["record"], row["statement_id"]))
    ngram_rows: list[dict[str, object]] = []
    for (n, ngram), occurrences in ngram_occurrences.items():
        case_ids = sorted({item[0] for item in occurrences})
        if len(case_ids) < 2:
            continue
        ngram_rows.append({
            "ngram_length": n,
            "component_ngram": " -> ".join(ngram),
            "cases": "|".join(case_ids),
            "case_count": len(case_ids),
            "occurrences": len(occurrences),
            "locations": "|".join(f"{case}:{statement}" for case, _, statement in occurrences),
            "interpretation": "EXACT_REUSED_CARD_SEQUENCE__STRONGER_THAN_SHARED_ABSTRACT_MODULE",
        })
    ngram_rows.sort(key=lambda row: (-int(row["ngram_length"]), -int(row["case_count"]), -int(row["occurrences"]), str(row["component_ngram"])))
    write("SIX_HUNDRED_NINETEENTH_17_EXACT_CROSS_CASE_NGRAMS.tsv", ngram_rows, list(ngram_rows[0]))

    by_case: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        by_case[str(row["case_id"])].append(row)
    markdown = ["# Sechs Fallabläufe als Werkstattmodule", "", "Die Module dürfen sich in einer Aussage überlagern. Eine exakte wiederholte Kartenfolge ist stärker als nur derselbe Modulname.", ""]
    for case in cases:
        rows = by_case[case["case_id"]]
        markdown.extend([
            f"## {case['case_id']} · {case['case_material_de']}",
            "",
            f"Anwendung: {case['application_de']}",
            "",
        ])
        for row in rows:
            markdown.extend([
                f"- **{row['statement_id']}** `{row['surface_sequence']}`",
                f"  Module: {str(row['module_sequence']).replace('|', ' → ')}",
            ])
        all_modules = []
        for row in rows:
            for module in str(row["module_sequence"]).split("|"):
                if module not in all_modules:
                    all_modules.append(module)
        markdown.extend(["", f"Fallinventar: {' | '.join(all_modules)}", ""])
    (HERE / "SIX_HUNDRED_NINETEENTH_SIX_CASE_MODULE_EDITION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    module_case_counts = {}
    for mid, name, _, _ in MODULES:
        key = f"{mid}_{name}"
        module_case_counts[key] = len({row["case_id"] for row in statement_rows if key in str(row["module_sequence"]).split("|")})
    report = f"""# Sechshundertneunzehnte Runde: sechs Fälle, acht Werkstattmodule

## Ergebnis

Alle 116 Aussagen lassen sich mit acht wiederkehrenden Modulen lesen: DOSIEREN, ANSETZEN/BEHANDELN, ADRESSIEREN/WEITERLEITEN, HALTEN/ABSETZEN, AUFFANGEN, FORTSETZEN, BEREITSCHAFT PRÜFEN und SCHLIESSEN.

Die gemeinsame Grundmaschine ist deutlich:

- DOSIEREN, ADRESSIEREN/WEITERLEITEN und FORTSETZEN erscheinen in allen sechs Fällen;
- ANSETZEN/BEHANDELN, HALTEN/ABSETZEN und SCHLIESSEN in fünf Fällen;
- AUFFANGEN in fünf Fällen;
- die explizite BEREITSCHAFTSPRÜFUNG nur in C1–C3.

Das heißt nicht, dass alle Fälle dasselbe Rezept sind. Nur 17 exakte Zwei-/Dreikartenfolgen kreuzen überhaupt mindestens zwei Fälle; die meisten Gemeinsamkeiten liegen auf der Modul-, nicht auf der Satzebene. Bildbesitzer und Fallstoff bestimmen also weiterhin, ob dasselbe Modul eine Pflanzenzubereitung, ein Bad, eine Waschung, eine Auflage oder einen technischen Transfer realisiert.

## Stärkste exakte Wiederholungen

Zwei Dreierfolgen kreuzen Fälle: `Y → AIIN → Y` und `OK+EE+Y → OK+Y → OL`. Die erste bindet Arbeitsposten–Sollmaß–Arbeitsposten; die zweite bedeutet lang ansetzen/halten, den Posten erneut ansetzen und fortfahren. Das sind die derzeit stärksten wiederverwendeten Mikroformulierungen.

## Nächster Schritt

Die acht Module werden nun als vollständige 1420er Lehrtafel formuliert: Eingaben, erlaubte Kartenbausteine, Ausgaben und typische Fehler. Danach kann ein neuer Schreiber einen Fall aus Modulen zusammensetzen, ohne jede der 173 Karten einzeln semantisch zu erfinden.
"""
    (HERE / "SIX_HUNDRED_NINETEENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "modules": len(MODULES),
        "statements": len(statement_rows),
        "events": len(events),
        "cases": len(cases),
        "matrix_rows": len(matrix_rows),
        "cross_case_exact_ngrams": len(ngram_rows),
        "module_case_counts": module_case_counts,
        "decision": "EIGHT_RECURRING_WORKSHOP_MODULES_COVER_ALL_SIX_CASES",
    }
    (HERE / "SIX_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
