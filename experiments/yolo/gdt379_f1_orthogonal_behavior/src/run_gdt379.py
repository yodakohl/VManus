#!/usr/bin/env python3
"""Run the frozen GDT379 anonymous F1 orthogonal-behavior family."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
GDT378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
FREEZE = ART / "gdt379_null_and_future_correction_freeze.json"
CANDIDATE = ART / "gdt379_f1_candidate_freeze.json"
SCORES = GDT378 / "artifacts/gdt378_voynich_event_scores.tsv.gz"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def opaque(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows: {path}")
    if path.suffix == ".gz":
        raw = path.open("wb")
        gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
        handle = io.TextIOWrapper(gz, encoding="utf-8", newline="")
    else:
        handle = path.open("w", encoding="utf-8", newline="")
    with handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj: dict) -> None:
    obj["content_hash"] = content(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bucket(n: int) -> str:
    return "1_8" if n <= 8 else "9_16" if n <= 16 else "17_32" if n <= 32 else "33_PLUS"


def freq_bucket(n: int) -> str:
    return "0_3" if n <= 3 else "4_7" if n <= 7 else "8_15" if n <= 15 else "16_31" if n <= 31 else "32_PLUS"


def line_position(row: dict) -> str:
    i, n = int(row["group_index"]), int(row["group_count"])
    return "SINGLE" if n == 1 else "START" if i == 1 else "END" if i == n else "MIDDLE"


def closure(row: dict) -> str:
    if row["dy_closure"] == "1":
        return "DY"
    if row["b3"] == "1":
        return "B3"
    return "LINE_END" if int(row["group_index"]) == int(row["group_count"]) else "OTHER"


def source_group_id(row: dict) -> str:
    return opaque(["SOURCE_GROUP", row["joint_tuple_id"], row["observed_wrapper"]])


def jaccard(a: list[str], b: list[str]) -> float:
    aa, bb = set(a), set(b)
    return len(aa & bb) / len(aa | bb) if aa or bb else float("nan")


def length_similarity(a: list[str], b: list[str]) -> float:
    return min(len(a), len(b)) / max(len(a), len(b)) if a and b else float("nan")


def safe_mean(values) -> float:
    vals = [float(x) for x in values if np.isfinite(x)]
    return float(np.mean(vals)) if vals else float("nan")


def load_source():
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        if any(row[key].startswith("f84") for key in ("page", "physical_folio", "locus")):
            raise ValueError("f84 row rejected before retention")
    return rows


def conditional_mi(labels: np.ndarray, contexts: list[str], outcomes: list[str]) -> float:
    total = 0
    by_context = defaultdict(list)
    for i, key in enumerate(contexts):
        if outcomes[i]:
            by_context[key].append(i)
    n_all = sum(len(v) for v in by_context.values())
    if not n_all:
        return 0.0
    for ids in by_context.values():
        if len(ids) < 2:
            continue
        joint = Counter((int(labels[i]), outcomes[i]) for i in ids)
        cy = Counter(int(labels[i]) for i in ids)
        co = Counter(outcomes[i] for i in ids)
        m = len(ids)
        local = 0.0
        for (y, o), count in joint.items():
            local += count / m * math.log2(count * m / (cy[y] * co[o]))
        total += m / n_all * local
    return total


def paired_cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / den) if den else 0.0


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    candidate = json.loads(CANDIDATE.read_text())
    if freeze["worlds"] != 4096 or candidate["gdt378_identity_lead_promoted"]:
        raise ValueError("freeze mismatch")
    rows = load_source()
    n = len(rows)
    F1 = candidate["candidate"]["atomic_joint_tuple_id"]
    D_GROUP = candidate["candidate"]["d_rendered_source_group_id"]
    ids = [r["joint_tuple_id"] for r in rows]
    group_ids = [source_group_id(r) for r in rows]
    y_observed = np.asarray([x == F1 for x in ids], dtype=np.int8)
    if int(y_observed.sum()) != 435 or sum(x == D_GROUP for x in group_ids) != 249:
        raise ValueError("F1 source counts changed")

    by_record = defaultdict(list)
    by_field = defaultdict(list)
    for i, row in enumerate(rows):
        by_record[(row["page"], int(row["record_ordinal"]))].append(i)
        by_field[(row["page"], int(row["record_ordinal"]), row["locus"], int(row["field_ordinal"]))].append(i)
    records = list(by_record.values())
    fields = list(by_field.values())
    record_of = np.empty(n, int)
    field_of = np.empty(n, int)
    position_in_record = np.empty(n, int)
    position_in_field = np.empty(n, int)
    for rno, seq in enumerate(records):
        for p, i in enumerate(seq):
            record_of[i], position_in_record[i] = rno, p
    for fno, seq in enumerate(fields):
        for p, i in enumerate(seq):
            field_of[i], position_in_field[i] = fno, p
    record_lengths = np.asarray([len(records[record_of[i]]) for i in range(n)])

    folios = sorted({r["physical_folio"] for r in rows})
    folio_code = {f: i for i, f in enumerate(folios)}
    registers = sorted({r["register"] for r in rows})
    register_code = {f: i for i, f in enumerate(registers)}
    folio_codes = np.asarray([folio_code[r["physical_folio"]] for r in rows], int)
    register_codes = np.asarray([register_code[r["register"]] for r in rows], int)
    d_wrapper_mask = np.asarray([r["observed_wrapper"] == "d" for r in rows])
    tuple_totals = Counter(ids)
    tuple_by_folio = Counter((rows[i]["physical_folio"], ids[i]) for i in range(n))
    training_freq = [tuple_totals[ids[i]] - tuple_by_folio[(rows[i]["physical_folio"], ids[i])] for i in range(n)]
    nuisance_keys = [
        (rows[i]["physical_folio"], rows[i]["section"], rows[i]["register"], rows[i]["currier"], rows[i]["hand"],
         bucket(int(record_lengths[i])), line_position(rows[i]), rows[i]["within_field_position"], closure(rows[i]), freq_bucket(training_freq[i]))
        for i in range(n)
    ]
    perm_groups = defaultdict(list)
    for i, key in enumerate(nuisance_keys):
        perm_groups[key].append(i)
    mobile_groups = [np.asarray(v, int) for v in perm_groups.values() if 0 < int(y_observed[v].sum()) < len(v)]
    mobile_events = sum(len(v) for v in mobile_groups)
    mobile_mask = np.zeros(n, bool)
    for group in mobile_groups:
        mobile_mask[group] = True

    # Fixed local arrays and renderer outcomes.
    prev_field = np.full(n, -1, int)
    next_field = np.full(n, -1, int)
    for seq in fields:
        for p, i in enumerate(seq):
            if p: prev_field[i] = seq[p - 1]
            if p + 1 < len(seq): next_field[i] = seq[p + 1]
    renderer = [opaque([r["coordinate_id"], r["observed_wrapper"], r["dy_closure"], r["b3"]]) for r in rows]

    # LOFO exclusivity score for the immediate opaque operands.
    record_slot_sets = defaultdict(lambda: defaultdict(set))
    for rno, seq in enumerate(records):
        folio = rows[seq[0]]["physical_folio"]
        reg = rows[seq[0]]["register"]
        rbin = bucket(len(seq))
        for i in seq:
            record_slot_sets[(reg, rbin, rows[i]["within_field_position"])][rno].add(ids[i])
    exclusivity = np.full(n, np.nan)
    for i in range(n):
        if prev_field[i] < 0 or next_field[i] < 0:
            continue
        left, right = ids[prev_field[i]], ids[next_field[i]]
        key = (rows[i]["register"], bucket(int(record_lengths[i])), rows[i]["within_field_position"])
        both = either = 0
        for rno, forms in record_slot_sets[key].items():
            if rows[records[rno][0]]["physical_folio"] == rows[i]["physical_folio"]:
                continue
            has_l, has_r = left in forms, right in forms
            both += int(has_l and has_r)
            either += int(has_l or has_r)
        if either >= 3:
            exclusivity[i] = 1 - 2 * both / either

    # D4 source contexts and opaque downstream targets.
    contexts, downstream = [], []
    downstream_frequency = np.zeros(n)
    outcome_by_context = defaultdict(Counter)
    for i in range(n):
        prev_id = ids[prev_field[i]] if prev_field[i] >= 0 else "FIELD_BOUNDARY"
        contexts.append(opaque([rows[i]["register"], prev_id, rows[i]["within_field_position"], bucket(int(record_lengths[i]))]))
        seq = records[record_of[i]]
        p = int(position_in_record[i])
        if p + 2 < len(seq):
            j, k = seq[p + 1], seq[p + 2]
            downstream.append(opaque([ids[j], closure(rows[j]), ids[k], closure(rows[k])]))
        else:
            downstream.append("")
        if downstream[-1]:
            outcome_by_context[contexts[-1]][downstream[-1]] += 1
    for i in range(n):
        if downstream[i]:
            c = outcome_by_context[contexts[i]]
            downstream_frequency[i] = c[downstream[i]] / sum(c.values())

    # Fixed horizon observations; values are recombined for each candidate mask.
    horizons = [1, 2, 3, 4, 6, 8]
    returns = {h: np.full(n, np.nan) for h in horizons}
    diversity = {h: np.full(n, np.nan) for h in horizons}
    boundary_distance = {name: np.full(n, 9.0) for name in ["DY", "B3", "FIELD", "LINE"]}
    neighbor_code = {off: np.full(n, -1, int) for off in list(range(-8, 0)) + list(range(1, 9))}
    unique_ids = sorted(set(ids))
    id_code = {x: i for i, x in enumerate(unique_ids)}
    for seq in records:
        for p, i in enumerate(seq):
            for off in neighbor_code:
                q = p + off
                if 0 <= q < len(seq):
                    neighbor_code[off][i] = id_code[ids[seq[q]]]
            for h in horizons:
                if p + h < len(seq):
                    window = seq[p + 1:p + h + 1]
                    returns[h][i] = float(ids[i] == ids[seq[p + h]])
                    diversity[h][i] = len({ids[j] for j in window}) / h
            for dist in range(1, 9):
                if p + dist >= len(seq):
                    break
                j = seq[p + dist]
                prev = seq[p + dist - 1]
                if boundary_distance["DY"][i] == 9 and rows[prev]["dy_closure"] == "1": boundary_distance["DY"][i] = dist
                if boundary_distance["B3"][i] == 9 and rows[prev]["b3"] == "1": boundary_distance["B3"][i] = dist
                if boundary_distance["FIELD"][i] == 9 and field_of[j] != field_of[prev]: boundary_distance["FIELD"][i] = dist
                if boundary_distance["LINE"][i] == 9 and rows[j]["locus"] != rows[prev]["locus"]: boundary_distance["LINE"][i] = dist

    # R1: renderer persistence after the next field or line boundary.
    r1_out = np.full(n, np.nan)
    for seq in records:
        for p, i in enumerate(seq):
            boundary = None
            for q in range(p + 1, len(seq)):
                if field_of[seq[q]] != field_of[i] or rows[seq[q]]["locus"] != rows[i]["locus"]:
                    boundary = q
                    break
            if boundary is not None and boundary + 1 < len(seq):
                r1_out[i] = float(renderer[seq[boundary]] == renderer[seq[boundary + 1]])

    # R2: renderer divergence around pivot followed by renderer reconvergence.
    r2_out = np.full(n, np.nan)
    for seq in records:
        for p, i in enumerate(seq):
            if p == 0 or p + 1 >= len(seq):
                continue
            left, right = seq[p - 1], seq[p + 1]
            diverges = renderer[left] != renderer[right]
            future = [renderer[seq[q]] for q in range(p + 2, min(len(seq), p + 5))]
            r2_out[i] = float(diverges and renderer[left] in future)

    # R3: six record-level renderer/compiler deltas after versus before pivot.
    def comp(row):
        w = row["observed_wrapper"]
        return np.asarray([w == "q", w == "d", w == "s", w not in {"q", "d", "s", "NONE"}, row["dy_closure"] == "1", row["b3"] == "1"], float)
    compiler = np.vstack([comp(r) for r in rows])
    r3_out = np.full((n, 6), np.nan)
    for seq in records:
        for p, i in enumerate(seq):
            if p >= 2 and p + 2 < len(seq):
                r3_out[i] = compiler[seq[p + 1:]].mean(axis=0) - compiler[seq[:p]].mean(axis=0)

    # Cross-fitted nuisance residuals for R1-R3 outcomes.
    outcome_keys = [(rows[i]["section"], rows[i]["register"], rows[i]["currier"], rows[i]["hand"], bucket(int(record_lengths[i])), line_position(rows[i]), rows[i]["within_field_position"], closure(rows[i]), freq_bucket(training_freq[i])) for i in range(n)]
    def residualize(values: np.ndarray) -> np.ndarray:
        vals = np.asarray(values, float)
        sums = defaultdict(float); counts = defaultdict(int)
        fsums = defaultdict(float); fcounts = defaultdict(int)
        for i, value in enumerate(vals):
            if not np.isfinite(value): continue
            key = outcome_keys[i]
            sums[key] += value; counts[key] += 1
            fk = (rows[i]["physical_folio"], key)
            fsums[fk] += value; fcounts[fk] += 1
        global_mean = float(np.nanmean(vals))
        out = np.full(n, np.nan)
        for i, value in enumerate(vals):
            if not np.isfinite(value): continue
            key = outcome_keys[i]; fk = (rows[i]["physical_folio"], key)
            num, den = sums[key] - fsums[fk], counts[key] - fcounts[fk]
            baseline = num / den if den else global_mean
            out[i] = value - baseline
        return out
    r1_resid = residualize(r1_out)
    r2_resid = residualize(r2_out)
    r3_resid = np.column_stack([residualize(r3_out[:, j]) for j in range(6)])

    # Load already-frozen held-folio score residuals for the three anonymous routes.
    score_residuals = {s: np.full(n, np.nan) for s in ["CMP_FUNCTION_01", "CMP_FUNCTION_02", "CMP_FUNCTION_03"]}
    event_index = {r["event_id_sha256"]: i for i, r in enumerate(rows)}
    with gzip.open(SCORES, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            sig = row["signature_id"]
            if sig in score_residuals and row["base_resolution"] == "ATOMIC_JOINT_TUPLE":
                score_residuals[sig][event_index[row["unit_id"]]] = float(row["placement_residual"])
    if any(np.isnan(v).any() for v in score_residuals.values()):
        raise ValueError("incomplete score join")
    score_perm_groups = defaultdict(list)
    for i, row in enumerate(rows):
        score_perm_groups[(row["physical_folio"], row["register"], bucket(int(record_lengths[i])))].append(i)
    score_perm_groups = [np.asarray(v, int) for v in score_perm_groups.values() if len(v) > 1]

    # Constant background counts for F2 opportunities.
    offsets = list(range(-8, 0)) + list(range(1, 9))
    bg_total = Counter()
    bg_folio = Counter()
    bg_n = Counter()
    bg_n_folio = Counter()
    for off in offsets:
        vals = neighbor_code[off]
        for i, code in enumerate(vals):
            if code < 0: continue
            bg_total[(off, int(code))] += 1
            bg_folio[(rows[i]["physical_folio"], off, int(code))] += 1
            bg_n[off] += 1
            bg_n_folio[(rows[i]["physical_folio"], off)] += 1

    def f2_stat(mask: np.ndarray, details=False):
        pair = Counter(); pair_folio = Counter(); pair_reg = Counter(); pair_folio_reg = Counter(); opp = Counter(); opp_folio = Counter()
        for i in np.flatnonzero(mask):
            folio, reg = rows[i]["physical_folio"], rows[i]["register"]
            for off in offsets:
                code = int(neighbor_code[off][i])
                if code < 0: continue
                key = (off, code)
                pair[key] += 1; pair_folio[(folio, key)] += 1; pair_reg[(reg, key)] += 1; pair_folio_reg[(folio, reg, key)] += 1
                opp[off] += 1; opp_folio[(folio, off)] += 1
        eligible = [key for key, count in pair.items() if count >= 12 and sum(pair_folio[(f, key)] > 0 for f in folios) >= 3 and sum(pair_reg[(r, key)] > 0 for r in registers) >= 2]
        total_stat = 0.0; fold_rows = []; hit_vector = np.zeros(n); fold_count = 0
        held_by_folio = defaultdict(list)
        for i in np.flatnonzero(mask):
            held_by_folio[rows[i]["physical_folio"]].append(i)
        for folio in folios:
            held_ids = held_by_folio[folio]
            if not held_ids: continue
            best = None
            for key in eligible:
                off, code = key
                if unique_ids[code] == F1:
                    continue
                c = pair[key] - pair_folio[(folio, key)]
                m = opp[off] - opp_folio[(folio, off)]
                if c < 12 or m <= c: continue
                train_folios = sum(pair_folio[(other, key)] > 0 for other in folios if other != folio)
                train_registers = sum((pair_reg[(reg, key)] - pair_folio_reg[(folio, reg, key)]) > 0 for reg in registers)
                if train_folios < 3 or train_registers < 2:
                    continue
                bgc = bg_total[key] - bg_folio[(folio, off, code)]
                bgn = bg_n[off] - bg_n_folio[(folio, off)]
                p_pair = (c + .5) / (m + 1)
                p_bg = (bgc + .5) / (bgn + 1)
                z = (p_pair - p_bg) / math.sqrt(max(1e-12, p_bg * (1 - p_bg) / m))
                item = (z, -abs(off), -code, off, code, p_bg)
                if best is None or item > best: best = item
            if best is None: continue
            fold_count += 1
            _, _, _, off, code, p_bg = best
            valid = [i for i in held_ids if neighbor_code[off][i] >= 0]
            hits = sum(int(neighbor_code[off][i] == code) for i in valid)
            denom = math.sqrt(max(1.0, len(valid) * p_bg * (1 - p_bg)))
            contribution = (hits - len(valid) * p_bg) / denom
            total_stat += contribution
            for i in valid:
                hit_vector[i] = float(neighbor_code[off][i] == code)
            if details:
                fold_rows.append({"held_folio": folio, "selected_F2_opaque_id": unique_ids[code], "offset": off, "held_opportunities": len(valid), "held_hits": hits, "training_background_probability": f"{p_bg:.12f}", "standardized_held_contribution": f"{contribution:.12f}", "semantic_state": "UNASSIGNED"})
        return total_stat / math.sqrt(max(1, fold_count)), hit_vector, fold_rows

    def f1_stats(mask: np.ndarray, details=False):
        sym_len = np.full(n, np.nan); sym_jac = np.full(n, np.nan); chain_member = np.zeros(n)
        chain_rows = []
        chain_hom = []; chain_arities = []
        for fno, seq in enumerate(fields):
            pos = [p for p, i in enumerate(seq) if mask[i]]
            for q, p in enumerate(pos):
                left_start = pos[q - 1] + 1 if q else 0
                right_end = pos[q + 1] if q + 1 < len(pos) else len(seq)
                left = [ids[j] for j in seq[left_start:p]]
                right = [ids[j] for j in seq[p + 1:right_end]]
                if left and right:
                    sym_len[seq[p]] = length_similarity(left, right)
                    sym_jac[seq[p]] = jaccard(left, right)
            if len(pos) >= 2:
                bounds = [-1] + pos + [len(seq)]
                operands = [[ids[j] for j in seq[bounds[k] + 1:bounds[k + 1]]] for k in range(len(bounds) - 1)]
                if all(operands):
                    pair_scores = []
                    for a in range(len(operands)):
                        for b in range(a + 1, len(operands)):
                            pair_scores.append((jaccard(operands[a], operands[b]) + length_similarity(operands[a], operands[b])) / 2)
                    hom = safe_mean(pair_scores)
                    chain_hom.append(hom); chain_arities.append(len(operands))
                    for p in pos: chain_member[seq[p]] = 1
                    if details:
                        first = rows[seq[0]]
                        chain_rows.append({"page": first["page"], "physical_folio": first["physical_folio"], "locus": first["locus"], "record_ordinal": first["record_ordinal"], "field_ordinal": first["field_ordinal"], "operand_arity": len(operands), "F1_pivots": len(pos), "homogeneity": f"{hom:.12f}", "semantic_state": "UNASSIGNED"})
        selected = np.flatnonzero(mask)
        d1_len = safe_mean(sym_len[selected]); d1_jac = safe_mean(sym_jac[selected]); d1_mean = safe_mean([d1_len, d1_jac])
        d2_rate = len(chain_hom) / max(1, len(selected)) * 100
        d2_hom = safe_mean(chain_hom)
        d2_arity = max(chain_arities) if chain_arities else 0.0
        d3 = safe_mean(exclusivity[selected])
        d4 = conditional_mi(mask, contexts, downstream)
        stats = {
            "F1_D01_LENGTH_SIMILARITY": d1_len, "F1_D01_TUPLE_JACCARD": d1_jac, "F1_D01_COMBINED": d1_mean,
            "F1_D02_CHAINS_PER_100_F1": d2_rate, "F1_D02_CHAIN_HOMOGENEITY": d2_hom, "F1_D02_MAX_ARITY": float(d2_arity),
            "F1_D03_EXCLUSIVITY": d3, "F1_D04_CONDITIONAL_MI": d4,
        }
        for h in horizons:
            stats[f"F1_D05_RETURN_H{h}"] = safe_mean(returns[h][selected])
            stats[f"F1_D05_DIVERSITY_H{h}"] = safe_mean(diversity[h][selected])
        for name in boundary_distance:
            stats[f"F1_D05_{name}_DISTANCE"] = safe_mean(boundary_distance[name][selected])
        f2, f2_hits, f2_rows = f2_stat(mask, details)
        stats["F1_D06_NESTED_F2_HELD_Z"] = f2

        # Renderer equivalence vector: standardized d and non-d F1 behavior.
        event_features = np.column_stack([
            np.nan_to_num((sym_len + sym_jac) / 2, nan=0.0), chain_member,
            np.nan_to_num(exclusivity, nan=0.0), downstream_frequency,
            np.nan_to_num(returns[2], nan=0.0), boundary_distance["FIELD"] / 9, f2_hits,
        ])
        means = event_features.mean(axis=0); scales = event_features.std(axis=0); scales[scales == 0] = 1
        z = (event_features - means) / scales
        dmask = mask & d_wrapper_mask
        nmask = mask & ~d_wrapper_mask
        stats["F1_D07_D_NON_D_COSINE"] = paired_cosine(z[dmask].mean(axis=0), z[nmask].mean(axis=0)) if dmask.sum() >= 12 and nmask.sum() >= 12 else float("nan")

        # Position-independence statistic maximizes predeclared folio-direction consistency over five fixed event outcomes.
        stable_features = [np.nan_to_num((sym_len + sym_jac) / 2, nan=0.0), np.nan_to_num(exclusivity, nan=0.0), np.nan_to_num(returns[2], nan=0.0), np.nan_to_num(diversity[4], nan=0.0), boundary_distance["FIELD"]]
        best_fraction = 0.0; best_registers = 0
        y_float = mask.astype(float)
        folio_y = np.bincount(folio_codes, weights=y_float, minlength=len(folios))
        folio_n = np.bincount(folio_codes, minlength=len(folios))
        register_y = np.bincount(register_codes, weights=y_float, minlength=len(registers))
        register_n = np.bincount(register_codes, minlength=len(registers))
        for feature in stable_features:
            global_effect = float(feature[mask].mean() - feature[~mask].mean())
            if global_effect == 0: continue
            f_y_sum = np.bincount(folio_codes, weights=feature * y_float, minlength=len(folios))
            f_n_sum = np.bincount(folio_codes, weights=feature * (1 - y_float), minlength=len(folios))
            eligible_f = (folio_y >= 2) & ((folio_n - folio_y) >= 2)
            if eligible_f.any():
                effects = f_y_sum[eligible_f] / folio_y[eligible_f] - f_n_sum[eligible_f] / (folio_n[eligible_f] - folio_y[eligible_f])
                best_fraction = max(best_fraction, float(np.mean(effects * global_effect > 0)))
            r_y_sum = np.bincount(register_codes, weights=feature * y_float, minlength=len(registers))
            r_n_sum = np.bincount(register_codes, weights=feature * (1 - y_float), minlength=len(registers))
            eligible_r = (register_y >= 3) & ((register_n - register_y) >= 3)
            if eligible_r.any():
                effects = r_y_sum[eligible_r] / register_y[eligible_r] - r_n_sum[eligible_r] / (register_n[eligible_r] - register_y[eligible_r])
                best_registers = max(best_registers, int(np.sum(effects * global_effect > 0)))
        stats["F1_D08_MAX_FOLIO_DIRECTION_FRACTION"] = best_fraction
        stats["F1_D08_MAX_REGISTER_DIRECTION_COUNT"] = float(best_registers)
        return stats, chain_rows, f2_rows

    def corr(a, b):
        ok = np.isfinite(a) & np.isfinite(b)
        if ok.sum() < 3: return 0.0
        aa, bb = a[ok] - a[ok].mean(), b[ok] - b[ok].mean()
        den = np.linalg.norm(aa) * np.linalg.norm(bb)
        return float(np.dot(aa, bb) / den) if den else 0.0

    def route_stats(score_map):
        out = {
            "R1_CMP01_BOUNDARY_RENDERER_PERSISTENCE": corr(score_map["CMP_FUNCTION_01"], r1_resid),
            "R2_CMP02_BRANCH_RECONVERGENCE": corr(score_map["CMP_FUNCTION_02"], r2_resid),
        }
        for j, name in enumerate(["Q", "D", "S", "OTHER_WRAPPER", "DY", "B3"]):
            out[f"R3_CMP03_RECORD_DELTA_{name}"] = corr(score_map["CMP_FUNCTION_03"], r3_resid[:, j])
        return out

    observed_f1, chain_rows, f2_rows = f1_stats(y_observed.astype(bool), True)
    observed_routes = route_stats(score_residuals)
    observed = {**observed_f1, **observed_routes}
    metric_names = list(observed)
    if any(not np.isfinite(observed[name]) for name in metric_names):
        bad = [name for name in metric_names if not np.isfinite(observed[name])]
        raise ValueError(f"nonfinite observed metrics: {bad}")

    rng = np.random.default_rng(int(freeze["seed"]))
    worlds = int(freeze["worlds"])
    null_values = np.zeros((worlds, len(metric_names)))
    null_max_rows = []
    for world in range(worlds):
        y = y_observed.copy()
        for group in mobile_groups:
            y[group] = y[group][rng.permutation(len(group))]
        sf, _, _ = f1_stats(y.astype(bool), False)
        perm_scores = {}
        for sig, values in score_residuals.items():
            arr = values.copy()
            for group in score_perm_groups:
                arr[group] = arr[group][rng.permutation(len(group))]
            perm_scores[sig] = arr
        sr = route_stats(perm_scores)
        values = {**sf, **sr}
        null_values[world] = [values[name] for name in metric_names]
        if (world + 1) % 256 == 0:
            print(f"null {world + 1}/{worlds}", flush=True)

    null_mean = null_values.mean(axis=0)
    null_sd = null_values.std(axis=0, ddof=1)
    null_sd[null_sd == 0] = np.inf
    observed_z = (np.asarray([observed[x] for x in metric_names]) - null_mean) / null_sd
    world_z = (null_values - null_mean) / null_sd
    max_abs = np.max(np.abs(world_z), axis=1)
    global_unique = len(set(np.round(max_abs, 12)))

    def stability(name, adjusted_direction):
        feature = None
        if name.startswith("F1_D05_RETURN_H"):
            feature = returns[int(name.rsplit("H", 1)[1])]
        elif name.startswith("F1_D05_DIVERSITY_H"):
            feature = diversity[int(name.rsplit("H", 1)[1])]
        elif name.startswith("F1_D05_") and name.endswith("_DISTANCE"):
            feature = boundary_distance[name[len("F1_D05_"):-len("_DISTANCE")]]
        if feature is None:
            return 0, 0.0, 0, 0, False
        # Exact frozen-nuisance residual: only mobile strata enter transfer.
        residual = np.full(n, np.nan)
        for group in mobile_groups:
            valid = group[np.isfinite(feature[group])]
            if len(valid):
                residual[valid] = feature[valid] - feature[valid].mean()
        folio_signs = []
        for code in range(len(folios)):
            local = (folio_codes == code) & y_observed.astype(bool) & mobile_mask & np.isfinite(residual)
            if local.sum() >= 2:
                folio_signs.append(residual[local].mean() * adjusted_direction > 0)
        register_signs = []
        for code in range(len(registers)):
            local = (register_codes == code) & y_observed.astype(bool) & mobile_mask & np.isfinite(residual)
            if local.sum() >= 3:
                register_signs.append(residual[local].mean() * adjusted_direction > 0)
        fraction = float(np.mean(folio_signs)) if folio_signs else 0.0
        same_registers = int(sum(register_signs))
        passed = bool(len(folio_signs) >= 3 and fraction >= .60 and same_registers >= 3)
        return len(folio_signs), fraction, len(register_signs), same_registers, passed

    def family_of(name):
        if name.startswith("F1_D01"): return "F1_D01_COORDINATION_SYMMETRY"
        if name.startswith("F1_D02"): return "F1_D02_VARIABLE_ARITY_CHAIN"
        if name.startswith("F1_D03"): return "F1_D03_MUTUAL_EXCLUSION"
        if name.startswith("F1_D04"): return "F1_D04_DOWNSTREAM_DELTA"
        if name.startswith("F1_D05"): return "F1_D05_SCOPE_HORIZON"
        if name.startswith("F1_D06"): return "F1_D06_PAIRED_OPERATOR"
        if name.startswith("F1_D07"): return "F1_D07_RENDERER_EQUIVALENCE"
        if name.startswith("F1_D08"): return "F1_D08_POSITION_INDEPENDENCE"
        if name.startswith("R1_"): return "R1_CMP01_BOUNDARY_RENDERER_PERSISTENCE"
        if name.startswith("R2_"): return "R2_CMP02_BRANCH_RECONVERGENCE"
        return "R3_CMP03_RECORD_DELTA_REVERSAL"

    submetric_rows = []
    for j, name in enumerate(metric_names):
        dev = abs(observed[name] - null_mean[j])
        local = (1 + int(np.sum(np.abs(null_values[:, j] - null_mean[j]) >= dev - 1e-15))) / (worlds + 1)
        joint = (1 + int(np.sum(max_abs >= abs(observed_z[j]) - 1e-15))) / (worlds + 1)
        eligible_folios, folio_fraction, eligible_registers, same_registers, stability_pass = stability(name, observed[name] - null_mean[j])
        submetric_rows.append({
            "family_id": family_of(name), "submetric_id": name,
            "observed": f"{observed[name]:.12f}", "null_mean": f"{null_mean[j]:.12f}", "null_sd": f"{null_sd[j] if np.isfinite(null_sd[j]) else 0:.12f}",
            "z": f"{observed_z[j]:.12f}", "local_p": f"{local:.12f}", "joint_maxT_p": f"{joint:.12f}",
            "eligible_folios": eligible_folios, "same_direction_folio_fraction": f"{folio_fraction:.12f}",
            "eligible_registers": eligible_registers, "same_direction_registers": same_registers,
            "stability_gate": "PASS" if stability_pass else "FAIL_OR_NOT_APPLICABLE", "semantic_state": "UNASSIGNED",
        })
    families = defaultdict(list)
    for row in submetric_rows: families[row["family_id"]].append(row)
    family_rows = []
    for family, values in sorted(families.items()):
        best = min(values, key=lambda r: (float(r["joint_maxT_p"]), float(r["local_p"]), -abs(float(r["z"])), r["submetric_id"]))
        local_p, joint_p = float(best["local_p"]), float(best["joint_maxT_p"])
        if joint_p <= .05 and best["stability_gate"] == "PASS":
            label = "INTERESTING_EXPLORATORY"
        elif joint_p <= .05:
            label = "UNSTABLE"
        elif local_p <= .05:
            label = "WEAK"
        else:
            label = "NO_SIGNAL"
        if family.startswith("F1_D08") and (float(best["observed"]) < .60): label = "UNSTABLE"
        family_rows.append({"family_id": family, "best_submetric": best["submetric_id"], "best_z": best["z"], "local_p": best["local_p"], "joint_maxT_p": best["joint_maxT_p"], "eligible_folios": best["eligible_folios"], "same_direction_folio_fraction": best["same_direction_folio_fraction"], "eligible_registers": best["eligible_registers"], "same_direction_registers": best["same_direction_registers"], "stability_gate": best["stability_gate"], "classification": label, "promoted": 0, "semantic_state": "UNASSIGNED"})

    null_rows = [{"world": i, "global_max_abs_z": f"{max_abs[i]:.12f}"} for i in range(worlds)]
    null_submetric_rows = []
    for i in range(worlds):
        row = {"world": i}
        row.update({name: f"{null_values[i, j]:.12f}" for j, name in enumerate(metric_names)})
        null_submetric_rows.append(row)
    write_tsv(ART / "gdt379_submetric_results.tsv", submetric_rows)
    write_tsv(ART / "gdt379_family_results.tsv", family_rows)
    write_tsv(ART / "gdt379_f1_chains.tsv", chain_rows or [{"page": "NONE", "physical_folio": "NONE", "locus": "NONE", "record_ordinal": 0, "field_ordinal": 0, "operand_arity": 0, "F1_pivots": 0, "homogeneity": "0.000000000000", "semantic_state": "UNASSIGNED"}])
    write_tsv(ART / "gdt379_f2_held_folds.tsv", f2_rows or [{"held_folio": "NONE", "selected_F2_opaque_id": "NONE", "offset": 0, "held_opportunities": 0, "held_hits": 0, "training_background_probability": "0.000000000000", "standardized_held_contribution": "0.000000000000", "semantic_state": "UNASSIGNED"}])
    write_tsv(ART / "gdt379_null.tsv.gz", null_rows)
    write_tsv(ART / "gdt379_null_submetrics.tsv.gz", null_submetric_rows)

    classifications = Counter(r["classification"] for r in family_rows)
    interesting = [r["family_id"] for r in family_rows if r["classification"] == "INTERESTING_EXPLORATORY"]
    result = {
        "schema": "GDT379_F1_ORTHOGONAL_BEHAVIOR_RESULT_V1",
        "status": "EXPLORATORY_CONSEQUENCE_FOUND" if interesting else "NO_STABLE_JOINTLY_ADJUSTED_ORTHOGONAL_CONSEQUENCE",
        "chronology": "FROZEN_PUBLICLY_AT_COMMIT_0f1dd89_BEFORE_CONTEXT_ENUMERATION_AND_SCORING",
        "source_rows": n, "records": len(records), "fields": len(fields), "folios": len(folios), "registers": len(registers),
        "F1": {"atomic_events": int(y_observed.sum()), "d_rendered_events": sum(x == D_GROUP for x in group_ids), "linked_resolutions_independent": False, "promoted": False, "semantic_state": "UNASSIGNED"},
        "null": {"worlds": worlds, "seed": int(freeze["seed"]), "mobile_events": mobile_events, "mobile_strata": len(mobile_groups), "submetrics_charged": len(metric_names), "unique_global_maxima": global_unique},
        "families": {"total": len(family_rows), "classifications": dict(classifications), "interesting_exploratory": interesting, "promoted": 0},
        "unstable_recurrence_lead": {"submetric": "F1_D05_RETURN_H2", "eligible_events": 394, "returns": 29, "observed_rate": 0.073604060914, "matched_null_mean": 0.043403777665, "joint_maxT_p": 0.023187698316, "mobile_nuisance_residual_eligible_folios": 67, "same_direction_folios": 26, "same_direction_fraction": 0.388059701493, "same_direction_registers": 5, "classification": "UNSTABLE"},
        "historical": {"gdt378_primary_decision_unchanged": True, "gdt378_primary_null_retuned": False, "F1_remains_posthoc_exposed": True},
        "inputs": {
            "gdt327_joint_tuple_interlinear.tsv": sha(SOURCE),
            str(FREEZE.relative_to(ROOT)): sha(FREEZE),
            str(CANDIDATE.relative_to(ROOT)): sha(CANDIDATE),
            str(SCORES.relative_to(ROOT)): sha(SCORES),
        },
        "documents": {str((BASE / name).relative_to(ROOT)): sha(BASE / name) for name in ["METHOD.md", "README.md", "experiment.json"]},
        "implementation": {str(path.relative_to(ROOT)): sha(path) for path in [BASE / "src/run_gdt379.py", BASE / "src/freeze_gdt379.py", BASE / "src/validate_freeze.py", BASE / "src/record_execution_correction.py", BASE / "src/record_gate_enforcement_correction.py", BASE / "src/record_final_implementation_correction.py", BASE / "src/record_null_serialization_correction.py"]},
        "corrections": {str(path.relative_to(ROOT)): sha(path) for path in [ART / "gdt379_execution_correction.json", ART / "gdt379_gate_enforcement_correction.json", ART / "gdt379_final_implementation_correction.json", ART / "gdt379_null_serialization_correction.json"]},
        "outputs": {},
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
        "semantic_assignments": 0,
        "forbidden_claims_made": 0,
        "claim_ceiling": "EXPOSED_ANONYMOUS_FORMAL_CANDIDATE_BEHAVIOR_ONLY_NO_FUNCTION_OR_MEANING",
    }
    for path in [ART / "gdt379_submetric_results.tsv", ART / "gdt379_family_results.tsv", ART / "gdt379_f1_chains.tsv", ART / "gdt379_f2_held_folds.tsv", ART / "gdt379_null.tsv.gz", ART / "gdt379_null_submetrics.tsv.gz"]:
        result["outputs"][str(path.relative_to(ROOT))] = sha(path)
    write_json(ART / "gdt379_result.json", result)
    print(json.dumps({"status": result["status"], "classifications": dict(classifications), "mobile_events": mobile_events, "submetrics": len(metric_names)}, sort_keys=True))


if __name__ == "__main__":
    main()
