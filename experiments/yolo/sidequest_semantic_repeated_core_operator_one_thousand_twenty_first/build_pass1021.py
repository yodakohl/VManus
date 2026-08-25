#!/usr/bin/env python3
"""Adjudicate repeated cores into package nesting versus free doubling."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
SOURCE = OUT / "REPEATED_CORE_OCCURRENCES.tsv"
BASE_SHEET = (
    OUT.parent
    / "sidequest_semantic_apprentice_sheet_roundtrip_one_thousand_twentieth"
    / "HISTORICAL_ONE_PAGE_MASTER_SHEET.md"
)

FREE_READINGS = {
    "OL": "FORTSETZEN und nochmals FORTSETZEN; der Besitzer kann daraus mehrere laufende Gänge machen",
    "AR": "zwei AUSGÄNGE auf derselben lokalen Ebene",
    "AL": "zwei ZIELORTE auf derselben lokalen Ebene",
    "Y": "zwei gesetzte oder aufeinander bezogene AKTIVE POSTEN",
    "OK": "SETZEN und nochmals SETZEN",
}


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        source_rows = list(csv.DictReader(fh, delimiter="\t"))

    rows = []
    for source in source_rows:
        core = source["core"]
        if core == "CH":
            rule = "PACKAGE_SCOPE_DESCENT"
            reading = "äußeren Besitzer NEHMEN; darin die aktive Untereinheit NEHMEN; dann den rechten Kern ausführen"
            rationale = "27/27 CH-Doppelungen entstehen am Anfang oder in einem L-Rahmen vor T, K, P oder S"
        elif core == "OR":
            rule = "PACKAGE_SCOPE_DESCENT"
            reading = "äußere EINHEIT; darin aktive Untereinheit; darin AKTIVER POSTEN"
            rationale = "einziger Beleg steht zwischen OK und Y als OK+OR+OR+Y"
        else:
            rule = "FREE_PLURAL_OR_REPEAT"
            reading = FREE_READINGS[core]
            rationale = "Doppelung endet frei oder steht als zweiter gleichrangiger Handlungskopf; keine innere Ergänzung rechts"
        row = dict(source)
        row.update({
            "selected_doubling_rule": rule,
            "selected_reading_de": reading,
            "selection_reason_de": rationale,
        })
        rows.append(row)

    fields = list(rows[0])
    with (OUT / "PASS1021_ADJUDICATED_DOUBLING.tsv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    rule_counts = Counter(row["selected_doubling_rule"] for row in rows)
    summary = {
        "result": "TWO_RULE_DOUBLING_GRAMMAR_SELECTED",
        "occurrences": len(rows),
        "package_scope_descent": rule_counts["PACKAGE_SCOPE_DESCENT"],
        "free_plural_or_repeat": rule_counts["FREE_PLURAL_OR_REPEAT"],
        "triple_runs": 0,
        "new_core_values": 0,
        "f13r_s009": "OK + outer EINHEIT + inner EINHEIT + AKTIVER POSTEN",
    }
    (OUT / "PASS1021_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    base_sheet = BASE_SHEET.read_text(encoding="utf-8")
    doubling_section = """## Elfte Regel: zwei gleiche Kerne

```text
PAKETGRENZE:  X + X + Z  = äußeres X [inneres X [Z]]
FREI:         X + X      = mehrere X bei Dingen / X nochmals bei Handlungen
```

An einer geöffneten Paketgrenze gehören die zwei Kerne zu zwei benachbarten
Besitzerebenen. Frei stehende Doppelkerne werden beide gleichrangig gelesen.
Der zweite Kern wird nie als bloßes Ditto gelöscht und erhält kein neues Wort.

"""
    revised_sheet = base_sheet.replace("## So wird gelesen\n", doubling_section + "## So wird gelesen\n")
    if revised_sheet == base_sheet:
        raise RuntimeError("sheet insertion point not found")
    (OUT / "PASS1021_CURRENT_APPRENTICE_SHEET.md").write_text(revised_sheet, encoding="utf-8")


if __name__ == "__main__":
    main()
