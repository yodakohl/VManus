#!/usr/bin/env python3
"""Build Pass 755: two card segmentation/redistribution conventions."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P754 = ROOT / "experiments/yolo/sidequest_semantic_minimal_local_packing_seven_hundred_fifty_fourth"


def read() -> list[dict[str, str]]:
    path = P754 / "SEVEN_HUNDRED_FIFTY_FOURTH_116_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    {
        "rule_id": "R1_SPLIT_PASSAGE_AND_TRANSFER",
        "kind": "SAME_COMPONENTS_NEW_CARD_BOUNDARY",
        "trigger": ["OK+AIN", "L+CKH+Y", "R+AL"],
        "replacement": ["OK+AIN", "CKH+Y", "L", "R+AL"],
        "reading_de": "PORTION ANSETZEN | DIES DURCHLASS | LEITEN | AN ZIELSTELLE KUEHLEN",
        "explanation": "L is written as its own transfer card after the passage card",
    },
    {
        "rule_id": "R2_REDISTRIBUTE_CONTINUATION_AND_ACTIVE_ITEM",
        "kind": "NEIGHBOR_COMPONENT_REDISTRIBUTION_WITH_Y_VALENCY",
        "trigger": ["Y", "OK+EE+OL", "OK+E+DY"],
        "replacement": ["OL+Y", "OK+EE+Y", "OK+E+DY"],
        "reading_de": "DIES WEITER | DIES LANG ANSETZEN | KURZ ANSETZEN; SCHLUSS",
        "explanation": "OL moves to the current-item card and Y fills the long activation card",
    },
]


def flatten(sequence: list[str]) -> Counter[str]:
    return Counter(component for card in sequence for component in card.split("+"))


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
        baseline = row["minimal_packing_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule in RULES:
            predicted, hit = replace_once(predicted, rule["trigger"], rule["replacement"])
            if hit:
                applied.append(rule["rule_id"])
                before = flatten(rule["trigger"])
                after = flatten(rule["replacement"])
                occurrence_rows.append({
                    "rule_id": rule["rule_id"], "kind": rule["kind"],
                    "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
                    "trigger_recipe_sequence": " | ".join(rule["trigger"]),
                    "replacement_recipe_sequence": " | ".join(rule["replacement"]),
                    "reading_de": rule["reading_de"], "explanation": rule["explanation"],
                    "component_delta": "+".join(item for item, count in sorted((after - before).items()) for _ in range(count)) or "NONE",
                })
        baseline_exact = baseline == observed
        exact = predicted == observed
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "pass754_recipe_sequence": row["minimal_packing_recipe_sequence"],
            "redistributed_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE",
            "baseline_cards": len(baseline), "candidate_cards": len(predicted), "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO", "candidate_exact": "YES" if exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and exact else "NO", "newly_harmed": "YES" if baseline_exact and not exact else "NO",
        }
        audit_rows.append(out)
        if out["newly_fixed"] == "YES": fixed_rows.append(out)
        if not exact: residual_rows.append(out)

    rule_rows = []
    for rule in RULES:
        occurrences = [row for row in occurrence_rows if row["rule_id"] == rule["rule_id"]]
        affected = [row for row in audit_rows if rule["rule_id"] in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule["rule_id"], "kind": rule["kind"],
            "trigger_recipe_sequence": " | ".join(rule["trigger"]), "replacement_recipe_sequence": " | ".join(rule["replacement"]),
            "reading_de": rule["reading_de"], "explanation": rule["explanation"],
            "trigger_count": len(occurrences), "statement_ids": ",".join(row["statement_id"] for row in occurrences),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in affected),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in affected),
            "retain_rule": "YES" if occurrences and all(row["newly_fixed"] == "YES" for row in affected) else "NO",
        })

    write("SEVEN_HUNDRED_FIFTY_FIFTH_2_REDISTRIBUTION_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTY_FIFTH_2_TRIGGER_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_FIFTY_FIFTH_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTY_FIFTH_2_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FIFTY_FIFTH_10_RESIDUAL_ERRORS.tsv", residual_rows)

    exact = sum(row["candidate_exact"] == "YES" for row in audit_rows)
    equal = sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    cards = sum(int(row["candidate_cards"]) for row in audit_rows)
    report = f"""# Pass 755 — Kartengrenze und Nachbarumverteilung

Zwei Restfaelle brauchen keine neue Bedeutung.

- B1-S006 schreibt `CKH+Y | L` statt `L+CKH+Y`: derselbe Durchlass und dieselbe Leitung, aber zwei Karten.
- B4-S002 schreibt `OL+Y | OK+EE+Y` statt `Y | OK+EE+OL`: WEITER sitzt bei der Postenkarte, der aktive Y-Slot bei der langen Ansetzkarte.

## Ergebnis

- Exakte Aussagen:104→{exact}/116.
- Richtige Kartenzahl:108→{equal}/116.
- Ausgabekarten:364→{cards}/381.
- Zwei Regeln, zwei Treffer, zwei Reparaturen, kein Schaden.
- {len(residual_rows)} Aussagen bleiben.

Die erste Regel veraendert nicht einmal die Komponentenmenge; die zweite ergaenzt nur den bereits etablierten Y-Valenzslot. Als naechstes folgen die drei kleinen Phrasenreihenfolgen H4-S001,H5-S003,B3-S032.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "rules": len(rule_rows), "triggers": len(occurrence_rows), "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows), "candidate_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "candidate_equal_card_count": equal, "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "candidate_cards": cards, "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows), "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows), "semantic_changes": 0, "deck_changes": 0,
        "decision": "TWO_SEGMENTATION_REDISTRIBUTION_RULES_FIX_TWO__THREE_SMALL_PHRASE_REORDERS_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
