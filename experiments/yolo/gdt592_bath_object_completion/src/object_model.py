#!/usr/bin/env python3
"""Build the complete GDT592 bath-object working edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt592_bath_object_completion"
ART = EXP / "artifacts"
STATUS = (
    "PASS_254_BATH_ACTION_OBJECTS__149_OBJECTLESS_PLUS_5_FILL_ONLY_PATCHED__"
    "53_BODY__81_STATION__107_BATH_OBJECT__9_UNIT__4_PORTION__"
    "13_LOCAL_HANDOFFS__11_EPISODE_CARRIES__132_STATEMENTS__"
    "2_GDT569_DIVERGENCES_RETAINED"
)

BATH_PAGES = frozenset({"f75r", "f77r", "f81r", "f81v", "f82r", "f83r"})
ADMITTED_PAGES = frozenset(
    {
        "f1r", "f4r", "f10r", "f11r", "f13r", "f17r", "f18r", "f20v",
        "f24v", "f31r", "f55v", "f56r", "f66r", "f67r2", "f68r1",
        "f69v", "f70v", "f71v", "f72r", "f75r", "f76r", "f77r",
        "f81r", "f81v", "f82r", "f83r", "f88r", "f88v", "f89r", "f95v",
    }
)

BODY_BLOCKERS = frozenset(
    {
        "AL", "AR", "AIR", "L", "A_ADDR", "D_ADDR", "S_ADDR", "M_LOCAL",
        "O", "IIN", "DA", "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I",
        "CARRIER_Q",
    }
)
OBJECT_FORMS = {
    "BODY": ("Körper", "den Körper"),
    "STATION": ("Stationsansatz", "den Stationsansatz"),
    "BATH_OBJECT": ("Badegut", "das zu badende Gut"),
    "BATH_UNIT": ("Badeinheit", "die Badeinheit"),
    "PORTION": ("Anwendungsportion", "die Anwendungsportion"),
}
ANAPHORIC_OBJECT_FORMS = {
    "BODY": "denselben Körper",
    "STATION": "denselben Stationsansatz",
    "BATH_OBJECT": "dasselbe zu badende Gut",
    "BATH_UNIT": "dieselbe Badeinheit",
    "PORTION": "dieselbe Anwendungsportion",
}

# Occurrence-level refinements found by a complete manual scan of the original
# 24 bath-only carry targets.  Each named non-bath host lies after the old bath
# donor and before the target inside the same reader/physical segment.  The
# exact donor host/key is recovered and checked from the fixed GDT584/GDT590
# tables; these cards are not generalized to unseen occurrences.
LOCAL_HANDOFFS = {
    "G407-E1673": ("G407-E1670", "Y", "STATION"),
    "G407-E1746": ("G407-E1743", "AIN", "PORTION"),
    "G407-E2641": ("G407-E2640", "Y", "STATION"),
    "G407-E2736": ("G407-E2734", "Y", "STATION"),
    "G407-E3034": ("G407-E3033", "Y", "STATION"),
    "G407-E3067": ("G407-E3065", "OR", "BATH_UNIT"),
    "G407-E3221": ("G407-E3219", "Y", "STATION"),
    "G407-E3234": ("G407-E3233", "Y", "STATION"),
    "G407-E3304": ("G407-E3299", "Y", "STATION"),
    "G407-E3550": ("G407-E3549", "OR", "BATH_UNIT"),
    "G407-E3621": ("G407-E3619", "Y", "STATION"),
    "G407-E3625": ("G407-E3623", "AIN", "PORTION"),
    "G407-E3665": ("G407-E3664", "Y", "STATION"),
}
LOCAL_HANDOFF_EXPECTED_KEYS = {
    "G407-E1673": "ACTION:G407-E1670@4:T",
    "G407-E1746": "ACTION:G407-E1743@1:OK",
    "G407-E2641": "ACTION:G407-E2640@2:K",
    "G407-E2736": "ACTION:G407-E2734@1:CHD",
    "G407-E3034": "ACTION:G407-E3033@1:CHD",
    "G407-E3067": "ACTION:G407-E3065@2:T",
    "G407-E3221": "ACTION:G407-E3219@4:K",
    "G407-E3234": "ACTION:G407-E3233@3:K",
    "G407-E3304": "ACTION:G407-E3299@1:S",
    "G407-E3550": "ACTION:G407-E3549@1:S",
    "G407-E3621": "ACTION:G407-E3619@1:S",
    "G407-E3625": "ACTION:G407-E3623@1:S",
    "G407-E3665": "ACTION:G407-E3664@4:T",
}
LOCAL_HANDOFF_VISIBLE_SPANS = {
    "G407-E1673": "f75r.28_W6_TO_W9",
    "G407-E1746": "f75r.35_W3_TO_W6",
    "G407-E2641": "f77r.39_W5_TO_W6",
    "G407-E2736": "f81r.3_W6_TO_W8",
    "G407-E3034": "f81v.12_W3_TO_W4",
    "G407-E3067": "f81v.16_W1_TO_W2__CARRIER_E3066",
    "G407-E3221": "f82r.6_W5_TO_W7",
    "G407-E3234": "f82r.8_W1_TO_W2",
    "G407-E3304": "f82r.16_W10_TO_f82r.17_W1__CARRIER_E3301",
    "G407-E3550": "f83r.11_W1_TO_W2",
    "G407-E3621": "f83r.18_W9_TO_f83r.19_W2",
    "G407-E3625": "f83r.19_W4_TO_W6",
    "G407-E3665": "f83r.23_W6_TO_W7",
}
LOCAL_HANDOFF_FORM_OVERRIDES = {
    "G407-E3067": ("Stationseinheit", "dieselbe Stationseinheit"),
    "G407-E3550": ("Stationseinheit", "dieselbe Stationseinheit"),
}

INPUTS = {
    "gdt583_assignments": ROOT / "experiments/yolo/gdt583_object_conditioned_verb_refinement/artifacts/gdt583_target_occurrence_assignments.tsv",
    "gdt584_phrases": ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts/gdt584_statement_wide_host_phrases.tsv",
    "gdt587_phrases": ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/artifacts/gdt587_candidate_statement_host_phrases.tsv",
    "gdt581_slots": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_15889_complete_slot_ledger.tsv",
    "gdt590_slots": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_1243_adjudicated_slot_replay.tsv",
    "gdt590_statements": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_793_body_adjudicated_statement_reader.tsv",
    "gdt590_adjudications": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_4_bath_fork_adjudications.tsv",
    "gdt591_hosts": ROOT / "experiments/yolo/gdt591_bath_episode_continuity/artifacts/gdt591_92_bath_y_host_continuity.tsv",
    "gdt569_states": ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames/artifacts/gdt569_1656_context_voice_state_clauses.tsv",
    "events": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_5122_running_event_edition.tsv",
    "lines": ROOT / "transcription/voynich_zl3b_lines.tsv",
}

OUTPUTS = {
    "actions": ART / "gdt592_254_bath_action_objects.tsv",
    "episodes": ART / "gdt592_190_bath_episode_segments.tsv",
    "objectless": ART / "gdt592_149_objectless_completions.tsv",
    "fill_only": ART / "gdt592_5_fill_only_compositions.tsv",
    "carries": ART / "gdt592_11_episode_carries.tsv",
    "handoffs": ART / "gdt592_13_local_object_handoffs.tsv",
    "gdt569_divergences": ART / "gdt592_2_gdt569_object_divergences.tsv",
    "blockers": ART / "gdt592_25_blocker_station_defaults.tsv",
    "pages": ART / "gdt592_6_bath_page_profiles.tsv",
    "patched_statements": ART / "gdt592_132_patched_statements.tsv",
    "statements": ART / "gdt592_793_bath_object_statement_reader.tsv",
    "reader": ART / "GDT592_COMPLETE_BATH_OBJECT_READER.md",
    "result": ART / "gdt592_result.json",
    "validation": ART / "gdt592_validation.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def guarded_rows(path: Path, *, selector: str, allowed: Iterable[str]) -> list[dict[str, str]]:
    return list(
        GuardedTSV(
            path,
            selector_column=selector,
            allowed_values=set(allowed),
            forbidden_prefixes=("f84",),
            forbidden_action="skip",
        )
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_sealed_reader(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    pages = {row["physical_page"] for row in rows}
    if any(page.lower().startswith("f84") for page in pages):
        raise RuntimeError("sealed reader contains f84/f84r")
    if not pages <= ADMITTED_PAGES:
        raise RuntimeError(f"unexpected reader pages: {sorted(pages - ADMITTED_PAGES)}")
    return rows


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty TSV: {path}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def split_pipe(value: str) -> list[str]:
    return [part for part in value.split("|") if part and part != "NONE"]


def pipe(values: Iterable[str]) -> str:
    materialized = [value for value in values if value and value != "NONE"]
    return "|".join(materialized) if materialized else "NONE"


def event_number(event_id: str) -> int:
    match = re.search(r"-E(\d+)", event_id)
    if not match:
        raise RuntimeError(f"not a running event ID: {event_id}")
    return int(match.group(1))


def locus_line_number(locus: str) -> int:
    try:
        return int(locus.rsplit(".", 1)[1])
    except (IndexError, ValueError) as exc:
        raise RuntimeError(f"locus lacks numeric line: {locus}") from exc


def gdt569_relation(
    state: dict[str, str] | None, object_class: str, route: str
) -> tuple[str, str]:
    if state is None:
        return "NO_GDT569_STATE_ROW", "Keine ältere GDT569-State-Zeile für dieses Event."
    if state["argument_carry"] != "YES":
        return (
            "GDT569_LOCAL_EXPLICIT_PARALLEL",
            "Lokales GDT569-Argument bleibt als parallele Ereignisspur sichtbar.",
        )
    root = state["inherited_argument_root"]
    if root == "AIIN":
        return (
            "GDT569_CARRY_FILL_PARALLEL",
            "AIIN bleibt Füllung/Wertspur und wird nicht mit dem Badegut gleichgesetzt.",
        )
    if route == "COLD_BATH_OBJECT_DEFAULT":
        return (
            "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT",
            "Die ältere Wurzel ist ein konkreter Kandidat für das noch neutrale Badegut und wird für den nächsten Pass behalten.",
        )
    if (root == "OR" and object_class == "BATH_UNIT") or (
        root == "AIN" and object_class == "PORTION"
    ) or (root == "Y" and object_class == "STATION"):
        return (
            "GDT569_CARRY_CLASS_ALIGNED",
            "Die ältere Argumentwurzel und die neue Objektklasse sind kompatibel; Identität wird nicht behauptet.",
        )
    if route.startswith("WRITTEN_"):
        return (
            "GDT569_CURRENT_WRITTEN_OBJECT_PRECEDENCE",
            "Das aktuell geschriebene Objekt hat Vorrang; die ältere getragene Argumentspur bleibt daneben sichtbar.",
        )
    if root in {"OR", "AIN"}:
        return (
            "GDT569_CARRY_CLASS_DIVERGENCE_RETAINED",
            "Episode und ältere Argumentspur wählen verschiedene Klassen; beide bleiben sichtbar.",
        )
    if root == "Y":
        raise RuntimeError(
            f"unresolved non-generic Y relation: route={route} object={object_class}"
        )
    raise RuntimeError(f"unexpected GDT569 inherited argument root: {root}")


def sentence_case(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip(" ;.")
    if not text:
        return text
    return text[0].upper() + text[1:]


def _paragraph_map(lines: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in lines:
        if row["kind"] == "P":
            by_page[row["page"]].append(row)
    result: dict[str, dict[str, str]] = {}
    for page, rows in by_page.items():
        rows.sort(key=lambda row: int(row["line_number"]))
        paragraph = 0
        paragraph_start = 0
        staged: list[dict[str, str]] = []
        for row in rows:
            if row["paragraph_start"] == "1" or paragraph == 0:
                paragraph += 1
                paragraph_start = int(row["line_number"])
                staged = []
            staged.append(row)
            if row["paragraph_end"] == "1":
                end = int(row["line_number"])
                for member in staged:
                    result[member["locus"]] = {
                        "paragraph_key": f"{page}:P{paragraph}",
                        "paragraph_locus_range": f"{page}.{paragraph_start}–.{end}",
                    }
                staged = []
        if staged:
            end = int(staged[-1]["line_number"])
            for member in staged:
                result[member["locus"]] = {
                    "paragraph_key": f"{page}:P{paragraph}",
                    "paragraph_locus_range": f"{page}.{paragraph_start}–.{end}",
                }
    return result


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "gdt583_assignments": guarded_rows(INPUTS["gdt583_assignments"], selector="physical_page", allowed=BATH_PAGES),
        "gdt584_phrases": guarded_rows(INPUTS["gdt584_phrases"], selector="physical_page", allowed=BATH_PAGES),
        "gdt587_phrases": guarded_rows(INPUTS["gdt587_phrases"], selector="physical_page", allowed=BATH_PAGES),
        "gdt581_slots": guarded_rows(INPUTS["gdt581_slots"], selector="physical_page", allowed=BATH_PAGES),
        "gdt590_slots": guarded_rows(INPUTS["gdt590_slots"], selector="physical_page", allowed=BATH_PAGES),
        "gdt590_statements": read_sealed_reader(INPUTS["gdt590_statements"]),
        "gdt590_adjudications": guarded_rows(INPUTS["gdt590_adjudications"], selector="physical_page", allowed={"f77r", "f82r"}),
        "gdt591_hosts": guarded_rows(INPUTS["gdt591_hosts"], selector="physical_page", allowed=BATH_PAGES),
        "gdt569_states": guarded_rows(INPUTS["gdt569_states"], selector="physical_page", allowed=BATH_PAGES),
        "events": guarded_rows(INPUTS["events"], selector="physical_page", allowed=BATH_PAGES),
        "lines": guarded_rows(INPUTS["lines"], selector="page", allowed=BATH_PAGES),
    }


def _current_clause(
    phrase: dict[str, str],
    phrase587_by_identity: dict[tuple[str, str, str], dict[str, str]],
    adjudication_by_key: dict[str, dict[str, str]],
) -> str:
    identity = (
        phrase["statement_id"],
        phrase["host_ordinal_in_statement"],
        phrase["primary_governor_key"],
    )
    row587 = phrase587_by_identity.get(identity)
    clause = row587["gdt587_reader_clause_de"] if row587 else phrase["gdt584_reader_clause_de"]
    adjudication = adjudication_by_key.get(phrase["primary_governor_key"])
    if adjudication:
        old = adjudication["gdt589_station_clause_de"].removesuffix(".")
        new = adjudication["gdt590_body_clause_de"].removesuffix(".")
        if clause.count(old) != 1:
            raise RuntimeError(f"GDT590 current-clause patch not unique at {phrase['primary_governor_key']}")
        clause = clause.replace(old, new, 1)
    return clause


def _completed_clause(
    phrase: dict[str, str], current_clause: str, carrier_roots: list[str], object_form: str
) -> str:
    root_set = set(carrier_roots)
    if not root_set:
        prefix = "Halte im Bad"
        if current_clause.count(prefix) != 1:
            raise RuntimeError(
                f"objectless bath clause lacks exact prefix at {phrase['primary_governor_key']}: {current_clause}"
            )
        return current_clause.replace(prefix, f"Halte {object_form} im Bad", 1)
    if root_set == {"AIIN"}:
        prefix = "Halte die Badfüllung"
        if current_clause.count(prefix) != 1:
            raise RuntimeError(
                f"fill-only bath clause lacks exact prefix at {phrase['primary_governor_key']}: {current_clause}"
            )
        return current_clause.replace(
            prefix,
            f"Halte {object_form} im Bad bei der angegebenen Füllung",
            1,
        )
    raise RuntimeError(f"completed clause requested for explicit object host {phrase['primary_governor_key']}")


def _locate_phrase_spans(
    statement_text: str,
    phrases: list[dict[str, str]],
    current_clause_by_identity: dict[tuple[str, str, str], str],
) -> list[tuple[int, int, dict[str, str]]]:
    spans: list[tuple[int, int, dict[str, str]]] = []
    cursor = 0
    for phrase in phrases:
        identity = (
            phrase["statement_id"],
            phrase["host_ordinal_in_statement"],
            phrase["primary_governor_key"],
        )
        sentence = sentence_case(current_clause_by_identity[identity]) + "."
        start = statement_text.find(sentence, cursor)
        if start < 0:
            raise RuntimeError(
                f"cannot align host phrase {identity} after offset {cursor}: {sentence}"
            )
        end = start + len(sentence)
        spans.append((start, end, phrase))
        cursor = end
    return spans


def build(data: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    event_by_id: dict[str, dict[str, str]] = {}
    for row in data["events"]:
        event_by_id[row["global_running_event_id"]] = row
        event_by_id[row["source_event_id"]] = row
    paragraph_by_locus = _paragraph_map(data["lines"])
    statement_by_id = {row["statement_id"]: row for row in data["gdt590_statements"]}
    adjudication_by_key = {
        row["primary_governor_key"]: row for row in data["gdt590_adjudications"]
    }
    role_by_bath_key = {
        row["primary_governor_key"]: row for row in data["gdt591_hosts"]
    }
    gdt569_by_event: dict[str, dict[str, str]] = {}
    for row in data["gdt569_states"]:
        event_id = row["event_id"]
        if event_id in gdt569_by_event:
            raise RuntimeError(f"GDT569 state event is not unique: {event_id}")
        gdt569_by_event[event_id] = row

    phrase587_candidates: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt587_phrases"]:
        identity = (
            row["statement_id"],
            row["host_ordinal_in_statement"],
            row["primary_governor_key"],
        )
        phrase587_candidates[identity].append(row)
    phrase587_by_identity: dict[tuple[str, str, str], dict[str, str]] = {}
    for identity, candidates in phrase587_candidates.items():
        if len(candidates) != 1:
            raise RuntimeError(f"GDT587 phrase identity not unique: {identity} {len(candidates)}")
        phrase587_by_identity[identity] = candidates[0]

    phrases_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt584_phrases"]:
        phrases_by_statement[row["statement_id"]].append(row)
    for rows in phrases_by_statement.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))

    bath_phrases = [
        row for row in data["gdt584_phrases"]
        if row["gdt584_rule_id"] == "SH_BIO_BATHE"
    ]
    bath_phrases.sort(
        key=lambda row: (
            int(statement_by_id[row["statement_id"]]["reader_statement_ordinal"]),
            int(row["host_ordinal_in_statement"]),
        )
    )
    if len(bath_phrases) != 254:
        raise RuntimeError(f"expected 254 SH_BIO_BATHE phrases, found {len(bath_phrases)}")
    bath_keys = {row["primary_governor_key"] for row in bath_phrases}
    if len(bath_keys) != 254:
        raise RuntimeError("bath governor keys are not unique")
    bath583 = [
        row for row in data["gdt583_assignments"]
        if row["gdt583_rule_id"] == "SH_BIO_BATHE"
    ]
    if len(bath583) != 254 or {row["primary_governor_key"] for row in bath583} != bath_keys:
        raise RuntimeError("GDT583/GDT584 254-bath population mismatch")

    slots581_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt581_slots"]:
        slots581_by_host[row["primary_governor_key"]].append(row)
    for rows in slots581_by_host.values():
        rows.sort(key=lambda row: int(row["complete_slot_ordinal"]))
    carrier_slots_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt590_slots"]:
        carrier_slots_by_host[row["primary_governor_key"]].append(row)
    for rows in carrier_slots_by_host.values():
        rows.sort(key=lambda row: int(row["written_carrier_ordinal"]))

    current_clause_by_identity: dict[tuple[str, str, str], str] = {}
    for phrase in data["gdt584_phrases"]:
        identity = (
            phrase["statement_id"],
            phrase["host_ordinal_in_statement"],
            phrase["primary_governor_key"],
        )
        current_clause_by_identity[identity] = _current_clause(
            phrase, phrase587_by_identity, adjudication_by_key
        )

    bath_phrase_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for phrase in bath_phrases:
        bath_phrase_by_event[phrase["anchor_event_id"]].append(phrase)
    local_handoff_by_target: dict[str, dict[str, str]] = {}
    for target_event, (donor_event, donor_root, object_class) in LOCAL_HANDOFFS.items():
        target_candidates = bath_phrase_by_event[target_event]
        if len(target_candidates) != 1:
            raise RuntimeError(
                f"local handoff target does not identify one bath action: {target_event}"
            )
        target = target_candidates[0]
        donor_candidates = []
        for candidate in phrases_by_statement[target["statement_id"]]:
            roots = {
                row["slot_value"]
                for row in slots581_by_host[candidate["primary_governor_key"]]
            }
            if (
                candidate["anchor_event_id"] == donor_event
                and donor_root in roots
                and candidate["primary_governor_key"] not in bath_keys
                and int(candidate["host_ordinal_in_statement"])
                < int(target["host_ordinal_in_statement"])
            ):
                donor_candidates.append(candidate)
        if len(donor_candidates) != 1:
            raise RuntimeError(
                f"local handoff donor is not unique: {target_event} <- {donor_event}/{donor_root}: "
                f"{len(donor_candidates)}"
            )
        donor = donor_candidates[0]
        if donor["primary_governor_key"] != LOCAL_HANDOFF_EXPECTED_KEYS[target_event]:
            raise RuntimeError(
                f"local handoff donor key drift at {target_event}: "
                f"{donor['primary_governor_key']}"
            )
        donor_root_slots = [
            row
            for row in slots581_by_host[donor["primary_governor_key"]]
            if row["slot_value"] == donor_root
        ]
        if not donor_root_slots:
            raise RuntimeError(f"local handoff donor root slot missing: {target_event}")
        donor_root_source_events = sorted(
            {row["source_event_or_card_id"] for row in donor_root_slots}
        )
        if len(donor_root_source_events) != 1:
            raise RuntimeError(
                f"local handoff donor root source is not unique: {target_event}"
            )
        gdt587_assigned_root_slots = [
            row
            for row in carrier_slots_by_host[donor["primary_governor_key"]]
            if row["carrier_root"] == donor_root
        ]
        between = [
            phrase
            for phrase in phrases_by_statement[target["statement_id"]]
            if int(donor["host_ordinal_in_statement"])
            <= int(phrase["host_ordinal_in_statement"])
            < int(target["host_ordinal_in_statement"])
        ]
        donor_anchor = event_by_id[donor_event]
        target_anchor = event_by_id[target_event]
        if any(phrase["paragraph_boundary"] == "PARAGRAPH_AFTER" for phrase in between):
            raise RuntimeError(f"local handoff crosses reader boundary: {target_event}")
        if (
            paragraph_by_locus[donor_anchor["locus"]]["paragraph_key"]
            != paragraph_by_locus[target_anchor["locus"]]["paragraph_key"]
        ):
            raise RuntimeError(f"local handoff crosses physical paragraph: {target_event}")
        identity = (
            donor["statement_id"],
            donor["host_ordinal_in_statement"],
            donor["primary_governor_key"],
        )
        local_handoff_by_target[target_event] = {
            "object_class": object_class,
            "donor_root": donor_root,
            "donor_event_id": donor_event,
            "donor_primary_governor_key": donor["primary_governor_key"],
            "donor_action_slot_id": donor["action_slot_id"],
            "donor_carrier_slot_ids": pipe(
                row["slot_id"] for row in donor_root_slots
            ),
            "donor_carrier_source_event_id": donor_root_source_events[0],
            "donor_host_ordinal_in_statement": donor["host_ordinal_in_statement"],
            "donor_locus": donor_anchor["locus"],
            "donor_surface": donor_anchor["surface"],
            "donor_component_recipe": donor_anchor["component_recipe"],
            "donor_clause_de": current_clause_by_identity[identity],
            "donor_phrase_provenance": (
                "GDT587_ASSIGNMENT"
                if gdt587_assigned_root_slots
                else "GDT587_COMPLETE_READER__GDT584_CLAUSE_UNCHANGED"
            ),
            "visible_span": LOCAL_HANDOFF_VISIBLE_SPANS[target_event],
        }

    action_rows: list[dict[str, str]] = []
    action_by_key: dict[str, dict[str, str]] = {}
    segment_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    statement_ids = sorted(
        {row["statement_id"] for row in bath_phrases},
        key=lambda statement_id: int(statement_by_id[statement_id]["reader_statement_ordinal"]),
    )
    for statement_id in statement_ids:
        all_phrases = phrases_by_statement[statement_id]
        current_object: dict[str, str] | None = None
        previous_paragraph = "NONE"
        pending_reader_reset = False
        segment_ordinal = 1
        for phrase_index, phrase in enumerate(all_phrases):
            anchor = event_by_id[phrase["anchor_event_id"]]
            paragraph = paragraph_by_locus[anchor["locus"]]
            reset_reasons: list[str] = []
            if phrase_index == 0:
                reset_reasons.append("STATEMENT_START")
            else:
                if pending_reader_reset:
                    reset_reasons.append("GDT584_PARAGRAPH_AFTER")
                if paragraph["paragraph_key"] != previous_paragraph:
                    reset_reasons.append("PHYSICAL_PARAGRAPH_CHANGE")
                if reset_reasons:
                    current_object = None
                    segment_ordinal += 1
            segment_key = f"{statement_id}:BSEG{segment_ordinal:02d}"
            key = phrase["primary_governor_key"]
            if key in bath_keys:
                carriers = carrier_slots_by_host[key]
                carrier_roots = [row["carrier_root"] for row in carriers]
                root_set = set(carrier_roots)
                host_values = [row["slot_value"] for row in slots581_by_host[key]]
                blockers = sorted(set(host_values) & BODY_BLOCKERS)
                state_before = current_object
                target_event = phrase["anchor_event_id"]
                handoff = local_handoff_by_target.get(target_event)
                carry_source = "NONE"
                carry_source_slot = "NONE"
                carry_source_key = "NONE"
                carry_source_locus = "NONE"
                carry_gap = "NOT_APPLICABLE"
                carry_distance = "NOT_APPLICABLE"
                carry_event_gap = "NOT_APPLICABLE"
                carry_line_distance = "NOT_APPLICABLE"
                carry_reference_class = "NOT_APPLICABLE"
                handoff_anchor_source = "NONE"
                handoff_carrier_source = "NONE"
                handoff_source_slot = "NONE"
                handoff_source_carrier_slots = "NONE"
                handoff_source_key = "NONE"
                handoff_source_root = "NONE"
                handoff_source_locus = "NONE"
                handoff_host_distance = "NOT_APPLICABLE"
                handoff_anchor_event_gap = "NOT_APPLICABLE"
                handoff_event_gap = "NOT_APPLICABLE"
                handoff_line_distance = "NOT_APPLICABLE"
                handoff_visible_span = "NOT_APPLICABLE"
                retained_episode_alternative = "NOT_APPLICABLE"
                if "Y" in root_set:
                    role_row = role_by_bath_key.get(key)
                    if not role_row:
                        raise RuntimeError(f"Y bath host absent from GDT591: {key}")
                    object_class = role_row["gdt590_role"]
                    route = "WRITTEN_Y_GDT590"
                elif "OR" in root_set:
                    object_class = "BATH_UNIT"
                    route = "WRITTEN_OR_UNIT"
                elif "AIN" in root_set:
                    object_class = "PORTION"
                    route = "WRITTEN_AIN_PORTION"
                elif blockers:
                    object_class = "STATION"
                    route = "BODY_BLOCKER_STATION"
                elif handoff is not None:
                    object_class = handoff["object_class"]
                    route = "INTERVENING_OBJECT_HANDOFF"
                    handoff_anchor_source = handoff["donor_event_id"]
                    handoff_carrier_source = handoff["donor_carrier_source_event_id"]
                    handoff_source_slot = handoff["donor_action_slot_id"]
                    handoff_source_carrier_slots = handoff["donor_carrier_slot_ids"]
                    handoff_source_key = handoff["donor_primary_governor_key"]
                    handoff_source_root = handoff["donor_root"]
                    handoff_source_locus = handoff["donor_locus"]
                    handoff_host_distance = str(
                        int(phrase["host_ordinal_in_statement"])
                        - int(handoff["donor_host_ordinal_in_statement"])
                    )
                    handoff_anchor_event_gap = str(
                        event_number(target_event)
                        - event_number(handoff["donor_event_id"])
                        - 1
                    )
                    handoff_event_gap = str(
                        event_number(target_event)
                        - event_number(handoff["donor_carrier_source_event_id"])
                        - 1
                    )
                    handoff_line_distance = str(
                        locus_line_number(anchor["locus"])
                        - locus_line_number(handoff["donor_locus"])
                    )
                    handoff_visible_span = handoff["visible_span"]
                    if (
                        state_before is not None
                        and state_before["object_class"] != object_class
                    ):
                        retained_episode_alternative = OBJECT_FORMS[
                            state_before["object_class"]
                        ][0]
                elif current_object is not None:
                    object_class = current_object["object_class"]
                    route = "EPISODE_CARRY"
                    carry_source = current_object["source_event_id"]
                    carry_source_slot = current_object["source_action_slot_id"]
                    carry_source_key = current_object["source_primary_governor_key"]
                    carry_source_locus = current_object["source_locus"]
                    carry_distance = str(
                        int(phrase["host_ordinal_in_statement"])
                        - int(current_object["host_ordinal_in_statement"])
                    )
                    carry_gap = str(
                        int(carry_distance) - 1
                    )
                    carry_event_gap = str(
                        event_number(phrase["anchor_event_id"])
                        - event_number(current_object["source_event_id"])
                        - 1
                    )
                    carry_line_distance = str(
                        locus_line_number(anchor["locus"])
                        - locus_line_number(current_object["source_locus"])
                    )
                    carry_reference_class = (
                        "NEUTRAL_DEFAULT_REUSE"
                        if current_object["origin_route"] == "COLD_BATH_OBJECT_DEFAULT"
                        else "TYPED_BATH_ACTION_CARRY"
                    )
                else:
                    object_class = "BATH_OBJECT"
                    route = "COLD_BATH_OBJECT_DEFAULT"
                if target_event in LOCAL_HANDOFF_FORM_OVERRIDES:
                    lemma, object_form = LOCAL_HANDOFF_FORM_OVERRIDES[target_event]
                else:
                    lemma = OBJECT_FORMS[object_class][0]
                    object_form = (
                        ANAPHORIC_OBJECT_FORMS[object_class]
                        if route in {"INTERVENING_OBJECT_HANDOFF", "EPISODE_CARRY"}
                        else OBJECT_FORMS[object_class][1]
                    )
                patch_required = not (root_set & {"Y", "OR", "AIN"})
                identity = (
                    phrase["statement_id"],
                    phrase["host_ordinal_in_statement"],
                    key,
                )
                current_clause = current_clause_by_identity[identity]
                completed_clause = (
                    _completed_clause(phrase, current_clause, carrier_roots, object_form)
                    if patch_required else current_clause
                )
                if route != "EPISODE_CARRY":
                    carry_strength = "NOT_APPLICABLE"
                elif int(carry_event_gap) == 0:
                    carry_strength = "ADJACENT_VISIBLE_EVENT"
                elif int(carry_event_gap) <= 4:
                    carry_strength = "SHORT_VISIBLE_EVENT"
                elif int(carry_event_gap) <= 8:
                    carry_strength = "MEDIUM_VISIBLE_EVENT"
                else:
                    carry_strength = "LONG_VISIBLE_EVENT_WORKING"

                gdt569_state = gdt569_by_event.get(target_event)
                if gdt569_state is not None:
                    if (
                        gdt569_state["statement_id"] != statement_id
                        or gdt569_state["physical_page"] != phrase["physical_page"]
                        or gdt569_state["register"] != phrase["register"]
                        or gdt569_state["owner_id"] != phrase["owner_id"]
                    ):
                        raise RuntimeError(f"GDT569 event metadata drift: {target_event}")
                    if gdt569_state["action_carry"] != "NO":
                        raise RuntimeError(f"unexpected GDT569 action carry at {target_event}")
                gdt569_parallel_relation, gdt569_parallel_note = gdt569_relation(
                    gdt569_state, object_class, route
                )
                row = {
                    "bath_action_ordinal": str(len(action_rows) + 1),
                    "primary_governor_key": key,
                    "action_slot_id": phrase["action_slot_id"],
                    "source_event_id": phrase["anchor_event_id"],
                    "statement_id": statement_id,
                    "physical_page": phrase["physical_page"],
                    "locus": anchor["locus"],
                    "paragraph_key": paragraph["paragraph_key"],
                    "paragraph_locus_range": paragraph["paragraph_locus_range"],
                    "bath_segment_key": segment_key,
                    "host_ordinal_in_statement": phrase["host_ordinal_in_statement"],
                    "surface": anchor["surface"],
                    "component_recipe": anchor["component_recipe"],
                    "carrier_slot_count": str(len(carriers)),
                    "carrier_slot_ids": pipe(row["carrier_slot_id"] for row in carriers),
                    "carrier_root_sequence": pipe(carrier_roots),
                    "aiin_fill_present": "YES" if "AIIN" in root_set else "NO",
                    "body_blockers_present": pipe(blockers),
                    "state_before_object_class": state_before["object_class"] if state_before else "NONE",
                    "state_before_source_event_id": state_before["source_event_id"] if state_before else "NONE",
                    "reset_before": pipe(reset_reasons),
                    "object_selection_route": route,
                    "gdt592_object_class": object_class,
                    "gdt592_object_lemma_de": lemma,
                    "gdt592_object_form_de": object_form,
                    "gdt592_object_source_event_id": (
                        handoff_carrier_source
                        if route == "INTERVENING_OBJECT_HANDOFF"
                        else carry_source if route == "EPISODE_CARRY" else target_event
                    ),
                    "gdt592_reference_origin_route": (
                        current_object["origin_route"]
                        if route == "EPISODE_CARRY" and current_object is not None
                        else route
                    ),
                    "gdt592_reference_origin_event_id": (
                        current_object["origin_event_id"]
                        if route == "EPISODE_CARRY" and current_object is not None
                        else handoff_carrier_source if route == "INTERVENING_OBJECT_HANDOFF" else target_event
                    ),
                    "carry_source_event_id": carry_source,
                    "carry_source_action_slot_id": carry_source_slot,
                    "carry_source_primary_governor_key": carry_source_key,
                    "carry_source_locus": carry_source_locus,
                    "carry_host_ordinal_distance": carry_distance,
                    "carry_intervening_host_count": carry_gap,
                    "carry_intervening_event_number_count": carry_event_gap,
                    "carry_locus_line_distance": carry_line_distance,
                    "carry_reference_class": carry_reference_class,
                    "carry_working_strength": carry_strength,
                    "handoff_donor_anchor_event_id": handoff_anchor_source,
                    "handoff_donor_carrier_source_event_id": handoff_carrier_source,
                    "handoff_source_action_slot_id": handoff_source_slot,
                    "handoff_source_carrier_slot_ids": handoff_source_carrier_slots,
                    "handoff_source_primary_governor_key": handoff_source_key,
                    "handoff_donor_host_ordinal_in_statement": (
                        handoff["donor_host_ordinal_in_statement"]
                        if route == "INTERVENING_OBJECT_HANDOFF" and handoff is not None
                        else "NOT_APPLICABLE"
                    ),
                    "handoff_source_root": handoff_source_root,
                    "handoff_source_locus": handoff_source_locus,
                    "handoff_host_ordinal_distance": handoff_host_distance,
                    "handoff_anchor_intervening_event_number_count": handoff_anchor_event_gap,
                    "handoff_intervening_event_number_count": handoff_event_gap,
                    "handoff_locus_line_distance": handoff_line_distance,
                    "handoff_manual_visible_span": handoff_visible_span,
                    "handoff_donor_clause_de": (
                        handoff["donor_clause_de"]
                        if route == "INTERVENING_OBJECT_HANDOFF" and handoff is not None
                        else "NOT_APPLICABLE"
                    ),
                    "handoff_donor_phrase_provenance": (
                        handoff["donor_phrase_provenance"]
                        if route == "INTERVENING_OBJECT_HANDOFF" and handoff is not None
                        else "NOT_APPLICABLE"
                    ),
                    "retained_episode_alternative_de": retained_episode_alternative,
                    "gdt569_state_join_status": (
                        "MATCHED" if gdt569_state is not None else "NO_STATE_ROW"
                    ),
                    "gdt569_state_edition_ordinal": (
                        gdt569_state["state_edition_ordinal"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_argument_carry": (
                        gdt569_state["argument_carry"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_action_carry": (
                        gdt569_state["action_carry"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_argument_source_type": (
                        gdt569_state["argument_source_type"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_inherited_argument_root": (
                        gdt569_state["inherited_argument_root"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_explicit_argument_phrase_de": (
                        gdt569_state["explicit_argument_phrase_de"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_carried_argument_phrase_de": (
                        gdt569_state["carried_argument_phrase_de"] if gdt569_state else "NOT_APPLICABLE"
                    ),
                    "gdt569_parallel_relation": gdt569_parallel_relation,
                    "gdt569_parallel_note_de": gdt569_parallel_note,
                    "gdt590_current_clause_de": current_clause,
                    "gdt592_completed_clause_de": completed_clause,
                    "clause_patch_required": "YES" if patch_required else "NO",
                    "retained_alternative_de": "Stationsansatz" if phrase["anchor_event_id"] == "G407-E2652" else "NOT_APPLICABLE",
                    "retained_generic_alternative_de": (
                        "Badegut" if route == "EPISODE_CARRY" else "NOT_APPLICABLE"
                    ),
                    "paragraph_boundary_after": phrase["paragraph_boundary"],
                    "guard": "WRITTEN_OBJECT_FIRST__BLOCKER_THEN_13_EXACT_LOCAL_HANDOFFS__THEN_SAME_SEGMENT_BATH_CARRY__THEN_NEUTRAL_DEFAULT",
                }
                action_rows.append(row)
                action_by_key[key] = row
                segment_rows[segment_key].append(row)
                if route == "EPISODE_CARRY" and state_before is not None:
                    origin_route = state_before["origin_route"]
                    origin_event_id = state_before["origin_event_id"]
                elif route == "INTERVENING_OBJECT_HANDOFF":
                    origin_route = route
                    origin_event_id = handoff_carrier_source
                else:
                    origin_route = route
                    origin_event_id = target_event
                current_object = {
                    "object_class": object_class,
                    "source_event_id": phrase["anchor_event_id"],
                    "source_action_slot_id": phrase["action_slot_id"],
                    "source_primary_governor_key": key,
                    "source_locus": anchor["locus"],
                    "host_ordinal_in_statement": phrase["host_ordinal_in_statement"],
                    "origin_route": origin_route,
                    "origin_event_id": origin_event_id,
                }
            pending_reader_reset = phrase["paragraph_boundary"] == "PARAGRAPH_AFTER"
            previous_paragraph = paragraph["paragraph_key"]

    episode_rows: list[dict[str, str]] = []
    for segment_key, members in sorted(
        segment_rows.items(), key=lambda item: int(item[1][0]["bath_action_ordinal"])
    ):
        routes = [row["object_selection_route"] for row in members]
        episode_rows.append(
            {
                "bath_episode_ordinal": str(len(episode_rows) + 1),
                "bath_segment_key": segment_key,
                "statement_id": members[0]["statement_id"],
                "physical_page": members[0]["physical_page"],
                "paragraph_key": members[0]["paragraph_key"],
                "paragraph_locus_range": members[0]["paragraph_locus_range"],
                "bath_action_count": str(len(members)),
                "action_slot_sequence": pipe(row["action_slot_id"] for row in members),
                "primary_governor_sequence": pipe(
                    row["primary_governor_key"] for row in members
                ),
                "source_event_sequence": pipe(row["source_event_id"] for row in members),
                "surface_sequence": pipe(row["surface"] for row in members),
                "object_class_sequence": "→".join(row["gdt592_object_class"] for row in members),
                "object_lemma_sequence_de": "→".join(row["gdt592_object_lemma_de"] for row in members),
                "selection_route_sequence": "→".join(routes),
                "patch_count": str(sum(row["clause_patch_required"] == "YES" for row in members)),
                "carry_count": str(routes.count("EPISODE_CARRY")),
                "local_handoff_count": str(routes.count("INTERVENING_OBJECT_HANDOFF")),
                "cold_start_route": routes[0],
                "guard": "ONE_STATEMENT_AND_ONE_READER_PHYSICAL_SEGMENT__NO_BOUNDARY_CARRY",
            }
        )

    statement_rows: list[dict[str, str]] = []
    patched_statement_rows: list[dict[str, str]] = []
    actions_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in action_rows:
        actions_by_statement[row["statement_id"]].append(row)
    for source in data["gdt590_statements"]:
        statement_id = source["statement_id"]
        actions = actions_by_statement.get(statement_id, [])
        if not actions:
            statement_rows.append(
                {
                    **source,
                    "gdt592_bath_action_count": "0",
                    "gdt592_object_patch_count": "0",
                    "gdt592_patched_host_keys": "NONE",
                    "gdt592_bath_object_sequence": "NONE",
                    "gdt592_primary_reader_de": source["gdt590_primary_reader_de"],
                    "gdt592_reader_changed": "NO",
                    "gdt592_guard": "GDT590_READER_BYTE_RETAINED__NO_BATH_ACTION",
                }
            )
            continue
        phrases = phrases_by_statement[statement_id]
        spans = _locate_phrase_spans(
            source["gdt590_primary_reader_de"], phrases, current_clause_by_identity
        )
        replacements = {
            row["primary_governor_key"]: sentence_case(row["gdt592_completed_clause_de"]) + "."
            for row in actions
            if row["clause_patch_required"] == "YES"
        }
        pieces: list[str] = []
        cursor = 0
        for start, end, phrase in spans:
            key = phrase["primary_governor_key"]
            if key not in replacements:
                continue
            pieces.append(source["gdt590_primary_reader_de"][cursor:start])
            pieces.append(replacements[key])
            cursor = end
        pieces.append(source["gdt590_primary_reader_de"][cursor:])
        primary = "".join(pieces)
        patches = [row for row in actions if row["clause_patch_required"] == "YES"]
        changed = bool(patches)
        output = {
            **source,
            "gdt592_bath_action_count": str(len(actions)),
            "gdt592_object_patch_count": str(len(patches)),
            "gdt592_patched_host_keys": pipe(row["primary_governor_key"] for row in patches),
            "gdt592_bath_object_sequence": "→".join(row["gdt592_object_lemma_de"] for row in actions),
            "gdt592_primary_reader_de": primary,
            "gdt592_reader_changed": "YES" if changed else "NO",
            "gdt592_guard": "EXACT_HOST_SENTENCE_ALIGNMENT__ONLY_MISSING_BATH_OBJECTS_PATCHED" if changed else "GDT590_READER_BYTE_RETAINED__EXPLICIT_BATH_OBJECT",
        }
        statement_rows.append(output)
        if changed:
            patched_statement_rows.append(
                {
                    "patched_statement_ordinal": str(len(patched_statement_rows) + 1),
                    "statement_id": statement_id,
                    "physical_page": source["physical_page"],
                    "bath_action_count": str(len(actions)),
                    "object_patch_count": str(len(patches)),
                    "patched_event_ids": pipe(row["source_event_id"] for row in patches),
                    "patched_host_keys": pipe(row["primary_governor_key"] for row in patches),
                    "selected_object_sequence_de": "→".join(row["gdt592_object_lemma_de"] for row in patches),
                    "gdt590_primary_reader_de": source["gdt590_primary_reader_de"],
                    "gdt592_primary_reader_de": primary,
                    "guard": "COMPLETE_STATEMENT_BEFORE_AFTER__UNCHANGED_CLAUSES_RETAINED",
                }
            )

    objectless_rows = [
        {**row, "objectless_ordinal": str(index)}
        for index, row in enumerate(
            (row for row in action_rows if row["carrier_slot_count"] == "0"), 1
        )
    ]
    fill_only_rows = [
        {**row, "fill_only_ordinal": str(index)}
        for index, row in enumerate(
            (row for row in action_rows if row["carrier_root_sequence"] == "AIIN"), 1
        )
    ]
    carry_rows = [
        {**row, "carry_ordinal": str(index)}
        for index, row in enumerate(
            (row for row in action_rows if row["object_selection_route"] == "EPISODE_CARRY"), 1
        )
    ]
    handoff_rows = [
        {**row, "handoff_ordinal": str(index)}
        for index, row in enumerate(
            (
                row
                for row in action_rows
                if row["object_selection_route"] == "INTERVENING_OBJECT_HANDOFF"
            ),
            1,
        )
    ]
    gdt569_divergence_rows = [
        {**row, "gdt569_divergence_ordinal": str(index)}
        for index, row in enumerate(
            (
                row
                for row in action_rows
                if row["gdt569_parallel_relation"]
                == "GDT569_CARRY_CLASS_DIVERGENCE_RETAINED"
            ),
            1,
        )
    ]
    blocker_rows = [
        {**row, "blocker_default_ordinal": str(index)}
        for index, row in enumerate(
            (row for row in action_rows if row["object_selection_route"] == "BODY_BLOCKER_STATION"), 1
        )
    ]

    page_rows: list[dict[str, str]] = []
    for page in sorted(BATH_PAGES):
        members = [row for row in action_rows if row["physical_page"] == page]
        objects = Counter(row["gdt592_object_class"] for row in members)
        routes = Counter(row["object_selection_route"] for row in members)
        page_rows.append(
            {
                "page_profile_ordinal": str(len(page_rows) + 1),
                "physical_page": page,
                "bath_statement_count": str(len({row["statement_id"] for row in members})),
                "bath_episode_count": str(len({row["bath_segment_key"] for row in members})),
                "bath_action_count": str(len(members)),
                "body_count": str(objects["BODY"]),
                "station_count": str(objects["STATION"]),
                "bath_object_count": str(objects["BATH_OBJECT"]),
                "bath_unit_count": str(objects["BATH_UNIT"]),
                "portion_count": str(objects["PORTION"]),
                "written_object_count": str(sum(route.startswith("WRITTEN_") for route in (row["object_selection_route"] for row in members))),
                "blocker_default_count": str(routes["BODY_BLOCKER_STATION"]),
                "episode_carry_count": str(routes["EPISODE_CARRY"]),
                "local_handoff_count": str(routes["INTERVENING_OBJECT_HANDOFF"]),
                "cold_default_count": str(routes["COLD_BATH_OBJECT_DEFAULT"]),
                "clause_patch_count": str(sum(row["clause_patch_required"] == "YES" for row in members)),
                "guard": "SIX_ALREADY_ADMITTED_BIOLOGICAL_BATH_PAGES_ONLY",
            }
        )

    object_profile = Counter(row["gdt592_object_class"] for row in action_rows)
    route_profile = Counter(row["object_selection_route"] for row in action_rows)
    patch_profile = Counter(
        "FILL_ONLY" if row["carrier_root_sequence"] == "AIIN" else "OBJECTLESS"
        for row in action_rows
        if row["clause_patch_required"] == "YES"
    )
    carry_object_profile = Counter(row["gdt592_object_class"] for row in carry_rows)
    handoff_object_profile = Counter(row["gdt592_object_class"] for row in handoff_rows)
    gdt569_relation_profile = Counter(
        row["gdt569_parallel_relation"] for row in action_rows
    )
    result = {
        "experiment_id": "GDT592",
        "status": STATUS,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "bath_page_count": len(BATH_PAGES),
        "bath_statement_count": len(statement_ids),
        "bath_episode_count": len(episode_rows),
        "bath_action_count": len(action_rows),
        "object_profile": dict(sorted(object_profile.items())),
        "selection_route_profile": dict(sorted(route_profile.items())),
        "objectless_action_count": len(objectless_rows),
        "fill_only_action_count": len(fill_only_rows),
        "clause_patch_count": sum(row["clause_patch_required"] == "YES" for row in action_rows),
        "patch_profile": dict(sorted(patch_profile.items())),
        "patched_statement_count": len(patched_statement_rows),
        "unchanged_statement_count": len(statement_rows) - len(patched_statement_rows),
        "episode_carry_count": len(carry_rows),
        "local_handoff_count": len(handoff_rows),
        "typed_bath_carry_count": sum(
            row["carry_reference_class"] == "TYPED_BATH_ACTION_CARRY"
            for row in carry_rows
        ),
        "neutral_default_reuse_count": sum(
            row["carry_reference_class"] == "NEUTRAL_DEFAULT_REUSE"
            for row in carry_rows
        ),
        "long_visible_carry_count": sum(
            row["carry_working_strength"] == "LONG_VISIBLE_EVENT_WORKING"
            for row in carry_rows
        ),
        "carry_object_profile": dict(sorted(carry_object_profile.items())),
        "handoff_object_profile": dict(sorted(handoff_object_profile.items())),
        "gdt569_state_join_count": sum(
            row["gdt569_state_join_status"] == "MATCHED" for row in action_rows
        ),
        "gdt569_relation_profile": dict(sorted(gdt569_relation_profile.items())),
        "gdt569_class_divergence_count": len(gdt569_divergence_rows),
        "blocker_station_default_count": len(blocker_rows),
        "e2652_object_class": next(
            row["gdt592_object_class"] for row in action_rows
            if row["source_event_id"] == "G407-E2652"
        ),
        "e2652_retained_alternative_de": "Stationsansatz",
        "working_rule_de": (
            "Geschriebenes Y/OR/AIN vor Hostblocker vor 13 exakt benannten lokalen "
            "Objektübergaben vor Carry derselben Badeepisode; sonst Badegut. "
            "AIIN bleibt Badfüllung und GDT569 bleibt eine parallele Argumentspur."
        ),
    }
    return {
        "actions": action_rows,
        "episodes": episode_rows,
        "objectless": objectless_rows,
        "fill_only": fill_only_rows,
        "carries": carry_rows,
        "handoffs": handoff_rows,
        "gdt569_divergences": gdt569_divergence_rows,
        "blockers": blocker_rows,
        "pages": page_rows,
        "patched_statements": patched_statement_rows,
        "statements": statement_rows,
        "result": result,
    }


def render_reader(built: dict[str, Any]) -> str:
    statements = {
        row["statement_id"]: row for row in built["statements"]
    }
    actions_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in built["actions"]:
        actions_by_statement[row["statement_id"]].append(row)
    lines = [
        "# GDT592 — vollständiger Badegut-Arbeitsleser",
        "",
        "Alle 254 `SH_BIO_BATHE`-Handlungen besitzen hier ein sichtbares Arbeitsobjekt. "
        "Geschriebene Objekte bleiben vorrangig; fehlende Objekte kommen aus Blocker, "
        "13 exakt benannten lokalen Objektübergaben, elf kurzen Badeepisode-Carries "
        "oder dem neutralen Default `Badegut` (`das zu badende Gut`). Die ältere "
        "GDT569-Argumentspur bleibt daneben sichtbar und wird nicht mit dem Objekt gleichgesetzt.",
        "",
    ]
    for page in sorted(BATH_PAGES):
        lines.extend([f"## {page}", ""])
        statement_ids = list(
            dict.fromkeys(
                row["statement_id"]
                for row in built["actions"]
                if row["physical_page"] == page
            )
        )
        for statement_id in statement_ids:
            actions = actions_by_statement[statement_id]
            object_trace = " → ".join(
                f"{row['source_event_id']}={row['gdt592_object_lemma_de']}"
                f"[{row['object_selection_route']};GDT569={row['gdt569_inherited_argument_root']}"
                f"/{row['gdt569_parallel_relation']}]"
                for row in actions
            )
            lines.extend(
                [
                    f"### {statement_id}",
                    "",
                    f"Objektspur: `{object_trace}`",
                    "",
                    statements[statement_id]["gdt592_primary_reader_de"],
                    "",
                ]
            )
    lines.extend(
        [
            "## Die 13 lokalen Übergaben",
            "",
            "Diese Ziele übernehmen den zuletzt sichtbaren, näheren Y/OR/AIN-Träger "
            "anstelle des älteren Badehandlung-Donors:",
            "",
        ]
    )
    for row in built["handoffs"]:
        lines.append(
            f"- `{row['source_event_id']}` ← `{row['handoff_donor_carrier_source_event_id']}` "
            f"({row['handoff_source_root']}): **{row['gdt592_object_lemma_de']}**; "
            f"sichtbar `{row['handoff_manual_visible_span']}`."
        )
    lines.extend(
        [
            "",
            "## Zwei echte Parallelkonflikte",
            "",
        ]
    )
    for row in built["gdt569_divergences"]:
        lines.append(
            f"- `{row['source_event_id']}`: GDT592 **{row['gdt592_object_lemma_de']}** "
            f"gegen GDT569 `{row['gdt569_inherited_argument_root']}` / "
            f"{row['gdt569_carried_argument_phrase_de']}. Beide bleiben offen."
        )
    lines.extend(
        [
            "",
            "## Nächste konkrete Reserve",
            "",
            "Bei 61 neutralen Badegut-Defaults trägt GDT569 bereits einen spezifischeren "
            "Kandidaten: 49× `Y`, 8× `AIN`, 4× `OR`. Diese Spur ist absichtlich noch "
            "keine automatische Objektgleichung; sie ist der nächste Verfeinerungspass.",
            "",
            "## E2652 bleibt offen sichtbar",
            "",
            "E2652 bleibt `Körper` unter der GDT590/GDT591-Regel. Seine "
            "Stationsalternative wird nicht gelöscht; GDT592 ergänzt dort keinen neuen Default.",
            "",
        ]
    )
    return "\n".join(lines)


def write_built(built: dict[str, Any]) -> None:
    for name in (
        "actions", "episodes", "objectless", "fill_only", "carries", "handoffs",
        "gdt569_divergences", "blockers",
        "pages", "patched_statements", "statements",
    ):
        write_tsv(OUTPUTS[name], built[name])
    OUTPUTS["reader"].write_text(render_reader(built), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
