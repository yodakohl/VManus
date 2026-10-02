"""Replay the critic's already-used post-release dependency diagnostics.

Only frozen author files are read. The author run() is never called and no
files are written. Temporary in-memory function substitutions are restored.
These are implementation-lineage checks, not world/meaning tests or repairs.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTHOR = "GD_MOTION_SHARED_GRADE_AUTHOR_20261002"
PINS = {
    ".py": "d13016c532ad28652e9fe8944e01343a4dbf520f1bc931228da793218c623c9c",
    ".json": "1fa29aa7612a05143fcafad06da58b19e921854d211b1308f3343acdf8462f3b",
    ".md": "3068e8cb671648f563ea404ed12cd2a274527264aff2491e9489bdb88a2d6f22",
}
CASES = [
    ("CONDUIT_RETURN_ONLY", "qolchey", "$X1", {"C": "C_CHANGED"}, "IT2a|f83r.26|G001"),
    ("INTENTION_RETURN_ONLY", "qoky", "$X2", {"P2": "P_CHANGED"}, "IT2a|f83r.26|G006"),
    ("GOAL_RETURN_ONLY", "tol", "$X2", {"O": "O_CHANGED"}, "IT2a|f83r.26|G006"),
    ("REMAINDER_RETURN_ONLY", "sairn", "$X6", {"R": "R_CHANGED"}, "IT2a|f83r.30|G002"),
    ("LAST_SERIES_EVENT_RETURN_ONLY", "shckhedy", "$X3", {"E3c": "E_CHANGED", "I3c": "I_CHANGED"}, "IT2a|f83r.28|G001"),
]

def lines(rows):
    out = []
    for number in range(25, 31):
        selected = [row for row in rows if row["clause"] == number]
        out.append(("f83r." + str(number), [row["raw"] for row in selected],
                    [row["source_group_id"] for row in selected]))
    return out

def replay():
    for suffix, pin in PINS.items():
        actual = hashlib.sha256((HERE / (AUTHOR + suffix)).read_bytes()).hexdigest()
        if actual != pin:
            raise ValueError("Frozen author pin mismatch: " + suffix)
    account = json.loads((HERE / (AUTHOR + ".json")).read_text())
    spec = importlib.util.spec_from_file_location("frozen_motion_binding_diagnostic", HERE / (AUTHOR + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    baseline = {}
    for name, value in account["accounts"].items():
        output = module.execute(lines(value["rows"]), value["namespace"], value["parent_variant"])
        # Serialization normalizes in-memory series tuples to the frozen lists.
        baseline[name] = json.loads(json.dumps(output)) == value
    base = account["accounts"]["native_IT_G"]
    base_rows = {row["source_group_id"]: row for row in base["rows"]}
    original = module.compile_word
    diagnostics = []
    for name, donor_raw, patient, mapping, consumer in CASES:
        def patched(raw, world, owner, event, phase, context, variant):
            result = original(raw, world, owner, event, phase, context, variant)
            if raw == donor_raw and owner == patient:
                return module.substitute(result, mapping)
            return result
        try:
            module.compile_word = patched
            altered = module.execute(lines(base["rows"]), base["namespace"], base["parent_variant"])
        finally:
            module.compile_word = original
        altered_rows = {row["source_group_id"]: row for row in altered["rows"]}
        diagnostics.append({
            "id": name,
            "changed_donor_outputs": [sid for sid in base_rows if altered_rows[sid]["returned_predicates"] != base_rows[sid]["returned_predicates"]],
            "target_consumer": consumer,
            "consumer_return_unchanged": altered_rows[consumer]["returned_predicates"] == base_rows[consumer]["returned_predicates"],
            "consumer_context_unchanged": altered_rows[consumer]["operator_input"] == base_rows[consumer]["operator_input"],
            "mapping": mapping,
            "scope": "POST_RELEASE_RETURN_PAYLOAD_DIAGNOSTIC_NOT_WORLD_OR_MEANING_TEST",
        })
    original_pattern = module.pattern
    def alternative_pattern(number, world, event, owner, phase):
        return original_pattern(2 if number == 0 else number, world, event, owner, phase)
    try:
        module.pattern = alternative_pattern
        altered = module.execute(lines(base["rows"]), base["namespace"], base["parent_variant"])
    finally:
        module.pattern = original_pattern
    sites = [row for row in altered["rows"] if row["raw"] == "qokedy"]
    pattern = {
        "scope": "POST_RELEASE_OPERATOR_SENSITIVITY_NOT_MEANING_EVIDENCE",
        "changed_only": "pattern(0) calls original pattern(2); no donor/register change",
        "written_sites": [row["source_group_id"] for row in sites],
        "both_return_continuous": all("CONTINUOUS_FULL_PHASE" in json.dumps(row["returned_predicates"]) and "ZERO_FLOW_THROUGHOUT" not in json.dumps(row["returned_predicates"]) for row in sites),
    }
    return {"author_sha256": PINS, "baseline_replay": baseline,
            "diagnostics": diagnostics, "shared_pattern_return_diagnostic": pattern,
            "scope": "Reproduction of existing critic findings only; no author/source mutation or meaning evidence."}

if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
