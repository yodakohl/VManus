"""Independent bookkeeping/reduction checks; does not validate word meanings."""
import hashlib
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
AUTHOR = BASE / "GD_SHARED_CONSTRUCTION_AUTHOR_20261002.json"
GENERATOR = BASE / "GD_SHARED_CONSTRUCTION_GENERATOR_20261002.py"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def nodes(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from nodes(item)

def run():
    before = AUTHOR.read_bytes()
    a = json.loads(before)
    es_path = BASE / a["source_preservation"]["ES_author_file"]
    es = json.loads(es_path.read_bytes())
    checks = {}
    checks["ES_hash"] = digest(es_path) == a["source_preservation"]["ES_author_sha256"]
    checks["generator_hash"] = digest(GENERATOR) == a["generator_source"]["sha256"]
    checks["V1_retained"] = digest(BASE / a["exploratory_revision"]["prior_version_file"]) == a["exploratory_revision"]["prior_version_sha256"]
    rows = a["full_17_written_order_reduction"]
    checks["all17_raw_ID_value_tuples"] = [
        (r["source_group_id"], r["raw"], r["fixed_value"]) for r in rows
    ] == [(r["source_id"], r["raw"], r["value"]) for r in es["IT17_written_roles"]]
    checks["IT_full_native_unit"] = a["source_preservation"]["primary_IT_unit"] == es["complete_native_units"]["IT2a"][0]
    checks["RF_native_records_retained"] = a["source_preservation"]["RF_own_raw_lines"] == es["RF_own_raw_lines"]
    zl = a["source_preservation"]["complete_ZL_unit_reference"]
    checks["ZL_longer_unit_not_shortened"] = zl["groups"] == es["complete_native_units"]["ZL3b"][0]["groups"] == 36
    checks["seven_exact_surface_assemblies"] = len(a["core"]["finite_surface_licenses"]) == 7 and all(
        "".join(v["assembly"]) == k for k, v in a["core"]["finite_surface_licenses"].items())
    spec = importlib.util.spec_from_file_location("shared_constructor_checked", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks["seven_computed_templates"] = all(
        module.construct(a["core"], form, "$x", "$w", "$t", "$I", "$e", "$host_event") == entry["reduced_template"]
        for form, entry in a["computed_form_templates"].items())
    final = a["complete_conjunction"]
    atoms = [n for n in nodes(final) if n.get("op") == "ATOM"]
    def has(pred, args):
        return any(n["predicate"] == pred and n["arguments"] == args for n in atoms)
    checks["same_event_instrument_consumer"] = has("USING", ["W_actual", "E_fraction", "E_carrier"])
    checks["same_event_destination_consumer"] = has("ENTERS_SOME", ["W_actual", "E_out", "D", "V_receiver"])
    checks["all_four_event_ports_jointly_bound"] = set(a["discourse_existential_closure"]["events"]) <= set(final["binders"])
    checks["no_unresolved_template_ports_in_final"] = "$" not in json.dumps(final) and "WITNESS_PACKAGE" not in json.dumps(final)
    checks["no_liquid_requirement_in_finite_flow"] = not any(
        n.get("predicate") == "LIQUID" for n in nodes(a["computed_form_templates"]["qokeedy"]["reduced_template"]))
    for t, phase in (("T25", "I25"), ("T26", "I26")):
        checks[t + "_explicit_onset"] = has("SAME_TIME", [t, {"phase_start": phase}])
    module.build()
    checks["byte_identical_reproduction"] = AUTHOR.read_bytes() == before
    result = dict(status="PASS" if all(checks.values()) else "FAIL", checks=checks,
        author_sha256=digest(AUTHOR), generator_sha256=digest(GENERATOR),
        scope="Source preservation and finite logical reduction only; manual syntax bindings remain inputs",
        semantic_confirmation=False, independent_confirmation_capacity=0)
    (BASE / "GD_SHARED_CONSTRUCTION_VALIDATION_20261002.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)

if __name__ == "__main__":
    run()
