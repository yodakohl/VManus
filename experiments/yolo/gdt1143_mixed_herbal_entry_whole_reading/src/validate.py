#!/usr/bin/env python3
"""Independent protocol/accounting validator for GDT1143; no semantic decoder."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt1143_mixed_herbal_entry_whole_reading"
ART = EXP / "artifacts"
OUT_JSON = ART / "VALIDATION.json"
OUT_MD = ART / "VALIDATION.md"
CHECKS: list[dict] = []
ALL_OK = True


def add(name: str, passed: bool, detail: str, evidence: str = "independent_byte_or_row_check") -> None:
    global ALL_OK
    CHECKS.append({"check": name, "passed": bool(passed), "evidence_type": evidence, "detail": detail})
    ALL_OK = ALL_OK and bool(passed)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def jload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def time(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main() -> int:
    source = jload(EXP / "src/SOURCE.json")
    core_md_path = EXP / "CORE.md"
    core_json_path = EXP / "CORE.json"
    core = jload(core_json_path)
    method = (EXP / "METHOD.md").read_text(encoding="utf-8")
    plan_path = ART / "VALIDATION_PLAN.md"
    plan_hash = sha(plan_path)
    author_md_path = EXP / "AUTHOR_READING.md"
    account_path = ART / "AUTHOR_ACCOUNT.json"
    author_receipt_path = ART / "AUTHOR_RECEIPT.json"
    account = jload(account_path)
    author_receipt = jload(author_receipt_path)
    author_md = author_md_path.read_text(encoding="utf-8")

    # Registered inputs, core freeze, and author order.
    pin_results = []
    pins_ok = True
    for pin in source["inputs"]:
        path = ROOT / pin["path"]
        actual = sha(path) if path.is_file() else None
        ok = actual == pin["sha256"]
        pins_ok &= ok
        pin_results.append({"path": pin["path"], "expected_sha256": pin["sha256"],
                            "actual_sha256": actual, "passed": ok})
    add("registered_input_hashes", pins_ok,
        "All SOURCE.json input pins match current registered bytes; no outside inputs are read.")

    core_receipts = [EXP / "CORE_FREEZE_RECEIPT.json", ART / "CORE_FREEZE_RECEIPT.json"]
    receipts_equal = core_receipts[0].read_bytes() == core_receipts[1].read_bytes()
    core_receipt = jload(core_receipts[0])
    core_hashes_ok = (
        core_receipt.get("core_md_sha256") == sha(core_md_path)
        and core_receipt.get("core_json_sha256") == sha(core_json_path)
        and core_receipt.get("status") == "FROZEN_BEFORE_WHOLE_ACCOUNT"
        and core.get("status") == "FROZEN_C0_EXPLORATORY_CORE"
        and core.get("candidate") == core_receipt.get("candidate") == "01"
        and receipts_equal
    )
    add("frozen_core_bytes_and_duplicate_receipts", core_hashes_ok,
        "Both freeze receipts are byte-identical and bind the current CORE files and frozen status.")

    chronology_ok = False
    try:
        chronology_ok = (
            time(core["authored_utc"]) < time(core_receipt["frozen_utc"])
            and time(core_receipt["frozen_utc"]) < time(author_receipt["authored_utc"])
            and time(author_receipt["authored_utc"]) > time(core_receipt["frozen_utc"])
            and author_receipt.get("core_freeze_receipt_sha256") == sha(core_receipts[0])
            and author_receipt.get("files", {}).get("CORE.json") == sha(core_json_path)
            and author_receipt.get("status") == "WHOLE_ENTRY_C0_ATTEMPT_WITH_OPEN_BINDINGS"
            and core_receipt.get("subsequent_rule_changes") == 0
            and core_receipt.get("subsequent_semantic_repairs") == 0
        )
    except (KeyError, TypeError, ValueError):
        chronology_ok = False
    add("core_freeze_precedes_author_account", chronology_ok,
        "Recorded author/freeze timestamps and receipt hashes put the single frozen core before the account; timestamp provenance is receipt-backed.",
        "byte_check_plus_receipt_chronology")

    author_pin_paths = {
        "CORE.md": core_md_path,
        "CORE.json": core_json_path,
        "CORE_FREEZE_RECEIPT.json": core_receipts[0],
        "AUTHOR_READING.md": author_md_path,
        "artifacts/AUTHOR_ACCOUNT.json": account_path,
        "METHOD.md": EXP / "METHOD.md",
        "src/SOURCE.json": EXP / "src/SOURCE.json",
    }
    receipt_file_hashes_ok = set(author_receipt.get("files", {})) == set(author_pin_paths)
    for rel, p in author_pin_paths.items():
        receipt_file_hashes_ok &= author_receipt.get("files", {}).get(rel) == sha(p)
    add("author_receipt_binds_frozen_artifacts", receipt_file_hashes_ok,
        "AUTHOR_RECEIPT.json binds every listed frozen core, account, method, source, and reading byte; the account is independently checked below.")

    # Reconstruct the expected 176 rows from the registered, page-bounded GDT1094 inputs.
    full_rows = tsv(ROOT / "experiments/yolo/gdt1094_f25v_source_package_whole_reading/artifacts/FULL_PASSAGE.tsv")
    raw_rows = tsv(ROOT / "experiments/yolo/gdt1094_f25v_source_package_whole_reading/src/TARGET_RAW.tsv")
    full_expected: dict[tuple[str, str], list[str]] = {}
    full_counts: dict[str, int] = {}
    for row in full_rows:
        key = (row["edition"], row["locus"])
        groups = row["raw_groups"].split()
        full_expected[key] = groups
        full_counts[row["edition"]] = full_counts.get(row["edition"], 0) + int(row["raw_group_count"])
    raw_by_key: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    raw_index: dict[tuple[str, str, int], dict[str, str]] = {}
    for row in raw_rows:
        edition, locus, index = row["edition"], row["locus"], int(row["source_group_index"])
        raw_by_key[(edition, locus)].append(row)
        raw_index[(edition, locus, index)] = row
    for seq in raw_by_key.values():
        seq.sort(key=lambda r: int(r["source_group_index"]))
    raw_matches_full = set(raw_by_key) == set(full_expected)
    if raw_matches_full:
        for key, expected_groups in full_expected.items():
            raw_matches_full &= [r["ivtff_group_raw"] for r in raw_by_key[key]] == expected_groups
            raw_matches_full &= all(int(r["source_group_count"]) == len(expected_groups) for r in raw_by_key[key])
    expected_edition_counts = {"IT2a": 57, "ZL3b": 60, "RF1b": 59}
    raw_matches_full &= len(raw_rows) == 176 and full_counts == expected_edition_counts
    add("registered_three_reader_passage_reconciles", raw_matches_full,
        "The registered f25v FULL_PASSAGE sequences and TARGET_RAW group inventory agree exactly: IT2a 57, ZL3b 60, RF1b 59 (176 total).")
    boundary_counts = {}
    for edition in ["IT2a", "ZL3b", "RF1b"]:
        selected = [r for r in full_rows if r["edition"] == edition]
        boundary_counts[edition] = {
            "paragraph_starts": sum(int(r["paragraph_start"]) for r in selected),
            "paragraph_ends": sum(int(r["paragraph_end"]) for r in selected),
        }
    boundary_metadata_ok = (boundary_counts == {
        "IT2a": {"paragraph_starts": 1, "paragraph_ends": 1},
        "ZL3b": {"paragraph_starts": 1, "paragraph_ends": 1},
        "RF1b": {"paragraph_starts": 0, "paragraph_ends": 0},
    })
    add("reader_paragraph_boundary_metadata_is_kept_distinct", boundary_metadata_ok,
        f"Pinned FULL_PASSAGE marks one start/end for IT2a and ZL3b, while RF1b has no start/end flags in this projection. Treat RF as unscored/missing boundary evidence, not as evidence of no paragraph or of agreement: {boundary_counts}.")

    rows = account.get("rows", [])
    expected_ids = set(raw_index)
    actual_ids = [(r.get("edition"), r.get("locus"), r.get("index")) for r in rows]
    account_ids_unique = len(actual_ids) == len(set(actual_ids))
    account_id_set_ok = set(actual_ids) == expected_ids
    row_values_ok = account_id_set_ok and account_ids_unique and len(rows) == len(raw_rows)
    mismatch_rows = []
    if row_values_ok:
        for r in rows:
            key = (r["edition"], r["locus"], int(r["index"]))
            expected = raw_index[key]
            for out_key, in_key in (("raw", "ivtff_group_raw"),
                                    ("left_separator", "left_separator"),
                                    ("right_separator", "right_separator")):
                if r.get(out_key) != expected[in_key]:
                    mismatch_rows.append({"id": key, "field": out_key,
                                          "account": r.get(out_key), "input": expected[in_key]})
                    row_values_ok = False
    add("account_rows_exactly_match_all_176_registered_native_groups", row_values_ok,
        "Every account row has a unique reader/locus/index and matches its registered raw spelling and both separators; alternate-reader differences are retained.")

    # Validate the license table and account references without interpreting glosses.
    core_lex = core.get("lexicon", {})
    ext_lex = account.get("extension_values", {})
    ext_order = list(ext_lex)
    ext_ids = {raw: f"EX-C{i:02d}" for i, raw in enumerate(ext_order, 1)}
    license_counts_ok = (len(core_lex) == 18 and len(core.get("rules", [])) == 4
                         and len(ext_lex) == account.get("extension_count") == 25
                         and not (set(core_lex) & set(ext_lex))
                         and account.get("new_whole_form_values_total") == len(set(core_lex) | set(ext_lex)) == 43)
    refs_ok = license_counts_ok
    status_counts: Counter = Counter()
    assigned_by_raw: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        raw, status, value, ref = r.get("raw"), r.get("status"), r.get("value"), r.get("sense_or_rule_ref")
        status_counts[status] += 1
        if status == "CORE_C0":
            refs_ok &= raw in core_lex and ref == f"CORE:{raw}" and value == core_lex.get(raw, {}).get("value")
        elif status == "EXTENSION_C0":
            refs_ok &= raw in ext_lex and ref == ext_ids.get(raw) and value == ext_lex.get(raw, {}).get("value")
        elif status == "UNKNOWN_OR_UNSEGMENTED":
            refs_ok &= value is None and ref is None
        else:
            refs_ok = False
        if value is not None:
            assigned_by_raw[raw].add(value)
    value_stability = all(len(vals) <= 1 for vals in assigned_by_raw.values())
    add("finite_core_and_priced_extension_references", refs_ok and value_stability,
        "Each assigned occurrence resolves to its frozen whole-form core license or separately priced extension; identical exact raw forms never receive conflicting English values. This checks bookkeeping, not whether any value is true.")
    expected_status_counts = Counter({"CORE_C0": 86, "EXTENSION_C0": 68, "UNKNOWN_OR_UNSEGMENTED": 22})
    counts_ok = (status_counts == expected_status_counts
                 and account.get("bookkeeping", {}).get("native_groups") == 176
                 and account.get("bookkeeping", {}).get("typed_or_extended_occurrences") == 154
                 and account.get("bookkeeping", {}).get("unknown_or_unsegmented_occurrences") == 22)
    add("occurrence_status_arithmetic", counts_ok,
        f"Independently counted statuses are core={status_counts.get('CORE_C0', 0)}, extension={status_counts.get('EXTENSION_C0', 0)}, unknown={status_counts.get('UNKNOWN_OR_UNSEGMENTED', 0)}; numbers must sum to all 176 rows.")

    # Recurrence and adjacency obligations.
    counts_by_reader: dict[str, Counter] = defaultdict(Counter)
    by_reader_line: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        counts_by_reader[r["edition"]][r["raw"]] += 1
        by_reader_line[(r["edition"], r["locus"])].append(r)
    for vals in by_reader_line.values():
        vals.sort(key=lambda r: int(r["index"]))
    d_counts = {edition: counts_by_reader[edition].get("daiin", 0) for edition in ["IT2a", "ZL3b", "RF1b"]}
    double_occurrences: dict[str, list[str]] = {}
    for edition in ["IT2a", "ZL3b", "RF1b"]:
        double_occurrences[edition] = []
        for (ed, locus), seq in by_reader_line.items():
            if ed != edition:
                continue
            for a, b in zip(seq, seq[1:]):
                if a["raw"] == b["raw"] == "daiin" and int(b["index"]) == int(a["index"]) + 1:
                    double_occurrences[edition].append(locus)
    expected_daiin = {"IT2a": 11, "ZL3b": 11, "RF1b": 9}
    double_ok = d_counts == expected_daiin and len(double_occurrences["IT2a"]) == 1 and len(double_occurrences["ZL3b"]) == 1 and len(double_occurrences["RF1b"]) == 0
    double_ok &= all(r.get("value") == core_lex.get("daiin", {}).get("value")
                     and r.get("sense_or_rule_ref") == "CORE:daiin"
                     for r in rows if r.get("raw") == "daiin")
    add("all_daiin_occurrences_and_immediate_double_preserved", double_ok,
        f"Exact token counts IT2a/ZL3b/RF1b={d_counts}; adjacent double loci IT2a/ZL3b/RF1b={double_occurrences}. Every exact daiin keeps its frozen core value, including both members of the pair.")

    repeated_forms = ["qokcho", "dshey", "cho", "chor", "chol", "shol", "qokaiin", "daiity"]
    repeated_ok = True
    repeated_report = {}
    for form in repeated_forms:
        vals = {r.get("value") for r in rows if r.get("raw") == form and r.get("value") is not None}
        repeated_report[form] = {"occurrences": sum(r.get("raw") == form for r in rows), "assigned_values": sorted(vals)}
        repeated_ok &= len(vals) <= 1
    add("fixed_recurrent_surface_values", repeated_ok,
        f"Repeated exact forms retain one assigned whole-form value; counts and assigned values: {repeated_report}. Unknown alternate spellings remain separate.")

    profile = jload(ROOT / "experiments/yolo/gdt1094_f25v_source_package_whole_reading/src/WORD_PROFILES.json")
    profile_by_form = {p["form"]: p for p in profile.get("profiles", [])}
    salient_profile = {}
    profile_ok = profile.get("source_receipt", {}).get("guard_stats", {}).get("selected", 0) > 0
    for form in ["daiin", "chor", "chol", "shol", "qokcho"]:
        p = profile_by_form.get(form)
        ed = p.get("editions", {}).get("IT2a", {}) if p else {}
        profile_ok &= bool(ed)
        salient_profile[form] = {"IT2a_count": ed.get("count"), "IT2a_pages": ed.get("pages_with_form"),
                                  "edition_scope": "exact raw form; exploratory prior"}
    add("high_frequency_costs_referenced_to_registered_profiles", profile_ok,
        f"The common-form risk is checked against the pinned exact-form profile, not interpreted as a grammatical or semantic result: {salient_profile}.")

    # Record semantic coverage honestly; this is not a decoder verdict.
    source_choice_ok = (
        "base-text" in account.get("whole_source_choice", "")
        and "beta" in account.get("whole_source_choice", "").lower()
        and "do not combine" in author_md.lower()
        and "eats this herb" in author_md.lower()
        and "aestu" in author_md
    )
    add("base_text_and_beta_version_separation_recorded", source_choice_ok,
        "The author selects the CXIII base version and explicitly keeps beta eating/aestu omission separate; this checks version documentation, not historical or Voynich meaning.",
        "recorded_claim_check")

    author_plain = re.sub(r"[\\*_`]", "", author_md.lower())
    explicit_open_bindings = all(s in author_plain for s in [
        "not a complete syntax/argument derivation",
        "human patient in the hair function",
        "hare → plant → name causal attachment",
        "not derived by frozen rules",
    ])
    add("underived_recipient_habitat_and_naming_links_reported", explicit_open_bindings,
        "The author explicitly retains the hair-function recipient, habitat/argument bindings, and hare-to-plant-to-name attachment as underived; the proposed connected prose is not counted as a complete reading.",
        "manual_account_scope_check")

    wording_status = {
        "classification": "REGISTERED_WORDING_AMBIGUITY",
        "strict_literal_method_reading": "METHOD prohibits a named animal/plant, which conflicts with CORE C0 labels qokaiin=hare and daiity=hare-plant/epithet.",
        "stated_nonidentity_c0_reading": "Core/account mark those as tentative whole-form C0 labels, not pictured species, taxon, or identified native owner; root states the intended method restriction concerns native-owner identification.",
        "resolution": "NOT_SILENTLY_RESOLVED_BY_VALIDATOR",
        "meaning_credit": 0,
    }
    add("method_scope_wording_ambiguity_preserved", True,
        "The phrase and the competing literal versus nonidentity-C0 readings are reported as an ambiguity; this validation neither edits frozen METHOD nor awards semantic support.",
        "registered_protocol_ambiguity")

    # The account is explicitly a manual C0 attempt with admitted underived links.
    semantic_state = {
        "whole_account_status": "PARTIAL_LEXICAL_ACCOUNT_NO_COMPLETE_READING",
        "lexical_bookkeeping": "PASS" if row_values_ok and refs_ok and counts_ok else "FAIL",
        "shared_plant_values": "CONSISTENT_C0_ASSIGNMENT; discourse identity remains conjectural/underived",
        "separate_functions": "PROPOSED; habitat and hair/recipient syntax not derived",
        "prescription_recipients": "first is a tentative feverish-person guess; hair/eye recipient remains untyped/unread",
        "naming_reason_consumer": "NOT_DERIVED: author expressly leaves cross-line hare→plant→name causal attachment underbound",
        "paragraph_basis": "IT2a and ZL3b mark one paragraph; RF1b has no paragraph boundary flags in the registered projection, so no RF boundary agreement is inferred",
        "high_frequency_transfer_debt": "SUPPORTED_AS_COST; registered exact-form counts establish commonness only",
        "semantic_refutation_by_context_breadth": "NOT_ESTABLISHED_BY_REGISTERED_PROFILES; they contain distributional metadata, not independent semantic labels for these forms",
        "meaning_truth": "NOT_ASSESSED",
        "independent_confirmed_meanings": 0,
        "significance": "NOT_CLAIMED",
    }

    validation_status = "PASS_PROTOCOL_ACCOUNTING" if ALL_OK else "FAIL_PROTOCOL_ACCOUNTING"
    doc = {
        "experiment": "GDT1143",
        "validation_status": validation_status,
        "validation_plan_sha256": plan_hash,
        "validation_scope": "Independent source-pin, freeze, row-accounting, recurring-value, and contract checks. No new source/target/image access and no decoder or semantic truth test.",
        "core_freeze": {
            "core_sha256": sha(core_json_path),
            "core_md_sha256": sha(core_md_path),
            "core_receipts_identical": receipts_equal,
            "author_after_freeze_receipt_verified": chronology_ok,
        },
        "registered_inputs": pin_results,
        "source_accounting": {
            "full_passage_reader_counts": full_counts,
            "paragraph_boundary_counts": boundary_counts,
            "registered_raw_group_rows": len(raw_rows),
            "account_rows": len(rows),
            "account_to_input_mismatches": mismatch_rows,
            "account_status_counts": dict(status_counts),
            "daiin_counts_by_reader": d_counts,
            "adjacent_daiin_loci_by_reader": double_occurrences,
        },
        "frequent_form_profiles": salient_profile,
        "recurrent_form_assignments": repeated_report,
        "semantic_coverage_assessment": semantic_state,
        "registered_wording_ambiguity": wording_status,
        "checks": CHECKS,
        "limits": [
            "C0 assignment and complete row accounting do not demonstrate grammar, recipient binding, a shared discourse referent, a consumed naming reason, or a correct translation.",
            "This is one exposed physical page with alternate readings of the same manuscript; no blindness or independent confirmation is claimed.",
            "The CML IV base and apparatus beta are separate historical variants; neither identifies a Voynich exemplar.",
            "The frozen METHOD wording is unchanged; its named-animal/plant clause remains a recorded ambiguity, not silently overridden.",
        ],
    }
    OUT_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# GDT1143 validation",
        "",
        f"**Protocol/accounting validation: {validation_status} ({sum(c['passed'] for c in CHECKS)}/{len(CHECKS)} checks). Meaning: NOT ASSESSED.** This is not a parser, decoder, semantic test, or visual review.",
        "",
        f"The independent row reconstruction reconciles {len(rows)} accounted occurrences with the registered passage: {full_counts}. The exact-reader row spellings and separators are checked against the page-bounded GDT1094 input. Status counts are {dict(status_counts)}. All SOURCE pins and core/author byte receipts are checked. The exact daiin counts and immediate doubles are retained as recorded in VALIDATION.json.",
        "",
        "Repeated surface values and paid C0 references are internally consistent. The proposed value of `daiin` consistently denotes the same plant at the lexical-assignment level; this does not establish that all those occurrences refer to one discourse entity. The author calls the construction manual and explicitly leaves the recipient for the eye/hair function and the hare→plant→naming connection underived. Habitat attachments are also not derived. Therefore this is a complete lexical inventory with a partial C0 proposal, not a complete connected reading.",
        "",
        "The author selects the CXIII base-text version and explicitly excludes the beta eating variant and its `aestu` omission. The historical source does not establish a Voynich source witness. Confirmed meanings remain zero.",
        f"Paragraph evidence is asymmetric: registered IT2a and ZL3b flags each mark a single f25v paragraph start/end, while RF1b has no boundary flags in this projection. The latter is unscored/missing boundary evidence, not proof of no paragraph and not agreement; see {boundary_counts}.",
        "",
        "The frozen METHOD phrase prohibiting a “named animal/plant” sits in tension with C0 whole-form labels `hare` and `hare-plant/epithet`. The account distinguishes these as provisional lexical guesses, not pictured species, taxon, or identified native owner. This is retained as `REGISTERED_WORDING_AMBIGUITY`, not silently resolved by the validator; METHOD remains unchanged.",
        "The frequent-form profiles support treating the guesses as high transfer-debt assignments. They do not supply semantic counterexamples, so the AUTHOR_READING.md phrase “contradicted by the breadth of their known contexts” is not established by the registered frequency profiles alone and is not treated as a semantic refutation here.",
        "",
        "Per-check evidence and detailed counts are in [VALIDATION.json](VALIDATION.json). Reproduce with `python experiments/yolo/gdt1143_mixed_herbal_entry_whole_reading/src/validate.py`.",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"GDT1143 validation: {validation_status} ({sum(c['passed'] for c in CHECKS)}/{len(CHECKS)} checks)")
    return 0 if ALL_OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
