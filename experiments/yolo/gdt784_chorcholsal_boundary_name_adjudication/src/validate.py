#!/usr/bin/env python3
"""Independent validator for GDT784's ``chorcholsal`` adjudication.

The validator deliberately does not import the producer.  It reconstructs
the complete-word census, reader-exact inventory, exact chor/chol contacts,
the target boundary in four transcriptions, and the Stolfi comparison panel
through guarded source queries before inspecting any GDT784 result.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
LOCKS = SRC / "SOURCE_LOCK.tsv"
CANDIDATES = SRC / "CANDIDATE_4_SPECS.tsv"
FINAL = SRC / "FINAL_SELECTION_SPEC.tsv"
HISTORICAL = SRC / "HISTORICAL_COMPARATOR_SPECS.tsv"
MODELS = SRC / "SEGMENTATION_MODEL_SPECS.tsv"
STOLFI_SPECS = SRC / "STOLFI_COMPARATOR_LOCUS_SPECS.tsv"
TARGET_SPEC = SRC / "TARGET_BOUNDARY_SPEC.tsv"
VISUAL_SPEC = SRC / "VISUAL_AUDIT_SPEC.tsv"
REPORT = EXP / "REPORT.md"
MANIFEST = EXP / "experiment.json"

ALLOWLIST = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
LINES = Path("transcription/voynich_zl3b_lines.tsv")
STOLFI = Path("transcription/voynich_stolfi25e1_lines.tsv")
G759 = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/PART_STATE_23_EXACT_PAIR_ATLAS.tsv"
G768 = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G762 = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv"
G779 = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_WORKING_DICTIONARY.tsv"
G775 = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/EXACT_FRAME_REPETITION.tsv"
G781_SELECTED = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv"
G781_CARDS = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv"
G777_SAL = ROOT / "experiments/yolo/gdt777_ol_registered_split_fusion_composer/artifacts/SAL_SPLIT_NEGATIVE_CONTROL.tsv"
PARENT_RENDERER = ROOT / "experiments/yolo/gdt783_chsky_majority_variant_external_field/artifacts/GDT783_376_RENDERER.tsv"

EXPECTED_SOURCE_HASHES = {
    "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv": "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483",
    "transcription/voynich_zl3b_tokens.tsv": "6a061a26edc05ff37dc386c2215774c229a5ff087d3091e68bdd4983a6c007aa",
    "transcription/voynich_cross_transcription_lines.tsv": "ff3a4559004a29764c60102326de154b29fbba06a2a206bdd76d7feda432e16c",
    "transcription/voynich_zl3b_lines.tsv": "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv": "47e8c7375503c2af7c95049392660de23556993ef78c1f24a10af6d9d7a1ed3c",
    "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py": "94b15ffaa293ea0dc55b7467fbada2c0d9bd0e9c636070d3e93b6857491389cc",
    "transcription/voynich_stolfi25e1_lines.tsv": "b4c83c18f8f814e547ab4a849dab8cf24188680fc512d9497885bdaa0d944988",
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/PART_STATE_23_EXACT_PAIR_ATLAS.tsv": "ad16ce2036a2cbc67f85e506a34b8e2ca46bb270d0562c6027f278ab4056b990",
    "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv": "2c9c805b12aa1adf1b858b8e4c6355a1b30ebbc85f0b4d0f74578a4a4a6ccde9",
    "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/SEMANTIC_PRECEDENCE_REPAIR_AUDIT.tsv": "29364a5ef3f4a720d8e214e884c9198d2ccda8870acef86dfd81f132863f625f",
    "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_WORKING_DICTIONARY.tsv": "a6a425c6fec7a93237e42545debf39118e2c2d072d1071010782857ad5c81c51",
    "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/EXACT_FRAME_REPETITION.tsv": "d2037b1d0b03ce5ed2cf32a82eb9963afc542f7e0bdb996448ac8883942aca80",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv": "9b7026e64499bf952ab6d84554c5d60c20ad05f99278841df8e1057250bfaa40",
    "experiments/yolo/gdt777_ol_registered_split_fusion_composer/artifacts/SAL_SPLIT_NEGATIVE_CONTROL.tsv": "f6d3cc11930981213d84a8c50dcaa14cbb5ac231fe4e83ecef0bb5996c1fbce6",
    "experiments/yolo/gdt783_chsky_majority_variant_external_field/artifacts/GDT783_376_RENDERER.tsv": "e374472ef081871481960a8d9395cfb3ae78be9ab5e043ccd8bb1694c9bf687a",
}
EXPECTED_LOCK_TABLE_HASH = "0a2140c5032272b032dfd9113a0c2366b65c49b2947a73ca5079dc34d72f8d34"
EXPECTED_SPEC_HASHES = {
    TARGET_SPEC: "60fab72d89c153d6bb2474e5a589d65c7e0e24570ff947703358c708a1ecac86",
    STOLFI_SPECS: "8d5269ec605b34725ab72e4ae523821ae6272eebf9c3c4c1830eef3efea60482",
    VISUAL_SPEC: "1e50b8a352ce361502b6fe9d3b8b2e414f44d29c9883f13bdfe4e7a9b73183d0",
    MODELS: "ad46608b93f3d28bf46e81a811b0f8b912635cfa77de80d215301b31f4947aff",
    CANDIDATES: "8008fce06aeea745b51a3c5f0bf2a9396dd2e847bb4153eade8c9ab148c3124e",
    FINAL: "a892f69ee458d4ca4d4b0fc7ba30c7a0db0f1797ace3dba9b821db2d6694c0a3",
    HISTORICAL: "49e0b6a97983d62a960be137561e586004cc08c3591313baf8e932fd9de4ee2a",
}
EXPECTED_RUNNER_HASH = "b5daa9e958c85f4fc644845098a9efecc96c83cec817c2f724bd551ff247cb27"

SURFACES = ("chorcholsal", "chor", "chol", "sal")
EXPECTED_RAW = Counter({"chorcholsal": 1, "chor": 190, "chol": 343, "sal": 37})
EXPECTED_EXACT = Counter({"chorcholsal": 1, "chor": 176, "chol": 303, "sal": 33})
TARGET_LOCUS = "f88r.22"
TARGET_LINE = "ychey okaiin chol cheor ol chorcholsal"
COMPARATOR_LOCI = (
    "f2v.6", "f3r.8", "f9v.2", "f15v.12", "f16v.5", "f16v.9",
    "f28v.3", "f32v.10", "f42v.1", "f47r.7", "f49v.50",
    "f100r.15", "f100r.23",
)


class Audit:
    def __init__(self) -> None:
        self.count = 0

    def check(self, condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        self.count += 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def unique(rows: Sequence[Mapping[str, str]], field: str) -> dict[str, Mapping[str, str]]:
    output: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = row[field]
        if key in output:
            raise AssertionError(f"duplicate {field}: {key}")
        output[key] = row
    return output


def guarded_query(relative: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(relative), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guard stats missing")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"].startswith("f84") for row in rows):
        raise AssertionError("sealed selector materialized")
    return rows, {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}


def validate_locks_and_specs(audit: Audit) -> None:
    rows = read_tsv(LOCKS)
    audit.check(len(rows) == len(EXPECTED_SOURCE_HASHES) == 15, "fifteen source locks")
    by_path = unique(rows, "path")
    audit.check(set(by_path) == set(EXPECTED_SOURCE_HASHES), "exact source-lock path set")
    for relative, expected in EXPECTED_SOURCE_HASHES.items():
        path = Path(relative)
        audit.check(not path.is_absolute() and ".." not in path.parts, f"safe source path {relative}")
        audit.check(by_path[relative]["expected_sha256"] == expected, f"declared source hash {relative}")
        audit.check(sha256(ROOT / path) == expected, f"source rehash {relative}")
    audit.check(sha256(LOCKS) == EXPECTED_LOCK_TABLE_HASH, "source-lock table hash")
    for path, expected in EXPECTED_SPEC_HASHES.items():
        audit.check(sha256(path) == expected, f"frozen source spec {path.name}")
    audit.check(sha256(RUN) == EXPECTED_RUNNER_HASH, "frozen runner hash")

    target = read_tsv(TARGET_SPEC)
    audit.check(len(target) == 1, "one target boundary spec")
    target_row = target[0]
    audit.check(
        (target_row["surface"], target_row["page"], target_row["locus"], target_row["ol_ordinal"], target_row["target_ordinal"])
        == ("chorcholsal", "f88r", TARGET_LOCUS, "5", "6"),
        "target coordinate frozen",
    )
    audit.check(target_row["current_line_eva"] == TARGET_LINE and target_row["stolfi_target_fragment"] == "chor,chol.sal", "target forms frozen")
    audit.check(target_row["target_meaning_masked"] == "1", "target meaning masked during adjudication")
    audit.check(all(target_row[field] == "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit")), "target zero claims")

    stolfi = read_tsv(STOLFI_SPECS)
    audit.check(len(stolfi) == 13 and tuple(row["locus"] for row in stolfi) == COMPARATOR_LOCI, "thirteen frozen Stolfi controls")
    audit.check(all(row["target_excluded"] == "1" and row["semantic_credit"] == "0" for row in stolfi), "Stolfi controls are target-free and nonsemantic")

    visual = read_tsv(VISUAL_SPEC)
    audit.check(len(visual) == 1, "one frozen visual audit")
    audit.check(visual[0]["observed_external_boundary"] == "CLEAR_GAP_AFTER_OL", "visual external gap")
    audit.check(visual[0]["observed_internal_boundary"] == "NO_EQUAL_INTERNAL_GAP_INSIDE_CHORCHOLSAL", "visual fused interior")
    audit.check(visual[0]["visual_semantic_credit"] == visual[0]["new_image_access"] == "0", "visual audit zero semantic/new-image credit")

    models = read_tsv(MODELS)
    audit.check(len(models) == 4 and [row["model_id"] for row in models] == ["M01", "M02", "M03", "M04"], "four segmentation models")
    audit.check(sum(row["surface_whole_preserved"] == "1" for row in models) == 3, "three models preserve written whole")
    audit.check(sum(row["requires_equal_internal_gap"] == "1" for row in models) == 1, "only three-group rival requires internal gaps")
    audit.check(all(row["component_export_credit"] == "0" for row in models), "segmentation models export no components")

    candidates = read_tsv(CANDIDATES)
    audit.check(len(candidates) == 4 and len({row["candidate_id"] for row in candidates}) == 4, "four candidate specs")
    audit.check(sum(row["selected_by_practical_spec"] == "1" for row in candidates) == 1, "one practical candidate")
    audit.check(all(row[field] == "0" for row in candidates for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit")), "candidate zero claims")

    final = read_tsv(FINAL)
    audit.check(len(final) == 1 and final[0]["surface"] == "chorcholsal", "one final selection")
    audit.check(final[0]["selected_candidate_id"] in {row["candidate_id"] for row in candidates}, "final candidate exists")
    audit.check(final[0]["whole_boundary_confidence"] == "C2" and final[0]["part_dry_echo_confidence"] == "C1" and final[0]["sal_semantic_confidence"] == "C0_OPEN", "split confidence frozen")
    audit.check(all(final[0][field] == "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit", "specific_substance_confirmed")), "final zero claims")

    historical = read_tsv(HISTORICAL)
    audit.check(len(historical) == 5 and [row["comparator_id"] for row in historical] == [f"G784-HC{number:02d}" for number in range(1, 6)], "five historical comparators")
    audit.check(sum(int(row["supports_learned_name_plus_short_field"]) for row in historical) == 5, "five learned-name architecture comparators")
    audit.check(sum(int(row["supports_powder_or_dry_drug_form"]) for row in historical) == 2, "two powder-form architecture comparators")
    audit.check(all(row["selects_voynich_identity"] == row["spelling_credit"] == "0" for row in historical), "historical comparators have no identity or spelling credit")


def enumerate_partitions(surface: str, inventory: set[str], minimum: int) -> list[tuple[str, ...]]:
    output: list[tuple[str, ...]] = []

    def visit(start: int, parts: tuple[str, ...]) -> None:
        if start == len(surface):
            if len(parts) >= 2:
                output.append(parts)
            return
        for end in range(start + minimum, len(surface) + 1):
            segment = surface[start:end]
            if segment in inventory:
                visit(end, (*parts, segment))

    visit(0, ())
    return sorted(output)


def reconstruct_cache(audit: Audit) -> dict[str, object]:
    pages = {row["page"] for row in read_tsv(ALLOWLIST)}
    audit.check(len(pages) == 179 and not any(page.startswith("f84") for page in pages), "179-page unsealed selector")
    tokens, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean,all_three_present,all_present_exact")
    line_rows, line_stats = guarded_query(LINES, pages, "page,locus,line_number,section,language,hand,token_count")
    expected_stats = {
        "tokens": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
        "cross": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "lines": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150},
    }
    audit.check(token_stats == expected_stats["tokens"], "guarded token counts")
    audit.check(cross_stats == expected_stats["cross"], "guarded cross-reader counts")
    audit.check(line_stats == expected_stats["lines"], "guarded line counts")

    by_line: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for rows in by_line.values():
        rows.sort(key=lambda row: int(row["token_index"]))
    cross = unique(cross_rows, "locus")
    line_meta = unique(line_rows, "locus")
    audit.check(set(by_line) <= set(cross) and set(by_line) <= set(line_meta), "every tokenized locus has cross-reader and line metadata")
    audit.check(set(cross) == set(line_meta), "cross-reader and line-metadata locus identity")

    raw_counts: Counter[str] = Counter()
    exact_counts: Counter[str] = Counter()
    exact_flags: dict[tuple[str, int], int] = {}
    exact_pairs: Counter[tuple[str, str]] = Counter()
    exact_pair_loci: defaultdict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    for locus, line in by_line.items():
        readers = (
            cross[locus]["zl3b_clean"].split(),
            cross[locus]["it2a_clean"].split(),
            cross[locus]["rf1b_clean"].split(),
        )
        seen: Counter[str] = Counter()
        capacity = {
            surface: min(reader.count(surface) for reader in readers)
            for surface in {row["eva"] for row in line}
        }
        for ordinal, token in enumerate(line, 1):
            surface = token["eva"]
            raw_counts[surface] += 1
            seen[surface] += 1
            is_exact = int(seen[surface] <= capacity[surface])
            exact_flags[(locus, ordinal)] = is_exact
            if is_exact:
                exact_counts[surface] += 1
        for ordinal in range(1, len(line)):
            if exact_flags[(locus, ordinal)] and exact_flags[(locus, ordinal + 1)]:
                pair = (line[ordinal - 1]["eva"], line[ordinal]["eva"])
                exact_pairs[pair] += 1
                exact_pair_loci[pair].append((locus, ordinal))

    audit.check(sum(raw_counts.values()) == 32339, "raw complete-token universe")
    audit.check(sum(exact_counts.values()) == 24090, "reader-exact complete-token universe")
    audit.check(sum(exact_pairs.values()) == 16657, "reader-exact adjacent-pair universe")
    audit.check(Counter({surface: raw_counts[surface] for surface in SURFACES}) == EXPECTED_RAW, "four raw surface counts")
    audit.check(Counter({surface: exact_counts[surface] for surface in SURFACES}) == EXPECTED_EXACT, "four reader-exact surface counts")
    audit.check(exact_pairs[("chor", "chol")] == 8 and exact_pairs[("chol", "chor")] == 7, "bidirectional chor/chol exact contacts")
    audit.check(exact_pairs[("chol", "sal")] == exact_pairs[("chor", "sal")] == 0, "no separate sal pair support")
    audit.check(len({locus for locus, _ in exact_pair_loci[("chor", "chol")] + exact_pair_loci[("chol", "chor")]}) == 14, "fifteen contacts on fourteen loci")

    target_rows = [
        (locus, ordinal, row)
        for locus, rows in by_line.items()
        for ordinal, row in enumerate(rows, 1)
        if row["eva"] == "chorcholsal"
    ]
    audit.check(len(target_rows) == 1, "singleton target whole")
    locus, ordinal, target = target_rows[0]
    audit.check((locus, target["page"], ordinal, len(by_line[locus])) == (TARGET_LOCUS, "f88r", 6, 6), "target cache coordinate")
    audit.check(exact_flags[(locus, ordinal)] == 1 and by_line[locus][ordinal - 2]["eva"] == "ol", "target exact after ol")
    audit.check(" ".join(row["eva"] for row in by_line[locus]) == TARGET_LINE, "target ZL3b line")
    target_cross = cross[TARGET_LOCUS]
    reader_lines = (target_cross["zl3b_clean"], target_cross["it2a_clean"], target_cross["rf1b_clean"])
    audit.check(reader_lines == (TARGET_LINE,) * 3, "three current readers preserve fused target")
    audit.check(target_cross["all_three_present"] == target_cross["all_present_exact"] == "1", "target current readers exact")
    audit.check((line_meta[TARGET_LOCUS]["section"], line_meta[TARGET_LOCUS]["language"], line_meta[TARGET_LOCUS]["hand"], line_meta[TARGET_LOCUS]["token_count"]) == ("P", "A", "1", "6"), "target line metadata")

    exact_inventory = {surface for surface, count in exact_counts.items() if count}
    partitions3 = enumerate_partitions("chorcholsal", exact_inventory, 3)
    partitions2 = enumerate_partitions("chorcholsal", exact_inventory, 2)
    audit.check(partitions3 == [("chor", "chol", "sal")], "only min-length-three recurrent-whole split")
    audit.check(len(partitions2) == 10, "ten min-length-two recurrent-whole splits")
    audit.check(("chor", "chol", "sal") in partitions2 and ("chor", "chols", "al") in partitions2, "principal min-length-two rivals present")

    pair_rows = [row for row in read_tsv(G759) if {row["left_surface"], row["right_surface"]} == {"chor", "chol"}]
    audit.check(len(pair_rows) == 15, "fifteen inherited chor/chol contacts")
    audit.check(Counter(row["exact_span_eva"] for row in pair_rows) == Counter({"chor chol": 8, "chol chor": 7}), "inherited pair directions")
    pair_coordinates = {(row["locus"], int(row["left_token_ordinal"])) for row in pair_rows}
    reconstructed_coordinates = set(exact_pair_loci[("chor", "chol")] + exact_pair_loci[("chol", "chor")])
    audit.check(pair_coordinates == reconstructed_coordinates, "inherited pair atlas matches guarded reconstruction")
    audit.check(all(row["reader_exact_left"] == row["reader_exact_right"] == "1" and row["component_export_credit"] == "0" for row in pair_rows), "pair evidence exact and nonexporting")

    return {
        "pages": pages,
        "by_line": dict(by_line),
        "cross": cross,
        "line_meta": line_meta,
        "raw_counts": raw_counts,
        "exact_counts": exact_counts,
        "exact_pairs": exact_pairs,
        "pair_loci": exact_pair_loci,
        "partitions3": partitions3,
        "partitions2": partitions2,
        "guard_stats": expected_stats,
        "target_reader_lines": reader_lines,
        "pair_rows": pair_rows,
    }


def extract_pair_boundaries(raw_text: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(r"(?=(chor|chol)([.,])(chor|chol)(?=[.,<!]|$))")
    return [(match.group(1), match.group(2), match.group(3)) for match in pattern.finditer(raw_text)]


def reconstruct_stolfi(audit: Audit, cache: Mapping[str, object]) -> dict[str, object]:
    specs = read_tsv(STOLFI_SPECS)
    pages = cache["pages"]
    assert isinstance(pages, set)
    rows, stats = guarded_query(STOLFI, pages, "page,locus,old_locus,code,raw_text,clean_text")
    audit.check(stats == {"selected": 1894, "skipped_forbidden": 33, "skipped_not_allowed": 1090}, "guarded Stolfi counts")
    by_locus = unique(rows, "locus")
    audit.check(TARGET_LOCUS in by_locus, "Stolfi target line present")
    target = by_locus[TARGET_LOCUS]
    audit.check(".ol.chor,chol.sal" in target["raw_text"], "Stolfi target raw punctuation")
    audit.check(target["clean_text"].endswith("ol chor chol sal"), "Stolfi clean target expands both boundaries")
    audit.check(target["raw_text"].count("chor,chol.sal") == 1, "one Stolfi target fragment")

    pair_rows = cache["pair_rows"]
    assert isinstance(pair_rows, list)
    exact_contact_loci = {str(row["locus"]) for row in pair_rows}
    available = exact_contact_loci & set(by_locus)
    audit.check(available == set(COMPARATOR_LOCI), "all and only thirteen available Stolfi contact controls")
    audit.check(exact_contact_loci - available == {"f21r.12"}, "f21r.12 is sole unavailable Stolfi contact")

    controls: list[dict[str, object]] = []
    total_boundaries = 0
    for spec in specs:
        locus = spec["locus"]
        raw = by_locus[locus]["raw_text"]
        observed = extract_pair_boundaries(raw)
        wanted: list[tuple[str, str]] = []
        direction = spec["expected_direction"]
        if direction in {"CHOR_CHOL", "BOTH"}:
            wanted.append(("chor", "chol"))
        if direction in {"CHOL_CHOR", "BOTH"}:
            wanted.append(("chol", "chor"))
        selected = [entry for entry in observed if (entry[0], entry[2]) in wanted]
        audit.check({(entry[0], entry[2]) for entry in selected} == set(wanted), f"Stolfi expected direction {locus}")
        audit.check(all(entry[1] == "." for entry in selected), f"Stolfi definite-dot control {locus}")
        total_boundaries += len(selected)
        controls.append({"spec": spec, "source": by_locus[locus], "boundaries": selected})
    audit.check(len(controls) == 13 and total_boundaries == 14, "thirteen dot-control lines with fourteen boundaries")
    audit.check(sum(len(row["boundaries"]) == 2 for row in controls) == 1, "only f2v.6 contributes both directions")
    return {"target": target, "controls": controls, "query_stats": stats}


def validate_public_artifacts(
    audit: Audit,
    cache: Mapping[str, object],
    stolfi: Mapping[str, object],
) -> tuple[dict[str, object], list[str]]:
    raw_counts = cache["raw_counts"]
    exact_counts = cache["exact_counts"]
    by_line = cache["by_line"]
    pair_source = cache["pair_rows"]
    assert isinstance(raw_counts, Counter)
    assert isinstance(exact_counts, Counter)
    assert isinstance(by_line, dict)
    assert isinstance(pair_source, list)

    # Four complete-word census rows are rebuilt from the guarded cache.  The
    # substring spellings have no credit in this census.
    census_rows = read_tsv(ART / "GDT784_4_SURFACE_CENSUS.tsv")
    census = unique(census_rows, "surface")
    audit.check(len(census_rows) == 4 and tuple(row["surface"] for row in census_rows) == SURFACES, "four ordered census rows")
    for surface in SURFACES:
        pages = {
            token["page"]
            for line in by_line.values()
            for token in line
            if token["eva"] == surface
        }
        row = census[surface]
        audit.check(
            (int(row["cache_occurrences"]), int(row["reader_exact_occurrences"]), int(row["page_labels"]))
            == (raw_counts[surface], exact_counts[surface], len(pages)),
            f"independent census {surface}",
        )
        audit.check(row["allowed_page_count"] == "179" and int(row["target_surface"]) == int(surface == "chorcholsal"), f"census scope {surface}")
        audit.check(row["substring_counts_used_as_target_identity"] == row["confirmed_lexeme"] == row["component_export_credit"] == "0", f"census zero claims {surface}")

    # Target boundary: the current editions are three alternate readings of
    # one manuscript, while Stolfi retains his punctuation confidence.
    boundary_rows = read_tsv(ART / "GDT784_4_READER_BOUNDARY_ATLAS.tsv")
    boundary = unique(boundary_rows, "reader_id")
    audit.check(len(boundary_rows) == 4 and set(boundary) == {"ZL3b", "IT2a", "RF1b", "Stolfi25e1"}, "four boundary readers")
    target_cross = cache["cross"][TARGET_LOCUS]
    for reader_id, source_field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")):
        row = boundary[reader_id]
        audit.check(row["clean_line_eva"] == target_cross[source_field] == TARGET_LINE, f"current reader line {reader_id}")
        audit.check(
            (row["reader_class"], row["target_written_group"], row["target_group_count"], row["external_boundary_after_ol"], row["internal_chor_chol_boundary"], row["internal_chol_sal_boundary"])
            == ("CURRENT_READER", "chorcholsal", "1", "DEFINITE_SPACE", "NONE", "NONE"),
            f"current reader boundary {reader_id}",
        )
        audit.check((row["surface_whole_preserved"], row["supports_surface_whole"], row["supports_internal_segmentation"], row["reader_vote_weight"]) == ("1", "1", "0", "1"), f"current reader whole support {reader_id}")
    legacy = boundary["Stolfi25e1"]
    stolfi_target = stolfi["target"]
    assert isinstance(stolfi_target, Mapping)
    audit.check(legacy["clean_line_eva"] == stolfi_target["clean_text"], "legacy clean target line")
    audit.check(
        (legacy["target_written_group"], legacy["target_group_count"], legacy["external_boundary_after_ol"], legacy["internal_chor_chol_boundary"], legacy["internal_chol_sal_boundary"])
        == ("chor,chol.sal", "3", "DOT", "COMMA", "DOT"),
        "legacy comma/dot target parse",
    )
    audit.check((legacy["surface_whole_preserved"], legacy["supports_surface_whole"], legacy["supports_internal_segmentation"]) == ("0", "0", "1"), "legacy split retained as rival")
    audit.check(all(row["meaning_credit"] == row["component_export_credit"] == "0" for row in boundary_rows), "reader boundaries have zero semantic credit")

    dot_rows = read_tsv(ART / "GDT784_14_STOLFI_BOUNDARY_CONTROL_ATLAS.tsv")
    audit.check(len(dot_rows) == 14 and len({row["audit_id"] for row in dot_rows}) == 14, "target plus thirteen Stolfi controls")
    target_dot = next(row for row in dot_rows if row["audit_role"] == "TARGET_LEGACY_SPLIT")
    audit.check(
        (target_dot["locus"], target_dot["relevant_stolfi_fragment"], target_dot["stolfi_boundary_class"], target_dot["representative_definite_dot"])
        == (TARGET_LOCUS, "chor,chol.sal", "COMMA_THEN_DOT", "0"),
        "target Stolfi boundary kept distinct from controls",
    )
    controls = stolfi["controls"]
    assert isinstance(controls, list)
    dot_by_locus = unique([row for row in dot_rows if row["audit_role"] == "GDT759_PAIR_DOT_COMPARATOR"], "locus")
    audit.check(set(dot_by_locus) == set(COMPARATOR_LOCI), "exact thirteen Stolfi control loci")
    for item in controls:
        spec = item["spec"]
        source = item["source"]
        observed = item["boundaries"]
        locus = spec["locus"]
        row = dot_by_locus[locus]
        direction = spec["expected_direction"]
        fragment = "chol.chor.chol" if direction == "BOTH" else "chor.chol" if direction == "CHOR_CHOL" else "chol.chor"
        audit.check(fragment in source["raw_text"] and row["relevant_stolfi_fragment"] == fragment, f"published definite-dot fragment {locus}")
        audit.check(row["audit_id"] == spec["comparator_id"] and row["modern_exact_pair_directions"] == direction, f"Stolfi control identity {locus}")
        audit.check(len(observed) == (2 if direction == "BOTH" else 1) and all(entry[1] == "." for entry in observed), f"independent Stolfi dots {locus}")
        audit.check((row["stolfi_boundary_class"], row["representative_definite_dot"], row["available_stolfi_line"], row["target_excluded_from_comparator_count"]) == ("DOT", "1", "1", "1"), f"Stolfi control flags {locus}")
    audit.check(sum(int(row["representative_definite_dot"]) for row in dot_rows) == 13, "thirteen representative dot controls")
    audit.check(all(row["supports_general_stolfi_dot_as_physical_gap"] == row["semantic_credit"] == "0" for row in dot_rows), "Stolfi punctuation is not promoted to physical or semantic proof")

    visual_specs = read_tsv(VISUAL_SPEC)
    visual_rows = read_tsv(ART / "GDT784_VISUAL_BOUNDARY_AUDIT.tsv")
    audit.check(len(visual_specs) == len(visual_rows) == 1, "one visual source and audit row")
    visual = visual_rows[0]
    for field, value in visual_specs[0].items():
        audit.check(visual[field] == value, f"visual source copy {field}")
    audit.check((visual["supports_external_ol_target_boundary"], visual["supports_internal_equal_gap"], visual["supports_surface_whole"], visual["observation_scope"]) == ("1", "0", "1", "BOUNDARY_ONLY"), "visual boundary-only adjudication")
    audit.check(visual["meaning_credit"] == visual["component_export_credit"] == "0", "visual zero semantic credit")

    pair_rows = read_tsv(ART / "GDT784_2_GDT759_PAIR_EVIDENCE.tsv")
    pair_by_direction = unique(pair_rows, "direction")
    audit.check(len(pair_rows) == 2 and set(pair_by_direction) == {"chor_TO_chol", "chol_TO_chor"}, "two order directions")
    for left, right, expected in (("chor", "chol", 8), ("chol", "chor", 7)):
        source = [row for row in pair_source if row["left_surface"] == left and row["right_surface"] == right]
        row = pair_by_direction[f"{left}_TO_{right}"]
        audit.check(len(source) == expected == int(row["exact_pair_occurrences"]), f"pair occurrence count {left}->{right}")
        audit.check(int(row["physical_loci"]) == len({item["locus"] for item in source}) and int(row["page_labels"]) == len({item["page"] for item in source}), f"pair locus/page counts {left}->{right}")
        audit.check(row["working_render_de"] == source[0]["primary_render_de"] and row["fused_counterpart_surface"] == left + right, f"pair source evidence {left}->{right}")
        audit.check(row["fused_counterpart_reader_exact_occurrences"] == "0" and all(item["fused_counterpart_reader_exact_occurrences"] == "0" for item in source), f"fused pair null {left}->{right}")
        audit.check((row["internal_echo_credit"], row["free_component_export"], row["confirmed_plaintext"]) == ("1", "0", "0"), f"nonexporting pair echo {left}->{right}")

    provenance_rows = read_tsv(ART / "GDT784_5_CURRENT_WHOLE_PROVENANCE.tsv")
    provenance = unique(provenance_rows, "surface")
    audit.check(len(provenance_rows) == 5 and set(provenance) == {"chor", "chol", "sal", "cheor", "chorcholsal"}, "five current whole-provenance rows")
    chor_source = next(row for row in read_tsv(G768) if row["surface"] == "chor")
    audit.check(provenance["chor"]["current_role_or_default_de"] == chor_source["portable_default_de"] and provenance["chor"]["concrete_display_de"] == chor_source["concrete_default_de"], "chor current whole card")
    audit.check(provenance["chor"]["working_confidence"] == chor_source["working_confidence"] and provenance["chor"]["counterevidence_de"] == chor_source["counterevidence_de"], "chor confidence and counterevidence")
    sal_repair = next(row for row in read_tsv(G762) if row["surface"] == "sal")
    sal_null = read_tsv(G777_SAL)
    audit.check(len(sal_null) == 1 and (sal_null[0]["guarded_fused_exact_occurrences"], sal_null[0]["guarded_raw_split_occurrences"], sal_null[0]["guarded_reader_exact_split_occurrences"]) == ("33", "5", "0"), "independent sal fusion control")
    audit.check(provenance["sal"]["current_role_or_default_de"] == "semantisch offen" and sal_repair["eva_initial_semantic_credit"] == "0", "sal remains semantically open")
    audit.check("0_OF_5_READER_EXACT_S_PLUS_AL" in provenance["sal"]["usable_credit"] and "Salz" in provenance["sal"]["counterevidence_de"], "sal negative evidence published")
    cheor_source = next(row for row in read_tsv(G779) if row["entry"] == "cheor")
    audit.check(provenance["cheor"]["current_role_or_default_de"] == cheor_source["preferred_gdt779_default_de"] and provenance["cheor"]["working_confidence"] == cheor_source["confidence"], "cheor current whole card")
    parent_target = next(row for row in read_tsv(G781_SELECTED) if row["right_surface"] == "chorcholsal")
    audit.check(provenance["chorcholsal"]["current_role_or_default_de"] == provenance["chorcholsal"]["concrete_display_de"] == "MASKED", "target meaning masked in provenance")
    audit.check(provenance["chorcholsal"]["working_confidence"] == parent_target["confidence"] and provenance["chorcholsal"]["counterevidence_de"] == parent_target["counterevidence"], "target parent provenance")
    audit.check(provenance["chol"]["working_confidence"] == "C2_RECURRENT_PART_STATE" and provenance["chol"]["usable_credit"] == "DRY_WHOLE_ROLE", "chol recurrent dry role")
    audit.check(all(row["component_export_credit"] == "0" for row in provenance_rows), "whole provenance exports no components")

    slot_rows = read_tsv(ART / "GDT784_2_SLOT_TWIN_ATLAS.tsv")
    slots = unique(slot_rows, "slot_role")
    audit.check(len(slot_rows) == 2 and set(slots) == {"TARGET_MASKED", "EXACT_SLOT_TWIN"}, "target and one exact slot twin")
    frames = {
        row["frame"]: row
        for row in read_tsv(G775)
        if row["frame"] in {"cheor|ol|chorcholsal", "cheor|ol|chockhar"}
    }
    audit.check(len(frames) == 2, "two selected GDT775 cheor-ol frames")
    audit.check(frames["cheor|ol|chorcholsal"]["occurrences"] == frames["cheor|ol|chockhar"]["occurrences"] == "1", "two inherited singleton frames")
    target_slot = slots["TARGET_MASKED"]
    twin_slot = slots["EXACT_SLOT_TWIN"]
    audit.check((target_slot["locus"], target_slot["register"], target_slot["frame"], target_slot["cheor_ordinal"], target_slot["ol_ordinal"], target_slot["x_ordinal"]) == ("f88r.22", "P|A|1", "cheor|ol|chorcholsal", "4", "5", "6"), "target slot geometry")
    audit.check((twin_slot["locus"], twin_slot["register"], twin_slot["frame"], twin_slot["cheor_ordinal"], twin_slot["ol_ordinal"], twin_slot["x_ordinal"]) == ("f100v.20", "P|A|1", "cheor|ol|chockhar", "6", "7", "8"), "exact twin geometry")
    parent_renderer = read_tsv(PARENT_RENDERER)
    parent_by_locus = unique([row for row in parent_renderer if row["locus"] in {"f88r.22", "f100v.20"}], "locus")
    audit.check(parent_by_locus["f100v.20"]["gdt783_default_de"] == twin_slot["current_x_or_span_default_de"] == "erhitzter Ansatz", "twin current complete-whole display")
    audit.check(parent_by_locus["f100v.20"]["gdt783_functional_axes"] == twin_slot["current_axes"] == "HOT|PREPARATION", "twin current axes")
    audit.check(target_slot["current_x_or_span_default_de"] == target_slot["current_axes"] == "MASKED" and target_slot["supports_preparation_value_slot"] == "0", "target slot remained masked")
    audit.check(twin_slot["supports_preparation_value_slot"] == "1" and all(row["target_meaning_used"] == row["component_export_credit"] == "0" for row in slot_rows), "slot twin is nonsemantic target-independent support")

    model_specs = read_tsv(MODELS)
    model_rows = read_tsv(ART / "GDT784_4_SEGMENTATION_ATLAS.tsv")
    models = unique(model_rows, "model_id")
    audit.check(len(model_rows) == 4 and set(models) == {row["model_id"] for row in model_specs}, "four published segmentation models")
    for spec in model_specs:
        row = models[spec["model_id"]]
        for field, value in spec.items():
            audit.check(row[field] == value, f"segmentation source copy {spec['model_id']}:{field}")
        audit.check((row["current_reader_fused_support"], row["legacy_stolfi_split_support"], row["visual_external_gap_support"], row["visual_equal_internal_gap_support"]) == ("3", "1", "1", "0"), f"segmentation boundary evidence {spec['model_id']}")
        audit.check((row["chor_chol_exact_forward"], row["chol_chor_exact_reverse"], row["standalone_chorchol_exact"]) == ("8", "7", "0"), f"segmentation pair evidence {spec['model_id']}")
        audit.check(row["adjudication"] == ("SELECT" if spec["model_id"] == "M02" else "RETAIN_RIVAL"), f"segmentation adjudication {spec['model_id']}")
        audit.check(row["default_is_translation"] == row["confirmed_lexeme"] == "0", f"segmentation zero identity {spec['model_id']}")

    historical_specs = read_tsv(HISTORICAL)
    historical_rows = read_tsv(ART / "GDT784_5_HISTORICAL_COMPARATOR_AUDIT.tsv")
    historical = unique(historical_rows, "comparator_id")
    audit.check(len(historical_rows) == 5 and set(historical) == {row["comparator_id"] for row in historical_specs}, "five historical audit rows")
    for spec in historical_specs:
        row = historical[spec["comparator_id"]]
        for field, value in spec.items():
            audit.check(row[field] == value, f"historical source copy {spec['comparator_id']}:{field}")
        audit.check(row["allowed_use_in_gdt784"] == "ARCHITECTURE_AND_CANDIDATE_CLASS_ONLY", f"historical use ceiling {spec['comparator_id']}")
        audit.check(row["voynich_identity_credit"] == row["component_export_credit"] == "0", f"historical zero Voynich credit {spec['comparator_id']}")

    candidate_specs = read_tsv(CANDIDATES)
    candidate_rows = read_tsv(ART / "GDT784_4_CANDIDATE_SCORECARDS.tsv")
    candidates = unique(candidate_rows, "candidate_id")
    audit.check(len(candidate_rows) == 4 and set(candidates) == {row["candidate_id"] for row in candidate_specs}, "four candidate scorecards")
    computed_scores: dict[str, int] = {}
    for spec in candidate_specs:
        row = candidates[spec["candidate_id"]]
        for field, value in spec.items():
            audit.check(row[field] == value, f"candidate source copy {spec['candidate_id']}:{field}")
        score = sum(int(spec[field]) for field in ("surface_whole_fit_points", "slot_twin_fit_points", "part_dry_echo_points", "historical_architecture_points")) - int(spec["semantic_overreach_penalty"])
        computed_scores[spec["candidate_id"]] = score
        audit.check(int(row["diagnostic_score"]) == score and row["score_is_probability"] == "0", f"candidate score {spec['candidate_id']}")
        audit.check(row["selection_scope"] == "ONE_EXACT_WHOLE_PLUS_EXISTING_OL_SPAN", f"candidate scope {spec['candidate_id']}")
    ranking = sorted(computed_scores, key=lambda candidate_id: (-computed_scores[candidate_id], candidate_id))
    audit.check([row["candidate_id"] for row in candidate_rows] == ranking and [int(candidates[candidate_id]["score_rank"]) for candidate_id in ranking] == [1, 2, 3, 4], "deterministic candidate ranking")
    final = read_tsv(FINAL)[0]
    audit.check(ranking[0] == final["selected_candidate_id"] == "C01_DRY_FLOWER_DRUG", "practical card is diagnostic winner")
    audit.check(sum(int(row["practical_selection"]) for row in candidate_rows) == 1 and candidates[final["selected_candidate_id"]]["practical_selection"] == "1", "one practical candidate selected")

    revision_rows = read_tsv(ART / "GDT784_1_WORKING_REVISION.tsv")
    audit.check(len(revision_rows) == 1, "one working revision")
    revision = revision_rows[0]
    audit.check((revision["surface"], revision["target_occurrence_id"], revision["locus"], revision["parent_default_de"]) == ("chorcholsal", "G769-T0488", "f88r.22", parent_target["new_gdt781_default_de"]), "revision parent coordinate")
    for field in ("selected_candidate_id", "practical_whole_default_de", "target_span_default_de", "portable_role_de", "decision", "confidence", "whole_boundary_confidence", "part_dry_echo_confidence", "sal_semantic_confidence", "selection_rule", "positive_evidence_de", "counterevidence_de"):
        audit.check(revision[field] == final[field], f"revision final-spec copy {field}")
    audit.check((revision["current_readers_fused"], revision["legacy_stolfi_split"], revision["stolfi_dot_comparator_loci"], revision["exact_preparation_slot_twin"]) == ("3", "1", "13", "f100v.20"), "revision evidence counts")
    audit.check(revision["visual_external_gap"] == visual["observed_external_boundary"] and revision["visual_internal_gap"] == visual["observed_internal_boundary"], "revision visual evidence")
    audit.check(revision["target_meaning_masked_during_adjudication"] == revision["replaceable"] == "1", "revision masked and replaceable")
    audit.check(all(revision[field] == "0" for field in ("default_is_translation", "confirmed_lexeme", "confirmed_plaintext", "component_export_credit", "specific_substance_confirmed")), "revision zero claims")

    patch_rows = read_tsv(ART / "GDT784_1_TARGET_PASSAGE_PATCH.tsv")
    audit.check(len(patch_rows) == 1, "one target passage patch")
    passage = patch_rows[0]
    audit.check((passage["target_occurrence_id"], passage["locus"], passage["target_ordinal"], passage["target_surface"], passage["written_line_eva"]) == ("G769-T0488", "f88r.22", "6", "chorcholsal", TARGET_LINE), "passage target coordinate")
    audit.check(f"⟦{final['target_span_default_de']}⟧" in passage["gdt784_bracketed_line_de"] and final["target_span_default_de"] in passage["gdt784_field_display_de"], "passage revised display")
    audit.check(passage["readable_compact_de"].endswith(final["target_span_default_de"]) and passage["display_status"] == "WORKING_DISPLAY_NOT_PLAINTEXT", "readable patch remains working display")
    audit.check(passage["target_meaning_masked_during_adjudication"] == "1" and all(passage[field] == "0" for field in ("default_is_translation", "confirmed_plaintext", "component_export_credit")), "passage mask and zero claims")

    renderer_rows = read_tsv(ART / "GDT784_376_RENDERER.tsv")
    audit.check(len(parent_renderer) == len(renderer_rows) == 376, "376 parent and child renderer rows")
    parent_fields = list(parent_renderer[0])
    audit.check(len(parent_fields) == 129 and all(field in renderer_rows[0] for field in parent_fields), "129 inherited renderer columns")
    parent_by_id = unique(parent_renderer, "target_occurrence_id")
    renderer_by_id = unique(renderer_rows, "target_occurrence_id")
    audit.check(set(parent_by_id) == set(renderer_by_id), "renderer occurrence identity preserved")
    for occurrence_id, parent in parent_by_id.items():
        child = renderer_by_id[occurrence_id]
        for field in parent_fields:
            audit.check(child[field] == parent[field], f"inherited renderer field {occurrence_id}:{field}")
    mutated = [row for row in renderer_rows if row["gdt784_branch"] != "INHERITED_GDT783"]
    audit.check(len(mutated) == 1 and mutated[0]["target_occurrence_id"] == "G769-T0488", "one target renderer adjudication")
    target_renderer = mutated[0]
    audit.check(target_renderer["gdt784_branch"] == "GDT784_BOUNDARY_NAME_ADJUDICATION" and target_renderer["gdt784_default_de"] == final["target_span_default_de"], "target renderer branch and display")
    audit.check(target_renderer["gdt784_practical_whole_default_de"] == final["practical_whole_default_de"] and target_renderer["gdt784_portable_role_de"] == final["portable_role_de"], "target renderer final card")
    audit.check((target_renderer["gdt784_surface_whole_preserved"], target_renderer["gdt784_part_dry_echo"], target_renderer["gdt784_sal_semantic_open"], target_renderer["gdt784_display_changed"]) == ("1", "1", "1", "1"), "target renderer adjudication flags")
    audit.check(all(row["gdt784_default_de"] == row["gdt783_default_de"] for row in renderer_rows if row is not target_renderer), "non-target displays inherited")
    audit.check(sum(int(row["gdt784_renderer_contextual"]) for row in renderer_rows) == 270 and sum(1 - int(row["gdt784_renderer_contextual"]) for row in renderer_rows) == 106, "renderer 270 contextual and 106 fallback")
    consumed = [token for row in renderer_rows for token in row["gdt784_consumed_token_ids"].split("|") if token not in {"", "NONE"}]
    audit.check(len(consumed) == len(set(consumed)) == 230 and sum(int(row["gdt784_consumed_token_count"]) for row in renderer_rows) == 230, "230 noncolliding consumed tokens")
    audit.check(sum(int(row["gdt784_display_changed"]) for row in renderer_rows) == 1, "one renderer display change")
    audit.check(all(row["gdt784_default_is_translation"] == row["gdt784_confirmed_lexeme"] == row["gdt784_confirmed_plaintext"] == row["gdt784_component_export_credit"] == "0" for row in renderer_rows), "renderer zero translation, lexeme, plaintext and component claims")

    packet_rows = read_tsv(ART / "GDT784_GDT388_BOUNDARY_PACKET.tsv")
    crosswalk_rows = read_tsv(ART / "GDT784_RELATION_EDGE_CROSSWALK.tsv")
    audit.check(len(packet_rows) == len(crosswalk_rows) == 2 and {row["edge_id"] for row in packet_rows} == {row["edge_id"] for row in crosswalk_rows} == {"G784-E001", "G784-E002"}, "two boundary packet edges")
    audit.check({row["relation_type"] for row in packet_rows} == {"CLEAR_EXTERNAL_WORD_GAP", "NO_EQUAL_INTERNAL_GAP"}, "external and internal boundary edges")
    audit.check(all(row["page"] == "f88r" and row["physical_folio"] == "f88" and row["formal_access_state"] == "SEALED_NOT_ACCESSED" for row in packet_rows), "packet page and seal state")
    audit.check(all(row["page_crop_sha256"] == visual["crop_sha256"] and row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_BOUNDARY_RELATION" for row in packet_rows), "packet crop binding and ineligibility")
    audit.check(all(row["surface_whole_preserved"] == "1" and row["semantic_score_eligible"] == row["component_export_credit"] == "0" for row in crosswalk_rows), "crosswalk whole preserved and zero score/export")
    expected_intake = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 2,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
        "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(intake == expected_intake, "stored relation-packet intake")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / "GDT784_GDT388_BOUNDARY_PACKET.tsv")],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    audit.check(completed.returncode == 0 and json.loads(completed.stdout) == expected_intake, "executable relation-packet intake")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    expected_status = (
        "PASS__1_TARGET_WHOLE__3_CURRENT_READERS_FUSED__STOLFI_SPLIT__"
        "13_STOLFI_DOT_COMPARATOR_LOCI__VISUAL_EXTERNAL_GAP_INTERNAL_NO_EQUAL_GAP__"
        "190_176_CHOR__343_303_CHOL__37_33_SAL__8_7_PART_STATE_PAIRS__"
        "SLOT_TWIN_F100V20__PRACTICAL_TROCKENE_BLUETENDROGE__"
        "270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__ZERO_COMPONENT_EXPORT"
    )
    audit.check(result["experiment_id"] == "GDT784" and result["status"] == expected_status, "result identity and status")
    audit.check(result["source_locks"] == 15 and result["source_lock_sha256"] == sha256(LOCKS), "result source-lock binding")
    audit.check(result["inherited_guard"] == {"allowed_pages": 179, **cache["guard_stats"]}, "result guarded cache counts")
    audit.check(result["stolfi_guard"] == stolfi["query_stats"], "result guarded Stolfi counts")
    expected_census = {
        surface: {
            "cache": raw_counts[surface], "reader_exact": exact_counts[surface],
            "pages": len({token["page"] for line in by_line.values() for token in line if token["eva"] == surface}),
        }
        for surface in SURFACES
    }
    audit.check(result["surface_census"] == expected_census, "result surface census")
    audit.check(result["boundary"] == {"current_fused_readers": 3, "legacy_stolfi_split_readers": 1, "stolfi_dot_comparator_loci": 13, "visual_clear_external_gap": True, "visual_equal_internal_gap": False, "surface_whole_confidence": "C2"}, "result boundary summary")
    audit.check(result["constituent_order"] == {"chor_chol": 8, "chol_chor": 7, "contact_occurrences": 15, "contact_loci": 14, "standalone_chorchol_exact": 0, "part_dry_echo_confidence": "C1", "sal_semantic_confidence": "C0_OPEN"}, "result constituent-order summary")
    audit.check(result["adjudication"]["score_winner"] == final["selected_candidate_id"] and result["adjudication"]["practical_whole_default_de"] == final["practical_whole_default_de"] and result["adjudication"]["target_span_default_de"] == final["target_span_default_de"], "result final card")
    audit.check(result["adjudication"]["target_meaning_masked"] is True and result["adjudication"]["identity_confidence"] == "C0", "result target mask and identity confidence")
    audit.check(result["historical"] == {"comparators": 5, "identity_credit": 0, "spelling_credit": 0}, "result historical ceiling")
    audit.check(result["renderer"] == {"rows": 376, "contextual": 270, "fallbacks": 106, "unique_consumed_tokens": 230, "display_changes": 1, "unchanged_non_target_rows": 375, "inherited_parent_columns": 129}, "result renderer counts")
    audit.check(result["relation_packet"] == expected_intake, "result relation intake")
    for field in ("confirmed_lexemes", "confirmed_plaintext_clauses", "specific_substances", "component_exports", "new_pages", "new_images", "new_ocr", "new_transcriptions", "sealed_pages_accessed"):
        audit.check(result[field] == 0, f"result zero {field}")

    zero_fields = {
        "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
        "component_export_credit", "specific_substance_confirmed",
        "semantic_credit", "meaning_credit", "voynich_identity_credit",
        "spelling_credit", "selects_voynich_identity", "score_is_probability",
        "semantic_score_eligible", "substring_counts_used_as_target_identity",
        "free_component_export", "target_meaning_used", "new_image_access",
    }
    output_names = (
        "GDT784_4_SURFACE_CENSUS.tsv",
        "GDT784_4_READER_BOUNDARY_ATLAS.tsv",
        "GDT784_14_STOLFI_BOUNDARY_CONTROL_ATLAS.tsv",
        "GDT784_VISUAL_BOUNDARY_AUDIT.tsv",
        "GDT784_2_GDT759_PAIR_EVIDENCE.tsv",
        "GDT784_5_CURRENT_WHOLE_PROVENANCE.tsv",
        "GDT784_2_SLOT_TWIN_ATLAS.tsv",
        "GDT784_4_SEGMENTATION_ATLAS.tsv",
        "GDT784_5_HISTORICAL_COMPARATOR_AUDIT.tsv",
        "GDT784_4_CANDIDATE_SCORECARDS.tsv",
        "GDT784_1_WORKING_REVISION.tsv",
        "GDT784_1_TARGET_PASSAGE_PATCH.tsv",
        "GDT784_376_RENDERER.tsv",
        "GDT784_GDT388_BOUNDARY_PACKET.tsv",
        "GDT784_RELATION_EDGE_CROSSWALK.tsv",
        "RELATION_PACKET_INTAKE.json",
        "RESULT.json",
    )
    for name in output_names:
        if not name.endswith(".tsv"):
            continue
        for row_number, row in enumerate(read_tsv(ART / name), 2):
            for field in zero_fields & set(row):
                audit.check(row[field] == "0", f"claim zero {name}:{row_number}:{field}")

    with tempfile.TemporaryDirectory(prefix="gdt784_replay_") as raw:
        replay_root = Path(raw)
        replay_art = replay_root / "artifacts"
        replay_report = replay_root / "REPORT.md"
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_art), "--report-path", str(replay_report)],
            cwd=ROOT, env=environment, text=True, capture_output=True, check=False,
        )
        audit.check(completed.returncode == 0, "runner replay exits zero")
        replayed: list[str] = []
        for name in output_names:
            audit.check((replay_art / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")
            replayed.append(name)
        audit.check((replay_art / "README.md").read_bytes() == (ART / "README.md").read_bytes(), "byte replay artifact README")
        audit.check(replay_report.read_bytes() == REPORT.read_bytes(), "byte replay report")
        replayed.extend(("README.md", "../REPORT.md"))
    return result, replayed


def validate_manifest_and_privacy(audit: Audit, result: Mapping[str, object]) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit.check(manifest["schema_version"] == 1 and manifest["experiment_id"] == "GDT784" and manifest["slug"] == "chorcholsal_boundary_name_adjudication", "manifest identity")
    audit.check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest explicit seals")
    audit.check(
        manifest["commands"] == {
            "run": "python3 -B experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/src/run.py",
            "validate": "python3 -B experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/src/validate.py",
        },
        "manifest reproduction commands",
    )
    audit.check(bool(manifest["question"]) and bool(manifest["claim_ceiling"]), "manifest question and claim ceiling")
    audit.check(
        set(manifest["dependencies"]) >= {"GDT388", "GDT635", "GDT734", "GDT759", "GDT762", "GDT768", "GDT775", "GDT777", "GDT779", "GDT781", "GDT782", "GDT783"},
        "manifest dependency floor",
    )

    inputs = manifest["inputs"]
    input_by_path = unique(inputs, "path")
    audit.check(set(input_by_path) == set(EXPECTED_SOURCE_HASHES), "manifest exact input path set")
    for relative, expected in EXPECTED_SOURCE_HASHES.items():
        row = input_by_path[relative]
        audit.check(row["sha256"] == expected and bool(row["role"]), f"manifest input hash and role {relative}")

    validation_relative = "experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/artifacts/VALIDATION.json"
    outputs = manifest["outputs"]
    output_by_path = unique(outputs, "path")
    actual_core = {
        str(path.relative_to(ROOT))
        for path in EXP.rglob("*")
        if path.is_file() and path != MANIFEST and path != ART / "VALIDATION.json"
    }
    declared_core = set(output_by_path) - {validation_relative}
    audit.check(declared_core == actual_core, "manifest exact noncircular output path set")
    for relative in sorted(actual_core):
        row = output_by_path[relative]
        path = Path(relative)
        audit.check(not path.is_absolute() and ".." not in path.parts, f"manifest safe output path {relative}")
        audit.check(row["sha256"] == sha256(ROOT / path) and bool(row["role"]), f"manifest output hash and role {relative}")

    validation_meta = manifest["validation"]
    validation_declared = validation_relative in output_by_path
    validation_file_exists = (ART / "VALIDATION.json").is_file()
    audit.check(
        (
            validation_meta == {"artifact": None, "status": "NOT_RUN"}
            and not validation_declared
        )
        or (
            validation_meta == {"artifact": validation_relative, "status": "PASS"}
            and validation_declared
            and validation_file_exists
            and output_by_path[validation_relative]["sha256"] == sha256(ART / "VALIDATION.json")
        ),
        "manifest bootstrap-or-final validation state",
    )
    audit.check(
        manifest["status"] == result["status"]
        or (validation_meta["status"] == "NOT_RUN" and "RUN_COMPLETE" in manifest["status"]),
        "manifest run status",
    )

    sensitive_patterns = (
        re.compile(rb"/" + rb"home/[A-Za-z0-9_.-]+/"),
        re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(rb"AKIA[0-9A-Z]{16}"),
        re.compile(rb"(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}"),
    )
    for relative in sorted(actual_core):
        payload = (ROOT / relative).read_bytes()
        audit.check(not any(pattern.search(payload) for pattern in sensitive_patterns), f"privacy scan {relative}")


def write_validation(
    audit: Audit,
    result: Mapping[str, object],
    replayed: Sequence[str],
) -> None:
    validation = {
        "experiment_id": "GDT784",
        "status": "PASS",
        "checks": audit.count,
        "source_locks": 15,
        "source_lock_sha256": sha256(LOCKS),
        "source_spec_sha256": {
            "target_boundary": sha256(TARGET_SPEC),
            "stolfi_comparators": sha256(STOLFI_SPECS),
            "visual_audit": sha256(VISUAL_SPEC),
            "segmentation_models": sha256(MODELS),
            "candidates": sha256(CANDIDATES),
            "final_selection": sha256(FINAL),
            "historical_comparators": sha256(HISTORICAL),
        },
        "runner_sha256": sha256(RUN),
        "result_sha256": sha256(ART / "RESULT.json"),
        "report_sha256": sha256(REPORT),
        "independent_complete_whole_reconstruction": {
            "chorcholsal": {"raw": 1, "reader_exact": 1},
            "chor": {"raw": 190, "reader_exact": 176},
            "chol": {"raw": 343, "reader_exact": 303},
            "sal": {"raw": 37, "reader_exact": 33},
        },
        "independent_boundary_reconstruction": {
            "current_readers_fused": 3,
            "stolfi_target": "chor,chol.sal",
            "target_free_stolfi_dot_loci": 13,
            "target_free_stolfi_dot_boundaries": 14,
        },
        "independent_constituent_order_reconstruction": {
            "chor_to_chol": 8,
            "chol_to_chor": 7,
            "contacts": 15,
            "loci": 14,
            "minimum_length_3_complete_split": ["chor", "chol", "sal"],
        },
        "adjudication": {
            "surface_whole_confidence": "C2",
            "part_dry_echo_confidence": "C1",
            "sal_semantic_confidence": "C0_OPEN",
            "practical_whole_default_de": result["adjudication"]["practical_whole_default_de"],
            "target_span_default_de": result["adjudication"]["target_span_default_de"],
        },
        "renderer": {"rows": 376, "contextual": 270, "fallback": 106, "consumed": 230, "display_changes": 1},
        "edge_packet_intake": "PASS_VALID_ACQUISITION_NOT_SCORE_READY",
        "byte_replay": "PASS",
        "replayed_files": list(replayed),
        "run_py_imported": False,
        "sealed_pages_accessed": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    audit = Audit()
    validate_locks_and_specs(audit)
    cache = reconstruct_cache(audit)
    stolfi = reconstruct_stolfi(audit, cache)
    result, replayed = validate_public_artifacts(audit, cache, stolfi)
    validate_manifest_and_privacy(audit, result)
    write_validation(audit, result, replayed)
    print(f"GDT784_VALIDATION_PASS {audit.count} checks; {len(replayed)} files replayed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
