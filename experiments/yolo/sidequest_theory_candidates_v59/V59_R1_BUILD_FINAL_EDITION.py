#!/usr/bin/env python3
"""Build the complete V59 R1 ten-page edition from frozen published ledgers.

This is a deterministic sidequest assembler, not a decoder.  It deliberately
keeps exact/formal identity, mnemonic prompts, local iatromedical expansion,
nonmedical rival expansion, and unknown/exemplar status in separate columns.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v59"

P = {
    "v49_cards": ROOT / "experiments/yolo/sidequest_theory_candidates_v49/V49_SELECTED_173_CARD_DICTIONARY.tsv",
    "v49_events": ROOT / "experiments/yolo/sidequest_theory_candidates_v49/V49_SELECTED_381_EVENT_INTERLINEAR.tsv",
    "v49_fields": ROOT / "experiments/yolo/sidequest_theory_candidates_v49/V49_SELECTED_135_FIELD_TRANSLATION.tsv",
    "v43_dictionary": ROOT / "experiments/yolo/sidequest_theory_candidates_v43/V43_CURRENT_COMPLETE_DICTIONARY.tsv",
    "v22_lexicon": ROOT / "experiments/yolo/sidequest_theory_candidates_v22/V22_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv",
    "v22_ledger": ROOT / "experiments/yolo/sidequest_theory_candidates_v22/V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv",
    "v53_articles": ROOT / "experiments/yolo/sidequest_theory_candidates_v53/V53_SELECTED_FIVE_ARTICLES.tsv",
    "v54_bio": ROOT / "experiments/yolo/sidequest_theory_candidates_v54/V54_SELECTED_SIX_BIO_RECORDS.tsv",
    "v55_diagrams": ROOT / "experiments/yolo/sidequest_theory_candidates_v55/V55_SELECTED_THREE_DIAGRAMS.tsv",
    "v56_phrasebook": ROOT / "experiments/yolo/sidequest_theory_candidates_v56/V56_SELECTED_SHARED_PHRASEBOOK.tsv",
    "v57_manual": ROOT / "experiments/yolo/sidequest_theory_candidates_v57/V57_SELECTED_TEACHING_MANUAL.tsv",
    "v58_comparison": ROOT / "experiments/yolo/sidequest_theory_candidates_v58/V58_SELECTED_MODEL_COMPARISON.tsv",
}

ALLOWED_PAGES = {
    "f10r", "f11r", "f55v", "f56r",
    "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v",
}

# V56's eleven exact cross-register bridge cards: three formal constructions
# and eight exposed mnemonic cards.  The mapping is by exact tuple ID, never by
# a visible substring or host coordinate.
PORTABLE_MNEMONIC = {
    "2f1c5e56e8f0ff459065": "MASS?",
    "276a7c2d74d1143446f4": "VERWENDEN?",
    "e0b630cb1b5df5e7105b": "BEREIT?",
    "7a4bb8136330ee4e6e56": "BEREITUNG?",
    "dd0ecaf5e27d81befffc": "AN?",
    "b5df9126607030b95175": "KLAR?",
    "dec401773c1f0347793d": "ZUVOR?",
    "faf321940aed922846a9": "TEIL?",
}

BIO_LOCAL_MNEMONIC = {
    "de7321bface5628e35d6": ("ABLASSEN?", "BIO_LOCAL_ONLY_CLOSE_CONFOUNDED"),
    "7db18b2f0fb7ed0fcfd3": ("SPÜLEN?", "BIO_LOCAL_ONLY_CLOSE_CONFOUNDED"),
    "0275fbf14e07935b0a45": ("WARM?", "BIO_LOCAL_ONLY"),
}

STRICT_CONTROL = {
    "b5fcea1eaed06b2f2291": "STANDARDSLOT_SETZEN",
    "308e8ea2d5d190c498e8": "LOKALEN_RELATIONSSLOT_SETZEN",
    "dcda95c81a5460feb191": "AKTIVEN_ARBEITSSTAND_VERKNÜPFEN",
}

FORMULA_ID = "FORMULA_F3:Y>AIIN>Y"

RECORD_UNIT = {
    ("f10r", "1"): "H1",
    ("f10r", "2"): "H2",
    ("f11r", "1"): "H3",
    ("f55v", "1"): "H4",
    ("f56r", "1"): "H5",
    ("f81v", "1"): "B1",
    ("f82r", "1"): "B2",
    ("f83r", "1"): "B3",
    ("f83r", "2"): "B4",
    ("f83r", "3"): "B5",
    ("f83r", "4"): "B6",
}

NONMEDICAL_FULL = {
    "H1": "Wurzelstoff wässern, als Standardzusatz ansetzen und den Rest lagern.",
    "H2": "Obere Teile ausziehen, mit einem Träger verbinden und als zweite Charge buchen.",
    "H3": "Blüten- oder Krautanteil ausziehen, filtrieren und getrennt verwahren.",
    "H4": "Blattflotte und weichen Rest als zwei Arbeitsfraktionen führen.",
    "H5": "Seltenes klebriges Feuchtlandmaterial klein dosieren und trocknen.",
    "B1": "Den Hauptkreislauf temperieren, absetzen, klären und weitergeben.",
    "B2": "Das Einzelbecken füllen, bewegen, filtern, ablassen und nachfüllen.",
    "B3": "Einen wiederholten Mehrbecken- und Stationszyklus betreiben.",
    "B4": "Den bezeichneten Lauf warm reinigen, filtern und neu ansetzen.",
    "B5": "Den Restbestand erwärmen, halten und an die nächste Station übergeben.",
    "B6": "Den kalten Vorlauf filtern und zum sichtbaren Ziel bringen.",
    "A1": "Eine 7×12-Zeit- und Sektorkonfiguration mit lokaler Bedingung wählen.",
    "A2": "Zentrum und 28 räumliche Stern- oder Kalenderstationen nachschlagen.",
    "A3": "28 lokale Arbeits-, Ruhe-, Beschaffungs- oder Sperrregeln konsultieren.",
}

NONMEDICAL_CLAUSES = {
    "H1": ["Wurzelstoff aus dem Bildlos übernehmen", "wässern", "als Standardzusatz ansetzen", "Rest lagern"],
    "H2": ["obere Pflanzenteile übernehmen", "ausziehen", "mit einem Träger verbinden", "zweite Charge buchen"],
    "H3": ["Blüten- oder Krautanteil übernehmen", "ausziehen", "filtrieren", "getrennt verwahren"],
    "H4": ["Blattflotte ansetzen", "weichen Rest abteilen", "zwei Arbeitsfraktionen vergleichen", "Fraktionen buchen"],
    "H5": ["klebriges Feuchtlandmaterial übernehmen", "klein dosieren", "Materialprobe trennen", "trocknen und lagern"],
    "B1": ["Hauptkreislauf beschicken", "temperieren", "absetzen und klären", "weitergeben"],
    "B2": ["Einzelbecken füllen", "Fluss bewegen", "filtern und ablassen", "nachfüllen und übergeben"],
    "B3": ["Mehrbeckenlauf ansetzen", "durch Stationen führen", "absetzen und klären", "Zyklus wiederholen"],
    "B4": ["bezeichneten Lauf warm reinigen", "Rückstand filtern", "unten ablassen", "neu ansetzen"],
    "B5": ["Restbestand abziehen", "einmal erwärmen", "für die Arbeitsfrist halten", "nächster Station übergeben"],
    "B6": ["kalten Vorlauf übernehmen", "filtern", "zum sichtbaren Ziel führen", "offen weitertragen"],
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_formula(formula: str) -> str:
    # Preserve the selected formal tree while removing any temptation to read
    # its descriptive host coordinate as a semantic atom.
    return re.sub(r"UNKNOWN_HOST\[[^\]]+\]", "OPAQUE_PAYLOAD", formula)


def formal_value(formula: str) -> str:
    roles: list[str] = []
    if "SET(<ARG_AIIN>)" in formula:
        roles.append("SET_STANDARD_SLOT")
    elif "SET(<ARG_AL>)" in formula:
        roles.append("SET_LOCAL_RELATION_SLOT")
    elif "SET(" in formula:
        roles.append("SET_OPAQUE_SLOT")
    if "MARK(" in formula:
        roles.append("MARK_OPAQUE_REFERENCE")
    if "LINK" in formula:
        roles.append("LINK_ACTIVE_STATE")
    if "FRAME_OT" in formula:
        roles.append("FRAME_OT")
    elif "FRAME_O" in formula:
        roles.append("FRAME_O")
    if not roles:
        roles.append("OPAQUE_EXACT_CARD")
    if formula.startswith("CLOSE_B3"):
        roles.append("TERMINAL_B3")
    elif formula.startswith("CLOSE"):
        roles.append("TERMINAL")
    return "+".join(roles)


def mnemonic_for(tuple_id: str) -> tuple[str, str]:
    if tuple_id in PORTABLE_MNEMONIC:
        return PORTABLE_MNEMONIC[tuple_id], "EXPLORATORY_SHARED_EXACT_CARD_MNEMONIC"
    if tuple_id in BIO_LOCAL_MNEMONIC:
        return BIO_LOCAL_MNEMONIC[tuple_id]
    return "UNKNOWN", "UNKNOWN"


def strict_prompt(tuple_id: str, surface: str | None = None) -> str:
    prompts: list[str] = []
    if tuple_id in STRICT_CONTROL:
        prompts.append(STRICT_CONTROL[tuple_id])
    if tuple_id == "2f1c5e56e8f0ff459065" and surface == "daiin":
        prompts.append("VORGABEPARAMETER?")
    if tuple_id == "2f1c5e56e8f0ff459065" and surface is None:
        prompts.append("SURFACE_DAIIN_ONLY:VORGABEPARAMETER?")
    return "|".join(prompts) if prompts else "NONE"


def exemplar_status(tuple_id: str, formula: str) -> str:
    mnemonic, scope = mnemonic_for(tuple_id)
    if scope == "EXPLORATORY_SHARED_EXACT_CARD_MNEMONIC":
        return "MEANING_UNCONFIRMED;MNEMONIC_ONLY;LOCAL_EXPANSION_REQUIRES_EXEMPLAR"
    if scope.startswith("BIO_LOCAL_ONLY"):
        return f"MEANING_UNCONFIRMED;{scope};LOCAL_EXPANSION_REQUIRES_EXEMPLAR"
    if any(op in formula for op in ("SET(", "MARK(", "LINK")):
        return "FORMAL_VALUE_ONLY;SOURCE_MEANING_UNKNOWN;LOCAL_EXPANSION_REQUIRES_EXEMPLAR"
    return "UNKNOWN;LOCAL_EXPANSION_REQUIRES_EXEMPLAR"


def clause_for(unit_id: str, position: int, total: int) -> str:
    clauses = NONMEDICAL_CLAUSES[unit_id]
    index = min(len(clauses) - 1, ((position - 1) * len(clauses)) // total)
    return clauses[index]


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def replace_nonmedical(text: str) -> str:
    substitutions = [
        ("withhold treatment", "withhold the work pass"),
        ("avoid invasive treatment", "avoid heavy work"),
        ("apply the remedy", "execute the work order"),
        ("favorable for a warm bath", "favorable for a warm washhouse operation"),
        ("favorable for bathing", "ordinary work permitted"),
        ("avoid a hot bath", "avoid the hot washhouse operation"),
        ("make the ordinary bath", "run the ordinary washhouse operation"),
        ("use a cool washing", "run a cool washing pass"),
        ("bathe until gently warm", "warm the work charge gently"),
        ("bloodletting", "cutting work"),
        ("anointing", "surface finishing"),
        ("anoint", "finish"),
        ("upper body", "upper installation"),
        ("below the waist", "lower installation"),
        ("affected place", "marked worksite"),
        ("keep the patient at rest", "leave the crew and installation idle"),
        ("give no purge", "do not drain"),
        ("dried herb", "dried plant material"),
        ("herbal liquor", "plant-material liquor"),
        ("warm cloth", "warm covering"),
        ("application", "work pass"),
        ("treatment", "work pass"),
        ("remedy", "work order"),
        ("lunar station", "spatial calendar station"),
        ("Moon", "calendar cycle"),
        ("mansion", "calendar station"),
    ]
    result = text
    for old, new in substitutions:
        result = result.replace(old, new)
    return result


def astro_rival(row: dict[str, str]) -> str:
    page = row["page"]
    source_class = row["source_class"]
    number = locus_number(row["locus"])
    if page == "f67r2" and source_class == "ZODIAC_BODY_SAFETY_SELECTOR":
        return f"Arbeitsalmanach-Sektor {number}: Arbeitsbereich {number} schonen und schwere Arbeit dort verschieben"
    if page == "f67r2" and source_class == "ZODIAC_DIVISION":
        role = "lokale Zeitqualität" if "quality" in row["default_English"] else "lokale Arbeitsregel"
        return f"Arbeitsalmanach-Sektor {number}: {role} aus dem Exemplar übernehmen"
    if page == "f68r1" and source_class == "SPATIAL_LUNAR_STATION":
        return f"räumliche Stern- oder Kalenderstation am Locus {row['locus']} nach Bildlage nachschlagen"
    if page == "f68r1" and source_class == "CENTRAL_LUNAR_OWNER":
        return "Zentralzeichen als Besitzer des räumlichen Kalenderkatalogs führen"
    prefix = {
        "f67r2": "Arbeitsalmanach-Auswahl",
        "f68r1": "räumlicher Sternkatalog",
        "f69v": "Arbeitsalmanach-Regel",
    }[page]
    return f"{prefix}: {replace_nonmedical(row['default_English'])}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    src = {name: read_tsv(path) for name, path in P.items()}

    cards_in = src["v49_cards"]
    events_in = src["v49_events"]
    fields_in = src["v49_fields"]
    v43_prose = {r["lexicon_id"]: r for r in src["v43_dictionary"] if r["scope"] == "PROSE_EXACT_CARD"}
    v22_prose_lex = {r["lexicon_id"]: r for r in src["v22_lexicon"] if r["scope"] == "PROSE_EXACT_CARD"}
    astro_in = [r for r in src["v22_ledger"] if r["ledger_scope"] == "ZL3B_ASTRO_VISIBLE_TOKEN"]
    v22_prose_events = [r for r in src["v22_ledger"] if r["ledger_scope"] == "GDT327_PROSE"]

    assert len(cards_in) == 173
    assert len(events_in) == 381
    assert len(fields_in) == 135
    assert len(astro_in) == 395
    assert len(v22_prose_events) == 381
    assert len(v43_prose) == 173
    assert len(v22_prose_lex) == 173
    assert {r["page"] for r in events_in + astro_in} == ALLOWED_PAGES

    card_ids = {r["joint_tuple_id"] for r in cards_in}
    assert card_ids == set(v43_prose) == set(v22_prose_lex)
    for card in cards_in:
        tid = card["joint_tuple_id"]
        assert card["complete_default_German"] == v43_prose[tid]["current_default"]
    for v49, v22 in zip(events_in, v22_prose_events, strict=True):
        assert v49["page"] == v22["page"]
        assert v49["locus"] == v22["locus"]
        assert v49["surface"] == v22["surface"]
        assert v49["joint_tuple_id"] == v22["exact_tuple_id"]

    # Allocate all 381 event rows to the published 135 fields, checking exact
    # surface sequence and counts rather than trusting row totals alone.
    events_by_locus: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for event in events_in:
        events_by_locus[(event["page"], event["record"], event["locus"])].append(event)
    fields_by_locus: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for field in fields_in:
        fields_by_locus[(field["page"], field["record"], field["locus"])].append(field)

    event_field: dict[int, tuple[str, int]] = {}
    field_serial_for_row: dict[int, int] = {}
    field_serial = 0
    for key, locus_fields in fields_by_locus.items():
        locus_events = events_by_locus[key]
        offset = 0
        for field in locus_fields:
            field_serial += 1
            field_serial_for_row[id(field)] = field_serial
            count = int(field["event_count"])
            assigned = locus_events[offset: offset + count]
            assert len(assigned) == count
            assert [e["surface"] for e in assigned] == field["surface_sequence"].split()
            for event in assigned:
                event_field[id(event)] = (f"F{field_serial:03d}", int(field["field_ordinal"]))
            offset += count
        assert offset == len(locus_events)
    assert len(event_field) == 381

    record_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events_in:
        unit_id = RECORD_UNIT[(event["page"], event["record"])]
        record_events[unit_id].append(event)
    record_fields: dict[str, list[dict[str, str]]] = defaultdict(list)
    for field in fields_in:
        unit_id = RECORD_UNIT[(field["page"], field["record"])]
        record_fields[unit_id].append(field)

    event_pos: dict[int, tuple[int, int]] = {}
    event_rival_clause: dict[int, str] = {}
    for unit_id, rows in record_events.items():
        total = len(rows)
        for pos, row in enumerate(rows, start=1):
            event_pos[id(row)] = (pos, total)
            event_rival_clause[id(row)] = clause_for(unit_id, pos, total)

    field_pos: dict[int, tuple[int, int]] = {}
    for unit_id, rows in record_fields.items():
        total = len(rows)
        for pos, row in enumerate(rows, start=1):
            field_pos[id(row)] = (pos, total)

    # Complete 381-event layered interlinear.
    event_rows: list[dict[str, object]] = []
    occurrences: dict[str, list[dict[str, object]]] = defaultdict(list)
    terminal_events = 0
    for serial, event in enumerate(events_in, start=1):
        tid = event["joint_tuple_id"]
        unit_id = RECORD_UNIT[(event["page"], event["record"])]
        pos, total = event_pos[id(event)]
        field_id, field_ord = event_field[id(event)]
        formula_raw = event["formal_formula"]
        terminal = formula_raw.startswith("CLOSE")
        terminal_events += int(terminal)
        mnemonic, mnemonic_scope = mnemonic_for(tid)
        rival_clause = event_rival_clause[id(event)]
        row = {
            "event_serial": serial,
            "page": event["page"],
            "locus": event["locus"],
            "record": event["record"],
            "record_unit_id": unit_id,
            "field_id": field_id,
            "field_ordinal_in_locus": field_ord,
            "event_index_in_locus": event["event_index"],
            "event_index_in_record": pos,
            "surface": event["surface"],
            "joint_tuple_id": tid,
            "formal_formula_opaque": sanitize_formula(formula_raw),
            "FORMAL_VALUE": formal_value(formula_raw),
            "terminal_status": "TERMINAL" if terminal else "NONCLOSE",
            "strict_control_prompt": strict_prompt(tid, event["surface"]),
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": mnemonic,
            "mnemonic_scope": mnemonic_scope,
            "LOCAL_IATROMEDICAL_EXPANSION": event["complete_default_German"],
            "NONMEDICAL_RIVAL": f"{rival_clause} [lokaler {unit_id}-Musterbogenschritt {pos}/{total}; keine Kartenbedeutung]",
            "UNKNOWN_EXEMPLAR_STATUS": exemplar_status(tid, formula_raw),
            "source_lineage": "V43_DEFAULT>V49_EVENT>V50/V51/V56_STRICT_EXACT_BINDING>V59_R1",
        }
        event_rows.append(row)
        occurrences[tid].append(row)
    assert terminal_events == 90

    # Complete 173-card dictionary.  The nonmedical column summarizes only
    # occurrence-local defaults and explicitly refuses a card-level rival word.
    card_rows: list[dict[str, object]] = []
    for card in cards_in:
        tid = card["joint_tuple_id"]
        formula_raw = card["formal_formula"]
        mnemonic, mnemonic_scope = mnemonic_for(tid)
        seen_clauses: list[str] = []
        for occurrence in occurrences[tid]:
            text = str(occurrence["NONMEDICAL_RIVAL"]).split(" [lokaler", 1)[0]
            if text not in seen_clauses:
                seen_clauses.append(text)
        preview = " || ".join(seen_clauses[:4])
        if len(seen_clauses) > 4:
            preview += f" || +{len(seen_clauses) - 4} weitere lokale Defaults"
        pages = []
        for occurrence in occurrences[tid]:
            page = str(occurrence["page"])
            if page not in pages:
                pages.append(page)
        card_rows.append({
            "joint_tuple_id": tid,
            "surface_examples": card["surface_examples"],
            "occurrences": len(occurrences[tid]),
            "pages": "|".join(pages),
            "formal_formula_opaque": sanitize_formula(formula_raw),
            "FORMAL_VALUE": formal_value(formula_raw),
            "strict_control_prompt": strict_prompt(tid),
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": mnemonic,
            "mnemonic_scope": mnemonic_scope,
            "LOCAL_IATROMEDICAL_EXPANSION": card["complete_default_German"],
            "NONMEDICAL_RIVAL": f"OCCURRENCE_EXEMPLAR_ONLY: {preview}",
            "UNKNOWN_EXEMPLAR_STATUS": exemplar_status(tid, formula_raw) + ";NO_CARD_LEVEL_RIVAL_SEMANTICS",
            "source_lineage": "V43_173_CARD_DEFAULT=V49_173_CARD_DEFAULT>V50/V51/V56_STRICT_EXACT_BINDING>V59_R1",
        })
    assert len(card_rows) == 173

    # Complete 135-field edition with whole-field expansions kept separate
    # from the sequence of exact-card mnemonics.
    field_rows: list[dict[str, object]] = []
    terminal_fields = 0
    open_fields = 0
    for field in fields_in:
        unit_id = RECORD_UNIT[(field["page"], field["record"])]
        pos, total = field_pos[id(field)]
        key = (field["page"], field["record"], field["locus"])
        locus_fields = fields_by_locus[key]
        preceding = sum(int(f["event_count"]) for f in locus_fields if int(f["field_ordinal"]) < int(field["field_ordinal"]))
        count = int(field["event_count"])
        assigned = events_by_locus[key][preceding: preceding + count]
        terminal_flags = [e["formal_formula"].startswith("CLOSE") for e in assigned]
        assert sum(terminal_flags) <= 1
        if any(terminal_flags):
            assert terminal_flags[-1]
            closure = "TERMINAL"
            terminal_fields += 1
        else:
            closure = "OPEN"
            open_fields += 1
        mnemonic_sequence = []
        unknown_count = 0
        for event in assigned:
            mnemonic = mnemonic_for(event["joint_tuple_id"])[0]
            mnemonic_sequence.append(mnemonic)
            unknown_count += int(mnemonic == "UNKNOWN")
        rival_clause = clause_for(unit_id, pos, total)
        field_rows.append({
            "field_serial": field_serial_for_row[id(field)],
            "field_id": f"F{field_serial_for_row[id(field)]:03d}",
            "page": field["page"],
            "record": field["record"],
            "record_unit_id": unit_id,
            "locus": field["locus"],
            "field_ordinal_in_locus": field["field_ordinal"],
            "field_ordinal_in_record": pos,
            "event_count": count,
            "surface_sequence": field["surface_sequence"],
            "formal_sequence_opaque": " | ".join(sanitize_formula(e["formal_formula"]) for e in assigned),
            "FORMAL_VALUE": f"FIELD_{closure}:NONCLOSE* TERMINAL?",
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": " | ".join(mnemonic_sequence),
            "LOCAL_IATROMEDICAL_EXPANSION": field["complete_creative_translation_German"],
            "NONMEDICAL_RIVAL": f"{rival_clause} [Ganzfeldexemplar {unit_id}, Feld {pos}/{total}]",
            "UNKNOWN_EXEMPLAR_STATUS": f"WHOLE_FIELD_EXPANSIONS_NOT_COMPOSITIONAL;UNKNOWN_MNEMONIC_EVENTS={unknown_count};EXEMPLAR_REQUIRED",
            "closure_status": closure,
            "source_lineage": "V49_135_FIELD_TRANSLATION>V52_FIELD_GRAMMAR>V53/V54_RECORD_DEFAULTS>V58_RIVAL>V59_R1",
        })
    assert terminal_fields == 90 and open_fields == 45

    # Complete 395-group Astro edition directly inherited from V22, with a
    # separately generated nonmedical local rival and no prose-card import.
    astro_rows: list[dict[str, object]] = []
    for serial, row in enumerate(astro_in, start=1):
        diagram_id = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[row["page"]]
        status = "ASTRO_LOCAL_EXEMPLAR;SEMANTICS_UNANCHORED;NO_PROSE_CARD_IMPORT"
        if row["page"] in {"f68r1", "f69v"}:
            status += ";NO_DIRECT_28_TO_28_JOIN"
        astro_rows.append({
            "astro_serial": serial,
            "page": row["page"],
            "locus": row["locus"],
            "diagram_id": diagram_id,
            "group_index_in_locus": row["event_index"],
            "surface": row["surface"],
            "astro_token_id": row["exact_tuple_id"],
            "FORMAL_VALUE": f"ASTRO_LOCAL_SLOT:{row['source_class']}",
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": "NOT_APPLICABLE_ASTRO_LOCAL",
            "LOCAL_IATROMEDICAL_EXPANSION": row["default_English"],
            "NONMEDICAL_RIVAL": astro_rival(row),
            "UNKNOWN_EXEMPLAR_STATUS": status,
            "source_class": row["source_class"],
            "confidence": row["confidence"],
            "source_lineage": "V22_395_GROUP_LEDGER>V55_LOCAL_DIAGRAM_STATUS>V58_WORK_ALMANAC_RIVAL>V59_R1",
        })
    assert len(astro_rows) == 395

    # Fourteen complete record/diagram texts from selected V53/V54/V55 rows.
    text_rows: list[dict[str, object]] = []
    for row in src["v53_articles"]:
        unit_id = row["article_id"]
        page = row["folio_record"].split("_", 1)[0]
        text_rows.append({
            "unit_id": unit_id,
            "page": page,
            "module": "HERBAL_RECORD",
            "fields_or_loci": row["field_count"],
            "events_or_groups": row["event_count"],
            "FORMAL_VALUE": "PICTURED_OWNER+OPEN_HEAVY_HERBAL_RECORD+FIELD*",
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": row["strict_anchor_summary"],
            "LOCAL_IATROMEDICAL_EXPANSION": row["selected_complete_working_translation_German"],
            "NONMEDICAL_RIVAL": NONMEDICAL_FULL[unit_id],
            "UNKNOWN_EXEMPLAR_STATUS": "PICTURED_OWNER_AND_RECORD_PROSE_EXEMPLAR_REQUIRED;NOT_CARD_COMPOSITION",
            "strongest_contradiction": row["main_contradiction"],
            "teaching_rule": "Bildbesitzer still binden; vollständige lokale Kartenfolge kopieren; offene Felder nicht zu Sätzen machen.",
            "source_lineage": "V53_SELECTED_FIVE_ARTICLES>V58_SELECTED_RIVAL>V59_R1",
        })
    for row in src["v54_bio"]:
        unit_id = row["record_id"]
        text_rows.append({
            "unit_id": unit_id,
            "page": row["folio"],
            "module": "BIOLOGICAL_RECORD",
            "fields_or_loci": row["field_count"],
            "events_or_groups": row["event_count"],
            "FORMAL_VALUE": "PICTURED_WORKCELL_OWNER+SHORT_BIO_CELLS+FIELD*",
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": "V56_CONTROL_CORE+BIO_LOCAL_MNEMONICS;EXACT_ONLY",
            "LOCAL_IATROMEDICAL_EXPANSION": row["complete_working_translation_German"],
            "NONMEDICAL_RIVAL": NONMEDICAL_FULL[unit_id],
            "UNKNOWN_EXEMPLAR_STATUS": "APPARATUS/PATIENT_OWNER_UNRESOLVED;RECORD_PROSE_EXEMPLAR_REQUIRED;NOT_CARD_COMPOSITION",
            "strongest_contradiction": row["main_contradiction"],
            "teaching_rule": "Kurze Zellen und lokale Terminalkarte kopieren; CLOSE nicht sprechen; Gerät und Körper als Bildrivalen führen.",
            "source_lineage": "V54_SELECTED_SIX_BIO_RECORDS>V58_SELECTED_RIVAL>V59_R1",
        })
    for row in src["v55_diagrams"]:
        unit_id = row["diagram_id"]
        text_rows.append({
            "unit_id": unit_id,
            "page": row["folio"],
            "module": "ASTRO_DIAGRAM",
            "fields_or_loci": row["locus_count"],
            "events_or_groups": row["group_count"],
            "FORMAL_VALUE": row["selected_formal_role"],
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": "NOT_APPLICABLE_ASTRO_LOCAL",
            "LOCAL_IATROMEDICAL_EXPANSION": row["complete_working_translation_German"],
            "NONMEDICAL_RIVAL": NONMEDICAL_FULL[unit_id],
            "UNKNOWN_EXEMPLAR_STATUS": "ASTRO_LOCAL_EXEMPLAR;SEMANTICS_UNANCHORED;NO_PROSE_CARD_IMPORT;NO_DIRECT_CROSSPAGE_MAPPING",
            "strongest_contradiction": row["main_contradiction"],
            "teaching_rule": "Geometrie und lokales Label gemeinsam kopieren; weder Prosaglosse noch stillen 28er-Index importieren.",
            "source_lineage": "V22_395_GROUP_LEDGER>V55_SELECTED_THREE_DIAGRAMS>V58_SELECTED_RIVAL>V59_R1",
        })
    assert len(text_rows) == 14

    # Common 776-visible-unit edition.
    combined_rows: list[dict[str, object]] = []
    for event in event_rows:
        combined_rows.append({
            "visible_unit_serial": len(combined_rows) + 1,
            "register": "PROSE_HERBAL" if str(event["record_unit_id"]).startswith("H") else "PROSE_BIOLOGICAL",
            "page": event["page"],
            "locus": event["locus"],
            "record_or_diagram": event["record_unit_id"],
            "position": f"{event['field_id']}:E{event['event_index_in_record']}",
            "surface": event["surface"],
            "exact_identity": event["joint_tuple_id"],
            "FORMAL_VALUE": event["FORMAL_VALUE"],
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": event["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            "LOCAL_IATROMEDICAL_EXPANSION": event["LOCAL_IATROMEDICAL_EXPANSION"],
            "NONMEDICAL_RIVAL": event["NONMEDICAL_RIVAL"],
            "UNKNOWN_EXEMPLAR_STATUS": event["UNKNOWN_EXEMPLAR_STATUS"],
            "source_lineage": event["source_lineage"],
        })
    for astro in astro_rows:
        combined_rows.append({
            "visible_unit_serial": len(combined_rows) + 1,
            "register": "ASTRO_LOCAL",
            "page": astro["page"],
            "locus": astro["locus"],
            "record_or_diagram": astro["diagram_id"],
            "position": f"G{astro['group_index_in_locus']}",
            "surface": astro["surface"],
            "exact_identity": astro["astro_token_id"],
            "FORMAL_VALUE": astro["FORMAL_VALUE"],
            "ATOMIC_OR_WHOLE_CARD_MNEMONIC": astro["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
            "LOCAL_IATROMEDICAL_EXPANSION": astro["LOCAL_IATROMEDICAL_EXPANSION"],
            "NONMEDICAL_RIVAL": astro["NONMEDICAL_RIVAL"],
            "UNKNOWN_EXEMPLAR_STATUS": astro["UNKNOWN_EXEMPLAR_STATUS"],
            "source_lineage": astro["source_lineage"],
        })
    assert len(combined_rows) == 776

    card_fields = [
        "joint_tuple_id", "surface_examples", "occurrences", "pages",
        "formal_formula_opaque", "FORMAL_VALUE", "strict_control_prompt",
        "ATOMIC_OR_WHOLE_CARD_MNEMONIC", "mnemonic_scope",
        "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS", "source_lineage",
    ]
    event_fields = [
        "event_serial", "page", "locus", "record", "record_unit_id",
        "field_id", "field_ordinal_in_locus", "event_index_in_locus",
        "event_index_in_record", "surface", "joint_tuple_id",
        "formal_formula_opaque", "FORMAL_VALUE", "terminal_status",
        "strict_control_prompt", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "mnemonic_scope", "LOCAL_IATROMEDICAL_EXPANSION",
        "NONMEDICAL_RIVAL", "UNKNOWN_EXEMPLAR_STATUS", "source_lineage",
    ]
    field_fields = [
        "field_serial", "field_id", "page", "record", "record_unit_id",
        "locus", "field_ordinal_in_locus", "field_ordinal_in_record",
        "event_count", "surface_sequence", "formal_sequence_opaque",
        "FORMAL_VALUE", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS", "closure_status", "source_lineage",
    ]
    astro_fields = [
        "astro_serial", "page", "locus", "diagram_id",
        "group_index_in_locus", "surface", "astro_token_id",
        "FORMAL_VALUE", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS", "source_class", "confidence",
        "source_lineage",
    ]
    text_fields = [
        "unit_id", "page", "module", "fields_or_loci", "events_or_groups",
        "FORMAL_VALUE", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS", "strongest_contradiction",
        "teaching_rule", "source_lineage",
    ]
    combined_fields = [
        "visible_unit_serial", "register", "page", "locus",
        "record_or_diagram", "position", "surface", "exact_identity",
        "FORMAL_VALUE", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS", "source_lineage",
    ]

    output_paths = {
        "cards": OUT / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv",
        "events": OUT / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv",
        "fields": OUT / "V59_R1_FINAL_135_FIELD_EDITION.tsv",
        "astro": OUT / "V59_R1_FINAL_395_ASTRO_GROUP_EDITION.tsv",
        "texts": OUT / "V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv",
        "combined": OUT / "V59_R1_FINAL_776_VISIBLE_UNIT_EDITION.tsv",
    }
    write_tsv(output_paths["cards"], card_rows, card_fields)
    write_tsv(output_paths["events"], event_rows, event_fields)
    write_tsv(output_paths["fields"], field_rows, field_fields)
    write_tsv(output_paths["astro"], astro_rows, astro_fields)
    write_tsv(output_paths["texts"], text_rows, text_fields)
    write_tsv(output_paths["combined"], combined_rows, combined_fields)

    required_layers = [
        "FORMAL_VALUE", "ATOMIC_OR_WHOLE_CARD_MNEMONIC",
        "LOCAL_IATROMEDICAL_EXPANSION", "NONMEDICAL_RIVAL",
        "UNKNOWN_EXEMPLAR_STATUS",
    ]
    for rows in (card_rows, event_rows, field_rows, astro_rows, text_rows, combined_rows):
        for row in rows:
            for layer in required_layers:
                assert str(row[layer]).strip()

    allowed_mnemonics = {
        "UNKNOWN", "MASS?", "VERWENDEN?", "BEREIT?", "BEREITUNG?",
        "AN?", "KLAR?", "ZUVOR?", "TEIL?", "ABLASSEN?", "SPÜLEN?",
        "WARM?", "NOT_APPLICABLE_ASTRO_LOCAL",
    }
    assert {str(r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]) for r in card_rows} <= allowed_mnemonics
    assert {str(r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]) for r in event_rows} <= allowed_mnemonics

    strict_event_rows = [r for r in event_rows if r["strict_control_prompt"] != "NONE"]
    strict_field_ids = {r["field_id"] for r in strict_event_rows}
    formal_event_rows = [
        r for r in event_rows
        if any(tag in str(r["FORMAL_VALUE"]) for tag in ("SET_", "MARK_", "LINK_"))
    ]
    named_mnemonic_rows = [
        r for r in event_rows if r["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != "UNKNOWN"
    ]
    formal_serials = {r["event_serial"] for r in formal_event_rows}
    mnemonic_serials = {r["event_serial"] for r in named_mnemonic_rows}
    assert len(strict_event_rows) == 45
    assert len(strict_field_ids) == 35
    assert len(formal_event_rows) == 57
    assert len(named_mnemonic_rows) == 85
    assert not (formal_serials & mnemonic_serials)
    assert len(formal_serials | mnemonic_serials) == 142
    annotated_serials = formal_serials | mnemonic_serials
    events_by_final_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_final_field[str(row["field_id"])].append(row)
    annotated_field_ids = {
        str(row["field_id"]) for row in event_rows if row["event_serial"] in annotated_serials
    }
    fully_annotated_fields = sum(
        all(row["event_serial"] in annotated_serials for row in rows)
        for rows in events_by_final_field.values()
    )
    assert len(annotated_field_ids) == 82
    assert len(events_by_final_field) - len(annotated_field_ids) == 53
    assert fully_annotated_fields == 17

    # The identity constraint concerns the three complete radial entries.  One
    # additional surface-homograph occurs inside the circular instruction prose
    # and belongs to a different local slot.
    okeod = [
        r for r in astro_rows
        if r["page"] == "f69v"
        and r["surface"] == "okeod"
        and str(r["source_class"]).startswith("MANSION_ELECTION_RULE")
    ]
    assert len(okeod) == 3
    assert len({r["LOCAL_IATROMEDICAL_EXPANSION"] for r in okeod}) == 1
    assert len({r["NONMEDICAL_RIVAL"] for r in okeod}) == 1

    validation = {
        "status": "PASS",
        "scope": {
            "pages": sorted(ALLOWED_PAGES),
            "page_count": 10,
            "prose_record_count": 11,
            "astro_diagram_count": 3,
            "complete_text_count": 14,
        },
        "counts": {
            "exact_prose_cards": len(card_rows),
            "prose_events": len(event_rows),
            "prose_fields": len(field_rows),
            "astro_groups": len(astro_rows),
            "visible_units": len(combined_rows),
            "complete_record_diagram_texts": len(text_rows),
            "open_fields": open_fields,
            "terminal_fields": terminal_fields,
            "terminal_events": terminal_events,
            "tier_a_strict_prompt_events": len(strict_event_rows),
            "tier_a_strict_prompt_fields": len(strict_field_ids),
            "domain_neutral_formal_operation_events": len(formal_event_rows),
            "exact_card_mnemonic_events": len(named_mnemonic_rows),
            "formal_or_exact_mnemonic_annotated_events": len(formal_serials | mnemonic_serials),
            "strict_unknown_exemplar_events": len(event_rows) - len(formal_serials | mnemonic_serials),
            "fields_with_formal_or_exact_mnemonic_anchor": len(annotated_field_ids),
            "fields_without_formal_or_exact_mnemonic_anchor": len(events_by_final_field) - len(annotated_field_ids),
            "fully_formal_or_exact_mnemonic_annotated_fields": fully_annotated_fields,
        },
        "page_event_counts": dict(sorted(Counter(r["page"] for r in event_rows).items())),
        "page_astro_group_counts": dict(sorted(Counter(r["page"] for r in astro_rows).items())),
        "unit_text_counts": dict(sorted(Counter(r["module"] for r in text_rows).items())),
        "event_mnemonic_scope_counts": dict(sorted(Counter(r["mnemonic_scope"] for r in event_rows).items())),
        "card_mnemonic_scope_counts": dict(sorted(Counter(r["mnemonic_scope"] for r in card_rows).items())),
        "assertions": {
            "all_required_layers_nonblank": True,
            "exact_tuple_ids_equal_in_v43_v49_v22": True,
            "v43_and_v49_card_defaults_identical": True,
            "v49_and_v22_prose_event_identity_aligned": True,
            "all_events_assigned_once_to_published_fields": True,
            "field_surface_sequences_exact": True,
            "field_grammar_NONCLOSE_star_TERMINAL_optional": True,
            "no_host_coordinate_used_as_semantic_key": True,
            "mnemonics_bound_by_exact_tuple_id_only": True,
            "phrase_sized_stem_glosses_absent": True,
            "astro_prose_card_import_absent": True,
            "direct_f68_f69_join_absent": True,
            "okeod_three_occurrences_identity_consistent": True,
            "out_of_scope_pages_absent": True,
            "semantic_proof_claim_absent": True,
        },
        "formula": {
            "id": FORMULA_ID,
            "occurrences": 2,
            "status": "MEMORIZED_EXACT_FORM_ONLY;SEMANTIC_EXPANSION_UNKNOWN",
        },
        "source_sha256": {name: sha256(path) for name, path in P.items()},
        "output_sha256": {name: sha256(path) for name, path in output_paths.items()},
    }
    with (OUT / "V59_R1_VALIDATION.json").open("w", encoding="utf-8") as handle:
        json.dump(validation, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps({"status": "PASS", "counts": validation["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
