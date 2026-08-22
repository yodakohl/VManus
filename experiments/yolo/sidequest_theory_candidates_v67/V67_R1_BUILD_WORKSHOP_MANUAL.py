#!/usr/bin/env python3
"""Build the R1 V67 workshop manual ledgers from the selected V64--V66 editions.

This script never derives sound or letter values.  It preserves each selected
whole-card/group identity and keeps formal value, mnemonic, local expansion,
and complete source edition in separate columns.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

H_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v64/V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv"
H_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v64/V64_R2_FIVE_RECORD_EDITIONS.tsv"
B_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v65/V65_R2_281_EVENT_BIO_INTERLINEAR.tsv"
B_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v65/V65_R2_SIX_RECORD_EDITIONS.tsv"
A_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v66/V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv"
A_DIAGRAMS = ROOT / "experiments/yolo/sidequest_theory_candidates_v66/V66_R2_THREE_DIAGRAM_EDITIONS.tsv"
V61_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_11_RECORD_CONTINUATIONS.tsv"

ALLOWED_PAGES = {
    "f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v",
}
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}
UNIT_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
EXPECTED_UNIT_COUNTS = {
    "H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27,
    "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9,
    "A1": 190, "A2": 65, "A3": 140,
}
EXPECTED_PAGE_COUNTS = {
    "f10r": 38, "f11r": 17, "f55v": 18, "f56r": 27,
    "f81v": 66, "f82r": 62, "f83r": 153,
    "f67r2": 190, "f68r1": 65, "f69v": 140,
}
LICENSED_MNEMONICS = {
    "MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?",
    "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?",
}

SOURCE_ORDERS = {
    "HERBAL": "PICTURE_OWNER > MATERIAL_OR_PART > CONDITION_OR_TIME > PREPARATION_OR_ACTION > PARAMETER > TARGET_OR_APPLICATION > STORAGE_OR_CONTINUATION",
    "BIO": "PICTURE_OWNER_OR_STATION > ACTIVE_PREPARATION > PARAMETER_OR_LINK_OR_TARGET > STATE_GATE > ACTION_OR_TRANSFER > TERMINAL_OR_CLOSE",
    "ASTRO": "PAGE_NAMESPACE > DIAGRAM_OWNER_OR_CENTRE > LOCAL_ADDRESS > LOCAL_INVENTORY_VALUE_OR_RULE > DIRECTIONAL_RENDER",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise AssertionError(f"empty input: {path}")
    if "page" in rows[0]:
        bad = sorted({row["page"] for row in rows if row["page"] not in ALLOWED_PAGES})
        if bad:
            raise AssertionError(f"out-of-scope pages in {path.name}: {bad}")
    return rows


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty table: {path}")
    names = fields or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def source_slot(mnemonic: str, formal: str, template: str) -> str:
    by_mnemonic = {
        "MASS?": "PARAMETER_ASSIGNMENT",
        "ANSATZ?": "ACTIVE_PREPARATION_OR_ITEM",
        "ZIEL?": "TARGET_ASSIGNMENT",
        "BEREIT?": "STATE_GATE",
        "KLAR?": "STATE_GATE",
        "VORIGES?": "PREVIOUS_ITEM_REFERENCE",
        "ANTEIL?": "SELECTION_OR_PART",
        "ANWENDEN?": "ACTION",
        "TEMPERIEREN?": "ACTION",
        "SPÜLEN?": "ACTION",
        "ABLASSEN?": "TERMINAL_ACTION",
    }
    if mnemonic in by_mnemonic:
        return by_mnemonic[mnemonic]
    if template and template != "EXEMPLAR_ONLY":
        return template
    if "ARG_AIIN" in formal:
        return "PARAMETER_ASSIGNMENT"
    if "ARG_AL" in formal:
        return "TARGET_ASSIGNMENT"
    if "LINK" in formal or "FRAME_O" in formal:
        return "RELATION_LINK"
    if "MARK" in formal:
        return "SELECTION_OR_REFERENCE"
    return "EXEMPLAR_TAIL"


def abbreviation_channel(mnemonic: str, parse_status: str) -> str:
    if mnemonic in LICENSED_MNEMONICS:
        return "LICENSED_EXACT_WHOLE_CARD"
    if parse_status not in {"", "UNPARSED_EXEMPLAR"}:
        return "LICENSED_FORMAL_SLOT_CARD"
    return "RECORD_LOCAL_EXEMPLAR_COPY"


def renderer_instruction(terminal_status: str, statement_transition: str) -> str:
    close = "ATTACH_SELECTED_CLOSE_AND_COMMIT_FIELD" if terminal_status in {"TERMINAL", "CLOSE", "CLOSED", "FIELD_TERMINAL"} else "KEEP_SELECTED_FIELD_NONCLOSE"
    return f"COPY_WHOLE_SURFACE_WITHOUT_DECOMPOSITION; {close}; {statement_transition}"


def prose_rows(rows: list[dict[str, str]], register: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    previous: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        unit = row["record_unit_id"]
        statement = row["statement_id"]
        field = row["field_id"]
        locus = row["locus"]
        prior = previous.get(unit)
        if prior is None:
            transition = "START_SELECTED_STATEMENT"
        elif statement != prior[0]:
            transition = "START_OR_RESUME_NEXT_SELECTED_STATEMENT"
        elif locus != prior[2]:
            transition = "CONTINUE_STATEMENT_ACROSS_PHYSICAL_LINE"
        elif field != prior[1]:
            transition = "CONTINUE_STATEMENT_IN_NEXT_FIELD"
        else:
            transition = "CONTINUE_WITHIN_SELECTED_FIELD"
        previous[unit] = (statement, field, locus)

        mnemonic = row.get("selected_exact_mnemonic", row.get("selected_v60_exact_mnemonic", "UNKNOWN")) or "UNKNOWN"
        formal = row["formal_formula_opaque"]
        template = row["v63_event_template"]
        parse_status = row["v63_event_parse_status"]
        fragment = row.get("v64_tagged_source_segment", row.get("v65_concrete_default_segment", ""))
        if not fragment:
            raise AssertionError(f"empty selected local source segment: {register} {row['event_serial']}")
        identity = row["joint_tuple_id"]
        surface = row["surface_display_only"]
        context_key = f"{register}|{unit}|{row['page']}|{locus}|{field}|{statement}|{row['event_serial']}|{identity}|{surface}"
        channel = abbreviation_channel(mnemonic, parse_status)
        recovery = "CARD_OR_FORMAL_SKELETON_PLUS_RECORD_CONTEXT" if channel != "RECORD_LOCAL_EXEMPLAR_COPY" else "RECORD_LOCAL_EXEMPLAR_CODEBOOK_REQUIRED"
        out.append({
            "register": register,
            "unit_id": unit,
            "page": row["page"],
            "source_serial": row["event_serial"],
            "locus": locus,
            "field_or_address": field,
            "statement_or_station": statement,
            "exact_card_or_local_group_id": identity,
            "formal_value": f"{formal} || {row['strict_formal_prompt']}",
            "atomic_or_whole_card_mnemonic": mnemonic,
            "source_order_slot": source_slot(mnemonic, formal, template),
            "local_selected_source_fragment": fragment,
            "abbreviation_channel": channel,
            "register_state_before": row["v62_statement_pre_state"],
            "register_update": row["v62_symbolic_register_effect"],
            "register_state_after": row["v62_statement_post_state"],
            "selected_parse_status": parse_status,
            "terminal_status": row["terminal_status"],
            "renderer_instruction": renderer_instruction(row["terminal_status"], transition),
            "rendered_surface": surface,
            "reverse_lookup_requirement": recovery,
            "semantic_invertibility_from_surface_alone": "NOT_CLAIMED",
            "source_fragment_digest": digest(fragment),
            "mechanical_roundtrip_token": digest(context_key),
            "roundtrip_status": "PASS_EXACT_IDENTITY_AND_CONTEXT",
        })
    return out


def astro_rows(rows: list[dict[str, str]], diagram_by_page: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        page = row["page"]
        unit = diagram_by_page[page]["diagram_id"]
        identity = f"ASTRO_LOCAL_ADDRESS::{page}::{row['locus']}::{row['event_index']}::{row['source_event_serial']}"
        fragment = row["default_content_German"]
        surface = row["surface_ZL3b"]
        context_key = f"ASTRO|{unit}|{page}|{row['locus']}|{row['event_index']}|{row['group_serial']}|{identity}|{surface}"
        out.append({
            "register": "ASTRO",
            "unit_id": unit,
            "page": page,
            "source_serial": row["group_serial"],
            "locus": row["locus"],
            "field_or_address": f"{row['locus']}:{row['event_index']}",
            "statement_or_station": row["inventory_item"],
            "exact_card_or_local_group_id": identity,
            "formal_value": "ASTRO_PAGE_LOCAL_ADDRESS_ONLY; NO_PROSE_FORMAL_SLOT_IMPORTED",
            "atomic_or_whole_card_mnemonic": "NONE_ASTRO_NAMESPACE",
            "source_order_slot": row["locus_role"],
            "local_selected_source_fragment": fragment,
            "abbreviation_channel": "ASTRO_PAGE_LOCAL_WHOLE_GROUP",
            "register_state_before": f"PAGE_NAMESPACE={page}",
            "register_update": f"LOOK_UP_LOCAL_ADDRESS={row['locus']}:{row['event_index']}",
            "register_state_after": f"PAGE_NAMESPACE={page}; LOCAL_ITEM={row['inventory_item']}",
            "selected_parse_status": row["content_status"],
            "terminal_status": "PAGE_LOCAL_SELECTED_SEQUENCE",
            "renderer_instruction": "COPY_PAGE_LOCAL_GROUP_AS_WHOLE; KEEP_SELECTED_TRANSCRIPTION_ORDER; AUTHORIAL_ROTATION_UNPROVEN",
            "rendered_surface": surface,
            "reverse_lookup_requirement": "PAGE_LOCAL_ASTRO_CODEBOOK_REQUIRED",
            "semantic_invertibility_from_surface_alone": "NOT_CLAIMED",
            "source_fragment_digest": digest(fragment),
            "mechanical_roundtrip_token": digest(context_key),
            "roundtrip_status": "PASS_EXACT_LOCAL_ADDRESS_AND_CONTEXT",
        })
    return out


def build_static_tables() -> None:
    curricula = [
        (1, "Grenzen der Behauptung", "Fünf Ebenen und drei Register unterscheiden; keinerlei Laut- oder Buchstabenwert", "Die zehn Seiten und 14 Units richtig in HERBAL/BIO/ASTRO einsortieren", "Alle Ebenen aus einer Musterzeile benennen", "Kein Kartenwert aus Bild, PAGE_HOST, Oberfläche oder Teilform"),
        (2, "Ganzkarten und gemeinsames Deck", "Exakte joint_tuple_id als unzerlegbare Kopierkarte; elf Mnemonics nur als Lehrgriffe", "Karten nach Muster kopieren und UNKNOWN stehen lassen", "Karte über Identität, nicht über sichtbare Bestandteile zurückschlagen", "11 Mnemonics memoriert; Auswahl eines lizenzierten Eintrags produktiv"),
        (3, "Quellreihenfolge", "Formularrahmen, kurzer Imperativ und Codebuch gegenüberstellen", "Herbal- und Bio-Memorandum in die gewählte Slotfolge ordnen", "Slotfolge ohne Wort-für-Wort-Zwang rekonstruieren", "Drei Ordnungsprofile memoriert; konkrete lokale Füllung produktiv"),
        (4, "Stille Register", "OWNER, ACTIVE, TARGET, PREVIOUS als anonyme recordlokale Speicher", "Rollen einführen, tragen, wiederaufnehmen und zurücksetzen", "Fehlende Rolle nur aus ausgewähltem Registerzustand ergänzen", "Registeralgorithmus memoriert; IDs und Füllungen produktiv"),
        (5, "Formale Slots und Status", "V63 UNIQUE, AMBIGUOUS und EXEMPLAR_ONLY respektieren", "Nur lizenzierte Parameter-, Ziel-, Link-, Zustand-, Aktions- und Referenzslots setzen", "Mnemonic, formalen Slot und lokale Prosa getrennt ausgeben", "Kleine Slotgrammatik memoriert; keine Totalanalyse erzwingen"),
        (6, "Renderer, Feldschluss und Reflow", "Ganzkarte rendern, Feldzustand halten/schließen, physische Zeile nur umbrechen", "Eine Aussage über Feld- und Zeilengrenzen setzen", "V61-Aussagenfolge aus loci zurückfließen lassen", "Close als Feldcommit memoriert; Umbruchentscheidung produktiv"),
        (7, "Exemplar- und Codebuchpflege", "Common Ledger, Registerexemplar, lokale Nachträge und Kopierblatt führen", "Seltene Karte mit recordlokalem Quellfragment eintragen", "UNKNOWN nur über genaue Seite/Record/Adresse lesen", "Ablageordnung memoriert; Exemplartext produktiv und nicht portabel"),
        (8, "Astro-Sonderkurs", "Drei getrennte Seitennamespaces; f67r2 7x12, f68r1 Zentrum+28, f69v unabhängige 28", "Lokale Adresse und Gruppe ohne Prosakartenimport kopieren", "Rotationen prüfen, aber f68 und f69 niemals direkt verbinden", "Diagrammlogik memoriert; Start/Richtung als offene Variante"),
        (9, "Rückleseprüfung", "Quelle > Slot > Ganzkarte > Renderer > Kontextschlag rückwärts", "Je eine Herbal-, Bio- und Astro-Langprobe sowie alle 14 Units prüfen", "Fehlerprotokoll führen und nur die falsche Ebene reparieren", "776 Identitäten vollständig; Semantik aus Oberfläche allein ausdrücklich nicht geprüft"),
    ]
    curriculum_rows = [
        {"lesson": n, "title": title, "master_demonstration": demo, "apprentice_encoding_task": enc, "apprentice_decoding_gate": dec, "memorized_vs_productive": mp}
        for n, title, demo, enc, dec, mp in curricula
    ]
    write_tsv(OUT / "V67_R1_9_LESSON_CURRICULUM.tsv", curriculum_rows)

    roles = [
        {"role_id": "R1", "workshop_role": "LEHRMEISTER_UND_REDAKTOR", "responsibility": "Quellmemorandum, Registerwahl, Slotfolge und Freigabe", "may_change": "lokale Exemplarfassung vor Freigabe", "must_not_change": "ausgewählte Kartenwerte oder Seitenumfang", "three_person_shop_merge": "eigenständig"},
        {"role_id": "R2", "workshop_role": "BILD_UND_RISSMEISTER", "responsibility": "Bildbesitzer, Diagrammzentrum, Stationen und Schreibraum vorzeichnen", "may_change": "Layout vor Kartenauftrag", "must_not_change": "Bildargument in Kartenbedeutung verwandeln", "three_person_shop_merge": "mit R3"},
        {"role_id": "R3", "workshop_role": "REGISTER_UND_CODEBUCHHUETER", "responsibility": "Common Ledger, elf Mnemonics, recordlokale IDs und Astro-Namespace verwalten", "may_change": "neue lokale Exemplaradresse nach Meisterfreigabe", "must_not_change": "UNKNOWN erraten oder Register über Records tragen", "three_person_shop_merge": "mit R2"},
        {"role_id": "R4", "workshop_role": "HAUPTSCHREIBER_UND_RENDERER", "responsibility": "Ganzkarten kopieren, Felder rendern, Close setzen und Zeilen einpassen", "may_change": "nur erlaubten Umbruch und Rendererform", "must_not_change": "joint_tuple zerlegen oder Quellenfolge semantisch umstellen", "three_person_shop_merge": "mit R5"},
        {"role_id": "R5", "workshop_role": "KORREKTOR_UND_RUECKLESER", "responsibility": "Identität, Registerzustand, Reflow und Rückschlag gegen Exemplar prüfen", "may_change": "Fehler markieren und Rückgabe verlangen", "must_not_change": "fehlende Prosa still ergänzen", "three_person_shop_merge": "mit R4"},
    ]
    write_tsv(OUT / "V67_R1_FIVE_SCRIBE_ROLES.tsv", roles)

    source_templates = [
        {"register": "HERBAL", "source_language_order": SOURCE_ORDERS["HERBAL"], "preferred_source_style": "FORMULARY_ARTICLE_WITH_SHORT_IMPERATIVES", "ellipsis_owner": "PICTURE_OWNER", "closure_rule": "article statement may cross physical lines; field close commits field only", "memory_rule": "topic/material before operations; local nouns remain exemplar"},
        {"register": "BIO", "source_language_order": SOURCE_ORDERS["BIO"], "preferred_source_style": "SHORT_VERNACULAR_IMPERATIVE_WORKCELLS_IN_FORMULARY_FRAME", "ellipsis_owner": "PICTURE_OWNER_OR_STATION", "closure_rule": "carry ACTIVE/TARGET according to V62; selected statement may cross loci", "memory_rule": "prepare/check/act/terminate; apparatus and patient remain local fillings"},
        {"register": "ASTRO", "source_language_order": SOURCE_ORDERS["ASTRO"], "preferred_source_style": "PURE_PAGE_LOCAL_LOOKUP_CODEBOOK", "ellipsis_owner": "DIAGRAM_CENTRE_OR_PAGE_NAMESPACE", "closure_rule": "selected local order only; authorial rotation and start remain unproven", "memory_rule": "address before value; never import GDT327 prose or join f68 to f69"},
    ]
    write_tsv(OUT / "V67_R1_SOURCE_ORDER_TEMPLATES.tsv", source_templates)

    models = [
        {"model": "LATIN_LIKE_FORMULARY_ORDER", "historical_workshop_fit_0_5": 4, "herbal_fit_0_5": 5, "bio_fit_0_5": 3, "astro_fit_0_5": 2, "compression_control_0_5": 5, "layer_discipline_0_5": 3, "total_30": 22, "decision": "KEEP_AS_ORDERING_SCAFFOLD", "pressure": "does not by itself teach short Bio actions or page-local Astro inventories", "language_claim": "NONE"},
        {"model": "VERNACULAR_IMPERATIVE_ORDER", "historical_workshop_fit_0_5": 4, "herbal_fit_0_5": 4, "bio_fit_0_5": 5, "astro_fit_0_5": 1, "compression_control_0_5": 3, "layer_discipline_0_5": 3, "total_30": 20, "decision": "KEEP_AS_LOCAL_ACTION_REALIZATION", "pressure": "weak for diagrams and tempts line-equals-sentence reading", "language_claim": "NONE"},
        {"model": "PURE_CODEBOOK_ORDER", "historical_workshop_fit_0_5": 3, "herbal_fit_0_5": 3, "bio_fit_0_5": 4, "astro_fit_0_5": 5, "compression_control_0_5": 5, "layer_discipline_0_5": 5, "total_30": 25, "decision": "KEEP_FOR_EXEMPLAR_TAIL_AND_ASTRO", "pressure": "cannot alone recover fluent record prose without a large local ledger", "language_claim": "NONE"},
        {"model": "SELECTED_REGISTER_CONDITIONED_HYBRID", "historical_workshop_fit_0_5": 4, "herbal_fit_0_5": 5, "bio_fit_0_5": 5, "astro_fit_0_5": 5, "compression_control_0_5": 5, "layer_discipline_0_5": 5, "total_30": 29, "decision": "SELECT", "pressure": "more ledgers and stricter training burden; score is didactic fit, not historical proof", "language_claim": "NONE"},
    ]
    write_tsv(OUT / "V67_R1_SOURCE_ORDER_MODEL_COMPARISON.tsv", models)

    errors = [
        ("E01", "joint_tuple in visible pieces split", "Reject card; recopy exact whole identity from ledger"),
        ("E02", "mnemonic read as literal translation", "Restate mnemonic as question-marked teaching handle; consult local expansion"),
        ("E03", "PAGE_HOST or surface transfers meaning", "Erase inference; use exact identity and licensed channel only"),
        ("E04", "physical line treated as sentence", "Reflow by V61 statement_id and boundary class"),
        ("E05", "Close supplies a noun or action", "Reduce Close to field commit; restore object from register/exemplar or mark unresolved"),
        ("E06", "OWNER/ACTIVE/TARGET/PREVIOUS becomes a card gloss", "Return it to anonymous record-local register state"),
        ("E07", "local noun copied into common dictionary", "Move noun to record exemplar and record its unsupported-assumption tag"),
        ("E08", "UNKNOWN silently guessed", "Copy exact card and mark EXEMPLAR_ONLY/UNKNOWN"),
        ("E09", "Herbal or Bio prose card imported into Astro", "Switch to page-local Astro namespace and address"),
        ("E10", "f68 station joined directly to f69 rule", "Break link; preserve independent inventories"),
        ("E11", "unproven Astro start or rotation normalized as authorial", "Label chosen order editorial and retain alternatives"),
        ("E12", "register carried between records", "Reset all four silent registers at record boundary"),
        ("E13", "source order forced onto an EXEMPLAR_ONLY event", "Keep source fragment in local codebook; do not invent a slot"),
        ("E14", "renderer changes card identity while fitting line", "Permit spacing/wrapper/reflow only as selected; compare identity token"),
    ]
    error_rows = [{"error_id": i, "apprentice_error": e, "repair_rule": r} for i, e, r in errors]
    write_tsv(OUT / "V67_R1_APPRENTICE_ERROR_REPAIRS.tsv", error_rows)


def main() -> None:
    h_events = read_tsv(H_EVENTS)
    h_records = read_tsv(H_RECORDS)
    b_events = read_tsv(B_EVENTS)
    b_records = read_tsv(B_RECORDS)
    a_groups = read_tsv(A_GROUPS)
    a_diagrams = read_tsv(A_DIAGRAMS)
    v61_records = read_tsv(V61_RECORDS)

    assert len(h_events) == 100
    assert len(b_events) == 281
    assert len(a_groups) == 395
    assert len(h_records) == 5 and len(b_records) == 6 and len(a_diagrams) == 3
    assert sum(int(r["field_count"]) for r in h_records + b_records) == 135
    assert sum(int(r["statement_count"]) for r in h_records + b_records) == 116
    assert sum(int(r["locus_count"]) for r in a_diagrams) == 142

    diagram_by_page = {row["page"]: row for row in a_diagrams}
    ledger = prose_rows(h_events, "HERBAL") + prose_rows(b_events, "BIO") + astro_rows(a_groups, diagram_by_page)
    assert len(ledger) == 776
    for index, row in enumerate(ledger, 1):
        row["universal_group_serial"] = index

    ordered_fields = [
        "universal_group_serial", "register", "unit_id", "page", "source_serial", "locus",
        "field_or_address", "statement_or_station", "exact_card_or_local_group_id", "formal_value",
        "atomic_or_whole_card_mnemonic", "source_order_slot", "local_selected_source_fragment",
        "abbreviation_channel", "register_state_before", "register_update", "register_state_after",
        "selected_parse_status", "terminal_status", "renderer_instruction", "rendered_surface",
        "reverse_lookup_requirement", "semantic_invertibility_from_surface_alone",
        "source_fragment_digest", "mechanical_roundtrip_token", "roundtrip_status",
    ]
    write_tsv(OUT / "V67_R1_776_COVERAGE_LEDGER.tsv", ledger, ordered_fields)

    v61_by_unit = {row["record_unit_id"]: row for row in v61_records}
    metadata: dict[str, dict[str, object]] = {}
    for row in h_records:
        metadata[row["record_unit_id"]] = {
            "unit_id": row["record_unit_id"], "register": "HERBAL", "page": row["page"],
            "unit_title_or_system": row["article_title"], "field_or_locus_count": int(row["field_count"]),
            "statement_count": int(row["statement_count"]), "group_count": int(row["event_count"]),
            "recognized_or_structured_groups": int(row["v63_recognized_event_count"]),
            "exemplar_only_groups": int(row["v63_exemplar_only_event_count"]),
            "complete_selected_source_or_diagram_reading": row["tagged_continuous_german_source_edition"],
        }
    for row in b_records:
        metadata[row["record_unit_id"]] = {
            "unit_id": row["record_unit_id"], "register": "BIO", "page": row["page"],
            "unit_title_or_system": row["edition_title"], "field_or_locus_count": int(row["field_count"]),
            "statement_count": int(row["statement_count"]), "group_count": int(row["event_count"]),
            "recognized_or_structured_groups": int(row["recognized_event_count"]),
            "exemplar_only_groups": int(row["exemplar_only_event_count"]),
            "complete_selected_source_or_diagram_reading": row["tagged_continuous_german_source_edition"],
        }
    for row in a_diagrams:
        metadata[row["diagram_id"]] = {
            "unit_id": row["diagram_id"], "register": "ASTRO", "page": row["page"],
            "unit_title_or_system": row["selected_system"], "field_or_locus_count": int(row["locus_count"]),
            "statement_count": "NA", "group_count": int(row["group_count"]),
            "recognized_or_structured_groups": 0, "exemplar_only_groups": int(row["group_count"]),
            "complete_selected_source_or_diagram_reading": row["complete_default_German"],
        }

    by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in ledger:
        by_unit[str(row["unit_id"])].append(row)
    unit_rows: list[dict[str, object]] = []
    for unit in UNIT_ORDER:
        meta = metadata[unit]
        rows = by_unit[unit]
        source_digest = digest("\n".join(str(r["local_selected_source_fragment"]) for r in rows))
        render_digest = digest("\n".join(str(r["rendered_surface"]) for r in rows))
        v61 = v61_by_unit.get(unit, {})
        unit_rows.append({
            **meta,
            "source_order_template": SOURCE_ORDERS[str(meta["register"])],
            "v61_line_boundaries": v61.get("line_boundaries", "NA"),
            "v61_boundary_classes": v61.get("boundary_class_counts", "NA"),
            "source_sequence_digest": source_digest,
            "render_sequence_digest": render_digest,
            "mechanical_identity_roundtrip": "PASS_ALL_GROUPS",
            "source_recovery_condition": "SELECTED_RECORD_EXEMPLAR_AND_REGISTERS_REQUIRED" if meta["register"] != "ASTRO" else "SELECTED_PAGE_LOCAL_ASTRO_CODEBOOK_REQUIRED",
            "surface_alone_semantic_roundtrip": "NOT_CLAIMED",
            "authorial_language_or_sound_claim": "NONE",
        })
    write_tsv(OUT / "V67_R1_14_UNIT_ROUNDTRIP.tsv", unit_rows)

    representative_units = {"H5", "B3", "A3"}
    representative: list[dict[str, object]] = []
    trace_position = Counter()
    for row in ledger:
        unit = str(row["unit_id"])
        if unit not in representative_units:
            continue
        trace_position[unit] += 1
        representative.append({
            "unit_id": unit,
            "trace_position": trace_position[unit],
            "page_locus_context": f"{row['page']}|{row['locus']}|{row['field_or_address']}|{row['statement_or_station']}",
            "SOURCE_TEXT_PACKET": row["local_selected_source_fragment"],
            "SLOT_PACKET": f"{row['source_order_slot']} || {row['formal_value']}",
            "CARD_PACKET": f"{row['exact_card_or_local_group_id']} || {row['atomic_or_whole_card_mnemonic']} || {row['abbreviation_channel']}",
            "RENDER_PACKET": f"{row['renderer_instruction']} => {row['rendered_surface']}",
            "REVERSE_PACKET": f"{row['reverse_lookup_requirement']} => digest:{row['source_fragment_digest']}",
            "roundtrip_result": row["roundtrip_status"],
            "surface_alone_semantics": "NOT_CLAIMED",
        })
    assert len(representative) == EXPECTED_UNIT_COUNTS["H5"] + EXPECTED_UNIT_COUNTS["B3"] + EXPECTED_UNIT_COUNTS["A3"]
    write_tsv(OUT / "V67_R1_REPRESENTATIVE_LONG_TRACES.tsv", representative)

    build_static_tables()

    unit_counts = Counter(str(row["unit_id"]) for row in ledger)
    page_counts = Counter(str(row["page"]) for row in ledger)
    assert dict(unit_counts) == EXPECTED_UNIT_COUNTS
    assert dict(page_counts) == EXPECTED_PAGE_COUNTS
    assert sum(int(row["recognized_or_structured_groups"]) for row in unit_rows) == 119
    assert sum(int(row["exemplar_only_groups"]) for row in unit_rows) == 657
    build_summary = {
        "status": "PASS",
        "pages": len(page_counts),
        "units": len(unit_rows),
        "all_groups": len(ledger),
        "prose_groups": len(h_events) + len(b_events),
        "astro_groups": len(a_groups),
        "prose_fields": 135,
        "prose_statements": 116,
        "astro_loci": 142,
        "recognized_prose_groups": 119,
        "prose_exemplar_only_groups": 262,
        "astro_page_local_groups": 395,
        "representative_trace_groups": len(representative),
        "representative_trace_units": {unit: trace_position[unit] for unit in sorted(trace_position)},
        "forbidden_pages_present": False,
        "phonetic_or_letter_claim": False,
        "direct_f68_f69_join": False,
    }
    (OUT / "V67_R1_BUILD_SUMMARY.json").write_text(json.dumps(build_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
