#!/usr/bin/env python3
"""Invariant, edge-gate and byte-replay validation for GDT752."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt752_q_base_microfield_role_audit")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__44_Q_CONTACTS_12_PAIRS__42_NONQ_CONTROLS_26_PAIRS__"
    "27_Q_28_CONTROL_COMPLETE_FIELDS__ZERO_Q_EXACT_ROLE_SPLITS__"
    "ONE_CONTROL_REVERSE__ONE_Q_SYMMETRIC_AMBIGUOUS_FIELD__"
    "TEN_OKEEY_PREPARATION_CARDS_HYPOTHESIS_ONLY__HOT_END_RETAINED__"
    "ZERO_Q_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "Q_44_OUTER_MICROFIELD_AUDIT.tsv",
    "CONTROL_42_OUTER_MICROFIELD_AUDIT.tsv",
    "SIDE_ROLE_GROUP_COMPARISON.tsv",
    "Q_PAIR_TYPE_ROLE_CENSUS.tsv",
    "OKEEY_13_LOCAL_CARRIER_REVIEW.tsv",
    "GDT752_Q_BASE_MICROFIELD_READER.md",
    "GDT752_GDT388_SIDE_ROLE_EDGE_PACKET.tsv",
    "GDT752_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
EXPECTED_Q_TYPES = {
    "qokaiin": ("okaiin", 3),
    "qokain": ("okain", 5),
    "qokaly": ("okaly", 1),
    "qokar": ("okar", 5),
    "qokchey": ("okchey", 1),
    "qokedy": ("okedy", 4),
    "qokeedy": ("okeedy", 4),
    "qokeey": ("okeey", 13),
    "qokeol": ("okeol", 2),
    "qokey": ("okey", 2),
    "qotedy": ("otedy", 2),
    "qoteey": ("oteey", 2),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT752", "manifest id")
    check(manifest["slug"] == "q_base_microfield_role_audit", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(manifest["dependencies"] == [
        "GDT388", "GDT734", "GDT735", "GDT739", "GDT740", "GDT744",
        "GDT750", "GDT751",
    ], "manifest dependencies")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest ceiling")
    check(manifest["validation"] == {
        "artifact": str(VALIDATION_REL), "status": "PASS"
    }, "validation contract")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    q_rows = read_tsv(art / GENERATED[0])
    controls = read_tsv(art / GENERATED[1])
    groups = read_tsv(art / GENERATED[2])
    pair_types = read_tsv(art / GENERATED[3])
    okeey = read_tsv(art / GENERATED[4])
    check(len(q_rows) == 44, "44 q contacts")
    check(len(controls) == 42, "42 control contacts")
    check(len(groups) == 2, "two group rows")
    check(len(pair_types) == 12, "twelve q pair types")
    check(len(okeey) == 13, "thirteen okeey contacts")
    check(len({row["gdt752_contact_id"] for row in q_rows + controls}) == 86, "unique contact ids")
    check(len({row["page"] for row in q_rows}) == 27, "q 27 pages")
    check(len({row["page"] for row in controls}) == 36, "control 36 pages")
    check(Counter(row["written_order"] for row in q_rows) == Counter({
        "PREFIX_THEN_BASE": 24, "BASE_THEN_PREFIX": 20
    }), "q order 24 20")
    check(Counter(row["written_order"] for row in controls) == Counter({
        "PREFIX_THEN_BASE": 31, "BASE_THEN_PREFIX": 11
    }), "control order 31 11")

    for row in q_rows + controls:
        contact_id = row["gdt752_contact_id"]
        check(not row["page"].startswith("f84"), f"sealed page {contact_id}")
        words = row["written_line_eva"].split()
        prefix_ordinal = int(row["prefix_ordinal"])
        base_ordinal = int(row["base_ordinal"])
        check(abs(prefix_ordinal - base_ordinal) == 1, f"adjacent {contact_id}")
        check(words[prefix_ordinal - 1] == row["prefix_surface"], f"prefix coordinate {contact_id}")
        check(words[base_ordinal - 1] == row["base_surface"], f"base coordinate {contact_id}")
        check(row["prefix_surface"][1:] == row["base_surface"], f"complete pair identity {contact_id}")
        check(row["prefix_character"] == row["prefix_surface"][0], f"prefix label {contact_id}")
        if row["comparison_group"] == "Q_PREFIX":
            check(row["prefix_character"] == "q", f"q group {contact_id}")
        else:
            check(row["prefix_character"] != "q", f"nonq group {contact_id}")
        for side in ("prefix", "base"):
            reason = row[f"{side}_outer_boundary_reason"]
            complete = int(row[f"{side}_outer_boundary_complete"])
            check(complete == int(not reason.startswith("RADIUS5")), f"boundary completeness {contact_id} {side}")
            count = int(row[f"{side}_outer_anchor_count"])
            check((row[f"{side}_outer_anchor_tags"] == "NONE") == (count == 0), f"anchor tags {contact_id} {side}")
        complete = int(row["both_outer_boundaries_complete"])
        check(complete == int(
            row["prefix_outer_boundary_complete"] == "1"
            and row["base_outer_boundary_complete"] == "1"
        ), f"both boundaries {contact_id}")
        for field in (
            "exact_role_split_support", "exact_role_split_reverse",
            "broad_role_split_support", "broad_role_split_reverse",
        ):
            check(not int(row[field]) or complete, f"active only complete {contact_id} {field}")
        check(row["literal_identity"] == "OPEN", f"literal open {contact_id}")
        check(row["confirmed_lexeme"] == "0", f"zero lexeme {contact_id}")
        check(row["component_export_credit"] == "0", f"zero component {contact_id}")

    check(sum(int(row["both_outer_boundaries_complete"]) for row in q_rows) == 27, "27 complete q")
    check(sum(int(row["both_outer_boundaries_complete"]) for row in controls) == 28, "28 complete controls")
    check(Counter(row["independent_side_evidence_status"] for row in q_rows) == Counter({
        "NO_INDEPENDENT_SIDE_SIGNAL": 19,
        "MIXED_PARTIAL": 10,
        "PARTIAL_HYPOTHESIS_SIDE": 6,
        "PARTIAL_REVERSE_SIDE": 6,
        "AMBIGUOUS_BOTH_EXACT_SPLITS": 2,
        "SUPPORT_PREFIX_QUALITY_BASE_PREPARATION": 1,
    }), "q raw status census")
    check(Counter(row["independent_side_evidence_status"] for row in controls) == Counter({
        "NO_INDEPENDENT_SIDE_SIGNAL": 20,
        "PARTIAL_REVERSE_SIDE": 11,
        "MIXED_PARTIAL": 6,
        "REVERSE_PREFIX_PREPARATION_BASE_QUALITY": 2,
        "AMBIGUOUS_BOTH_EXACT_SPLITS": 2,
        "PARTIAL_HYPOTHESIS_SIDE": 1,
    }), "control raw status census")
    check(sum(int(row["raw_exact_role_split_support"]) for row in q_rows) == 1, "one raw q support")
    check(sum(int(row["exact_role_split_support"]) for row in q_rows) == 0, "zero active q support")
    check(sum(int(row["exact_role_split_reverse"]) for row in q_rows) == 0, "zero active q reverse")
    check(sum(int(row["exact_role_split_support"]) for row in controls) == 0, "zero control support")
    check(sum(int(row["exact_role_split_reverse"]) for row in controls) == 1, "one control reverse")

    raw_q = [row for row in q_rows if row["raw_exact_role_split_support"] == "1"]
    check(len(raw_q) == 1 and raw_q[0]["gdt752_contact_id"] == "G752-Q037", "qokeol raw lead id")
    check(raw_q[0]["prefix_surface"] == "qokeol" and raw_q[0]["base_surface"] == "okeol", "qokeol raw lead forms")
    check(raw_q[0]["locus"] == "f99v.22" and raw_q[0]["both_outer_boundaries_complete"] == "0", "qokeol lead censored")
    complete_ambiguous_q = [
        row for row in q_rows
        if row["both_outer_boundaries_complete"] == "1"
        and row["independent_side_evidence_status"] == "AMBIGUOUS_BOTH_EXACT_SPLITS"
    ]
    check(len(complete_ambiguous_q) == 1, "one complete ambiguous q")
    ambiguous = complete_ambiguous_q[0]
    check(ambiguous["gdt752_contact_id"] == "G752-Q027" and ambiguous["locus"] == "f99r.50", "ambiguous qokeey locus")
    check(ambiguous["prefix_outer_anchor_tags"] == "HOT|PREPARATION|LEVEL_II", "ambiguous prefix axes")
    check(ambiguous["base_outer_anchor_tags"] == "HOT|PREPARATION|LEVEL_II", "ambiguous base axes")

    group_map = {row["comparison_group"]: row for row in groups}
    check(set(group_map) == {"Q_PREFIX", "NONQ_PREFIX_CONTROL"}, "group ids")
    q_group = group_map["Q_PREFIX"]
    c_group = group_map["NONQ_PREFIX_CONTROL"]
    check(tuple(q_group[field] for field in (
        "contacts", "pair_types", "pages", "both_outer_boundaries_complete",
        "raw_exact_role_split_support", "raw_exact_role_split_reverse",
        "exact_role_split_support", "exact_role_split_reverse",
        "broad_role_split_support", "broad_role_split_reverse",
    )) == ("44", "12", "27", "27", "1", "0", "0", "0", "1", "1"), "q group exact")
    check(tuple(c_group[field] for field in (
        "contacts", "pair_types", "pages", "both_outer_boundaries_complete",
        "raw_exact_role_split_support", "raw_exact_role_split_reverse",
        "exact_role_split_support", "exact_role_split_reverse",
        "broad_role_split_support", "broad_role_split_reverse",
    )) == ("42", "26", "36", "28", "0", "2", "0", "1", "2", "3"), "control group exact")

    pair_map = {row["q_surface"]: row for row in pair_types}
    check(set(pair_map) == set(EXPECTED_Q_TYPES), "pair type surfaces")
    for surface, (base, count) in EXPECTED_Q_TYPES.items():
        row = pair_map[surface]
        check(row["base_surface"] == base, f"pair base {surface}")
        check(int(row["contacts"]) == count, f"pair contacts {surface}")
        check(row["independent_side_result"] == "NO_EXACT_SPLIT", f"pair no exact split {surface}")
        check(row["literal_identity"] == "OPEN" and row["confirmed_lexeme"] == "0", f"pair literal {surface}")
        check(row["component_export_credit"] == "0", f"pair component {surface}")

    check(Counter(row["review_decision"] for row in okeey) == Counter({
        "HOLD_MODEL_INTERNAL_NO_OUTER_SUPPORT": 10,
        "NO_GDT751_CARD": 3,
    }), "okeey review decisions")
    check(sum(int(row["independent_exact_role_split_support"]) for row in okeey) == 0, "zero okeey exact support")
    for row in okeey:
        review_id = row["gdt752_okeey_review_id"]
        check(row["scope"] == "THIS_OCCURRENCE_ONLY", f"okeey scope {review_id}")
        check(row["literal_identity"] == "OPEN", f"okeey literal {review_id}")
        check(row["confirmed_lexeme"] == "0" and row["component_export_credit"] == "0", f"okeey no export {review_id}")
        if row["gdt751_card_id"] != "NONE":
            check(row["current_safe_render_de"] == "heiß an der End-/Vollstufe; Trägerrolle offen", f"okeey safe render {review_id}")

    reader = (art / GENERATED[5]).read_text(encoding="utf-8")
    check("heiß an der End-/Vollstufe; Trägerrolle offen" in reader, "reader safe render")
    check("PREPARATION stays as a background hypothesis" in reader, "reader prep held")
    check("No value is assigned to EVA q" in reader, "reader no q export")

    packet_path = art / GENERATED[6]
    packet = read_tsv(packet_path)
    intake = json.loads((art / GENERATED[7]).read_text(encoding="utf-8"))
    check(len(packet) == 1 and packet[0]["edge_id"] == "G752E001", "one ambiguous edge")
    check(packet[0]["relation_type"] == "AMBIGUOUS_BOTH_EXACT_SPLITS", "edge ambiguous")
    check(packet[0]["pivot_locus"] == "f99r.50@3" and packet[0]["target_locus"] == "f99r.50@2", "edge coordinates")
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge invalid")
    check(intake["errors"] == ["edge row 2: formal access is not sealed"], "edge formal error")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / GENERATED[8]).read_text(encoding="utf-8"))
    check(result["schema"] == "GDT752_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {
        "control_contacts": 42,
        "control_pages": 36,
        "control_pair_types": 26,
        "gdt751_okeey_cards_reviewed": 10,
        "okeey_pair_contacts": 13,
        "q_contacts": 44,
        "q_pages": 27,
        "q_pair_types": 12,
    }, "result scope")
    formal = result["independent_outer_microfield_result"]
    check(formal["q_specific_quality_vs_base_preparation_split_supported"] is False, "result split false")
    check(formal["q_exact_support"] == 0 and formal["control_exact_reverse"] == 1, "result exact counts")
    check(formal["only_complete_q_exact_pattern"] == "SYMMETRIC_BOTH_SIDES_AT_f99r.50_NOT_DIRECTIONAL", "result symmetry")
    renderer = result["renderer_decision"]
    check(renderer["gdt751_okeey_preparation_cards_retained_as_spoken"] == 0, "renderer zero prep spoken")
    check(renderer["gdt751_okeey_preparation_cards_demoted_to_hypothesis_only"] == 10, "renderer ten prep held")
    check(renderer["gdt750_hot_end_occurrence_cards_retained"] == 10, "renderer ten hot end")
    check(renderer["current_render_de"] == "heiß an der End-/Vollstufe; Trägerrolle offen", "result current render")
    check(result["guard"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard exact")
    check(result["claim_boundary"]["q_component_export_credit"] == 0, "result no q export")
    check(result["claim_boundary"]["f84_accessed"] is False and result["claim_boundary"]["f84r_accessed"] is False, "result sealed")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt752_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT752_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "independent_outer_microfield_result": result["independent_outer_microfield_result"],
        "renderer_decision": result["renderer_decision"],
        "claim_ceiling": (
            "Occurrence-local complete-whole outer-field roles only. No q "
            "character, prefix, morpheme, sound, abbreviation, substring, "
            "lexeme, literal preparation, ingredient, plant, disease, cure, "
            "person, vessel, unit, plaintext, unseen form, image, "
            "transcription, new page, f84 or f84r."
        ),
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
