#!/usr/bin/env python3
"""Replay original-edge folding certificates without importing the producer.

All word paths start at 0 and end at 1. Those vertices are NOT initially
identified. Only determinism or injectivity at a currently common origin
licenses a logged merge. Relations are never imposed at every state.
"""
import argparse
from collections import deque
import gzip
import hashlib
import json
from pathlib import Path
import re


BASE = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "bd8b58523e4e49754f4e49e3901f00ecef748679d90ac46184e453294c8753c2"


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Classes:
    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def merge(self, x, y):
        x, y = self.find(x), self.find(y)
        require(x != y, "REDUNDANT_LOGGED_MERGE")
        if self.size[x] < self.size[y]:
            x, y = y, x
        self.parent[y] = x
        self.size[x] += self.size[y]


def initial_paths(words, alphabet):
    require(alphabet == sorted(set(alphabet)), "UNSORTED_OR_REPEATED_ALPHABET")
    require(all(isinstance(c, str) and len(c) == 1 for c in alphabet), "ALPHABET_ITEM")
    labels = {c: i + 1 for i, c in enumerate(alphabet)}
    edges, next_vertex = [], 2
    for word in words:
        require(isinstance(word, str) and bool(word), "EMPTY_OR_NONSTRING_WORD")
        previous = 0
        for j, char in enumerate(word):
            require(char in labels, "UNDECLARED_CHARACTER")
            if j == len(word) - 1:
                target = 1
            else:
                target = next_vertex
                next_vertex += 1
            edges.append((previous, labels[char], target))
            previous = target
    require(bool(words), "EMPTY_WORD_COLLECTION")
    return next_vertex, edges


def orient(edge, direction):
    u, label, v = edge
    return (u, label, v) if direction == 1 else (v, -label, u)


def canonical(vertices, positive_edges, base, terminal=None):
    adjacency = {v: [] for v in vertices}
    for u, label, v in positive_edges:
        require(u in adjacency and v in adjacency and label > 0, "GRAPH_EDGE_SCHEMA")
        adjacency[u].append((label, v))
        adjacency[v].append((-label, u))
    numbering, queue = {base: 0}, deque([base])
    while queue:
        u = queue.popleft()
        for label, v in sorted(adjacency[u]):
            if v not in numbering:
                numbering[v] = len(numbering)
                queue.append(v)
    require(len(numbering) == len(vertices), "DISCONNECTED_QUOTIENT")
    out = {"vertices": len(vertices), "edges": sorted([numbering[u], label, numbering[v]] for u, label, v in positive_edges)}
    if terminal is None:
        out["base"] = 0
    else:
        out["start"] = 0
        out["terminal"] = numbering[terminal]
    return out


def pointed_core(graph):
    # Count incidences, not distinct neighbours: loops have degree two and
    # parallel edges with different labels must not be mistaken for leaves.
    edges = [tuple(e) for e in graph["edges"]]
    incident = [set() for _ in range(graph["vertices"])]
    degree = [0] * graph["vertices"]
    for eid, (u, _, v) in enumerate(edges):
        incident[u].add(eid)
        incident[v].add(eid)
        degree[u] += 1
        degree[v] += 1
    alive_vertices = set(range(graph["vertices"]))
    alive_edges = set(range(len(edges)))
    pending = deque(v for v in alive_vertices if v != 0 and degree[v] <= 1)
    while pending:
        u = pending.popleft()
        if u not in alive_vertices or degree[u] > 1 or u == 0:
            continue
        alive_vertices.remove(u)
        for eid in incident[u]:
            if eid not in alive_edges:
                continue
            alive_edges.remove(eid)
            a, _, b = edges[eid]
            degree[a] -= 1
            degree[b] -= 1
            for v in (a, b):
                if v in alive_vertices and v != 0 and degree[v] <= 1:
                    pending.append(v)
    return canonical(alive_vertices, {edges[i] for i in alive_edges}, 0)


def replay_unions(words, alphabet, fold_log):
    nvertices, edges = initial_paths(words, alphabet)
    classes = Classes(nvertices)
    require(isinstance(fold_log, list), "FOLD_LOG_NOT_LIST")
    for step, entry in enumerate(fold_log):
        require(isinstance(entry, list) and len(entry) == 3, "LOG_ENTRY_SCHEMA")
        first, second, direction = entry
        require(all(type(x) is int for x in entry), "LOG_ENTRY_NONINTEGER")
        require(0 <= first < len(edges) and 0 <= second < len(edges), "LOG_EDGE_OUT_OF_RANGE")
        require(direction in (-1, 1), "LOG_DIRECTION")
        u, label, v = orient(edges[first], direction)
        a, other_label, b = orient(edges[second], direction)
        require(label == other_label, "DIFFERENT_LABELS_AT_STEP_" + str(step))
        require(classes.find(u) == classes.find(a), "UNJUSTIFIED_ORIGIN_AT_STEP_" + str(step))
        require(classes.find(v) != classes.find(b), "NONACTUAL_UNION_AT_STEP_" + str(step))
        classes.merge(v, b)

    transitions, quotient_edges = {}, set()
    for u, label, v in edges:
        u, v = classes.find(u), classes.find(v)
        quotient_edges.add((u, label, v))
        for a, signed_label, b in ((u, label, v), (v, -label, u)):
            key = (a, signed_label)
            require(key not in transitions or transitions[key] == b, "INCOMPLETE_DETERMINISTIC_OR_INJECTIVE_FOLD")
            transitions[key] = b
    vertices = {classes.find(v) for v in range(nvertices)}
    require(len(vertices) == nvertices - len(fold_log), "UNION_CLASS_COUNT")
    graph = canonical(vertices, quotient_edges, classes.find(0), classes.find(1))
    core = pointed_core(graph)
    full = core["vertices"] == 1 and core["edges"] == [[0, label, 0] for label in range(1, len(alphabet) + 1)]
    return {"initial_vertices": nvertices, "initial_edges": len(edges), "union_count": len(fold_log), "graph": graph, "core": core, "full_group": full}


def replay_completion(words, alphabet, graph, completion):
    require(isinstance(completion, dict), "MISSING_COMPLETION")
    n = completion["states"]
    require(type(n) is int and n >= graph["vertices"], "COMPLETION_STATE_COUNT")
    require(completion["start"] == 0 and completion["terminal"] == graph["terminal"], "COMPLETION_ENDPOINT_BINDING")
    require(set(completion["permutations"]) == set(alphabet), "COMPLETION_ALPHABET")
    permutations = completion["permutations"]
    for char in alphabet:
        p = permutations[char]
        require(isinstance(p, list) and all(type(x) is int for x in p), "PERMUTATION_SCHEMA")
        require(sorted(p) == list(range(n)), "NOT_A_PERMUTATION_" + char)
    for u, label, v in graph["edges"]:
        require(permutations[alphabet[label - 1]][u] == v, "COMPLETION_DROPPED_QUOTIENT_EDGE")
    for word in words:
        q = 0
        for char in word:
            q = permutations[char][q]
        require(q == completion["terminal"], "ORIGINAL_LINE_ENDPOINT_MISMATCH")
    reached, queue = {0}, deque([0])
    while queue:
        u = queue.popleft()
        for char in alphabet:
            v = permutations[char][u]
            if v not in reached:
                reached.add(v)
                queue.append(v)
    require(len(reached) > 1, "TRIVIAL_START_ORBIT")
    return {"states": n, "reachable_states": len(reached), "all_original_endpoints_equal": True, "all_letter_actions_bijective": True}


def check_result(words, alphabet, fold_log, result):
    expected = replay_unions(words, alphabet, fold_log)
    require(result["alphabet"] == alphabet, "RESULT_ALPHABET")
    for name, value in expected.items():
        require(result[name] == value, "RESULT_DISAGREEMENT_" + name.upper())
    if expected["full_group"]:
        require(result["completion"] is None, "UNEXPECTED_FULL_GROUP_COMPLETION")
        witness = None
    else:
        witness = replay_completion(words, alphabet, expected["graph"], result["completion"])
    return expected, witness


def validate_files(source_path, log_path, result_path, producer_code=None):
    # The exact previously admitted source binding is checked before parsing.
    source_raw = source_path.read_bytes()
    require(sha(source_raw) == SOURCE_SHA256, "UNADMITTED_SOURCE_BYTES")
    records = json.loads(source_raw)
    require(isinstance(records, list) and len(records) == 413, "SOURCE_LINE_COUNT")
    require(len({r["locus"] for r in records}) == 413, "SOURCE_LOCUS_DUPLICATION")
    pages = {r["page"] for r in records}
    require(len(pages) == 43, "SOURCE_PAGE_COUNT")
    for page in pages:
        match = re.fullmatch(r"f(\d+)[rv]\d*", page)
        require(match is not None and int(match.group(1)) % 2 == 1 and not page.startswith("f84"), "SOURCE_OUTSIDE_ODD_SCOPE")
    words = [r["literal"] for r in records]
    require(all(re.fullmatch(r"[a-z]+", w) for w in words), "SOURCE_LITERAL_FORMAT")
    alphabet = sorted(set("".join(words)))
    require(len(alphabet) == 20, "SOURCE_ALPHABET_COUNT")
    result_raw, log_raw = result_path.read_bytes(), log_path.read_bytes()
    result = json.loads(result_raw)
    require(result["source_sha256"] == SOURCE_SHA256, "RESULT_SOURCE_BINDING")
    require(result["fold_log_sha256"] == sha(log_raw), "RESULT_LOG_BINDING")
    require(isinstance(result["code_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", result["code_sha256"]), "RESULT_CODE_HASH_FORMAT")
    if producer_code is not None:
        require(sha(producer_code.read_bytes()) == result["code_sha256"], "PRODUCER_CODE_BINDING")
    fold_log = json.loads(gzip.decompress(log_raw))
    expected, witness = check_result(words, alphabet, fold_log, result)
    return {
        "schema": "GDT903_INDEPENDENT_FORCED_UNION_VALIDATION_V1",
        "status": "PASS",
        "source_sha256": SOURCE_SHA256,
        "result_sha256": sha(result_raw),
        "fold_log_sha256": sha(log_raw),
        "declared_producer_code_sha256": result["code_sha256"],
        "producer_code_bytes_rechecked": producer_code is not None,
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "source_counts": {"lines": 413, "pages": 43, "alphabet": 20},
        "certificate_counts": {k: expected[k] for k in ("initial_vertices", "initial_edges", "union_count")},
        "folded_vertices": expected["graph"]["vertices"],
        "core_vertices": expected["core"]["vertices"],
        "full_group": expected["full_group"],
        "all_merges_individually_forced": True,
        "outgoing_and_incoming_folds_complete": True,
        "every_original_edge_preserved": True,
        "canonical_graph_and_pointed_core_exact": True,
        "completion_replay": witness,
        "claim": "NO_NONTRIVIAL_REVERSIBLE_COMMON_ENDPOINT_ACTION" if expected["full_group"] else "EXPLICIT_NONTRIVIAL_FINITE_COMMON_ENDPOINT_ACTION",
        "claim_ceiling": "Exact fixed literal source scope, arbitrary shared endpoint, local point stabilizer. No language, historical writing rule or meaning identified. Unreachable external states are unconstrained."
    }


def selftest():
    # A deliberately slow all-edge-pairs certificate producer is used only
    # on invented cases; it shares no input or code with the real producer.
    def fixture(words, alphabet):
        n, edges = initial_paths(words, alphabet)
        component = [{v} for v in range(n)]
        def block(v):
            return next(s for s in component if v in s)
        log = []
        while True:
            collision = None
            for d in (1, -1):
                for i, first in enumerate(edges):
                    u, x, v = orient(first, d)
                    for j in range(i + 1, len(edges)):
                        a, y, b = orient(edges[j], d)
                        if x == y and block(u) is block(a) and block(v) is not block(b):
                            collision = (i, j, d, v, b)
                            break
                    if collision:
                        break
                if collision:
                    break
            if collision is None:
                break
            i, j, d, v, b = collision
            left, right = block(v), block(b)
            component.remove(right)
            left.update(right)
            log.append([i, j, d])
        folded = replay_unions(words, alphabet, log)
        result = dict(folded, alphabet=alphabet, completion=None)
        if not folded["full_group"]:
            graph = folded["graph"]
            count = graph["vertices"]
            extra = count == 1
            count += int(extra)
            partial = {c: {} for c in alphabet}
            for u, label, v in graph["edges"]:
                partial[alphabet[label - 1]][u] = v
            if extra:
                missing = next(c for c in alphabet if 0 not in partial[c])
                partial[missing][0] = 1
            perms = {}
            for c in alphabet:
                mapping = partial[c]
                origins = sorted(set(range(count)) - set(mapping))
                targets = sorted(set(range(count)) - set(mapping.values()))
                mapping.update(zip(origins, targets))
                perms[c] = [mapping[i] for i in range(count)]
            result["completion"] = {"states": count, "start": 0, "terminal": graph["terminal"], "permutations": perms, "construction": "invented fixture"}
        check_result(words, alphabet, log, result)
        return log, result

    cases = [
        (["a"], ["a"], False),
        (["a", "b"], ["a", "b"], False),
        (["a", "aa"], ["a"], True),
        (["a", "aa"], ["a", "b"], False),
        (["ab", "aab"], ["a", "b"], False),
        (["ab", "abb", "aab"], ["a", "b"], True),
        (["ab", "ba"], ["a", "b"], False),
    ]
    for words, alphabet, full in cases:
        _, result = fixture(words, alphabet)
        require(result["full_group"] == full, "SELFTEST_CLASSIFICATION")
    def rejects(call):
        try:
            call()
        except ValueError:
            return
        raise AssertionError("malformed certificate accepted")
    log, result = fixture(["a", "aa"], ["a"])
    rejects(lambda: check_result(["a", "aa"], ["a"], log[:-1], result))
    rejects(lambda: check_result(["a", "aa"], ["a"], log + [log[0]], result))
    bad = [row[:] for row in log]
    bad[-1][2] *= -1
    rejects(lambda: check_result(["a", "aa"], ["a"], bad, result))
    rejects(lambda: replay_unions(["a", "b"], ["a", "b"], [[0, 1, 1]]))
    log, result = fixture(["ab", "ba"], ["a", "b"])
    modified = json.loads(json.dumps(result))
    modified["graph"]["edges"].pop()
    rejects(lambda: check_result(["ab", "ba"], ["a", "b"], log, modified))
    modified = json.loads(json.dumps(result))
    modified["completion"]["permutations"]["a"] = [0] * modified["completion"]["states"]
    rejects(lambda: check_result(["ab", "ba"], ["a", "b"], log, modified))
    modified = json.loads(json.dumps(result))
    modified["core"]["vertices"] += 1
    rejects(lambda: check_result(["ab", "ba"], ["a", "b"], log, modified))
    log, result = fixture(["a", "aa"], ["a", "b"])
    modified = json.loads(json.dumps(result))
    modified["completion"]["permutations"] = {"a": [0, 1], "b": [0, 1]}
    rejects(lambda: check_result(["a", "aa"], ["a", "b"], log, modified))
    return {"status": "PASS", "invented_complete_cases": len(cases), "malformed_certificates_rejected": 8, "actual_source_read": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--source-lines", type=Path, default=BASE / "artifacts/SOURCE_LINES.json")
    ap.add_argument("--fold-log", type=Path, default=BASE / "artifacts/FOLD_LOG.json.gz")
    ap.add_argument("--result", type=Path, default=BASE / "artifacts/FOLD_RESULT.json")
    ap.add_argument("--producer-code", type=Path, default=BASE / "src/fold.py")
    ap.add_argument("--output", type=Path, default=BASE / "artifacts/CERTIFICATE_VALIDATION.json")
    args = ap.parse_args()
    if args.selftest:
        print(json.dumps(selftest()))
        return
    result = validate_files(args.source_lines, args.fold_log, args.result, args.producer_code)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "full_group", "folded_vertices", "core_vertices", "claim")}))


if __name__ == "__main__":
    main()
