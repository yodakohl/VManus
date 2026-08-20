#!/usr/bin/env python3
"""Static, non-executing validation of the frozen GDT395 decoder panel."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
FREEZE = EXP / "artifacts/gdt395_decoder_panel_freeze.json"
OUT = EXP / "artifacts/gdt395_decoder_panel_validation.json"
REPS = {"FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS", "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY"}
LOCAL_IMPORTS = {"src.decoder_api"}


def assignment(tree: ast.Module, name: str):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError(f"missing {name}")


def main() -> None:
    data = json.loads(FREEZE.read_text())
    checks = {}
    checks["five_decoders"] = len(data["decoders"]) == 5
    checks["bindings"] = all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest for path, digest in data["bindings"].items())
    ids = []
    models = []
    source_ok = api_ok = imports_ok = no_io = attest_ok = True
    forbidden_calls = {"open", "eval", "exec", "compile", "__import__"}
    for row in data["decoders"]:
        directory = ROOT / row["directory"]
        source = directory / "decoder.py"
        attestation = directory / "ATTESTATION.md"
        source_ok &= hashlib.sha256(source.read_bytes()).hexdigest() == row["source_sha256"]
        source_ok &= hashlib.sha256(attestation.read_bytes()).hexdigest() == row["attestation_sha256"]
        tree = ast.parse(source.read_text())
        meta = assignment(tree, "DECODER_META")
        ids.append(meta["decoder_id"])
        models.append(str(meta["designer_model"]).lower())
        api_ok &= meta == row["meta"] and meta["oracle_blind"] is True and set(meta["supported_representations"]) == REPS
        functions = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        api_ok &= "decode" in functions and "classify_world" in functions
        if "decode" in functions:
            api_ok &= [arg.arg for arg in functions["decode"].args.args] == ["train_rows", "held_rows", "representation"]
        if "classify_world" in functions:
            api_ok &= [arg.arg for arg in functions["classify_world"].args.args] == ["train_rows"]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports_ok &= all(alias.name.split(".")[0] in sys.stdlib_module_names for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports_ok &= module in LOCAL_IMPORTS or module.split(".")[0] in sys.stdlib_module_names
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                no_io &= node.func.id not in forbidden_calls
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                no_io &= node.func.attr not in {"read_text", "read_bytes", "write_text", "write_bytes", "open"}
        words = " ".join(attestation.read_text().lower().split())
        no_execution = any(term in words for term in (
            "not execute", "not been run", "did not execute", "no execution",
            "no decoder import or function execution", "has not executed",
        ))
        attest_ok &= all(term in words for term in ("oracle", "voynich", "f84")) and no_execution
    checks["source_hashes"] = source_ok
    checks["api_exact"] = api_ok
    checks["unique_ids"] = len(ids) == len(set(ids)) == 5
    checks["model_mix"] = (
        models.count("gpt-5.6-sol") == 1
        and models.count("openai codex (sol)") == 1
        and models.count("gpt-5.6-luna") == 3
    )
    checks["stdlib_only"] = imports_ok
    checks["no_file_or_dynamic_io"] = no_io
    checks["attestations"] = attest_ok
    checks["pre_execution"] = (
        data["decoder_claims_generated"] == 0
        and not data["oracle_scoring_performed"]
        and all(not row["executed_before_freeze"] for row in data["decoders"])
        and data["pre_execution_evidence"] == {
            "claim_root_file_count": 0,
            "freeze_output_absent_on_entry": True,
            "one_shot_overwrite_guard": True,
        }
    )
    checks["seal"] = data["voynich_rows"] == 0 and not any(data["f84"].values())
    tmp = dict(data)
    expected = tmp.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected
    result = {
        "schema": "GDT395_DECODER_PANEL_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"})
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
