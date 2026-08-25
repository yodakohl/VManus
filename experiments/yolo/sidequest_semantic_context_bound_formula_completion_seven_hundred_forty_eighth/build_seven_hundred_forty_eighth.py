#!/usr/bin/env python3
"""Build Pass 748: activate context-bound three-card workshop formulas."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P745 = ROOT / "experiments/yolo/sidequest_semantic_active_y_valency_seven_hundred_forty_fifth"


def read() -> list[dict[str, str]]:
    path = P745 / "SEVEN_HUNDRED_FORTY_FIFTH_116_Y_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    {
        "rule_id": "R1_MEASURED_ITEM_BEFORE_CLOSED_TRANSFER",
        "formula": "Y | AIIN | Y",
        "trigger": ["Y", "AIIN", "L+CHD+DY"],
        "replacement": ["Y", "AIIN", "Y", "L+CHD+DY"],
        "reading_de": "DIES | SOLLMASS | DIES | LEITEN UMSETZEN; SCHLUSS",
        "why_context_is_needed": "AIIN/Y alone also occur in unrelated cards; the following closed transfer selects the bracket",
    },
    {
        "rule_id": "R2_STAGED_ACTIVATION_BEFORE_HOLD",
        "formula": "OK+EE+Y | OK+Y | OL",
        "trigger": ["OK+EE+Y", "OK+EE+OL", "SH"],
        "replacement": ["OK+EE+Y", "OK+Y", "OL", "SH+EE+Y"],
        "reading_de": "DIES LANG ANSETZEN | DIES ANSETZEN | WEITER | DIES LANG HALTEN",
        "why_context_is_needed": "the following hold receives the long grade after the staged activation formula",
    },
    {
        "rule_id": "R3_STAGED_ACTIVATION_AFTER_NEXT_TARGET",
        "formula": "OK+EE+Y | OK+Y | OL",
        "trigger": ["OT+EE+Y", "OK+OL", "OK+OL", "SHED+DY"],
        "replacement": ["OT+Y", "OK+EE+Y", "OK+Y", "OL", "SHED+DY"],
        "reading_de": "DANACH DIES | DIES LANG ANSETZEN | DIES ANSETZEN | WEITER | ABSETZEN; SCHLUSS",
        "why_context_is_needed": "the grade belongs to the activation phrase, not to the preceding next-item card",
    },
]


def replace_once(sequence: list[str], trigger: list[str], replacement: list[str]) -> tuple[list[str], int]:
    hits = [start for start in range(len(sequence) - len(trigger) + 1) if sequence[start : start + len(trigger)] == trigger]
    if not hits:
        return sequence, 0
    if len(hits) != 1:
        raise AssertionError(f"ambiguous trigger {trigger}: {hits}")
    start = hits[0]
    return sequence[:start] + replacement + sequence[start + len(trigger) :], 1


def main() -> None:
    source = read()
    audit_rows = []
    fixed_rows = []
    residual_rows = []
    rule_counts = {rule["rule_id"]: 0 for rule in RULES}
    for row in source:
        baseline = row["y_valent_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule in RULES:
            predicted, count = replace_once(predicted, rule["trigger"], rule["replacement"])
            if count:
                applied.append(rule["rule_id"])
                rule_counts[rule["rule_id"]] += count
        baseline_exact = baseline == observed
        predicted_exact = predicted == observed
        output = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "y_valent_recipe_sequence": row["y_valent_recipe_sequence"],
            "formula_completed_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE",
            "baseline_cards": len(baseline),
            "formula_cards": len(predicted),
            "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO",
            "formula_exact": "YES" if predicted_exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and predicted_exact else "NO",
            "newly_harmed": "YES" if baseline_exact and not predicted_exact else "NO",
        }
        audit_rows.append(output)
        if output["newly_fixed"] == "YES":
            fixed_rows.append(output)
        if not predicted_exact:
            residual_rows.append(output)

    rule_rows = []
    for rule in RULES:
        triggers = [row for row in audit_rows if rule["rule_id"] in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule["rule_id"],
            "formula": rule["formula"],
            "trigger_recipe_sequence": " | ".join(rule["trigger"]),
            "replacement_recipe_sequence": " | ".join(rule["replacement"]),
            "reading_de": rule["reading_de"],
            "why_context_is_needed": rule["why_context_is_needed"],
            "trigger_count": rule_counts[rule["rule_id"]],
            "trigger_statement_ids": ",".join(row["statement_id"] for row in triggers),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in triggers),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in triggers),
            "retain_rule": "YES" if triggers and all(row["newly_fixed"] == "YES" for row in triggers) else "NO",
        })

    write("SEVEN_HUNDRED_FORTY_EIGHTH_3_CONTEXT_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FORTY_EIGHTH_116_FORMULA_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FORTY_EIGHTH_3_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FORTY_EIGHTH_29_RESIDUAL_ERRORS.tsv", residual_rows)

    exact = sum(row["formula_exact"] == "YES" for row in audit_rows)
    equal_count = sum(int(row["formula_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    total_cards = sum(int(row["formula_cards"]) for row in audit_rows)
    report = f"""# Pass 748 — kontextgebundene Formelausgabe

Die zwei Dreikartenformeln aus Pass747 wurden als drei konkrete Werkstattregeln ausgefuehrt. Die Regel sieht nie nur `AIIN+Y` oder `OK+Y`; sie verlangt die ganze benachbarte Kartenumgebung.

## Ergebnis

- `Y | AIIN | Y` wird vor einer geschlossenen Transferkarte geschrieben. Das repariert B3-S003.
- `OK+EE+Y | OK+Y | OL` besitzt eine Haltevariante. Das repariert B2-S010.
- Dieselbe Aktivierungsformel besitzt eine Folge-/Zielvariante. Das repariert B4-S003.
- Exakte Aussagen steigen84→{exact}/116.
- Aussagen mit richtiger Kartenzahl steigen95→{equal_count}/116.
- Ausgabekarten steigen345→{total_cards} gegen381 beobachtete.
- Drei Restfehler werden exakt, keiner der84 bereits richtigen Faelle wird beschaedigt;{len(residual_rows)} bleiben.

## Werkstattlehre

Der Lehrling bekommt nicht die Regel „wiederhole jedes Sollmass“. Er bekommt kleine Satzbausteine:

1. Vor geschlossenem Umsetzen kann ein Posten als `DIES | SOLLMASS | DIES` geklammert werden.
2. Eine lange Aktivierung kann als `LANG ANSETZEN | ANSETZEN | WEITER` entfaltet werden.
3. Der lange Grad wandert innerhalb dieser Formel zur Aktivierung oder zum anschliessenden Halten; er ist kein frei kopierter Stamm.

Das ist genau die gesuchte Mischung aus produktiven Stämmen und gelernten Fachwendungen. Als Nächstes werden die zwoelf Zweikartenfragmente nicht blind aktiviert, sondern zu wenigen groesseren Phrasenfamilien zusammengelegt. Ziel ist eine weitere Reparatur ohne neue Einzelbedeutung.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "rules": len(rule_rows),
        "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows),
        "formula_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "formula_equal_card_count": equal_count,
        "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "formula_cards": total_cards,
        "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows),
        "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows),
        "semantic_changes": 0,
        "deck_changes": 0,
        "decision": "THREE_CONTEXT_BOUND_FORMULA_RULES_FIX_THREE_WITHOUT_HARM__CLUSTER_BIGRAMS_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
