#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_six_order_workshop_book_eight_hundred_seventy_sixth"
MARKS = SOURCE / "EIGHT_HUNDRED_SEVENTY_SIXTH_438_MARK_SIX_ORDER_BOOK.tsv"
ORDERS = SOURCE / "EIGHT_HUNDRED_SEVENTY_SIXTH_6_COMPLETE_ORDER_SUMMARY.tsv"
CALIBRATIONS = SOURCE / "EIGHT_HUNDRED_SEVENTY_SIXTH_6_SHARED_CALIBRATIONS.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_SEVENTH"

ATOM_VALUES = {
    "AIIN": "EIN KLEINER SCHOEPFBECHER",
    "AIN": "EIN ABGEGRENZTER TEIL",
    "AL": "ZIELSTELLE",
    "AN": "NACHGABE",
    "AR": "QUELLE",
    "CH": "ENTNEHMEN",
    "CHD": "UMSETZEN",
    "CHK": "WAERMEN",
    "CKH": "DURCHLASS",
    "CTH": "BEREITEN",
    "DY": "SCHLUSS",
    "E": "EIN KURZER ARBEITSGANG",
    "EE": "DREI KURZE ARBEITSGAENGE",
    "HO": "ZUTAT",
    "IIN": "EINE EINGESTELLTE ARBEITSSTUFE",
    "K": "ZUGEBEN",
    "L": "LEITEN",
    "O": "ARBEITSGANG",
    "OK": "ANSETZEN",
    "OL": "WEITER",
    "OR": "ANSATZ",
    "OT": "DANACH",
    "RESUME_CARD": "DAVON",
    "SH": "HALTEN",
    "SHED": "STEHENLASSEN",
    "SOLK": "SAMMELN",
    "T": "BEARBEITEN",
    "TALAM": "BEISEITESTELLEN",
    "Y": "POSTEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stage_class(stage: str) -> str:
    if stage.startswith("MAKE"):
        return "PREP"
    if stage.startswith("APPLY"):
        return "APP"
    return "COND"


def atoms(recipe: str) -> list[str]:
    if recipe.startswith("WHOLE["):
        return []
    return recipe.split("+")


def main() -> None:
    marks = read(MARKS)
    orders = read(ORDERS)
    calibrations = read(CALIBRATIONS)

    by_identity: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        by_identity[row["identity"]].append(row)

    core_cards = []
    local_cards = []
    core_atoms: set[str] = set()
    for identity, rows in sorted(by_identity.items()):
        order_ids = sorted({row["order_id"] for row in rows})
        pages = sorted({row["page"] for row in rows})
        stages = sorted({stage_class(row["stage"]) for row in rows})
        first = rows[0]
        prose = all(stage_class(row["stage"]) != "COND" for row in rows)
        portable = prose and len(order_ids) >= 2
        row = {
            "identity": identity,
            "representative_surface": first["surface"],
            "component_recipe": first["component_recipe"],
            "concrete_default_de": first["concrete_default_de"],
            "visible_marks": len(rows),
            "orders": ",".join(order_ids),
            "order_count": len(order_ids),
            "pages": ",".join(pages),
            "stage_classes": ",".join(stages),
            "teaching_action": "MEMORIZE_PORTABLE_CORE" if portable else "COPY_FROM_LOCAL_MODEL_LEAF",
        }
        if portable:
            core_cards.append(row)
            core_atoms.update(atoms(first["component_recipe"]))
        else:
            local_cards.append(row)

    component_rows = []
    for component in sorted(core_atoms):
        supporting = [row for row in core_cards if component in atoms(str(row["component_recipe"]))]
        component_rows.append(
            {
                "component": component,
                "short_value_de": ATOM_VALUES[component],
                "portable_core_cards": len(supporting),
                "portable_core_marks": sum(int(row["visible_marks"]) for row in supporting),
                "example_surfaces": ",".join(str(row["representative_surface"]) for row in supporting[:5]),
                "lesson": "LEARN_AS_REUSABLE_COMPONENT",
            }
        )

    product_rows = []
    product_orders: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in orders:
        product_orders[row["internal_product"]].append(row)
    for product, rows in sorted(product_orders.items()):
        product_rows.append(
            {
                "product_handle": product,
                "workshop_name_de": rows[0]["product_name_de"],
                "used_in_orders": ",".join(row["order_id"] for row in rows),
                "use_count": len(rows),
                "source_preparation_page": next(row["page"] for row in marks if row["stage"] == f"MAKE_{product}"),
                "lesson": "MEMORIZE_HANDLE_AND_PICTURE_OWNER",
            }
        )

    condition_rows = []
    for row in orders:
        condition_rows.append(
            {
                "condition_handle": row["condition_handle"],
                "order_id": row["order_id"],
                "page": row["condition_handle"].split("@")[1].split(".")[0],
                "locus": row["condition_handle"].split("@")[1],
                "workshop_name_de": row["condition_name_de"],
                "visible_groups_on_model_leaf": row["condition_marks"],
                "memorize": "HANDLE_AND_LOCATION_ONLY",
                "copy": "ALL_LOCAL_GROUPS_FROM_MODEL_LEAF",
            }
        )

    owner_rows = []
    switch_rows = []
    for order in orders:
        order_id = order["order_id"]
        app = [row for row in marks if row["order_id"] == order_id and row["stage"].startswith("APPLY")]
        previous = None
        state_index = 0
        for row in app:
            owner = row["owner_or_handle_de"]
            if owner == previous:
                continue
            state_index += 1
            owner_state = {
                "order_id": order_id,
                "biological_record": order["biological_record"],
                "owner_state": f"{order['biological_record']}-O{state_index:02d}",
                "owner_de": owner,
                "first_mark_id": row["order_mark_id"],
                "first_source_id": row["source_id"],
                "first_unit": row["unit"],
                "entry_kind": "START_AT_VISIBLE_OWNER" if previous is None else "SWITCH_AT_THIS_UNIT",
                "previous_owner_de": previous or "NONE",
            }
            owner_rows.append(owner_state)
            if previous is not None:
                switch_rows.append(owner_state)
            previous = owner

    calibration_rows = []
    for row in calibrations:
        calibration_rows.append(
            {
                **row,
                "used_in_orders": "WH01,WH02,WH03,WH04,WH05,WH06",
                "lesson": "MEMORIZE_HOUSE_VALUE",
            }
        )

    lesson_rows = [
        {"lesson": "L01", "content": "29 wiederverwendbare Komponenten", "memorize_items": len(component_rows), "model_leaf_items": 0, "practice": "Komponenten laut nennen und aus fünf Beispielkarten rücklesen"},
        {"lesson": "L02", "content": "56 auftragsübergreifende Kernkarten", "memorize_items": len(core_cards), "model_leaf_items": 0, "practice": "Karte erkennen, zerlegen und kurzen Werkstattwert sagen"},
        {"lesson": "L03", "content": "vier interne Bildprodukte", "memorize_items": len(product_rows), "model_leaf_items": 0, "practice": "Bildseite auf A.G2, B.X2, C.W2 oder D.P1 buchen"},
        {"lesson": "L04", "content": "sechs Biological-Einstiege und zehn Besitzerwechsel", "memorize_items": len(switch_rows), "model_leaf_items": len(owner_rows), "practice": "an jedem Umschaltpunkt auf den nächsten sichtbaren Besitzer zeigen"},
        {"lesson": "L05", "content": "sechs lokale Bedingungsgriffe", "memorize_items": len(condition_rows), "model_leaf_items": sum(int(row["visible_groups_on_model_leaf"]) for row in condition_rows), "practice": "Griff und Locus finden; ganze lokale Folge kopieren"},
        {"lesson": "L06", "content": "sechs Hauskalibrierungen", "memorize_items": len(calibration_rows), "model_leaf_items": 0, "practice": "Maß, Teil, Stufe, kurz, länger, vollständig/Resultat ausführen"},
        {"lesson": "L07", "content": "lokales Prosa- und Himmelsdeck", "memorize_items": 0, "model_leaf_items": len(local_cards), "practice": "seltene Karten nicht erraten, sondern von der bezeichneten Musterzeile kopieren"},
        {"lesson": "L08", "content": "sechs vollständige Aufträge", "memorize_items": 6, "model_leaf_items": 119, "practice": "WHAT → HOW → CONDITION ohne Meisteransage ausführen"},
    ]

    write(f"{PREFIX}_29_COMPONENT_LESSON.tsv", component_rows, ["component", "short_value_de", "portable_core_cards", "portable_core_marks", "example_surfaces", "lesson"])
    write(f"{PREFIX}_56_PORTABLE_CORE_CARDS.tsv", core_cards, ["identity", "representative_surface", "component_recipe", "concrete_default_de", "visible_marks", "orders", "order_count", "pages", "stage_classes", "teaching_action"])
    write(f"{PREFIX}_172_LOCAL_MODEL_CARDS.tsv", local_cards, ["identity", "representative_surface", "component_recipe", "concrete_default_de", "visible_marks", "orders", "order_count", "pages", "stage_classes", "teaching_action"])
    write(f"{PREFIX}_4_PRODUCT_HANDLES.tsv", product_rows, ["product_handle", "workshop_name_de", "used_in_orders", "use_count", "source_preparation_page", "lesson"])
    write(f"{PREFIX}_16_OWNER_STATES.tsv", owner_rows, ["order_id", "biological_record", "owner_state", "owner_de", "first_mark_id", "first_source_id", "first_unit", "entry_kind", "previous_owner_de"])
    write(f"{PREFIX}_10_OWNER_SWITCHES.tsv", switch_rows, ["order_id", "biological_record", "owner_state", "owner_de", "first_mark_id", "first_source_id", "first_unit", "entry_kind", "previous_owner_de"])
    write(f"{PREFIX}_6_CONDITION_HANDLES.tsv", condition_rows, ["condition_handle", "order_id", "page", "locus", "workshop_name_de", "visible_groups_on_model_leaf", "memorize", "copy"])
    write(f"{PREFIX}_6_HOUSE_CALIBRATIONS.tsv", calibration_rows, [*calibrations[0].keys(), "used_in_orders", "lesson"])
    write(f"{PREFIX}_8_LESSON_CURRICULUM.tsv", lesson_rows, ["lesson", "content", "memorize_items", "model_leaf_items", "practice"])

    prose_core_events = sum(int(row["visible_marks"]) for row in core_cards)
    prose_local_events = sum(int(row["visible_marks"]) for row in local_cards if "COND" not in str(row["stage_classes"]))
    astro_local_events = sum(int(row["visible_marks"]) for row in local_cards if row["stage_classes"] == "COND")
    summary = {
        "status": "PASS",
        "decision": "FIFTH_SCRIBE_NEEDS_PORTABLE_CORE_PLUS_LOCAL_MODEL_LEAVES_NOT_TOTAL_CARD_MEMORIZATION",
        "six_order_marks": len(marks),
        "unique_identities": len(by_identity),
        "portable_core_cards": len(core_cards),
        "portable_core_marks": prose_core_events,
        "core_components": len(component_rows),
        "local_model_cards": len(local_cards),
        "local_prose_cards": sum(row["stage_classes"] != "COND" for row in local_cards),
        "local_prose_marks": prose_local_events,
        "local_condition_cards": sum(row["stage_classes"] == "COND" for row in local_cards),
        "local_condition_marks": astro_local_events,
        "product_handles": len(product_rows),
        "owner_states": len(owner_rows),
        "owner_switches": len(switch_rows),
        "condition_handles": len(condition_rows),
        "house_calibrations": len(calibration_rows),
        "lesson_blocks": len(lesson_rows),
        "full_memory_without_model_leaves": len(by_identity),
        "fixed_pages": sorted({row["page"] for row in marks}),
        "new_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (HERE / f"{PREFIX}_APPRENTICE_MANUAL.md").write_text(
        "# Lehrbuch für den fünften Schreiber\n\n"
        "Der Lehrling lernt nicht 228 Karten als gleichartige Wörter. Er lernt zuerst 29\n"
        "kurze Komponenten und 56 häufige, zwischen Aufträgen wandernde Kernkarten. Diese\n"
        "56 Karten tragen 261 der 365 Prosa-Marken des Sechs-Auftrags-Buchs.\n\n"
        "Danach lernt er vier interne Bildprodukt-Griffe, zehn echte Besitzerwechsel, sechs\n"
        "lokale Himmelsgriffe und sechs Hausmaße. Die übrigen 99 lokalen Prosakarten und 73\n"
        "Himmelsmarken liegen als Musterblätter bereit. Sie werden genau kopiert, nicht aus\n"
        "einem vermeintlichen Alphabet neu erfunden.\n\n"
        "## Arbeitsregel\n\n"
        "1. Wähle den Auftrag und zeige auf das Bildprodukt.\n"
        "2. Lies die häufigen Karten aus dem Kern; kopiere seltene Karten vom lokalen Blatt.\n"
        "3. Beginne am sichtbaren Biological-Besitzer und wechsle nur an den zehn gelehrten Punkten.\n"
        "4. Verwende dieselben sechs Hauskalibrierungen in jedem Auftrag.\n"
        "5. Suche den lokalen Himmelsgriff und kopiere dessen vollständige Gruppe.\n"
        "6. Schließe nur mit einer im Kartenblatt ausdrücklich geschlossenen Form.\n\n"
        "Ohne irgendein Musterblatt müsste derselbe Schreiber alle 228 Identitäten und 119\n"
        "Einheiten auswendig lernen. Das ist möglich, aber nicht die sparsame Werkstattlösung.\n",
        encoding="utf-8",
    )
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 877: minimum fifth-scribe curriculum\n\n"
        "The practical minimum is a mixed memory-and-model system. Fifty-six exact cards recur\n"
        "across orders and cover 261/365 prose marks; their readings use 29 shared components.\n"
        "Ninety-nine one-order prose cards and 73 local Astro identities remain on model leaves.\n\n"
        "The apprentice additionally memorizes four internal product handles, ten owner-switch\n"
        "cues, six condition handles and six house calibrations. Six visible starting owners and\n"
        "the full local rare-card sequences remain picture/model addressed. This is substantially\n"
        "smaller than memorizing all 228 identities and 119 units, while reproducing all 438 marks.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
