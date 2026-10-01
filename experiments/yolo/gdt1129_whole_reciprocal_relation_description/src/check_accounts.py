#!/usr/bin/env python3
"""Bounded GDT1129 accounting checks. No rule execution or meaning validation.

Run only after root releases BOTH final accounts, passing their exact hashes:
  python .../src/check_accounts.py --final-a SHA256 --final-b SHA256
The release hashes prevent a draft from being silently certified as final.
Preparation/implementation/validation/publication budget: 20 active minutes;
root owns scientific review, ledger update and publication. Waiting for authors
does not authorize unattended polling or further implementation expansion.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
SOURCE_SHA256 = "2ac5094a1d4394cae01141050912c5ad2cef0ca3d0053918b0294af828eccac0"
FREEZE_SHA256 = {
    "A": "1f90ec4505f9e75198db2a8f25695491cb0ec9235deff6193cc5992f9beb1cbe",
    "B": "941460d2579fb7ee9fcef8cc98444cf818189a93f5dc75f678a3f7e8a497d628",
}
NATIVE_FIELDS = ("source_group_id", "ivtff_group_raw", "source_group_index",
                 "left_separator", "right_separator")
MANUAL = [
    "Actual argument identity, constructor arity/type truth and scope in free prose.",
    "Whether recorded contribution/consumption is an effective content operation.",
    "Semantic atomicity, hidden defaults, nominal constants and paid co-reference.",
    "Whether declared overload conditions apply without occurrence-fitted repair.",
    "Written continuation's relation/event consequence and scientific selection.",
    "Hypothetical word meanings and manuscript participant/reference truth.",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def first(obj, names, default=None):
    for name in names:
        if name in obj:
            return obj[name]
    return default


def declaration_id(item):
    return first(item, ("id", "rule_id", "constructor_id", "rule"))


def whole(item):
    return first(item, ("raw", "raw_form", "whole", "ivtff_group_raw"))


def binding(item):
    # Inputs/outputs may vary by state; dictionary-fixed rule/value may not.
    return {k: item[k] for k in ("rule", "rule_id", "constructor_id", "value",
            "value_id", "fixed_parameters", "parameters", "overload_ids",
            "overload_condition", "ordered_parts") if k in item}


class Audit:
    def __init__(self):
        self.checks = []
        self.unverified = []

    def check(self, name, passed, details=None):
        row = {"check": name, "status": "PASS" if passed else "FAIL"}
        if details is not None:
            row["details"] = details
        self.checks.append(row)

    def unverifiable(self, name, details):
        self.unverified.append({"check": name, "status": "MANUAL_REVIEW", "details": details})


def source_rows(source):
    expected = []
    for reader in ("IT2a", "ZL3b", "RF1b"):
        paragraphs = source["paragraphs"][reader]
        plines = {line["locus"]: line for para in paragraphs for line in para["lines"]}
        for line in source["raw"][reader]:
            metadata = line["metadata"]
            pline = plines.get(metadata["locus"])
            for group in line["groups"]:
                expected.append({**group, "reader": reader, "locus": metadata["locus"],
                    "line_metadata": metadata, "paragraph_line_metadata":
                    None if pline is None else {k: v for k, v in pline.items()
                                               if k not in ("source_ids", "words")},
                    "inherited_anchor_eligible": None if pline is None else pline["anchor_eligible"],
                    "inherited_capacity_status": "NO_COMPLETE_PARAGRAPH_RECORD" if pline is None else
                        ("ELIGIBLE" if pline["anchor_eligible"] else "INELIGIBLE_LINE"),
                    "adjacent_uncertain_space": any(group[k] == "UNCERTAIN_SMALL_SPACE"
                                                   for k in ("left_separator", "right_separator"))})
    return expected


def audit_source(audit, plan, source, accounting, prior):
    expected = source_rows(source)
    ids = [r["source_group_id"] for r in expected]
    audit.check("source_unique_176_ids", len(ids) == len(set(ids)) == 176)
    audit.check("source_reader_counts", dict(Counter(r["reader"] for r in expected)) == plan["scope"])
    ledger = accounting["all_native_groups"]
    by_id = {r["native_group"]["source_group_id"]: r for r in ledger}
    problems = []
    for row in expected:
        other = by_id.get(row["source_group_id"], {})
        checks = {"native_group": {k: row[k] for k in NATIVE_FIELDS},
                  "line_metadata": row["line_metadata"],
                  "paragraph_line_metadata": row["paragraph_line_metadata"],
                  "inherited_anchor_eligible": row["inherited_anchor_eligible"],
                  "inherited_capacity_status": row["inherited_capacity_status"],
                  "adjacent_uncertain_space": row["adjacent_uncertain_space"]}
        for key, value in checks.items():
            if other.get(key) != value:
                problems.append({"id": row["source_group_id"], "field": key})
    audit.check("source_accounting_matches_primary", len(ledger) == 176 and
                set(by_id) == set(ids) and not problems, problems)
    it = Counter(r["ivtff_group_raw"] for r in expected if r["reader"] == "IT2a")
    prior_it = {r["whole"]: r for r in prior["IT_complete_whole_inventory"]}
    audit.check("exact_39_IT_wholes_prior_agreement", len(it) == 39 and
                set(it) == set(prior_it) and all(prior_it[k]["count"] == v for k, v in it.items()))
    return expected


def audit_account(author, account, freeze, expected, audit):
    rows = first(account, ("group_ledger", "rows", "group_accounting", "groups"), [])
    if author == "A" and "IT2a" in account:
        # A uses lexical IDs (A/K/PAIR/OL) distinct from constructor IDs.
        # Keep those namespaces separate; inspect actual constructor_steps.
        native_rows = account["IT2a"]["rows"] + [r for reader in ("ZL3b", "RF1b")
                        for r in account["alternates"][reader]["rows"]]
        rows = []
        for native in native_rows:
            normalized = {**native, **native["source_raw"],
                          "line_metadata": native["source_metadata"],
                          "rule": native["dictionary_rule"],
                          "later_consumption_source_ids": [sid for consumption in native["later_consumption"]
                                                           for sid in consumption["consumer_ids"]]}
            rows.append(normalized)
    dictionary = first(account, ("whole_dictionary", "dictionary", "whole_inventory"), [])
    if isinstance(dictionary, dict):
        dictionary = [{"raw": k, **v} for k, v in dictionary.items()]
    rules = first(account, ("rules", "constructors", "rule_inventory"), [])
    frozen_rules = first(freeze, ("rules", "constructors"), [])
    rule_ids = [declaration_id(r) for r in frozen_rules]
    label = lambda name: author + ":" + name
    audit.check(label("declared_rules_unique"), None not in rule_ids and len(rule_ids) == len(set(rule_ids)))
    audit.check(label("frozen_rule_inventory"), not rules or rules == frozen_rules,
                {"frozen_rules": len(frozen_rules), "account_rules": len(rules)})
    if not rules:
        audit.unverifiable(label("account_rule_definitions"), "Account uses pinned constructor inventory by reference; prose adaptations require manual review.")
    if "types" in account:
        audit.check(label("frozen_type_inventory"), account["types"] == freeze["types"])
    if "costs_at_freeze" in freeze:
        audit.check(label("frozen_cost_inventory"), account.get("costs") == freeze["costs_at_freeze"])
    else:
        audit.unverifiable(label("cost_inventory_freeze"), "Freeze defines policies/constructors, not a numeric full dictionary cost inventory; inspect paid declarations manually.")
    if "whole_dictionary" in freeze:
        audit.check(label("frozen_dictionary"), dictionary == freeze["whole_dictionary"])
    forms = [whole(item) for item in dictionary]
    itforms = {r["ivtff_group_raw"] for r in expected if r["reader"] == "IT2a"}
    audit.check(label("dictionary_exact_39_IT_forms"), len(forms) == len(set(forms)) == 39 and set(forms) == itforms)
    dby = {whole(item): item for item in dictionary}
    ids = [r.get("source_group_id") for r in rows]
    expected_ids = [r["source_group_id"] for r in expected]
    audit.check(label("all_176_native_ids_once"), len(ids) == len(set(ids)) == 176 and set(ids) == set(expected_ids))
    # Reader ordering can differ between independently authored schemas.
    audit.check(label("native_order_within_reader"), all(
        [i for i in ids if i and i.startswith(reader + "|")] ==
        [i for i in expected_ids if i.startswith(reader + "|")]
        for reader in ("IT2a", "ZL3b", "RF1b")))
    by_id = {r.get("source_group_id"): r for r in rows}
    native_position = {r["source_group_id"]: i for i, r in enumerate(expected)}
    mismatches, ref_problems, binding_problems, status_problems = [], [], [], []
    capacity_missing, capacity_wrong = [], []
    statuses = Counter()
    for source in expected:
        sid = source["source_group_id"]
        row = by_id.get(sid, {})
        for key in NATIVE_FIELDS:
            if row.get(key) != source[key]:
                mismatches.append({"id": sid, "field": key})
        metadata = first(row, ("native_metadata", "line_metadata", "metadata"))
        if metadata != source["line_metadata"]:
            mismatches.append({"id": sid, "field": "line_metadata"})
        status = str(row.get("status", ""))
        statuses[(source["reader"], status)] += 1
        blocked = any(x in status.upper() for x in ("UNKNOWN", "BLOCK", "UNSCORABLE"))
        if not status:
            status_problems.append({"id": sid, "reason": "missing status"})
        rule = first(row, ("rule", "rule_id", "constructor_id"))
        if author == "A":
            for step in row.get("constructor_steps", []):
                constructor = step.get("constructor")
                if constructor == "COMPARE_INCLUSION_OLDER_IN_NEWER" and row.get("dictionary_rule") == "COMPARE":
                    audit.unverifiable(label("COMPARE_specialized_constructor_label"),
                                       {"id": sid, "parent": "COMPARE", "declared_specialization": "older relation included in newer relation",
                                        "note": "Frozen COMPARE permits dictionary-fixed inclusion comparator. Exact label specializes that declaration; record-context extra operand and application require manual review."})
                elif constructor not in rule_ids:
                    ref_problems.append({"id": sid, "constructor": step.get("constructor")})
        elif rule is not None and rule not in rule_ids:
            ref_problems.append({"id": sid, "rule": rule})
        for substep in row.get("substeps", []):
            if substep.get("rule") not in rule_ids:
                ref_problems.append({"id": sid, "substep_rule": substep.get("rule")})
        if not blocked and rule is None:
            status_problems.append({"id": sid, "reason": "active row without declared rule"})
        entry = dby.get(source["ivtff_group_raw"])
        if not blocked and entry is not None:
            if binding(row) != binding(entry):
                binding_problems.append({"id": sid, "raw": source["ivtff_group_raw"]})
        for ref in row.get("later_consumption_source_ids", []):
            if ref not in by_id or ref.split("|")[0] != source["reader"]:
                ref_problems.append({"id": sid, "later_reference": ref})
            elif native_position[ref] < native_position[sid]:
                ref_problems.append({"id": sid, "earlier_consumer_reference": ref})
        for operand in row.get("operands", []):
            if isinstance(operand, dict):
                producers = operand.get("actual_producer_source_ids", [])
                if operand.get("producer_source_id"):
                    producers = producers + [operand["producer_source_id"]]
                for ref in producers:
                    if ref not in by_id or ref.split("|")[0] != source["reader"] or native_position[ref] > native_position[sid]:
                        ref_problems.append({"id": sid, "invalid_recorded_producer_reference": ref})
        for key in ("inherited_anchor_eligible", "inherited_capacity_status", "adjacent_uncertain_space"):
            if key in row and row[key] != source[key]:
                capacity_wrong.append({"id": sid, "field": key})
            elif key not in row and source["reader"] != "IT2a":
                capacity_missing.append({"id": sid, "field": key})
    audit.check(label("raw_metadata_separator_conservation"), not mismatches, mismatches)
    audit.check(label("declared_rule_and_later_source_references"), not ref_problems, ref_problems)
    audit.check(label("dictionary_identity_on_active_occurrences"), not binding_problems, binding_problems)
    audit.check(label("row_status_rule_honesty"), not status_problems, status_problems)
    audit.check(label("no_alternate_capacity_flag_overwrite"), not capacity_wrong, capacity_wrong)
    if capacity_missing:
        audit.unverifiable(label("alternate_capacity_fields_missing"),
                           {"missing_fields": len(capacity_missing), "note": "Native metadata conserved; inherited eligibility is separately pinned in SOURCE_ACCOUNTING, not copied into these account rows. Do not infer eligibility from C0 compatibility."})
    itrows = [r for r in rows if r.get("source_group_id", "").startswith("IT2a|")]
    itblocked = [r["source_group_id"] for r in itrows if any(x in str(r.get("status", "")).upper() for x in ("UNKNOWN", "BLOCK", "UNSCORABLE"))]
    if "complete_IT" in account:
        audit.check(label("complete_IT_status_consistency"), not account["complete_IT"] or len(itrows) == 59 and not itblocked,
                    {"complete_IT_claim": account["complete_IT"], "IT_blocked_ids": itblocked})
    if author == "A":
        audit.check(label("complete_IT_status_consistency"), len(itrows) == 59 and not itblocked)
        declared_occurrences = {whole(entry): entry.get("occurrences", []) for entry in dictionary}
        audit.check(label("dictionary_occurrence_inventory"), all(
            declared_occurrences[raw] == [r["source_group_id"] for r in expected
                                         if r["reader"] == "IT2a" and r["ivtff_group_raw"] == raw]
            for raw in itforms))
        lexical_rules = {entry["rule"] for entry in dictionary}
        unresolved = [{"id": r["source_group_id"], "resolved_rule": r.get("resolved_rule")}
                      for r in itrows if r.get("resolved_rule") not in lexical_rules]
        audit.check(label("resolved_lexical_rules_declared"), not unresolved, unresolved)
        audit.check(label("primitive_assignment_cost_total"), account["costs"]["primitive_assignments_including_compounds_and_overload_branches"] ==
                    sum(entry["primitive_assignments"] for entry in dictionary))
        objects = account["IT2a"]["objects"]
        object_problems = []
        for row in itrows:
            available = {oid for oid, obj in objects.items()
                         if obj["producer"] in native_position and native_position[obj["producer"]] <= native_position[row["source_group_id"]]}
            for ref in row["actual_operands"] + row["outputs"]:
                if ref not in available:
                    object_problems.append({"id": row["source_group_id"], "object_reference": ref})
            for consumption in row["later_consumption"]:
                if consumption["output"] not in row["outputs"]:
                    object_problems.append({"id": row["source_group_id"], "unlisted_consumption_output": consumption["output"]})
        audit.check(label("recorded_object_references_exist_by_row"), not object_problems, object_problems)
        audit.check(label("object_type_labels_declared"), all(obj["type"] in freeze["types"] for obj in objects.values()))
        audit.unverifiable(label("OL_typed_overload_application"),
                           {"declared_condition": account["costs"]["overload_condition"],
                            "uses": [{"id": r["source_group_id"], "resolved_rule": r["resolved_rule"]}
                                     for r in itrows if r["dictionary_rule"] == "OL"],
                            "note": "Declaration and occurrences enumerated; condition/type truth requires independent review."})
    # Check alternate paragraph capacity independently of author compatibility.
    if author == "A":
        capacity_claims = {reader: d["complete_paragraph_flag"] for reader, d in account["alternates"].items()}
    else:
        capacity_claims = {d["reader"]: d["native_whole_paragraph_available"]
                           for d in account.get("alternate_obligations", [])}
    audit.check(label("alternate_native_paragraph_capacity"), capacity_claims == {"ZL3b": True, "RF1b": False})
    costs = account.get("costs", {})
    aliases = costs.get("new_whole_aliases", [])
    observed_aliases = defaultdict(list)
    for entry in dictionary:
        observed_aliases[canonical(binding(entry))].append(whole(entry))
    shared = [sorted(v) for v in observed_aliases.values() if len(v) > 1]
    if aliases:
        audit.check(label("alias_form_inventory"), sorted(shared) == sorted(sorted(a["forms"]) for a in aliases),
                    {"observed_shared_bindings": shared})
    elif shared:
        if author == "A":
            audit.check(label("alias_cost_count"), sum(len(forms) - 1 for forms in shared) == costs["aliases_beyond_first_identical_semantic_rule"],
                        {"observed_shared_bindings": shared})
        else:
            audit.unverifiable(label("alias_pricing"), {"shared_bindings": shared, "note": "Check schema-specific paid alias declarations manually."})
    return {"source_rows": len(rows), "dictionary_forms": len(forms), "frozen_rules": len(rule_ids),
            "status_counts": [{"reader": r, "status": s, "count": n} for (r, s), n in sorted(statuses.items())],
            "author_status": account["status"],
            "author_complete_IT_claim": account.get("complete_IT", "complete IT claimed in author status"),
            "operational_materialization_complete_IT": account.get("operational_materialization_complete_IT"),
            "strict_retention_assessment": account.get("strict_retention_assessment"),
            "complete_content_automatic_validation": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-a", required=True, help="root-released final A_ACCOUNT SHA256")
    parser.add_argument("--final-b", required=True, help="root-released final B_ACCOUNT SHA256")
    args = parser.parse_args()
    audit = Audit()
    plan = read(D / "src/AUTHOR_PLAN.json")
    sourcepath = ROOT / plan["source"]
    audit.check("unchanged_registered_source_pin", digest(sourcepath) == plan["source_sha256"] == SOURCE_SHA256)
    source = read(sourcepath)
    accounting = read(D / "artifacts/SOURCE_ACCOUNTING.json")
    prior = read(D / "artifacts/GRAMMAR_PRIOR_CONSTRAINTS.json")
    expected = audit_source(audit, plan, source, accounting, prior)
    inputs, summaries = {}, {}
    for author, released in (("A", args.final_a), ("B", args.final_b)):
        accountpath = D / f"artifacts/{author}_ACCOUNT.json"
        freezepath = D / f"src/{author}_CONSTRUCTOR_FREEZE.json"
        actual, frozen = digest(accountpath), digest(freezepath)
        inputs[author] = {"account_sha256": actual, "root_released_final_sha256": released,
                          "constructor_sha256": frozen}
        audit.check(author + ":released_final_account_identity", actual == released)
        audit.check(author + ":constructor_bytes_unchanged", frozen == FREEZE_SHA256[author])
        account, freeze = read(accountpath), read(freezepath)
        if "source_packet_sha256" in account:
            audit.check(author + ":account_source_pin", account["source_packet_sha256"] == SOURCE_SHA256)
        if "constructor_freeze_sha256" in account:
            audit.check(author + ":account_constructor_pin", account["constructor_freeze_sha256"] == frozen)
        summaries[author] = audit_account(author, account, freeze, expected, audit)
        audit.check(author + ":account_and_constructor_unchanged_after_validation",
                    digest(accountpath) == released and digest(freezepath) == FREEZE_SHA256[author])
    audit.check("source_unchanged_after_validation", digest(sourcepath) == SOURCE_SHA256)
    failures = sum(c["status"] == "FAIL" for c in audit.checks)
    result = {"schema": "GDT1129_AUTHOR_ACCOUNTING_VALIDATION_v1",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "status": "FAIL_ACCOUNTING" if failures else "PASS_ACCOUNTING_ONLY_MANUAL_REVIEW_REQUIRED",
              "claim_ceiling": "Source, declaration and accounting consistency only. No semantic PASS, type/argument truth certification, complete-content certification, manuscript meaning selection or source-independent confirmation.",
              "budget_minutes": 20, "publication_owner": "root",
              "source_sha256": digest(sourcepath), "inputs": inputs,
              "auxiliary_input_sha256": {str(path.relative_to(D)): digest(path) for path in
                   (D / "src/AUTHOR_PLAN.json", D / "artifacts/SOURCE_ACCOUNTING.json",
                    D / "artifacts/GRAMMAR_PRIOR_CONSTRAINTS.json", D / "src/check_accounts.py")},
              "author_summaries": summaries, "checks": audit.checks,
              "schema_or_prose_unverifiable": audit.unverified,
              "mandatory_manual_checks": MANUAL,
              "automatic_semantic_validation": False}
    (D / "artifacts/AUTHOR_VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(audit.checks),
                      "failures": failures, "manual_items": len(audit.unverified) + len(MANUAL)}))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
