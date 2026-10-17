"""Exploratory signed alternative to R1, with every root meaning unassigned."""
import copy
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

B = Path(__file__).resolve().parent
R = B.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed(word, pairs):
    return {"predicate": pairs.get(word, word), "positive": word not in pairs}


def facts(descriptions, pairs):
    result = {}
    for word in descriptions:
        item = signed(word, pairs)
        key = item["predicate"]
        if key in result and result[key] != item["positive"]:
            return None
        result[key] = item["positive"]
    return result


def pair_licenses(words):
    # This is an imposed semantic license, not an inferred prefix meaning.
    return {w: w[1:] for w in sorted(words) if w.startswith("q") and w[1:] in words}


def main():
    parent_path = B / "F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json"
    rules_path = B / "F45R_RECORD_SYNTHESIS_RULES_20261015.json"
    source_path = B / "F45R_WHOLE_PAGE_SOURCE_20261015.json"
    plan_path = B / "F45R_SIGNED_PLAN_20261017.json"
    plan = read(plan_path)
    for binding in plan["pins"]:
        assert sha(R / binding["path"]) == binding["sha256"]
    parent = read(parent_path)
    rules = read(rules_path)
    assert parent["rules_sha256"] == sha(rules_path)
    assert parent["source_sha256"] == sha(source_path)
    assert len(parent["trace"]) == 86
    assert parent["summary"]["explicit_reprise_events"] == 4
    vocabulary = {d for e in parent["entities"] for d in e["descriptor_set"]}
    licenses = pair_licenses(vocabulary)
    assert licenses == {"qokaiin": "okaiin", "qoky": "oky"}
    trace = copy.deepcopy(parent["trace"])
    for row in trace:
        row["conditional_description"] = (
            signed(row["descriptor"], licenses) if row.get("descriptor") else None
        )
    entities = []
    for entity in parent["entities"]:
        values = facts(entity["descriptor_set"], licenses)
        assert values is not None
        entities.append({"id": entity["id"], "required_truth_values": values})
    inequalities = []
    for left, right in itertools.combinations(entities, 2):
        a, b = left["required_truth_values"], right["required_truth_values"]
        conflicts = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
        if conflicts:
            inequalities.append({"left": left["id"], "right": right["id"], "because": conflicts})
    assert inequalities == [{"left": "P1.subject", "right": "P3.subject", "because": ["okaiin", "oky"]}]

    worksheet = R / "research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/LEXICAL_WORKSHEET_20261016.json"
    unit = [u for u in read(worksheet)["units"] if u["unit_id"] == "f75v_IT2a"]
    assert len(unit) == 1
    lines = unit[0]["lines"]
    assert [l["metadata"]["paragraph_start"] for l in lines] == ["1"] + ["0"] * 6
    assert [l["metadata"]["paragraph_end"] for l in lines] == ["0"] * 6 + ["1"]
    flat = [copy.deepcopy(g) for line in lines for g in line["original_groups"]]
    assert len(flat) == 77
    assert not any(g[2] in rules["bound_forms"] for g in flat)
    markers = set(rules["free_markers"])
    transfer = []
    for index, group in enumerate(flat):
        word = group[2]
        follower = flat[index + 1][2] if index + 1 < len(flat) else None
        if word in markers:
            role, entity = "free_marker", None
        elif follower in markers:
            role, entity = "field_description", "field." + follower
        else:
            role, entity = "subject_description", "subject"
        transfer.append({"original_group": group, "role_under_R1": role, "entity_under_R1": entity})
    tvocab = {r["original_group"][2] for r in transfer if r["entity_under_R1"] is not None}
    tlicenses = pair_licenses(tvocab)
    assert tlicenses == {"qokain": "okain", "qokeedy": "okeedy", "qol": "ol", "qolchedy": "olchedy"}
    slots = {}
    for row in transfer:
        if row["entity_under_R1"] is None:
            row["conditional_description"] = None
            continue
        word = row["original_group"][2]
        row["conditional_description"] = signed(word, tlicenses)
        slot = slots.setdefault(row["entity_under_R1"], {})
        slot.setdefault(row["conditional_description"]["predicate"], []).append({
            "positive": row["conditional_description"]["positive"],
            "source_id": row["original_group"][0], "raw": word,
        })
    clashes = []
    for entity, predicates in sorted(slots.items()):
        for predicate, witnesses in sorted(predicates.items()):
            if {r["positive"] for r in witnesses} == {False, True}:
                clashes.append({"entity": entity, "predicate": predicate, "witnesses": witnesses})
    assert [(c["entity"], c["predicate"]) for c in clashes] == [
        ("subject", "okain"), ("subject", "okeedy"),
        ("subject", "ol"), ("subject", "olchedy")]

    command = [str(R / "vmanus-work"), "words", "profile", "qoky", "oky", "qokaiin", "okaiin", "--json", "--limit", "2"]
    profiles = json.loads(subprocess.check_output(command, cwd=R, text=True))["profiles"]
    profile_receipts = []
    for profile in profiles:
        editions = {}
        for edition, value in profile["editions"].items():
            editions[edition] = {k: value[k] for k in ("count", "pages_with_form", "positions", "repetition")}
            editions[edition]["strata"] = {k: {r["value"]: r["count"] for r in rows} for k, rows in value["strata"].items()}
        profile_receipts.append({"form": profile["form"], "editions": editions})
    result = {
        "status": "CONDITIONAL_SIGNED_R1_ONLY_GLOBAL_CONJUNCTION_COUNTER",
        "phase": "Exploratory authorship after source exposure; not a registered statistical experiment",
        "root_meanings": "ALL_UNASSIGNED",
        "operator_status": "ASSUMED_COMPLEMENT_NOT_A_q_TRANSLATION",
        "f45r": {"parent_summary_unchanged": parent["summary"], "pair_licenses_assumed": licenses,
                   "records_unchanged": parent["records"], "equalities_unchanged": parent["equalities"],
                   "all_86_positions": trace, "conditional_consistent_state_assignment": entities,
                   "forced_state_inequalities": inequalities},
        "f75v_global_conjunction_counter": {"all_77_positions": transfer, "pair_licenses_assumed": tlicenses,
            "contradictions": clashes, "scope": "Same-state R1 paragraph scope AND generalized complement licenses only. Not a refutation of original local R1, finite f45r licenses, all q functions or changed-state grammars. Earlier page fields/reprises are unnecessary for these subject clashes and are not reconstructed."},
        "profiles": profile_receipts,
        "preserved_limits": plan["retained_limits"],
        "source_pins": plan["pins"],
        "builder_sha256": sha(Path(__file__)),
        "no_new_image_or_lexical_meaning": True,
    }
    (B / "F45R_SIGNED_20261017.json").write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "f45r_positions": 86, "f75v_positions": 77,
                      "conditional_forced_state_inequalities": inequalities,
                      "global_conjunction_clashes": len(clashes), "translated_words": 0}))


if __name__ == "__main__":
    main()
