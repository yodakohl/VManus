#!/usr/bin/env python3
"""Build V76 R1 historical book-purpose competition over the frozen 14 units."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"
V75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"
RULE = ROOT / "experiments/yolo/SIDEQUEST_CODEBOOK_ATTESTATION_RULE.md"

H_SUMMARY = V73 / "V73_SELECTED_FIVE_ARTICLES.tsv"
B_SUMMARY = V74 / "V74_SELECTED_SIX_RECORD_EDITION.tsv"
A_SUMMARY = V75 / "V75_SELECTED_THREE_INSTRUMENTS.tsv"
H_DETAIL = V73 / "V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
B_DETAIL = V74 / "V74_SELECTED_281_EVENT_INTERLINEAR.tsv"
A_DETAIL = V75 / "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"

MATRIX_OUT = OUT / "V76_R1_14_UNIT_PURPOSE_MATRIX.tsv"
WORKFLOW_OUT = OUT / "V76_R1_PRODUCTION_WORKFLOW.tsv"
SCORE_OUT = OUT / "V76_R1_COMPETITION_SCORECARD.tsv"
CONTRA_OUT = OUT / "V76_R1_CONTRADICTION_LEDGER.tsv"
BUILD_OUT = OUT / "V76_R1_BUILD_SUMMARY.json"

LEAD = "C1420_ILLUSTRATED_PRACTITIONER_BATH_AND_CELESTIAL_ELECTION_COMPENDIUM"
RIVAL = "C1420_NATURALIA_COSMOGRAPHIA_WORKSHOP_MODEL_AND_MEMORY_BOOK"
MNEMONIC_STATUS = "PROVISIONAL_UNATTESTED_MNEMONIC_OR_FORMAL_LABEL_NOT_WORD"
ATTESTED_WORDS = "0"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_pipe(value: str) -> int:
    return 0 if not value else len(value.split("|"))


H_COMPACT = {
    "H1": "Wurzel-/Pflanzenmaterial reinigen, wässrig ausziehen, kleine Portion führen und Rest lagern",
    "H2": "zwei Erntefraktionen pressen, vereinigen und als ölhaltige äußere Zubereitung führen",
    "H3": "Blüten-/Blattmaterial in Wein ausziehen, klären und einen zweiten Ölposten halten",
    "H4": "Blattansatz klären sowie zweiten warmen Honig-/Auflageposten führen",
    "H5": "frisches Pflanzenmaterial kurz äußerlich verwenden und Rest trocknen/ausziehen",
}

A_COMPACT = {
    "A1": "zwei getrennte Himmelsräder: rechts Sektor-/Bedingungsplätze, links Stern-/Radialfelder; kein 7×12",
    "A2": "mehrpaneeliger Sternatlas mit mehreren Zentren und 28 räumlichen, ungeordneten Sternetiketten",
    "A3": "drei getrennte Räder; nur links ein lokales, ungeordnetes 28-Platz-Inventar",
}


def common_row(*, unit_id: str, section: str, page: str, group_count: int,
               subunit_kind: str, subunit_count: int, source_summary: Path,
               source_detail: Path, source_selector: str, visible_owner: str,
               selected_content_binding: str, strongest_contradiction: str) -> dict[str, object]:
    if section == "HERBAL":
        lead_role = "materia-medica-/Receptarium-Artikel: Bildpflanze wählen, occurrence-gebundene Zubereitung und Gebrauch nachschlagen"
        rival_role = "Pflanzenexemplar und Materialprozess-Musterblatt ohne Arznei- oder Indikationsanspruch"
        practical = "ein lokaler Pflanzenartikel für Auswahl, Aufbereitung, Portion und Lagerung"
        source_layer = "eigenständiges Herbal-/Receptarium-Vorlagenheft; Ganzpflanzenbild zuerst, Artikeltext danach"
        apprentice = "Ganzpflanzenbesitzer setzen, Ereignisfolge vollständig kopieren, exemplarische Zutaten/Aktionen nicht ins Wörterbuch übertragen"
    elif section == "BIOLOGICAL":
        lead_role = "lokaler Bade-/Wasch-/Anwendungsstationsartikel innerhalb eines therapeutischen Praxisatlas"
        rival_role = "Badehaus-/Apparate- oder ikonographisches Stationsmuster ohne Patientensemantik"
        practical = "eine lokale Station einrichten oder konsultieren; an jeder Bildlücke Stoff, Ziel und Richtung löschen"
        source_layer = "eigenständiges balneologisches/Stations-Vorlagenheft; Großkonfiguration zuerst, lokale Texte danach"
        apprentice = "kleinsten sichtbaren Stationsbesitzer setzen, nur echte Kontakte übernehmen, nie globalen Fluss ergänzen"
    else:
        lead_role = "lokales astronomisch-kalendarisches oder iatromathematisches Auswahl-/Bedingungsinstrument"
        rival_role = "astronomisch-kosmographisches Merk-, Lehr- oder Kopierdiagramm ohne medizinische Wahlfunktion"
        practical = "lokalen Himmelsort zeigen, Etikett kopieren und nur im selben Instrument nachschlagen"
        source_layer = "eigenständiges astronomisches Tafel-/Diagrammvorlagenheft; Räder/Paneele zuerst, lokale Etiketten danach"
        apprentice = "Instrumentnamensraum ausrufen, Etiketten lokal halten, Start/Richtung/Rotation und Seitenjoin niemals ergänzen"
    return {
        "matrix_row": 0,
        "unit_id": unit_id,
        "section": section,
        "page": page,
        "bound_group_kind": "PROSE_EVENT" if section != "ASTRO" else "VISIBLE_ASTRO_GROUP",
        "bound_group_count": group_count,
        "subunit_kind": subunit_kind,
        "subunit_count": subunit_count,
        "source_summary_file": source_summary.relative_to(ROOT).as_posix(),
        "source_detail_file": source_detail.relative_to(ROOT).as_posix(),
        "source_detail_sha256": sha256(source_detail),
        "source_unit_selector": source_selector,
        "visible_owner_or_instrument_binding": visible_owner,
        "selected_v73_v75_content_binding": selected_content_binding,
        "lead_book_purpose": LEAD,
        "lead_unit_role": lead_role,
        "rival_book_purpose": RIVAL,
        "rival_unit_role": rival_role,
        "practical_use_at_unit": practical,
        "compilation_source_layer": source_layer,
        "picture_first_production": "VISIBLE_OWNER_OR_INSTRUMENT_LAID_OUT_BEFORE_LOCAL_TEXT; SPACE_FIT_IS_COMPATIBLE_NOT_PURPOSE_PROOF",
        "multiple_scribe_fit": "SECTION_TEMPLATE_CAN_BE_LEARNED_LOCALLY; SHARED_PAGE_GRAMMAR_DOES_NOT_REQUIRE_SHARED_SEMANTICS",
        "master_exemplar_dependency": "HIGH__VISIBLE_FORM_PRESERVES_LOCAL_IDENTITY_BUT_OCCURRENCE_CONTENT_IS_NOT_SELF_DECODING",
        "lead_intended_user": "unterrichteter Praktiker, Bad-/Heilgehilfe oder Haus-/Infirmariumsnutzer mit Zugriff auf Vorwissen/Exemplar",
        "rival_intended_user": "Schreiber, Zeichner oder Schüler einer gelehrten Werkstatt, der Bildtypen und lokale Legenden kopiert/rezitiert",
        "apprentice_lesson": apprentice,
        "coexistence_explanation": (
            "LEAD: Pflanzenmaterial → lokale Anwendung/Bad → himmlische Bedingung als thematische Dreiteilung ohne Direktpointer; "
            "RIVAL: Naturalia → Körper-/Apparatbilder → Kosmographie als gemeinsamer visueller Muster- und Merkbestand"),
        "legacy_mnemonic_status": MNEMONIC_STATUS,
        "qualifying_codebook_attestations": ATTESTED_WORDS,
        "strongest_unit_contradiction": strongest_contradiction,
        "semantic_ceiling": "BOOK_PURPOSE_COMPETITION_NOT_WORD_MEANING_LANGUAGE_OR_TRANSLATION",
    }


def build_matrix() -> list[dict[str, object]]:
    rule_text = RULE.read_text(encoding="utf-8")
    if "PROVISIONAL_UNATTESTED_MNEMONIC" not in rule_text or "No surface resemblance" not in rule_text:
        raise ValueError("frozen codebook-attestation rule is missing required ceiling")
    h = read_tsv(H_SUMMARY)
    b = read_tsv(B_SUMMARY)
    a = read_tsv(A_SUMMARY)
    if [r["record_unit_id"] for r in h] != [f"H{i}" for i in range(1, 6)]:
        raise ValueError("Herbal unit source mismatch")
    if [r["record_unit_id"] for r in b] != [f"B{i}" for i in range(1, 7)]:
        raise ValueError("Biological unit source mismatch")
    if [r["diagram_id"] for r in a] != [f"A{i}" for i in range(1, 4)]:
        raise ValueError("Astro unit source mismatch")
    rows: list[dict[str, object]] = []
    for r in h:
        unit = r["record_unit_id"]
        rows.append(common_row(
            unit_id=unit, section="HERBAL", page=r["page"],
            group_count=count_pipe(r["event_serials"]), subunit_kind="FIELD",
            subunit_count=count_pipe(r["field_ids"]), source_summary=H_SUMMARY,
            source_detail=H_DETAIL, source_selector=f"record_unit_id={unit}",
            visible_owner=r["whole_plant_owner"], selected_content_binding=H_COMPACT[unit],
            strongest_contradiction=r["strongest_contradiction"]))
    for r in b:
        unit = r["record_unit_id"]
        rows.append(common_row(
            unit_id=unit, section="BIOLOGICAL", page=r["page"],
            group_count=count_pipe(r["event_serials"]), subunit_kind="FIELD",
            subunit_count=count_pipe(r["field_ids"]), source_summary=B_SUMMARY,
            source_detail=B_DETAIL, source_selector=f"record_unit_id={unit}",
            visible_owner=r["local_owner_sequence"],
            selected_content_binding=r["fluent_record_synopsis"],
            strongest_contradiction=r["strongest_contradiction"]))
    for r in a:
        unit = r["diagram_id"]
        rows.append(common_row(
            unit_id=unit, section="ASTRO", page=r["page"],
            group_count=int(r["group_count"]), subunit_kind="LOCUS",
            subunit_count=int(r["locus_count"]), source_summary=A_SUMMARY,
            source_detail=A_DETAIL, source_selector=f"diagram_id={unit}",
            visible_owner=r["repaired_visual_system"],
            selected_content_binding=A_COMPACT[unit],
            strongest_contradiction=r["strongest_counterevidence"]))
    for i, row in enumerate(rows, 1):
        row["matrix_row"] = i
    return rows


def workflow_rows() -> list[dict[str, object]]:
    raw = [
        (1, "COMMISSION_AND_SCOPE", "Eine kleine Praxis-/Hauswerkstatt bestellt ein kompaktes Bildnachschlagebuch.", "Eine gelehrte Schreib-/Bildwerkstatt sammelt ein Muster- und Merkbuch.", "Zweck wird nicht aus einer einzelnen Seite abgeleitet.", "NO_SEMANTIC_STRING_ASSIGNMENT"),
        (2, "GATHER_INDEPENDENT_QUIRES", "Herbal-, Bade-/Stations- und Himmeltafeln aus getrennten Vorlagen zusammenbringen.", "Naturalia-, Figuren-/Apparat- und Kosmographieblätter aus getrennten Musterbeständen zusammenbringen.", "Abschnittsunterschiede und fehlende Crosspointer werden erwartet.", "RESET_SOURCE_VOCABULARY_AT_SECTION_BOUNDARY"),
        (3, "PLAN_HERBAL_IMAGES", "Vier Ganzpflanzenbilder als Artikelbesitzer disponieren; f10r erhält zwei Records unter einem Bild.", "Vier Pflanzenexemplare als Zeichen-/Bildmodelle disponieren.", "Kein Pflanzenname oder Zutat wird aus dem Bild ergänzt.", "WHOLE_PLANT_OWNER_ONLY"),
        (4, "ADD_HERBAL_TEXT", "Fünf occurrence-gebundene Artikel aus der Herbalvorlage in Restflächen eintragen.", "Material-/Kopiernotizen um die Pflanzenmodelle setzen.", "100 Ereignisse bleiben an H1–H5 gebunden.", "NO_DICTIONARY_PROMOTION"),
        (5, "PLAN_BIO_STATIONS", "Lokale Bade-/Anwendungsbilder und Apparatekonfigurationen als Stationsbesitzer zeichnen.", "Figuren-/Gefäß-/Bandmotive als eigenständige Modellstationen zeichnen.", "Nur sichtbare Kontakte; keine globale Flussrichtung.", "RESET_AT_VISIBLE_GAP"),
        (6, "ADD_BIO_TEXT", "Sechs Records stationenweise aus der balneologischen Vorlage ergänzen.", "Bedien-, Varianten- oder Kopierlegenden lokal ergänzen.", "281 Ereignisse und 16 Besitzer; ungelöste Zonen bleiben ungelöst.", "NO_CROSS_STATION_CARRY"),
        (7, "PLAN_CELESTIAL_INSTRUMENTS", "Zwei f67-Räder, f68-Mehrpaneelatlas und drei f69-Räder vorzeichnen.", "Himmelsdiagramme als Lehr-/Musterbilder vorzeichnen.", "Mehrere Instrumente statt universaler Matrix.", "RESET_AT_WHEEL_PANEL_PAGE"),
        (8, "ADD_CELESTIAL_LABELS", "395 lokale Himmels-/Kalenderetikettsegmente aus der Instrumentvorlage einsetzen.", "395 lokale Kopier-/Merketikettsegmente einsetzen.", "Kein Start, keine Richtung, Rotation oder f68↔f69-Verbindung.", "LOCAL_NAMESPACE_ONLY"),
        (9, "SECTION_SPECIALIST_COPYING", "Verschiedene Schreiber lernen je eine Abschnittsschablone; ein Korrektor prüft Besitzer und Vollständigkeit.", "Schreiber/Zeichner spezialisieren sich auf Pflanzen-, Figuren- und Radseiten.", "Mehrhändigkeit erklärt Variation, beweist aber keinen Zweck.", "SHARED_FORM_GRAMMAR_NOT_SHARED_GLOSS"),
        (10, "MASTER_EXEMPLAR_CHECK", "Occurrence-Werte gegen ausgeschriebene/unterrichtete Vorlage rücklesen.", "Bild- und Legendenidentität gegen Werkstattvorlage rücklesen.", "Ohne Exemplar bleiben konkrete Werte unbekannt.", "EXEMPLAR_VALUE_NOT_PORTABLE_WORD"),
        (11, "ASSEMBLE_OR_BIND", "Drei thematisch aufeinander bezogene, aber nicht direkt verlinkte Quellenlagen zusammenführen.", "Drei Bildrepertorien als gelehrtes Miscellaneum zusammenführen.", "Physische Gesamtordnung wird aus zehn Seiten nicht rekonstruiert.", "NO_INFERRED_CROSS_SECTION_POINTER"),
        (12, "APPRENTICE_USE", "Bildbesitzer wählen, lokalen Artikel/Station/Instrumenteintrag konsultieren und jeden Grenzreset beachten.", "Bildtyp zeigen, lokale Legende kopieren/rezitieren und Varianten unterscheiden.", "Lehrbarkeit beruht auf Bildort+Exemplar, nicht auf entschlüsselten Wörtern.", "ALL_LEGACY_MNEMONICS_PROVISIONAL_UNATTESTED"),
    ]
    fields = ("step", "production_phase", "lead_workflow", "rival_workflow",
              "visible_or_ledger_binding", "hard_reset_or_ceiling")
    return [dict(zip(fields, row)) for row in raw]


def score_rows() -> list[dict[str, object]]:
    raw = [
        ("S01", "Fit zu drei ausgewählten Abschnittsausgaben", 3, 4, 3, "Lead nutzt die konkrete Herbal-/Bad-/Himmelslesung; Rivale nutzt vor allem deren sichtbare Träger."),
        ("S02", "praktische Kohärenz der 14 Einheiten", 3, 4, 2, "Material, Anwendung und Bedingung bilden eine plausible Praxisdreiteilung; der Rivale braucht keine operative Einheit."),
        ("S03", "Bild-zuerst/Text-danach-Produktion", 3, 3, 4, "Beide passen; ein Musterbuch erwartet Bildpriorität besonders direkt."),
        ("S04", "mehrere Schreiber und lokale Schablonen", 2, 4, 4, "Abschnittsspezialisierung ist unter beiden Zwecken gut lehrbar."),
        ("S05", "Notwendigkeit eines Masterexemplars", 3, 4, 4, "Beide erklären, warum opake lokale Werte nicht aus der Oberfläche allein folgen."),
        ("S06", "circa-1420 Nutzer- und Gebrauchspraxis", 2, 3, 3, "Unterrichtete Praxis- wie Bildwerkstätten sind zeitgemäße Arbeitsmilieus; keine enge Provenienz wird behauptet."),
        ("S07", "warum die drei Sektionen koexistieren", 3, 4, 3, "Lead besitzt die stärkere Material→Anwendung→Bedingung-Klammer; Rivale besitzt eine breitere Naturalia/Kosmos-Klammer."),
        ("S08", "fehlende direkte Crosspointer", 3, 3, 4, "Thematische Praxiszusammenstellung toleriert fehlende Pointer; ein Muster-Miscellaneum erwartet sie noch eher."),
        ("S09", "Codebuchregel und null attestierte Wörter", 3, 4, 4, "Beide funktionieren mit occurrence-gebundenen Exemplarwerten und ohne portable Glossen."),
        ("S10", "Widerspruchslast", 2, 2, 3, "Lead muss viele unbebilderte Inhalte und iatromedizinische Zwecke ergänzen; Rivale verliert dafür konkrete Gebrauchstiefe."),
    ]
    rows = []
    for sid, criterion, weight, lead, rival, rationale in raw:
        rows.append({
            "score_id": sid, "criterion": criterion, "weight": weight,
            "lead_score_0_4": lead, "lead_weighted": weight * lead,
            "rival_score_0_4": rival, "rival_weighted": weight * rival,
            "rationale": rationale, "score_status": "CREATIVE_COMPARISON_NOT_STATISTICAL_EVIDENCE",
        })
    lead_total = sum(int(r["lead_weighted"]) for r in rows)
    rival_total = sum(int(r["rival_weighted"]) for r in rows)
    rows.append({
        "score_id": "TOTAL", "criterion": "selector-paid creative total",
        "weight": sum(int(r["weight"]) for r in rows),
        "lead_score_0_4": "NA", "lead_weighted": lead_total,
        "rival_score_0_4": "NA", "rival_weighted": rival_total,
        "rationale": f"{LEAD} leads narrowly by {lead_total-rival_total} weighted points; rival remains live.",
        "score_status": "LEAD_SELECTED_NARROWLY; RIVAL_NOT_REJECTED",
    })
    return rows


def contradiction_rows() -> list[dict[str, object]]:
    raw = [
        ("C01", "ALL", "Kein direkter Herbal→Bio→Astro-Pointer ist sichtbar.", 3, 1, "Lead nur als thematische, nicht ausführbare Kette formulieren.", "OPEN"),
        ("C02", "HERBAL", "Keine der vier Pflanzenarten ist identifiziert.", 3, 2, "Ganzpflanzenbesitzer behalten; Artname offenlassen.", "CONTAINED"),
        ("C03", "HERBAL", "Medien, Dosen, Indikationen und viele Teile sind nicht gezeichnet.", 4, 2, "Nur occurrence-gebundene Masterexemplarfüllung zulassen.", "OPEN"),
        ("C04", "HERBAL", "71/100 Ereignisse besitzen nur exemplarische, keine formale Inhaltsstützung.", 4, 3, "V73-Bindung offenlegen; keine Wörter promovieren.", "OPEN"),
        ("C05", "BIOLOGICAL", "191/281 Ereignisse sind exemplarisch; nur 90 haben Mnemonic-/Formalstützung.", 4, 3, "Lokale Station und Exemplarwert getrennt halten.", "OPEN"),
        ("C06", "BIOLOGICAL", "Kein seitenweiter Stoff, Pfeil, Rücklauf oder geschlossener Kreislauf ist gezeichnet.", 3, 1, "Nur lokale, ungerichtete Kontakte und harte Resets verwenden.", "CONTAINED"),
        ("C07", "BIOLOGICAL", "32 Ereignisse liegen an ungelösten Besitzern; vier Aussagen queren echte Lücken.", 3, 2, "Unresolved-Status und interne Besitzerresets unverändert binden.", "CONTAINED"),
        ("C08", "ASTRO_A1", "f67r2 zeigt keine globale 7×12-Matrix und keinen Rad-zu-Rad-Schlüssel.", 2, 1, "Zwei Instrumente getrennt halten.", "CONTAINED"),
        ("C09", "ASTRO_A2", "f68r1 besitzt mehrere Paneele und Zentren statt eines Zentrum+28-Rades.", 2, 1, "28 Sternetiketten nur räumlich und ungeordnet führen.", "CONTAINED"),
        ("C10", "ASTRO_A3", "f69v besitzt drei heterogene Räder; nur links etwa 28 Plätze.", 2, 1, "Nur links lokales ungeordnetes 28-Inventar zulassen.", "CONTAINED"),
        ("C11", "ASTRO", "Start, Richtung, Rotation und f68↔f69-Key fehlen.", 3, 2, "Alle Orientierungen ungewählt lassen.", "CONTAINED"),
        ("C12", "DICTIONARY", "Für keinen portablen Voynich-Wortwert liegt eine qualifizierende Codebuchattestation vor.", 4, 4, "Alle Legacy-Mnemonics PROVISIONAL_UNATTESTED oder FORMAL_LABEL_NOT_WORD führen.", "HARD_CEILING"),
        ("C13", "PRODUCTION", "Bild-zuerst kann reine Platzplanung sein und beweist keinen Buchzweck.", 3, 3, "Nur Produktionskompatibilität, keine Semantik daraus ableiten.", "OPEN"),
        ("C14", "HANDS", "Mehrere Schreiber können arbeitsteilig kopieren, ohne unterschiedliche Inhalte verstanden zu haben.", 2, 2, "Lokale Lehrschablonen behaupten, keine Wissensrollen identifizieren.", "OPEN"),
        ("C15", "MASTER_EXEMPLAR", "Das verlorene Masterexemplar kann beliebige occurrence-Werte aufnehmen und schwächt Falsifizierbarkeit.", 4, 4, "Exemplarabhängigkeit als Kosten, nicht als Beweis behandeln.", "OPEN_HIGH_COST"),
        ("C16", "COVERAGE", "V76s 776-Gruppen-Abdeckung ist nur eine Bindung an V73–V75, keine neue Inhaltsbestätigung.", 4, 4, "Keine Zeile neu übersetzen; nur Zweckmodelle vergleichen.", "HARD_CEILING"),
    ]
    rows = []
    for cid, scope, observation, lead_p, rival_p, repair, status in raw:
        rows.append({
            "contradiction_id": cid, "scope": scope, "observation": observation,
            "pressure_on_lead_0_4": lead_p, "pressure_on_rival_0_4": rival_p,
            "allowed_repair": repair, "remaining_status": status,
            "dictionary_effect": MNEMONIC_STATUS if scope in {"DICTIONARY", "MASTER_EXEMPLAR", "COVERAGE"} else "NO_PORTABLE_WORD_LICENSE",
            "semantic_ceiling": "PURPOSE_PRESSURE_NOT_DECRYPTION_EVIDENCE",
        })
    return rows


def main() -> None:
    matrix = build_matrix()
    workflow = workflow_rows()
    scores = score_rows()
    contradictions = contradiction_rows()
    write_tsv(MATRIX_OUT, matrix, list(matrix[0]))
    write_tsv(WORKFLOW_OUT, workflow, list(workflow[0]))
    write_tsv(SCORE_OUT, scores, list(scores[0]))
    write_tsv(CONTRA_OUT, contradictions, list(contradictions[0]))
    lead_total = int(scores[-1]["lead_weighted"])
    rival_total = int(scores[-1]["rival_weighted"])
    result = {
        "experiment": "V76_R1_HISTORICAL_BOOK_PURPOSE_COMPETITION",
        "status": "BUILT",
        "selected_lead": LEAD,
        "strongest_genuinely_different_rival": RIVAL,
        "counts": {
            "units": len(matrix),
            "bound_groups": sum(int(r["bound_group_count"]) for r in matrix),
            "herbal_units": sum(r["section"] == "HERBAL" for r in matrix),
            "biological_units": sum(r["section"] == "BIOLOGICAL" for r in matrix),
            "astro_units": sum(r["section"] == "ASTRO" for r in matrix),
            "workflow_steps": len(workflow),
            "score_criteria": len(scores) - 1,
            "contradictions": len(contradictions),
            "qualifying_codebook_attestations": 0,
        },
        "creative_score": {"lead": lead_total, "rival": rival_total,
                           "maximum": 4 * sum(int(r["weight"]) for r in scores[:-1])},
        "constraints": {
            "new_row_translation": False,
            "new_card_stem_sound_language_or_dictionary_word": False,
            "legacy_mnemonics_promoted": False,
            "desired_codebook_words_hunted": False,
            "new_pages_read": False,
            "f84_or_f84r_opened": False,
        },
    }
    BUILD_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
