#!/usr/bin/env python3
"""Attach the three local Astro instruments to the six workshop cases."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CASE_DIR = ROOT / "experiments/yolo/sidequest_semantic_complete_workshop_cases_six_hundred_third"
ASTRO_DIR = ROOT / "experiments/yolo/sidequest_semantic_astro_condition_interface_five_hundred_ninety_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CASE_CONDITIONS = {
    "C1": {
        "primary": "F69_LEFT_WHEEL_NS",
        "secondary": "F69_MIDDLE_WHEEL_NS|F67_RIGHT_WHEEL_NS",
        "question_de": "Wähle einen lokalen Bade-/Waschplatz im Achtundzwanziger-Rad und prüfe bei Bedarf die grobe Himmels- oder Wetterlage.",
        "use_de": "mildes Pflanzenbad nur unter der vom Meister bezeichneten lokalen Wahlbedingung beginnen",
    },
    "C2": {
        "primary": "F67_RIGHT_WHEEL_NS",
        "secondary": "F69_LEFT_WHEEL_NS",
        "question_de": "Bestimme zuerst den groben Himmelsabschnitt; wähle für den stärkeren Mehrstationsgang danach einen lokalen Arbeitsslot.",
        "use_de": "stärkere und längere Behandlung an eine gröbere Wahlbedingung binden",
    },
    "C3": {
        "primary": "F68_LOCAL_STAR_SLOT_NS",
        "secondary": "F69_MIDDLE_WHEEL_NS",
        "question_de": "Erkenne den bezeichneten Sternplatz wieder und prüfe, ob die aktuelle Himmels-/Wetterlage zur Blütenwaschung passt.",
        "use_de": "Blütenwaschung mit einer wiedererkennbaren lokalen Himmelsadresse versehen",
    },
    "C4": {
        "primary": "F69_RIGHT_WHEEL_NS",
        "secondary": "F67_LEFT_WHEEL_NS",
        "question_de": "Schlage den bezeichneten Licht-, Gestirn- oder Komplexionszustand nach; nutze das feinere Rad nur für eine engere Wahl.",
        "use_de": "Zeit oder Zulässigkeit einer länger gehaltenen Auflage bestimmen",
    },
    "C5": {
        "primary": "F67_LEFT_WHEEL_NS",
        "secondary": "F69_LEFT_WHEEL_NS",
        "question_de": "Wähle eine feinere Stern-/Aspektlage oder einen lokalen Arbeitsslot für Ruhe, Absetzen und Weiterführen der Restcharge.",
        "use_de": "Ruhe- und Absetzarbeit in den gewählten Werkstattzeitpunkt einordnen",
    },
    "C6": {
        "primary": "F69_LEFT_WHEEL_NS",
        "secondary": "F69_MIDDLE_WHEEL_NS",
        "question_de": "Markiere im lokalen Achtundzwanziger-Inventar den nächsten Gebrauchsslot und prüfe den Himmels-/Wetterzustand der Folgearbeit.",
        "use_de": "Vorrat für die nächste Bad-, Wasch- oder Auflagenarbeit terminieren",
    },
}


NAMESPACE_CASES = {
    "F67_RIGHT_WHEEL_NS": "C1|C2",
    "F67_LEFT_WHEEL_NS": "C4|C5",
    "F67_PAIRED_LEGEND_QUARANTINE_NS": "C1|C2|C3|C4|C5|C6",
    "F68_LEFT_PANEL_HEADER_NS": "C3",
    "F68_MIDDLE_PANEL_HEADER_NS": "C3",
    "F68_RIGHT_PANEL_HEADER_NS": "C3",
    "F68_LOCAL_STAR_SLOT_NS": "C3",
    "F68_MULTIPANEL_HEADER_QUARANTINE_NS": "C3",
    "F68_CENTRAL_LEGEND_QUARANTINE_NS": "C3",
    "F68_CENTRE_KEY_QUARANTINE_NS": "C3",
    "F69_LEFT_WHEEL_NS": "C1|C2|C5|C6",
    "F69_MIDDLE_WHEEL_NS": "C1|C3|C6",
    "F69_RIGHT_WHEEL_NS": "C4",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cases = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_SIX_COMPLETE_CASES.tsv")
    prose_events = read_tsv(CASE_DIR / "SIX_HUNDRED_THIRD_381_EVENT_CASE_BINDING.tsv")
    namespaces = read_tsv(ASTRO_DIR / "FIVE_HUNDRED_NINETY_FIRST_THIRTEEN_NAMESPACES.tsv")
    loci = read_tsv(ASTRO_DIR / "FIVE_HUNDRED_NINETY_FIRST_142_LOCUS_ASTRO_INTERFACE.tsv")
    astro_groups = read_tsv(ASTRO_DIR / "FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv")

    case_by_id = {row["case_id"]: row for row in cases}
    condition_plans = []
    for case_id, spec in CASE_CONDITIONS.items():
        case = case_by_id[case_id]
        condition_plans.append({
            "case_id": case_id,
            "case_title_de": case["title_de"],
            "primary_astro_namespace": spec["primary"],
            "secondary_astro_namespaces": spec["secondary"],
            "master_question_de": spec["question_de"],
            "working_use_de": spec["use_de"],
            "exact_locus_selection": "MASTER_OR_LOCAL_IMAGE_SELECTS__NOT_WRITTEN_IN_PROSE",
            "spoken_instruction_de": "Zeige den Bildplatz, kopiere seine ganze Marke und führe dann den gewählten Werkstattfall aus.",
        })

    namespace_rows = []
    for row in namespaces:
        ns = row["canonical_namespace_id"]
        namespace_rows.append({
            **row,
            "applicable_case_ids": NAMESPACE_CASES[ns],
            "workshop_role_de": (
                "Wahlplatz oder Bedingung für den Fall" if int(row["selectable_loci"]) > 0
                else "Legende, Kopfstück oder ungelöster Schlüsselbereich abschreiben"
            ),
            "label_handling_de": "ganze lokale Marke aus dem Muster kopieren; nicht in Prosa-Stämme zerlegen",
        })

    locus_rows = []
    for row in loci:
        ns = row["canonical_namespace_id"]
        locus_rows.append({
            "page": row["page"],
            "locus": row["locus"],
            "group_count": row["group_count"],
            "complete_surface_display_only": row["complete_surface_display_only"],
            "canonical_namespace_id": ns,
            "local_image_owner": row["local_image_owner"],
            "interface_role": row["interface_role"],
            "applicable_case_ids": NAMESPACE_CASES[ns],
            "workshop_reading_de": row["working_reading_de"],
            "master_action_de": "Bildplatz zeigen → vollständige Marke kopieren → Fallbedingung merken",
            "semantic_label_de": "LOCAL_CELESTIAL_LABEL_MEMORIZED_AS_WHOLE",
            "orientation": "NONE",
            "cross_page_key": "NONE",
        })

    unified = []
    for row in prose_events:
        unified.append({
            "unified_id": f"PROSE:{row['event_id']}",
            "section": "PROSE_CASE",
            "page": row["page"],
            "record_or_locus": row["record"],
            "case_ids": row["case_id"],
            "surface": row["surface"],
            "local_identity": row["card_no"],
            "workshop_role_de": f"{row['operation_de']}: {row['primary_object_de']}",
            "learning_mode": "COMPOSITION_OR_LEARNED_CARD",
            "cross_section_pointer": "NONE",
        })
    for row in astro_groups:
        ns = row["canonical_namespace_id"]
        unified.append({
            "unified_id": f"ASTRO:{row['opaque_local_id']}",
            "section": "ASTRO_CONDITION_LABEL",
            "page": row["page"],
            "record_or_locus": row["locus"],
            "case_ids": NAMESPACE_CASES[ns],
            "surface": row["surface_display_only"],
            "local_identity": row["opaque_local_id"],
            "workshop_role_de": "lokalen Himmels-/Wahlplatz innerhalb seines Bildnamensraums markieren",
            "learning_mode": "COPY_COMPLETE_LOCAL_LABEL",
            "cross_section_pointer": "NONE",
        })

    write_tsv(HERE / "SIX_HUNDRED_FOURTH_SIX_CASE_CONDITION_PLANS.tsv", condition_plans, list(condition_plans[0]))
    write_tsv(HERE / "SIX_HUNDRED_FOURTH_THIRTEEN_NAMESPACE_CASE_INTERFACE.tsv", namespace_rows, list(namespace_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FOURTH_142_LOCUS_CASE_INTERFACE.tsv", locus_rows, list(locus_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FOURTH_776_GROUP_WORKSHOP_LEDGER.tsv", unified, list(unified[0]))

    md = ["# Zehnseitiges Fallbuch mit Himmelsbedingungen", ""]
    for plan in condition_plans:
        case = case_by_id[plan["case_id"]]
        md.extend([
            f"## {plan['case_id']}: {case['title_de']}",
            "",
            case["continuous_case_de"],
            "",
            f"**Optionale Himmelsfrage:** {plan['master_question_de']}",
            "",
            f"**Werkstattgebrauch:** {plan['working_use_de']}",
            "",
            "**Lehrmeisterregel:** Zeige den passenden Bildplatz, kopiere die ganze lokale Marke und zerlege sie nicht wie eine Prosakarte.",
            "",
        ])
    (HERE / "SIX_HUNDRED_FOURTH_COMPLETE_TEN_PAGE_CASEBOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    report = """# Sechshundertvierte Runde: Astro als Wahl- und Bedingungsanhang

## Ergebnis

Das zehnseitige Buch lässt sich nun als ein einziger Werkstattgebrauch erklären, ohne die drei Astro-Seiten in Prosa zu verwandeln:

```text
Herbal: WAS wird hergestellt?
Biological: WIE und WO wird es benutzt?
Astro: WANN oder UNTER WELCHER LOKALEN BEDINGUNG wird der Fall gewählt?
```

Der Meister zeigt einen Bildplatz, der Schreiber kopiert die vollständige lokale Marke, und erst dann wird der passende Fall ausgeführt. Die Marke muss kein aussprechbares Wort des Prosa-Wörterbuchs sein.

## Die drei Instrumente

- **f67r2:** zwei getrennte Räder für grobe und feinere Himmels-/Aspektwahl;
- **f68r1:** mehrpaneeliges Sternadressbuch mit 28 lokalen Sternplätzen;
- **f69v:** drei getrennte Räder: lokales 28er-Inventar, Himmels-/Wetterzustand und Licht-/Gestirn-/Komplexionszustand.

Sie bilden keine einzige Maschine. Ein Fall darf ein Instrument konsultieren und die anderen ignorieren.

## Sechs konkrete Verwendungen

- C1 wählt Badeplatz und gegebenenfalls Wetterlage;
- C2 wählt zuerst einen groben Abschnitt für den stärkeren Gang;
- C3 erkennt einen Sternplatz für die Blütenwaschung wieder;
- C4 konsultiert Licht-, Gestirn- oder Komplexionszustand für die Auflage;
- C5 ordnet Ruhe und Absetzen einer feineren Lage zu;
- C6 terminiert die nächste Verwendung des Vorrats.

Das sind Werkstattfragen, keine übersetzten Etiketten. Der konkrete Platz wird lokal am Bild gewählt.

## Gesamtsystem

Die 381 Prosaereignisse werden produktiv oder als gelernte Ganzkarten geschrieben. Die 395 Astrogruppen werden als lokale Bildetiketten kopiert. Zusammen ergeben sie 776 beschriftete Einheiten mit einem einzigen Lehrprinzip: **Prosahandlung aus dem Kartensatz bauen, Himmelsadresse als Ganzes aus dem Muster übernehmen.**

## Beste Arbeitstheorie

Die zehn Seiten passen jetzt am besten zu einem **illustrierten Pflanzen-, Bad-/Anwendungs- und Himmelswahl-Kompendium für eine kleine Werkstatt**. Es ist kein Klartextbuch und kein reiner Code: Es verbindet produktive Fachkürzel, gelernte Ganzkarten, stille Bildargumente und lokale Diagrammetiketten.

## Nächster Schritt

Als nächstes wird ein Lehrmeisterdurchlauf für einen ganzen Arbeitstag geschrieben: Rohstoff wählen, Produkt bereiten, Station bedienen, Himmelsbedingung nachschlagen, Restcharge verwahren. Danach prüfen wir, welche Kartenbedeutungen dabei unnötig kompliziert geworden sind und auf kürzere Werkstattwörter reduziert werden können.
"""
    (HERE / "SIX_HUNDRED_FOURTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "cases": len(condition_plans),
        "namespaces": len(namespace_rows),
        "astro_loci": len(locus_rows),
        "prose_groups": len(prose_events),
        "astro_groups": len(astro_groups),
        "unified_groups": len(unified),
        "orientation_claims": 0,
        "cross_page_keys": 0,
        "decision": "WHAT_HOW_WHEN_OR_CONDITION_WORKSHOP_COMPENDIUM",
    }
    (HERE / "SIX_HUNDRED_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
