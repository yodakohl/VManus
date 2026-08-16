#!/usr/bin/env python3
"""Blind surface and layout-assisted VManus-style diagnostics for GDT170."""
from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt170_observation_corpus.json.gz"
SOURCE_FREEZE = R / "gdt170_observation_oracle_freeze.json"
DESIGN = R / "gdt170_blind_design.json"
METHOD = R / "GDT170_FULL_OBSERVATION_INSTRUMENT_METHOD.md"
PARSES = R / "gdt170_blind_parses.json.gz"
OPERATIONS = R / "gdt170_blind_operations.tsv"
DIAGNOSTICS = R / "gdt170_blind_diagnostics.tsv"
RESULT = R / "gdt170_blind_result.json"
MODES = ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED")
ALPHA, BETA, NULL_WORLDS = 16.0, 8.0, 1024


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)


def write_tsv(path: Path, rows: list[dict]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def write_gzip(path: Path, payload) -> None:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle:
            handle.write(raw)


def load_rows() -> list[dict]:
    with gzip.open(SOURCE, "rt", encoding="utf8") as handle:
        payload = json.load(handle)
    assert payload["schema"] == "GDT170_STRICT_OBSERVATION_CORPUS_V1"
    rows = payload["rows"]
    assert len(rows) == 240000
    allowed = set(json.loads(SOURCE_FREEZE.read_text())["observation_allowed_fields"])
    assert all(set(row) == allowed for row in rows)
    return rows


def discover(rows: list[dict]) -> tuple[list[str], list[str], list[dict], dict[str, int], Counter]:
    counts = Counter(str(row["surface_group"]) for row in rows)
    folios: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        folios[str(row["surface_group"])].add(str(row["folio_id"]))
    vocab = set(counts)
    stats: dict[tuple[str, str], dict] = {}
    envelope = Counter()
    for word in sorted(vocab):
        if len(word) < 2:
            continue
        for length in range(1, min(3, len(word) - 1) + 1):
            base = word[length:]
            if base in vocab:
                item = stats.setdefault(("LEFT", word[:length]), {"hosts": set(), "folios": set(), "pairs": set(), "occ": 0})
                item["hosts"].add(base); item["folios"].update(folios[word] | folios[base]); item["pairs"].add((base, word)); item["occ"] += counts[word]
                envelope[base] += 1
            base = word[:-length]
            if base in vocab:
                item = stats.setdefault(("RIGHT", word[-length:]), {"hosts": set(), "folios": set(), "pairs": set(), "occ": 0})
                item["hosts"].add(base); item["folios"].update(folios[word] | folios[base]); item["pairs"].add((base, word)); item["occ"] += counts[word]
                envelope[base] += 1
    out = []
    for (side, op), item in stats.items():
        eligible = len(item["hosts"]) >= 8 and len(item["folios"]) >= 5
        out.append({"side": side, "operation": op, "operation_length": len(op),
                    "distinct_hosts": len(item["hosts"]), "exact_pair_types": len(item["pairs"]),
                    "synthetic_folios": len(item["folios"]), "transformed_occurrences": item["occ"],
                    "eligible": int(eligible), "host_set": item["hosts"]})
    out.sort(key=lambda x: (x["side"], -int(x["distinct_hosts"]), -int(x["exact_pair_types"]), str(x["operation"])))
    left = [str(x["operation"]) for x in out if x["side"] == "LEFT" and x["eligible"]][:12]
    right = [str(x["operation"]) for x in out if x["side"] == "RIGHT" and x["eligible"]][:12]
    return left, right, out, dict(envelope), counts


def log_lift(k: int, n: int, base_k: int, base_n: int) -> float:
    return math.log2(((k + 1) / (n + 2)) / ((base_k + 1) / (base_n + 2)))


def annotation_scores(rows: list[dict], left: list[str], right: list[str]) -> dict[tuple[str, str], float]:
    starts = sum(int(x["paragraph_start"]) and int(x["group_index"]) == 1 for x in rows)
    line_ends = sum(x["right_separator"] == "LINE_END" for x in rows)
    para_ends = sum(int(x["paragraph_end"]) and x["right_separator"] == "LINE_END" for x in rows)
    by_rh: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_rh[str(row["register"]), str(row["hand"])].append(row)
    result = {}
    for side, ops in (("LEFT", left), ("RIGHT", right)):
        for op in ops:
            occ = [x for x in rows if (str(x["surface_group"]).startswith(op) if side == "LEFT" else str(x["surface_group"]).endswith(op))]
            if side == "LEFT":
                lift = log_lift(sum(int(x["paragraph_start"]) and int(x["group_index"]) == 1 for x in occ), len(occ), starts, len(rows))
            else:
                lift = .5 * log_lift(sum(x["right_separator"] == "LINE_END" for x in occ), len(occ), line_ends, len(rows))
                lift += log_lift(sum(int(x["paragraph_end"]) and x["right_separator"] == "LINE_END" for x in occ), len(occ), para_ends, len(rows))
            rh_lifts = []
            for values in by_rh.values():
                sub = [x for x in values if (str(x["surface_group"]).startswith(op) if side == "LEFT" else str(x["surface_group"]).endswith(op))]
                if not sub:
                    continue
                if side == "LEFT":
                    rh_lifts.append(log_lift(sum(int(x["paragraph_start"]) and int(x["group_index"]) == 1 for x in sub), len(sub), starts, len(rows)))
                else:
                    rh_lifts.append(log_lift(sum(int(x["paragraph_end"]) and x["right_separator"] == "LINE_END" for x in sub), len(sub), para_ends, len(rows)))
            variance = float(np.var(rh_lifts)) if len(rh_lifts) > 1 else 0.0
            result[side, op] = .5 * lift - .25 * variance
    return result


def parse_token(token: str, counts: Counter, left: list[str], right: list[str], envelope: dict[str, int],
                mode: str, annotations: dict[tuple[str, str], float]) -> dict:
    states = {(token, (), ())}; frontier = {(token, (), ())}
    for _ in range(3):
        nxt = set()
        for host, ls, rs in frontier:
            if len(ls) < 2 and len(ls) + len(rs) < 3:
                for op in left:
                    if host.startswith(op) and len(host) > len(op):
                        residual = host[len(op):]
                        if counts[residual] or envelope.get(residual, 0) >= 2:
                            nxt.add((residual, ls + (op,), rs))
            if len(rs) < 2 and len(ls) + len(rs) < 3:
                for op in right:
                    if host.endswith(op) and len(host) > len(op):
                        residual = host[:-len(op)]
                        if counts[residual] or envelope.get(residual, 0) >= 2:
                            nxt.add((residual, ls, rs + (op,)))
        nxt -= states
        if not nxt:
            break
        states |= nxt; frontier = nxt

    def rank(state):
        host, ls, rs = state
        recurrence = counts[host] + .25 * envelope.get(host, 0)
        bonus = 0.0
        if mode == "VMANUS_ANNOTATION_ASSISTED":
            bonus = sum(annotations.get(("LEFT", op), 0.0) for op in ls) + sum(annotations.get(("RIGHT", op), 0.0) for op in rs)
        score = math.log1p(recurrence) + bonus
        return (-score, len(ls) + len(rs), -len(host), ls, rs, host)

    host, ls, rs = min(states, key=rank)
    return {"inferred_host": host or "EMPTY", "outer_left": ls[0] if ls else "NONE",
            "local_left": ls[1] if len(ls) > 1 else "NONE", "right_outer": rs[0] if rs else "NONE",
            "right_inner": rs[1] if len(rs) > 1 else "NONE", "operation_count": len(ls) + len(rs)}


def compiler_signature(row: dict) -> str:
    return "|".join(str(row[x]) for x in ("outer_left", "local_left", "right_inner", "right_outer"))


def lines_for(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        out[str(row["physical_line_id"])].append(row)
    for line in out.values():
        line.sort(key=lambda x: int(x["group_index"]))
    return out


def held_gain(rows: list[dict], endpoint: str) -> dict:
    lines = lines_for(rows); events = []
    for line in lines.values():
        for i, row in enumerate(line):
            if endpoint == "NEXT_HOST":
                if i + 1 < len(line): events.append((row, str(line[i + 1]["inferred_host"]), 1.0))
            else:
                others = Counter(str(x["inferred_host"]) for j, x in enumerate(line) if j != i)
                total = sum(others.values())
                for target, n in others.items(): events.append((row, target, n / total))
    vocab = {target for _, target, _ in events}; gt = Counter(); gn = 0.0
    nt, nn, ht, hn = Counter(), Counter(), Counter(), Counter()
    ft, fn, fnt, fnn, fht, fhn = defaultdict(Counter), Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for row, target, weight in events:
        fold = int(row["layout_folio_ordinal"]); nk = (int(row["group_index"]), int(row["line_ordinal_on_folio"]) % 3, int(row["group_count"])); host = str(row["inferred_host"])
        gt[target] += weight; gn += weight; nt[nk, target] += weight; nn[nk] += weight; ht[host, target] += weight; hn[host] += weight
        ft[fold][target] += weight; fn[fold] += weight; fnt[fold][nk, target] += weight; fnn[fold][nk] += weight; fht[fold][host, target] += weight; fhn[fold][host] += weight
    gains = Counter()
    for row, target, weight in events:
        fold = int(row["layout_folio_ordinal"]); nk = (int(row["group_index"]), int(row["line_ordinal_on_folio"]) % 3, int(row["group_count"])); host = str(row["inferred_host"])
        q = (gt[target] - ft[fold][target] + .5) / (gn - fn[fold] + .5 * len(vocab))
        base = (nt[nk, target] - fnt[fold][nk, target] + ALPHA * q) / (nn[nk] - fnn[fold][nk] + ALPHA)
        hp = (ht[host, target] - fht[fold][host, target] + BETA * base) / (hn[host] - fhn[fold][host] + BETA)
        gains[fold] += weight * math.log2(hp / base)
    return {"endpoint": endpoint, "gain_bits": sum(gains.values()), "positive_content_folios": sum(x > 0 for x in gains.values()),
            "content_folios": len(gains), "event_rows": len(events)}


def short_and_substitution(rows: list[dict]) -> tuple[dict, dict, dict]:
    freq = Counter(str(x["inferred_host"]) for x in rows); hosts = sorted(freq)
    short_mass = sum(n for h, n in freq.items() if len(h) in (2, 3)) / len(rows)
    patterns = defaultdict(list)
    for host in hosts:
        if len(host) not in (2, 3):
            continue
        for i in range(len(host)):
            patterns[len(host), i, host[:i] + "_" + host[i + 1:]].append(host)
    edges = set()
    for values in patterns.values():
        edges.update(itertools.combinations(sorted(set(values)), 2))
    same = defaultdict(Counter); external = defaultdict(Counter)
    for row in rows: same[str(row["inferred_host"])][compiler_signature(row)] += 1
    for line in lines_for(rows).values():
        for i, row in enumerate(line):
            for j in range(max(0, i - 2), min(len(line), i + 3)):
                if j != i: external[str(row["inferred_host"])][str(line[j]["inferred_host"])] += 1

    def cosine(a: Counter, b: Counter) -> float:
        dot = sum(v * b.get(k, 0.0) for k, v in a.items()); na = math.sqrt(sum(v * v for v in a.values())); nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def delta_score(profiles: dict[str, Counter]) -> dict:
        classes = defaultdict(list)
        for a, b in edges:
            diffs = [i for i in range(len(a)) if a[i] != b[i]]
            if len(diffs) != 1: continue
            i = diffs[0]; delta = Counter(profiles[b]); delta.subtract(profiles[a]); scale = sum(abs(v) for v in delta.values())
            if scale: delta = Counter({k: v / scale for k, v in delta.items() if v})
            classes[len(a), i, a[i], b[i]].append(delta)
        vals = []
        for group in classes.values():
            if len(group) >= 3: vals.extend(cosine(a, b) for a, b in itertools.combinations(group, 2))
        return {"repeated_substitution_classes": sum(len(v) >= 3 for v in classes.values()), "delta_vector_pairs": len(vals),
                "mean_delta_cosine": sum(vals) / len(vals) if vals else 0.0}

    structure = {"host_types": len(freq), "short_host_mass": short_mass, "recurrent_host_mass": sum(n for n in freq.values() if n >= 2) / len(rows),
                 "hamming1_edges": len(edges), "hamming1_density": 2 * len(edges) / max(1, len(hosts) * (len(hosts) - 1))}
    return structure, delta_score(same), delta_score(external)


def compatibility(forms: set[str], left: list[str], right: list[str], label: str) -> dict:
    left_support = {op: {h for h in forms if op + h in forms} for op in left}
    right_support = {op: {h for h in forms if h + op in forms} for op in right}
    observed = sum(bool(left_support[l] & right_support[r] & {h for h in forms if l + h + r in forms}) for l in left for r in right)
    hosts = sorted(forms); rng = random.Random(seed("GDT170_COMPAT_" + label)); null = []
    for _ in range(NULL_WORLDS):
        total = 0
        for l in left:
            ls = left_support[l]
            for r in right:
                k = len(right_support[r]); shuffled = set(rng.sample(hosts, min(k, len(hosts))))
                total += bool(ls & shuffled)
        null.append(total)
    return {"left_operations": len(left), "right_operations": len(right), "compatible_pairs": observed,
            "compatible_pair_density": observed / max(1, len(left) * len(right)), "null_mean": sum(null) / len(null),
            "inclusive_p": (1 + sum(x >= observed for x in null)) / (len(null) + 1)}


def record_metrics(rows: list[dict]) -> dict:
    ends = [x for x in rows if int(x["paragraph_end"]) and x["right_separator"] == "LINE_END"]
    nonends = [x for x in rows if x["right_separator"] != "LINE_END" or not int(x["paragraph_end"])]
    right_marked = [x for x in rows if x["right_outer"] != "NONE" or x["right_inner"] != "NONE"]
    line_ends = [x for x in rows if x["right_separator"] == "LINE_END"]
    return {"record_end_rows": len(ends), "right_marked_rows": len(right_marked),
            "right_marked_record_end_precision": sum(x in ends for x in right_marked) / max(1, len(right_marked)),
            "record_end_right_mark_recall": sum(x["right_outer"] != "NONE" or x["right_inner"] != "NONE" for x in ends) / max(1, len(ends)),
            "line_end_right_mark_recall": sum(x["right_outer"] != "NONE" or x["right_inner"] != "NONE" for x in line_ends) / max(1, len(line_ends)),
            "nonend_right_mark_rate": sum(x["right_outer"] != "NONE" or x["right_inner"] != "NONE" for x in nonends) / max(1, len(nonends))}


def host_signature(rows: list[dict], panel: list[str]) -> np.ndarray:
    acc = defaultdict(Counter)
    for row in rows:
        host = str(row["inferred_host"])
        if host not in panel: continue
        acc[host]["N"] += 1; acc[host]["P" + str(row["group_index"])] += 1
        acc[host]["L" + str(int(row["line_ordinal_on_folio"]) % 3)] += 1
        acc[host]["LEFT"] += int(row["outer_left"] != "NONE" or row["local_left"] != "NONE")
        acc[host]["RIGHT"] += int(row["right_outer"] != "NONE" or row["right_inner"] != "NONE")
    out = []
    for host in panel:
        n = acc[host]["N"]
        vec = [math.log1p(n)] + [acc[host]["P" + str(i)] / max(1, n) for i in range(1, 7)]
        vec += [acc[host]["L" + str(i)] / max(1, n) for i in range(3)]
        vec += [acc[host]["LEFT"] / max(1, n), acc[host]["RIGHT"] / max(1, n)]
        out.append(vec)
    a = np.asarray(out, float); sd = a.std(axis=0); sd[sd < 1e-12] = 1
    return (a - a.mean(axis=0)) / sd


def greedy_alignment(a: np.ndarray, b: np.ndarray) -> float:
    # Deterministic one-to-one maximum cosine matching; adequate as a blind geometry diagnostic.
    an = np.linalg.norm(a, axis=1); bn = np.linalg.norm(b, axis=1); sim = a @ b.T / np.maximum(1e-12, an[:, None] * bn[None, :])
    candidates = sorted(((float(sim[i, j]), i, j) for i in range(len(a)) for j in range(len(b))), reverse=True)
    used_i, used_j, vals = set(), set(), []
    for value, i, j in candidates:
        if i not in used_i and j not in used_j:
            used_i.add(i); used_j.add(j); vals.append(value)
            if len(vals) == min(len(a), len(b)): break
    return sum(vals) / len(vals) if vals else 0.0


def main() -> None:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_BLIND_SURFACE_PARSE"
    rows = load_rows(); by_view = defaultdict(list)
    for row in rows: by_view[str(row["world_view"]), str(row["witness_renderer"])].append(row)
    assert len(by_view) == 20 and all(len(v) == 12000 for v in by_view.values())

    parse_rows, operation_rows, diagnostic_rows = [], [], []
    parsed_by: dict[tuple[str, str, str], list[dict]] = {}
    for (world, renderer), values in sorted(by_view.items()):
        left, right, stats, envelope, counts = discover(values)
        ann = annotation_scores(values, left, right)
        selected = {("LEFT", x) for x in left} | {("RIGHT", x) for x in right}
        for item in stats:
            if (item["side"], item["operation"]) not in selected: continue
            operation_rows.append({"world_view": world, "witness_renderer": renderer, "side": item["side"], "operation": item["operation"],
                                   "selected_rank": (left.index(item["operation"]) + 1) if item["side"] == "LEFT" else (right.index(item["operation"]) + 1),
                                   "distinct_hosts": item["distinct_hosts"], "exact_pair_types": item["exact_pair_types"],
                                   "synthetic_folios": item["synthetic_folios"], "transformed_occurrences": item["transformed_occurrences"],
                                   "annotation_rank_adjustment": ann.get((item["side"], item["operation"]), 0.0)})
        token_cache = {}
        for mode in MODES:
            token_cache[mode] = {token: parse_token(token, counts, left, right, envelope, mode, ann) for token in counts}
            parsed = []
            for row in values:
                item = {"observation_id": row["observation_id"], "world_view": world, "witness_renderer": renderer,
                        "register": row["register"], "hand": row["hand"], "folio_id": row["folio_id"],
                        "layout_folio_ordinal": row["layout_folio_ordinal"], "physical_line_id": row["physical_line_id"],
                        "line_ordinal_on_folio": row["line_ordinal_on_folio"], "group_index": row["group_index"],
                        "group_count": row["group_count"], "paragraph_start": row["paragraph_start"],
                        "paragraph_end": row["paragraph_end"], "right_separator": row["right_separator"],
                        "surface_group": row["surface_group"], "parser_level": mode, **token_cache[mode][row["surface_group"]]}
                parsed.append(item); parse_rows.append(item)
            parsed_by[world, renderer, mode] = parsed
            rec = record_metrics(parsed); compat = compatibility(set(counts), left, right, world + renderer + mode)
            short, same_sub, ext_sub = short_and_substitution(parsed)
            diagnostic_rows.append({"diagnostic": "RECORD_ARCHITECTURE", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **rec})
            diagnostic_rows.append({"diagnostic": "OPERATION_COMPATIBILITY", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **compat})
            diagnostic_rows.append({"diagnostic": "SHORT_HOST_STRUCTURE", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **short})
            diagnostic_rows.append({"diagnostic": "SAME_GROUP_SUBSTITUTION", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **same_sub})
            diagnostic_rows.append({"diagnostic": "EXTERNAL_CONTEXT_SUBSTITUTION", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **ext_sub})
            diagnostic_rows.append({"diagnostic": "HELD_CONTEXT", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **held_gain(parsed, "NEXT_HOST")})
            diagnostic_rows.append({"diagnostic": "HELD_CONTEXT", "world_view": world, "witness_renderer": renderer, "parser_level": mode, **held_gain(parsed, "WHOLE_LINE")})

    # Renderer/scribe geometry, computed without string identity across views.
    worlds = sorted({x[0] for x in by_view}); renderers = sorted({x[1] for x in by_view})
    for world in worlds:
        for mode in MODES:
            base_rows = parsed_by[world, "R1_S1", mode]; base_freq = Counter(str(x["inferred_host"]) for x in base_rows)
            base_panel = [x for x, _ in base_freq.most_common(100)]; a = host_signature(base_rows, base_panel)
            for renderer in renderers:
                if renderer == "R1_S1": continue
                other_rows = parsed_by[world, renderer, mode]; other_freq = Counter(str(x["inferred_host"]) for x in other_rows)
                panel = [x for x, _ in other_freq.most_common(100)]; b = host_signature(other_rows, panel)
                diagnostic_rows.append({"diagnostic": "RENDERER_GEOMETRY_ALIGNMENT", "world_view": world, "witness_renderer": renderer,
                                        "parser_level": mode, "reference_renderer": "R1_S1", "panel_hosts": min(len(a), len(b)),
                                        "greedy_matched_mean_cosine": greedy_alignment(a, b)})

    parse_rows.sort(key=lambda x: (x["parser_level"], x["world_view"], x["witness_renderer"], int(x["layout_folio_ordinal"]), int(x["line_ordinal_on_folio"]), int(x["group_index"])))
    write_gzip(PARSES, {"schema": "GDT170_BLIND_PARSES_V1", "rows": parse_rows})
    write_tsv(OPERATIONS, operation_rows); write_tsv(DIAGNOSTICS, diagnostic_rows)
    summary = {}
    for world in worlds:
        for mode in MODES:
            rows0 = parsed_by[world, "R1_S1", mode]
            summary[world + "|" + mode] = {"inferred_host_types": len({x["inferred_host"] for x in rows0}),
                                                "mean_operation_count": sum(int(x["operation_count"]) for x in rows0) / len(rows0),
                                                "surface_exact_host_rate": sum(x["inferred_host"] == x["surface_group"] for x in rows0) / len(rows0)}
    result = {"schema": "GDT170_BLIND_INSTRUMENT_RESULT_V1", "status": "BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION",
              "counts": {"observation_rows": len(rows), "parse_rows": len(parse_rows), "operation_rows": len(operation_rows),
                         "diagnostic_rows": len(diagnostic_rows), "anonymous_worlds": len(worlds), "renderer_views": len(renderers)},
              "primary_renderer_summary": summary, "inputs": {SOURCE.name: sha(SOURCE), SOURCE_FREEZE.name: sha(SOURCE_FREEZE), DESIGN.name: sha(DESIGN)},
              "outputs": {PARSES.name: sha(PARSES), OPERATIONS.name: sha(OPERATIONS), DIAGNOSTICS.name: sha(DIAGNOSTICS)},
              "commitments": {"parse_content_sha256": csha(parse_rows), "diagnostic_content_sha256": csha(diagnostic_rows)},
              "implementation": {Path(__file__).name: sha(Path(__file__))}, "documents": {METHOD.name: sha(METHOD)},
              "blind_firewall": {"read_files": [SOURCE.name, SOURCE_FREEZE.name, DESIGN.name, METHOD.name],
                                   "forbidden_inputs_opened": False, "truth_fields_used": False, "voynich_inputs": 0, "f84r_access": False},
              "claim_ceiling": "Blind synthetic instrument outputs only; no Voynich word, code value, language, meaning, plaintext, or translation."}
    result["result_content_sha256"] = csha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
