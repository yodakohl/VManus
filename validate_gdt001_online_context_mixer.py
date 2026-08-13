#!/usr/bin/env python3
"""Independent deterministic reconstruction of the causal context mixer."""

import hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

from gdt001_core import LETTERS, canonical, fixed_costs, load_lattice, universal_uint_bits
from gdt001_scaffold_payload import common_selected_paths
from run_gdt001_source_selected_nulls import encoded

ROOT = Path(__file__).resolve().parent
SHARES = (0.0, 1 / 4096, 1 / 1024, 1 / 256, 1 / 64, 1 / 16)
EXPERTS = (("SHARED", None), ("HISTORY3", None), ("CURRIER", "currier"), ("SECTION", "section"),
           ("HAND", "hand"), ("KIND", "kind"), ("GRAMMAR_SCOPE", "grammar_scope"))


def probability(counter, token, alphabet):
    return (counter[token] + .5) / (sum(counter.values()) + .5 * alphabet)


def reconstruct(lines, paths, share):
    nulls = frozenset("juz"); sequences, _, _, active, _, side = encoded(paths, nulls); alphabet = len(active) + 1; bos = alphabet
    tables = {name: defaultdict(Counter) for name, _ in EXPERTS}; weights = {}; payload = 0.0; dominant = Counter()
    for line, sequence in zip(lines, sequences):
        history = [bos, bos, bos]
        for token in sequence:
            context = tuple(history[-2:]); keys = [("SHARED", context), ("HISTORY3", (context, history[-3]))]
            keys.extend((name, (context, getattr(line, field) or "_")) for name, field in EXPERTS[2:])
            counters = [tables[name][key] for name, key in keys]; probabilities = [probability(counter, token, alphabet) for counter in counters]
            current = weights.setdefault(context, [1 / len(counters)] * len(counters)); mixture = sum(weight * p for weight, p in zip(current, probabilities))
            payload -= math.log2(mixture); posterior = [weight * p / mixture for weight, p in zip(current, probabilities)]
            weights[context] = [(1 - share) * value + share / len(counters) for value in posterior]
            dominant[EXPERTS[max(range(len(current)), key=lambda i: (current[i], EXPERTS[i][0]))][0]] += 1
            for counter in counters: counter[token] += 1
            history = history[1:] + [token]
    rare_key = universal_uint_bits(3) + math.log2(math.comb(len(LETTERS), 3)); key = 3.0 + rare_key + math.log2(2) + math.log2(len(SHARES)); fixed = sum(fixed_costs(paths).values())
    return {"share": share, "total_bits": fixed + side + key + payload, "key_bits": key, "payload_bits": payload, "side_channel_bits": side,
            "fixed_bits": fixed, "dominant_expert_events": json.dumps(dict(sorted(dominant.items())), sort_keys=True, separators=(",", ":"))}


def main():
    checks = []
    def need(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    result = json.load(open(ROOT / "gdt001_online_context_mixer_results.json")); controls = json.load(open(ROOT / "gdt001_online_context_mixer_control_results.json"))
    need(result["schema"] == "GDT001_ONLINE_CONTEXT_MIXER_V1", "schema"); need(result["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "status")
    _, lines = load_lattice(); paths = common_selected_paths(lines); rebuilt = [reconstruct(lines, paths, share) for share in SHARES]
    need([row["share"] for row in result["rows"]] == list(SHARES), "share_grid")
    for expected, stored in zip(rebuilt, result["rows"]):
        for field in ("total_bits", "key_bits", "payload_bits", "side_channel_bits", "fixed_bits"):
            need(abs(expected[field] - stored[field]) < 1e-6, f"rebuild_{field}_{stored['share']}")
        need(expected["dominant_expert_events"] == stored["dominant_expert_events"], f"dominance_{stored['share']}")
    winner = min(rebuilt, key=lambda row: row["total_bits"]); need(winner["share"] == result["best"]["share"] == 1 / 64, "winning_share")
    need(abs(winner["total_bits"] - result["best"]["total_bits"]) < 1e-6, "winning_total")
    decoder = result["best"]["decoder"]; need(hashlib.sha256(canonical(decoder)).hexdigest() == result["best"]["decoder_hash"], "decoder_hash"); need(decoder["serialization_order"] == "canonical corpus-lattice line order, not asserted physical writing chronology", "serialization_order")
    need(sum(len(word) for path in paths for word in path.words) == 194324, "source_symbols")
    need(controls["decision"] == "STOP_CONTROL_MATCHES_CONTEXT_MIXER", "control_stop"); real_gain = controls["real"]["gain_vs_matched_variable_context_bits"]
    identity = next(row for row in controls["controls"] if row["manuscript"] == "BOUNDARY_PRESERVING_IDENTITY_PERMUTATION")
    timm = next(row for row in controls["controls"] if row["manuscript"] == "TIMM_COPY_MODIFY_SYNTHETIC")
    need(abs(real_gain - identity["gain_vs_matched_variable_context_bits"]) < 1e-6, "identity_invariance"); need(timm["gain_vs_matched_variable_context_bits"] > real_gain, "timm_exceeds_real")
    output = {"schema": "GDT001_ONLINE_CONTEXT_MIXER_VALIDATION_V1", "status": "PASS_CPU_EXACT_RECONSTRUCTION_CONTROL_NOT_SPECIFIC",
              "check_count": len(checks), "checks": checks, "total_bits": winner["total_bits"],
              "claim_ceiling": "Independent source-code arithmetic only; no language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_online_context_mixer_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "total_bits": winner["total_bits"]}))


if __name__ == "__main__": main()
