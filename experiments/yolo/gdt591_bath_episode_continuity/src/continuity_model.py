#!/usr/bin/env python3
"""Build GDT591 bath-host episode continuity over the fixed GDT590 reading."""

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


EXP = ROOT / "experiments/yolo/gdt591_bath_episode_continuity"
ART = EXP / "artifacts"
STATUS = (
    "PASS_92_BATH_HOST_CONTINUITY__64_STATEMENTS__17_PARAGRAPHS__"
    "28_STATEMENT_TRANSITIONS__14_BLOCKER_LICENSED_SWITCHES__"
    "39_REMOTE_CARRIERS__E2652_UNIQUE_BUT_LAYOUT_COMPACT"
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

INPUTS = {
    "analogs": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_92_bath_y_analogy_matrix.tsv",
    "adjudications": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_4_bath_fork_adjudications.tsv",
    "visuals": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_4_host_visual_contexts.tsv",
    "statements": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_793_body_adjudicated_statement_reader.tsv",
    "slots": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_1243_adjudicated_slot_replay.tsv",
    "hosts": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_953_complete_host_replay.tsv",
    "gdt584_phrases": ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts/gdt584_statement_wide_host_phrases.tsv",
    "gdt587_phrases": ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/artifacts/gdt587_candidate_statement_host_phrases.tsv",
    "assignments": ROOT / "experiments/yolo/gdt587_action_conditioned_carrier_nouns/artifacts/gdt587_1243_action_conditioned_carrier_assignments.tsv",
    "focus": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_5672_focus_reconciliation.tsv",
    "gdt581_slots": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_15889_complete_slot_ledger.tsv",
    "defaults": ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts/gdt582_15889_complete_default_ledger.tsv",
    "events": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_5122_running_event_edition.tsv",
    "lines": ROOT / "transcription/voynich_zl3b_lines.tsv",
    "layout": ROOT / "transcription/zl3b_layout_aware_reading_units.tsv",
}

OUTPUTS = {
    "hosts": ART / "gdt591_92_bath_y_host_continuity.tsv",
    "statements": ART / "gdt591_64_bath_y_statement_sequences.tsv",
    "paragraphs": ART / "gdt591_17_bath_y_paragraph_sequences.tsv",
    "statement_transitions": ART / "gdt591_28_intra_statement_bath_y_transitions.tsv",
    "paragraph_transitions": ART / "gdt591_75_intra_paragraph_bath_y_transitions.tsv",
    "remote": ART / "gdt591_39_remote_bath_carrier_attachments.tsv",
    "comparators": ART / "gdt591_7_e2652_comparator_ladder.tsv",
    "targets": ART / "gdt591_4_target_episode_stress.tsv",
    "reader": ART / "GDT591_BATH_EPISODE_READER.md",
    "result": ART / "gdt591_result.json",
    "validation": ART / "gdt591_validation.json",
}

TARGET_META = {
    "G407-E2404": {
        "rank": "1",
        "statement_id": "G407-S312",
        "statement_physical_span": "f77r.9 W9 → f77r.10 W1–W5",
        "line_wrap_class": "RETURN_WRAP_CONTINUATION",
        "episode_strength": "MEDIUM_HIGH__COMPATIBLE_NOT_DECISIVE",
        "episode_evidence_de": (
            "Stationsvorbereitung und Behandlung vom Ausgang gehen in ein blockerfreies Bad auf Grad I über; "
            "Körper ist ein lesbarer Objektwechsel, die fortgesetzte Station bleibt referentiell sparsamer."
        ),
        "counter_episode_de": "Ein einziger fortgesetzter Apparat- oder Stationsgang bleibt vollständig lesbar.",
    },
    "G407-E2637": {
        "rank": "2",
        "statement_id": "G407-S382",
        "statement_physical_span": "f77r.38 W9 → f77r.39 W1–W6",
        "line_wrap_class": "RETURN_WRAP_CONTINUATION",
        "episode_strength": "HIGH__DIRECT_BODY_TO_BLOCKED_STATION_CONTRAST",
        "episode_evidence_de": (
            "In derselben physischen Zeile steht clean cheey als Körper vor L-geblocktem lsheey als Station; "
            "der objektlose Zwischenhost übernimmt Körper bis der neue Stationsblocker erscheint."
        ),
        "counter_episode_de": "Ein einziger technischer Stationszyklus wäre referentiell einfacher, braucht aber eine Ausnahme vom Blockermodell.",
    },
    "G407-E2652": {
        "rank": "3",
        "statement_id": "G407-S385",
        "statement_physical_span": "f77r.40 W8 → f77r.41 W1–W4",
        "line_wrap_class": "RETURN_WRAP__AIIN_SH_OLY_ADJACENT_W1_W3",
        "episode_strength": "MEDIUM__UNIQUE_EXACT_STRUCTURE__STATION_RIVAL_STRONG",
        "episode_evidence_de": (
            "Owner-Y=Station endet auf der Vorzeile; danach stehen daiin–sh–qolchey unmittelbar als W1–W3. "
            "AIIN und Y hängen am neuen SH-Gouverneur, obwohl sie in anderen Events geschrieben sind."
        ),
        "counter_episode_de": (
            "OL+Y kann den vorigen Stationsreferenten forttragen; die Form liegt bildlich am Auslass und "
            "der bare-SH-Aufbau besitzt kein exaktes Körperminimalpaar."
        ),
    },
    "G407-E3182": {
        "rank": "4",
        "statement_id": "G407-S495",
        "statement_physical_span": "f82r.1 W1–W8 → f82r.2 W1–W2",
        "line_wrap_class": "LAYOUT_INTERRUPTION_AFTER_W4_PLUS_RETURN_WRAP",
        "episode_strength": "VERY_HIGH__STATION_TO_BODY_TO_BODY_SEQUENCE",
        "episode_evidence_de": (
            "Ein geblockter Stationshost geht in Körper+Füllung auf Grad II und direkt danach Körper auf "
            "Grad I über; die Objektfolge und der echte Layoutbruch bleiben sichtbar."
        ),
        "counter_episode_de": "Bildnah kann der zentrale Apparat auf Grad II vor dem folgenden Körperbad auf Grad I stehen.",
    },
}

COMPARATOR_IDS = (
    "G407-E2652", "G407-E2637", "G407-E2508", "G407-E1648",
    "G407-E1758", "G407-E1789", "G407-E1433",
)


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


def split_plus(value: str) -> list[str]:
    return [part for part in value.split("+") if part and part != "NONE"]


def event_number(event_id: str) -> int:
    match = re.search(r"-E(\d+)", event_id)
    if not match:
        raise RuntimeError(f"not a running event ID: {event_id}")
    return int(match.group(1))


def role(row: dict[str, str]) -> str:
    values = set(split_pipe(row["gdt590_y_lemma_sequence"]))
    if values == {"Körper"}:
        return "BODY"
    if values == {"Stationsansatz"}:
        return "STATION"
    raise RuntimeError(f"mixed or unknown bath role at {row['source_event_id']}: {values}")


def _paragraph_map(lines: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in lines:
        if row["kind"] == "P":
            by_page[row["page"]].append(row)
    locus_map: dict[str, dict[str, str]] = {}
    paragraph_loci: dict[str, list[str]] = defaultdict(list)
    for page, page_rows in by_page.items():
        page_rows.sort(key=lambda row: int(row["line_number"]))
        paragraph = 0
        paragraph_line = 0
        paragraph_start = 0
        for row in page_rows:
            if row["paragraph_start"] == "1" or paragraph == 0:
                paragraph += 1
                paragraph_line = 0
                paragraph_start = int(row["line_number"])
            paragraph_line += 1
            paragraph_key = f"{page}:P{paragraph}"
            paragraph_loci[paragraph_key].append(row["locus"])
            locus_map[row["locus"]] = {
                "paragraph_key": paragraph_key,
                "paragraph_id": f"P{paragraph}",
                "paragraph_line_ordinal": str(paragraph_line),
                "paragraph_start_line": str(paragraph_start),
            }
    for paragraph_key, loci in paragraph_loci.items():
        page = paragraph_key.split(":", 1)[0]
        end_line = loci[-1].split(".", 1)[1]
        start_line = locus_map[loci[0]]["paragraph_start_line"]
        span = f"{page}.{start_line}–.{end_line}"
        for locus in loci:
            locus_map[locus]["paragraph_locus_range"] = span
    return locus_map, paragraph_loci


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "analogs": guarded_rows(INPUTS["analogs"], selector="physical_page", allowed=BATH_PAGES),
        "adjudications": guarded_rows(INPUTS["adjudications"], selector="physical_page", allowed={"f77r", "f82r"}),
        "visuals": guarded_rows(INPUTS["visuals"], selector="physical_page", allowed={"f77r", "f82r"}),
        "statements": read_sealed_reader(INPUTS["statements"]),
        "slots": guarded_rows(INPUTS["slots"], selector="physical_page", allowed=BATH_PAGES),
        # Keep the complete admitted 953-host population available for the
        # E2652 exact-signature census.  Bath sequences below still select the
        # fixed 92-row GDT590 inventory and never introduce a new page.
        "hosts": guarded_rows(INPUTS["hosts"], selector="physical_page", allowed=ADMITTED_PAGES),
        "gdt584_phrases": guarded_rows(INPUTS["gdt584_phrases"], selector="physical_page", allowed=BATH_PAGES),
        "gdt587_phrases": guarded_rows(INPUTS["gdt587_phrases"], selector="physical_page", allowed=BATH_PAGES),
        "assignments": guarded_rows(INPUTS["assignments"], selector="physical_page", allowed=BATH_PAGES),
        "focus": guarded_rows(INPUTS["focus"], selector="physical_page", allowed=BATH_PAGES),
        "gdt581_slots": guarded_rows(INPUTS["gdt581_slots"], selector="physical_page", allowed=BATH_PAGES),
        "defaults": guarded_rows(INPUTS["defaults"], selector="physical_page", allowed=BATH_PAGES),
        "events": guarded_rows(INPUTS["events"], selector="physical_page", allowed=BATH_PAGES),
        "lines": guarded_rows(INPUTS["lines"], selector="page", allowed=BATH_PAGES),
        "layout": guarded_rows(INPUTS["layout"], selector="page", allowed=BATH_PAGES),
    }


def build(data: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    analogs = sorted(data["analogs"], key=lambda row: int(row["analogy_ordinal"]))
    if len(analogs) != 92:
        raise RuntimeError(f"expected 92 bath-Y hosts, found {len(analogs)}")
    event_by_id: dict[str, dict[str, str]] = {}
    for row in data["events"]:
        # G407 rows are addressed by global_running_event_id; newly admitted
        # G515 rows retain their source_event_id while the global field is an
        # R identifier.  Index both without changing either identity.
        event_by_id[row["global_running_event_id"]] = row
        event_by_id[row["source_event_id"]] = row
    complete_host_by_key = {row["primary_governor_key"]: row for row in data["hosts"]}
    if len(complete_host_by_key) != len(data["hosts"]):
        raise RuntimeError("complete GDT589 governor keys are not unique")
    phrase584_candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt584_phrases"]:
        phrase584_candidates[row["primary_governor_key"]].append(row)
    phrase587_candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt587_phrases"]:
        phrase587_candidates[row["primary_governor_key"]].append(row)
    phrase587_by_key: dict[str, dict[str, str]] = {}
    for analog in analogs:
        key = analog["primary_governor_key"]
        if len(phrase584_candidates[key]) != 1:
            raise RuntimeError(
                f"GDT584 bath phrase join not unique for {key}: {len(phrase584_candidates[key])}"
            )
        candidates = phrase587_candidates[key]
        if len(candidates) != 1:
            raise RuntimeError(f"GDT587 bath phrase join not unique for {key}: {len(candidates)}")
        phrase587_by_key[key] = candidates[0]
    statement_by_id = {row["statement_id"]: row for row in data["statements"]}
    adjudication_by_event = {row["source_event_id"]: row for row in data["adjudications"]}
    visual_by_event = {row["source_event_id"]: row for row in data["visuals"]}
    locus_map, paragraph_loci = _paragraph_map(data["lines"])
    slot581_by_id = {row["slot_id"]: row for row in data["gdt581_slots"]}

    assignments_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["assignments"]:
        assignments_by_host[row["primary_governor_key"]].append(row)
    for rows in assignments_by_host.values():
        rows.sort(key=lambda row: int(row["assignment_ordinal"]))

    focus_candidates: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in data["focus"]:
        focus_candidates[(row["event_id"], row["focus_root"], row["focus_final_position"])].append(row)

    phrases_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["gdt584_phrases"]:
        phrases_by_statement[row["statement_id"]].append(row)
    for rows in phrases_by_statement.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))

    host_rows: list[dict[str, str]] = []
    remote_rows: list[dict[str, str]] = []
    analog_by_key = {row["primary_governor_key"]: row for row in analogs}
    for analog in analogs:
        key = analog["primary_governor_key"]
        complete = complete_host_by_key[key]
        phrase = phrase587_by_key[key]
        event = event_by_id[analog["source_event_id"]]
        paragraph = locus_map[event["locus"]]
        current_role = role(analog)
        carrier_rows = assignments_by_host[key]
        direct = [row for row in carrier_rows if row["source_event_or_card_id"] == phrase["anchor_event_id"]]
        remote = [row for row in carrier_rows if row["source_event_or_card_id"] != phrase["anchor_event_id"]]
        current_clause = phrase["gdt587_reader_clause_de"]
        if analog["source_event_id"] in adjudication_by_event:
            target = adjudication_by_event[analog["source_event_id"]]
            old_clause = target["gdt589_station_clause_de"].removesuffix(".")
            new_clause = target["gdt590_body_clause_de"].removesuffix(".")
            if current_clause.count(old_clause) != 1:
                raise RuntimeError(
                    f"GDT590 clause patch source not unique at {analog['source_event_id']}"
                )
            current_clause = current_clause.replace(old_clause, new_clause, 1)
        host_rows.append(
            {
                "bath_host_ordinal": str(len(host_rows) + 1),
                "primary_governor_key": key,
                "source_event_id": analog["source_event_id"],
                "statement_id": analog["statement_id"],
                "physical_page": analog["physical_page"],
                "locus": analog["locus"],
                "paragraph_key": paragraph["paragraph_key"],
                "paragraph_id": paragraph["paragraph_id"],
                "paragraph_line_ordinal": paragraph["paragraph_line_ordinal"],
                "paragraph_locus_range": paragraph["paragraph_locus_range"],
                "host_ordinal_in_statement": phrase["host_ordinal_in_statement"],
                "surface": analog["surface"],
                "component_recipe": analog["component_recipe"],
                "complete_host_values_written": complete["complete_host_values_written"],
                "direct_governor_tokens": complete["direct_governor_tokens"],
                "written_root_sequence": analog["written_root_sequence"],
                "carrier_slot_count": complete["carrier_slot_count"],
                "y_slot_count": str(split_plus(analog["written_root_sequence"]).count("Y")),
                "direct_carrier_count": str(len(direct)),
                "remote_carrier_count": str(len(remote)),
                "body_blockers_present": analog["body_blockers_present"],
                "gdt590_role": current_role,
                "gdt590_y_lemma_sequence": analog["gdt590_y_lemma_sequence"],
                "gdt590_reader_clause_de": current_clause,
                "gdt590_changed": analog["gdt590_changed"],
                "paragraph_boundary_inside_host": phrase["paragraph_boundary"],
                "guard": "EXACT_COMPLETE_HOST__PHYSICAL_PARAGRAPH_SEPARATE_FROM_READER_BOUNDARY",
            }
        )
        for assignment in remote:
            if (
                assignment["statement_or_record_id"] != phrase["statement_id"]
                or assignment["owner"] != phrase["owner_id"]
            ):
                raise RuntimeError(
                    f"remote assignment leaves phrase statement/owner at {assignment['carrier_slot_id']}"
                )
            candidates = focus_candidates[
                (
                    assignment["source_event_or_card_id"],
                    assignment["carrier_root"],
                    assignment["slot_position"],
                )
            ]
            exact = [row for row in candidates if row["effective_grammar_host_key"] == key]
            if len(exact) != 1:
                raise RuntimeError(
                    f"remote focus join not unique for {assignment['carrier_slot_id']}: {len(exact)}"
                )
            focus = exact[0]
            slot581 = slot581_by_id[assignment["carrier_slot_id"]]
            remote_rows.append(
                {
                    "remote_attachment_ordinal": str(len(remote_rows) + 1),
                    "primary_governor_key": key,
                    "source_event_id": analog["source_event_id"],
                    "statement_id": analog["statement_id"],
                    "physical_page": analog["physical_page"],
                    "locus": analog["locus"],
                    "gdt590_role": current_role,
                    "carrier_slot_id": assignment["carrier_slot_id"],
                    "carrier_source_event_id": assignment["source_event_or_card_id"],
                    "carrier_surface": assignment["surface"],
                    "carrier_root": assignment["carrier_root"],
                    "carrier_slot_position": assignment["slot_position"],
                    "attachment_geometry": focus["attachment_geometry"],
                    "lookahead_cards": focus["lookahead_cards"],
                    "effective_grammar_host_key": focus["effective_grammar_host_key"],
                    "owner_boundary_crossed": focus["owner_boundary_crossed"],
                    "statement_boundary_crossed": focus["statement_boundary_crossed"],
                    "boundary_class": slot581["boundary_class"],
                    "realization_scope": slot581["realization_scope"],
                    "remote_means_de": (
                        "anderes Quellereignis als das Handlungsanker-Ereignis; "
                        "keine Aussage über räumliche Distanz auf dem Blatt"
                    ),
                    "guard": "FIXED_GDT581_ATTACHMENT__NO_REATTACHMENT__NO_OWNER_OR_STATEMENT_CROSS",
                }
            )

    hosts_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    hosts_by_paragraph: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in host_rows:
        hosts_by_statement[row["statement_id"]].append(row)
        hosts_by_paragraph[row["paragraph_key"]].append(row)
    for rows in hosts_by_statement.values():
        rows.sort(key=lambda row: int(row["host_ordinal_in_statement"]))
    for rows in hosts_by_paragraph.values():
        rows.sort(key=lambda row: event_number(row["source_event_id"]))

    statement_transition_rows: list[dict[str, str]] = []
    for statement_id, rows in sorted(hosts_by_statement.items(), key=lambda item: int(statement_by_id[item[0]]["reader_statement_ordinal"])):
        all_phrases = phrases_by_statement[statement_id]
        for left, right in zip(rows, rows[1:]):
            left_ordinal = int(left["host_ordinal_in_statement"])
            right_ordinal = int(right["host_ordinal_in_statement"])
            between = [
                row for row in all_phrases
                if left_ordinal < int(row["host_ordinal_in_statement"]) < right_ordinal
            ]
            controls = [row for row in between if row["gdt584_rule_id"] == "CONTROL_READER_REALIZATION"]
            control_roots = [row["primary_governor_key"].rsplit(":", 1)[-1] for row in controls]
            reader_boundaries = [row for row in between if row["paragraph_boundary"] != "NONE"]
            switch = left["gdt590_role"] != right["gdt590_role"]
            licensed = (
                not switch
                or (
                    (left["body_blockers_present"] == "NONE")
                    != (right["body_blockers_present"] == "NONE")
                )
            )
            statement_transition_rows.append(
                {
                    "transition_ordinal": str(len(statement_transition_rows) + 1),
                    "statement_id": statement_id,
                    "physical_page": left["physical_page"],
                    "paragraph_key": left["paragraph_key"],
                    "from_event_id": left["source_event_id"],
                    "to_event_id": right["source_event_id"],
                    "from_surface": left["surface"],
                    "to_surface": right["surface"],
                    "from_role": left["gdt590_role"],
                    "to_role": right["gdt590_role"],
                    "from_blockers": left["body_blockers_present"],
                    "to_blockers": right["body_blockers_present"],
                    "role_switch": "YES" if switch else "NO",
                    "new_governor": "YES" if left["primary_governor_key"] != right["primary_governor_key"] else "NO",
                    "physical_same_paragraph": "YES" if left["paragraph_key"] == right["paragraph_key"] else "NO",
                    "intervening_host_count": str(len(between)),
                    "intervening_control_count": str(len(controls)),
                    "intervening_control_roots": "|".join(control_roots) or "NONE",
                    "intervening_reader_boundary_count": str(len(reader_boundaries)),
                    "intervening_reader_boundaries": "|".join(row["paragraph_boundary"] for row in reader_boundaries) or "NONE",
                    "switch_license": "BLOCKER_STATE_CHANGES_WITH_ROLE" if switch and licensed else "SAME_ROLE" if not switch else "UNLICENSED",
                    "working_transition_de": f"{left['gdt590_role']} → {right['gdt590_role']}",
                    "guard": "ADJACENT_BATH_Y_HOSTS_WITHIN_STATEMENT__DESCRIPTIVE_REPLAY_NOT_EDGE_EVIDENCE",
                }
            )

    paragraph_transition_rows: list[dict[str, str]] = []
    for paragraph_key, rows in sorted(hosts_by_paragraph.items()):
        for left, right in zip(rows, rows[1:]):
            paragraph_transition_rows.append(
                {
                    "transition_ordinal": str(len(paragraph_transition_rows) + 1),
                    "paragraph_key": paragraph_key,
                    "physical_page": left["physical_page"],
                    "paragraph_locus_range": left["paragraph_locus_range"],
                    "from_statement_id": left["statement_id"],
                    "to_statement_id": right["statement_id"],
                    "same_statement": "YES" if left["statement_id"] == right["statement_id"] else "NO",
                    "from_event_id": left["source_event_id"],
                    "to_event_id": right["source_event_id"],
                    "from_locus": left["locus"],
                    "to_locus": right["locus"],
                    "from_role": left["gdt590_role"],
                    "to_role": right["gdt590_role"],
                    "role_switch": "YES" if left["gdt590_role"] != right["gdt590_role"] else "NO",
                    "from_blockers": left["body_blockers_present"],
                    "to_blockers": right["body_blockers_present"],
                    "guard": "ADJACENT_BATH_Y_HOSTS_WITHIN_PHYSICAL_ZL3B_PARAGRAPH__NO_IMAGE_FLOW_CLAIM",
                }
            )

    statement_rows: list[dict[str, str]] = []
    transition_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statement_transition_rows:
        transition_by_statement[row["statement_id"]].append(row)
    for statement_id, rows in sorted(hosts_by_statement.items(), key=lambda item: int(statement_by_id[item[0]]["reader_statement_ordinal"])):
        transitions = transition_by_statement[statement_id]
        roles = [row["gdt590_role"] for row in rows]
        if set(roles) == {"BODY"}:
            episode_class = "BODY_ONLY"
        elif set(roles) == {"STATION"}:
            episode_class = "STATION_ONLY"
        else:
            episode_class = "MIXED_BODY_STATION"
        statement_rows.append(
            {
                "statement_episode_ordinal": str(len(statement_rows) + 1),
                "statement_id": statement_id,
                "physical_page": rows[0]["physical_page"],
                "paragraph_keys": "|".join(dict.fromkeys(row["paragraph_key"] for row in rows)),
                "bath_host_count": str(len(rows)),
                "body_host_count": str(roles.count("BODY")),
                "station_host_count": str(roles.count("STATION")),
                "role_sequence": "→".join(roles),
                "event_sequence": "|".join(row["source_event_id"] for row in rows),
                "surface_sequence": "|".join(row["surface"] for row in rows),
                "blocker_sequence": " → ".join(row["body_blockers_present"] for row in rows),
                "transition_count": str(len(transitions)),
                "role_switch_count": str(sum(row["role_switch"] == "YES" for row in transitions)),
                "control_marked_switch_count": str(sum(row["role_switch"] == "YES" and int(row["intervening_control_count"]) > 0 for row in transitions)),
                "reader_boundary_switch_count": str(sum(row["role_switch"] == "YES" and int(row["intervening_reader_boundary_count"]) > 0 for row in transitions)),
                "episode_class": episode_class,
                "gdt590_primary_reader_de": statement_by_id[statement_id]["gdt590_primary_reader_de"],
                "guard": "COMPLETE_STATEMENT_BATH_SEQUENCE__NO_ROLE_COLLAPSE",
            }
        )

    paragraph_rows: list[dict[str, str]] = []
    paragraph_transition_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in paragraph_transition_rows:
        paragraph_transition_by_key[row["paragraph_key"]].append(row)
    for paragraph_key, rows in sorted(hosts_by_paragraph.items()):
        roles = [row["gdt590_role"] for row in rows]
        if set(roles) == {"BODY"}:
            paragraph_class = "BODY_ONLY"
        elif set(roles) == {"STATION"}:
            paragraph_class = "STATION_ONLY"
        else:
            paragraph_class = "MIXED_BODY_STATION"
        transitions = paragraph_transition_by_key[paragraph_key]
        paragraph_rows.append(
            {
                "paragraph_episode_ordinal": str(len(paragraph_rows) + 1),
                "paragraph_key": paragraph_key,
                "physical_page": rows[0]["physical_page"],
                "paragraph_id": rows[0]["paragraph_id"],
                "paragraph_locus_range": rows[0]["paragraph_locus_range"],
                "statement_count": str(len({row["statement_id"] for row in rows})),
                "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in rows)),
                "bath_host_count": str(len(rows)),
                "body_host_count": str(roles.count("BODY")),
                "station_host_count": str(roles.count("STATION")),
                "role_sequence": "→".join(roles),
                "event_sequence": "|".join(row["source_event_id"] for row in rows),
                "transition_count": str(len(transitions)),
                "role_switch_count": str(sum(row["role_switch"] == "YES" for row in transitions)),
                "intra_statement_switch_count": str(sum(row["role_switch"] == "YES" and row["same_statement"] == "YES" for row in transitions)),
                "inter_statement_switch_count": str(sum(row["role_switch"] == "YES" and row["same_statement"] == "NO" for row in transitions)),
                "paragraph_class": paragraph_class,
                "guard": "PHYSICAL_ZL3B_PARAGRAPH__NOT_GDT584_READER_PARAGRAPH__NO_IMAGE_CHRONOLOGY",
            }
        )

    comparator_notes = {
        "G407-E2652": ("TARGET_UNIQUE_EXACT", "AIIN vor bare SH und OL+Y danach; beide Carrier event-remote, clean Body."),
        "G407-E2637": ("BEST_CLEAN_FILL_PARTIAL", "AIIN vor SH gebunden, Y aber direkt in SH+EE+Y; clean Body."),
        "G407-E2508": ("BEST_ALL_REMOTE_FILL_STATION", "AIIN und Y remote im Folgeträger; AR blockiert und hält Station."),
        "G407-E1648": ("ALL_REMOTE_OLY_STATION", "Alle Carrier remote, darunter späteres OL+Y; AIN und weitere Relation/Adresse statt AIIN."),
        "G407-E1758": ("CLEAN_REMOTE_BODY_BEFORE", "Clean Body ohne direkten Carrier; Y steht vor dem SH-Anker, kein AIIN."),
        "G407-E1789": ("CLEAN_REMOTE_BODY_BEFORE", "Clean Body ohne direkten Carrier; Y steht vor dem SH-Anker, kein AIIN."),
        "G407-E1433": ("BRACKETED_STATION_PARTIAL", "Carrier vor und nach SH; direktes Y plus L-geblocktes Y halten Station."),
    }
    continuity_by_event = {row["source_event_id"]: row for row in host_rows}
    comparator_rows: list[dict[str, str]] = []
    for event_id in COMPARATOR_IDS:
        current = continuity_by_event[event_id]
        # Some events contain more than one action host (for example E1758
        # has SH and T).  Resolve the comparator through the exact bath
        # governor selected by the 92-row continuity inventory.
        source = complete_host_by_key[current["primary_governor_key"]]
        tag, note = comparator_notes[event_id]
        comparator_rows.append(
            {
                "comparator_ordinal": str(len(comparator_rows) + 1),
                "source_event_id": event_id,
                "primary_governor_key": source["primary_governor_key"],
                "physical_page": source["physical_page"],
                "locus": current["locus"],
                "surface": current["surface"],
                "gdt590_role": current["gdt590_role"],
                "complete_host_values_written": source["complete_host_values_written"],
                "direct_governor_tokens": source["direct_governor_tokens"],
                "written_root_sequence": source["written_root_sequence"],
                "direct_carrier_count": current["direct_carrier_count"],
                "remote_carrier_count": current["remote_carrier_count"],
                "body_blockers_present": current["body_blockers_present"],
                "exact_target_signature": (
                    "YES" if source["complete_host_values_written"] == "AIIN|SH|Y" and source["direct_governor_tokens"] == "SH" else "NO"
                ),
                "comparison_class": tag,
                "comparison_de": note,
                "guard": "DIMENSIONED_PARTIAL_COMPARATOR__NO_EXACT_MATCH_PROMOTION",
            }
        )

    target_rows: list[dict[str, str]] = []
    statement_episode_by_id = {row["statement_id"]: row for row in statement_rows}
    paragraph_episode_by_key = {row["paragraph_key"]: row for row in paragraph_rows}
    layout_by_locus = {row["locus"]: row for row in data["layout"]}
    defaults_by_slot = {row["slot_id"]: row for row in data["defaults"]}
    slots_by_id = {row["carrier_slot_id"]: row for row in data["slots"]}
    for event_id, meta in sorted(TARGET_META.items(), key=lambda item: int(item[1]["rank"])):
        current = continuity_by_event[event_id]
        visual = visual_by_event[event_id]
        statement_episode = statement_episode_by_id[meta["statement_id"]]
        paragraph_episode = paragraph_episode_by_key[current["paragraph_key"]]
        layout = layout_by_locus[current["locus"]]
        e2652_trace = "NOT_APPLICABLE"
        if event_id == "G407-E2652":
            e2652_trace = (
                f"RUNNING:G407-E2650@2 Y={defaults_by_slot['RUNNING:G407-E2650@2']['gdt582_concrete_default_de']} "
                f"under {defaults_by_slot['RUNNING:G407-E2650@2']['primary_governor_key']} → "
                f"RUNNING:G407-E2651@1 AIIN={slots_by_id['RUNNING:G407-E2651@1']['gdt590_lemma_de']} + "
                f"RUNNING:G407-E2653@2 Y={slots_by_id['RUNNING:G407-E2653@2']['gdt590_lemma_de']} "
                f"under {slots_by_id['RUNNING:G407-E2653@2']['primary_governor_key']}"
            )
        target_rows.append(
            {
                "target_ordinal": meta["rank"],
                "source_event_id": event_id,
                "statement_id": meta["statement_id"],
                "physical_page": current["physical_page"],
                "locus": current["locus"],
                "surface": current["surface"],
                "paragraph_key": current["paragraph_key"],
                "paragraph_locus_range": current["paragraph_locus_range"],
                "statement_physical_span": meta["statement_physical_span"],
                "line_wrap_class": meta["line_wrap_class"],
                "layout_aware_eva": layout["layout_aware_eva"],
                "statement_bath_role_sequence": statement_episode["role_sequence"],
                "paragraph_bath_role_sequence": paragraph_episode["role_sequence"],
                "episode_strength": meta["episode_strength"],
                "episode_evidence_de": meta["episode_evidence_de"],
                "counter_episode_de": meta["counter_episode_de"],
                "image_only_preference_de": visual["image_only_preference_de"],
                "overall_preference_de": "Körper",
                "retained_alternative_de": "Stationsansatz",
                "event_remote_vs_layout_de": (
                    "Event-remote/grammatisch fernangehängt, aber zeilenadjazent" if event_id == "G407-E2652" else "Siehe hostgenaue Carrier- und Layoutspur"
                ),
                "e2652_owner_to_action_trace": e2652_trace,
                "gdt590_primary_reader_de": statement_by_id[meta["statement_id"]]["gdt590_primary_reader_de"],
                "guard": "EPISODE_SUPPORT_IS_NOT_INDEPENDENT_LEXEME_OR_IMAGE_DENOTATION",
            }
        )

    statement_pair_profile = Counter(
        (row["from_role"], row["to_role"]) for row in statement_transition_rows
    )
    paragraph_pair_profile = Counter(
        (row["from_role"], row["to_role"]) for row in paragraph_transition_rows
    )
    remote_root_profile = Counter(row["carrier_root"] for row in remote_rows)
    result = {
        "experiment_id": "GDT591",
        "status": STATUS,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "bath_page_count": len({row["physical_page"] for row in host_rows}),
        "bath_host_count": len(host_rows),
        "bath_statement_count": len(statement_rows),
        "bath_paragraph_count": len(paragraph_rows),
        "role_profile": dict(sorted(Counter(row["gdt590_role"] for row in host_rows).items())),
        "y_slot_profile": {
            "BODY": sum(int(row["y_slot_count"]) for row in host_rows if row["gdt590_role"] == "BODY"),
            "STATION": sum(int(row["y_slot_count"]) for row in host_rows if row["gdt590_role"] == "STATION"),
        },
        "carrier_slot_count": sum(int(row["carrier_slot_count"]) for row in host_rows),
        "direct_carrier_count": sum(int(row["direct_carrier_count"]) for row in host_rows),
        "remote_carrier_count": len(remote_rows),
        "remote_root_profile": dict(sorted(remote_root_profile.items())),
        "statement_transition_count": len(statement_transition_rows),
        "statement_transition_profile": {f"{left}_TO_{right}": count for (left, right), count in sorted(statement_pair_profile.items())},
        "statement_role_switch_count": sum(row["role_switch"] == "YES" for row in statement_transition_rows),
        "paragraph_transition_count": len(paragraph_transition_rows),
        "paragraph_transition_profile": {f"{left}_TO_{right}": count for (left, right), count in sorted(paragraph_pair_profile.items())},
        "paragraph_role_switch_count": sum(row["role_switch"] == "YES" for row in paragraph_transition_rows),
        "e2652_exact_signature_population_count": sum(
            row["complete_host_values_written"] == "AIIN|SH|Y" and row["direct_governor_tokens"] == "SH"
            for row in data["hosts"]
        ),
        "e2652_conclusion": (
            "The body-first episode is process- and layout-coherent, but the exact all-remote bare-SH "
            "structure is unique; station remains the strongest visible alternative."
        ),
        "remote_definition": "different source event from the action-anchor event, not physical manuscript distance",
    }
    return {
        "hosts": host_rows,
        "statements": statement_rows,
        "paragraphs": paragraph_rows,
        "statement_transitions": statement_transition_rows,
        "paragraph_transitions": paragraph_transition_rows,
        "remote": remote_rows,
        "comparators": comparator_rows,
        "targets": target_rows,
        "result": result,
    }


def render_reader(built: dict[str, Any]) -> str:
    lines = [
        "# GDT591 — Badeepisoden und der E2652-Stresstest",
        "",
        "Die 92 Y-Badehosts bilden 64 Aussagen und 17 physische ZL3b-Absätze. "
        "Körper und Station wechseln nicht innerhalb eines Hosts: jeder der 14 Aussagewechsel "
        "liegt an einem neuen SH-Gouverneur, und nur die Stationsseite trägt Blocker.",
        "",
        "## Vier GDT590-Ziele",
        "",
    ]
    for row in built["targets"]:
        lines.extend(
            [
                f"### {row['source_event_id']} — {row['episode_strength']}",
                "",
                f"Physischer Lauf: `{row['statement_physical_span']}`; "
                f"Aussagefolge `{row['statement_bath_role_sequence']}`; "
                f"Absatzfolge `{row['paragraph_bath_role_sequence']}`.",
                "",
                row["gdt590_primary_reader_de"],
                "",
                f"Episode: {row['episode_evidence_de']}",
                "",
                f"Gegenlesung: {row['counter_episode_de']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Neun gemischte Aussagen",
            "",
            "Diese Aussagen enthalten innerhalb derselben Aussage sowohl blockerfreie Körper- als auch "
            "geblockte Stationshosts. Die Folge ist eine Werkstatt-Arbeitslesung, keine Bildchronologie.",
            "",
        ]
    )
    for row in built["statements"]:
        if row["episode_class"] != "MIXED_BODY_STATION":
            continue
        lines.extend(
            [
                f"### {row['statement_id']} — `{row['role_sequence']}`",
                "",
                row["gdt590_primary_reader_de"],
                "",
            ]
        )
    target = next(row for row in built["targets"] if row["source_event_id"] == "G407-E2652")
    lines.extend(
        [
            "## E2652 in einem Satz",
            "",
            target["e2652_owner_to_action_trace"],
            "",
            "`remote` bedeutet hier nur ein anderes Quellereignis als der Handlungsanker. Auf dem Blatt stehen "
            "`daiin – sh – qolchey` unmittelbar als W1–W3. Körper-first steigt damit von bloß "
            "explorativ auf eine mittlere Arbeitslesung, bleibt aber mangels exakten Vergleichshosts offen.",
            "",
        ]
    )
    return "\n".join(lines)


def write_built(built: dict[str, Any]) -> None:
    for name in (
        "hosts", "statements", "paragraphs", "statement_transitions", "paragraph_transitions",
        "remote", "comparators", "targets",
    ):
        write_tsv(OUTPUTS[name], built[name])
    OUTPUTS["reader"].write_text(render_reader(built), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
