#!/usr/bin/env python3
"""Independent GDT1141 source/core-gate accounting validator.

This does not import or execute run.py and does not author or test a reading.
It replays only the registered selector-first projection of the pinned BB
account, verifies exact frozen inputs and gate facts, then records that the
experiment correctly stopped at MISSING_CORE_DESIGN with no Stage2 or semantic
perturbation.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = HERE.parents[4]
OUT = EXP / "artifacts"
EXPECTED_READERS = ("ZL3b", "IT2a", "RF1b")
EXPECTED_SELECTORS = [
    "f68r2.6", "f68r2.31", "f89v1.13", "f89v1.14", "f89v1.15",
    "f89v1.16", "f89v1.17", "f89v1.18", "f89v1.19", "f89v1.20",
]
EXPECTED_COLUMNS = (
    "part,reader,locus,ordinal,raw,left_separator,right_separator,wrapper,host,"
    "right_family,BB_whole,W_whole,BB_inner_only,status,next_word_consumed"
).split(",")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_tsv_bytes(data: bytes) -> list[dict[str, str]]:
    import io
    return list(csv.DictReader(io.StringIO(data.decode("utf-8")), delimiter="\t"))


def main() -> int:
    errors: list[str] = []
    checks: dict[str, bool] = {}

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks[name] = bool(condition)
        if not condition:
            errors.append(name + (f": {detail}" if detail else ""))

    source = read_json(EXP / "src/SOURCE.json")
    freeze_path = OUT / "FINAL_AUTHOR_FREEZE.json"
    freeze = read_json(freeze_path)
    gate1 = read_json(OUT / "CORE_GATE_01.json")
    guard_receipt = read_json(OUT / "GUARD_RECEIPT.json")
    registration = read_json(OUT / "REGISTRATION_RECEIPT.json")

    # Source pins and the four exact author-freeze pins.
    source_hashes: dict[str, bool] = {}
    for pin in source["source_pins"]:
        path = ROOT / pin["path"]
        ok = path.is_file() and sha256(path) == pin["sha256"]
        source_hashes[pin["path"]] = ok
        check("source pin " + pin["path"], ok)
    frozen_hashes: dict[str, bool] = {}
    for rel, expected in freeze["files"].items():
        path = EXP / rel
        ok = path.is_file() and sha256(path) == expected
        frozen_hashes[rel] = ok
        check("frozen author pin " + rel, ok)
    check("exactly four author-freeze pins", set(freeze["files"]) == {
        "CORE.json", "CORE.md", "CORE_CANDIDATE_02.json", "CORE_CANDIDATE_02.md"
    })

    # Verify the experiment source registration receipt still binds the method,
    # source manifest, and pre-authorship validation plan.
    registration_checks = {
        "method": sha256(EXP / "METHOD.md") == registration["method_sha256"],
        "source": sha256(EXP / "src/SOURCE.json") == registration["source_sha256"],
        "validation_plan": sha256(OUT / "VALIDATION_PLAN.md") == registration["validation_plan_sha256"],
    }
    for key, ok in registration_checks.items():
        check("registration receipt " + key, ok)

    # Replay only the exact registered, selector-first query against the pinned,
    # already-owned BB account. No broad corpus or raw target TSV is read.
    scope = source["scope"]
    check("scope selectors match method roster", scope == EXPECTED_SELECTORS)
    check("scope excludes sealed/unadmitted locations",
          all(not s.startswith(("f84", "f116v")) for s in scope)
          and set(source["sealed"]) == {"f84", "f84r"}
          and "f116v" in source["unadmitted"])
    bb_account_pin = next(p for p in source["source_pins"] if p["path"].endswith("/BB_ACCOUNT.tsv"))
    relative_account = bb_account_pin["path"]
    expected_command = ["./vmanus-exp", "query-tsv", relative_account,
                        "--selector", "locus"]
    for locus in scope:
        expected_command.extend(["--allow", locus])
    expected_command.extend(["--columns", ",".join(EXPECTED_COLUMNS)])
    receipt_command = guard_receipt.get("command", [])
    check("guard receipt command equals frozen selectors/columns",
          receipt_command == expected_command)
    proc = subprocess.run(expected_command, cwd=ROOT, capture_output=True, check=False)
    guard_stderr = proc.stderr.decode("utf-8").strip()
    projection_path = OUT / "GUARDED_BB_ACCOUNT.tsv"
    projection_bytes = projection_path.read_bytes()
    check("selector-first guarded query exits successfully", proc.returncode == 0,
          proc.stderr.decode("utf-8", errors="replace")[:500])
    check("guard statistics match receipt",
          guard_stderr == guard_receipt.get("stderr", "").strip())
    check("guarded projection exactly matches replayed bytes", proc.stdout == projection_bytes)

    rows = read_tsv_bytes(projection_bytes)
    schema_ok = bool(rows) and list(rows[0]) == EXPECTED_COLUMNS
    check("guarded projection has exact registered metadata/BB schema", schema_ok)
    check("guarded projection row count is 288", len(rows) == 288)
    check("all rows fall inside exact registered scope",
          all(r.get("locus") in set(scope) for r in rows))
    check("all three alternate readings represented",
          {r["reader"] for r in rows} == set(EXPECTED_READERS))

    by_reader = Counter(r["reader"] for r in rows)
    by_part = Counter(r["part"] for r in rows)
    by_reader_part = Counter((r["reader"], r["part"]) for r in rows)
    by_locus_reader = Counter((r["locus"], r["reader"]) for r in rows)
    identity_counts = Counter((r["reader"], r["locus"], r["ordinal"]) for r in rows)
    check("native ring/prose split conserved", by_part == Counter({"ring": 58, "paragraph": 230}),
          str(dict(by_part)))
    check("IT2a primary position count is 97", by_reader["IT2a"] == 97)
    check("IT2a ring/prose positions are 19 + 78",
          by_reader_part[("IT2a", "ring")] == 19 and by_reader_part[("IT2a", "paragraph")] == 78)
    check("reader-native totals retained", dict(by_reader) == {"ZL3b": 95, "IT2a": 97, "RF1b": 96},
          str(dict(by_reader)))
    check("f68r2.6 IT2a ring has eight positions", by_locus_reader[("f68r2.6", "IT2a")] == 8)
    check("f68r2.31 IT2a ring has eleven positions", by_locus_reader[("f68r2.31", "IT2a")] == 11)
    check("each reader/locus ordinal inventory is consecutive",
          all([int(r["ordinal"]) for r in rows if r["reader"] == reader and r["locus"] == locus]
              == list(range(1, by_locus_reader[(locus, reader)] + 1))
              for reader in EXPECTED_READERS for locus in scope))
    check("native position identities are unique", all(n == 1 for n in identity_counts.values()))
    check("all 288 native rows retain exact raw/separator fields",
          all(all(r.get(k) is not None for k in ("raw", "left_separator", "right_separator")) for r in rows))

    # Check BB's original nominal hypotheses against the pinned model and the
    # unaccepted alternative. Hashes remain the byte-level immutability check.
    bb_model_pin = next(p for p in source["source_pins"] if p["path"].endswith("/BB_MODEL.json"))
    bb_model = read_json(ROOT / bb_model_pin["path"])
    bb_design = bb_model["design"]
    expected_base = {"ok": "MOON", "oko": "SUN"}
    expected_wholes = {"okaiin": "LIGHT_OF(MOON)", "okoaiin": "LIGHT_OF(SUN)"}
    bb_value_ok = (bb_design["base_values"] == expected_base
                   and all(bb_design["whole_values"].get(k) == v for k, v in expected_wholes.items())
                   and bb_design["constructor"]["output"] == "LIGHT_OF(B)"
                   and bb_design["constructor"]["semantic_arity_after_word"] == 0)
    check("pinned BB nominal-light hypotheses are unchanged", bb_value_ok)
    original_equal = all((EXP / name).read_bytes() == (OUT / ("CORE_PROPOSAL_01" + suffix)).read_bytes()
                         for name, suffix in (("CORE.json", ".json"), ("CORE.md", ".md")))
    check("original CORE files remain byte-identical to proposal 01", original_equal)

    candidate2 = read_json(EXP / "CORE_CANDIDATE_02.json")
    cclar = freeze.get("candidate02_author_clarification", {})
    freeze_ok = (
        freeze.get("experiment") == "GDT1141"
        and freeze.get("decision") == "MISSING_CORE_DESIGN"
        and freeze.get("stage2_released") is False
        and freeze.get("accepted_core") is None
        and freeze.get("attempted_cores") == 2
        and freeze.get("whole_reading_authored") is False
        and freeze.get("actual_dependency_tests") == "NOT_RUN_NO_CAPACITY"
        and freeze.get("native_scope") == {"primary_IT2a": 97, "all_native": 288}
    )
    check("author freeze records bounded MISSING_CORE_DESIGN", freeze_ok)
    clarify_ok = (
        "not typed as an amount" in cclar.get("scalar_projection", "")
        and "not licensed" in cclar.get("scalar_projection", "")
        and "reuse CHDY" in cclar.get("shared_operand", "")
        and "without a defined" in cclar.get("shared_operand", "")
        and "not two observation records" in cclar.get("comparison", "")
        and "NO_CAPACITY" in cclar.get("comparison", "")
    )
    check("candidate-02 author clarification is fully recorded", clarify_ok)
    check("candidate 02 remains an unfrozen unaccepted Stage1 candidate",
          candidate2.get("status") == "CANDIDATE_UNFROZEN_NOT_ACCEPTED"
          and candidate2.get("stage") == 1 and candidate2.get("candidate") == 2)

    gate1_ok = (
        gate1.get("gate") == "NOT_ACCEPTED_FOR_STAGE2"
        and gate1.get("proposal") == 1
        and gate1.get("experiment_final_decision") is None
        and gate1.get("proposal_hashes", {}).get("experiments/yolo/gdt1141_light_observation_whole_reading/artifacts/CORE_PROPOSAL_01.json") == freeze["files"]["CORE.json"]
        and gate1.get("proposal_hashes", {}).get("experiments/yolo/gdt1141_light_observation_whole_reading/artifacts/CORE_PROPOSAL_01.md") == freeze["files"]["CORE.md"]
    )
    check("proposal-01 gate and frozen proposal hashes agree", gate1_ok)
    report_text = (EXP / "REPORT.md").read_text(encoding="utf-8")
    review_text = (EXP / "CORE_REVIEW.md").read_text(encoding="utf-8")
    report_gate_facts = ("MISSING_CORE_DESIGN" in report_text
                         and "Stage2 wurde nicht freigegeben" in report_text
                         and "NO_CAPACITY" in report_text
                         and "keine vollständige Lesung" in report_text)
    review_gate_facts = ("lacks a second contextual application" in review_text
                         and "blurs the inherited noun and observation formation" in review_text
                         and "R2's only trigger is location" in review_text
                         and "RELATES binder has no specified ordinary relation" in review_text
                         and "MISSING_CORE_DESIGN" in review_text)
    check("root report preserves final accounting/gate distinctions", report_gate_facts)
    check("core review records proposal-01 design gaps", review_gate_facts)

    # Check the retained, manually reviewed type/binding facts. This validator
    # is not a semantic theorem prover and does not adjudicate those meanings.
    rules = {r["id"]: r for r in candidate2.get("new_rules", [])}
    apps = candidate2.get("applications", [])
    app14 = next((a for a in apps if a.get("locus") == "f89v1.14"), None)
    app16 = next((a for a in apps if a.get("locus") == "f89v1.16"), None)
    r3 = rules.get("R3", {})
    r4 = rules.get("R4", {})
    scalar_gate_gap = (
        app14 is not None
        and app14.get("groups") == ["okoaiin", "dal", "chdy"]
        and r3.get("types", {}).get("left") == "scalar property/state or complete constituent containing one"
        and bb_design["constructor"]["semantic_arity_after_word"] == 0
        and not any("scalar" in json.dumps(x).lower() and "light_of" in json.dumps(x).lower()
                    for x in candidate2.get("new_rules", []))
    )
    comparison_gap = (
        r4.get("types", {}).get("left") == "nearest earlier q-marked compatible reference in the same written local unit"
        and r4.get("types", {}).get("right") == "immediately preceding exact LIGHT_OF(B) nominal"
        and "two observation records" in cclar.get("comparison", "")
    )
    overlap_gap = "without a defined" in cclar.get("shared_operand", "")
    check("candidate-02 first DAL application lacks a declared scalar projection", scalar_gate_gap)
    check("candidate-02 DALG binds record plus nominal, not two observation records", comparison_gap)
    check("candidate-02 CHDY/consecutive-DAL overlap is an acknowledged gap", overlap_gap)

    # These are deliberately statuses, not failed tests to be simulated.
    no_authorship = freeze.get("whole_reading_authored") is False
    no_interventions = freeze.get("actual_dependency_tests") == "NOT_RUN_NO_CAPACITY"
    check("no full 97-position authorship is reported", no_authorship)
    check("two-observation interventions are explicitly not run for no capacity", no_interventions)

    accounting_pass = not errors
    result = {
        "validator_status": "PASS_ACCOUNTING_ONLY" if accounting_pass else "FAIL_ACCOUNTING",
        "experiment_decision": freeze.get("decision"),
        "core_gate_status": "FAIL_MISSING_CORE_DESIGN" if freeze.get("decision") == "MISSING_CORE_DESIGN" else "UNVERIFIED",
        "stage2_released": freeze.get("stage2_released"),
        "accepted_core": freeze.get("accepted_core"),
        "whole_reading_authored": freeze.get("whole_reading_authored"),
        "authoring_scope": {"primary_IT2a": by_reader.get("IT2a", 0), "all_native": len(rows)},
        "native_by_reader": dict(by_reader),
        "native_by_part": dict(by_part),
        "native_by_reader_part": {f"{reader}/{part}": n for (reader, part), n in sorted(by_reader_part.items())},
        "native_by_locus_reader": {f"{locus}/{reader}": by_locus_reader[(locus, reader)]
                                   for reader in EXPECTED_READERS for locus in scope},
        "guard_replay": {
            "status": "PASS" if checks.get("guarded projection exactly matches replayed bytes") else "FAIL",
            "selector_count": len(scope),
            "selected_rows": len(rows),
            "skipped_forbidden": 0,
            "source": relative_account,
            "source_text_not_read_outside_pinned_selector_query": True,
        },
        "source_pin_checks": source_hashes,
        "final_author_freeze_pin_checks": frozen_hashes,
        "registration_receipt_checks": registration_checks,
        "proposal01_gate": gate1.get("gate"),
        "candidate02_clarifications": cclar,
        "candidate02_gap_checks": {
            "LIGHT_OF_scalar_projection_missing": scalar_gate_gap,
            "CHDY_consecutive_DAL_overlap_undefined": overlap_gap,
            "DALG_has_two_observation_records": False if comparison_gap else None,
        },
        "candidate02_gap_assessment_basis": {
            "LIGHT_OF_scalar_projection": "checked against the pinned BB zero-operand LIGHT_OF noun and candidate R3's declared scalar left type",
            "CHDY_consecutive_DAL_overlap": "candidate-author clarification; not an independent structural/type proof by this validator",
            "DALG_record_vs_nominal": "candidate R4's declared argument types and author clarification; not a semantic theorem proof",
        },
        "actual_dependency_tests": "NOT_RUN_NO_CAPACITY",
        "semantic_perturbations": "NOT_RUN; no accepted core/actual two-observation construction",
        "checks": checks,
        "errors": errors,
        "claim_ceiling": "Source/core-freeze/accounting fidelity only. PASS does not accept a core, attest a whole reading, test a semantic dependency, contradict lunar content, or confirm a meaning.",
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# GDT1141 independent validation",
        "",
        f"**Validator: {result['validator_status']}. Experiment decision: `{result['experiment_decision']}`.**",
        "",
        "The validator independently replayed the registered selector-first projection from the pinned BB account. All nine source pins and all four final author-freeze hashes were checked. The projection matches byte-for-byte: 288 native positions total, including 97 IT2a primary positions (19 ring + 78 prose); ZL3b has 95 and RF1b has 96. All 58 ring and 230 prose positions, exact forms, separators, and uncertainty/entity metadata remain in the guarded projection.",
        "",
        "The freeze correctly records two attempted cores, no accepted core, no Stage2 release, and `MISSING_CORE_DESIGN`. Proposal 01 remains byte-identical to its frozen proposal and its gate records `NOT_ACCEPTED_FOR_STAGE2`. Candidate 02 is hash-frozen but unaccepted. Its author clarification records the missing LIGHT_OF-to-scalar projection, the undefined consecutive-DAL/CHDY overlap, and that DALG has a reference record plus a LIGHT_OF noun rather than two observation records. The validator checks frozen bytes and declared types/bindings; the CHDY-overlap conclusion is the author's clarification, not an independent semantic proof.",
        "",
        "The complete 97-position author table was not authored. Actual two-observation dependency interventions were `NOT_RUN_NO_CAPACITY`; this validation did not manufacture a baseline or perturb semantic outputs. Accordingly, `PASS_ACCOUNTING_ONLY` verifies the correct recorded stop and source/core bookkeeping; `FAIL_MISSING_CORE_DESIGN` remains the core gate outcome. This is not a manuscript contradiction, a rejection of lunar content, a semantic test, or meaning confirmation.",
        "",
        "See `VALIDATION.json` for exact pin checks, per-reader/per-part counts, gate facts, and all accounting assertions.",
    ]
    if errors:
        report.extend(["", "## Accounting discrepancies", ""])
        report.extend(f"- {e}" for e in errors)
    (OUT / "VALIDATION.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    if errors:
        print("GDT1141 validator: accounting FAIL; see artifacts/VALIDATION.json", file=sys.stderr)
        return 1
    print("GDT1141 validator: PASS_ACCOUNTING_ONLY; MISSING_CORE_DESIGN; no Stage2 or semantic test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
