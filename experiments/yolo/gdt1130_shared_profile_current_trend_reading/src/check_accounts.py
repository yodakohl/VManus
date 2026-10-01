#!/usr/bin/env python3
"""GDT1130 bounded source preparation/accounting; never selects a meaning.

--prepare-source builds SOURCE.json using only the two registered JSON packets.
Final author checks require root-released account AND constructor hashes.
No semantic execution, parser fitting, new target query or image access.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
READERS = ("IT2a", "ZL3b", "RF1b")


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_source(plan):
    pins = plan["source_inputs"]
    packets = []
    for pin in pins:
        path = ROOT / pin["path"]
        if sha(path) != pin["sha256"]:
            raise ValueError("Registered source changed: " + pin["path"])
        packets.append(load(path))
    ring, prose, _, formal = packets
    ringrows = next(query["rows"] for query in ring["queries"] if query["id"] == "groups")
    proserows = prose["query"]["rows"]
    annotations = {(r["edition"], r["locus"], r["index"]): r for r in formal["groups"]}
    rows = []
    for reader in READERS:
        for part, native_rows, packet_index in (("ring", ringrows, 0), ("body", proserows, 1)):
            for position, native in enumerate(native_rows):
                if native["edition"] != reader:
                    continue
                locus, index = native["locus"], int(native["source_group_index"])
                raw = native["ivtff_group_raw"]
                annotation = annotations[(reader, locus, index)]
                if (annotation["raw"], annotation["left_separator"], annotation["right_separator"]) != (
                        raw, native["left_separator"], native["right_separator"]):
                    raise ValueError("1051 annotation differs from native group")
                rows.append({"source_group_id": f"{reader}|{locus}|G{index:03d}",
                    "edition": reader, "locus": locus, "part": part, "index": index,
                    "source_group_index": native["source_group_index"],
                    "ivtff_group_raw": raw, "raw": raw,
                    "left_separator": native["left_separator"], "right_separator": native["right_separator"],
                    "native_metadata": native,
                    "source_pointer": {"packet": pins[packet_index]["path"],
                        "array": "queries[id=groups].rows" if part == "ring" else "query.rows", "index": position},
                    "paragraph_start": native.get("paragraph_start"),
                    "paragraph_end": native.get("paragraph_end"),
                    "source_group_count": native.get("source_group_count"),
                    "uncertainty": {"adjacent_uncertain_space": any(native[k] == "UNCERTAIN_SMALL_SPACE"
                        for k in ("left_separator", "right_separator")),
                        "literal_entities": re.findall(r"@\d+;", raw),
                        "literal_brackets": re.findall(r"\[[^]]*\]", raw),
                        "literal_braces": re.findall(r"\{[^}]*\}", raw)},
                    "formal_annotation_GDT1051": annotation})
    units = []
    for reader in READERS:
        for part, native_units, packet_index in (("ring", ring["groups"], 0), ("body", prose["units"], 1)):
            for position, unit in enumerate(native_units):
                if unit["edition"] == reader:
                    ids = [r["source_group_id"] for r in rows if r["edition"] == reader and r["locus"] == unit["locus"]]
                    units.append({"edition": reader, "locus": unit["locus"], "part": part,
                        "native_unit": unit, "source_group_ids": ids,
                        "source_pointer": {"packet": pins[packet_index]["path"],
                                           "array": "groups" if part == "ring" else "units", "index": position}})
    ids = [r["source_group_id"] for r in rows]
    if len(ids) != len(set(ids)) or len(ids) != 288 or dict(Counter(r["edition"] for r in rows)) != plan["raw_counts"]:
        raise ValueError("Registered position counts differ")
    for unit in units:
        actual = [r["raw"] for r in rows if r["edition"] == unit["edition"] and r["locus"] == unit["locus"]]
        if actual != unit["native_unit"]["groups"]:
            raise ValueError("Native unit/group order differs")
    return {"schema": "GDT1130_LOSSLESS_BOUNDED_SOURCE_v1", "registered_utc": plan["registered_utc"],
        "source_inputs": pins, "scope_loci": plan["scope_loci"], "raw_counts": plan["raw_counts"],
        "physical_leaves": [68, 89], "independent_confirmation_leaves": [],
        "independent_confirmation_leaf_count": 0, "all_source_already_exposed": True, "new_access": False,
        "native_ID_policy": "Source packets have no group-ID field. ID is edition|locus|G plus zero-padded native index; source_pointer and native_metadata preserve the exact mapping.",
        "capacity_limits": {"ring_paragraph_flags": "Not present in cached ring position rows; null means unavailable, never inferred.",
            "RF1b_body": "All native paragraph_start/end flags are0; comparison window, not automatically a complete native paragraph.",
            "alternate_readers": "Three readings of the same two leaves, not independent confirmation."},
        "annotation_limit": "Unchanged GDT1051 annotations only; no parser replay/change or semantic assignment. Raw packet values outrank annotations.",
        "units": units, "groups": rows,
        "raw_packets": {"ring": ring, "body": prose}}


def write_source(plan):
    source = build_source(plan)
    (D / "src/SOURCE.json").write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n")
    summary = []
    for reader in READERS:
        selected = [r for r in source["groups"] if r["edition"] == reader]
        counts = Counter(r["locus"] for r in selected)
        summary.append(f"| {reader} | {counts['f68r2.6']} | {counts['f68r2.31']} | {sum(v for k,v in counts.items() if k.startswith('f89v1.'))} | {len(selected)} |")
    text = """# GDT1130 source accounting

Prepared only from the two already exposed, registered ring/body JSON packets.
All original packet objects are retained in `SOURCE.json.raw_packets`; no TSV,
target image, new query or access admission was used. All four registered inputs
are hash checked; GDT1051 supplies unchanged formal annotations only.

| Reader | f68r2.6 | f68r2.31 | f89v1.13–20 | Total |
|---|---:|---:|---:|---:|
""" + "\n".join(summary) + """

There are six ring units,24 body units and288 unique native positions. Physical
leaves68/89 are exposed development material; independent confirmation leaves:0.

## Source format

`src/SOURCE.json.groups` is the canonical author input, ordered IT/ZL/RF then
ring/body/native order. Each row has `source_group_id`, `edition`, `locus`,
`part`, `index`, unchanged string `source_group_index`, `raw` and
`ivtff_group_raw`, separators, full `native_metadata`, literal uncertainty,
and an exact `source_pointer` to the original packet array/position.
IDs are derived as `EDITION|LOCUS|GNNN`; the original packets have no ID column.
`units` retains every original six ring/24 body unit plus ordered native IDs.
`raw_packets` retains every original metadata/query/flag field losslessly.
Formal annotations are labeled `formal_annotation_GDT1051` and have no meanings.

Cached ring position rows contain no native paragraph flags or group-count
field: their corresponding values are null, not invented. Prose native flags
and counts are retained verbatim. RF body has no complete native paragraph
flags and stays a comparison window. Literal entities/brackets/braces remain
raw; uncertain spaces are neither joined nor normalized.

## Bounded validator criteria

`python src/check_accounts.py --prepare-source` reproduces the source from the
registered JSONs. Final author validation runs only after root releases account
and constructor hashes. It checks exact coverage/source mapping, unchanged
constructor pins, finite declaration limits, repeated dictionary identity,
explicit constant/reference/part-effect declarations and honest barriers.
Declared non-null shared parts are bookkeeping claims, not validated meanings:
manual review must establish same semantic interface and actual effects on a
retained owner/property/basis. No automatic semantic winner or complete reading
certification is produced. Preparation/checker budget:15 active minutes;
root owns final scientific review, ledger and publication.
"""
    # Initial format documentation may later contain the independent review.
    # Reproducing SOURCE must preserve those appended review notes.
    documentation = D / "artifacts/SOURCE_ACCOUNTING.md"
    if not documentation.exists():
        documentation.write_text(text)
    print(json.dumps({"source_sha256": sha(D / "src/SOURCE.json"), "groups": 288, "units": len(source["units"]), "raw_counts": source["raw_counts"]}))


def audit_a_adapter(account, freeze, source):
    """Inspect A's literal declarations/references, not predicate truth."""
    checks = []
    def check(name, passed, details=None):
        checks.append({"check": "A:" + name, "status": "PASS" if passed else "FAIL", "details": details})
    expected = {r["source_group_id"]: r for r in source["groups"]}
    rows, dictionary, objects = account["rows"], account["dictionary"], account["objects"]
    check("all_embedded_SOURCE_rows_exact", all(row["source"] == expected.get(row["source_id"]) for row in rows))
    forms = {row["raw"] for row in source["groups"]}
    check("dictionary_all_exact_forms_including_unknowns", {e["raw_form"] for e in dictionary} == forms)
    check("dictionary_occurrence_lists_exact", all(e["occurrences"] == [r["source_group_id"] for r in source["groups"] if r["raw"] == e["raw_form"]] for e in dictionary))
    families = {c["id"] for c in freeze["constructors"]}
    check("step_families_declared", all(step["family"] in families for row in rows for step in row["steps"]))
    check("object_type_labels_declared", all(obj["type"] in freeze["types"] for obj in objects.values()))
    badrefs = []
    for row in rows:
        for ref in row["actual_operands"] + row["outputs"]:
            if ref not in objects:
                badrefs.append({"id": row["source_id"], "object": ref})
        for use in row["later_consumption"]:
            if use["output"] not in row["outputs"] or any(sid not in expected for sid in use["consumer_ids"]):
                badrefs.append({"id": row["source_id"], "consumption": use["output"]})
    check("recorded_object_and_consumption_references_exist", not badrefs, badrefs)
    known_constants = {c.split(":", 1)[0] for c in freeze["opaque_constants"]}
    badconstants = [oid for oid,obj in objects.items() if obj["type"] in ("Owner", "Property", "Basis") and obj["value"] not in known_constants]
    check("named_constant_values_from_freeze", not badconstants, badconstants)
    statuses = Counter(row["status"] for row in rows)
    check("row_statuses_explicit", set(statuses) <= {"UNKNOWN", "BLOCKED", "FRAGMENT_ACCOUNTED"})
    check("fragment_not_complete_unit_claim", all(not unit["full_connected_reading_available"] for unit in account["units"]), dict(statuses))
    costs = account["costs"]
    assigned = [e for e in dictionary if e["rule"] != "UNKNOWN_EXACT_WHOLE"]
    check("assigned_unresolved_dictionary_costs", costs["assigned_exact_wholes"] == len(assigned) and costs["unresolved_exact_wholes"] == len(dictionary)-len(assigned))
    check("primitive_assignment_costs", costs["primitive_constructor_assignments"] == sum(e.get("primitive_constructor_assignments", 0) for e in assigned))
    check("exact_alias_costs", costs["exact_aliases_beyond_first_rule"] == len(assigned)-len({e["rule"] for e in assigned}))
    effects = account["semantic_part_effects"]
    errors = []
    for effect in effects:
        sid = effect["source_id"]
        if sid not in expected or effect["raw_form"] != expected[sid]["raw"] or effect["interface"] not in families:
            errors.append({"id": sid, "field": "source/form/interface"})
        if effect["field_operand"] not in objects or effect["written_value_operand"] not in objects or effect["completion_source_id"] not in expected:
            errors.append({"id": sid, "field": "recorded_operands/completion"})
        if not effect["nonnull_world_effect"] or effect["complete_unit"]:
            errors.append({"id": sid, "field": "declared_effect/partiality"})
    check("shared_part_declarations_and_references", bool(effects) and not errors, errors)
    supported = {e["raw_form"] for e in effects if e["interface"] == "aN"} & {"okaiin", "qokaiin", "chokaiin", "daiin"}
    check("at_least_two_declared_licensed_aN_forms", len(supported) >= 2,
          {"supported_forms": sorted(supported), "declarations": len(effects), "actual_nonnull_semantic_effect_verified": False})
    return checks


def audit_b_adapter(account, freeze, source):
    checks = []
    def check(name, passed, details=None):
        checks.append({"check": "B:" + name, "status": "PASS" if passed else "FAIL", "details": details})
    rows, dictionary = account["group_ledger"], account["full_dictionary"]
    expected = {r["source_group_id"]: r for r in source["groups"]}
    by_id = {r["source_group_id"]: r for r in rows}
    check("all_SOURCE_fields_exact", all({k:row.get(k) for k in original} == original
          for sid,original in expected.items() for row in [by_id.get(sid, {})]))
    for key in ("core_families", "types", "opaque_content_constants", "reference_and_basis_policy"):
        check("frozen_" + key, account[key] == freeze[key])
    extensions_path = D / "src/B_EXTENSIONS.json"
    extensions = load(extensions_path)
    check("extension_pin", sha(extensions_path) == account["extension_sha256"] and extensions["frozen_core_sha256"] == account["constructor_sha256"])
    check("core_and_extension_dictionary_identity", dictionary == extensions["full_dictionary"] and
          all(dictionary[k] == v for k,v in freeze["core_dictionary"].items()))
    check("each_added_whole_priced", all(v.get("price") for v in extensions["extension_dictionary"].values()))
    costs = account["costs"]
    check("core_extension_constant_cost_counts", costs["core_families"] == len(freeze["core_families"]) and
          costs["opaque_constants"] == len(freeze["opaque_content_constants"]) and
          costs["core_words"] == len(freeze["core_dictionary"]) and
          costs["priced_added_exact_forms"] == len(extensions["extension_dictionary"]) and
          costs["total_exact_interpreted_forms"] == len(dictionary) and
          costs["unknown_raw_form_types"] == len({r["raw"] for r in source["groups"]}-set(dictionary)))
    check("all_occurrences_use_identical_whole_entry", all(row["frozen_dictionary_entry"] == dictionary.get(row["raw"]) for row in rows))
    families = {c["id"] for c in freeze["core_families"]}
    check("materialized_step_families_declared", all(step["family"] in families for row in rows for step in row["substeps"]))
    status = Counter(row["status"] for row in rows)
    check("row_statuses_explicit", set(status) <= {"DERIVED_C0_WORLD_CONTENT", "BLOCKED_AFTER_FIRST_BARRIER", "UNKNOWN_FIRST_BARRIER"}, dict(status))
    badrefs = []
    for row in rows:
        sid = row["source_group_id"]
        for ref in row["later_consumption_source_ids"]:
            if ref not in by_id or by_id[ref]["edition"] != row["edition"]:
                badrefs.append({"id": sid, "consumer": ref})
        for operand in row["operands"]:
            producers = operand.get("actual_producer_source_ids", []) + ([operand["producer_source_id"]] if operand.get("producer_source_id") else [])
            for ref in producers:
                if ref not in by_id or by_id[ref]["edition"] != row["edition"]:
                    badrefs.append({"id": sid, "producer": ref})
    check("recorded_consumer_producer_references_exist", not badrefs, badrefs)
    repeated = {raw for raw,n in Counter(r["raw"] for r in source["groups"]).items() if n > 1}
    audit = {e["raw"]:e for e in account["exact_repeat_inventory"]}
    check("exact_repeat_inventory_positions", set(audit) == repeated & set(dictionary) and all(
          e["positions"] == [r["source_group_id"] for r in source["groups"] if r["raw"] == raw] and
          e["materialized_positions"] == [r["source_group_id"] for r in rows if r["raw"] == raw and r["status"] == "DERIVED_C0_WORLD_CONTENT"]
          for raw,e in audit.items()),
          {"interpreted_repeat_types": len(audit), "unassigned_repeated_raw_forms": sorted(repeated-set(dictionary)),
           "unassigned_forms_have_no_semantic_repeat_identity": True})
    for unit in account["units"]:
        selected = [r for r in rows if r["edition"] == unit["edition"] and r["unit"] == unit["unit"]]
        derived = sum(r["status"] == "DERIVED_C0_WORLD_CONTENT" for r in selected)
        check("unit_counts_" + unit["edition"] + "_" + unit["unit"], len(selected) == unit["groups"] and derived == unit["materialized_groups"] and
              (not unit["operational_complete"] or derived == len(selected)) and
              (not unit["complete"] or unit["operational_complete"]),
              {"operational_complete": unit["operational_complete"], "author_complete": unit["complete"],
               "semantic_coherence_assessment": unit["semantic_coherence_assessment"]})
    parts = account["semantic_part_effect_inventory"]
    check("declared_exact_parts_concatenate", all("".join(e["exact_parts"]) == e["raw"] for e in parts))
    licensed = [e for e in parts if e["raw"] in {"okaiin", "qokaiin", "chokaiin", "daiin"}]
    check("shared_aiin_effect_declarations_same_nonempty", len(licensed) >= 2 and
          len({e["semantic_effects"]["aiin"] for e in licensed}) == 1 and
          all(e["semantic_effects"]["aiin"] and e["materialized_positions"] for e in licensed),
          {"forms": [e["raw"] for e in licensed], "actual_semantic_interface_verified": False})
    check("part_materialization_positions_real", all(sid in by_id and by_id[sid]["raw"] == e["raw"] and by_id[sid]["status"] == "DERIVED_C0_WORLD_CONTENT"
          for e in parts for sid in e["materialized_positions"]))
    return checks


def replay_b():
    """Replay author-owned sources in a temporary copy, leaving originals intact."""
    receipt = load(D / "artifacts/B_FINAL_FREEZE_RECEIPT.json")
    files = receipt["files"]
    before = {name:sha(D/name) for name in files}
    checks = [{"check": "B:final_receipt_file_pins", "status": "PASS" if before == files else "FAIL"}]
    with tempfile.TemporaryDirectory(prefix="gdt1130_replay_") as directory:
        temporary = Path(directory)
        for name in ["src/SOURCE.json", "src/B_CONSTRUCTORS.json", "src/B_EXTENSIONS.json", "src/B_MATERIALIZE.py", "src/B_WRITE_READING.py"]:
            dest = temporary / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(D/name, dest)
        (temporary / "artifacts").mkdir()
        returns = []
        for name in ("B_MATERIALIZE.py", "B_WRITE_READING.py"):
            result = subprocess.run([sys.executable, str(temporary/"src"/name)], capture_output=True, text=True, timeout=30)
            returns.append(result.returncode)
        match = all((temporary/name).exists() and sha(temporary/name) == before[name]
                    for name in ("artifacts/B_ACCOUNT.json", "artifacts/B_READING.md"))
        checks.append({"check": "B:temporary_replay_exact_account_and_reading_bytes", "status": "PASS" if returns == [0,0] and match else "FAIL",
                       "details": {"return_codes": returns, "semantic_validation": False}})
    checks.append({"check": "B:original_replay_inputs_and_outputs_unchanged", "status": "PASS" if before == {name:sha(D/name) for name in files} else "FAIL"})
    return checks


def final_checks(plan, args):
    """Accounting only; schema-specific semantic declarations stay manual."""
    checks, manual, pins = [], [], {}
    def check(name, passed, details=None):
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "details": details})
    source = load(D / "src/SOURCE.json")
    check("lossless_source_reproduces_registered_packets", source == build_source(plan))
    expected = {r["source_group_id"]: r for r in source["groups"]}
    source_sha = sha(D / "src/SOURCE.json")
    for author in ("A", "B"):
        account_path = D / f"artifacts/{author}_ACCOUNT.json"
        freeze_path = D / (f"artifacts/{author}_CONSTRUCTORS.json" if author == "A" else "src/B_CONSTRUCTORS.json")
        released_account = getattr(args, "final_" + author.lower())
        released_freeze = getattr(args, "freeze_" + author.lower())
        pins[author] = {"account_sha256": sha(account_path), "constructor_sha256": sha(freeze_path)}
        check(author + ":released_account_identity", pins[author]["account_sha256"] == released_account)
        check(author + ":released_constructor_identity", pins[author]["constructor_sha256"] == released_freeze)
        account, freeze = load(account_path), load(freeze_path)
        declared_source = account.get("shared_source_sha256", account.get("source_sha256"))
        check(author + ":account_source_pin", declared_source == source_sha)
        if "constructor_sha256" in account:
            check(author + ":account_constructor_pin", account["constructor_sha256"] == released_freeze)
        constructors = freeze.get("constructors", freeze.get("core_families", []))
        constants = freeze.get("opaque_constants", freeze.get("opaque_content_constants", []))
        check(author + ":constructor_family_limit", 0 < len(constructors) <= plan["constructor_limits"]["core_families"])
        check(author + ":constant_limit", 0 < len(constants) <= plan["constructor_limits"]["opaque_content_constants"])
        if "constructors" in account:
            check(author + ":account_core_constructor_identity", account["constructors"] == constructors)
        rows = account.get("rows", account.get("group_ledger", []))
        ids = [r.get("source_group_id", r.get("source_id")) for r in rows]
        check(author + ":exact_288_native_ID_coverage", len(ids) == len(set(ids)) == 288 and set(ids) == set(expected))
        problems = []
        for row, sid in zip(rows, ids):
            if sid not in expected:
                continue
            original = expected[sid]
            native = row.get("source_raw", row.get("source", row))
            raw = native.get("ivtff_group_raw", row.get("raw", row.get("raw_form")))
            if raw != original["raw"]:
                problems.append({"id": sid, "field": "raw"})
            for key in ("source_group_index", "left_separator", "right_separator"):
                if key in native and native[key] != original[key]:
                    problems.append({"id": sid, "field": key})
            metadata = native.get("native_metadata", row.get("native_metadata", row.get("source_metadata")))
            if metadata is not None and metadata != original["native_metadata"]:
                problems.append({"id": sid, "field": "native_metadata"})
        check(author + ":unchanged_native_values_where_materialized", not problems, problems)
        dictionary = account.get("dictionary", account.get("whole_dictionary", account.get("full_dictionary", [])))
        if isinstance(dictionary, dict):
            dictionary = [{"raw": k, **v} for k,v in dictionary.items()]
        raw_forms = [e.get("raw", e.get("raw_form")) for e in dictionary]
        check(author + ":dictionary_forms_unique", bool(dictionary) and len(raw_forms) == len(set(raw_forms)))
        lookup = dict(zip(raw_forms, dictionary))
        repeated_errors = []
        for row, sid in zip(rows, ids):
            if sid not in expected:
                continue
            entry = lookup.get(expected[sid]["raw"])
            rule = row.get("dictionary_rule", row.get("rule"))
            if entry and rule is not None and rule != entry.get("rule", entry.get("rule_id")):
                repeated_errors.append(sid)
        check(author + ":repeated_declared_dictionary_rule_identity", not repeated_errors, repeated_errors)
        if author == "A":
            checks.extend(audit_a_adapter(account, freeze, source))
        else:
            checks.extend(audit_b_adapter(account, freeze, source))
        manual.append({"author": author, "author_status": account.get("status"),
            "required_review": ["Source metadata not materialized in a row remains pinned in SOURCE; inspect omitted author fields separately.",
                "Each reused constant denotes one fixed content value; actual typed references and paid overload conditions.",
                "Shared part: at least two exact licensed forms, same interface and actual non-null owner/property/basis effect.",
                "Every residual/default/alias is priced and cannot override frozen core/types.",
                "UNKNOWN/BLOCKED versus full construction, actual consumers and connected reading.",
                "World predication, lower-owner ambiguity, common basis/time/condition and discriminating consequence."],
            "automatic_semantic_certification": False})
        check(author + ":released_inputs_unchanged_after_checks", sha(account_path) == released_account and sha(freeze_path) == released_freeze)
    checks.extend(replay_b())
    check("SOURCE_unchanged_after_checks", sha(D / "src/SOURCE.json") == source_sha)
    failures = sum(c["status"] == "FAIL" for c in checks)
    result = {"schema": "GDT1130_ACCOUNTING_ONLY_v1", "status": "FAIL_ACCOUNTING" if failures else "PASS_ACCOUNTING_ONLY_MANUAL_REVIEW_REQUIRED",
        "source_sha256": source_sha, "inputs": pins, "checks": checks, "manual_review": manual,
        "semantic_winner": None, "confirmed_meanings": 0,
        "claim_ceiling": "Exact source/declaration accounting only. Repeated labels and declared non-null effects are not proven semantic interfaces or complete readings."}
    (D / "artifacts/AUTHOR_VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    (D / "artifacts/AUTHOR_VALIDATION.md").write_text(
        "# GDT1130 author accounting validation\n\n" + result["status"] + f". {len(checks)} checks, {failures} failures.\n\n"
        "Both released accounts conserve all288 native positions and unchanged source/freeze bytes. "
        "A has96 fragment-accounted,182 UNKNOWN and10 BLOCKED rows; no complete connected unit. "
        "B has161 materialized,121 blocked and6 first-unknown rows. Its operationally complete IT prose remains "
        "distinct from the exact candidate's reported Appearance LOW/HIGH contradiction. These author statements "
        "are retained for manual review, not promoted by accounting PASS.\n\n"
        "A declares30 assigned and84 unresolved wholes,12 core families and8 constants. B declares98 interpreted "
        "wholes including83 individually priced extensions,10 families and7 constants. Inventory counts are not "
        "a calibrated model-selection score. Shared-part declarations and referenced consumers are enumerated; "
        "actual semantic interfaces, non-null world effects, owner/basis/time truth and connected-reading adequacy "
        "require independent manual review.\n\n"
        "Author B's materializer and reading writer reproduce exact released bytes in a temporary copy. Original "
        "author inputs/outputs remain unchanged. This is engineering reproducibility, not independent manuscript "
        "evidence or semantic confirmation. SOURCE reproduces both pinned source packets without new access.\n\n"
        "See AUTHOR_VALIDATION.json for exact input pins, objective checks and manual-review limits. "
        "No semantic winner, confirmed meaning or independent confirmation is produced.\n")
    print(json.dumps({"status": result["status"], "checks": len(checks), "failures": failures}))
    return bool(failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-source", action="store_true")
    for author in ("a", "b"):
        parser.add_argument("--final-" + author, help="root-released final account SHA256")
        parser.add_argument("--freeze-" + author, help="root-released constructor SHA256")
    args = parser.parse_args()
    plan = load(D / "src/AUTHOR_PLAN.json")
    if args.prepare_source:
        write_source(plan)
        return 0
    if not all((args.final_a, args.final_b, args.freeze_a, args.freeze_b)):
        parser.error("Final checks require both account and constructor release hashes.")
    return final_checks(plan, args)


if __name__ == "__main__":
    raise SystemExit(main())
