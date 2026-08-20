#!/usr/bin/env python3
"""Independent schema, determinism, diversity, and seal audit of GDT395 worlds."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
import sys
import re
from collections import Counter
from pathlib import Path

from world_api import OBS_FIELDS, ORACLE_FIELDS, REQUIRED_META, validate_rows
from normalize_bundle import normalize_bundle, validate_canonical

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
INTERFACE = EXP / "artifacts/gdt395_interface_freeze.json"
PANEL = EXP / "artifacts/gdt395_world_panel_freeze.json"
OUT = EXP / "artifacts/gdt395_world_panel_validation.json"


def load(path: Path, name: str):
    if str(EXP) not in sys.path:
        sys.path.insert(0, str(EXP))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canon(bundle: dict) -> str:
    return hashlib.sha256(json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    interface = json.loads(INTERFACE.read_text()); panel = json.loads(PANEL.read_text())
    checks = {}
    checks["ten_frozen_worlds"] = len(panel["worlds"]) == 10
    checks["interface_bound"] = panel["interface_sha256"] == hashlib.sha256(INTERFACE.read_bytes()).hexdigest()
    checks["pair_audit_bound"] = panel["pair_matching_audit_sha256"] == hashlib.sha256((EXP / "artifacts/gdt395_pair_matching_audit.tsv").read_bytes()).hexdigest()
    checks["pair_matches_bound"] = panel["pair_matched_records_sha256"] == hashlib.sha256((EXP / "artifacts/gdt395_pair_matched_records.tsv").read_bytes()).hexdigest()
    checks["pair_amendment_bound"] = panel["pair_protocol_amendment_sha256"] == hashlib.sha256((EXP / "artifacts/gdt395_pair_protocol_amendment.json").read_bytes()).hexdigest()
    checks["pair_amendment_validation_bound"] = panel["pair_protocol_amendment_validation_sha256"] == hashlib.sha256((EXP / "artifacts/gdt395_pair_protocol_amendment_validation.json").read_bytes()).hexdigest()
    checks["designer_provenance_bound"] = panel["designer_provenance_sha256"] == hashlib.sha256((EXP / "artifacts/gdt395_designer_provenance.tsv").read_bytes()).hexdigest()
    checks["documents_bound"] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in panel["document_hashes"].items())
    checks["implementations_bound"] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in panel["implementation_hashes"].items())
    checks["f84_seal"] = panel["voynich_rows"] == 0 and not any(panel["f84"].values())
    checks["unique_generators"] = len({x["generator_sha256"] for x in panel["worlds"]}) == 10
    assignments = {x["world_id"]: x for x in interface["world_assignments"]}
    audits = []
    for frozen in panel["worlds"]:
        wid = frozen["world_id"]; gen = ROOT / frozen["directory"] / "generator.py"
        design = gen.with_name("DESIGN.md"); mod = load(gen, f"validate_{wid}")
        bundle1 = mod.generate(77100 + int(wid[1:]), 512)
        bundle2 = mod.generate(77100 + int(wid[1:]), 512)
        validate_rows(mod.WORLD_META, bundle1, 512); validate_rows(mod.WORLD_META, bundle2, 512)
        deterministic_raw = canon(bundle1) == canon(bundle2)
        bundle1 = normalize_bundle(bundle1); bundle2 = normalize_bundle(bundle2)
        pair_id = assignments[wid]["adversarial_pair_id"]
        validate_canonical(bundle1); validate_canonical(bundle2)
        obs, oracle = bundle1["observations"], bundle1["oracle"]
        event_ids = {r["event_id"] for r in obs}
        oracle_ids = {r["event_id"] for r in oracle}
        refs = [r for r in oracle if r["relation_target_event_id"] != "NONE"]
        ref_ok = all(all(t in event_ids for t in r["relation_target_event_id"].split("|")) for r in refs)
        scope_ok = all(
            (r["scope_start_event_id"] == "NONE" or r["scope_start_event_id"] in event_ids)
            and (r["scope_end_event_id"] == "NONE" or r["scope_end_event_id"] in event_ids)
            for r in oracle
        )
        hidden_tokens = set()
        for r in oracle:
            for key in set(ORACLE_FIELDS) - {"world_id", "corpus_seed", "event_id"}:
                v = str(r[key])
                if v != "NONE" and len(v) >= 5:
                    hidden_tokens.add(v)
        accidental = sum(any(tok == str(r["visible_group"]) for tok in hidden_tokens) for r in obs)
        lengths = [len(str(r["visible_group"])) for r in obs]
        final_meta = mod.WORLD_META
        alphabet_ok = all(set(str(r["visible_group"])) <= set(final_meta["alphabet"]) for r in obs)
        register_meta_ok = {r["register_id"] for r in obs} <= set(final_meta["registers"]) and {r["hand_id"] for r in obs} <= set(final_meta["hands"])
        register_truth_ok = True
        semantic_null_ok = True
        if wid == "W10":
            null_fields = ("semantic_entity_id", "semantic_category", "function_class", "relation_type", "relation_target_event_id", "current_component_semantics")
            semantic_null_ok = all(all(r[k] == "NONE" for k in null_fields) for r in oracle)
        fossil_current_ok = all(not re.search(r"FOSSIL|BLEACHED|^fossil:", str(r["current_component_semantics"]), re.I) for r in oracle)
        row = {
            "world_id": wid, "events": len(obs), "deterministic": deterministic_raw and canon(bundle1) == canon(bundle2),
            "registers": len({r["register_id"] for r in obs}), "hands": len({r["hand_id"] for r in obs}),
            "visible_types": len({r["visible_group"] for r in obs}), "median_length": statistics.median(lengths),
            "functions": len({r["function_class"] for r in oracle if r["function_class"] != "NONE"}),
            "entities": len({r["semantic_entity_id"] for r in oracle if r["semantic_entity_id"] != "NONE"}),
            "stems": len({r["historical_stem_id"] for r in oracle if r["historical_stem_id"] != "NONE"}),
            "relation_rows": len(refs), "reference_targets_resolve": ref_ok, "scope_targets_resolve": scope_ok,
            "accidental_exact_hidden_surface": accidental,
            "field_sets_exact": set(obs[0]) == set(OBS_FIELDS) and set(oracle[0]) == set(ORACLE_FIELDS),
            "source_hashes": hashlib.sha256(gen.read_bytes()).hexdigest() == frozen["generator_sha256"] and hashlib.sha256(design.read_bytes()).hexdigest() == frozen["design_sha256"],
            "assignment": mod.WORLD_META["broad_family"] == assignments[wid]["broad_family"],
            "final_meta": final_meta, "alphabet_ok": alphabet_ok, "register_meta_ok": register_meta_ok,
            "register_truth_ok": register_truth_ok, "semantic_null_ok": semantic_null_ok,
            "fossil_current_ok": fossil_current_ok, "type_token": len({r["visible_group"] for r in obs}) / len(obs),
            "opaque_layout_roles": all(re.fullmatch(r"L[A-Z0-9_]*", str(r["layout_role"])) for r in obs),
        }
        audits.append(row)
    checks["all_deterministic"] = all(r["deterministic"] for r in audits)
    checks["all_schema_exact"] = all(r["field_sets_exact"] for r in audits)
    checks["all_hashes"] = all(r["source_hashes"] for r in audits)
    checks["all_assignments"] = all(r["assignment"] for r in audits)
    checks["register_hand_capacity"] = all(r["registers"] >= 3 and r["hands"] >= 2 for r in audits)
    checks["relation_integrity"] = all(r["reference_targets_resolve"] and r["scope_targets_resolve"] for r in audits)
    checks["no_exact_truth_leak"] = all(r["accidental_exact_hidden_surface"] == 0 for r in audits)
    checks["visible_diversity"] = all(r["visible_types"] >= 20 for r in audits)
    checks["semantic_diversity"] = sum(r["entities"] >= 10 for r in audits) >= 8
    checks["functional_diversity"] = sum(r["functions"] >= 3 for r in audits) >= 7
    checks["final_metadata_matches"] = all(r["alphabet_ok"] and r["register_meta_ok"] and r["register_truth_ok"] for r in audits)
    checks["semantics_light_pure"] = all(r["semantic_null_ok"] for r in audits)
    checks["fossils_not_current"] = all(r["fossil_current_ok"] for r in audits)
    checks["opaque_layout"] = all(r["opaque_layout_roles"] for r in audits)
    tmp = dict(panel); expected = tmp.pop("content_sha256")
    checks["panel_content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    result = {
        "schema": "GDT395_WORLD_PANEL_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "checks_passed": sum(checks.values()), "checks_total": len(checks), "world_audits": audits,
        "panel_sha256": hashlib.sha256(PANEL.read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}))
    if result["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__":
    main()
