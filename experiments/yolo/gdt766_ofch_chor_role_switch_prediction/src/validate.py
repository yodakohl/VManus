#!/usr/bin/env python3
"""Validate and byte-replay GDT766 without widening its source scope."""

from __future__ import annotations

import argparse
import csv
import importlib.util
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
EXP = ROOT / "experiments/yolo/gdt766_ofch_chor_role_switch_prediction"
DEFAULT_ARTIFACTS = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"

EXPECTED_OUTPUTS = (
    "OFCH_CORE_43_OCCURRENCE_ATLAS.tsv",
    "OFCH_CORE_25_FORM_PROFILE.tsv",
    "OFCH_CORE_3_SCOPE_SUMMARY.tsv",
    "OFCH_REPRODUCTIVE_4_BRIDGE_ATLAS.tsv",
    "GDT766_GDT388_ROOT_BRIDGE_EDGE_PACKET.tsv",
    "OFCHEDY_QOFCHEDY_10_PAIR_AUDIT.tsv",
    "OFCH_25_WORKING_DICTIONARY.tsv",
    "OFCH_43_CONCRETE_RENDERER.tsv",
    "OFCH_22_MATCHED_GEOMETRY_CONTROL.tsv",
    "OFCH_22_MATCHED_CONTROL_SUMMARY.tsv",
    "CHOR_ROLE_191_OCCURRENCE_ATLAS.tsv",
    "CHOR_ROLE_4_PROFILE.tsv",
    "CHOR_STATE_VALUE_CONTACT_ATLAS.tsv",
    "CHOR_PCHOR_GEOMETRY_CONTRAST.tsv",
    "CHOR_ROLE_SUBSTITUTION_MATRIX.tsv",
    "CHOR_ROLE_4_WORKING_DICTIONARY.tsv",
    "FAMILY_MODEL_SCORECARD.tsv",
    "CONCRETE_WHOLE_CANDIDATE_TOURNAMENT.tsv",
    "FAMILY_DERIVATION_QUARANTINE.tsv",
    "FIVE_COMPLETE_LINE_WORKING_READER.tsv",
    "HISTORICAL_MIXED_RECORD_COMPARATORS.tsv",
    "RESULT.json",
)


def load_run():
    spec = importlib.util.spec_from_file_location("gdt766_run_for_validation", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT766 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="run every check but do not write VALIDATION.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    art = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    run = load_run()
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    check(tuple(run.OUTPUT_NAMES) == EXPECTED_OUTPUTS, "declared generated-output set")
    for name in EXPECTED_OUTPUTS:
        check((art / name).is_file(), f"declared output exists: {name}")

    ofch = read_tsv(art / EXPECTED_OUTPUTS[0])
    ofch_profiles = read_tsv(art / EXPECTED_OUTPUTS[1])
    ofch_scopes = read_tsv(art / EXPECTED_OUTPUTS[2])
    bridges = read_tsv(art / EXPECTED_OUTPUTS[3])
    packet_path = art / EXPECTED_OUTPUTS[4]
    packet = read_tsv(packet_path)
    pair_audit = read_tsv(art / EXPECTED_OUTPUTS[5])
    ofch_dictionary = read_tsv(art / EXPECTED_OUTPUTS[6])
    ofch_renderer = read_tsv(art / EXPECTED_OUTPUTS[7])
    controls = read_tsv(art / EXPECTED_OUTPUTS[8])
    control_summary_rows = read_tsv(art / EXPECTED_OUTPUTS[9])
    chor = read_tsv(art / EXPECTED_OUTPUTS[10])
    chor_profiles = read_tsv(art / EXPECTED_OUTPUTS[11])
    chor_contacts = read_tsv(art / EXPECTED_OUTPUTS[12])
    chor_contrast = read_tsv(art / EXPECTED_OUTPUTS[13])
    substitutions = read_tsv(art / EXPECTED_OUTPUTS[14])
    chor_dictionary = read_tsv(art / EXPECTED_OUTPUTS[15])
    family_models = read_tsv(art / EXPECTED_OUTPUTS[16])
    tournament = read_tsv(art / EXPECTED_OUTPUTS[17])
    quarantine = read_tsv(art / EXPECTED_OUTPUTS[18])
    reader = read_tsv(art / EXPECTED_OUTPUTS[19])
    history = read_tsv(art / EXPECTED_OUTPUTS[20])
    result = json.loads((art / EXPECTED_OUTPUTS[21]).read_text(encoding="utf-8"))

    # Rebind the three occurrence-bearing products to the guarded reader rather
    # than accepting the builder's exactness assertion on trust.
    env = run.g765.g764.semantic_environment()
    context = env["context"]

    def check_exact_token(row: dict[str, str], label: str) -> None:
        locus = row["locus"]
        ordinal = int(row["ordinal"])
        check(locus in context.by_line, f"known reader locus {label}")
        line = context.by_line[locus]
        check(1 <= ordinal <= len(line), f"reader ordinal in range {label}")
        token = line[ordinal - 1]
        check(str(token["eva"]) == row["surface"], f"surface rebound {label}")
        check(run.is_exact(env, locus, token), f"reader-exact gate {label}")

    for row in ofch:
        check_exact_token(row, row["occurrence_id"])
    for row in chor:
        check_exact_token(row, row["occurrence_id"])
    for row in reader:
        check_exact_token(row, row["reader_token_id"])

    # Complete reader-exact census of every admitted surface containing ``ofch``.
    check(len(ofch) == 43, "43 exact ofch-containing occurrences")
    check(len({row["occurrence_id"] for row in ofch}) == 43, "unique ofch occurrence ids")
    check(len({row["surface"] for row in ofch}) == 25, "25 exact ofch-containing forms")
    check(all("ofch" in row["surface"] for row in ofch), "ofch-containing predicate")
    check(len(ofch_profiles) == 25, "25 ofch whole-form profiles")
    check({row["surface"] for row in ofch_profiles} == {row["surface"] for row in ofch}, "profile covers census")
    check(sum(row["surface"].startswith("ofch") for row in ofch) == 25, "25 exact ofch-prefix occurrences")
    check(sum(not row["surface"].startswith("ofch") for row in ofch) == 18, "18 exact outer-shell occurrences")
    check(Counter(row["line_position"] for row in ofch) == Counter({"MIDDLE": 36, "LAST": 6, "FIRST": 1}), "ofch geometry")
    check(sum(row["paragraph_start_line"] == "1" for row in ofch) == 34, "34 ofch paragraph-start lines")
    check(sum(int(row["true_paragraph_opener"]) for row in ofch) == 1, "one true ofch opener")
    check(sum(row["paragraph_end_line"] == "1" for row in ofch) == 0, "zero ofch paragraph-end lines")

    scope_map = {row["scope"]: row for row in ofch_scopes}
    check(len(ofch_scopes) == 3 and set(scope_map) == {"OFCH_CONTAINING", "OFCH_PREFIX_ONLY", "OUTER_SHELL_ONLY"}, "three scope summaries")
    all_scope = scope_map["OFCH_CONTAINING"]
    prefix_scope = scope_map["OFCH_PREFIX_ONLY"]
    check(tuple(int(all_scope[key]) for key in ("raw_occurrences", "raw_forms", "reader_exact_occurrences", "reader_exact_forms", "pages", "loci")) == (58, 32, 43, 25, 36, 41), "containing scope census")
    check(all_scope["line_positions"] == "FIRST:1|LAST:6|MIDDLE:36", "containing scope position summary")
    check(tuple(int(all_scope[key]) for key in ("paragraph_start_lines", "true_paragraph_openers", "paragraph_end_lines")) == (34, 1, 0), "containing paragraph geometry")
    check(tuple(int(prefix_scope[key]) for key in ("raw_occurrences", "raw_forms", "reader_exact_occurrences", "reader_exact_forms")) == (30, 15, 25, 13), "prefix scope census")
    check(prefix_scope["line_positions"] == "LAST:4|MIDDLE:21", "prefix zero line-first geometry")
    check(int(prefix_scope["repeated_exact_immediate_edges"]) == 0, "prefix zero repeated exact immediate edges")

    expected_bridges = {
        ("f8r.9", "ofchey", "shor"),
        ("f22r.4", "ofchy", "schor"),
        ("f37r.1", "ofchor", "chory"),
        ("f95v2.1", "ofchdy", "shor"),
    }
    check(len(bridges) == len(packet) == 4, "four reproductive bridges and edge rows")
    check({(row["locus"], row["ofch_surface"], row["reproductive_surface"]) for row in bridges} == expected_bridges, "exact reproductive bridge set")
    check(all(row["bridge_support"] == "WEAK_SAME_LINE_DOMAIN_COMPATIBILITY" and row["score_ready_relation_credit"] == "0" for row in bridges), "bridge claim ceiling")
    check(Counter(row["surface"] for row in pair_audit) == Counter({"ofchedy": 5, "qofchedy": 5}), "ofchedy/qofchedy five-plus-five")
    check(all(row["old_action_composition"] == "REMOVED" and row["q_command_export"] == "0" for row in pair_audit), "old action composition removed")
    check(len(ofch_dictionary) == 25 and len(ofch_renderer) == 43, "ofch dictionary and renderer coverage")
    check(all(row["family_analogy_scope"] == "1" and row["global_component_export"] == "0" for row in ofch_dictionary), "family analogy is whole-form scope, not root export")
    check(all(row["specific_identity_is_replaceable"] == "1" and row["confirmed_lexeme"] == "0" and row["unseen_form_export"] == "0" for row in ofch_dictionary), "ofch defaults remain replaceable observed wholes")
    check(all(row["scope"] == "THIS_OBSERVED_EXACT_WHOLE_FORM" and row["confirmed_plaintext"] == "0" for row in ofch_renderer), "ofch renderer occurrence scope")

    # Full control pools: same section and exact whole-form frequency; all
    # ofch-prefix forms excluded; no outcome matching and no sampling.
    check(len(controls) == 22 and len(control_summary_rows) == 1, "22 non-ofchy prefix targets and one control summary")
    check(all(row["target_surface"].startswith("ofch") and row["target_surface"] != "ofchy" for row in controls), "control target definition")
    check(all(row["matching_rule"] == "SAME_SECTION_AND_GLOBAL_EXACT_WHOLE_FORM_FREQUENCY__EXCLUDE_OFCH_PREFIX" for row in controls), "control matching rule")
    check(all(row["sampling"] == "NONE_FULL_POOL" and row["outcome_matched"] == "0" for row in controls), "deterministic full-pool controls")
    target_rows = {
        row["occurrence_id"]: row
        for row in ofch
        if row["surface"].startswith("ofch") and row["surface"] != "ofchy"
    }
    check({row["target_occurrence_id"] for row in controls} == set(target_rows), "controls cover exact 22-target set")

    # Independently rebuild every full comparison pool. This fixes the eligible
    # universe and verifies that no line-position or paragraph outcome entered
    # matching or tie-breaking (there is no sampling and therefore no tie).
    exact_counts = run.exact_surface_counts(env)
    control_pools: dict[tuple[str, int], list[tuple[int, int]]] = {}
    eligible_control_occurrences = 0
    eligible_control_forms: set[str] = set()
    for locus, line in sorted(context.by_line.items()):
        for ordinal, token in enumerate(line, 1):
            if not run.is_exact(env, locus, token):
                continue
            surface = str(token["eva"])
            if surface.startswith("ofch"):
                continue
            section = str(token["section"])
            key = (section, int(exact_counts[surface]))
            control_pools.setdefault(key, []).append((
                int(ordinal == 1),
                int(str(env["line_meta"][locus]["paragraph_start"]) == "1"),
            ))
            eligible_control_occurrences += 1
            eligible_control_forms.add(surface)
    check(sum(exact_counts.values()) == 24090, "independent exact-token universe")
    check(eligible_control_occurrences == 24065 and len(eligible_control_forms) == 4803, "independent eligible control universe")
    for row in controls:
        target = target_rows[row["target_occurrence_id"]]
        frequency = int(exact_counts[target["surface"]])
        check((row["target_surface"], row["target_page"], row["target_locus"], row["target_section"]) == (target["surface"], target["page"], target["locus"], target["section"]), f"target metadata {row['match_id']}")
        check(int(row["target_global_exact_form_frequency"]) == frequency, f"target frequency {row['match_id']}")
        pool = control_pools[(target["section"], frequency)]
        first = sum(item[0] for item in pool)
        pstart = sum(item[1] for item in pool)
        check(int(row["control_pool_occurrences"]) == len(pool), f"pool size {row['match_id']}")
        check(int(row["control_line_first_occurrences"]) == first, f"pool line-first count {row['match_id']}")
        check(row["control_line_first_rate"] == f"{first / len(pool):.12f}", f"pool line-first rate {row['match_id']}")
        check(int(row["control_paragraph_start_occurrences"]) == pstart, f"pool paragraph-start count {row['match_id']}")
        check(row["control_paragraph_start_rate"] == f"{pstart / len(pool):.12f}", f"pool paragraph-start rate {row['match_id']}")
    control = control_summary_rows[0]
    exact_control_bookkeeping = {
        "target_occurrences": 22,
        "target_line_first_occurrences": 0,
        "target_paragraph_start_occurrences": 17,
        "reader_exact_token_universe": 24090,
        "eligible_control_occurrences": 24065,
        "eligible_control_forms": 4803,
        "used_control_union_occurrences": 4335,
        "control_pool_appearances_with_reuse": 11471,
    }
    check(all(int(control[key]) == value for key, value in exact_control_bookkeeping.items()), "exact matched-control bookkeeping")
    check(control["target_line_first_rate"] == "0.000000000000" and control["macro_control_line_first_rate"] == "0.192545528074", "line-first 0% versus 19.2546%")
    check(control["target_paragraph_start_rate"] == "0.772727272727" and control["macro_control_paragraph_start_rate"] == "0.263922798558", "paragraph-start 77.2727% versus 26.3923%")
    check(control["interpretation"] == "OFCH_PREFIX_IS_ENRICHED_ON_PARAGRAPH_START_LINES_BUT_AVOIDS_LINE_FIRST_POSITION", "matched-control interpretation")

    # Complete-whole chor family and its pchor opener contrast.
    expected_chor = Counter({"chor": 176, "pchor": 10, "schor": 3, "lchor": 2})
    check(len(chor) == 191 and Counter(row["surface"] for row in chor) == expected_chor, "191 exact chor-family occurrences")
    check(len({row["occurrence_id"] for row in chor}) == 191, "unique chor occurrence ids")
    check(len({row["page"] for row in chor}) == 99 and len({row["locus"] for row in chor}) == 183, "chor coverage")
    check(len(chor_profiles) == 4 and {row["surface"] for row in chor_profiles} == set(expected_chor), "four chor profiles")
    check(Counter(row["line_position"] for row in chor if row["surface"] == "chor") == Counter({"MIDDLE": 161, "FIRST": 10, "LAST": 5}), "chor medial content geometry")
    check(Counter(row["line_position"] for row in chor if row["surface"] == "pchor") == Counter({"FIRST": 7, "MIDDLE": 3}), "pchor opening geometry")
    check(sum(row["paragraph_start_line"] == "1" for row in chor if row["surface"] == "pchor") == 9, "pchor paragraph-start lines")
    check(sum(int(row["true_paragraph_opener"]) for row in chor if row["surface"] == "pchor") == 6, "six pchor true openers")
    check(len(chor_contacts) == 41 and Counter(row["contact_class"] for row in chor_contacts) == Counter({"STATE": 22, "VALUE": 19}), "41 chor state/value contacts")
    expected_contrast = {
        "LINE_FIRST": (7, 3, 10, 166, "0.700000000000", "0.056818181818", "1.47209264739e-06"),
        "TRUE_PARAGRAPH_OPENER": (6, 4, 0, 176, "0.600000000000", "0.000000000000", "3.96139585617e-09"),
    }
    check(len(chor_contrast) == 2 and {row["outcome"] for row in chor_contrast} == set(expected_contrast), "two chor/pchor contrasts")
    for row in chor_contrast:
        expected = expected_contrast[row["outcome"]]
        observed = tuple(int(row[key]) for key in ("pchor_yes", "pchor_no", "chor_yes", "chor_no")) + tuple(row[key] for key in ("pchor_rate", "chor_rate", "fisher_two_sided_p"))
        check(observed == expected, f"exact pchor/chor contrast {row['outcome']}")
    check(len(substitutions) == 16 and sum(row["selected_for_surface"] == "1" for row in substitutions) == 4, "four-by-four role substitution matrix")
    check(len(chor_dictionary) == 4 and all(row["whole_word_only"] == "1" for row in chor_dictionary), "four whole-word chor defaults")
    check(next(row for row in chor_dictionary if row["surface"] == "pchor")["bold_default_de"] == "nimm", "pchor bold opening default")
    check(next(row for row in chor_dictionary if row["surface"] == "chor")["bold_default_de"] == "Blütenstand", "chor bold content default")
    check(next(row for row in chor_dictionary if row["surface"] == "lchor")["bold_default_de"] == "Blütenzubereitung", "lchor extraction overclaim removed")
    check(sum(row["surface"] == "pchor" and row["occurrence_bold_default_de"] == "nimm" for row in chor) == 6 and sum(row["surface"] == "pchor" and row["occurrence_bold_default_de"] == "Rezept- oder Eintragsmarker" for row in chor) == 4, "pchor imperative dispatched only at true paragraph openers")

    check(len(family_models) == 7 and sum(row["selected_portable"] == "1" for row in family_models) == 2 and sum(row["selected_bold"] == "1" for row in family_models) == 2, "selected portable and bold family models")
    check({row["hypothesis_id"]: int(row["working_score"]) for row in family_models} == {"OFC_GENERIC_DRUG_CORE": 15, "OFC_FLOWER_DRUG_CORE": 13, "OFC_PROCESS_COMMAND_CORE": -5, "OFC_ORTHOGRAPHIC_ONLY": -1, "CHR_ROLE_SWITCHED_WHOLES": 18, "CHR_SHARED_PLANT_NOUN": 2, "CHR_SHARED_FORMULA": -2}, "registered family-model score order")
    check(len(tournament) == 87 and all(row["identity_is_replaceable"] == "1" for row in tournament), "87 replaceable whole candidates")
    check(len(quarantine) == 6 and all(row["component_export"] == "0" for row in quarantine), "six derivation quarantines")
    check(len(history) == 7 and all(row["target_spelling_credit"] == "0" and row["target_identity_credit"] == "0" for row in history), "seven architecture-only comparators")

    # Five complete cached lines, all 46 exact tokens supplied with a local
    # default, but with no plaintext or component promotion.
    expected_line_lengths = {"f22r.4": 9, "f22v.1": 8, "f41v.2": 9, "f93r.2": 11, "f107r.38": 9}
    check(len(reader) == 46 and Counter(row["locus"] for row in reader) == Counter(expected_line_lengths), "five full lines and 46 tokens")
    for locus, length in expected_line_lengths.items():
        rows = sorted((row for row in reader if row["locus"] == locus), key=lambda row: int(row["ordinal"]))
        check([int(row["ordinal"]) for row in rows] == list(range(1, length + 1)), f"complete ordinal coverage {locus}")
        check(len({row["portable_line_renderer_de"] for row in rows}) == 1, f"single portable renderer {locus}")
        check(len({row["bold_line_renderer_de"] for row in rows}) == 1, f"single bold renderer {locus}")
    check(all(row["local_default_de"] and row["global_export"] == "0" and row["confirmed_plaintext"] == "0" for row in reader), "local defaults without global export")

    # No generated table may silently export a component, plaintext, identity,
    # or sealed-page locus.
    tables = (
        ofch, ofch_profiles, ofch_scopes, bridges, packet, pair_audit, ofch_dictionary,
        ofch_renderer, controls, control_summary_rows, chor, chor_profiles,
        chor_contacts, chor_contrast, substitutions, chor_dictionary, family_models,
        tournament, quarantine, reader, history,
    )
    zero_fields = {
        "component_export", "component_export_credit", "global_component_export",
        "global_export", "q_command_export", "score_ready_relation_credit",
        "confirmed_lexeme", "confirmed_plaintext", "unseen_form_export",
        "identity_credit", "specific_flower_credit", "target_spelling_credit",
        "target_identity_credit",
    }
    for rows in tables:
        for row in rows:
            for field in zero_fields & row.keys():
                check(row[field] == "0", f"zero claim/export field {field}")
            for field in ("page", "physical_folio", "locus", "target_locus", "pivot_locus"):
                check(not row.get(field, "").lower().startswith("f84"), f"sealed f84 absent from {field}")

    # Pass the official intake validator: the text-cooccurrence rows are valid
    # acquisition records but deliberately have no eligible relation edges.
    check(all(row["relation_type"] == "SAME_LINE_TEXT_COOCCURRENCE" for row in packet), "edge relation type")
    check(all(row["formal_access_state"] == "SEALED_NOT_ACCESSED" and row["eligibility_status"] == "INELIGIBLE_TEXT_COOCCURRENCE" for row in packet), "edge packet remains ineligible")
    intake_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    check(intake_run.returncode == 0, "official edge intake exits zero")
    intake = json.loads(intake_run.stdout)
    expected_intake = {
        "capacity_gate_50_edges_5_folios": False,
        "discovery_edges": 0,
        "eligible_edges": 0,
        "eligible_folios": 0,
        "errors": [],
        "holdout_edges": 0,
        "holdout_gate": False,
        "mobile_edges": 0,
        "mobile_null_gate": False,
        "packet_rows": 4,
        "score_ready": False,
        "status": "VALID_ACQUISITION_NOT_SCORE_READY",
    }
    check(intake == expected_intake, "official four-row relation intake")

    check(result["schema"] == "GDT766_RESULT_V1" and result["status"] == run.STATUS, "result schema/status")
    check(result["scope"] == {
        "ofch_containing_exact_occurrences": 43,
        "ofch_containing_exact_forms": 25,
        "ofch_containing_pages": 36,
        "ofch_containing_loci": 41,
        "ofch_prefix_exact_occurrences": 25,
        "ofch_prefix_exact_forms": 13,
        "matched_control_targets": 22,
        "reproductive_same_line_bridges": 4,
        "chor_family_exact_occurrences": 191,
        "chor_family_pages": 99,
        "chor_family_loci": 183,
        "complete_reader_lines": 5,
        "complete_reader_tokens": 46,
        "historical_comparators": 7,
    }, "result exact scope")
    check(result["relation_packet"] == intake, "result embeds official packet status")
    check(result["guard"] == {"inherited_token_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}}, "guarded reader provenance")
    boundary = result["claim_boundary"]
    check(boundary == {
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "confirmed_substances": 0,
        "confirmed_units": 0,
        "component_values": 0,
        "unseen_form_exports": 0,
        "new_pages": 0,
        "new_images": 0,
        "f84_accessed": False,
        "f84r_accessed": False,
    }, "result claim boundary")

    # Rebuild in isolation and compare every builder-declared output bytewise.
    with tempfile.TemporaryDirectory(prefix=".gdt766_replay_", dir=EXP) as temp_name:
        replay = Path(temp_name)
        run.build(replay)
        for name in run.OUTPUT_NAMES:
            check((art / name).read_bytes() == (replay / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT766_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "declared_outputs_byte_identical": len(run.OUTPUT_NAMES),
        "ofch_exact_occurrences": len(ofch),
        "ofch_exact_forms": len({row["surface"] for row in ofch}),
        "ofch_prefix_exact_occurrences": sum(row["surface"].startswith("ofch") for row in ofch),
        "matched_control_targets": len(controls),
        "chor_family_exact_occurrences": len(chor),
        "complete_line_tokens": len(reader),
        "relation_packet_status": intake["status"],
        "relation_packet_score_ready": intake["score_ready"],
        "component_exports": 0,
        "sealed_f84": "FORBIDDEN_NOT_ACCESSED",
        "sealed_f84r": "FORBIDDEN_NOT_ACCESSED",
        "new_pages": 0,
    }
    if not args.check_only:
        art.mkdir(parents=True, exist_ok=True)
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
