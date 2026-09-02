#!/usr/bin/env python3
"""Invariant, edge-gate and byte-replay validation for GDT751."""

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
BASE = Path("experiments/yolo/gdt751_q_base_carrier_shell_audit")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__51_Q_BASE_PAIRS__3761_EXACT_OCCURRENCES__"
    "47_QS_PRESERVED_INHERITED__41_BASE_ONLY_PREPARATION_INHERITED__"
    "Q_POSITION_EFFECT_NOT_SPECIFIC__44_DIRECT_CONTACTS_12_PAIR_TYPES__"
    "10_OKEEY_PREPARATION_CARDS__ZERO_Q_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "Q_BASE_51_PAIR_DECK.tsv",
    "Q_BASE_3761_OCCURRENCE_FEATURES.tsv",
    "NONQ_PREFIX_160_CONTROL_DECK.tsv",
    "MATCHED_51_CONTROL_MAP.tsv",
    "PAIR_GROUP_COMPARISON.tsv",
    "DIRECT_Q_BASE_CONTACTS.tsv",
    "OKEEY_10_CARRIER_ENRICHED_CARDS.tsv",
    "GDT751_Q_BASE_PAIR_READER.md",
    "GDT751_GDT388_Q_BASE_EDGE_PACKET.tsv",
    "GDT751_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
EXPECTED_GROUPS = {
    "Q_PREFIX_51": (51, 2060, 1701, 47, 41, 0, "-0.066507", 33, 18, 0, "-0.066200", "0.007412", "-0.052709", 12, 44, "35.313002"),
    "MATCHED_NONQ_PREFIX_51": (51, 941, 1369, 34, 0, 25, "-0.061454", 32, 18, 1, "-0.060830", "0.157524", "-0.004158", 6, 7, "14.000000"),
    "ALL_NONQ_PREFIX_160": (160, 3194, 12840, 90, 1, 50, "-0.080680", 102, 57, 1, "-0.080325", "0.204046", "0.003261", 26, 42, "20.348837"),
    "NONQ_O_BASE_PREFIX_14": (14, 90, 990, 7, 0, 1, "-0.167448", 11, 3, 0, "-0.165541", "0.320915", "-0.064446", 1, 2, "22.222222"),
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


def axes(text: str) -> set[str]:
    return set() if text in {"", "NONE", "OPEN"} else set(text.split("|"))


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
    check(manifest["experiment_id"] == "GDT751", "manifest id")
    check(manifest["slug"] == "q_base_carrier_shell_audit", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"]
        == ["GDT388", "GDT734", "GDT737", "GDT738", "GDT745", "GDT746", "GDT749", "GDT750"],
        "manifest dependencies",
    )
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed data")
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest ceiling")
    check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "validation contract")
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    q_pairs = read_tsv(art / GENERATED[0])
    occurrences = read_tsv(art / GENERATED[1])
    controls = read_tsv(art / GENERATED[2])
    matches = read_tsv(art / GENERATED[3])
    groups = read_tsv(art / GENERATED[4])
    contacts = read_tsv(art / GENERATED[5])
    enriched = read_tsv(art / GENERATED[6])

    check(len(q_pairs) == 51, "51 q pairs")
    check(len(occurrences) == 3761, "3761 q base occurrences")
    check(len(controls) == 160, "160 nonq controls")
    check(len(matches) == 51, "51 matched controls")
    check(len(groups) == 4, "four group summaries")
    check(len(contacts) == 44, "44 direct contacts")
    check(len(enriched) == 10, "ten carrier cards")
    check(len({row["pair_id"] for row in q_pairs}) == 51, "unique q pair ids")
    check(len({row["gdt751_occurrence_id"] for row in occurrences}) == 3761, "unique occurrence ids")
    check(len({row["pair_id"] for row in controls}) == 160, "unique control ids")
    check(len({row["gdt751_contact_id"] for row in contacts}) == 44, "unique contact ids")
    check(len({row["gdt751_carrier_card_id"] for row in enriched}) == 10, "unique carrier ids")

    for row in q_pairs:
        pair_id = row["pair_id"]
        check(row["prefix_character"] == "q", f"q prefix {pair_id}")
        check(row["prefix_surface"] == "q" + row["base_surface"], f"q base identity {pair_id}")
        check(row["base_initial"] == "o", f"q base o initial {pair_id}")
        check(row["literal_identity"] == "OPEN", f"q pair literal {pair_id}")
        check(row["confirmed_lexeme"] == "0", f"q pair lexeme {pair_id}")
        check(row["component_export_credit"] == "0", f"q pair component {pair_id}")
    check(sum(int(row["prefix_reader_exact_occurrences"]) for row in q_pairs) == 2060, "2060 q occurrences")
    check(sum(int(row["base_reader_exact_occurrences"]) for row in q_pairs) == 1701, "1701 base occurrences")
    check(sum(int(row["quality_stage_exactly_preserved"]) for row in q_pairs) == 47, "47 inherited quality stage matches")
    check(Counter(row["preparation_relation"] for row in q_pairs) == Counter({"BASE_ONLY": 41, "BOTH": 8, "NEITHER": 2}), "q preparation relations")
    check(sum(int(row["direct_contacts"]) for row in q_pairs) == 44, "q pair contact sum")
    check(sum(int(row["direct_contacts"]) > 0 for row in q_pairs) == 12, "twelve direct pair types")
    q_map = {row["prefix_surface"]: row for row in q_pairs}
    check(q_map["qokeey"]["base_surface"] == "okeey", "qokeey base")
    check(q_map["qokeey"]["prefix_canonical_axes"] == "HOT|END_STAGE", "qokeey axes")
    check(q_map["qokeey"]["base_canonical_axes"] == "HOT|END_STAGE|PREPARATION", "okeey inherited carrier")
    check(q_map["qokeey"]["direct_contacts"] == "13", "qokeey thirteen contacts")

    check(Counter(row["pair_side"] for row in occurrences) == Counter({"Q_SIDE": 2060, "UNPREFIXED_SIDE": 1701}), "occurrence side counts")
    check(sum(int(row["direct_pair_contact"]) for row in occurrences) == 102, "102 raw direct-contact flags")
    for row in occurrences:
        occurrence_id = row["gdt751_occurrence_id"]
        check(not row["page"].startswith("f84"), f"sealed occurrence {occurrence_id}")
        check(row["written_line_eva"].split()[int(row["token_ordinal"]) - 1] == row["surface"], f"occurrence coordinate {occurrence_id}")
        if row["pair_side"] == "Q_SIDE":
            check(row["surface"] == "q" + row["paired_surface"], f"occurrence q pair {occurrence_id}")
        else:
            check(row["paired_surface"] == "q" + row["surface"], f"occurrence base pair {occurrence_id}")
        check(row["literal_identity"] == "OPEN", f"occurrence literal {occurrence_id}")
        check(row["confirmed_lexeme"] == "0", f"occurrence lexeme {occurrence_id}")
        check(row["component_export_credit"] == "0", f"occurrence component {occurrence_id}")

    for row in controls:
        pair_id = row["pair_id"]
        check(row["prefix_character"] != "q", f"control nonq {pair_id}")
        check(row["prefix_surface"][1:] == row["base_surface"], f"control base identity {pair_id}")
        check(row["literal_identity"] == "OPEN", f"control literal {pair_id}")
        check(row["confirmed_lexeme"] == "0", f"control lexeme {pair_id}")
        check(row["component_export_credit"] == "0", f"control component {pair_id}")
    check(sum(int(row["quality_stage_exactly_preserved"]) for row in controls) == 90, "control 90 quality stage matches")
    check(Counter(row["preparation_relation"] for row in controls) == Counter({"NEITHER": 89, "PREFIX_ONLY": 50, "BOTH": 20, "BASE_ONLY": 1}), "control preparation relations")

    check(len({row["q_pair_id"] for row in matches}) == 51, "matched all q pairs")
    check(len({row["control_pair_id"] for row in matches}) == 51, "matched controls unique")
    check(all(row["matching_used_position_or_semantic_outcome"] == "0" for row in matches), "outcome-free matching")
    check(all(row["component_export_credit"] == "0" for row in matches), "match zero component")

    group_map = {row["group_id"]: row for row in groups}
    check(set(group_map) == set(EXPECTED_GROUPS), "group ids")
    for group_id, expected in EXPECTED_GROUPS.items():
        row = group_map[group_id]
        actual = (
            int(row["pair_count"]),
            int(row["reader_exact_prefix_occurrences"]),
            int(row["reader_exact_base_occurrences"]),
            int(row["quality_stage_exactly_preserved_pairs"]),
            int(row["preparation_base_only_pairs"]),
            int(row["preparation_prefix_only_pairs"]),
            row["mean_raw_position_delta_prefix_minus_base"],
            int(row["prefix_earlier_pairs"]), int(row["prefix_later_pairs"]),
            int(row["position_ties"]),
            row["mean_section_residual_position_delta"],
            row["mean_line_first_delta"], row["mean_line_last_delta"],
            int(row["direct_contact_pair_types"]), int(row["direct_contacts"]),
            row["contacts_per_1000_min_occurrences"],
        )
        check(actual == expected, f"group result {group_id}")
        check(row["literal_identity_credit"] == "0", f"group literal {group_id}")
        check(row["confirmed_lexeme"] == "0", f"group lexeme {group_id}")
        check(row["component_export_credit"] == "0", f"group component {group_id}")

    check(len({row["pair_id"] for row in contacts}) == 12, "contact twelve pair ids")
    check(len({row["page"] for row in contacts}) == 27, "contact 27 pages")
    check(Counter(row["written_order"] for row in contacts) == Counter({"Q_THEN_BASE": 24, "BASE_THEN_Q": 20}), "contact order 24 20")
    check(Counter(row["q_surface"] for row in contacts)["qokeey"] == 13, "thirteen qokeey contacts")
    for row in contacts:
        contact_id = row["gdt751_contact_id"]
        check(not row["page"].startswith("f84"), f"sealed contact {contact_id}")
        words = row["written_line_eva"].split()
        check(words[int(row["q_ordinal"]) - 1] == row["q_surface"], f"contact q coordinate {contact_id}")
        check(words[int(row["base_ordinal"]) - 1] == row["base_surface"], f"contact base coordinate {contact_id}")
        check(abs(int(row["signed_base_from_q"])) == 1, f"contact adjacent {contact_id}")
        check(int(row["base_ordinal"]) - int(row["q_ordinal"]) == int(row["signed_base_from_q"]), f"contact direction {contact_id}")
        check(row["literal_identity"] == "OPEN", f"contact literal {contact_id}")
        check(row["confirmed_lexeme"] == "0", f"contact lexeme {contact_id}")
        check(row["component_export_credit"] == "0", f"contact component {contact_id}")

    check(len({row["gdt750_active_card_id"] for row in enriched}) == 10, "ten distinct predecessor cards")
    check(len({row["page"] for row in enriched}) == 7, "carrier cards seven pages")
    for row in enriched:
        card_id = row["gdt751_carrier_card_id"]
        check(row["target_surface"] == "okeey" and row["q_pair_surface"] == "qokeey", f"carrier pair {card_id}")
        check(row["gdt750_emitted_axes"] == "HOT|END_STAGE", f"carrier axes {card_id}")
        check(row["added_carrier_role"] == "PREPARATION", f"carrier role {card_id}")
        check(row["working_render_de"] == "heiße Zubereitung an der End-/Vollstufe", f"carrier render {card_id}")
        check(":qokeey:" in row["local_direct_pair_host"], f"carrier local host {card_id}")
        check(row["pair_quality_stage_preserved"] == "1" and row["pair_preparation_relation"] == "BASE_ONLY", f"carrier pair evidence {card_id}")
        check(row["scope"] == "THIS_OCCURRENCE_ONLY", f"carrier scope {card_id}")
        check(row["written_line_eva"].split()[int(row["token_ordinal"]) - 1] == "okeey", f"carrier coordinate {card_id}")
        check(row["literal_identity"] == "OPEN", f"carrier literal {card_id}")
        check(row["confirmed_lexeme"] == "0", f"carrier lexeme {card_id}")
        check(row["component_export_credit"] == "0", f"carrier component {card_id}")

    reader = (art / GENERATED[7]).read_text(encoding="utf-8")
    check("heiße Zubereitung an der End-/Vollstufe" in reader, "reader concrete carrier")
    check("q character or substring value is exported" in reader, "reader no q export")

    packet_path = art / GENERATED[8]
    packet = read_tsv(packet_path)
    intake = json.loads((art / GENERATED[9]).read_text(encoding="utf-8"))
    check(len(packet) == 44, "44 edge rows")
    check(len({row["edge_id"] for row in packet}) == 44, "unique edge ids")
    for row in packet:
        edge_id = row["edge_id"]
        check(row["page"] == row["pivot_locus"].split(".")[0].split("@")[0], f"edge pivot page {edge_id}")
        check(row["page"] == row["target_locus"].split(".")[0].split("@")[0], f"edge target page {edge_id}")
        check(row["relation_type"] == "DIRECT_Q_BASE_COMPLETE_WHOLE_PAIR", f"edge relation {edge_id}")
    expected_errors = [f"edge row {number}: formal access is not sealed" for number in range(2, 46)]
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge invalid not ready")
    check(intake["errors"] == expected_errors, "edge sole formal errors")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker expected return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / GENERATED[10]).read_text(encoding="utf-8"))
    check(result["schema"] == "GDT751_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {
        "all_prefix_pairs": 211,
        "allowed_pages": 179,
        "base_reader_exact_occurrences": 1701,
        "clean_complete_surfaces": 690,
        "direct_q_base_contacts": 44,
        "direct_q_base_pages": 27,
        "direct_q_base_pair_types": 12,
        "nonq_prefix_controls": 160,
        "okeey_carrier_enriched_positions": 10,
        "q_base_pairs": 51,
        "q_reader_exact_occurrences": 2060,
    }, "result scope")
    check(result["inherited_semantic_pattern"] == {
        "evidence_status": "MODEL_INTERNAL_NOT_INDEPENDENT",
        "preparation_base_only_pairs": 41,
        "preparation_q_only_pairs": 0,
        "quality_stage_exactly_preserved_pairs": 47,
    }, "result inherited pattern")
    formal = result["independent_formal_controls"]
    check(formal["q_specific_entry_position_supported"] is False, "result q position not special")
    check(formal["q_to_nonq_contact_density_ratio"] == 1.735382, "result contact ratio")
    check(result["guard"]["tokens_cross"]["allowed_pages"] == 179, "result allowed pages")
    check(result["guard"]["lines"]["selected"] == 4137, "result guarded lines")
    check(result["edge_intake"]["errors"] == expected_errors, "result edge errors")
    check("No q character" in result["claim_ceiling"], "result claim ceiling")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt751_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT751_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "inherited_semantic_pattern": result["inherited_semantic_pattern"],
        "independent_formal_controls": result["independent_formal_controls"],
        "claim_ceiling": result["claim_ceiling"],
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
