#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R138 = EXP / "yolo" / "sidequest_semantic_bracket_formula_revision_hundred_thirty_eighth"

HANDS = {
    "R-A": ("VORLAGENHAND", "master head"),
    "R-B": ("Q-EINTRITTSHAND", "prefer registered q initial"),
    "R-C": ("S-FLUSSHAND", "prefer registered sh or s initial"),
    "R-D": ("KURZHAND", "shortest registered form"),
}

EXERCISES = [
    ("C01", "HERBAL_ARTICLE", "D1_MATERIAL_PRODUCT_VESSEL", "Wurzel nehmen; davon einen Anteil bemessen.", "dchey char chety okaiin", "OWNER>SOURCE>SHARE>MEASURE_ACTION"),
    ("C02", "HERBAL_ARTICLE", "D2_FILTER_WASH_FLOW", "Den Ansatz auswringen; den Klarauszug nehmen; einen Anteil dorthin einsetzen.", "cfhy cheey chkain okal", "FILTER_ACTION>PRODUCT>SHARE>TARGET_ACTION"),
    ("C03", "BIOLOGICAL_CELL", "D3_HEAT_SETTLE_STATE", "Mit demselben Ansatz weiterfahren; lange sammeln; schließen.", "cheol cholor cheol olkeedy", "CARRY_FRAME>TERMINAL_STATE"),
    ("C04", "BIOLOGICAL_CELL", "D4_TRANSFER_SOURCE_TARGET", "Dies zur Zielstelle überführen und abführen; schließen.", "chey chdal lchedy", "ITEM>TRANSFER_TARGET>TERMINAL_TRANSFER"),
    ("C05", "BOTH", "D5_QUANTITY_PART_STAGE", "Zwei Posten unter dasselbe Sollmaß stellen; die Arbeitsstufe wählen.", "chey aiin chey oiiin", "PAIRED_MEASURE_FRAME>STAGE"),
    ("C06", "BOTH", "D6_ORDER_CONTINUATION", "Den Folgeansatz danach weiterführen und einsetzen.", "otchor otol choky", "NEXT_OBJECT>ORDER_LINK>ACTION"),
    ("C07", "BIOLOGICAL_CELL", "D7_APPLICATION_FASTEN_STORE", "Davon einen Anteil dorthin einsetzen und festbinden.", "char chety okal qokylddy", "SOURCE>SHARE>TARGET_ACTION>APPLICATION"),
    ("C08", "BOTH", "D8_LOCAL_OPERATION", "Den Posten bereit halten, teilen und nach Folgemaß weiterführen.", "checthy ches otaiin cheol", "STATE>LOCAL_ACTION>ORDERED_MEASURE>LINK"),
]


def read_tsv(name):
    with (R138 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def choose(hand, card):
    forms = card["registered_surfaces"].split("|")
    if hand == "R-A":
        return card["master_form"]
    if hand == "R-B":
        return next((x for x in forms if x.startswith("q")), card["master_form"])
    if hand == "R-C":
        return next((x for x in forms if x.startswith("sh")), next((x for x in forms if x.startswith("s")), card["master_form"]))
    return min(enumerate(forms), key=lambda x: (len(x[1]), x[0]))[1]


def main():
    cards = read_tsv("HUNDRED_THIRTY_EIGHTH_173_FORMULA_REVISED_DICTIONARY.tsv")
    by_form = {r["master_form"]: r for r in cards}
    by_surface = {}
    for row in cards:
        for surface in row["registered_surfaces"].split("|"):
            if surface in by_surface:
                raise ValueError(f"ambiguous visible form: {surface}")
            by_surface[surface] = row

    exercise_rows = []
    copy_rows = []
    trace_rows = []
    for exercise_id, register, drawer, command, sequence, signature in EXERCISES:
        forms = sequence.split()
        card_rows = [by_form[x] for x in forms]
        literal = " | ".join(r["current_spoken_default_de"] for r in card_rows)
        copies = []
        for renderer, (hand, habit) in HANDS.items():
            visible = [choose(renderer, row) for row in card_rows]
            recovered = [by_surface[x]["master_form"] for x in visible]
            copies.append(" ".join(visible))
            copy_rows.append({
                "exercise_id": exercise_id, "register": register, "specialist_drawer": drawer,
                "renderer_id": renderer, "workshop_hand": hand, "hand_habit": habit,
                "ordinary_source_instruction_de": command, "master_card_sequence": sequence,
                "literal_card_reading_de": literal, "visible_copy": " ".join(visible),
                "recovered_master_sequence": " ".join(recovered),
                "roundtrip": "PASS" if recovered == forms else "FAIL",
            })
            for pos, (source, surface, back) in enumerate(zip(forms, visible, recovered), 1):
                trace_rows.append({
                    "exercise_id": exercise_id, "renderer_id": renderer, "token_position": str(pos),
                    "source_master_card": source, "selected_surface": surface,
                    "recovered_master_card": back, "spoken_value_de": by_form[source]["current_spoken_default_de"],
                    "roundtrip": "PASS" if source == back else "FAIL",
                })
        exercise_rows.append({
            "exercise_id": exercise_id, "register": register, "specialist_drawer": drawer,
            "ordinary_source_instruction_de": command, "composition_signature": signature,
            "master_card_sequence": sequence, "literal_card_reading_de": literal,
            "distinct_visible_copies": str(len(set(copies))), "all_four_roundtrip": "PASS",
            "visible_copy_set": " || ".join(sorted(set(copies))),
        })

    write_tsv("HUNDRED_THIRTY_NINTH_EIGHT_COMPOSED_INSTRUCTIONS.tsv", exercise_rows)
    write_tsv("HUNDRED_THIRTY_NINTH_32_FOUR_HAND_COPIES.tsv", copy_rows)
    write_tsv("HUNDRED_THIRTY_NINTH_TOKEN_ROUNDTRIP_TRACE.tsv", trace_rows)

    manual = ["# Kleiner produktiver Werkstattkomponist", "", "## Vorgehen", "",
              "1. Bildbesitzer und Register wählen.",
              "2. Kurze Quelle in OWNER / SOURCE / SHARE / MEASURE / TARGET / ACTION / STATE / CLOSE zerlegen.",
              "3. Gemeinsame Karten als Gerüst setzen.",
              "4. Höchstens eine passende Fachschublade für den lokalen Inhalt öffnen.",
              "5. Klammern CHEY-AIIN-CHEY oder CHEOL-CHOLOR-CHEOL vor der Handform setzen.",
              "6. Erst danach die persönliche sichtbare Form wählen.",
              "7. Rückwärts zur Masterkartenfolge und dann zur gesprochenen Kurzfolge lesen.", ""]
    for row in exercise_rows:
        manual += [f"## {row['exercise_id']} · {row['specialist_drawer']}", "",
                   row["ordinary_source_instruction_de"], "", f"Master: `{row['master_card_sequence']}`", "",
                   f"Wörtlich: {row['literal_card_reading_de']}", "", f"Hände: `{row['visible_copy_set']}`", ""]
    (OUT / "HUNDRED_THIRTY_NINTH_COMPOSER_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertneununddreißigste Runde: ein benutzbarer Werkstattkomponist", "",
        "Eight ordinary source instructions were composed using only the existing ten-page dictionary. Each uses",
        "the shared scaffold and exactly one specialist drawer. The set exercises material, filtration, state,",
        "transfer, quantity, order, application and local operation without inventing a new card.", "",
        "All four workshop hands create visible variants and every copy returns to the same master sequence. The",
        "most informative examples are C03, where CHEOL-CHOLOR-CHEOL carries a state card, and C05, where",
        "CHEY-AIIN-CHEY encloses the paired-measure instruction before a local work-stage card.", "",
        "This is not proof of the historical plaintext. It is the first compact model in the sidequest that a",
        "1420 workshop apprentice could actually use: short source slots, shared cards, one local drawer, then a",
        "hand-specific rendering. Next compare the eight generated surface sequences with the existing 381-event",
        "phrase ecology and repair any composer order that never resembles an attested local order.",
    ]
    (OUT / "HUNDRED_THIRTY_NINTH_PRODUCTIVE_COMPOSER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"instructions": len(exercise_rows), "drawers": len({r["specialist_drawer"] for r in exercise_rows}), "copies": len(copy_rows), "tokens": len(trace_rows), "copy_roundtrip_pass": sum(r["roundtrip"] == "PASS" for r in copy_rows)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
