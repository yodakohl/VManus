#!/usr/bin/env python3
"""Conservative reversible paradigm decoder for the Voynich EVA corpus.

The decoder deliberately assigns no sounds or meanings.  It separates exact
monotone units into a paradigm identifier and an exactly reversible member
state.  Only alternations supported by prior held-out analyses are eligible:
initial q, initial ch/sh, AL/AR, terminal m/g (optional mode), and k/t only in
B/S registers (optional mode).  e/i length and all other distinctions remain
literal.

Evaluation is performed on whole held-out folios.  It asks whether the
paradigm sequence recovers cross-folio n-grams and improves reversible
prediction while retaining page-specific information.  Frequency/length-
matched random family mappings are used as controls.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import pickle
import random
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
import voynich_fast_state_graph as core

VERSION = 1
NAMES = ("ZL3b", "IT2a", "RF1b")
CORPUS_FILES = {"ZL3b": "ZL3b-n.txt", "IT2a": "IT2a-n.txt", "RF1b": "RF1b-e.txt"}

STAGE1_SUFFIXES = (
    ("eeed", "EEED"), ("eed", "EED"), ("ed", "ED"),
    ("eee", "EEE"), ("ee", "EE"), ("e", "E"),
)
STAGE2_SUFFIXES = (
    ("aiii", "AIII"), ("aii", "AII"), ("ai", "AI"),
    ("al", "AL"), ("ar", "AR"), ("ol", "OL"), ("or", "OR"),
    ("a", "A"),
)
INV_STAGE1 = {label: suffix for suffix, label in STAGE1_SUFFIXES}
INV_STAGE2 = {label: suffix for suffix, label in STAGE2_SUFFIXES}

# Modes are cumulative.  E/EE, ED/EED, AI/AII, OL/OR and final y are never merged.
MODES: dict[str, tuple[str, ...]] = {
    "Q_ONLY": ("q",),
    "Q_H": ("q", "chsh"),
    "CONSERVATIVE": ("q", "chsh", "alar"),
    "WITH_CLOSURE": ("q", "chsh", "alar", "mg"),
    "REGISTER_AWARE": ("q", "chsh", "alar", "mg", "kt"),
}

# Train-only evidence thresholds.  They are intentionally fixed before the
# model tournament; no test-fold optimisation is performed.
MIN_COUNT = 3
MIN_PAGES = 2
MIN_CONTEXT_COS = {"q": 0.20, "chsh": 0.25, "alar": 0.20, "kt": 0.25, "mg": 0.0}
MIN_PAGE_COS = {"q": 0.05, "chsh": 0.05, "alar": 0.05, "kt": 0.05, "mg": 0.02}
KT_SECTIONS = frozenset({"B", "S"})

Sig = tuple[str, bool, str, str, str, str]
TypeKey = tuple[str, Sig]  # section + exact signature; needed for register-aware mapping


def strict_parse(unit: str) -> Sig:
    """Parse a monotone unit without merging contested distinctions."""
    s = unit.lower()
    q = s.startswith("q")
    if q:
        s = s[1:]
    initial = "NONE"
    if s.startswith(("p", "f")):
        initial = s[0].upper()
        s = s[1:]
    final = "NONE"
    if s and s[-1] in "ynmg":
        final = s[-1].upper()
        s = s[:-1]
    stage2 = "NONE"
    for suffix, label in STAGE2_SUFFIXES:
        if s.endswith(suffix) and len(s) > len(suffix):
            s = s[:-len(suffix)]
            stage2 = label
            break
    stage1 = "NONE"
    for suffix, label in STAGE1_SUFFIXES:
        if s.endswith(suffix) and len(s) > len(suffix):
            s = s[:-len(suffix)]
            stage1 = label
            break
    return (s or "EMPTY", q, initial, stage1, stage2, final)


def render_sig(sig: Sig) -> str:
    root, q, initial, stage1, stage2, final = sig
    return (
        ("q" if q else "")
        + ("" if initial == "NONE" else initial.lower())
        + ("" if root == "EMPTY" else root)
        + ("" if stage1 == "NONE" else INV_STAGE1[stage1])
        + ("" if stage2 == "NONE" else INV_STAGE2[stage2])
        + ("" if final == "NONE" else final.lower())
    )


def sig_text(sig: Sig) -> str:
    root, q, initial, s1, s2, final = sig
    return f"{root}|q{int(q)}|{initial}|{s1}|{s2}|{final}"


def coarse_state(sig: Sig | None) -> str:
    if sig is None:
        return "BOUNDARY"
    root, q, initial, s1, s2, final = sig
    if s1 == "NONE":
        s1c = "0"
    else:
        s1c = ("D" if s1.endswith("D") else "E") + ("L" if s1.startswith("EE") else "S")
    if s2 == "NONE":
        s2c = "0"
    elif s2.startswith("AI"):
        s2c = "I"
    elif s2 in {"AL", "OL"}:
        s2c = "L"
    elif s2 in {"AR", "OR"}:
        s2c = "R"
    else:
        s2c = s2
    return f"q{int(q)}|{initial}|{s1c}|{s2c}|{final}"


def line_number(locus: str) -> int:
    m = re.search(r"\.(\d+)$", locus)
    return int(m.group(1)) if m else 0


@dataclass(frozen=True)
class Occ:
    page: str
    locus: str
    kind: str
    section: str
    language: str
    hand: str
    parity: int
    word_index: int
    unit_index: int
    surface_word: str
    surface_unit: str
    sig: Sig


@dataclass
class UnitLine:
    page: str
    locus: str
    kind: str
    section: str
    language: str
    hand: str
    parity: int
    occurrences: list[Occ]


def materialize(cache: Mapping[str, Any]) -> list[UnitLine]:
    out: list[UnitLine] = []
    for line in cache["lines"]:
        occs: list[Occ] = []
        for wi, word in enumerate(line["words"]):
            for ui, unit in enumerate(word["units"]):
                sig = strict_parse(unit)
                if render_sig(sig) != unit:
                    raise AssertionError(f"non-reversible parse: {unit} -> {sig} -> {render_sig(sig)}")
                occs.append(Occ(
                    page=line["page"], locus=line["locus"], kind=line["kind"],
                    section=line["section"] or "?", language=line["language"] or "?",
                    hand=line["hand"] or "?", parity=line["parity"],
                    word_index=wi, unit_index=ui, surface_word=word["surface"],
                    surface_unit=unit, sig=sig,
                ))
        if occs:
            out.append(UnitLine(
                page=line["page"], locus=line["locus"], kind=line["kind"],
                section=line["section"] or "?", language=line["language"] or "?",
                hand=line["hand"] or "?", parity=line["parity"], occurrences=occs,
            ))
    return out


def cosine(a: Counter, b: Counter) -> float:
    if len(a) > len(b):
        a, b = b, a
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na = sum(v * v for v in a.values())
    nb = sum(v * v for v in b.values())
    return dot / math.sqrt(na * nb) if na and nb else 0.0


def operation_key(sig: Sig, section: str, op: str) -> tuple[Any, Any] | None:
    """Return (neutral key, surface variant) for an eligible alternation."""
    root, q, initial, s1, s2, final = sig
    if op == "q":
        return ("q", root, initial, s1, s2, final), int(q)
    if op == "chsh":
        if root.startswith("ch"):
            return ("chsh", "H" + root[2:], q, initial, s1, s2, final), "ch"
        if root.startswith("sh"):
            return ("chsh", "H" + root[2:], q, initial, s1, s2, final), "sh"
        return None
    if op == "alar":
        if s2 in {"AL", "AR"}:
            return ("alar", root, q, initial, s1, "A_LR", final), s2
        return None
    if op == "mg":
        if final in {"NONE", "M", "G"}:
            return ("mg", root, q, initial, s1, s2, "MG"), final
        return None
    if op == "kt":
        if section not in KT_SECTIONS or root.count("k") + root.count("t") != 1:
            return None
        canon_root = "".join("K" if c in "kt" else c for c in root)
        variant = "k" if "k" in root else "t"
        return ("kt", section, canon_root, q, initial, s1, s2, final), variant
    raise ValueError(op)


def build_evidence(lines: Sequence[UnitLine], train_parity: int | None = None) -> dict[str, Any]:
    """Count variants, page distributions and neighbouring coarse states."""
    groups: dict[str, dict[Any, dict[Any, dict[str, Any]]]] = {
        op: defaultdict(lambda: defaultdict(lambda: {
            "count": 0, "pages": set(), "context": Counter(), "sections": Counter(),
        })) for op in ("q", "chsh", "alar", "mg", "kt")
    }
    for line in lines:
        if line.kind != "P" or (train_parity is not None and line.parity != train_parity):
            continue
        seq = line.occurrences
        for i, occ in enumerate(seq):
            left = coarse_state(seq[i - 1].sig) if i else "BOUNDARY"
            right = coarse_state(seq[i + 1].sig) if i + 1 < len(seq) else "BOUNDARY"
            for op in groups:
                kv = operation_key(occ.sig, occ.section, op)
                if kv is None:
                    continue
                key, variant = kv
                rec = groups[op][key][variant]
                rec["count"] += 1
                rec["pages"].add(occ.page)
                rec["context"]["L=" + left] += 1
                rec["context"]["R=" + right] += 1
                rec["sections"][occ.section] += 1
    return groups


def validate_groups(evidence: Mapping[str, Any], enabled_ops: Iterable[str]) -> tuple[dict[str, set[Any]], list[dict[str, Any]]]:
    valid: dict[str, set[Any]] = {op: set() for op in enabled_ops}
    rows: list[dict[str, Any]] = []
    for op in enabled_ops:
        for key, variants in evidence[op].items():
            eligible = {
                v: rec for v, rec in variants.items()
                if rec["count"] >= MIN_COUNT and len(rec["pages"]) >= MIN_PAGES
            }
            if len(eligible) < 2:
                continue
            variant_items = sorted(eligible.items(), key=lambda x: str(x[0]))
            context_values: list[float] = []
            page_values: list[float] = []
            for ia in range(len(variant_items)):
                for ib in range(ia + 1, len(variant_items)):
                    a = variant_items[ia][1]
                    b = variant_items[ib][1]
                    context_values.append(cosine(a["context"], b["context"]))
                    page_values.append(cosine(Counter(a["pages"]), Counter(b["pages"])))
            min_ctx = min(context_values) if context_values else 0.0
            min_page = min(page_values) if page_values else 0.0
            if min_ctx < MIN_CONTEXT_COS[op] or min_page < MIN_PAGE_COS[op]:
                continue
            valid[op].add(key)
            rows.append({
                "operation": op, "key": repr(key),
                "variants": {str(v): rec["count"] for v, rec in variant_items},
                "min_context_cosine": min_ctx, "min_page_cosine": min_page,
            })
    return valid, rows


def stable_full_validation(lines: Sequence[UnitLine], enabled_ops: Iterable[str]) -> tuple[dict[str, set[Any]], list[dict[str, Any]]]:
    odd, odd_rows = validate_groups(build_evidence(lines, 1), enabled_ops)
    even, even_rows = validate_groups(build_evidence(lines, 0), enabled_ops)
    valid = {op: odd.get(op, set()) & even.get(op, set()) for op in enabled_ops}
    row_index: dict[tuple[str, str], dict[str, Any]] = {}
    for split, rows in (("odd", odd_rows), ("even", even_rows)):
        for row in rows:
            key = (row["operation"], row["key"])
            row_index.setdefault(key, {"operation": row["operation"], "key": row["key"]})[split] = row
    rows_out = [row for (op, key), row in row_index.items() if eval(key) in valid.get(op, set())]
    return valid, rows_out


def canonical_key(sig: Sig, section: str, valid: Mapping[str, set[Any]], enabled_ops: Iterable[str]) -> tuple[Any, ...]:
    root, q, initial, s1, s2, final = sig
    flags: list[str] = []
    enabled = set(enabled_ops)
    if "q" in enabled:
        kv = operation_key(sig, section, "q")
        if kv and kv[0] in valid.get("q", set()):
            q = False
            flags.append("Q")
    if "chsh" in enabled:
        kv = operation_key(sig, section, "chsh")
        if kv and kv[0] in valid.get("chsh", set()):
            root = "H" + root[2:]
            flags.append("H")
    if "kt" in enabled:
        kv = operation_key(sig, section, "kt")
        if kv and kv[0] in valid.get("kt", set()):
            root = "".join("K" if c in "kt" else c for c in root)
            flags.append("KT" + section)
    if "alar" in enabled:
        kv = operation_key(sig, section, "alar")
        if kv and kv[0] in valid.get("alar", set()):
            s2 = "A_LR"
            flags.append("LR")
    if "mg" in enabled:
        kv = operation_key(sig, section, "mg")
        if kv and kv[0] in valid.get("mg", set()):
            final = "MG"
            flags.append("MG")
    return (root, q, initial, s1, s2, final, tuple(flags))


def member_features(sig: Sig, canonical: tuple[Any, ...]) -> str:
    """Return only the residual choices needed inside this paradigm.

    Fields that were not abstracted remain inside the canonical key and are not
    repeated here.  Singleton paradigms therefore use the common code BASE.
    """
    root, q, initial, s1, s2, final = sig
    croot, cq, cini, cs1, cs2, cfinal, flags_tuple = canonical
    flags = set(flags_tuple)
    details: list[str] = []
    if "Q" in flags:
        details.append(f"Q={int(q)}")
    if "H" in flags:
        details.append("H=ch" if root.startswith("ch") else "H=sh")
    if any(x.startswith("KT") for x in flags):
        details.append("KT=k" if "k" in root else "KT=t")
    if "LR" in flags:
        details.append(f"LR={s2}")
    if "MG" in flags:
        details.append(f"MG={final}")
    return ";".join(details) if details else "BASE"


def decode_member(canonical: tuple[Any, ...], member: str) -> Sig:
    """Invert paradigm key + residual member code to the exact strict signature."""
    root, q, initial, s1, s2, final, flags_tuple = canonical
    values: dict[str, str] = {}
    if member != "BASE":
        for field in member.split(";"):
            k, v = field.split("=", 1)
            values[k] = v
    flags = set(flags_tuple)
    if "Q" in flags:
        q = values["Q"] == "1"
    if "H" in flags:
        root = values["H"] + root[1:]
    if any(x.startswith("KT") for x in flags):
        root = root.replace("K", values["KT"], 1)
    if "LR" in flags:
        s2 = values["LR"]
    if "MG" in flags:
        final = values["MG"]
    return (root, bool(q), initial, s1, s2, final)

def type_key(occ: Occ) -> TypeKey:
    return (occ.section, occ.sig)


def map_lines(lines: Sequence[UnitLine], valid: Mapping[str, set[Any]], enabled_ops: Iterable[str]) -> tuple[list[dict[str, Any]], dict[TypeKey, tuple[Any, ...]]]:
    mapping: dict[TypeKey, tuple[Any, ...]] = {}
    out: list[dict[str, Any]] = []
    for line in lines:
        exact: list[str] = []
        paradigms: list[tuple[Any, ...]] = []
        members: list[str] = []
        keys: list[TypeKey] = []
        for occ in line.occurrences:
            key = type_key(occ)
            canonical = mapping.setdefault(key, canonical_key(occ.sig, occ.section, valid, enabled_ops))
            member = member_features(occ.sig, canonical)
            decoded = decode_member(canonical, member)
            if decoded != occ.sig or render_sig(decoded) != occ.surface_unit:
                raise AssertionError(f"paradigm round-trip failed: {occ.surface_unit} -> {canonical} + {member} -> {decoded}")
            exact.append(occ.surface_unit)
            paradigms.append(canonical)
            members.append(member)
            keys.append(key)
        out.append({
            "page": line.page, "locus": line.locus, "kind": line.kind,
            "section": line.section, "parity": line.parity,
            "exact": exact, "paradigms": paradigms, "members": members,
            "type_keys": keys, "occurrences": line.occurrences,
        })
    return out, mapping


def ngrams(seq: Sequence[Any], n: int) -> Iterator[tuple[Any, ...]]:
    for i in range(len(seq) - n + 1):
        yield tuple(seq[i:i + n])


def ngram_coverage_between(train: Sequence[dict[str, Any]], test: Sequence[dict[str, Any]], n_values: Sequence[int] = (2, 3, 4, 5)) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for field in ("exact", "paradigms"):
        values: dict[str, Any] = {}
        for n in n_values:
            train_set = set()
            for line in train:
                if line["kind"] == "P":
                    train_set.update(ngrams(line[field], n))
            total = seen = 0
            for line in test:
                if line["kind"] != "P":
                    continue
                for gram in ngrams(line[field], n):
                    total += 1
                    seen += gram in train_set
            values[str(n)] = {"seen": seen, "total": total, "rate": seen / total if total else None}
        out[field] = values
    out["gain"] = {str(n): out["paradigms"][str(n)]["rate"] - out["exact"][str(n)]["rate"] for n in n_values}
    return out


def aggregate_ngram_folds(folds: Sequence[dict[str, Any]], n_values: Sequence[int] = (2, 3, 4, 5)) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for field in ("exact", "paradigms"):
        out[field] = {}
        for n in n_values:
            seen = sum(f[field][str(n)]["seen"] for f in folds)
            total = sum(f[field][str(n)]["total"] for f in folds)
            out[field][str(n)] = {"seen": seen, "total": total, "rate": seen / total if total else None}
    out["gain"] = {str(n): out["paradigms"][str(n)]["rate"] - out["exact"][str(n)]["rate"] for n in n_values}
    return out


def random_mapping(mapping: Mapping[TypeKey, tuple[Any, ...]], train_freq: Counter, rng: random.Random) -> dict[TypeKey, tuple[Any, ...]]:
    bins: dict[tuple[int, int], list[TypeKey]] = defaultdict(list)
    for key in mapping:
        surface = render_sig(key[1])
        freq = train_freq[key]
        bins[(len(surface), int(math.log2(freq + 1)))].append(key)
    out: dict[TypeKey, tuple[Any, ...]] = {}
    for keys in bins.values():
        labels = [mapping[k] for k in keys]
        rng.shuffle(labels)
        out.update(zip(keys, labels))
    return out


def remap_with_random(mapped: Sequence[dict[str, Any]], random_map: Mapping[TypeKey, tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [dict(line, paradigms=[random_map[k] for k in line["type_keys"]]) for line in mapped]


def random_ngram_control_between(train: Sequence[dict[str, Any]], test: Sequence[dict[str, Any]], mapping: Mapping[TypeKey, tuple[Any, ...]], iterations: int, seed: int) -> dict[str, Any]:
    train_freq = Counter()
    for line in train:
        if line["kind"] == "P":
            train_freq.update(line["type_keys"])
    rng = random.Random(seed)
    values = {str(n): [] for n in (2, 3, 4, 5)}
    for _ in range(iterations):
        rm = random_mapping(mapping, train_freq, rng)
        tr = remap_with_random(train, rm)
        te = remap_with_random(test, rm)
        rr = ngram_coverage_between(tr, te)["paradigms"]
        for n in values:
            values[n].append(rr[n]["rate"])
    return {n: {"values": v} for n, v in values.items()}

def logprob_hierarchical(
    token: Any, section: str, prev: Any,
    global_counts: Counter, section_counts: Counter, bigram_counts: Counter,
    global_n: int, section_n: Counter, context_n: Counter,
    vocab_size: int, alpha: float = 0.25, section_strength: float = 20.0,
    context_strength: float = 8.0,
) -> float:
    p0 = (global_counts[token] + alpha) / (global_n + alpha * vocab_size)
    p1 = (section_counts[(section, token)] + section_strength * p0) / (section_n[section] + section_strength)
    if prev is None:
        return p1
    return (bigram_counts[(section, prev, token)] + context_strength * p1) / (context_n[(section, prev)] + context_strength)


def reversible_bits_between(train: Sequence[dict[str, Any]], test: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Compare exact bigram coding with paradigm + member coding on seen units."""
    raw_global = Counter(); raw_sec = Counter(); raw_big = Counter(); raw_sec_n = Counter(); raw_ctx_n = Counter()
    pid_global = Counter(); pid_sec = Counter(); pid_big = Counter(); pid_sec_n = Counter(); pid_ctx_n = Counter()
    mem_global = Counter(); mem_sec = Counter(); mem_ctx = Counter(); mem_pid_n = Counter(); mem_pid_sec_n = Counter(); mem_pid_ctx_n = Counter()
    train_surfaces = set()
    for line in train:
        if line["kind"] != "P":
            continue
        prev_raw = prev_pid = None
        for surface, pid in zip(line["exact"], line["paradigms"]):
            train_surfaces.add(surface)
            raw_global[surface] += 1; raw_sec[(line["section"], surface)] += 1; raw_sec_n[line["section"]] += 1
            if prev_raw is not None:
                raw_big[(line["section"], prev_raw, surface)] += 1; raw_ctx_n[(line["section"], prev_raw)] += 1
            pid_global[pid] += 1; pid_sec[(line["section"], pid)] += 1; pid_sec_n[line["section"]] += 1
            if prev_pid is not None:
                pid_big[(line["section"], prev_pid, pid)] += 1; pid_ctx_n[(line["section"], prev_pid)] += 1
            mem_global[(pid, surface)] += 1; mem_pid_n[pid] += 1
            mem_sec[(line["section"], pid, surface)] += 1; mem_pid_sec_n[(line["section"], pid)] += 1
            if prev_pid is not None:
                mem_ctx[(line["section"], prev_pid, pid, surface)] += 1
                mem_pid_ctx_n[(line["section"], prev_pid, pid)] += 1
            prev_raw, prev_pid = surface, pid

    member_vocab = Counter(pid for pid, _ in mem_global)
    raw_vocab = max(1, len(raw_global)); pid_vocab = max(1, len(pid_global))
    raw_n = sum(raw_global.values()); pid_n = sum(pid_global.values())
    raw_bits = pid_bits = member_bits = 0.0
    n = seen = 0
    for line in test:
        if line["kind"] != "P":
            continue
        prev_raw = prev_pid = None
        for surface, pid in zip(line["exact"], line["paradigms"]):
            n += 1
            if surface not in train_surfaces or pid not in pid_global:
                prev_raw, prev_pid = surface, pid
                continue
            seen += 1
            pr = logprob_hierarchical(surface, line["section"], prev_raw,
                raw_global, raw_sec, raw_big, raw_n, raw_sec_n, raw_ctx_n, raw_vocab)
            pp = logprob_hierarchical(pid, line["section"], prev_pid,
                pid_global, pid_sec, pid_big, pid_n, pid_sec_n, pid_ctx_n, pid_vocab)
            members = max(1, member_vocab[pid])
            pm0 = (mem_global[(pid, surface)] + 0.25) / (mem_pid_n[pid] + 0.25 * members)
            pm1 = (mem_sec[(line["section"], pid, surface)] + 10.0 * pm0) / (mem_pid_sec_n[(line["section"], pid)] + 10.0)
            if prev_pid is None:
                pm = pm1
            else:
                pm = (mem_ctx[(line["section"], prev_pid, pid, surface)] + 6.0 * pm1) / (mem_pid_ctx_n[(line["section"], prev_pid, pid)] + 6.0)
            raw_bits -= math.log2(max(pr, 1e-15))
            pid_bits -= math.log2(max(pp, 1e-15))
            member_bits -= math.log2(max(pm, 1e-15))
            prev_raw, prev_pid = surface, pid
    return {
        "tokens": n, "seen_tokens": seen, "seen_rate": seen / n if n else None,
        "raw_bits": raw_bits, "paradigm_bits": pid_bits, "member_bits_total": member_bits,
        "raw_bpt": raw_bits / seen if seen else None,
        "paradigm_bpt": pid_bits / seen if seen else None,
        "member_bpt": member_bits / seen if seen else None,
        "total_reversible_bpt": (pid_bits + member_bits) / seen if seen else None,
        "gain_bpt": (raw_bits - pid_bits - member_bits) / seen if seen else None,
    }


def aggregate_bit_folds(folds: Sequence[dict[str, Any]]) -> dict[str, Any]:
    seen = sum(f["seen_tokens"] for f in folds); tokens = sum(f["tokens"] for f in folds)
    raw = sum(f["raw_bits"] for f in folds); pid = sum(f["paradigm_bits"] for f in folds); mem = sum(f["member_bits_total"] for f in folds)
    return {
        "folds": list(folds), "tokens": tokens, "seen_tokens": seen, "seen_rate": seen / tokens if tokens else None,
        "raw_bpt": raw / seen if seen else None, "paradigm_bpt": pid / seen if seen else None,
        "member_bpt": mem / seen if seen else None, "total_reversible_bpt": (pid + mem) / seen if seen else None,
        "gain_bpt": (raw - pid - mem) / seen if seen else None,
    }

def tfidf_vectors(docs: Mapping[Any, Counter]) -> dict[Any, dict[Any, float]]:
    n = len(docs)
    df = Counter()
    for c in docs.values():
        df.update(c.keys())
    out: dict[Any, dict[Any, float]] = {}
    for key, c in docs.items():
        vec = {term: (1 + math.log(count)) * (math.log((1 + n) / (1 + df[term])) + 1) for term, count in c.items()}
        norm = math.sqrt(sum(v * v for v in vec.values()))
        out[key] = {k: v / norm for k, v in vec.items()} if norm else {}
    return out


def dot(a: Mapping[Any, float], b: Mapping[Any, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


def page_retrieval(mapped: Sequence[dict[str, Any]], remove_n: int = 0) -> dict[str, Any]:
    modes = ("exact", "paradigms", "members", "combined")
    totals = {mode: Counter() for mode in modes}
    for line in mapped:
        if line["kind"] != "P":
            continue
        values = {
            "exact": line["exact"], "paradigms": line["paradigms"],
            "members": line["members"],
            "combined": list(zip(line["paradigms"], line["members"])),
        }
        for mode in modes:
            totals[mode].update(values[mode])
    removed = {mode: {t for t, _ in totals[mode].most_common(remove_n)} for mode in modes}
    results = {}
    for mode in modes:
        docs: dict[tuple[str, str, int], Counter] = defaultdict(Counter)
        for line in mapped:
            if line["kind"] != "P":
                continue
            half = line_number(line["locus"]) % 2
            if mode == "exact": vals = line["exact"]
            elif mode == "paradigms": vals = line["paradigms"]
            elif mode == "members": vals = line["members"]
            else: vals = list(zip(line["paradigms"], line["members"]))
            for token in vals:
                if token not in removed[mode]:
                    docs[(line["section"], line["page"], half)][token] += 1
        pooled_ranks: list[float] = []; pooled_top = pooled_queries = 0
        sections = sorted({k[0] for k in docs})
        per_section = {}
        for section in sections:
            pages = sorted({k[1] for k in docs if k[0] == section and sum(docs.get((section, k[1], 0), Counter()).values()) >= 8 and sum(docs.get((section, k[1], 1), Counter()).values()) >= 8})
            if len(pages) < 4:
                continue
            vecs = tfidf_vectors({(p, h): docs[(section, p, h)] for p in pages for h in (0, 1)})
            ranks = []; top = 0
            for h in (0, 1):
                other = 1 - h
                for p in pages:
                    scored = sorted(((dot(vecs[(p, h)], vecs[(cand, other)]), cand) for cand in pages), reverse=True)
                    rank = next(i + 1 for i, (_, cand) in enumerate(scored) if cand == p)
                    ranks.append(rank); top += rank == 1
                    pooled_ranks.append(rank / len(pages)); pooled_top += rank == 1; pooled_queries += 1
            per_section[section] = {"pages": len(pages), "top1": top / len(ranks), "mean_rank": statistics.mean(ranks)}
        results[mode] = {
            "queries": pooled_queries, "top1": pooled_top / pooled_queries if pooled_queries else None,
            "mean_normalized_rank": statistics.mean(pooled_ranks) if pooled_ranks else None,
            "sections": per_section,
        }
    return results


def repeated_motifs(mapped: Sequence[dict[str, Any]], n_values: Sequence[int] = (4, 5, 6, 7), top_n: int = 80) -> dict[str, Any]:
    results: dict[str, Any] = {}
    paradigm_occ: dict[int, dict[tuple[Any, ...], list[dict[str, Any]]]] = {}
    for field in ("exact", "paradigms"):
        summary = {}
        for n in n_values:
            counter = Counter()
            occ: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
            for line in mapped:
                if line["kind"] != "P" or line["section"] not in {"P", "S"}:
                    continue
                seq = line[field]
                for i, gram in enumerate(ngrams(seq, n)):
                    counter[gram] += 1
                    if field == "paradigms" and len(occ[gram]) < 12:
                        occ[gram].append({
                            "locus": line["locus"], "section": line["section"],
                            "surface": " ".join(line["exact"][i:i + n]),
                        })
            summary[str(n)] = {
                "repeated_types": sum(v >= 2 for v in counter.values()),
                "repeated_occurrences": sum(v for v in counter.values() if v >= 2),
                "max_count": max(counter.values(), default=0),
            }
            if field == "paradigms":
                paradigm_occ[n] = occ
        results[field] = summary
    motifs = []
    for n in sorted(n_values, reverse=True):
        for gram, examples in paradigm_occ[n].items():
            if len(examples) < 2:
                continue
            sections = Counter(x["section"] for x in examples)
            motifs.append({
                "n": n, "count": len(examples), "P_count": sections["P"], "S_count": sections["S"],
                "paradigm": " ".join(repr(x) for x in gram), "examples": examples,
            })
    motifs.sort(key=lambda x: (-x["n"], -x["count"], x["paradigm"]))
    results["motifs"] = motifs[:top_n]
    results["cross_section_motifs"] = [m for m in motifs if m["P_count"] and m["S_count"]][:top_n]
    return results


def build_full_lexicon(mapped: Sequence[dict[str, Any]]) -> tuple[dict[tuple[Any, ...], str], list[dict[str, Any]]]:
    counts = Counter(); members: dict[tuple[Any, ...], Counter] = defaultdict(Counter); sections: dict[tuple[Any, ...], Counter] = defaultdict(Counter)
    for line in mapped:
        for pid, surface in zip(line["paradigms"], line["exact"]):
            counts[pid] += 1; members[pid][surface] += 1; sections[pid][line["section"]] += 1
    ordered = sorted(counts, key=lambda p: (-counts[p], repr(p)))
    ids = {p: f"P{i:04d}" for i, p in enumerate(ordered, 1)}
    rows = []
    for p in ordered:
        rep = members[p].most_common(1)[0][0]
        rows.append({
            "paradigm_id": ids[p], "representative": rep, "count": counts[p],
            "member_types": len(members[p]), "members": members[p].most_common(),
            "sections": sections[p], "canonical": repr(p),
        })
    return ids, rows


def write_lexicon(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.writer(handle, delimiter="\t")
        w.writerow(["paradigm_id", "representative", "token_count", "member_types", "members", "section_counts", "canonical_key"])
        for row in rows:
            w.writerow([
                row["paradigm_id"], row["representative"], row["count"], row["member_types"],
                " ".join(f"{x}:{n}" for x, n in row["members"]),
                " ".join(f"{s}:{n}" for s, n in sorted(row["sections"].items())), row["canonical"],
            ])


def write_tokens(path: Path, mapped: Sequence[dict[str, Any]], ids: Mapping[tuple[Any, ...], str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.writer(handle, delimiter="\t")
        w.writerow(["page", "locus", "kind", "section", "word_index", "unit_index", "surface_word", "surface_unit", "paradigm_id", "member_features", "root", "q", "initial", "stage1", "stage2", "final"])
        for line in mapped:
            for occ, pid, member in zip(line["occurrences"], line["paradigms"], line["members"]):
                root, q, initial, s1, s2, final = occ.sig
                w.writerow([occ.page, occ.locus, occ.kind, occ.section, occ.word_index, occ.unit_index, occ.surface_word, occ.surface_unit, ids[pid], member, root, int(q), initial, s1, s2, final])


def write_motifs(path: Path, motifs: Sequence[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        w = csv.writer(handle, delimiter="\t")
        w.writerow(["n", "count", "P_count", "S_count", "paradigm", "examples"])
        for m in motifs:
            w.writerow([m["n"], m["count"], m["P_count"], m["S_count"], m["paradigm"], " | ".join(f"{e['locus']}:{e['surface']}" for e in m["examples"])])


def serialise(obj: Any) -> Any:
    if isinstance(obj, Counter):
        return dict(obj)
    if isinstance(obj, set):
        return sorted(obj, key=repr)
    if isinstance(obj, tuple):
        return [serialise(x) for x in obj]
    if isinstance(obj, list):
        return [serialise(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): serialise(v) for k, v in obj.items()}
    return obj


def run_one(name: str, cache: Mapping[str, Any], random_iterations: int) -> dict[str, Any]:
    t0 = time.perf_counter()
    lines = materialize(cache)
    mode_results = {}
    for mode, ops in MODES.items():
        coverage_folds = []; bit_folds = []; validation_counts = []
        random_fold_values = {str(n): [] for n in (2, 3, 4, 5)}
        random_fold_totals = {str(n): [] for n in (2, 3, 4, 5)}
        for test_parity in (0, 1):
            train_parity = 1 - test_parity
            valid, _ = validate_groups(build_evidence(lines, train_parity), ops)
            validation_counts.append({"test_parity": test_parity, "valid_groups": {op: len(valid.get(op, set())) for op in ops}})
            train_lines = [line for line in lines if line.parity == train_parity]
            test_lines = [line for line in lines if line.parity == test_parity]
            mapped_train, map_train = map_lines(train_lines, valid, ops)
            mapped_test, map_test = map_lines(test_lines, valid, ops)
            mapping = dict(map_train); mapping.update(map_test)
            cov = ngram_coverage_between(mapped_train, mapped_test)
            coverage_folds.append(cov)
            bit_folds.append(reversible_bits_between(mapped_train, mapped_test))
            rc = random_ngram_control_between(mapped_train, mapped_test, mapping, random_iterations, seed=104729 + test_parity * 1009 + len(mode) * 37)
            for n in random_fold_values:
                random_fold_values[n].append(rc[n]["values"])
                random_fold_totals[n].append(cov["paradigms"][n]["total"])
        ng_agg = aggregate_ngram_folds(coverage_folds)
        random_ctrl = {}
        for n in random_fold_values:
            totals = random_fold_totals[n]; denom = sum(totals)
            vals = []
            for i in range(random_iterations):
                vals.append(sum(random_fold_values[n][j][i] * totals[j] for j in range(len(totals))) / denom)
            obs = ng_agg["paradigms"][n]["rate"]
            mean = statistics.mean(vals); sd = statistics.pstdev(vals)
            random_ctrl[n] = {
                "mean": mean, "sd": sd, "max": max(vals), "min": min(vals),
                "p_ge_observed": (1 + sum(v >= obs for v in vals)) / (len(vals) + 1),
                "z": (obs - mean) / sd if sd else None,
            }
        mode_results[mode] = {
            "operations": list(ops), "validation_counts": validation_counts,
            "ngram_coverage": {"folds": coverage_folds, "aggregate": ng_agg},
            "reversible_bits": aggregate_bit_folds(bit_folds), "random_ngram_control": random_ctrl,
        }
    full_modes = {}
    for mode, ops in MODES.items():
        valid, _ = stable_full_validation(lines, ops)
        mapped, _ = map_lines(lines, valid, ops)
        full_modes[mode] = {
            "valid_group_counts": {op: len(valid.get(op, set())) for op in ops},
            "page_retrieval": {"raw": page_retrieval(mapped, 0)},
        }
    return {"mode_results": mode_results, "full_modes": full_modes, "lines": len(lines), "runtime_seconds": time.perf_counter() - t0}

def score_mode(transcriptions: Mapping[str, Any], mode: str) -> dict[str, Any]:
    n4_gain = []; n5_gain = []; mdl_gain = []; page_loss = []; p4 = []
    for name, tr in transcriptions.items():
        mr = tr["mode_results"][mode]
        n4_gain.append(mr["ngram_coverage"]["aggregate"]["gain"]["4"])
        n5_gain.append(mr["ngram_coverage"]["aggregate"]["gain"]["5"])
        mdl_gain.append(mr["reversible_bits"]["gain_bpt"])
        p4.append(mr["random_ngram_control"]["4"]["p_ge_observed"])
        pr = tr["full_modes"][mode]["page_retrieval"]["raw"]
        exact = pr["exact"]["mean_normalized_rank"]
        paradigm = pr["paradigms"]["mean_normalized_rank"]
        page_loss.append(paradigm - exact)
    return {
        "mean_4gram_coverage_gain": statistics.mean(n4_gain),
        "mean_5gram_coverage_gain": statistics.mean(n5_gain),
        "mean_reversible_gain_bpt": statistics.mean(mdl_gain),
        "mean_page_rank_loss": statistics.mean(page_loss),
        "max_random_p_4gram": max(p4),
    }


def choose_mode(scores: Mapping[str, Mapping[str, float]]) -> str:
    # Prefer a positive reversible gain and strong held-out recurrence while
    # penalising page-rank loss.  This is a fixed transparent score, not a fit.
    def objective(item: tuple[str, Mapping[str, float]]) -> float:
        _, s = item
        mdl = s["mean_reversible_gain_bpt"] or -1.0
        return 4.0 * s["mean_4gram_coverage_gain"] + 2.0 * s["mean_5gram_coverage_gain"] + mdl - 2.0 * max(0.0, s["mean_page_rank_loss"])
    return max(scores.items(), key=objective)[0]


def fnum(x: Any, n: int = 3) -> str:
    return "n/a" if x is None or not isinstance(x, (int, float)) or not math.isfinite(x) else f"{x:.{n}f}"


def make_report(result: Mapping[str, Any]) -> str:
    names = list(result["transcriptions"])
    modes = list(MODES)
    chosen = result["chosen_mode"]
    out = [
        "# Voynich: reversibler Paradigmadecoder und Held-out-Test",
        "",
        "Der Decoder vergibt keine Laute oder Bedeutungen. Jede monotone Einheit wird als `Paradigma-ID + exakte Mitgliedsform` gespeichert und lässt sich verlustfrei zur EVA-Oberfläche zurückwandeln. `e/ee`, `i/ii`, `ED/EED`, `AI/AII`, `OL/OR` und finales `y` werden nie pauschal zusammengelegt.",
        "",
        "## 1. Reversibilität",
        "",
        "Für alle drei Transkriptionen gilt: `decode(encode(unit)) == unit` für jede analysierte Einheit. Die Dekodierung ist daher keine verlustbehaftete Normalisierung.",
        "",
        "## 2. Modellturnier",
        "",
        "| Modus | abstrahierte Relationen | 4-Gramm-Coverage-Gewinn | 5-Gramm-Gewinn | reversibler Bitgewinn | Verlust Seitenrang |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for mode in modes:
        s = result["mode_scores"][mode]
        out.append(f"| **{mode}**{' ← gewählt' if mode == chosen else ''} | {', '.join(MODES[mode])} | {fnum(s['mean_4gram_coverage_gain'],4)} | {fnum(s['mean_5gram_coverage_gain'],4)} | {fnum(s['mean_reversible_gain_bpt'],4)} Bit/Einh. | {fnum(s['mean_page_rank_loss'],4)} |")
    out += [
        "",
        f"Gewählt wurde **{chosen}**. Die Auswahl verwendet eine feste Kombination aus Held-out-n-Grammgewinn, reversibler Codelänge und Verlust der Seiteninformation; sie wurde nicht anhand einzelner lesbar wirkender Passagen getroffen.",
        "",
        "## 3. Held-out-Wiederkehr der Syntax",
        "",
        "Anteil der n-Gramm-Positionen auf vollständig zurückgehaltenen Folios, deren Sequenz bereits in den Trainingsfolios vorkam:",
        "",
        "| Transkription | Darstellung | 2-Gramm | 3-Gramm | 4-Gramm | 5-Gramm | Zufall-p für 4-Gramm |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for name in names:
        mr = result["transcriptions"][name]["mode_results"][chosen]
        agg = mr["ngram_coverage"]["aggregate"]
        for field, label in (("exact", "exakte Einheit"), ("paradigms", "Paradigma")):
            out.append("| " + name + " | " + label + " | " + " | ".join(fnum(agg[field][str(n)]["rate"], 4) for n in (2,3,4,5)) + (f" | {fnum(mr['random_ngram_control']['4']['p_ge_observed'],4)} |" if field == "paradigms" else " | – |"))
    out += [
        "",
        "Die Zufallskontrolle mischt Paradigma-IDs nur unter Einheiten gleicher Länge und ähnlicher Häufigkeit. Sie bewahrt damit den bloßen Vorteil eines kleineren Vokabulars, zerstört aber die konkrete Paradigmabildung.",
        "",
        "## 4. Reversible Vorhersage",
        "",
        "| Transkription | exakte Einheit | Paradigmaskelett | Mitgliedsrest | vollständig reversibel | Gewinn | gesehene Testeinheiten |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name in names:
        x = result["transcriptions"][name]["mode_results"][chosen]["reversible_bits"]
        out.append(f"| {name} | {fnum(x['raw_bpt'])} | {fnum(x['paradigm_bpt'])} | {fnum(x['member_bpt'])} | **{fnum(x['total_reversible_bpt'])}** | {fnum(x['gain_bpt'],4)} | {fnum(x['seen_rate'],3)} |")
    out += [
        "",
        "Ein positiver Gewinn bedeutet, dass die Paradigmafolge leichter vorherzusagen ist und die Kosten für die genaue Oberflächenvariante diesen Vorteil nicht wieder vollständig aufzehren.",
        "",
        "## 5. Bleibt der Seiteninhalt erhalten?",
        "",
        "Eine Hälfte der Zeilen muss die andere Hälfte derselben Seite innerhalb ihres Abschnitts finden. Niedrigerer normalisierter Rang ist besser; Zufall liegt ungefähr bei 0,5.",
        "",
        "| Transkription | exakte Einheit | Paradigma allein | Formrest allein | Paradigma + Rest |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in names:
        pr = result["transcriptions"][name]["full_modes"][chosen]["page_retrieval"]["raw"]
        out.append(f"| {name} | {fnum(pr['exact']['mean_normalized_rank'])} | {fnum(pr['paradigms']['mean_normalized_rank'])} | {fnum(pr['members']['mean_normalized_rank'])} | {fnum(pr['combined']['mean_normalized_rank'])} |")
    out += [
        "",
        "`Paradigma + Rest` ist eine eins-zu-eins-Repräsentation der EVA-Einheit und muss daher dieselbe Seiteninformation wie die exakte Oberfläche bewahren. Entscheidend ist, wie viel bereits das Paradigma allein trägt und wie groß der zusätzliche Formkanal bleibt.",
        "",
        "## 6. Stabile Paradigmenbeziehungen",
        "",
        "Zahl der Relationen, die getrennt auf geraden und ungeraden Folios die Mindestbedingungen erfüllen:",
        "",
        "| Transkription | " + " | ".join(MODES[chosen]) + " | Paradigmen | Mehrgliedrige Paradigmen | Tokenabdeckung |",
        "|---|" + "---:|" * (len(MODES[chosen]) + 3),
    ]
    for name in names:
        fm = result["transcriptions"][name]["full_modes"][chosen]
        lex = result["exports"][name]
        vals = [str(fm["valid_group_counts"].get(op, 0)) for op in MODES[chosen]]
        out.append("| " + name + " | " + " | ".join(vals + [str(lex["paradigms"]), str(lex["multi_member_paradigms"]), f"{lex['multi_member_token_rate']:.1%}"]) + " |")
    out += [
        "",
        "## 7. Was daraus folgt",
        "",
        "1. Eine konservative Paradigmaebene existiert, wenn sie auf ungesehenen Folios längere Sequenzen wiedererkennbar macht und gegenüber frequenzgleichen Zufallsfamilien gewinnt.",
        "2. Sie ersetzt die Oberfläche nicht: Der Mitgliedsrest bleibt vollständig erhalten und trägt weiterhin Seiten- beziehungsweise Fachinformation.",
        "3. Der korrekte Arbeitsgegenstand ist damit `Paradigma + Formzustand`, nicht ein aggressiv normalisiertes angebliches Klartextwort.",
        "4. Noch folgt daraus keine konkrete Bedeutung. Der nächste Schritt ist, die wiederkehrenden Paradigma-Motive auf konstante freie Felder und konstante Funktionspositionen zu zerlegen.",
        "",
        "## 8. Effizienz",
        "",
        f"Summierte CPU-Laufzeit einschließlich drei Transkriptionen, Modellturnier, Zufallskontrollen, Seitentest und Export: **{fnum(result['runtime_seconds'],2)} Sekunden**. Der Code unterstützt Shards (`--only ZL3b`, `--only IT2a`, `--only RF1b`) und anschließendes `--combine-partials`.",
    ]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", type=Path, default=Path("/mnt/data/user-jv7eUcFXWWGB7DsvCBA7hdiA"))
    ap.add_argument("--out-dir", type=Path, default=Path("/mnt/data"))
    ap.add_argument("--random-iterations", type=int, default=40)
    ap.add_argument("--only", choices=NAMES, default=None, help="analyse one transcription and write a partial pickle")
    ap.add_argument("--combine-partials", action="store_true", help="combine previously written partial pickles")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    trans: dict[str, Any] = {}
    caches: dict[str, Any] = {}

    if args.only is not None:
        name = args.only
        corpus = args.corpus_dir / CORPUS_FILES[name]
        cache_path = args.out_dir / f"voynich_paradigm_{name.lower()}_cache.pkl.gz"
        cache, _ = core.load_cache(corpus, cache_path)
        print(f"[paradigm] analysing {name}...", flush=True)
        result_one = run_one(name, cache, args.random_iterations)
        partial = args.out_dir / f"voynich_paradigm_partial_{name.lower()}.pkl.gz"
        with gzip.open(partial, "wb", compresslevel=5) as handle:
            pickle.dump(result_one, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"[paradigm] {name} done in {result_one['runtime_seconds']:.2f}s -> {partial}", flush=True)
        return

    if args.combine_partials:
        for name in NAMES:
            partial = args.out_dir / f"voynich_paradigm_partial_{name.lower()}.pkl.gz"
            with gzip.open(partial, "rb") as handle:
                trans[name] = pickle.load(handle)
            corpus = args.corpus_dir / CORPUS_FILES[name]
            cache_path = args.out_dir / f"voynich_paradigm_{name.lower()}_cache.pkl.gz"
            caches[name], _ = core.load_cache(corpus, cache_path)
    else:
        for name in NAMES:
            corpus = args.corpus_dir / CORPUS_FILES[name]
            cache_path = args.out_dir / f"voynich_paradigm_{name.lower()}_cache.pkl.gz"
            cache, _ = core.load_cache(corpus, cache_path)
            caches[name] = cache
            print(f"[paradigm] analysing {name}...", flush=True)
            trans[name] = run_one(name, cache, args.random_iterations if name == "ZL3b" else max(5, args.random_iterations // 2))
            print(f"[paradigm] {name} done in {trans[name]['runtime_seconds']:.2f}s", flush=True)

    print("[paradigm] scoring modes...", flush=True)
    scores = {mode: score_mode(trans, mode) for mode in MODES}
    chosen = choose_mode(scores)
    print(f"[paradigm] chosen mode: {chosen}", flush=True)
    exports = {}
    for name in NAMES:
        print(f"[paradigm] exporting {name}...", flush=True)
        fm = trans[name]["full_modes"][chosen]
        lines = materialize(caches[name])
        valid, _ = stable_full_validation(lines, MODES[chosen])
        mapped, _ = map_lines(lines, valid, MODES[chosen])
        # Detailed descriptive metrics are computed only for the selected mode.
        fm["page_retrieval"]["raw"] = page_retrieval(mapped, 0)
        fm["page_retrieval"]["minus20"] = page_retrieval(mapped, 20)
        fm["motifs"] = repeated_motifs(mapped)
        ids, lex_rows = build_full_lexicon(mapped)
        multi = sum(row["member_types"] > 1 for row in lex_rows)
        multi_tokens = sum(row["count"] for row in lex_rows if row["member_types"] > 1)
        total_tokens = sum(row["count"] for row in lex_rows)
        exports[name] = {
            "paradigms": len(lex_rows), "multi_member_paradigms": multi,
            "multi_member_tokens": multi_tokens,
            "multi_member_token_rate": multi_tokens / total_tokens if total_tokens else None,
        }
        prefix = "voynich_paradigm" if name == "ZL3b" else f"voynich_paradigm_{name.lower()}"
        write_lexicon(args.out_dir / f"{prefix}_lexicon.tsv", lex_rows)
        write_tokens(args.out_dir / f"{prefix}_tokens.tsv", mapped, ids)
        if name == "ZL3b":
            write_motifs(args.out_dir / "voynich_paradigm_motifs.tsv", fm["motifs"]["motifs"])

    result = {
        "version": VERSION, "modes": {k: list(v) for k, v in MODES.items()},
        "chosen_mode": chosen, "mode_scores": scores, "transcriptions": trans,
        "exports": exports, "runtime_seconds": (sum(x.get("runtime_seconds", 0.0) for x in trans.values()) + (time.perf_counter() - t0)),
    }
    print("[paradigm] serialising results...", flush=True)
    json_path = args.out_dir / "voynich_paradigm_decoder_results.json"
    json_path.write_text(json.dumps(serialise(result), indent=2, ensure_ascii=False), encoding="utf-8")
    report_path = args.out_dir / "voynich_paradigm_decoder_report.md"
    report_path.write_text(make_report(result), encoding="utf-8")
    print(json.dumps({
        "chosen_mode": chosen, "mode_scores": scores,
        "exports": exports, "runtime_seconds": round(result["runtime_seconds"], 2),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
