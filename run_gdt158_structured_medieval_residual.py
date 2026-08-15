#!/usr/bin/env python3
"""Score authentic medieval document boundaries against the GDT157 residual."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import multiprocessing as mp
import re
import statistics
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from run_gdt003_structural_fingerprint_comparator import evaluate_corpus
from run_gdt157_learned_abbreviation_causal import discover, parse_token

ROOT = Path(__file__).resolve().parent
BLIND = ROOT / "gdt155_blinded_diplomatic.tsv"
EXPANDED = ROOT / "gdt155_unblinded_lines.tsv"
FREEZE = ROOT / "gdt158_source_freeze.json"
GDT157_FP = ROOT / "gdt157_structural_fingerprints.tsv"
GDT003_FP = ROOT / "gdt003_structural_fingerprints.tsv"
METHOD = ROOT / "GDT158_STRUCTURED_MEDIEVAL_RESIDUAL_METHOD.md"
AUDIT = ROOT / "GDT158_STRUCTURED_CONTROL_SOURCE_AUDIT.md"
MANIFEST = ROOT / "gdt158_structured_source_manifest.tsv"

OUT_FP = ROOT / "gdt158_structural_fingerprints.tsv"
OUT_LAYOUT = ROOT / "gdt158_layout_effects.tsv"
OUT_CLOSURE = ROOT / "gdt158_closure_folds.tsv"
OUT_NULL = ROOT / "gdt158_null_results.tsv"
OUT_COUNTER = ROOT / "gdt158_counterexamples.tsv"
OUT_RESULT = ROOT / "gdt158_result.json"
OUT_REPORT = ROOT / "GDT158_STRUCTURED_MEDIEVAL_RESIDUAL_REPORT.md"

AUG_SHA = "bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
SEED = "GDT158_BOUNDARY_ROTATION_V1"
WORLDS = 4096
FOLD_MAP = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s"})


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


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
        for row in rows:
            writer.writerow({field: row.get(field, "NA") for field in fields})


def norm(value: str) -> str:
    value = unicodedata.normalize("NFC", value).translate(FOLD_MAP).lower()
    return "".join(ch for ch in value if ch.isalnum())


def tokens(value: str) -> list[str]:
    return [token for part in value.split() if (token := norm(part))]


def char3(value: str) -> set[str]:
    value = "^" + value + "$"
    return {value[i:i + 3] for i in range(max(1, len(value) - 2))}


def jaccard(left: str, right: str) -> float:
    a, b = char3(left), char3(right)
    return len(a & b) / max(1, len(a | b))


def js_counts(left: np.ndarray, right: np.ndarray) -> float:
    lt, rt = float(left.sum()), float(right.sum())
    if not lt or not rt:
        return 0.0
    p, q = left / lt, right / rt
    m = (p + q) / 2
    pmask, qmask = p > 0, q > 0
    klp = np.sum(p[pmask] * np.log2(p[pmask] / m[pmask]))
    klq = np.sum(q[qmask] * np.log2(q[qmask] / m[qmask]))
    return math.sqrt(max(0.0, float((klp + klq) / 2)))


@dataclass
class Line:
    corpus: str
    view: str
    fold: str
    parent: str
    line_id: str
    order: int
    toks: list[str]


def augsburg_lines(path: Path) -> list[Line]:
    assert sha(path) == AUG_SHA
    lines: list[Line] = []
    parent_order: Counter[str] = Counter()
    with zipfile.ZipFile(path) as archive:
        strings: list[str] = []
        for _, node in ET.iterparse(archive.open("xl/sharedStrings.xml"), events=("end",)):
            if node.tag == NS + "si":
                strings.append("".join(part.text or "" for part in node.iter(NS + "t")))
                node.clear()
        source_row = 0
        for _, node in ET.iterparse(archive.open("xl/worksheets/sheet1.xml"), events=("end",)):
            if node.tag != NS + "row":
                continue
            source_row += 1
            values: dict[str, str] = {}
            for cell in node.findall(NS + "c"):
                match = re.match(r"[A-Z]+", cell.get("r", ""))
                value_node = cell.find(NS + "v")
                value = "" if value_node is None else (value_node.text or "")
                if cell.get("t") == "s" and value:
                    value = strings[int(value)]
                if match:
                    values[match.group()] = value
            year, surface = values.get("A", ""), values.get("D", "").strip()
            if year.isdigit() and 1402 <= int(year) <= 1425 and surface:
                parent = f"AUG_{year}_{values.get('B', 'NOFOLIO')}"
                parent_order[parent] += 1
                lines.append(Line("AUGSBURG_ACCOUNTS", "ORIGINAL_ENTRY", year, parent, f"AUG_XLSX_R{source_row:06d}", parent_order[parent], tokens(surface)))
            node.clear()
    # The source-freeze count is whitespace-delimited. Analysis discards the
    # few punctuation-only groups, so only the entry count is invariant here.
    assert len(lines) == 22071
    return lines


def external_lines() -> list[Line]:
    blind = read(BLIND)
    expanded = {row["line_id"]: row for row in read(EXPANDED)}
    assert len(blind) == len(expanded) == 48347
    lines: list[Line] = []
    for row in blind:
        corpus = row["corpus"]
        if corpus == "NUREMBERG":
            base = "NUREMBERG_LETTERBOOKS"
            fold = row["book_or_ms"]
        else:
            base = "STE1_RECIPES"
            fold = row["record_id"]
        common = (base, fold, row["record_id"], row["line_id"], int(row["line_index"]))
        lines.append(Line(common[0], "REAL_DIPLOMATIC", common[1], common[2], common[3], common[4], tokens(row["diplomatic_bare"])))
        lines.append(Line(common[0], "EXPANDED", common[1], common[2], common[3], common[4], tokens(expanded[row["line_id"]]["expanded_diplomatic"])))
    return lines


def stable_fold(value: str, count: int = 12) -> str:
    return f"F{int(hashlib.sha256((value + '|GDT158').encode()).hexdigest()[:12], 16) % count:02d}"


def fingerprint_sample(lines: list[Line]) -> list[dict[str, object]]:
    bins: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for line in lines:
        fold = stable_fold(line.parent)
        for index, token in enumerate(line.toks, 1):
            key = f"{line.line_id}|{index:03d}"
            if token.isalnum() and 2 <= len(token) <= 30:
                bins[fold].append((key, token))
    selected: list[dict[str, object]] = []
    for fold in [f"F{i:02d}" for i in range(12)]:
        values = bins[fold]
        values.sort(key=lambda item: hashlib.sha256((item[0] + "|GDT158_SAMPLE").encode()).hexdigest())
        assert len(values) >= 1000, (fold, len(values))
        selected.extend({"fold_id": fold, "form": token} for _, token in values[:1000])
    return selected


def learned_signatures(lines: list[Line]) -> tuple[dict[tuple[str, str, int], str], dict[tuple[str, str, int], tuple[str, ...]]]:
    by_fold: dict[str, list[Line]] = defaultdict(list)
    for line in lines:
        by_fold[line.fold].append(line)
    signatures: dict[tuple[str, str, int], str] = {}
    right_ops: dict[tuple[str, str, int], tuple[str, ...]] = {}
    for held in sorted(by_fold):
        training = [line for fold, values in by_fold.items() if fold != held for line in values]
        counts = Counter(token for line in training for token in line.toks)
        token_parents: dict[str, set[str]] = defaultdict(set)
        for line in training:
            for token in line.toks:
                token_parents[token].add(line.parent)
        left, right, _, envelope = discover(counts, token_parents)
        for line in by_fold[held]:
            for index, token in enumerate(line.toks):
                parsed = parse_token(token, counts, left, right, envelope)
                signature = "L=" + "+".join(x for x in (str(parsed["outer_left"]), str(parsed["local_left"])) if x != "NONE")
                signature += "|R=" + "+".join(x for x in (str(parsed["right_outer"]), str(parsed["right_inner"])) if x != "NONE")
                signature += "|H=" + ("1_3" if len(str(parsed["page_host"])) <= 3 else "4_5" if len(str(parsed["page_host"])) <= 5 else "6_PLUS")
                key = (line.parent, line.line_id, index)
                signatures[key] = signature
                right_ops[key] = tuple(x for x in (str(parsed["right_outer"]), str(parsed["right_inner"])) if x != "NONE")
    return signatures, right_ops


class BoundaryPanel:
    def __init__(self, lines: list[Line]):
        self.lines = [line for line in lines if line.toks]
        self.folds = sorted({line.fold for line in self.lines})
        fold_index = {fold: i for i, fold in enumerate(self.folds)}
        signatures, right_ops = learned_signatures(self.lines)
        grouped: dict[str, list[Line]] = defaultdict(list)
        for line in self.lines:
            grouped[line.parent].append(line)
        self.parents: list[dict[str, object]] = []
        all_tokens: list[str] = []
        all_signatures: list[str] = []
        all_candidates: list[tuple[str, ...]] = []
        token_folds: list[int] = []
        token_parents: list[int] = []
        self.true_starts: list[int] = []
        self.true_ends: list[int] = []
        self.parent_boundary_pairs: list[tuple[int, int]] = []
        offset = 0
        ordered_parents = sorted(grouped, key=lambda parent: (grouped[parent][0].fold, min(line.line_id for line in grouped[parent])))
        previous_by_fold: dict[str, int] = {}
        for pindex, parent in enumerate(ordered_parents):
            values = sorted(grouped[parent], key=lambda line: (line.order, line.line_id))
            stream = [token for line in values for token in line.toks]
            lengths = [len(line.toks) for line in values]
            starts, ends, cursor = [], [], offset
            for line in values:
                starts.append(cursor)
                cursor += len(line.toks)
                ends.append(cursor - 1)
                for index, token in enumerate(line.toks):
                    key = (line.parent, line.line_id, index)
                    signature = signatures[key]
                    suffixes = tuple(f"SUFFIX{n}:{token[-n:]}" for n in range(1, min(3, len(token)) + 1))
                    rops = tuple(f"RIGHT_OP:{op}" for op in right_ops[key])
                    all_tokens.append(token)
                    all_signatures.append(signature)
                    all_candidates.append(suffixes + rops)
                    token_folds.append(fold_index[line.fold])
                    token_parents.append(pindex)
            self.true_starts.extend(starts)
            self.true_ends.extend(ends)
            if values[0].fold in previous_by_fold:
                self.parent_boundary_pairs.append((previous_by_fold[values[0].fold], offset))
            previous_by_fold[values[0].fold] = cursor - 1
            self.parents.append({"parent": parent, "fold": fold_index[values[0].fold], "offset": offset, "lengths": lengths, "size": len(stream)})
            offset = cursor
        self.tokens = all_tokens
        self.token_folds = np.asarray(token_folds, dtype=np.int16)
        self.token_parents = np.asarray(token_parents, dtype=np.int32)
        signature_names = sorted(set(all_signatures)); self.signature_names = signature_names
        smap = {value: i for i, value in enumerate(signature_names)}
        self.signature_ids = np.asarray([smap[value] for value in all_signatures], dtype=np.int32)
        candidate_names = sorted({value for values in all_candidates for value in values}); self.candidate_names = candidate_names
        cmap = {value: i for i, value in enumerate(candidate_names)}
        width = max((len(values) for values in all_candidates), default=1)
        matrix = np.full((len(all_candidates), width), -1, dtype=np.int32)
        for i, values in enumerate(all_candidates):
            matrix[i, :len(values)] = [cmap[value] for value in values]
        self.candidate_matrix = matrix
        self.candidate_total_fold = np.zeros((len(self.folds), len(candidate_names)), dtype=np.int64)
        self.candidate_parent_fold: list[dict[int, set[int]]] = [defaultdict(set) for _ in candidate_names]
        for index in range(len(self.tokens)):
            fold, parent = int(self.token_folds[index]), int(self.token_parents[index])
            for cid in self.candidate_matrix[index]:
                if cid >= 0:
                    self.candidate_total_fold[fold, cid] += 1
                    self.candidate_parent_fold[int(cid)][fold].add(parent)
        self.adj_sim = np.zeros(len(self.tokens), dtype=float)
        for parent in self.parents:
            start, size = int(parent["offset"]), int(parent["size"])
            for index in range(start, start + size - 1):
                self.adj_sim[index] = jaccard(self.tokens[index], self.tokens[index + 1])
        self.valid_adj = np.zeros(len(self.tokens), dtype=bool)
        for parent in self.parents:
            start, size = int(parent["offset"]), int(parent["size"])
            self.valid_adj[start:start + size - 1] = True

    def boundaries(self, world: int | None) -> tuple[np.ndarray, np.ndarray]:
        if world is None:
            return np.asarray(self.true_starts, dtype=np.int64), np.asarray(self.true_ends, dtype=np.int64)
        starts: list[int] = []; ends: list[int] = []
        for parent in self.parents:
            lengths = list(parent["lengths"]); count = len(lengths)
            if count > 1:
                base = int(hashlib.sha256(f"{SEED}|{parent['parent']}".encode()).hexdigest()[:12], 16)
                shift = 1 + ((base + world * 104729) % (count - 1))
                lengths = lengths[shift:] + lengths[:shift]
            cursor = int(parent["offset"])
            for length in lengths:
                starts.append(cursor); cursor += length; ends.append(cursor - 1)
        return np.asarray(starts, dtype=np.int64), np.asarray(ends, dtype=np.int64)

    def metrics(self, starts: np.ndarray, ends: np.ndarray, closure_rows: list[dict[str, object]] | None = None) -> dict[str, float]:
        all_sig = np.bincount(self.signature_ids, minlength=len(self.signature_names)).astype(float)
        first_sig = np.bincount(self.signature_ids[starts], minlength=len(self.signature_names)).astype(float)
        last_sig = np.bincount(self.signature_ids[ends], minlength=len(self.signature_names)).astype(float)
        # A one-token line is both opening and closing but is not interior.
        boundary = np.unique(np.concatenate((starts, ends)))
        boundary_sig = np.bincount(self.signature_ids[boundary], minlength=len(self.signature_names)).astype(float)
        interior_sig = all_sig - boundary_sig
        cross_positions = ends[self.valid_adj[ends]]
        cross_sum = float(self.adj_sim[cross_positions].sum()); cross_n = len(cross_positions)
        total_sum = float(self.adj_sim[self.valid_adj].sum()); total_n = int(self.valid_adj.sum())
        within_sum, within_n = total_sum - cross_sum, total_n - cross_n
        line_reset = within_sum / max(1, within_n) - cross_sum / max(1, cross_n)
        fold_term = np.zeros((len(self.folds), len(self.candidate_names)), dtype=np.int64)
        fold_lines = np.zeros(len(self.folds), dtype=np.int64)
        for fold in range(len(self.folds)):
            selected = ends[self.token_folds[ends] == fold]
            fold_lines[fold] = len(selected)
            ids = self.candidate_matrix[selected].ravel()
            ids = ids[ids >= 0]
            fold_term[fold] = np.bincount(ids, minlength=len(self.candidate_names))
        agg_t_hit = agg_i_hit = agg_t_total = agg_i_total = 0
        for held, held_name in enumerate(self.folds):
            train_term = fold_term.sum(axis=0) - fold_term[held]
            train_total = self.candidate_total_fold.sum(axis=0) - self.candidate_total_fold[held]
            train_lines = int(fold_lines.sum() - fold_lines[held])
            train_tokens = int(np.sum(self.token_folds != held))
            train_interior_total = train_tokens - train_lines
            eligible = []
            for cid, name in enumerate(self.candidate_names):
                parent_support = sum(len(values) for fold, values in self.candidate_parent_fold[cid].items() if fold != held)
                if train_term[cid] >= 8 and parent_support >= 5 and train_total[cid] > train_term[cid]:
                    t_rate = (train_term[cid] + .5) / (train_lines + 1)
                    i_rate = (train_total[cid] - train_term[cid] + .5) / (train_interior_total + 1)
                    effect = math.log2(t_rate / i_rate)
                    eligible.append((effect, int(train_term[cid]), name, cid))
            if not eligible:
                chosen = (0.0, 0, "NONE", -1)
            else:
                chosen = min(eligible, key=lambda item: (-item[0], -item[1], item[2]))
            effect, _, name, cid = chosen
            t_hit = int(fold_term[held, cid]) if cid >= 0 else 0
            total_hit = int(self.candidate_total_fold[held, cid]) if cid >= 0 else 0
            t_total = int(fold_lines[held]); i_total = int(np.sum(self.token_folds == held) - t_total); i_hit = total_hit - t_hit
            agg_t_hit += t_hit; agg_i_hit += i_hit; agg_t_total += t_total; agg_i_total += i_total
            if closure_rows is not None:
                held_effect = math.log2(((t_hit + .5) / (t_total + 1)) / ((i_hit + .5) / (i_total + 1)))
                closure_rows.append({"fold": held_name, "selected_predicate": name, "training_log2_lift": effect, "held_terminal_hits": t_hit, "held_terminal_total": t_total, "held_interior_hits": i_hit, "held_interior_total": i_total, "held_log2_lift": held_effect})
        closure_lift = math.log2(((agg_t_hit + .5) / (agg_t_total + 1)) / ((agg_i_hit + .5) / (agg_i_total + 1)))
        parent_cross = [jaccard(self.tokens[left], self.tokens[right]) for left, right in self.parent_boundary_pairs]
        line_cross = cross_sum / max(1, cross_n)
        record_reset = line_cross - (statistics.mean(parent_cross) if parent_cross else line_cross)
        return {
            "line_open_edge_js": js_counts(first_sig, interior_sig),
            "line_close_edge_js": js_counts(last_sig, interior_sig),
            "line_reset_char3_contrast": line_reset,
            "record_reset_char3_contrast": record_reset,
            "b3_like_closure_log2_lift": closure_lift,
            "b3_like_terminal_coverage": agg_t_hit / max(1, agg_t_total),
            "b3_like_interior_rate": agg_i_hit / max(1, agg_i_total),
            "line_count": float(len(ends)),
            "group_count": float(len(self.tokens)),
            "mobile_parent_count": float(sum(len(parent["lengths"]) > 1 for parent in self.parents)),
        }


NULL_PANEL: BoundaryPanel | None = None


def null_worker(worlds: list[int]) -> list[tuple[int, dict[str, float]]]:
    assert NULL_PANEL is not None
    out = []
    for world in worlds:
        starts, ends = NULL_PANEL.boundaries(world)
        out.append((world, NULL_PANEL.metrics(starts, ends)))
    return out


def boundary_analysis(corpus_view: str, lines: list[Line], workers: int) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    global NULL_PANEL
    panel = BoundaryPanel(lines)
    starts, ends = panel.boundaries(None)
    closure_rows: list[dict[str, object]] = []
    observed = panel.metrics(starts, ends, closure_rows)
    for row in closure_rows:
        row["corpus_view"] = corpus_view
    NULL_PANEL = panel
    chunks = [list(range(i, WORLDS, workers)) for i in range(workers)]
    if workers == 1:
        evaluated = [null_worker(chunks[0])]
    else:
        with mp.get_context("fork").Pool(workers) as pool:
            evaluated = pool.map(null_worker, chunks)
    null_rows: list[dict[str, object]] = []
    metric_names = ("line_open_edge_js", "line_close_edge_js", "line_reset_char3_contrast", "b3_like_closure_log2_lift")
    null_values: dict[str, list[float]] = defaultdict(list)
    for chunk in evaluated:
        for world, metrics in chunk:
            for metric in metric_names:
                value = float(metrics[metric]); null_values[metric].append(value)
                null_rows.append({"corpus_view": corpus_view, "world": world, "metric": metric, "value": value})
    summaries = {}
    for metric in metric_names:
        values = null_values[metric]; obs = float(observed[metric])
        summaries[metric] = {
            "observed": obs,
            "null_mean": statistics.mean(values),
            "null_sd": statistics.pstdev(values),
            "local_p_greater": (1 + sum(value >= obs for value in values)) / (1 + len(values)),
            "null_q025": sorted(values)[int(.025 * len(values))],
            "null_q975": sorted(values)[min(len(values) - 1, int(.975 * len(values)))],
        }
    layout = {"corpus_view": corpus_view, **observed, "null_worlds": WORLDS, "null_summaries": summaries}
    return layout, closure_rows, null_rows


def flatten_layout(layout: dict[str, object]) -> dict[str, object]:
    row = {key: value for key, value in layout.items() if key != "null_summaries"}
    for metric, values in layout["null_summaries"].items():
        for key, value in values.items():
            row[f"{metric}__{key}"] = value
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--augsburg", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=min(16, mp.cpu_count()))
    args = parser.parse_args()
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert freeze["status"] == "SOURCE_PANEL_FROZEN_BEFORE_RESIDUAL_SCORING"
    assert sha(args.augsburg) == AUG_SHA
    aug = augsburg_lines(args.augsburg)
    ext = external_lines()
    panels: dict[str, list[Line]] = {
        "AUGSBURG_ACCOUNTS:ORIGINAL_ENTRY": aug,
        "NUREMBERG_LETTERBOOKS:REAL_DIPLOMATIC": [line for line in ext if line.corpus == "NUREMBERG_LETTERBOOKS" and line.view == "REAL_DIPLOMATIC"],
        "NUREMBERG_LETTERBOOKS:EXPANDED": [line for line in ext if line.corpus == "NUREMBERG_LETTERBOOKS" and line.view == "EXPANDED"],
        "STE1_RECIPES:REAL_DIPLOMATIC": [line for line in ext if line.corpus == "STE1_RECIPES" and line.view == "REAL_DIPLOMATIC"],
        "STE1_RECIPES:EXPANDED": [line for line in ext if line.corpus == "STE1_RECIPES" and line.view == "EXPANDED"],
    }

    # Exact GDT003 diagnostic for the powered new corpus; reuse immutable GDT157 anchors.
    sample = fingerprint_sample(aug)
    evaluation = evaluate_corpus(("AUGSBURG_ACCOUNTS_ORIGINAL", sample, {"tier": "GDT158_STRUCTURED_CONTROL", "capacity_state": "MATCHED_12000", "sampled_tokens": 12000, "source_units": 1817, "eligible_source_tokens": 281557, "language": "Latin_and_German", "family": "ACCOUNTING_REGISTER", "historical_status": "EARLY_15C_ACCOUNTING"}))
    aug_fp = evaluation["fingerprint"]
    g157 = read(GDT157_FP)
    fp_rows = [aug_fp]
    for source_id in ("EXPANDED_PLAINTEXT", "REAL_DIPLOMATIC"):
        row = dict(next(item for item in g157 if item["corpus_id"] == source_id))
        row["corpus_id"] = "NUREMBERG_" + source_id
        row["tier"] = "GDT158_REUSED_GDT157_ANCHOR"
        fp_rows.append(row)
    voy = dict(next(row for row in read(GDT003_FP) if row["corpus_id"] == "VOYNICH_MATCHED"))
    voy["tier"] = "PUBLISHED_F84R_FREE_REFERENCE"; fp_rows.append(voy)
    write(OUT_FP, fp_rows)

    layout_rows: list[dict[str, object]] = []
    closure_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    for name, lines in panels.items():
        if name.startswith("STE1"):
            # Preserve the honest low-capacity observation; no 4096-world claim.
            panel = BoundaryPanel(lines); starts, ends = panel.boundaries(None); local_closure: list[dict[str, object]] = []
            observed = panel.metrics(starts, ends, local_closure)
            layout_rows.append({"corpus_view": name, **observed, "null_worlds": 0, "capacity_state": "LOW_CAPACITY_TWO_RECORDS_NO_NULL_INFERENCE"})
            for row in local_closure: row["corpus_view"] = name
            closure_rows.extend(local_closure)
            continue
        layout, folds, nulls = boundary_analysis(name, lines, max(1, args.workers))
        layout["capacity_state"] = "POWERED_BOUNDARY_ROTATION"
        layout_rows.append(flatten_layout(layout)); closure_rows.extend(folds); null_rows.extend(nulls)

    # Family-wise maxT across every exercised powered view and endpoint. The
    # same world index is a joint deterministic boundary-rotation world.
    metric_names = ("line_open_edge_js", "line_close_edge_js", "line_reset_char3_contrast", "b3_like_closure_log2_lift")
    null_by_key: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0.0] * WORLDS)
    for row in null_rows:
        null_by_key[(str(row["corpus_view"]), str(row["metric"]))][int(row["world"])] = float(row["value"])
    observed_z: dict[tuple[str, str], float] = {}
    null_z: dict[tuple[str, str], list[float]] = {}
    for row in layout_rows:
        if row.get("capacity_state") != "POWERED_BOUNDARY_ROTATION":
            continue
        for metric in metric_names:
            key = (str(row["corpus_view"]), metric); values = null_by_key[key]
            mean, sd = statistics.mean(values), statistics.pstdev(values)
            observed_z[key] = (float(row[metric]) - mean) / max(sd, 1e-12)
            null_z[key] = [(value - mean) / max(sd, 1e-12) for value in values]
    max_world = [max(values[world] for values in null_z.values()) for world in range(WORLDS)]
    for row in layout_rows:
        if row.get("capacity_state") != "POWERED_BOUNDARY_ROTATION":
            continue
        for metric in metric_names:
            z = observed_z[(str(row["corpus_view"]), metric)]
            row[f"{metric}__observed_z"] = z
            row[f"{metric}__search_adjusted_p"] = (1 + sum(value >= z for value in max_world)) / (WORLDS + 1)
    write(OUT_LAYOUT, layout_rows); write(OUT_CLOSURE, closure_rows); write(OUT_NULL, null_rows)

    fp = {row["corpus_id"]: row for row in fp_rows}
    target = fp["VOYNICH_MATCHED"]
    augrow = fp["AUGSBURG_ACCOUNTS_ORIGINAL"]
    nbreal = fp["NUREMBERG_REAL_DIPLOMATIC"]
    direct_metrics = ("mean_discovered_operations", "compatible_pair_density", "left_right_log2_support_ratio")
    comparison = {metric: {"voynich": float(target[metric]), "augsburg": float(augrow[metric]), "nuremberg_real": float(nbreal[metric])} for metric in direct_metrics}
    powered = [row for row in layout_rows if row.get("capacity_state") == "POWERED_BOUNDARY_ROTATION"]
    strong_boundary = []
    for row in powered:
        passed = []
        for metric in ("line_open_edge_js", "line_close_edge_js", "line_reset_char3_contrast", "b3_like_closure_log2_lift"):
            p = float(row[f"{metric}__search_adjusted_p"])
            passed.append(p <= .05 and float(row[metric]) > float(row[f"{metric}__null_mean"]))
        strong_boundary.append((row["corpus_view"], sum(passed)))
    aug_boundary = next(count for name, count in strong_boundary if name.startswith("AUGSBURG"))
    closure_stability = {}
    for name in panels:
        rows_here = [row for row in closure_rows if row["corpus_view"] == name]
        selected = Counter(str(row["selected_predicate"]) for row in rows_here)
        modal = min(selected, key=lambda value: (-selected[value], value)) if selected else "NONE"
        closure_stability[name] = {"folds": len(rows_here), "unique_predicates": len(selected), "modal_predicate": modal, "modal_fold_fraction": selected.get(modal, 0) / max(1, len(rows_here))}
    algebra_hits = sum([
        float(augrow["mean_discovered_operations"]) >= .5 * float(target["mean_discovered_operations"]),
        float(augrow["compatible_pair_density"]) >= .5 * float(target["compatible_pair_density"]),
        float(augrow["left_right_log2_support_ratio"]) < 0,
    ])
    status = "DOCUMENT_STRUCTURE_GENERATES_MOST_RESIDUAL_ARCHITECTURE" if aug_boundary >= 3 and algebra_hits >= 2 else "DOCUMENT_STRUCTURE_GENERATES_PARTIAL_RESIDUAL_ARCHITECTURE" if aug_boundary >= 2 or algebra_hits >= 1 else "DOCUMENT_STRUCTURE_DOES_NOT_GENERATE_RESIDUAL_ARCHITECTURE"
    counter = [
        {"counterexample": "STRUCTURE_CHANGES_EDGE_ALGEBRA", "evidence": "Boundary rotations preserve every token and its order, so operation scale, compatibility density, and edge support are invariant to layout alone.", "impact": "Any surface-algebra resemblance belongs to genre plus historical writing/abbreviation, not boundary placement."},
        {"counterexample": "AUGSBURG_ENTRY_IS_PHYSICAL_LINE", "evidence": "The workbook row is an editorial account entry; physical manuscript line identity is not claimed.", "impact": "Augsburg supports record-entry architecture, not palaeographic line-reset identity."},
        {"counterexample": "STE1_IS_POWERED_RECIPE_CONFIRMATION", "evidence": "Ste1 contains only two admitted recipe records and ten lines.", "impact": "Recipe results remain descriptive capacity checks."},
        {"counterexample": "NUREMBERG_IS_NEW_ABBREVIATION_REPLICATION", "evidence": "Nuremberg is the unchanged GDT155/GDT157 calibration corpus and no channel is refit.", "impact": "Its paired views are integrity anchors, not new evidence for abbreviation."},
        {"counterexample": "B3_LIKE_CLOSER_IS_VOYNICH_B3", "evidence": "The held-fold closer is selected from generic suffix/right-edge predicates and receives no Voynich literal.", "impact": "A closure effect establishes only an analogous endpoint class."},
        {"counterexample": "F84R_USED", "evidence": "All raw sources are external; the only Voynich input is the previously published f84r-free GDT003 aggregate.", "impact": "f84r remains sealed and unqueried."},
    ]
    write(OUT_COUNTER, counter)

    result = {
        "schema": "GDT158_STRUCTURED_MEDIEVAL_RESIDUAL_RESULT_V1",
        "status": status,
        "chronology": {"source_freeze_commit": "56f5f07", "scoring_after_freeze": True},
        "counts": {"augsburg_entries": len(aug), "augsburg_groups": sum(len(line.toks) for line in aug), "nuremberg_lines": len(panels["NUREMBERG_LETTERBOOKS:REAL_DIPLOMATIC"]), "ste1_lines": len(panels["STE1_RECIPES:REAL_DIPLOMATIC"]), "boundary_null_worlds_per_powered_view": WORLDS, "powered_boundary_views": len(powered)},
        "surface_algebra": comparison,
        "boundary_metrics_above_family_maxT_p_05": dict(strong_boundary),
        "augsburg_residual_components": {"boundary_components_maxT_05": aug_boundary, "descriptive_surface_algebra_half_target_or_sign_components": algebra_hits, "components_total": 7},
        "decision_rubric_provenance": "Endpoints and null were source-frozen; family maxT<=.05 is conventional. The half-target/sign surface summary is a transparent post-freeze descriptive rubric, not a preregistered confirmation threshold.",
        "closure_predicate_stability": closure_stability,
        "interpretation": "Authentic document structure is sufficient only for the components explicitly passing the frozen boundary/algebra criteria; residual components are not semantics.",
        "f84r": {"voynich_source_inputs": 0, "opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "External structured-medieval formal calibration only; no Voynich language, word, morpheme, sound, plaintext, semantic role, meaning, origin, scribal tradition, or translation.",
        "inputs": {path.name: sha(path) for path in (BLIND, EXPANDED, FREEZE, GDT157_FP, GDT003_FP, MANIFEST)},
        "external_inputs": {"augsburg_workbook_sha256": sha(args.augsburg)},
        "documents": {METHOD.name: sha(METHOD), AUDIT.name: sha(AUDIT)},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "validate_gdt158_structured_medieval_residual.py": sha(ROOT / "validate_gdt158_structured_medieval_residual.py")},
        "outputs": {path.name: sha(path) for path in (OUT_FP, OUT_LAYOUT, OUT_CLOSURE, OUT_NULL, OUT_COUNTER)},
    }
    a = comparison["mean_discovered_operations"]; c = comparison["compatible_pair_density"]; lr = comparison["left_right_log2_support_ratio"]
    lines = [
        "# GDT158 — structured medieval document residual report", "", f"Decision: **{status}**.", "",
        "## Result", "",
        f"The powered Augsburg accounting transfer supplies {aug_boundary}/4 predeclared boundary endpoints at family-maxT p≤.05 and {algebra_hits}/3 surface-algebra components under a transparent post-freeze half-target/sign rubric. Document structure is therefore a partial, not complete, generator of the GDT157 residual; the surface rubric is descriptive rather than a preregistered threshold.", "",
        "| Direct GDT003 metric | Augsburg accounts | Nuremberg diplomatic | Voynich published reference |", "|---|---:|---:|---:|",
        f"| discovered operations/fold | {a['augsburg']:.3f} | {a['nuremberg_real']:.3f} | {a['voynich']:.3f} |",
        f"| compatible-pair density | {c['augsburg']:.6f} | {c['nuremberg_real']:.6f} | {c['voynich']:.6f} |",
        f"| right/left log2 support (negative = left-dominant) | {lr['augsburg']:.4f} | {lr['nuremberg_real']:.4f} | {lr['voynich']:.4f} |", "",
        "## Boundary findings", "",
    ]
    for row in powered:
        lines.append(f"### {row['corpus_view']}")
        lines.append("")
        lines.append("| Endpoint | Observed | Null mean | local p | maxT p |")
        lines.append("|---|---:|---:|---:|---:|")
        for metric in ("line_open_edge_js", "line_close_edge_js", "line_reset_char3_contrast", "b3_like_closure_log2_lift"):
            lines.append(f"| {metric} | {float(row[metric]):.6f} | {float(row[f'{metric}__null_mean']):.6f} | {float(row[f'{metric}__local_p_greater']):.6f} | {float(row[f'{metric}__search_adjusted_p']):.6f} |")
        lines.append(f"\nThe selected B3-like predicate covers {100*float(row['b3_like_terminal_coverage']):.3f}% of authentic endpoints versus {100*float(row['b3_like_interior_rate']):.4f}% of interior positions; it is an analogous sparse closer, not Voynich B3 identity.")
        stable = closure_stability[str(row["corpus_view"])]
        lines.append(f"The training-selected closer is `{stable['modal_predicate']}` in {100*float(stable['modal_fold_fraction']):.1f}% of folds ({stable['unique_predicates']} distinct selected predicates), so predicate identity stability is reported separately from endpoint enrichment.")
        lines.append("")
    lines.extend([
        "Ste1 remains a two-record descriptive recipe sensitivity and is not used to claim a general recipe effect.", "",
        "## What this explains—and what it does not", "",
        "Authentic accounting/register boundaries can create stable opening/closing and generic closer classes without a Voynich-specific rule. Boundary placement cannot itself create the token-level operation algebra because the null holds the entire token stream fixed. Any remaining deficit in operation scale, compatible-pair density, or leftward support therefore still requires language/genre texture, abbreviation behavior beyond the calibrated channel, or an additional compiler.", "",
        "This result does not identify B3, PAGE_HOST semantics, a language, plaintext, or translation. Augsburg rows are editorial account entries, Nuremberg is an already-exposed calibration anchor, and Ste1 is underpowered.", "",
        "## Seal", "",
        "No Voynich source row or image was read. The sole numerical Voynich comparison is the published f84r-free GDT003 aggregate. f84r was not opened, queried, retained, joined, or scored.", "",
        "## Claim ceiling", "",
        result["claim_ceiling"], "",
    ])
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    result["outputs"][OUT_REPORT.name] = sha(OUT_REPORT)
    result["result_content_sha256"] = csha(result)
    OUT_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "boundary": dict(strong_boundary), "algebra_hits": algebra_hits}, sort_keys=True))


if __name__ == "__main__":
    main()
