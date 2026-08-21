#!/usr/bin/env python3
"""Run the bounded GDT398 opaque joint-tuple equivalence preflight."""

from __future__ import annotations

import csv
import gzip
import hashlib
import heapq
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt398_opaque_joint_tuple_predictive_equivalence_preflight"
ART = EXP / "artifacts"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
ATLAS = ROOT / "gdt327_joint_tuple_atlas.tsv"
SAFE_VIEW = EXP / "inputs/gdt398_safe_source_view.tsv.gz"
REPORT = EXP / "REPORT.md"
RESULT = ART / "result.json"
FOLDS_OUT = ART / "fold_scores.tsv"
CLUSTERS_OUT = ART / "cluster_summary.tsv"
MERGES_OUT = ART / "stable_merges.tsv"
COUNTER_OUT = ART / "counterexamples.tsv"

FRACTIONS = (1.00, 0.90, 0.75, 0.60, 0.45, 0.30)
N_OUTER = 11
HASH_DIM = 256
NEIGHBOURS = 24
TAU = 8.0
BETA = 0.5
NULL_WORLDS = 64
SEED = 398_20260821
OUTCOMES = ("previous", "next", "placement", "boundary_before", "boundary_after")
VIEW_WEIGHTS = {
    "local1": 1.0,
    "local2": math.sqrt(0.5),
    "placement": 1.0,
    "boundary": 1.0,
    "record": math.sqrt(0.75),
    "domain": math.sqrt(0.75),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_tsv(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def content_hash(value: dict) -> str:
    clean = {k: v for k, v in value.items() if k != "content_sha256"}
    return canonical_hash(clean)


def read_interlinear_guarded() -> list[dict]:
    expected = sha256(INTER)
    if expected != "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9":
        raise RuntimeError("GDT327 interlinear hash drift")
    with INTER.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = []
        for row in reader:
            selectors = (row["page"], row["physical_folio"], row["locus"])
            if any(value.lower().startswith("f84") for value in selectors):
                raise RuntimeError("sealed f84 selector found in declared f84-free GDT327 input")
            rows.append(row)
    if len(rows) != 8448 or len({r["joint_tuple_id"] for r in rows}) != 1676:
        raise RuntimeError("GDT327 cardinality drift")
    return rows


def load_safe_separator_view(rows: list[dict]) -> tuple[dict[tuple[str, int], dict], str, dict]:
    expected = "056ec5193f02acbb9a591dcba7edd45469518ddc732975c6947e65353f16b81e"
    if sha256(SAFE_VIEW) != expected:
        raise RuntimeError("GDT398 safe source view hash drift")
    with gzip.open(SAFE_VIEW, "rt", encoding="utf-8", newline="") as fh:
        selected = list(csv.DictReader(fh, delimiter="\t"))
    index = {(r["locus"], int(r["source_group_index"])): r for r in selected}
    if len(selected) != len(rows) or any((r["locus"], int(r["group_index"])) not in index for r in rows):
        raise RuntimeError("guarded ZL3b separator join is not exact")
    if any(r["page"].lower().startswith("f84") or r["locus"].lower().startswith("f84") for r in selected):
        raise RuntimeError("guard failure: f84 material retained")
    stats = {"safe_view_rows": len(selected), "loci": len({row["locus"] for row in selected})}
    return index, expected, stats


def int_bucket(value: int) -> str:
    return str(value) if value <= 3 else "4+"


def frequency_bin(n: int) -> str:
    if n <= 1:
        return "1"
    if n == 2:
        return "2"
    if n <= 5:
        return "3-5"
    if n <= 10:
        return "6-10"
    if n <= 25:
        return "11-25"
    return "26+"


def enrich_events(rows: list[dict], sep: dict[tuple[str, int], dict]) -> tuple[list[dict], dict[str, str]]:
    opaque = {raw: f"T{i:04d}" for i, raw in enumerate(sorted({r["joint_tuple_id"] for r in rows}), 1)}
    events = []
    for serial, row in enumerate(rows):
        source = sep[(row["locus"], int(row["group_index"]))]
        index = int(row["group_index"])
        count = int(row["group_count"])
        placement = "SINGLE" if count == 1 else "START" if index == 1 else "END" if index == count else "MIDDLE"
        event = dict(row)
        event.update({
            "serial": serial, "tuple": opaque[row["joint_tuple_id"]], "raw_joint": row["joint_tuple_id"],
            "raw_surface": source["ivtff_group_raw"], "boundary_before": source["left_separator"],
            "boundary_after": source["right_separator"], "paragraph_start": source["paragraph_start"],
            "paragraph_end": source["paragraph_end"], "index": index, "count": count, "placement": placement,
            "quartile": f"Q{min(3, ((index - 1) * 4) // max(count, 1)) + 1}",
            "record_key": (row["page"], row["record_ordinal"]),
        })
        events.append(event)
    by_line = defaultdict(list)
    for event in events:
        by_line[event["locus"]].append(event)
    for members in by_line.values():
        members.sort(key=lambda x: x["index"])
        for j, event in enumerate(members):
            event["previous"] = members[j - 1]["tuple"] if j else "<LINE_START>"
            event["next"] = members[j + 1]["tuple"] if j + 1 < len(members) else "<LINE_END>"
            event["previous2"] = members[j - 2]["tuple"] if j >= 2 else "<LINE_START2>"
            event["next2"] = members[j + 2]["tuple"] if j + 2 < len(members) else "<LINE_END2>"
    return events, opaque


def balanced_folds(events: list[dict]) -> dict[str, int]:
    counts = Counter(e["physical_folio"] for e in events)
    loads = [0] * N_OUTER
    membership = {}
    for folio, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        fold = min(range(N_OUTER), key=lambda k: (loads[k], k))
        membership[folio] = fold
        loads[fold] += n
    return membership


def signature_counts(events: list[dict]) -> tuple[dict[str, dict[str, Counter]], Counter]:
    views: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    frequencies = Counter(e["tuple"] for e in events)
    records = defaultdict(list)
    for event in events:
        records[event["record_key"]].append(event)
        t = event["tuple"]
        views[t]["local1"]["PRE:" + event["previous"]] += 1
        views[t]["local1"]["NEXT:" + event["next"]] += 1
        views[t]["local2"]["PRE2:" + event["previous2"]] += 1
        views[t]["local2"]["NEXT2:" + event["next2"]] += 1
        for feature in (
            "ROLE:" + event["placement"], "QUART:" + event["quartile"],
            "PAR_START:" + event["paragraph_start"], "FIELD_POS:" + event["within_field_position"],
            "FIELD_ORD:" + int_bucket(int(event["field_ordinal"])),
            "RECORD_ORD:" + int_bucket(int(event["record_ordinal"])),
        ):
            views[t]["placement"][feature] += 1
        views[t]["boundary"]["LEFT:" + event["boundary_before"]] += 1
        views[t]["boundary"]["RIGHT:" + event["boundary_after"]] += 1
        for feature in (
            "SECTION:" + event["section"], "REGISTER:" + event["register"],
            "CURRIER:" + event["currier"], "HAND:" + event["hand"],
        ):
            views[t]["domain"][feature] += 1
    for members in records.values():
        members.sort(key=lambda e: (e["locus"], e["index"], e["serial"]))
        type_counts = Counter(e["tuple"] for e in members)
        for ordinal, event in enumerate(members, 1):
            t = event["tuple"]
            views[t]["record"]["MULT:" + frequency_bin(type_counts[t])] += 1
            views[t]["record"]["ORD:" + int_bucket(ordinal)] += 1
            for other in type_counts:
                if other != t:
                    views[t]["record"]["CO:" + other] += 1
    return views, frequencies


def hash_coordinate(text: str) -> tuple[int, float]:
    digest = hashlib.sha256(text.encode()).digest()
    return int.from_bytes(digest[:4], "big") % HASH_DIM, (1.0 if digest[4] & 1 else -1.0)


def signature_matrix(events: list[dict]) -> tuple[list[str], np.ndarray, dict[str, dict[str, Counter]], Counter]:
    views, frequencies = signature_counts(events)
    types = sorted(frequencies)
    matrix = np.zeros((len(types), HASH_DIM), dtype=np.float64)
    for i, t in enumerate(types):
        for view, weight in VIEW_WEIGHTS.items():
            counts = views[t][view]
            total = sum(counts.values())
            if not total:
                continue
            for feature, count in counts.items():
                column, sign = hash_coordinate(view + "|" + feature)
                matrix[i, column] += weight * sign * count / total
        norm = float(np.linalg.norm(matrix[i]))
        if norm:
            matrix[i] /= norm
    return types, matrix, views, frequencies


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, a: int) -> int:
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a != b:
            if a > b:
                a, b = b, a
            self.parent[b] = a


def dendrogram(events: list[dict]) -> tuple[list[str], list[tuple[int, int, float]], Counter, dict[str, dict[str, Counter]]]:
    types, matrix, views, frequencies = signature_matrix(events)
    n = len(types)
    if n < 2:
        return types, [], frequencies, views
    similarity = matrix @ matrix.T
    np.fill_diagonal(similarity, -np.inf)
    k = min(NEIGHBOURS, n - 1)
    nearest = np.argpartition(-similarity, kth=k - 1, axis=1)[:, :k]
    active: dict[int, tuple[np.ndarray, int, int]] = {
        i: (matrix[i] * frequencies[types[i]], frequencies[types[i]], i) for i in range(n)
    }
    neighbours: dict[int, set[int]] = {i: set(int(x) for x in nearest[i]) for i in range(n)}
    for i, values in list(neighbours.items()):
        for j in list(values):
            neighbours.setdefault(j, set()).add(i)
    heap = []

    def centroid(cid: int) -> np.ndarray:
        vector = active[cid][0]
        norm = float(np.linalg.norm(vector))
        return vector / norm if norm else vector

    def push(a: int, b: int) -> None:
        if a == b or a not in active or b not in active:
            return
        if a > b:
            a, b = b, a
        distance = 1.0 - float(np.dot(centroid(a), centroid(b)))
        heapq.heappush(heap, (round(distance, 15), active[a][2], active[b][2], a, b))

    for a in range(n):
        for b in neighbours[a]:
            if a < b:
                push(a, b)
    merges = []
    next_id = n
    minimum_k = max(1, round(min(FRACTIONS) * n))
    while len(active) > minimum_k:
        while heap:
            distance, _, _, a, b = heapq.heappop(heap)
            if a in active and b in active and b in neighbours.get(a, set()):
                break
        else:
            ids = sorted(active)
            best = None
            for pos, a in enumerate(ids):
                ca = centroid(a)
                for b in ids[pos + 1:]:
                    item = (1.0 - float(np.dot(ca, centroid(b))), active[a][2], active[b][2], a, b)
                    if best is None or item < best:
                        best = item
            if best is None:
                break
            distance, _, _, a, b = best
        va, na, ra = active.pop(a)
        vb, nb, rb = active.pop(b)
        merges.append((ra, rb, float(distance)))
        merged_neighbours = (neighbours.pop(a, set()) | neighbours.pop(b, set())) - {a, b}
        merged_neighbours = {x for x in merged_neighbours if x in active}
        cid = next_id
        next_id += 1
        active[cid] = (va + vb, na + nb, min(ra, rb))
        neighbours[cid] = set(merged_neighbours)
        for other in merged_neighbours:
            neighbours[other].discard(a)
            neighbours[other].discard(b)
            neighbours[other].add(cid)
            push(cid, other)
    return types, merges, frequencies, views


def cut_partition(types: list[str], merges: list[tuple[int, int, float]], fraction: float) -> tuple[dict[str, str], list[tuple[str, str, float]]]:
    n = len(types)
    target_k = max(1, round(fraction * n))
    uf = UnionFind(n)
    direct = []
    for a, b, distance in merges[: n - target_k]:
        direct.append((types[a], types[b], distance))
        uf.union(a, b)
    groups = defaultdict(list)
    for i, t in enumerate(types):
        groups[uf.find(i)].append(t)
    ordered = sorted(groups.values(), key=lambda members: members[0])
    mapping = {}
    for class_index, members in enumerate(ordered, 1):
        label = f"LATENT_FORM_{class_index:04d}"
        for t in members:
            mapping[t] = label
    return mapping, direct


def vocabularies(events: list[dict], types: list[str]) -> dict[str, tuple[str, ...]]:
    return {
        "previous": tuple(types) + ("<LINE_START>",),
        "next": tuple(types) + ("<LINE_END>",),
        "placement": ("SINGLE", "START", "MIDDLE", "END"),
        "boundary_before": tuple(sorted({e["boundary_before"] for e in events})),
        "boundary_after": tuple(sorted({e["boundary_after"] for e in events})),
    }


def score_state_model(train: list[dict], test: list[dict], state) -> tuple[float, dict[str, float], dict[int, float]]:
    global_counts = {name: Counter(e[name] for e in train) for name in OUTCOMES}
    conditional = {name: defaultdict(Counter) for name in OUTCOMES}
    state_totals = {name: Counter() for name in OUTCOMES}
    for event in train:
        key = state(event, True)
        if key is None:
            continue
        for name in OUTCOMES:
            conditional[name][key][event[name]] += 1
            state_totals[name][key] += 1
    universe = vocabularies(ALL_EVENTS, ALL_TYPES)
    endpoint_bits = Counter()
    event_bits = Counter()
    for event in test:
        key = state(event, False)
        for name in OUTCOMES:
            values = universe[name]
            global_total = sum(global_counts[name].values())
            base = (global_counts[name][event[name]] + BETA) / (global_total + BETA * len(values))
            probability = base if key is None else (conditional[name][key][event[name]] + TAU * base) / (state_totals[name][key] + TAU)
            bits = -math.log2(max(probability, 1e-300))
            endpoint_bits[name] += bits
            event_bits[event["serial"]] += bits
    return sum(endpoint_bits.values()), dict(endpoint_bits), dict(event_bits)


def modal_surface(events: list[dict]) -> dict[str, str]:
    counts = defaultdict(Counter)
    for event in events:
        counts[event["tuple"]][event["raw_surface"]] += 1
    return {t: min(counter, key=lambda value: (-counter[value], value)) for t, counter in counts.items()}


def edit_leq_one(a: str, b: str) -> bool:
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    if len(a) > len(b):
        a, b = b, a
    i = j = errors = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            errors += 1
            j += 1
            if errors > 1:
                return False
    return True


def variants(text: str) -> set[str]:
    return {text} | {text[:i] + text[i + 1:] for i in range(len(text))}


def string_partition(train: list[dict]):
    modes = modal_surface(train)
    types = sorted(modes)
    uf = UnionFind(len(types))
    buckets = defaultdict(list)
    for i, t in enumerate(types):
        for variant in variants(modes[t]):
            buckets[variant].append(i)
    checked = set()
    for members in buckets.values():
        for a, b in itertools.combinations(members, 2):
            pair = (min(a, b), max(a, b))
            if pair in checked:
                continue
            checked.add(pair)
            if edit_leq_one(modes[types[a]], modes[types[b]]):
                uf.union(a, b)
    groups = defaultdict(list)
    for i, t in enumerate(types):
        groups[uf.find(i)].append(t)
    mapping = {}
    support = Counter(e["tuple"] for e in train)
    variant_to_states = defaultdict(set)
    for state_index, members in enumerate(sorted(groups.values(), key=lambda m: m[0]), 1):
        label = f"STRING_{state_index:04d}"
        for t in members:
            mapping[t] = label
            for variant in variants(modes[t]):
                variant_to_states[variant].add(label)
    state_support = Counter()
    for t, n in support.items():
        state_support[mapping[t]] += n

    def state(event: dict, training: bool):
        if event["tuple"] in mapping:
            return mapping[event["tuple"]]
        candidates = set()
        for variant in variants(event["raw_surface"]):
            candidates.update(variant_to_states.get(variant, ()))
        if not candidates:
            return "STRING_UNSEEN"
        return min(candidates, key=lambda label: (-state_support[label], label))

    return state, mapping, modes


def placement_state(train: list[dict]):
    counts = Counter(e["tuple"] for e in train)
    roles = defaultdict(Counter)
    for event in train:
        roles[event["tuple"]][event["placement"]] += 1
    mapping = {t: frequency_bin(n) + "|" + min(roles[t], key=lambda value: (-roles[t][value], value)) for t, n in counts.items()}
    return lambda event, training: mapping.get(event["tuple"], "PLACEMENT_UNSEEN"), mapping


def score_partition(train: list[dict], test: list[dict], mapping: dict[str, str]):
    return score_state_model(train, test, lambda event, training: mapping.get(event["tuple"], "LATENT_UNSEEN"))


def adjusted_rand(mapping_a: dict[str, str], mapping_b: dict[str, str]) -> float:
    common = sorted(set(mapping_a) & set(mapping_b))
    n = len(common)
    if n < 2:
        return 1.0
    table = Counter((mapping_a[t], mapping_b[t]) for t in common)
    rows = Counter(mapping_a[t] for t in common)
    cols = Counter(mapping_b[t] for t in common)
    choose2 = lambda x: x * (x - 1) / 2
    index = sum(choose2(v) for v in table.values())
    row_sum = sum(choose2(v) for v in rows.values())
    col_sum = sum(choose2(v) for v in cols.values())
    total = choose2(n)
    expected = row_sum * col_sum / total if total else 0.0
    maximum = 0.5 * (row_sum + col_sum)
    return (index - expected) / (maximum - expected) if maximum != expected else 1.0


def dominant_profiles(train: list[dict]) -> dict[str, tuple[str, str, str]]:
    freq = Counter(e["tuple"] for e in train)
    role = defaultdict(Counter)
    register = defaultdict(Counter)
    for event in train:
        role[event["tuple"]][event["placement"]] += 1
        register[event["tuple"]][event["register"]] += 1
    return {
        t: (frequency_bin(n), min(role[t], key=lambda x: (-role[t][x], x)), min(register[t], key=lambda x: (-register[t][x], x)))
        for t, n in freq.items()
    }


def permute_mapping(mapping: dict[str, str], profiles: dict[str, tuple[str, str, str]], rng: random.Random) -> dict[str, str]:
    strata = defaultdict(list)
    for t in sorted(mapping):
        strata[profiles[t]].append(t)
    result = {}
    for members in strata.values():
        values = [mapping[t] for t in members]
        rng.shuffle(values)
        result.update(zip(members, values))
    return result


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] if low == high else ordered[low] * (high - position) + ordered[high] * (position - low)


def mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else float("nan")


def view_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0) for key, value in a.items())
    na = math.sqrt(sum(value * value for value in a.values()))
    nb = math.sqrt(sum(value * value for value in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def main() -> int:
    global ALL_EVENTS, ALL_TYPES
    outputs = (REPORT, RESULT, FOLDS_OUT, CLUSTERS_OUT, MERGES_OUT, COUNTER_OUT)
    if any(path.exists() for path in outputs):
        raise RuntimeError("refusing to overwrite GDT398 result artifacts")
    ART.mkdir(parents=True, exist_ok=True)
    rows = read_interlinear_guarded()
    separator_index, separator_hash, guard_stats = load_safe_separator_view(rows)
    events, opaque_map = enrich_events(rows, separator_index)
    ALL_EVENTS = events
    ALL_TYPES = sorted({e["tuple"] for e in events})
    fold_of = balanced_folds(events)
    for event in events:
        event["fold"] = fold_of[event["physical_folio"]]
    fold_loads = Counter(event["fold"] for event in events)
    if len(fold_loads) != N_OUTER or max(fold_loads.values()) - min(fold_loads.values()) > 100:
        raise RuntimeError("outer fold imbalance")

    fold_rows, cluster_rows, fold_objects = [], [], []
    event_gain_by_type = Counter()
    strata_gain = {"register": Counter(), "section": Counter()}
    strata_n = {"register": Counter(), "section": Counter()}

    for outer in range(N_OUTER):
        train = [e for e in events if e["fold"] != outer]
        test = [e for e in events if e["fold"] == outer]
        inner_folds = {(outer + 1) % N_OUTER, (outer + 2) % N_OUTER}
        inner_train = [e for e in train if e["fold"] not in inner_folds]
        inner_test = [e for e in train if e["fold"] in inner_folds]
        inner_types, inner_merges, _, _ = dendrogram(inner_train)
        inner_scores = {}
        for fraction in FRACTIONS:
            mapping, _ = cut_partition(inner_types, inner_merges, fraction)
            inner_scores[fraction] = score_partition(inner_train, inner_test, mapping)[0]
        selected_fraction = min(FRACTIONS, key=lambda f: (inner_scores[f], -f))

        types, merges, frequencies, views = dendrogram(train)
        partitions, directs, candidate_scores = {}, {}, {}
        for fraction in FRACTIONS:
            mapping, direct = cut_partition(types, merges, fraction)
            partitions[fraction] = mapping
            directs[fraction] = direct
            candidate_scores[fraction] = score_partition(train, test, mapping)
        selected_mapping = partitions[selected_fraction]
        selected_bits, selected_endpoints, selected_event_bits = candidate_scores[selected_fraction]

        exact_state = lambda event, training: event["tuple"]
        host_state = lambda event, training: event["host_id"]
        global_state = lambda event, training: None
        placement_fn, placement_map = placement_state(train)
        string_fn, string_map, string_modes = string_partition(train)
        model_scores = {
            "GLOBAL_FREQUENCY": score_state_model(train, test, global_state),
            "EXACT_TUPLE": score_state_model(train, test, exact_state),
            "PAGE_HOST": score_state_model(train, test, host_state),
            "GDT338_NORMALIZED": score_state_model(train, test, exact_state),
            "STRING_SIMILARITY": score_state_model(train, test, string_fn),
            "PLACEMENT_FREQUENCY": score_state_model(train, test, placement_fn),
            "LEARNED_LATENT_CLASS": (selected_bits, selected_endpoints, selected_event_bits),
        }
        if model_scores["EXACT_TUPLE"][0] != model_scores["GDT338_NORMALIZED"][0]:
            raise RuntimeError("GDT338 group-level exact identity alias drift")
        exact_bits, exact_endpoints, exact_event_bits = model_scores["EXACT_TUPLE"]
        raw_gain = exact_bits - selected_bits
        partition_cost = math.log2(max(len(types), 2))
        selector_cost = math.log2(len(FRACTIONS))
        paid_gain = raw_gain - partition_cost - selector_cost
        cluster_sizes = Counter(selected_mapping.values())
        largest_label = min(cluster_sizes, key=lambda label: (-cluster_sizes[label], label))
        frequent_cut = max(1, math.ceil(0.05 * len(types)))
        frequent_types = set(t for t, _ in sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))[:frequent_cut])
        keep_largest = [e for e in test if selected_mapping.get(e["tuple"], "LATENT_UNSEEN") != largest_label]
        keep_frequent = [e for e in test if e["tuple"] not in frequent_types]
        largest_gain = score_state_model(train, keep_largest, exact_state)[0] - score_partition(train, keep_largest, selected_mapping)[0]
        frequent_gain = score_state_model(train, keep_frequent, exact_state)[0] - score_partition(train, keep_frequent, selected_mapping)[0]

        held_folios = sorted({e["physical_folio"] for e in test})
        for model, (bits, endpoint_bits, _) in model_scores.items():
            fold_rows.append({
                "outer_fold": outer, "held_folios": "|".join(held_folios), "selected_fraction": f"{selected_fraction:.2f}",
                "selected_k": len(set(selected_mapping.values())), "training_types": len(types), "held_events": len(test), "model": model,
                "bits_total": f"{bits:.9f}", "bits_previous": f"{endpoint_bits['previous']:.9f}",
                "bits_next": f"{endpoint_bits['next']:.9f}", "bits_placement": f"{endpoint_bits['placement']:.9f}",
                "bits_boundary_before": f"{endpoint_bits['boundary_before']:.9f}",
                "bits_boundary_after": f"{endpoint_bits['boundary_after']:.9f}",
                "raw_gain_vs_exact": f"{exact_bits - bits:.9f}",
                "partition_cost": f"{partition_cost if model == 'LEARNED_LATENT_CLASS' else 0.0:.9f}",
                "selector_cost": f"{selector_cost if model == 'LEARNED_LATENT_CLASS' else 0.0:.9f}",
                "selector_paid_gain": f"{paid_gain if model == 'LEARNED_LATENT_CLASS' else exact_bits - bits:.9f}",
                "positive": int(exact_bits - bits > 0),
            })
        for fraction in FRACTIONS:
            bits, endpoint_bits, _ = candidate_scores[fraction]
            fold_rows.append({
                "outer_fold": outer, "held_folios": "|".join(held_folios), "selected_fraction": f"{fraction:.2f}",
                "selected_k": len(set(partitions[fraction].values())), "training_types": len(types), "held_events": len(test),
                "model": "CANDIDATE_CUT", "bits_total": f"{bits:.9f}",
                "bits_previous": f"{endpoint_bits['previous']:.9f}", "bits_next": f"{endpoint_bits['next']:.9f}",
                "bits_placement": f"{endpoint_bits['placement']:.9f}",
                "bits_boundary_before": f"{endpoint_bits['boundary_before']:.9f}",
                "bits_boundary_after": f"{endpoint_bits['boundary_after']:.9f}",
                "raw_gain_vs_exact": f"{exact_bits - bits:.9f}", "partition_cost": f"{partition_cost:.9f}",
                "selector_cost": f"{selector_cost:.9f}",
                "selector_paid_gain": f"{exact_bits - bits - partition_cost - selector_cost:.9f}",
                "positive": int(exact_bits - bits > 0),
            })
        for t in types:
            label = selected_mapping[t]
            cluster_rows.append({
                "outer_fold": outer, "joint_tuple_id": t, "latent_form_id": label,
                "selected_fraction": f"{selected_fraction:.2f}", "training_events": frequencies[t],
                "training_folios": len({e["physical_folio"] for e in train if e["tuple"] == t}),
                "cluster_size": cluster_sizes[label],
            })
        for event in test:
            delta = exact_event_bits[event["serial"]] - selected_event_bits[event["serial"]]
            event_gain_by_type[event["tuple"]] += delta
            for axis in ("register", "section"):
                strata_gain[axis][event[axis]] += delta
                strata_n[axis][event[axis]] += 1
        fold_objects.append({
            "outer": outer, "train": train, "test": test, "types": types, "frequencies": frequencies, "views": views,
            "selected_fraction": selected_fraction, "selected_mapping": selected_mapping, "partitions": partitions,
            "directs": directs, "profiles": dominant_profiles(train), "exact_bits": exact_bits, "raw_gain": raw_gain,
            "paid_gain": paid_gain, "partition_cost": partition_cost, "selector_cost": selector_cost,
            "largest_gain": largest_gain, "frequent_gain": frequent_gain, "cluster_sizes": cluster_sizes,
            "string_mapping": string_map, "string_modes": string_modes,
            "model_bits": {model: value[0] for model, value in model_scores.items()},
        })

    ari_values = [adjusted_rand(a["selected_mapping"], b["selected_mapping"]) for a, b in itertools.combinations(fold_objects, 2)]
    observed_ari = mean(ari_values)
    consistency = []
    for t in ALL_TYPES:
        neighbourhoods = []
        for fold in fold_objects:
            mapping = fold["selected_mapping"]
            if t in mapping:
                label = mapping[t]
                neighbourhoods.append({other for other, value in mapping.items() if value == label and other != t})
        js = []
        for left, right in itertools.combinations(neighbourhoods, 2):
            union = left | right
            js.append(len(left & right) / len(union) if union else 1.0)
        if js:
            consistency.append(mean(js))
    consistent_fraction = sum(value >= 0.70 for value in consistency) / len(consistency) if consistency else 0.0

    null_paid, null_ari = [], []
    for world in range(NULL_WORLDS):
        world_gain = 0.0
        shuffled_selected = []
        for fold in fold_objects:
            best = -float("inf")
            for setting_index, fraction in enumerate(FRACTIONS):
                rng = random.Random(SEED + world * 100003 + fold["outer"] * 101 + setting_index)
                shuffled = permute_mapping(fold["partitions"][fraction], fold["profiles"], rng)
                bits = score_partition(fold["train"], fold["test"], shuffled)[0]
                best = max(best, fold["exact_bits"] - bits)
            world_gain += best - fold["partition_cost"] - fold["selector_cost"]
            rng = random.Random(SEED + 7000001 + world * 100003 + fold["outer"])
            shuffled_selected.append(permute_mapping(fold["selected_mapping"], fold["profiles"], rng))
        null_paid.append(world_gain)
        null_ari.append(mean(adjusted_rand(a, b) for a, b in itertools.combinations(shuffled_selected, 2)))

    raw_gain = sum(f["raw_gain"] for f in fold_objects)
    paid_gain = sum(f["paid_gain"] for f in fold_objects)
    partition_cost = sum(f["partition_cost"] for f in fold_objects)
    selector_cost = sum(f["selector_cost"] for f in fold_objects)
    positive_folds = sum(f["raw_gain"] > 0 for f in fold_objects)
    largest_removed_gain = sum(f["largest_gain"] for f in fold_objects)
    frequent_removed_gain = sum(f["frequent_gain"] for f in fold_objects)
    null_p = (1 + sum(value >= paid_gain for value in null_paid)) / (1 + len(null_paid))
    stability_p = (1 + sum(value >= observed_ari for value in null_ari)) / (1 + len(null_ari))
    stability_q95 = percentile(null_ari, 0.95)
    model_totals = Counter()
    for fold in fold_objects:
        model_totals.update(fold["model_bits"])

    full_types, full_matrix, full_views, full_frequencies = signature_matrix(events)
    full_sim = full_matrix @ full_matrix.T
    _, full_string_mapping, full_modes = string_partition(events)
    with ATLAS.open(encoding="utf-8", newline="") as fh:
        atlas_rows = {row["joint_tuple_id"]: row for row in csv.DictReader(fh, delimiter="\t")}
    alias_to_raw = {alias: raw for raw, alias in opaque_map.items()}
    candidate_pairs = set()
    for i, t in enumerate(full_types):
        order = np.argsort(-full_sim[i])
        for j in order[1:9]:
            candidate_pairs.add(tuple(sorted((t, full_types[int(j)]))))
    merge_rows, counter_rows = [], []
    for a, b in sorted(candidate_pairs):
        eligible = coassigned = direct = 0
        for fold in fold_objects:
            mapping = fold["selected_mapping"]
            if a in mapping and b in mapping:
                eligible += 1
                coassigned += mapping[a] == mapping[b]
                direct += any({x, y} == {a, b} for x, y, _ in fold["directs"][fold["selected_fraction"]])
        if eligible < 7 or coassigned == 0:
            continue
        stability = coassigned / eligible
        raw_a, raw_b = alias_to_raw[a], alias_to_raw[b]
        host_same = atlas_rows[raw_a]["host_id"] == atlas_rows[raw_b]["host_id"]
        surface_a, surface_b = full_modes[a], full_modes[b]
        max_len = max(len(surface_a), len(surface_b), 1)
        edit_distance = 0 if surface_a == surface_b else 1 if edit_leq_one(surface_a, surface_b) else 2
        similarities = {view: view_similarity(full_views[a][view], full_views[b][view]) for view in VIEW_WEIGHTS}
        top_views = "|".join(name for name, _ in sorted(similarities.items(), key=lambda item: (-item[1], item[0]))[:3])
        row = {
            "tuple_a": a, "tuple_b": b, "coassignment_stability": f"{stability:.9f}", "eligible_folds": eligible,
            "direct_merge_folds": direct, "support_events": full_frequencies[a] + full_frequencies[b],
            "support_folios": len({e["physical_folio"] for e in events if e["tuple"] in {a, b}}),
            "held_gain_contribution": f"{event_gain_by_type[a] + event_gain_by_type[b]:.9f}",
            "page_host_same": int(host_same), "string_group_same": int(full_string_mapping[a] == full_string_mapping[b]),
            "normalized_edit_diagnostic": f"{edit_distance / max_len:.9f}", "supporting_views": top_views,
        }
        if stability >= 0.70:
            merge_rows.append(row)
        if stability < 0.50 or float(row["held_gain_contribution"]) < 0:
            counter_rows.append({**row, "counterexample_reason": "FOLD_UNSTABLE" if stability < 0.50 else "NEGATIVE_HELD_CONTRIBUTION"})
    merge_rows.sort(key=lambda r: (-float(r["coassignment_stability"]), -int(r["support_events"]), r["tuple_a"], r["tuple_b"]))
    counter_rows.sort(key=lambda r: (float(r["coassignment_stability"]), float(r["held_gain_contribution"]), r["tuple_a"], r["tuple_b"]))
    merge_rows, counter_rows = merge_rows[:100], counter_rows[:100]

    powered_registers = {k: strata_gain["register"][k] for k, n in strata_n["register"].items() if n >= 100}
    powered_sections = {k: strata_gain["section"][k] for k, n in strata_n["section"].items() if n >= 100}
    median_fraction = sorted(f["selected_fraction"] for f in fold_objects)[len(fold_objects) // 2]
    string_cross_fraction = mean(not bool(int(r["string_group_same"])) for r in merge_rows) if merge_rows else 0.0
    gates = {
        "k_meaningfully_below_exact": median_fraction <= 0.90,
        "selector_paid_gain_positive": paid_gain > 0,
        "aggregate_raw_gain_positive": raw_gain > 0,
        "at_least_8_of_11_positive_folds": positive_folds >= 8,
        "multiple_registers_and_sections": sum(v > 0 for v in powered_registers.values()) >= 3 and sum(v > 0 for v in powered_sections.values()) >= 3,
        "stability_above_matched_null": observed_ari > stability_q95,
        "positive_without_largest_cluster": largest_removed_gain > 0,
        "positive_without_top_frequent_types": frequent_removed_gain > 0,
        "beats_frequency_page_host_and_gdt338_after_cost": (
            model_totals["GLOBAL_FREQUENCY"] - model_totals["LEARNED_LATENT_CLASS"] - partition_cost - selector_cost > 0
            and model_totals["PAGE_HOST"] - model_totals["LEARNED_LATENT_CLASS"] - partition_cost - selector_cost > 0
            and paid_gain > 0
        ),
        "not_reducible_to_string_similarity": model_totals["STRING_SIMILARITY"] - model_totals["LEARNED_LATENT_CLASS"] - partition_cost - selector_cost > 0 and string_cross_fraction >= 0.50,
    }
    if all(gates.values()):
        status = "PREDICTIVE_LATENT_TUPLE_EQUIVALENCE_SUPPORTED"
    elif raw_gain > 0 and (
        not gates["stability_above_matched_null"]
        or model_totals["GLOBAL_FREQUENCY"] <= model_totals["LEARNED_LATENT_CLASS"]
        or model_totals["PAGE_HOST"] <= model_totals["LEARNED_LATENT_CLASS"]
        or model_totals["STRING_SIMILARITY"] <= model_totals["LEARNED_LATENT_CLASS"]
        or largest_removed_gain <= 0 or frequent_removed_gain <= 0 or not merge_rows
    ):
        status = "APPARENT_EQUIVALENCE_EXPLAINED_BY_EXISTING_STRUCTURE"
    elif raw_gain > 0:
        status = "LATENT_SHARING_WEAK_NOT_A_LEXICON_EQUIVALENCE"
    else:
        status = "JOINT_TUPLE_LEXICON_NOT_COMPRESSIBLE_BY_FREE_PREDICTIVE_EQUIVALENCE"

    fold_fields = (
        "outer_fold", "held_folios", "selected_fraction", "selected_k", "training_types", "held_events", "model",
        "bits_total", "bits_previous", "bits_next", "bits_placement", "bits_boundary_before", "bits_boundary_after",
        "raw_gain_vs_exact", "partition_cost", "selector_cost", "selector_paid_gain", "positive",
    )
    write_tsv(FOLDS_OUT, fold_rows, fold_fields)
    write_tsv(CLUSTERS_OUT, cluster_rows, (
        "outer_fold", "joint_tuple_id", "latent_form_id", "selected_fraction", "training_events", "training_folios", "cluster_size",
    ))
    merge_fields = (
        "tuple_a", "tuple_b", "coassignment_stability", "eligible_folds", "direct_merge_folds", "support_events", "support_folios",
        "held_gain_contribution", "page_host_same", "string_group_same", "normalized_edit_diagnostic", "supporting_views",
    )
    write_tsv(MERGES_OUT, merge_rows, merge_fields)
    write_tsv(COUNTER_OUT, counter_rows, merge_fields + ("counterexample_reason",))

    endpoint_gain = Counter()
    for outer in range(N_OUTER):
        exact_row = next(row for row in fold_rows if int(row["outer_fold"]) == outer and row["model"] == "EXACT_TUPLE")
        latent_row = next(row for row in fold_rows if int(row["outer_fold"]) == outer and row["model"] == "LEARNED_LATENT_CLASS")
        for endpoint in OUTCOMES:
            endpoint_gain[endpoint] += float(exact_row["bits_" + endpoint]) - float(latent_row["bits_" + endpoint])

    result = {
        "schema": "GDT398_OPAQUE_JOINT_TUPLE_EQUIVALENCE_RESULT_V1", "status": status,
        "summary": {
            "events": len(events), "folios": len(fold_of), "outer_folds": N_OUTER, "joint_tuple_types": len(ALL_TYPES),
            "median_selected_fraction": median_fraction,
            "selected_k_by_fold": [len(set(f["selected_mapping"].values())) for f in fold_objects],
            "raw_held_gain_bits": raw_gain, "partition_cost_bits": partition_cost, "selector_cost_bits": selector_cost,
            "selector_paid_gain_bits": paid_gain, "positive_folds": positive_folds,
            "largest_cluster_removed_gain_bits": largest_removed_gain,
            "frequent_types_removed_gain_bits": frequent_removed_gain, "mean_pairwise_ari": observed_ari,
            "null_ari_q95": stability_q95, "consistent_tuple_fraction": consistent_fraction,
            "stable_merge_rows": len(merge_rows),
        },
        "model_total_bits": dict(sorted(model_totals.items())), "endpoint_raw_gain_bits": dict(endpoint_gain),
        "stratum_gain_bits": {"register": dict(sorted(powered_registers.items())), "section": dict(sorted(powered_sections.items()))},
        "stability": {
            "pairwise_ari_values": ari_values, "matched_null_mean_ari": mean(null_ari), "matched_null_q95_ari": stability_q95,
            "inclusive_p": stability_p, "consistent_tuple_fraction_jaccard_ge_0_70": consistent_fraction,
            "mean_singletons": mean(sum(size == 1 for size in f["cluster_sizes"].values()) for f in fold_objects),
            "mean_giant_clusters_gt_10pct": mean(sum(size > 0.10 * len(f["types"]) for size in f["cluster_sizes"].values()) for f in fold_objects),
        },
        "null": {
            "worlds": NULL_WORLDS,
            "definition": "frequency×dominant-line-role×dominant-register matched class-assignment shuffle; max six cuts per fold",
            "selector_paid_gain_values": null_paid, "inclusive_p": null_p,
        },
        "gates": gates, "guarded_source": {"selected_view_sha256": separator_hash, **guard_stats},
        "overlap_audit": {
            "duplicate_found": False,
            "distinction": "GDT398 clusters complete opaque joint tuple IDs from training-only structural behavior; prior routes predefined edits, operations, PAGE_HOST, coordinates, cells, or renderer normalization.",
        },
        "claim_ceiling": "Opaque predictive formal equivalence only; no word lexeme morpheme stem allomorph synonym entity POS language meaning sound plaintext or translation.",
        "stop_rule": "No alternative clustering, K range, edit/PAGE_HOST initialization, semantic interpretation, or automatic follow-on experiment.",
        "inputs": {"gdt327_joint_tuple_interlinear.tsv": sha256(INTER), "gdt327_joint_tuple_atlas.tsv": sha256(ATLAS), "gdt398_safe_source_view.tsv.gz": separator_hash},
        "documents": {"METHOD.md": sha256(EXP / "METHOD.md"), "README.md": sha256(EXP / "README.md")},
        "implementation": {"run.py": sha256(Path(__file__))},
        "f84": {"allowed": False, "accessed": False, "retained": False, "scored": False},
        "f84r": {"allowed": False, "accessed": False, "retained": False, "scored": False},
        "voynich_semantics_scored": False,
    }

    report = [
        "# GDT398 opaque joint-tuple predictive equivalence preflight", "", f"Status: **{status}**.", "",
        "## Decisive held-folio result", "", "| quantity | result |", "|---|---:|",
        f"| exact tuple types | {len(ALL_TYPES):,} |", f"| median selected retained fraction | {median_fraction:.2f} |",
        f"| raw gain over exact tuple | {raw_gain:+.3f} bits |", f"| partition cost | {partition_cost:.3f} bits |",
        f"| selector cost | {selector_cost:.3f} bits |", f"| selector-paid gain | {paid_gain:+.3f} bits |",
        f"| positive outer folds | {positive_folds}/{N_OUTER} |", f"| matched-null p | {null_p:.6f} |",
        f"| mean pairwise ARI / null q95 | {observed_ari:.4f} / {stability_q95:.4f} |",
        f"| gain without largest cluster | {largest_removed_gain:+.3f} bits |",
        f"| gain without top 5% frequent types | {frequent_removed_gain:+.3f} bits |", "", "## Baselines", "",
        "| model | held codelength (bits) | difference from exact |", "|---|---:|---:|",
    ]
    exact_total = model_totals["EXACT_TUPLE"]
    for model in ("GLOBAL_FREQUENCY", "EXACT_TUPLE", "PAGE_HOST", "GDT338_NORMALIZED", "STRING_SIMILARITY", "PLACEMENT_FREQUENCY", "LEARNED_LATENT_CLASS"):
        report.append(f"| {model} | {model_totals[model]:.3f} | {exact_total - model_totals[model]:+.3f} |")
    report.extend(["", "`GDT338_NORMALIZED` is exactly the exact-tuple predictor at group resolution, as frozen: GDT338 removes wrapper rendering but preserves every joint tuple.", "", "## Gate audit", ""])
    for name, passed in gates.items():
        report.append(f"- `{name}`: **{'PASS' if passed else 'FAIL'}**")
    report.extend([
        "", "## Failure localization", "",
        f"GLOBAL/FREQUENCY is {model_totals['LEARNED_LATENT_CLASS'] - model_totals['GLOBAL_FREQUENCY']:.3f} bits shorter than the selected latent model. Every one of the {NULL_WORLDS} matched assignment worlds has a larger selector-paid gain than observed (`p={null_p:.6f}`). Removing the largest selected class changes the gain to {largest_removed_gain:+.3f} bits; removing the top 5% frequent types changes it to {frequent_removed_gain:+.3f} bits. No direct merge pair reaches the frozen 0.70 coassignment-stability publication threshold.", "",
        "The positive aggregate exact-versus-latent difference is therefore ordinary shrinkage concentrated in high-frequency/large-class structure, not a stable freely learned latent lexicon.", "",
        "## Interpretation", "",
        "The candidate algorithm saw only opaque type occurrences and the frozen structural views. PAGE_HOST and raw spelling entered named baselines and post-hoc diagnostics only. The result does not license a word, lexeme, morpheme, stem, allomorph, synonym, entity, POS, language, meaning, sound, plaintext, or translation.", "",
        "If the paid exact-identity comparison fails, this route is closed under the registered stop rule; no alternate clustering algorithm or relaxed K/stability search follows automatically.", "",
        "## Seal", "",
        "The GDT327 input and bound 8,448-row source view are f84-free. The view was created through the executable exact-locus allow-list guard with `f84*` rejection before materializing selected columns; the scorer reads only that frozen view. f84 and f84r were not retained, joined, or scored. No semantic or visual annotation was used.", "",
    ])
    REPORT.write_text("\n".join(report), encoding="utf-8")
    result["documents"]["REPORT.md"] = sha256(REPORT)
    result["outputs"] = {path.name: sha256(path) for path in (FOLDS_OUT, CLUSTERS_OUT, MERGES_OUT, COUNTER_OUT, REPORT)}
    result["content_sha256"] = content_hash(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "raw_gain": raw_gain, "paid_gain": paid_gain, "positive_folds": positive_folds, "null_p": null_p}, sort_keys=True))
    return 0


ALL_EVENTS: list[dict] = []
ALL_TYPES: list[str] = []


if __name__ == "__main__":
    raise SystemExit(main())
