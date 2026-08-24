#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_biological_whole_card_audit_four_hundred_forty_ninth"

COMPONENTS = {
    "AIIN": ("ARGUMENT", "Mass"), "AIN": ("ARGUMENT", "Portion"), "AIR": ("ARGUMENT", "Wasser"),
    "AL": ("ARGUMENT", "Stelle"), "AR": ("ARGUMENT", "Quelle oder Vorrat"), "CH": ("OPERATION", "abziehen"),
    "CHD": ("OPERATION", "umsetzen"), "CHK": ("OPERATION", "waermen"), "CKH": ("OPERATION", "Durchlass"),
    "CKHE": ("OPERATION", "seihen"), "CTH": ("STATE", "bereit"), "DY": ("ENDPOINT", "Schluss"),
    "E": ("GRADE", "kurz"), "EE": ("GRADE", "laenger"), "EEE": ("GRADE", "vollstaendig"),
    "IIN": ("ARGUMENT", "Sollstufe"), "K": ("OPERATION", "zufuehren"), "L": ("OPERATION", "fuehren"),
    "LDDY": ("ENDPOINT", "befestigen und schliessen"), "LS": ("OPERATION", "abfuehren"),
    "LSH": ("OPERATION", "Waschgang"), "O": ("FRAME", "Arbeitszustand"), "OK": ("FRAME", "ansetzen"),
    "OL": ("FRAME", "fortsetzen"), "OR": ("ARGUMENT", "Ansatz"), "OT": ("FRAME", "danach oder naechster"),
    "P": ("OPERATION", "hinein"), "R": ("OPERATION", "abkuehlen"), "SH": ("OPERATION", "halten"),
    "SHED": ("OPERATION", "absetzen"), "SOLK": ("OPERATION", "auffangen"), "T": ("OPERATION", "fuellen"),
    "Y": ("ARGUMENT", "dieser laufende Posten"),
}

VALUE_REVISIONS = {
    "259b2b3b0bf859882e2c": "umsetzen; Schluss",
    "5e8441397e7c0faf042b": "dies umsetzen",
    "7d2404c835b10a2c06af": "Wasser in Gang setzen",
    "b154ff779abe5f196c80": "Wasser weiterfuehren",
    "8aedd154964a78e555d6": "Wasserlauf schliessen",
    "4de12cf322dfb76ded1e": "danach umsetzen; Schluss",
    "d788d8d72d41b25a3c71": "Ansatz an der Stelle abkuehlen",
    "98bdc4244c84cbef3321": "an der Stelle kurz abkuehlen",
    "9247e38d29c79a0d2fa5": "dies vollstaendig fuellen",
}

DEMOTED_WHOLE = "fcc1deda9e24ec268eb0"

COMPOSITION_OVERRIDE = {
    "bc4f1f5c006c74a4d26d": "SHED+DY",
    "97ddca78c9ebcc956d04": "L+AL+OR",
    "3e9c7f217843b588489d": "R+AL+Y",
    "348e81ba084c5acdb32b": "SH+E+CTH+CHD+Y",
    "a7af89ab31ce5e247395": "T+E+Y",
    "80ebbbbf238eee9f0aef": "T+Y",
    "d788d8d72d41b25a3c71": "AL+R+OR",
    "98bdc4244c84cbef3321": "R+SH+E+AL",
    "9247e38d29c79a0d2fa5": "EEE+T+Y",
    "5eff216ba51fbfb21f22": "LS",
}

FLUENT = {
    "B1-S002": "Bemessen, Wasser zufuehren und an die Stelle setzen; denselben Posten mit einer und einer weiteren Portion fortsetzen; weiter abkuehlen, weiterfuehren und einen weiteren Ansatz zugeben; kurz an der Durchlassstelle halten, auf Mass bringen, laenger an der Stelle halten, nochmals bemessen, durchfuehren, umsetzen und schliessen.",
    "B2-S001": "Umsetzen und schliessen.",
    "B2-S017": "An der Stelle kurz abkuehlen und dort schliessen.",
    "B3-S005": "Umsetzen und schliessen.",
    "B3-S006": "Dies umsetzen, an die Stelle setzen, weiterfuehren und schliessen.",
    "B3-S014": "Wasser in Gang setzen, laenger absetzen und schliessen.",
    "B3-S022": "Danach umsetzen und schliessen.",
    "B3-S024": "Umsetzen und schliessen.",
    "B3-S026": "Laenger aus der Quelle fuehren, das Abfuehrmass setzen, dies umsetzen, eine Portion zugeben, bereitstellen, den Ansatz an der Stelle abkuehlen, laenger auffangen und schliessen.",
    "B3-S029": "Fortsetzen, dies vollstaendig fuellen, kurz ansetzen und schliessen.",
    "B3-S030": "Dies verwenden, auf Mass bringen, Wasser weiterfuehren, danach umsetzen und schliessen.",
    "B4-S014": "Den Ansatz und diesen Posten kurz durchfuehren und den Wasserlauf schliessen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def collect_compositions() -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}

    def add(joint_id: str, composition: str, source: str) -> None:
        result[joint_id] = (composition, source)

    b1 = ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv"
    for row in read(b1):
        if row["drawer"] == "PRODUCTIVE_COMPOSITION":
            add(row["joint_tuple_id"], row["construction"], "B1_DICTIONARY")

    sources = (
        ("B2_DIRECTION", ROOT / "experiments/yolo/sidequest_semantic_b2_directional_composition_four_hundred_thirty_sixth/FOUR_HUNDRED_THIRTY_SIXTH_SEVEN_NEW_COMPOSITIONS.tsv"),
        ("B2_LIQUID", ROOT / "experiments/yolo/sidequest_semantic_b2_liquid_application_four_hundred_thirty_eighth/FOUR_HUNDRED_THIRTY_EIGHTH_FOUR_REVISIONS.tsv"),
        ("B2_FINAL", ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FIVE_FINAL_COMPOSITIONS.tsv"),
        ("B3", ROOT / "experiments/yolo/sidequest_semantic_b3_productive_completion_four_hundred_forty_first/FOUR_HUNDRED_FORTY_FIRST_SEVENTEEN_NEW_COMPOSITIONS.tsv"),
        ("B4", ROOT / "experiments/yolo/sidequest_semantic_b4_productive_completion_four_hundred_forty_fourth/FOUR_HUNDRED_FORTY_FOURTH_THIRTEEN_NEW_COMPOSITIONS.tsv"),
        ("B56", ROOT / "experiments/yolo/sidequest_semantic_b5_b6_dictionary_four_hundred_forty_sixth/FOUR_HUNDRED_FORTY_SIXTH_SIX_NEW_COMPOSITIONS.tsv"),
        ("PASS448", ROOT / "experiments/yolo/sidequest_semantic_biological_local_cleanup_four_hundred_forty_eighth/FOUR_HUNDRED_FORTY_EIGHTH_24_PROMOTED_COMPOSITIONS.tsv"),
        ("PASS449", ROOT / "experiments/yolo/sidequest_semantic_biological_whole_card_audit_four_hundred_forty_ninth/FOUR_HUNDRED_FORTY_NINTH_SEVEN_PROMOTIONS.tsv"),
    )
    for source, path in sources:
        for row in read(path):
            add(row["joint_tuple_id"], row["composition"], source)

    grade = ROOT / "experiments/yolo/sidequest_semantic_b2_grade_ladder_four_hundred_thirty_seventh/FOUR_HUNDRED_THIRTY_SEVENTH_B2_GRADE_LADDER.tsv"
    for row in read(grade):
        if row["source"] == "B2_NEW":
            add(row["joint_tuple_id"], row["composition"], "B2_GRADE")
    add("c1913ec4ff84148da6d3", "SH+E+CKH+Y", "B2_PREDICTED_SEED")
    add("9247e38d29c79a0d2fa5", "EEE+T+Y", "PASS450_T_REPAIR")
    return result


def normalize(joint_id: str, composition: str) -> list[str]:
    composition = COMPOSITION_OVERRIDE.get(joint_id, composition)
    replacements = {"CHED": "CHD", "CHY": "Y", "CHEY": "Y", "OLK": "SOLK", "RSHE": "R+SH+E", "L_TRANSFER": "L", "RAL": "R+AL"}
    ignored_renderer_tokens = {"D", "S", "CHE"}
    result: list[str] = []
    for token in composition.split("+"):
        for normalized in replacements.get(token, token).split("+"):
            if normalized not in ignored_renderer_tokens:
                result.append(normalized)
    return result


def main() -> None:
    events = read(PREV / "FOUR_HUNDRED_FORTY_NINTH_281_EVENT_EDITION.tsv")
    for row in events:
        if row["joint_tuple_id"] in VALUE_REVISIONS:
            row["small_value_de"] = VALUE_REVISIONS[row["joint_tuple_id"]]
        if row["joint_tuple_id"] == DEMOTED_WHOLE:
            row["union_drawer"] = "RECORD_LOCAL_LEARNED_WHOLE_CARD"
    write("FOUR_HUNDRED_FIFTIETH_281_EVENT_EDITION.tsv", events)

    values = {row["joint_tuple_id"]: row["small_value_de"] for row in events}
    dictionary = read(PREV / "FOUR_HUNDRED_FORTY_NINTH_124_CARD_DICTIONARY.tsv")
    for row in dictionary:
        row["small_value_de"] = values[row["joint_tuple_id"]]
        if row["joint_tuple_id"] == DEMOTED_WHOLE:
            row["union_drawer"] = "RECORD_LOCAL_LEARNED_WHOLE_CARD"
            row["origin_drawer"] = "PASS450_DEMOTED_UNIQUE_AIIIN_SIGN"
    write("FOUR_HUNDRED_FIFTIETH_124_CARD_DICTIONARY.tsv", dictionary)

    event_by_id = {row["event_id"]: row for row in events}
    statements = read(PREV / "FOUR_HUNDRED_FORTY_NINTH_97_STATEMENT_EDITION.tsv")
    for row in statements:
        statement_events = [event_by_id[event_id] for event_id in row["event_ids"].split("|")]
        row["card_sequence_de"] = " > ".join(event["small_value_de"] for event in statement_events)
        if row["statement_id"] in FLUENT:
            row["continuous_reading_de"] = FLUENT[row["statement_id"]]
    write("FOUR_HUNDRED_FIFTIETH_97_STATEMENT_EDITION.tsv", statements)

    compositions = collect_compositions()
    product_ids = {row["joint_tuple_id"] for row in dictionary if row["union_drawer"] == "PRODUCTIVE_COMPOSITION"}
    if product_ids != set(compositions) - {DEMOTED_WHOLE}:
        raise ValueError("composition coverage mismatch")

    component_counts: Counter[str] = Counter()
    generator = []
    card_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    for joint_id in sorted(product_ids, key=lambda item: int(card_by_id[item]["card_no"][4:])):
        source_composition, source = compositions[joint_id]
        tokens = normalize(joint_id, source_composition)
        unknown = [token for token in tokens if token not in COMPONENTS]
        if unknown:
            raise ValueError(f"unknown components for {joint_id}: {unknown}")
        component_counts.update(set(tokens))
        roles = [COMPONENTS[token][0] for token in tokens]
        generator.append({
            "card_no": card_by_id[joint_id]["card_no"], "joint_tuple_id": joint_id,
            "surfaces": card_by_id[joint_id]["surfaces"], "events": card_by_id[joint_id]["events"],
            "source_composition": source_composition, "normalized_components": "+".join(tokens),
            "slot_signature": ">".join(roles), "endpoint": "CLOSED" if any(token in {"DY", "LDDY"} for token in tokens) else "OPEN",
            "small_value_de": card_by_id[joint_id]["small_value_de"], "composition_source": source,
            "licensed_by_manual": "YES",
        })
    write("FOUR_HUNDRED_FIFTIETH_117_PRODUCTIVE_CARD_GENERATOR.tsv", generator)

    component_rows = []
    for component, (role, value) in COMPONENTS.items():
        support = component_counts[component]
        component_rows.append({
            "component": component, "role": role, "value_de": value, "support_cards": support,
            "teaching_status": "LEARNED_BOUND_SIGN" if support == 1 else "RECURRING_COMPONENT",
        })
    write("FOUR_HUNDRED_FIFTIETH_33_COMPONENT_INVENTORY.tsv", component_rows)

    wholes = [row for row in dictionary if row["union_drawer"] != "PRODUCTIVE_COMPOSITION"]
    for row in wholes:
        row["teaching_rule"] = "MEMORIZE_EXACT_CARD"
    write("FOUR_HUNDRED_FIFTIETH_SEVEN_WHOLE_CARDS.tsv", wholes)

    repairs = []
    old_cards = {row["joint_tuple_id"]: row for row in read(PREV / "FOUR_HUNDRED_FORTY_NINTH_124_CARD_DICTIONARY.tsv")}
    for joint_id, new_value in VALUE_REVISIONS.items():
        repairs.append({
            "joint_tuple_id": joint_id, "surfaces": old_cards[joint_id]["surfaces"],
            "old_value_de": old_cards[joint_id]["small_value_de"], "new_value_de": new_value,
            "reason": "COMPONENT_INVARIANCE",
        })
    repairs.append({
        "joint_tuple_id": DEMOTED_WHOLE, "surfaces": old_cards[DEMOTED_WHOLE]["surfaces"],
        "old_value_de": old_cards[DEMOTED_WHOLE]["small_value_de"], "new_value_de": old_cards[DEMOTED_WHOLE]["small_value_de"],
        "reason": "UNIQUE_AIIIN_HAS_NO_PRODUCTIVE_SISTER_CARD",
    })
    write("FOUR_HUNDRED_FIFTIETH_TEN_REPAIRS.tsv", repairs)

    summary = {
        "status": "PASS", "cards": len(dictionary), "events": len(events), "statements": len(statements),
        "productive_cards": len(generator), "whole_cards": len(wholes), "components": len(component_rows),
        "recurring_components": sum(row["teaching_status"] == "RECURRING_COMPONENT" for row in component_rows),
        "learned_bound_signs": sum(row["teaching_status"] == "LEARNED_BOUND_SIGN" for row in component_rows),
        "productive_events": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in events),
        "whole_card_events": sum(row["union_drawer"] != "PRODUCTIVE_COMPOSITION" for row in events),
    }
    (HERE / "FOUR_HUNDRED_FIFTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
