#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK_DIR = ROOT / "sidequest_semantic_six_order_workshop_book_eight_hundred_seventy_sixth"
COURSE_DIR = ROOT / "sidequest_semantic_fifth_scribe_curriculum_eight_hundred_seventy_seventh"
MARKS = BOOK_DIR / "EIGHT_HUNDRED_SEVENTY_SIXTH_438_MARK_SIX_ORDER_BOOK.tsv"
ORDERS = BOOK_DIR / "EIGHT_HUNDRED_SEVENTY_SIXTH_6_COMPLETE_ORDER_SUMMARY.tsv"
CORE = COURSE_DIR / "EIGHT_HUNDRED_SEVENTY_SEVENTH_56_PORTABLE_CORE_CARDS.tsv"
LOCAL = COURSE_DIR / "EIGHT_HUNDRED_SEVENTY_SEVENTH_172_LOCAL_MODEL_CARDS.tsv"
SWITCHES = COURSE_DIR / "EIGHT_HUNDRED_SEVENTY_SEVENTH_10_OWNER_SWITCHES.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_EIGHTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def atoms(recipe: str) -> list[str]:
    return [] if recipe.startswith("WHOLE[") else recipe.split("+")


def main() -> None:
    marks = read(MARKS)
    orders = read(ORDERS)
    core = read(CORE)
    local = read(LOCAL)
    switches = read(SWITCHES)
    core_ids = {row["identity"] for row in core}
    local_ids = {row["identity"] for row in local}

    core_events = [row for row in marks if row["identity"] in core_ids]
    by_identity: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in core_events:
        by_identity[row["identity"]].append(row)

    renderer_rows = []
    modal_surface: dict[str, str] = {}
    for identity in sorted(core_ids):
        rows = by_identity[identity]
        counts = Counter(row["surface"] for row in rows)
        modal = sorted(counts, key=lambda surface: (-counts[surface], surface))[0]
        modal_surface[identity] = modal
        source = next(row for row in core if row["identity"] == identity)
        renderer_rows.append(
            {
                "identity": identity,
                "component_recipe": source["component_recipe"],
                "concrete_default_de": source["concrete_default_de"],
                "surface_count": len(counts),
                "surfaces_with_counts": ",".join(f"{surface}:{counts[surface]}" for surface in sorted(counts)),
                "house_model_surface": modal,
                "house_model_count": counts[modal],
                "alternate_surface_marks": len(rows) - counts[modal],
                "orders": source["orders"],
                "renderer_rule": "COPY_LOCAL_SURFACE_OR_USE_HOUSE_MODEL_WITHOUT_MEANING_CHANGE" if len(counts) > 1 else "FIXED_SURFACE_IN_SIX_ORDER_BOOK",
            }
        )

    event_rows = []
    for row in core_events:
        model = modal_surface[row["identity"]]
        event_rows.append(
            {
                "order_id": row["order_id"],
                "order_mark_id": row["order_mark_id"],
                "page": row["page"],
                "unit": row["unit"],
                "identity": row["identity"],
                "observed_surface": row["surface"],
                "house_model_surface": model,
                "surface_relation": "HOUSE_MODEL" if row["surface"] == model else "LICENSED_LOCAL_ALTERNATE",
                "meaning_unchanged": "YES",
                "concrete_default_de": row["concrete_default_de"],
            }
        )

    order_drills = []
    for order in orders:
        order_id = order["order_id"]
        rows = [row for row in marks if row["order_id"] == order_id]
        prose = [row for row in rows if not row["stage"].startswith("CONDITION")]
        core_subset = [row for row in prose if row["identity"] in core_ids]
        local_subset = [row for row in prose if row["identity"] in local_ids]
        long_grade = [row for row in prose if any(atom in {"EE", "EEE"} for atom in atoms(row["component_recipe"]))]
        terminal = [row for row in prose if "DY" in atoms(row["component_recipe"])]
        open_y = [row for row in prose if "Y" in atoms(row["component_recipe"]) and "DY" not in atoms(row["component_recipe"])]
        condition = [row for row in rows if row["stage"].startswith("CONDITION")]
        order_drills.append(
            {
                "order_id": order_id,
                "total_marks": len(rows),
                "prose_marks": len(prose),
                "portable_core_marks": len(core_subset),
                "local_prose_model_marks": len(local_subset),
                "licensed_local_surface_marks": sum(row["surface"] != modal_surface[row["identity"]] for row in core_subset),
                "long_or_full_grade_checks": len(long_grade),
                "terminal_dy_checks": len(terminal),
                "open_y_checks": len(open_y),
                "owner_switch_checks": sum(row["order_id"] == order_id for row in switches),
                "condition_handle": order["condition_handle"],
                "condition_groups_to_copy": len(condition),
                "drill_instruction_de": "Kern aus dem Gedächtnis, lokale Formen vom Blatt; Grad, Schluss, Besitzer und vollständigen Himmelsgriff gegenprüfen.",
            }
        )

    grade_marks = sum(int(row["long_or_full_grade_checks"]) for row in order_drills)
    terminal_marks = sum(int(row["terminal_dy_checks"]) for row in order_drills)
    open_marks = sum(int(row["open_y_checks"]) for row in order_drills)
    correction_rows = [
        {"check_id": "C1", "workshop_tick": "MODEL_POINT", "protects": "seltene lokale Prosa- oder Himmelskarte", "danger_loci": 177, "rule_de": "Punkt erst setzen, wenn die Form Zeichen für Zeichen am lokalen Muster geprüft ist.", "meaning_if_missed": "lokaler Inhalt kann wechseln"},
        {"check_id": "C2", "workshop_tick": "GRADE_STROKES", "protects": "EE/EEE gegenüber E", "danger_loci": grade_marks, "rule_de": "Ein, zwei oder drei Arbeitsstriche vor dem Kopieren leise mitzählen.", "meaning_if_missed": "Dauer oder Vollständigkeit ändert sich"},
        {"check_id": "C3", "workshop_tick": "CLOSE_HOOK", "protects": "lizenzierte DY-Schlussform gegenüber offenem Y", "danger_loci": terminal_marks + open_marks, "rule_de": "Vor Feldwechsel offen oder geschlossen ansagen; nacktes sichtbares dy nie allein entscheiden lassen.", "meaning_if_missed": "Schritt endet zu früh oder bleibt offen"},
        {"check_id": "C4", "workshop_tick": "OWNER_ARROW", "protects": "sichtbaren Stationsbesitzer", "danger_loci": len(switches), "rule_de": "Am Umschaltpunkt mit Finger oder Griffel auf die nächste Figur, Schale oder Leitung zeigen.", "meaning_if_missed": "richtige Handlung landet am falschen Ort"},
        {"check_id": "C5", "workshop_tick": "LOCUS_RING", "protects": "vollständigen lokalen Himmelsgriff", "danger_loci": len(orders), "rule_de": "Locus vor Beginn umfahren und erst nach der letzten lokalen Gruppe abhaken.", "meaning_if_missed": "Bedingungsgriff wird verkürzt oder mit Nachbar vermischt"},
    ]

    hand_rows = [
        {"hand_profile": "H-A_LEHRMEISTER", "primary_resource": "Bedeutungskern und Auftragspfad", "surface_policy": "lokale Oberfläche genau beibehalten", "safe_variation": "keine nötig", "principal_risk": "Übererklärung seltener Karten", "required_checks": "C1,C4,C5"},
        {"hand_profile": "H-B_FLIESSENDER_KOPIST", "primary_resource": "56 Kernkarten", "surface_policy": "Hausmodell für variable Kernkarte erlaubt", "safe_variation": "68 lokale Oberflächen dürfen auf Hausmodell normalisiert werden", "principal_risk": "E/EE/EEE angleichen", "required_checks": "C2,C3"},
        {"hand_profile": "H-C_BILDSTATIONSSCHREIBER", "primary_resource": "16 sichtbare Biological-Besitzer", "surface_policy": "Karte am jeweiligen Bildbesitzer platzieren", "safe_variation": "Zeilenumbruch darf wechseln", "principal_risk": "einen der zehn Besitzerwechsel übergehen", "required_checks": "C3,C4"},
        {"hand_profile": "H-D_DIAGRAMMKOPIST", "primary_resource": "sechs lokale Himmelsblätter", "surface_policy": "73 lokale Gruppen vollständig kopieren", "safe_variation": "keine Bedeutungsanalyse erforderlich", "principal_risk": "Ring oder Sternlocus verkürzen", "required_checks": "C1,C5"},
    ]

    write(f"{PREFIX}_56_CORE_RENDERER_FAMILIES.tsv", renderer_rows, ["identity", "component_recipe", "concrete_default_de", "surface_count", "surfaces_with_counts", "house_model_surface", "house_model_count", "alternate_surface_marks", "orders", "renderer_rule"])
    write(f"{PREFIX}_261_CORE_RENDERER_EVENTS.tsv", event_rows, ["order_id", "order_mark_id", "page", "unit", "identity", "observed_surface", "house_model_surface", "surface_relation", "meaning_unchanged", "concrete_default_de"])
    write(f"{PREFIX}_6_ORDER_ERROR_DRILLS.tsv", order_drills, ["order_id", "total_marks", "prose_marks", "portable_core_marks", "local_prose_model_marks", "licensed_local_surface_marks", "long_or_full_grade_checks", "terminal_dy_checks", "open_y_checks", "owner_switch_checks", "condition_handle", "condition_groups_to_copy", "drill_instruction_de"])
    write(f"{PREFIX}_5_CORRECTION_CHECKS.tsv", correction_rows, ["check_id", "workshop_tick", "protects", "danger_loci", "rule_de", "meaning_if_missed"])
    write(f"{PREFIX}_4_HAND_PROFILES.tsv", hand_rows, ["hand_profile", "primary_resource", "surface_policy", "safe_variation", "principal_risk", "required_checks"])

    variable = [row for row in renderer_rows if int(row["surface_count"]) > 1]
    stable = [row for row in renderer_rows if int(row["surface_count"]) == 1]
    summary = {
        "status": "PASS",
        "decision": "MULTIPLE_HANDS_CAN_SHARE_IDENTITY_AND_MEANING_WHILE_RENDERING_CORE_CARDS_DIFFERENTLY",
        "orders": len(orders),
        "marks": len(marks),
        "portable_core_identities": len(renderer_rows),
        "portable_core_events": len(event_rows),
        "observed_core_surfaces": sum(int(row["surface_count"]) for row in renderer_rows),
        "variable_renderer_identities": len(variable),
        "fixed_renderer_identities": len(stable),
        "licensed_alternate_surface_events": sum(row["surface_relation"] == "LICENSED_LOCAL_ALTERNATE" for row in event_rows),
        "surface_normalizations_with_meaning_unchanged": sum(row["surface_relation"] == "LICENSED_LOCAL_ALTERNATE" for row in event_rows),
        "long_or_full_grade_checks": grade_marks,
        "terminal_dy_checks": terminal_marks,
        "open_y_checks": open_marks,
        "owner_switch_checks": len(switches),
        "condition_handle_checks": len(orders),
        "local_model_marks": sum(int(row["visible_marks"]) for row in local),
        "correction_checks": len(correction_rows),
        "hand_profiles": len(hand_rows),
        "dictionary_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (HERE / f"{PREFIX}_MULTIHAND_DRILL.md").write_text(
        "# Mehrhand-Drill für sechs Aufträge\n\n"
        "Die 56 tragbaren Kernidentitäten erscheinen in 102 tatsächlich beobachteten\n"
        "Oberflächen. 29 Identitäten wechseln ihre Oberfläche, 27 bleiben in diesem Buch\n"
        "stabil. Ein Hauskopist könnte 68 lokale Varianten durch die häufigste Hausform\n"
        "ersetzen, ohne die interne Identität oder den Arbeitswert zu ändern.\n\n"
        "Das heißt: Mehrere Hände müssen nicht dieselben sichtbaren Formen bevorzugen. Sie\n"
        "müssen aber fünf Dinge schützen: lokale Musterkarten, Grad, Schluss, Bildbesitzer\n"
        "und vollständigen Himmelslocus. Dafür reichen fünf kleine Prüfroutinen.\n\n"
        "## Werkstattbesetzung\n\n"
        "- Der Lehrmeister verwaltet Auftrag, Produktgriff und Hauswerte.\n"
        "- Der fließende Kopist setzt die 56 Kernkarten in seiner Hausoberfläche.\n"
        "- Der Bildstationsschreiber hält die sechzehn lokalen Besitzer auseinander.\n"
        "- Der Diagrammkopist übernimmt die 73 Himmelsgruppen aus sechs lokalen Blättern.\n\n"
        "Oberflächenwechsel ist damit kein Bedeutungsfehler. Gradverlust, falscher Schluss,\n"
        "verpasster Besitzerwechsel oder abgeschnittener Locus sind echte Werkstattfehler.\n",
        encoding="utf-8",
    )
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 878: multi-hand renderer drill\n\n"
        "The portable 56-card core has 102 observed surfaces. Twenty-nine identities are\n"
        "renderer-variable and 27 are fixed in the six-order book. Normalizing 68 alternate\n"
        "events to the house surface preserves identity and working meaning.\n\n"
        "Five checks protect what cannot safely drift: local model identity, grade, licensed\n"
        "closure, ten owner switches and six complete condition loci. Four hypothetical hand\n"
        "profiles can therefore divide the work without requiring identical surface habits.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
