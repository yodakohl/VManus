#!/usr/bin/env python3
"""Independent artifact replay for GDT1045; does not import src/run.py."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys


def repo_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "AGENTS.md").is_file() and (p / ".git").exists():
            return p
    raise RuntimeError("repository root not found")


ROOT = repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt1045_f85_fixed_recipient_incorporation"
LOCK_PATH = EXP / "src/PREREG_LOCK.json"
SPEC_PATH = EXP / "src/SPEC.json"
PROJECTION = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv"
DRAFT = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926/until_s_draft/DRAFT.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def jcol(value: str):
    return json.loads(value)


def block_for(locus: int, blocks: dict[str, list[int]]) -> str:
    hits = [name for name, loci in blocks.items() if locus in loci]
    if len(hits) != 1:
        raise AssertionError(f"locus {locus} maps to {hits}")
    return hits[0]


def main() -> int:
    errors: list[str] = []
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)

    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    check(lock.get("status") == "FROZEN_BEFORE_FOLLOWUP_ROW_ENUMERATION", "unexpected preregistration lock status")
    check(sha(SPEC_PATH) == lock["inputs"].get("experiments/yolo/gdt1045_f85_fixed_recipient_incorporation/src/SPEC.json"), "SPEC hash differs from lock")
    check(sha(PROJECTION) == lock["projection"]["sha256"], "projection hash differs from lock")
    check(sha(DRAFT) == lock["inputs"].get("research_registry/proposals/laufenberg_f85r2_20260926/until_s_draft/DRAFT.json"), "frozen whole-form draft hash differs from lock")
    for rel, expected in lock["inputs"].items():
        path = ROOT / rel
        check(path.is_file() and sha(path) == expected, f"frozen input missing/hash mismatch: {rel}")

    draft = json.loads(DRAFT.read_text(encoding="utf-8"))
    baseline = {}
    for form, item in draft["fixed_idea550_bindings"].items():
        baseline[form] = (item["type"], item["meaning"])
    for form, item in draft["new_whole_form_values"].items():
        if form in baseline:
            check(False, f"duplicate baseline form across frozen dictionaries: {form}")
        baseline[form] = (item["type"], item["meaning"])
    check(len(baseline) == 24, f"frozen dictionary has {len(baseline)} rather than 24 values")

    source = read_tsv(PROJECTION)
    check(len(source) == 473, f"projection row count {len(source)} != 473")
    check(len({r["source_group_id"] for r in source}) == len(source), "projection group IDs are not unique")
    editions = list(spec["editions"])
    check(set(r["edition"] for r in source) == set(editions), "projection editions differ from frozen SPEC")

    # Reconstruct every projected row's complete block context from the raw, guarded projection.
    by_ed_block: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    context_expected = []
    for r in source:
        loc = int(r["locus"].rsplit(".", 1)[1])
        block = block_for(loc, spec["blocks"])
        by_ed_block[(r["edition"], block)].append(r)
        typ, meaning = baseline.get(r["ivtff_group_raw"], ("UNASSIGNED", ""))
        context_expected.append({**r, "line_number": str(loc), "block": block,
                                 "baseline_type": typ, "baseline_meaning": meaning})
    context_actual = read_tsv(EXP / "artifacts/CONTEXTS.tsv")
    check(context_actual == context_expected, f"complete contexts differ from independent reconstruction ({len(context_actual)} actual/{len(context_expected)} expected)")
    projected_baseline_forms = {r["ivtff_group_raw"] for r in source} & set(baseline)
    check(projected_baseline_forms == set(baseline),
          "the full 24-form baseline dictionary is not represented in the source projection")

    frame = spec["licensed_frame"]["required_tokens"]
    frame_tokens = {key: val[1] for key, val in frame.items()}
    by_id = {r["source_group_id"]: r for r in source}
    qod = [r for r in source if r["ivtff_group_raw"].startswith("qod")]
    check(len(qod) == 10, f"literal qod-initial occurrence count {len(qod)} != 10")
    source_form_counts = Counter(r["ivtff_group_raw"] for r in qod)
    check(source_form_counts == Counter({"qodaiin": 5, "qodain": 3, "qodar": 2}), f"literal qod form counts differ: {dict(source_form_counts)}")

    case_expected = []
    for r in qod:
        loc = int(r["locus"].rsplit(".", 1)[1])
        block = block_for(loc, spec["blocks"])
        raw = r["ivtff_group_raw"]
        remainder = raw[3:]
        for candidate in spec["candidates"]:
            if remainder in spec["type_rules"]:
                rule = spec["type_rules"][remainder]
                rem_type = rule["fixed_type"]
                type_result = rule[candidate]
                if type_result == "TYPED" or type_result == "TYPED_WITH_LOC_OWNER":
                    pred = "ATTRACT(f,x,Goal=r)"
                    goal = rule["goal"]
                    extra = type_result == "TYPED_WITH_LOC_OWNER"
                else:
                    pred, goal, extra = "", "", False
            else:
                rem_type, type_result = "UNASSIGNED", "UNBOUND_COMPONENT"
                pred, goal, extra = "", "", False

            availability = {}
            if block == spec["licensed_frame"]["block"] and loc == spec["licensed_frame"]["predicate_locus"]:
                for frame_name, token in frame_tokens.items():
                    frame_locus = frame[frame_name][0]
                    availability[frame_name] = any(
                        int(x["locus"].rsplit(".", 1)[1]) == frame_locus and x["ivtff_group_raw"] == token
                        for x in source if x["edition"] == r["edition"]
                    )
            typed = type_result in ("TYPED", "TYPED_WITH_LOC_OWNER")
            if not typed:
                binding = "NO_TYPED_OUTPUT"
            elif block == spec["licensed_frame"]["block"] and loc == spec["licensed_frame"]["predicate_locus"] and all(availability.values()):
                binding = "AUTHORED_S_GOAL_AGREEMENT"
            elif block == spec["licensed_frame"]["block"]:
                binding = "MISSING_EXACT_S_FRAME"
            else:
                binding = "NO_LICENSED_TRANSFER_FRAME"
            missing = [] if availability and all(availability.values()) else (
                [k for k, present in availability.items() if not present] if availability else ["NO_LICENSED_BLOCK_FRAME"]
            )
            context = by_ed_block[(r["edition"], block)]
            unassigned = [{"id": x["source_group_id"], "raw": x["ivtff_group_raw"]}
                          for x in context if x["ivtff_group_raw"] not in baseline]
            case_expected.append({
                "candidate": candidate,
                "edition": r["edition"],
                "source_group_id": r["source_group_id"],
                "locus": r["locus"],
                "group_index": r["source_group_index"],
                "block": block,
                "raw": raw,
                "remainder": remainder,
                "remainder_type": rem_type,
                "type_result": type_result,
                "predicted_predicate": pred,
                "goal_derivation": goal,
                "extra_lift": str(extra).lower(),
                "binding_result": binding,
                "frame_token_availability": json.dumps(availability, sort_keys=True, separators=(",", ":")),
                "missing_frame": json.dumps(missing, separators=(",", ":")),
                "context_group_count": str(len(context)),
                "baseline_unassigned_groups": str(len(unassigned)),
                "baseline_unassigned_context": json.dumps(unassigned, ensure_ascii=False, separators=(",", ":")),
                "meaning_confirmed": "false",
            })
    cases_actual = read_tsv(EXP / "artifacts/CASES.tsv")
    # JSON-valued TSV fields are parsed before comparison, so harmless key ordering is immaterial.
    json_fields = {"frame_token_availability", "missing_frame", "baseline_unassigned_context"}
    normalized_actual = []
    normalized_expected = []
    for rows, dest in ((cases_actual, normalized_actual), (case_expected, normalized_expected)):
        for row in rows:
            dest.append({k: jcol(v) if k in json_fields else v for k, v in row.items()})
    check(normalized_actual == normalized_expected,
          f"occurrence table differs from independent reconstruction ({len(cases_actual)} actual/{len(case_expected)} expected)")

    # Recompute the compact tallies only from independently reconstructed case rows.
    expected_result = {
        "status": "FIXED_FAMILY_TYPE_AND_BINDING_CAPACITY_ONLY",
        "source_rows": len(source),
        "f85_loci_per_edition": 24,
        "baseline_values": len(baseline),
        "family_occurrences": len(qod),
        "family_forms": dict(sorted(source_form_counts.items())),
        "candidate_rows": len(case_expected),
        "candidates": {},
        "independent_meaning_confirmation": 0,
        "new_target_access": False,
        "new_whole_senses": 0,
        "new_atomic_dictionary_entries": 0,
        "new_derived_form_predictions": ["qodain"],
        "new_whole_senses_field_scope": "No new atomic sense values; qodain receives a new conditional derived form-to-meaning prediction.",
        "alternative_reader_independence": False,
        "counterexample_selection": "all literal qod-initial groups",
        "decision": "No productive or translated prefix selected. LOC_OWNER is an extra typed hypothesis; transfer requires written reference rules."
    }
    for candidate in spec["candidates"]:
        rows = [r for r in case_expected if r["candidate"] == candidate]
        expected_result["candidates"][candidate] = {
            "type_results": dict(Counter(r["type_result"] for r in rows)),
            "binding_results": dict(Counter(r["binding_result"] for r in rows)),
            "nondevelopment_goal_comparisons": 0,
            "extra_loc_owner_applications": sum(r["extra_lift"] == "true" for r in rows),
        }
    actual_result = json.loads((EXP / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    check(actual_result == expected_result, "compact RESULT differs from independently reconstructed values/tallies")

    if errors:
        print("FAIL")
        for e in errors:
            print("- " + e)
        return 1
    print("PASS: frozen input hashes; all 473 complete projected contexts; 24 fixed baseline values; all 10 raw qod-initial groups / 20 candidate rows; five S.16 frame-token availability checks; complete block contexts and unassigned lists; compact tallies.")
    print("Ceiling: deterministic type/reference-availability replay only. This is not independent meaning confirmation, a productive-prefix result, a semantic grammar rejection, or confirmation of any reading.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
