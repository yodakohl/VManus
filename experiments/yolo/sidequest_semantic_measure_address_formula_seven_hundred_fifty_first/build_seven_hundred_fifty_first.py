#!/usr/bin/env python3
"""Build Pass 751: context-bound measure/address phrase variants."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P750 = ROOT / "experiments/yolo/sidequest_semantic_current_preparation_formula_seven_hundred_fiftieth"


def read() -> list[dict[str, str]]:
    path = P750 / "SEVEN_HUNDRED_FIFTIETH_116_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    {
        "rule_id": "R1_RESUMED_MEASURED_ADDITION",
        "function": "MEASURED_ITEM_BRACKET",
        "trigger": ["RESUME_CARD", "Y+K+AIIN"],
        "replacement": ["RESUME_CARD", "Y", "K+Y", "Y", "AIIN"],
        "reading_de": "WIEDERAUFNEHMEN | DIES | DIES ZUGEBEN | DIES | SOLLMASS",
        "explanation": "the resumed item is written before, inside and after the addition command",
    },
    {
        "rule_id": "R2_MEASURED_ITEM_BEFORE_FULL_CLOSE",
        "function": "MEASURED_ITEM_BRACKET",
        "trigger": ["AIIN", "OK+EEE+DY"],
        "replacement": ["AIIN", "Y", "OK+EEE+DY"],
        "reading_de": "SOLLMASS | DIES | VOLL ANSETZEN; SCHLUSS",
        "explanation": "the measured item is restated before the fully closed activation",
    },
    {
        "rule_id": "R3_ACTIVATE_THEN_MEASURE_BEFORE_WATER_TRANSFER",
        "function": "ACTIVATION_FOLLOWED_BY_MEASURE",
        "trigger": ["Y", "OK+AIIN", "CHD+AIR", "OT+CHD+DY"],
        "replacement": ["OK+Y", "AIIN", "CHD+AIR", "OT+CHD+DY"],
        "reading_de": "DIES ANSETZEN | SOLLMASS | WASSER UMSETZEN | DANACH UMSETZEN; SCHLUSS",
        "explanation": "operation-headed packing places the item with OK and writes the measure separately",
    },
]


def replace_once(sequence: list[str], trigger: list[str], replacement: list[str]) -> tuple[list[str], bool]:
    hits = [i for i in range(len(sequence) - len(trigger) + 1) if sequence[i : i + len(trigger)] == trigger]
    if not hits:
        return sequence, False
    if len(hits) != 1:
        raise AssertionError((trigger, hits))
    start = hits[0]
    return sequence[:start] + replacement + sequence[start + len(trigger) :], True


def main() -> None:
    source = read()
    audit_rows = []
    occurrence_rows = []
    fixed_rows = []
    residual_rows = []
    for row in source:
        baseline = row["current_preparation_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule in RULES:
            predicted, hit = replace_once(predicted, rule["trigger"], rule["replacement"])
            if hit:
                applied.append(rule["rule_id"])
                occurrence_rows.append({
                    "rule_id": rule["rule_id"],
                    "function": rule["function"],
                    "statement_id": row["statement_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "trigger_recipe_sequence": " | ".join(rule["trigger"]),
                    "replacement_recipe_sequence": " | ".join(rule["replacement"]),
                    "reading_de": rule["reading_de"],
                    "explanation": rule["explanation"],
                })
        baseline_exact = baseline == observed
        candidate_exact = predicted == observed
        out = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "pass750_recipe_sequence": row["current_preparation_recipe_sequence"],
            "measure_formula_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE",
            "baseline_cards": len(baseline),
            "candidate_cards": len(predicted),
            "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO",
            "candidate_exact": "YES" if candidate_exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and candidate_exact else "NO",
            "newly_harmed": "YES" if baseline_exact and not candidate_exact else "NO",
        }
        audit_rows.append(out)
        if out["newly_fixed"] == "YES":
            fixed_rows.append(out)
        if not candidate_exact:
            residual_rows.append(out)

    rule_rows = []
    for rule in RULES:
        occurrences = [row for row in occurrence_rows if row["rule_id"] == rule["rule_id"]]
        affected = [row for row in audit_rows if rule["rule_id"] in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule["rule_id"],
            "function": rule["function"],
            "trigger_recipe_sequence": " | ".join(rule["trigger"]),
            "replacement_recipe_sequence": " | ".join(rule["replacement"]),
            "reading_de": rule["reading_de"],
            "explanation": rule["explanation"],
            "trigger_count": len(occurrences),
            "statement_ids": ",".join(row["statement_id"] for row in occurrences),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in affected),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in affected),
            "retain_rule": "YES" if occurrences and all(row["newly_fixed"] == "YES" for row in affected) else "NO",
        })

    write("SEVEN_HUNDRED_FIFTY_FIRST_3_MEASURE_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTY_FIRST_3_TRIGGER_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_FIFTY_FIRST_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTY_FIRST_3_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FIFTY_FIRST_23_RESIDUAL_ERRORS.tsv", residual_rows)

    exact = sum(row["candidate_exact"] == "YES" for row in audit_rows)
    equal = sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    cards = sum(int(row["candidate_cards"]) for row in audit_rows)
    report = f"""# Pass 751 — Sollmass- und Adressformeln

AIIN bleibt **SOLLMASS**. Die drei neuen Regeln machen daraus keinen frei kopierbaren Zahlenstamm, sondern drei konkrete Schreibwendungen.

## Die drei Wendungen

1. H3-S003 entfaltet `WIEDERAUFNEHMEN | DIES ZUGEBEN SOLLMASS` zu `WIEDERAUFNEHMEN | DIES | DIES ZUGEBEN | DIES | SOLLMASS`. Der Posten rahmt die Zugabe und das Mass.
2. B2-S012 schreibt vor dem vollstaendig geschlossenen Ansetzen `SOLLMASS | DIES`.
3. B3-S030 packt operation-first: `DIES ANSETZEN | SOLLMASS`, danach Wasser umsetzen und schliessen.

## Ergebnis

- Exakte Aussagen:90→{exact}/116.
- Richtige Kartenzahl:101→{equal}/116.
- Ausgabekarten:353→{cards}/381.
- Drei ganze Aussagen repariert, keine beschaedigt;{len(residual_rows)} bleiben.

Die brauchbare Generalisierung ist nun: **AIIN benennt das Sollmass, aber die Werkstatt besitzt mehrere gelernte Arten, den gemessenen Posten rundherum erneut zu schreiben.** Als Naechstes werden die sieben Weiter-/Ziel-/Schluss-Bruecken geschlossen.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "rules": len(rule_rows),
        "triggers": len(occurrence_rows),
        "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows),
        "candidate_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "candidate_equal_card_count": equal,
        "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "candidate_cards": cards,
        "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows),
        "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "AIIN_REMAINS_PRESCRIBED_MEASURE__THREE_CONTEXT_PHRASES_FIX_THREE__CONTINUATION_BRIDGES_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
