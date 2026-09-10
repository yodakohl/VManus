"""Independent audit of the ten pre-fit global role partitions.

Build occurrence roles directly from the sealed B observation. The original
35-atom source and its earlier validation remain byte-frozen.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

SOURCE_HASH = "0daf60d86d63ec371137378310871dd0f3bc0b7d16ac78770986b66647fe5d65"
SPEC_HASH = "119be016d348b28d0915792bdb59a2c4f40496ed821be9c5fcddae2c2856b17a"
B_HASH = "5ff9f2ecbce567c8ba5c5d6e6de2b59784223fce964fd227d9305e7f222cbb8f"
PRIOR_VALIDATION_HASH = "96ce1bc3f8a928b0dfb9b882abab9c61424779c6175ac2dda2ffcafe7b6be0c4"
NAMES = ("Gamma", "A", "B_square", "C", "D", "E", "F", "G", "a", "b_flat", "b_square", "c", "d", "e", "f", "g", "aa", "bb_flat", "bb_square", "cc", "dd", "ee")
PITCH = {f"P{i:02d}": name for i, name in enumerate(NAMES, 1)}
TYPE = {"H": "hard", "N": "natural", "S": "soft"}
DIR = {"ascendendo": "ascending", "descendendo": "descending"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def partitions(n):
    result = []
    for labels in itertools.product(range(n), repeat=n):
        canonical, encountered = [], {}
        for label in labels:
            encountered.setdefault(label, len(encountered))
            canonical.append(encountered[label])
        if tuple(canonical) == labels:
            result.append(list(labels))
    return result


def validate(source_path, spec_path, compiler_path):
    source_path, spec_path, compiler_path = map(Path, (source_path, spec_path, compiler_path))
    source_blob, spec_blob = source_path.read_bytes(), spec_path.read_bytes()
    require(sha(source_blob) == SOURCE_HASH, "original_source_unchanged")
    require(sha(spec_blob) == SPEC_HASH, "separate_model_spec_frozen")
    source, spec = json.loads(source_blob), json.loads(spec_blob)
    require(spec["source_sha256"] == SOURCE_HASH, "model_bound_to_original_source")
    require(sha(compiler_path.read_bytes()) == spec["role_compiler_sha256"], "frozen_role_compiler")
    b_blob = (source_path.parent / "SOURCE_OBSERVER_B.json").read_bytes()
    require(sha(b_blob) == B_HASH, "independent_B_seal")
    prior_blob = (source_path.parent / "SOURCE_VALIDATION.json").read_bytes()
    require(sha(prior_blob) == PRIOR_VALIDATION_HASH, "prior_source_validation_unchanged")
    observer = json.loads(b_blob)
    pitch_parts, voice_parts = partitions(2), partitions(3)
    require(len(pitch_parts) == 2 and len(voice_parts) == 5, "complete_Bell_partitions")
    cases = [{"pitch": pitch, "voice": voice} for pitch, voice in itertools.product(pitch_parts, voice_parts)]
    require(spec["cases"] == cases, "complete_ten_case_union")
    role_positions, occurrences = [], Counter()
    for row in observer["records"]:
        current = row["pitch_id"]
        pitch = PITCH[current]
        positions = [("PITCH", pitch, 0)]
        def add_origin(origin):
            positions.append((None, "SELF", None) if origin == current else ("PITCH", PITCH[origin], 1))
        for member in row["voice_memberships_in_written_order"]:
            positions.extend((("VOICE", member["voice"], 0), (None, "CANTUS:" + TYPE[member["cantus_type"]], None)))
            add_origin(member["origin_pitch_id"])
        for mutation in row["directed_mutations"]:
            positions.extend((("VOICE", mutation["from_voice"], 1), ("VOICE", mutation["to_voice"], 2), (None, "DIRECTION:" + DIR[mutation["direction"]], None), (None, "CANTUS:" + TYPE[mutation["destination_cantus_type"]], None)))
            add_origin(mutation["destination_origin_pitch_id"])
        if row["explicit_zero"]:
            positions.append((None, "ZERO", None))
        for family, value, role in positions:
            label = ("PITCH_HEAD", "PITCH_ORIGIN")[role] if family == "PITCH" else ("VOICE_MEMBER", "VOICE_FROM", "VOICE_TO")[role] if family == "VOICE" else value.split(":")[0]
            occurrences[label] += 1
        role_positions.append((pitch, positions))
    require(sum(occurrences.values()) == 416, "all_416_occurrences_retained")
    expected, summaries = [], []
    for case_index, case in enumerate(cases):
        forms, records = {}, []
        for pitch, positions in role_positions:
            sequence = []
            for family, value, role in positions:
                if family is None:
                    name, metadata = value, {"family": None, "root": None, "roleclass": None}
                else:
                    block = case["pitch" if family == "PITCH" else "voice"][role]
                    roleclass = family + ":" + str(block)
                    name = roleclass + ":" + value
                    metadata = {"family": family, "root": value, "roleclass": roleclass}
                require(name not in forms or forms[name] == metadata, "global_role_class_reuse")
                forms[name] = metadata
                sequence.append(name)
            records.append({"id": pitch, "head_atom": sequence[0], "sequence": sequence})
        compiled = {"records": records, "atoms": sorted(forms), "forms": forms, "role_partition": case}
        collapsed = []
        for record in records:
            def semantic(name):
                info = forms[name]
                return name if info["family"] is None else info["family"] + ":" + info["root"]
            collapsed.append({"id": record["id"], "head_atom": semantic(record["head_atom"]), "sequence": [semantic(name) for name in record["sequence"]]})
        require(collapsed == source["records"], "all_cases_exact_original_semantic_projection")
        if case_index == 0:
            require(len(forms) == len(source["atoms"]) == 35, "merged_case_bijective_renaming")
            require(len({name if meta["family"] is None else meta["family"] + ":" + meta["root"] for name, meta in forms.items()}) == 35, "merged_case_no_hidden_alias")
        expected.append(compiled)
        summaries.append({"case": case_index, "partition": case, "records": len(records), "forms": len(forms), "positions": sum(len(r["sequence"]) for r in records), "original_semantics_exact": True, "compiled_sha256": sha(json.dumps(compiled, sort_keys=True, separators=(",", ":")).encode())})
    counts = [len(case["atoms"]) for case in expected]
    require(spec["form_counts"] == counts == [35, 41, 41, 41, 47, 42, 48, 48, 48, 54], "all_realized_form_counts")
    probe = """import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('role_compiler_under_test',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=json.load(open(sys.argv[2]));print(json.dumps({'cases':m.CASES,'compiled':[m.compile_case(s,c) for c in m.CASES]}))
"""
    process = subprocess.run([sys.executable, "-c", probe, str(compiler_path.resolve()), str(source_path.resolve())], capture_output=True, text=True, check=True)
    actual = json.loads(process.stdout)
    require(actual["cases"] == cases and actual["compiled"] == expected, "all_ten_primary_compilations_exact")
    return {"schema": "GDT901_INDEPENDENT_ROLE_COMPILER_VALIDATION_V1", "status": "PASS", "source_input_sha256": SOURCE_HASH, "model_spec_sha256": SPEC_HASH, "role_compiler_sha256": spec["role_compiler_sha256"], "observer_B_sha256": B_HASH, "prior_source_validation_sha256": PRIOR_VALIDATION_HASH, "validator_sha256": sha(Path(__file__).read_bytes()), "complete_partition_count": 10, "pitch_partition_count": 2, "voice_partition_count": 5, "role_occurrences_per_case": dict(occurrences), "cases": summaries, "checks": ["All Bell(2) pitch-role and Bell(3) voice-role partitions included globally", "Occurrence roles independently assigned directly from the sealed B memberships and detailed mutation clauses", "Each case retains all 22 records and 416 semantic positions", "All ten compiled record sequences and form metadata match the primary compiler exactly", "Erasing role classes recovers the original source in every case", "The all-merged case is exactly the original 35-atom model by a bijective renaming", "Cantus, direction, SELF and ZERO remain unmodified shared atoms", "Original source packet and earlier source validation remain unchanged"], "scope": "Pre-fit source/compiler validation only. The model specification permits empty role affixes and requires nonempty shared semantic roots plus distinct realized whole-word values; this audit does not validate a factorization solver or claim identifiable root boundaries. No target data, domains or fits."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-input", required=True)
    parser.add_argument("--model-spec", required=True)
    parser.add_argument("--role-compiler", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(args.source_input, args.model_spec, args.role_compiler)
    output = Path(args.output)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    temporary.replace(output)
    print(json.dumps({"status": result["status"], "cases": result["complete_partition_count"], "form_counts": [case["forms"] for case in result["cases"]], "positions_checked": sum(case["positions"] for case in result["cases"])}))


if __name__ == "__main__":
    main()
