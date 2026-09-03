#!/usr/bin/env python3
"""Build GDT783's target-masked majority-variant chsky field audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt783_chsky_majority_variant_external_field"
SRC, ART, REPORT = EXP / "src", EXP / "artifacts", EXP / "REPORT.md"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
CANDIDATES = SRC / "CANDIDATE_6_SPECS.tsv"
FINAL_SPEC = SRC / "FINAL_SELECTION_SPEC.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_COMPARATOR_SPECS.tsv"
G782_RUN = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py"
G754_PROVENANCE = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G768_WORKING = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G781_SELECTED = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv"
G781_CARDS = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv"
G781_ANALOGY = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv"
G782_RENDERER = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/GDT782_376_RENDERER.tsv"
G782_RESULT = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/RESULT.json"
G622_OBSERVATIONS = ROOT / "experiments/yolo/gdt622_clm667_temperament_codebook/artifacts/SOURCE_OBSERVATIONS.tsv"
G626_COMPARATORS = ROOT / "experiments/yolo/gdt626_mobile_operation_lexicon/artifacts/HISTORICAL_NUMERAL_COMPARATORS.tsv"

TARGET = "chsky"
LOCUS_SPECS = (
    ("G783-L001", "f86v5", "f86v5.15", 12, "TARGET_MASKED_SENSITIVITY", "EXACT_3_OF_3", ("chsky", "chsky", "chsky"), 5, 99),
    ("G783-L002", "f25r", "f25r.2", 3, "EXTERNAL_STRONG_MAJORITY", "ZL_RF_CHSKY__IT_CHRKY", ("chsky", "chrky", "chsky"), 3, 4),
    ("G783-L003", "f103r", "f103r.37", 7, "EXTERNAL_WEAK_MAJORITY", "ZL_IT_CHSKY__RF_CHSTY", ("chsky", "chsky", "chsty"), 3, 1),
)
READERS = ("zl3b", "it2a", "rf1b")
READER_FIELDS = tuple(f"{reader}_clean" for reader in READERS)
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "STAGE", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)
OPPOSITE = {"HOT": "COLD", "COLD": "HOT", "DRY": "MOIST", "MOIST": "DRY"}
STATUS = (
    "PASS__3_PHYSICAL_LOCI_ONCE__1_TARGET_MASKED__2_EXTERNAL_MAJORITY_VARIANTS__"
    "28_POSITIONAL_NEIGHBORS__4_ANALOGS_1_GDT754_BLOCKED__"
    "PRACTICAL_HOT_DRY_WITH_HOT_MINIMUM_CORE__270_CONTEXTUAL__106_FALLBACKS__"
    "230_CONSUMED__ZERO_VARIANT_LETTER_EXPORT"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output: {path.name}")
    fields = list(rows[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: int(value) if isinstance(value := row.get(field, ""), bool) else value for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def one_by(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        if row[key] in output:
            raise AssertionError(f"duplicate {key}: {row[key]}")
        output[row[key]] = dict(row)
    return output


def split_axes(value: str) -> set[str]:
    return set() if value in {"", "NONE", "OPEN"} else set(value.split("|"))


def expanded_axes(values: Iterable[str]) -> set[str]:
    axes = set(values)
    if axes & {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III"}:
        axes.add("STAGE")
    return axes


def joined(values: Iterable[str]) -> str:
    axes = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in axes) or "NONE"


def counted(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{axis}:{counts[axis]}" for axis in AXIS_ORDER if counts[axis]) or "NONE"


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise AssertionError(page)
    return match.group(1)


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if len(rows) != 17:
        raise AssertionError(f"expected 17 source locks, got {len(rows)}")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source path: {relative}")
        if sha256(ROOT / relative) != row["expected_sha256"]:
            raise AssertionError(f"source changed: {relative}")
    return len(rows), sha256(SOURCE_LOCK)


def load_base():
    spec = importlib.util.spec_from_file_location("gdt782_locked", G782_RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT782 helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_loci(cross: Mapping[str, Mapping[str, str]], by_line: Mapping[str, Sequence[Mapping[str, str]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locus_id, page, locus, ordinal, role, strength, expected, radius, warning in LOCUS_SPECS:
        source = cross[locus]
        sequences = [source[field].split() for field in READER_FIELDS]
        forms = tuple(sequence[ordinal - 1] for sequence in sequences)
        if forms != expected or " ".join(row["eva"] for row in by_line[locus]) != source["zl3b_clean"]:
            raise AssertionError(f"locus reconstruction changed: {locus}")
        counts = Counter(forms)
        majority, majority_count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
        rows.append({
            "locus_id": locus_id, "page": page, "physical_folio": physical_folio(page), "locus": locus,
            "locus_role": role, "variant_strength": strength, "target_ordinal_in_each_reader": ordinal,
            "zl3b_target_form": forms[0], "it2a_target_form": forms[1], "rf1b_target_form": forms[2],
            "majority_surface": majority, "majority_reader_count": majority_count,
            "physical_locus_weight": 1, "alternate_readers_counted_independently": 0,
            "external_field_vote": int(role.startswith("EXTERNAL")),
            "target_context_sensitivity_only": int(role.startswith("TARGET")),
            "primary_field_radius": radius, "alignment_warning_from_positive_offset": warning,
            "zl3b_line": source["zl3b_clean"], "it2a_line": source["it2a_clean"], "rf1b_line": source["rf1b_clean"],
            "target_masked_in_all_reader_fields": 1, "variant_letters_semantically_exported": 0,
            "default_is_translation": 0,
        })
    if Counter(row["majority_reader_count"] for row in rows) != Counter({2: 2, 3: 1}):
        raise AssertionError("reader-majority shape changed")
    return rows


def neighbor_details(surface: str, pool: Mapping[str, Mapping[str, object]], provenance: Mapping[str, Mapping[str, str]], later: Mapping[str, Mapping[str, str]]) -> dict[str, object]:
    prov, clean, override = provenance.get(surface), pool.get(surface), later.get(surface)
    if prov and prov["source_literal_prose_spoken_after_gdt754"] == "0":
        return {"neighbor_class": "SANITIZED_GDT754_WHOLE_HYPOTHESIS", "clean_pool_reading_ids": "NONE", "clean_pool_axes": "NONE", "working_display_de": prov["current_working_whole_default_de"], "gdt754_provenance_present": 1, "gdt754_renderer_disposition": prov["renderer_disposition"], "gdt754_sanitized_axes": prov["later_role_axes_selected"], "gdt768_display_override": 0}
    if clean:
        return {"neighbor_class": "CLEAN_W2W3_COMPLETE_WHOLE", "clean_pool_reading_ids": clean["reading_ids"], "clean_pool_axes": joined(expanded_axes(clean["core_axes"])), "working_display_de": override["concrete_default_de"] if override else clean["best_gloss"], "gdt754_provenance_present": int(prov is not None), "gdt754_renderer_disposition": prov["renderer_disposition"] if prov else "NONE", "gdt754_sanitized_axes": prov["later_role_axes_selected"] if prov else "NONE", "gdt768_display_override": int(override is not None)}
    return {"neighbor_class": "OPEN_OR_NONAXIS_MAJORITY_WHOLE", "clean_pool_reading_ids": "NONE", "clean_pool_axes": "NONE", "working_display_de": "NONE", "gdt754_provenance_present": int(prov is not None), "gdt754_renderer_disposition": prov["renderer_disposition"] if prov else "NONE", "gdt754_sanitized_axes": prov["later_role_axes_selected"] if prov else "NONE", "gdt768_display_override": 0}


def build_neighbors(loci: Sequence[Mapping[str, object]], pool: Mapping[str, Mapping[str, object]], provenance: Mapping[str, Mapping[str, str]], later: Mapping[str, Mapping[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for locus in loci:
        sequences = [str(locus[f"{reader}_line"]).split() for reader in READERS]
        target_ordinal, radius = int(locus["target_ordinal_in_each_reader"]), int(locus["primary_field_radius"])
        for ordinal in range(1, max(map(len, sequences)) + 1):
            if ordinal == target_ordinal:
                continue
            offset = ordinal - target_ordinal
            forms = tuple(sequence[ordinal - 1] if ordinal <= len(sequence) else "<ABSENT>" for sequence in sequences)
            counts = Counter(form for form in forms if form != "<ABSENT>")
            majority, majority_count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
            if majority_count < 2:
                majority = "NONE"
                detail = {"neighbor_class": "NO_READER_MAJORITY", "clean_pool_reading_ids": "NONE", "clean_pool_axes": "NONE", "working_display_de": "NONE", "gdt754_provenance_present": 0, "gdt754_renderer_disposition": "NONE", "gdt754_sanitized_axes": "NONE", "gdt768_display_override": 0}
            else:
                detail = neighbor_details(majority, pool, provenance, later)
            within = int(abs(offset) <= radius)
            eligible = int(within and majority_count >= 2 and detail["neighbor_class"] == "CLEAN_W2W3_COMPLETE_WHOLE")
            rows.append({
                "neighbor_id": f"G783-N{len(rows)+1:03d}", "locus_id": locus["locus_id"], "page": locus["page"],
                "physical_folio": locus["physical_folio"], "locus": locus["locus"], "locus_role": locus["locus_role"],
                "target_ordinal": target_ordinal, "neighbor_ordinal": ordinal, "offset": offset, "absolute_distance": abs(offset),
                "zl3b_surface": forms[0], "it2a_surface": forms[1], "rf1b_surface": forms[2], "majority_surface": majority,
                "majority_reader_count": majority_count, "reader_consensus_class": "THREE_OF_THREE" if majority_count == 3 else "TWO_OF_THREE" if majority_count == 2 else "NO_MAJORITY",
                **detail, "within_primary_radius": within, "eligible_field_vote": eligible,
                "reader_boundary_shift_warning": int(offset > 0 and offset >= int(locus["alignment_warning_from_positive_offset"])),
                "target_slot_removed_before_reading": 1, "physical_locus_weight": 1,
                "alternate_readers_counted_independently": 0, "variant_letters_semantically_exported": 0,
                "component_export_credit": 0,
            })
    if len(rows) != 28 or any(row["majority_surface"] == TARGET for row in rows):
        raise AssertionError("neighbor atlas shape or target mask changed")
    if sum(int(row["gdt768_display_override"]) for row in rows) != 1:
        raise AssertionError("expected current chor display override")
    return rows


def build_fields(loci: Sequence[Mapping[str, object]], neighbors: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in neighbors:
        grouped[str(row["locus_id"])].append(row)
    output: list[dict[str, object]] = []
    for locus in loci:
        donors = [row for row in grouped[str(locus["locus_id"])] if int(row["eligible_field_vote"])]
        contacts = [axis for row in donors for axis in expanded_axes(split_axes(str(row["clean_pool_axes"])))]
        axes = set(contacts)
        output.append({
            "locus_id": locus["locus_id"], "page": locus["page"], "physical_folio": locus["physical_folio"],
            "locus": locus["locus"], "locus_role": locus["locus_role"], "variant_strength": locus["variant_strength"],
            "primary_radius": locus["primary_field_radius"], "eligible_consensus_donors": len(donors),
            "eligible_consensus_surfaces": "|".join(str(row["majority_surface"]) for row in donors) or "NONE",
            "field_axis_union": joined(axes), "field_axis_contacts": counted(contacts),
            "hot_present": int("HOT" in axes), "cold_present": int("COLD" in axes),
            "dry_present": int("DRY" in axes), "moist_present": int("MOIST" in axes),
            "material_present": int("MATERIAL" in axes), "preparation_present": int("PREPARATION" in axes),
            "process_present": int("PROCESS" in axes), "stage_present": int("STAGE" in axes),
            "target_masked": 1, "physical_locus_weight": 1, "alternate_readers_counted_independently": 0,
            "field_axes_are_target_meanings": 0, "component_export_credit": 0,
        })
    if len(output) != 3:
        raise AssertionError("expected three fields")
    return output


def build_analogs(pool: Mapping[str, Mapping[str, object]], provenance: Mapping[str, Mapping[str, str]]) -> list[dict[str, object]]:
    sources = [row for row in read_tsv(G781_ANALOGY) if row["candidate_surface"] == TARGET]
    if [row["known_neighbor_surface"] for row in sources] != ["cheky", "chky", "choky", "chyky"]:
        raise AssertionError("parent analogy quartet changed")
    output: list[dict[str, object]] = []
    for source in sources:
        donor = source["known_neighbor_surface"]
        clean, prov = pool.get(donor), provenance.get(donor)
        if clean is None:
            raise AssertionError(f"missing clean donor: {donor}")
        blocked = int(prov is not None and prov["source_literal_prose_spoken_after_gdt754"] == "0")
        axes = expanded_axes(clean["core_axes"])
        output.append({
            "audit_id": f"G783-A{len(output)+1:03d}", "gdt781_relation_id": source["relation_id"],
            "candidate_surface": TARGET, "donor_surface": donor,
            "whole_levenshtein_distance": source["whole_levenshtein_distance"],
            "gdt781_donor_default_de": source["known_neighbor_best_gloss_de"],
            "current_clean_pool_axes": joined(axes), "gdt754_provenance_present": int(prov is not None),
            "gdt754_source_literal_spoken": prov["source_literal_prose_spoken_after_gdt754"] if prov else "NONE",
            "gdt754_current_whole_default_de": prov["current_working_whole_default_de"] if prov else "NONE",
            "audit_decision": "BLOCK_GDT754_SOURCE_COMPOSITION" if blocked else "KEEP_CLEAN_COMPLETE_WHOLE_ANALOG",
            "eligible_analogy_vote": 1 - blocked, "hot_axis_vote": int(not blocked and "HOT" in axes),
            "dry_axis_vote": int(not blocked and "DRY" in axes), "donor_identity_exported": 0,
            "substring_or_variant_letter_used": 0, "component_export_credit": 0,
        })
    if Counter(row["audit_decision"] for row in output) != Counter({"KEEP_CLEAN_COMPLETE_WHOLE_ANALOG": 3, "BLOCK_GDT754_SOURCE_COMPOSITION": 1}):
        raise AssertionError("GDT754 analogy sanitation changed")
    return output


def build_historical() -> list[dict[str, object]]:
    specs, observations = read_tsv(HISTORICAL_SPECS), read_tsv(G622_OBSERVATIONS)
    comparators = one_by(read_tsv(G626_COMPARATORS), "source_id")
    hot_dry = sum(row["thermal"] == "HOT" and row["moisture"] == "DRY" for row in observations)
    hot_moist = sum(row["thermal"] == "HOT" and row["moisture"] == "MOIST" for row in observations)
    hot_only = sum(row["thermal"] == "HOT" and not row["moisture"] for row in observations)
    if (len(observations), hot_dry, hot_moist, hot_only) != (28, 19, 3, 1):
        raise AssertionError("historical census changed")
    output: list[dict[str, object]] = []
    for source in specs:
        if source["comparator_id"] == "G783-H01":
            witness = "GDT622 bound CLM667 source-observation census"
            observed = f"28 rows: HOT+DRY={hot_dry}; HOT+MOIST={hot_moist}; HOT-only={hot_only}"
            url = observations[0]["image_url"]
        else:
            row = comparators[source["source_id"]]
            witness, observed, url = row["witness_or_text"], row["mechanism_relevant_to_gdt626"], row["url"]
        output.append({
            **source, "bound_witness": witness, "observed_architecture": observed, "source_url": url,
            "supports_hot_slot_architecture": 1,
            "supports_hot_dry_pair_architecture": int(source["comparator_id"] in {"G783-H01", "G783-H02"}),
            "selects_chsky_candidate": 0, "default_is_translation": 0,
        })
    if len(output) != 3:
        raise AssertionError("historical spec shape changed")
    return output


def build_scores(candidates: Sequence[Mapping[str, str]], analogs: Sequence[Mapping[str, object]], fields: Sequence[Mapping[str, object]], final: Mapping[str, str]) -> list[dict[str, object]]:
    donor_axes = [expanded_axes(split_axes(str(row["current_clean_pool_axes"]))) for row in analogs if int(row["eligible_analogy_vote"])]
    external = [expanded_axes(split_axes(str(row["field_axis_union"]))) for row in fields if str(row["locus_role"]).startswith("EXTERNAL")]
    target = next(expanded_axes(split_axes(str(row["field_axis_union"]))) for row in fields if str(row["locus_role"]).startswith("TARGET"))
    all_fields = external + [target]
    output: list[dict[str, object]] = []
    for source in candidates:
        axes = split_axes(source["candidate_axes"])
        analog_full = sum(axes <= donor for donor in donor_axes)
        external_full = sum(axes <= field for field in external)
        target_full = int(axes <= target)
        external_axis_mean = sum(sum(axis in field for field in external) / len(external) for axis in axes) / len(axes)
        target_coverage = sum(axis in target for axis in axes) / len(axes)
        opposition = sum(OPPOSITE.get(axis, "NONE") in field for axis in axes if axis in OPPOSITE for field in all_fields)
        complexity = 0.5 * (len(axes) - 1)
        continuity = 0.25 * int(source["parent_candidate"])
        score = 2 * analog_full + 3 * external_full + target_full + external_axis_mean + 0.5 * target_coverage - opposition - complexity + continuity
        output.append({
            **source, "eligible_analogy_full_support": analog_full,
            "external_physical_locus_full_support": external_full, "target_masked_context_full_support": target_full,
            "external_axis_presence_mean": f"{external_axis_mean:.6f}", "target_axis_coverage": f"{target_coverage:.6f}",
            "opposed_field_contacts": opposition, "axis_complexity_penalty": f"{complexity:.6f}",
            "parent_continuity_bonus": f"{continuity:.6f}", "exploratory_score": f"{score:.6f}",
            "score_formula": "2*A_FULL+3*E_FULL+T_FULL+E_AXIS_MEAN+0.5*T_AXIS_COVERAGE-OPPOSITION-0.5*(AXES-1)+0.25*PARENT",
            "score_selected": 0, "practical_selection_spec": int(source["candidate_id"] == final["selected_candidate_id"]),
            "score_is_lexical_probability": 0, "variant_letters_used_as_features": 0,
        })
    ranked = sorted(output, key=lambda row: (-float(row["exploratory_score"]), str(row["candidate_id"])))
    for rank, row in enumerate(ranked, 1):
        row["score_rank"] = rank
        row["score_selected"] = int(rank == 1)
    if ranked[0]["candidate_id"] != "C01_HOT_QUALITY" or final["selected_candidate_id"] != "C02_HOT_DRY_QUALITY":
        raise AssertionError("expected conservative score/practical dissent split changed")
    return sorted(output, key=lambda row: str(row["candidate_id"]))


def build_revision(final: Mapping[str, str], scores: Sequence[Mapping[str, object]], analogs: Sequence[Mapping[str, object]], fields: Sequence[Mapping[str, object]]) -> dict[str, object]:
    parent = next(row for row in read_tsv(G781_CARDS) if row["surface"] == TARGET)
    selected_score = next(row for row in scores if row["candidate_id"] == final["selected_candidate_id"])
    dissent_score = next(row for row in scores if row["candidate_id"] == final["dissent_candidate_id"])
    if parent["preferred_gdt781_default_de"] != "heiß und trocken":
        raise AssertionError("parent default changed")
    return {
        "card_id": "G783-C001", **final, "gdt781_parent_default_de": parent["preferred_gdt781_default_de"],
        "working_role": "QUALITY_STATE_WHOLE_WITH_LOCAL_OL_PREPARATION_CARRIER",
        "selected_exploratory_score": selected_score["exploratory_score"],
        "dissent_exploratory_score": dissent_score["exploratory_score"],
        "score_winner_candidate_id": dissent_score["candidate_id"],
        "rival_1_de": "heiß", "rival_2_de": "heißgetrocknetes Arzneigut",
        "further_rivals": "Heißstufe der Zubereitung|Trockenzubereitung|Erwärmungsvorgang",
        "eligible_analogs": sum(int(row["eligible_analogy_vote"]) for row in analogs),
        "blocked_analogs": sum(1 - int(row["eligible_analogy_vote"]) for row in analogs),
        "external_physical_loci": 2, "external_hot_loci": sum(int(row["hot_present"]) for row in fields if str(row["locus_role"]).startswith("EXTERNAL")),
        "external_dry_loci": sum(int(row["dry_present"]) for row in fields if str(row["locus_role"]).startswith("EXTERNAL")),
        "external_display_license": 0,
    }


def build_renderer(parent: Sequence[Mapping[str, str]], revision: Mapping[str, object]) -> tuple[list[dict[str, object]], set[str]]:
    output: list[dict[str, object]] = []
    owners: set[str] = set()
    target_rows = 0
    for source in parent:
        row: dict[str, object] = dict(source)
        target = source["locus"] == "f86v5.15" and source["right_surface"] == TARGET and source["gdt781_span_id"] == "G781-S020"
        if target:
            target_rows += 1
            additions = {
                "gdt783_branch": "GDT783_VARIANT_SAFE_WHOLE_CARD_CONFIRMATION",
                "gdt783_default_de": revision["target_span_default_de"],
                "gdt783_practical_whole_default_de": revision["practical_whole_default_de"],
                "gdt783_portable_minimum_core_de": revision["portable_minimum_core_de"],
                "gdt783_renderer_contextual": source["gdt782_renderer_contextual"], "gdt783_card_id": revision["card_id"],
                "gdt783_decision": revision["decision"], "gdt783_confidence": f"HOT={revision['hot_confidence']}|DRY={revision['dry_confidence']}",
                "gdt783_working_role": revision["working_role"], "gdt783_functional_axes": "HOT|DRY",
                "gdt783_external_physical_loci": revision["external_physical_loci"],
                "gdt783_variant_policy": "PHYSICAL_LOCUS_ONCE__TWO_OF_THREE_ADMITTED__NO_VARIANT_LETTER_EXPORT",
                "gdt783_consumed_token_count": source["gdt782_consumed_token_count"], "gdt783_consumed_token_ids": source["gdt782_consumed_token_ids"],
                "gdt783_display_changed": int(source["gdt782_default_de"] != revision["target_span_default_de"]),
                "gdt783_default_is_translation": 0, "gdt783_confirmed_lexeme": 0, "gdt783_confirmed_plaintext": 0,
                "gdt783_component_export_credit": 0, "gdt783_variant_letter_export_credit": 0,
            }
        else:
            additions = {
                "gdt783_branch": "INHERITED_GDT782", "gdt783_default_de": source["gdt782_default_de"],
                "gdt783_practical_whole_default_de": "INHERITED_GDT782", "gdt783_portable_minimum_core_de": "INHERITED_GDT782",
                "gdt783_renderer_contextual": source["gdt782_renderer_contextual"], "gdt783_card_id": "NONE",
                "gdt783_decision": "INHERITED_GDT782", "gdt783_confidence": "INHERITED_GDT782",
                "gdt783_working_role": "INHERITED_GDT782", "gdt783_functional_axes": source["gdt782_functional_axes"],
                "gdt783_external_physical_loci": 0, "gdt783_variant_policy": "INHERITED_GDT782",
                "gdt783_consumed_token_count": source["gdt782_consumed_token_count"], "gdt783_consumed_token_ids": source["gdt782_consumed_token_ids"],
                "gdt783_display_changed": 0, "gdt783_default_is_translation": source["gdt782_default_is_translation"],
                "gdt783_confirmed_lexeme": source["gdt782_confirmed_lexeme"], "gdt783_confirmed_plaintext": source["gdt782_confirmed_plaintext"],
                "gdt783_component_export_credit": source["gdt782_component_export_credit"], "gdt783_variant_letter_export_credit": 0,
            }
        row.update(additions)
        for token_id in str(row["gdt783_consumed_token_ids"]).split("|"):
            if token_id in {"", "NONE"}:
                continue
            if token_id in owners:
                raise AssertionError(f"consumption collision: {token_id}")
            owners.add(token_id)
        output.append(row)
    if len(output) != 376 or target_rows != 1 or sum(int(row["gdt783_renderer_contextual"]) for row in output) != 270 or len(owners) != 230:
        raise AssertionError("renderer totals changed")
    # The practical parent wording stays, but the local carrier and split axis confidence become explicit.
    if sum(int(row["gdt783_display_changed"]) for row in output) != 1:
        raise AssertionError("expected one target-span display refinement")
    return output, owners


def build_patch(revision: Mapping[str, object]) -> dict[str, object]:
    source = next(row for row in read_tsv(G781_SELECTED) if row["right_surface"] == TARGET)
    if (source["locus"], source["ol_ordinal"], source["right_ordinal"]) != ("f86v5.15", "11", "12"):
        raise AssertionError("target span changed")
    words = source["written_line_eva"].split()
    if words[10:12] != ["ol", "chsky"]:
        raise AssertionError("target token pair changed")
    prefix = " ".join(words[:10])
    return {
        "patch_id": "G783-P001", "card_id": revision["card_id"], "gdt781_span_id": source["span_id"],
        "target_occurrence_id": source["target_occurrence_id"], "page": source["page"], "physical_folio": source["physical_folio"],
        "locus": source["locus"], "ol_ordinal": source["ol_ordinal"], "right_ordinal": source["right_ordinal"],
        "right_surface": source["right_surface"], "written_line_eva": source["written_line_eva"],
        "gdt782_inherited_patch_de": f"{prefix} ⟦heiß und trocken⟧",
        "gdt783_practical_patch_de": f"{prefix} ⟦{revision['target_span_default_de']}⟧",
        "practical_whole_default_de": revision["practical_whole_default_de"],
        "portable_minimum_core_de": revision["portable_minimum_core_de"],
        "target_masked_during_adjudication": 1, "new_token_consumption": 0,
        "patch_legend": "double brackets are one replaceable existing ol-plus-whole span; unbracketed EVA remains unresolved",
        "default_is_translation": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
    }


def display_neighbor(row: Mapping[str, object]) -> str:
    if row["neighbor_class"] == "CLEAN_W2W3_COMPLETE_WHOLE":
        return f"⟨{row['working_display_de']}⟩"
    if row["neighbor_class"] == "SANITIZED_GDT754_WHOLE_HYPOTHESIS":
        return f"⟨{row['working_display_de']}; GDT754-Ganzformhypothese⟩"
    variants = "/".join(str(row[field]) for field in ("zl3b_surface", "it2a_surface", "rf1b_surface"))
    return f"[{variants}:Leservarianten]" if row["neighbor_class"] == "NO_READER_MAJORITY" else f"[{row['majority_surface']}:?]"


def build_external_readers(loci: Sequence[Mapping[str, object]], neighbors: Sequence[Mapping[str, object]], revision: Mapping[str, object]) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in neighbors:
        grouped[str(row["locus_id"])].append(row)
    output: list[dict[str, object]] = []
    for locus in loci:
        if not str(locus["locus_role"]).startswith("EXTERNAL"):
            continue
        by_ordinal = {int(row["neighbor_ordinal"]): row for row in grouped[str(locus["locus_id"])]}
        target_ordinal, maximum = int(locus["target_ordinal_in_each_reader"]), max(by_ordinal)
        variants = "/".join(str(locus[field]) for field in ("zl3b_target_form", "it2a_target_form", "rf1b_target_form"))
        rendered = []
        for ordinal in range(1, maximum + 1):
            rendered.append(
                f"⟦{variants}: Kartenprüfung {revision['practical_whole_default_de']}⟧"
                if ordinal == target_ordinal else display_neighbor(by_ordinal[ordinal])
            )
        output.append({
            "external_reader_id": f"G783-X{len(output)+1:03d}", "locus_id": locus["locus_id"], "page": locus["page"],
            "physical_folio": locus["physical_folio"], "locus": locus["locus"], "variant_strength": locus["variant_strength"],
            "reader_target_forms": variants, "majority_surface": locus["majority_surface"],
            "working_consensus_field_render_de": " | ".join(rendered),
            "practical_card_under_test_de": revision["practical_whole_default_de"],
            "portable_minimum_core_de": revision["portable_minimum_core_de"],
            "status": "AGGREGATE_CARD_AUDIT_NOT_EXTERNAL_RENDERER_LICENSE",
            "legend": "masked card-under-test; clean donor angles; open/variant squares; alternate readers count once as one physical locus",
            "external_renderer_license": 0, "default_is_translation": 0, "confirmed_plaintext": 0,
            "variant_letter_export_credit": 0, "component_export_credit": 0,
        })
    if len(output) != 2:
        raise AssertionError("expected two external readers")
    return output


def make_packet(loci: Sequence[Mapping[str, object]], neighbors: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    grouped: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in neighbors:
        grouped[str(row["locus_id"])].append(row)
    packet, crosswalk = [], []
    for number, locus in enumerate((row for row in loci if str(row["locus_role"]).startswith("EXTERNAL")), 1):
        candidates = [row for row in grouped[str(locus["locus_id"])] if int(row["eligible_field_vote"])]
        pivot = min(candidates, key=lambda row: (int(row["absolute_distance"]), int(row["neighbor_ordinal"])))
        edge_id = f"G783-E{number:03d}"
        packet.append({
            "edge_id": edge_id, "batch_id": "GDT783_CHSKY_MAJORITY_VARIANT_FIELDS", "page": locus["page"],
            "physical_folio": locus["physical_folio"], "diagram_unit_id": f"LINE:{locus['locus']}",
            "pivot_visual_id": f"TOKEN:{locus['locus']}:{pivot['neighbor_ordinal']}", "pivot_locus": f"{locus['locus']}@{pivot['neighbor_ordinal']}",
            "target_visual_id": f"TOKEN:{locus['locus']}:{locus['target_ordinal_in_each_reader']}", "target_locus": f"{locus['locus']}@{locus['target_ordinal_in_each_reader']}",
            "relation_type": "MAJORITY_VARIANT_EXTERNAL_FIELD_CONTACT", "direction_basis": "TARGET_ALIGNED_TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_FIELD_ADJACENCY", "geometry_only_selection": "FALSE", "source_manifest_id": "GDT783",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT783_RUNNER", "relation_reviewer": "GDT783_VALIDATOR",
            "relation_confidence": "EXPLORATORY", "ambiguity_state": "TWO_OF_THREE_READER_MAJORITY__VARIANT_LETTERS_UNINTERPRETED",
            "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": "GDT783_CHSKY_MAJORITY_VARIANT_FIELDS", "locus_id": locus["locus_id"],
            "page": locus["page"], "physical_folio": locus["physical_folio"], "locus": locus["locus"],
            "reader_target_forms": "/".join(str(locus[field]) for field in ("zl3b_target_form", "it2a_target_form", "rf1b_target_form")),
            "target_ordinal": locus["target_ordinal_in_each_reader"], "pivot_ordinal": pivot["neighbor_ordinal"],
            "pivot_surface": pivot["majority_surface"], "pivot_axes": pivot["clean_pool_axes"], "target_masked": 1,
            "physical_locus_weight": 1, "score_eligible": 0, "variant_letter_export_credit": 0, "component_export_credit": 0,
        })
    return packet, crosswalk


def artifact_readme() -> str:
    return """# GDT783 artifacts

- `GDT783_3_PHYSICAL_LOCUS_ATLAS.tsv`: target plus two external majority-variant loci, each counted once.
- `GDT783_28_POSITIONAL_READER_CONSENSUS_NEIGHBOR_ATLAS.tsv`: target-aligned, target-masked reader-consensus fields with GDT754 sanitation and GDT768 displays.
- `GDT783_3_TARGET_MASKED_FIELD_SUMMARY.tsv`: two external R3 fields plus separate target R5 sensitivity.
- `GDT783_4_GDT781_ANALOG_PROVENANCE_AUDIT.tsv`: four parent analogs; `chky` is blocked.
- `GDT783_3_HISTORICAL_COMPARATOR_AUDIT.tsv`: real quality-register architectures with zero form credit.
- `GDT783_6_CANDIDATE_SCORECARDS.tsv`: transparent diagnostic ranking; HOT-only wins the sparse score.
- `GDT783_1_WORKING_REVISION.tsv`: practical HOT|DRY retained with split confidence; HOT-only published as minimum core and dissent.
- `GDT783_1_TARGET_PASSAGE_PATCH.tsv`: the only practical display refinement.
- `GDT783_2_EXTERNAL_WORKING_READER.tsv`: field audits, explicitly not renderer licences.
- `GDT783_376_RENDERER.tsv`: all 109 GDT782 columns inherited unchanged, then GDT783 fields.
- `GDT783_GDT388_VARIANT_FIELD_PACKET.tsv`, crosswalk and intake: acquisition-only relations.
- `RESULT.json`: compact result.

No artifact interprets a reader-variant letter as a component. German defaults are not plaintext.
"""


def build_report(result: Mapping[str, object], loci: Sequence[Mapping[str, object]], fields: Sequence[Mapping[str, object]], analogs: Sequence[Mapping[str, object]], scores: Sequence[Mapping[str, object]], revision: Mapping[str, object], patch: Mapping[str, object], readers: Sequence[Mapping[str, object]]) -> str:
    locus_table = "\n".join(f"| `{r['locus']}` | {r['locus_role']} | `{r['zl3b_target_form']}` | `{r['it2a_target_form']}` | `{r['rf1b_target_form']}` | {r['majority_reader_count']}/3 |" for r in loci)
    field_table = "\n".join(f"| `{r['locus']}` | {r['primary_radius']} | {r['eligible_consensus_donors']} | `{r['eligible_consensus_surfaces']}` | `{r['field_axis_union']}` |" for r in fields)
    analog_table = "\n".join(f"| `{r['donor_surface']}` | `{r['current_clean_pool_axes']}` | {r['audit_decision']} | {r['eligible_analogy_vote']} |" for r in analogs)
    score_table = "\n".join(f"| {r['score_rank']} | {r['candidate_id']} | {r['portable_default_de']} | `{r['candidate_axes']}` | {r['eligible_analogy_full_support']} | {r['external_physical_locus_full_support']} | {r['exploratory_score']} | {r['practical_selection_spec']} |" for r in sorted(scores, key=lambda row: int(row["score_rank"])))
    reader_quotes = "\n\n".join(f"> `{r['locus']}`: {r['working_consensus_field_render_de']}" for r in readers)
    return f"""# GDT783 — `chsky` majority-variant external-field audit

Status: `{result['status']}`

## Working result

The practical GDT781 whole default **`chsky=heiß und trocken`** remains
standing, now explicitly as a quality/state label with split confidence:
HOT is the portable C1 role; DRY is a C0 standing extension. At the one
already licensed target span the carrier is made explicit as
**`ol chsky=heiß-trockener Ansatz`**. None of these is a recovered lexeme.

The deliberately published dissent is important: the sparse deterministic
field score ranks **HOT-only / `heiß`** first. We do not suppress that result.
But three independently GDT754-clean edit-neighbor wholes still agree on
HOT|DRY, the strong external field supplies DRY, and historical pharmacy
registers make paired hot/dry labels ordinary. Under the exploratory retention
rule, DRY is therefore not discarded before a better card makes it impossible;
instead HOT-only becomes the portable minimum core and first rival.

## Three physical loci, never nine witnesses

| locus | role | ZL3b | IT2a | RF1b | majority |
|---|---|---|---|---|---:|
{locus_table}

Each physical locus has weight one. The `chrky` and `chsty` readings admit the
two external fields through a fixed two-of-three rule. Their differing letters
receive zero semantic credit. Every target slot—including the exact
`f86v5.15@12` discovery position—is removed before its context is read.

## Target-excluding fields

| locus | radius | clean donors | donor wholes | axes |
|---|---:|---:|---|---|
{field_table}

The fields genuinely disagree: `f25r.2` is locally cold/dry, while `f103r.37`
is hot/moist with stage values. The target R5 sensitivity is hot and not dry.
Reader-boundary shifts are marked; no alternate reader is counted as another
occurrence. GDT768 supplies the current `chor=Blütenstand` display but only its
inherited PART axis votes.

## Four parent analogs

| donor | current axes | audit | vote |
|---|---|---|---:|
{analog_table}

`chky` is a GDT754 source composition and cannot vote. The remaining three
complete wholes still share HOT|DRY. Their correlation and the absence of DRY
from both HOT-bearing target-excluding fields are the main counterevidence,
so DRY is C0 rather than a second C1 axis.

## Six explicit candidates and the unresolved dissent

| rank | id | default | axes | clean analogs | external full fields | score | practical spec |
|---:|---|---|---|---:|---:|---:|---:|
{score_table}

The diagnostic score is not a lexical probability. It favors minimum complete
axis coverage and therefore chooses HOT-only. The separate frozen practical
selection retains the still-possible parent HOT|DRY card with split confidence.
Material, preparation-stage and process readings remain published rivals;
`erhitzt` would overstate a process absent from the primary fields.

## Historical comparison

Bound Clm 667 observations contain 19 HOT+DRY, three HOT+MOIST and one HOT-only
row among 28. Early-fifteenth-century Wellcome MS.542 explicitly has
*calidum et siccum* plus degree; Pal.lat.1234 has thermal degree rubrics. These
sources show that both single and paired quality slots are historically real.
They contribute zero `chsky` form, letter or lexeme credit and cannot decide
the dissent.

## Practical target patch

Parent:

> {patch['gdt782_inherited_patch_de']}

GDT783:

> {patch['gdt783_practical_patch_de']}

The brackets are one existing `ol`+whole span; no new token is consumed.

## External audit displays

{reader_quotes}

Both are `AGGREGATE_CARD_AUDIT_NOT_EXTERNAL_RENDERER_LICENSE`: they test the
card but install no external translation.

## Renderer and claim ceiling

All 109 GDT782 columns are inherited row-for-row. One added GDT783 target
display changes because the local carrier is now visible. Counts stay 270/376
contextual, 106 fallback and 230 consumed.

Confirmed lexemes, plaintext, substances, components and variant-letter
values all remain zero. No new page, image, OCR or transcription was opened;
`f84` and `f84r` remain sealed.

## Reproduction

```bash
python3 -B experiments/yolo/gdt783_chsky_majority_variant_external_field/src/run.py
python3 -B experiments/yolo/gdt783_chsky_majority_variant_external_field/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt783_chsky_majority_variant_external_field/artifacts/GDT783_GDT388_VARIANT_FIELD_PACKET.tsv
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts, report_path = args.artifacts_dir.resolve(), args.report_path.resolve()

    lock_count, lock_hash = verify_locks()
    base = load_base()
    by_line, _, cross, _, _, guard = base.load_context()
    pool, pool_diagnostics, _ = base.build_clean_pool()
    provenance = one_by(read_tsv(G754_PROVENANCE), "surface")
    later = one_by(read_tsv(G768_WORKING), "surface")
    final_rows = read_tsv(FINAL_SPEC)
    if len(final_rows) != 1 or any(final_rows[0][field] != "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit", "variant_letter_export_credit")):
        raise AssertionError("final selection spec changed")
    final = final_rows[0]

    loci = build_loci(cross, by_line)
    neighbors = build_neighbors(loci, pool, provenance, later)
    fields = build_fields(loci, neighbors)
    analogs = build_analogs(pool, provenance)
    historical = build_historical()
    candidates = read_tsv(CANDIDATES)
    if len(candidates) != 6 or any(row[field] != "0" for row in candidates for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit")):
        raise AssertionError("candidate deck changed")
    scores = build_scores(candidates, analogs, fields, final)
    revision = build_revision(final, scores, analogs, fields)
    renderer, owners = build_renderer(read_tsv(G782_RENDERER), revision)
    patch = build_patch(revision)
    external_readers = build_external_readers(loci, neighbors, revision)
    packet, crosswalk = make_packet(loci, neighbors)

    outputs = {
        "GDT783_3_PHYSICAL_LOCUS_ATLAS.tsv": loci,
        "GDT783_28_POSITIONAL_READER_CONSENSUS_NEIGHBOR_ATLAS.tsv": neighbors,
        "GDT783_3_TARGET_MASKED_FIELD_SUMMARY.tsv": fields,
        "GDT783_4_GDT781_ANALOG_PROVENANCE_AUDIT.tsv": analogs,
        "GDT783_3_HISTORICAL_COMPARATOR_AUDIT.tsv": historical,
        "GDT783_6_CANDIDATE_SCORECARDS.tsv": scores,
        "GDT783_1_WORKING_REVISION.tsv": [revision],
        "GDT783_1_TARGET_PASSAGE_PATCH.tsv": [patch],
        "GDT783_2_EXTERNAL_WORKING_READER.tsv": external_readers,
        "GDT783_376_RENDERER.tsv": renderer,
        "GDT783_GDT388_VARIANT_FIELD_PACKET.tsv": packet,
        "GDT783_RELATION_EDGE_CROSSWALK.tsv": crosswalk,
    }
    for name, rows in outputs.items():
        write_tsv(artifacts / name, rows)

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet
    intake = validate_relation_edge_packet(artifacts / "GDT783_GDT388_VARIANT_FIELD_PACKET.tsv")
    expected_intake = {"status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 2, "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0, "holdout_edges": 0, "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False, "holdout_gate": False, "mobile_null_gate": False, "score_ready": False, "errors": []}
    if intake != expected_intake:
        raise AssertionError(f"unexpected edge intake: {intake}")
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    parent_result = json.loads(G782_RESULT.read_text(encoding="utf-8"))
    result: dict[str, object] = {
        "experiment_id": "GDT783", "status": STATUS, "source_locks": lock_count,
        "source_lock_sha256": lock_hash,
        "source_spec_sha256": {"candidates": sha256(CANDIDATES), "final_selection": sha256(FINAL_SPEC), "historical_comparators": sha256(HISTORICAL_SPECS)},
        "inherited_guard": guard, "clean_pool": pool_diagnostics,
        "loci": {"physical_loci": 3, "masked_target_loci": 1, "external_majority_variant_loci": 2, "alternate_reader_independent_votes": 0, "positional_neighbor_slots": len(neighbors), "eligible_primary_field_donors": sum(int(row["eligible_field_vote"]) for row in neighbors), "gdt754_sanitized_neighbor_slots": sum(row["neighbor_class"] == "SANITIZED_GDT754_WHOLE_HYPOTHESIS" for row in neighbors), "gdt768_display_override_slots": sum(int(row["gdt768_display_override"]) for row in neighbors)},
        "analogy": {"parent_analogs": 4, "eligible_clean_analogs": 3, "gdt754_blocked_analogs": 1, "blocked_surface": "chky", "eligible_common_axes": "HOT|DRY"},
        "adjudication": {"candidate_rows": 6, "score_winner": "C01_HOT_QUALITY", "practical_selected_candidate": final["selected_candidate_id"], "practical_whole_default_de": final["practical_whole_default_de"], "target_span_default_de": final["target_span_default_de"], "portable_minimum_core_de": final["portable_minimum_core_de"], "hot_confidence": final["hot_confidence"], "dry_confidence": final["dry_confidence"], "dissent_retained": True, "external_renderer_licenses": 0},
        "historical": {"comparators": 3, "clm667_rows": 28, "clm667_hot_dry": 19, "clm667_hot_moist": 3, "clm667_hot_only": 1, "voynich_form_credit": 0},
        "renderer": {"rows": len(renderer), "gdt782_contextual": parent_result["renderer"]["gdt782_contextual"], "gdt783_contextual": sum(int(row["gdt783_renderer_contextual"]) for row in renderer), "gdt782_fallbacks": parent_result["renderer"]["gdt782_fallbacks"], "gdt783_fallbacks": sum(1-int(row["gdt783_renderer_contextual"]) for row in renderer), "display_changes": sum(int(row["gdt783_display_changed"]) for row in renderer), "unchanged_non_target_rows": 375, "inherited_parent_columns": len(read_tsv(G782_RENDERER)[0])},
        "consumption": {"gdt782_unique_right_tokens": parent_result["consumption"]["gdt782_unique_right_tokens"], "gdt783_unique_right_tokens": len(owners), "new_consumptions": 0, "collisions": 0},
        "relation_packet": intake, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "numeric_identities": 0, "specific_substances": 0, "component_exports": 0, "variant_letter_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": "One replaceable practical HOT|DRY whole card with HOT-only minimum core and one existing local ol-plus-whole span display; external fields are audits only; no lexeme, plaintext, substance, component or variant-letter value.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.write_text(build_report(result, loci, fields, analogs, scores, revision, patch, external_readers), encoding="utf-8")
    (artifacts / "README.md").write_text(artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
