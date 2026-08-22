#!/usr/bin/env python3
"""Build the bounded V79 R4 apprentice reconstruction audit.

Creative fixed-page sidequest only.  This script reads the already selected
V78 prose and V75 celestial editions; it never reads a manuscript source.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
V78_EVENTS = YOLO / "sidequest_theory_candidates_v78" / "V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = YOLO / "sidequest_theory_candidates_v78" / "V78_SELECTED_116_STATEMENTS.tsv"
V75_LOCI = YOLO / "sidequest_theory_candidates_v75" / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


events = read_tsv(V78_EVENTS)
statements = read_tsv(V78_STATEMENTS)
astro_loci = read_tsv(V75_LOCI)

assert len(events) == 381
assert len(statements) == 116
assert len(astro_loci) == 142
assert not any(row["page"].startswith("f84") for row in events + astro_loci)


manual_rows = [
    ("M01", "SEITE_UND_REGISTER", "Bestimme Herbal, Biological oder Astro nur aus der bereits gezeichneten Seite.", "Kein Register darf Kartenbedeutungen aus einem anderen Register erben."),
    ("M02", "SICHTBARER_BESITZER", "Öffne am Bild den kleinsten sichtbaren Besitzer: Pflanze, lokale Bio-Station oder lokales Himmelsfeld.", "Eine sichtbare Lücke setzt Stoff, Ziel und Richtung zurück."),
    ("M03", "EXAKTE_KARTE", "Kopiere jede opake Ganzkarte aus dem Meisterexemplar in derselben Reihenfolge.", "Keine Karte wird aus Stamm, Klang, PAGE_HOST oder moderner Wortähnlichkeit erzeugt."),
    ("M04", "FELD_UND_AUSSAGE", "Ein Feld ist ein Kopierfach; die Aussage darf über Feld und physische Zeile weiterlaufen.", "Zeilenende ist nicht automatisch Satzende."),
    ("M05", "CLOSE", "DY/B3-artige Close-Zustände schließen das lokale Fach, nicht notwendig einen sprachlichen Satz.", "Close ist eine Formregel und kein historisch attestiertes Wort."),
    ("M06", "OWNER_RESET", "Bei sichtbarem Besitzerwechsel beginne einen neuen lokalen Gegenstand, selbst wenn dieselbe Aussage weiterläuft.", "Keine unsichtbare Leitung oder Richtung über die Lücke ergänzen."),
    ("M07", "READ_ONCE_CARRY", "Steht dieselbe exakte Karte unmittelbar am Ende einer physischen Zeile und am Anfang der nächsten, bei gleicher Aussage und gleichem Besitzer und ohne Close dazwischen, lies die erste Kopie als Randvorausnahme und die zweite als Haupttoken.", "Allgemeine sichtbare Hypothese; keine locus-spezifische Ausnahme und kein behaupteter Standard-Catchword."),
    ("M08", "ET_FRAGEZEICHEN", "Die Karte dcda… darf probeweise als ET? (UND/AUCH?) gelesen werden.", "Sie bleibt gegen einen lautlosen LINK/SLOT formal ununterscheidbar."),
    ("M09", "PER_FRAGEZEICHEN", "Die Karte b5fcea… darf probeweise als PER? (DURCH/GEMÄSS?) gelesen werden; eine Read-once-Paarung zählt als ein Quelltoken.", "Sie bleibt gegen ENTRY/RESET formal ununterscheidbar."),
    ("M10", "FORMALPROMPTS", "Die zwei eingefrorenen Parameter-/Relationskanäle werden als Formanweisungen, nicht als Wörter, geführt.", "Sie dürfen keine deutsche Lexikglosse erhalten."),
    ("M11", "EXEMPLARSCHWANZ", "Alle übrigen konkreten Inhalte werden occurrence-gebunden aus dem Meisterexemplar gelernt und ausdrücklich als [EXEMPLAR:…] markiert.", "Ohne Exemplar bleibt der Wert UNKNOWN; nicht erraten."),
    ("M12", "ASTRO_NAMENSRAUM", "Kopiere jedes Astro-Etikett nur in seinem lokalen Rad-, Feld- oder Sternplatz-Namensraum.", "Kein Start, keine Drehrichtung und kein f68↔f69-Schlüssel."),
]
manual = [
    {"rule_id": rid, "state": state, "apprentice_instruction": instruction, "guard": guard}
    for rid, state, instruction, guard in manual_rows
]
write_tsv(HERE / "V79_R4_COMPACT_MANUAL.tsv", list(manual[0]), manual)


line_rows: list[dict[str, object]] = []
for before, after in zip(events, events[1:]):
    if before["statement_id"] != after["statement_id"] or before["locus"] == after["locus"]:
        continue
    same_card = before["joint_tuple_id"] == after["joint_tuple_id"]
    same_owner = before["image_owner_id"] == after["image_owner_id"]
    no_close = before["terminal_status"] == "NONCLOSE"
    predicate = same_card and same_owner and no_close
    owner_reset = after["owner_break_before"].startswith("BREAK_VISIBLE_GAP")
    line_rows.append(
        {
            "transition_id": f"L{len(line_rows) + 1:02d}",
            "record_unit_id": before["record_unit_id"],
            "statement_id": before["statement_id"],
            "before_event": before["event_id"],
            "after_event": after["event_id"],
            "before_locus": before["locus"],
            "after_locus": after["locus"],
            "before_tuple": before["joint_tuple_id"],
            "after_tuple": after["joint_tuple_id"],
            "same_exact_card": "YES" if same_card else "NO",
            "same_visible_owner": "YES" if same_owner else "NO",
            "no_close_between": "YES" if no_close else "NO",
            "visible_owner_reset": "YES" if owner_reset else "NO",
            "generic_read_once_predicate": "MATCH" if predicate else "NO_MATCH",
            "selected_reading": "ONE_SOURCE_TOKEN__FIRST_ANTICIPATORY_COPY" if predicate else "ORDINARY_CROSS_LINE_CONTINUATION",
            "remaining_rival": "INTENTIONAL_REPETITION_OR_LOCAL_DITTOGRAPHY" if predicate else "NONE",
        }
    )

line_fields = list(line_rows[0])
write_tsv(HERE / "V79_R4_19_LINE_TRANSITION_AUDIT.tsv", line_fields, line_rows)


def prose_unit(unit: str) -> list[dict[str, str]]:
    return [row for row in events if row["record_unit_id"] == unit]


h2 = prose_unit("H2")
b2 = prose_unit("B2")
a3_slots = [
    row
    for row in astro_loci
    if row["diagram_id"] == "A3" and row["local_image_owner"].startswith("A3_LEFT_RADIAL_SLOT_")
]
assert len(h2) == 24
assert len(b2) == 62
assert len(a3_slots) == 28


def control_counts(rows: list[dict[str, str]]) -> tuple[int, int, int]:
    et = sum(row["portable_token_or_formal_prompt"].startswith("ET?") for row in rows)
    per = sum(row["portable_token_or_formal_prompt"].startswith("PER?") for row in rows)
    formal = sum(row["portable_status"] == "FORMAL_LABEL_NOT_WORD" for row in rows)
    return et, per, formal


def exact_sequence(rows: list[dict[str, str]]) -> str:
    return ">".join(row["joint_tuple_id"] for row in rows)


traces: list[dict[str, object]] = []


def add_prose_traces(unit: str, rows: list[dict[str, str]], visible_note: str) -> None:
    et, per, formal = control_counts(rows)
    n = len(rows)
    logical = n - (1 if unit == "B2" else 0)
    source = " ".join(row["selected_continuous_event_token"] for row in rows)
    sequence = exact_sequence(rows)
    common = {
        "unit_id": unit,
        "visible_owner_or_namespace": visible_note,
        "visible_item_count": n,
        "logical_item_count_after_read_once": logical,
        "taught_word_candidates": f"ET={et};PER_VISIBLE={per}",
        "formal_nonword_events": formal,
    }
    variants = [
        ("FORWARD", "WITH_MASTER_EXEMPLAR", "owner+source expansion+master card ledger", sequence, "COMPLETE", "COMPLETE_BY_LOOKUP", "The apprentice copies, does not derive, the opaque sequence."),
        ("BACKWARD", "WITH_MASTER_EXEMPLAR", "visible card sequence+owner+master card ledger", source, "COMPLETE", "COMPLETE_BY_LOOKUP", "The ledger supplies every bracketed source expansion."),
        ("FORWARD", "WITHOUT_MASTER_EXEMPLAR", "owner+intended source expansion only", "ET?/PER?/formal channel positions cannot determine the remaining opaque cards", "INCOMPLETE", "ZERO_INDEPENDENT_CONCRETE_CONTENT", "Opaque card selection is underdetermined."),
        ("BACKWARD", "WITHOUT_MASTER_EXEMPLAR", "visible card sequence+owner only", f"ET?={et}; PER?={per}; formal nonwords={formal}; other values UNKNOWN", "VISIBLE_FORM_ONLY", "ZERO_INDEPENDENT_CONCRETE_CONTENT", "Formal skeleton survives; source content does not."),
    ]
    for direction, access, input_layer, output, form, content, error in variants:
        traces.append(
            {
                "trace_id": f"T{len(traces) + 1:02d}",
                **common,
                "direction": direction,
                "master_exemplar_access": access,
                "input_layer": input_layer,
                "reconstructed_output": output,
                "exact_form_recovery": form,
                "concrete_content_recovery": content,
                "line_carry_handling": "E180/E181_READ_ONCE_BY_GENERIC_RULE" if unit == "B2" else "NO_MATCH_IN_UNIT",
                "decisive_error_or_limit": error,
            }
        )


add_prose_traces("H2", h2, "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB")
add_prose_traces("B2", b2, "FIVE_LOCAL_F82R_STATIONS_WITH_RESETS")

a3_labels = ">".join(row["opaque_group_ids"] for row in a3_slots)
a3_count = sum(int(row["group_count"]) for row in a3_slots)
for direction, access, input_layer, output, form, content, error in [
    ("FORWARD", "WITH_MASTER_EXEMPLAR", "left-wheel geometry+28 local exemplar labels", a3_labels, "COMPLETE", "LOCAL_LABELS_COMPLETE_BY_LOOKUP", "Start and direction remain editorial, not recovered."),
    ("BACKWARD", "WITH_MASTER_EXEMPLAR", "28 visible local labels+master atlas", "28 distinct local slot entries; no ordered rule sequence", "COMPLETE", "LOCAL_LABELS_COMPLETE_BY_LOOKUP", "No external celestial names are licensed."),
    ("FORWARD", "WITHOUT_MASTER_EXEMPLAR", "left-wheel geometry only", "28 empty local addresses; opaque labels underdetermined", "INCOMPLETE", "ZERO_EXTERNAL_LABEL_RECOVERY", "Geometry does not select the copied strings."),
    ("BACKWARD", "WITHOUT_MASTER_EXEMPLAR", "28 visible local labels only", "28 anonymous local labels in one wheel namespace", "VISIBLE_FORM_ONLY", "ZERO_EXTERNAL_LABEL_RECOVERY", "Neither external referents nor reading order are recoverable."),
]:
    traces.append(
        {
            "trace_id": f"T{len(traces) + 1:02d}",
            "unit_id": "A3_LEFT_28",
            "visible_owner_or_namespace": "A3_LEFT_WHEEL_ONLY",
            "visible_item_count": a3_count,
            "logical_item_count_after_read_once": a3_count,
            "taught_word_candidates": "ET=0;PER_VISIBLE=0",
            "formal_nonword_events": 0,
            "direction": direction,
            "master_exemplar_access": access,
            "input_layer": input_layer,
            "reconstructed_output": output,
            "exact_form_recovery": form,
            "concrete_content_recovery": content,
            "line_carry_handling": "NOT_APPLICABLE",
            "decisive_error_or_limit": error,
        }
    )

write_tsv(HERE / "V79_R4_FORWARD_BACKWARD_TRACES.tsv", list(traces[0]), traces)


error_rows = [
    ("E01", "MASTER_EXEMPLAR_ABSENT", "ALL", "Concrete source content cannot be reconstructed independently.", "HARD", "Retain EXAMPLAR_VALUE_UNKNOWN; do not invent a word."),
    ("E02", "E180_E181_DUPLICATE", "B2", "Two visible PER? copies precede one complement.", "REPAIRED_PROVISIONALLY", "Apply M07; count one source token, while preserving both visible events."),
    ("E03", "OWNER_RESET_INSIDE_STATEMENT", "PROSE", "Four of 19 cross-line transitions change visible owner inside the selected statement.", "HARD", "Reset substance/target/direction; syntax may continue but referent may not."),
    ("E04", "ET_VS_SILENT_LINK", "PROSE", "The same 19 positions admit an unspoken structural link.", "UNRESOLVED", "ET? remains a learned codebook-compatible convention, not an internally proven word."),
    ("E05", "PER_VS_ENTRY_RESET", "PROSE", "The nine positions admit a formal entry or scope-reset mark.", "UNRESOLVED", "PER? remains provisional even if M07 is teachable."),
    ("E06", "PHYSICAL_LINE_AS_SENTENCE", "PROSE", "Nineteen selected statement transitions cross physical loci.", "REJECTED", "Carry statement state across the line unless Close/statement boundary says otherwise."),
    ("E07", "ASTRO_ORDER", "A3_LEFT_28", "Twenty-eight local places have no authorial start or direction.", "HARD", "Use addresses only; do not turn the wheel into an ordered 28-rule text."),
    ("E08", "F68_F69_KEY", "ASTRO", "No visible key joins the namespaces.", "HARD", "Keep pages independent."),
    ("E09", "CLOSE_AS_WORD", "PROSE", "Terminal forms are position-confounded and unattested as words.", "REJECTED", "Teach Close only as renderer/form state."),
    ("E10", "OPAQUE_TAIL_LOAD", "ALL", "Most exact values must be copied or memorized occurrence by occurrence.", "HARD", "Call the system exemplar-learnable, not independently decipherable."),
]
errors = [
    {"error_id": eid, "failure": failure, "scope": scope, "observation": observation, "status": status, "repair_or_ceiling": repair}
    for eid, failure, scope, observation, status, repair in error_rows
]
write_tsv(HERE / "V79_R4_ERROR_AUDIT.tsv", list(errors[0]), errors)


outputs = [
    HERE / "V79_R4_CHANCERY_APPRENTICE_AUDIT.md",
    HERE / "V79_R4_COMPACT_MANUAL.tsv",
    HERE / "V79_R4_19_LINE_TRANSITION_AUDIT.tsv",
    HERE / "V79_R4_FORWARD_BACKWARD_TRACES.tsv",
    HERE / "V79_R4_ERROR_AUDIT.tsv",
]
summary = {
    "schema": "SIDEQUEST_V79_R4_BUILD_V1",
    "status": "PASS",
    "input_bindings": {path.name: sha256(path) for path in (V78_EVENTS, V78_STATEMENTS, V75_LOCI)},
    "counts": {
        "manual_rules": len(manual),
        "cross_line_transitions": len(line_rows),
        "generic_read_once_matches": sum(row["generic_read_once_predicate"] == "MATCH" for row in line_rows),
        "owner_resets_in_cross_line_transitions": sum(row["visible_owner_reset"] == "YES" for row in line_rows),
        "trace_rows": len(traces),
        "error_rows": len(errors),
        "h2_events": len(h2),
        "b2_events": len(b2),
        "a3_left_slots": len(a3_slots),
        "a3_left_groups": a3_count,
    },
    "output_hashes": {path.name: sha256(path) for path in outputs},
    "word_candidates": ["ET?", "PER?"],
    "new_words_added": 0,
    "f84_opened": False,
    "f84r_opened": False,
    "semantic_ceiling": "FORMAL_COPYING_RECOVERABLE_WITH_EXEMPLAR__CONCRETE_CONTENT_NOT_RECOVERABLE_WITHOUT_EXEMPLAR",
}
(HERE / "V79_R4_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
