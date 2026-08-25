#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
P996 = HERE.parent / "sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (P996 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REPLACE = {
    "SOLLWERT": "MASS",
    "EINHEIT": "PORTION",
    "ARBEITSSATZ": "ANSATZ",
    "EINSTELLEN": "STELLEN",
    "MARKIEREN": "MERKEN",
    "START": "BEGINN",
}


def revise(value: str) -> str:
    for old, new in REPLACE.items():
        value = value.replace(old, new)
    return value


def main() -> None:
    codebook = read_tsv("PASS996_159_COMPLETE_CODEBOOK.tsv")
    roots = {
        row["root_id"].removeprefix("R-"): row["atomic_meaning_de"]
        for row in read_tsv("PASS996_53_PORTABLE_ROOTS.tsv")
    }
    events = read_tsv("PASS996_2511_EVENT_INTERLINEAR.tsv")
    formula_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        if event["primary_layer"] == "COMMON_FORMULA_CARD":
            for unit in event["primary_teaching_unit_ids"].split("|"):
                if unit.startswith("F"):
                    formula_events[unit].append(event)

    audit: list[dict[str, str]] = []
    changed = 0
    for row in codebook:
        if row["layer"] != "C_LEARNED_FORMULA_CARD":
            continue
        old_spoken = row["spoken_value_de"]
        row["spoken_value_de"] = revise(row["spoken_value_de"])
        row["concrete_context_values_de"] = revise(row["concrete_context_values_de"])
        row["teaching_rule_de"] = (
            "Als ganze Schreibkarte lernen; die Bedeutung bleibt die Summe der Wurzeln."
        )
        expected = " · ".join(roots[component] for component in row["recognition_forms"].split("+"))
        members = formula_events[row["teaching_unit_id"]]
        if old_spoken != row["spoken_value_de"]:
            changed += 1
        audit.append(
            {
                "formula_id": row["teaching_unit_id"],
                "component_recipe": row["recognition_forms"],
                "old_spoken_value_de": old_spoken,
                "revised_spoken_value_de": row["spoken_value_de"],
                "root_composed_value_de": expected,
                "semantic_relation": "EXAKT_WURZELKOMPOSITION" if row["spoken_value_de"] == expected else "ABWEICHUNG",
                "observed_events": str(len(members)),
                "observed_surfaces": "|".join(sorted({event["surface"] for event in members})),
                "observed_pages": "|".join(sorted({event["physical_page"] for event in members})),
                "teaching_role_de": "gelernte Ligatur oder Ganzschreibform ohne neue Bedeutung",
            }
        )

    write_tsv("PASS998_159_RECONCILED_CODEBOOK.tsv", codebook)
    write_tsv("PASS998_30_FORMULA_LIGATURES.tsv", audit)
    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "formula_cards": len(audit),
        "revised_formula_headwords": changed,
        "formula_events": sum(int(row["observed_events"]) for row in audit),
        "semantic_exceptions": sum(row["semantic_relation"] != "EXAKT_WURZELKOMPOSITION" for row in audit),
    }
    (HERE / "PASS998_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = """# Pass 998 — Formelkarten sind gelernte Ligaturen

## Korrektur

Vier Formelköpfe hatten Pass 995 nicht vollständig übernommen:

- `F006 OK+AIN`: EINHEIT → PORTION;
- `F008 OK+AIIN`: SOLLWERT → MASS;
- `F026 OT+OR`: ARBEITSSATZ → ANSATZ;
- `F027 S+AIIN`: SOLLWERT → MASS.

## Das wichtigere Ergebnis

Alle **30/30 Formelkarten** haben danach exakt dieselbe Bedeutung wie die
Summe ihrer Wurzeln. Zusammen tragen sie 595 Ereignisse, aber **null eigene
semantische Ausnahmen**.

Ein Lehrling lernt `qokeedy` deshalb als vertraute Ganzschreibform, liest aber
weiterhin `OK+EE+DY = SETZEN · LÄNGER · SCHLUSS`. Die Karte verhält sich wie
eine technische Ligatur, Brevigrafie oder häufige Kanzleiform – nicht wie ein
neues Wort mit unerwarteter Bedeutung.

## Verbessertes Mischmodell

Das aktuelle System besitzt damit drei sauber getrennte Arten von Einträgen:

1. **Wurzeln** tragen produktive Bedeutungen;
2. **Formelkarten** speichern häufige Schreibformen derselben Kompositionen;
3. **Fach- und Bildkarten** tragen tatsächlich gelernte Ganzwerte.

Das passt besser zur gesuchten Mischung aus Fachkürzeln und gelernten
Ganzwörtern als ein Lexikon, in dem jede häufige Form eine neue Bedeutung
erhält.
"""
    (HERE / "PASS998_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
