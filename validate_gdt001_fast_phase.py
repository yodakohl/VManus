#!/usr/bin/env python3
"""Independent CPU reconstruction of the compact GDT001 source follow-up."""

import json, math
from collections import Counter, defaultdict

from gdt001_core import ROOT, LETTERS, canonical, categorical_bits, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths


AXES = (("CURRIER", "currier"), ("SECTION", "section"), ("HAND", "hand"),
        ("KIND", "kind"), ("GRAMMAR_SCOPE", "grammar_scope"))


def cat(counter, alphabet):
    return categorical_bits([counter.get(i, 0) for i in range(alphabet)])


def main():
    checks = []
    def ok(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    _, lines = load_lattice(); paths = common_selected_paths(lines); alphabet_chars = [c for c in LETTERS if c not in "juz"]
    index = {c: i for i, c in enumerate(alphabet_chars)}; space = len(alphabet_chars); seqs = []; flags = []; rare = []
    for path in paths:
        seq = []
        for wi, word in enumerate(path.words):
            if wi: seq.append(space)
            for char in word:
                if char in "juz": flags.append(1); rare.append(char)
                else: flags.append(0); seq.append(index[char])
        seqs.append(seq)
    side = categorical_bits([flags.count(0), flags.count(1)]) + categorical_bits([rare.count(c) for c in "juz"])
    ok(Counter(rare) == Counter({"j": 2, "u": 2, "z": 3}), "rare_counts")
    order = 2; alphabet = len(alphabet_chars) + 1; global_counts = defaultdict(Counter)
    split = {name: defaultdict(lambda: defaultdict(Counter)) for name, _ in AXES}
    for line, seq in zip(lines, seqs):
        history = [alphabet] * order
        for token in seq:
            context = tuple(history); global_counts[context][token] += 1
            for name, field in AXES: split[name][context][getattr(line, field) or "_"][token] += 1
            history = history[1:] + [token]
    contexts = sorted(global_counts); base = sum(cat(global_counts[c], alphabet) for c in contexts); options = []
    for context in contexts:
        shared = cat(global_counts[context], alphabet); candidates = []
        for axis, _ in AXES:
            separated = sum(cat(counter, alphabet) for counter in split[axis][context].values())
            candidates.append((shared - separated, axis))
        gain, axis = max(candidates, key=lambda item: (item[0], item[1])); options.append((gain, context, axis))
    options.sort(key=lambda item: (-item[0], item[1], item[2])); n = len(options); cumulative = 0.0; candidates = []
    rare_key = universal_uint_bits(3) + math.log2(math.comb(len(LETTERS), 3))
    for k in range(n + 1):
        if k: cumulative += options[k - 1][0]
        subset = universal_uint_bits(k) + (math.log2(math.comb(n, k)) if 0 < k < n else 0.0) + k * math.log2(len(AXES))
        key = 3.0 + math.log2(3) + rare_key + subset; payload = base - cumulative
        candidates.append((sum(fixed_costs(paths).values()) + side + key + payload, k, key, payload))
    total, k, key, payload = min(candidates)
    result = json.loads((ROOT / "gdt001_context_axis_source_results.json").read_text()); published = result["best"]
    ok(result["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "status")
    ok(result["decision"] == "CONTINUE_CONTEXT_AXIS_SOURCE", "decision")
    ok(k == published["selected_contexts"] == 40 and n == published["available_contexts"] == 321, "context_counts")
    axis_counts = dict(sorted(Counter(item[2] for item in options[:k]).items()))
    ok(json.dumps(axis_counts, sort_keys=True, separators=(",", ":")) == published["axis_counts"], "axis_counts")
    ok(abs(total - published["total_bits"]) < 1e-8, "total_bits")
    ok(abs(key - published["key_bits"]) < 1e-8 and abs(payload - published["payload_bits"]) < 1e-8, "components")
    controls = json.loads((ROOT / "gdt001_context_axis_control_results.json").read_text())
    ok(controls["decision"] == "STOP_CONTROL_MATCHES_REAL", "control_stop")
    identity = next(x for x in controls["controls"] if x["manuscript"] == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION")
    timm = next(x for x in controls["controls"] if x["manuscript"] == "TIMM_COPY_MODIFY_SYNTHETIC")
    ok(abs(identity["gain_vs_matched_global_bits"] - controls["real"]["gain_vs_matched_global_bits"]) < 1e-8, "identity_invariance")
    ok(timm["gain_vs_matched_global_bits"] > controls["real"]["gain_vs_matched_global_bits"], "timm_exceeds_real")
    boundary = json.loads((ROOT / "gdt001_boundary_rule_results.json").read_text())
    ok(boundary["decision"].startswith("STOP_BOUNDARY_RULES"), "boundary_stop")
    ok(boundary["accounting_correction"] == "EXACT_KT_BINARY_MASK_RESTORES_EVERY_DROPPED_MANUAL_BOUNDARY_POSITION", "boundary_mask")
    role = json.loads((ROOT / "gdt001_role_conditioned_source_results.json").read_text())
    ok(role["decision"] == "STOP_ROLE_CONDITIONED_SOURCE", "role_stop")
    output = {"schema": "GDT001_FAST_PHASE_VALIDATION_V1", "status": "PASS_INDEPENDENT_CPU_RECONSTRUCTION",
              "check_count": len(checks), "checks": checks, "total_bits": total, "bits_per_symbol": published["bits_per_symbol"],
              "selected_contexts": k, "axis_counts": axis_counts,
              "claim_ceiling": "Exact exploratory score reconstruction only; no language, cipher, meaning, plaintext, or translation."}
    (ROOT / "gdt001_fast_phase_validation.json").write_bytes(canonical(output))
    print(json.dumps({"status": output["status"], "checks": len(checks), "bits_per_symbol": output["bits_per_symbol"]}))


if __name__ == "__main__":
    main()
