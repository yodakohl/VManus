#!/usr/bin/env python3
"""Render the complete GDT599 object edition with a compact surface grammar.

GDT600 changes no selected object, source pointer, state transition, host,
paragraph, root, page, or manuscript segmentation.  It only replaces recurring
German workshop-language defects and exposes two GDT599 provenance families
that were previously represented by individual or overly broad cards.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt600_complete_object_surface_grammar"
ARTIFACTS = BASE / "artifacts"
G599 = ROOT / "experiments/yolo/gdt599_remaining_action_object_completion/artifacts"

PAGES = ("f75r", "f77r", "f81r", "f81v", "f82r", "f83r")
ACTION_ROOTS = {"CH", "K", "OK", "P", "R", "SH", "T", "S", "CHD"}
GUARD = "GDT599_PUBLISHED_SIX_PAGE_ARTIFACTS_ONLY__SURFACE_GRAMMAR_ONLY"

SOURCE_RAW = "von der Ausgangsstation oder aus dem Ausgangsbecken"
SOURCE_CASED = "aus der Ausgangsstation oder dem Ausgangsbecken"
SOURCE_CONDITION = "nach dem Zustand der Ausgangsstation oder des Ausgangsbeckens"
SOURCE_FRAME = "ausgehend von der Ausgangsstation oder dem Ausgangsbecken"
TARGET_RAW = "zur Zielstation oder ins Zielbecken"
TARGET_DIRECTION = "zur Zielstation oder in das Zielbecken"
TARGET_FLOW_DIRECTION = "zur Zielstation hin beziehungsweise in das Zielbecken"
TARGET_RECIPIENT = "der Zielstation oder dem Zielbecken"
TARGET_PURPOSE = "für die Zielstation oder das Zielbecken"
TARGET_STATIC = "an der Zielstation oder im Zielbecken"
CONTACT_RAW = "über den Stationskontakt oder die Leitung"
CONTACT_SHORT = "über Kontakt oder Leitung"


INPUTS = {
    "hosts": G599 / "gdt599_2272_complete_host_edition.tsv",
    "actions": G599 / "gdt599_1443_complete_action_edition.tsv",
    "statements": G599 / "gdt599_313_complete_statements.tsv",
    "replay": G599 / "gdt599_793_remaining_action_object_replay.tsv",
    "q_transitions": G599 / "gdt599_24_action_q_result_transitions.tsv",
    "manual_decisions": G599 / "gdt599_11_manual_workshop_decisions.tsv",
    "manual_polish": G599 / "gdt599_3_manual_clause_polish.tsv",
    "review_queue": G599 / "gdt599_projection_review_queue.tsv",
    "defaults": G599 / "gdt599_6_root_default_cards.tsv",
    "aiin_bindings": G599 / "gdt599_46_aiin_quantity_bindings.tsv",
    "propagation": G599 / "gdt599_3_override_propagation_effects.tsv",
    "local_cards": G599 / "gdt599_40_local_card_passthrough.tsv",
    "manual_reviews": G599 / "gdt599_40_inherited_manual_reviews.tsv",
}

OUTPUTS = {
    "actions": ARTIFACTS / "gdt600_1443_surface_action_edition.tsv",
    "hosts": ARTIFACTS / "gdt600_2272_surface_host_edition.tsv",
    "statements": ARTIFACTS / "gdt600_313_surface_statements.tsv",
    "rules": ARTIFACTS / "gdt600_renderer_rule_cards.tsv",
    "changes": ARTIFACTS / "gdt600_clause_change_audit.tsv",
    "flow_generalizations": ARTIFACTS / "gdt600_7_flow_rule_generalizations.tsv",
    "manual_remaining": ARTIFACTS / "gdt600_4_remaining_manual_object_decisions.tsv",
    "condition_relations": ARTIFACTS / "gdt600_6_condition_relation_rules.tsv",
    "bounded_right": ARTIFACTS / "gdt600_21_bounded_right_provenance.tsv",
    "q_grammar": ARTIFACTS / "gdt600_24_q_result_grammar.tsv",
    "q_followups": ARTIFACTS / "gdt600_7_q_result_followups.tsv",
    "repeats": ARTIFACTS / "gdt600_18_repeat_markers.tsv",
    "control_repeats": ARTIFACTS / "gdt600_34_control_repeat_markers.tsv",
    "reviews": ARTIFACTS / "gdt600_125_review_passthrough.tsv",
    "aiin_passthrough": ARTIFACTS / "gdt600_46_aiin_quantity_passthrough.tsv",
    "propagation_passthrough": ARTIFACTS / "gdt600_3_override_propagation_passthrough.tsv",
    "local_passthrough": ARTIFACTS / "gdt600_40_local_card_passthrough.tsv",
    "manual_review_passthrough": ARTIFACTS / "gdt600_40_inherited_manual_review_passthrough.tsv",
    "pages": ARTIFACTS / "gdt600_6_page_profiles.tsv",
    "reader": ARTIFACTS / "GDT600_SURFACE_GRAMMAR_READER.md",
    "result": ARTIFACTS / "gdt600_result.json",
    "validation": ARTIFACTS / "gdt600_validation.json",
}


RULE_SPECS = {
    "R01_CH_LINE_FLOW_GENERALIZATION": "Sieben lokale CH+Leitung-Fälle als eine post-selection FLOW-Regel statt sieben Einzelentscheidungen führen.",
    "R02_CH_OBJECT_VALENCY": "CH nach Objektklasse und sichtbarem Abflusspfad als entnehmen, herausnehmen oder ablassen sprechen.",
    "R03_OK_PREPARE": "Das doppelte OK-Verb in allen belegten Objektklassen als vorbereiten sprechen.",
    "R04_CONDITION_SOURCE": "T+CONDITION+SOURCE nach dem Ausgangszustand einstellen.",
    "R05_CONDITION_TARGET": "T+CONDITION+TARGET für Zielstation oder Zielbecken regulieren.",
    "R06_SOURCE_CASE": "Quellenangabe als Herkunft aus der Ausgangsstation oder dem Ausgangsbecken realisieren.",
    "R07_TARGET_VALENCY": "Zielangabe je nach Empfänger, Flussrichtung, statischer oder zweckbezogener Handlung realisieren.",
    "R08_CONTACT_SHORT": "Den Pfad knapp als über Kontakt oder Leitung sprechen.",
    "R09_WORKSITE_SHORT": "Stations-Ortsbezeichnungen in der deutschen Oberfläche kürzen.",
    "R10_PROCESS_GRADE": "Grad außerhalb von T als Arbeitsbedingung bei Grad statt Zielzustand auf Grad sprechen.",
    "R11_MULTI_GRADE": "Zwei sichtbare Grade als Gradangaben nennen, ohne Gleichzeitigkeit zu erfinden.",
    "R12_MODIFIER_ORDER": "Erkannte Modifier als Modus, Grad, Bad, Arbeitsort, Quelle, Pfad und Ziel ordnen.",
    "R13_FRAME_COMPLETE": "Das strukturelle Verwende-für-Fragment als vollständigen Ausführungsimperativ sprechen.",
    "R14_Q_RESULT_STATE": "Q nach abgeschlossener Eingangsaktion als nachfolgende Zustandsdeklaration sprechen.",
    "R15_Q_FOLLOWUP_NEW": "Die erste Folgeaktion nach Q auch über CARRY/HANDOFF-Aliase auf diesen neuen Stationsansatz beziehen.",
    "R16_REPEAT_AGAIN": "Die nächste identische Aktion desselben Arbeitsgangs auch über OL- und Rahmenhosts hinweg mit erneut markieren.",
    "R17_PROBE_REFERENCE": "Die Probe bei Erstentnahme unbestimmt und bei der Folgeaktion demonstrativ sprechen.",
    "R18_BODY_PART_GENDER": "Den einmaligen falschen Neutrumbezug auf den maskulinen Körperteil korrigieren.",
    "R19_K_SOURCE_VALENCY": "K mit sichtbarer Quelle, aber ohne Empfänger als Heranführen oder Heranbringen sprechen.",
    "R20_FRAME_GRADE_SCOPE": "T-gebundene FRAME-Grade als Einstellung und ungebundene FRAME-Grade neutral als Gradangabe sprechen.",
    "R21_PEER_MODE_COORDINATION": "Zwei gleichrangige Formangaben als sowohl … als auch statt als Präpositionsstapel sprechen.",
    "R22_CONTROL_REPEAT": "Unmittelbar wiederholte OL- und OT-Kontrollen als erneute Fortsetzung beziehungsweise weiteren Arbeitsgang sprechen.",
    "R23_T_STAGE_GRADE": "T mit Anwendungsstufe und Zielgrad als bis auf Grad sprechen.",
    "R24_T_COOLING_ORDER": "Beim Abkühlen den Arbeitsort vor den Zielgrad stellen.",
}


MODIFIER_SPECS = (
    ("MODE_APPLICATION", 10, "in Anwendungsform"),
    ("MODE_FINE", 11, "in Feinform"),
    ("MODE_ALTERNATE", 11, "in der Alternativform"),
    ("MODE_INNER", 11, "in der Innenform"),
    ("MODE_B_VARIANT", 11, "in der b-Variante"),
    ("MODE_G_VARIANT", 11, "in der g-Variante"),
    ("MODE_SECOND_PASS", 9, "im zweiten Durchgang"),
    ("MODE_STATION_KIND", 13, "in der bezeichneten Stationsart"),
    ("APPLICATION_STAGE", 14, "auf der Anwendungsstufe"),
    ("SOURCE_FRAME", 15, SOURCE_FRAME),
    ("SOURCE_CONDITION", 15, SOURCE_CONDITION),
    ("SOURCE", 5, SOURCE_CASED),
    ("GRADE_I_AT", 20, "bei Grad I"),
    ("GRADE_II_AT", 20, "bei Grad II"),
    ("GRADE_III_AT", 20, "bei Grad III"),
    ("GRADE_I_TO", 20, "auf Grad I"),
    ("GRADE_II_TO", 20, "auf Grad II"),
    ("GRADE_III_TO", 20, "auf Grad III"),
    ("GRADE_I_II", 20, "unter Beachtung der Gradangaben I und II"),
    ("GRADE_II_III", 20, "unter Beachtung der Gradangaben II und III"),
    ("GRADE_I_FRAME_TARGET", 20, "mit Einstellung auf Grad I"),
    ("GRADE_II_FRAME_TARGET", 20, "mit Einstellung auf Grad II"),
    ("GRADE_III_FRAME_TARGET", 20, "mit Einstellung auf Grad III"),
    ("GRADE_I_FRAME_NEUTRAL", 20, "mit der Gradangabe I"),
    ("GRADE_II_FRAME_NEUTRAL", 20, "mit der Gradangabe II"),
    ("GRADE_III_FRAME_NEUTRAL", 20, "mit der Gradangabe III"),
    ("FILL", 21, "bei der angegebenen Füllung"),
    ("WORK_MAIN", 30, "an der Hauptstelle"),
    ("WORK_MIDDLE", 31, "an der Mittelstelle"),
    ("WORK_SIDE", 32, "an der Nebenstelle"),
    ("WORK_ACTIVE", 33, "an der Arbeitsstelle"),
    ("WORK_END", 34, "an der Endstelle"),
    ("BATH", 35, "im Bad"),
    ("PATH_CONTACT", 50, CONTACT_SHORT),
    ("PATH_STATION", 51, "entlang des Stationswegs oder des Kanals"),
    ("PATH_READING", 52, "entlang der Lesebahn"),
    ("TARGET_PURPOSE", 60, TARGET_PURPOSE),
    ("TARGET_STATIC", 60, TARGET_STATIC),
    ("TARGET_DIRECTION", 60, TARGET_DIRECTION),
    ("TARGET_FLOW_DIRECTION", 60, TARGET_FLOW_DIRECTION),
    ("TARGET_RECIPIENT", 16, TARGET_RECIPIENT),
    ("FRAME_AS_NEW", 70, "als neuen Bad- oder Stationsansatz"),
    ("FRAME_NEW_LABEL", 70, "unter der Rahmenangabe „neuer Bad- oder Stationsansatz“"),
)

PARTICLES = (
    " im vorangehenden Arbeitsschritt", " abkühlen", " heraus", " heran", " aufrecht", " vor",
    " zu", " ein", " an", " aus", " um", " ab",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_inputs() -> dict[str, list[dict[str, str]]]:
    data = {name: read_tsv(path) for name, path in INPUTS.items()}
    expected = {
        "hosts": 2272,
        "actions": 1443,
        "statements": 313,
        "replay": 793,
        "q_transitions": 24,
        "manual_decisions": 11,
        "manual_polish": 3,
        "review_queue": 125,
        "defaults": 6,
        "aiin_bindings": 46,
        "propagation": 3,
        "local_cards": 40,
        "manual_reviews": 40,
    }
    for name, count in expected.items():
        if len(data[name]) != count:
            raise RuntimeError(f"GDT599 {name} population drift: {len(data[name])} != {count}")
    if {row["physical_page"] for row in data["hosts"]} != set(PAGES):
        raise RuntimeError("GDT599 fixed-page population drift")
    if any(row["physical_page"].startswith("f84") for row in data["hosts"]):
        raise RuntimeError("forbidden page in GDT599 input")
    return data


def sentence_case(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip(" ;.")
    return cleaned[:1].upper() + cleaned[1:] if cleaned else ""


def compose_paragraphs(rows: list[dict[str, str]], field: str) -> tuple[str, int]:
    paragraphs: list[list[str]] = [[]]
    for row in rows:
        clause = sentence_case(row[field])
        if clause:
            paragraphs[-1].append(clause + ".")
        if row["paragraph_boundary"] == "PARAGRAPH_AFTER" and paragraphs[-1]:
            paragraphs.append([])
    nonempty = [paragraph for paragraph in paragraphs if paragraph]
    return "\n\n".join(" ".join(paragraph) for paragraph in nonempty), len(nonempty)


def split_particle(clause: str) -> tuple[str, str]:
    for particle in PARTICLES:
        if clause.endswith(particle):
            return clause[: -len(particle)].rstrip(), particle
    return clause.rstrip(), ""


def remove_terminal_particle(clause: str, expected: str) -> str:
    suffix = " " + expected
    if clause.endswith(suffix):
        return clause[: -len(suffix)].rstrip()
    raise RuntimeError(f"expected terminal particle {expected!r}: {clause}")


def replace_terminal_particle(clause: str, old: str, new: str) -> str:
    return remove_terminal_particle(clause, old) + " " + new


def collapse_multiple_grades(clause: str) -> tuple[str, bool]:
    replacements = {
        "bei Grad I, bei Grad II": "unter Beachtung der Gradangaben I und II",
        "bei Grad I und bei Grad II": "unter Beachtung der Gradangaben I und II",
        "bei Grad II, bei Grad III": "unter Beachtung der Gradangaben II und III",
        "bei Grad II und bei Grad III": "unter Beachtung der Gradangaben II und III",
    }
    for old, new in replacements.items():
        if old in clause:
            return clause.replace(old, new), True
    return clause, False


def modifier_matches(text: str) -> list[tuple[int, int, str, int, str]]:
    candidates: list[tuple[int, int, str, int, str]] = []
    for modifier_id, order, phrase in sorted(MODIFIER_SPECS, key=lambda item: -len(item[2])):
        start = 0
        while True:
            index = text.find(phrase, start)
            if index < 0:
                break
            end = index + len(phrase)
            if (
                (index and phrase[:1].isalnum() and text[index - 1].isalnum())
                or (end < len(text) and phrase[-1:].isalnum() and text[end].isalnum())
            ):
                start = index + 1
                continue
            candidates.append((index, end, modifier_id, order, phrase))
            start = end
    chosen: list[tuple[int, int, str, int, str]] = []
    occupied: list[tuple[int, int]] = []
    for candidate in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
        if any(not (candidate[1] <= left or candidate[0] >= right) for left, right in occupied):
            continue
        chosen.append(candidate)
        occupied.append((candidate[0], candidate[1]))
    return sorted(chosen)


def reorder_modifiers(clause: str) -> tuple[str, bool, str, str]:
    """Reorder only a fully recognized contiguous modifier tail."""
    base_with_tail, particle = split_particle(clause)
    matches = modifier_matches(base_with_tail)
    if len(matches) < 2:
        return clause, False, "NONE", "NONE"
    start = min(match[0] for match in matches)
    tail = base_with_tail[start:]
    relative_spans = [(left - start, right - start) for left, right, *_rest in matches]
    pieces: list[str] = []
    cursor = 0
    for left, right in relative_spans:
        pieces.append(tail[cursor:left])
        cursor = right
    pieces.append(tail[cursor:])
    leftover = "".join(pieces)
    leftover = re.sub(r"(?:\s|,|;|\bund\b)+", "", leftover)
    if leftover:
        return clause, False, "NONE", "NONE"
    before_ids = [match[2] for match in matches]
    ordered = sorted(enumerate(matches), key=lambda item: (item[1][3], item[0]))
    ordered_matches = [match for _index, match in ordered]
    phrases = [match[4] for match in ordered_matches]
    # These are not peer noun phrases.  Prepositional modifiers form a typed
    # tail; flat comma/und coordination was the defect being removed.
    joined = " ".join(phrases)
    base = base_with_tail[:start].rstrip(" ,")
    rebuilt = f"{base} {joined}{particle}"
    after_ids = [match[2] for match in ordered_matches]
    changed = rebuilt != clause
    return rebuilt, changed, "|".join(before_ids), "|".join(after_ids)


def apply_ch_valency(clause: str, object_class: str, object_lemma: str) -> tuple[str, bool]:
    marker = "Entnimm oder lass "
    if not clause.startswith(marker):
        return clause, False
    remainder = clause[len(marker):]
    if object_class == "STATION":
        if (
            CONTACT_RAW in clause
            or CONTACT_SHORT in clause
            or "entlang des Stationswegs" in clause
        ):
            return "Lass " + remainder, True
        return remove_terminal_particle("Entnimm " + remainder, "ab"), True
    if object_lemma == "Probe":
        return remove_terminal_particle("Entnimm " + remainder, "ab"), True
    if object_class in {"BODY", "BODY_PART", "UNIT"}:
        return replace_terminal_particle("Nimm " + remainder, "ab", "heraus"), True
    if object_class == "PORTION":
        return remove_terminal_particle("Entnimm " + remainder, "ab"), True
    if object_class in {"FLOW", "MEASURE"}:
        return "Lass " + remainder, True
    return clause, False


def apply_relation_grammar(
    clause: str, root: str, object_class: str, rules: list[str]
) -> str:
    condition_target_visible = TARGET_RAW in clause or TARGET_PURPOSE in clause
    condition_source_visible = SOURCE_RAW in clause or SOURCE_CONDITION in clause
    if root == "T" and object_class == "CONDITION" and condition_source_visible:
        clause = clause.replace(SOURCE_RAW, SOURCE_CONDITION)
        if clause.startswith("Reguliere "):
            clause = "Stelle " + clause[len("Reguliere "):]
        if not clause.endswith(" ein"):
            clause += " ein"
        rules.append("R04_CONDITION_SOURCE")
    elif root == "T" and object_class == "CONDITION" and condition_target_visible:
        clause = clause.replace(TARGET_RAW, TARGET_PURPOSE)
        rules.append("R05_CONDITION_TARGET")

    if SOURCE_RAW in clause:
        clause = clause.replace(SOURCE_RAW, SOURCE_FRAME if root == "FRAME" else SOURCE_CASED)
        rules.append("R06_SOURCE_CASE")
    if TARGET_RAW in clause:
        if root == "CH":
            flowing = (
                object_class in {"FLOW", "MEASURE"}
                or (
                    object_class == "STATION"
                    and (
                        CONTACT_RAW in clause
                        or CONTACT_SHORT in clause
                        or "entlang des Stationswegs" in clause
                    )
                )
            )
            replacement = TARGET_FLOW_DIRECTION if flowing else TARGET_PURPOSE
        elif root == "K" and object_class == "BODY":
            replacement = TARGET_DIRECTION
        elif root == "K":
            replacement = TARGET_RECIPIENT
        elif root in {"OK", "CHD", "R", "P", "T"}:
            replacement = TARGET_PURPOSE
        elif root in {"SH", "FRAME"}:
            replacement = TARGET_STATIC
        else:
            replacement = TARGET_DIRECTION
        clause = clause.replace(TARGET_RAW, replacement)
        if root == "K" and object_class == "BODY" and clause.endswith(" ein"):
            clause = remove_terminal_particle(clause, "ein")
        rules.append("R07_TARGET_VALENCY")
    return clause


def q_result_clause(object_class: str, root: str) -> str:
    if root == "OK" and object_class == "STATION":
        return "der vorbereitete Stationsansatz gilt nun als neuer Bad- oder Stationsansatz"
    if root == "CH" and object_class == "FLOW":
        return "der Ablauf gilt nun als neuer Bad- oder Stationsansatz"
    if root == "S" and object_class == "UNIT":
        return "die ausgewählte Einheit gilt nun als neuer Bad- oder Stationsansatz"
    if root == "K" and object_class == "MEASURE":
        return "das Ergebnis der Zuführung gilt nun als neuer Bad- oder Stationsansatz"
    return "das Ergebnis gilt nun als neuer Bad- oder Stationsansatz"


def q_event_id(key: str) -> str:
    match = re.search(r"G407-E\d+", key)
    return match.group(0) if match else ""


def resolve_q_source(
    source_pointer: str,
    q_by_key: dict[str, dict[str, str]],
    q_by_event: dict[str, str],
) -> str:
    if source_pointer in q_by_key:
        return source_pointer
    if source_pointer.startswith(("CARRY:", "HANDOFF:")):
        return q_by_event.get(q_event_id(source_pointer), "NONE")
    return "NONE"


def explicit_process_grade(row: dict[str, str]) -> bool:
    """True only when the visible grade has an explicit non-T governor."""
    root = row["action_root"]
    if root in ACTION_ROOTS:
        return root != "T"
    if root != "FRAME":
        return False
    key = row["primary_governor_key"]
    if not key.startswith("ACTION_CHAIN:"):
        return False
    tail = key.rsplit(":", 1)[-1]
    roots = set(tail.split("+"))
    return bool(roots) and "T" not in roots


def frame_has_t_governor(row: dict[str, str]) -> bool:
    if row["action_root"] != "FRAME" or not row["primary_governor_key"].startswith("ACTION_CHAIN:"):
        return False
    return "T" in set(row["primary_governor_key"].rsplit(":", 1)[-1].split("+"))


def target_relation(clause: str) -> str:
    for phrase, relation in (
        (TARGET_FLOW_DIRECTION, "FLOW_DIRECTION"),
        (TARGET_RECIPIENT, "RECIPIENT"),
        (TARGET_PURPOSE, "PURPOSE"),
        (TARGET_STATIC, "STATIC_LOCATION"),
        (TARGET_DIRECTION, "DIRECTION"),
        (TARGET_RAW, "RAW_UNRESOLVED"),
    ):
        if phrase in clause:
            return relation
    return "NONE"


def source_relation(clause: str) -> str:
    if SOURCE_CONDITION in clause:
        return "CONDITION_SOURCE"
    if SOURCE_FRAME in clause:
        return "FRAME_ORIGIN"
    if SOURCE_CASED in clause:
        return "ORIGIN"
    if SOURCE_RAW in clause:
        return "RAW_UNRESOLVED"
    return "NONE"


def grade_relation(row: dict[str, str], clause: str) -> str:
    if "Grad" not in clause:
        return "NONE"
    if row["action_root"] == "T" or frame_has_t_governor(row):
        return "TARGET_GRADE"
    if explicit_process_grade(row):
        return "PROCESS_CONDITION"
    if row["action_root"] == "FRAME":
        return "NEUTRAL_FRAME_GRADE"
    return "PRESERVED_OTHER_GRADE"


def flow_generalization_eligible(row: dict[str, str]) -> bool:
    """Recover W03–W09 from visible path plus the pre-override baseline.

    This predicate deliberately does not inspect the manual override ID.  It
    excludes an already inherited FLOW (E3568) and the local BODY_PART sample
    while recovering BODY baselines and CH-rootdefault STATION baselines.
    """
    return (
        row["action_root"] == "CH"
        and row["written_carrier_count"] == "0"
        and CONTACT_RAW in row["gdt584_upstream_clause_de"]
        and (
            row["baseline_object_class"] == "BODY"
            or (
                row["baseline_selection_route"] == "ROOT_DEFAULT"
                and row["baseline_object_class"] == "STATION"
            )
        )
    )


def add_again(clause: str) -> str:
    main, separator, result = clause.partition("; ")
    core, particle = split_particle(main)
    marked = f"{core} erneut{particle}"
    return marked + (separator + result if separator else "")


def render_surface(
    row: dict[str, str],
    q_by_key: dict[str, dict[str, str]],
    q_by_event: dict[str, str],
    replay_by_key: dict[str, dict[str, str]],
) -> dict[str, Any]:
    key = row["primary_govern_key"] if "primary_govern_key" in row else row["primary_governor_key"]
    root = row["action_root"]
    object_class = row["object_class"]
    original = row["gdt599_complete_clause_de"]
    clause = original
    rules: list[str] = []

    replay = replay_by_key.get(key)
    if replay is not None and flow_generalization_eligible(replay):
        rules.append("R01_CH_LINE_FLOW_GENERALIZATION")

    resolved_q_source = resolve_q_source(row.get("source_pointer", ""), q_by_key, q_by_event)
    if resolved_q_source != "NONE" and key != resolved_q_source:
        if "denselben Stationsansatz" not in clause:
            raise RuntimeError(f"Q-result followup NP drift at {key}: {clause}")
        clause = clause.replace("denselben Stationsansatz", "diesen neuen Stationsansatz", 1)
        rules.append("R15_Q_FOLLOWUP_NEW")

    if row.get("object_lemma_de") == "Probe":
        if row.get("reference_mode") == "DEFINITE" and "die Probe" in clause:
            clause = clause.replace("die Probe", "eine Probe", 1)
            rules.append("R17_PROBE_REFERENCE")
        elif row.get("reference_mode") == "ANAPHORIC" and "dieselbe Probe" in clause:
            clause = clause.replace("dieselbe Probe", "diese Probe", 1)
            rules.append("R17_PROBE_REFERENCE")
    if row.get("object_lemma_de") == "Körperteil" and "dasselbe Körperteil" in clause:
        clause = clause.replace("dasselbe Körperteil", "denselben Körperteil", 1)
        rules.append("R18_BODY_PART_GENDER")

    main, separator, _old_result = clause.partition("; ")
    if root == "FRAME" and main.startswith("Verwende für den vorangehenden Arbeitsschritt"):
        rest = main[len("Verwende für den vorangehenden Arbeitsschritt"):].strip()
        object_markers = (
            "den Stationsansatz", "die Anwendungsportion",
            "die Becken- oder Körpereinheit", "das Stations- oder Badmaß",
        )
        if any(marker in rest for marker in object_markers):
            rest = rest.replace("als neuer Bad- oder Stationsansatz", "als neuen Bad- oder Stationsansatz")
            rest = rest.replace(f" und {SOURCE_RAW}", f" {SOURCE_RAW}")
            object_prefixes = (
                "den Stationsansatz und die Becken- oder Körpereinheit",
                "den Stationsansatz und das Stations- oder Badmaß",
                "die Anwendungsportion", "die Becken- oder Körpereinheit",
                "den Stationsansatz", "das Stations- oder Badmaß",
            )
            object_prefix = next((prefix for prefix in object_prefixes if rest.startswith(prefix)), "")
            if not object_prefix:
                raise RuntimeError(f"unparsed FRAME participant phrase at {key}: {rest}")
            modifiers = rest[len(object_prefix):].lstrip(" ,")
            main = f"Verwende {object_prefix} im vorangehenden Arbeitsschritt"
            if modifiers:
                main += f" {modifiers}"
        else:
            rest = rest.replace(
                "als neuer Bad- oder Stationsansatz",
                "unter der Rahmenangabe „neuer Bad- oder Stationsansatz“",
            )
            main = "Führe den vorangehenden Arbeitsschritt" + (f" {rest}" if rest else "") + " aus"
        rules.append("R13_FRAME_COMPLETE")

    if root == "CH":
        main, changed = apply_ch_valency(main, object_class, row["object_lemma_de"])
        if changed:
            rules.append("R02_CH_OBJECT_VALENCY")
    if root == "OK" and main.startswith("Beschicke oder bereite "):
        main = "Bereite " + main[len("Beschicke oder bereite "):]
        rules.append("R03_OK_PREPARE")

    main = apply_relation_grammar(main, root, object_class, rules)

    if (
        root == "K"
        and SOURCE_CASED in main
        and not any(target in main for target in (
            TARGET_DIRECTION, TARGET_FLOW_DIRECTION, TARGET_RECIPIENT,
            TARGET_PURPOSE, TARGET_STATIC,
        ))
        and (main.endswith(" zu") or main.endswith(" ein"))
    ):
        terminal = "zu" if main.endswith(" zu") else "ein"
        main = replace_terminal_particle(main, terminal, "heran")
        rules.append("R19_K_SOURCE_VALENCY")

    if CONTACT_RAW in main:
        main = main.replace(CONTACT_RAW, CONTACT_SHORT)
        rules.append("R08_CONTACT_SHORT")
    worksite_replacements = {
        "an der Stations-Hauptstelle": "an der Hauptstelle",
        "an der Stations-Mittelstelle": "an der Mittelstelle",
        "an der Stations-Nebenstelle": "an der Nebenstelle",
        "an der Stations-Arbeitsstelle": "an der Arbeitsstelle",
        "an der Stations-Endstelle": "an der Endstelle",
        "entlang des Stationswegs oder Kanals": "entlang des Stationswegs oder des Kanals",
    }
    if any(old in main for old in worksite_replacements):
        for old, new in worksite_replacements.items():
            main = main.replace(old, new)
        rules.append("R09_WORKSITE_SHORT")

    if explicit_process_grade(row) and re.search(r"auf Grad (?:III|II|I)(?!I)", main):
        main = re.sub(r"auf Grad (III|II|I)(?!I)", r"bei Grad \1", main)
        rules.append("R10_PROCESS_GRADE")
    if root == "FRAME" and re.search(r"auf Grad (?:III|II|I)(?!I)", main):
        if frame_has_t_governor(row):
            main = re.sub(r"auf Grad (III|II|I)(?!I)", r"mit Einstellung auf Grad \1", main)
        else:
            main = re.sub(r"auf Grad (III|II|I)(?!I)", r"mit der Gradangabe \1", main)
        rules.append("R20_FRAME_GRADE_SCOPE")
    main, multi_grade = collapse_multiple_grades(main)
    if multi_grade:
        rules.append("R11_MULTI_GRADE")

    main, reordered, modifier_before, modifier_after = reorder_modifiers(main)
    if reordered:
        rules.append("R12_MODIFIER_ORDER")

    main = re.sub(
        r"bei Grad (III|II|I) bei der angegebenen Füllung",
        r"bei angegebener Füllung sowie bei Grad \1",
        main,
    )
    worksite_coordination = {
        "an der Hauptstelle an der Nebenstelle an der Arbeitsstelle":
            "an der Haupt-, Neben- und Arbeitsstelle",
        "an der Hauptstelle an der Arbeitsstelle":
            "an der Haupt- und Arbeitsstelle",
        "an der Nebenstelle an der Arbeitsstelle":
            "an der Neben- und Arbeitsstelle",
    }
    for old, new in worksite_coordination.items():
        main = main.replace(old, new)

    peer_mode_replacements = {
        "in Anwendungsform in Feinform": "sowohl in Anwendungsform als auch in Feinform",
        "in Anwendungsform in der Innenform": "sowohl in Anwendungsform als auch in der Innenform",
    }
    peer_mode_changed = False
    for old, new in peer_mode_replacements.items():
        if old in main:
            main = main.replace(old, new)
            peer_mode_changed = True
    if peer_mode_changed:
        rules.append("R21_PEER_MODE_COORDINATION")

    if root == "T" and "auf der Anwendungsstufe auf Grad" in main:
        main = main.replace("auf der Anwendungsstufe auf Grad", "auf der Anwendungsstufe bis auf Grad")
        rules.append("R23_T_STAGE_GRADE")

    cooling = re.search(
        r"anschließend auf Grad (III|II|I) an der Arbeitsstelle abkühlen$", main
    )
    if root == "T" and cooling:
        main = re.sub(
            r"anschließend auf Grad (III|II|I) an der Arbeitsstelle abkühlen$",
            r"anschließend an der Arbeitsstelle auf Grad \1 abkühlen",
            main,
        )
        rules.append("R24_T_COOLING_ORDER")

    if root == "K" and main.startswith("Führe ") and TARGET_RECIPIENT in main:
        payload = main[len("Führe "):]
        before_target, target_separator, after_target = payload.partition(" " + TARGET_RECIPIENT)
        if not target_separator:
            raise RuntimeError(f"K recipient placement drift at {key}: {main}")
        main = f"Führe {TARGET_RECIPIENT} {before_target}{after_target}"

    if root == "CH" and row.get("object_lemma_de") == "Probe":
        probe = re.match(r"^Entnimm ((?:eine|die|diese) Probe am selben Körperteil) (.+)$", main)
        if probe:
            main = f"Entnimm {probe.group(2)} {probe.group(1)}"

    q_surface = "NONE"
    if key in q_by_key:
        q_surface = q_result_clause(object_class, root)
        clause = f"{main}; {q_surface}"
        rules.append("R14_Q_RESULT_STATE")
    else:
        if separator:
            raise RuntimeError(f"unexpected non-Q semicolon at {key}: {original}")
        clause = main

    return {
        "clause": re.sub(r"\s+", " ", clause).strip(),
        "rules": list(dict.fromkeys(rules)),
        "modifier_reordered": "YES" if reordered else "NO",
        "modifier_order_before": modifier_before,
        "modifier_order_after": modifier_after,
        "q_surface": q_surface,
        "q_source_key": resolved_q_source,
    }


def quality_profile(rows: Iterable[dict[str, str]], field: str) -> dict[str, int]:
    values = [row[field] for row in rows]
    return {
        "frame_fragment": sum("Verwende für den vorangehenden Arbeitsschritt" in value for value in values),
        "ch_double_verb": sum("Entnimm oder lass" in value for value in values),
        "ok_double_verb": sum("Beschicke oder bereite" in value for value in values),
        "q_takeover": sum("; übernimm" in value for value in values),
        "raw_source_case": sum(SOURCE_RAW in value for value in values),
        "raw_target_case": sum(TARGET_RAW in value for value in values),
        "verbose_contact": sum(CONTACT_RAW in value for value in values),
        "non_t_on_grade": sum(
            bool(re.search(r"auf Grad (?:III|II|I)(?!I)", row[field]))
            for row in rows
            if explicit_process_grade(row)
        ),
        "old_q_followup": sum(
            "denselben Stationsansatz" in value and row.get("gdt600_q_followup") == "YES"
            for row, value in zip(rows, values)
        ),
        "wrong_body_part_gender": sum("dasselbe Körperteil" in value for value in values),
        "definite_first_probe": sum("Entnimm die Probe" in value for value in values),
    }


def build(inputs: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    source_hosts = sorted(inputs["hosts"], key=lambda row: int(row["host_ordinal_global"]))
    source_actions = sorted(inputs["actions"], key=lambda row: int(row["complete_action_ordinal"]))
    source_statements = sorted(inputs["statements"], key=lambda row: int(row["statement_ordinal"]))
    replay_by_key = {row["primary_governor_key"]: row for row in inputs["replay"]}
    q_by_key = {row["primary_governor_key"]: row for row in inputs["q_transitions"]}
    q_by_event = {q_event_id(key): key for key in q_by_key}
    action_source_by_key = {row["primary_governor_key"]: row for row in source_actions}
    defaults_by_root = {row["action_root"]: row for row in inputs["defaults"]}

    if (
        len(q_by_key) != 24 or len(q_by_event) != 24
        or len(replay_by_key) != 793 or len(action_source_by_key) != 1443
    ):
        raise RuntimeError("nonunique GDT599 action identity")

    # OWNER/FRAME descriptive governor keys can repeat; host ordinal is the
    # lossless identity of the 2,272-row stream.
    rendered_by_ordinal: dict[str, dict[str, Any]] = {}
    for row in source_hosts:
        if row["action_root"] in ACTION_ROOTS or row["action_root"] == "FRAME":
            rendered_by_ordinal[row["host_ordinal_global"]] = render_surface(
                row, q_by_key, q_by_event, replay_by_key
            )

    host_rows: list[dict[str, str]] = []
    repeat_rows: list[dict[str, str]] = []
    control_repeat_rows: list[dict[str, str]] = []
    previous_action_source: dict[str, str] | None = None
    previous_host_source: dict[str, str] | None = None
    current_statement = ""
    repeat_barrier = False
    intervening_host_count = 0
    for source in source_hosts:
        if source["statement_id"] != current_statement:
            current_statement = source["statement_id"]
            previous_action_source = None
            previous_host_source = None
            repeat_barrier = False
            intervening_host_count = 0
        row = dict(source)
        rendered = rendered_by_ordinal.get(source["host_ordinal_global"])
        if rendered is None:
            clause = source["gdt599_complete_clause_de"]
            rules: list[str] = []
            modifier_reordered = "NO"
            modifier_before = "NONE"
            modifier_after = "NONE"
            q_surface = "NONE"
        else:
            clause = rendered["clause"]
            rules = list(rendered["rules"])
            modifier_reordered = rendered["modifier_reordered"]
            modifier_before = rendered["modifier_order_before"]
            modifier_after = rendered["modifier_order_after"]
            q_surface = rendered["q_surface"]
            q_source_key = rendered["q_source_key"]
        if rendered is None:
            q_source_key = "NONE"

        control_repeat = (
            previous_host_source is not None
            and source["action_root"] == "CONTROL"
            and previous_host_source["action_root"] == "CONTROL"
            and source["gdt599_complete_clause_de"] == previous_host_source["gdt599_complete_clause_de"]
        )
        if control_repeat:
            before_control_repeat = clause
            if clause == "Fahre im selben Arbeitsgang fort":
                clause = "Fahre erneut im selben Arbeitsgang fort"
                control_kind = "OL_REPEAT_SAME_WORKSTEP"
            elif clause == "Beginne danach den nächsten Arbeitsgang":
                clause = "Beginne danach einen weiteren Arbeitsgang"
                control_kind = "OT_REPEAT_NEXT_WORKSTEP"
            else:
                raise RuntimeError(
                    f"unhandled repeated CONTROL clause at {source['primary_governor_key']}: {clause}"
                )
            rules.append("R22_CONTROL_REPEAT")
            control_repeat_rows.append({
                "control_repeat_ordinal": str(len(control_repeat_rows) + 1),
                "primary_governor_key": source["primary_governor_key"],
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "previous_governor_key": previous_host_source["primary_governor_key"],
                "control_repeat_kind": control_kind,
                "gdt599_repeated_clause_de": source["gdt599_complete_clause_de"],
                "gdt600_pre_repeat_clause_de": before_control_repeat,
                "gdt600_repeat_clause_de": clause,
            })

        strict_repeat = (
            previous_action_source is not None
            and not repeat_barrier
            and source["action_root"] in ACTION_ROOTS
            and source["gdt599_complete_clause_de"] == previous_action_source["gdt599_complete_clause_de"]
        )
        if strict_repeat:
            before_repeat = clause
            clause = add_again(clause)
            rules.append("R16_REPEAT_AGAIN")
            repeat_rows.append({
                "repeat_ordinal": str(len(repeat_rows) + 1),
                "primary_governor_key": source["primary_governor_key"],
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "action_root": source["action_root"],
                "previous_governor_key": previous_action_source["primary_governor_key"],
                "repeat_scope": "NEXT_ACTION_SAME_WORKSTEP__CONTROL_OR_FRAME_HOSTS_IGNORED",
                "intervening_host_count": str(intervening_host_count),
                "gdt599_repeated_clause_de": source["gdt599_complete_clause_de"],
                "gdt600_pre_repeat_clause_de": before_repeat,
                "gdt600_repeat_clause_de": clause,
            })
        if source["action_root"] in ACTION_ROOTS:
            previous_action_source = source
            repeat_barrier = False
            intervening_host_count = 0
        elif previous_action_source is not None:
            intervening_host_count += 1
            if source["action_root"] == "CONTROL" and source["gdt599_complete_clause_de"].startswith("Beginne danach"):
                repeat_barrier = True

        resolved_q_source = resolve_q_source(source.get("source_pointer", ""), q_by_key, q_by_event)
        q_followup = (
            "YES"
            if resolved_q_source != "NONE"
            and source["primary_governor_key"] != resolved_q_source
            else "NO"
        )
        if q_followup == "YES":
            surface_reference_mode = "DEMONSTRATIVE_NEW_Q_RESULT"
        elif source.get("object_lemma_de") == "Probe" and source.get("reference_mode") == "DEFINITE":
            surface_reference_mode = "INDEFINITE_INTRODUCTION"
        elif source.get("object_lemma_de") == "Probe" and source.get("reference_mode") == "ANAPHORIC":
            surface_reference_mode = "DEMONSTRATIVE_ANAPHORIC"
        else:
            surface_reference_mode = f"INHERITED_{source.get('reference_mode', 'NOT_APPLICABLE')}"
        row.update({
            "gdt600_surface_clause_de": clause,
            "gdt600_surface_changed": "YES" if clause != source["gdt599_complete_clause_de"] else "NO",
            "gdt600_rule_ids": "|".join(dict.fromkeys(rules)) if rules else "NONE",
            "gdt600_modifier_reordered": modifier_reordered,
            "gdt600_modifier_order_before": modifier_before,
            "gdt600_modifier_order_after": modifier_after,
            "gdt600_q_result_clause_de": q_surface,
            "gdt600_q_followup": q_followup,
            "gdt600_q_result_source_key": resolved_q_source,
            "gdt600_surface_reference_mode": surface_reference_mode,
            "gdt600_source_relation": source_relation(clause),
            "gdt600_target_relation": target_relation(clause),
            "gdt600_grade_relation": grade_relation(source, clause),
            "gdt600_guard": GUARD,
        })
        host_rows.append(row)
        previous_host_source = source

    host_by_ordinal = {row["host_ordinal_global"]: row for row in host_rows}
    action_rows: list[dict[str, str]] = []
    for source in source_actions:
        host = host_by_ordinal[source["host_ordinal_global"]]
        row = dict(source)
        for field in (
            "gdt600_surface_clause_de", "gdt600_surface_changed", "gdt600_rule_ids",
            "gdt600_modifier_reordered", "gdt600_modifier_order_before",
            "gdt600_modifier_order_after", "gdt600_q_result_clause_de",
            "gdt600_q_followup", "gdt600_q_result_source_key", "gdt600_guard",
            "gdt600_surface_reference_mode", "gdt600_source_relation",
            "gdt600_target_relation", "gdt600_grade_relation",
        ):
            row[field] = host[field]
        action_rows.append(row)

    action_by_key = {row["primary_governor_key"]: row for row in action_rows}
    changes = []
    for row in host_rows:
        if row["gdt600_surface_changed"] == "YES":
            changes.append({
                "change_ordinal": str(len(changes) + 1),
                "host_ordinal_global": row["host_ordinal_global"],
                "primary_governor_key": row["primary_governor_key"],
                "statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "action_root": row["action_root"],
                "object_class": row["object_class"],
                "object_lemma_de": row["object_lemma_de"],
                "rule_ids": row["gdt600_rule_ids"],
                "gdt599_clause_de": row["gdt599_complete_clause_de"],
                "gdt600_clause_de": row["gdt600_surface_clause_de"],
            })

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in host_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows: list[dict[str, str]] = []
    for source in source_statements:
        rows = sorted(by_statement[source["statement_id"]], key=lambda row: int(row["host_ordinal_in_statement"]))
        reader, paragraph_count = compose_paragraphs(rows, "gdt600_surface_clause_de")
        row = dict(source)
        row.update({
            "gdt600_surface_reader_de": reader,
            "gdt600_changed_host_count": str(sum(item["gdt600_surface_changed"] == "YES" for item in rows)),
            "gdt600_changed_action_count": str(sum(
                item["gdt600_surface_changed"] == "YES" and item["action_root"] in ACTION_ROOTS
                for item in rows
            )),
            "gdt600_paragraph_count": str(paragraph_count),
            "gdt600_paragraph_count_preserved": "YES" if paragraph_count == int(source["paragraph_count"]) else "NO",
        })
        statement_rows.append(row)

    flow_generalizations = []
    manual_remaining = []
    for source in inputs["manual_decisions"]:
        if source["review_id"] in {f"W{index:02d}" for index in range(3, 10)}:
            replay = replay_by_key[source["primary_governor_key"]]
            flow_generalizations.append({
                "generalization_ordinal": str(len(flow_generalizations) + 1),
                "review_id": source["review_id"],
                "primary_governor_key": source["primary_governor_key"],
                "statement_id": source["statement_id"],
                "physical_page": source["physical_page"],
                "baseline_selection_route": source["baseline_selection_route"],
                "baseline_object_class": source["baseline_object_class"],
                "written_carrier_count": replay["written_carrier_count"],
                "contact_or_line_visible": "YES" if CONTACT_RAW in replay["gdt584_upstream_clause_de"] else "NO",
                "generalized_rule_id": "R01_CH_LINE_FLOW_GENERALIZATION",
                "final_object_class": source["final_object_class"],
                "final_object_lemma_de": source["final_object_lemma_de"],
                "gdt600_status": "SUBSUMED_BY_ONE_RULE__OBJECT_UNCHANGED",
            })
        else:
            row = dict(source)
            row["gdt600_status"] = "RETAINED_MANUAL_OBJECT_DECISION"
            manual_remaining.append(row)

    condition_relations = []
    for row in action_rows:
        if row["action_root"] != "T" or row["object_class"] != "CONDITION":
            continue
        relation = (
            "SOURCE" if SOURCE_RAW in row["gdt599_complete_clause_de"] or SOURCE_CONDITION in row["gdt599_complete_clause_de"]
            else "TARGET" if TARGET_RAW in row["gdt599_complete_clause_de"] or TARGET_PURPOSE in row["gdt599_complete_clause_de"]
            else "NONE"
        )
        if relation == "NONE":
            continue
        condition_relations.append({
            "relation_ordinal": str(len(condition_relations) + 1),
            "primary_governor_key": row["primary_governor_key"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "relation_class": relation,
            "renderer_rule_id": "R04_CONDITION_SOURCE" if relation == "SOURCE" else "R05_CONDITION_TARGET",
            "gdt599_clause_de": row["gdt599_complete_clause_de"],
            "gdt600_clause_de": row["gdt600_surface_clause_de"],
            "already_polished_in_gdt599": "YES" if row["primary_governor_key"] in {
                item["primary_governor_key"] for item in inputs["manual_polish"]
            } else "NO",
        })

    bounded_right = []
    for target in inputs["replay"]:
        if target["selection_route"] != "RIGHT_SAME_EVENT_COMPLETED_OR_ROOT_DEFAULT":
            continue
        preview = action_source_by_key[target["source_pointer"]]
        if preview["completion_layer"] != "GDT599_REMAINING_OBJECT_COMPLETION":
            route = "T06A_RIGHT_RETAINED_COMPLETED"
            causal_source = target["source_pointer"]
            retained_layer = preview["completion_layer"]
        else:
            route = "T06B_RIGHT_ROOT_DEFAULT_PREVIEW"
            default = defaults_by_root[preview["action_root"]]
            causal_source = f"DEFAULT:{preview['action_root']}:{default['default_object_class']}"
            retained_layer = "ROOT_DEFAULT_PREVIEW_SEED"
        bounded_right.append({
            "provenance_ordinal": str(len(bounded_right) + 1),
            "primary_governor_key": target["primary_governor_key"],
            "statement_id": target["statement_id"],
            "physical_page": target["physical_page"],
            "action_root": target["action_root"],
            "gdt599_selection_route": target["selection_route"],
            "gdt600_provenance_route": route,
            "causal_source_pointer": causal_source,
            "preview_host_pointer": target["source_pointer"],
            "preview_completion_layer": retained_layer,
            "object_class": target["object_class"],
            "object_lemma_de": target["object_lemma_de"],
            "object_changed": "NO",
        })

    q_grammar = []
    for transition in inputs["q_transitions"]:
        action = action_by_key[transition["primary_governor_key"]]
        q_grammar.append({
            "q_ordinal": transition["transition_ordinal"],
            "primary_governor_key": transition["primary_governor_key"],
            "statement_id": transition["statement_id"],
            "physical_page": transition["physical_page"],
            "action_root": transition["action_root"],
            "input_object_class": transition["input_object_class"],
            "input_object_lemma_de": transition["input_object_lemma_de"],
            "gdt599_clause_de": action["gdt599_complete_clause_de"],
            "gdt600_input_clause_de": action["gdt600_surface_clause_de"].split("; ", 1)[0],
            "gdt600_result_clause_de": action["gdt600_q_result_clause_de"],
            "result_object_class": transition["result_object_class"],
            "result_object_lemma_de": transition["result_object_lemma_de"],
            "commit_order": transition["commit_order"],
        })

    q_followups = []
    for action in action_rows:
        if action["gdt600_q_followup"] == "YES":
            q_followups.append({
                "followup_ordinal": str(len(q_followups) + 1),
                "primary_governor_key": action["primary_governor_key"],
                "statement_id": action["statement_id"],
                "physical_page": action["physical_page"],
                "q_source_pointer": action["source_pointer"],
                "resolved_q_source_key": action["gdt600_q_result_source_key"],
                "gdt599_clause_de": action["gdt599_complete_clause_de"],
                "gdt600_clause_de": action["gdt600_surface_clause_de"],
                "required_reference_np_de": "diesen neuen Stationsansatz",
            })

    review_rows = []
    for source in inputs["review_queue"]:
        action = action_by_key[source["primary_governor_key"]]
        row = dict(source)
        row.update({
            "gdt600_surface_changed": action["gdt600_surface_changed"],
            "gdt600_rule_ids": action["gdt600_rule_ids"],
            "gdt600_surface_clause_de": action["gdt600_surface_clause_de"],
            "semantic_review_status": "RETAINED__SURFACE_PASS_DOES_NOT_DISMISS_OBJECT_OR_SOURCE_REVIEW",
        })
        review_rows.append(row)

    aiin_passthrough = []
    for source in inputs["aiin_bindings"]:
        row = dict(source)
        row["gdt600_status"] = "PRESERVED__SURFACE_GRAMMAR_DOES_NOT_CHANGE_QUANTITY_BINDING"
        aiin_passthrough.append(row)
    propagation_passthrough = []
    for source in inputs["propagation"]:
        row = dict(source)
        row["gdt600_status"] = "PRESERVED__OBJECT_HISTORY_UNCHANGED"
        propagation_passthrough.append(row)
    local_passthrough = []
    for source in inputs["local_cards"]:
        row = dict(source)
        row["gdt600_status"] = "PRESERVED_SEPARATE__NEVER_INHERIT_INTO_RUNNING_STATEMENT"
        local_passthrough.append(row)
    manual_review_passthrough = []
    for source in inputs["manual_reviews"]:
        row = dict(source)
        row["gdt600_status"] = "PRESERVED__SURFACE_PASS_DOES_NOT_DISMISS_REVIEW"
        manual_review_passthrough.append(row)

    page_rows = []
    for page in PAGES:
        page_hosts = [row for row in host_rows if row["physical_page"] == page]
        page_actions = [row for row in action_rows if row["physical_page"] == page]
        page_statements = [row for row in statement_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "statement_count": str(len(page_statements)),
            "host_count": str(len(page_hosts)),
            "action_count": str(len(page_actions)),
            "changed_host_count": str(sum(row["gdt600_surface_changed"] == "YES" for row in page_hosts)),
            "changed_action_count": str(sum(row["gdt600_surface_changed"] == "YES" for row in page_actions)),
            "frame_completion_count": str(sum("R13_FRAME_COMPLETE" in row["gdt600_rule_ids"] for row in page_hosts)),
            "modifier_reorder_count": str(sum(row["gdt600_modifier_reordered"] == "YES" for row in page_hosts)),
            "q_result_count": str(sum("R14_Q_RESULT_STATE" in row["gdt600_rule_ids"] for row in page_actions)),
            "repeat_marker_count": str(sum("R16_REPEAT_AGAIN" in row["gdt600_rule_ids"] for row in page_actions)),
            "control_repeat_marker_count": str(sum("R22_CONTROL_REPEAT" in row["gdt600_rule_ids"] for row in page_hosts)),
        })

    rule_occurrences = Counter()
    rule_changed_occurrences = Counter()
    for row in host_rows:
        if row["gdt600_rule_ids"] == "NONE":
            continue
        for rule in row["gdt600_rule_ids"].split("|"):
            rule_occurrences[rule] += 1
            if row["gdt600_surface_changed"] == "YES":
                rule_changed_occurrences[rule] += 1
    rule_rows = []
    for index, (rule_id, description) in enumerate(RULE_SPECS.items(), start=1):
        rule_rows.append({
            "rule_order": str(index),
            "rule_id": rule_id,
            "description_de": description,
            "occurrence_count": str(rule_occurrences[rule_id]),
            "changed_clause_count": str(rule_changed_occurrences[rule_id]),
        })

    before_quality = quality_profile(source_hosts, "gdt599_complete_clause_de")
    after_quality = quality_profile(host_rows, "gdt600_surface_clause_de")
    # The source edition predates the GDT600 marker column, so its Q-followup
    # population has to be recovered from the unchanged source pointers.
    before_quality["old_q_followup"] = sum(
        resolve_q_source(row.get("source_pointer", ""), q_by_key, q_by_event) != "NONE"
        and row["primary_governor_key"] != resolve_q_source(
            row.get("source_pointer", ""), q_by_key, q_by_event
        )
        and "denselben Stationsansatz" in row["gdt599_complete_clause_de"]
        for row in source_hosts
    )
    after_quality["old_q_followup"] = sum(
        row["gdt600_q_followup"] == "YES"
        and "denselben Stationsansatz" in row["gdt600_surface_clause_de"]
        for row in host_rows
    )
    changed_action_count = sum(row["gdt600_surface_changed"] == "YES" for row in action_rows)
    changed_host_count = sum(row["gdt600_surface_changed"] == "YES" for row in host_rows)
    changed_statement_count = sum(int(row["gdt600_changed_host_count"]) > 0 for row in statement_rows)
    result = {
        "experiment_id": "GDT600",
        "status": "PASS_COMPLETE_SURFACE_GRAMMAR__1443_ACTIONS__2272_HOSTS__313_STATEMENTS__7_FLOW_DECISIONS_GENERALIZED__6_CONDITION_RELATIONS__21_BOUNDED_RIGHT_SPLIT__24_Q_RESULTS__7_Q_FOLLOWUPS__18_ACTION_REPEATS__34_CONTROL_REPEATS__0_OBJECT_OR_STATE_FIELD_CHANGES__SURFACE_RELATIONS_EXPLICIT",
        "guard": GUARD,
        "fixed_pages": list(PAGES),
        "host_count": len(host_rows),
        "action_count": len(action_rows),
        "statement_count": len(statement_rows),
        "changed_host_count": changed_host_count,
        "changed_action_count": changed_action_count,
        "changed_statement_count": changed_statement_count,
        "unchanged_object_count": len(action_rows),
        "unchanged_source_pointer_count": len(action_rows),
        "unchanged_q_transition_count": len(q_grammar),
        "flow_manual_decisions_generalized_count": len(flow_generalizations),
        "remaining_manual_object_decision_count": len(manual_remaining),
        "condition_relation_rule_occurrence_count": len(condition_relations),
        "bounded_right_retained_completed_count": sum(row["gdt600_provenance_route"] == "T06A_RIGHT_RETAINED_COMPLETED" for row in bounded_right),
        "bounded_right_root_default_preview_count": sum(row["gdt600_provenance_route"] == "T06B_RIGHT_ROOT_DEFAULT_PREVIEW" for row in bounded_right),
        "q_result_grammar_count": len(q_grammar),
        "q_result_followup_count": len(q_followups),
        "repeat_marker_count": len(repeat_rows),
        "control_repeat_marker_count": len(control_repeat_rows),
        "modifier_reorder_count": sum(row["gdt600_modifier_reordered"] == "YES" for row in host_rows),
        "review_passthrough_count": len(review_rows),
        "aiin_passthrough_count": len(aiin_passthrough),
        "propagation_passthrough_count": len(propagation_passthrough),
        "local_card_passthrough_count": len(local_passthrough),
        "manual_review_passthrough_count": len(manual_review_passthrough),
        "surface_reference_profile": dict(sorted(Counter(row["gdt600_surface_reference_mode"] for row in host_rows).items())),
        "source_relation_profile": dict(sorted(Counter(row["gdt600_source_relation"] for row in host_rows).items())),
        "target_relation_profile": dict(sorted(Counter(row["gdt600_target_relation"] for row in host_rows).items())),
        "grade_relation_profile": dict(sorted(Counter(row["gdt600_grade_relation"] for row in host_rows).items())),
        "rule_occurrence_profile": dict(sorted(rule_occurrences.items())),
        "quality_before": before_quality,
        "quality_after": after_quality,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }
    reader = render_reader(statement_rows, page_rows, result)
    return {
        "hosts": host_rows,
        "actions": action_rows,
        "statements": statement_rows,
        "rules": rule_rows,
        "changes": changes,
        "flow_generalizations": flow_generalizations,
        "manual_remaining": manual_remaining,
        "condition_relations": condition_relations,
        "bounded_right": bounded_right,
        "q_grammar": q_grammar,
        "q_followups": q_followups,
        "repeats": repeat_rows,
        "control_repeats": control_repeat_rows,
        "reviews": review_rows,
        "aiin_passthrough": aiin_passthrough,
        "propagation_passthrough": propagation_passthrough,
        "local_passthrough": local_passthrough,
        "manual_review_passthrough": manual_review_passthrough,
        "pages": page_rows,
        "reader": reader,
        "result": result,
    }


def render_reader(
    statements: list[dict[str, str]], pages: list[dict[str, str]], result: dict[str, Any]
) -> str:
    lines = [
        "# GDT600 – vollständiger Leser mit Objektgrammatik",
        "",
        f"Status: `{result['status']}`",
        "",
        "Alle GDT599-Objekte, Quellenpointer und Zustandswechsel bleiben erhalten. Verb-, Referenz-, Quellen-, Ziel- und Gradrelationen sind explizite neue Arbeitslesungen; jede Regel bleibt im maschinenlesbaren Sidecar sichtbar.",
        "",
    ]
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statements:
        by_page[row["physical_page"]].append(row)
    page_by_id = {row["physical_page"]: row for row in pages}
    for page in PAGES:
        profile = page_by_id[page]
        lines.extend((
            f"## {page}",
            "",
            f"{profile['statement_count']} Aussagen; {profile['changed_host_count']} von {profile['host_count']} Hostklauseln oberflächlich verbessert.",
            "",
        ))
        for row in by_page[page]:
            lines.extend((f"### {row['statement_id']}", "", row["gdt600_surface_reader_de"], ""))
    return "\n".join(lines).rstrip() + "\n"


def tsv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise RuntimeError("cannot serialize empty TSV")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def write_built(built: dict[str, Any]) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for name in (
        "actions", "hosts", "statements", "rules", "changes", "flow_generalizations",
        "manual_remaining", "condition_relations", "bounded_right", "q_grammar",
        "q_followups", "repeats", "control_repeats", "reviews", "pages",
        "aiin_passthrough", "propagation_passthrough", "local_passthrough",
        "manual_review_passthrough",
    ):
        OUTPUTS[name].write_bytes(tsv_bytes(built[name]))
    OUTPUTS["reader"].write_text(built["reader"], encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
