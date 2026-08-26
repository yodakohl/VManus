#!/usr/bin/env python3
"""Validate GDT466 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
READER = BASE / "src/read_address.py"

SOURCE_LABELS = ROOT / "experiments/yolo/gdt465_oiil_cross_reading_renderer_closure/artifacts/gdt465_107_final_hybrid_dictionary.tsv"
EDGE_SOURCE = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_27_calibrated_edge_stems.tsv"
INTERNAL_SOURCE = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts/gdt461_9_calibrated_internal_stems.tsv"
FAMILY_SOURCE = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_17_owner_class_family_stems.tsv"
CHEO_SOURCE = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts/gdt461_residual_owner_family_bridge.tsv"
AR_SOURCE = ROOT / "experiments/yolo/gdt462_near_threshold_ar_edge_exception_audit/artifacts/gdt462_residual_edge_channel_inventory.tsv"
THIN_SOURCE = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges/artifacts/gdt463_4_bridge_decisions.tsv"
BRIDGE_SOURCE = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge/artifacts/gdt464_4_bridge_decisions.tsv"

RULES_OUT = OUT / "gdt466_44_function_channel_deck.tsv"
FAMILIES_OUT = OUT / "gdt466_18_owner_family_channel_deck.tsv"
CORRECTION_OUT = OUT / "gdt466_propagation_correction.tsv"
DICTIONARY_OUT = OUT / "gdt466_107_intake_dictionary.tsv"
EXACT_OUT = OUT / "gdt466_107_exact_label_replay.tsv"
COLD_OUT = OUT / "gdt466_107_cold_shell_replay.tsv"
CORE_OUT = OUT / "gdt466_89_unseen_core_insertion_probes.tsv"
PROBE_OUT = OUT / "gdt466_81_channel_and_fallback_probes.tsv"
CONTRACT_OUT = OUT / "gdt466_intake_contract.json"
RESULT_OUT = OUT / "gdt466_result.json"
VALIDATION_OUT = OUT / "gdt466_validation.json"
GENERATED = (RULES_OUT, FAMILIES_OUT, CORRECTION_OUT, DICTIONARY_OUT, EXACT_OUT, COLD_OUT, CORE_OUT, PROBE_OUT, CONTRACT_OUT, RESULT_OUT)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reader(surface: str, content_class: str) -> tuple[int, dict[str, object], str]:
    completed = subprocess.run([sys.executable, str(READER), surface, content_class], cwd=ROOT, capture_output=True, text=True, check=False)
    payload = json.loads(completed.stdout) if completed.stdout else {}
    return completed.returncode, payload, completed.stderr


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    source = read_tsv(SOURCE_LABELS)
    edge_source = read_tsv(EDGE_SOURCE)
    internal_source = read_tsv(INTERNAL_SOURCE)
    family_source = read_tsv(FAMILY_SOURCE)
    cheo_source = read_tsv(CHEO_SOURCE)
    ar_source = read_tsv(AR_SOURCE)
    thin_source = read_tsv(THIN_SOURCE)
    bridge_source = read_tsv(BRIDGE_SOURCE)
    rules = read_tsv(RULES_OUT)
    families = read_tsv(FAMILIES_OUT)
    correction = read_tsv(CORRECTION_OUT)
    labels = read_tsv(DICTIONARY_OUT)
    exact = read_tsv(EXACT_OUT)
    cold = read_tsv(COLD_OUT)
    core = read_tsv(CORE_OUT)
    probes = read_tsv(PROBE_OUT)
    contract = json.loads(CONTRACT_OUT.read_text(encoding="utf-8"))
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))

    check("source_label_count", len(source) == 107 and len({row["surface"] for row in source}) == 107, f"observed={len(source)}")
    check("edge_source_count", len(edge_source) == 27, f"observed={len(edge_source)}")
    check("internal_source_count", len(internal_source) == 9, f"observed={len(internal_source)}")
    check("family_source_count", len(family_source) == 17, f"observed={len(family_source)}")
    check("cheo_source_count", len(cheo_source) == 1 and cheo_source[0]["surface_substring"] == "cheo", str(cheo_source))
    promoted_ar = [row for row in ar_source if row["decision"] == "PROMOTE_AFTER_PACKAGE_EXCEPTION"]
    check("ar_source_single_promotion", len(promoted_ar) == 1 and promoted_ar[0]["edge"] == "PREFIX" and promoted_ar[0]["surface_stem"] == "ar", str(promoted_ar))
    check("thin_source_count", len(thin_source) == 4 and {row["surface_stem"] for row in thin_source} == {"oin", "kor", "yky", "cfhy"}, "four thin bridges")
    general_bridges = [row for row in bridge_source if row["channel"].split("_", 1)[0] in {"PREFIX", "SUFFIX"}]
    check("bridge_source_general_count", len(general_bridges) == 3 and {row["channel"] for row in general_bridges} == {"PREFIX_of", "SUFFIX_ainy", "SUFFIX_eey"}, str([row["channel"] for row in general_bridges]))

    check("function_rule_count", len(rules) == 44, f"observed={len(rules)}")
    check("function_rule_ids", [row["channel_id"] for row in rules] == [f"G466-C{i:02d}" for i in range(1, 45)], "C01-C44")
    check("function_rule_lineage", Counter(row["source_experiment"] for row in rules) == Counter({"GDT460": 27, "GDT461": 9, "GDT462": 1, "GDT463": 4, "GDT464": 3}), str(Counter(row["source_experiment"] for row in rules)))
    check("function_rule_kinds", Counter(row["channel_kind"] for row in rules) == Counter({"PREFIX": 12, "SUFFIX": 23, "INTERNAL": 9}), str(Counter(row["channel_kind"] for row in rules)))
    check("function_rule_unique_keys", len({(row["channel_kind"], row["surface_stem"]) for row in rules}) == 44, "direction/stem unique")
    source_ids = {row["edge_stem_id"] for row in edge_source} | {row["internal_stem_id"] for row in internal_source} | {"G462-PREFIX-ar"} | {row["bridge_id"] for row in thin_source} | {row["bridge_id"] for row in general_bridges}
    check("function_rule_source_ids", {row["source_rule_id"] for row in rules} == source_ids, f"observed={len({row['source_rule_id'] for row in rules})}")
    check("function_rule_values_present", all(row["component_recipe"] and row["literal_working_value_de"] for row in rules), "no empty recipe or value")

    check("family_rule_count", len(families) == 18, f"observed={len(families)}")
    check("family_rule_ids", [row["family_id"] for row in families] == [f"G466-F{i:02d}" for i in range(1, 19)], "F01-F18")
    check("family_rule_lineage", Counter(row["source_experiment"] for row in families) == Counter({"GDT460": 17, "GDT461": 1}), str(Counter(row["source_experiment"] for row in families)))
    check("family_rule_classes", Counter(row["content_class"] for row in families) == Counter({"STAR_BEARING_RING_POSITION": 14, "DRUG_OR_INGREDIENT_OBJECT": 4}), str(Counter(row["content_class"] for row in families)))
    check("family_rule_cheo", len([row for row in families if row["surface_stem"] == "cheo" and row["working_family_value_de"] == "DROGENFAMILIE"]) == 1, "cheo drug family")
    check("family_rule_unique_keys", len({(row["content_class"], row["surface_stem"]) for row in families}) == 18, "class/stem unique")

    check("correction_count", len(correction) == 1 and correction[0]["surface"] == "ararchodaiin", str(correction))
    corrected = correction[0]
    check("correction_counts", corrected["old_known_function_character_count"] == "7" and corrected["new_known_function_character_count"] == "9", str(corrected))
    check("correction_channel", corrected["accepted_channel"] == "PREFIX ar=AR" and corrected["correction_kind"] == "MISSED_PROPAGATION_OF_ALREADY_ACCEPTED_GDT462_CHANNEL__NO_NEW_MEANING", str(corrected))

    check("dictionary_count", len(labels) == 107, f"observed={len(labels)}")
    check("dictionary_order", [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source], "source order exact")
    check("dictionary_surfaces", [row["surface"] for row in labels] == [row["surface"] for row in source], "surface order exact")
    changed = [row for row in labels if row["gdt466_change"] != "UNCHANGED_FROM_GDT465"]
    check("dictionary_one_change", len(changed) == 1 and changed[0]["surface"] == "ararchodaiin", str([(row["surface"], row["gdt466_change"]) for row in changed]))
    allowed_changed_fields = {"surface_segmentation", "prefix_stem", "prefix_recipe", "known_function_character_count", "remaining_learned_character_count", "known_function_fraction", "ordered_function_recipe_trace", "revised_short_default_de"}
    source_fields = list(source[0])
    check("dictionary_unchanged_source_fields", all(all(row[field] == old[field] for field in source_fields) for row, old in zip(labels, source) if row["surface"] != "ararchodaiin"), "106 rows field-identical")
    check("dictionary_corrected_field_scope", all(row[field] == old[field] for row, old in zip(labels, source) if row["surface"] == "ararchodaiin" for field in source_fields if field not in allowed_changed_fields), "only eight old fields revised")
    ar_label = changed[0]
    check("dictionary_corrected_parse", ar_label["prefix_stem"] == "ar" and ar_label["internal_stem_trace"] == "2:ar=AR" and ar_label["suffix_stem"] == "daiin" and ar_label["ordered_function_recipe_trace"] == "AR+AR+AIIN", str(ar_label))
    check("dictionary_corrected_reading", ar_label["revised_short_default_de"] == "AUSGANG · AUSGANG · [DROGENNAME:cho] · WERT", ar_label["revised_short_default_de"])
    check("dictionary_status_counts", Counter(row["gdt466_hybrid_status"] for row in labels) == Counter({"FULL_FUNCTION_FORMULA": 18, "FUNCTION_SHELL_PLUS_LEARNED_CORE": 87, "OWNER_FAMILY_STEM_ONLY": 1, "WHOLE_LEARNED_LABEL": 1}), str(Counter(row["gdt466_hybrid_status"] for row in labels)))
    check("dictionary_character_totals", sum(int(row["known_function_character_count"]) for row in labels) == 442 and sum(int(row["surface_character_count"]) for row in labels) == 713, "442/713")
    check("dictionary_character_reconciliation", all(int(row["known_function_character_count"]) + int(row["remaining_learned_character_count"]) == len(row["surface"]) == int(row["surface_character_count"]) for row in labels), "all rows reconcile")
    check("dictionary_whole_tail", [row["surface"] for row in labels if row["gdt466_hybrid_status"] == "WHOLE_LEARNED_LABEL"] == ["oiil"], "oiil only")

    check("exact_replay_count", len(exact) == 107, f"observed={len(exact)}")
    check("exact_replay_all_pass", all(row["exact_replay"] == "YES" and row["observed_route"] == "EXACT_KNOWN_LABEL" for row in exact), "107/107")
    check("exact_replay_readings", [row["observed_reading_de"] for row in exact] == [row["revised_short_default_de"] for row in labels], "all revised readings exact")

    check("cold_replay_count", len(cold) == 107, f"observed={len(cold)}")
    check("cold_relation_counts", Counter(row["mask_relation"] for row in cold) == Counter({"EXACT": 105, "UNDER": 2}), str(Counter(row["mask_relation"] for row in cold)))
    under = [row for row in cold if row["mask_relation"] == "UNDER"]
    check("cold_exact_package_only", {row["surface"] for row in under} == {"ykyd", "yddy"} and all(row["cold_disposition"] == "EXACT_PACKAGE_ONLY" for row in under), str([(row["surface"], row["cold_disposition"]) for row in under]))
    check("cold_under_counts", {row["surface"]: int(row["missing_function_character_count"]) for row in under} == {"ykyd": 1, "yddy": 4}, str([(row["surface"], row["missing_function_character_count"]) for row in under]))
    check("cold_no_overread", sum(int(row["extra_function_character_count"]) for row in cold) == 0, "zero extra characters")
    check("cold_totals", sum(int(row["recovered_function_character_count"]) for row in cold) == 437 and sum(int(row["missing_function_character_count"]) for row in cold) == 5, "437 recovered / 5 exact-package-only")
    check("cold_ar_correction_exact", next(row for row in cold if row["surface"] == "ararchodaiin")["mask_relation"] == "EXACT", "propagation closes old overread")

    learned_surfaces = {row["surface"] for row in labels if int(row["remaining_learned_character_count"]) > 0}
    check("core_probe_count", len(core) == 89 and len(learned_surfaces) == 89, f"observed={len(core)}")
    check("core_probe_source_set", {row["source_surface"] for row in core} == learned_surfaces, "every learned-core label once")
    check("core_probe_surfaces_novel", all(row["synthetic_unseen_surface"] not in {label["surface"] for label in labels} for row in core), "all exact identities absent")
    check("core_probe_exact_route_blocked", all(row["exact_known_route_blocked"] == "YES" for row in core), "89/89")
    check("core_probe_masks", all(row["expected_function_mask"] == row["observed_function_mask"] for row in core), "89/89")
    check("core_probe_pass", all(row["probe_pass"] == "YES" for row in core), "89/89")

    check("probe_count", len(probes) == 81, f"observed={len(probes)}")
    check("probe_kind_counts", Counter(row["probe_kind"] for row in probes) == Counter({"FUNCTION_CHANNEL": 44, "OWNER_FAMILY_CORRECT_CLASS": 18, "OWNER_FAMILY_WRONG_CLASS": 18, "WHOLE_NAME_FALLBACK": 1}), str(Counter(row["probe_kind"] for row in probes)))
    check("probe_all_pass", all(row["probe_pass"] == "YES" for row in probes), "81/81")
    function_probes = [row for row in probes if row["probe_kind"] == "FUNCTION_CHANNEL"]
    check("probe_function_coverage", {row["source_rule_id"] for row in function_probes} == {row["channel_id"] for row in rules}, "all 44 rules")
    positive_family = [row for row in probes if row["probe_kind"] == "OWNER_FAMILY_CORRECT_CLASS"]
    negative_family = [row for row in probes if row["probe_kind"] == "OWNER_FAMILY_WRONG_CLASS"]
    check("probe_family_coverage", {row["source_rule_id"] for row in positive_family} == {row["family_id"] for row in families} == {row["source_rule_id"] for row in negative_family}, "all 18 positive and negative")
    fallback = [row for row in probes if row["probe_kind"] == "WHOLE_NAME_FALLBACK"]
    check("probe_fallback", len(fallback) == 1 and fallback[0]["surface"] == "zxqv" and fallback[0]["observed_route"] == "WHOLE_LEARNED_OWNER_NAME", str(fallback))

    check("contract_status", contract["status"] == "FROZEN_MIXED_DICTIONARY_INTAKE_READY", contract["status"])
    check("contract_precedence", [row["order"] for row in contract["precedence"]] == [1, 2, 3, 4] and [row["route"] for row in contract["precedence"]] == ["EXACT_KNOWN_LABEL", "CALIBRATED_FUNCTION_CHANNELS", "STRICT_OWNER_FAMILY", "WHOLE_LEARNED_OWNER_NAME"], str(contract["precedence"]))
    check("contract_counts", contract["known_label_count"] == 107 and contract["function_channel_count"] == 44 and contract["owner_family_channel_count"] == 18 and contract["propagation_correction_count"] == 1, str(contract))
    check("contract_forbidden_outputs", set(contract["forbidden_outputs"]) == {"NEW_COMPONENT_MEANING", "INDIVIDUAL_OBJECT_IDENTITY", "SURFACE_PREDICTION", "CROSS_OWNER_FAMILY_TRANSFER"}, str(contract["forbidden_outputs"]))

    code, payload, error = reader("ararchodaiin", "DRUG_OR_INGREDIENT_OBJECT")
    check("cli_exact_exit", code == 0, error or "exit 0")
    check("cli_exact_correction", payload.get("route") == "EXACT_KNOWN_LABEL" and payload.get("known_function_character_count") == 9 and payload.get("reading_de") == "AUSGANG · AUSGANG · [DROGENNAME:cho] · WERT", str(payload))
    code, payload, error = reader("otxainy", "STAR_BEARING_RING_POSITION")
    check("cli_unknown_shell_exit", code == 0, error or "exit 0")
    check("cli_unknown_shell", payload.get("known_label") == "NO" and payload.get("route") == "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE" and payload.get("known_function_character_count") == 6 and payload.get("reading_de") == "DANACH · [STERNSTELLENNAME:x] · ANTEIL · POSTEN", str(payload))
    code, payload, error = reader("zxqv", "PICTURED_PLANT")
    check("cli_fallback_exit", code == 0, error or "exit 0")
    check("cli_fallback", payload.get("route") == "WHOLE_LEARNED_OWNER_NAME" and payload.get("reading_de") == "[PFLANZENNAME:zxqv]", str(payload))

    check("result_status", result["status"] == "FROZEN_MIXED_DICTIONARY_INTAKE_READY", result["status"])
    check("result_counts", result["known_label_count"] == 107 and result["function_channel_count"] == 44 and result["owner_family_channel_count"] == 18 and result["propagation_correction_count"] == 1, str(result))
    check("result_exact_and_cold", result["exact_label_replay_pass_count"] == 107 and result["cold_shell_mask_relations"] == {"EXACT": 105, "UNDER": 2} and result["cold_recovered_function_character_count"] == 437 and result["cold_missing_function_character_count"] == 5 and result["cold_extra_function_character_count"] == 0, str(result))
    check("result_dictionary_totals", result["revised_known_function_character_count"] == 442 and result["surface_character_count"] == 713, "442/713")
    check("result_probe_counts", result["unseen_core_insertion_probe_count"] == result["unseen_core_insertion_pass_count"] == 89 and result["channel_and_fallback_probe_count"] == result["channel_and_fallback_pass_count"] == 81, str(result))
    check("result_claim_ceiling", result["new_pages"] == result["new_component_meanings"] == result["surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")
    check("sealed_pages_absent", all(not row.get("physical_page", "").startswith("f84") for table in (source, labels, correction) for row in table), "no sealed page rows")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {"status": "PASS" if failed == 0 else "FAIL", "check_count": len(checks), "passed": passed, "failed": failed, "checks": checks}
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
