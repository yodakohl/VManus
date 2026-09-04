#!/usr/bin/env python3
"""Independent validation and two-replay audit for GDT797."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt797_aqabba_surface_host_domain_discriminator"
SRC = BASE / "src"
ART = BASE / "artifacts"
RUN = SRC / "run.py"
LOCK = SRC / "SOURCE_LOCK.tsv"
VALIDATION = ART / "VALIDATION.json"

OUTPUTS = (
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


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.errors: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.errors.append(label)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.checks += 1
        if actual != expected:
            self.errors.append(f"{label}: {actual!r} != {expected!r}")

    def close(self, actual: float, expected: float, label: str, tolerance: float = 1e-6) -> None:
        self.checks += 1
        if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
            self.errors.append(f"{label}: {actual!r} != {expected!r}")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pipe_counts(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) if counts else "NONE"


def mode_credit(actual: str, training: list[str]) -> float:
    counts = Counter(training)
    maximum = max(counts.values())
    modes = [key for key, value in counts.items() if value == maximum]
    return 1.0 / len(modes) if actual in modes else 0.0


def recompute_family(rows: list[dict[str, str]]) -> dict[str, float | int | str]:
    if not rows:
        return {"n": 0, "coverage": 0, "keyed": 0.0, "pooled": 0.0, "gain": 0.0,
                "surface_counts": "NONE", "domain_counts": "NONE"}
    coverage = 0
    keyed = 0.0
    pooled = 0.0
    for index, target in enumerate(rows):
        training = [row for other, row in enumerate(rows) if other != index]
        same = [row["independent_domain"] for row in training if row["surface"] == target["surface"]]
        if not same:
            continue
        coverage += 1
        keyed += mode_credit(target["independent_domain"], same)
        pooled += mode_credit(target["independent_domain"], [row["independent_domain"] for row in training])
    return {
        "n": len(rows), "coverage": coverage, "keyed": keyed, "pooled": pooled,
        "gain": (keyed - pooled) / coverage if coverage else 0.0,
        "surface_counts": pipe_counts(row["surface"] for row in rows),
        "domain_counts": pipe_counts(row["independent_domain"] for row in rows),
    }


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    row1, row2, col1 = a + b, c + d, a + c
    total = row1 + row2

    def probability(x: int) -> float:
        return math.comb(col1, x) * math.comb(total - col1, row1 - x) / math.comb(total, row1)

    low, high = max(0, row1 - (total - col1)), min(row1, col1)
    observed = probability(a)
    return min(1.0, sum(probability(x) for x in range(low, high + 1) if probability(x) <= observed + 1e-15))


def validate_lock(audit: Audit) -> None:
    rows = read_tsv(LOCK)
    audit.equal(len(rows), 18, "source lock row count")
    audit.equal(len({row["path"] for row in rows}), len(rows), "source lock unique paths")
    locked = {row["path"] for row in rows}
    audit.check(RUN.relative_to(ROOT).as_posix() in locked, "run.py must be source-locked")
    audit.check(Path(__file__).resolve().relative_to(ROOT).as_posix() in locked, "validate.py must be source-locked")
    for row in rows:
        path = Path(row["path"])
        audit.check(not path.is_absolute() and ".." not in path.parts, f"safe lock path {row['path']}")
        full = ROOT / path
        audit.check(full.is_file(), f"locked source exists {row['path']}")
        if full.is_file():
            audit.equal(sha256(full), row["sha256"], f"locked source hash {row['path']}")


def validate_targets(audit: Audit) -> None:
    rows = read_tsv(ART / OUTPUTS[0])
    audit.equal(len(rows), 7, "target contact count")
    audit.equal(sum(row["primary_analysis"] == "YES" for row in rows), 6, "primary target count")
    audit.equal(sum(row["contact_class"] == "EXTERNAL_EXACT_WHOLE" for row in rows), 4, "external target count")
    audit.equal(sum(row["contact_class"] == "SOURCE_FAMILY_LABEL" for row in rows), 2, "source label count")
    audit.equal(sum(row["contact_class"] == "READER_BOUNDARY_SENSITIVITY" for row in rows), 1, "boundary sensitivity count")
    expected = {
        "f18r.8": ("okaldy", "PLANT_DRUG_MATERIAL", "1", "ONE_ALTERNATE_ONLY_EXACT_WHOLE"),
        "f70v2.17": ("otaldy", "CELESTIAL_ARRAY", "2", "ZL3B_ONLY_EXACT_WHOLE"),
        "f72r2.27": ("okaldy", "CELESTIAL_ARRAY", "3", "ALL_THREE_EXACT_WHOLE"),
        "f75r.27": ("okaldy", "FIGURE_STATION_SYSTEM", "3", "TWO_OF_THREE_EXACT_WHOLE"),
        "f82r.37": ("okaldy", "FIGURE_STATION_SYSTEM", "3", "ZL3B_ONLY_EXACT_WHOLE"),
        "f88r.12": ("otaldy", "PLANT_DRUG_MATERIAL", "3", "ALL_THREE_EXACT_WHOLE"),
        "f95v1.4": ("otaldy", "PLANT_DRUG_MATERIAL", "3", "ALL_THREE_EXACT_WHOLE"),
    }
    audit.equal({row["locus"] for row in rows}, set(expected), "target loci")
    for row in rows:
        exp = expected[row["locus"]]
        audit.equal((row["target_surface"], row["independent_domain"], row["source_family_single_group_support"], row["alternate_reader_status"]), exp, f"target tuple {row['locus']}")
        audit.equal(row["component_export_credit"], "ZERO", f"target no export {row['locus']}")
        audit.equal(row["confirmed_lexeme"], "NO", f"target no lexeme {row['locus']}")
    by_surface = defaultdict(list)
    for row in rows:
        if row["contact_class"] == "EXTERNAL_EXACT_WHOLE":
            by_surface[row["target_surface"]].append(row["independent_domain"])
    audit.equal(Counter(by_surface["okaldy"]), Counter({"FIGURE_STATION_SYSTEM": 2}), "okaldy external split")
    audit.equal(Counter(by_surface["otaldy"]), Counter({"PLANT_DRUG_MATERIAL": 2}), "otaldy external split")


def validate_profiles_and_paragraphs(audit: Audit) -> None:
    profiles = read_tsv(ART / OUTPUTS[1])
    audit.equal(len(profiles), 2, "surface profile count")
    by_surface = {row["target_surface"]: row for row in profiles}
    audit.equal(by_surface["okaldy"]["external_domain_counts"], "FIGURE_STATION_SYSTEM:2", "okaldy profile")
    audit.equal(by_surface["otaldy"]["external_domain_counts"], "PLANT_DRUG_MATERIAL:2", "otaldy profile")
    audit.equal(by_surface["okaldy"]["bold_contextual_working_default_de"], "Bade-/Behandlungseintrag", "okaldy working display")
    audit.equal(by_surface["otaldy"]["bold_contextual_working_default_de"], "Wurzel-/Drogenartikel", "otaldy working display")
    for row in profiles:
        audit.equal(row["renderer_license"], "ENUMERATED_CONTEXTUAL_COMPLETE_WHOLE_ONLY", f"profile scope {row['target_surface']}")
        audit.equal(row["component_export_credit"], "ZERO", f"profile no export {row['target_surface']}")

    paragraphs = read_tsv(ART / OUTPUTS[2])
    audit.equal(len(paragraphs), 6, "paragraph candidate rows")
    audit.equal(Counter(row["model_id"] for row in paragraphs), Counter({"FAMILY_POOLED_STATUS": 2, "SURFACE_SPECIFIC_LEARNED_ENTRIES": 2, "OPAQUE_RECURRENCE": 2}), "paragraph model balance")
    audit.equal({row["paragraph_id"] for row in paragraphs}, {"f75r:P2", "f95v1:P1"}, "target paragraphs")
    for row in paragraphs:
        audit.check("MASKED" in row["target_masked_whole_paragraph"], f"target masking {row['candidate_reader_id']}")
        audit.equal(row["translation_status"], "CANDIDATE_TARGET_INSERTION_ONLY__SURROUNDING_PARAGRAPH_UNTRANSLATED", f"paragraph ceiling {row['candidate_reader_id']}")
        audit.equal(row["component_export_credit"], "ZERO", f"paragraph no export {row['candidate_reader_id']}")


def validate_controls(audit: Audit) -> None:
    contacts = read_tsv(ART / OUTPUTS[3])
    tournament = read_tsv(ART / OUTPUTS[4])
    audit.equal(len(contacts), 48, "recurrent external contacts")
    audit.equal(len(tournament), 11, "family tournament rows")
    audit.equal(len({row["external_contact_ordinal"] for row in contacts}), 48, "contact ordinals unique")
    audit.check(all(not row["representative_locus"].startswith("f84") for row in contacts), "no sealed contact locus")
    by_family = defaultdict(list)
    for row in contacts:
        by_family[row["canonical_boundary_family"]].append(row)
        audit.equal(row["component_export_credit"], "ZERO", f"control no export {row['external_contact_ordinal']}")
    table = {row["canonical_boundary_family"]: row for row in tournament}
    for family, row in table.items():
        metrics = recompute_family(by_family[family])
        audit.equal(int(row["external_host_unit_count"]), metrics["n"], f"family contact count {family}")
        audit.equal(int(row["leave_one_host_out_coverage"]), metrics["coverage"], f"family coverage {family}")
        audit.equal(row["external_surface_counts"], metrics["surface_counts"], f"family surface counts {family}")
        audit.equal(row["external_domain_counts"], metrics["domain_counts"], f"family domain counts {family}")
        audit.close(float(row["surface_keyed_credit"]), float(metrics["keyed"]), f"family keyed credit {family}")
        audit.close(float(row["family_pooled_credit"]), float(metrics["pooled"]), f"family pooled credit {family}")
        audit.close(float(row["surface_minus_pooled_gain"]), float(metrics["gain"]), f"family gain {family}")
        audit.equal(row["semantic_export"], "NONE", f"family semantic ceiling {family}")
    qualified = [row for row in tournament if row["capacity_qualified"] == "YES"]
    audit.equal({row["canonical_boundary_family"] for row in qualified}, {"AQAB", "AQABA", "AQABBA"}, "qualified family set")
    audit.equal(table["AQABBA"]["qualified_gain_rank"], "1", "AQABBA gain rank")
    audit.close(float(table["AQABBA"]["surface_minus_pooled_gain"]), 1.0, "AQABBA gain")
    audit.close(float(table["AQAB"]["surface_minus_pooled_gain"]), -0.086207, "AQAB gain")
    audit.close(float(table["AQABA"]["surface_minus_pooled_gain"]), -0.25, "AQABA gain")


def validate_surface_and_branch_calibration(audit: Audit) -> None:
    surfaces = read_tsv(ART / OUTPUTS[5])
    audit.equal(len(surfaces), 71, "all source surface count")
    audit.equal(sum(int(row["external_host_unit_count"]) > 0 for row in surfaces), 21, "surfaces with external contacts")
    audit.equal(sum(row["same_domain_local_running_bridges"] != "NONE" for row in surfaces), 9, "surfaces with bridges")
    audit.equal({row["surface"] for row in surfaces if row["noncelestial_minimal_bridge"] == "YES"}, {"okaldy", "otaldy"}, "minimal noncelestial bridge surfaces")
    for row in surfaces:
        audit.equal(row["semantic_export"], "NONE", f"surface semantic ceiling {row['surface']}")

    branch = read_tsv(ART / OUTPUTS[6])
    audit.equal(len(branch), 2, "branch sensitivity rows")
    expected = {
        "TARGET_EXCLUDED_CONTROLS": (20, 7, 4, 4, 5, 2.1875, 0.653417),
        "TARGET_INCLUDED_SENSITIVITY": (24, 9, 4, 4, 7, 3.9375, 0.217326),
    }
    for row in branch:
        n, a, b, c, d, odds, p = expected[row["scenario"]]
        audit.equal(int(row["surface_host_contact_count"]), n, f"branch surface-host contact count {row['scenario']}")
        audit.equal((int(row["ok_figure_station"]), int(row["ok_plant_drug"]), int(row["ot_figure_station"]), int(row["ot_plant_drug"])), (a, b, c, d), f"branch table {row['scenario']}")
        audit.close(float(row["odds_ratio_ok_figure_vs_ot_figure"]), odds, f"branch odds {row['scenario']}")
        audit.close(float(row["fisher_two_sided_p"]), fisher_two_sided(a, b, c, d), f"branch Fisher {row['scenario']}")
        audit.close(float(row["fisher_two_sided_p"]), p, f"branch expected p {row['scenario']}")
        audit.equal(row["decision"], "WEAK_FORMAL_SENSITIVITY_ONLY__NO_COMPONENT_EXPORT", f"branch ceiling {row['scenario']}")


def validate_decisions_renderer_scope(audit: Audit) -> None:
    decisions = read_tsv(ART / OUTPUTS[7])
    audit.equal(len(decisions), 7, "decision row count")
    by_id = {row["candidate_id"]: row for row in decisions}
    audit.equal(by_id["HYBRID_SOURCE_STATUS_PLUS_LEARNED_ENTRIES"]["decision"], "SELECT_PRIMARY_C0", "hybrid selected")
    audit.equal(by_id["OPAQUE_RECURRENCE"]["decision"], "RETAIN_LIVE_NULL", "opaque null retained")
    audit.equal(by_id["GDT666_OTALDY_COMPOSITIONAL_ACTION"]["decision"], "QUARANTINE_ON_RELEASED_30_PAGE_SPINE", "legacy action quarantined")
    audit.equal(by_id["OKALDY_BATH_TREATMENT_ENTRY"]["working_interpretation"], "okaldy = Bade-/Behandlungseintrag", "okaldy decision")
    audit.equal(by_id["OTALDY_ROOT_DRUG_ARTICLE"]["working_interpretation"], "otaldy = Wurzel-/Drogenartikel", "otaldy decision")
    for row in decisions:
        audit.equal(row["component_export_credit"], "ZERO", f"decision no export {row['candidate_id']}")
        audit.equal(row["confirmed_lexeme"], "NO", f"decision no lexeme {row['candidate_id']}")

    renderer = read_tsv(ART / OUTPUTS[8])
    audit.equal(len(renderer), 6, "renderer row count")
    audit.equal(sum(row["previous_otaldy_action_present"] == "YES" for row in renderer), 2, "active legacy action cells")
    audit.equal(sum(row["confidence"] == "C0_PREDICTED_HYBRID_SOURCE_LABEL" for row in renderer), 2, "predicted source-label rows")
    audit.equal(sum(row["confidence"] == "C0_CONTEXTUAL_WHOLE" for row in renderer), 4, "direct contextual rows")
    for row in renderer:
        audit.equal(row["component_export_credit"], "ZERO", f"renderer no export {row['locus']}")
        audit.equal(row["confirmed_lexeme"], "NO", f"renderer no lexeme {row['locus']}")
        if row["previous_otaldy_action_present"] == "YES":
            audit.equal(row["previous_card_disposition"], "QUARANTINED_GDT666_COMPOSITIONAL_ACTION_CELL", f"active-cell quarantine {row['locus']}")

    scope = read_tsv(ART / OUTPUTS[9])
    audit.equal(len(scope), 3, "scope audit rows")
    cross = next(row for row in scope if row["audit_id"] == "GDT797_EXACT_LOCUS_CROSS_QUERY")
    sta = next(row for row in scope if row["audit_id"] == "GDT797_EXACT_LOCUS_SOURCE_STA_QUERY")
    scratch = next(row for row in scope if row["audit_id"] == "PRE_GDT797_CANVAS_ID_SCRATCH_SEARCH")
    audit.equal((cross["selected_rows"], cross["sealed_rows_rejected_before_materialization"], cross["other_rows_skipped"]), ("7", "98", "5281"), "cross guard stats")
    audit.equal((sta["selected_rows"], sta["sealed_rows_rejected_before_materialization"], sta["other_rows_skipped"]), ("93", "2122", "113255"), "STA guard stats")
    audit.equal(cross["count_status"], "MEASURED_GUARDED_QUERY", "cross count status")
    audit.equal(sta["count_status"], "MEASURED_GUARDED_QUERY", "STA count status")
    audit.equal(scratch["count_status"], "NOT_APPLICABLE_TO_UNGUARDED_SCRATCH_INCIDENT", "scratch count status")
    audit.equal(scratch["disposition"], "TRANSIENT_DISPLAY_EXCLUDED_FROM_ALL_INPUTS_ARTIFACTS_AND_SCORES", "scratch disposition")
    audit.check(all(row["retained_sealed_values"] == "0" for row in scope), "no retained sealed values")


def validate_result(audit: Audit) -> None:
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.equal(result["experiment_id"], "GDT797", "result experiment id")
    audit.equal(result["scope"]["primary_exact_events"], 6, "result primary count")
    audit.equal(result["scope"]["external_exact_host_units"], 4, "result external count")
    audit.equal(result["scope"]["sealed_rows_materialized_in_executable_build"], 0, "result executable seal")
    audit.check("pre_experiment_scratch_incident" in result["scope"], "result scratch incident present")
    audit.close(result["target_split"]["surface_keyed_leave_one_host_out_credit"], 4.0, "result keyed credit")
    audit.close(result["target_split"]["family_pooled_leave_one_host_out_credit"], 0.0, "result pooled credit")
    audit.close(result["target_split"]["inclusive_exact_micro_p"], 1 / 3, "result exact micro p")
    audit.equal(result["surface_calibration"]["noncelestial_minimal_local_running_bridges"], ["okaldy", "otaldy"], "result minimal bridges")
    audit.equal(result["selected_working_theory"]["okaldy"], "Bade-/Behandlungseintrag", "result okaldy")
    audit.equal(result["selected_working_theory"]["otaldy"], "Wurzel-/Drogenartikel", "result otaldy")
    audit.equal(result["renderer"]["legacy_otaldy_action_cells_quarantined"], 2, "result action quarantine")
    audit.equal(result["renderer"]["component_exports"], 0, "result component exports")
    audit.equal(result["renderer"]["confirmed_lexemes"], 0, "result lexemes")
    audit.equal(result["renderer"]["confirmed_plaintext_clauses"], 0, "result clauses")
    audit.equal(tuple(result["outputs"]), OUTPUTS, "result output list")


def validate_replays(audit: Audit) -> None:
    canonical = {name: (ART / name).read_bytes() for name in OUTPUTS}
    for replay_index in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f"gdt797_replay_{replay_index}_") as temporary:
            completed = subprocess.run(
                [sys.executable, str(RUN), "--output-dir", temporary],
                cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            audit.equal(completed.returncode, 0, f"builder replay {replay_index} exit")
            if completed.returncode:
                audit.errors.append(f"builder replay {replay_index} stderr: {completed.stderr[-2000:]}")
                continue
            replay = Path(temporary)
            for name in OUTPUTS:
                path = replay / name
                audit.check(path.is_file(), f"builder replay {replay_index} output {name}")
                if path.is_file():
                    audit.equal(path.read_bytes(), canonical[name], f"builder replay {replay_index} bytes {name}")


def validate_privacy(audit: Audit) -> None:
    scanned = [RUN, Path(__file__).resolve(), BASE / "REPORT.md", BASE / "METHOD.md", BASE / "PREREGISTRATION.md"]
    scanned.extend(ART / name for name in OUTPUTS)
    for path in scanned:
        text = path.read_text(encoding="utf-8")
        absolute_home_marker = "/" + "home/"
        file_uri_marker = "file:" + "//"
        audit.check(absolute_home_marker not in text, f"no absolute home path {path.relative_to(ROOT)}")
        audit.check(file_uri_marker not in text, f"no file URI {path.relative_to(ROOT)}")
    contacts = read_tsv(ART / OUTPUTS[0])
    controls = read_tsv(ART / OUTPUTS[3])
    audit.check(all(not row["locus"].startswith("f84") for row in contacts), "target atlas excludes sealed loci")
    audit.check(all(not row["representative_locus"].startswith("f84") for row in controls), "control atlas excludes sealed loci")


def main() -> int:
    audit = Audit()
    validate_lock(audit)
    validate_targets(audit)
    validate_profiles_and_paragraphs(audit)
    validate_controls(audit)
    validate_surface_and_branch_calibration(audit)
    validate_decisions_renderer_scope(audit)
    validate_result(audit)
    validate_replays(audit)
    validate_privacy(audit)
    status = "PASS" if not audit.errors else "FAIL"
    payload = {
        "experiment_id": "GDT797",
        "status": status,
        "checks": audit.checks,
        "errors": audit.errors,
        "builder_replays": 2,
        "byte_identical_outputs_per_replay": len(OUTPUTS) if status == "PASS" else 0,
        "independent_findings": {
            "primary_exact_events": 6,
            "external_surface_domain_split": "4_OF_4",
            "surface_keyed_credit": "4_OF_4",
            "family_pooled_credit": "0_OF_4",
            "exact_micro_p": "0.333333",
            "single_token_source_surfaces": 71,
            "minimal_noncelestial_bridges": ["okaldy", "otaldy"],
            "legacy_action_cells_quarantined": 2,
            "component_exports": 0,
            "confirmed_lexemes": 0,
        },
    }
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"experiment_id": "GDT797", "status": status, "checks": audit.checks, "errors": len(audit.errors)}))
    if audit.errors:
        for error in audit.errors:
            print("FAIL", error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
