#!/usr/bin/env python3
"""Build the GDT590 body/station adjudication over the fixed GDT589 base."""

from __future__ import annotations

import csv
import hashlib
import json
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


EXP = ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication"
ART = EXP / "artifacts"
STATUS = (
    "PASS_FOUR_BATH_FORKS_BODY_DEFAULT__52_OF_92_CLEAN_BODY__"
    "40_BLOCKED_STATION__FOUR_READER_PATCHES"
)

ADMITTED_PAGES = frozenset(
    {
        "f1r", "f4r", "f10r", "f11r", "f13r", "f17r", "f18r", "f20v",
        "f24v", "f31r", "f55v", "f56r", "f66r", "f67r2", "f68r1",
        "f69v", "f70v", "f71v", "f72r", "f75r", "f76r", "f77r",
        "f81r", "f81v", "f82r", "f83r", "f88r", "f88v", "f89r", "f95v",
    }
)

INPUTS = {
    "hosts": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_953_complete_host_replay.tsv",
    "slots": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_1243_slot_replay.tsv",
    "body_guard": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_361_biological_y_host_guard.tsv",
    "forks": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_4_clean_bath_body_forks.tsv",
    "bath_packets": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_74_special_packet_replay.tsv",
    "statements": ROOT / "experiments/yolo/gdt589_full_host_carrier_intake_replay/artifacts/gdt589_793_count_overlay_statement_reader.tsv",
    "running_events": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_5122_running_event_edition.tsv",
    "transcription": ROOT / "transcription/voynich_zl3b_lines.tsv",
    "layout_units": ROOT / "transcription/zl3b_layout_aware_reading_units.tsv",
    "exact_annotations": ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv",
    "image_sources": EXP / "sources/gdt590_manual_image_sources.tsv",
    "f82r_paragraphs": ROOT / "gdt242_f82r_paragraph_coordinate.tsv",
}

OUTPUTS = {
    "adjudications": ART / "gdt590_4_bath_fork_adjudications.tsv",
    "bath_analogs": ART / "gdt590_92_bath_y_analogy_matrix.tsv",
    "bath_packets": ART / "gdt590_11_bath_fill_packet_matrix.tsv",
    "body_guard": ART / "gdt590_361_biological_y_host_guard.tsv",
    "slots": ART / "gdt590_1243_adjudicated_slot_replay.tsv",
    "statements": ART / "gdt590_793_body_adjudicated_statement_reader.tsv",
    "visual": ART / "gdt590_4_host_visual_contexts.tsv",
    "reader": ART / "GDT590_FOUR_BATH_READER.md",
    "result": ART / "gdt590_result.json",
    "validation": ART / "gdt590_validation.json",
}

TARGETS: dict[str, dict[str, str]] = {
    "G407-E2404": {
        "rank": "1",
        "host_key": "ACTION:G407-E2404@1:SH",
        "statement_id": "G407-S312",
        "page": "f77r",
        "locus": "f77r.10",
        "surface": "shey",
        "recipe": "SH+E+Y",
        "paragraph_id": "P1",
        "paragraph_line_ordinal": "2",
        "old_clause_de": "Halte den Stationsansatz im Bad bei der angegebenen Füllung auf Grad I.",
        "body_clause_de": "Halte den Körper im Bad bei der angegebenen Füllung auf Grad I.",
        "strength": "MEDIUM_HIGH",
        "sequence_evidence_de": (
            "Der Satz bereitet zunächst einen Stationsansatz vor und behandelt den Ansatz vom Ausgang; "
            "der blockerfreie shey-Host kann danach zum Badeobjekt Körper wechseln, ohne einen späteren "
            "Rückverweis zu beschädigen."
        ),
        "analogy_evidence_de": (
            "shey hat 19 blockerfreie Körperanaloga und zwei geblockte Stationsanaloga; E2404 ist die "
            "einzige blockerfreie station-first Ausnahme dieser Oberfläche."
        ),
        "closest_pair_de": "SH+E+Y: 20 vorhandene Körperhosts, zwei geblockte Stationshosts, plus diese alte Ausnahme.",
        "statement_carrier_multiplicity": "Y×2; AIIN×1",
        "target_word_position": "3/10",
        "y_carrier_event_id": "G407-E2404",
        "y_carrier_surface": "shey",
        "y_carrier_word_position": "3/10",
        "image_only_preference": "STATION_SLIGHT_MEDIUM",
        "image_alternative": "BODY",
        "image_evidence_de": (
            "Das Zielwort steht unter dem dominanten oberen Rohr- und Auslasssystem; die menschlichen "
            "Endfiguren bleiben Teil desselben Feldes, aber kein Zeiger bindet das Wort an eine Figur."
        ),
    },
    "G407-E2637": {
        "rank": "2",
        "host_key": "ACTION:G407-E2637@1:SH",
        "statement_id": "G407-S382",
        "page": "f77r",
        "locus": "f77r.39",
        "surface": "cheey",
        "recipe": "SH+EE+Y",
        "paragraph_id": "P3",
        "paragraph_line_ordinal": "2",
        "old_clause_de": "Halte den Stationsansatz im Bad bei der angegebenen Füllung auf Grad II.",
        "body_clause_de": "Halte den Körper im Bad bei der angegebenen Füllung auf Grad II.",
        "strength": "HIGH",
        "sequence_evidence_de": (
            "Der erste blockerfreie Badehost kann Körper sein; später nennt der Satz den Stationsansatz "
            "unter Zuführung und Verbindung ausdrücklich neu. Das nachfolgende L+SH+EE+Y bildet im selben "
            "Satz den geblockten Stationskontrast."
        ),
        "analogy_evidence_de": (
            "cheey hat elf blockerfreie Körperanaloga und vier geblockte Stationsanaloga; E2637 und E3182 "
            "waren seine einzigen blockerfreien station-first Ausnahmen."
        ),
        "closest_pair_de": "E2625 auf f77r.37 ist clean cheey=Körper; das spätere lsheey im selben Satz ist L-geblockt=Stationsansatz.",
        "statement_carrier_multiplicity": "Y×4; AIIN×2",
        "target_word_position": "2/7",
        "y_carrier_event_id": "G407-E2637",
        "y_carrier_surface": "cheey",
        "y_carrier_word_position": "2/7",
        "image_only_preference": "BODY_SLIGHT",
        "image_alternative": "STATION",
        "image_evidence_de": (
            "Das Zielwort liegt im unteren Prosafeld unmittelbar neben einer menschlichen Figur und einem "
            "dunkelblauen Rundgefäß; Körper ist bildlich leicht näher, ohne exklusiven Wortbesitzer."
        ),
    },
    "G407-E2652": {
        "rank": "3",
        "host_key": "ACTION:G407-E2652@1:SH",
        "statement_id": "G407-S385",
        "page": "f77r",
        "locus": "f77r.41",
        "surface": "sh",
        "recipe": "SH",
        "paragraph_id": "P3",
        "paragraph_line_ordinal": "4",
        "old_clause_de": "Halte den Stationsansatz im Bad bei der angegebenen Füllung.",
        "body_clause_de": "Halte den Körper im Bad bei der angegebenen Füllung.",
        "strength": "MEDIUM_EXPLORATORY",
        "sequence_evidence_de": (
            "AIIN steht vor dem bloßen SH und Y erst im Fortsetzungsträger danach. Der vorherige Owner-Y ist "
            "Stationsansatz; der Gouverneurwechsel erlaubt Körper, macht die Stationsalternative hier aber "
            "stärker als an den drei anderen Stellen."
        ),
        "analogy_evidence_de": (
            "Bloßes SH ist im Y-Badbestand einzigartig und hat kein exaktes Formminimalpaar. Die allgemeine "
            "blockerfreie Y+AIIN-Komposition spricht dennoch für Körper plus Badfüllung."
        ),
        "closest_pair_de": "Der vorausgehende AIIN-only-Badehost hält nur die Badfüllung; das zusätzliche blockerfreie Y liefert das Badeobjekt.",
        "statement_carrier_multiplicity": "Y×2; AIIN×1",
        "target_word_position": "2/10",
        "y_carrier_event_id": "G407-E2653",
        "y_carrier_surface": "qolchey",
        "y_carrier_word_position": "3/10",
        "image_only_preference": "STATION_SLIGHT_OPEN",
        "image_alternative": "BODY",
        "image_evidence_de": (
            "Das bloße SH steht an Wort 2; sein fortgesetzter Y-Träger qolchey an Wort 3 liegt näher am "
            "großen Auslass- oder Beckenkopf. Das macht die Stationslesung bildlich knapp stärker."
        ),
    },
    "G407-E3182": {
        "rank": "4",
        "host_key": "ACTION:G407-E3182@1:SH",
        "statement_id": "G407-S495",
        "page": "f82r",
        "locus": "f82r.1",
        "surface": "cheey",
        "recipe": "SH+EE+Y",
        "paragraph_id": "P1",
        "paragraph_line_ordinal": "1",
        "old_clause_de": "Halte den Stationsansatz im Bad bei der angegebenen Füllung auf Grad II.",
        "body_clause_de": "Halte den Körper im Bad bei der angegebenen Füllung auf Grad II.",
        "strength": "VERY_HIGH",
        "sequence_evidence_de": (
            "Unmittelbar davor wird eine Becken- oder Körpereinheit auf Grad II vorbereitet; unmittelbar "
            "danach folgt bereits der blockerfreie Körperbad-Host shey auf Grad I. Körper-first ergibt eine "
            "zusammenhängende zweistufige Badfolge."
        ),
        "analogy_evidence_de": (
            "Auf f82r stehen weitere blockerfreie cheey-Hosts als Körper, während L-geblocktes cheey Station "
            "bleibt. E3182 ist zusammen mit E2637 die einzige alte blockerfreie cheey-Ausnahme."
        ),
        "closest_pair_de": "Direkt folgendes E3184 shey=Körper; fünf weitere saubere cheey auf f82r=Körper, L+cheey auf f82r.13=Station.",
        "statement_carrier_multiplicity": "Y×5; AIIN×2",
        "target_word_position": "6/8",
        "y_carrier_event_id": "G407-E3182",
        "y_carrier_surface": "cheey",
        "y_carrier_word_position": "6/8",
        "image_only_preference": "STATION_SLIGHT",
        "image_alternative": "BODY",
        "image_evidence_de": (
            "Nach dem sichtbaren Zeilenbruch hinter Wort 4 liegt cheey an Wort 6 näher am zentralen "
            "Apparat; das folgende shey an Wort 8 liegt näher bei Hand, Frau und blauem Becken. Bildlich "
            "ist daher Station→Füllung→Körper möglich."
        ),
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def split_plus(value: str) -> list[str]:
    return [part for part in value.split("+") if part]


def split_pipe(value: str) -> list[str]:
    if not value or value == "NONE":
        return []
    return [part for part in value.split("|") if part]


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


def read_sealed_derived_tsv(
    path: Path, *, selector: str, allowed: Iterable[str]
) -> list[dict[str, str]]:
    """Read an upstream manifest-sealed derived TSV that contains quoted newlines.

    GuardedTSV intentionally reads one physical line at a time and therefore cannot
    materialize this already f84-free GDT589 reader. Fail closed if its upstream
    sealed-data guarantee or admitted-page population ever drifts.
    """
    rows = read_tsv(path)
    allowed_values = set(allowed)
    values = {row[selector] for row in rows}
    if any(value.lower().startswith("f84") for value in values):
        raise RuntimeError(f"sealed selector leaked into derived input: {path}")
    if not values <= allowed_values:
        raise RuntimeError(f"unexpected selector values in derived input: {sorted(values - allowed_values)}")
    return rows


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f"refusing to write empty TSV: {path}")
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: str(row.get(key, "")) for key in fieldnames})


def _paragraph_map(lines: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in lines:
        if row["kind"] == "P":
            by_page[row["page"]].append(row)
    result: dict[str, dict[str, str]] = {}
    for page, page_rows in by_page.items():
        page_rows.sort(key=lambda row: int(row["line_number"]))
        paragraph_ordinal = 0
        paragraph_line = 0
        start_line = 0
        staged: list[tuple[dict[str, str], int, int]] = []
        for row in page_rows:
            if row["paragraph_start"] == "1":
                paragraph_ordinal += 1
                paragraph_line = 0
                start_line = int(row["line_number"])
            paragraph_line += 1
            staged.append((row, paragraph_ordinal, paragraph_line))
            if row["paragraph_end"] == "1":
                end_line = int(row["line_number"])
                for staged_row, staged_paragraph, staged_line in staged:
                    if staged_paragraph == paragraph_ordinal:
                        result[staged_row["locus"]] = {
                            "paragraph_id": f"P{staged_paragraph}",
                            "paragraph_line_ordinal": str(staged_line),
                            "paragraph_locus_range": f"{page}.{start_line}–.{end_line}",
                        }
                staged = []
    return result


def _new_y_lemma(row: dict[str, str]) -> tuple[str, str]:
    written_roots = split_plus(row["written_root_sequence"])
    roots = set(written_roots)
    blockers = row["body_blockers_present"]
    if (
        row["gdt584_rule_id"] == "SH_BIO_BATHE"
        and "Y" in roots
        and roots <= {"Y", "AIIN"}
        and blockers == "NONE"
    ):
        return "|".join("Körper" for root in written_roots if root == "Y"), "CLEAN_BATH_Y_WITH_OPTIONAL_FILL"
    return row["portable_y_lemma_sequence"], "GDT589_RETAINED"


def _noun_forms(lemma: str) -> tuple[str, str]:
    if lemma == "Körper":
        return "den Körper", "des Körpers"
    if lemma == "Stationsansatz":
        return "den Stationsansatz", "des Stationsansatzes"
    if lemma == "Strom":
        return "den Strom", "des Stroms"
    raise RuntimeError(f"unsupported patched Y lemma: {lemma}")


def load_inputs() -> dict[str, list[dict[str, str]]]:
    data = {
        "hosts": guarded_rows(INPUTS["hosts"], selector="physical_page", allowed=ADMITTED_PAGES),
        "slots": guarded_rows(INPUTS["slots"], selector="physical_page", allowed=ADMITTED_PAGES),
        "body_guard": guarded_rows(INPUTS["body_guard"], selector="physical_page", allowed=ADMITTED_PAGES),
        "forks": guarded_rows(INPUTS["forks"], selector="physical_page", allowed={"f77r", "f82r"}),
        "bath_packets": guarded_rows(INPUTS["bath_packets"], selector="physical_page", allowed=ADMITTED_PAGES),
        "statements": read_sealed_derived_tsv(
            INPUTS["statements"], selector="physical_page", allowed=ADMITTED_PAGES
        ),
        "running_events": guarded_rows(INPUTS["running_events"], selector="physical_page", allowed=ADMITTED_PAGES),
        "transcription": guarded_rows(INPUTS["transcription"], selector="page", allowed={"f77r", "f82r"}),
        "layout_units": guarded_rows(INPUTS["layout_units"], selector="page", allowed={"f77r", "f82r"}),
        "exact_annotations": guarded_rows(INPUTS["exact_annotations"], selector="page", allowed={"f77r", "f82r"}),
        "image_sources": guarded_rows(INPUTS["image_sources"], selector="physical_page", allowed={"f77r", "f82r"}),
        "f82r_paragraphs": guarded_rows(INPUTS["f82r_paragraphs"], selector="page", allowed={"f82r"}),
    }
    return data


def build(data: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    event_by_id = {row["global_running_event_id"]: row for row in data["running_events"]}
    fork_by_event = {row["source_event_or_card_id"]: row for row in data["forks"]}
    statement_by_id = {row["statement_id"]: row for row in data["statements"]}
    paragraph_by_locus = _paragraph_map(data["transcription"])
    line_by_locus = {row["locus"]: row for row in data["transcription"]}
    f82r_coordinate_by_locus = {row["locus"]: row for row in data["f82r_paragraphs"]}
    if (
        f82r_coordinate_by_locus.get("f82r.1", {}).get("paragraph_id") != "P1"
        or f82r_coordinate_by_locus.get("f82r.1", {}).get("paragraph_line_ordinal") != "1"
    ):
        raise RuntimeError("f82r.1 is no longer paragraph P1 line 1")

    slots_by_host: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["slots"]:
        slots_by_host[row["primary_governor_key"]].append(row)
    for rows in slots_by_host.values():
        rows.sort(key=lambda row: int(row["written_carrier_ordinal"]))

    updated_guard: list[dict[str, str]] = []
    for row in data["body_guard"]:
        new_lemma, route = _new_y_lemma(row)
        changed = new_lemma != row["portable_y_lemma_sequence"]
        updated_guard.append(
            {
                **row,
                "gdt590_y_lemma_sequence": new_lemma,
                "gdt590_body_station_route": route,
                "gdt590_changed": "YES" if changed else "NO",
                "gdt590_retained_alternative_de": "Stationsansatz" if changed else "NOT_APPLICABLE",
                "gdt590_guard": "AIIN_IS_BATH_FILL_COMPANION__NOT_OBJECT_CLASS_BLOCKER" if changed else "GDT589_GUARD_RETAINED",
            }
        )
    guard_by_host = {row["primary_governor_key"]: row for row in updated_guard}

    bath_analogs: list[dict[str, str]] = []
    for row in updated_guard:
        if row["gdt584_rule_id"] != "SH_BIO_BATHE" or "Y" not in split_plus(row["written_root_sequence"]):
            continue
        event = event_by_id[row["source_event_or_card_id"]]
        clean = row["body_blockers_present"] == "NONE"
        roots = set(split_plus(row["written_root_sequence"]))
        if clean and roots == {"Y"}:
            analogy_class = "CLEAN_Y_BODY_EXISTING"
        elif clean and roots == {"Y", "AIIN"}:
            analogy_class = "CLEAN_Y_PLUS_FILL_BODY_GDT590"
        else:
            analogy_class = "BLOCKED_Y_STATION"
        bath_analogs.append(
            {
                "analogy_ordinal": str(len(bath_analogs) + 1),
                "primary_governor_key": row["primary_governor_key"],
                "source_event_id": row["source_event_or_card_id"],
                "statement_id": row["statement_or_record_id"],
                "physical_page": row["physical_page"],
                "locus": event["locus"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "written_root_sequence": row["written_root_sequence"],
                "body_blockers_present": row["body_blockers_present"],
                "gdt589_y_lemma_sequence": row["portable_y_lemma_sequence"],
                "gdt590_y_lemma_sequence": row["gdt590_y_lemma_sequence"],
                "analogy_class": analogy_class,
                "gdt590_changed": row["gdt590_changed"],
                "guard": "COMPLETE_HOST_VALUES__NO_CONTAINED_SUBSTRING_SEGMENTATION",
            }
        )

    adjudications: list[dict[str, str]] = []
    for event_id, target in sorted(TARGETS.items(), key=lambda item: int(item[1]["rank"])):
        fork = fork_by_event[event_id]
        event = event_by_id[event_id]
        paragraph = paragraph_by_locus[event["locus"]]
        host_slots = slots_by_host[target["host_key"]]
        statement = statement_by_id[target["statement_id"]]
        if statement["gdt589_primary_reader_de"].count(target["old_clause_de"]) != 1:
            raise RuntimeError(f"target clause is not unique in {target['statement_id']}")
        adjudications.append(
            {
                "adjudication_ordinal": target["rank"],
                "primary_governor_key": target["host_key"],
                "source_event_id": event_id,
                "statement_id": target["statement_id"],
                "physical_page": target["page"],
                "locus": event["locus"],
                "paragraph_id": paragraph["paragraph_id"],
                "paragraph_line_ordinal": paragraph["paragraph_line_ordinal"],
                "paragraph_locus_range": paragraph["paragraph_locus_range"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "written_root_sequence": fork["written_root_sequence"],
                "complete_host_values_written": fork["complete_host_values_written"],
                "carrier_slot_ids": "|".join(row["carrier_slot_id"] for row in host_slots),
                "carrier_attachment_pattern": " | ".join(
                    f"{row['written_carrier_ordinal']}:{row['carrier_slot_id']}={row['carrier_root']}"
                    for row in host_slots
                ),
                "body_blockers_present": fork["body_blockers_present"],
                "owner_de": statement["owner_id"],
                "statement_surface_sequence": statement["surface_sequence"],
                "statement_carrier_multiplicity": target["statement_carrier_multiplicity"],
                "sequence_evidence_de": target["sequence_evidence_de"],
                "analogy_evidence_de": target["analogy_evidence_de"],
                "closest_minimal_pair_de": target["closest_pair_de"],
                "image_only_preference": target["image_only_preference"],
                "image_alternative": target["image_alternative"],
                "image_evidence_de": target["image_evidence_de"],
                "image_supports_overall_body_default": (
                    "YES" if target["image_only_preference"] == "BODY_SLIGHT" else "NO"
                ),
                "gdt589_station_clause_de": target["old_clause_de"],
                "gdt590_body_clause_de": target["body_clause_de"],
                "retained_station_alternative_de": target["old_clause_de"],
                "working_strength": target["strength"],
                "gdt590_decision": "BODY_DEFAULT__STATION_RETAINED_AS_VISIBLE_ALTERNATIVE",
                "guard": "OWNER_INTERNAL__NO_PARAGRAPH_BOUNDARY__NO_REPEAT_HOST__NO_NEW_PAGE",
            }
        )

    updated_slots: list[dict[str, str]] = []
    target_hosts = {target["host_key"] for target in TARGETS.values()}
    for row in data["slots"]:
        changed = row["primary_governor_key"] in target_hosts and row["carrier_root"] == "Y"
        lemma = "Körper" if changed else row["expected_lemma_de"]
        if changed:
            object_form, genitive_form = _noun_forms(lemma)
        else:
            object_form = row["expected_object_form_de"]
            genitive_form = row["expected_genitive_form_de"]
        updated_slots.append(
            {
                **row,
                "gdt590_context_family": row["expected_context_family"],
                "gdt590_lemma_de": lemma,
                "gdt590_object_form_de": object_form,
                "gdt590_genitive_form_de": genitive_form,
                "gdt590_changed": "YES" if changed else "NO",
                "gdt590_decision_source": "CLEAN_BATH_Y_WITH_AIIN_FILL" if changed else "GDT589_RETAINED",
                "gdt590_retained_alternative_de": "Stationsansatz" if changed else "NOT_APPLICABLE",
                "gdt590_guard": "AIIN_RETAINS_BADFÜLLUNG__Y_SELECTS_BODY" if changed else "GDT589_SLOT_RETAINED",
            }
        )

    target_by_statement = {target["statement_id"]: (event_id, target) for event_id, target in TARGETS.items()}
    updated_statements: list[dict[str, str]] = []
    for row in data["statements"]:
        target_item = target_by_statement.get(row["statement_id"])
        if target_item:
            event_id, target = target_item
            primary = row["gdt589_primary_reader_de"].replace(
                target["old_clause_de"], target["body_clause_de"], 1
            )
            updated_statements.append(
                {
                    **row,
                    "gdt590_primary_reader_de": primary,
                    "gdt590_body_adjudication_count": "1",
                    "gdt590_adjudicated_host_keys": target["host_key"],
                    "gdt590_retained_station_clause_de": target["old_clause_de"],
                    "gdt590_reader_changed": "YES",
                    "gdt590_guard": f"BODY_DEFAULT_AT_{event_id}__STATION_ALTERNATIVE_RETAINED",
                }
            )
        else:
            updated_statements.append(
                {
                    **row,
                    "gdt590_primary_reader_de": row["gdt589_primary_reader_de"],
                    "gdt590_body_adjudication_count": "0",
                    "gdt590_adjudicated_host_keys": "NONE",
                    "gdt590_retained_station_clause_de": "NOT_APPLICABLE",
                    "gdt590_reader_changed": "NO",
                    "gdt590_guard": "GDT589_READER_BYTE_RETAINED",
                }
            )

    fork_host_keys = {target["host_key"] for target in TARGETS.values()}
    packet_rows = [
        row for row in data["bath_packets"]
        if row["packet_rule_id"] == "BIOLOGICAL_BATH_FILL"
    ]
    updated_packets: list[dict[str, str]] = []
    for row in packet_rows:
        changed = row["primary_governor_key"] in fork_host_keys
        ordered = row["ordered_written_slot_lemmas_de"]
        sentence = row["sentence_layer_de"]
        composition = row["packet_composition_elements_de"]
        if changed:
            ordered = ordered.replace("Y=Stationsansatz", "Y=Körper")
            target = TARGETS[row["source_event_or_card_id"]]
            sentence = sentence.replace(target["old_clause_de"].rstrip("."), target["body_clause_de"].rstrip("."), 1)
            composition = composition.replace("Stationsansatz", "Körper")
        roots = set(split_plus(row["written_root_sequence"]))
        blockers = guard_by_host.get(row["primary_governor_key"], {}).get("body_blockers_present", "NONE")
        if roots == {"AIIN"}:
            packet_class = "FILL_ONLY"
        elif changed:
            packet_class = "CLEAN_BODY_PLUS_FILL"
        else:
            packet_class = "BLOCKED_STATION_PLUS_FILL"
        updated_packets.append(
            {
                **row,
                "gdt590_ordered_written_slot_lemmas_de": ordered,
                "gdt590_packet_composition_elements_de": composition,
                "gdt590_sentence_layer_de": sentence,
                "body_blockers_present": blockers,
                "gdt590_packet_class": packet_class,
                "gdt590_changed": "YES" if changed else "NO",
                "gdt590_guard": "BODY_AND_FILL_COMPOSE__AIIN_DOES_NOT_RECLASSIFY_Y" if changed else "GDT589_PACKET_RETAINED",
            }
        )

    image_by_page = {row["physical_page"]: row for row in data["image_sources"]}
    layout_by_locus = {row["locus"]: row for row in data["layout_units"]}
    exact_annotation_loci = {row["locus"] for row in data["exact_annotations"]}
    visual_rows: list[dict[str, str]] = []
    for event_id, target in sorted(TARGETS.items(), key=lambda item: int(item[1]["rank"])):
        page = target["page"]
        line = line_by_locus[target["locus"]]
        layout = layout_by_locus[target["locus"]]
        image = image_by_page[page]
        if line["kind"] != "P":
            raise RuntimeError(f"target is no longer prose: {event_id} {target['locus']}")
        if target["locus"] in exact_annotation_loci:
            raise RuntimeError(f"target unexpectedly acquired an exact graphical annotation: {event_id}")
        if event_id == "G407-E3182" and "4" not in split_plus(
            layout["extreme_gap_positions"].replace(",", "+")
        ):
            raise RuntimeError("f82r.1 layout interruption after word 4 is missing")
        if event_id == "G407-E3182":
            layout_trace = "S1=W1–W4|LAYOUT_INTERRUPTION|S2=W5–W8;TARGET=S2/W2"
        elif event_id == "G407-E2652":
            layout_trace = "S1=W1–W10;ACTION=S1/W2;Y=S1/W3"
        else:
            action_word = target["target_word_position"].split("/", 1)[0]
            layout_trace = f"S1=W1–W{line['token_count']};TARGET=S1/W{action_word}"
        host_slots = slots_by_host[target["host_key"]]
        y_slot = next(row for row in host_slots if row["carrier_root"] == "Y")
        aiin_slot = next(row for row in host_slots if row["carrier_root"] == "AIIN")
        aiin_event_id = aiin_slot["carrier_slot_id"].split(":", 1)[1].split("@", 1)[0]
        aiin_event = event_by_id[aiin_event_id]
        aiin_word_position = {
            "G407-E2404": "4/10",
            "G407-E2637": "1/7",
            "G407-E2652": "1/10",
            "G407-E3182": "7/8",
        }[event_id]
        visual_rows.append(
            {
                "visual_context_id": f"GDT590-VH{target['rank'].zfill(2)}",
                "primary_governor_key": target["host_key"],
                "source_event_id": event_id,
                "y_carrier_event_id": target["y_carrier_event_id"],
                "y_carrier_slot_id": y_slot["carrier_slot_id"],
                "aiin_carrier_event_id": aiin_event_id,
                "statement_id": target["statement_id"],
                "physical_page": page,
                "locus": target["locus"],
                "paragraph_id": target["paragraph_id"],
                "paragraph_line_ordinal": target["paragraph_line_ordinal"],
                "paragraph_locus_range": paragraph_by_locus[target["locus"]]["paragraph_locus_range"],
                "line_eva_clean": line["eva_clean"],
                "line_word_count": line["token_count"],
                "action_surface": target["surface"],
                "action_word_ordinal_in_line": target["target_word_position"].split("/", 1)[0],
                "y_carrier_surface": target["y_carrier_surface"],
                "y_word_ordinal_in_line": target["y_carrier_word_position"].split("/", 1)[0],
                "aiin_surface": aiin_event["surface"],
                "aiin_word_ordinal_in_line": aiin_word_position.split("/", 1)[0],
                "layout_segment_trace": layout_trace,
                "source_text_kind": line["kind"],
                "exact_graphical_annotation_match": "NO",
                "visual_unit_class": "PROSE_NOT_GRAPHICAL_LABEL",
                "visual_owner_status": "NO_EXACT_WORD_OR_OBJECT_OWNER",
                "canvas_id": image["canvas_id"],
                "review_image_url": image["image_url"],
                "review_image_sha256": image["sha256"],
                "pixel_dimensions": f"{image['pixel_width']}×{image['pixel_height']}",
                "image_only_preference_de": (
                    "Körper" if target["image_only_preference"] == "BODY_SLIGHT" else "Stationsansatz"
                ),
                "image_only_alternative_de": (
                    "Stationsansatz" if target["image_alternative"] == "STATION" else "Körper"
                ),
                "image_only_strength": target["image_only_preference"],
                "exact_visual_evidence_de": target["image_evidence_de"],
                "overall_preference_de": "Körper",
                "overall_working_strength": target["strength"],
                "overall_decision": "BODY_DEFAULT__STATION_RETAINED_AS_VISIBLE_ALTERNATIVE",
                "guard": (
                    "PROSE_POSITION_ONLY__NO_EXACT_VISUAL_OWNER__"
                    "IMAGE_ONLY_PREFERENCE_IS_NONOVERRIDING__NO_NEW_PAGE"
                ),
            }
        )

    body_profile = Counter(
        row["gdt590_lemma_de"]
        for row in updated_slots
        if row["register"] == "BIOLOGICAL" and row["carrier_root"] == "Y"
    )
    analogy_profile = Counter(row["analogy_class"] for row in bath_analogs)
    packet_profile = Counter(row["gdt590_packet_class"] for row in updated_packets)
    surface_profile: dict[str, dict[str, int]] = {}
    for surface in ("shey", "cheey"):
        subset = [row for row in bath_analogs if row["surface"] == surface]
        surface_profile[surface] = {
            "clean_prior_body": sum(
                row["body_blockers_present"] == "NONE"
                and set(split_pipe(row["gdt589_y_lemma_sequence"])) == {"Körper"}
                for row in subset
            ),
            "clean_promoted": sum(row["gdt590_changed"] == "YES" for row in subset),
            "blocked_station": sum(row["body_blockers_present"] != "NONE" for row in subset),
        }

    result = {
        "experiment_id": "GDT590",
        "status": STATUS,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "admitted_page_count": len(ADMITTED_PAGES),
        "target_host_count": len(adjudications),
        "target_statement_count": sum(row["gdt590_reader_changed"] == "YES" for row in updated_statements),
        "bath_host_count": sum(row["gdt584_rule_id"] == "SH_BIO_BATHE" for row in data["hosts"]),
        "bath_y_host_count": len(bath_analogs),
        "bath_y_analogy_profile": dict(sorted(analogy_profile.items())),
        "bath_fill_packet_profile": dict(sorted(packet_profile.items())),
        "biological_y_slot_profile": dict(sorted(body_profile.items())),
        "surface_analogy_profile": surface_profile,
        "image_only_preference_profile": {
            "BODY_SLIGHT": 1,
            "STATION_LEANING": 3,
        },
        "visual_interpretation": (
            "Image-only preference is body at one target and station-leaning at three; all four overall "
            "body defaults come from complete-host analogy and sequence, not word-level image ownership."
        ),
        "slot_count": len(updated_slots),
        "changed_slot_count": sum(row["gdt590_changed"] == "YES" for row in updated_slots),
        "statement_count": len(updated_statements),
        "changed_statement_count": sum(row["gdt590_reader_changed"] == "YES" for row in updated_statements),
        "working_rule": (
            "BIOLOGICAL + SH_BIO_BATHE + no relation/form/address blocker + all written carriers in "
            "{Y,AIIN} + at least one Y => each Y=Körper and each AIIN=Badfüllung; written order and "
            "multiplicity remain visible"
        ),
        "retained_alternative": "Stationsansatz remains visible at all four adjudicated hosts, especially E2652.",
    }

    return {
        "adjudications": adjudications,
        "bath_analogs": bath_analogs,
        "bath_packets": updated_packets,
        "body_guard": updated_guard,
        "slots": updated_slots,
        "statements": updated_statements,
        "visual": visual_rows,
        "result": result,
    }


def render_reader(built: dict[str, Any]) -> str:
    statement_by_id = {row["statement_id"]: row for row in built["statements"]}
    lines = [
        "# GDT590 — vier konkrete Badpassagen",
        "",
        "Arbeitsregel: blockerfreies Biological-`Y` unter `SH_BIO_BATHE` heißt auch mit "
        "`AIIN=Badfüllung` zuerst **Körper**. `Stationsansatz` bleibt an jeder Stelle als "
        "sichtbare Alternative erhalten.",
        "",
    ]
    for row in built["adjudications"]:
        statement = statement_by_id[row["statement_id"]]
        lines.extend(
            [
                f"## {row['source_event_id']} — {row['locus']} / {row['working_strength']}",
                "",
                f"Oberfläche: `{statement['surface_sequence']}`",
                "",
                statement["gdt590_primary_reader_de"],
                "",
                f"Alternative am Zielhost: {row['retained_station_alternative_de']}",
                "",
                f"Warum Körper zuerst: {row['sequence_evidence_de']} {row['analogy_evidence_de']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Kurzfassung",
            "",
            "- E3182 ist der klarste Fall: Körperbad Grad II, direkt danach Körperbad Grad I.",
            "- E2637 besitzt im selben Satz das lokale Minimalpaar clean `cheey` gegen L-geblocktes `lsheey`.",
            "- E2404 bleibt wegen der vorausgehenden Stationsvorbereitung mittelstark.",
            "- E2652 bleibt die offenste Stelle, weil das bloße `SH` zwischen entfernt geschriebenem AIIN und Y steht.",
            "",
            "Kein Ziel ist ein Figuren- oder Objektlabel. Bildlich neigt nur E2637 leicht zu Körper; E2404, "
            "E2652 und schwach E3182 neigen zu Station. Die 4/4-Körperentscheidung kommt deshalb ausdrücklich "
            "aus vollständiger 92-Host-Analogie und Satzfolge, nicht aus einem erfundenen Bildlabel.",
            "",
        ]
    )
    return "\n".join(lines)


def write_built(built: dict[str, Any], outputs: dict[str, Path] = OUTPUTS) -> None:
    for name in (
        "adjudications", "bath_analogs", "bath_packets", "body_guard", "slots", "statements", "visual",
    ):
        write_tsv(outputs[name], built[name])
    outputs["reader"].write_text(render_reader(built), encoding="utf-8")
    outputs["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
