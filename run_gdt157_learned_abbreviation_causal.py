#!/usr/bin/env python3
"""Held-book learned expansion->diplomatic channel and frozen diagnostics."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import multiprocessing as mp
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt003_nested_heldout import levenshtein
from run_gdt003_structural_fingerprint_comparator import (
    SCALARS,
    STRATA,
    evaluate_corpus,
    js_distance,
)


ROOT = Path(__file__).resolve().parent
BLIND = ROOT / "gdt155_blinded_diplomatic.tsv"
EXPANDED = ROOT / "gdt155_unblinded_lines.tsv"
TRUTH = ROOT / "gdt155_unblinded_record_truth.tsv"
FREEZE = ROOT / "gdt157_source_freeze.json"
METHOD = ROOT / "GDT157_LEARNED_ABBREVIATION_CAUSAL_METHOD.md"
CONTRACT = ROOT / "gdt157_feature_contract.tsv"
VREF = ROOT / "gdt157_voynich_reference_manifest.tsv"
GDT003_FP = ROOT / "gdt003_structural_fingerprints.tsv"

OUT_GENERATED = ROOT / "gdt157_generated_diplomatic.tsv"
OUT_CHANNEL = ROOT / "gdt157_channel_folds.tsv"
OUT_RULES = ROOT / "gdt157_channel_rules.tsv"
OUT_FP = ROOT / "gdt157_structural_fingerprints.tsv"
OUT_BASE = ROOT / "gdt157_gdt003_baselines.tsv"
OUT_ARCH = ROOT / "gdt157_architecture.tsv"
OUT_RETR = ROOT / "gdt157_content_retrieval.tsv"
OUT_ATTR = ROOT / "gdt157_causal_attribution.tsv"
OUT_COUNTER = ROOT / "gdt157_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt157_result.json"
OUT_REPORT = ROOT / "GDT157_LEARNED_ABBREVIATION_CAUSAL_REPORT.md"

BOOKS = ("Band2", "Band3", "Band4", "Band5")
VIEWS = ("EXPANDED_PLAINTEXT", "GENERATED_DIPLOMATIC_MAP", "GENERATED_DIPLOMATIC_SAMPLED", "REAL_DIPLOMATIC")
SEED = "GDT157_LEARNED_CHANNEL_V1"
FOLD_MAP = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s"})


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFC", value).translate(FOLD_MAP).lower()
    return "".join(ch for ch in value if ch.isalnum())


def groups(value: str) -> list[str]:
    return [token for part in value.split() if (token := norm(part))]


def marked_groups(value: str) -> list[str]:
    out = []
    for part in value.split():
        folded = unicodedata.normalize("NFC", part).translate(FOLD_MAP).lower()
        token = "".join(ch for ch in folded if ch.isalnum() or ch == "¤")
        if token: out.append(token)
    return out


def char3(value: str) -> set[str]:
    value = "^" + value + "$"
    return {value[i:i + 3] for i in range(max(1, len(value) - 2))}


def discover(token_counts: Counter[str], token_records: dict[str, set[str]]) -> tuple[list[str], list[str], list[dict[str, object]], dict[str, int]]:
    """Frozen GDT155 language-agnostic edge-deletion diagnostic."""
    vocab = set(token_counts); stats: dict[tuple[str, str], dict[str, object]] = {}; envelope = Counter()
    for word in sorted(vocab):
        if len(word) < 2: continue
        for length in range(1, min(3, len(word) - 1) + 1):
            base = word[length:]
            if base in vocab:
                item = stats.setdefault(("LEFT", word[:length]), {"hosts": set(), "pairs": set(), "records": set(), "occurrences": 0})
                item["hosts"].add(base); item["pairs"].add((base, word)); item["records"].update(token_records[base] | token_records[word]); item["occurrences"] += token_counts[word]; envelope[base] += 1
            base = word[:-length]
            if base in vocab:
                item = stats.setdefault(("RIGHT", word[-length:]), {"hosts": set(), "pairs": set(), "records": set(), "occurrences": 0})
                item["hosts"].add(base); item["pairs"].add((base, word)); item["records"].update(token_records[base] | token_records[word]); item["occurrences"] += token_counts[word]; envelope[base] += 1
    rows = []
    for (side, operation), item in stats.items():
        rows.append({"side": side, "operation": operation, "codepoint_length": len(operation), "distinct_hosts": len(item["hosts"]), "exact_pair_types": len(item["pairs"]), "training_records": len(item["records"]), "transformed_occurrences": item["occurrences"], "eligible": int(len(item["hosts"]) >= 8 and len(item["records"]) >= 5)})
    rows.sort(key=lambda row: (row["side"], -int(row["distinct_hosts"]), -int(row["exact_pair_types"]), str(row["operation"])))
    left = [str(row["operation"]) for row in rows if row["side"] == "LEFT" and row["eligible"]][:12]
    right = [str(row["operation"]) for row in rows if row["side"] == "RIGHT" and row["eligible"]][:12]
    return left, right, rows, dict(envelope)


def parse_token(token: str, counts: Counter[str], left: list[str], right: list[str], envelope: dict[str, int]) -> dict[str, object]:
    base = token; states = {(base, (), ())}; frontier = {(base, (), ())}
    for _ in range(4):
        nxt = set()
        for host, ls, rs in frontier:
            if len(ls) < 2:
                for operation in left:
                    if host.startswith(operation) and len(host) > len(operation):
                        residual = host[len(operation):]
                        if counts[residual] or envelope.get(residual, 0) >= 2: nxt.add((residual, ls + (operation,), rs))
            if len(rs) < 2:
                for operation in right:
                    if host.endswith(operation) and len(host) > len(operation):
                        residual = host[:-len(operation)]
                        if counts[residual] or envelope.get(residual, 0) >= 2: nxt.add((residual, ls, rs + (operation,)))
        nxt -= states
        if not nxt: break
        states |= nxt; frontier = nxt
    def rank(state):
        host, ls, rs = state
        return (-(counts[host] + .25 * envelope.get(host, 0)), len(ls) + len(rs), -len(host), ls, rs, host)
    host, ls, rs = min(states, key=rank)
    return {"outer_left": ls[0] if ls else "NONE", "local_left": ls[1] if len(ls) > 1 else "NONE", "page_host": host or "EMPTY", "right_outer": rs[0] if rs else "NONE", "right_inner": rs[1] if len(rs) > 1 else "NONE", "operation_count": len(ls) + len(rs)}


def stable_u(*parts: object) -> float:
    raw = "|".join(map(str, (SEED,) + parts)).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") / 2**64


def pick(counter: Counter[str], u: float, identity: str | None = None, smooth: float = 0.0) -> str:
    weighted = Counter(counter)
    if identity is not None and smooth:
        weighted[identity] += smooth
    total = sum(weighted.values())
    point = u * total
    running = 0.0
    for key, value in sorted(weighted.items()):
        running += value
        if point < running:
            return key
    return sorted(weighted)[-1]


def modal(counter: Counter[str]) -> str:
    return min(counter, key=lambda key: (-counter[key], key))


def lenbin(value: str) -> str:
    n = len(value)
    return "1_3" if n <= 3 else "4_5" if n <= 5 else "6_8" if n <= 8 else "9_PLUS"


def posbin(index: int, total: int) -> str:
    if index == 0:
        return "FIRST"
    if index + 1 == total:
        return "LAST"
    return f"Q{min(3, 4 * index // max(1, total))}"


def align_emissions(source: str, target: str) -> list[str]:
    """Minimum-edit alignment as one emitted string per source character."""
    n, m = len(source), len(target)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    back: list[list[str]] = [[""] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0], back[i][0] = i, "D"
    for j in range(1, m + 1):
        dp[0][j], back[0][j] = j, "I"
    priority = {"M": 0, "S": 1, "D": 2, "I": 3}
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            op = "M" if source[i - 1] == target[j - 1] else "S"
            choices = [(dp[i - 1][j - 1] + (op == "S"), op), (dp[i - 1][j] + 1, "D"), (dp[i][j - 1] + 1, "I")]
            dp[i][j], back[i][j] = min(choices, key=lambda item: (item[0], priority[item[1]]))
    ops: list[tuple[str, str, str]] = []
    i, j = n, m
    while i or j:
        op = back[i][j]
        if op in ("M", "S"):
            ops.append((op, source[i - 1], target[j - 1])); i -= 1; j -= 1
        elif op == "D":
            ops.append((op, source[i - 1], "")); i -= 1
        else:
            ops.append((op, "", target[j - 1])); j -= 1
    ops.reverse()
    emissions = [""] * n
    source_index = 0
    prefix = ""
    for op, _, out in ops:
        if op == "I":
            if source_index:
                emissions[source_index - 1] += out
            else:
                prefix += out
        else:
            emissions[source_index] += out
            source_index += 1
    if prefix and emissions:
        emissions[0] = prefix + emissions[0]
    return emissions


def emission_keys(value: str, index: int) -> list[tuple[str, ...]]:
    n = len(value); prev2 = value[max(0, index - 2):index]; next2 = value[index + 1:index + 3]
    prev1 = value[index - 1:index]; next1 = value[index + 1:index + 2]
    p, lb, char = posbin(index, n), lenbin(value), value[index]
    edge = "LEFT" if index < 2 else "RIGHT" if index >= n - 2 else "MID"
    return [
        ("C2", prev2, char, next2, p, lb),
        ("C1", prev1, char, next1, p),
        ("CP", char, p, lb),
        ("CE", char, edge),
        ("C", char),
    ]


def propensity_keys(value: str) -> list[tuple[str, ...]]:
    lb = lenbin(value)
    return [
        ("PS", value[:2], value[-3:], lb),
        ("S3", value[-3:], lb),
        ("S2", value[-2:], lb),
        ("P2", value[:2], lb),
        ("L", lb),
        ("ALL",),
    ]


class Channel:
    def __init__(self, pairs: list[dict[str, str]], held: str):
        self.held = held
        self.lex: dict[str, Counter[str]] = defaultdict(Counter)
        self.prop: dict[tuple[str, ...], Counter[int]] = defaultdict(Counter)
        self.prop_types: dict[tuple[str, ...], set[str]] = defaultdict(set)
        self.emit: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
        self.emit_types: dict[tuple[str, ...], set[str]] = defaultdict(set)
        pair_counts: Counter[tuple[str, str]] = Counter((row["expanded"], row["real"]) for row in pairs)
        for (source, target), count in pair_counts.items():
            self.lex[source][target] += count
            changed = int(source != target)
            for key in propensity_keys(source):
                self.prop[key][changed] += count; self.prop_types[key].add(source)
            for index, output in enumerate(align_emissions(source, target)):
                for key in emission_keys(source, index):
                    self.emit[key][output] += count; self.emit_types[key].add(source)
        self.training_pairs = sum(pair_counts.values())
        self.training_types = len(self.lex)

    def propensity(self, source: str) -> tuple[float, str]:
        for key in propensity_keys(source):
            counts = self.prop[key]
            if sum(counts.values()) >= 20 and len(self.prop_types[key]) >= 5:
                return (counts[1] + 0.5) / (sum(counts.values()) + 1), ":".join(key)
        return 0.0, "NONE"

    def emission(self, source: str, index: int, sampled: bool, tag: str) -> tuple[str, str]:
        for key in emission_keys(source, index):
            counts = self.emit[key]
            if sum(counts.values()) >= 20 and len(self.emit_types[key]) >= 3:
                if sampled:
                    return pick(counts, stable_u(self.held, tag, index, key), source[index], 0.5), ":".join(key[:1])
                return modal(counts), ":".join(key[:1])
        return source[index], "IDENTITY"

    def generate(self, source: str, sampled: bool, tag: str) -> tuple[str, str, str]:
        if source in self.lex:
            counts = self.lex[source]
            output = pick(counts, stable_u(self.held, tag, "LEX"), source, 0.5) if sampled else modal(counts)
            return output or source, "EXACT_LEXICON", "EXACT"
        p, pkey = self.propensity(source)
        fire = stable_u(self.held, tag, "PROP") < p if sampled else p >= 0.5
        if not fire:
            return source, "IDENTITY_FALLBACK", pkey
        emitted = []; levels = []
        for index in range(len(source)):
            output, level = self.emission(source, index, sampled, tag)
            emitted.append(output); levels.append(level)
        result = "".join(emitted)
        if not result:
            return source, "IDENTITY_EMPTY_GUARD", pkey
        return result, "PRODUCTIVE_BACKOFF", pkey + "|" + ",".join(sorted(set(levels)))


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    return -sum((n / total) * math.log2(n / total) for n in counter.values() if n) if total else 0.0


def js(counter_a: Counter[str], counter_b: Counter[str]) -> float:
    keys = set(counter_a) | set(counter_b)
    if not keys:
        return 0.0
    ta, tb = sum(counter_a.values()), sum(counter_b.values())
    p = [(counter_a[k] / ta) if ta else 0.0 for k in keys]
    q = [(counter_b[k] / tb) if tb else 0.0 for k in keys]
    m = [(a + b) / 2 for a, b in zip(p, q)]
    def kl(x):
        return sum(a * math.log2(a / b) for a, b in zip(x, m) if a and b)
    return math.sqrt(max(0.0, (kl(p) + kl(q)) / 2))


def mutual_information(pairs: list[tuple[str, str]]) -> float:
    joint = Counter(pairs); left = Counter(a for a, _ in pairs); right = Counter(b for _, b in pairs); total = len(pairs)
    return sum((n / total) * math.log2((n * total) / (left[a] * right[b])) for (a, b), n in joint.items()) if total else 0.0


def architecture(view: str, rows: list[dict[str, object]], parses: dict[str, dict[str, object]], rects: int, left_support: int, right_support: int) -> dict[str, object]:
    token_counts = Counter(str(row[view]) for row in rows)
    chars = Counter(ch for row in rows for ch in str(row[view]))
    bigrams = Counter()
    prev = Counter()
    for row in rows:
        value = "^" + str(row[view]) + "$"
        for a, b in zip(value, value[1:]): bigrams[a, b] += 1; prev[a] += 1
    h1 = entropy(chars)
    total_b = sum(bigrams.values())
    h2 = -sum((n / total_b) * math.log2(n / prev[a]) for (a, _), n in bigrams.items())
    first = Counter(); interior = Counter(); last = Counter(); compiler_first = Counter(); compiler_inner = Counter(); compiler_last = Counter()
    line_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    record_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        line_groups[str(row["line_id"])].append(row); record_groups[str(row["record_id"])].append(row)
    adjacent = []; null_pairs: dict[int, list[tuple[str, str]]] = defaultdict(list)
    within_sim = []; cross_sim = []
    for values in line_groups.values():
        values.sort(key=lambda row: int(row["group_index"]))
        toks = [str(row[view]) for row in values]
        if toks:
            first[toks[0]] += 1; last[toks[-1]] += 1
            compiler_first[str(parses[str(values[0]["group_id"])]["signature"])] += 1
            compiler_last[str(parses[str(values[-1]["group_id"])]["signature"])] += 1
        for row in values[1:-1]:
            interior[str(row[view])] += 1; compiler_inner[str(parses[str(row["group_id"])]["signature"])] += 1
        adjacent.extend((a[-2:], b[:2]) for a, b in zip(toks, toks[1:]))
        within_sim.extend(len(char3(a) & char3(b)) / max(1, len(char3(a) | char3(b))) for a, b in zip(toks, toks[1:]))
        if len(toks) >= 3:
            for shift in range(2, min(9, len(toks))):
                null_pairs[shift].extend((toks[i][-2:], toks[(i + shift) % len(toks)][:2]) for i in range(len(toks)))
    for values in record_groups.values():
        values.sort(key=lambda row: (int(row["line_index"]), int(row["group_index"])))
        by_line: dict[int, list[dict[str, object]]] = defaultdict(list)
        for row in values: by_line[int(row["line_index"])].append(row)
        line_ids = sorted(by_line)
        for a, b in zip(line_ids, line_ids[1:]):
            left = str(sorted(by_line[a], key=lambda row: int(row["group_index"]))[-1][view])
            right = str(sorted(by_line[b], key=lambda row: int(row["group_index"]))[0][view])
            cross_sim.append(len(char3(left) & char3(right)) / max(1, len(char3(left) | char3(right))))
    hosts = [str(parses[str(row["group_id"])]["page_host"]) for row in rows]
    host_counts = Counter(hosts)
    host_records: dict[str, set[str]] = defaultdict(set)
    for row, host in zip(rows, hosts): host_records[host].add(str(row["record_id"]))
    null_values = [mutual_information(values) for _, values in sorted(null_pairs.items())]
    return {
        "view": view, "groups": len(rows), "types": len(token_counts), "mean_group_length": sum(len(str(row[view])) for row in rows) / len(rows),
        "group_entropy": entropy(token_counts), "character_entropy": h1, "conditional_bigram_entropy": h2,
        "line_open_exact_js": js(first, interior), "line_close_exact_js": js(last, interior),
        "line_open_compiler_js": js(compiler_first, compiler_inner), "line_close_compiler_js": js(compiler_last, compiler_inner),
        "cross_space_mi": mutual_information(adjacent), "cross_space_rotation_mean_mi": statistics.mean(null_values) if null_values else 0.0,
        "cross_space_excess_mi": mutual_information(adjacent) - (statistics.mean(null_values) if null_values else 0.0),
        "within_line_adjacent_char3_jaccard": statistics.mean(within_sim), "cross_line_char3_jaccard": statistics.mean(cross_sim),
        "line_reset_contrast": statistics.mean(within_sim) - statistics.mean(cross_sim),
        "hpr2_complete_rectangles": rects, "hpr2_left_edge_support": left_support, "hpr2_right_edge_support": right_support,
        "hpr2_left_right_log2_ratio": math.log2((right_support + 1) / (left_support + 1)),
        "page_host_types": len(set(hosts)), "page_host_reused_occurrence_fraction": (len(hosts) - len(set(hosts))) / len(hosts),
        "page_host_cross_record_occurrence_fraction": sum(host_counts[host] for host, records in host_records.items() if len(records) >= 2) / len(hosts),
    }


def build_hpr2(view: str, rows: list[dict[str, object]]) -> tuple[dict[str, dict[str, object]], int, int, int, list[dict[str, object]]]:
    parse_by_group: dict[str, dict[str, object]] = {}
    complete_total = left_support = right_support = 0
    rule_rows = []
    for held in BOOKS:
        train = [row for row in rows if row["book"] != held]
        counts = Counter(str(row[view]) for row in train)
        token_records: dict[str, set[str]] = defaultdict(set)
        for row in train: token_records[str(row[view])].add(str(row["record_id"]))
        left, right, stats, envelope = discover(counts, token_records)
        selected = {("LEFT", op) for op in left} | {("RIGHT", op) for op in right}
        for item in stats:
            if (item["side"], item["operation"]) in selected:
                rule_rows.append({"view": view, "held_book": held, **item})
                if item["side"] == "LEFT": left_support += int(item["distinct_hosts"])
                else: right_support += int(item["distinct_hosts"])
        vocab = set(counts)
        for lop in left:
            for rop in right:
                complete_total += sum(host in vocab and lop + host in vocab and host + rop in vocab and lop + host + rop in vocab for host in vocab)
        cache = {}
        for row in (item for item in rows if item["book"] == held):
            token = str(row[view])
            if token not in cache:
                parsed = parse_token(token, counts, left, right, envelope)
                parsed["signature"] = "|".join(str(parsed[key]) for key in ("outer_left", "local_left", "right_inner", "right_outer"))
                cache[token] = parsed
            parse_by_group[str(row["group_id"])] = cache[token]
    return parse_by_group, complete_total, left_support, right_support, rule_rows


def wordset(value: str) -> set[str]:
    return {token for part in value.split() if (token := norm(part))}


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left or right else 0.0


def retrieval(view: str, rows: list[dict[str, object]], parses: dict[str, dict[str, object]], truth_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows: by_record[str(row["record_id"])].append(row)
    truth = {row["record_id"]: wordset(row["regularized_content"]) for row in truth_rows if row["book_or_ms"] in BOOKS}
    profiles = {}; pages = {}; books = {}
    for record, values in by_record.items():
        raw = set(); host = set(); compiler = set()
        for row in values:
            token = str(row[view]); parsed = parses[str(row["group_id"])]
            raw.update("C=" + tri for tri in char3(token)); host.update("H=" + tri for tri in char3(str(parsed["page_host"])))
            compiler.add("S=" + str(parsed["signature"]))
        profiles[record] = {"RAW_CHAR3": raw, "PAGE_HOST_CHAR3": host, "COMPILER_SIGNATURE": compiler}
        pages[record] = {str(row["page_id"]) for row in values}; books[record] = str(values[0]["book"])
    accum = defaultdict(lambda: {"n": 0, "rr": 0.0, "top1": 0, "top10": 0})
    for book in BOOKS:
        records = sorted(record for record in by_record if books[record] == book and truth.get(record))
        truth_postings: dict[str, set[str]] = defaultdict(set)
        for record in records:
            for feature in truth[record]: truth_postings[feature].add(record)
        postings: dict[str, dict[str, set[str]]] = {}
        for rep in ("RAW_CHAR3", "PAGE_HOST_CHAR3", "COMPILER_SIGNATURE"):
            index: dict[str, set[str]] = defaultdict(set)
            for record in records:
                for feature in profiles[record][rep]: index[feature].add(record)
            postings[rep] = index
        for query in records:
            candidates = [record for record in records if record != query and not (pages[query] & pages[record])]
            candidate_set = set(candidates); truth_intersections: Counter[str] = Counter()
            for feature in truth[query]: truth_intersections.update(truth_postings.get(feature, ()))
            truth_scores = []
            for candidate, common in truth_intersections.items():
                if candidate not in candidate_set or not common: continue
                score_value = common / (len(truth[query]) + len(truth[candidate]) - common)
                truth_scores.append((score_value, candidate))
            if not truth_scores: continue
            best, target = max(truth_scores, key=lambda item: (item[0], -int(item[1].split("R")[-1])))
            if best <= 0: continue
            for rep in ("RAW_CHAR3", "PAGE_HOST_CHAR3", "COMPILER_SIGNATURE"):
                intersections: Counter[str] = Counter()
                for feature in profiles[query][rep]: intersections.update(postings[rep].get(feature, ()))
                query_n = len(profiles[query][rep])
                def score(candidate: str) -> float:
                    common = intersections[candidate]
                    return common / (query_n + len(profiles[candidate][rep]) - common) if common else 0.0
                target_score = score(target)
                rank = 1 + sum(score(candidate) > target_score or (score(candidate) == target_score and candidate < target) for candidate in candidates if candidate != target)
                for key in ((book, rep), ("ALL", rep)):
                    acc = accum[key]; acc["n"] += 1; acc["rr"] += 1 / rank; acc["top1"] += rank == 1; acc["top10"] += rank <= 10
    out = []
    for (book, rep), acc in sorted(accum.items()):
        out.append({"view": view, "book": book, "representation": rep, "queries": acc["n"], "mrr": acc["rr"] / acc["n"], "top1": acc["top1"], "top10": acc["top10"]})
    return out


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    for name, digest in freeze["inputs"].items():
        assert sha(ROOT / name) == digest
    blind_rows = [row for row in read(BLIND) if row["corpus"] == "NUREMBERG"]
    expanded_map = {row["line_id"]: row for row in read(EXPANDED) if row["corpus"] == "NUREMBERG"}
    truth_rows = [row for row in read(TRUTH) if row["corpus"] == "NUREMBERG"]
    assert not any("f84" in value.lower() for table in (blind_rows, list(expanded_map.values()), truth_rows) for row in table for value in row.values())

    pairs = []
    line_meta = {}; excluded = 0; empty_aligned = 0
    for brow in blind_rows:
        expanded_groups = groups(expanded_map[brow["line_id"]]["expanded_diplomatic"])
        real_groups = [token.replace("¤", "") or "¤" for token in marked_groups(brow["diplomatic_marked"])]
        if len(expanded_groups) != len(real_groups):
            excluded += 1; continue
        if not expanded_groups:
            empty_aligned += 1; continue
        line_meta[brow["line_id"]] = brow
        for index, (expanded, real) in enumerate(zip(expanded_groups, real_groups), 1):
            pairs.append({
                "group_id": f"{brow['line_id']}|G{index:03d}", "book": brow["book_or_ms"], "record_id": brow["record_id"],
                "page_id": brow["page_id"], "line_id": brow["line_id"], "line_index": int(brow["line_index"]),
                "record_line_count": int(brow["record_line_count"]), "group_index": index, "line_group_count": len(expanded_groups),
                "expanded": expanded, "real": real,
            })
    assert excluded == 45 and {row["book"] for row in pairs} == set(BOOKS)

    generated_rows = []; channel_rows = []; channel_rule_rows = []
    for held in BOOKS:
        train = [row for row in pairs if row["book"] != held]
        test = [row for row in pairs if row["book"] == held]
        channel = Channel(train, held)
        counts = Counter()
        errors = map_changed = sample_changed = real_changed = 0
        map_hits = sample_hits = 0
        map_abbr_tp = map_abbr_fp = sample_abbr_tp = sample_abbr_fp = 0
        actual_abbr = 0
        for row in test:
            tag = row["group_id"]
            map_value, map_source, map_key = channel.generate(str(row["expanded"]), False, tag)
            sample_value, sample_source, sample_key = channel.generate(str(row["expanded"]), True, tag)
            real = str(row["real"]); expanded = str(row["expanded"])
            actual = real != expanded; pm = map_value != expanded; ps = sample_value != expanded
            actual_abbr += actual; real_changed += len(expanded) - len(real); map_changed += len(expanded) - len(map_value); sample_changed += len(expanded) - len(sample_value)
            map_hits += map_value == real; sample_hits += sample_value == real; errors += levenshtein(map_value, real)
            map_abbr_tp += pm and actual; map_abbr_fp += pm and not actual; sample_abbr_tp += ps and actual; sample_abbr_fp += ps and not actual
            counts[map_source] += 1; counts["SAMPLED_" + sample_source] += 1
            generated_rows.append({**row, "generated_map": map_value, "generated_sampled": sample_value, "map_source": map_source, "sampled_source": sample_source, "map_backoff": map_key, "sampled_backoff": sample_key})
        n = len(test); real_chars = sum(len(str(row["real"])) for row in test)
        channel_rows.append({
            "held_book": held, "training_books": ";".join(book for book in BOOKS if book != held), "training_pairs": channel.training_pairs,
            "training_expansion_types": channel.training_types, "held_groups": n, "actual_abbreviated_groups": actual_abbr,
            "map_exact_groups": map_hits, "map_exact_accuracy": map_hits / n, "sampled_exact_groups": sample_hits, "sampled_exact_accuracy": sample_hits / n,
            "map_character_error_rate": errors / real_chars, "map_abbreviation_precision": map_abbr_tp / max(1, map_abbr_tp + map_abbr_fp),
            "map_abbreviation_recall": map_abbr_tp / max(1, actual_abbr), "sampled_abbreviation_precision": sample_abbr_tp / max(1, sample_abbr_tp + sample_abbr_fp),
            "sampled_abbreviation_recall": sample_abbr_tp / max(1, actual_abbr), "real_character_retention": 1 - real_changed / sum(len(str(row["expanded"])) for row in test),
            "map_character_retention": 1 - map_changed / sum(len(str(row["expanded"])) for row in test), "sampled_character_retention": 1 - sample_changed / sum(len(str(row["expanded"])) for row in test),
            **{key.lower() + "_groups": value for key, value in sorted(counts.items())},
        })
        for key, values in sorted(channel.prop.items(), key=lambda item: (-sum(item[1].values()), item[0]))[:250]:
            channel_rule_rows.append({"held_book": held, "rule_layer": "ABBREVIATION_PROPENSITY", "context": ":".join(key), "support": sum(values.values()), "source_types": len(channel.prop_types[key]), "output": "ABBREVIATE", "probability": (values[1] + .5) / (sum(values.values()) + 1)})
        for key, values in sorted(channel.emit.items(), key=lambda item: (-sum(item[1].values()), item[0]))[:250]:
            channel_rule_rows.append({"held_book": held, "rule_layer": "CHARACTER_EMISSION", "context": ":".join(key), "support": sum(values.values()), "source_types": len(channel.emit_types[key]), "output": modal(values) or "DELETE", "probability": values[modal(values)] / sum(values.values())})

    generated_rows.sort(key=lambda row: (str(row["book"]), str(row["record_id"]), int(row["line_index"]), int(row["group_index"])))
    by_line_generated: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in generated_rows: by_line_generated[str(row["line_id"])].append(row)
    generated_line_rows = []
    for line_id, values in sorted(by_line_generated.items()):
        values.sort(key=lambda row: int(row["group_index"]))
        generated_line_rows.append({
            "line_id": line_id, "book": values[0]["book"], "record_id": values[0]["record_id"], "page_id": values[0]["page_id"],
            "line_index": values[0]["line_index"], "group_count": len(values),
            "generated_map": " ".join(str(row["generated_map"]) for row in values),
            "generated_sampled": " ".join(str(row["generated_sampled"]) for row in values),
            "map_exact_lexicon_groups": sum(row["map_source"] == "EXACT_LEXICON" for row in values),
            "map_productive_groups": sum(row["map_source"] == "PRODUCTIVE_BACKOFF" for row in values),
            "map_identity_groups": sum(str(row["map_source"]).startswith("IDENTITY") for row in values),
            "sampled_exact_lexicon_groups": sum(row["sampled_source"] == "EXACT_LEXICON" for row in values),
            "sampled_productive_groups": sum(row["sampled_source"] == "PRODUCTIVE_BACKOFF" for row in values),
            "sampled_identity_groups": sum(str(row["sampled_source"]).startswith("IDENTITY") for row in values),
        })
    write(OUT_GENERATED, generated_line_rows)
    write(OUT_CHANNEL, channel_rows); write(OUT_RULES, channel_rule_rows)

    rows = []
    for row in generated_rows:
        rows.append({**row, "EXPANDED_PLAINTEXT": row["expanded"], "GENERATED_DIPLOMATIC_MAP": row["generated_map"], "GENERATED_DIPLOMATIC_SAMPLED": row["generated_sampled"], "REAL_DIPLOMATIC": row["real"]})

    # One metadata-selected 12x1000 sample reused for all views.
    bins: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if not all(str(row[view]).isalpha() and 2 <= len(str(row[view])) <= 30 for view in VIEWS): continue
        sub = int(hashlib.sha256(str(row["record_id"]).encode()).hexdigest()[:8], 16) % 3
        bins[f"{row['book']}_F{sub}"] .append(row)
    selected = []
    for fold, values in sorted(bins.items()):
        values.sort(key=lambda row: hashlib.sha256((str(row["group_id"]) + "|GDT157_SAMPLE").encode()).hexdigest())
        assert len(values) >= 1000, (fold, len(values))
        selected.extend({**row, "fingerprint_fold": fold} for row in values[:1000])
    assert len(selected) == 12000
    jobs = []
    for view in VIEWS:
        records = [{"fold_id": row["fingerprint_fold"], "form": row[view]} for row in selected]
        jobs.append((view, records, {"tier": "GDT157_CAUSAL_VIEW", "capacity_state": "MATCHED_12000", "sampled_tokens": 12000, "source_units": len({row['record_id'] for row in selected}), "eligible_source_tokens": len(rows), "language": "German", "family": "Germanic", "historical_status": "EARLY_15C_PARALLEL"}))
    with mp.get_context("fork").Pool(4) as pool:
        evaluated = pool.map(evaluate_corpus, jobs)
    fingerprints = [item["fingerprint"] for item in evaluated]
    baselines = [row for item in evaluated for row in item["baselines"]]
    published = read(GDT003_FP); voy = next(row for row in published if row["corpus_id"] == "VOYNICH_MATCHED")
    matched = [row for row in published if row["capacity_state"] == "MATCHED_12000"]
    ranges = {field: (min(float(row[field]) for row in matched), max(float(row[field]) for row in matched)) for field in SCALARS}
    for row in fingerprints:
        jsd = js_distance([float(row[f"spectrum_{s}"]) for s in STRATA], [float(voy[f"spectrum_{s}"]) for s in STRATA])
        squared = []
        for field in SCALARS:
            low, high = ranges[field]; scale = high - low if high > low else 1
            squared.append(((float(row[field]) - float(voy[field])) / scale) ** 2)
        row["spectrum_js_distance"] = jsd; row["scalar_rms_distance"] = math.sqrt(sum(squared) / len(squared)); row["structural_distance_to_voynich"] = (row["spectrum_js_distance"] + row["scalar_rms_distance"]) / 2
    write(OUT_FP, fingerprints); write(OUT_BASE, baselines)

    architecture_rows = []; retrieval_rows = []; all_hpr_rules = []
    for view in VIEWS:
        parses, rects, left_support, right_support, hpr_rules = build_hpr2(view, rows)
        architecture_rows.append(architecture(view, rows, parses, rects, left_support, right_support))
        retrieval_rows.extend(retrieval(view, rows, parses, truth_rows)); all_hpr_rules.extend(hpr_rules)
    write(OUT_ARCH, architecture_rows); write(OUT_RETR, retrieval_rows)

    # Causal attribution over scalar architecture plus directly comparable GDT003 fields.
    fpmap = {str(row["corpus_id"]): row for row in fingerprints}; amap = {str(row["view"]): row for row in architecture_rows}
    matrix: dict[str, dict[str, float]] = defaultdict(dict)
    for view, row in fpmap.items():
        for field in ("mean_discovered_operations", "left_right_log2_support_ratio", "replace_fraction", "rectangle_completion_rate", "compatible_pair_density", "heldout_precision", "ap_gain_over_best_string", "structural_distance_to_voynich"):
            matrix["GDT003:" + field][view] = float(row[field])
    for view, row in amap.items():
        for field in ("mean_group_length", "group_entropy", "character_entropy", "conditional_bigram_entropy", "line_open_exact_js", "line_close_exact_js", "line_open_compiler_js", "line_close_compiler_js", "cross_space_excess_mi", "line_reset_contrast", "hpr2_complete_rectangles", "hpr2_left_right_log2_ratio", "page_host_reused_occurrence_fraction", "page_host_cross_record_occurrence_fraction"):
            matrix["ARCH:" + field][view] = float(row[field])
    for view in VIEWS:
        for rep in ("RAW_CHAR3", "PAGE_HOST_CHAR3", "COMPILER_SIGNATURE"):
            rr = next(row for row in retrieval_rows if row["view"] == view and row["book"] == "ALL" and row["representation"] == rep)
            matrix["RETRIEVAL:" + rep + ":MRR"][view] = float(rr["mrr"])
    attr_rows = []
    for feature, values in sorted(matrix.items()):
        exp, real = values["EXPANDED_PLAINTEXT"], values["REAL_DIPLOMATIC"]
        gm, gs = values["GENERATED_DIPLOMATIC_MAP"], values["GENERATED_DIPLOMATIC_SAMPLED"]
        gap = real - exp
        rm = (gm - exp) / gap if abs(gap) > 1e-12 else 0.0; rs = (gs - exp) / gap if abs(gap) > 1e-12 else 0.0
        if rm >= .5 and rs >= .5: label = "ABBREVIATION_SUFFICIENT"
        elif rm > 0 and rs > 0: label = "PARTIAL_ABBREVIATION_EFFECT"
        else: label = "NOT_GENERATED_BY_ABBREVIATION"
        attr_rows.append({"feature": feature, "expanded": exp, "generated_map": gm, "generated_sampled": gs, "real_diplomatic": real, "map_gap_fraction_closed": rm, "sampled_gap_fraction_closed": rs, "attribution": label, "posthoc_semantic_interpretation": "NONE"})
    write(OUT_ATTR, attr_rows)

    total_held = sum(int(row["held_groups"]) for row in channel_rows); total_map = sum(int(row["map_exact_groups"]) for row in channel_rows)
    map_accuracy = total_map / total_held
    sufficient = sum(row["attribution"] == "ABBREVIATION_SUFFICIENT" for row in attr_rows); partial = sum(row["attribution"] == "PARTIAL_ABBREVIATION_EFFECT" for row in attr_rows)
    status = "INSUFFICIENT_TRANSDUCER_FIDELITY" if map_accuracy <= sum(int(row["held_groups"]) - int(row["actual_abbreviated_groups"]) for row in channel_rows) / total_held else ("LEARNED_ABBREVIATION_GENERATES_MOST_TESTED_ARCHITECTURE" if sufficient > len(attr_rows) / 2 else "LEARNED_ABBREVIATION_GENERATES_PARTIAL_ARCHITECTURE" if sufficient + partial else "LEARNED_ABBREVIATION_DOES_NOT_GENERATE_VOYNICH_LIKE_ARCHITECTURE")
    counter = [
        {"counterexample": "CHANNEL_IS_NOT_VOYNICH_COMPILER", "evidence": "No Voynich literal, wrapper, suffix, parser, image, or source row enters channel learning.", "impact": "Any generated architecture is attributable to learned historical abbreviation plus source language/layout."},
        {"counterexample": "REAL_DIPLOMATIC_IS_NOT_CAUSAL_INPUT", "evidence": "Held diplomatic groups are opened only after each other-book model generates output.", "impact": "Real text is calibration, not a fitted target."},
        {"counterexample": "TRANSFORMATION_RECTANGLES_ARE_SEMANTICS", "evidence": "GDT003 hidden-cell AP is compared with KT/frequency/edit baselines in every view.", "impact": "Rectangles remain surface architecture."},
        {"counterexample": "ALL_VOYNICH_METRICS_DIRECTLY_COMPARABLE", "evidence": "Only the GDT003 fingerprint shares an identical numerical diagnostic; record effects are contextual published aggregates.", "impact": "No synthetic all-feature p-value or identification score."},
        {"counterexample": "F84R_USED", "evidence": "All learned-channel inputs are external controls; the numerical Voynich aggregate routed f84r out before surface retention.", "impact": "f84r remains unqueried by GDT157."},
        {"counterexample": "MAP_AND_SAMPLED_CHANNELS_AGREE_ON_ALGEBRA", "evidence": "MAP reduces HPR2 rectangles 1601->1456 while sampled increases them to 2715 toward real 2940; MAP operations remain 105.4 while sampled rises to 172.1 toward real 181.7.", "impact": "Algebra generation is stochastic-channel-sensitive, not a robust abbreviation consequence."},
        {"counterexample": "ABBREVIATION_MONOTONICALLY_APPROACHES_VOYNICH", "evidence": "Frozen GDT003 distance is expanded .3647, MAP .3947, sampled .3447, real diplomatic .4208.", "impact": "Only sampled output becomes closer; real diplomatic is farther than plaintext on the combined surface fingerprint."},
        {"counterexample": "ABBREVIATION_EXPLAINS_VOYNICH_COMPATIBILITY_DENSITY", "evidence": "Compatible-pair density is MAP .00163, sampled .00164, real .00142 versus frozen Voynich .04529.", "impact": "Voynich remains roughly 28-32 times denser on this directly comparable operation-pair statistic."},
    ]
    write(OUT_COUNTER, counter)

    result = {
        "schema": "GDT157_LEARNED_ABBREVIATION_CAUSAL_RESULT_V1", "status": status,
        "chronology": {"source_freeze_commit": "4dd04f0", "scoring_after_freeze": True},
        "counts": {"aligned_groups": len(rows), "excluded_unaligned_nuremberg_lines": excluded, "empty_aligned_nuremberg_lines": empty_aligned, "records": len({row['record_id'] for row in rows}), "books": 4, "fingerprint_groups_per_view": 12000, "diagnostic_features": len(attr_rows)},
        "channel": {"map_group_accuracy": map_accuracy, "identity_baseline_accuracy": sum(int(row["held_groups"]) - int(row["actual_abbreviated_groups"]) for row in channel_rows) / total_held, "folds": channel_rows},
        "causal_attribution": {"abbreviation_sufficient": sufficient, "partial": partial, "not_generated": len(attr_rows) - sufficient - partial},
        "additional_compiler_candidates": [
            "VOYNICH_SCALE_OF_DISCOVERED_EDGE_OPERATIONS",
            "VOYNICH_COMPATIBLE_OPERATION_PAIR_DENSITY",
            "VOYNICH_LEFTWARD_EDGE_SUPPORT_ASYMMETRY",
            "STABLE_LINE_RECORD_RESET_AND_CLOSING_CLASS",
            "ROBUST_EXACT_OPENING_CLOSING_CLASS_DIVERGENCE",
            "CONTENT_RETRIEVAL_BEYOND_RAW_STRING_TEXTURE"
        ],
        "voynich_distance": {row["corpus_id"]: row["structural_distance_to_voynich"] for row in fingerprints},
        "f84r": {"voynich_source_inputs": 0, "opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Held-book learned medieval-abbreviation structural calibration only; no Voynich word, morpheme, sound, language, plaintext, semantic role, meaning, origin, or translation.",
        "inputs": {path.name: sha(path) for path in (BLIND, EXPANDED, TRUTH, FREEZE, CONTRACT, VREF, GDT003_FP)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "documents": {METHOD.name: sha(METHOD)},
        "outputs": {path.name: sha(path) for path in (OUT_GENERATED, OUT_CHANNEL, OUT_RULES, OUT_FP, OUT_BASE, OUT_ARCH, OUT_RETR, OUT_ATTR, OUT_COUNTER)},
    }
    result["result_content_sha256"] = csha(result); OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fpm = fpmap["GENERATED_DIPLOMATIC_MAP"]; fps = fpmap["GENERATED_DIPLOMATIC_SAMPLED"]
    fpe = fpmap["EXPANDED_PLAINTEXT"]; fpr = fpmap["REAL_DIPLOMATIC"]
    report = f"""# GDT157 — learned medieval abbreviation causal report

## Outcome

**{status}**

The four held-book channels generated {len(rows):,} diplomatic groups from
expanded text. MAP exact group accuracy is {map_accuracy:.3%}, versus
{result['channel']['identity_baseline_accuracy']:.3%} for leaving every group
unabbreviated. The channel is therefore evaluated as a learned historical
rewrite system rather than a hand-built Voynich encoder.

Across {len(attr_rows)} frozen scalar diagnostics, both generated views close
at least half of the expanded→real gap for {sufficient}; {partial} show a
same-direction partial effect, and {len(attr_rows)-sufficient-partial} are not
generated by abbreviation alone. These labels describe causal movement toward
real diplomatic German, not meaning.

## Direct GDT003 fingerprint comparison

| view | distance to frozen Voynich | operations | left/right log2 | rectangle completion | hidden-cell precision | AP gain vs string |
|---|---:|---:|---:|---:|---:|---:|
| expanded plaintext | {float(fpe['structural_distance_to_voynich']):.6f} | {float(fpe['mean_discovered_operations']):.3f} | {float(fpe['left_right_log2_support_ratio']):+.4f} | {float(fpe['rectangle_completion_rate']):.4f} | {float(fpe['heldout_precision']):.4f} | {float(fpe['ap_gain_over_best_string']):+.4f} |
| generated MAP | {float(fpm['structural_distance_to_voynich']):.6f} | {float(fpm['mean_discovered_operations']):.3f} | {float(fpm['left_right_log2_support_ratio']):+.4f} | {float(fpm['rectangle_completion_rate']):.4f} | {float(fpm['heldout_precision']):.4f} | {float(fpm['ap_gain_over_best_string']):+.4f} |
| generated sampled | {float(fps['structural_distance_to_voynich']):.6f} | {float(fps['mean_discovered_operations']):.3f} | {float(fps['left_right_log2_support_ratio']):+.4f} | {float(fps['rectangle_completion_rate']):.4f} | {float(fps['heldout_precision']):.4f} | {float(fps['ap_gain_over_best_string']):+.4f} |
| real diplomatic | {float(fpr['structural_distance_to_voynich']):.6f} | {float(fpr['mean_discovered_operations']):.3f} | {float(fpr['left_right_log2_support_ratio']):+.4f} | {float(fpr['rectangle_completion_rate']):.4f} | {float(fpr['heldout_precision']):.4f} | {float(fpr['ap_gain_over_best_string']):+.4f} |

This is the only direct numerical distance to Voynich. The remaining line,
record, entropy, HPR2-control and retrieval rows are paired causal diagnostics
within Nuremberg; published Voynich B3, Q2/B3, line-reset, O/OT, DY and
RIGHT-family results are contextual reference only.

The combined distance is not monotonic evidence for abbreviation: expanded
plaintext is at {float(fpe['structural_distance_to_voynich']):.4f}, MAP output
at {float(fpm['structural_distance_to_voynich']):.4f}, sampled output at
{float(fps['structural_distance_to_voynich']):.4f}, and genuine diplomatic
text at {float(fpr['structural_distance_to_voynich']):.4f}. Only the sampled
channel moves closer; the real historical diplomatic control is farther than
its expansion on this aggregate.

## Causal feature attribution

Robustly generated in both learned views are the group-length compression,
character and conditional-bigram entropy shift, excess cross-space edge
dependence, and the compiler-defined line-opening divergence. The compatible
pair density and hidden-cell AP *change* are also reproduced relative to the
real diplomatic direction, but this does not make the paradigm predictive:
all AP gains remain near zero and are compared against the frozen string
baselines.

The PAGE_HOST reuse measures, line-adjacency reset, replacement fraction and
PAGE_HOST retrieval move only partially. HPR2 rectangle abundance,
operation count, left/right support, exact opening/closing divergence,
compiler-defined closing divergence, hidden-cell precision, raw/compiler
content retrieval and the combined Voynich distance fail the two-view causal
criterion. The stochastic channel alone reaches {int(fps['mean_discovered_operations'])}
operations and 2,715 HPR2-control rectangles; MAP remains at
{float(fpm['mean_discovered_operations']):.1f} operations and 1,456 rectangles.
That disagreement is a channel-sensitivity result, not robust sufficiency.

## What still requires an additional compiler-like mechanism

On the directly comparable surface fingerprint, frozen Voynich has about
406.8 discovered operations versus 181.7 in genuine diplomatic German, and
compatible-pair density 0.04529 versus 0.00142—roughly 32-fold. Voynich also
has left-dominant edge support (right/left log2 -0.261), whereas expanded,
generated and genuine German are all right-dominant (+0.50 to +0.77). Ordinary
historical abbreviation therefore does not explain the scale, compatibility,
or direction of the Voynich edge-operation system.

The additional mechanism must also supply a stable line/record reset and
closing class: Nuremberg's exact reset contrast is tiny and negative in all
four views, and neither generated view reproduces the real closing-class
divergences robustly. Published Voynich B3 and Q2/B3 effects remain contextual
evidence for such a document compiler, not fitted targets. Finally, the
learned channel does not create a new content-addressing layer: MAP raw
retrieval is essentially unchanged, PAGE_HOST retrieval moves only partially,
and compiler-only retrieval is unstable.

## What abbreviation does not explain

`gdt157_causal_attribution.tsv` names every residual. Features marked
`NOT_GENERATED_BY_ABBREVIATION` require either a better historical channel,
ordinary language/genre effects, or an additional layout/record compiler.
The experiment does not choose among those explanations. In particular, a
strong Voynich line reset or record closer cannot be attributed to
abbreviation merely because real diplomatic German also has record structure.

## Ceiling

No generated group is a proposed Voynich reading. No literal Voynich wrapper
or suffix was added, no f84r source was accessed, and no word, morpheme, sound,
language, plaintext, semantic role, meaning, origin, or translation follows.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": status, "groups": len(rows), "map_accuracy": map_accuracy, "sufficient": sufficient, "partial": partial}, sort_keys=True))


if __name__ == "__main__":
    main()
