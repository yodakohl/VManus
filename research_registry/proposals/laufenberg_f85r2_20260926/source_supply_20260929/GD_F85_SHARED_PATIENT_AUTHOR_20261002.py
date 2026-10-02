"""One bounded, conditional PART attempt; never a whole target decoder.

Only the already-exposed GDT1042 projection at eleven registered loci is read,
through the selector-first guard. Profiles use an existing read-only cache.
"""
from __future__ import annotations
import copy, csv, datetime, hashlib, io, json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
STEM = "GD_F85_SHARED_PATIENT_AUTHOR_20261002"
SOURCE = "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/guarded_projection.tsv"
COLS = ["source_group_id", "edition", "locus", "page", "source_group_index", "source_group_count", "paragraph_start", "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw"]

# Declared before any reduction. These are paid C0 proposals, not learned units.
INVENTORY = {
    "frame": {"parts": ["p", "f", "ot"], "signature": "explicit BlockInput -> Frame", "action": "Return supplied scene frame without creating patient, examiner, specimen or observation."},
    "subject": {"parts": ["che", "ch"], "signature": "Frame -> Person", "action": "Project explicitly supplied described participant; never pictured actor by default."},
    "specimen": {"parts": ["d"], "signature": "Person -> Specimen", "action": "Select the unique supplied specimen whose actual owner is that person."},
    "diagnose": {"parts": ["ee"], "signature": "Specimen -> Description", "action": "Read supplied OBSERVE(examiner,specimen,sign), apply supplied sign-to-condition rule, and retain actual specimen owner and observation. Two primitive operations, not a bare label."},
    "assert": {"parts": ["y", "dy"], "signature": "Description|ConditionRead -> Assertion", "action": "Assert the actual owner-specific conditional content; no new observation or condition."},
    "reference": {"parts": ["ol", "qo", "she"], "signature": "latest actual Description -> same Description", "action": "Identity-preserving reference; most recent Description selection is a paid scope default."},
    "owner_reference": {"parts": ["k"], "signature": "Description -> OwnerReference", "action": "Retain actual description and its original described patient."},
    "read_condition": {"parts": ["e"], "signature": "OwnerReference -> ConditionRead", "action": "Check actual original owner identity, then read actual description condition, mode, specimen and evidence fields."},
    "owner": {"parts": ["o"], "signature": "Description -> Person", "action": "Return actual original described participant."},
    "support": {"parts": ["s"], "signature": "Person -> Description", "action": "Read supplied USE_SUPPORT(person,support) fact, preserving user as described subject; no specimen inference."},
    "retained_person": {"parts": ["aiin"], "signature": "latest actual written Person return -> same Person", "action": "Identity-preserving reference. No aN historical translation or unseen person donor."},
}
PARTS = {part: name for name, definition in INVENTORY.items() for part in definition["parts"]}
# Exact reductions used for the conditional program, not singleton clause macros.
TREES = {
    "pchedeey": ["p", "che", "d", "ee", "y"],
    "olkey": ["ol", "k", "e", "y"],
    "qokedy": ["qo", "k", "e", "dy"],
    "sheos": ["she", "o", "s"],
    "fcheey": ["f", "che", "ee", "y"],
    "otchs": ["ot", "ch", "s"],
    "shedor": ["she", "d", "or"],
    "oteey": ["ot", "ee", "y"],
    "aiin": ["aiin"],
}

def world(condition=True, patient_label="P", southern_patient_label=None):
    patient = {"type": "Person", "id": patient_label}
    examiner = {"type": "Person", "id": "X"}
    southern = patient if southern_patient_label is None else {"type": "Person", "id": southern_patient_label}
    specimen = {"type": "Specimen", "id": "U", "owner": patient}
    observation = {"type": "Observation", "id": "OBS", "agent": examiner, "specimen": specimen, "sign": "SIGN1" if condition else "SIGN0"}
    return {"frames": {"E": {"type": "Frame", "subject": patient, "pictured_actor": examiner}, "S": {"type": "Frame", "subject": southern, "pictured_actor": southern}},
            "specimens": [specimen], "observations": [observation], "rule": {"SIGN1": True, "SIGN0": False},
            "support": [{"user": southern, "object": "STAFF", "uses_support": True}], "same_patient_is_supplied_assumption": southern is patient}

def serial(value):
    if isinstance(value, dict): return {k: serial(v) for k, v in value.items()}
    if isinstance(value, list): return [serial(v) for v in value]
    return value

def reduce_word(raw, block, state, w, source_id):
    parts = TREES[raw]
    value = None
    trace = []
    for index, part in enumerate(parts):
        name = PARTS.get(part)
        before = value.get("type") if isinstance(value, dict) else None
        step = {"part": part, "function": name, "input_type": before}
        trace.append(step)
        try:
            if name is None: raise ValueError("UNDEFINED_PART:" + part)
            if name == "frame": value = w["frames"][block]
            elif name == "reference":
                if "description" not in state: raise ValueError("NO_WRITTEN_DESCRIPTION_SUPPLIER")
                value = state["description"]
                step["actual_supplier"] = state["description_source"]
            elif name == "retained_person":
                if "person" not in state: raise ValueError("NO_WRITTEN_PERSON_SUPPLIER")
                value = state["person"]
                step["actual_supplier"] = state["person_source"]
            else:
                expected = {"subject": ["Frame"], "specimen": ["Person"], "diagnose": ["Specimen"], "assert": ["Description", "ConditionRead"], "owner_reference": ["Description"], "read_condition": ["OwnerReference"], "owner": ["Description"], "support": ["Person"]}[name]
                if not isinstance(value, dict) or value.get("type") not in expected:
                    raise ValueError("TYPE_GAP:" + name + ":requires:" + "|".join(expected) + ":received:" + str(before))
                if name == "subject": value = value["subject"]
                elif name == "specimen":
                    matches = [s for s in w["specimens"] if s["owner"] is value]
                    if len(matches) != 1: raise ValueError("NO_UNIQUE_ACTUAL_OWNED_SPECIMEN")
                    value = matches[0]
                elif name == "diagnose":
                    matches = [o for o in w["observations"] if o["specimen"] is value and o["agent"] is w["frames"][block]["pictured_actor"]]
                    if len(matches) != 1: raise ValueError("NO_ACTUAL_OBSERVATION")
                    obs = matches[0]
                    if obs["sign"] not in w["rule"]: raise ValueError("NO_SUPPLIED_INFERENCE_RULE")
                    value = {"type": "Description", "mode": "DIAGNOSTIC", "patient": value["owner"], "specimen": value, "observation": obs, "condition": w["rule"][obs["sign"]]}
                elif name == "assert": value = {"type": "Assertion", "content": value}
                elif name == "owner_reference": value = {"type": "OwnerReference", "description": value, "patient": value["patient"]}
                elif name == "read_condition":
                    desc = value["description"]
                    if value["patient"] is not desc["patient"]: raise ValueError("ORIGINAL_OWNER_MISMATCH")
                    if "condition" not in desc: raise ValueError("MISSING_ACTUAL_CONDITION_FIELD")
                    value = {"type": "ConditionRead", "patient": value["patient"], "condition": desc["condition"], "mode": desc["mode"], "source_description": desc}
                elif name == "owner": value = value["patient"]
                elif name == "support":
                    matches = [s for s in w["support"] if s["user"] is value]
                    if len(matches) != 1: raise ValueError("NO_ACTUAL_SUPPORT_RELATION")
                    value = {"type": "Description", "mode": "SUPPORT_USE", "patient": value, "support_fact": matches[0], "condition": matches[0]["uses_support"]}
            if value.get("type") == "Person":
                state["person"], state["person_source"] = value, source_id + ":part" + str(index + 1)
            if value.get("type") == "Description":
                state["description"], state["description_source"] = value, source_id + ":part" + str(index + 1)
            step["output"] = serial(value)
        except ValueError as error:
            step["barrier"] = str(error)
            return {"status": "CONDITIONAL_CONSTRUCTION_GAP", "trace": trace, "barrier": str(error), "output": None}
    return {"status": "CONDITIONAL_REDUCED", "trace": trace, "barrier": None, "output": serial(value)}

def evaluate(rows, w):
    state, barrier, result = {}, None, []
    for row in rows:
        raw = row["ivtff_group_raw"]
        entry = {**row, "chosen_parts": TREES.get(raw), "written_target_derivation": False}
        if barrier:
            entry.update(status="UNCONSUMED_REMAINDER", barrier=barrier, conditional_program=None)
        elif raw not in TREES:
            barrier = row["source_group_id"]
            entry.update(status="UNKNOWN_PART_CONSTRUCTION", barrier=barrier, conditional_program=None)
        else:
            reduced = reduce_word(raw, "E" if int(row["locus"].split(".")[1]) < 12 else "S", state, w, row["source_group_id"])
            entry.update(status=reduced["status"], barrier=reduced["barrier"], conditional_program=reduced)
            if reduced["barrier"]: barrier = row["source_group_id"]
        result.append(entry)
    return {"first_gap": barrier, "rows": result, "completed_target_reading": False}

def main():
    output_path = HERE / (STEM + ".json")
    if output_path.exists(): raise SystemExit("Frozen author account already exists; do not overwrite")
    command = [str(ROOT / "vmanus-exp"), "query-tsv", SOURCE, "--selector", "locus"]
    for n in range(7, 18): command += ["--allow", "f85r2." + str(n)]
    command += ["--columns", ",".join(COLS)]
    guarded = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    rows = list(csv.DictReader(io.StringIO(guarded.stdout), delimiter="\t"))
    assert len(rows) == 159 and all(r["page"] == "f85r2" for r in rows)
    accounts = {}
    for edition in ("IT2a", "ZL3b", "RF1b"):
        selected = [r for r in rows if r["edition"] == edition]
        accounts[edition] = {}
        for block, lo, hi in (("E", 7, 11), ("S", 12, 17)):
            body = [r for r in selected if lo <= int(r["locus"].split(".")[1]) <= hi]
            assert len(body) == (27 if block == "E" else 26)
            accounts[edition][block] = evaluate(body, world())
    # These are conditional supplied-world examples, not post-barrier target execution.
    prefix = [r for r in rows if r["edition"] == "IT2a" and r["locus"] == "f85r2.7" and int(r["source_group_index"]) <= 3]
    counterfactuals = []
    for name, w in (("OBSERVED_WEAKNESS_TRUE", world(True)), ("OBSERVED_WEAKNESS_FALSE", world(False)), ("GLOBAL_PATIENT_RENAMING", world(True, "P2"))):
        reduced = evaluate(prefix, w)
        assertion = reduced["rows"][-1]["conditional_program"]["output"]
        counterfactuals.append({"name": name, "actual_condition_read": assertion["content"]["condition"], "actual_owner": assertion["content"]["patient"]["id"], "example_only": True})
    # Rival payloads keep a patient and intended outcome, rather than fail on labels.
    for name, payload in (("ADMINISTRATION_ONLY", {"type": "Description", "mode": "ADMINISTRATION", "patient": {"type": "Person", "id": "P"}, "intended_change": True}), ("GENERIC_INSTRUCTION", {"type": "Description", "mode": "INSTRUCTION", "patient": {"type": "Person", "id": "P"}, "intended_change": True})):
        result = reduce_word("olkey", "E", {"description": payload, "description_source": "DECLARED_RIVAL_PAYLOAD"}, world(), "DECLARED_COUNTERFACTUAL")
        counterfactuals.append({"name": name, "barrier": result["barrier"], "trace": result["trace"], "example_only": True})
    import sys
    sys.path.insert(0, str(ROOT))
    from tools import word_profiles as wp
    connection = wp._connect_readonly(wp.DEFAULT_CACHE)
    receipt = wp.receipt(connection)
    profiles = []
    for form in sorted(set(TREES) | {"chedy", "chey", "or", "daiin"}):
        profile = wp.profile(connection, form, limit=1)
        profiles.append({"form": form, "editions": {e: {k: v[k] for k in ("count", "rank", "pages_with_form", "pages_total")} for e, v in profile["editions"].items()}})
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    account = {"status": "NO_COMPLETED_TARGET_READING_CONDITIONAL_PART_FRAGMENT_ONLY", "freeze_utc": now,
               "constructors": INVENTORY, "constructor_inventory_sha256": hashlib.sha256(json.dumps(INVENTORY, sort_keys=True).encode()).hexdigest(), "chosen_segmentation": TREES,
               "segmentation_policy": "Declared local exact trees, not established parser; no per-occurrence trees or bracket/entity normalization. Undeclared words remain unknown.",
               "composition": "Within each word, explicit left-to-right typed function composition. The reference parts have explicitly declared typed selection defaults. No forward binding rule, invisible type cast or partial-token donation.",
               "accounts": accounts, "raw_rows": rows, "guard_receipt": guarded.stderr.strip(), "source_projection_sha256": hashlib.sha256(guarded.stdout.encode()).hexdigest(),
               "legacy_gdt1042_projection_sha256": hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
               "counterfactuals": counterfactuals, "frequency_profiles": profiles,
               "frequency_receipt": {k: v for k, v in receipt.items() if k not in ("selectors",)},
               "costs": {"function_families": len(INVENTORY), "part_spellings": len(PARTS), "extra_alias_spellings": len(PARTS)-len(INVENTORY), "exact_development_trees": len(TREES), "whole_clause_macros": 0, "diagnose_internal_operations": 2, "reference_scope_defaults": 2, "background_world_facts": ["E subject patient distinct from pictured examiner", "S subject equals pictured support user", "E patient equals S user (separate cross-block hypothesis)", "patient owns one specimen", "examiner observes specimen sign", "two-branch sign-to-condition inference rule", "patient uses supplied support"], "word_meanings_confirmed": 0},
               "meaning_binding": "All function meanings, source/world links, segmentation and inference rule are C0 supplied assumptions; no written target patient or specimen supplier is independently bound.",
               "cross_block_identity": "Default supplied world shares one actual Person. This is not a written E-to-S returned-value edge. Fresh-person S world remains a rival; unknown E/S suffixes prohibit claiming any carry.",
               "source_asymmetry": "Arundel staff-user owns support action, patient owns illness while examiner is separate. Arundel illness inscription does not itself narrate OBSERVE or establish these target terms.",
               "first_gap_scope": "Gaps belong to this proposed typed construction, not a manuscript contradiction. Every suffix is unconsumed, not inert. No gap repair or further grammar expansion.",
               "new_access": False, "independent_confirmation_capacity": 0, "whole_E_reading": False, "whole_S_reading": False, "N_W_debt": "Other owned blocks remain unread; aiin/or/daiin/chedy recurrence meanings outside this task untested."}
    output_path.write_text(json.dumps(account, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": account["status"], "rows": len(rows), "first_gaps": {e: {b: v["first_gap"] for b, v in blocks.items()} for e, blocks in accounts.items()}, "sha256": hashlib.sha256(output_path.read_bytes()).hexdigest()}))

if __name__ == "__main__": main()
