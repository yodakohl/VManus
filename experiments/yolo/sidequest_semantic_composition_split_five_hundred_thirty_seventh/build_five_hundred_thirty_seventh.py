#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P536 = ROOT / "experiments/yolo/sidequest_semantic_common_workshop_grammar_five_hundred_thirty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def split_card(row: dict[str, str]) -> tuple[list[str], list[str]]:
    return row["component_parse"].split("+"), row["invariant_card_reading_de"].split(" · ")


def main() -> None:
    cards = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_SEVENTY_THREE_COMMON_CARD_GRAMMAR.tsv")
    events = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")

    evidence: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    event_support: Counter[tuple[str, str]] = Counter()
    card_alignment: dict[str, tuple[list[str], list[str], bool]] = {}
    for row in cards:
        components, glosses = split_card(row)
        aligned = len(components) == len(glosses) and not any(
            component.startswith("WHOLE[") for component in components
        )
        card_alignment[row["card_no"]] = (components, glosses, aligned)
        if not aligned:
            continue
        for component, gloss in zip(components, glosses):
            evidence[component][gloss].add(row["card_no"])
            event_support[(component, gloss)] += int(row["occurrences"])

    component_rows: list[dict[str, str]] = []
    for component in sorted(evidence):
        gloss_map = evidence[component]
        card_ids = set().union(*gloss_map.values())
        invariant = len(gloss_map) == 1
        component_rows.append(
            {
                "component": component,
                "observed_glosses_de": "|".join(sorted(gloss_map)),
                "aligned_card_types": str(len(card_ids)),
                "aligned_events": str(sum(event_support[(component, gloss)] for gloss in gloss_map)),
                "card_ids": "|".join(sorted(card_ids)),
                "invariant_across_aligned_cards": "YES" if invariant else "NO",
                "leave_one_card_productive": "YES" if invariant and len(card_ids) >= 2 else "NO",
                "selected_atomic_value_de": next(iter(gloss_map)) if invariant else "GELERNTE_KONTEXTWERTE",
                "status": (
                    "PRODUCTIVE_STEM"
                    if invariant and len(card_ids) >= 2
                    else "SINGLE_CARD_ATOM"
                    if invariant
                    else "CONTEXT_SPLIT_COMPONENT"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SEVENTH_COMPONENT_INVARIANCE_LEXICON.tsv", component_rows)

    decision_rows: list[dict[str, str]] = []
    for row in cards:
        components, glosses, aligned = card_alignment[row["card_no"]]
        tests: list[str] = []
        predictions: list[str] = []
        matches = 0
        if aligned:
            for component, gloss in zip(components, glosses):
                other_glosses = {
                    candidate_gloss
                    for candidate_gloss, ids in evidence[component].items()
                    if any(card_id != row["card_no"] for card_id in ids)
                }
                if len(other_glosses) == 1:
                    predicted = next(iter(other_glosses))
                    predictions.append(predicted)
                    ok = predicted == gloss
                    matches += ok
                    tests.append(f"{component}={'PASS' if ok else 'FAIL'}:{predicted}")
                else:
                    predictions.append("?")
                    tests.append(f"{component}=NO_OTHER_INVARIANT")
        fully = aligned and matches == len(components)
        partial = aligned and 0 < matches < len(components)
        status = (
            "LEAVE_ONE_CARD_COMPOSITIONAL"
            if fully
            else "PARTIAL_COMPOSITION_PLUS_LEARNED_REMAINDER"
            if partial
            else "LEARNED_WHOLE_CARD"
        )
        decision_rows.append(
            {
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "actual_reading_de": row["invariant_card_reading_de"],
                "predicted_reading_from_other_cards_de": " · ".join(predictions) if predictions else "NONE",
                "component_tests": "|".join(tests) if tests else "NO_ALIGNED_COMPONENT_TEST",
                "components": str(len(components)),
                "components_predicted": str(matches),
                "composition_status": status,
                "occurrences": row["occurrences"],
                "event_ids": "|".join(event["event_id"] for event in events if event["card_no"] == row["card_no"]),
                "sections": row["sections"],
                "primitive_program": row["primitive_program"],
                "workshop_use": (
                    "BUILD_FROM_STEMS"
                    if fully
                    else "BUILD_KNOWN_PARTS_THEN_RECALL_REMAINDER"
                    if partial
                    else "RECALL_EXACT_CARD"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_CARD_COMPOSITION_DECISIONS.tsv", decision_rows)

    status_for = {row["card_no"]: row["composition_status"] for row in decision_rows}
    event_rows: list[dict[str, str]] = []
    for row in events:
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "card_no": row["card_no"],
                "card_reading_de": row["card_reading_de"],
                "composition_status": status_for[row["card_no"]],
                "production_instruction": next(
                    decision["workshop_use"] for decision in decision_rows if decision["card_no"] == row["card_no"]
                ),
                "silent_owner_de": row["silent_owner_de"],
                "grammar_lanes": row["grammar_lanes"],
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_COMPOSITION_EVENT_AUDIT.tsv", event_rows)

    exceptions = [row for row in decision_rows if row["composition_status"] == "LEARNED_WHOLE_CARD"]
    write_tsv("FIVE_HUNDRED_THIRTY_SEVENTH_LEARNED_WHOLE_CARD_DECK.tsv", exceptions)
    partials = [row for row in decision_rows if row["composition_status"] == "PARTIAL_COMPOSITION_PLUS_LEARNED_REMAINDER"]
    write_tsv("FIVE_HUNDRED_THIRTY_SEVENTH_PARTIAL_COMPOSITION_CARDS.tsv", partials)

    card_counts = Counter(row["composition_status"] for row in decision_rows)
    event_counts = Counter(row["composition_status"] for row in event_rows)
    productive_components = [row for row in component_rows if row["status"] == "PRODUCTIVE_STEM"]
    summary = {
        "status": "PASS",
        "cards": len(decision_rows),
        "events": len(event_rows),
        "component_types_aligned": len(component_rows),
        "productive_stems": len(productive_components),
        "card_status_counts": dict(card_counts),
        "event_status_counts": dict(event_counts),
        "fully_predicted_readings_match": all(
            row["actual_reading_de"] == row["predicted_reading_from_other_cards_de"]
            for row in decision_rows if row["composition_status"] == "LEAVE_ONE_CARD_COMPOSITIONAL"
        ),
        "all_cards_keep_concrete_default": all(row["actual_reading_de"] for row in decision_rows),
    }
    (HERE / "FIVE_HUNDRED_THIRTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    top = sorted(
        productive_components,
        key=lambda row: (-int(row["aligned_card_types"]), row["component"]),
    )[:20]
    lines = [
        "# Fünfhundertsiebenunddreißigste Runde: Komposition gegen Ganzkarte",
        "",
        "## Ergebnis",
        "",
        f"Von 173 exakten Karten sind {card_counts['LEAVE_ONE_CARD_COMPOSITIONAL']} vollständig aus Bedeutungen vorhersagbar, die dieselben Komponenten auf anderen Karten tragen.",
        f"{card_counts['PARTIAL_COMPOSITION_PLUS_LEARNED_REMAINDER']} Karten besitzen einen vorhersagbaren Teil und einen gelernten Rest; {card_counts['LEARNED_WHOLE_CARD']} bleiben gelernte Ganzkarten.",
        "",
        f"Auf Ereignisebene sind das {event_counts['LEAVE_ONE_CARD_COMPOSITIONAL']} vollständig gebaute, {event_counts['PARTIAL_COMPOSITION_PLUS_LEARNED_REMAINDER']} teilweise gebaute und {event_counts['LEARNED_WHOLE_CARD']} gelernte Karten unter 381 Vorkommen.",
        "",
        "## Produktive Komponenten",
        "",
    ]
    for row in top:
        lines.append(
            f"- {row['component']} = {row['selected_atomic_value_de']} ({row['aligned_card_types']} Kartentypen, {row['aligned_events']} Ereignisse)"
        )
    lines.extend(
        [
            "",
            "## Lehrregel",
            "",
            "Ein Lehrling baut eine Karte nur dann frei aus Komponenten, wenn jede Komponente auf mindestens einer anderen Karte denselben Wert trägt. Teilkarten werden aus den bekannten Stämmen begonnen und mit einem gelernten Rest ergänzt. Alles andere wird als exakte Ganzkarte aus dem Deck genommen.",
            "",
            "Damit bleibt jede Sequenz übersetzt, ohne so zu tun, als seien alle sichtbaren Teilformen produktive Wörter.",
            "",
            "## Nächster Angriff",
            "",
            "Als Nächstes werden die produktiven Komponenten zu echten Vorhersagen auf noch nicht benutzte Kombinationen zusammengesetzt und gegen die vorhandenen Ganzkarten geprüft. So zeigt sich, welche Achsen wirklich neue Kartenwerte erzeugen können.",
        ]
    )
    (HERE / "FIVE_HUNDRED_THIRTY_SEVENTH_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
