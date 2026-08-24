#!/usr/bin/env python3
"""Join the complete prose curriculum to the separate copied Astro layer."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P624 = ROOT / "experiments/yolo/sidequest_semantic_six_case_astro_architecture_six_hundred_twenty_fourth"
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    prose = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    astro_groups = read_tsv(P624 / "SIX_HUNDRED_TWENTY_FOURTH_395_ASTRO_GROUP_INTERFACE.tsv")
    astro_loci = read_tsv(P624 / "SIX_HUNDRED_TWENTY_FOURTH_142_ASTRO_LOCUS_INTERFACE.tsv")
    namespaces = read_tsv(P624 / "SIX_HUNDRED_TWENTY_FOURTH_13_ASTRO_NAMESPACE_INTERFACE.tsv")

    unified = []
    for row in prose:
        unified.append({
            "unified_id": f"PROSE:{row['event_id']}",
            "section": "PROSE_WORKSHOP",
            "page": row["page"],
            "record_or_locus": row["record"],
            "case_or_namespace": row["case_id"],
            "visible_surface": row["surface"],
            "local_identity": row["card_no"],
            "short_default_reading_de": row["standard_command_de"],
            "learning_layer": row["semantic_burden_class"],
            "writing_or_copy_rule": row["surface_writer_layer"],
            "owner_address_policy": "VISIBLE_CASE_OWNER_AND_RECORD_STATE",
            "required_for_case": "YES",
            "orientation": "NOT_APPLICABLE",
            "cross_page_key": "NONE",
        })
    for row in astro_groups:
        unified.append({
            "unified_id": f"ASTRO:{row['opaque_local_id']}",
            "section": "ASTRO_COPIED_LOOKUP",
            "page": row["page"],
            "record_or_locus": row["locus"],
            "case_or_namespace": row["canonical_namespace_id"],
            "visible_surface": row["surface_display_only"],
            "local_identity": row["opaque_local_id"],
            "short_default_reading_de": f"LOKALE HIMMELS-/ADRESSMARKE AM BILDPLATZ {row['local_image_owner']}",
            "learning_layer": "WHOLE_LOCAL_ASTRO_LABEL",
            "writing_or_copy_rule": "COPY_COMPLETE_LABEL_FROM_LOCAL_CELESTIAL_EXEMPLAR",
            "owner_address_policy": row["local_image_owner"],
            "required_for_case": row["required_for_case"],
            "orientation": row["orientation_or_rotation"],
            "cross_page_key": row["f68_f69_key"],
        })

    namespace_lessons = []
    for number, row in enumerate(namespaces, 1):
        namespace_lessons.append({
            "lesson_no": number,
            "namespace_id": row["canonical_namespace_id"],
            "page": row["page"],
            "loci": row["loci"],
            "groups": row["groups"],
            "instrument_reading_de": row["instrument_reading_de"],
            "apprentice_action_de": "Bildplatz zeigen; vollstaendige lokale Marke in ihrer Reihenfolge kopieren; nur innerhalb dieses Namensraums wiederfinden",
            "possible_case_use_de": row["possible_condition_use_de"],
            "required_for_case": row["required_for_case"],
            "orientation": row["orientation"],
            "cross_page_key": row["cross_page_key"],
            "prose_word_import": "NONE",
        })

    page_rows = []
    page_order = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]
    for page in page_order:
        prows = [row for row in prose if row["page"] == page]
        grows = [row for row in astro_groups if row["page"] == page]
        lrows = [row for row in astro_loci if row["page"] == page]
        nrows = [row for row in namespaces if row["page"] == page]
        page_rows.append({
            "page": page,
            "section": "PROSE_WORKSHOP" if prows else "ASTRO_COPIED_LOOKUP",
            "visible_groups": len(prows) + len(grows),
            "prose_events": len(prows),
            "astro_groups": len(grows),
            "astro_loci": len(lrows),
            "astro_namespaces": len(nrows),
            "case_ids": "|".join(sorted({row["case_id"] for row in prows})) if prows else "NONE",
            "learning_instruction_de": "KARTENBEDEUTUNG LESEN UND OBERFLAECHE SCHREIBEN" if prows else "BILDPLATZ UND GANZE LOKALE ETIKETTE KOPIEREN",
        })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_EIGHTH_776_TEN_PAGE_APPRENTICE_LEDGER.tsv", unified, list(unified[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_EIGHTH_13_ASTRO_NAMESPACE_LESSONS.tsv", namespace_lessons, list(namespace_lessons[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_EIGHTH_142_ASTRO_LOCUS_COPY_TRACE.tsv", astro_loci, list(astro_loci[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_EIGHTH_10_PAGE_CURRICULUM.tsv", page_rows, list(page_rows[0]))

    page_counts = {row["page"]: int(row["visible_groups"]) for row in page_rows}
    astro_surface_count = len({row["surface_display_only"] for row in astro_groups})
    md = [
        "# Zehnseiten-Handbuch der kleinen Werkstatt",
        "",
        "## Zwei getrennte Leseweisen",
        "",
        "### Pflanzen- und Badseiten",
        "",
        "Bildbesitzer bestimmen, 39 kurze Komponenten sprechen, Kartenfolge lesen, exakten Kartenkoerper und lokale Huelle schreiben.",
        "",
        "### Himmelsseiten",
        "",
        "Bildplatz und Namensraum bestimmen, die vollstaendige lokale Marke kopieren und nur innerhalb desselben Instruments wiederfinden. Keine Prosa-Wortstaemme hineinlesen.",
        "",
        "## Seitenumfang",
        "",
    ]
    for page in page_order:
        md.append(f"- **{page}:** {page_counts[page]} sichtbare Gruppen.")
    md.extend([
        "",
        "## Gesamtheft",
        "",
        f"- Prosa: {len(prose)} Ereignisse, 39 Woerter, 173 Karten, 17 lokale Oberflaecheneintraege.",
        f"- Astro: {len(astro_groups)} Gruppen in {len(astro_loci)} Bildorten und {len(namespaces)} Namensraeumen; {astro_surface_count} verschiedene sichtbare Gruppenformen.",
        f"- Gesamt: {len(unified)} sichtbare Gruppen auf zehn Seiten.",
        "- Astro ist optional; kein Fall benoetigt eine Himmelsmarke.",
        "- Keine Startposition, Drehrichtung, f68-f69-Verbindung oder Prosa-Astro-Wortgleichung wird gelehrt.",
    ])
    (HERE / "SIX_HUNDRED_THIRTY_EIGHTH_TEN_PAGE_APPRENTICE_HANDBOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "pages": len(page_rows),
        "prose_pages": sum(row["section"] == "PROSE_WORKSHOP" for row in page_rows),
        "astro_pages": sum(row["section"] == "ASTRO_COPIED_LOOKUP" for row in page_rows),
        "prose_events": len(prose),
        "astro_groups": len(astro_groups),
        "astro_loci": len(astro_loci),
        "astro_namespaces": len(namespaces),
        "astro_unique_surface_displays": astro_surface_count,
        "unified_groups": len(unified),
        "astro_required_for_case": sum(row["required_for_case"] == "YES" for row in astro_groups),
        "astro_prose_word_imports": sum(row["prose_dictionary_import"] != "NONE" for row in astro_groups),
        "oriented_astro_groups": sum(row["orientation_or_rotation"] != "NONE" for row in astro_groups),
        "f68_f69_keys": sum(row["f68_f69_key"] != "NONE" for row in astro_groups),
        "decision": "TEN_PAGE_BOOK_USES_PRODUCTIVE_PROSE_AND_SEPARATE_COPIED_ASTRO_LOOKUP",
    }
    (HERE / "SIX_HUNDRED_THIRTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
