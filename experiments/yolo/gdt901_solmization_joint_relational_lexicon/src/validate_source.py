"""Independently compile all 22 operational records from the sealed B reading.

No target or model fitting. Expected records are built directly from B's typed
memberships and detailed mutation clauses, without using the primary compiler.
The primary compiler is invoked afterward only as the subject of exact parity.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SOURCE_HASH = "0daf60d86d63ec371137378310871dd0f3bc0b7d16ac78770986b66647fe5d65"
RECEIPTS = {
    "SOURCE_GRAPH_A.json": "a850cb7f0152275ea2d108cdb6aaa5cd5917e51175450e344a4bf178bbcde136",
    "SOURCE_OBSERVER_B.json": "5ff9f2ecbce567c8ba5c5d6e6de2b59784223fce964fd227d9305e7f222cbb8f",
    "SOURCE_SYMMETRY_A.json": "be1a5e8e72425abcc1cf8ced871ab8ddc1a6aaddcb891e63ddb2797d403445ee",
}
PITCH_NAMES = ("Gamma", "A", "B_square", "C", "D", "E", "F", "G", "a", "b_flat", "b_square", "c", "d", "e", "f", "g", "aa", "bb_flat", "bb_square", "cc", "dd", "ee")
NAVIGATION = ("[Gamma] ut", "A re", "[sqb] mi (grave)", "C fa ut", "D sol re", "E la mi", "F fa ut", "G sol re ut", "a la mi re", "b fa", "[sqb] mi (acute)", "c sol fa ut", "d la sol re", "e la mi", "f fa ut", "g sol re ut", "aa la mi re", "bb fa", "[sqb][sqb] mi", "cc sol fa", "dd la sol", "ee la")
TYPE = {"H": "hard", "N": "natural", "S": "soft"}
DIRECTION = {"ascendendo": "ascending", "descendendo": "descending"}
PITCH = {f"P{index:02d}": name for index, name in enumerate(PITCH_NAMES, 1)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def origin_atom(origin, current):
    return "SELF" if origin == current else "PITCH:" + PITCH[origin]


def validate(source_path, compiler_path):
    source_path, compiler_path = Path(source_path), Path(compiler_path)
    blob = source_path.read_bytes()
    require(sha(blob) == SOURCE_HASH, "frozen_source_hash")
    packet = json.loads(blob)
    require(packet["schema"] == "GDT901_FROZEN_OPERATIONAL_SOURCE_V1", "packet_schema")
    bound = {item["file"]: item["sha256"] for item in packet["source_receipts"]}
    require(bound == RECEIPTS, "complete_source_receipt_bindings")
    receipts = {}
    for name, expected_hash in RECEIPTS.items():
        data = (source_path.parent / name).read_bytes()
        require(sha(data) == expected_hash, "receipt_bytes:" + name)
        receipts[name] = json.loads(data)
    observer = receipts["SOURCE_OBSERVER_B.json"]
    require(observer["schema"] == "IERTDM1_CH12_INDEPENDENT_OBSERVER_B_V1", "independent_observer_schema")
    graph = packet["source_graph"]
    require(graph == receipts["SOURCE_GRAPH_A.json"], "A_graph_exact_embedding")
    require(graph["source_sha256"] == observer["source"]["primary_html_sha256"], "same_electronic_source_bytes")
    rows = observer["records"]
    require(len(rows) == 22, "all_22_observer_records")
    compiled, expected_pitches, expected_mutations, summaries = [], [], [], []
    origins, direction_counts, zero_ids = {}, Counter(), []
    total_members, total_mutations = 0, 0
    for index, row in enumerate(rows, 1):
        row_id = f"P{index:02d}"
        pitch = PITCH[row_id]
        require(row["pitch_id"] == row_id and row["source_pitch_ordinal"] == index, "native_record_order")
        require(row["label_for_navigation"] == NAVIGATION[index - 1], "named_pitch_alias_binding")
        require(row["modern_addition_explicit"] == (row_id == "P22"), "modern_addition_retained_only_at_ee")
        sequence, memberships, membership_by_voice = ["PITCH:" + pitch], [], {}
        for member in row["voice_memberships_in_written_order"]:
            voice, kind, origin = member["voice"], member["cantus_type"], member["origin_pitch_id"]
            require(voice not in membership_by_voice, "unique_voice_within_record")
            membership_by_voice[voice] = member
            require(origin not in origins or origins[origin] == kind, "consistent_origin_cantus_type")
            origins[origin] = kind
            memberships.append({"voice": voice, "origin": PITCH[origin]})
            sequence.extend(("VOICE:" + voice, "CANTUS:" + TYPE[kind], origin_atom(origin, row_id)))
            if member["raw_origin_phrase"] == "sui":
                require(origin == row_id, "literal_sui_is_self")
            total_members += 1
        mutations = row["directed_mutations"]
        require(len(mutations) == row["mutation_count_explicit"], "all_explicit_mutations")
        require(len(row["enumerated_pairs_in_source_order"]) == len(mutations), "introductory_pair_list_not_extra_mutations")
        for ordinal, mutation in enumerate(mutations, 1):
            require(mutation["listed_ordinal"] == ordinal, "detailed_mutation_order")
            before, after = mutation["from_voice"], mutation["to_voice"]
            require(before in membership_by_voice and after in membership_by_voice, "mutation_voices_same_pitch")
            source_member, destination_member = membership_by_voice[before], membership_by_voice[after]
            kind, origin = mutation["destination_cantus_type"], mutation["destination_origin_pitch_id"]
            require(kind == destination_member["cantus_type"] and origin == destination_member["origin_pitch_id"], "detailed_destination_matches_membership")
            direction = DIRECTION[mutation["direction"]]
            sequence.extend(("VOICE:" + before, "VOICE:" + after, "DIRECTION:" + direction, "CANTUS:" + TYPE[kind], origin_atom(origin, row_id)))
            expected_mutations.append({"pitch": pitch, "from_voice": before, "from_origin": PITCH[source_member["origin_pitch_id"]], "to_voice": after, "to_origin": PITCH[origin], "direction": direction})
            direction_counts[direction] += 1
            total_mutations += 1
        require(row["explicit_zero"] == (len(mutations) == 0), "explicit_zero_complete")
        if row["explicit_zero"]:
            sequence.append("ZERO")
            zero_ids.append(row_id)
        require(sequence.count("ZERO") == int(row["explicit_zero"]), "only_final_zero_marker")
        expected_pitches.append({"id": pitch, "memberships": memberships, "mutation_count": len(mutations), "zero_explicit": row["explicit_zero"], "modern_addition_explicit": row["modern_addition_explicit"]})
        compiled.append({"id": pitch, "head_atom": "PITCH:" + pitch, "sequence": sequence})
        summaries.append({"observer_id": row_id, "pitch": pitch, "memberships": len(memberships), "directed_mutations": len(mutations), "explicit_zero": row["explicit_zero"], "positions": len(sequence), "self_positions": sequence.count("SELF"), "sequence_sha256": sha(canonical(sequence)), "source_paragraph_inner_html_sha256": row["source_paragraph_inner_html_sha256"]})
    require(graph["pitches"] == expected_pitches, "all_graph_pitch_memberships_exact")
    require(graph["mutations"] == expected_mutations, "all_52_graph_mutation_arguments_exact")
    expected_origins = [{"id": PITCH[origin], "cantus_type": TYPE[origins[origin]], "origin_pitch": PITCH[origin]} for origin in sorted(origins)]
    require(graph["origins"] == expected_origins, "all_seven_origins_exact")
    require("P20" not in origins and len(origins) == 7, "no_added_cc_natural_origin")
    require(total_members == 42 and total_mutations == 52 and len(zero_ids) == 8, "complete_source_counts")
    require(direction_counts == {"ascending": 26, "descending": 26}, "literal_direction_counts")
    require(zero_ids == observer["explicit_zero_pitch_ids"], "all_explicit_zero_ids")
    require(packet["records"] == compiled, "all_416_compiled_positions_exact")
    atoms = sorted({atom for record in compiled for atom in record["sequence"]})
    require(packet["atoms"] == atoms and len(atoms) == 35, "all_35_atoms_exact")
    require(sum(len(record["sequence"]) for record in compiled) == 416, "416_positions")
    require(len({record["head_atom"] for record in compiled}) == 22, "distinct_pitch_heads")
    for flat, square in (("b_flat", "b_square"), ("bb_flat", "bb_square")):
        require("PITCH:" + flat in atoms and "PITCH:" + square in atoms, "flat_square_not_merged")
        require(next(r for r in compiled if r["id"] == flat)["sequence"] != next(r for r in compiled if r["id"] == square)["sequence"], "flat_square_complete_records_distinct")
    require(rows[0]["voice_memberships_in_written_order"][0]["raw_origin_phrase"] == "[Gamma] ut et sui", "gamma_duplicate_source_phrase_preserved")
    require(compiled[0]["sequence"] == ["PITCH:Gamma", "VOICE:ut", "CANTUS:hard", "SELF", "ZERO"], "gamma_alias_canonicalized_once")
    # Runtime primary comparison is downstream of the independent B compilation.
    probe = """import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('source_under_test',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.load(sys.argv[2]);print(json.dumps(m.compile_graph(p['source_graph'])))
"""
    process = subprocess.run([sys.executable, "-c", probe, str(compiler_path.resolve()), str(source_path.resolve())], check=True, capture_output=True, text=True)
    require(json.loads(process.stdout) == compiled, "primary_compiler_exact_runtime_parity")
    return {"schema": "GDT901_INDEPENDENT_SOURCE_VALIDATION_V1", "status": "PASS", "source_input_sha256": SOURCE_HASH, "validator_sha256": sha(Path(__file__).read_bytes()), "compiler_sha256": sha(compiler_path.read_bytes()), "source_receipt_sha256": RECEIPTS, "primary_html_sha256": observer["source"]["primary_html_sha256"], "chapter_inner_html_sha256": observer["source"]["chapter_inner_html_sha256"], "counts": {"records": 22, "atoms": 35, "positions": 416, "memberships": 42, "directed_mutations": 52, "ascending": 26, "descending": 26, "explicit_zero_records": 8, "origins": 7}, "records": summaries, "checks": ["All 22 named pitch aliases bound to B's source order and labels", "All 42 membership voice/type/origin triples included once in source order", "All 52 detailed mutation voice-pair/direction/destination-type/destination-origin tuples included once in source order", "Every origin equal to the record head becomes shared SELF, including Gamma's explicitly duplicated named/self phrase once", "All eight explicit zero records end with ZERO", "Both flat/square distinctions, octave case, final ee and absence of a cc origin retained", "The 416 positions and all 35 atoms agree exactly with independent B-derived compilation and primary runtime output"], "scope": "Validation of a fixed formal operational-register projection from two sealed readings of the TML electronic critical edition. Introductory duplicate lists, explanatory prose and lexical Latin wording are intentionally outside this model. This is not a new native manuscript or printed-edition collation. No target processing or fit."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-input", required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(args.source_input, args.compiler)
    output = Path(args.output)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    temporary.replace(output)
    print(json.dumps({"status": result["status"], "counts": result["counts"]}))


if __name__ == "__main__":
    main()
