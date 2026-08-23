#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R129 = ROOT / "experiments/yolo/sidequest_semantic_specialist_drawers_hundred_twenty_ninth"
R132 = ROOT / "experiments/yolo/sidequest_semantic_four_practical_jobs_hundred_thirty_second"
PATHS = ROOT / "experiments/yolo/sidequest_semantic_selected_job_paths"

MAP = {
    "D1_ROOT_BATH_RIGHT_WHEEL": "J1_ROOT_AND_LEAF_BASIN",
    "D2_CLEAR_EXTRACT_STAR_ATLAS": "J2_CLEAR_EXTRACT_STATIONS",
    "D3_STORED_APPLICATION_THREE_WHEELS": "J3_BOUND_APPLICATION_SERVICE",
    "D4_FRESH_PLANT_LEFT_WHEEL": "J4_FRESH_PLANT_LONG_ROUTE",
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = read_tsv(R132 / "HUNDRED_THIRTY_SECOND_FOUR_JOB_PROFILES.tsv")
    prose = read_tsv(R132 / "HUNDRED_THIRTY_SECOND_381_EVENT_JOB_LEDGER.tsv")
    cards = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_173_CARD_DICTIONARY.tsv")
    choices = read_tsv(PATHS / "SELECTED_13_ASTRO_CHOICES.tsv")
    menu = read_tsv(PATHS / "ASTRO_395_MENU_STATUS.tsv")
    old_paths = read_tsv(PATHS / "FOUR_SELECTED_JOB_PATHS.tsv")
    old_path_by_new = {MAP[row["work_order_id"]]: row for row in old_paths}
    job_by_id = {row["job_id"]: row for row in jobs}

    surface_to_card = {}
    for card in cards:
        for surface in card["registered_surfaces"].split("|"):
            surface_to_card[surface] = card

    choice_rows = []
    for row in choices:
        job_id = MAP[row["work_order_id"]]
        surfaces = row["visible_surface_sequence"].split()
        echoes = []
        for surface in surfaces:
            if surface in surface_to_card:
                echoes.append(f"{surface}={surface_to_card[surface]['current_spoken_default_de']}")
        choice_rows.append({
            "job_id": job_id,
            "selection_id": row["selection_id"],
            "choice_order": row["choice_order"],
            "choice_type": row["choice_type"],
            "page": row["page"],
            "source_module": row["source_unit"],
            "visible_owner_loci": row["reading_unit_ids"],
            "source_group_ids": row["source_group_ids"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "selected_when_value_de": row["selected_workshop_value_de"],
            "current_prose_echoes": " | ".join(echoes) or "NONE",
            "selection_reason_de": row["selection_reason_de"],
            "orientation": "NONE__CHOOSE_VISIBLE_OWNER",
            "crosspage_key": "NONE__OPTIONAL_JOB_SCENARIO",
        })
    write_tsv("HUNDRED_THIRTY_THIRD_THIRTEEN_WHEN_CHOICES.tsv", choice_rows)

    profile_rows = []
    for job in jobs:
        path = old_path_by_new[job["job_id"]]
        profile_rows.append({
            "job_id": job["job_id"],
            "title_de": job["title_de"],
            "selected_when_condition_de": path["selected_condition_de"],
            "when_choice_count": path["astro_choice_count"],
            "selected_astro_group_count": path["selected_astro_group_count"],
            "unselected_astro_menu_groups": path["unselected_astro_menu_group_count"],
            "what_records": job["herbal_records"],
            "how_records": job["biological_records"],
            "prose_event_count": job["event_count"],
            "complete_job_instruction_de": job["complete_job_instruction_de"],
            "execution_order": "OPTIONAL_WHEN>WHAT>HOW",
            "claim_boundary": "USE_SCENARIO_ONLY__NO_WRITTEN_POINTER_OR_REQUIRED_ASTRO_KEY",
        })
    write_tsv("HUNDRED_THIRTY_THIRD_FOUR_WHAT_HOW_WHEN_JOBS.tsv", profile_rows)

    menu_rows = []
    for row in menu:
        job_id = MAP[row["work_order_id"]]
        card = surface_to_card.get(row["visible_surface"])
        menu_rows.append({
            "job_id": job_id,
            "page": row["page"],
            "source_module": row["source_unit"],
            "reading_unit_id": row["reading_unit_id"],
            "source_group_id": row["source_group_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "local_astro_value_de": row["current_reader_value_de"],
            "prose_echo_de": card["current_spoken_default_de"] if card else "NO_PROSE_ECHO",
            "menu_status": row["menu_status"],
            "selection_id": row["selection_id"],
            "orientation": "NONE__VISIBLE_OWNER_ONLY",
            "crosspage_key": "NONE",
        })
    write_tsv("HUNDRED_THIRTY_THIRD_395_ASTRO_JOB_MENU.tsv", menu_rows)

    unified = []
    serial = 0
    for row in prose:
        serial += 1
        unified.append({
            "unified_serial": f"U{serial:03d}",
            "job_id": row["job_id"],
            "phase": "WHAT_OR_HOW_PROSE",
            "page": row["page"],
            "local_unit": row["statement_id"],
            "source_group_id": f"E{int(row['event_serial']):03d}",
            "visible_owner": row["record_unit_id"],
            "visible_surface": row["visible_surface"],
            "current_reading_de": row["current_spoken_default_de"],
            "menu_status": "ACTIVE_PROSE",
            "orientation": "PROSE_ORDER",
            "crosspage_key": "NONE",
        })
    for row in menu_rows:
        serial += 1
        unified.append({
            "unified_serial": f"U{serial:03d}",
            "job_id": row["job_id"],
            "phase": "OPTIONAL_WHEN_MENU",
            "page": row["page"],
            "local_unit": row["reading_unit_id"],
            "source_group_id": row["source_group_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "current_reading_de": row["local_astro_value_de"],
            "menu_status": row["menu_status"],
            "orientation": row["orientation"],
            "crosspage_key": row["crosspage_key"],
        })
    write_tsv("HUNDRED_THIRTY_THIRD_776_JOB_LEDGER.tsv", unified)

    active = [row for row in unified if row["menu_status"] in {"ACTIVE_PROSE", "SELECTED_FOR_SAMPLE_JOB"}]
    write_tsv("HUNDRED_THIRTY_THIRD_402_ACTIVE_JOB_GROUPS.tsv", active)

    md = ["# Vier Werkstattaufträge mit optionaler Himmelsbedingung", ""]
    for job in profile_rows:
        md += [f"## {job['job_id']}: {job['title_de']}", "", f"WANN: {job['selected_when_condition_de']}", "",
               f"WAS: {job['what_records']}", "", f"WIE: {job['how_records']}", "", job["complete_job_instruction_de"], "",
               "Die Astro-Auswahl ist eine sichtbare Menüwahl für dieses Szenario, kein gelesener Querverweis.", ""]
    (OUT / "HUNDRED_THIRTY_THIRD_FOUR_OPTIONAL_WHEN_WORK_ORDERS.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertdreiunddreißigste Runde: optionales WANN vor WAS und WIE", "",
        "The four updated prose jobs now reuse the thirteen visible Astro choices already available on the",
        "three fixed diagram pages. Those choices activate 21 of 395 Astro groups; the other 374 remain menu",
        "options. Together with all 381 prose events the active job reader has 402 groups, while the complete",
        "reference ledger retains all 776.", "",
        "The practical order is optional WHEN, then WHAT material, then HOW operation. No wheel start, rotation,",
        "reading direction, f68-to-f69 key or written cross-page pointer is introduced. Matching surfaces such",
        "as `aiin`, `cheey`, `cho`, `dal`, `dy`, `okeey`, `okey`, `oldy`, and `sheey` receive their current",
        "short prose nucleus plus a local diagram expansion.", "",
        "Next step: rewrite the complete ten-page reader around these four jobs and the new 173-card dictionary,",
        "so the prose, diagram choices, hand variants and apprentice manual are once again one current edition.",
    ]
    (OUT / "HUNDRED_THIRTY_THIRD_OPTIONAL_WHEN_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "jobs": len(profile_rows), "when_choices": len(choice_rows),
               "selected_astro_groups": sum(row["menu_status"] == "SELECTED_FOR_SAMPLE_JOB" for row in menu_rows),
               "unselected_astro_groups": sum(row["menu_status"] == "UNSELECTED_REFERENCE_OPTION" for row in menu_rows),
               "complete_groups": len(unified), "active_groups": len(active)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
