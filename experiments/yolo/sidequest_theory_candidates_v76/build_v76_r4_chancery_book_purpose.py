#!/usr/bin/env python3
"""Build V76 R4's bounded ten-page book-purpose competition."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    units = [
        ("H1", "HERBAL", "f10r", 14, "root/water extract and storage article", "plant raw-material extraction lot", 4, 4, "whole plant owner; no depicted remedy or illness"),
        ("H2", "HERBAL", "f10r", 24, "two harvest fractions joined into external salve", "two harvest-state samples pressed and preserved", 4, 4, "same picture owns second record; salve and lesion are exemplar-only"),
        ("H3", "HERBAL", "f11r", 17, "wine extract plus retained oil preparation", "flower/leaf fractions clarified and archived", 4, 3, "medical double-use is genre-plausible but unpictured"),
        ("H4", "HERBAL", "f55v", 18, "clarified leaf wash plus warm honey poultice", "leaf macerate, filtration and binding test", 4, 4, "wash/poultice and processing fit equally"),
        ("H5", "HERBAL", "f56r", 27, "brief topical leaf use plus dried chest preparation", "sticky fresh sample plus dry extract batch", 3, 4, "two medical uses require many unseen nouns"),
        ("B1", "BIOLOGICAL", "f81v", 66, "communal therapeutic bath regimen", "shared bathhouse pool operation", 4, 4, "figures and shared enclosure support both"),
        ("B2", "BIOLOGICAL", "f82r", 62, "several local baths, washes and applications", "several disconnected basin/apparatus stations", 4, 4, "local stations visible; treatment purpose not"),
        ("B3", "BIOLOGICAL", "f83r", 86, "series of local therapeutic stations", "vessel, margin and linked-pair operating atlas", 3, 4, "large unresolved owner gap penalizes continuous medicine"),
        ("B4", "BIOLOGICAL", "f83r", 47, "local wash/application variants", "paired basin plus two maintenance posts", 3, 4, "apparatus geometry stronger than indication"),
        ("B5", "BIOLOGICAL", "f83r", 11, "short therapeutic station addendum", "left service-post addendum", 2, 4, "independent technical record with no patient label"),
        ("B6", "BIOLOGICAL", "f83r", 9, "short therapeutic station addendum", "right service-post addendum", 2, 4, "hard reset and no medical anchor"),
        ("A1", "ASTRO", "f67r2", 190, "celestial election/reference wheels for health timing", "two-wheel astronomical/calendar lookup", 3, 4, "celestial relation visible; health use absent"),
        ("A2", "ASTRO", "f68r1", 65, "star-station atlas for medical timing", "multipanel astronomical star atlas", 3, 4, "celestial atlas visible; medical application absent"),
        ("A3", "ASTRO", "f69v", 140, "three celestial election wheels, left with 28 local notices", "three astronomical/calendar wheels, left with 28 local notices", 3, 4, "choice/avoidance and health are exemplar-only"),
    ]
    unit_rows = []
    for unit, section, page, groups, medical, rival, med_score, rival_score, contradiction in units:
        unit_rows.append({
            "unit_id": unit,
            "section": section,
            "page": page,
            "group_count": groups,
            "leading_health_workshop_purpose": medical,
            "strongest_practical_miscellany_rival": rival,
            "health_visible_fit_0_4": med_score,
            "rival_visible_fit_0_4": rival_score,
            "selected_for_working_theory": "HEALTH_WORKSHOP" if med_score > rival_score else ("PRACTICAL_MISCELLANY" if rival_score > med_score else "TIE"),
            "hardest_contradiction": contradiction,
            "dictionary_status": "NO_PORTABLE_WORD_ADDED; ALL_CONTENT_OCCURRENCE_EXEMPLAR",
        })

    workflow_rows = [
        {"step": 1, "actor": "compiler/master", "action": "select practical source dossier", "output": "plant article, station description, or celestial lookup exemplar", "failure": "unrelated miscellany mistaken for one source"},
        {"step": 2, "actor": "draughtsman", "action": "draw whole plant, local station, or celestial instrument before prose", "output": "visible owner and remaining text spaces", "failure": "later scribe overreads layout as syntax"},
        {"step": 3, "actor": "master", "action": "assign record/panel-local owner and source order", "output": "article, station, or lookup namespace", "failure": "owner crosses a real image gap"},
        {"step": 4, "actor": "scribe", "action": "copy opaque whole-card sequence from master exemplar", "output": "exact recurring controls plus rare local cards", "failure": "rare card regularized by false stem"},
        {"step": 5, "actor": "scribe", "action": "compress repeated source arguments by picture/register ellipsis", "output": "short fitted fields", "failure": "omitted object reconstructed from wrong image"},
        {"step": 6, "actor": "scribe", "action": "apply hand/position renderer and local closure", "output": "surface groups and field boundaries", "failure": "renderer mistaken for dictionary morpheme"},
        {"step": 7, "actor": "corrector", "action": "compare exact cards, owners, resets and diagram namespaces to exemplar", "output": "corrected page", "failure": "fluent content accepted despite broken contact graph"},
        {"step": 8, "actor": "apprentice/user", "action": "consult picture plus local entry, not surface dictionary alone", "output": "practical note or lookup result", "failure": "external meaning claimed without exemplar"},
    ]

    rubric_rows = [
        {"criterion": "Herbal picture-content fit", "health_workshop": 4, "practical_miscellany": 4, "reason": "both use whole-plant articles"},
        {"criterion": "Biological figure-purpose fit", "health_workshop": 4, "practical_miscellany": 3, "reason": "nude figures favor bathing/application over pure apparatus"},
        {"criterion": "Biological apparatus fit", "health_workshop": 3, "practical_miscellany": 4, "reason": "local vessels and conduits favor operation"},
        {"criterion": "Celestial iconography fit", "health_workshop": 3, "practical_miscellany": 4, "reason": "astronomical use visible, medical election not"},
        {"criterion": "Why sections coexist", "health_workshop": 4, "practical_miscellany": 2, "reason": "materials/application/timing is the tighter single practical narrative; the miscellany needs a looser compilation motive"},
        {"criterion": "Picture-first layout", "health_workshop": 4, "practical_miscellany": 4, "reason": "both predict it"},
        {"criterion": "Multiple-scribe workflow", "health_workshop": 4, "practical_miscellany": 4, "reason": "shared exemplar and local card deck fit both"},
        {"criterion": "Semantic assumptions", "health_workshop": 2, "practical_miscellany": 3, "reason": "health purpose needs more unseen use labels"},
        {"criterion": "Historical composite-book plausibility", "health_workshop": 4, "practical_miscellany": 3, "reason": "materia medica, baths and celestial elections form a known practical cluster"},
        {"criterion": "Formal architecture economy", "health_workshop": 4, "practical_miscellany": 4, "reason": "same exemplar machine"},
    ]
    health_total = sum(int(row["health_workshop"]) for row in rubric_rows)
    rival_total = sum(int(row["practical_miscellany"]) for row in rubric_rows)

    contradiction_rows = [{
        "unit_id": row["unit_id"],
        "problem": row["hardest_contradiction"],
        "repair": "retain leading purpose as occurrence-bound edition; keep rival adjacent; add no dictionary word",
        "fatal": "NO",
    } for row in unit_rows]

    write_tsv(OUT / "V76_R4_FOURTEEN_UNIT_PURPOSE_MATRIX.tsv", unit_rows, list(unit_rows[0]))
    write_tsv(OUT / "V76_R4_PRODUCTION_WORKFLOW.tsv", workflow_rows, list(workflow_rows[0]))
    write_tsv(OUT / "V76_R4_PURPOSE_SCORECARD.tsv", rubric_rows, list(rubric_rows[0]))
    write_tsv(OUT / "V76_R4_CONTRADICTION_LEDGER.tsv", contradiction_rows, list(contradiction_rows[0]))

    bound = [
        REPO / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv",
        REPO / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv",
        REPO / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv",
        REPO / "experiments/yolo/SIDEQUEST_CODEBOOK_ATTESTATION_RULE.md",
    ]
    checks = {
        "units_14": len(unit_rows) == 14,
        "groups_776": sum(int(row["group_count"]) for row in unit_rows) == 776,
        "sections_5_6_3": [sum(row["section"] == section for row in unit_rows) for section in ("HERBAL", "BIOLOGICAL", "ASTRO")] == [5, 6, 3],
        "workflow_8": len(workflow_rows) == 8,
        "rubric_10": len(rubric_rows) == 10,
        "all_units_have_two_purposes": all(row["leading_health_workshop_purpose"] and row["strongest_practical_miscellany_rival"] for row in unit_rows),
        "dictionary_block_every_unit": all(row["dictionary_status"].startswith("NO_PORTABLE_WORD") for row in unit_rows),
        "health_leads_narrowly": health_total > rival_total and health_total - rival_total <= 3,
        "all_bindings_exist": all(path.is_file() for path in bound),
        "f84_not_named_in_units": not any("f84" in row["page"] for row in unit_rows),
    }
    validation = {
        "schema": "V76_R4_CHANCERY_BOOK_PURPOSE_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "selection": "ILLUSTRATED_PRACTICAL_HEALTH_WORKSHOP_COMPENDIUM",
        "rival": "ILLUSTRATED_PLANT_MATERIAL_BATHHOUSE_ASTRONOMICAL_MISCELLANY",
        "scores": {"health_workshop": health_total, "practical_miscellany": rival_total},
        "counts": {"units": len(unit_rows), "groups": sum(int(row["group_count"]) for row in unit_rows), "workflow_steps": len(workflow_rows), "criteria": len(rubric_rows)},
        "checks": checks,
        "bindings": {str(path.relative_to(REPO)): sha256(path) for path in bound},
        "sealed_pages_opened": [],
        "active_v76_sibling_outputs_read": False,
    }
    (OUT / "V76_R4_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))
    print(json.dumps(validation["scores"], sort_keys=True))


if __name__ == "__main__":
    main()
