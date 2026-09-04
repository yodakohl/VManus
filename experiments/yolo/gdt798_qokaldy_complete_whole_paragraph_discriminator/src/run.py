#!/usr/bin/env python3
"""Build GDT798: complete-qokaldy paragraph and host discrimination."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import re
import subprocess
import sys
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
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
TARGET_SPECS = SRC / "TARGET_LOCUS_SPECS.tsv"
CANDIDATE_SPECS = SRC / "CANDIDATE_SPECS.tsv"
LOCK = SRC / "SOURCE_LOCK.tsv"

G734_READER = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
G735_HISTORY = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_ENTRY_ATLAS.tsv"
G791 = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts"
SPINE = G791 / "GDT791_5866_OCCURRENCE_SPINE.tsv"
LINES = G791 / "GDT791_1007_LINE_OWNER_ATLAS.tsv"
G795_ATLAS = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
G797 = ROOT / "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator/artifacts"
G797_SOURCE_PROFILES = G797 / "GDT797_71_SOURCE_SURFACE_HOST_PROFILES.tsv"
G797_TARGET_PROFILES = G797 / "GDT797_2_TARGET_SURFACE_HOST_PROFILES.tsv"
CROSS = ROOT / "transcription/voynich_cross_transcription_lines.tsv"

TARGET = "qokaldy"
OUTPUT_NAMES = (
    "GDT798_10_CACHE_OCCURRENCE_ATLAS.tsv",
    "GDT798_2_RELEASED_PARAGRAPH_HOSTS.tsv",
    "GDT798_10_PARAGRAPH_CANDIDATE_READERS.tsv",
    "GDT798_69_Q_SOURCE_HOST_CONTACTS.tsv",
    "GDT798_71_Q_SOURCE_SURFACE_PROFILES.tsv",
    "GDT798_8_Q_SOURCE_MULTIHOST_TOURNAMENT.tsv",
    "GDT798_14_QDY_CONTROL_PROFILES.tsv",
    "GDT798_EXACT_TESTS.tsv",
    "GDT798_3_COMPLETE_SURFACE_DOMAIN_TRIAD.tsv",
    "GDT798_NEAREST_WHOLE_CONTROLS.tsv",
    "GDT798_CANDIDATE_ADJUDICATION.tsv",
    "GDT798_10_CONTEXTUAL_WHOLE_RENDERER.tsv",
    "GDT798_SCOPE_AND_GUARD_AUDIT.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__10_CACHE_CELLS__8_PAGES__3_RELEASED_EVENTS__2_PARAGRAPH_HOSTS__"
    "24_OF_30_READER_WHOLES__14_OF_71_QS_CONTROLS__"
    "QOKALDY_TEXT_HOST_PURITY_RANK1_OF8_P0_125__TEXT_PAGE_CONFOUNDED__"
    "THREE_SURFACE_DOMAIN_TRIAD_6_OF6_EXACT_P0_066667__"
    "DAQABBA_NOT_SOURCE_NATIVE__QREF_QREM_C0_TIE__NO_EVIDENCE_WINNER__"
    "OPAQUE_SURVIVES__ZERO_COMPONENT_EXPORT__"
    "ZERO_CONFIRMED_LEXEMES"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: Sequence[str] | None = None) -> None:
    materialized = list(rows)
    fieldnames = list(fields) if fields is not None else (list(materialized[0]) if materialized else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="raise"
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source_lock() -> None:
    rows = read_tsv(LOCK)
    if not rows or len(rows) != len({row["path"] for row in rows}):
        raise RuntimeError("source lock missing, empty, or duplicated")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"unsafe source-lock path: {row['path']}")
        path = ROOT / relative
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def guarded_cross_query(loci: Sequence[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", CROSS.relative_to(ROOT).as_posix(),
        "--selector", "locus",
    ]
    for locus in loci:
        command.extend(("--allow", locus))
    command.extend((
        "--columns", "page,locus,zl3b_clean,it2a_clean,rf1b_clean",
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded alternate-reader query failed")
    matches = re.findall(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if len(matches) != 1:
        raise RuntimeError("guard statistics missing or duplicated")
    stats = {key: int(value) for key, value in json.loads(matches[0]).items()}
    expected = {"selected": 10, "skipped_forbidden": 98, "skipped_not_allowed": 5278}
    if stats != expected:
        raise RuntimeError(f"guard statistics changed: {stats} != {expected}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if len(rows) != 10 or any(row["locus"].startswith("f84") for row in rows):
        raise RuntimeError("guarded alternate-reader target set changed")
    return rows, stats


def pipe(values: Iterable[str]) -> str:
    result: list[str] = []
    for value in values:
        if value and value != "NONE" and value not in result:
            result.append(value)
    return "|".join(result) if result else "NONE"


def f6(value: float) -> str:
    return f"{value:.6f}"


def replace_exact(text: str, target: str, replacement: str) -> str:
    return " ".join(replacement if token == target else token for token in text.split())


def build_paragraphs(
    line_rows: list[dict[str, str]],
) -> tuple[dict[str, str], dict[str, list[dict[str, str]]]]:
    counters: Counter[str] = Counter()
    current: dict[str, str] = {}
    locus_to_paragraph: dict[str, str] = {}
    paragraphs: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in line_rows:
        selector = row["source_selector"]
        if selector not in current or row["paragraph_start"] == "1":
            counters[selector] += 1
            current[selector] = f"{selector}:P{counters[selector]}"
        paragraph_id = current[selector]
        locus_to_paragraph[row["locus"]] = paragraph_id
        if row["line_kind"] == "RUNNING_PROSE":
            paragraphs[paragraph_id].append(row)
    return locus_to_paragraph, paragraphs


def paragraph_text(rows: Sequence[dict[str, str]]) -> str:
    return " / ".join(row["eva_clean"] for row in rows)


def macro_domain(topology: str) -> str:
    if topology in {"RADIAL_ARRAY", "POOL_APPARATUS_NETWORK"}:
        return "FIGURE_STATION_SYSTEM"
    if topology in {"WHOLE_PLANT_ARTICLE", "MATERIAL_REGISTER"}:
        return "PLANT_DRUG_MATERIAL"
    if topology == "TEXT_BLOCK":
        return "TEXT_OR_OTHER"
    raise RuntimeError(f"unmapped topology: {topology}")


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def hypergeom_tail(population: int, successes: int, draws: int, observed: int) -> float:
    denominator = math.comb(population, draws)
    return sum(
        math.comb(successes, value) * math.comb(population - successes, draws - value) / denominator
        for value in range(observed, min(draws, successes) + 1)
        if 0 <= draws - value <= population - successes
    )


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row_one = a + b
    total_success = a + c
    total = a + b + c + d
    low = max(0, row_one - (total - total_success))
    high = min(row_one, total_success)

    def probability(value: int) -> float:
        return (
            math.comb(total_success, value)
            * math.comb(total - total_success, row_one - value)
            / math.comb(total, row_one)
        )

    observed = probability(a)
    return sum(probability(value) for value in range(low, high + 1) if probability(value) <= observed + 1e-15)


def collapse_contacts(
    occurrence_rows: Sequence[dict[str, str]],
    locus_to_paragraph: dict[str, str],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrence_rows:
        host_id = (
            locus_to_paragraph[row["locus"]]
            if row["occurrence_kind"] == "RUNNING_EVENT"
            else f"LOCAL:{row['locus']}"
        )
        grouped[host_id].append(row)
    contacts: list[dict[str, Any]] = []
    for host_id, rows in sorted(grouped.items()):
        domains = {macro_domain(row["topology_family"]) for row in rows}
        pages = {row["physical_page"] for row in rows}
        kinds = {row["occurrence_kind"] for row in rows}
        topologies = {row["topology_family"] for row in rows}
        if len(domains) != 1 or len(pages) != 1 or len(kinds) != 1:
            raise RuntimeError(f"host collapse conflict: {host_id}")
        contacts.append({
            "host_id": host_id,
            "physical_page": next(iter(pages)),
            "occurrence_kind": next(iter(kinds)),
            "topology_families": pipe(sorted(topologies)),
            "independent_domain": next(iter(domains)),
            "event_count": len(rows),
            "loci": pipe(row["locus"] for row in rows),
        })
    return contacts


def model_credit(actual: str, training: Sequence[str]) -> float:
    counts = Counter(training)
    maximum = max(counts.values())
    modes = {value for value, count in counts.items() if count == maximum}
    return 1.0 / len(modes) if actual in modes else 0.0


def build(output_dir: Path) -> dict[str, Any]:
    verify_source_lock()
    specs = read_tsv(TARGET_SPECS)
    candidates = read_tsv(CANDIDATE_SPECS)
    cache = read_tsv(G734_READER)
    history = read_tsv(G735_HISTORY)
    spine = read_tsv(SPINE)
    lines = read_tsv(LINES)
    source_atlas = read_tsv(G795_ATLAS)
    source_profiles = read_tsv(G797_SOURCE_PROFILES)
    target_profiles = read_tsv(G797_TARGET_PROFILES)

    if len(specs) != 10 or len(candidates) != 5:
        raise RuntimeError("fixed target or candidate deck changed")
    if len(cache) != 4128 or len(spine) != 5866 or len(lines) != 1007:
        raise RuntimeError("predecessor cache capacity changed")
    if len(source_atlas) != 101 or len(source_profiles) != 71 or len(target_profiles) != 2:
        raise RuntimeError("source-surface predecessor capacity changed")
    if not any(row.get("observation_id") == "HEO015" and "CROSS_REFERENCE" in row.get("observed_slots", "") for row in history):
        raise RuntimeError("historical cross-reference architecture row changed")

    target_loci = [row["locus"] for row in specs]
    if len(target_loci) != len(set(target_loci)):
        raise RuntimeError("duplicate target locus")
    cross_rows, cross_stats = guarded_cross_query(target_loci)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    cache_by_locus = {row["locus"]: row for row in cache}
    line_by_locus = {row["locus"]: row for row in lines}
    locus_to_paragraph, paragraphs = build_paragraphs(lines)
    source_loci = {row["locus"] for row in source_atlas}
    spine_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    spine_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        spine_by_locus[row["locus"]].append(row)
        spine_by_surface[row["surface"]].append(row)

    atlas_rows: list[dict[str, Any]] = []
    for spec in specs:
        locus = spec["locus"]
        cache_row = cache_by_locus.get(locus)
        if cache_row is None:
            raise RuntimeError(f"target missing from inherited cache: {locus}")
        tokens = cache_row["zl3b_line"].split()
        positions = [index for index, token in enumerate(tokens, 1) if token == TARGET]
        if len(positions) != int(spec["expected_zl3b_count"]) or len(positions) != 1:
            raise RuntimeError(f"target count changed at {locus}")
        target_position = positions[0]
        semantic_values = cache_row["v99r7_semantic_token_values_de"].split(" | ")
        if len(semantic_values) != len(tokens):
            raise RuntimeError(f"cache semantic width mismatch: {locus}")
        cross = cross_by_locus[locus]
        reader_fields = ("zl3b_clean", "it2a_clean", "rf1b_clean")
        exact_readers = [field.split("_")[0].upper() for field in reader_fields if TARGET in cross[field].split()]
        exact_count = len(exact_readers)
        released_matches = [row for row in spine_by_locus.get(locus, []) if row["surface"] == TARGET]
        released = spec["released_primary"] == "YES"
        if released != bool(released_matches) or (released and len(released_matches) != 1):
            raise RuntimeError(f"released target mismatch: {locus}")
        occurrence = released_matches[0] if released else None
        paragraph_id = locus_to_paragraph[locus] if occurrence else "NOT_IN_RELEASED_SPINE"
        atlas_rows.append({
            "target_ordinal": spec["target_ordinal"],
            "surface": TARGET,
            "page": spec["page"],
            "locus": locus,
            "evidence_layer": spec["evidence_layer"],
            "released_primary": spec["released_primary"],
            "section": cache_row["section"],
            "language": cache_row["language"],
            "line_token_count": len(tokens),
            "target_token_ordinal": target_position,
            "relative_position": f6(target_position / len(tokens)),
            "position_class": "INITIAL" if target_position == 1 else ("FINAL" if target_position == len(tokens) else "MIDDLE"),
            "left_whole": tokens[target_position - 2] if target_position > 1 else "NONE",
            "right_whole": tokens[target_position] if target_position < len(tokens) else "NONE",
            "direct_okaldy_adjacency": "YES" if "okaldy" in {tokens[target_position - 2] if target_position > 1 else "", tokens[target_position] if target_position < len(tokens) else ""} else "NO",
            "previous_v99r7_value": semantic_values[target_position - 1],
            "zl3b_exact_whole": "YES" if TARGET in cross["zl3b_clean"].split() else "NO",
            "it2a_exact_whole": "YES" if TARGET in cross["it2a_clean"].split() else "NO",
            "rf1b_exact_whole": "YES" if TARGET in cross["rf1b_clean"].split() else "NO",
            "exact_whole_reader_count": exact_count,
            "exact_whole_readers": pipe(exact_readers),
            "reader_stability": {3: "ALL3_EXACT", 2: "TWO_OF_THREE_EXACT", 1: "ONE_OF_THREE_EXACT"}[exact_count],
            "topology_family": occurrence["topology_family"] if occurrence else "NOT_VISUALLY_CLASSIFIED_HERE",
            "register": occurrence["register"] if occurrence else "INHERITED_CACHE_ONLY",
            "paragraph_id": paragraph_id,
            "raw_line": cache_row["zl3b_line"],
            "target_masked_line": replace_exact(cache_row["zl3b_line"], TARGET, "⟦TARGET⟧"),
            "it2a_line": cross["it2a_clean"],
            "rf1b_line": cross["rf1b_clean"],
            "semantic_export": "NONE",
        })
    write_tsv(output_dir / OUTPUT_NAMES[0], atlas_rows)

    primary_occurrences = [
        row for row in spine if row["surface"] == TARGET and row["locus"] in target_loci
    ]
    primary_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in primary_occurrences:
        primary_groups[locus_to_paragraph[row["locus"]]].append(row)
    paragraph_rows: list[dict[str, Any]] = []
    for paragraph_id, occurrences in sorted(primary_groups.items()):
        paragraph_lines = paragraphs[paragraph_id]
        raw_paragraph = paragraph_text(paragraph_lines)
        flat = [token for line in paragraph_lines for token in line["eva_clean"].split()]
        owner_ids = {row["legacy_owner"] for row in occurrences}
        if len(owner_ids) != 1:
            raise RuntimeError(f"target owner conflict: {paragraph_id}")
        owner_id = next(iter(owner_ids))
        selector = occurrences[0]["source_selector"]
        owner_loci = {
            row["locus"] for row in spine
            if row["source_selector"] == selector and row["legacy_owner"] == owner_id
        }
        owner_lines = sorted(
            (line_by_locus[locus] for locus in owner_loci if line_by_locus[locus]["line_kind"] == "RUNNING_PROSE"),
            key=lambda row: int(row["line_number"]),
        )
        owner_text = paragraph_text(owner_lines)
        owner_flat = [token for line in owner_lines for token in line["eva_clean"].split()]
        paragraph_rows.append({
            "paragraph_ordinal": len(paragraph_rows) + 1,
            "paragraph_id": paragraph_id,
            "physical_page": occurrences[0]["physical_page"],
            "register": occurrences[0]["register"],
            "topology_family": occurrences[0]["topology_family"],
            "independent_domain": macro_domain(occurrences[0]["topology_family"]),
            "target_event_count": len(occurrences),
            "target_loci": pipe(row["locus"] for row in occurrences),
            "paragraph_line_start": paragraph_lines[0]["line_number"],
            "paragraph_line_end": paragraph_lines[-1]["line_number"],
            "paragraph_line_count": len(paragraph_lines),
            "paragraph_token_count": len(flat),
            "target_paragraph_positions": pipe(str(index) for index, token in enumerate(flat, 1) if token == TARGET),
            "qok_prefix_token_count": sum(token.startswith("qok") for token in flat),
            "dy_suffix_token_count": sum(token.endswith("dy") for token in flat),
            "visible_owner_id": owner_id,
            "owner_line_start": owner_lines[0]["line_number"],
            "owner_line_end": owner_lines[-1]["line_number"],
            "owner_line_count": len(owner_lines),
            "owner_token_count": len(owner_flat),
            "target_owner_positions": pipe(str(index) for index, token in enumerate(owner_flat, 1) if token == TARGET),
            "raw_whole_paragraph": raw_paragraph,
            "target_masked_whole_paragraph": replace_exact(raw_paragraph, TARGET, "⟦TARGET⟧"),
            "raw_visible_owner_window": owner_text,
            "target_masked_owner_window": replace_exact(owner_text, TARGET, "⟦TARGET⟧"),
            "semantic_export": "NONE",
        })
    if len(paragraph_rows) != 2:
        raise RuntimeError("released paragraph host count changed")
    write_tsv(output_dir / OUTPUT_NAMES[1], paragraph_rows)

    candidate_reader_rows: list[dict[str, Any]] = []
    for paragraph in paragraph_rows:
        for candidate in candidates:
            display = f"⟦qokaldy:{candidate['candidate_display_de']}?⟧"
            candidate_reader_rows.append({
                "reader_ordinal": len(candidate_reader_rows) + 1,
                "paragraph_id": paragraph["paragraph_id"],
                "physical_page": paragraph["physical_page"],
                "candidate_id": candidate["candidate_id"],
                "candidate_display_de": candidate["candidate_display_de"],
                "raw_whole_paragraph": paragraph["raw_whole_paragraph"],
                "candidate_whole_paragraph": replace_exact(paragraph["raw_whole_paragraph"], TARGET, display),
                "raw_visible_owner_window": paragraph["raw_visible_owner_window"],
                "candidate_owner_window": replace_exact(paragraph["raw_visible_owner_window"], TARGET, display),
                "translation_status": "TARGET_INSERTION_ONLY__SURROUNDING_TEXT_UNTRANSLATED",
            })
    write_tsv(output_dir / OUTPUT_NAMES[2], candidate_reader_rows)

    base_profile_by_surface = {row["surface"]: row for row in source_profiles}
    q_surfaces = {f"q{surface}": surface for surface in base_profile_by_surface}
    q_rows_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        if row["surface"] in q_surfaces and row["locus"] not in source_loci:
            q_rows_by_surface[row["surface"]].append(row)

    q_contacts_by_surface: dict[str, list[dict[str, Any]]] = {}
    contact_rows: list[dict[str, Any]] = []
    for q_surface, rows in sorted(q_rows_by_surface.items()):
        contacts = collapse_contacts(rows, locus_to_paragraph)
        q_contacts_by_surface[q_surface] = contacts
        base_surface = q_surfaces[q_surface]
        for contact in contacts:
            contact_rows.append({
                "contact_ordinal": len(contact_rows) + 1,
                "q_surface": q_surface,
                "base_source_surface": base_surface,
                "base_source_families": base_profile_by_surface[base_surface]["source_families"],
                **contact,
                "q_component_export": "NONE",
            })
    if len(contact_rows) != 69 or len(q_contacts_by_surface) != 14:
        raise RuntimeError("q-source host cohort changed")
    write_tsv(output_dir / OUTPUT_NAMES[3], contact_rows)

    profile_rows: list[dict[str, Any]] = []
    for base_surface, base_profile in sorted(base_profile_by_surface.items()):
        q_surface = f"q{base_surface}"
        events = q_rows_by_surface.get(q_surface, [])
        contacts = q_contacts_by_surface.get(q_surface, [])
        domain_counts = Counter(contact["independent_domain"] for contact in contacts)
        profile_rows.append({
            "profile_ordinal": len(profile_rows) + 1,
            "base_source_surface": base_surface,
            "base_source_families": base_profile["source_families"],
            "q_complete_surface": q_surface,
            "q_event_count": len(events),
            "q_host_contact_count": len(contacts),
            "q_page_count": len({row["physical_page"] for row in events}),
            "running_event_count": sum(row["occurrence_kind"] == "RUNNING_EVENT" for row in events),
            "local_event_count": sum(row["occurrence_kind"] != "RUNNING_EVENT" for row in events),
            "figure_station_hosts": domain_counts["FIGURE_STATION_SYSTEM"],
            "plant_drug_hosts": domain_counts["PLANT_DRUG_MATERIAL"],
            "text_other_hosts": domain_counts["TEXT_OR_OTHER"],
            "domain_counts": pipe(f"{key}:{domain_counts[key]}" for key in sorted(domain_counts)),
            "host_purity": f6(max(domain_counts.values()) / len(contacts)) if contacts else "NA",
            "observed_q_complete_whole": "YES" if events else "NO",
            "q_component_export": "NONE",
        })
    write_tsv(output_dir / OUTPUT_NAMES[4], profile_rows)

    multi_profiles = [row for row in profile_rows if int(row["q_host_contact_count"]) >= 2]
    target_purity = float(next(row for row in multi_profiles if row["q_complete_surface"] == TARGET)["host_purity"])
    multi_rows: list[dict[str, Any]] = []
    for row in sorted(multi_profiles, key=lambda item: (-float(item["host_purity"]), item["q_complete_surface"])):
        purity = float(row["host_purity"])
        multi_rows.append({
            "purity_rank": 1 + sum(float(other["host_purity"]) > purity for other in multi_profiles),
            **row,
            "target_or_control": "TARGET" if row["q_complete_surface"] == TARGET else "CONTROL",
            "interpretation": "TEXT_ONLY_TARGET" if row["q_complete_surface"] == TARGET else "SOURCE_DERIVED_Q_WHOLE_CONTROL",
        })
    if len(multi_rows) != 8:
        raise RuntimeError("multi-host q-source cohort changed")
    write_tsv(output_dir / OUTPUT_NAMES[5], multi_rows)

    recurrent_qdy = {
        surface: rows for surface, rows in spine_by_surface.items()
        if surface.startswith("q") and surface.endswith("dy") and len(rows) >= 3
    }
    qdy_rows: list[dict[str, Any]] = []
    for surface, rows in sorted(recurrent_qdy.items()):
        page_topology = {(row["physical_page"], row["topology_family"]) for row in rows}
        qdy_rows.append({
            "surface": surface,
            "event_count": len(rows),
            "text_event_count": sum(row["topology_family"] == "TEXT_BLOCK" for row in rows),
            "text_event_purity": f6(sum(row["topology_family"] == "TEXT_BLOCK" for row in rows) / len(rows)),
            "page_topology_contact_count": len(page_topology),
            "text_page_topology_contact_count": sum(topology == "TEXT_BLOCK" for _, topology in page_topology),
            "text_page_topology_purity": f6(sum(topology == "TEXT_BLOCK" for _, topology in page_topology) / len(page_topology)),
            "running_event_count": sum(row["occurrence_kind"] == "RUNNING_EVENT" for row in rows),
            "local_event_count": sum(row["occurrence_kind"] != "RUNNING_EVENT" for row in rows),
            "target_or_control": "TARGET" if surface == TARGET else "CONTROL",
        })
    if len(qdy_rows) != 14:
        raise RuntimeError("recurrent q-dy control cohort changed")
    write_tsv(output_dir / OUTPUT_NAMES[6], qdy_rows)

    q_prefixed = {surface: rows for surface, rows in spine_by_surface.items() if surface.startswith("q")}
    q_running_only_types = sum(all(row["occurrence_kind"] == "RUNNING_EVENT" for row in rows) for rows in q_prefixed.values())
    q_total_events = sum(len(rows) for rows in q_prefixed.values())
    q_running_events = sum(
        row["occurrence_kind"] == "RUNNING_EVENT" for rows in q_prefixed.values() for row in rows
    )

    qdy_population = sum(int(row["event_count"]) for row in qdy_rows)
    qdy_text = sum(int(row["text_event_count"]) for row in qdy_rows)
    qdy_target = next(row for row in qdy_rows if row["surface"] == TARGET)
    qdy_event_p = hypergeom_tail(qdy_population, qdy_text, 3, 3)
    qdy_contact_population = sum(int(row["page_topology_contact_count"]) for row in qdy_rows)
    qdy_text_contacts = sum(int(row["text_page_topology_contact_count"]) for row in qdy_rows)
    qdy_contact_p = hypergeom_tail(qdy_contact_population, qdy_text_contacts, 2, 2)

    exact_three_q = {
        surface: rows for surface, rows in q_prefixed.items() if len(rows) == 3
    }
    exact_three_all_text = sum(
        all(row["topology_family"] == "TEXT_BLOCK" for row in rows)
        for rows in exact_three_q.values()
    )
    purity_p = sum(float(row["host_purity"]) >= target_purity for row in multi_profiles) / len(multi_profiles)

    target_contacts = q_contacts_by_surface[TARGET]
    target_host_ids = {row["host_id"] for row in target_contacts}
    control_contacts = [
        row for surface, contacts in q_contacts_by_surface.items() if surface != TARGET for row in contacts
    ]
    unique_control_hosts: dict[str, dict[str, Any]] = {}
    for row in control_contacts:
        previous = unique_control_hosts.get(row["host_id"])
        if previous and previous["independent_domain"] != row["independent_domain"]:
            raise RuntimeError("control host has conflicting domains")
        unique_control_hosts[row["host_id"]] = row
    disjoint_hosts = [row for host, row in unique_control_hosts.items() if host not in target_host_ids]
    disjoint_counts = Counter(row["independent_domain"] for row in disjoint_hosts)
    pair_denominator = math.comb(len(disjoint_hosts), 2)
    any_same_numerator = sum(math.comb(value, 2) for value in disjoint_counts.values())
    text_pair_numerator = math.comb(disjoint_counts["TEXT_OR_OTHER"], 2)
    target_pages = {row["physical_page"] for row in target_contacts}
    page_excluded_contacts = [row for row in control_contacts if row["physical_page"] not in target_pages]
    page_excluded_counts = Counter(row["independent_domain"] for row in page_excluded_contacts)

    qokaly_contacts = q_contacts_by_surface["qokaly"]
    qokaldy_text = sum(row["independent_domain"] == "TEXT_OR_OTHER" for row in target_contacts)
    qokaly_text = sum(row["independent_domain"] == "TEXT_OR_OTHER" for row in qokaly_contacts)
    qokaly_fisher = fisher_two_sided(
        qokaldy_text, len(target_contacts) - qokaldy_text,
        qokaly_text, len(qokaly_contacts) - qokaly_text,
    )

    triad_defaults = {
        "qokaldy": "davon / Heilmittel",
        "okaldy": "Bade-/Behandlungseintrag",
        "otaldy": "Wurzel-/Drogenartikel",
    }
    triad_rows: list[dict[str, Any]] = []
    triad_events: list[tuple[str, str]] = []
    for surface in ("qokaldy", "okaldy", "otaldy"):
        rows = [row for row in spine_by_surface[surface] if row["locus"] not in source_loci]
        contacts = collapse_contacts(rows, locus_to_paragraph)
        counts = Counter(row["independent_domain"] for row in contacts)
        if len(contacts) != 2 or len(counts) != 1:
            raise RuntimeError(f"three-surface triad changed: {surface}")
        for contact in contacts:
            triad_events.append((surface, contact["independent_domain"]))
        triad_rows.append({
            "surface": surface,
            "external_host_count": len(contacts),
            "external_host_ids": pipe(row["host_id"] for row in contacts),
            "external_pages": pipe(row["physical_page"] for row in contacts),
            "external_domain": next(iter(counts)),
            "working_default_de": triad_defaults[surface],
            "source_native_family_status": "NO_Q_SOURCE_LABEL_OBSERVED" if surface == TARGET else "AQABBA_SOURCE_LABEL_PRESENT",
            "component_export": "NONE",
        })
    keyed_credit = 0.0
    pooled_credit = 0.0
    for index, (surface, domain) in enumerate(triad_events):
        training = [event for other, event in enumerate(triad_events) if other != index]
        keyed_credit += model_credit(domain, [value for key, value in training if key == surface])
        pooled_credit += model_credit(domain, [value for _, value in training])
    domain_multiset = ["FIGURE_STATION_SYSTEM"] * 2 + ["PLANT_DRUG_MATERIAL"] * 2 + ["TEXT_OR_OTHER"] * 2
    assignments = set(itertools.permutations(domain_multiset))
    triad_extreme = 0
    for assignment in assignments:
        pairs = (assignment[0:2], assignment[2:4], assignment[4:6])
        if all(pair[0] == pair[1] for pair in pairs) and len({pair[0] for pair in pairs}) == 3:
            triad_extreme += 1
    triad_p = triad_extreme / len(assignments)
    write_tsv(output_dir / OUTPUT_NAMES[8], triad_rows)

    exact_tests = [
        {
            "test_id": "QDY_EVENT_TEXT_HYPERGEOMETRIC",
            "unit": "EVENT",
            "universe_n": qdy_population,
            "success_n": qdy_text,
            "target_n": 3,
            "target_success": 3,
            "statistic": "TEXT_PURITY_1.000000",
            "p_value": f6(qdy_event_p),
            "selection_role": "DIAGNOSTIC_ONLY__WITHIN_PAGE_REPEAT",
            "result": "APPARENT_CONCENTRATION",
        },
        {
            "test_id": "QDY_PAGE_TOPOLOGY_TEXT_HYPERGEOMETRIC",
            "unit": "SURFACE_PAGE_TOPOLOGY_CONTACT",
            "universe_n": qdy_contact_population,
            "success_n": qdy_text_contacts,
            "target_n": 2,
            "target_success": 2,
            "statistic": "TEXT_PURITY_1.000000",
            "p_value": f6(qdy_contact_p),
            "selection_role": "CLUSTER_SENSITIVITY",
            "result": "SUGGESTIVE_NOT_STRONG",
        },
        {
            "test_id": "EXACT3_Q_SURFACE_EMPIRICAL",
            "unit": "COMPLETE_SURFACE",
            "universe_n": len(exact_three_q),
            "success_n": exact_three_all_text,
            "target_n": 1,
            "target_success": 1,
            "statistic": "TARGET_UNIQUE_ALL_TEXT",
            "p_value": f6(exact_three_all_text / len(exact_three_q)),
            "selection_role": "MATCHED_FREQUENCY_DESCRIPTION",
            "result": "TARGET_RANK_1",
        },
        {
            "test_id": "SOURCE_Q_MULTIHOST_PURITY_RANK",
            "unit": "Q_COMPLETE_SURFACE",
            "universe_n": len(multi_profiles),
            "success_n": sum(float(row["host_purity"]) >= target_purity for row in multi_profiles),
            "target_n": 1,
            "target_success": 1,
            "statistic": "PURITY_RANK_1_OF_8",
            "p_value": f6(purity_p),
            "selection_role": "PRIMARY_QS_CONTROL",
            "result": "DESCRIPTIVE_ONLY",
        },
        {
            "test_id": "TARGET_EXCLUDED_ANY_SAME_DOMAIN_PAIR",
            "unit": "UNIQUE_HOST_CLUSTER_PAIR",
            "universe_n": pair_denominator,
            "success_n": any_same_numerator,
            "target_n": 1,
            "target_success": 1,
            "statistic": f"PAIR_NUMERATOR_{any_same_numerator}_OF_{pair_denominator}",
            "p_value": f6(any_same_numerator / pair_denominator),
            "selection_role": "PREDECLARED_DOMAIN_PURITY_NULL",
            "result": "ANY_PURE_DOMAIN_COMMON",
        },
        {
            "test_id": "TARGET_EXCLUDED_TEXT_PAIR_POSTHOC",
            "unit": "UNIQUE_HOST_CLUSTER_PAIR",
            "universe_n": pair_denominator,
            "success_n": text_pair_numerator,
            "target_n": 1,
            "target_success": 1,
            "statistic": f"TEXT_PAIR_NUMERATOR_{text_pair_numerator}_OF_{pair_denominator}",
            "p_value": f6(text_pair_numerator / pair_denominator),
            "selection_role": "POSTHOC_DIRECTION_ONLY",
            "result": "PAGE_CONFOUNDED",
        },
        {
            "test_id": "QOKALY_NEAREST_WHOLE_FISHER",
            "unit": "PARAGRAPH_OR_LOCAL_HOST",
            "universe_n": len(target_contacts) + len(qokaly_contacts),
            "success_n": qokaldy_text + qokaly_text,
            "target_n": len(target_contacts),
            "target_success": qokaldy_text,
            "statistic": f"TARGET_2_0_CONTROL_{qokaly_text}_{len(qokaly_contacts)-qokaly_text}",
            "p_value": f6(qokaly_fisher),
            "selection_role": "NEAREST_COMPLETE_WHOLE_CONTROL",
            "result": "NO_DISCRIMINATION",
        },
        {
            "test_id": "THREE_SURFACE_DOMAIN_ASSIGNMENT_EXACT",
            "unit": "SIX_HOST_DOMAIN_ASSIGNMENT",
            "universe_n": len(assignments),
            "success_n": triad_extreme,
            "target_n": 1,
            "target_success": 1,
            "statistic": f"KEYED_{f6(keyed_credit/6)}_POOLED_{f6(pooled_credit/6)}",
            "p_value": f6(triad_p),
            "selection_role": "TARGETED_GDT797_FOLLOWUP",
            "result": "THREE_LEARNED_WHOLES_FAVOURED",
        },
        {
            "test_id": "ALL_Q_RUNNING_ONLY_BASE_RATE",
            "unit": "COMPLETE_SURFACE_TYPE",
            "universe_n": len(q_prefixed),
            "success_n": q_running_only_types,
            "target_n": 1,
            "target_success": 1,
            "statistic": f"RUNNING_EVENTS_{q_running_events}_OF_{q_total_events}",
            "p_value": "NOT_APPLICABLE",
            "selection_role": "DEPLOYMENT_BASE_RATE",
            "result": "RUNNING_ONLY_NONDIAGNOSTIC",
        },
        {
            "test_id": "TARGET_PAGE_EXCLUSION_SENSITIVITY",
            "unit": "SURFACE_HOST_CONTACT",
            "universe_n": len(page_excluded_contacts),
            "success_n": page_excluded_counts["TEXT_OR_OTHER"],
            "target_n": 2,
            "target_success": 2,
            "statistic": pipe(f"{key}:{page_excluded_counts[key]}" for key in sorted(page_excluded_counts)),
            "p_value": "NOT_IDENTIFIABLE",
            "selection_role": "MANDATORY_PAGE_CONFOUND_CHECK",
            "result": "ZERO_TEXT_CONTROLS_AFTER_F66_F76_REMOVAL",
        },
    ]
    write_tsv(output_dir / OUTPUT_NAMES[7], exact_tests)

    nearest_rows: list[dict[str, Any]] = []
    for surface, rows in sorted(spine_by_surface.items(), key=lambda item: (levenshtein(TARGET, item[0]), item[0])):
        distance = levenshtein(TARGET, surface)
        if distance > 2:
            continue
        contacts = collapse_contacts([row for row in rows if row["locus"] not in source_loci], locus_to_paragraph)
        counts = Counter(row["independent_domain"] for row in contacts)
        nearest_rows.append({
            "edit_distance": distance,
            "surface": surface,
            "event_count": len(rows),
            "page_count": len({row["physical_page"] for row in rows}),
            "external_host_count": len(contacts),
            "figure_station_hosts": counts["FIGURE_STATION_SYSTEM"],
            "plant_drug_hosts": counts["PLANT_DRUG_MATERIAL"],
            "text_other_hosts": counts["TEXT_OR_OTHER"],
            "running_event_count": sum(row["occurrence_kind"] == "RUNNING_EVENT" for row in rows),
            "local_event_count": sum(row["occurrence_kind"] != "RUNNING_EVENT" for row in rows),
            "meaning_transfer_credit": "ZERO",
        })
    write_tsv(output_dir / OUTPUT_NAMES[9], nearest_rows)

    evidence = {
        "QREF": (
            "3/3 released events are text-internal|0/10 line-initial|f66 repeats after 17 intervening tokens|f33 has all-reader exact okaldy qokaldy adjacency|historical glossary comparators attest cross-reference fields",
            "no antecedent is independently identified at nine of ten lines",
            "RETAIN_C0_TIED",
            "C0_TIED",
        ),
        "QREM": (
            "flexible middle/final positions|four inherited section codes|f66 repetition|learned drug/compound heads are historically plausible",
            "no released material owner|no identified remedy or compound",
            "RETAIN_C0_TIED",
            "C0_TIED",
        ),
        "QAPP": (
            "10/10 running-line deployment|2/10 line-final",
            "0/10 line-initial|three released legacy positions disagree|no repeated clause frame",
            "HOLD",
            "LOW",
        ),
        "QSAME": (
            "complete surfaces differ by one EVA character",
            "okaldy host model predicts 0/2 qokaldy hosts|no q-prefixed source label exists",
            "REJECT_PORTABILITY",
            "REJECTED",
        ),
        "QOPAQUE": (
            "requires no unsupported lexical identity",
            "supplies no practical content",
            "SURVIVES_PRIMARY",
            "HIGH_ARCHITECTURE_LOW_SEMANTICS",
        ),
    }
    adjudication_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        support, counter, decision, confidence = evidence[candidate["candidate_id"]]
        adjudication_rows.append({
            **candidate,
            "supporting_observations": support,
            "counterevidence": counter,
            "supporting_note_count_nondecisional": len(support.split("|")),
            "counterevidence_note_count_nondecisional": len(counter.split("|")),
            "unmatched_note_balance_nondecisional": len(support.split("|")) - len(counter.split("|")),
            "matched_independent_axis_score": "NOT_ESTABLISHED",
            "evidence_winner": "NO",
            "decision": decision,
            "confidence": confidence,
            "component_export": "NONE",
            "confirmed_lexeme": "NO",
        })
    write_tsv(output_dir / OUTPUT_NAMES[10], adjudication_rows)

    paragraph_by_locus: dict[str, str] = {}
    for paragraph in paragraph_rows:
        for locus in paragraph["target_loci"].split("|"):
            paragraph_by_locus[locus] = paragraph["paragraph_id"]
    renderer_rows: list[dict[str, Any]] = []
    for atlas in atlas_rows:
        count = int(atlas["exact_whole_reader_count"])
        if atlas["direct_okaldy_adjacency"] == "YES":
            antecedent = "DIRECT_LEFT_OKALDY_WHOLE"
        elif atlas["page"] == "f66r":
            antecedent = "SAME_PARAGRAPH_QOKALDY_REPEAT"
        else:
            antecedent = "NO_IDENTIFIED_ANTECEDENT"
        display_token = "⟦qokaldy:davon?/Heilmittel?⟧"
        renderer_rows.append({
            "renderer_ordinal": len(renderer_rows) + 1,
            "surface": TARGET,
            "page": atlas["page"],
            "locus": atlas["locus"],
            "paragraph_id": paragraph_by_locus.get(atlas["locus"], "INHERITED_LINE_ONLY"),
            "previous_v99r7_value": atlas["previous_v99r7_value"],
            "gdt798_working_default_de": "davon / Heilmittel",
            "display": display_token,
            "rendered_line": replace_exact(atlas["raw_line"], TARGET, display_token),
            "confidence": {3: "C0_ALL3_WHOLE", 2: "C0_TWO_OF_THREE_WHOLE", 1: "C0_ZL_ONLY_WHOLE"}[count],
            "evidence": "text-internal deployment; multiple within-line positions; bounded complete-whole reference/remedy tie",
            "antecedent_status": antecedent,
            "counterevidence": "text topology is page-confounded; no referent is independently decoded",
            "scope": "ENUMERATED_CACHE_CELL_ONLY",
            "renderer_precedence": "GDT798_CONTEXTUAL_WHOLE_TIE_OVER_UNKNOWN",
            "component_export": "ZERO",
            "confirmed_lexeme": "NO",
        })
    write_tsv(output_dir / OUTPUT_NAMES[11], renderer_rows)

    q_source_labels = [row for row in source_atlas if row["complete_label_surface"].startswith("q")]
    daqabba_rows = [
        row for row in source_atlas
        if "DAQABBA" in {row.get("canonical_boundary_family", ""), row.get("canonical_compact_family", "")}
    ]
    scope_rows = [
        {
            "audit_id": "GDT798_EXACT_LOCUS_CROSS_QUERY",
            "source": CROSS.relative_to(ROOT).as_posix(),
            "selector": "locus",
            "allowed_count": 10,
            "selected_count": cross_stats["selected"],
            "sealed_rejected_before_materialization": cross_stats["skipped_forbidden"],
            "other_skipped": cross_stats["skipped_not_allowed"],
            "new_page_or_image": "NO",
            "finding": "TEN_ENUMERATED_LINES_ONLY",
        },
        {
            "audit_id": "GDT798_RELEASED_SPINE",
            "source": SPINE.relative_to(ROOT).as_posix(),
            "selector": "surface=qokaldy",
            "allowed_count": 3,
            "selected_count": len(primary_occurrences),
            "sealed_rejected_before_materialization": "NOT_APPLICABLE",
            "other_skipped": len(spine) - len(primary_occurrences),
            "new_page_or_image": "NO",
            "finding": "TWO_PARAGRAPH_HOSTS",
        },
        {
            "audit_id": "GDT798_INHERITED_LINE_CACHE",
            "source": G734_READER.relative_to(ROOT).as_posix(),
            "selector": "exact ZL3b whole in ten fixed lines",
            "allowed_count": 10,
            "selected_count": len(atlas_rows),
            "sealed_rejected_before_materialization": "NOT_APPLICABLE_PREVALIDATED_CACHE",
            "other_skipped": len(cache) - len(atlas_rows),
            "new_page_or_image": "NO",
            "finding": "TEXT_LINE_CONTEXT_ONLY__NO_NEW_VISUAL_REVIEW",
        },
        {
            "audit_id": "GDT798_DAQABBA_CORRECTION",
            "source": G795_ATLAS.relative_to(ROOT).as_posix(),
            "selector": "source-native q-prefix and DAQABBA",
            "allowed_count": 101,
            "selected_count": len(source_atlas),
            "sealed_rejected_before_materialization": "NOT_APPLICABLE_PREVALIDATED_ATLAS",
            "other_skipped": 0,
            "new_page_or_image": "NO",
            "finding": f"Q_PREFIXED_SOURCE_LABELS_{len(q_source_labels)}__DAQABBA_ROWS_{len(daqabba_rows)}__NOT_SOURCE_NATIVE",
        },
    ]
    if q_source_labels or daqabba_rows:
        raise RuntimeError("DAQABBA correction premise changed")
    write_tsv(output_dir / OUTPUT_NAMES[12], scope_rows)

    result = {
        "experiment_id": "GDT798",
        "status": STATUS,
        "target": {
            "surface": TARGET,
            "cache_cells": len(atlas_rows),
            "pages": len({row["page"] for row in atlas_rows}),
            "released_events": len(primary_occurrences),
            "released_paragraph_hosts": len(paragraph_rows),
            "exact_reader_wholes": sum(int(row["exact_whole_reader_count"]) for row in atlas_rows),
            "reader_opportunities": len(atlas_rows) * 3,
            "line_initial": sum(row["position_class"] == "INITIAL" for row in atlas_rows),
            "line_final": sum(row["position_class"] == "FINAL" for row in atlas_rows),
            "direct_okaldy_adjacencies": sum(row["direct_okaldy_adjacency"] == "YES" for row in atlas_rows),
        },
        "controls": {
            "source_surfaces": len(source_profiles),
            "observed_q_source_wholes": len(q_contacts_by_surface),
            "q_source_host_contacts": len(contact_rows),
            "q_source_multihost_surfaces": len(multi_rows),
            "qokaldy_purity_rank": "1_OF_8",
            "qokaldy_purity_empirical_p": f6(purity_p),
            "all_q_types": len(q_prefixed),
            "all_q_running_only_types": q_running_only_types,
            "all_q_events": q_total_events,
            "all_q_running_events": q_running_events,
            "page_excluded_text_control_contacts": page_excluded_counts["TEXT_OR_OTHER"],
        },
        "triad": {
            "surface_keyed_credit": f6(keyed_credit / 6),
            "pooled_credit": f6(pooled_credit / 6),
            "exact_assignments": len(assignments),
            "as_extreme": triad_extreme,
            "p_value": f6(triad_p),
        },
        "decision": {
            "selected_c0_complete_whole": "NONE__NO_EVIDENCE_WINNER",
            "tied_c0_complete_wholes": ["qokaldy=davon", "qokaldy=Heilmittel"],
            "practical_display_order": ["davon", "Heilmittel"],
            "same_as_okaldy": "REJECT_PORTABILITY",
            "opaque_null": "SURVIVES",
            "daqabba_source_family": "NOT_SOURCE_NATIVE__UNOBSERVED_IN_101_SOURCE_ATLAS",
            "component_exports": 0,
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
        },
        "scope": {
            "new_pages": 0,
            "new_images": 0,
            "sealed_rows_materialized_by_executable_build": 0,
            "released_visually_reviewed_target_pages_used": ["f66r", "f76r"],
            "released_control_spine_pages_available": len({row["physical_page"] for row in spine}),
            "released_qs_control_pages_touched": sorted({row["physical_page"] for row in contact_rows}),
            "released_qs_control_page_count": len({row["physical_page"] for row in contact_rows}),
            "inherited_cache_line_pages_not_visually_interpreted_here": 6,
        },
        "outputs": list(OUTPUT_NAMES),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({"experiment_id": "GDT798", "status": result["status"], "output_dir": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
