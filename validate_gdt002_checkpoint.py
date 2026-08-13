#!/usr/bin/env python3
"""Independent integrity validator for the first GDT002 checkpoint."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
R = ROOT / "experiments/semantic_assumptions/results"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_payload(data: list[dict[str, object]], fields: list[str]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, delimiter="\t", fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in data:
        writer.writerow({key: row.get(key, "") for key in fields})
    return out.getvalue().encode("utf-8")


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


checks: dict[str, bool] = {}
result = json.loads((ROOT / "gdt002_checkpoint_result.json").read_text())
inventory = rows(ROOT / "gdt002_visual_inventory.tsv")
alternate = rows(ROOT / "gdt002_grammar_projection.tsv")
consensus = rows(ROOT / "gdt002_grammar_consensus_projection.tsv")
atlas = rows(ROOT / "gdt002_repeated_structure_atlas.tsv")
holdout = json.loads((ROOT / "gdt002_f84r_holdout_projection_commitment.json").read_text())
hypotheses = json.loads((ROOT / "gdt002_joint_hypotheses.json").read_text())
discovery = json.loads((ROOT / "gdt002_discovery_results.json").read_text())

checks["branch_is_gdt002"] = subprocess.check_output(
    ["git", "branch", "--show-current"], cwd=ROOT, text=True
).strip() == "yolo/gdt002-visual-grammar-constraints"
checks["canonical_files_unmodified"] = subprocess.run(
    ["git", "diff", "--quiet", "c7874a9", "--", "VOYNICH_ACTIVE_STATE.md",
     "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv",
     "experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv"], cwd=ROOT
).returncode == 0
checks["inventory_only_human_provenance"] = bool(inventory) and {r["provenance"] for r in inventory} == {"EXISTING_HUMAN_ANNOTATION"}
checks["inventory_zero_ai_direct"] = all(r["provenance"] != "AI_DIRECT_VISUAL_OBSERVATION" for r in inventory)
checks["visual_no_formal_strings"] = all(not r["local_text_loci"] or not any(k in r for k in ("family_surface", "sta_codes", "source_text")) for r in inventory)
checks["ownership_vocab"] = {r["ownership_evidence"] for r in inventory} <= {
    "DIRECT_LEADER", "SAME_ENCLOSURE", "CONNECTED_COMPONENT", "PROXIMITY_ONLY", "UNKNOWN"
}
checks["only_f82r10_connected_component"] = [r["local_text_loci"] for r in inventory if r["ownership_evidence"] == "CONNECTED_COMPONENT"] == ["f82r.10"]
checks["pages_exact"] = {r["folio"] for r in inventory} == {"f80r", "f82r", "f84r"}
unit_ids = {r["visual_unit_id"] for r in inventory}
checks["graph_edges_resolve"] = all(not r["connected_to"] or r["connected_to"] in unit_ids for r in inventory)
checks["graph_nulls_explicit"] = all(r["inside_outside"] and r["endpoint_role"] for r in inventory)

source_sep = {r["source_group_id"]: r for r in rows(R / "source_separator_transcription.tsv") if r["page"] in {"f80r", "f82r"}}
source_align = {r["source_group_id"]: r for r in rows(R / "source_sta_group_alignment.tsv") if r["locus"].split(".")[0] in {"f80r", "f82r"}}
checks["alternate_exact_key_set"] = {r["source_group_id"] for r in alternate} == set(source_sep) == set(source_align)
checks["alternate_three_editions_only"] = {r["edition"] for r in alternate} == {"ZL3b", "IT2a", "RF1b"}
checks["alternate_discovery_only"] = {r["page"] for r in alternate} == {"f80r", "f82r"} and all(r["holdout_role"] == "DISCOVERY" for r in alternate)
checks["alternate_exact_join"] = all(
    r["edition"] == source_sep[r["source_group_id"]]["edition"] == source_align[r["source_group_id"]]["edition"]
    and r["locus"] == source_sep[r["source_group_id"]]["locus"] == source_align[r["source_group_id"]]["locus"]
    and r["ivtff_group_raw"] == source_sep[r["source_group_id"]]["ivtff_group_raw"]
    and r["primary_sta_codes"] == source_align[r["source_group_id"]]["primary_sta_codes"]
    and r["primary_sta_families"] == source_align[r["source_group_id"]]["primary_sta_families"]
    for r in alternate
)
checks["alternate_no_preferred_reading"] = all(r["semantic_role"] == "UNASSIGNED" for r in alternate)

coverage = {r["coverage_state"] for r in consensus}
checks["consensus_coverage_states"] = coverage == {"STRICT_EXACT_FAMILY", "EXACT_FAMILY_WITH_ALTERNATIVE", "NO_EXACT_FAMILY_CONSENSUS"}
checks["consensus_discovery_only"] = {r["page"] for r in consensus} == {"f80r", "f82r"}
checks["consensus_all_loci_visible"] = {r["locus"] for r in consensus} == {r["locus"] for r in source_sep.values()}
checks["consensus_uncertain_rows_have_no_family"] = all(
    r["coverage_state"] == "STRICT_EXACT_FAMILY" or not r["family_surface"] for r in consensus
)
checks["consensus_fitted_tags_excluded"] = all(
    r["descriptive_only_full_corpus_tags_excluded"] == "exact_first_last;exact_edge_core;opening;closing;transition;favored_path"
    for r in consensus
)

checks["atlas_row_per_visual"] = len(atlas) == len(inventory) and {r["visual_unit_id"] for r in atlas} == {r["visual_unit_id"] for r in inventory}
checks["atlas_f84_sealed"] = all(
    r["formal_access_state"] != "DISCOVERY_FORMAL_STRUCTURE_OPEN" and not r["family_expression"]
    for r in atlas if r["folio"] == "f84r"
)
checks["atlas_no_roles"] = all(r["latent_role"] == "UNASSIGNED" and r["interpretation"] == "NONE" for r in atlas)

checks["holdout_state_discloses_prior_exposure"] = "PRIOR_REPOSITORY_TEXT_EXPOSURE_DISCLOSED" in holdout["access_state"]
checks["holdout_rows_positive"] = holdout["alternate_projection"]["rows"] > 0 and holdout["consensus_projection"]["rows"] > 0
checks["holdout_only_commitment_no_payload"] = not any(ROOT.glob("gdt002_f84r_*projection.tsv"))

# Independently form both committed f84r tables from primary source tables.
alt_fields = list(alternate[0])
edition_order = {"ZL3b": 0, "IT2a": 1, "RF1b": 2}
f84_sep = {r["source_group_id"]: r for r in rows(R / "source_separator_transcription.tsv") if r["page"] == "f84r"}
f84_align = {r["source_group_id"]: r for r in rows(R / "source_sta_group_alignment.tsv") if r["locus"].split(".")[0] == "f84r"}
f84_alt = []
for key, sep in f84_sep.items():
    ali = f84_align[key]
    f84_alt.append({
        "evidence_class": "FORMAL_STRUCTURE", "holdout_role": "HOLDOUT", "semantic_role": "UNASSIGNED",
        "source_group_id": key, "edition": sep["edition"], "locus": sep["locus"], "page": sep["page"],
        "grammar_scope": sep["grammar_scope"], "code": sep["code"], "kind": sep["kind"],
        "source_group_index": sep["source_group_index"], "source_group_count": sep["source_group_count"],
        "paragraph_start": sep["paragraph_start"], "paragraph_end": sep["paragraph_end"],
        "left_separator": sep["left_separator"], "right_separator": sep["right_separator"],
        "ivtff_group_raw": sep["ivtff_group_raw"], "sta_group_raw": ali["sta_group_raw"],
        "primary_sta_codes": ali["primary_sta_codes"], "primary_sta_families": ali["primary_sta_families"],
        "primary_sta_symbol_count": ali["primary_sta_symbol_count"], "alternative_site_count": ali["alternative_site_count"],
    })
f84_alt.sort(key=lambda r: (locus_number(r["locus"]), edition_order[r["edition"]], int(r["source_group_index"])))
f84_alt_bytes = tsv_payload(f84_alt, alt_fields)
checks["holdout_alternate_independent_count"] = len(f84_alt) == holdout["alternate_projection"]["rows"] == 1101
checks["holdout_alternate_independent_digest"] = hashlib.sha256(f84_alt_bytes).hexdigest() == holdout["alternate_projection"]["sha256"]

cons_fields = list(consensus[0])
f84_locus_cons = {r["locus"]: r for r in rows(R / "source_sta_family_consensus_loci.tsv") if r["page"] == "f84r"}
f84_meta = {}
for row in f84_sep.values():
    f84_meta[row["locus"]] = row
f84_groups = {}
for row in rows(R / "source_native_structural_interlinear_v1.tsv"):
    if row["page"] == "f84r":
        f84_groups.setdefault(row["locus"], []).append(row)
f84_cons = []
for locus, meta in sorted(f84_meta.items(), key=lambda item: locus_number(item[0])):
    loc = f84_locus_cons.get(locus)
    state = "NO_EXACT_FAMILY_CONSENSUS" if loc is None else (
        "STRICT_EXACT_FAMILY" if loc["strict_zero_alternative"] == "1" else "EXACT_FAMILY_WITH_ALTERNATIVE"
    )
    groups = sorted(f84_groups.get(locus, []), key=lambda r: int(r["group_index"])) or [{}]
    for group in groups:
        f84_cons.append({
            "evidence_class": "FORMAL_STRUCTURE", "holdout_role": "HOLDOUT", "semantic_role": "UNASSIGNED",
            "coverage_state": state, "consensus_group_id": group.get("consensus_group_id", ""),
            "locus": locus, "page": "f84r", "grammar_scope": meta["grammar_scope"], "code": meta["code"],
            "kind": meta["kind"], "group_index": group.get("group_index", ""), "group_count": group.get("group_count", ""),
            "factual_position": group.get("factual_position", ""), "family_surface": group.get("family_surface", ""),
            "zl_sta_codes": group.get("zl_sta_codes", ""), "it_sta_codes": group.get("it_sta_codes", ""),
            "rf_sta_codes": group.get("rf_sta_codes", ""), "left_boundary_profile": group.get("left_boundary_profile", ""),
            "left_boundary_support": group.get("left_boundary_support", ""), "right_boundary_profile": group.get("right_boundary_profile", ""),
            "right_boundary_support": group.get("right_boundary_support", ""),
            "descriptive_only_full_corpus_tags_excluded": "exact_first_last;exact_edge_core;opening;closing;transition;favored_path",
        })
f84_cons_bytes = tsv_payload(f84_cons, cons_fields)
checks["holdout_consensus_independent_counts"] = (
    len(f84_cons) == holdout["consensus_projection"]["rows"] == 294
    and sum(bool(r["consensus_group_id"]) for r in f84_cons) == holdout["consensus_projection"]["strict_group_rows"] == 281
)
checks["holdout_consensus_independent_digest"] = hashlib.sha256(f84_cons_bytes).hexdigest() == holdout["consensus_projection"]["sha256"]

checks["hypotheses_capacity_blocked"] = hypotheses["status"] == "CAPACITY_BLOCKED_NO_IDENTIFIABLE_WORLD_TEMPLATES" and not hypotheses["templates"] and hypotheses["selection_state"] == "NO_BEST_HYPOTHESIS"
checks["hypotheses_roles_allowed"] = all(
    role in hypotheses["role_vocabulary"] for item in hypotheses["templates"] for role in item["assignments"].values()
)
checks["discovery_capacity_stop"] = discovery["status"] == "NO_IDENTIFIABLE_SOLVER_FROM_CURRENT_PANEL" and not discovery["scores"]
checks["result_access_exact"] = result["access"] == {
    "f84r_exact_projection_displayed_or_manually_inspected": False,
    "f84r_exact_projection_generated_transiently_for_commitment": True,
    "f84r_exact_projection_joined_or_used_for_discovery": False,
    "f84r_exact_projection_published": False,
    "f84r_prior_repository_text_exposure_disclosed": True,
    "images_opened": False,
    "joint_solver_run": False,
    "new_ai_direct_visual_observations": False,
    "ocr_or_automated_vision_used": False,
}
checks["result_output_hashes"] = all(sha(ROOT / name) == digest for name, digest in result["outputs"].items())
checks["result_input_hashes"] = all(sha(ROOT / name) == digest for name, digest in result["inputs"].items())
checks["result_document_hashes"] = all(sha(ROOT / name) == digest for name, digest in result["documents_and_implementation"].items())

# Independently reconstruct summary/count and atlas constraints.
locus_states = {}
for row in consensus:
    locus_states[row["locus"]] = row["coverage_state"]
strict_loci = {locus for locus, state in locus_states.items() if state == "STRICT_EXACT_FAMILY"}
strict_prose_loci = {
    row["locus"] for row in consensus
    if row["coverage_state"] == "STRICT_EXACT_FAMILY" and row["grammar_scope"] == "CONFIRMED_PROSE"
}
linked = [r for r in atlas if r["formal_access_state"] == "DISCOVERY_FORMAL_STRUCTURE_OPEN"]
strict_linked = [r for r in linked if r["coverage_state"] == "STRICT_EXACT_FAMILY"]
family_counts = Counter(r["family_expression"] for r in strict_linked if r["family_expression"])
expected_counts = {
    "visual_inventory_rows": len(inventory), "existing_human_rows": len(inventory),
    "new_ai_direct_visual_observation_rows": 0, "discovery_alternate_rows": len(alternate),
    "discovery_consensus_rows": len(consensus), "atlas_rows": len(atlas),
    "text_linked_discovery_rows": len(linked), "strict_text_linked_discovery_rows": len(strict_linked),
    "repeated_strict_family_expressions": sum(v > 1 for v in family_counts.values()),
    "discovery_loci": len(locus_states), "discovery_strict_exact_family_loci": len(strict_loci),
    "discovery_strict_confirmed_prose_loci": len(strict_prose_loci),
    "discovery_strict_confirmed_prose_groups": sum(
        bool(r["consensus_group_id"]) and r["coverage_state"] == "STRICT_EXACT_FAMILY"
        and r["grammar_scope"] == "CONFIRMED_PROSE" for r in consensus
    ),
}
checks["summary_counts_independent"] = result["counts"] == expected_counts
checks["summary_expected_exact_values"] = expected_counts["discovery_alternate_rows"] == 2203 and expected_counts["discovery_loci"] == 98 \
    and expected_counts["discovery_consensus_rows"] == 454 and expected_counts["discovery_strict_exact_family_loci"] == 62 \
    and expected_counts["discovery_strict_confirmed_prose_loci"] == 44 and expected_counts["discovery_strict_confirmed_prose_groups"] == 400 \
    and expected_counts["text_linked_discovery_rows"] == 23 and expected_counts["strict_text_linked_discovery_rows"] == 18
checks["repeats_exact"] = {k for k, value in family_counts.items() if value > 1} == {"AQABA", "AQAC"}
atlas_by_locus = {r["local_text_locus"]: r for r in atlas if r["local_text_locus"]}
checks["constraint_c01_reconstructed"] = (
    atlas_by_locus["f80r.3"]["family_expression"] == atlas_by_locus["f80r.4"]["family_expression"] == "AQABA"
    and "SINGULAR_COMMON_CLASS_OWNED" in atlas_by_locus["f80r.3"]["prior_ai_visual_state"]
    and atlas_by_locus["f80r.4"]["ownership_evidence"] == "PROXIMITY_ONLY"
)
checks["constraint_c02_reconstructed"] = (
    atlas_by_locus["f80r.9"]["family_expression"] == atlas_by_locus["f82r.34"]["family_expression"] == "AQAC"
    and atlas_by_locus["f80r.9"]["ownership_evidence"] == atlas_by_locus["f82r.34"]["ownership_evidence"] == "PROXIMITY_ONLY"
)
checks["constraint_c03_reconstructed"] = (
    atlas_by_locus["f82r.10"]["ownership_evidence"] == "CONNECTED_COMPONENT"
    and atlas_by_locus["f82r.10"]["coverage_state"] == "EXACT_FAMILY_WITH_ALTERNATIVE"
)
f80_array = [r for r in atlas if r["repetition_group"] == "F80_TOP_TEXT_POSITIONS" and r["family_expression"]]
f82_array = [r for r in atlas if r["repetition_group"] in {"F82_BOTTOM_REGION_TOP_ROW", "F82_BOTTOM_REGION_BOTTOM_ROW"} and r["family_expression"]]
checks["constraint_c04_reconstructed"] = len(f80_array) == 8 and len({r["family_expression"] for r in f80_array}) == 7 and len(f82_array) == 8 and len({r["family_expression"] for r in f82_array}) == 8

# Rebuild into a separate tree, never touching published files, and compare all
# deterministic outputs byte-for-byte.
with tempfile.TemporaryDirectory(prefix="gdt002-validate-") as temp:
    target = Path(temp)
    (target / "experiments").symlink_to(ROOT / "experiments", target_is_directory=True)
    (target / "transcription").symlink_to(ROOT / "transcription", target_is_directory=True)
    for name in (
        "build_gdt002_checkpoint.py", "validate_gdt002_checkpoint.py", "YOLO_MODE.md",
        "GDT002_METHOD.md", "GDT002_EXISTING_VISUAL_EVIDENCE_AUDIT.md",
        "GDT002_DISCOVERY_REPORT.md", "GDT002_YOLO_LEDGER.tsv",
    ):
        shutil.copy2(ROOT / name, target / name)
    subprocess.run([sys.executable, "build_gdt002_checkpoint.py"], cwd=target, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    generated = [
        "gdt002_visual_inventory.tsv", "gdt002_grammar_projection.tsv",
        "gdt002_grammar_consensus_projection.tsv", "gdt002_repeated_structure_atlas.tsv",
        "gdt002_f84r_holdout_projection_commitment.json", "gdt002_discovery_atlas.json",
        "gdt002_joint_hypotheses.json", "gdt002_discovery_results.json",
        "gdt002_checkpoint_result.json",
    ]
    checks["deterministic_rebuild_byte_exact"] = all((target / name).read_bytes() == (ROOT / name).read_bytes() for name in generated)

ledger_rows = rows(ROOT / "GDT002_YOLO_LEDGER.tsv")
checks["ledger_first_checkpoint_immutable_and_append_only"] = (
    bool(ledger_rows)
    and ledger_rows[0] == {
        "checkpoint_id": "GDT002_CKPT001",
        "phase": "SOURCE_ONLY_INVENTORY_AND_PROJECTION",
        "status": "PASS_INVENTORY_NO_IDENTIFIABLE_SOLVER_CURRENT_PANEL",
        "discovery_pages": "f80r;f82r",
        "holdout_page": "f84r",
        "images_opened": "0",
        "new_ai_visual_rows": "0",
        "joint_solver_run": "0",
        "result_artifact": "gdt002_checkpoint_result.json",
        "notes": "EXPLORATORY; human descriptions reused; f84r projection transiently generated for commitment, not persisted, inspected, or used; no role or translation",
    }
)

failed = [name for name, passed in checks.items() if not passed]
validation = {
    "experiment": "GDT002_VISUAL_GRAMMAR_CONSTRAINTS",
    "phase": "FIRST_CHECKPOINT_VALIDATION",
    "status": "PASS" if not failed else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()),
    "total": len(checks),
    "failed": failed,
    "scope": "Record-integrity and source-table reconstruction only; no independent image or semantic judgment.",
    "result_sha256": sha(ROOT / "gdt002_checkpoint_result.json"),
}
(ROOT / "gdt002_checkpoint_validation.json").write_text(
    json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps({"status": validation["status"], "passed": validation["passed"], "total": validation["total"], "failed": failed}))
sys.exit(1 if failed else 0)
