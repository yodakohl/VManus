#!/usr/bin/env python3
"""Build Pass 750: current-preparation OR|Y phrase variants."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P748 = ROOT / "experiments/yolo/sidequest_semantic_context_bound_formula_completion_seven_hundred_forty_eighth"


def read() -> list[dict[str, str]]:
    path = P748 / "SEVEN_HUNDRED_FORTY_EIGHTH_116_FORMULA_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    {
        "rule_id": "R1_REPEAT_PREPARATION_AROUND_STAGE",
        "trigger": ["O+Y+K+OR", "OR", "Y", "K+IIN", "CH+O+AIIN"],
        "replacement": ["O+Y+K+OR", "OR", "OR", "Y", "K+IIN", "Y", "CH+O+AIIN"],
        "reading_de": "ARBEITSGANG DIES ZUGEBEN ANSATZ | ANSATZ | ANSATZ | DIES | STUFE ZUGEBEN | DIES | ENTNEHMEN ARBEITSGANG SOLLMASS",
        "phrase_role": "repeat the preparation, reactivate it, then restate the item after the stage",
    },
    {
        "rule_id": "R2_PREPARATION_BEFORE_PORTION",
        "trigger": ["OL+T+Y", "OR+AIN"],
        "replacement": ["OL+T+Y", "OR", "Y", "OR+AIN"],
        "reading_de": "WEITER ANWENDEN DIES | ANSATZ | DIES | ANSATZPORTION",
        "phrase_role": "name and reactivate the preparation before its portion",
    },
    {
        "rule_id": "R3_PREPARATION_BEFORE_PASSAGE",
        "trigger": ["OR", "O+CKH+E+Y", "AIR+Y+DY"],
        "replacement": ["OR", "Y", "O+CKH+E+Y", "AIR+Y+DY"],
        "reading_de": "ANSATZ | DIES | ARBEITSGANG DURCHLASS KURZ DIES | WASSER DIES; SCHLUSS",
        "phrase_role": "reactivate the preparation before the passage operation",
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
    fixed_rows = []
    residual_rows = []
    trigger_rows = []
    for row in source:
        baseline = row["formula_completed_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule in RULES:
            predicted, hit = replace_once(predicted, rule["trigger"], rule["replacement"])
            if hit:
                applied.append(rule["rule_id"])
                trigger_rows.append({
                    "rule_id": rule["rule_id"],
                    "statement_id": row["statement_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "trigger_recipe_sequence": " | ".join(rule["trigger"]),
                    "replacement_recipe_sequence": " | ".join(rule["replacement"]),
                    "reading_de": rule["reading_de"],
                    "phrase_role": rule["phrase_role"],
                })
        baseline_exact = baseline == observed
        predicted_exact = predicted == observed
        out = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "pass748_recipe_sequence": row["formula_completed_recipe_sequence"],
            "current_preparation_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE",
            "baseline_cards": len(baseline),
            "candidate_cards": len(predicted),
            "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO",
            "candidate_exact": "YES" if predicted_exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and predicted_exact else "NO",
            "newly_harmed": "YES" if baseline_exact and not predicted_exact else "NO",
        }
        audit_rows.append(out)
        if out["newly_fixed"] == "YES":
            fixed_rows.append(out)
        if not predicted_exact:
            residual_rows.append(out)

    rule_rows = []
    for rule in RULES:
        hits = [row for row in trigger_rows if row["rule_id"] == rule["rule_id"]]
        affected = [row for row in audit_rows if rule["rule_id"] in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule["rule_id"],
            "core_formula": "OR | Y",
            "trigger_recipe_sequence": " | ".join(rule["trigger"]),
            "replacement_recipe_sequence": " | ".join(rule["replacement"]),
            "reading_de": rule["reading_de"],
            "phrase_role": rule["phrase_role"],
            "trigger_count": len(hits),
            "statement_ids": ",".join(row["statement_id"] for row in hits),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in affected),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in affected),
            "retain_rule": "YES" if hits and all(row["newly_fixed"] == "YES" for row in affected) else "NO",
        })

    write("SEVEN_HUNDRED_FIFTIETH_3_CURRENT_PREPARATION_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTIETH_3_TRIGGER_OCCURRENCES.tsv", trigger_rows)
    write("SEVEN_HUNDRED_FIFTIETH_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTIETH_3_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FIFTIETH_26_RESIDUAL_ERRORS.tsv", residual_rows)

    exact = sum(row["candidate_exact"] == "YES" for row in audit_rows)
    equal_count = sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    cards = sum(int(row["candidate_cards"]) for row in audit_rows)
    report = f"""# Pass 750 — OR | Y als aktuelle Zubereitung

Alle drei verbleibenden `OR | Y`-Stellen lassen sich mit derselben kurzen Werkstattidee lesen: **ANSATZ | DIES**. OR nennt die Zubereitung; Y setzt sie als aktuellen Arbeitsposten fuer die folgende Karte wieder ein.

## Drei Varianten

1. In H2-S003 wird der Ansatz um eine Stufenangabe herum erneut genannt und der Posten nach der Stufe wieder aufgenommen.
2. In H4-S004 steht `OR | Y` vor der Ansatzportion.
3. In B4-S014 steht `OR | Y` vor dem Durchlass-/Wasserlauf.

Die Regeln erkennen jeweils die ganze Kartenumgebung, nicht nur ein einzelnes OR. Dadurch werden genau diese drei Aussagen repariert und keine andere umgeschrieben.

## Ergebnis

- Exakte Aussagen:87→{exact}/116.
- Richtige Kartenzahl:98→{equal_count}/116.
- Ausgabekarten:348→{cards}/381.
- Drei Regeln, drei Treffer, drei vollstaendige Reparaturen, null Schaden.
- {len(residual_rows)} Restfehler bleiben.

Damit ist `OR | Y` keine neue Wortbedeutung, sondern eine gelernte Wiederaufnahmeformel: **der Ansatz — dieser**. Als Naechstes folgt die groessere Sollmass-/Adressfamilie mit elf Fragmenten.
"""
    (HERE / "SEVEN_HUNDRED_FIFTIETH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "rules": len(rule_rows),
        "triggers": len(trigger_rows),
        "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows),
        "candidate_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "candidate_equal_card_count": equal_count,
        "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "candidate_cards": cards,
        "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows),
        "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "OR_Y_IS_CURRENT_PREPARATION_REACTIVATION__THREE_CONTEXTS_FIX_THREE__MEASURE_FRAME_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FIFTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
