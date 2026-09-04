#!/usr/bin/env python3
"""Build GDT797: AQABBA complete-surface host-domain discrimination."""

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
BASE = ROOT / "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
LOCK = SRC / "SOURCE_LOCK.tsv"
CONTACT_SPECS = SRC / "TARGET_CONTACT_SPECS.tsv"
DOMAIN_MAP = SRC / "DOMAIN_MAP.tsv"
MODEL_SPECS = SRC / "MODEL_SPECS.tsv"

G795 = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts"
G795_ATLAS = G795 / "GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
G795_RECURRENT = G795 / "GDT795_11_RECURRENT_FAMILY_SIGNATURES.tsv"
G791 = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts"
SPINE = G791 / "GDT791_5866_OCCURRENCE_SPINE.tsv"
LINES = G791 / "GDT791_1007_LINE_OWNER_ATLAS.tsv"
G581_LOCAL = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_744_local_card_hosts.tsv"
G790_LABELS = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_27_LABEL_OWNER_ATLAS.tsv"
G796_STATUS = ROOT / "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/artifacts/GDT796_HISTORICAL_FAMILY_STATUS_CENSUS.tsv"
G796_ADJ = ROOT / "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/artifacts/GDT796_CANDIDATE_ADJUDICATION.tsv"
G734_READER = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
CROSS = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
SOURCE_STA = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"

CROSS_LOCI = (
    "f18r.8", "f70v2.17", "f72r2.27", "f75r.27", "f82r.37", "f88r.12", "f95v1.4",
)
RECURRENT_FAMILIES = (
    "AQAB", "AQABA", "AQABAB", "AQABAC", "AQABAG", "AQABBA",
    "AQABLA", "AQACAB", "AQACABBA", "AQAFA", "AQKA|ACA",
)
BRANCH_CONTROL_FAMILIES = ("AQAB", "AQABA")

OUTPUT_NAMES = (
    "GDT797_7_TARGET_CONTACT_ATLAS.tsv",
    "GDT797_2_TARGET_SURFACE_HOST_PROFILES.tsv",
    "GDT797_PARAGRAPH_MASKED_CANDIDATE_READERS.tsv",
    "GDT797_RECURRENT_FAMILY_EXTERNAL_CONTACT_ATLAS.tsv",
    "GDT797_11_FAMILY_SURFACE_DOMAIN_TOURNAMENT.tsv",
    "GDT797_71_SOURCE_SURFACE_HOST_PROFILES.tsv",
    "GDT797_OK_OT_BRANCH_SENSITIVITY.tsv",
    "GDT797_MODEL_ADJUDICATION.tsv",
    "GDT797_6_CONTEXTUAL_WHOLE_RENDERER.tsv",
    "GDT797_SCOPE_AND_GUARD_AUDIT.tsv",
    "RESULT.json",
)

STATUS = (
    "PARTIAL__6_PRIMARY_EXACT_EVENTS__4_EXTERNAL_HOST_UNITS__"
    "4_OF_4_SURFACE_DOMAIN_SPLIT__3_CAPACITY_QUALIFIED_FAMILIES__"
    "AQABBA_UNIQUE_POSITIVE_LOHO_GAIN__MICRO_EXACT_P_0_333333__"
    "71_SOURCE_SURFACES__2_TARGET_NONCELESTIAL_MINIMAL_BRIDGES__"
    "OK_OT_CONTROL_DIRECTION_WEAK__OKALDY_BATH_ENTRY_C0__"
    "OTALDY_ROOT_DRUG_ARTICLE_C0__2_LEGACY_ACTION_CELLS_QUARANTINED__"
    "OPAQUE_NULL_SURVIVES__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
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
            raise RuntimeError(f"invalid source-lock path: {row['path']}")
        path = ROOT / relative
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def guarded_query(
    source: Path,
    columns: str,
    expected: dict[str, int],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", source.relative_to(ROOT).as_posix(),
        "--selector", "locus",
    ]
    for locus in CROSS_LOCI:
        command.extend(("--allow", locus))
    command.extend((
        "--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded query failed: {source}")
    matches = re.findall(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if len(matches) != 1:
        raise RuntimeError("guard statistics missing or duplicated")
    stats = {key: int(value) for key, value in json.loads(matches[0]).items()}
    if stats != expected:
        raise RuntimeError(f"guard statistics changed: {stats} != {expected}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["locus"].startswith("f84") for row in rows):
        raise RuntimeError("sealed row materialized")
    return rows, stats


def pipe(values: Iterable[str]) -> str:
    result: list[str] = []
    for value in values:
        if value and value != "NONE" and value not in result:
            result.append(value)
    return "|".join(result) if result else "NONE"


def f6(value: float) -> str:
    return f"{value:.6f}"


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


def replace_token(text: str, target: str, replacement: str) -> str:
    return " ".join(replacement if token == target else token for token in text.split())


def mode_credit(actual: str, training: Sequence[str]) -> float:
    counts = Counter(training)
    maximum = max(counts.values())
    modes = [value for value, count in counts.items() if count == maximum]
    return 1.0 / len(modes) if actual in modes else 0.0


def family_metrics(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {
            "contact_count": 0, "surface_count": 0, "domain_count": 0,
            "surface_counts": "NONE", "domain_counts": "NONE",
            "surface_purity": 0.0, "pooled_purity": 0.0,
            "loo_coverage": 0, "keyed_credit": 0.0, "pooled_credit": 0.0,
            "keyed_accuracy": 0.0, "pooled_accuracy": 0.0, "loo_gain": 0.0,
            "capacity": False,
        }
    surface_counts = Counter(row["surface"] for row in rows)
    domain_counts = Counter(row["independent_domain"] for row in rows)
    surface_majorities = sum(
        max(Counter(row["independent_domain"] for row in rows if row["surface"] == surface).values())
        for surface in surface_counts
    )
    coverage = 0
    keyed_credit = 0.0
    pooled_credit = 0.0
    for index, target in enumerate(rows):
        training = [row for other, row in enumerate(rows) if other != index]
        keyed = [row["independent_domain"] for row in training if row["surface"] == target["surface"]]
        if not keyed:
            continue
        coverage += 1
        keyed_credit += mode_credit(target["independent_domain"], keyed)
        pooled_credit += mode_credit(target["independent_domain"], [row["independent_domain"] for row in training])
    capacity = (
        len(rows) >= 4
        and sum(count >= 2 for count in surface_counts.values()) >= 2
        and len(domain_counts) >= 2
        and coverage >= 4
    )
    return {
        "contact_count": len(rows), "surface_count": len(surface_counts),
        "domain_count": len(domain_counts),
        "surface_counts": pipe(f"{key}:{surface_counts[key]}" for key in sorted(surface_counts)),
        "domain_counts": pipe(f"{key}:{domain_counts[key]}" for key in sorted(domain_counts)),
        "surface_purity": surface_majorities / len(rows),
        "pooled_purity": max(domain_counts.values()) / len(rows),
        "loo_coverage": coverage, "keyed_credit": keyed_credit,
        "pooled_credit": pooled_credit,
        "keyed_accuracy": keyed_credit / coverage if coverage else 0.0,
        "pooled_accuracy": pooled_credit / coverage if coverage else 0.0,
        "loo_gain": (keyed_credit - pooled_credit) / coverage if coverage else 0.0,
        "capacity": capacity,
    }


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1, row2, col1 = a + b, c + d, a + c
    total = row1 + row2

    def probability(x: int) -> float:
        return math.comb(col1, x) * math.comb(total - col1, row1 - x) / math.comb(total, row1)

    low, high = max(0, row1 - (total - col1)), min(row1, col1)
    observed = probability(a)
    return min(1.0, sum(probability(x) for x in range(low, high + 1) if probability(x) <= observed + 1e-15))


def alternate_status(surface: str, cross: dict[str, str], local: bool) -> tuple[int, str]:
    readings = [cross[key].strip() for key in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
    hits = [reading == surface for reading in readings] if local else [surface in reading.split() for reading in readings]
    count = sum(hits)
    names = {
        3: "ALL_THREE_EXACT_WHOLE", 2: "TWO_OF_THREE_EXACT_WHOLE",
        1: "ZL3B_ONLY_EXACT_WHOLE" if hits[0] else "ONE_ALTERNATE_ONLY_EXACT_WHOLE",
        0: "NO_READER_EXACT_WHOLE",
    }
    return count, names[count]


def sta_support(locus: str, rows: list[dict[str, str]]) -> tuple[int, str]:
    locus_rows = [row for row in rows if row["locus"] == locus]
    editions = ("ZL3b", "IT2a", "RF1b")
    support = []
    for edition in editions:
        families = [row["primary_sta_families"] for row in locus_rows if row["edition"] == edition]
        support.append("AQABBA" in families)
    return sum(support), pipe(edition for edition, hit in zip(editions, support) if hit)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    specs = read_tsv(CONTACT_SPECS)
    if len(specs) != 7 or {row["locus"] for row in specs} != set(CROSS_LOCI):
        raise RuntimeError("target contact specification changed")
    models = {row["model_id"]: row for row in read_tsv(MODEL_SPECS)}
    if set(models) != {"FAMILY_POOLED_STATUS", "SURFACE_SPECIFIC_LEARNED_ENTRIES", "OPAQUE_RECURRENCE"}:
        raise RuntimeError("candidate model set changed")
    domains = {row["topology_family"]: row["independent_domain"] for row in read_tsv(DOMAIN_MAP)}

    atlas = read_tsv(G795_ATLAS)
    recurrent = read_tsv(G795_RECURRENT)
    spine = read_tsv(SPINE)
    lines = read_tsv(LINES)
    local_hosts = {row["locus"]: row for row in read_tsv(G581_LOCAL)}
    deep_labels = {row["locus"]: row for row in read_tsv(G790_LABELS)}
    historical_status = read_tsv(G796_STATUS)
    historical_adjudication = read_tsv(G796_ADJ)
    prior_reader = {row["locus"]: row for row in read_tsv(G734_READER)}
    cross_rows, cross_stats = guarded_query(
        CROSS,
        "page,locus,zl3b_clean,it2a_clean,rf1b_clean",
        {"selected": 7, "skipped_forbidden": 98, "skipped_not_allowed": 5281},
    )
    sta_rows, sta_stats = guarded_query(
        SOURCE_STA,
        "source_group_id,edition,locus,source_group_index,source_group_count,left_separator,right_separator,sta_group_raw,primary_sta_codes,primary_sta_families,primary_sta_symbol_count,alternative_site_count,nearest_basic_eva_primary",
        {"selected": 93, "skipped_forbidden": 2122, "skipped_not_allowed": 113255},
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}

    if len(atlas) != 101 or len(spine) != 5866 or len(lines) != 1007:
        raise RuntimeError("predecessor spine capacity changed")
    if tuple(row["canonical_boundary_family"] for row in recurrent) != RECURRENT_FAMILIES:
        raise RuntimeError("recurrent family registry changed")

    locus_to_paragraph, paragraphs = build_paragraphs(lines)
    line_by_locus = {row["locus"]: row for row in lines}
    spine_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        spine_by_locus[row["locus"]].append(row)
    atlas_by_locus = {row["locus"]: row for row in atlas}

    contact_rows: list[dict[str, Any]] = []
    for ordinal, spec in enumerate(specs, 1):
        locus = spec["locus"]
        surface = spec["target_surface"]
        line = line_by_locus[locus]
        matches = [row for row in spine_by_locus[locus] if row["surface"] == surface]
        sensitivity = spec["contact_class"] == "READER_BOUNDARY_SENSITIVITY"
        if sensitivity:
            if matches or line["eva_clean"] != "qokchor ckhol olody okal dy dary":
                raise RuntimeError("f18 boundary sensitivity changed")
            occurrence = {
                "occurrence_id": "BOUND_SPAN:f18r.8:4-5",
                "occurrence_kind": "RUNNING_EVENT",
                "source_selector": line["source_selector"],
                "physical_page": line["physical_page"],
                "register": line["register"],
                "topology_family": line["topology_family"],
                "token_ordinal_in_line": "4-5",
                "context_owner_id": line["context_scope"],
            }
        else:
            if len(matches) != 1:
                raise RuntimeError(f"expected one exact occurrence at {locus}, found {len(matches)}")
            occurrence = matches[0]
        if occurrence["occurrence_kind"] != spec["expected_occurrence_kind"]:
            raise RuntimeError(f"occurrence kind changed at {locus}")
        domain = domains[occurrence["topology_family"]]
        if domain != spec["expected_domain"]:
            raise RuntimeError(f"host domain changed at {locus}: {domain}")

        if occurrence["occurrence_kind"] == "RUNNING_EVENT":
            paragraph_id = locus_to_paragraph[locus]
            context_unit = paragraph_id
            context_lines = paragraphs[paragraph_id]
            raw_context = paragraph_text(context_lines)
            line_span = f"{context_lines[0]['locus']}--{context_lines[-1]['locus']}"
            owner_id = occurrence["context_owner_id"]
            owner_description = f"{occurrence['topology_family']} complete paragraph"
        else:
            paragraph_id = "NA"
            context_unit = f"LOCAL:{locus}"
            raw_context = surface
            line_span = locus
            if locus in atlas_by_locus:
                source = atlas_by_locus[locus]
                owner_id = source["array_id"]
                owner_description = f"radial member {source['kluge_a_member']}A; slot {source['slot_index']}"
            elif locus in deep_labels:
                source = deep_labels[locus]
                owner_id = source["component_id"]
                owner_description = f"{source['owner_class']}; {source['local_position']}; {source['attachment_relation']}"
            elif locus in local_hosts:
                source = local_hosts[locus]
                owner_id = source["local_card_host_key"]
                owner_description = source["owner_de"]
            else:
                raise RuntimeError(f"no visible owner source for {locus}")

        exact_count, reading_status = alternate_status(
            surface, cross_by_locus[locus], occurrence["occurrence_kind"] != "RUNNING_EVENT"
        )
        family_support, family_editions = sta_support(locus, sta_rows)
        masked = replace_token(raw_context, surface, f"⟦{surface}:MASKED⟧")
        if sensitivity:
            masked = raw_context.replace("okal dy", "⟦okal dy:BOUNDARY_SENSITIVITY⟧")
        source_locus = next(
            row["locus"] for row in atlas
            if row["canonical_boundary_family"] == "AQABBA"
            and row["complete_label_surface"] == surface
        )
        contact_rows.append({
            "contact_ordinal": ordinal,
            "contact_id": spec["contact_id"],
            "target_surface": surface,
            "canonical_boundary_family": "AQABBA",
            "contact_class": spec["contact_class"],
            "primary_analysis": spec["primary_analysis"],
            "source_family_locus": source_locus,
            "occurrence_id": occurrence["occurrence_id"],
            "occurrence_kind": occurrence["occurrence_kind"],
            "source_selector": occurrence["source_selector"],
            "physical_page": occurrence["physical_page"],
            "register": occurrence["register"],
            "topology_family": occurrence["topology_family"],
            "independent_domain": domain,
            "locus": locus,
            "token_ordinal_in_line": occurrence["token_ordinal_in_line"],
            "paragraph_id": paragraph_id,
            "context_unit_id": context_unit,
            "line_span": line_span,
            "visible_owner_id": owner_id,
            "visible_owner_description": owner_description,
            "raw_whole_context": raw_context,
            "target_masked_whole_context": masked,
            "zl3b_clean": cross_by_locus[locus]["zl3b_clean"],
            "it2a_clean": cross_by_locus[locus]["it2a_clean"],
            "rf1b_clean": cross_by_locus[locus]["rf1b_clean"],
            "source_family_single_group_support": family_support,
            "source_family_supporting_editions": family_editions,
            "alternate_reader_exact_whole_count": exact_count,
            "alternate_reader_status": reading_status,
            "alternate_reader_credit": "SAME_MANUSCRIPT_READING_ONLY",
            "working_default_de": spec["working_default_de"],
            "evidence_role": spec["evidence_role"],
            "counterevidence": (
                "not an exact ZL3b whole; alternate boundary sensitivity only"
                if sensitivity else
                "host domain does not identify plaintext; alternate readers may split or alter the whole"
            ),
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        })
    write_tsv(out / OUTPUT_NAMES[0], contact_rows)

    primary_external = [
        row for row in contact_rows
        if row["contact_class"] == "EXTERNAL_EXACT_WHOLE" and row["primary_analysis"] == "YES"
    ]
    surface_profiles: list[dict[str, Any]] = []
    for surface, domain_name, display in (
        ("okaldy", "FIGURE_STATION_SYSTEM", "Bade-/Behandlungseintrag"),
        ("otaldy", "PLANT_DRUG_MATERIAL", "Wurzel-/Drogenartikel"),
    ):
        source_rows = [row for row in contact_rows if row["target_surface"] == surface and row["contact_class"] == "SOURCE_FAMILY_LABEL"]
        external = [row for row in primary_external if row["target_surface"] == surface]
        sensitivity_rows = [row for row in contact_rows if row["target_surface"] == surface and row["contact_class"] == "READER_BOUNDARY_SENSITIVITY"]
        counts = Counter(row["independent_domain"] for row in external)
        local_anchors = [row for row in external if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"]
        running_hosts = [row for row in external if row["occurrence_kind"] == "RUNNING_EVENT"]
        if counts != Counter({domain_name: 2}):
            raise RuntimeError(f"target surface host profile changed: {surface}")
        surface_profiles.append({
            "target_surface": surface,
            "source_label_count": len(source_rows),
            "source_label_domain": pipe(row["independent_domain"] for row in source_rows),
            "external_host_unit_count": len(external),
            "external_fine_topologies": pipe(row["topology_family"] for row in external),
            "external_domain_counts": pipe(f"{key}:{counts[key]}" for key in sorted(counts)),
            "external_domain_mode": counts.most_common(1)[0][0],
            "external_domain_purity": f6(max(counts.values()) / len(external)),
            "exact_local_owner_anchor": pipe(row["visible_owner_description"] for row in local_anchors),
            "separate_running_paragraphs": pipe(row["paragraph_id"] for row in running_hosts),
            "boundary_sensitivity_count": len(sensitivity_rows),
            "boundary_sensitivity_domain": pipe(row["independent_domain"] for row in sensitivity_rows),
            "conservative_complete_whole_class": domain_name,
            "bold_contextual_working_default_de": display,
            "confidence": "C0_TWO_HOSTS_ONE_EXACT_VISIBLE_OWNER",
            "evidence": "two external host units share one fixed macro-domain; one is an exact visible-owner label",
            "counterevidence": (
                "only two external hosts; f18 IT2a-only fusion conflicts with a narrow bath meaning"
                if surface == "okaldy" else
                "only two external hosts; unity requires the prespecified herbal-plus-pharma macro-domain"
            ),
            "renderer_license": "ENUMERATED_CONTEXTUAL_COMPLETE_WHOLE_ONLY",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        })
    write_tsv(out / OUTPUT_NAMES[1], surface_profiles)

    paragraph_candidates: list[dict[str, Any]] = []
    for target in [row for row in primary_external if row["occurrence_kind"] == "RUNNING_EVENT"]:
        for model_id in ("FAMILY_POOLED_STATUS", "SURFACE_SPECIFIC_LEARNED_ENTRIES", "OPAQUE_RECURRENCE"):
            if model_id == "FAMILY_POOLED_STATUS":
                replacement = "⟦AQABBA:Jupiter-/Venus-Faciesklasse?⟧"
            elif model_id == "SURFACE_SPECIFIC_LEARNED_ENTRIES":
                replacement = f"⟦{target['target_surface']}:{target['working_default_de']}?⟧"
            else:
                replacement = f"⟦{target['target_surface']}:unbekannter-gelernter-Eintrag⟧"
            paragraph_candidates.append({
                "candidate_reader_id": f"{target['contact_id']}__{model_id}",
                "contact_id": target["contact_id"],
                "target_surface": target["target_surface"],
                "physical_page": target["physical_page"],
                "paragraph_id": target["paragraph_id"],
                "line_span": target["line_span"],
                "independent_domain": target["independent_domain"],
                "model_id": model_id,
                "model_prediction": models[model_id]["whole_context_prediction"],
                "raw_whole_paragraph": target["raw_whole_context"],
                "target_masked_whole_paragraph": target["target_masked_whole_context"],
                "candidate_whole_paragraph": replace_token(target["raw_whole_context"], target["target_surface"], replacement),
                "translation_status": "CANDIDATE_TARGET_INSERTION_ONLY__SURROUNDING_PARAGRAPH_UNTRANSLATED",
                "component_export_credit": "ZERO",
            })
    write_tsv(out / OUTPUT_NAMES[2], paragraph_candidates)

    recurrent_surface_map: dict[str, set[str]] = defaultdict(set)
    source_surface_count: dict[str, Counter[str]] = defaultdict(Counter)
    for row in atlas:
        family = row["canonical_boundary_family"]
        surface = row["complete_label_surface"]
        if family in RECURRENT_FAMILIES and " " not in surface:
            recurrent_surface_map[surface].add(family)
            source_surface_count[family][surface] += 1
    source_loci = {row["locus"] for row in atlas}
    external_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in spine:
        surface = row["surface"]
        if surface not in recurrent_surface_map or row["locus"] in source_loci:
            continue
        host_unit = (
            locus_to_paragraph[row["locus"]]
            if row["occurrence_kind"] == "RUNNING_EVENT" else f"LOCAL:{row['locus']}"
        )
        for family in recurrent_surface_map[surface]:
            key = (family, surface, host_unit)
            domain = domains[row["topology_family"]]
            candidate = {
                "canonical_boundary_family": family,
                "surface": surface,
                "source_register_event_count": source_surface_count[family][surface],
                "external_host_unit_id": host_unit,
                "occurrence_kind": row["occurrence_kind"],
                "physical_page": row["physical_page"],
                "source_selector": row["source_selector"],
                "register": row["register"],
                "topology_family": row["topology_family"],
                "independent_domain": domain,
                "representative_locus": row["locus"],
                "host_unit_definition": "COMPLETE_PARAGRAPH" if row["occurrence_kind"] == "RUNNING_EVENT" else "LOCAL_VISIBLE_OWNER_LOCUS",
                "target_family": "YES" if family == "AQABBA" else "NO",
                "component_export_credit": "ZERO",
            }
            if key in external_by_key and external_by_key[key]["independent_domain"] != domain:
                raise RuntimeError(f"one host unit acquired conflicting domains: {key}")
            external_by_key.setdefault(key, candidate)
    external_contacts = sorted(
        external_by_key.values(),
        key=lambda row: (RECURRENT_FAMILIES.index(row["canonical_boundary_family"]), row["surface"], row["external_host_unit_id"]),
    )
    for ordinal, row in enumerate(external_contacts, 1):
        row["external_contact_ordinal"] = ordinal
    contact_fields = ["external_contact_ordinal"] + [field for field in external_contacts[0] if field != "external_contact_ordinal"]
    write_tsv(out / OUTPUT_NAMES[3], external_contacts, contact_fields)

    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in external_contacts:
        by_family[row["canonical_boundary_family"]].append(row)
    metrics_by_family = {family: family_metrics(by_family[family]) for family in RECURRENT_FAMILIES}
    qualified = sorted(
        [family for family in RECURRENT_FAMILIES if metrics_by_family[family]["capacity"]],
        key=lambda family: (-metrics_by_family[family]["loo_gain"], family),
    )
    tournament: list[dict[str, Any]] = []
    for family in RECURRENT_FAMILIES:
        metrics = metrics_by_family[family]
        tournament.append({
            "canonical_boundary_family": family,
            "source_register_event_count": sum(source_surface_count[family].values()),
            "source_register_surface_count": len(source_surface_count[family]),
            "external_host_unit_count": metrics["contact_count"],
            "external_surface_count": metrics["surface_count"],
            "external_domain_count": metrics["domain_count"],
            "external_surface_counts": metrics["surface_counts"],
            "external_domain_counts": metrics["domain_counts"],
            "surface_domain_purity": f6(metrics["surface_purity"]),
            "family_pooled_domain_purity": f6(metrics["pooled_purity"]),
            "leave_one_host_out_coverage": metrics["loo_coverage"],
            "surface_keyed_credit": f6(metrics["keyed_credit"]),
            "family_pooled_credit": f6(metrics["pooled_credit"]),
            "surface_keyed_accuracy": f6(metrics["keyed_accuracy"]),
            "family_pooled_accuracy": f6(metrics["pooled_accuracy"]),
            "surface_minus_pooled_gain": f6(metrics["loo_gain"]),
            "capacity_qualified": "YES" if metrics["capacity"] else "NO",
            "qualified_gain_rank": qualified.index(family) + 1 if family in qualified else "NA",
            "target_family": "YES" if family == "AQABBA" else "NO",
            "interpretation": (
                "surface-specific split candidate" if metrics["loo_gain"] > 0
                else "no positive surface-specific prediction" if metrics["capacity"]
                else "insufficient repeated external surface capacity"
            ),
            "semantic_export": "NONE",
        })
    write_tsv(out / OUTPUT_NAMES[4], tournament)

    target_rows = by_family["AQABBA"]
    target_metrics = family_metrics(target_rows)
    observed_gain = target_metrics["loo_gain"]
    domain_permutations = sorted(set(itertools.permutations(row["independent_domain"] for row in target_rows)))
    permutation_gains = [
        family_metrics([dict(row, independent_domain=domain) for row, domain in zip(target_rows, permutation)])["loo_gain"]
        for permutation in domain_permutations
    ]
    micro_p = sum(gain >= observed_gain - 1e-12 for gain in permutation_gains) / len(permutation_gains)
    if (len(domain_permutations), f6(micro_p)) != (6, "0.333333"):
        raise RuntimeError("AQABBA exact micro-permutation changed")

    all_source_surfaces = sorted({row["complete_label_surface"] for row in atlas if " " not in row["complete_label_surface"]})
    if len(all_source_surfaces) != 71:
        raise RuntimeError("single-token source-surface count changed")
    all_surface_profiles: list[dict[str, Any]] = []
    noncelestial_minimal_bridges: list[str] = []
    for surface in all_source_surfaces:
        units: dict[tuple[str, str], dict[str, str]] = {}
        for row in spine:
            if row["surface"] != surface or row["locus"] in source_loci:
                continue
            host_unit = locus_to_paragraph[row["locus"]] if row["occurrence_kind"] == "RUNNING_EVENT" else f"LOCAL:{row['locus']}"
            units.setdefault((row["occurrence_kind"], host_unit), row)
        local_counts = Counter(domains[row["topology_family"]] for (kind, _), row in units.items() if kind != "RUNNING_EVENT")
        running_counts = Counter(domains[row["topology_family"]] for (kind, _), row in units.items() if kind == "RUNNING_EVENT")
        bridges = sorted(set(local_counts) & set(running_counts))
        minimal = (
            len(units) == 2 and sum(local_counts.values()) == 1 and sum(running_counts.values()) == 1
            and len(bridges) == 1 and bridges[0] in {"FIGURE_STATION_SYSTEM", "PLANT_DRUG_MATERIAL"}
        )
        if minimal:
            noncelestial_minimal_bridges.append(surface)
        families = sorted({row["canonical_boundary_family"] for row in atlas if row["complete_label_surface"] == surface})
        all_surface_profiles.append({
            "surface": surface,
            "source_event_count": sum(row["complete_label_surface"] == surface for row in atlas),
            "source_families": pipe(families),
            "external_host_unit_count": len(units),
            "external_local_count": sum(local_counts.values()),
            "external_running_paragraph_count": sum(running_counts.values()),
            "external_local_domain_counts": pipe(f"{key}:{local_counts[key]}" for key in sorted(local_counts)),
            "external_running_domain_counts": pipe(f"{key}:{running_counts[key]}" for key in sorted(running_counts)),
            "same_domain_local_running_bridges": pipe(bridges),
            "noncelestial_minimal_bridge": "YES" if minimal else "NO",
            "target_surface": "YES" if surface in {"okaldy", "otaldy"} else "NO",
            "semantic_export": "NONE",
        })
    if noncelestial_minimal_bridges != ["okaldy", "otaldy"]:
        raise RuntimeError(f"target-independent bridge census changed: {noncelestial_minimal_bridges}")
    write_tsv(out / OUTPUT_NAMES[5], all_surface_profiles)

    branch_rows: list[dict[str, Any]] = []
    for scenario, families in (
        ("TARGET_EXCLUDED_CONTROLS", BRANCH_CONTROL_FAMILIES),
        ("TARGET_INCLUDED_SENSITIVITY", BRANCH_CONTROL_FAMILIES + ("AQABBA",)),
    ):
        selected = [
            row for family in families for row in by_family[family]
            if row["independent_domain"] in {"FIGURE_STATION_SYSTEM", "PLANT_DRUG_MATERIAL"}
            and (row["surface"].startswith("ok") or row["surface"].startswith("ot"))
        ]
        counts = Counter(("OK_SURFACE" if row["surface"].startswith("ok") else "OT_SURFACE", row["independent_domain"]) for row in selected)
        a = counts[("OK_SURFACE", "FIGURE_STATION_SYSTEM")]
        b = counts[("OK_SURFACE", "PLANT_DRUG_MATERIAL")]
        c = counts[("OT_SURFACE", "FIGURE_STATION_SYSTEM")]
        d = counts[("OT_SURFACE", "PLANT_DRUG_MATERIAL")]
        branch_rows.append({
            "scenario": scenario,
            "families": pipe(families),
            "surface_host_contact_count": len(selected),
            "ok_figure_station": a,
            "ok_plant_drug": b,
            "ot_figure_station": c,
            "ot_plant_drug": d,
            "odds_ratio_ok_figure_vs_ot_figure": f6((a * d) / (b * c)) if b and c else "INF",
            "fisher_two_sided_p": f6(fisher_two_sided(a, b, c, d)),
            "direction": "OK_LEANS_FIGURE__OT_LEANS_PLANT" if a / (a + b) > c / (c + d) else "NO_EXPECTED_DIRECTION",
            "decision": "WEAK_FORMAL_SENSITIVITY_ONLY__NO_COMPONENT_EXPORT",
            "component_export_credit": "ZERO",
        })
    write_tsv(out / OUTPUT_NAMES[6], branch_rows)

    expected_support = {
        "f18r.8": 1, "f70v2.17": 2, "f72r2.27": 3, "f75r.27": 3,
        "f82r.37": 3, "f88r.12": 3, "f95v1.4": 3,
    }
    if {row["locus"]: row["source_family_single_group_support"] for row in contact_rows} != expected_support:
        raise RuntimeError("source-native family support changed")
    picatrix = [row for row in historical_status if row["canonical_boundary_family"] == "AQABBA" and row["matrix_id"] == "PICATRIX_INDIAN"]
    chaldean = [row for row in historical_status if row["canonical_boundary_family"] == "AQABBA" and row["matrix_id"] == "CHALDEAN"]
    inherited = [row for row in historical_adjudication if row["candidate_id"] == "AQABBA_BENEFIC_RULER_FACIES"]
    if len(picatrix) != 2 or len(chaldean) != 2 or len(inherited) != 1:
        raise RuntimeError("inherited AQABBA status evidence changed")
    unique_positive = (
        target_metrics["capacity"]
        and observed_gain > 0
        and all(metrics_by_family[family]["loo_gain"] < observed_gain for family in qualified if family != "AQABBA")
    )
    exact_owner_domains = {
        row["target_surface"]: row["independent_domain"]
        for row in primary_external if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"
    }
    if exact_owner_domains != {"okaldy": "FIGURE_STATION_SYSTEM", "otaldy": "PLANT_DRUG_MATERIAL"}:
        raise RuntimeError("visible owner anchors changed")

    adjudication = [
        {
            "candidate_id": "HYBRID_SOURCE_STATUS_PLUS_LEARNED_ENTRIES",
            "working_interpretation": "AQABBA ist mögliche Jupiter-/Venus-Faciesklasse; okaldy und otaldy sind verschiedene gelernte Fachartikel",
            "confidence": "C0_BEST_CURRENT_THEORY",
            "decision": "SELECT_PRIMARY_C0" if unique_positive else "HOLD",
            "evidence": "Picatrix H0/H1 gives Jupiter/Venus at both source labels; external hosts split 4/4 by complete surface; target is the only positive capacity-qualified family",
            "counterevidence": f"only four external hosts; exact micro-permutation p={f6(micro_p)}; Chaldean status differs; opaque null survives",
            "renderer_license": "ENUMERATED_CONTEXTUAL_COMPLETE_WHOLES_ONLY",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "FAMILY_POOLED_BENEFIC_STATUS",
            "working_interpretation": "AQABBA = Jupiter-/Venus-beherrschte Faciesklasse",
            "confidence": "C0_SOURCE_LOCAL_ONLY",
            "decision": "RETAIN_SOURCE_REGISTER_RIVAL__NOT_PORTABLE_TO_EXTERNAL_HOSTS",
            "evidence": "Picatrix H0 and H1 each assign BENEFIC:2 to the two source events",
            "counterevidence": "external hosts contain no independent planet or status marker; Chaldean control disagrees",
            "renderer_license": "SOURCE_REGISTER_RIVAL_ONLY",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "SURFACE_SPECIFIC_LEARNED_ENTRIES",
            "working_interpretation": "okaldy und otaldy sind verschiedene gelernte Einträge",
            "confidence": "C0_BEST_CURRENT_ARCHITECTURE",
            "decision": "SELECT_PRIMARY_C0" if unique_positive else "HOLD",
            "evidence": "surface leave-one-host-out is 4/4 versus family-pooled 0/4; among 71 source surfaces only okaldy and otaldy form minimal non-celestial local-plus-running bridges",
            "counterevidence": f"only four external hosts; exact micro-permutation p={f6(micro_p)}; macro-domain collapse is necessary",
            "renderer_license": "ENUMERATED_CONTEXTUAL_COMPLETE_WHOLE_ONLY",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "OPAQUE_RECURRENCE",
            "working_interpretation": "beide Oberflächen bleiben ungelöste gelernte Einträge",
            "confidence": "C0_LIVE_NULL",
            "decision": "RETAIN_LIVE_NULL",
            "evidence": "four-contact split has an exact one-third calibration and alternate-reader boundary instability",
            "counterevidence": "double local-plus-running bridge is unique in the full 71-surface calibration",
            "renderer_license": "UNKNOWN_FALLBACK",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "OKALDY_BATH_TREATMENT_ENTRY",
            "working_interpretation": "okaldy = Bade-/Behandlungseintrag",
            "confidence": "C0_CONTEXTUAL_WHOLE",
            "decision": "SELECT_BOLD_REPLACEABLE_DEFAULT",
            "evidence": "exact f82 top-figure label plus separate f75 pool/apparatus paragraph and f72 radial member label",
            "counterevidence": "f18 IT2a-only fusion lies on a whole-plant page; f82 attachment is proximity-only; no independently read treatment name",
            "renderer_license": "ENUMERATED_OKALDY_CONTEXTS_ONLY",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "OTALDY_ROOT_DRUG_ARTICLE",
            "working_interpretation": "otaldy = Wurzel-/Drogenartikel",
            "confidence": "C0_CONTEXTUAL_WHOLE",
            "decision": "SELECT_BOLD_REPLACEABLE_DEFAULT",
            "evidence": "exact f88 Gabelwurzelstock label plus separate f95 whole-plant paragraph and f70 radial member label",
            "counterevidence": "f70 source label is celestial; no independently readable historical drug name",
            "renderer_license": "ENUMERATED_OTALDY_CONTEXTS_ONLY",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "GDT666_OTALDY_COMPOSITIONAL_ACTION",
            "working_interpretation": "otaldy = kalten Rohstoff-I-Ansatz fertigstellen",
            "confidence": "RETIRED",
            "decision": "QUARANTINE_ON_RELEASED_30_PAGE_SPINE",
            "evidence": "none independent; old card was composed as O_PREP+T_COLD+AL_RAW_I+DY_FINISHED",
            "counterevidence": "one-word radial and rootstock labels are not imperative process clauses; free-component route is retired",
            "renderer_license": "NONE",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
    ]
    write_tsv(out / OUTPUT_NAMES[7], adjudication)

    renderer_rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate([item for item in contact_rows if item["primary_analysis"] == "YES"], 1):
        prior = prior_reader.get(row["locus"], {})
        previous = prior.get("v99r7_practical_render_de", "NOT_IN_GDT734_LINE_CACHE")
        old_action_present = "kalten Rohstoff-I-Ansatz fertigstellen" in previous
        source_prediction = row["contact_class"] == "SOURCE_FAMILY_LABEL"
        display = (
            f"⟦{row['target_surface']}:{row['working_default_de']}? + AQABBA:Faciesklasse?⟧"
            if source_prediction else f"⟦{row['target_surface']}:{row['working_default_de']}?⟧"
        )
        renderer_rows.append({
            "renderer_ordinal": ordinal,
            "contact_id": row["contact_id"],
            "target_surface": row["target_surface"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "context_unit_id": row["context_unit_id"],
            "independent_domain": row["independent_domain"],
            "fine_topology": row["topology_family"],
            "visible_owner_description": row["visible_owner_description"],
            "previous_v99r7_line_render": previous,
            "previous_otaldy_action_present": "YES" if old_action_present else "NO",
            "previous_card_disposition": (
                "QUARANTINED_GDT666_COMPOSITIONAL_ACTION_CELL" if old_action_present
                else "GDT666_FORM_CARD_QUARANTINED__NO_ACTIVE_CELL_HERE" if row["target_surface"] == "otaldy"
                else "NO_PREVIOUS_OKALDY_MEANING"
            ),
            "gdt797_working_default_de": row["working_default_de"],
            "display": display,
            "confidence": "C0_PREDICTED_HYBRID_SOURCE_LABEL" if source_prediction else "C0_CONTEXTUAL_WHOLE",
            "evidence": row["evidence_role"],
            "counterevidence": row["counterevidence"],
            "scope": "EXACT_SOURCE_LABEL_HYBRID_RIVAL_ONLY" if source_prediction else "EXACT_WHOLE_AT_ENUMERATED_CONTEXT_ONLY",
            "renderer_precedence": "GDT797_CONTEXTUAL_WHOLE_OVER_GDT734",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        })
    if sum(row["previous_otaldy_action_present"] == "YES" for row in renderer_rows) != 2:
        raise RuntimeError("legacy otaldy action-cell count changed")
    write_tsv(out / OUTPUT_NAMES[8], renderer_rows)

    scope_rows = [
        {
            "audit_id": "GDT797_EXACT_LOCUS_CROSS_QUERY",
            "event_stage": "EXECUTABLE_BUILD",
            "selector": "locus", "allowed_count": len(CROSS_LOCI),
            "selected_rows": cross_stats["selected"],
            "sealed_rows_rejected_before_materialization": cross_stats["skipped_forbidden"],
            "other_rows_skipped": cross_stats["skipped_not_allowed"],
            "count_status": "MEASURED_GUARDED_QUERY",
            "retained_sealed_values": 0, "disposition": "PASS_EXACT_GUARD",
            "note": "seven enumerated alternate-reader loci only",
        },
        {
            "audit_id": "GDT797_EXACT_LOCUS_SOURCE_STA_QUERY",
            "event_stage": "EXECUTABLE_BUILD",
            "selector": "locus", "allowed_count": len(CROSS_LOCI),
            "selected_rows": sta_stats["selected"],
            "sealed_rows_rejected_before_materialization": sta_stats["skipped_forbidden"],
            "other_rows_skipped": sta_stats["skipped_not_allowed"],
            "count_status": "MEASURED_GUARDED_QUERY",
            "retained_sealed_values": 0, "disposition": "PASS_EXACT_GUARD",
            "note": "family support kept separate from EVA exact-whole agreement",
        },
        {
            "audit_id": "PRE_GDT797_CANVAS_ID_SCRATCH_SEARCH",
            "event_stage": "PRE_EXPERIMENT_SCRATCH",
            "selector": "NOT_APPLICABLE", "allowed_count": 0, "selected_rows": 0,
            "sealed_rows_rejected_before_materialization": 0,
            "other_rows_skipped": 0,
            "count_status": "NOT_APPLICABLE_TO_UNGUARDED_SCRATCH_INCIDENT",
            "retained_sealed_values": 0,
            "disposition": "TRANSIENT_DISPLAY_EXCLUDED_FROM_ALL_INPUTS_ARTIFACTS_AND_SCORES",
            "note": "a broad canvas-ID search traversed pre-existing sealed metadata text; no image transcription identity or value was retained or used",
        },
    ]
    write_tsv(out / OUTPUT_NAMES[9], scope_rows)

    result = {
        "experiment_id": "GDT797",
        "status": STATUS,
        "scope": {
            "released_physical_pages": 30, "source_family_loci": 2,
            "primary_exact_events": 6, "external_exact_host_units": 4,
            "boundary_sensitivity_rows": 1, "new_pages": 0,
            "sealed_rows_materialized_in_executable_build": 0,
            "pre_experiment_scratch_incident": "TRANSIENT_DISPLAY_EXCLUDED_FROM_ALL_INPUTS_ARTIFACTS_AND_SCORES",
        },
        "target_split": {
            "okaldy_external_domains": {"FIGURE_STATION_SYSTEM": 2},
            "otaldy_external_domains": {"PLANT_DRUG_MATERIAL": 2},
            "surface_keyed_leave_one_host_out_credit": target_metrics["keyed_credit"],
            "family_pooled_leave_one_host_out_credit": target_metrics["pooled_credit"],
            "surface_minus_pooled_gain": target_metrics["loo_gain"],
            "exact_micro_permutations": len(domain_permutations),
            "inclusive_exact_micro_p": micro_p,
            "capacity_qualified_families": qualified,
            "target_qualified_gain_rank": qualified.index("AQABBA") + 1,
        },
        "surface_calibration": {
            "single_token_source_surfaces": len(all_source_surfaces),
            "surfaces_with_external_contacts": sum(row["external_host_unit_count"] > 0 for row in all_surface_profiles),
            "surfaces_with_any_local_running_bridge": sum(row["same_domain_local_running_bridges"] != "NONE" for row in all_surface_profiles),
            "noncelestial_minimal_local_running_bridges": noncelestial_minimal_bridges,
        },
        "selected_working_theory": {
            "architecture": "HYBRID_SOURCE_STATUS_PLUS_SURFACE_SPECIFIC_LEARNED_ENTRIES",
            "aqabba": "possible Jupiter/Venus facies class in source register",
            "okaldy": "Bade-/Behandlungseintrag",
            "otaldy": "Wurzel-/Drogenartikel",
            "confidence": "C0_CONTEXTUAL_WHOLE",
            "opaque_null_survives": True,
        },
        "renderer": {
            "contextual_rows": len(renderer_rows),
            "legacy_otaldy_action_cells_quarantined": sum(row["previous_otaldy_action_present"] == "YES" for row in renderer_rows),
            "component_exports": 0, "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
        },
        "controls": {
            "recurrent_families": len(RECURRENT_FAMILIES),
            "families_with_external_contacts": sum(bool(by_family[family]) for family in RECURRENT_FAMILIES),
            "capacity_qualified": len(qualified),
            "target_excluded_branch_fisher_two_sided_p": float(branch_rows[0]["fisher_two_sided_p"]),
        },
        "outputs": list(OUTPUT_NAMES),
    }
    with (out / OUTPUT_NAMES[10]).open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"experiment_id": "GDT797", "status": STATUS, "output_dir": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
