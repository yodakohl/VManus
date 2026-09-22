"""Independent GDT1031 reconstruction; never imports the primary runner.

--self-test reads only SPEC and constructed fixtures.  --execute is for the
root-authorized post-publication validation phase and prints its receipt.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys

import numpy as np


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


class ValidationFailure(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ValidationFailure(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def family_maps(spec):
    lookup = {}
    for fi, family in enumerate(spec["families"]):
        lengths = family["forms_and_raw_lengths"]
        low, high = min(lengths.values()), max(lengths.values())
        require(high > low, "family has no fixed length contrast")
        for form, length in lengths.items():
            require(form not in lookup, "overlapping families")
            require(len(form) == length and form.isascii(), "wrong raw length")
            lookup[form] = (fi, family["value"], length,
                            (length - low) / (high - low))
    require(len(lookup) == 14 and len(spec["families"]) == 6,
            "six/fourteen invariant")
    return lookup


def block_sort(block):
    return (block["paragraph"], block["family_index"], block["edge"],
            block["prev_dy"], block["current_dy"])


def reconstruct(packet, spec):
    """Selector/metadata gates precede every access to a words field."""
    forms = family_maps(spec)
    scope, occurrences, blocks = [], [], []
    literal_text = {}
    require(set(packet) == set(spec["readers"]), "reader keys differ")
    for reader in spec["readers"]:
        require(isinstance(packet[reader], list), "reader is not a paragraph list")
        ids = set()
        source_ids = set()
        for para in sorted(packet[reader], key=lambda p: p["id"]):
            page = para["page"]
            require(isinstance(page, str), "nonstring selector")
            require(not page.startswith(spec["forbidden_prefix"])
                    and page not in spec["forbidden_exact"], "forbidden selector")
            leaf_match = re.match(r"^f([0-9]+)", page)
            require(leaf_match is not None, "unparseable leaf selector")
            leaf = int(leaf_match.group(1))
            require(type(para["leaf"]) is int and para["leaf"] == leaf,
                    "selector/leaf disagreement")
            pid = para["id"]
            require(pid.startswith(page + "|") and pid not in ids,
                    "paragraph identity mismatch/duplicate")
            ids.add(pid)
            lines = para["lines"]
            row = dict(reader=reader, paragraph=pid, page=page, leaf=leaf,
                       groups=para["groups"],
                       lines=[dict(locus=l["locus"],
                                   anchor_eligible=l.get("anchor_eligible"))
                              for l in lines])
            if leaf in spec["exclude_leaves"]:
                row["category"] = "EXCLUDED_DEVELOPMENT"
                scope.append(row)
                continue
            if not lines or any(l.get("anchor_eligible") is not True for l in lines):
                row["category"] = "SOURCE_UNCERTAIN"
                scope.append(row)
                continue
            row["category"] = "LITERAL"
            require(pid == page + "|" + lines[0]["locus"] + "-" + lines[-1]["locus"],
                    "paragraph boundary identity differs")
            per_family = defaultdict(list)
            offset = 0
            for line in lines:
                require(line["locus"].startswith(page + "."), "line selector differs")
                words, sids = line["words"], line["source_ids"]
                require(len(words) == len(sids), "word/source-ID length mismatch")
                require(line["offset"] == offset, "noncontiguous paragraph offset")
                literal_text[(reader, pid, line["locus"])] = tuple(words)
                for i, (word, sid) in enumerate(zip(words, sids)):
                    require(isinstance(word, str), "nonstring whole form")
                    require(sid not in source_ids, "source ID repeated in reader")
                    source_ids.add(sid)
                    if word not in forms:
                        continue
                    fi, name, length, z = forms[word]
                    if len(words) == 1:
                        edge = "SINGLE"
                    elif i == 0:
                        edge = "FIRST"
                    elif i == len(words) - 1:
                        edge = "LAST"
                    else:
                        edge = "INTERIOR"
                    per_family[fi].append(dict(
                        reader=reader, paragraph=pid, leaf=leaf,
                        family=name, family_index=fi, position=offset+i+1,
                        locus=line["locus"], line_position=i+1, source_id=sid,
                        form=word, length=length, z=z,
                        edge=edge, prev_dy=i > 0 and words[i-1].endswith("dy"),
                        current_dy=word.endswith("dy")))
                offset += len(words)
            require(offset == para["groups"] and offset > 0,
                    "whole paragraph group count mismatch/empty")
            local_blocks = []
            for fi in sorted(per_family):
                family_occ = per_family[fi]
                m = len(family_occ)
                by_layout = defaultdict(list)
                for j, occ in enumerate(family_occ):
                    occ["family_count"] = m
                    occ["u"] = j / (m-1) if m > 1 else None
                    occurrences.append(occ)
                    by_layout[(occ["edge"], occ["prev_dy"], occ["current_dy"])].append(occ)
                for layout, group in by_layout.items():
                    edge, prev, current = layout
                    name = group[0]["family"]
                    labels = [o["form"] for o in group]
                    counts = dict(sorted(Counter(labels).items()))
                    local_blocks.append(dict(
                        id="#".join((reader, pid, name, edge, str(int(prev)), str(int(current)))),
                        reader=reader, paragraph=pid, leaf=leaf, family=name,
                        family_index=fi, edge=edge, prev_dy=prev, current_dy=current,
                        source_ids=[o["source_id"] for o in group], forms=labels,
                        u=[o["u"] for o in group], z=[o["z"] for o in group],
                        counts=counts, dp_states=math.prod(c+1 for c in counts.values()),
                        mobile=len(group) >= 2 and len({o["length"] for o in group}) >= 2))
            row["literal_category"] = ("NO_FAMILY" if not per_family else
                                       "MOBILE" if any(b["mobile"] for b in local_blocks)
                                       else "IMMOBILE")
            scope.append(row)
            blocks.extend(sorted(local_blocks, key=block_sort))
    return scope, occurrences, blocks, literal_text


def capacity(blocks, scope, packet, spec):
    cap = spec["capacity"]
    out = {}
    for reader in spec["readers"]:
        mobile = [b for b in blocks if b["reader"] == reader and b["mobile"]]
        family_info = {}
        for family in spec["families"]:
            relevant = [b for b in mobile if b["family"] == family["value"]]
            leaves = sorted({b["leaf"] for b in relevant})
            family_info[family["value"]] = dict(
                blocks=len(relevant), positions=sum(len(b["forms"]) for b in relevant),
                leaves=leaves,
                powered=len(relevant) >= cap["family_blocks"] and len(leaves) >= cap["family_leaves"])
        leaves = sorted({b["leaf"] for b in mobile})
        positions = sum(len(b["forms"]) for b in mobile)
        powered = [f["value"] for f in spec["families"] if family_info[f["value"]]["powered"]]
        passed = (len(mobile) >= cap["blocks"] and positions >= cap["positions"]
                  and len(leaves) >= cap["leaves"] and len(powered) >= cap["families"])
        out[reader] = dict(blocks=len(mobile), positions=positions, leaves=leaves,
                           families=family_info, powered_families=powered, passes=passed,
                           status=("NO_OWNED_PARAGRAPH_DATA" if not packet[reader] else
                                   "CAPACITY_PASS" if passed else "NO_CAPACITY"))
    return out


def log_partition(u, counts, z_by_form, beta=math.log(3), state_cap=100000):
    """Recursive remaining-count DP over DISTINCT multiset strings."""
    labels = tuple(sorted(counts))
    initial = tuple(counts[w] for w in labels)
    states = math.prod(c+1 for c in initial)
    require(states <= state_cap, "ENGINEERING_BUDGET_OR_STATE_CAP")
    n = sum(initial)
    require(n == len(u) and all(x is not None for x in u), "invalid DP ranks")
    if n*3 + 200 > sys.getrecursionlimit():
        sys.setrecursionlimit(n*3 + 200)

    @lru_cache(maxsize=None)
    def remaining(state):
        total = sum(state)
        if total == 0:
            return 0.0
        pos = n-total
        terms = []
        for k, amount in enumerate(state):
            if amount:
                next_state = state[:k] + (amount-1,) + state[k+1:]
                terms.append(-beta*u[pos]*z_by_form[labels[k]] + remaining(next_state))
        high = max(terms)
        return high + math.log(math.fsum(math.exp(x-high) for x in terms))

    log_z = remaining(initial)
    require(remaining.cache_info().currsize <= states, "DP state count overflow")
    log_n = math.lgamma(n+1) - math.fsum(math.lgamma(c+1) for c in initial)
    return log_z, log_n, remaining.cache_info().currsize


def block_parameters(block, spec, fmap):
    require(block["mobile"], "score requested for immobile block")
    zmap = {w: fmap[w][3] for w in block["counts"]}
    log_z, log_n, visited = log_partition(block["u"], block["counts"], zmap,
                                         state_cap=spec["dp_state_cap"])
    return dict(logZ=log_z, logN=log_n, visited_states=visited,
                base=(log_n-log_z)/math.log(2), zmap=zmap)


def gain(block, labels, params):
    energy = math.fsum(u*params["zmap"][w] for u, w in zip(block["u"], labels))
    return params["base"] - (math.log(3)/math.log(2))*energy


def aggregate(blocks, gains, spec):
    leaf_gain = defaultdict(list)
    leaf_positions = Counter()
    family_leaf_gain = defaultdict(lambda: defaultdict(list))
    family_leaf_positions = defaultdict(Counter)
    for block, value in zip(blocks, gains):
        leaf, family = block["leaf"], block["family"]
        n = len(block["forms"])
        leaf_gain[leaf].append(value)
        leaf_positions[leaf] += n
        family_leaf_gain[family][leaf].append(value)
        family_leaf_positions[family][leaf] += n
    leaves = {str(f): dict(gain_bits=math.fsum(leaf_gain[f]), positions=leaf_positions[f],
                           gain_per_position=math.fsum(leaf_gain[f])/leaf_positions[f])
              for f in sorted(leaf_gain)}
    families = {}
    for family in spec["families"]:
        name = family["value"]
        fs = family_leaf_gain[name]
        vals = [math.fsum(fs[f])/family_leaf_positions[name][f] for f in sorted(fs)]
        families[name] = (math.fsum(vals)/len(vals) if vals else None)
    g = math.fsum(x["gain_per_position"] for x in leaves.values())/len(leaves)
    return dict(G=g, leaves=leaves, families=families)


def evaluate(blocks, cap, occurrences, literal_text, spec):
    fmap = family_maps(spec)
    readers = [r for r in spec["readers"] if cap[r]["passes"]]
    mobile = {r: sorted([b for b in blocks if b["reader"] == r and b["mobile"]],
                        key=block_sort) for r in readers}
    params, observed, block_scores = {}, {}, []
    for reader in readers:
        ps = [block_parameters(b, spec, fmap) for b in mobile[reader]]
        params[reader] = ps
        gs = []
        for block, p in zip(mobile[reader], ps):
            value = gain(block, block["forms"], p)
            gs.append(value)
            block_scores.append(dict(id=block["id"], gain_bits=value,
                                      logZ=p["logZ"], logN=p["logN"]))
        observed[reader] = aggregate(mobile[reader], gs, spec)
    if not readers:
        return observed, [], block_scores
    sid_meta = {o["source_id"]: o for o in occurrences}
    rng = np.random.Generator(np.random.PCG64(spec["seed"]))
    worlds = []
    for world in range(1, spec["null_worlds"]+1):
        scores, changed = {}, {}
        for reader in readers:
            gs, changed_count, replacement = [], 0, {}
            for block, p in zip(mobile[reader], params[reader]):
                labels = [block["forms"][int(i)] for i in rng.permutation(len(block["forms"]))]
                require(Counter(labels) == Counter(block["forms"]), "null multiset changed")
                for sid, old, new in zip(block["source_ids"], block["forms"], labels):
                    require(old.endswith("dy") == new.endswith("dy"), "self-dy stratum violated")
                    replacement[sid] = new
                    changed_count += old != new
                gs.append(gain(block, labels, p))
            # Explicitly rebuild every affected line, then recompute PREV_DY
            # for every group in it, including nonfamily and immobile groups.
            affected = {}
            for sid, new in replacement.items():
                occ = sid_meta[sid]
                key = (reader, occ["paragraph"], occ["locus"])
                if key not in affected:
                    affected[key] = list(literal_text[key])
                affected[key][occ["line_position"]-1] = new
            for key, after in affected.items():
                before = literal_text[key]
                for i in range(len(before)):
                    old_prev = i > 0 and before[i-1].endswith("dy")
                    new_prev = i > 0 and after[i-1].endswith("dy")
                    require(old_prev == new_prev, "null changed preceding-dy covariate")
            scores[reader] = aggregate(mobile[reader], gs, spec)["G"]
            changed[reader] = changed_count
        worlds.append(dict(world=world, scores=scores, changed_positions=changed))
    for reader in readers:
        result = observed[reader]
        vals = [w["scores"][reader] for w in worlds]
        tol, g = spec["tail_tolerance"], result["G"]
        result["p_upper"] = (1+sum(v >= g-tol for v in vals))/(len(vals)+1)
        result["p_lower"] = (1+sum(v <= g+tol for v in vals))/(len(vals)+1)
        result["positive_leaf_fraction"] = sum(x["gain_per_position"] > 0 for x in result["leaves"].values())/len(result["leaves"])
        result["positive_powered_families"] = [name for name in cap[reader]["powered_families"]
                                                if result["families"][name] > 0]
        result["supported"] = (g > 0 and result["p_upper"] <= spec["support"]["tail_upper"]
                               and result["positive_leaf_fraction"] >= spec["support"]["positive_leaf_fraction"]
                               and len(result["positive_powered_families"]) >= spec["support"]["positive_powered_families"])
        result["adverse"] = g < 0 and result["p_lower"] <= spec["support"]["tail_upper"]
        result["status"] = ("SUPPORTED" if result["supported"] else
                            "ADVERSE" if result["adverse"] else
                            "FAIL_FIXED_PREDICTION" if g <= 0 else "INCONCLUSIVE")
    return observed, worlds, block_scores


def assert_tree(actual, expected, at="root", tol=1e-10):
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), at+": keys differ")
        for key in expected:
            assert_tree(actual[key], expected[key], at+"."+key, tol)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), at+": list length differs")
        for i, (a, e) in enumerate(zip(actual, expected)):
            assert_tree(a, e, at+f"[{i}]", tol)
    elif isinstance(expected, float):
        require(isinstance(actual, (int, float)) and math.isfinite(actual)
                and abs(actual-expected) <= tol, at+": numeric mismatch")
    else:
        require(type(actual) is type(expected) and actual == expected, at+": differs")


def check_locked_inputs(spec):
    lock = read_json(EXP/"PREREG_LOCK.json")
    require("files" in lock and isinstance(lock["files"], dict), "lock format")
    required = [Path(__file__).resolve().relative_to(ROOT).as_posix(),
                (EXP/"src/SPEC.json").relative_to(ROOT).as_posix(),
                (EXP/"PREREGISTRATION.md").relative_to(ROOT).as_posix(),
                (EXP/"src/run.py").relative_to(ROOT).as_posix(),
                spec["proposal_path"], spec["parent"]["path"], spec["packet"]["path"]]
    require(set(required).issubset(lock["files"]), "critical scientific file absent from lock")
    for relative, expected in lock["files"].items():
        require(not Path(relative).is_absolute() and ".." not in Path(relative).parts,
                "unsafe lock path")
        require(digest(ROOT/relative) == expected, "lock digest changed: "+relative)
    for binding in [dict(path=spec["proposal_path"], sha256=spec["proposal_sha256"]),
                    spec["parent"], spec["packet"]]:
        require(digest(ROOT/binding["path"]) == binding["sha256"], "input digest changed")
    proposal = read_json(ROOT/spec["proposal_path"])
    require(proposal["six_frozen_synonym_sets"] == spec["families"], "proposal families differ")
    parent = read_json(ROOT/spec["parent"]["path"])
    entries = sum((parent[k] for k in spec["parent"]["json_locations"]), [])
    require(len(entries) == spec["parent"]["entries"] == 59, "parent entry count")
    lexical = {x["form"]: x for x in entries}
    require(len(lexical) == 59, "duplicate parent forms")
    for family in spec["families"]:
        for form in family["forms_and_raw_lengths"]:
            require(lexical[form]["value"] == family["value"], "parent synonym tag differs")
    return {"prereg_lock_sha256": digest(EXP/"PREREG_LOCK.json"),
            "validator_sha256": digest(Path(__file__)), "locked_files": len(lock["files"])}


def fixture(words, leaf=12, anchor=True, suffix="r"):
    page = f"f{leaf}{suffix}"
    locus = page+".1"
    return dict(id=page+"|"+locus+"-"+locus, page=page, leaf=leaf,
                groups=len(words), lines=[dict(locus=locus, row=1, start=True, end=True,
                    offset=0, words=words, source_ids=[f"ZL3b|{locus}|G{i+1:03}" for i in range(len(words))],
                    anchor_eligible=anchor)])


def self_test(spec):
    checks = []
    # Independent exhaustive distinct-string calculation catches multiplicity errors.
    for labels, u, z in [(["a", "b"], [0, 1], {"a": 0., "b": 1.}),
                         (["a", "a", "b"], [0, .5, 1], {"a": 0., "b": 1.}),
                         (["a", "b", "c", "a"], [0, .2, .8, 1], {"a": 0., "b": .25, "c": 1.})]:
        distinct = set(itertools.permutations(labels))
        zz = math.fsum(math.exp(-math.log(3)*sum(ui*z[w] for ui, w in zip(u, ws))) for ws in distinct)
        dp, logn, _ = log_partition(u, Counter(labels), z)
        require(abs(dp-math.log(zz)) < 1e-12 and abs(logn-math.log(len(distinct))) < 1e-12,
                "distinct-permutation DP mismatch")
    checks.append("recursive_DP_matches_three_exhaustive_multisets")
    zz, _, _ = log_partition([0, 1], {"a": 1, "b": 1}, {"a": 0., "b": 1.})
    require(abs(math.exp(-zz)-.75) < 1e-12, "two-position directional probability")
    checks.append("long_then_short_probability_3_over_4")
    data = {r: [] for r in spec["readers"]}
    data["ZL3b"] = [fixture(["a", "qoky", "b", "r", "c"]),
                     fixture(["a", "qokain", "b", "okedy", "c"], leaf=13)]
    scope, occ, blocks, text = reconstruct(data, spec)
    require(sum(b["mobile"] for b in blocks) == 1, "synthetic block mobility")
    require(all(not b["mobile"] for b in blocks if b["family"] == "LENTIL"), "dy split failed")
    require([o["u"] for o in occ if o["family"] == "IS"] == [0., 1.], "family ranks")
    cap = capacity(blocks, scope, data, spec)
    require(not any(x["passes"] for x in cap.values()), "no-capacity fixture passed")
    require(cap["RF1b"]["status"] == "NO_OWNED_PARAGRAPH_DATA", "RF empty treated as failure")
    require(evaluate(blocks, cap, occ, text, spec) == ({}, [], []), "no-capacity scored")
    checks.append("ranks_strata_LENTIL_immobility_and_no_capacity_stop")
    class Poison(dict):
        def __getitem__(self, key):
            if key in ("words", "source_ids"):
                raise AssertionError("payload accessed before metadata gate")
            return super().__getitem__(key)
    for leaf, anchor, expected in [(76, True, "EXCLUDED_DEVELOPMENT"),
                                    (80, True, "EXCLUDED_DEVELOPMENT"),
                                    (14, False, "SOURCE_UNCERTAIN"),
                                    (14, 1, "SOURCE_UNCERTAIN")]:
        p = fixture(["qoky", "r"], leaf=leaf, anchor=anchor)
        p["lines"] = [Poison(p["lines"][0])]
        packet = {r: [] for r in spec["readers"]}; packet["ZL3b"] = [p]
        s, o, b, _ = reconstruct(packet, spec)
        require(s[0]["category"] == expected and not o and not b, "whole metadata gate")
    for page in ("f84r", "f84v", "f116v"):
        p = fixture(["qoky", "r"]); p["page"] = page
        p["lines"] = [Poison(p["lines"][0])]
        packet = {r: [] for r in spec["readers"]}; packet["ZL3b"] = [p]
        try:
            reconstruct(packet, spec)
            raise AssertionError("forbidden selector admitted")
        except ValidationFailure as error:
            require(str(error) == "forbidden selector", "wrong forbidden failure")
    checks.append("poison_payload_selector_development_and_whole_uncertainty_gates")
    try:
        log_partition([0, 1], {"a": 1, "b": 1}, {"a": 0., "b": 1.}, state_cap=3)
        raise AssertionError("DP state cap not enforced")
    except ValidationFailure as error:
        require(str(error) == "ENGINEERING_BUDGET_OR_STATE_CAP", "wrong state-cap failure")
    checks.append("state_cap_before_recursion")
    # Global paragraph ranks are not recomputed separately in layout blocks.
    rank_packet = {r: [] for r in spec["readers"]}
    rank_packet["ZL3b"] = [fixture(["qoky", "r", "x", "qoky"], leaf=19)]
    _, ranked, rank_blocks, _ = reconstruct(rank_packet, spec)
    require([o["u"] for o in ranked] == [0., .5, 1.], "rank reset at layout boundary")
    require({b["edge"] for b in rank_blocks} == {"FIRST", "INTERIOR", "LAST"},
            "physical edge classification")
    checks.append("paragraph_rank_precedes_layout_partition")
    # A small explicitly synthetic capacity-open run exercises nulls and gates.
    synthetic_spec = json.loads(json.dumps(spec))
    synthetic_spec["capacity"] = dict(blocks=1, positions=2, leaves=1, families=1,
                                       family_blocks=1, family_leaves=1)
    synthetic_spec["null_worlds"] = 15
    synthetic_packet = {r: [] for r in spec["readers"]}
    synthetic_packet["ZL3b"] = [fixture(["a", "qoky", "b", "r", "c"])]
    other = fixture(["a", "sshey", "b", "sol", "c", "or", "d", "sol", "e"], leaf=15)
    other["lines"][0]["source_ids"] = [s.replace("ZL3b|", "IT2a|") for s in other["lines"][0]["source_ids"]]
    synthetic_packet["IT2a"] = [other]
    sc, oc, bs, tx = reconstruct(synthetic_packet, synthetic_spec)
    cp = capacity(bs, sc, synthetic_packet, synthetic_spec)
    obs, nulls, _ = evaluate(bs, cp, oc, tx, synthetic_spec)
    require(set(obs) == {"ZL3b", "IT2a"} and len(nulls) == 15,
            "capacity-passing reader/null coverage")
    independent_rng = np.random.Generator(np.random.PCG64(spec["seed"]))
    fmap = family_maps(spec)
    for world in nulls:
        for reader in ["ZL3b", "IT2a"]:
            block, = [b for b in bs if b["reader"] == reader and b["mobile"]]
            original = block["forms"]
            permuted = [original[int(i)] for i in independent_rng.permutation(len(original))]
            possible = set(itertools.permutations(original))
            weight = lambda labels: math.exp(-math.log(3)*sum(u*fmap[w][3] for u,w in zip(block["u"], labels)))
            brute_gain = math.log2(len(possible)*weight(permuted)/sum(weight(x) for x in possible))
            require(abs(world["scores"][reader]-brute_gain/len(original)) < 1e-12,
                    "null likelihood/order differs from direct enumeration")
            require(world["changed_positions"][reader] == sum(a != b for a,b in zip(original, permuted)),
                    "null realized label movement differs")
    for reader, result in obs.items():
        vals = [w["scores"][reader] for w in nulls]
        upper = (1+sum(v >= result["G"]-spec["tail_tolerance"] for v in vals))/16
        lower = (1+sum(v <= result["G"]+spec["tail_tolerance"] for v in vals))/16
        require(upper == result["p_upper"] and lower == result["p_lower"], "inclusive tails")
    checks.append("two_reader_PCG64_world_order_multiset_null_bruteforce_and_tails")
    return dict(status="PASS", checks=checks, count=len(checks),
                manuscript_packets_opened=False, primary_runner_imported=False)


def validate(spec):
    receipts = check_locked_inputs(spec)
    packet = read_json(ROOT/spec["packet"]["path"])
    scope, occ, blocks, text = reconstruct(packet, spec)
    primary_scope = read_json(EXP/"artifacts/SCOPE.json")
    primary_occ = read_json(EXP/"artifacts/OCCURRENCES.json")
    primary_blocks = read_json(EXP/"artifacts/BLOCKS.json")
    rorder = {r: i for i, r in enumerate(spec["readers"])}
    skey = lambda row: (rorder[row["reader"]], row["paragraph"])
    okey = lambda row: (rorder[row["reader"]], row["paragraph"], row["position"])
    assert_tree(sorted(primary_scope, key=skey), sorted(scope, key=skey), "scope")
    assert_tree(sorted(primary_occ, key=okey), sorted(occ, key=okey), "occurrences")
    assert_tree(primary_blocks, blocks, "blocks")
    cap = capacity(blocks, scope, packet, spec)
    observed, worlds, block_scores = evaluate(blocks, cap, occ, text, spec)
    assert_tree(read_json(EXP/"artifacts/NULL.json"), worlds, "null")
    result_checks = compare_results(cap, observed, block_scores, scope, occ, blocks, spec)
    return dict(status="PASS", independent=True, primary_runner_imported=False,
                scope_rows=len(scope), occurrences=len(occ), all_blocks=len(blocks),
                mobile_blocks=sum(b["mobile"] for b in blocks), null_worlds=len(worlds),
                capacity=cap, scores=observed, result_checks=result_checks, receipts=receipts)


def compare_results(cap, observed, block_scores, scope, occ, blocks, spec):
    """Root-declared artifact interface, fixed before either target execution."""
    capacity_expected = {}
    for reader in spec["readers"]:
        reader_scope = [s for s in scope if s["reader"] == reader]
        c = cap[reader]
        capacity_expected[reader] = dict(
            scope_paragraphs=len(reader_scope), scope_groups=sum(s["groups"] for s in reader_scope),
            categories=dict(Counter(s["category"] for s in reader_scope)),
            literal_categories=dict(Counter(s["literal_category"] for s in reader_scope
                                            if s["category"] == "LITERAL")),
            occurrences=sum(o["reader"] == reader for o in occ),
            mobile_blocks=c["blocks"], mobile_positions=c["positions"], mobile_leaves=len(c["leaves"]),
            families={name: dict(blocks=d["blocks"], positions=d["positions"],
                                 leaves=len(d["leaves"]), powered=d["powered"])
                      for name, d in c["families"].items()},
            powered_families=len(c["powered_families"]), passes=c["passes"],
            status="READY" if c["passes"] else c["status"])
    assert_tree(read_json(EXP/"artifacts/CAPACITY.json"), capacity_expected, "capacity")
    by_id = {b["id"]: b for b in blocks}
    likelihoods = []
    for row in block_scores:
        b = by_id[row["id"]]
        likelihoods.append(dict(block_id=row["id"], log_partition=row["logZ"],
                                log_distinct_assignments=row["logN"],
                                energy=math.fsum(u*z for u, z in zip(b["u"], b["z"])),
                                gain_bits=row["gain_bits"]))
    assert_tree(read_json(EXP/"artifacts/LIKELIHOODS.json"), likelihoods, "likelihoods")
    reader_results = {}
    for reader in spec["readers"]:
        if reader not in observed:
            reader_results[reader] = dict(status=capacity_expected[reader]["status"], supports=False, G=None)
            continue
        d = observed[reader]
        reader_results[reader] = dict(
            G=d["G"], leaf_scores={leaf: x["gain_per_position"] for leaf, x in d["leaves"].items()},
            family_scores=d["families"], positive_leaf_fraction=d["positive_leaf_fraction"],
            positive_powered_families=len(d["positive_powered_families"]),
            tail_upper=d["p_upper"], tail_lower=d["p_lower"], supports=d["supported"],
            status=("SUPPORT_CONDITIONAL_WRITING_RULE" if d["supported"] else
                    "FAIL_FIXED_PREDICTIVE_RULE" if d["G"] <= 0 else "INCONCLUSIVE"),
            directionally_adverse=d["adverse"])
    expected = dict(experiment="GDT1031", status="EXECUTED" if observed else "NO_CAPACITY",
                    readers=reader_results,
                    overall_retained_lead=all(reader_results[r]["supports"] for r in ["ZL3b", "IT2a"]),
                    null_worlds=spec["null_worlds"] if observed else 0, confirmed_words=0,
                    source_identified=False, project_wide_significance=False,
                    independent_confirmation=False)
    assert_tree(read_json(EXP/"artifacts/RESULT.json"), expected, "result")
    return ["capacity_census_all_readers", "all_scored_block_exact_likelihoods",
            "readerwise_support_failure_adverse_gates", "overall_requires_both_readers",
            "no_score_without_capacity", "explicit_claim_ceilings"]


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    spec = read_json(EXP/"src/SPEC.json")
    try:
        report = self_test(spec) if args.self_test else validate(spec)
    except (ValidationFailure, AssertionError) as error:
        print(json.dumps(dict(status="FAIL", reason=str(error)), ensure_ascii=False))
        raise SystemExit(1)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
