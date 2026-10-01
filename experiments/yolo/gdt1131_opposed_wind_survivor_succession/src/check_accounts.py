#!/usr/bin/env python3
"""GDT1131 bounded preservation/declaration checks; no semantic execution.

--source-only reads no author content. Final checks require --release PATH,
a root-authored JSON mapping A/B/C to account/constructor {path,sha256} pins
and optional initial_receipt/final_receipt paths. All paths are relative to
this experiment. Partial/UNKNOWN accounts may pass preservation validation.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

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
        raise ValueError("Artifact path must be experiment-relative")
    return D / candidate


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
    families = freeze.get("constructors", freeze.get("core_families", []))
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
    for entry in dictionary:
        occurrences = entry.get("occurrences", entry.get("source_ids"))
        if occurrences is not None:
            raw = entry.get("raw_form", entry.get("raw"))
            audit.check(author + ":exact_occurrences:" + raw,
                        set(occurrences) == {r["source_group_id"] for r in source["rows"] if r["ivtff_group_raw"] == raw})
    badrefs = []
    for row, n in zip(rows, native):
        for ref in row.get("consumer_source_ids", row.get("later_consumption_source_ids", [])):
            if ref not in expected:
                badrefs.append({"id": n.get("source_group_id"), "reference": ref})
    audit.check(author + ":consumer_source_references_exist", not badrefs, badrefs)
    audit.check(author + ":row_status_explicit", all(isinstance(r.get("status"), str) and r["status"] for r in rows), dict(Counter(r.get("status") for r in rows)))
    units = account.get("primary_units", [])
    if not units:
        audit.unverified(author + ":primary_unit_schema", "N/E declaration adapter required; coverage alone is not primary completion.")
    for unit in units:
        reader, block = unit["edition"], unit["block"]
        selected = {sid for sid,n in expected.items() if n["edition"] == reader and n["block"] == block}
        audit.check(author + ":primary_unit_IDs:" + reader + ":" + block, block in ("N", "E") and set(unit["source_ids"]) == selected)
    uses = account.get("shared_part_uses", [])
    supported = set()
    for use in uses:
        sid = use["source_group_id"]
        raw = expected.get(sid, {}).get("ivtff_group_raw")
        valid = raw in LICENSED_AN_FORMS and use.get("raw_form") == raw
        audit.check(author + ":licensed_shared_part_source:" + sid, valid)
        if valid:
            supported.add(raw)
        audit.check(author + ":shared_part_reference_fields:" + sid,
                    bool(use.get("interface_id")) and bool(use.get("arguments")) and
                    use.get("returned_value") is not None and bool(use.get("effect")) and
                    all(ref in expected for ref in use.get("consumer_source_ids", [])))
    audit.unverified(author + ":shared_part_actual_effect", {"declared_supported_forms": sorted(supported),
                "at_least_two_forms_declared": len(supported) >= 2, "note": "Missing use leaves construction obligation unmet; preservation can still PASS. Actual semantic license, argument type and non-null effect require manual review."})
    costs = account.get("costs", {})
    if "dictionary_entries" in costs:
        audit.check(author + ":dictionary_cost_count", costs["dictionary_entries"] == len(dictionary))
    audit.unverified(author + ":semantic_and_cost_review", {"author_status": account.get("status"),
        "note": "Inspect constants, aliases/defaults, unknown carry, added rules, unused instructions, actual consumers and owner/time/cause identity. No semantic or whole-completion certification."})


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
        (D / "artifacts/AUTHOR_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "source_only": args.source_only, "checks": len(audit.checks), "failures": failures}))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
