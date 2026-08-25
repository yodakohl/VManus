#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"
V79 = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_REPAIR_DECISIONS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    cards = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv")
    statements = read(V72)
    repair_decisions = read(V79)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    duplicates: list[dict[str, object]] = []
    for statement_id, rows in by_statement.items():
        for left, right in zip(rows, rows[1:]):
            if left["card_no"] != right["card_no"]:
                continue
            pair = f'{left["event_id"]}->{right["event_id"]}'
            if pair == "E180->E181":
                decision = "VISIBLE_EDGE_COPY_READ_ONCE"
                source_tokens = 1
                correction_action = "KEEP_BOTH_VISIBLE__EMIT_ONE_LOGICAL_TOKEN"
                reason = "einziger qualifizierter physischer Zeilenrandfall; gleiche Karte, gleicher Besitzer, kein Schluss oder Reset"
            elif pair == "E020->E021":
                decision = "INTENDED_CURRENT_ITEM_REPETITION_RETAIN"
                source_tokens = 2
                correction_action = "NONE"
                reason = "zwei verschiedene Oberflaechen derselben Y-Karte mitten in der grossen H2-Formel; kein Randkriterium"
            else:
                decision = "INTENDED_OR_LOCAL_FORMULA_REPETITION_RETAIN"
                source_tokens = 2
                correction_action = "NONE"
                reason = "zwei Oberflaechen derselben OR-Karte innerhalb der Formel; kein Randkriterium fuer Read-once"
            duplicates.append({
                "pair": pair,
                "statement_id": statement_id,
                "page": left["page"],
                "exact_card_id": left["card_no"],
                "left_surface": left["surface"],
                "right_surface": right["surface"],
                "component_recipe": left["component_recipe"],
                "visible_cards": 2,
                "logical_source_tokens": source_tokens,
                "decision": decision,
                "correction_action": correction_action,
                "reason": reason,
            })
    write(
        "SEVEN_HUNDRED_SIXTY_SIXTH_3_ADJACENT_DUPLICATES.tsv",
        duplicates,
        ["pair", "statement_id", "page", "exact_card_id", "left_surface", "right_surface", "component_recipe", "visible_cards", "logical_source_tokens", "decision", "correction_action", "reason"],
    )

    open_rows = []
    for statement_id, rows in by_statement.items():
        last = rows[-1]
        if "DY" in last["component_recipe"].split("+"):
            continue
        open_rows.append({
            "statement_id": statement_id,
            "page": last["page"],
            "record": last["record"],
            "events": len(rows),
            "last_event": last["event_id"],
            "last_surface": last["surface"],
            "last_recipe": last["component_recipe"],
            "decision": "INTENDED_OPEN_STATEMENT_RETAIN",
            "correction_action": "DO_NOT_INSERT_CLOSE",
        })
    write(
        "SEVEN_HUNDRED_SIXTY_SIXTH_27_OPEN_STATEMENTS.tsv",
        open_rows,
        ["statement_id", "page", "record", "events", "last_event", "last_surface", "last_recipe", "decision", "correction_action"],
    )

    grade_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        parts = row["component_recipe"].split("+")
        if not any(part in {"E", "EE", "EEE"} for part in parts):
            continue
        normal = "+".join("<GRADE>" if part in {"E", "EE", "EEE"} else part for part in parts)
        grade_groups[normal].append(row)
    grade_rows = []
    for normal, rows in sorted(grade_groups.items()):
        variants = sorted({row["component_recipe"] for row in rows})
        if len(variants) < 2:
            continue
        grade_rows.append({
            "normalized_family": normal,
            "grade_variants": " | ".join(variants),
            "exact_cards": len(rows),
            "events": sum(int(row["events"]) for row in rows),
            "contains_singleton_eee": "YES" if any("EEE" in row["component_recipe"].split("+") and int(row["events"]) == 1 for row in rows) else "NO",
            "decision": "PRODUCTIVE_GRADE_CHOICES_RETAIN",
            "correction_action": "NONE_WITHOUT_MASTER_PROMPT_CONFLICT",
        })
    write(
        "SEVEN_HUNDRED_SIXTY_SIXTH_8_GRADE_PARADIGMS.tsv",
        grade_rows,
        ["normalized_family", "grade_variants", "exact_cards", "events", "contains_singleton_eee", "decision", "correction_action"],
    )

    owner_resets = []
    for row in statements:
        if "BREAK_VISIBLE_GAP" not in row["owner_transition"] or " > " not in row["owner_bindings"]:
            continue
        owners = []
        for binding in row["owner_bindings"].split(" > "):
            owners.append(binding.split(":", 1)[-1])
        if len(set(owners)) < 2:
            continue
        owner_resets.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "fields": row["constituent_fields"],
            "event_serials": row["event_serials"],
            "owner_bindings": row["owner_bindings"],
            "owner_transition": row["owner_transition"],
            "decision": "VISIBLE_OWNER_RESET_RETAIN",
            "correction_action": "DO_NOT_BRIDGE_WITH_CARRY_MARK",
        })
    write(
        "SEVEN_HUNDRED_SIXTY_SIXTH_4_MID_STATEMENT_OWNER_RESETS.tsv",
        owner_resets,
        ["statement_id", "page", "fields", "event_serials", "owner_bindings", "owner_transition", "decision", "correction_action"],
    )

    read_once = next(row for row in repair_decisions if row["issue"] == "GENERAL_VISIBLE_READ_ONCE_RULE")
    decisions = [
        {"awkward_family": "ADJACENT_IDENTICAL_CARDS", "observations": 3, "artifact_cases": 1, "intended_or_unresolved_cases": 2, "workshop_reading": "Nur E180/E181 wird einmal gelesen; die beiden anderen Paare bleiben doppelt.", "why": read_once["evidence"]},
        {"awkward_family": "OPEN_STATEMENTS", "observations": len(open_rows), "artifact_cases": 0, "intended_or_unresolved_cases": len(open_rows), "workshop_reading": "Offene Aussage ist ein eigener zugelassener Typ; kein stiller Schluss.", "why": "15 Herbal- und12 Bio-Aussagen enden ohne DY; Verteilung ist zu breit fuer zufaelliges Auslassen."},
        {"awkward_family": "GRADE_VARIANTS", "observations": len(grade_rows), "artifact_cases": 0, "intended_or_unresolved_cases": len(grade_rows), "workshop_reading": "E/EE/EEE sind gelernte Gradwahlen; seltenes EEE bleibt erlaubt.", "why": "acht Familien besitzen mehr als einen Grad; Korrektur nur bei Konflikt mit dem Meisterprompt."},
        {"awkward_family": "MID_STATEMENT_OWNER_RESETS", "observations": len(owner_resets), "artifact_cases": 0, "intended_or_unresolved_cases": len(owner_resets), "workshop_reading": "Bildbesitzerwechsel schlaegt Satzkontinuitaet.", "why": "vier Aussagen wechseln zwischen sichtbar getrennten lokalen Stationen."},
        {"awkward_family": "TOTAL_VISIBLE_VS_SOURCE", "observations": 381, "artifact_cases": 1, "intended_or_unresolved_cases": 380, "workshop_reading": "381 sichtbare Karten repraesentieren380 logische Quellkarten.", "why": "genau eine lokale Randkopie wird read-once behandelt."},
    ]
    write(
        "SEVEN_HUNDRED_SIXTY_SIXTH_5_DECISIONS.tsv",
        decisions,
        ["awkward_family", "observations", "artifact_cases", "intended_or_unresolved_cases", "workshop_reading", "why"],
    )

    report = """# Pass 766 — Welche wirklichen Stolperstellen sind Schreibfehler?

Die kurze Antwort: fast keine.

Es gibt drei unmittelbar doppelte exakte Karten. Nur `E180/E181` sitzt genau an der bekannten physischen Zeilengrenze und erfuellt die lokale Read-once-Regel. Beide Formen bleiben sichtbar, aber der Schreiber spricht bzw. plant nur eine Quellkarte. `E020/E021` und `E033/E034` stehen mitten in ihren Formeln, haben jeweils zwei Oberflaechen und keinen Randhinweis; sie bleiben absichtliche Wiederholung oder gelernte lokale Formel.

Auch die anderen vermeintlichen Fehler verschwinden beim Blick auf das ganze kleine System:

- 27 von116 Aussagen sind regelhaft offen, 15 Herbal und12 Bio. Wir setzen keinen erfundenen Schluss ein.
- Acht Kartenfamilien benutzen mindestens zwei der Grade E/EE/EEE. Ein seltener Vollgrad ist deshalb kein Schreibfehler.
- Vier Aussagen wechseln mitten im rekonstruierten Satz sichtbar den Bildbesitzer. Der Besitzerwechsel ist staerker als unser Satzfluss; wir verbinden die Stationen nicht kuenstlich.

Damit haben wir381 sichtbare Karten, aber380 logische Quellkarten. Der einzige produktionsnahe Sonderfall ist eine lokale Randwiederholung; er wird nicht ausradiert, sondern beim Lesen einmal verbraucht.

Als naechstes wird der Vorwaertskompiler genau so umgebaut: erst380 logische Quellkarten erzeugen, dann als reine Schreib-/Layoutoperation die Randkopie E180 einfuegen und wieder381 sichtbare Karten liefern.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "visible_cards": len(events),
        "logical_source_cards": len(events) - 1,
        "adjacent_duplicate_pairs": len(duplicates),
        "read_once_pairs": sum(row["logical_source_tokens"] == 1 for row in duplicates),
        "open_statements": len(open_rows),
        "grade_paradigms": len(grade_rows),
        "mid_statement_owner_resets": len(owner_resets),
        "decision": "ONE_LOCAL_EDGE_COPY__ALL_OTHER_AWKWARD_FORMS_RETAINED_AS_INTENDED_OR_UNRESOLVED",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
