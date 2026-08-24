#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P467 = ROOT / "experiments/yolo/sidequest_semantic_astro_nomenclator_closure_four_hundred_sixty_seventh"
P463 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third"

CARDS = P463 / "FOUR_HUNDRED_SIXTY_THIRD_173_CARD_COMMON_ROOT_DICTIONARY.tsv"
EVENTS = P463 / "FOUR_HUNDRED_SIXTY_THIRD_381_PROSE_EVENT_COMMON_ROOTS.tsv"
STATEMENTS = P463 / "FOUR_HUNDRED_SIXTY_THIRD_116_PROSE_STATEMENT_DUAL_READINGS.tsv"
COMPONENTS = P463 / "FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv"
ASTRO = P467 / "FOUR_HUNDRED_SIXTY_SEVENTH_395_ASTRO_GROUP_CLOSED_NOMENCLATOR.tsv"
LEDGER = P467 / "FOUR_HUNDRED_SIXTY_SEVENTH_776_GROUP_COMPLETE_APPRENTICE_LEDGER.tsv"
DICTIONARY = P467 / "FOUR_HUNDRED_SIXTY_SEVENTH_52_UNIT_APPRENTICE_DICTIONARY.tsv"

REVISIONS = {
    "R": ("abkuehlen", "senken", "abkuehlen", "eine Lage oder Stufe senken"),
    "CHK": ("waermen", "anheben", "waermen", "eine Lage oder Stufe anheben"),
    "CKHE": ("seihen", "trennen", "seihen", "Eintraege oder Bereiche trennen"),
    "CHEO": ("Auszug", "Entnahme", "Pflanzenauszug", "aus einem Feld entnommener Wert"),
    "CH": ("abziehen", "entnehmen", "Fluessigkeit abziehen", "einen Eintrag entnehmen"),
    "CKH": ("Durchlass", "Durchgang", "Rohr- oder Seihdurchlass", "Diagrammdurchgang"),
    "LS": ("abfuehren", "hinausfuehren", "Fluessigkeit abfuehren", "aus einem Bereich hinausfuehren"),
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


def revise(text: str) -> str:
    output = text
    for _, (old, new, _, _) in REVISIONS.items():
        output = output.replace(old, new).replace(old.capitalize(), new.capitalize())
    return output


def main() -> None:
    cards = []
    changed_ids = set()
    for row in read(CARDS):
        out = dict(row)
        out["previous_atomic_value_de"] = row["small_value_de"]
        out["small_value_de"] = revise(row["small_value_de"])
        out["common_action_revision"] = "YES" if out["small_value_de"] != row["small_value_de"] else "NO"
        if out["common_action_revision"] == "YES":
            changed_ids.add(row["joint_tuple_id"])
        cards.append(out)
    write("FOUR_HUNDRED_SIXTY_EIGHTH_173_CARD_COMMON_ACTION_DICTIONARY.tsv", cards)
    card_by_id = {row["joint_tuple_id"]: row for row in cards}

    events = []
    for row in read(EVENTS):
        out = dict(row)
        out["previous_atomic_value_de"] = row["small_value_de"]
        out["small_value_de"] = card_by_id[row["joint_tuple_id"]]["small_value_de"]
        out["common_action_revision"] = "YES" if row["joint_tuple_id"] in changed_ids else "NO"
        events.append(out)
    write("FOUR_HUNDRED_SIXTY_EIGHTH_381_PROSE_EVENT_COMMON_ACTIONS.tsv", events)

    old_statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        old = old_statements[statement_id]
        statements.append({
            "statement_id": statement_id,
            "register": rows[0]["register"],
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "owner_zones": old["owner_zones"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "common_action_atomic_reading_de": "; ".join(row["small_value_de"] for row in rows) + ".",
            "wet_context_expansion_de": old["wet_context_expansion_de"],
            "revised_events": sum(row["common_action_revision"] == "YES" for row in rows),
        })
    write("FOUR_HUNDRED_SIXTY_EIGHTH_116_PROSE_STATEMENT_COMMON_ACTIONS.tsv", statements)

    components = []
    for row in read(COMPONENTS):
        out = dict(row)
        out["previous_atomic_value_de"] = row["value_de"]
        if row["component"] in REVISIONS:
            out["value_de"] = REVISIONS[row["component"]][1]
            out["wet_context_expansion_de"] = REVISIONS[row["component"]][2]
            out["astro_context_expansion_de"] = REVISIONS[row["component"]][3]
            out["common_action_revision"] = "YES"
        else:
            out["wet_context_expansion_de"] = row["value_de"]
            out["astro_context_expansion_de"] = row["value_de"]
            out["common_action_revision"] = "NO"
        components.append(out)
    write("FOUR_HUNDRED_SIXTY_EIGHTH_35_COMPONENT_COMMON_ACTION_MANUAL.tsv", components)

    astro = []
    for row in read(ASTRO):
        out = dict(row)
        out["previous_atomic_value_de"] = row["atomic_common_root_value_de"]
        out["atomic_common_root_value_de"] = revise(row["atomic_common_root_value_de"])
        out["common_action_revision"] = "YES" if out["atomic_common_root_value_de"] != row["atomic_common_root_value_de"] else "NO"
        astro.append(out)
    write("FOUR_HUNDRED_SIXTY_EIGHTH_395_ASTRO_GROUP_COMMON_ACTIONS.tsv", astro)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in by_locus.items():
        whole = sum(row["nomenclator_resolution"] == "MEMORIZED_WHOLE_NAME" for row in rows)
        loci.append({
            "locus_row": len(loci) + 1,
            "diagram_id": rows[0]["diagram_id"],
            "page": rows[0]["page"],
            "locus": locus,
            "local_namespace": rows[0]["local_namespace"],
            "groups": len(rows),
            "group_serials": "|".join(row["group_serial"] for row in rows),
            "common_action_reading_de": "; ".join(row["atomic_common_root_value_de"] for row in rows),
            "revised_groups": sum(row["common_action_revision"] == "YES" for row in rows),
            "memorized_whole_names": whole,
            "orientation": "UNSPECIFIED",
            "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_EIGHTH_142_ASTRO_LOCUS_COMMON_ACTIONS.tsv", loci)

    astro_by_serial = {int(row["group_serial"]): row for row in astro}
    event_by_id = {row["event_id"]: row for row in events}
    ledger = []
    for row in read(LEDGER):
        out = dict(row)
        if row["domain"] == "PROSE":
            event = event_by_id[row["unified_id"].split(":")[1]]
            out["atomic_default_de"] = event["small_value_de"]
        else:
            group = astro_by_serial[int(row["unified_id"].split(":")[1])]
            out["atomic_default_de"] = group["atomic_common_root_value_de"]
            out["context_expansion_de"] = group["atomic_common_root_value_de"]
        ledger.append(out)
    write("FOUR_HUNDRED_SIXTY_EIGHTH_776_GROUP_COMMON_ACTION_LEDGER.tsv", ledger)

    dictionary = []
    for row in read(DICTIONARY):
        out = dict(row)
        out["previous_default_value_de"] = row["default_value_de"]
        out["default_value_de"] = revise(row["default_value_de"])
        out["common_action_revision"] = "YES" if out["default_value_de"] != row["default_value_de"] else "NO"
        dictionary.append(out)
    write("FOUR_HUNDRED_SIXTY_EIGHTH_52_UNIT_COMMON_ACTION_DICTIONARY.tsv", dictionary)

    revision_rows = []
    for component, (old, new, wet, sky) in REVISIONS.items():
        revision_rows.append({
            "component": component,
            "old_narrow_default_de": old,
            "new_common_action_de": new,
            "wet_context_expansion_de": wet,
            "astro_context_expansion_de": sky,
            "prose_card_types": sum(component in row["component_parse"].replace("WHOLE[", "").replace("]", "").split("+") for row in cards),
            "prose_events": sum(component in row["component_parse"].replace("WHOLE[", "").replace("]", "").split("+") for row in events),
            "astro_groups": sum(component in row["selected_component_parse"].split("+") for row in astro),
        })
    write("FOUR_HUNDRED_SIXTY_EIGHTH_SEVEN_COMMON_ACTION_REVISIONS.tsv", revision_rows)

    summary = {
        "status": "PASS",
        "revisions": len(revision_rows),
        "changed_card_types": len(changed_ids),
        "changed_prose_events": sum(row["common_action_revision"] == "YES" for row in events),
        "changed_prose_statements": sum(int(row["revised_events"]) > 0 for row in statements),
        "changed_astro_groups": sum(row["common_action_revision"] == "YES" for row in astro),
        "changed_astro_loci": sum(int(row["revised_groups"]) > 0 for row in loci),
        "unified_groups": len(ledger),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
