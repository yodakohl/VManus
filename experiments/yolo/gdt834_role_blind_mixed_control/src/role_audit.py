#!/usr/bin/env python3
"""Discovery-only positional role census, with separately identified stages.

The default navigation diagnostic reads public GDT833 discovery only. --fresh
performs the prospective GDT834 ambiguity gate using anonymous discovery only.
Neither mode reads plaintext, keys, held ciphertext, reference models, or
manuscript material. Typed predecessor IDs are independently permuted to opaque
integers before inference; original prefixes enter only its post-audit table.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ROLE_ORDER = ("L", "S", "W")
CAPACITIES = (26, 4, 8)
PUBLIC_WORLDS = (83301, 83302, 83303)


def infer_domains(paragraphs, inventory_size=38):
    """Infer positional domains from anonymous IDs; no prefix or value input."""
    occurrences = [[] for _ in range(inventory_size)]
    for paragraph in paragraphs:
        for word in paragraph:
            if not word:
                raise ValueError("empty observation word")
            for position, symbol in enumerate(word):
                if not isinstance(symbol, int) or not 0 <= symbol < inventory_size:
                    raise ValueError("opaque symbol outside inventory")
                occurrences[symbol].append((position, len(word)))
    domains = []
    for events in occurrences:
        roles = {"L"}
        if all(length == 1 for _, length in events):
            roles.add("W")
        if all(position == length - 1 and length >= 4 for position, length in events):
            roles.add("S")
        domains.append(frozenset(roles))
    # Every possible suffix has literal-only predecessors by occurrence logic.
    for paragraph in paragraphs:
        for word in paragraph:
            if "S" in domains[word[-1]]:
                assert len(word) >= 4 and all(domains[symbol] == {"L"} for symbol in word[:-1])
    return domains, occurrences


def assignment_counts(domains, active, capacities=CAPACITIES):
    """Count active assignments separately from completions of unused slots."""
    if len(domains) != len(active) or len(domains) != sum(capacities):
        raise ValueError("inventory/capacity mismatch")
    distribution = {(0, 0, 0): 1}
    for domain, observed in zip(domains, active):
        if not observed:
            if domain != set(ROLE_ORDER):
                raise ValueError("unused symbols must retain all roles")
            continue
        following = Counter()
        for counts, number in distribution.items():
            for role in domain:
                index = ROLE_ORDER.index(role)
                changed = list(counts)
                changed[index] += 1
                if changed[index] <= capacities[index]:
                    following[tuple(changed)] += number
        distribution = dict(following)
    unused = sum(not value for value in active)
    observed_total = complete_total = 0
    allocation_rows = []
    for counts, number in sorted(distribution.items()):
        remaining = tuple(capacity - count for capacity, count in zip(capacities, counts))
        if min(remaining) < 0 or sum(remaining) != unused:
            continue
        multiplicity = math.factorial(unused)
        for count in remaining:
            multiplicity //= math.factorial(count)
        observed_total += number
        complete_total += number * multiplicity
        allocation_rows.append({
            "active_role_counts": dict(zip(ROLE_ORDER, counts)),
            "unused_role_counts": dict(zip(ROLE_ORDER, remaining)),
            "observable_assignments": number,
            "unused_completion_multiplicity": multiplicity,
            "complete_assignments": number * multiplicity,
        })
    return {
        "unused_slots": unused,
        "observable_role_assignments": observed_total,
        "complete_role_assignments": complete_total,
        "allocation_rows": allocation_rows,
    }


def opaque_projection(source, seed):
    # The complete nominal inventory is input metadata, not an active-role hint.
    labels = [f"{role}{index:02d}" for role, capacity in zip(ROLE_ORDER, CAPACITIES)
              for index in range(capacity)]
    random.Random(seed).shuffle(labels)
    opaque = {label: index for index, label in enumerate(labels)}
    paragraphs = [[[opaque[label] for label in word] for word in row["words"]]
                  for row in source["paragraphs"]]
    return paragraphs, labels


def audit_public_world(path, world):
    payload = path.read_bytes()
    source = json.loads(payload)
    if source.get("split") != "discovery" or source.get("world_id") != world:
        raise ValueError("unexpected public predecessor discovery identity")
    seed = 7000 + world
    paragraphs, original_labels = opaque_projection(source, seed)
    domains, events = infer_domains(paragraphs)
    counts = assignment_counts(domains, [bool(row) for row in events])
    groups = defaultdict(list)
    for symbol, domain in enumerate(domains):
        groups[tuple(sorted(domain))].append(symbol)
    # Original typed labels are consulted only after inferred domains/counts.
    group_rows = []
    for domain, symbols in sorted(groups.items()):
        group_rows.append({
            "allowed_roles": list(domain),
            "symbol_count": len(symbols),
            "occurrences": sum(len(events[symbol]) for symbol in symbols),
            "post_audit_original_role_counts": dict(sorted(Counter(original_labels[s][0] for s in symbols).items())),
        })
    ambiguous = [{
        "opaque_symbol": symbol,
        "allowed_roles": sorted(domains[symbol]),
        "occurrences": len(events[symbol]),
        "post_audit_original_symbol": original_labels[symbol],
    } for symbol in range(38) if events[symbol] and len(domains[symbol]) > 1]
    forced_occurrences = sum(len(events[symbol]) for symbol in range(38) if domains[symbol] == {"L"})
    total_occurrences = sum(map(len, events))
    return {
        "world_id": world,
        "source": path.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(payload).hexdigest(),
        "anonymous_permutation_seed": seed,
        "paragraphs": len(paragraphs),
        "word_occurrences": sum(map(len, paragraphs)),
        "primitive_occurrences": total_occurrences,
        "domain_groups": group_rows,
        "ambiguous_used_symbols": ambiguous,
        **counts,
        "forced_literal_occurrence_fraction": forced_occurrences / total_occurrences,
        "log2_observable_assignment_count": math.log2(counts["observable_role_assignments"]),
    }


def build_audit():
    rows = []
    for world in PUBLIC_WORLDS:
        path = ROOT / "experiments/yolo/gdt833_reference_orthography_intervention/prepared" / f"world_{world}_discovery.json"
        rows.append(audit_public_world(path, world))
    return {
        "schema": "GDT834_PUBLIC_PREDECESSOR_ROLE_AUDIT_V1",
        "status": "POSTHOC_DISCOVERY_POSITIONAL_IDENTIFIABILITY_DIAGNOSTIC",
        "nominal_capacities": dict(zip(ROLE_ORDER, CAPACITIES)),
        "active_role_counts_supplied_to_inference": False,
        "inference": "Opaque equality and within-word occurrence positions only; no frequencies, historical words, fitted keys, or plaintext used to assign domains.",
        "unused_equivalence": "Only equivalence on the observed discovery; no claim about future occurrences of unused symbols.",
        "interpretation": "This known architecture leaves a small finite role ambiguity after positional constraints. Removing typed prefixes alone is not general role or segmentation induction.",
        "public_worlds": rows,
        "audit_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "fresh_gdt834_accessed": False,
        "held_or_plaintext_accessed": False,
        "fits_run": 0,
    }


def anonymous_payload_audit(source, capacities=CAPACITIES):
    """Fresh input must contain only the fixed X00..X37 anonymous inventory."""
    if source.get("split") != "discovery":
        raise ValueError("role inference accepts discovery only")
    paragraphs = []
    for row in source["paragraphs"]:
        words = []
        for word in row["words"]:
            symbols = []
            for symbol in word:
                if not isinstance(symbol, str) or len(symbol) != 3 or symbol[0] != "X" or not symbol[1:].isdigit():
                    raise ValueError("fresh role audit requires opaque X identifiers")
                index = int(symbol[1:])
                if not 0 <= index < sum(capacities):
                    raise ValueError("opaque identifier outside inventory")
                symbols.append(index)
            words.append(symbols)
        paragraphs.append(words)
    domains, occurrences = infer_domains(paragraphs, sum(capacities))
    counts = assignment_counts(domains, [bool(events) for events in occurrences], capacities)
    group_counts = Counter(tuple(sorted(domain)) for domain in domains)
    return {
        "paragraphs": len(paragraphs),
        "word_occurrences": sum(map(len, paragraphs)),
        "primitive_occurrences": sum(map(len, occurrences)),
        "domain_groups": [{"allowed_roles": list(domain), "symbol_count": number}
                          for domain, number in sorted(group_counts.items())],
        "symbol_domains": {f"X{index:02d}": {"allowed_roles": sorted(domain),
                                              "occurrences": len(occurrences[index])}
                           for index, domain in enumerate(domains)},
        **counts,
    }


def build_fresh_audit():
    spec_path = EXP / "src/SPEC.json"
    spec = json.loads(spec_path.read_bytes())
    rows = []
    for world in spec["world_ids"]:
        path = EXP / "prepared" / f"world_{world}_discovery.json"
        raw = path.read_bytes()
        source = json.loads(raw)
        if source.get("world_id") != world:
            raise ValueError("anonymous discovery identity mismatch")
        result = anonymous_payload_audit(source)
        rows.append({"world_id": world, "source": path.relative_to(EXP).as_posix(),
                     "source_sha256": hashlib.sha256(raw).hexdigest(), **result})
    passed = bool(rows) and all(row["observable_role_assignments"] >= 2 for row in rows)
    return {
        "schema": "GDT834_PROSPECTIVE_ROLE_AMBIGUITY_V1",
        "status": "ROLE_AMBIGUITY_PASS" if passed else "ROLE_AMBIGUITY_STOP",
        "gate": "At least two observable role partitions on every anonymous discovery world",
        "stage": "Before fitting; no typed projection or truth accessed",
        "nominal_capacities": dict(zip(ROLE_ORDER, CAPACITIES)),
        "active_role_counts_supplied_to_inference": False,
        "worlds": rows,
        "spec_sha256": hashlib.sha256(spec_path.read_bytes()).hexdigest(),
        "audit_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "held_or_plaintext_accessed": False,
        "typed_projection_accessed": False,
        "fits_run": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fresh", action="store_true", help="prospective anonymous GDT834 discovery gate")
    args = parser.parse_args()
    result = build_fresh_audit() if args.fresh else build_audit()
    output = EXP / "artifacts" / ("ROLE_AMBIGUITY.json" if args.fresh else "ROLE_AUDIT_833.json")
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if args.check:
        if output.read_bytes() != encoded:
            raise RuntimeError("role-audit replay mismatch")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encoded)
    print(("FRESH_ROLE_AMBIGUITY_REPLAY_PASS" if args.check else result["status"]) if args.fresh else
          ("PUBLIC_PREDECESSOR_ROLE_AUDIT_REPLAY_PASS" if args.check else "PUBLIC_PREDECESSOR_ROLE_AUDIT_WRITTEN"))
    print(json.dumps({str(row["world_id"]): {key: row[key] for key in
                      ("observable_role_assignments", "complete_role_assignments", "unused_slots")}
                      for row in result["worlds" if args.fresh else "public_worlds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
