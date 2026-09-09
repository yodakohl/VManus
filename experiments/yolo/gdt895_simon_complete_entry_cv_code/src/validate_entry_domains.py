#!/usr/bin/env python3
"""Independent full-entry domain replay by direct two-way word dictionaries.

The primary checker is never imported. No target file is read in --self-test.
Actual replay requires a frozen independently audited source pool and the exact
previously admitted odd-only packet before its compressed contents are parsed.
"""
from __future__ import annotations

import argparse
import collections
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re

PACKET_SHA256 = "1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed"
CAPTURE_SHA256 = "033800bc117abe9031364800c703d4b061299d47a642b53398bd478429f9d322"
SOURCE_VALIDATOR_SHA256 = "d13a09a6cae513f526d137d3f50a1d8bddfe049ec56b731869e566cae7e6ace2"
PANEL_COUNTS = {"ZL3b": 14, "IT2a": 259, "RF1b": 11, "CONSENSUS": 1}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def word_bijection(source, target):
    """True iff this entire ordered pair of word sequences has a bijection."""
    if len(source) != len(target):
        return False
    forward, reverse = {}, {}
    for left, right in zip(source, target):
        if left in forward and forward[left] != right:
            return False
        if right in reverse and reverse[right] != left:
            return False
        forward[left] = right
        reverse[right] = left
    return True


def certificate_partition(words):
    """Certificate formatting only; never used to decide domain membership.

    Build each word's earliest equal position by pairwise comparisons, then rank
    those positions. This independently checks the primary's partition fields.
    """
    earliest = [next(j for j in range(i + 1) if words[j] == words[i])
                for i in range(len(words))]
    origins = sorted(set(earliest))
    return [origins.index(j) for j in earliest]


def normalized_words(words):
    return isinstance(words, list) and bool(words) and all(
        isinstance(w, str) and re.fullmatch(r"[a-z]+", w) for w in words)


def reconstruct(pool, packet):
    """Reconstruct all source profiles and every mandatory paragraph domain."""
    if packet.get("schema") != "GDT893_ODD_ONLY_FIT_PACKET_V1":
        raise ValueError("INVALID_TARGET_PACKET_SCHEMA")
    if set(packet.get("panels", {})) != set(PANEL_COUNTS):
        raise ValueError("INVALID_TARGET_PANELS")
    entries = pool["entries"]
    sources, by_length, source_ids = [], collections.defaultdict(list), set()
    for e in entries:
        if e.get("status") != "ACCEPTED" or not normalized_words(e.get("words")):
            raise ValueError("INVALID_SOURCE_ENTRY")
        if e["id"] in source_ids:
            raise ValueError("DUPLICATE_SOURCE_ID")
        source_ids.add(e["id"])
        words = e["words"]
        by_length[len(words)].append(e)
        sources.append({"id": e["id"], "word_count": len(words),
                        "equality_partition": certificate_partition(words),
                        "word_sequence_sha256": digest(json.dumps(words, ensure_ascii=False,
                            separators=(",", ":")).encode("utf-8")),
                        "html_sha256": e["html_sha256"]})
    panels = {}
    for edition, targets in packet["panels"].items():
        if len(targets) != PANEL_COUNTS[edition] or len({t["id"] for t in targets}) != len(targets):
            raise ValueError("MANDATORY_PARAGRAPH_SCOPE_CHANGED")
        records = []
        for t in targets:
            folio = t["physical_folio"]
            if (not isinstance(folio, str) or not re.fullmatch(r"f[0-9]+", folio)
                    or int(folio[1:]) % 2 != 1 or t["page"].startswith(("f84", "f116"))):
                raise ValueError("FORBIDDEN_TARGET_FOLIO")
            words = t["words"]
            if not normalized_words(words) or len(words) != len(t["source_group_ids"]):
                raise ValueError("INCOMPLETE_OR_NONLITERAL_TARGET_PARAGRAPH")
            candidates = []
            for source in by_length[len(words)]:
                if word_bijection(source["words"], words):
                    candidates.append(source["id"])
            records.append({"paragraph": t["id"], "page": t["page"],
                            "word_count": len(words),
                            "equality_partition": certificate_partition(words),
                            "same_length_source_entries": len(by_length[len(words)]),
                            "candidate_source_ids": candidates})
        empty = [r["paragraph"] for r in records if not r["candidate_source_ids"]]
        panels[edition] = {"status": "UNSAT_EMPTY_COMPLETE_ENTRY_DOMAIN" if empty else "NECESSARY_CONDITION_ONLY",
                           "paragraphs": len(records),
                           "target_words": sum(r["word_count"] for r in records),
                           "empty_domains": len(empty), "empty_domain_paragraphs": empty,
                           "length_only_empty_domains": sum(r["same_length_source_entries"] == 0 for r in records),
                           "candidate_pairs": sum(len(r["candidate_source_ids"]) for r in records),
                           "records": records}
    return {"schema": "GDT895_COMPLETE_ENTRY_DOMAINS_V1",
            "status": "ALL_PANELS_UNSAT" if all(p["empty_domains"] for p in panels.values()) else "SOME_PANELS_NOT_EXCLUDED",
            "source_entry_count": len(sources), "source_profiles": sources, "panels": panels,
            "key_search_performed": False, "held_access": False,
            "claim_ceiling": "Necessary-condition rejection of total complete-entry copying on this frozen partial edited pool only."}


def differing_paths(expected, actual, path="$"):
    """Return all mismatching fields; only compact paths, no source prose."""
    if type(expected) is not type(actual):
        return [path + ":TYPE"]
    if isinstance(expected, dict):
        differences = []
        for k in sorted(set(expected) | set(actual)):
            if k not in expected or k not in actual:
                differences.append(path + "." + str(k) + ":KEY")
            else:
                differences.extend(differing_paths(expected[k], actual[k], path + "." + str(k)))
        return differences
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return [path + ":LENGTH"]
        return [p for i, (a, b) in enumerate(zip(expected, actual))
                for p in differing_paths(a, b, path + "[" + str(i) + "]")]
    return [] if expected == actual else [path + ":VALUE"]


def source_gate(pool_raw, lock_raw, audit_raw):
    pool, lock, audit = map(json.loads, (pool_raw, lock_raw, audit_raw))
    if (lock.get("status") != "FROZEN" or lock.get("source_pool_sha256") != digest(pool_raw)
            or lock.get("source_audit_sha256") != digest(audit_raw)
            or audit.get("status") != "PASS" or audit.get("source_pool_sha256") != digest(pool_raw)
            or audit.get("capture_sha256") != CAPTURE_SHA256
            or pool.get("capture_sha256") != CAPTURE_SHA256 or pool.get("pending") != []
            or audit.get("validator_sha256") != SOURCE_VALIDATOR_SHA256):
        raise ValueError("SOURCE_NOT_FROZEN_AND_INDEPENDENTLY_BOUND")
    return pool


def validate_files(source_pool, source_lock, source_audit, target_packet, result_file):
    source_raw, lock_raw, audit_raw = [p.read_bytes() for p in (source_pool, source_lock, source_audit)]
    pool = source_gate(source_raw, lock_raw, audit_raw)
    # This ordering is intentional: no target read precedes the source gate.
    packet_raw = target_packet.read_bytes()
    if digest(packet_raw) != PACKET_SHA256:
        raise ValueError("TARGET_PACKET_BYTE_HASH_MISMATCH_REFUSING_PARSE")
    packet = json.loads(gzip.decompress(packet_raw))
    expected = reconstruct(pool, packet)
    checker_hash = digest(Path(__file__).with_name("check_entry_domains.py").read_bytes())
    expected.update(source_pool_sha256=digest(source_raw), source_lock_sha256=digest(lock_raw),
                    source_audit_sha256=digest(audit_raw), target_packet_sha256=digest(packet_raw),
                    implementation_sha256=checker_hash)
    result_raw = result_file.read_bytes()
    actual = json.loads(result_raw)
    mismatches = differing_paths(expected, actual)
    return {"schema": "GDT895_INDEPENDENT_ENTRY_DOMAIN_VALIDATION_V1",
            "status": "FAIL" if mismatches else "PASS",
            "source_pool_sha256": digest(source_raw), "source_lock_sha256": digest(lock_raw),
            "source_audit_sha256": digest(audit_raw), "target_packet_sha256": digest(packet_raw),
            "result_sha256": digest(result_raw), "primary_implementation_sha256": checker_hash,
            "validator_sha256": digest(Path(__file__).read_bytes()),
            "source_entry_count": expected["source_entry_count"],
            "mandatory_paragraph_count": sum(p["paragraphs"] for p in expected["panels"].values()),
            "reconstructed_status": expected["status"],
            "panels": {e: {k: v for k, v in p.items() if k not in {"records", "empty_domain_paragraphs"}}
                       for e, p in expected["panels"].items()},
            "mismatches": mismatches,
            "method": "Every equal-length complete source/target pair checked through direct forward and reverse word dictionaries; no primary partition/check import.",
            "claim_ceiling": "Exact complete-domain necessity only; no component-key solution, held reading or word meaning."}


def self_test():
    # Independent finite oracle: enumerate all alphabet bijections, not partitions.
    comparisons = 0
    for length in range(5):
        for source in itertools.product(("a", "b", "c"), repeat=length):
            possible = {tuple(dict(zip(("a", "b", "c"), values))[w] for w in source)
                        for values in itertools.permutations(("x", "y", "z"))}
            for target in itertools.product(("x", "y", "z"), repeat=length):
                assert word_bijection(source, target) == (target in possible), (source, target)
                comparisons += 1
    assert not word_bijection(["a"], ["x", "x"])
    assert not word_bijection(["a", "a"], ["x", "y"])
    assert not word_bijection(["a", "b"], ["x", "x"])
    assert word_bijection(["longword", "a", "longword"], ["x", "yyyy", "x"])
    assert certificate_partition(["q", "q", "a", "z", "a"]) == [0, 0, 1, 2, 1]
    entries = [{"id": ident, "status": "ACCEPTED", "html_sha256": "0" * 64, "words": words}
               for ident, words in [("s1", ["a", "b", "a"]), ("s2", ["c", "d", "c"]),
                                    ("s3", ["a", "b", "c"]), ("s4", ["a", "a", "a"]),
                                    ("s5", ["a", "b"])]]
    pool = {"entries": entries}
    packet = {"schema": "GDT893_ODD_ONLY_FIT_PACKET_V1", "panels": {}}
    patterns = [["x", "y", "x"], ["x", "x", "y"], ["x", "y", "z"],
                ["x", "x", "x"], ["x", "y"], ["x", "y", "z", "x"]]
    expected_candidates = [["s1", "s2"], [], ["s3"], ["s4"], ["s5"], []]
    for edition, count in PANEL_COUNTS.items():
        packet["panels"][edition] = [{"id": edition + str(i), "page": "f1r", "physical_folio": "f1",
            "words": patterns[i % len(patterns)], "source_group_ids": list(range(len(patterns[i % len(patterns)])))}
            for i in range(count)]
    got = reconstruct(pool, packet)
    for edition, records in packet["panels"].items():
        found = got["panels"][edition]["records"]
        assert len(found) == len(records)
        assert [r["candidate_source_ids"] for r in found] == [expected_candidates[i % len(patterns)] for i in range(len(records))]
    assert got["status"] == "SOME_PANELS_NOT_EXCLUDED"  # One mandatory consensus paragraph has a nonempty domain.
    no_sources = reconstruct({"entries": []}, packet)
    assert no_sources["status"] == "ALL_PANELS_UNSAT"
    assert all(p["length_only_empty_domains"] == p["paragraphs"] for p in no_sources["panels"].values())
    bad = copy.deepcopy(got); bad["panels"]["ZL3b"]["records"][0]["candidate_source_ids"].pop()
    assert differing_paths(got, bad) == ["$.panels.ZL3b.records[0].candidate_source_ids:LENGTH"]
    bad = copy.deepcopy(got); bad["panels"]["IT2a"]["records"].pop()
    assert differing_paths(got, bad) == ["$.panels.IT2a.records:LENGTH"]
    rejected = 0
    for mutation in ("scope", "even", "forbidden", "groups", "alphabet", "duplicate_source", "empty_source"):
        p, t = copy.deepcopy(pool), copy.deepcopy(packet)
        if mutation == "scope": t["panels"]["ZL3b"].pop()
        elif mutation == "even": t["panels"]["ZL3b"][0]["physical_folio"] = "f2"
        elif mutation == "forbidden": t["panels"]["ZL3b"][0]["page"] = "f84r"
        elif mutation == "groups": t["panels"]["ZL3b"][0]["source_group_ids"] = []
        elif mutation == "alphabet": t["panels"]["ZL3b"][0]["words"][0] = "x?"
        elif mutation == "duplicate_source": p["entries"].append(p["entries"][0])
        elif mutation == "empty_source": p["entries"][0]["words"] = []
        try:
            reconstruct(p, t)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("mutation accepted: " + mutation)
    class BytesInput:
        def __init__(self, raw): self.raw = raw
        def read_bytes(self): return self.raw
    class Unreadable:
        def read_bytes(self): raise AssertionError("forbidden input was read")
    pool_raw = json.dumps({"entries": [], "pending": [], "capture_sha256": CAPTURE_SHA256}).encode()
    audit_raw = json.dumps({"status": "PASS", "source_pool_sha256": digest(pool_raw),
                           "capture_sha256": CAPTURE_SHA256,
                           "validator_sha256": SOURCE_VALIDATOR_SHA256}).encode()
    lock = {"status": "FROZEN", "source_pool_sha256": digest(pool_raw), "source_audit_sha256": digest(audit_raw)}
    assert source_gate(pool_raw, json.dumps(lock).encode(), audit_raw)["entries"] == []
    try:
        validate_files(BytesInput(pool_raw), BytesInput(json.dumps({**lock, "status": "PENDING"}).encode()),
                       BytesInput(audit_raw), Unreadable(), Unreadable())
    except ValueError as exc:
        assert str(exc) == "SOURCE_NOT_FROZEN_AND_INDEPENDENTLY_BOUND"
    else:
        raise AssertionError("unfrozen source accepted")
    try:
        validate_files(BytesInput(pool_raw), BytesInput(json.dumps(lock).encode()),
                       BytesInput(audit_raw), BytesInput(b"not the admitted packet"), Unreadable())
    except ValueError as exc:
        assert str(exc) == "TARGET_PACKET_BYTE_HASH_MISMATCH_REFUSING_PARSE"
    else:
        raise AssertionError("wrong packet accepted")
    return {"status": "PASS", "exhaustive_bijection_pairs": comparisons,
            "complete_synthetic_paragraphs": sum(PANEL_COUNTS.values()),
            "scope_mutations_rejected": rejected, "source_and_packet_read_order_gates": 2,
            "real_source_or_target_opened": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-pool", type=Path)
    p.add_argument("--source-lock", type=Path)
    p.add_argument("--source-audit", type=Path)
    p.add_argument("--target-packet", type=Path)
    p.add_argument("--result", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True)); return 0
    required = (args.source_pool, args.source_lock, args.source_audit, args.target_packet, args.result, args.output)
    if any(x is None for x in required):
        p.error("all six source/target/result/output paths are required outside --self-test")
    result = validate_files(*required[:5])
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "mismatches"}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
