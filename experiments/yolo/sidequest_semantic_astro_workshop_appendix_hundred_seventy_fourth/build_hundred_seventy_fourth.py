#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_395_ASTRO_OWNER_MENU.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


MODULE_JOB = {
    "M67_RIGHT_SECTORS": ("F67_PREPARATION_CONDITION", "Bedingungsplatz fuer Sammeln oder Zubereiten"),
    "M67_RIGHT_RING_RULES": ("F67_PREPARATION_SEASON", "Jahres- oder Saisonregel fuer Pflanzenarbeit"),
    "M67_RIGHT_PHASES": ("F67_PREPARATION_PHASE", "lokale Phasenbedingung fuer den Ansatz"),
    "M67_SHARED_LEGEND": ("F67_PAGE_LEGEND", "gemeinsame Legende der beiden unabhaengigen Pruefraeder"),
    "M67_LEFT_ASPECT_FIELDS": ("F67_APPLICATION_CONDITION", "Bedingungsfeld fuer Baden Waschen oder Auflegen"),
    "M67_LEFT_OUTER_STATIONS": ("F67_APPLICATION_CLASS", "Koerper- oder Anwendungsklasse am linken Rad"),
    "M67_LEFT_RING_RULE": ("F67_APPLICATION_SEASON", "Jahres- oder Saisonregel fuer die Anwendung"),
    "M68_PANEL_HEADERS": ("F68_SKY_REGION", "Kopf oder Region im Beobachtungsatlas"),
    "M68_STAR_STATIONS": ("F68_STAR_ADDRESS", "lokale Sternadresse zum Bestimmen der aktuellen Himmelslage"),
    "M68_CENTER_KEY": ("F68_LOCAL_REFERENCE", "lokales Bezugsmedaillon oder Zentrum innerhalb eines Paneels"),
    "M69_LEFT_RUBRIC": ("F69_WORK_CHOICE_RUBRIC", "Rubrik des linken Arbeitswahlrads"),
    "M69_LEFT_28_SLOTS": ("F69_WORK_CHOICE", "einer von achtundzwanzig ungeordneten lokalen Arbeitsfaellen"),
    "M69_MIDDLE_QUALITY": ("F69_MOISTURE_WEATHER", "Feuchte Wetter oder Mediumbedingung am mittleren Rad"),
    "M69_RIGHT_LIGHT": ("F69_LIGHT_HEAT", "Licht Sonnen- oder Waermebedingung am rechten Rad"),
}


PAGE_JOBS = [
    ("f67r2", "TWO_INDEPENDENT_ELIGIBILITY_WHEELS", "rechtes Rad prueft Sammeln/Zubereiten; linkes Rad prueft Baden/Waschen/Auflegen", "zwei getrennte Jahres- oder Bedingungspruefer", "keine 7x12-Matrix und kein rechter-linker Paarindex"),
    ("f68r1", "MULTIPANEL_CELESTIAL_OBSERVATION_ATLAS", "aktuelle Himmelsregion und lokale Sternadresse im passenden Paneel finden", "Beobachtungsatlas vor der Arbeitswahl", "mehrere Zentren; die 28 Sterne sind kein geordneter Ring"),
    ("f69v", "THREE_INDEPENDENT_WORK_CONDITION_WHEELS", "links Arbeitsfall; Mitte Feuchte/Wetter; rechts Licht/Waerme nachschlagen", "drei getrennte Regler fuer die praktische Ausfuehrung", "nur links 28 lokale Plaetze; keine gemeinsame Richtung"),
]


def main() -> None:
    source = read(ASTRO)
    group_rows = []
    for row in source:
        job_id, job_de = MODULE_JOB[row["source_module"]]
        group_rows.append(
            {
                "source_group_id": row["source_group_id"],
                "page": row["page"],
                "reading_unit_id": row["reading_unit_id"],
                "source_module": row["source_module"],
                "visible_owner": row["visible_owner"],
                "visible_surface": row["visible_surface"],
                "local_job_id": job_id,
                "concrete_workshop_value_de": f"{job_de}: {row['local_astro_value_de']}",
                "ordering_rule": "SOURCE_ORDER_ONLY_NOT_CIRCLE_DIRECTION",
                "crosspage_key": "NONE",
            }
        )
    write(OUT / "HUNDRED_SEVENTY_FOURTH_395_GROUP_WORKSHOP_APPENDIX.tsv", group_rows)

    loci: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in group_rows:
        loci.setdefault(row["reading_unit_id"], []).append(row)
    locus_rows = []
    for locus_id, members in loci.items():
        locus_rows.append(
            {
                "reading_unit_id": locus_id,
                "page": members[0]["page"],
                "source_module": members[0]["source_module"],
                "visible_owner": members[0]["visible_owner"],
                "member_group_count": len(members),
                "visible_surface_sequence": " ".join(row["visible_surface"] for row in members),
                "local_job_id": members[0]["local_job_id"],
                "workshop_instruction_de": members[0]["concrete_workshop_value_de"],
                "apprentice_action_de": "Zeige den Bildort kopiere alle Gruppen und lies nur den lokalen Exemplareintrag fuer diesen Job.",
            }
        )
    write(OUT / "HUNDRED_SEVENTY_FOURTH_142_LOCUS_JOB_EDITION.tsv", locus_rows)

    page_rows = [
        {
            "page": page,
            "selected_page_job": job,
            "concrete_use_de": use,
            "book_role_de": role,
            "hard_boundary_de": boundary,
        }
        for page, job, use, role, boundary in PAGE_JOBS
    ]
    write(OUT / "HUNDRED_SEVENTY_FOURTH_3_ASTRO_PAGE_JOBS.tsv", page_rows)

    no_key = [
        ("N1", "f67 right to left", "NONE", "beide Raeder werden getrennt nach Aufgabe aufgeschlagen"),
        ("N2", "f67 12 by 12", "NONE", "zwei Zwoelfheiten bilden keine Matrix"),
        ("N3", "f68 star 1 to f69 slot 1", "NONE", "gleiche editorische Nummer ist kein historischer Schluessel"),
        ("N4", "f69 left to middle", "NONE", "Arbeitsfall und Feuchtebedingung werden getrennt gewaehlt"),
        ("N5", "f69 left to right", "NONE", "Arbeitsfall und Lichtbedingung werden getrennt gewaehlt"),
        ("N6", "circle start or direction", "NONE", "Lehrling benutzt Bildort und Mastereintrag nicht eine erfundene Kreisrichtung"),
    ]
    no_key_rows = [{"rule_id": rid, "forbidden_join": join, "key": key, "replacement_workflow_de": replacement} for rid, join, key, replacement in no_key]
    write(OUT / "HUNDRED_SEVENTY_FOURTH_6_NO_KEY_RULES.tsv", no_key_rows)

    summary = {
        "source_astro_sha256": hashlib.sha256(ASTRO.read_bytes()).hexdigest(),
        "pages": 3,
        "groups": len(group_rows),
        "loci": len(locus_rows),
        "module_jobs": len(MODULE_JOB),
        "no_key_rules": len(no_key_rows),
        "f67_groups": sum(row["page"] == "f67r2" for row in group_rows),
        "f68_groups": sum(row["page"] == "f68r1" for row in group_rows),
        "f69_groups": sum(row["page"] == "f69v" for row in group_rows),
        "f68_f69_key": None,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
