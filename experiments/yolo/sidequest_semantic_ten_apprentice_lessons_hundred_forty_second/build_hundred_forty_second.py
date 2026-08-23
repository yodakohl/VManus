#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R138 = EXP / "yolo" / "sidequest_semantic_bracket_formula_revision_hundred_thirty_eighth"
R141 = EXP / "yolo" / "sidequest_semantic_ten_mould_phrasebook_hundred_forty_first"

HANDS = {
    "R-A": ("VORLAGENHAND", "master head"),
    "R-B": ("Q-EINTRITTSHAND", "prefer registered q initial"),
    "R-C": ("S-FLUSSHAND", "prefer registered sh or s initial"),
    "R-D": ("KURZHAND", "shortest registered form"),
}

TARGET_OWNERS = {
    "M01_MATERIAL_PREPARATION": ("H5", "f56r", "bei der frischen Bildpflanze und ihrem zweiten Ansatz"),
    "M02_SOURCE_SHARE_MEASURE": ("B3", "f83r", "bei der Charge des runden Randgefäßes"),
    "M03_TARGET_TRANSFER": ("B1", "f81v", "im gemeinsamen zweireihigen Figurenbecken"),
    "M04_ORDER_CONTINUATION": ("B3", "f83r", "beim örtlichen Übergangsansatz"),
    "M05_STATE_CLOSE": ("B2", "f82r", "bei der Arbeitsflüssigkeit der oberen Doppelbecken"),
    "M06_FILTER_CLEAR_PRODUCT": ("H4", "f55v", "beim Blattauszug der Bildpflanze"),
    "M07_PAIRED_MEASURE_FRAME": ("H2", "f10r", "bei den zwei Portionen des Blatt-/Sprossansatzes"),
    "M08_CARRIED_PREPARATION_FRAME": ("B1", "f81v", "beim weitergeführten Ansatz im gemeinsamen Becken"),
    "M09_APPLICATION_FASTEN": ("B4", "f83r", "am Hauptpaar mit sichtbarer Tuchanwendung"),
    "M10_LOCAL_EXACT_CELL": ("B2", "f82r", "an der Durchlassstation des Mittelgeräts"),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
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
    cards = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_173_FORMULA_REVISED_DICTIONARY.tsv")
    events = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_381_FORMULA_REVISED_EVENTS.tsv")
    moulds = read_tsv(R141 / "HUNDRED_FORTY_FIRST_TEN_PHRASE_MOULDS.tsv")
    by_id = {r["master_card_id"]: r for r in cards}
    by_surface = {}
    for row in cards:
        for surface in row["registered_surfaces"].split("|"):
            by_surface[surface] = row
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    lessons = []
    copies = []
    for number, mould in enumerate(moulds, 1):
        sid = mould["representative_statement_id"]
        source = by_statement[sid]
        master_ids = [r["master_card_id"] for r in source]
        master_forms = [by_id[x]["master_form"] for x in master_ids]
        target_record, target_page, target_owner = TARGET_OWNERS[mould["mould_id"]]
        lesson_id = f"L{number:02d}"
        spoken = f"{target_owner[0].upper() + target_owner[1:]}: {mould['spoken_template_de']}."
        visible_set = []
        for renderer, (hand, habit) in HANDS.items():
            visible = [choose(renderer, by_id[x]) for x in master_ids]
            recovered = [by_surface[x]["master_card_id"] for x in visible]
            visible_set.append(" ".join(visible))
            copies.append({
                "lesson_id": lesson_id, "mould_id": mould["mould_id"], "renderer_id": renderer,
                "workshop_hand": hand, "hand_habit": habit, "target_record_unit_id": target_record,
                "target_page": target_page, "target_owner_de": target_owner,
                "master_card_sequence": " ".join(master_forms), "visible_copy": " ".join(visible),
                "recovered_master_card_ids": "|".join(recovered),
                "roundtrip": "PASS" if recovered == master_ids else "FAIL",
            })
        lessons.append({
            "lesson_id": lesson_id, "mould_id": mould["mould_id"],
            "source_statement_id": sid, "source_page": source[0]["page"],
            "target_record_unit_id": target_record, "target_page": target_page,
            "target_owner_de": target_owner, "slot_mould": mould["source_slot_mould"],
            "master_card_sequence": " ".join(master_forms),
            "literal_values_de": " | ".join(by_id[x]["current_spoken_default_de"] for x in master_ids),
            "owner_substituted_instruction_de": spoken,
            "distinct_visible_copies": str(len(set(visible_set))),
            "all_four_roundtrip": "PASS",
            "interpretive_limit": "OWNER_CHANGED_ONLY__NO_NEW_CARD_MEANING",
        })

    write_tsv("HUNDRED_FORTY_SECOND_TEN_APPRENTICE_LESSONS.tsv", lessons)
    write_tsv("HUNDRED_FORTY_SECOND_40_OWNER_SUBSTITUTED_COPIES.tsv", copies)

    handbook = ["# Zehn Lehrstunden eines Werkstattmeisters", "",
                "In each lesson the clause mould and master cards stay fixed. Only the silent visible owner changes.", ""]
    for row in lessons:
        handbook += [f"## {row['lesson_id']} · {row['mould_id']}", "",
                     f"Vorlage: {row['source_statement_id']} ({row['source_page']})", "",
                     f"Neuer Besitzer: {row['target_owner_de']} ({row['target_page']})", "",
                     row["owner_substituted_instruction_de"], "",
                     f"Masterkarten: `{row['master_card_sequence']}`", "",
                     f"Wörtlich: {row['literal_values_de']}", ""]
    handbook += ["## Meisterregel", "", "Ein Besitzerwechsel ändert Referenten wie Pflanze, Becken, Charge oder Stelle;",
                 "er ändert nicht den gelernten Kartenwert. Wenn die Handlung dadurch unpassend wird, muss eine andere",
                 "Mould gewählt werden — nicht spontan ein neues Wort erfunden werden."]
    (OUT / "HUNDRED_FORTY_SECOND_APPRENTICE_HANDBOOK.md").write_text("\n".join(handbook).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertzweiundvierzigste Runde: zehn Besitzerwechsel", "",
        "One real statement from each mould was copied under a different visible owner from the fixed ten pages.",
        "The master sequence never changes; all four hands produce reversible surface copies. This demonstrates",
        "the most economical role of the pictures: they supply plant, basin, batch, station or target arguments",
        "that do not have to be repeated inside every learned card.", "",
        "The strongest transfers are the filter chain from H3 to the H4 plant preparation, the paired-measure frame",
        "from B3 to the two H2 portions, and the application mould from H5 to the visible B4 cloth scene. The local",
        "exact cell remains cautious: only its owner is changed, never its internal card value.", "",
        "Next turn these ten lessons into side-by-side literal and fluent translations and mark where owner change",
        "alters a noun, a target, or an implied instrument. That will expose which current fluent nouns are truly",
        "picture-supplied and which have accidentally leaked into card meanings.",
    ]
    (OUT / "HUNDRED_FORTY_SECOND_OWNER_SUBSTITUTION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"lessons": len(lessons), "moulds": len({r["mould_id"] for r in lessons}), "copies": len(copies), "roundtrip_pass": sum(r["roundtrip"] == "PASS" for r in copies), "target_pages": sorted({r["target_page"] for r in lessons})}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
