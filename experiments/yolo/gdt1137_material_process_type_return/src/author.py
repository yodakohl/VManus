#!/usr/bin/env python3
"""Finite IT32 C0 account. Literal local licenses; no decoder or raw-data reads."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import core

ROOT = Path(__file__).resolve().parents[1]

# Meanings added only AFTER core.py/CORE_FREEZE root acknowledgment.
EXTENSION = {
    "qokeedy": {"parts": ["qo", "keedy"], "sense": "prescribe closed enclosure for the active specification"},
    "qolchey": {"parts": ["qol", "che", "y"], "sense": "specify fine powder-form feedstock"},
    "qokeey": {"parts": ["qokeey"], "sense": "require source surface available to the prescribed conversion within the enclosure", "whole_residual": True},
    "otal": {"parts": ["otal"], "sense": "retain the active preparation in its enclosure", "whole_residual": True},
    "otchey": {"parts": ["ot", "che", "y"], "sense": "state the fine powder-form feedstock charge", "whole_residual": False},
    "qoky": {"parts": ["qoky"], "sense": "prescribe a covered condition for the active specification", "whole_residual": True},
    "tol": {"parts": ["tol"], "sense": "consider the contrasting preparation recipe", "whole_residual": True},
    "qokylddy": {"parts": ["qokylddy"], "sense": "prescribe prolonged covered treatment for that recipe", "whole_residual": True},
    "dain": {"parts": ["dain"], "sense": "resume the first specified product type", "whole_residual": True},
    "shckhedy": {"parts": ["shckhedy"], "sense": "add one renewed contact-treatment step to its prescription", "whole_residual": True},
    "saiin": {"parts": ["saiin"], "sense": "turn to the contrasting material preparation case", "whole_residual": True},
    "cheeky": {"parts": ["che", "eky"], "sense": "take powder-form feedstock as the comparison material"},
    "oldy": {"parts": ["oldy"], "sense": "set aside the active preparation specification", "whole_residual": True},
    "kesd": {"parts": ["kesd"], "sense": "require a dry friable finish of the further preparation", "whole_residual": True},
    "sokeedy": {"parts": ["so", "keedy"], "sense": "then prescribe closed enclosure for the active specification"},
    "sairn": {"parts": ["sairn"], "sense": "close this preparation specification", "whole_residual": True},
}
CORE_WORDS = {
    "chedy": {"parts": ["che", "dy"], "sense": "converted powder preparation recipe"},
    "shedy": {"parts": ["she", "dy"], "sense": "converted sheet preparation recipe"},
    "cheey": {"parts": ["che", "ey"], "sense": "powder source preparation recipe"},
    "sheey": {"parts": ["she", "ey"], "sense": "sheet source preparation recipe"},
    "qokedy": {"parts": ["qokedy"], "sense": "specify the product TYPE derived from the supplied converted recipe"},
    "solchedy": {"parts": ["sol", "che", "dy"], "sense": "return to the actual earlier converted powder product TYPE"},
    "qody": {"parts": ["qody"], "sense": "prescribe further dry-setting of the returned TYPE"},
}
LEXICON = dict(CORE_WORDS, **EXTENSION)

# Every attachment is paid. Physical lines are display addresses, not recovered sentences.
BINDINGS = [
 ("f83r.25", 1, "method", "closed_enclosure"),
 ("f83r.25", 2, "first_source", "fine_source"),
 ("f83r.25", 3, "first_source", "surface_exposure"),
 ("f83r.25", 4, "first_type", "generate_right_recipe"),
 ("f83r.25", 5, "first_type", "first_converted_recipe"),
 ("f83r.25", 6, "first_type", "retention"),
 ("f83r.26", 1, "first_source", "feedstock_charge"),
 ("f83r.26", 2, "first_source", "surface_exposure"),
 ("f83r.26", 3, "first_source", "cover"),
 ("f83r.26", 4, "second_recipe", "contrast_right_recipe"),
 ("f83r.26", 5, "second_recipe", "second_nominal_mention"),
 ("f83r.26", 6, "second_recipe", "extended_covered_treatment"),
 ("f83r.27", 1, "first_type", "resume_first"),
 ("f83r.27", 2, "first_type", "restate_first_recipe"),
 ("f83r.27", 3, "first_type", "closed_enclosure"),
 ("f83r.27", 4, "first_type", "renew_contact"),
 ("f83r.27", 5, "first_type", "renew_contact"),
 ("f83r.28", 1, "second_case", "other_case"),
 ("f83r.28", 2, "second_case", "comparison_material"),
 ("f83r.28", 3, "second_source", "source_recipe"),
 ("f83r.28", 4, "second_type", "generate_right_recipe"),
 ("f83r.28", 5, "second_type", "second_converted_recipe"),
 ("f83r.28", 6, "second_type", "set_aside"),
 ("f83r.29", 1, "returned_type", "earlier_selection"),
 ("f83r.29", 2, "returned_type", "late_source_assertion"),
 ("f83r.29", 3, "further_prescription", "further_process"),
 ("f83r.29", 4, "further_prescription", "finish_constraint"),
 ("f83r.29", 5, "further_prescription", "set_aside"),
 ("f83r.30", 1, "further_prescription", "subsequent_enclosure"),
 ("f83r.30", 2, "further_prescription", "closed_enclosure"),
 ("f83r.30", 3, "further_prescription", "cover"),
 ("f83r.30", 4, "whole_specification", "close"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fine_source(root="che", materials=None):
    # CHEY is CHE+Y, not CHE+EY. Y adds the separately paid fine-grade criterion.
    material = deepcopy((core.MATERIALS if materials is None else materials)[root])
    return {"sort": "feedstock criterion", "material": material, "grade": "fine"}


def comparison_material(root="che", materials=None):
    material = deepcopy((core.MATERIALS if materials is None else materials)[root])
    return {"sort": "comparison criterion", "material": material, "role": "comparison"}


def enclosure(prefix):
    # Same K E E D Y nominal contribution in both literal whole licenses.
    return {"constraint": "enclosure", "value": "closed chamber",
            "ordering": "subsequent" if prefix == "so" else "current"}


def merge_fields(value, replacements):
    for key, item in replacements.items():
        if isinstance(item, dict) and isinstance(value.get(key), dict):
            merge_fields(value[key], item)
        else:
            value[key] = deepcopy(item)


def execute(policy="explicit-earlier-type", producer_overrides=None, materials=None, states=None, return_overrides=None):
    """Deterministic account, with local returned-field overrides for independent probes.

    Overrides modify ONLY actual QOKEDY returned objects after generation, leaving all
    later lexical values fixed. return_overrides instead intervenes in these same actual
    returned objects immediately before late selection, so an earlier local assertion
    need not block inspection of the late dependency. Neither hook is author retuning
    or manuscript evidence.
    """
    native = json.loads((ROOT / "artifacts/NATIVE_SOURCE.json").read_text())
    primary = [r for r in native["rows"] if r["edition"] == "IT2a"]
    rows_by_address = {(r["locus"], int(r["source_group_index"])): r for r in primary}
    nominal_kw = {"materials": materials, "states": states}
    types = []
    first_source = fine_source(materials=materials)
    second_recipe = core.lexical_nominal("shedy", **nominal_kw)
    objects = {"method": {"sort": "method specification"}, "first_source": first_source,
               "second_recipe": second_recipe, "second_case": {"sort": "contrasting case"},
               "whole_specification": {"sort": "whole type/prescription account"}}
    contributions, constraints, treatment_steps, archive = [], [], [], []
    halted = None
    selected = None
    late_assertion = None
    contact_count = 0
    for locus, index, subject, action in BINDINGS:
        row = rows_by_address[locus, index]
        word = row["ivtff_group_raw"]
        entry = {"source_group_id": row["source_group_id"], "locus": locus,
                 "source_group_index": index, "raw": word, "lexical_rule": deepcopy(LEXICON[word]),
                 "binding": {"subject": subject, "action": action},
                 "status": "contributes", "contribution": None}
        if halted:
            entry["status"] = "not-reached-after-first-failure"
            entry["contribution"] = {"declared_action": action, "blocked_by": halted}
            contributions.append(entry)
            continue
        try:
            if action in ("closed_enclosure", "subsequent_enclosure"):
                contribution = enclosure("so" if word == "sokeedy" else "qo")
                contribution["subject"] = subject
                constraints.append(deepcopy(contribution))
            elif action in ("fine_source", "feedstock_charge"):
                contribution = fine_source(materials=materials)
                if action == "feedstock_charge":
                    contribution["role"] = "charge specification; no loading event"
                contribution["subject"] = subject
            elif action == "surface_exposure":
                contribution = {"constraint": "surface exposure", "subject": subject, "required": True}
                constraints.append(deepcopy(contribution))
            elif action == "generate_right_recipe":
                argument = rows_by_address[locus, index + 1]
                recipe = core.lexical_nominal(argument["ivtff_group_raw"], **nominal_kw)
                value = core.qokedy(recipe, row["source_group_id"])
                if producer_overrides and row["source_group_id"] in producer_overrides:
                    merge_fields(value, producer_overrides[row["source_group_id"]])
                types.append(value)
                objects[subject] = value  # exact returned object; no independently seeded type
                source_key = "first_source" if subject == "first_type" else "second_source"
                declared_source = objects[source_key]
                agrees = value["material"] == declared_source["material"]
                contribution = {"function": "core.qokedy", "argument_id": argument["source_group_id"],
                                "argument": recipe, "returned_type": deepcopy(value),
                                "declared_source_binding": source_key,
                                "declared_source_material": deepcopy(declared_source["material"]),
                                "source_material_agreement": agrees,
                                "shared_method_constraints": [deepcopy(c) for c in constraints if c.get("subject") == "method"]}
                if not agrees:
                    halted = row["source_group_id"]
                    entry["status"] = "first-failure"
            elif action in ("first_converted_recipe", "second_converted_recipe", "restate_first_recipe"):
                recipe = core.lexical_nominal(word, **nominal_kw)
                patient = objects[subject]
                contribution = {"nominal_recipe": recipe, "describes_producer": patient["producer_id"],
                                "material_agreement": recipe["material"] == patient["material"],
                                "process_agreement": recipe["operations"] == patient["operations"]}
                if not contribution["material_agreement"] or not contribution["process_agreement"]:
                    contribution["assertion_status"] = "unsatisfied nominal description"
                    # Diagnostic overrides preserve the first actual rejection.
                    halted = row["source_group_id"]
                    entry["status"] = "first-failure"
            elif action == "retention":
                contribution = {"prescription": "retain in enclosure", "patient_producer": objects[subject]["producer_id"]}
                treatment_steps.append(deepcopy(contribution))
            elif action == "cover":
                contribution = {"constraint": "covered", "subject": subject, "required": True}
                constraints.append(deepcopy(contribution))
            elif action == "contrast_right_recipe":
                contribution = {"relation": "contrast", "left_material": deepcopy(first_source["material"]),
                                "right_recipe": deepcopy(second_recipe),
                                "argument_id": rows_by_address[locus, index + 1]["source_group_id"]}
            elif action == "second_nominal_mention":
                contribution = {"nominal_recipe": core.lexical_nominal(word, **nominal_kw),
                                "status": "mentioned recipe; not generated type or batch"}
            elif action == "extended_covered_treatment":
                contribution = {"prescription": "prolonged covered treatment", "patient_recipe": deepcopy(second_recipe),
                                "duration": "prolonged", "covered": True}
                treatment_steps.append(deepcopy(contribution))
            elif action == "resume_first":
                contribution = {"reference": "first generated type", "producer": objects[subject]["producer_id"]}
            elif action == "renew_contact":
                contact_count += 1
                contribution = {"prescription": "renew contact-treatment", "patient_producer": objects[subject]["producer_id"],
                                "step_number": contact_count, "repeat_rule": "append exactly one prescribed step"}
                treatment_steps.append(deepcopy(contribution))
            elif action == "other_case":
                contribution = {"discourse": "contrasting material preparation case", "contrasts_with": "first_type"}
            elif action == "comparison_material":
                contribution = comparison_material(materials=materials)
                contribution["compared_case"] = "second_case"
            elif action == "source_recipe":
                contribution = core.lexical_nominal(word, **nominal_kw)
                objects[subject] = contribution
                contribution = deepcopy(contribution)
            elif action == "set_aside":
                patient = objects[subject]
                contribution = {"prescription": "set aside specification", "patient": deepcopy(patient),
                                "status": "specification archival; no batch put down"}
                archive.append(deepcopy(contribution))
            elif action == "earlier_selection":
                if return_overrides:
                    for generated in types:
                        if generated["producer_id"] in return_overrides:
                            merge_fields(generated, return_overrides[generated["producer_id"]])
                embedded = core.lexical_nominal("chedy", **nominal_kw)
                selected = core.sol(types, embedded, policy)
                objects[subject] = selected["selected_type"]
                contribution = deepcopy(selected)
            elif action == "late_source_assertion":
                recipe = core.lexical_nominal(word, **nominal_kw)
                late_assertion = core.source_predicate(objects[subject], recipe)
                contribution = deepcopy(late_assertion)
                if not late_assertion["satisfied"]:
                    halted = row["source_group_id"]
                    entry["status"] = "first-failure"
            elif action == "further_process":
                value = core.qody(objects["returned_type"])
                objects[subject] = value
                contribution = deepcopy(value)
                treatment_steps.append(deepcopy(value))
            elif action == "finish_constraint":
                patient = objects[subject]
                contribution = {"constraint": "dry friable finish", "subject": subject,
                                "material": deepcopy(patient["material"]),
                                "process_path": list(patient["operations"]),
                                "status": "required endpoint; no measured/world satisfaction asserted"}
                constraints.append(deepcopy(contribution))
            elif action == "close":
                contribution = {"discourse": "end specification", "scope": "whole finite preparation account",
                                "physical_completion": "not asserted"}
            else:
                raise ValueError("undeclared finite action")
            entry["contribution"] = contribution
        except (KeyError, ValueError) as error:
            halted = row["source_group_id"]
            entry["status"] = "first-failure"
            entry["contribution"] = {"error": str(error), "declared_action": action}
        contributions.append(entry)
    return {"policy": policy, "generated_types": deepcopy(types), "contributions": contributions,
            "selection": deepcopy(selected), "late_source_assertion": deepcopy(late_assertion),
            "further_prescription": deepcopy(objects.get("further_prescription")),
            "constraints": constraints, "treatment_steps": treatment_steps, "set_aside": archive,
            "first_failure": halted, "complete_connected_primary": halted is None and len(contributions) == 32,
            "ontology": "recipes, types and prescriptions; no material-production event or instance identity"}


def build_account():
    native = json.loads((ROOT / "artifacts/NATIVE_SOURCE.json").read_text())
    original = execute()
    rival = execute("latest-product-only")
    residuals = [word for word, entry in EXTENSION.items() if entry.get("whole_residual")]
    alternate_limits = {
        "ZL3b": ["33 groups; .30 s + okeedy preserved without IT sokeedy alias",
                   ".29 salche'dy is not literal SOL+CHEDY; return construction unresolved",
                   ".30 saii@208; uncertain ending remains unknown"],
        "RF1b": ["32 groups; she@152;y is not exact SHEDY",
                  ".28 {ch'}edy is not exact SHEDY; second focal generation unlicensed",
                  ".29 solche'@152;y is not SOL+CHEDY; kes@152; not KESD",
                  ".30 saiin is not IT sairn; no terminal alias"],
        "all": ["One exposed physical leaf, alternative readings rather than confirmation",
                "ZL complete paragraph; IT end flag missing; RF both boundary flags missing"]}
    return {
        "experiment": "GDT1137", "stage": "scoped exploratory finite C0 author",
        "input_pins": {name: digest(ROOT / name) for name in
                       ["METHOD.md", "PREREGISTRATION.md", "artifacts/NATIVE_SOURCE.json", "artifacts/WORD_PRIORS.json", "src/core.py", "src/CORE_FREEZE.json"]},
        "native_source": native, "primary_reader": "IT2a", "primary_positions": 32,
        "all_native_groups": 97, "native_conservation": "complete verbatim native objects retained; no normalization",
        "lexicon": LEXICON, "bindings": [{"locus": l, "index": i, "subject": s, "action": a} for l,i,s,a in BINDINGS],
        "execution": original, "same_lexicon_latest_only": rival,
        "policy_consequence": {"earlier": {"selected_producer": original["selection"]["selected_type"]["producer_id"],
                                          "material": original["selection"]["selected_type"]["material"],
                                          "next_written_predicate": original["late_source_assertion"],
                                          "further_prescription": original["further_prescription"]},
                               "latest": {"selected_producer": rival["selection"]["selected_type"]["producer_id"],
                                          "material": rival["selection"]["selected_type"]["material"],
                                          "written_restriction_matches": rival["selection"]["written_type_matches"],
                                          "next_written_predicate": rival["late_source_assertion"],
                                          "first_failure": rival["first_failure"],
                                          "further_prescription": rival["further_prescription"]},
                               "interpretation": "Latest-only disregards embedded CHEDY restriction and then fails CHEEY source assertion. This is a conflict within paid lexical/binding assumptions, not evidence the other material cannot be dry-set."},
        "cost_inventory": {
            "material_kind_primitives": 2, "nominal_state_primitives": 2,
            "core_operator_senses": 3, "core_source_predication_rule": 1,
            "extension_primitive_senses": {"qo": "current prescription attachment", "so": "subsequent prescription attachment",
                                            "keedy": "closed chamber", "qol": "specify feedstock", "ot": "charge specification",
                                            "y": "fine-grade criterion in CHEY only", "eky": "comparison material in CHEEKY only"},
            "extension_whole_residuals": residuals, "whole_residual_count": len(residuals),
            "distinct_primary_lexical_rules": len(LEXICON), "literal_assemblies": 10,
            "source_aligned_bindings": len(BINDINGS), "reference_policies": 2,
            "scope_defaults": ["IT primary account only", "types/recipes/prescriptions, never physical events",
                               "explicit attachment table, not physical-line sentence grammar",
                               "right-argument attachment for the two QOKEDY sites and TOL",
                               "first actually generated type for DAIN",
                               "early SHEDY.26 nominal mention, not generation",
                               "late CHEEY source predicate of returned type",
                               "repeated contact word adds one prescribed step each time",
                               "QOKEEDY at opening attaches to shared method, later to named patient",
                               "OLDY archives active specification, not material batch",
                               "first failed assertion stops rival tail",
                               "opening shared method condition applies to both generated type prescriptions"],
            "scope_default_count": 12, "overloads": [], "aliases": [],
            "economy_limit": "Counts describe declarations, not a minimum semantic description length. English senses, attachment selection and qualitative constraints carry uncalibrated author freedom."},
        "alternate_reader_limits": alternate_limits,
        "assumptions_and_dependencies": [
            "che/she powder/sheet senses are paid local guesses, not source-given or independently bound",
            "EY/DY recipe states and surface-convert operation are local finite licenses, not recovered morphology",
            "same QOKEDY computes both product types from actual material and operation fields",
            "fine CHEY is not source-preparation CHEEY; no inserted E",
            "all descriptions/prescriptions can be stated before or after a nominal recipe mention; no implicit loads",
            "no assertion of actual chemical feasibility or satisfaction of emitted endpoint constraints",
            "32 attachments and discourse references are hypothesis choices, not recovered grammar",
            "same type permits fresh or persistent batch; no written instance rule was purchased",
            "alternate uncertainty bars extension of primary account to all97 groups",
            "registered independent whole label/prose duty of IDEA876 remains outside stage"],
        "known_counterexamples_and_retained_decisions": [
            "CHEDY.25 precedes CHEEY.29; SHEDY.26 precedes SHEEY.28: nominal ontology explicitly permits both",
            "QOLCHEY contains CHEY, not CHEEY; distinct fine-grade license",
            "GDT719 old failed DY decomposition and GDT1114 immediate-right-result universal CHEDY remain failed",
            "GDT1136 inert parts and prior separately seeded reference accounts are not imported",
            "GDT914/925/928 exact-parallel failures unchanged; no new corpus criterion",
            "Frequent forms across exposed profiles preclude interpreting this local account as global operation grammar"],
        "claim_ceiling": "Complete IT32 hypothesis if audited; alternate reading gaps remain. Coherent implementation is distinct from true source relationship, physical execution and manuscript meaning. No confirmed English word, significance, preferred source, metal name, independent confirmation or reserve eligibility."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/AUTHOR_ACCOUNT.json")
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_account(), ensure_ascii=False, indent=2) + "\n")

if __name__ == "__main__":
    main()
