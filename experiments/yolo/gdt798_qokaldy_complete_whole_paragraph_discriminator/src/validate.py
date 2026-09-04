#!/usr/bin/env python3
"""Independent GDT798 validation and deterministic double replay."""

from __future__ import annotations

import csv
import hashlib
import io
import itertools
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator"
SRC, ART = BASE / "src", BASE / "artifacts"
RUN, LOCK = SRC / "run.py", SRC / "SOURCE_LOCK.tsv"
TARGET_SPECS, CANDIDATE_SPECS = SRC / "TARGET_LOCUS_SPECS.tsv", SRC / "CANDIDATE_SPECS.tsv"
CACHE = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
HISTORY = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv"
SPINE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
LINES = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv"
SOURCE_ATLAS = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
SOURCE_PROFILES = ROOT / "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator/artifacts/GDT797_71_SOURCE_SURFACE_HOST_PROFILES.tsv"
TARGET_PROFILES = ROOT / "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator/artifacts/GDT797_2_TARGET_SURFACE_HOST_PROFILES.tsv"
CROSS = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
TARGET = "qokaldy"
LOCI = ("f107v.6", "f33r.2", "f46r.4", "f46v.6", "f58r.19", "f58r.32", "f66r.67", "f66r.69", "f76r.24", "f79r.13")
OUTPUTS = (
    "GDT798_10_CACHE_OCCURRENCE_ATLAS.tsv", "GDT798_2_RELEASED_PARAGRAPH_HOSTS.tsv",
    "GDT798_10_PARAGRAPH_CANDIDATE_READERS.tsv", "GDT798_69_Q_SOURCE_HOST_CONTACTS.tsv",
    "GDT798_71_Q_SOURCE_SURFACE_PROFILES.tsv", "GDT798_8_Q_SOURCE_MULTIHOST_TOURNAMENT.tsv",
    "GDT798_14_QDY_CONTROL_PROFILES.tsv", "GDT798_EXACT_TESTS.tsv",
    "GDT798_3_COMPLETE_SURFACE_DOMAIN_TRIAD.tsv", "GDT798_NEAREST_WHOLE_CONTROLS.tsv",
    "GDT798_CANDIDATE_ADJUDICATION.tsv", "GDT798_10_CONTEXTUAL_WHOLE_RENDERER.tsv",
    "GDT798_SCOPE_AND_GUARD_AUDIT.tsv", "RESULT.json",
)
EXPECTED_STATUS = (
    "PARTIAL__10_CACHE_CELLS__8_PAGES__3_RELEASED_EVENTS__2_PARAGRAPH_HOSTS__"
    "24_OF_30_READER_WHOLES__14_OF_71_QS_CONTROLS__"
    "QOKALDY_TEXT_HOST_PURITY_RANK1_OF8_P0_125__TEXT_PAGE_CONFOUNDED__"
    "THREE_SURFACE_DOMAIN_TRIAD_6_OF6_EXACT_P0_066667__"
    "DAQABBA_NOT_SOURCE_NATIVE__QREF_QREM_C0_TIE__NO_EVIDENCE_WINNER__"
    "OPAQUE_SURVIVES__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
)
BASE_LOCK_PATHS = {
    "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator/PREREGISTRATION.md",
    "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator/METHOD.md",
    "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator/src/TARGET_LOCUS_SPECS.tsv",
    "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator/src/CANDIDATE_SPECS.tsv",
    "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator/src/run.py",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv",
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv",
    "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator/artifacts/GDT797_71_SOURCE_SURFACE_HOST_PROFILES.tsv",
    "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator/artifacts/GDT797_2_TARGET_SURFACE_HOST_PROFILES.tsv",
    "transcription/voynich_cross_transcription_lines.tsv",
}
VALIDATOR_LOCK_PATH = "experiments/yolo/gdt798_qokaldy_complete_whole_paragraph_discriminator/src/validate.py"


def F(text: str) -> tuple[str, ...]:
    return tuple(text.split())


SCHEMAS = {
    OUTPUTS[0]: F("target_ordinal surface page locus evidence_layer released_primary section language line_token_count target_token_ordinal relative_position position_class left_whole right_whole direct_okaldy_adjacency previous_v99r7_value zl3b_exact_whole it2a_exact_whole rf1b_exact_whole exact_whole_reader_count exact_whole_readers reader_stability topology_family register paragraph_id raw_line target_masked_line it2a_line rf1b_line semantic_export"),
    OUTPUTS[1]: F("paragraph_ordinal paragraph_id physical_page register topology_family independent_domain target_event_count target_loci paragraph_line_start paragraph_line_end paragraph_line_count paragraph_token_count target_paragraph_positions qok_prefix_token_count dy_suffix_token_count visible_owner_id owner_line_start owner_line_end owner_line_count owner_token_count target_owner_positions raw_whole_paragraph target_masked_whole_paragraph raw_visible_owner_window target_masked_owner_window semantic_export"),
    OUTPUTS[2]: F("reader_ordinal paragraph_id physical_page candidate_id candidate_display_de raw_whole_paragraph candidate_whole_paragraph raw_visible_owner_window candidate_owner_window translation_status"),
    OUTPUTS[3]: F("contact_ordinal q_surface base_source_surface base_source_families host_id physical_page occurrence_kind topology_families independent_domain event_count loci q_component_export"),
    OUTPUTS[4]: F("profile_ordinal base_source_surface base_source_families q_complete_surface q_event_count q_host_contact_count q_page_count running_event_count local_event_count figure_station_hosts plant_drug_hosts text_other_hosts domain_counts host_purity observed_q_complete_whole q_component_export"),
    OUTPUTS[5]: F("purity_rank profile_ordinal base_source_surface base_source_families q_complete_surface q_event_count q_host_contact_count q_page_count running_event_count local_event_count figure_station_hosts plant_drug_hosts text_other_hosts domain_counts host_purity observed_q_complete_whole q_component_export target_or_control interpretation"),
    OUTPUTS[6]: F("surface event_count text_event_count text_event_purity page_topology_contact_count text_page_topology_contact_count text_page_topology_purity running_event_count local_event_count target_or_control"),
    OUTPUTS[7]: F("test_id unit universe_n success_n target_n target_success statistic p_value selection_role result"),
    OUTPUTS[8]: F("surface external_host_count external_host_ids external_pages external_domain working_default_de source_native_family_status component_export"),
    OUTPUTS[9]: F("edit_distance surface event_count page_count external_host_count figure_station_hosts plant_drug_hosts text_other_hosts running_event_count local_event_count meaning_transfer_credit"),
    OUTPUTS[10]: F("candidate_id candidate_display_de semantic_type primary_prediction principal_risk supporting_observations counterevidence supporting_note_count_nondecisional counterevidence_note_count_nondecisional unmatched_note_balance_nondecisional matched_independent_axis_score evidence_winner decision confidence component_export confirmed_lexeme"),
    OUTPUTS[11]: F("renderer_ordinal surface page locus paragraph_id previous_v99r7_value gdt798_working_default_de display rendered_line confidence evidence antecedent_status counterevidence scope renderer_precedence component_export confirmed_lexeme"),
    OUTPUTS[12]: F("audit_id source selector allowed_count selected_count sealed_rejected_before_materialization other_skipped new_page_or_image finding"),
}
ROW_COUNTS = dict(zip(OUTPUTS[:-1], (10, 2, 10, 69, 71, 8, 14, 10, 3, 21, 5, 10, 4)))
KEYS = {
    OUTPUTS[0]: ("target_ordinal", "locus"), OUTPUTS[1]: ("paragraph_id",),
    OUTPUTS[2]: ("paragraph_id", "candidate_id"), OUTPUTS[3]: ("q_surface", "host_id"),
    OUTPUTS[4]: ("base_source_surface",), OUTPUTS[5]: ("q_complete_surface",),
    OUTPUTS[6]: ("surface",), OUTPUTS[7]: ("test_id",), OUTPUTS[8]: ("surface",),
    OUTPUTS[9]: ("surface",), OUTPUTS[10]: ("candidate_id",), OUTPUTS[11]: ("locus",),
    OUTPUTS[12]: ("audit_id",),
}


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.errors: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(label)


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return tuple(reader.fieldnames or ()), list(reader)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def srow(row: dict[str, Any]) -> dict[str, str]:
    return {key: str(value) for key, value in row.items()}


def pipe(values: Iterable[str]) -> str:
    result: list[str] = []
    for value in values:
        if value and value != "NONE" and value not in result:
            result.append(value)
    return "|".join(result) if result else "NONE"


def f6(value: float) -> str:
    return f"{value:.6f}"


def replace_exact(text: str, replacement: str) -> str:
    return " ".join(replacement if token == TARGET else token for token in text.split())


def macro(topology: str) -> str:
    if topology in {"RADIAL_ARRAY", "POOL_APPARATUS_NETWORK"}:
        return "FIGURE_STATION_SYSTEM"
    if topology in {"WHOLE_PLANT_ARTICLE", "MATERIAL_REGISTER"}:
        return "PLANT_DRUG_MATERIAL"
    if topology == "TEXT_BLOCK":
        return "TEXT_OR_OTHER"
    raise RuntimeError(f"unknown topology {topology}")


def paragraphs(lines: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, list[dict[str, str]]]]:
    count: Counter[str] = Counter()
    current: dict[str, str] = {}
    lookup: dict[str, str] = {}
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in lines:
        selector = row["source_selector"]
        if selector not in current or row["paragraph_start"] == "1":
            count[selector] += 1
            current[selector] = f"{selector}:P{count[selector]}"
        lookup[row["locus"]] = current[selector]
        if row["line_kind"] == "RUNNING_PROSE":
            groups[current[selector]].append(row)
    return lookup, groups


def collapse(rows: Sequence[dict[str, str]], para: dict[str, str]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        host = para[row["locus"]] if row["occurrence_kind"] == "RUNNING_EVENT" else f"LOCAL:{row['locus']}"
        groups[host].append(row)
    result = []
    for host, members in sorted(groups.items()):
        domains = {macro(row["topology_family"]) for row in members}
        pages = {row["physical_page"] for row in members}
        kinds = {row["occurrence_kind"] for row in members}
        if len(domains) != 1 or len(pages) != 1 or len(kinds) != 1:
            raise RuntimeError(f"conflicting collapsed host {host}")
        result.append({"host_id": host, "physical_page": next(iter(pages)), "occurrence_kind": next(iter(kinds)), "topology_families": pipe(sorted({row['topology_family'] for row in members})), "independent_domain": next(iter(domains)), "event_count": len(members), "loci": pipe(row["locus"] for row in members)})
    return result


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def hypergeom(population: int, successes: int, draws: int, observed: int) -> float:
    denominator = math.comb(population, draws)
    return sum(math.comb(successes, x) * math.comb(population - successes, draws - x) / denominator for x in range(observed, min(draws, successes) + 1) if 0 <= draws - x <= population - successes)


def fisher(a: int, b: int, c: int, d: int) -> float:
    row_one, total_success, total = a + b, a + c, a + b + c + d
    low, high = max(0, row_one - (total - total_success)), min(row_one, total_success)
    def probability(x: int) -> float:
        return math.comb(total_success, x) * math.comb(total - total_success, row_one - x) / math.comb(total, row_one)
    observed = probability(a)
    return sum(probability(x) for x in range(low, high + 1) if probability(x) <= observed + 1e-15)


def guarded_cross() -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", CROSS.relative_to(ROOT).as_posix(), "--selector", "locus"]
    for locus in LOCI:
        command.extend(("--allow", locus))
    command.extend(("--columns", "page,locus,zl3b_clean,it2a_clean,rf1b_clean", "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip())
    matches = re.findall(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if len(matches) != 1:
        raise RuntimeError("guard stats missing or duplicated")
    stats = {key: int(value) for key, value in json.loads(matches[0]).items()}
    reader = csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")
    rows = list(reader)
    if tuple(reader.fieldnames or ()) != ("page", "locus", "zl3b_clean", "it2a_clean", "rf1b_clean"):
        raise RuntimeError("guarded cross schema changed")
    return rows, stats


def main() -> int:
    audit = Audit()

    lock_schema, lock_rows = read_tsv(LOCK)
    audit.check(lock_schema == ("path", "sha256", "role"), "SOURCE_LOCK schema")
    lock_paths = [row["path"] for row in lock_rows]
    allowed_lock_sets = (BASE_LOCK_PATHS, BASE_LOCK_PATHS | {VALIDATOR_LOCK_PATH})
    audit.check(set(lock_paths) in allowed_lock_sets and len(lock_paths) == len(set(lock_paths)), "SOURCE_LOCK exact unique allowed path set")
    audit.check(all(row["role"] for row in lock_rows), "SOURCE_LOCK roles populated")
    for row in lock_rows:
        relative = Path(row["path"])
        safe = not relative.is_absolute() and ".." not in relative.parts
        audit.check(safe, f"safe lock path {row['path']}")
        if not safe:
            continue
        path = ROOT / relative
        audit.check(path.is_file(), f"locked source exists {row['path']}")
        audit.check(bool(re.fullmatch(r"[0-9a-f]{64}", row["sha256"])), f"lock hash format {row['path']}")
        if path.is_file():
            audit.check(sha256(path) == row["sha256"], f"locked source hash {row['path']}")

    manifest = json.loads((BASE / "experiment.json").read_text(encoding="utf-8"))
    audit.check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals f84/f84r")
    method = (BASE / "METHOD.md").read_text(encoding="utf-8")
    prereg = (BASE / "PREREGISTRATION.md").read_text(encoding="utf-8")
    audit.check("cannot confirm a word, morpheme" in method and "ten enumerated cached ZL3b cells" in method, "method claim ceiling")
    audit.check("No free q/operator" in prereg and "f84 and f84r remain sealed" in prereg, "preregistered privacy/component ceiling")

    canonical: dict[str, list[dict[str, str]]] = {}
    for name, schema in SCHEMAS.items():
        actual_schema, rows = read_tsv(ART / name)
        audit.check(actual_schema == schema, f"schema {name}")
        audit.check(len(rows) == ROW_COUNTS[name], f"row count {name}")
        audit.check(all(all(value != "" for value in row.values()) for row in rows), f"no blank cells {name}")
        key_fields = KEYS[name]
        keys = [tuple(row[field] for field in key_fields) for row in rows]
        audit.check(len(keys) == len(set(keys)), f"unique key {name}")
        canonical[name] = rows
    result = json.loads((ART / OUTPUTS[-1]).read_text(encoding="utf-8"))
    audit.check(result.get("experiment_id") == "GDT798" and result.get("status") == EXPECTED_STATUS, "RESULT identity/status")
    audit.check(result.get("outputs") == list(OUTPUTS), "RESULT declares exactly 14 outputs")

    cross_rows, cross_stats = guarded_cross()
    audit.check(cross_stats == {"selected": 10, "skipped_forbidden": 98, "skipped_not_allowed": 5278}, "ten-locus guard stats")
    audit.check(len(cross_rows) == 10 and {row["locus"] for row in cross_rows} == set(LOCI), "guard returns exact target loci")
    audit.check(not any(row["locus"].lower().startswith("f84") for row in cross_rows), "guard retains no sealed locus")
    cross = {row["locus"]: row for row in cross_rows}

    _, specs = read_tsv(TARGET_SPECS)
    _, candidate_specs = read_tsv(CANDIDATE_SPECS)
    _, cache = read_tsv(CACHE)
    _, history = read_tsv(HISTORY)
    _, spine = read_tsv(SPINE)
    _, lines = read_tsv(LINES)
    _, source_atlas = read_tsv(SOURCE_ATLAS)
    _, source_profiles = read_tsv(SOURCE_PROFILES)
    _, target_profiles = read_tsv(TARGET_PROFILES)
    audit.check(tuple(row["locus"] for row in specs) == LOCI and tuple(int(row["target_ordinal"]) for row in specs) == tuple(range(1, 11)), "ten fixed target specs")
    audit.check(len(candidate_specs) == 5 and {row["candidate_id"] for row in candidate_specs} == {"QREF", "QREM", "QAPP", "QSAME", "QOPAQUE"}, "five fixed candidates")
    audit.check((len(cache), len(spine), len(lines), len(source_atlas), len(source_profiles), len(target_profiles)) == (4128, 5866, 1007, 101, 71, 2), "predecessor capacities")
    audit.check(any(row.get("observation_id") == "HEO015" and "CROSS_REFERENCE" in row.get("observed_slots", "") for row in history), "historical cross-reference architecture row")
    audit.check(not any(row["locus"].lower().startswith("f84") for row in source_atlas + spine + lines), "safe admitted spines contain no sealed loci")

    cache_by_locus = {row["locus"]: row for row in cache}
    line_by_locus = {row["locus"]: row for row in lines}
    para_by_locus, para_groups = paragraphs(lines)
    spine_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    spine_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        spine_by_locus[row["locus"]].append(row)
        spine_by_surface[row["surface"]].append(row)
    occurrence_rows = canonical[OUTPUTS[0]]
    output_by_locus = {row["locus"]: row for row in occurrence_rows}
    reader_total = initial = final = adjacency = 0
    released_occurrences: list[dict[str, str]] = []
    for spec in specs:
        locus = spec["locus"]
        out = output_by_locus[locus]
        cached = cache_by_locus[locus]
        tokens = cached["zl3b_line"].split()
        positions = [i for i, token in enumerate(tokens, 1) if token == TARGET]
        audit.check(positions == [int(out["target_token_ordinal"])] and len(positions) == int(spec["expected_zl3b_count"]), f"exact cache whole {locus}")
        position = positions[0]
        position_class = "INITIAL" if position == 1 else "FINAL" if position == len(tokens) else "MIDDLE"
        initial += position_class == "INITIAL"
        final += position_class == "FINAL"
        direct = "okaldy" in {tokens[position - 2] if position > 1 else "", tokens[position] if position < len(tokens) else ""}
        adjacency += direct
        readers = [name for name, field in (("ZL3B", "zl3b_clean"), ("IT2A", "it2a_clean"), ("RF1B", "rf1b_clean")) if TARGET in cross[locus][field].split()]
        reader_total += len(readers)
        released = [row for row in spine_by_locus[locus] if row["surface"] == TARGET]
        expected_released = spec["released_primary"] == "YES"
        audit.check((len(released) == 1) == expected_released, f"released occurrence status {locus}")
        released_occurrences.extend(released)
        audit.check(out["target_ordinal"] == spec["target_ordinal"] and out["surface"] == TARGET and out["page"] == spec["page"], f"target identity {locus}")
        audit.check(out["raw_line"] == cached["zl3b_line"] and out["target_masked_line"] == replace_exact(cached["zl3b_line"], "⟦TARGET⟧"), f"exact line mask {locus}")
        audit.check(out["line_token_count"] == str(len(tokens)) and out["relative_position"] == f6(position / len(tokens)) and out["position_class"] == position_class, f"line position {locus}")
        audit.check(out["left_whole"] == (tokens[position - 2] if position > 1 else "NONE") and out["right_whole"] == (tokens[position] if position < len(tokens) else "NONE"), f"whole neighbours {locus}")
        audit.check(out["direct_okaldy_adjacency"] == ("YES" if direct else "NO"), f"direct okaldy adjacency {locus}")
        audit.check(int(out["exact_whole_reader_count"]) == len(readers) and out["exact_whole_readers"] == pipe(readers), f"reader support {locus}")
        audit.check(out["it2a_line"] == cross[locus]["it2a_clean"] and out["rf1b_line"] == cross[locus]["rf1b_clean"], f"guarded alternate lines {locus}")
        audit.check(out["semantic_export"] == "NONE", f"occurrence ceiling {locus}")
    audit.check((len(occurrence_rows), len({row['page'] for row in occurrence_rows}), len(released_occurrences), reader_total) == (10, 8, 3, 24), "10 cells/8 pages/3 released/24 of 30 readers")
    audit.check((initial, final, adjacency) == (0, 2, 1), "line-position and adjacency controls")

    released_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in released_occurrences:
        released_groups[para_by_locus[row["locus"]]].append(row)
    paragraph_rows = {row["paragraph_id"]: row for row in canonical[OUTPUTS[1]]}
    audit.check(set(released_groups) == set(paragraph_rows) == {"f66r:P5", "f76r:P1"}, "two released paragraph hosts")
    for paragraph_id, events in released_groups.items():
        out = paragraph_rows[paragraph_id]
        paragraph_lines = para_groups[paragraph_id]
        flat = [token for line in paragraph_lines for token in line["eva_clean"].split()]
        raw = " / ".join(line["eva_clean"] for line in paragraph_lines)
        owner = next(iter({event["legacy_owner"] for event in events}))
        selector = events[0]["source_selector"]
        owner_loci = {row["locus"] for row in spine if row["source_selector"] == selector and row["legacy_owner"] == owner}
        owner_lines = sorted((line_by_locus[locus] for locus in owner_loci if line_by_locus[locus]["line_kind"] == "RUNNING_PROSE"), key=lambda row: int(row["line_number"]))
        owner_raw = " / ".join(line["eva_clean"] for line in owner_lines)
        owner_flat = [token for line in owner_lines for token in line["eva_clean"].split()]
        audit.check(out["physical_page"] == events[0]["physical_page"] and out["independent_domain"] == "TEXT_OR_OTHER", f"paragraph domain {paragraph_id}")
        audit.check(int(out["target_event_count"]) == len(events) and out["target_loci"] == pipe(row["locus"] for row in events), f"paragraph event collapse {paragraph_id}")
        audit.check((int(out["paragraph_line_count"]), int(out["paragraph_token_count"])) == (len(paragraph_lines), len(flat)), f"paragraph dimensions {paragraph_id}")
        audit.check(out["target_paragraph_positions"] == pipe(str(i) for i, token in enumerate(flat, 1) if token == TARGET), f"paragraph target positions {paragraph_id}")
        audit.check(out["raw_whole_paragraph"] == raw and out["target_masked_whole_paragraph"] == replace_exact(raw, "⟦TARGET⟧"), f"whole paragraph mask {paragraph_id}")
        audit.check(out["raw_visible_owner_window"] == owner_raw and out["target_masked_owner_window"] == replace_exact(owner_raw, "⟦TARGET⟧"), f"owner window mask {paragraph_id}")
        audit.check((int(out["owner_line_count"]), int(out["owner_token_count"])) == (len(owner_lines), len(owner_flat)), f"owner dimensions {paragraph_id}")
        audit.check(out["semantic_export"] == "NONE", f"paragraph ceiling {paragraph_id}")
    audit.check((paragraph_rows["f66r:P5"]["target_event_count"], paragraph_rows["f66r:P5"]["paragraph_line_count"], paragraph_rows["f66r:P5"]["paragraph_token_count"], paragraph_rows["f76r:P1"]["target_event_count"], paragraph_rows["f76r:P1"]["paragraph_line_count"], paragraph_rows["f76r:P1"]["paragraph_token_count"]) == ("2", "3", "30", "1", "29", "368"), "paragraph control fingerprint")

    candidate_by_id = {row["candidate_id"]: row for row in candidate_specs}
    paragraph_candidates = canonical[OUTPUTS[2]]
    audit.check({(row["paragraph_id"], row["candidate_id"]) for row in paragraph_candidates} == set(itertools.product(paragraph_rows, candidate_by_id)), "2x5 paragraph candidate grid")
    for row in paragraph_candidates:
        paragraph = paragraph_rows[row["paragraph_id"]]
        candidate = candidate_by_id[row["candidate_id"]]
        display = f"⟦qokaldy:{candidate['candidate_display_de']}?⟧"
        audit.check(row["candidate_display_de"] == candidate["candidate_display_de"] and row["raw_whole_paragraph"] == paragraph["raw_whole_paragraph"], f"candidate source {row['paragraph_id']} {row['candidate_id']}")
        audit.check(row["candidate_whole_paragraph"] == replace_exact(paragraph["raw_whole_paragraph"], display) and row["candidate_owner_window"] == replace_exact(paragraph["raw_visible_owner_window"], display), f"target-only candidate insertion {row['paragraph_id']} {row['candidate_id']}")
        audit.check(row["translation_status"] == "TARGET_INSERTION_ONLY__SURROUNDING_TEXT_UNTRANSLATED", f"candidate ceiling {row['paragraph_id']} {row['candidate_id']}")

    source_loci = {row["locus"] for row in source_atlas}
    base_profiles = {row["surface"]: row for row in source_profiles}
    q_for_base = {f"q{surface}": surface for surface in base_profiles}
    q_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        if row["surface"] in q_for_base and row["locus"] not in source_loci:
            q_rows[row["surface"]].append(row)
    contacts_by_q: dict[str, list[dict[str, Any]]] = {}
    expected_contacts: list[dict[str, str]] = []
    for q_surface, rows in sorted(q_rows.items()):
        contacts = collapse(rows, para_by_locus)
        contacts_by_q[q_surface] = contacts
        base = q_for_base[q_surface]
        for contact in contacts:
            expected_contacts.append(srow({"contact_ordinal": len(expected_contacts) + 1, "q_surface": q_surface, "base_source_surface": base, "base_source_families": base_profiles[base]["source_families"], **contact, "q_component_export": "NONE"}))
    audit.check(canonical[OUTPUTS[3]] == expected_contacts and (len(expected_contacts), len(contacts_by_q)) == (69, 14), "69 contacts from 14 observed qS wholes")

    expected_profiles: list[dict[str, str]] = []
    for base, base_profile in sorted(base_profiles.items()):
        q_surface = f"q{base}"
        events, contacts = q_rows.get(q_surface, []), contacts_by_q.get(q_surface, [])
        counts = Counter(row["independent_domain"] for row in contacts)
        expected_profiles.append(srow({"profile_ordinal": len(expected_profiles) + 1, "base_source_surface": base, "base_source_families": base_profile["source_families"], "q_complete_surface": q_surface, "q_event_count": len(events), "q_host_contact_count": len(contacts), "q_page_count": len({row['physical_page'] for row in events}), "running_event_count": sum(row["occurrence_kind"] == "RUNNING_EVENT" for row in events), "local_event_count": sum(row["occurrence_kind"] != "RUNNING_EVENT" for row in events), "figure_station_hosts": counts["FIGURE_STATION_SYSTEM"], "plant_drug_hosts": counts["PLANT_DRUG_MATERIAL"], "text_other_hosts": counts["TEXT_OR_OTHER"], "domain_counts": pipe(f"{key}:{counts[key]}" for key in sorted(counts)), "host_purity": f6(max(counts.values()) / len(contacts)) if contacts else "NA", "observed_q_complete_whole": "YES" if events else "NO", "q_component_export": "NONE"}))
    audit.check(canonical[OUTPUTS[4]] == expected_profiles and len(expected_profiles) == 71, "all 71 qS profiles independently reconstructed")
    multi = [row for row in expected_profiles if int(row["q_host_contact_count"]) >= 2]
    expected_multi = []
    for row in sorted(multi, key=lambda item: (-float(item["host_purity"]), item["q_complete_surface"])):
        purity = float(row["host_purity"])
        expected_multi.append({"purity_rank": str(1 + sum(float(other["host_purity"]) > purity for other in multi)), **row, "target_or_control": "TARGET" if row["q_complete_surface"] == TARGET else "CONTROL", "interpretation": "TEXT_ONLY_TARGET" if row["q_complete_surface"] == TARGET else "SOURCE_DERIVED_Q_WHOLE_CONTROL"})
    audit.check(canonical[OUTPUTS[5]] == expected_multi and len(expected_multi) == 8, "eight multihost qS tournament rows")
    target_multi = next(row for row in expected_multi if row["q_complete_surface"] == TARGET)
    audit.check(target_multi["purity_rank"] == "1" and target_multi["host_purity"] == "1.000000" and sum(float(row["host_purity"]) >= 1 for row in expected_multi) == 1, "qokaldy purity rank 1/8")

    q_prefixed = {surface: rows for surface, rows in spine_by_surface.items() if surface.startswith("q")}
    q_running_only = sum(all(row["occurrence_kind"] == "RUNNING_EVENT" for row in rows) for rows in q_prefixed.values())
    q_total_events = sum(len(rows) for rows in q_prefixed.values())
    q_running_events = sum(row["occurrence_kind"] == "RUNNING_EVENT" for rows in q_prefixed.values() for row in rows)
    audit.check((len(q_prefixed), q_running_only, q_total_events, q_running_events) == (225, 213, 854, 842), "broad q running/local base rate")
    recurrent_qdy = {surface: rows for surface, rows in spine_by_surface.items() if surface.startswith("q") and surface.endswith("dy") and len(rows) >= 3}
    expected_qdy = []
    for surface, rows in sorted(recurrent_qdy.items()):
        page_topology = {(row["physical_page"], row["topology_family"]) for row in rows}
        text_events = sum(row["topology_family"] == "TEXT_BLOCK" for row in rows)
        text_contacts = sum(topology == "TEXT_BLOCK" for _, topology in page_topology)
        expected_qdy.append(srow({"surface": surface, "event_count": len(rows), "text_event_count": text_events, "text_event_purity": f6(text_events / len(rows)), "page_topology_contact_count": len(page_topology), "text_page_topology_contact_count": text_contacts, "text_page_topology_purity": f6(text_contacts / len(page_topology)), "running_event_count": sum(row["occurrence_kind"] == "RUNNING_EVENT" for row in rows), "local_event_count": sum(row["occurrence_kind"] != "RUNNING_EVENT" for row in rows), "target_or_control": "TARGET" if surface == TARGET else "CONTROL"}))
    audit.check(canonical[OUTPUTS[6]] == expected_qdy and len(expected_qdy) == 14, "fourteen recurrent q...dy profiles")

    qdy_population = sum(int(row["event_count"]) for row in expected_qdy)
    qdy_text = sum(int(row["text_event_count"]) for row in expected_qdy)
    qdy_contacts = sum(int(row["page_topology_contact_count"]) for row in expected_qdy)
    qdy_text_contacts = sum(int(row["text_page_topology_contact_count"]) for row in expected_qdy)
    exact_three = {surface: rows for surface, rows in q_prefixed.items() if len(rows) == 3}
    exact_three_text = sum(all(row["topology_family"] == "TEXT_BLOCK" for row in rows) for rows in exact_three.values())
    target_contacts = contacts_by_q[TARGET]
    target_hosts = {row["host_id"] for row in target_contacts}
    control_contacts = [row for surface, contacts in contacts_by_q.items() if surface != TARGET for row in contacts]
    unique_control_hosts: dict[str, dict[str, Any]] = {}
    for row in control_contacts:
        audit.check(row["host_id"] not in unique_control_hosts or unique_control_hosts[row["host_id"]]["independent_domain"] == row["independent_domain"], f"consistent control host {row['host_id']}")
        unique_control_hosts[row["host_id"]] = row
    disjoint = [row for host, row in unique_control_hosts.items() if host not in target_hosts]
    disjoint_counts = Counter(row["independent_domain"] for row in disjoint)
    pair_denominator = math.comb(len(disjoint), 2)
    any_same = sum(math.comb(count, 2) for count in disjoint_counts.values())
    text_pairs = math.comb(disjoint_counts["TEXT_OR_OTHER"], 2)
    target_pages = {row["physical_page"] for row in target_contacts}
    page_excluded = [row for row in control_contacts if row["physical_page"] not in target_pages]
    page_counts = Counter(row["independent_domain"] for row in page_excluded)
    qokaly = contacts_by_q["qokaly"]
    qokaldy_text = sum(row["independent_domain"] == "TEXT_OR_OTHER" for row in target_contacts)
    qokaly_text = sum(row["independent_domain"] == "TEXT_OR_OTHER" for row in qokaly)
    qokaly_fisher = fisher(qokaldy_text, len(target_contacts) - qokaldy_text, qokaly_text, len(qokaly) - qokaly_text)
    audit.check((len(disjoint), disjoint_counts, pair_denominator, any_same, text_pairs) == (36, Counter({"FIGURE_STATION_SYSTEM": 16, "PLANT_DRUG_MATERIAL": 13, "TEXT_OR_OTHER": 7}), 630, 219, 21), "target-excluded host-cluster null")
    audit.check((len(page_excluded), page_counts) == (52, Counter({"FIGURE_STATION_SYSTEM": 36, "PLANT_DRUG_MATERIAL": 16})), "page-excluded zero-text sensitivity")
    audit.check(f6(qokaly_fisher) == "0.400000" and (qokaldy_text, len(target_contacts), qokaly_text, len(qokaly)) == (2, 2, 1, 3), "qokaldy/qokaly Fisher .4")

    triad_defaults = {"qokaldy": "davon / Heilmittel", "okaldy": "Bade-/Behandlungseintrag", "otaldy": "Wurzel-/Drogenartikel"}
    expected_triad: list[dict[str, str]] = []
    triad_events: list[tuple[str, str]] = []
    for surface in ("qokaldy", "okaldy", "otaldy"):
        contacts = collapse([row for row in spine_by_surface[surface] if row["locus"] not in source_loci], para_by_locus)
        counts = Counter(row["independent_domain"] for row in contacts)
        audit.check(len(contacts) == 2 and len(counts) == 1, f"pure two-host triad surface {surface}")
        triad_events.extend((surface, row["independent_domain"]) for row in contacts)
        expected_triad.append(srow({"surface": surface, "external_host_count": len(contacts), "external_host_ids": pipe(row["host_id"] for row in contacts), "external_pages": pipe(row["physical_page"] for row in contacts), "external_domain": next(iter(counts)), "working_default_de": triad_defaults[surface], "source_native_family_status": "NO_Q_SOURCE_LABEL_OBSERVED" if surface == TARGET else "AQABBA_SOURCE_LABEL_PRESENT", "component_export": "NONE"}))
    audit.check(canonical[OUTPUTS[8]] == expected_triad, "three-surface domain triad reconstructed")
    keyed = pooled = 0.0
    for index, (surface, domain) in enumerate(triad_events):
        training = [event for other, event in enumerate(triad_events) if other != index]
        for which, values in (("keyed", [value for key, value in training if key == surface]), ("pooled", [value for _, value in training])):
            counts = Counter(values); maximum = max(counts.values()); modes = {value for value, count in counts.items() if count == maximum}
            credit = 1 / len(modes) if domain in modes else 0
            if which == "keyed": keyed += credit
            else: pooled += credit
    assignments = set(itertools.permutations(["FIGURE_STATION_SYSTEM"] * 2 + ["PLANT_DRUG_MATERIAL"] * 2 + ["TEXT_OR_OTHER"] * 2))
    extreme = sum(all(pair[0] == pair[1] for pair in (assignment[:2], assignment[2:4], assignment[4:])) and len({assignment[0], assignment[2], assignment[4]}) == 3 for assignment in assignments)
    audit.check((keyed, pooled, len(assignments), extreme, f6(extreme / len(assignments))) == (6.0, 0.0, 90, 6, "0.066667"), "triad 6/90 exact permutation")

    expected_tests = {
        "QDY_EVENT_TEXT_HYPERGEOMETRIC": (qdy_population, qdy_text, f6(hypergeom(qdy_population, qdy_text, 3, 3))),
        "QDY_PAGE_TOPOLOGY_TEXT_HYPERGEOMETRIC": (qdy_contacts, qdy_text_contacts, f6(hypergeom(qdy_contacts, qdy_text_contacts, 2, 2))),
        "EXACT3_Q_SURFACE_EMPIRICAL": (len(exact_three), exact_three_text, f6(exact_three_text / len(exact_three))),
        "SOURCE_Q_MULTIHOST_PURITY_RANK": (8, 1, "0.125000"),
        "TARGET_EXCLUDED_ANY_SAME_DOMAIN_PAIR": (pair_denominator, any_same, f6(any_same / pair_denominator)),
        "TARGET_EXCLUDED_TEXT_PAIR_POSTHOC": (pair_denominator, text_pairs, f6(text_pairs / pair_denominator)),
        "QOKALY_NEAREST_WHOLE_FISHER": (5, 3, f6(qokaly_fisher)),
        "THREE_SURFACE_DOMAIN_ASSIGNMENT_EXACT": (90, 6, "0.066667"),
        "ALL_Q_RUNNING_ONLY_BASE_RATE": (225, 213, "NOT_APPLICABLE"),
        "TARGET_PAGE_EXCLUSION_SENSITIVITY": (52, 0, "NOT_IDENTIFIABLE"),
    }
    tests = {row["test_id"]: row for row in canonical[OUTPUTS[7]]}
    audit.check(set(tests) == set(expected_tests), "ten exact test identifiers")
    for test_id, (universe, success, p_value) in expected_tests.items():
        audit.check((tests[test_id]["universe_n"], tests[test_id]["success_n"], tests[test_id]["p_value"]) == (str(universe), str(success), p_value), f"exact test arithmetic {test_id}")
    audit.check(tests["TARGET_EXCLUDED_ANY_SAME_DOMAIN_PAIR"]["statistic"] == "PAIR_NUMERATOR_219_OF_630" and tests["TARGET_EXCLUDED_TEXT_PAIR_POSTHOC"]["statistic"] == "TEXT_PAIR_NUMERATOR_21_OF_630", "cluster-null numerators")
    audit.check(tests["TARGET_PAGE_EXCLUSION_SENSITIVITY"]["result"] == "ZERO_TEXT_CONTROLS_AFTER_F66_F76_REMOVAL", "page confound decision")

    expected_nearest = []
    for surface, rows in sorted(spine_by_surface.items(), key=lambda item: (levenshtein(TARGET, item[0]), item[0])):
        distance = levenshtein(TARGET, surface)
        if distance > 2:
            continue
        contacts = collapse([row for row in rows if row["locus"] not in source_loci], para_by_locus)
        counts = Counter(row["independent_domain"] for row in contacts)
        expected_nearest.append(srow({"edit_distance": distance, "surface": surface, "event_count": len(rows), "page_count": len({row['physical_page'] for row in rows}), "external_host_count": len(contacts), "figure_station_hosts": counts["FIGURE_STATION_SYSTEM"], "plant_drug_hosts": counts["PLANT_DRUG_MATERIAL"], "text_other_hosts": counts["TEXT_OR_OTHER"], "running_event_count": sum(row["occurrence_kind"] == "RUNNING_EVENT" for row in rows), "local_event_count": sum(row["occurrence_kind"] != "RUNNING_EVENT" for row in rows), "meaning_transfer_credit": "ZERO"}))
    audit.check(canonical[OUTPUTS[9]] == expected_nearest and len(expected_nearest) == 21, "all edit-distance <=2 complete-whole controls")

    adjudication = {row["candidate_id"]: row for row in canonical[OUTPUTS[10]]}
    expected_decisions = {"QREF": ("RETAIN_C0_TIED", "C0_TIED"), "QREM": ("RETAIN_C0_TIED", "C0_TIED"), "QAPP": ("HOLD", "LOW"), "QSAME": ("REJECT_PORTABILITY", "REJECTED"), "QOPAQUE": ("SURVIVES_PRIMARY", "HIGH_ARCHITECTURE_LOW_SEMANTICS")}
    audit.check(set(adjudication) == set(expected_decisions), "five adjudicated candidates")
    for candidate_id, (decision, confidence) in expected_decisions.items():
        row, spec = adjudication[candidate_id], candidate_by_id[candidate_id]
        audit.check(all(row[field] == spec[field] for field in ("candidate_display_de", "semantic_type", "primary_prediction", "principal_risk")), f"fixed candidate fields {candidate_id}")
        audit.check((int(row["supporting_note_count_nondecisional"]), int(row["counterevidence_note_count_nondecisional"]), int(row["unmatched_note_balance_nondecisional"])) == (len(row["supporting_observations"].split("|")), len(row["counterevidence"].split("|")), len(row["supporting_observations"].split("|")) - len(row["counterevidence"].split("|"))), f"candidate nondecisional note-count arithmetic {candidate_id}")
        audit.check(row["matched_independent_axis_score"] == "NOT_ESTABLISHED" and row["evidence_winner"] == "NO", f"no candidate evidence winner {candidate_id}")
        audit.check(row["decision"] == decision and row["confidence"] == confidence and row["component_export"] == "NONE" and row["confirmed_lexeme"] == "NO", f"candidate decision/ceiling {candidate_id}")

    renderer = canonical[OUTPUTS[11]]
    audit.check(tuple(row["locus"] for row in renderer) == LOCI, "renderer exact ten-locus scope")
    for row in renderer:
        source = output_by_locus[row["locus"]]
        count = int(source["exact_whole_reader_count"])
        confidence = {3: "C0_ALL3_WHOLE", 2: "C0_TWO_OF_THREE_WHOLE", 1: "C0_ZL_ONLY_WHOLE"}[count]
        antecedent = "DIRECT_LEFT_OKALDY_WHOLE" if source["direct_okaldy_adjacency"] == "YES" else "SAME_PARAGRAPH_QOKALDY_REPEAT" if source["page"] == "f66r" else "NO_IDENTIFIED_ANTECEDENT"
        audit.check(row["gdt798_working_default_de"] == "davon / Heilmittel" and row["display"] == "⟦qokaldy:davon?/Heilmittel?⟧" and row["rendered_line"] == replace_exact(source["raw_line"], row["display"]), f"bounded tied renderer replacement {row['locus']}")
        audit.check(row["confidence"] == confidence and row["antecedent_status"] == antecedent, f"renderer evidence class {row['locus']}")
        audit.check(row["evidence"] == "text-internal deployment; multiple within-line positions; bounded complete-whole reference/remedy tie" and row["counterevidence"] == "text topology is page-confounded; no referent is independently decoded" and row["renderer_precedence"] == "GDT798_CONTEXTUAL_WHOLE_TIE_OVER_UNKNOWN", f"renderer tied evidence and precedence {row['locus']}")
        audit.check(row["scope"] == "ENUMERATED_CACHE_CELL_ONLY" and row["component_export"] == "ZERO" and row["confirmed_lexeme"] == "NO", f"renderer ceiling {row['locus']}")

    scope = {row["audit_id"]: row for row in canonical[OUTPUTS[12]]}
    audit.check(set(scope) == {"GDT798_EXACT_LOCUS_CROSS_QUERY", "GDT798_RELEASED_SPINE", "GDT798_INHERITED_LINE_CACHE", "GDT798_DAQABBA_CORRECTION"}, "four scope/guard rows")
    guard_row = scope["GDT798_EXACT_LOCUS_CROSS_QUERY"]
    audit.check((guard_row["allowed_count"], guard_row["selected_count"], guard_row["sealed_rejected_before_materialization"], guard_row["other_skipped"]) == ("10", "10", "98", "5278"), "scope guard counts")
    q_source_labels = [row for row in source_atlas if row["complete_label_surface"].startswith("q")]
    daqabba = [row for row in source_atlas if "DAQABBA" in {row.get("canonical_boundary_family", ""), row.get("canonical_compact_family", "")}]
    audit.check(not q_source_labels and not daqabba and scope["GDT798_DAQABBA_CORRECTION"]["finding"] == "Q_PREFIXED_SOURCE_LABELS_0__DAQABBA_ROWS_0__NOT_SOURCE_NATIVE", "DAQABBA absent from source-native atlas")
    audit.check(all(row["new_page_or_image"] == "NO" for row in scope.values()), "no new page/image")

    audit.check(result["target"] == {"surface": TARGET, "cache_cells": 10, "pages": 8, "released_events": 3, "released_paragraph_hosts": 2, "exact_reader_wholes": 24, "reader_opportunities": 30, "line_initial": 0, "line_final": 2, "direct_okaldy_adjacencies": 1}, "RESULT target controls")
    audit.check(result["controls"] == {"source_surfaces": 71, "observed_q_source_wholes": 14, "q_source_host_contacts": 69, "q_source_multihost_surfaces": 8, "qokaldy_purity_rank": "1_OF_8", "qokaldy_purity_empirical_p": "0.125000", "all_q_types": 225, "all_q_running_only_types": 213, "all_q_events": 854, "all_q_running_events": 842, "page_excluded_text_control_contacts": 0}, "RESULT cohort controls")
    audit.check(result["triad"] == {"surface_keyed_credit": "1.000000", "pooled_credit": "0.000000", "exact_assignments": 90, "as_extreme": 6, "p_value": "0.066667"}, "RESULT triad")
    audit.check(result["decision"] == {"selected_c0_complete_whole": "NONE__NO_EVIDENCE_WINNER", "tied_c0_complete_wholes": ["qokaldy=davon", "qokaldy=Heilmittel"], "practical_display_order": ["davon", "Heilmittel"], "same_as_okaldy": "REJECT_PORTABILITY", "opaque_null": "SURVIVES", "daqabba_source_family": "NOT_SOURCE_NATIVE__UNOBSERVED_IN_101_SOURCE_ATLAS", "component_exports": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0}, "RESULT tie decision/ceiling")
    control_pages = sorted({row["physical_page"] for row in expected_contacts})
    audit.check(len({row["physical_page"] for row in spine}) == 30, "released control spine covers 30 pages")
    audit.check(len(control_pages) == 17, "q-source contacts touch 17 released pages")
    audit.check(result["scope"] == {"new_pages": 0, "new_images": 0, "sealed_rows_materialized_by_executable_build": 0, "released_visually_reviewed_target_pages_used": ["f66r", "f76r"], "released_control_spine_pages_available": 30, "released_qs_control_pages_touched": control_pages, "released_qs_control_page_count": 17, "inherited_cache_line_pages_not_visually_interpreted_here": 6}, "RESULT privacy and released-control scope")

    for name, rows in canonical.items():
        for ordinal, row in enumerate(rows, 1):
            for field in ("q_component_export", "component_export"):
                if field in row:
                    audit.check(row[field] in {"NONE", "ZERO"}, f"zero component export {name}:{ordinal}")
            if "semantic_export" in row:
                audit.check(row["semantic_export"] == "NONE", f"no semantic export {name}:{ordinal}")
            if "confirmed_lexeme" in row:
                audit.check(row["confirmed_lexeme"] == "NO", f"no confirmed lexeme {name}:{ordinal}")

    replay_hashes: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="gdt798_validate_") as temporary:
        temporary_root = Path(temporary)
        for replay in (1, 2):
            output_dir = temporary_root / f"replay_{replay}"
            completed = subprocess.run([sys.executable, str(RUN), "--output-dir", str(output_dir)], cwd=ROOT, text=True, capture_output=True, check=False)
            audit.check(completed.returncode == 0, f"builder replay {replay} exits zero")
            names = {path.name for path in output_dir.iterdir()} if output_dir.is_dir() else set()
            audit.check(names == set(OUTPUTS), f"builder replay {replay} exact 14-output set")
            hashes: dict[str, str] = {}
            for name in OUTPUTS:
                replay_path, canonical_path = output_dir / name, ART / name
                audit.check(replay_path.is_file(), f"replay {replay} writes {name}")
                if replay_path.is_file():
                    replay_bytes = replay_path.read_bytes()
                    hashes[name] = hashlib.sha256(replay_bytes).hexdigest()
                    audit.check(replay_bytes == canonical_path.read_bytes(), f"replay {replay} matches canonical {name}")
                    audit.check(b"f84" not in replay_bytes.lower(), f"replay {replay} retains no sealed token {name}")
            replay_hashes.append(hashes)
    byte_identical = len(replay_hashes) == 2 and replay_hashes[0] == replay_hashes[1]
    audit.check(byte_identical, "two builder replays byte-identical")

    payload = {
        "experiment_id": "GDT798", "status": "PASS" if not audit.errors else "FAIL",
        "checks": audit.checks, "errors": audit.errors, "replays": 2,
        "byte_identical_replays": byte_identical, "canonical_outputs_checked": len(OUTPUTS),
        "source_lock_validator_row_present": VALIDATOR_LOCK_PATH in set(lock_paths),
        "target_cells": 10, "reader_exact_wholes": reader_total, "reader_opportunities": 30,
        "released_events": 3, "paragraph_hosts": 2, "q_source_host_contacts": len(expected_contacts),
        "q_source_surfaces": len(expected_profiles), "observed_q_source_wholes": len(contacts_by_q),
        "q_source_multihost_surfaces": len(expected_multi), "qdy_control_surfaces": len(expected_qdy),
        "qokaly_fisher_two_sided_p": qokaly_fisher,
        "host_cluster_null": {"clusters": len(disjoint), "pairs": pair_denominator, "any_same": any_same, "text_same": text_pairs},
        "triad_permutation": {"assignments": len(assignments), "as_extreme": extreme, "p_value": extreme / len(assignments)},
        "component_exports": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "sealed_rows_materialized": 0,
    }
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not audit.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
