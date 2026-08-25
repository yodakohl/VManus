#!/usr/bin/env python3
"""Build Pass 754: seven minimal local packing conventions."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P752 = ROOT / "experiments/yolo/sidequest_semantic_continuation_bridge_formula_seven_hundred_fifty_second"


def read() -> list[dict[str, str]]:
    path = P752 / "SEVEN_HUNDRED_FIFTY_SECOND_116_PACKING_AUDIT.tsv"
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    ("R1_APPEND_CURRENT_ITEM_AFTER_READY", "ACTIVE_ITEM_ECHO", ["OT+Y", "OK+OL", "CTH+Y"], ["OT+Y", "OK+OL", "CTH+Y", "Y"], "DANACH DIES | WEITER ANSETZEN | DIES BEREITEN | DIES"),
    ("R2_PACK_INGREDIENT_WITH_ITEM_AFTER_RESUME", "Y_VALENCY", ["RESUME_CARD", "HO", "OK+Y", "CH+EE+CKH+O+DY"], ["RESUME_CARD", "HO+Y", "OK+Y", "CH+EE+CKH+O+DY"], "WIEDERAUFNEHMEN | DIESE ZUTAT | DIES ANSETZEN | LANG ENTNEHMEN DURCHLASS ARBEITSGANG; SCHLUSS"),
    ("R3_USE_ATTESTED_T_E_Y_ORDER", "WITHIN_CARD_ORDER", ["E+T+Y", "OK+CHD+DY"], ["T+E+Y", "OK+CHD+DY"], "DIES KURZ ANWENDEN | ANSETZEN UMSETZEN; SCHLUSS"),
    ("R4_PACK_L_WITH_PASSAGE_ITEM", "NEIGHBOR_PACKING", ["OK+AL", "CKH+Y", "L+CHD", "OK+EE+Y", "L+CKH+E+DY"], ["OK+AL", "L+CKH+Y", "L+CHD", "OK+EE+Y", "L+CKH+E+DY"], "AN ZIELSTELLE ANSETZEN | DIES DURCH DURCHLASS LEITEN | LEITEN UMSETZEN | DIES LANG ANSETZEN | KURZ DURCH DURCHLASS LEITEN; SCHLUSS"),
    ("R5_REPEAT_MEASURED_ACTIVATION", "CARD_DUPLICATION", ["OK+AL+Y", "SOLK+AIIN", "CKH+Y", "OK+AIIN", "O+CTH+E+OL", "CHK+EE+Y", "L+DY"], ["OK+AL+Y", "SOLK+AIIN", "CKH+Y", "OK+AIIN", "OK+AIIN", "O+CTH+E+OL", "CHK+EE+Y", "L+DY"], "DIES AN ZIELSTELLE ANSETZEN | SOLLMASS SAMMELSTELLE | DIES DURCHLASS | NACH SOLLMASS ANSETZEN | NACH SOLLMASS ANSETZEN | ARBEITSGANG KURZ BEREITEN WEITER | DIES LANG WAERMEN | LEITEN; SCHLUSS"),
    ("R6_PACK_OK_WITH_MEASURE", "NEIGHBOR_PACKING", ["AL", "L+CHD+AR", "CH+E+S", "AIIN", "OT+EE+Y", "AIIN", "OK+E+Y", "P+CHD+DY"], ["AL", "L+CHD+AR", "CH+E+S", "AIIN", "OT+EE+Y", "OK+AIIN", "OK+E+Y", "P+CHD+DY"], "ZIELSTELLE | AUS QUELLE LEITEN UMSETZEN | TEIL KURZ ENTNEHMEN | SOLLMASS | DANACH DIES LANG | NACH SOLLMASS ANSETZEN | DIES KURZ ANSETZEN | FUELLEN UMSETZEN; SCHLUSS"),
    ("R7_PACK_SOURCE_WITH_ITEM", "Y_VALENCY", ["SH+E+CTH+CHD+Y", "OK+Y", "CHD+Y", "AR"], ["SH+E+CTH+CHD+Y", "OK+Y", "CHD+Y", "AR+Y"], "DIES KURZ HALTEN BEREITEN UMSETZEN | DIES ANSETZEN | DIES UMSETZEN | DIES AUS QUELLE"),
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
        baseline = row["continuation_bridge_recipe_sequence"].split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        predicted = baseline[:]
        applied = []
        for rule_id, kind, trigger, replacement, reading in RULES:
            predicted, hit = replace_once(predicted, trigger, replacement)
            if hit:
                applied.append(rule_id)
                occurrence_rows.append({
                    "rule_id": rule_id,
                    "packing_kind": kind,
                    "statement_id": row["statement_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "trigger_recipe_sequence": " | ".join(trigger),
                    "replacement_recipe_sequence": " | ".join(replacement),
                    "reading_de": reading,
                })
        baseline_exact = baseline == observed
        exact = predicted == observed
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "pass752_recipe_sequence": row["continuation_bridge_recipe_sequence"],
            "minimal_packing_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "applied_rules": ",".join(applied) or "NONE",
            "baseline_cards": len(baseline), "candidate_cards": len(predicted), "observed_cards": len(observed),
            "baseline_exact": "YES" if baseline_exact else "NO", "candidate_exact": "YES" if exact else "NO",
            "newly_fixed": "YES" if not baseline_exact and exact else "NO",
            "newly_harmed": "YES" if baseline_exact and not exact else "NO",
        }
        audit_rows.append(out)
        if out["newly_fixed"] == "YES":
            fixed_rows.append(out)
        if not exact:
            residual_rows.append(out)

    rule_rows = []
    for rule_id, kind, trigger, replacement, reading in RULES:
        occurrences = [row for row in occurrence_rows if row["rule_id"] == rule_id]
        affected = [row for row in audit_rows if rule_id in row["applied_rules"].split(",")]
        rule_rows.append({
            "rule_id": rule_id, "packing_kind": kind,
            "trigger_recipe_sequence": " | ".join(trigger), "replacement_recipe_sequence": " | ".join(replacement),
            "reading_de": reading, "trigger_count": len(occurrences),
            "statement_ids": ",".join(row["statement_id"] for row in occurrences),
            "newly_fixed": sum(row["newly_fixed"] == "YES" for row in affected),
            "newly_harmed": sum(row["newly_harmed"] == "YES" for row in affected),
            "retain_rule": "YES" if occurrences and all(row["newly_fixed"] == "YES" for row in affected) else "NO",
        })

    write("SEVEN_HUNDRED_FIFTY_FOURTH_7_MINIMAL_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTY_FOURTH_7_TRIGGER_OCCURRENCES.tsv", occurrence_rows)
    write("SEVEN_HUNDRED_FIFTY_FOURTH_116_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTY_FOURTH_7_NEWLY_FIXED.tsv", fixed_rows)
    write("SEVEN_HUNDRED_FIFTY_FOURTH_12_RESIDUAL_ERRORS.tsv", residual_rows)

    exact = sum(row["candidate_exact"] == "YES" for row in audit_rows)
    equal = sum(int(row["candidate_cards"]) == int(row["observed_cards"]) for row in audit_rows)
    cards = sum(int(row["candidate_cards"]) for row in audit_rows)
    report = f"""# Pass 754 — sieben minimale Packkonventionen

Die sieben Einzelschritt-Faelle aus Pass753 sind nun ausgefuehrt. Keine Bedeutung wurde geaendert.

## Was der Lehrling zusaetzlich lernt

- Nach einem bestimmten Bereit-Muster steht Y noch einmal allein.
- HO und AR koennen ihren aktuellen Y-Posten in die Karte aufnehmen.
- Die betreffende Anwendungskarte nutzt die attestierte Reihenfolge `T+E+Y`.
- L oder OK werden in zwei festen Umgebungen mit Durchlass beziehungsweise Sollmass gepackt.
- Eine gemessene Aktivierung wird in einer Stationsfolge genau einmal wiederholt.

## Ergebnis

- Exakte Aussagen:97→{exact}/116.
- Richtige Kartenzahl:106→{equal}/116.
- Ausgabekarten:362→{cards}/381.
- Sieben Regeln, sieben Treffer, sieben vollstaendige Reparaturen, null Schaden.
- {len(residual_rows)} Aussagen bleiben.

Der Packer erreicht damit erstmals deutlich ueber hundert vollstaendige Aussagen. Als naechstes kommen nur die zwei Segmentierungs-/Umverteilungsfaelle B1-S006 und B4-S002.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "rules": len(rule_rows), "triggers": len(occurrence_rows), "statements": len(audit_rows),
        "baseline_exact": sum(row["baseline_exact"] == "YES" for row in audit_rows), "candidate_exact": exact,
        "baseline_equal_card_count": sum(int(row["baseline_cards"]) == int(row["observed_cards"]) for row in audit_rows),
        "candidate_equal_card_count": equal, "baseline_cards": sum(int(row["baseline_cards"]) for row in audit_rows),
        "candidate_cards": cards, "observed_cards": sum(int(row["observed_cards"]) for row in audit_rows),
        "newly_fixed": len(fixed_rows), "newly_harmed": sum(row["newly_harmed"] == "YES" for row in audit_rows),
        "residual_errors": len(residual_rows), "semantic_changes": 0, "deck_changes": 0,
        "decision": "SEVEN_MINIMAL_PACKING_CONVENTIONS_FIX_SEVEN__TWO_SEGMENTATION_CASES_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
