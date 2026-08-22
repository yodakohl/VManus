#!/usr/bin/env python3
"""Build the bounded V76 R3 dual-purpose competition.

This is a creative ten-page working model.  It does not decode any Voynich
form.  Unit counts and owner strings are imported only from the frozen central
V73--V75 selections; all purpose readings below are occurrence-bound rival
expansions over those same units.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent

HERBAL = YOLO / "sidequest_theory_candidates_v73" / "V73_SELECTED_FIVE_ARTICLES.tsv"
BIO = YOLO / "sidequest_theory_candidates_v74" / "V74_SELECTED_SIX_RECORD_EDITION.tsv"
ASTRO = YOLO / "sidequest_theory_candidates_v75" / "V75_SELECTED_THREE_INSTRUMENTS.tsv"
ASTRO_NS = YOLO / "sidequest_theory_candidates_v75" / "V75_SELECTED_NAMESPACE_REGISTRY.tsv"

MEDICAL = "ILLUSTRATED_IATROMEDICAL_COMPENDIUM"
NONMEDICAL = "ILLUSTRATED_MATERIAL_BATHHOUSE_AND_CELESTIAL_WORK_ALMANAC"
FORMAL_RIVAL = "IMAGE_ADDRESSED_PATTERN_AND_EXEMPLAR_MISCELLANY"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pipe_count(value: str) -> int:
    return 0 if not value or value == "NONE" else len(value.split("|"))


def local_score(values: dict[str, int]) -> int:
    return (
        2 * values["image_fit"]
        + 2 * values["owner_fit"]
        + 2 * values["local_fit"]
        + 2 * values["purpose_fit"]
        + values["period_fit"]
        - 2 * values["unsupported_cost"]
        - 2 * values["geometry_cost"]
        - 4 * values["attestation_cost"]
    )


HERBAL_READINGS = {
    "H1": (
        "Unbenannter Ganzpflanzenartikel: Wurzelanteil, waessriger Auszug, kleines Gebrauchsmaß und Verwahrung.",
        "Pflanzenmaterial-Los: Wurzelbestand reinigen, schneiden, mit Wasser ausziehen, Pruefportion buchen und Rest lagern.",
    ),
    "H2": (
        "Unbenannter Ganzpflanzenartikel: junge Spitzen zweier Erntezustaende, Pressfraktionen, Oelzubereitung und aeusserer Gebrauch.",
        "Zwei Erntelose: Spitzen pressen, Fraktionen vergleichen oder vereinigen und als Materialprobe konservieren.",
    ),
    "H3": (
        "Unbenannter Ganzpflanzenartikel: Blueten und junge Blaetter extrahieren, klaeren, einen Anteil als Trank und einen als aeusseres Oel fuehren.",
        "Blueten- und Blattfraktionen extrahieren, klaeren und getrennt als Referenz- oder Vorratsproben lagern.",
    ),
    "H4": (
        "Unbenannter Ganzpflanzenartikel: Blattmazerat als Waschmittel und zweiter Blattanteil als warmer Auftrag.",
        "Zwei Blattlose mazerieren, waschen, vergleichen und als Arbeits- oder Vorratsposten lagern.",
    ),
    "H5": (
        "Unbenannter Ganzpflanzenartikel: frische klebrige Blaetter aeusserlich gebrauchen; bluehende Stiele trocknen und schwach ausziehen.",
        "Kopf-, Blatt- und Krautfraktionen als klebrige Probe, Trockenlos und schwachen Auszug fuehren.",
    ),
}

BIO_READINGS = {
    "B1": (
        "Gemeinsames balneologisches Regimen fuer das zweireihige Figurenfeld; Reihen sind keine Zeitfolge.",
        "Badehaus-Charge fuer das zweireihige Beckenfeld bereitstellen, bemessen, temperieren, waschen, spuelen, absetzen und schliessen.",
    ),
    "B2": (
        "Lokaler Katalog therapeutischer Becken-, Bade-, Ruhe- und Anwendungsstationen mit Reset an jedem Besitzerwechsel.",
        "Badehaus-/Waschhaus-Konfigurationsregister fuer Paarbecken, Mittelgeraet, ungeklaerte Station, unteren Pool und Randposten.",
    ),
    "B3": (
        "Drei lokale Behandlungsstationen, ungeklaerte Zone und danach das sichtbar gekoppelte Hauptpaar; keine Therapie kreuzt die Luecke.",
        "Drei lokale Bedienposten, Quarantaenezone und gekoppeltes Hauptpaar; Stoff und Arbeitsstand werden an der Luecke geloescht.",
    ),
    "B4": (
        "Lokale Wasch-/Auflagehandlungen am Hauptpaar sowie getrennte Anwendungen am linken und rechten Endposten.",
        "Betriebsbuchungen fuer Hauptpaar, offenen Fransenposten und S-Lauf-/Mehrarmknoten; keine gemeinsame Richtung.",
    ),
    "B5": (
        "Kurzer eigenstaendiger Waerme-, Maß- und Zielnachtrag an einer lokalen Anwendungsstation.",
        "Kurzer eigenstaendiger Einrichtungs- und Maßnachtrag am linken offenen Endposten.",
    ),
    "B6": (
        "Kurzer eigenstaendiger Zubereitungs-/Filternachtrag an einer lokalen Anwendungsstation.",
        "Kurzer eigenstaendiger Einrichtungs-, Maß- und Filternachtrag am rechten Mehrarm-Endposten.",
    ),
}

ASTRO_READINGS = {
    "A1": (
        "Zwei getrennte iatromathematische Nachschlageraeder fuer lokale Himmelsbedingungen und Wahl-/Meidungshinweise; kein Zwischenradschluessel.",
        "Zwei getrennte astronomische Arbeitsraeder fuer Sektor-, Kalender-, Phasen- und Beobachtungsnotizen; keine medizinische Wahlfunktion noetig.",
    ),
    "A2": (
        "Mehrpaneeliger Sternatlas mit lokal kopierten Himmelsbedingungen fuer eine moegliche iatromathematische Konsultation; keine seitenweite Ordnung.",
        "Mehrpaneeliger Sternatlas fuer lokale Sternfeld-, Stations- oder Kalendernachschlaege; die 28 Plaetze bleiben ungeordnet.",
    ),
    "A3": (
        "Drei getrennte Raeder fuer lokal kopierte Wahl-, Prognose- oder Komplexionshinweise; nur links ein ungeordnetes 28er-Inventar.",
        "Drei getrennte Kalender-, Beobachtungs- oder Qualitaetsraeder; nur das linke besitzt 28 lokale Radialplaetze.",
    ),
}


def unit_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in read_tsv(HERBAL):
        unit = source["record_unit_id"]
        count = pipe_count(source["event_serials"])
        med, nonmed = HERBAL_READINGS[unit]
        base = {
            "unit_id": unit,
            "section": "HERBAL",
            "page": source["page"],
            "group_count": count,
            "locus_or_field_count": pipe_count(source["field_ids"]),
            "statement_or_namespace_count": pipe_count(source["statement_ids"]),
            "smallest_owner_or_namespace": source["whole_plant_owner"],
            "owner_guard": "WHOLE_PLANT_PAGE_OWNER_ONLY__NO_PART_LEADER_LINES",
            "shared_formal_machine": "WHOLE_PLANT_OWNER > RECORD_LOCAL_CARD_SEQUENCE > CLOSE/RESET",
            "medical_reading": med,
            "nonmedical_reading": nonmed,
            "strongest_formal_rival": FORMAL_RIVAL,
            "strongest_contradiction": source["strongest_contradiction"],
        }
        add_scores(rows, base, med_values=(4, 4, 4, 4, 4, 4, 0, 0), non_values=(4, 4, 4, 3, 4, 3, 0, 0))

    for source in read_tsv(BIO):
        unit = source["record_unit_id"]
        count = pipe_count(source["event_serials"])
        med, nonmed = BIO_READINGS[unit]
        owners = source["local_owner_sequence"]
        base = {
            "unit_id": unit,
            "section": "BIOLOGICAL",
            "page": source["page"],
            "group_count": count,
            "locus_or_field_count": pipe_count(source["field_ids"]),
            "statement_or_namespace_count": pipe_count(source["statement_ids"]),
            "smallest_owner_or_namespace": owners,
            "owner_guard": "LOCAL_CONTACT_OWNER__RESET_AT_VISIBLE_BREAK__NO_GLOBAL_FLOW",
            "shared_formal_machine": "LOCAL_STATION_OWNER > ACTIVE/PREVIOUS/TARGET REGISTERS > RESET/CLOSE",
            "medical_reading": med,
            "nonmedical_reading": nonmed,
            "strongest_formal_rival": FORMAL_RIVAL,
            "strongest_contradiction": source["strongest_contradiction"],
        }
        add_scores(rows, base, med_values=(4, 4, 4, 4, 4, 3, 0, 0), non_values=(4, 4, 4, 3, 4, 2, 0, 0))

    ns_by_page: dict[str, list[str]] = {}
    for ns in read_tsv(ASTRO_NS):
        ns_by_page.setdefault(ns["page"], []).append(ns["namespace_id"])
    for source in read_tsv(ASTRO):
        unit = source["diagram_id"]
        med, nonmed = ASTRO_READINGS[unit]
        page = source["page"]
        base = {
            "unit_id": unit,
            "section": "ASTRO",
            "page": page,
            "group_count": int(source["group_count"]),
            "locus_or_field_count": int(source["locus_count"]),
            "statement_or_namespace_count": len(ns_by_page[page]),
            "smallest_owner_or_namespace": "|".join(ns_by_page[page]),
            "owner_guard": "PAGE_LOCAL_NAMESPACE__NO_SELECTED_START_DIRECTION_OR_CROSSPAGE_KEY",
            "shared_formal_machine": "LOCAL_DIAGRAM_NAMESPACE > EXACT_COPY_SEGMENT > NAMESPACE_RESET",
            "medical_reading": med,
            "nonmedical_reading": nonmed,
            "strongest_formal_rival": FORMAL_RIVAL,
            "strongest_contradiction": source["strongest_counterevidence"],
        }
        add_scores(rows, base, med_values=(4, 4, 3, 4, 4, 4, 0, 0), non_values=(4, 4, 4, 3, 4, 3, 0, 0))
    return rows


def add_scores(
    rows: list[dict[str, object]],
    base: dict[str, object],
    med_values: tuple[int, int, int, int, int, int, int, int],
    non_values: tuple[int, int, int, int, int, int, int, int],
) -> None:
    labels = ("image_fit", "owner_fit", "local_fit", "purpose_fit", "period_fit", "unsupported_cost", "geometry_cost", "attestation_cost")
    med = dict(zip(labels, med_values))
    non = dict(zip(labels, non_values))
    med_score = local_score(med)
    non_score = local_score(non)
    row = dict(base)
    for label in labels:
        row[f"medical_{label}_0_4"] = med[label]
        row[f"nonmedical_{label}_0_4"] = non[label]
    row["medical_local_score"] = med_score
    row["nonmedical_local_score"] = non_score
    row["local_score_lead"] = "TIE" if med_score == non_score else (MEDICAL if med_score > non_score else NONMEDICAL)
    row["portable_dictionary_status"] = "NO_PORTABLE_GLOSS_ASSERTED__EXEMPLAR_VALUE_UNKNOWN"
    row["interpretation_ceiling"] = "PURPOSE_MODEL_ONLY__NO_WORD_STEM_SOUND_LANGUAGE_OR_DECIPHERMENT"
    rows.append(row)


RUBRIC = [
    ("R01", "VISIBLE_SECTION_FIT", "BENEFIT", 3, 4, 4, "Both models accept whole plants, local figure/apparatus stations and celestial diagrams as drawn."),
    ("R02", "FORMAL_OWNER_COVERAGE", "BENEFIT", 3, 4, 4, "Both cover all 776 groups through exactly the same frozen owners and namespaces."),
    ("R03", "LOCAL_EXECUTABILITY", "BENEFIT", 2, 3, 4, "The operational rival needs fewer unshown indications; the medical model remains executable only through exemplar expansion."),
    ("R04", "CROSS_SECTION_PURPOSE_COHESION", "BENEFIT", 4, 4, 2, "Materia medica, balneology and celestial election form a tighter single-purpose chain than material lots, bathhouse operation and astronomy."),
    ("R05", "PICTURE_FIRST_COMPILATION_FIT", "BENEFIT", 2, 4, 4, "Both naturally permit image planning before text was fitted into residual spaces."),
    ("R06", "MULTIPLE_HAND_WORKSHOP_FIT", "BENEFIT", 1, 4, 4, "Both permit section/quire division among trained hands using one formal copying discipline."),
    ("R07", "MASTER_EXEMPLAR_ECONOMY", "BENEFIT", 2, 3, 3, "Both require lost exemplar values; neither recovers concrete content from group form."),
    ("R08", "USER_PROFILE_PLAUSIBILITY", "BENEFIT", 2, 3, 3, "A medical compiler/bath practitioner and an institutional workshop/bathhouse steward are both practical users, but neither is pictured or named."),
    ("R09", "UNSUPPORTED_CONTENT_BURDEN", "COST", 4, 4, 3, "Medical readings add indications, therapeutic valency and election; the rival adds plant-material and work-scheduling functions."),
    ("R10", "GEOMETRY_OVERRIDE_BURDEN", "COST", 4, 0, 0, "Both obey the V74 contact graph and V75 namespace/orientation guards."),
    ("R11", "UNATTESTED_PORTABLE_GLOSS_BURDEN", "COST", 8, 0, 0, "Neither model promotes a word; all concrete content remains occurrence-bound exemplar prose."),
    ("R12", "MIXED_MISCELLANY_BURDEN", "COST", 1, 1, 3, "The nonmedical book needs a broader institutional miscellany; the medical model needs less genre breadth."),
]


def rubric_rows() -> list[dict[str, object]]:
    result = []
    for rid, criterion, polarity, weight, med, non, reason in RUBRIC:
        sign = 1 if polarity == "BENEFIT" else -1
        result.append(
            {
                "rubric_id": rid,
                "criterion": criterion,
                "polarity": polarity,
                "weight": weight,
                "medical_score_0_4": med,
                "nonmedical_score_0_4": non,
                "medical_weighted_contribution": sign * weight * med,
                "nonmedical_weighted_contribution": sign * weight * non,
                "symmetric_reason": reason,
                "epistemic_status": "CREATIVE_PURPOSE_COMPARISON_NOT_EMPIRICAL_LIKELIHOOD",
            }
        )
    return result


def graph_rows(units: list[dict[str, object]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []

    def add(scope: str, source: str, target: str, relation: str, visibility: str, guard: str) -> None:
        result.append(
            {
                "edge_id": f"E{len(result)+1:03d}",
                "model_scope": scope,
                "source_node": source,
                "target_node": target,
                "relation": relation,
                "edge_status": visibility,
                "guard_or_reset": guard,
                "semantic_status": "FORMAL_OR_PURPOSE_LEVEL_ONLY__NO_CARD_GLOSS",
            }
        )

    add("SHARED_PRODUCTION", "LAYOUT_PLAN", "LARGE_IMAGE_OR_DIAGRAM", "DRAW_BEFORE_TEXT", "INFERRED_FROM_TEXT_REFLOW", "DOES_NOT_PROVE_TEXT_SEMANTICS")
    add("SHARED_PRODUCTION", "LARGE_IMAGE_OR_DIAGRAM", "LOCAL_OWNER_OR_NAMESPACE", "ASSIGN_SMALLEST_VISIBLE_OWNER", "FROZEN_V70_V71", "RESET_AT_TRUE_IMAGE_BREAK")
    add("SHARED_PRODUCTION", "MASTER_EXEMPLAR", "OPAQUE_ENTRY_SEQUENCE", "SELECT_AND_COPY_LOCAL_SOURCE_ENTRY", "REQUIRED_INFERENCE", "CONCRETE_VALUE_UNRECOVERED")
    add("SHARED_PRODUCTION", "LOCAL_OWNER_OR_NAMESPACE", "OPAQUE_ENTRY_SEQUENCE", "SET_SILENT_ARGUMENT_OR_ADDRESS", "EXECUTABLE_FORMAL_RULE", "OWNER_IS_NOT_PROVEN_REFERENT")
    add("SHARED_PRODUCTION", "OPAQUE_ENTRY_SEQUENCE", "RESIDUAL_PAGE_SPACE", "FIT_TEXT_AROUND_PRIOR_IMAGE", "VISIBLE_LAYOUT_COMPATIBLE", "PHYSICAL_LINE_NOT_STATEMENT_BOUNDARY")
    add("SHARED_PRODUCTION", "SHARED_FORMAL_CODEBOOK", "SECTION_LOCAL_HAND_RENDERER", "TEACH_COPYING_DISCIPLINE", "WORKSHOP_HYPOTHESIS", "MULTIPLE_HANDS_DO_NOT_PROVE PURPOSE")
    add("SHARED_PRODUCTION", "TRUE_OWNER_BREAK", "ACTIVE_PREVIOUS_TARGET_REGISTERS", "RESET", "FROZEN_V74", "NO_STUFF_OR_DIRECTION_INHERITANCE")
    add("SHARED_PRODUCTION", "ASTRO_NAMESPACE_BREAK", "ASTRO_LOCAL_STATE", "RESET", "FROZEN_V75", "NO_CROSSWHEEL_OR_CROSSPAGE_KEY")

    for row in units:
        add("SHARED_OWNERSHIP", str(row["smallest_owner_or_namespace"]), str(row["unit_id"]), "OWNS_ALL_LISTED_GROUPS_IN_UNIT", "FROZEN_CENTRAL_SELECTION", str(row["owner_guard"]))

    add(MEDICAL, "HERBAL_UNITS_H1_H5", "BIO_UNITS_B1_B6", "SIMPLES_AND_PREPARATIONS_TO_BALNEOLOGICAL_USE", "PURPOSE_HYPOTHESIS", "NO_CARD_VALUE_TRANSFER")
    add(MEDICAL, "BIO_UNITS_B1_B6", "ASTRO_UNITS_A1_A3", "TREATMENT_TO_CELESTIAL_ELECTION_OR_AVOIDANCE", "PURPOSE_HYPOTHESIS", "NO_VISIBLE_CROSS_SECTION_KEY")
    add(NONMEDICAL, "HERBAL_UNITS_H1_H5", "BIO_UNITS_B1_B6", "PLANT_MATERIAL_PREPARATION_TO_BATHHOUSE_OR_WORKSHOP_OPERATION", "PURPOSE_HYPOTHESIS", "NO_CARD_VALUE_TRANSFER")
    add(NONMEDICAL, "BIO_UNITS_B1_B6", "ASTRO_UNITS_A1_A3", "FACILITY_OPERATION_TO_CALENDAR_OR_OBSERVATION_SCHEDULING", "PURPOSE_HYPOTHESIS", "NO_VISIBLE_CROSS_SECTION_KEY")
    add("DEEP_RIVAL", "TEN_PAGE_IMAGE_SET", FORMAL_RIVAL, "LOCAL_PATTERN_OR_EXEMPLAR_ADDRESSING_WITHOUT_SINGLE_CONTENT_PURPOSE", "OPEN_RIVAL", "EXPLAINS_FORM_BUT_WEAKENS_CONTENT_COHESION")
    return result


CONTRADICTIONS = [
    ("C01", "ALL", "No exact card, stem, sound or language value is confirmed.", "BOTH", "Keep all values occurrence-bound and exemplar-supplied.", "OPEN_HARD_CEILING"),
    ("C02", "ALL", "The master exemplar is absent; 776/776 concrete group values remain unrecovered from form alone.", "BOTH", "Purpose comparison may use content classes, never portable glosses.", "OPEN_HARD_CEILING"),
    ("C03", "HERBAL", "The four drawings show no vessel, liquid, dose, disease or application.", "BOTH", "Treat preparation and use as invisible exemplar hypotheses.", "OPEN"),
    ("C04", "HERBAL", "No plant species identification survives V70.", "BOTH", "Use only unnamed whole-plant owners.", "RESOLVED_BY_QUARANTINE"),
    ("C05", "BIOLOGICAL", "Sixteen local owners do not form one connected or directed machine.", "BOTH", "Enforce V74 contact/reset graph; do not inherit flow.", "RESOLVED_BY_CONTRACT"),
    ("C06", "BIOLOGICAL", "Thirty-two events occupy unresolved-owner zones and four statements cross visible breaks.", "BOTH", "Quarantine gaps and split literal readings at the owner break.", "RESOLVED_BY_CONTRACT"),
    ("C07", "BIOLOGICAL", "Naked figures support bathing/application more directly than an abstract industrial machine.", "NONMEDICAL", "Use bathhouse/washhouse operation, not an unpictured factory.", "OPEN_COST"),
    ("C08", "ASTRO", "No common start, direction or rotation is visible.", "BOTH", "Leave all 36 V75 alternatives unselected.", "RESOLVED_BY_CONTRACT"),
    ("C09", "ASTRO", "f68r1 and f69v have no visible cross-page key.", "BOTH", "Keep all 13 namespaces page-local.", "RESOLVED_BY_CONTRACT"),
    ("C10", "ASTRO", "Celestial imagery supports astronomy but not a medical election function.", "MEDICAL", "Iatromathematical use remains exemplar-level only.", "OPEN_COST"),
    ("C11", "PRODUCTION", "Text fitted around pictures may reflect space management alone.", "BOTH", "Picture-first order does not prove image-to-text reference.", "OPEN"),
    ("C12", "PRODUCTION", "Multiple hands may mark quire division rather than one workshop purpose.", "BOTH", "Use multiple hands only to test teachability of the copying rule.", "OPEN"),
    ("C13", "PURPOSE", "The ten pages may be a compiled miscellany rather than one integrated book purpose.", "BOTH", "Retain the formal pattern/exemplar miscellany as deepest rival.", "OPEN"),
    ("C14", "CODEBOOK", "Old mnemonics lack qualifying 1370--1450 codebook attestations.", "BOTH", "Label them PROVISIONAL_UNATTESTED_MNEMONIC or FORMAL_LABEL_NOT_WORD.", "RESOLVED_BY_RULE"),
]


def contradiction_rows() -> list[dict[str, object]]:
    return [
        {
            "contradiction_id": cid,
            "scope": scope,
            "counterevidence": text,
            "burdens_model": model,
            "required_guard_or_repair": repair,
            "status": status,
            "semantic_ceiling": "NO_PURPOSE_DECISION_FROM_THIS_ROW_ALONE",
        }
        for cid, scope, text, model, repair, status in CONTRADICTIONS
    ]


def main() -> None:
    units = unit_rows()
    assert len(units) == 14
    assert sum(int(row["group_count"]) for row in units) == 776
    assert sum(int(row["group_count"]) for row in units if row["section"] == "HERBAL") == 100
    assert sum(int(row["group_count"]) for row in units if row["section"] == "BIOLOGICAL") == 281
    assert sum(int(row["group_count"]) for row in units if row["section"] == "ASTRO") == 395

    unit_fields = list(units[0])
    write_tsv(HERE / "V76_R3_14_UNIT_DUAL_PURPOSE.tsv", units, unit_fields)

    rubric = rubric_rows()
    write_tsv(HERE / "V76_R3_SYMMETRIC_PURPOSE_RUBRIC.tsv", rubric, list(rubric[0]))

    graph = graph_rows(units)
    write_tsv(HERE / "V76_R3_PROCESS_OWNERSHIP_GRAPH.tsv", graph, list(graph[0]))

    contradictions = contradiction_rows()
    write_tsv(HERE / "V76_R3_CONTRADICTIONS.tsv", contradictions, list(contradictions[0]))

    medical_local = sum(int(row["medical_local_score"]) for row in units)
    nonmedical_local = sum(int(row["nonmedical_local_score"]) for row in units)
    medical_global = sum(int(row["medical_weighted_contribution"]) for row in rubric)
    nonmedical_global = sum(int(row["nonmedical_weighted_contribution"]) for row in rubric)
    outputs = [
        "V76_R3_14_UNIT_DUAL_PURPOSE.tsv",
        "V76_R3_SYMMETRIC_PURPOSE_RUBRIC.tsv",
        "V76_R3_PROCESS_OWNERSHIP_GRAPH.tsv",
        "V76_R3_CONTRADICTIONS.tsv",
    ]
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in outputs}
    summary = {
        "round": "V76_R3",
        "status": "BUILT",
        "scope": {"pages": 10, "units": 14, "groups": 776, "herbal": 100, "biological": 281, "astro": 395},
        "medical_model": MEDICAL,
        "nonmedical_model": NONMEDICAL,
        "deep_formal_rival": FORMAL_RIVAL,
        "local_unit_score_totals": {"medical": medical_local, "nonmedical": nonmedical_local},
        "whole_book_rubric_totals": {"medical": medical_global, "nonmedical": nonmedical_global},
        "decision": "PURPOSE_UNRESOLVED__NONMEDICAL_LOCAL_ECONOMY__MEDICAL_CROSS_SECTION_COHESION",
        "portable_dictionary_words_added": 0,
        "confirmed_translations_added": 0,
        "sealed": ["f84", "f84r"],
        "source_files": [str(path.relative_to(YOLO.parent.parent)) for path in (HERBAL, BIO, ASTRO, ASTRO_NS)],
        "output_sha256": hashes,
    }
    (HERE / "V76_R3_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
