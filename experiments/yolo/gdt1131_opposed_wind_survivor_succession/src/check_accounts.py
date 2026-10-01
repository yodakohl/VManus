#!/usr/bin/env python3
"""GDT1131 bounded preservation/declaration checks; no semantic execution.

--source-only reads no author content. Final checks require --release PATH,
a root-authored JSON mapping A/B/C to account/constructor {path,sha256} pins
and optional initial_receipt/final_receipt paths. Paths may be experiment-relative
or repository-relative within this experiment. Partial/UNKNOWN accounts may
pass preservation validation.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
SOURCE_PIN = "d228057d52a97287f071b336a09dbaf9782f20c1ccde201df99c24f269e45a68"
LICENSED_AN_FORMS = {"aiin", "daiin", "shodaiin"}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(path):
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Artifact path must remain within this experiment")
    experiment_parts = D.relative_to(ROOT).parts
    if candidate.parts[:len(experiment_parts)] == experiment_parts:
        result = ROOT / candidate
    elif candidate.parts and candidate.parts[0] == "experiments":
        raise ValueError("Repository-relative artifact belongs to another experiment")
    else:
        result = D / candidate
    if not result.resolve().is_relative_to(D.resolve()):
        raise ValueError("Artifact path resolves outside this experiment")
    return result


class Audit:
    def __init__(self):
        self.checks, self.manual = [], []

    def check(self, name, passed, details=None):
        self.checks.append({"check": name, "status": "PASS" if passed else "FAIL", "details": details})

    def unverified(self, name, details):
        self.manual.append({"check": name, "status": "MANUAL_REVIEW", "details": details})


def source_checks(audit):
    plan, source = read(D / "src/AUTHOR_PLAN.json"), read(D / "src/SOURCE.json")
    rows, fields = source["rows"], plan["columns"]
    audit.check("owned_source_pin", sha(D / "src/SOURCE.json") == SOURCE_PIN)
    audit.check("registered_input_pins", all(sha(ROOT/p["path"]) == p["sha256"] for p in plan["source_inputs"]))
    receipt = read(D / "src/HISTORICAL_RECEIPT.json")
    historical = D / "src/HISTORICAL_PRIMARY.html"
    audit.check("historical_primary_bytes_receipt", sha(historical) == receipt["sha256"] and historical.stat().st_size == receipt["bytes"])
    ids = [r["source_group_id"] for r in rows]
    audit.check("source_473_unique_native_IDs", len(ids) == len(set(ids)) == 473)
    audit.check("all12_native_fields", len(fields) == 12 and all(set(r) == set(fields) for r in rows))
    audit.check("source_reader_counts", dict(Counter(r["edition"] for r in rows)) == plan["raw_counts"])
    audit.check("source_scope_and_zero_confirmation", {r["locus"] for r in rows} == set(plan["scope_loci"]) and
                source["independent_confirmation_leaves"] == plan["independent_confirmation_leaves"] == [])
    for block, indices, count in (("N", range(2,7), 19), ("E", range(7,12), 27)):
        audit.check("primary_" + block + "_native_scope", all(
            {r["locus"] for r in rows if r["edition"] == reader and r["block"] == block} == {f"f85r2.{i}" for i in indices} and
            sum(r["edition"] == reader and r["block"] == block for r in rows) == count
            for reader in plan["raw_counts"]))
    return plan, source


def receipt_check(audit, author, path):
    receipt = read(local(path))
    files = receipt.get("files", receipt.get("hashes", {}))
    if not files:
        audit.unverified(author + ":receipt_schema", "No files/hash map; adapt final receipt fields explicitly.")
        return
    audit.check(author + ":receipt_file_pins:" + path, all(sha(local(p)) == digest for p,digest in files.items()))


def account_checks(audit, author, account, freeze, source, constructor_pin):
    """Technical shared schema; root may coordinate a small final adapter."""
    expected = {r["source_group_id"]: r for r in source["rows"]}
    fields = list(source["rows"][0])
    rows = account.get("rows", account.get("group_ledger", []))
    native = [r.get("native", r.get("source", r.get("source_raw", r))) for r in rows]
    ids = [n.get("source_group_id") for n in native]
    audit.check(author + ":exact_473_native_IDs", len(ids) == len(set(ids)) == 473 and set(ids) == set(expected))
    wrong = [{"id": n.get("source_group_id"), "field": key} for n in native
             for key in fields if n.get("source_group_id") in expected and n.get(key) != expected[n["source_group_id"]][key]]
    audit.check(author + ":all12_native_values_unchanged", not wrong, wrong)
    audit.check(author + ":source_pin", account.get("source_sha256") == SOURCE_PIN)
    audit.check(author + ":constructor_pin", account.get("constructor_sha256") == constructor_pin)
    families = freeze.get("constructors", freeze.get("core_families", freeze.get("families", [])))
    constants = freeze.get("opaque_constants", freeze.get("opaque_content_constants", []))
    audit.check(author + ":initial_core_limits", 0 < len(families) <= 12 and len(constants) <= 8,
                {"constructor_families": len(families), "opaque_constants": len(constants)})
    dictionary = account.get("dictionary", account.get("full_dictionary", []))
    if isinstance(dictionary, dict):
        dictionary = [{"raw_form": raw, **value} for raw,value in dictionary.items()]
    forms = [e.get("raw_form", e.get("raw")) for e in dictionary]
    lookup = dict(zip(forms, dictionary))
    audit.check(author + ":dictionary_forms_unique_and_source_owned", len(forms) == len(set(forms)) and
                set(forms) <= {r["ivtff_group_raw"] for r in source["rows"]})
    repeat_errors, missing_identity = [], []
    for row, n in zip(rows, native):
        raw = n.get("ivtff_group_raw")
        if raw not in lookup:
            continue
        entry = lookup[raw]
        if "entry_id" in entry:
            if row.get("entry_id") != entry["entry_id"]:
                repeat_errors.append(n["source_group_id"])
        elif "frozen_dictionary_entry" in row:
            if row["frozen_dictionary_entry"] != {k:v for k,v in entry.items() if k != "raw_form"}:
                repeat_errors.append(n["source_group_id"])
        else:
            missing_identity.append(n["source_group_id"])
    audit.check(author + ":assigned_whole_repeat_entry_identity", not repeat_errors, repeat_errors)
    if missing_identity:
        audit.unverified(author + ":row_entry_identity_schema", {"rows": len(missing_identity), "note": "Schema-specific declared rule/value mapping needs adapter; no semantic identity certification."})
    recurrence = {e["raw_form"]: e for e in account.get("recurrence_audit", [])}
    for entry in dictionary:
        raw = entry.get("raw_form", entry.get("raw"))
        occurrences = entry.get("occurrences", entry.get("source_ids", recurrence.get(raw, {}).get("exact_positions")))
        if occurrences is not None:
            audit.check(author + ":exact_occurrences:" + raw,
                        len(occurrences) == len(set(occurrences)) and
                        set(occurrences) == {r["source_group_id"] for r in source["rows"] if r["ivtff_group_raw"] == raw})
        else:
            audit.unverified(author + ":exact_occurrence_inventory:" + raw, "Assigned occurrence list not declared; row entry identity is checked separately.")
    badrefs = []
    for row, n in zip(rows, native):
        for ref in row.get("consumer_source_ids", row.get("later_consumption_source_ids", [])):
            if ref not in expected:
                badrefs.append({"id": n.get("source_group_id"), "reference": ref})
    audit.check(author + ":consumer_source_references_exist", not badrefs, badrefs)
    objects = account.get("objects", {})
    argument_edges, argument_errors = set(), []
    for row,n in zip(rows,native):
        for argument in row.get("arguments", []):
            if isinstance(argument, str):
                obj = objects.get(argument)
                if obj is None:
                    argument_errors.append({"id": n["source_group_id"], "object": argument})
                    continue
                refs = [obj.get("producer_source_id", obj.get("producer"))]
            else:
                refs = argument.get("producer_source_ids", [])
            for ref in refs:
                if ref not in expected:
                    argument_errors.append({"id": n["source_group_id"], "producer": ref})
                else:
                    argument_edges.add((ref,n["source_group_id"]))
    audit.check(author + ":argument_producer_source_references_exist", not argument_errors, argument_errors)
    unmatched = [{"id": n["source_group_id"], "consumer": ref} for row,n in zip(rows,native)
                 for ref in row.get("consumer_source_ids", []) if (n["source_group_id"],ref) not in argument_edges]
    audit.check(author + ":consumers_have_recorded_argument_edges", not unmatched, unmatched)
    audit.check(author + ":row_status_explicit", all(isinstance(r.get("status"), str) and r["status"] for r in rows), dict(Counter(r.get("status") for r in rows)))
    units = account.get("primary_units", [])
    if not units:
        audit.unverified(author + ":primary_unit_schema", "N/E declaration adapter required; coverage alone is not primary completion.")
    for unit in units:
        reader, block = unit.get("edition", unit.get("reader")), unit["block"]
        selected = {sid for sid,n in expected.items() if n["edition"] == reader and n["block"] == block}
        unit_ids = unit.get("source_ids", unit.get("source_group_ids", unit.get("native_ids", [])))
        audit.check(author + ":primary_unit_IDs:" + reader + ":" + block, block in ("N", "E") and
                    len(unit_ids) == len(set(unit_ids)) and set(unit_ids) == selected)
        declared_count = unit.get("native_count", unit.get("count"))
        audit.check(author + ":primary_unit_count:" + reader + ":" + block, declared_count == len(selected))
    uses = account.get("shared_part_uses", [])
    supported = set()
    by_id = {n["source_group_id"]: r for r,n in zip(rows,native)}
    shared_reference_errors = []
    for use in uses:
        sid = use["source_group_id"]
        raw = expected.get(sid, {}).get("ivtff_group_raw")
        valid = use.get("raw_form") == raw and sid in expected
        audit.check(author + ":shared_part_source_literal:" + sid, valid)
        blocked = any(word in use.get("status", "").upper() for word in ("BLOCKED", "UNKNOWN"))
        if valid and raw in LICENSED_AN_FORMS and not blocked:
            supported.add(raw)
        audit.check(author + ":shared_part_reference_fields:" + sid,
                    bool(use.get("interface_id")) and bool(use.get("effect")) and
                    all(ref in expected for ref in use.get("consumer_source_ids", [])) and
                    (blocked or bool(use.get("arguments")) and use.get("returned_value") is not None),
                    {"status": use.get("status"), "execution_claimed": not blocked})
        if raw not in LICENSED_AN_FORMS:
            audit.unverified(author + ":additional_shared_form_license:" + sid,
                             {"raw_form": raw, "note": "Source literal checked; extra exact-form license/effect is not certified by the required three-form interface."})
        if not blocked and sid in by_id:
            returned = use.get("returned_value")
            returned_id = returned if isinstance(returned,str) else returned.get("id") if isinstance(returned,dict) else None
            row_return_ids = {value if isinstance(value,str) else value.get("id") for value in by_id[sid].get("returns", [])}
            if returned_id not in row_return_ids:
                shared_reference_errors.append({"id": sid, "returned_ID_not_in_row": returned_id})
            for ref in use.get("consumer_source_ids", []):
                if (sid,ref) not in argument_edges:
                    shared_reference_errors.append({"id": sid, "consumer_without_recorded_argument_edge": ref})
            for argument in use.get("arguments", []):
                if isinstance(argument,str):
                    if argument not in objects:
                        shared_reference_errors.append({"id": sid, "missing_argument_object": argument})
                elif any(ref not in expected for ref in argument.get("producer_source_ids", [])):
                    shared_reference_errors.append({"id": sid, "unknown_argument_producer": True})
    audit.check(author + ":executed_shared_use_return_and_source_references", not shared_reference_errors, shared_reference_errors)
    audit.unverified(author + ":shared_part_actual_effect", {"declared_supported_forms": sorted(supported),
                "at_least_two_forms_declared": len(supported) >= 2, "note": "Missing use leaves construction obligation unmet; preservation can still PASS. Actual semantic license, argument type and non-null effect require manual review."})
    costs = account.get("costs", {})
    if "dictionary_entries" in costs:
        audit.check(author + ":dictionary_cost_count", costs["dictionary_entries"] == len(dictionary))
    declared_cost_checks(audit, author, account, freeze, dictionary)
    audit.unverified(author + ":semantic_and_cost_review", {"author_status": account.get("status"),
        "note": "Inspect constants, aliases/defaults, unknown carry, added rules, unused instructions, actual consumers and owner/time/cause identity. No semantic or whole-completion certification."})


def declared_cost_checks(audit, author, account, freeze, dictionary):
    costs, rows = account["costs"], account["rows"]
    if author == "A":
        audit.check("A:declared_cost_counts", costs["assigned_exact_wholes"] == len(dictionary) and
                    costs["unassigned_exact_wholes"] == len(account["unassigned_dictionary"]) and
                    costs["constructor_template_components"] == sum(e["cost"]["constructor_components"] for e in dictionary) and
                    costs["exact_aliases_beyond_first_identical_rule"] == len(dictionary)-len({e["rule"] for e in dictionary}) and
                    costs["initial_core_families"] == len(freeze["constructors"]) and
                    costs["initial_opaque_constants"] == len(freeze["opaque_constants"]))
        audit.check("A:declared_unknown_carry_counts", costs["unknown_carry_rows"] == sum(bool(r["unknown_carry_source_ids"]) for r in rows) and
                    costs["unknown_carry_uses"] == sum(len(r["unknown_carry_source_ids"]) for r in rows))
        audit.check("A:unused_auxiliary_IDs_exist", all(oid in account["objects"] for oid in costs["unconsumed_auxiliary_outputs"]))
    elif author == "B":
        extensions = read(D/"src/B_EXTENSIONS.json")
        audit.check("B:extension_and_core_dictionary_pins", sha(D/"src/B_EXTENSIONS.json") == account["extension_sha256"] and
                    account["dictionary"] == extensions["dictionary"] and
                    all(account["dictionary"].get(raw) == entry for raw,entry in freeze["core_dictionary"].items()))
        added = [e for e in dictionary if e["raw_form"] not in freeze["core_dictionary"]]
        audit.check("B:declared_cost_counts", costs["total_assigned_exact_forms"] == len(dictionary) and
                    costs["added_exact_forms"] == len(added) and costs["initial"]["core_exact_forms"] == len(freeze["core_dictionary"]) and
                    costs["core_families"] == len(freeze["core_families"]) and
                    costs["initial_opaque_constants"] == len(freeze["opaque_constants"]))
        audit.check("B:each_added_whole_priced", all(e.get("price") for e in added))
        allowed = {family["id"] for family in freeze["core_families"]}
        audit.check("B:dictionary_and_substep_family_references", all(e["family"] in allowed and all(op["family"] in allowed for op in e.get("operations", [])) for e in dictionary) and
                    all(step["family"] in allowed for r in rows for step in r["substeps"]))
        audit.check("B:unknown_bridge_count_lists", all(e["count"] == len(e["intervening_unknown_ids"]) for e in costs["known_entry_unknown_bridge_row_counts"]))
    else:
        audit.check("C:declared_cost_counts", costs["initial_constructor_families"] == len(freeze["families"]) and
                    costs["initial_opaque_constants"] == len(freeze["opaque_constants"]) and
                    costs["initial_exact_entries"] == len(freeze["initial_exact_entries"]) and
                    costs["extension_exact_entries"] == sum(e["extension"] for e in dictionary) and
                    costs["whole_residual_payloads"] == sum(e["whole_residual_cost"] for e in dictionary) and
                    costs["additional_payload_or_rule_items"] == sum(len(e["additional_costs"]) for e in dictionary))
        allowed = {family["id"] for family in freeze["families"]}
        audit.check("C:dictionary_family_references", all(family in allowed for e in dictionary for family in e["families"]))
        audit.check("C:unknown_carry_count_ledger", costs["unknown_carry_row_edge_count"] == sum(r["cost"].get("unknown_carry_rows", 0) for r in rows) and
                    costs["unknown_carry_occurrence_rows"] == sum(bool(r["cost"].get("unknown_carry_rows")) for r in rows))


def replay(audit, author, pins):
    """Execute only frozen author sources in an isolated copy; never repair them."""
    receipt = read(local(pins["final_receipt"]))
    originals = {path:sha(local(path)) for path in receipt["files"]}
    with tempfile.TemporaryDirectory(prefix="gdt1131_replay_") as directory:
        temporary = Path(directory)
        names = ["src/SOURCE.json", "src/STRUCTURAL_PRIORS.json"]
        names += [str(path.relative_to(D)) for path in (D/"src").glob(author + "_*") if path.is_file()]
        names += [pins["initial_receipt"]]
        for name in names:
            original = local(name)
            target = temporary / original.relative_to(D)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original,target)
        (temporary/"artifacts").mkdir(exist_ok=True)
        programs = [author + "_MATERIALIZE.py"] + (["B_WRITE_READING.py"] if author == "B" else [])
        returns = []
        for program in programs:
            completed = subprocess.run([sys.executable,str(temporary/"src"/program)], capture_output=True, timeout=30)
            returns.append(completed.returncode)
        audit.check(author + ":temporary_replay_programs_complete", all(code == 0 for code in returns), {"return_codes": returns})
        account_name = str(local(pins["account"]["path"]).relative_to(D))
        generated = temporary/account_name
        byte_match = generated.exists() and sha(generated) == pins["account"]["sha256"]
        details = {"semantic_validation": False}
        if generated.exists() and author == "A":
            previous, current = read(local(account_name)), read(generated)
            differing = sorted(key for key in set(previous)|set(current) if previous.get(key) != current.get(key))
            details["differing_top_fields"] = differing
            audit.check("A:replay_payload_except_runtime_freeze_utc", {k:v for k,v in previous.items() if k != "freeze_utc"} ==
                        {k:v for k,v in current.items() if k != "freeze_utc"},
                        {"excluded_field": "freeze_utc", "exact_byte_result_retained_separately": True})
        audit.check(author + ":replay_account_exact_bytes", byte_match, details)
        for name in (f"artifacts/{author}_READING.md", f"artifacts/{author}_CHECK.json"):
            if (temporary/name).exists() and (D/name).exists():
                audit.check(author + ":replay_exact_bytes:" + name, sha(temporary/name) == sha(D/name))
    audit.check(author + ":original_final_files_unchanged_by_replay", all(sha(local(path)) == digest for path,digest in originals.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--release", help="root-authored A/B/C final artifact/hash map")
    args = parser.parse_args()
    audit = Audit()
    plan, source = source_checks(audit)
    if not args.source_only:
        if not args.release:
            parser.error("Read author accounts only after root releases all A/B/C hashes.")
        release = read(local(args.release))
        if set(release) != set(plan["candidate_ids"]):
            parser.error("Release must contain all A/B/C, not a draft subset.")
        for author,pins in release.items():
            # Verify the release before opening author content.
            for kind in ("account", "constructor"):
                if sha(local(pins[kind]["path"])) != pins[kind]["sha256"]:
                    raise ValueError(author + " released " + kind + " hash mismatch")
            account_checks(audit, author, read(local(pins["account"]["path"])),
                           read(local(pins["constructor"]["path"])), source, pins["constructor"]["sha256"])
            for kind in ("initial_receipt", "final_receipt"):
                if kind in pins:
                    receipt_check(audit, author, pins[kind])
            replay(audit,author,pins)
            audit.check(author + ":released_account_and_freeze_unchanged", all(
                sha(local(pins[kind]["path"])) == pins[kind]["sha256"] for kind in ("account", "constructor")))
    audit.check("owned_source_unchanged_after_checks", sha(D / "src/SOURCE.json") == SOURCE_PIN)
    failures = sum(c["status"] == "FAIL" for c in audit.checks)
    result = {"schema": "GDT1131_ACCOUNTING_ONLY_v1", "status": "FAIL_ACCOUNTING" if failures else "PASS_ACCOUNTING_ONLY_MANUAL_REVIEW_REQUIRED",
              "source_sha256": SOURCE_PIN, "source_only": args.source_only,
              "checks": audit.checks, "manual_review": audit.manual, "semantic_validation": False,
              "claim_ceiling": "Native source/declaration preservation only; partial and UNKNOWN rows do not fail coverage, but do not satisfy whole semantic construction."}
    if not args.source_only:
        result["root_release"] = release
        result["candidate_summaries"] = {}
        for author,pins in release.items():
            account = read(local(pins["account"]["path"]))
            costs = account["costs"]
            result["candidate_summaries"][author] = {
                "author_status": account["status"],
                "row_status_counts": dict(Counter(row["status"] for row in account["rows"])),
                "dictionary_entries": len(account["dictionary"]),
                "primary_units": [{"reader": unit.get("edition",unit.get("reader")), "block": unit["block"],
                    "author_complete": unit["complete"], "operational_complete": unit.get("operational_complete"),
                    "author_status": unit["status"]} for unit in account["primary_units"]],
                "unused_cost_labels": {key: len(costs[key]) for key in ("unconsumed_auxiliary_outputs", "unused_reference_outputs", "unused_retained_reference_values", "unused_instructions") if key in costs},
                "unused_label_definitions_comparable": False,
                "semantic_validation": False}
        (D / "artifacts/AUTHOR_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
        failed = [c for c in audit.checks if c["status"] == "FAIL"]
        report = "# GDT1131 preservation and reproducibility audit\n\n" + result["status"] + f"; {len(audit.checks)} checks, {failures} failures.\n\n"
        report += "This validates source coverage, literal recurrences, declared reference edges, initial budgets, count ledgers and frozen-file reproducibility. It does not validate meanings, participant identity, causal/time truth or complete narrative construction. Partial/UNKNOWN status is preserved.\n\n"
        if failed:
            report += "Retained failures:\n\n" + "\n".join("- `" + c["check"] + "`: " + json.dumps(c["details"]) for c in failed) + "\n\n"
        report += "Every candidate must conserve473 rows and all12 native fields. Each assigned exact whole is checked against all literal occurrences, including outside N/E. Consumer IDs are checked against recorded argument-producer source edges; this is reference accounting, not proof of effective semantics. Shared-part declarations and blocked attempts remain distinct; additional exact forms have no automatically certified license.\n\n"
        report += "A/B/C costs and unused-output labels use author-specific definitions; no calibrated complexity ranking or cross-author equivalence is implied. Root must inspect semantic atomicity, hidden defaults/ambient premises, unknown carry, unused auxiliary/ref/instruction distinctions, and actual non-null effects. B's operational E coverage does not establish strict completeness. A/C complete claims remain author hypotheses.\n\n"
        report += "All author replays run in temporary copies. Original freezes/accounts/receipts and the raw historical HTML remain byte-preserved. A's runtime timestamp is tested separately from its payload; any exact-byte failure stays recorded. Zero meanings or independent confirmation are certified. See AUTHOR_VALIDATION.json for pins, all checks and manual-review items.\n"
        (D / "artifacts/AUTHOR_VALIDATION.md").write_text(report)
    print(json.dumps({"status": result["status"], "source_only": args.source_only, "checks": len(audit.checks), "failures": failures}))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
