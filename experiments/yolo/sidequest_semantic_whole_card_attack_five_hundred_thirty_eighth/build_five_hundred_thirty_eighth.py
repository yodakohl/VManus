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


OVERRIDES = {
    "PROC005": ("OS", "Arbeitsfach", "KEEP_WHOLE", "OS hat keine wiederkehrende innere Achse"),
    "PROC028": ("CFH+Y", "auswringen · dies", "PARTIAL", "Y ist der bekannte laufende Posten; CFH bleibt Fachstamm"),
    "PROC031": ("SH+EE+Y", "halten · länger · dies", "FULL", "cheey/shey ist dieselbe gradierte Haltekarte in vier Kontexten"),
    "PROC043": ("TALAM", "verwahren", "KEEP_WHOLE", "TALAM erscheint nur einmal und trägt keinen sicheren Schnitt"),
    "PROC045": ("CH+E+O+AR", "abziehen · kurz · Arbeitsgang · von dort", "FULL", "CHEO entfaltet exakt CH+E+O vor AR"),
    "PROC061": ("OK+CH+E+O", "ansetzen · abziehen · kurz · Arbeitsgang", "FULL", "dieselbe CHEO-Entfaltung nach OK"),
    "PROC099": ("SH+CKH+E+DY", "halten · Durchlass · kurz · Schluss", "FULL", "CKHE ist CKH+E zwischen SH und DY"),
    "PROC103": ("L+CKH+E+DY", "führen · Durchlass · kurz · Schluss", "FULL", "dieselbe CKH+E-Folge nach L"),
    "PROC115": ("LS", "fortsetzen", "KEEP_WHOLE", "LS ist ein einmaliges Fortsetzungszeichen"),
    "PROC124": ("CH+E+S", "abziehen · kurz · teilen", "PARTIAL", "CH+E ist bekannt; S ist der kleine Teilungsstamm"),
    "PROC155": ("OK+Y+LD+DY", "ansetzen · dies · befestigen · Schluss", "PARTIAL", "OK+Y und DY sind bekannt; LD bezeichnet Befestigen"),
    "PROC169": ("DA+IIN", "zweite · Sollstufe", "PARTIAL", "IIN ist Zielstufe; DA setzt die zweite Stufe"),
}


def main() -> None:
    base_cards = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_SEVENTY_THREE_COMMON_CARD_GRAMMAR.tsv")
    base_events = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")
    revised_cards: list[dict[str, str]] = []
    for row in base_cards:
        revised = dict(row)
        if row["card_no"] in OVERRIDES:
            parse, reading, _, _ = OVERRIDES[row["card_no"]]
            revised["component_parse"] = parse
            revised["invariant_card_reading_de"] = reading
        revised_cards.append(revised)

    evidence: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in revised_cards:
        components = row["component_parse"].split("+")
        glosses = row["invariant_card_reading_de"].split(" · ")
        if len(components) != len(glosses) or any(component.startswith("WHOLE[") for component in components):
            continue
        for component, gloss in zip(components, glosses):
            evidence[component][gloss].add(row["card_no"])

    decisions: list[dict[str, str]] = []
    for row in revised_cards:
        components = row["component_parse"].split("+")
        glosses = row["invariant_card_reading_de"].split(" · ")
        aligned = len(components) == len(glosses) and not any(component.startswith("WHOLE[") for component in components)
        predictions: list[str] = []
        tests: list[str] = []
        matches = 0
        if aligned:
            for component, gloss in zip(components, glosses):
                others = {
                    candidate
                    for candidate, card_ids in evidence[component].items()
                    if any(card_id != row["card_no"] for card_id in card_ids)
                }
                if len(others) == 1:
                    predicted = next(iter(others))
                    predictions.append(predicted)
                    matches += predicted == gloss
                    tests.append(f"{component}={'PASS' if predicted == gloss else 'FAIL'}:{predicted}")
                else:
                    predictions.append("?")
                    tests.append(f"{component}=LEARNED_ATOM")
        full = aligned and matches == len(components)
        partial = aligned and 0 < matches < len(components)
        status = "COMPOSITIONAL" if full else "PARTIAL_WITH_LEARNED_ATOM" if partial else "LEARNED_WHOLE_CARD"
        decisions.append(
            {
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "invariant_card_reading_de": row["invariant_card_reading_de"],
                "predicted_from_other_cards_de": " · ".join(predictions) if predictions else "NONE",
                "component_tests": "|".join(tests) if tests else "NO_ALIGNED_TEST",
                "composition_status": status,
                "occurrences": row["occurrences"],
                "sections": row["sections"],
                "records": row["records"],
                "primitive_program": row["primitive_program"],
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv", decisions)

    reanalysis: list[dict[str, str]] = []
    by_no = {row["card_no"]: row for row in decisions}
    base_by_no = {row["card_no"]: row for row in base_cards}
    for card_no, (parse, reading, intended, reason) in OVERRIDES.items():
        old = base_by_no[card_no]
        new = by_no[card_no]
        reanalysis.append(
            {
                "card_no": card_no,
                "surfaces": "|".join(
                    dict.fromkeys(
                        event["surface"]
                        for event in base_events
                        if event["card_no"] == card_no
                    )
                ),
                "old_parse": old["component_parse"],
                "new_parse": parse,
                "old_reading_de": old["invariant_card_reading_de"],
                "new_reading_de": reading,
                "intended_reanalysis": intended,
                "computed_status": new["composition_status"],
                "occurrences": old["occurrences"],
                "reason": reason,
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_EIGHTH_TWELVE_REMAINDER_REANALYSES.tsv", reanalysis)

    events: list[dict[str, str]] = []
    for row in base_events:
        decision = by_no[row["card_no"]]
        events.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "card_no": row["card_no"],
                "revised_card_reading_de": decision["invariant_card_reading_de"],
                "revised_component_parse": decision["component_parse"],
                "composition_status": decision["composition_status"],
                "silent_owner_de": row["silent_owner_de"],
                "primitive_program": row["primitive_program"],
            }
        )
    write_tsv("FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_EDITION.tsv", events)

    learned = [row for row in decisions if row["composition_status"] == "LEARNED_WHOLE_CARD"]
    partial = [row for row in decisions if row["composition_status"] == "PARTIAL_WITH_LEARNED_ATOM"]
    write_tsv("FIVE_HUNDRED_THIRTY_EIGHTH_THREE_TRUE_WHOLE_CARDS.tsv", learned)
    write_tsv("FIVE_HUNDRED_THIRTY_EIGHTH_FOUR_LEARNED_ATOM_CARDS.tsv", partial)

    card_counts = Counter(row["composition_status"] for row in decisions)
    event_counts = Counter(row["composition_status"] for row in events)
    summary = {
        "status": "PASS",
        "cards": len(decisions),
        "events": len(events),
        "reanalysed_cards": len(reanalysis),
        "card_status_counts": dict(card_counts),
        "event_status_counts": dict(event_counts),
        "true_whole_cards": [row["card_no"] for row in learned],
        "learned_atom_cards": [row["card_no"] for row in partial],
        "new_learned_atoms": {"CFH": "auswringen", "S": "teilen", "LD": "befestigen", "DA": "zweite"},
    }
    (HERE / "FIVE_HUNDRED_THIRTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
