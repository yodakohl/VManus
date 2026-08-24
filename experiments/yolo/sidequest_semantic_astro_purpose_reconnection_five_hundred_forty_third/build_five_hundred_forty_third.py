#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"
P542 = ROOT / "experiments/yolo/sidequest_semantic_dual_purpose_expansion_five_hundred_forty_second"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


PURPOSES = {
    "F67_RIGHT_WHEEL_NS": ("Behandlungswahl nach lokalem Himmelssektor", ["Behandlungswahl", "Körpersektor"], "Arbeitswahl nach lokalem Himmelssektor", ["Arbeitswahl"]),
    "F67_LEFT_WHEEL_NS": ("Planeteneinfluss für einen Körperteil nachschlagen", ["Planeteneinfluss", "Körperteil"], "örtliche Wetterlage am Himmelsrad nachschlagen", ["Wetterlage"]),
    "F67_PAIRED_LEGEND_QUARANTINE_NS": ("örtliche Wahllegende kopieren", ["Wahllegende"], "örtliche Arbeitslegende kopieren", ["Arbeitslegende"]),
    "F68_LEFT_PANEL_HEADER_NS": ("Kopf einer medizinischen Wahltafel", ["Wahltafel"], "Kopf einer Beobachtungstafel", ["Beobachtungstafel"]),
    "F68_MIDDLE_PANEL_HEADER_NS": ("Kopf einer medizinischen Wahltafel", ["Wahltafel"], "Kopf einer Beobachtungstafel", ["Beobachtungstafel"]),
    "F68_RIGHT_PANEL_HEADER_NS": ("Kopf einer medizinischen Wahltafel", ["Wahltafel"], "Kopf einer Beobachtungstafel", ["Beobachtungstafel"]),
    "F68_MULTIPANEL_HEADER_QUARANTINE_NS": ("ungelöster Teil einer medizinischen Wahltafel", ["Wahltafel"], "ungelöster Teil einer Beobachtungstafel", ["Beobachtungstafel"]),
    "F68_CENTRE_KEY_QUARANTINE_NS": ("Mondphase als Schlüssel einer Behandlungswahl", ["Mondphase", "Behandlungswahl"], "örtliche Zeitmarke als Schlüssel", ["Zeitmarke"]),
    "F68_LOCAL_STAR_SLOT_NS": ("Mondstation für eine Anwendungszeit", ["Mondstation", "Anwendungszeit"], "örtliche Sternstation für den Arbeitskalender", ["Sternstation"]),
    "F68_CENTRAL_LEGEND_QUARANTINE_NS": ("zentrale Wahllegende kopieren", ["Wahllegende"], "zentrale Arbeitslegende kopieren", ["Arbeitslegende"]),
    "F69_LEFT_WHEEL_NS": ("Mondstation für einen Behandlungstermin", ["Mondstation", "Behandlungstermin"], "lokalen Arbeitstag im 28-Platz-Rad nachschlagen", ["Arbeitstag"]),
    "F69_MIDDLE_WHEEL_NS": ("Feuchtigkeitsprognose für einen Körperzustand", ["Feuchtigkeitsprognose", "Körperzustand"], "Wetterzustand am Wolken-/Wellenrad nachschlagen", ["Wetterzustand"]),
    "F69_RIGHT_WHEEL_NS": ("Komplexion am Gesicht-/Strahlenrad nachschlagen", ["Komplexion"], "Tageslicht und Arbeitszustand am Strahlenrad nachschlagen", ["Tageslicht", "Arbeitszustand"]),
}


def main() -> None:
    loci = read_tsv(P75 / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv")
    groups = read_tsv(P75 / "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv")
    registry = read_tsv(P75 / "V75_SELECTED_NAMESPACE_REGISTRY.tsv")
    prose_summary = read_tsv(P542 / "FIVE_HUNDRED_FORTY_SECOND_PURPOSE_COST_SUMMARY.tsv")

    namespace_rows: list[dict[str, str]] = []
    for namespace in registry:
        medical, medical_terms, technical, technical_terms = PURPOSES[namespace["namespace_id"]]
        med_cost = len(medical_terms)
        tech_cost = len(technical_terms)
        namespace_rows.append(
            {
                "namespace_id": namespace["namespace_id"],
                "page": namespace["page"],
                "visible_kind": namespace["visible_kind"],
                "locus_count": namespace["locus_count"],
                "group_count": namespace["group_count"],
                "medical_working_purpose_de": medical,
                "medical_silent_terms": "|".join(medical_terms),
                "medical_insertion_cost": str(med_cost),
                "technical_working_purpose_de": technical,
                "technical_silent_terms": "|".join(technical_terms),
                "technical_insertion_cost": str(tech_cost),
                "local_winner": "MEDICAL" if med_cost < tech_cost else "TECHNICAL" if tech_cost < med_cost else "TIE",
                "orientation": "NONE_SELECTED",
                "crosspage_join": "NONE",
                "prose_card_import": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_THIRD_THIRTEEN_ASTRO_PURPOSE_NAMESPACES.tsv", namespace_rows)
    purpose_for = {row["namespace_id"]: row for row in namespace_rows}
    namespace_for_locus = {
        locus: namespace["namespace_id"]
        for namespace in registry
        for locus in namespace["source_loci"].split("|")
    }

    locus_rows: list[dict[str, str]] = []
    for locus in loci:
        namespace_id = namespace_for_locus[locus["locus"]]
        purpose = purpose_for[namespace_id]
        locus_rows.append(
            {
                "page": locus["page"],
                "diagram_id": locus["diagram_id"],
                "locus": locus["locus"],
                "group_count": locus["group_count"],
                "opaque_group_ids": locus["opaque_group_ids"],
                "local_image_owner": locus["local_image_owner"],
                "local_namespace": namespace_id,
                "visible_content_class": locus["local_content_class"],
                "medical_expansion_de": f"{locus['locus']}: {purpose['medical_working_purpose_de']}; örtlichen Eintrag aus dem Exemplar lesen.",
                "technical_expansion_de": f"{locus['locus']}: {purpose['technical_working_purpose_de']}; örtlichen Eintrag aus dem Exemplar lesen.",
                "orientation": "UNORDERED_OR_UNSELECTED",
                "f68_f69_mapping": "NONE",
                "prose_card_import": "NONE",
                "exact_external_label": "NOT_ASSIGNED",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_THIRD_ONE_HUNDRED_FORTY_TWO_DUAL_ASTRO_LOCI.tsv", locus_rows)

    group_rows: list[dict[str, str]] = []
    for group in groups:
        namespace_id = namespace_for_locus[group["locus"]]
        group_rows.append(
            {
                "group_serial": group["group_serial"],
                "diagram_id": group["diagram_id"],
                "page": group["page"],
                "locus": group["locus"],
                "opaque_local_id": group["opaque_local_id"],
                "local_image_owner": group["local_image_owner"],
                "local_namespace": namespace_id,
                "surface_group_status": "OPAQUE_LOCAL_EXEMPLAR_LABEL",
                "medical_purpose_source": "NAMESPACE_EXPANSION_ONLY",
                "technical_purpose_source": "NAMESPACE_EXPANSION_ONLY",
                "orientation": "NONE_SELECTED",
                "crosspage_join": "NONE",
                "prose_card_import": "NONE",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_THIRD_THREE_HUNDRED_NINETY_FIVE_ASTRO_GROUP_BINDING.tsv", group_rows)

    page_rows = [
        {
            "diagram_id": "A1", "page": "f67r2", "loci": "74", "groups": "190",
            "visible_structure": "two disconnected celestial reference wheels",
            "medical_reading_de": "zwei getrennte Wahl-/Einflussräder für Behandlungszeit und Körperbezug",
            "technical_reading_de": "zwei getrennte Himmels-/Wetterräder für Arbeitswahl und Saisonlage",
            "hard_geometry_rule": "kein 7x12 Raster und keine Kante zwischen den Rädern",
        },
        {
            "diagram_id": "A2", "page": "f68r1", "loci": "37", "groups": "65",
            "visible_structure": "multipanel star atlas with several centres and 28 local star loci",
            "medical_reading_de": "lokale Mond-/Sternstationen für Anwendungszeiten",
            "technical_reading_de": "lokale Stern-/Zeitstationen eines Arbeitskalenders",
            "hard_geometry_rule": "kein gemeinsames Zentrum und kein f69-Schlüssel",
        },
        {
            "diagram_id": "A3", "page": "f69v", "loci": "31", "groups": "140",
            "visible_structure": "three disconnected wheels; 28 slots on left only",
            "medical_reading_de": "links Behandlungstermine, Mitte Feuchtigkeitsprognose, rechts Komplexion",
            "technical_reading_de": "links Arbeitstage, Mitte Wetterzustand, rechts Tageslicht/Arbeitszustand",
            "hard_geometry_rule": "keine gemeinsame Richtung; keine 28er-Folge über alle drei Räder",
        },
    ]
    write_tsv("FIVE_HUNDRED_FORTY_THIRD_THREE_DUAL_ASTRO_INSTRUMENTS.tsv", page_rows)

    med_astro = sum(int(row["medical_insertion_cost"]) for row in namespace_rows)
    tech_astro = sum(int(row["technical_insertion_cost"]) for row in namespace_rows)
    prose_total = next(row for row in prose_summary if row["scope"] == "TOTAL")
    combined_rows = [
        {"scope": "PROSE", "medical_insertions": prose_total["medical_insertions"], "technical_insertions": prose_total["technical_insertions"]},
        {"scope": "ASTRO_NAMESPACES", "medical_insertions": str(med_astro), "technical_insertions": str(tech_astro)},
        {"scope": "TEN_PAGE_TOTAL", "medical_insertions": str(int(prose_total["medical_insertions"]) + med_astro), "technical_insertions": str(int(prose_total["technical_insertions"]) + tech_astro)},
    ]
    write_tsv("FIVE_HUNDRED_FORTY_THIRD_TEN_PAGE_PURPOSE_TOTALS.tsv", combined_rows)

    summary = {
        "status": "PASS",
        "namespaces": len(namespace_rows),
        "loci": len(locus_rows),
        "groups": len(group_rows),
        "astro_medical_insertions": med_astro,
        "astro_technical_insertions": tech_astro,
        "astro_medical_wins": sum(row["local_winner"] == "MEDICAL" for row in namespace_rows),
        "astro_technical_wins": sum(row["local_winner"] == "TECHNICAL" for row in namespace_rows),
        "astro_ties": sum(row["local_winner"] == "TIE" for row in namespace_rows),
        "ten_page_medical_insertions": int(combined_rows[-1]["medical_insertions"]),
        "ten_page_technical_insertions": int(combined_rows[-1]["technical_insertions"]),
        "selected_working_purpose": "PRACTICAL_PLANT_MATERIAL_BATHHOUSE_WITH_CELESTIAL_WORK_ALMANAC",
        "f68_f69_joins": 0,
        "prose_card_imports": 0,
    }
    (HERE / "FIVE_HUNDRED_FORTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Fünfhundertdreiundvierzigste Runde: Astro wieder angeschlossen",
        "",
        "## Drei eigenständige Instrumente",
        "",
        "f67r2 bleibt ein Paar unverbundener Himmelsräder, f68r1 ein Mehrpaneel-Sternatlas mit mehreren Zentren, f69v drei getrennte Räder mit 28 Plätzen ausschließlich links. Keine Richtung, kein gemeinsamer Start und kein f68-f69-Schlüssel werden ergänzt.",
        "",
        "## Zweckvergleich",
        "",
        f"Über dreizehn lokale Astro-Namespaces braucht die medizinische Wahlkalenderfassung {med_astro} stille Funktionswörter, der allgemeine Arbeitsalmanach {tech_astro}. Sechs Namespaces sprechen sparsamer technisch, einer medizinisch, sechs bleiben gleich teuer.",
        "",
        "Der medizinische Sondergewinn liegt am rechten Gesicht-/Strahlenrad von f69v: Komplexion ist dort eine natürliche Bildlesung. Der technische Gewinn liegt besonders bei den Arbeitssektoren, Sternstationen, 28 Arbeitstagen und dem Wolken-/Wetterrad.",
        "",
        "## Neue Gesamtarbeitstheorie",
        "",
        f"Prosa und Astro zusammen benötigen medizinisch {summary['ten_page_medical_insertions']} und technisch {summary['ten_page_technical_insertions']} stille Zweckwörter. Die beste zehnseitige Arbeitstheorie ist deshalb jetzt: ein illustriertes Pflanzenmaterial- und Nasswerkstattbuch mit Badehaus-/Anwendungsstationen und einem getrennten Himmels-/Arbeitsalmanach. Einzelne Anwendungen können medizinisch sein; das ganze Buch muss es nicht sein.",
        "",
        "## Nächster Angriff",
        "",
        "Als Nächstes entsteht eine vollständige zehnseitige Lesefassung dieser neuen Arbeitstheorie: vier Pflanzenartikel, sechs Biological-Records und drei lokale Astro-Instrumente, mit unserem kompositionellen Wörterbuch und ohne leere Sequenzen.",
    ]
    (HERE / "FIVE_HUNDRED_FORTY_THIRD_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
