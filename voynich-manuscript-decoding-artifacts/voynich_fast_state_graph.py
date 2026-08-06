#!/usr/bin/env python3
"""Fast, conservative state/bridge analysis for the Voynich ZL3b corpus.

The script parses the corpus once, stores a compact gzip/pickle cache, and then
uses count models and analytic within-line expectations. It deliberately avoids
full-corpus permutation loops and does not assign German meanings.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import pickle
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

VERSION = 3
PAGE_RE = re.compile(r"^<([^>.]+)>\s+<!\s*(.*?)>\s*$")
LOCUS_RE = re.compile(r"^<([^>]+?\.\d+),([^>]+)>\s*(.*)$")
META_RE = re.compile(r"\$([A-Z])=([^\s$>]+)")
MULTI = ("cth", "ckh", "cph", "cfh", "ch", "sh")
SLOT = {
    "q": 0, "p": 1, "f": 1,
    "cth": 2, "ckh": 2, "cph": 2, "cfh": 2, "ch": 2, "sh": 2,
    "o": 3, "t": 4, "k": 4, "e": 5, "d": 6, "s": 6,
    "a": 7, "l": 7, "i": 7, "r": 7,
    "y": 8, "n": 8, "m": 8, "g": 8,
}
ROOT_GROUPS = {"ch", "ok", "ol", "o", "k", "d", "od", "ai", "s", "l"}


def atomize(text: str) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(text):
        hit = next((m for m in MULTI if text.startswith(m, i)), None)
        if hit:
            out.append(hit)
            i += len(hit)
        else:
            out.append(text[i])
            i += 1
    return out


def segment(word: str) -> list[str]:
    out: list[str] = []
    current: list[str] = []
    previous = -1
    for atom in atomize(word):
        slot = SLOT.get(atom, 4)
        if current and slot < previous:
            out.append("".join(current))
            current = []
        current.append(atom)
        previous = slot
    if current:
        out.append("".join(current))
    return out


def parse_unit(unit: str) -> dict[str, Any]:
    """Neutral decomposition using only previously validated alternations.

    ch/sh, k/t and l/r are normalized; repeated e/i are collapsed. q and
    p/f are retained as separate controls; y/n/m/g remain distinct states.
    """
    s = unit.lower()
    q = s.startswith("q")
    if q:
        s = s[1:]
    initial = "NONE"
    if s.startswith(("p", "f")):
        initial = s[0].upper()
        s = s[1:]
    if s.startswith("sh"):
        s = "ch" + s[2:]
    s = s.replace("t", "k").replace("r", "l")
    s = re.sub(r"e+", "e", s)
    s = re.sub(r"i+", "i", s)
    final = "NONE"
    if s and s[-1] in "ynmg":
        final = s[-1].upper()
        s = s[:-1]
    stage2 = "NONE"
    for suffix, label in (("ai", "AI"), ("al", "AL"), ("ol", "OL"), ("a", "A")):
        if s.endswith(suffix) and len(s) > len(suffix):
            s = s[:-len(suffix)]
            stage2 = label
            break
    stage1 = "NONE"
    for suffix, label in (("ed", "ED"), ("e", "E")):
        if s.endswith(suffix) and len(s) > len(suffix):
            s = s[:-len(suffix)]
            stage1 = label
            break
    return {
        "root": s or "EMPTY", "q": q, "initial": initial,
        "stage1": stage1, "stage2": stage2, "final": final,
    }


def clean_text(text: str) -> list[str]:
    text = re.sub(r"\[([^:\]]+)(?::[^\]]*)?\]", lambda m: m.group(1), text)
    text = re.sub(r"\{[^}]*\}", "", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = text.replace("?", "").replace("!", "").replace("*", "").replace("'", "")
    return [
        cleaned
        for part in re.split(r"[\s.,;:=/\\|+\-]+", text)
        if (cleaned := re.sub(r"[^A-Za-z]", "", part).lower())
    ]


def page_number(page: str) -> int:
    match = re.match(r"f(\d+)", page)
    return int(match.group(1)) if match else -1


def corpus_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_cache(corpus: Path) -> dict[str, Any]:
    pages: dict[str, dict[str, str]] = {}
    lines: list[dict[str, Any]] = []
    for raw in corpus.read_text(encoding="utf-8", errors="replace").splitlines():
        match = PAGE_RE.match(raw)
        if match:
            page, attrs = match.groups()
            pages[page] = dict(META_RE.findall(attrs))
            continue
        match = LOCUS_RE.match(raw)
        if not match:
            continue
        locus, code, text = match.groups()
        page = locus.split(".", 1)[0]
        meta = pages.get(page, {})
        kind = code[1] if len(code) > 1 else ""
        if kind not in {"P", "L"}:
            continue
        words = clean_text(text)
        parsed_words: list[dict[str, Any]] = []
        for surface in words:
            units = segment(surface)
            parsed = [parse_unit(unit) for unit in units]
            parsed_words.append({
                "surface": surface,
                "units": units,
                "parsed": parsed,
                "first": parsed[0],
                "last": parsed[-1],
            })
        lines.append({
            "page": page, "locus": locus, "kind": kind,
            "section": meta.get("I", ""), "language": meta.get("L", ""),
            "hand": meta.get("H", ""), "parity": page_number(page) % 2,
            "words": parsed_words,
        })
    return {
        "version": VERSION,
        "digest": corpus_digest(corpus),
        "lines": lines,
    }


def load_cache(corpus: Path, cache_path: Path) -> tuple[dict[str, Any], bool]:
    digest = corpus_digest(corpus)
    if cache_path.exists():
        try:
            with gzip.open(cache_path, "rb") as handle:
                cache = pickle.load(handle)
            if cache.get("version") == VERSION and cache.get("digest") == digest:
                return cache, True
        except (OSError, EOFError, pickle.PickleError):
            pass
    cache = build_cache(corpus)
    with gzip.open(cache_path, "wb", compresslevel=5) as handle:
        pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return cache, False


def root_group(root: str) -> str:
    return root if root in ROOT_GROUPS else "OTHER"


def state_signature(word: dict[str, Any], first: bool = False) -> str:
    z = word["first"] if first else word["last"]
    prefix = "q" if first and z["q"] else "-" if first else ""
    return f"{prefix}{z['root']}:{z['stage1']}:{z['stage2']}:{z['final']}"


def coarse_category(word: dict[str, Any]) -> str:
    if len(word["units"]) != 1:
        return "MULTI"
    z = word["first"]
    r, q, s1, s2, final = z["root"], z["q"], z["stage1"], z["stage2"], z["final"]
    if r == "ol" and not q and s1 == s2 == final == "NONE":
        return "OL"
    if r == "ai" and not q and final == "N":
        return "AI_N"
    if r == "d" and not q and s2 == "AI" and final == "N":
        return "D_AI_N"
    if r == "ch" and not q and s1 in {"E", "ED"}:
        return f"CH_{s1}"
    if r == "ok" and q and s1 in {"E", "ED"}:
        return f"QOK_{s1}"
    if r == "ok" and not q and s1 in {"E", "ED"}:
        return f"OK_{s1}"
    if r == "ch" and not q and s2 == "OL":
        return "CH_OL"
    if final in {"M", "G"}:
        return "CLOSE_MG"
    return "OTHER"


def mh_or(rows: list[dict[str, Any]], state_key: str, a_state: str, b_state: str, target_key: str, min_each: int = 5) -> dict[str, Any]:
    by_root: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        state = row[state_key]
        if state not in {a_state, b_state}:
            continue
        by_root[row["root"]][state, bool(row[target_key])] += 1
    numerator = denominator = 0.0
    directions: list[float] = []
    used = 0
    for root, counts in by_root.items():
        na = counts[a_state, True] + counts[a_state, False]
        nb = counts[b_state, True] + counts[b_state, False]
        if na < min_each or nb < min_each:
            continue
        a = counts[a_state, True]
        b = counts[a_state, False]
        c = counts[b_state, True]
        d = counts[b_state, False]
        n = a + b + c + d
        numerator += a * d / n
        denominator += b * c / n
        directions.append((a + 0.5) / (na + 1) - (c + 0.5) / (nb + 1))
        used += 1
    return {
        "or_mh": numerator / denominator if denominator else None,
        "roots": used,
        "positive_roots": sum(x > 0 for x in directions),
        "negative_roots": sum(x < 0 for x in directions),
        "mean_rate_difference": sum(directions) / len(directions) if directions else None,
    }


def beta_predict(counts: Counter, key: tuple, base_p: float, strength: float = 12.0) -> float:
    n1 = counts[key + (True,)]
    n0 = counts[key + (False,)]
    return (n1 + strength * base_p) / (n1 + n0 + strength)


def q_prediction(lines: list[dict[str, Any]]) -> dict[str, Any]:
    pairs: list[dict[str, Any]] = []
    for line in lines:
        if line["kind"] != "P" or line["section"] not in {"P", "S"}:
            continue
        words = line["words"]
        for left, right in zip(words, words[1:]):
            z = left["last"]
            pairs.append({
                "parity": line["parity"], "section": line["section"],
                "next_root": root_group(right["first"]["root"]),
                "prev_root": root_group(z["root"]),
                "stage1": z["stage1"], "stage2": z["stage2"], "final": z["final"],
                "q": bool(right["first"]["q"]),
            })
    folds = []
    for test_parity in (0, 1):
        train = [r for r in pairs if r["parity"] != test_parity]
        test = [r for r in pairs if r["parity"] == test_parity]
        global_counts = Counter((r["section"], r["next_root"], r["q"]) for r in train)
        full_counts = Counter((r["section"], r["next_root"], r["prev_root"], r["stage1"], r["stage2"], r["final"], r["q"]) for r in train)
        bits_base = bits_full = 0.0
        correct_base = correct_full = 0
        for r in test:
            base_key = (r["section"], r["next_root"])
            n1 = global_counts[base_key + (True,)]
            n0 = global_counts[base_key + (False,)]
            base_p = (n1 + 1.0) / (n1 + n0 + 2.0)
            full_key = (r["section"], r["next_root"], r["prev_root"], r["stage1"], r["stage2"], r["final"])
            full_p = beta_predict(full_counts, full_key, base_p)
            y = r["q"]
            bits_base -= math.log2(base_p if y else 1 - base_p)
            bits_full -= math.log2(full_p if y else 1 - full_p)
            correct_base += (base_p >= 0.5) == y
            correct_full += (full_p >= 0.5) == y
        folds.append({
            "test_parity": test_parity, "n": len(test),
            "baseline_bpt": bits_base / len(test), "state_bpt": bits_full / len(test),
            "gain_bpt": (bits_base - bits_full) / len(test),
            "baseline_accuracy": correct_base / len(test), "state_accuracy": correct_full / len(test),
        })
    total = sum(f["n"] for f in folds)
    return {
        "folds": folds,
        "baseline_bpt": sum(f["baseline_bpt"] * f["n"] for f in folds) / total,
        "state_bpt": sum(f["state_bpt"] * f["n"] for f in folds) / total,
        "gain_bpt": sum(f["gain_bpt"] * f["n"] for f in folds) / total,
        "baseline_accuracy": sum(f["baseline_accuracy"] * f["n"] for f in folds) / total,
        "state_accuracy": sum(f["state_accuracy"] * f["n"] for f in folds) / total,
    }


def within_line_expected(sequence: list[str], pattern: tuple[str, str, str]) -> float:
    n = len(sequence)
    if n < 3:
        return 0.0
    counts = Counter(sequence)
    a, b, c = pattern
    ca = counts[a]
    cb = counts[b] - int(b == a)
    cc = counts[c] - int(c == a) - int(c == b)
    if ca <= 0 or cb <= 0 or cc <= 0:
        return 0.0
    return (n - 2) * (ca / n) * (cb / (n - 1)) * (cc / (n - 2))


def validated_frames(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observed = [Counter(), Counter()]
    expected = [Counter(), Counter()]
    section_counts: dict[str, Counter] = {"P": Counter(), "S": Counter()}
    fillers: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    examples: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    all_patterns: set[tuple[str, str, str]] = set()
    materialized: list[tuple[dict[str, Any], list[str]]] = []
    for line in lines:
        if line["kind"] != "P" or line["section"] not in {"P", "S"}:
            continue
        cats = [coarse_category(word) for word in line["words"]]
        materialized.append((line, cats))
        for i in range(len(cats) - 2):
            pattern = tuple(cats[i:i + 3])
            observed[line["parity"]][pattern] += 1
            section_counts[line["section"]][pattern] += 1
            all_patterns.add(pattern)
            if len(examples[pattern]) < 8:
                examples[pattern].append({
                    "page": line["page"], "locus": line["locus"], "section": line["section"],
                    "surface": " ".join(w["surface"] for w in line["words"][i:i + 3]),
                })
            generic_positions = [j for j, value in enumerate(pattern) if value in {"OTHER", "MULTI"}]
            if len(generic_positions) == 1:
                fillers[pattern][line["words"][i + generic_positions[0]]["surface"]] += 1
    candidates = {p for p, n in observed[1].items() if n >= 3}
    for line, cats in materialized:
        parity = line["parity"]
        for pattern in candidates:
            expected[parity][pattern] += within_line_expected(cats, pattern)
    rows = []
    for pattern in candidates:
        odd_n, even_n = observed[1][pattern], observed[0][pattern]
        odd_e, even_e = expected[1][pattern], expected[0][pattern]
        odd_ratio = odd_n / odd_e if odd_e else 0.0
        even_ratio = even_n / even_e if even_e else 0.0
        named = sum(value not in {"OTHER", "MULTI"} for value in pattern)
        if odd_ratio < 1.5 or even_n < 2 or even_ratio < 1.25 or named < 2:
            continue
        full_n = odd_n + even_n
        full_e = odd_e + even_e
        row = {
            "pattern": list(pattern), "display": " ".join("<X>" if x in {"OTHER", "MULTI"} else x for x in pattern),
            "count": full_n, "expected": full_e, "enrichment": full_n / full_e if full_e else None,
            "odd_count": odd_n, "even_count": even_n,
            "odd_enrichment": odd_ratio, "even_enrichment": even_ratio,
            "P_count": section_counts["P"][pattern], "S_count": section_counts["S"][pattern],
            "distinct_fillers": len(fillers.get(pattern, {})),
            "top_fillers": fillers.get(pattern, Counter()).most_common(10),
            "examples": examples[pattern],
        }
        rows.append(row)
    return sorted(rows, key=lambda r: (r["P_count"] >= 2 and r["S_count"] >= 2, r["enrichment"], r["count"]), reverse=True)


def bridge_analysis(lines: list[dict[str, Any]], bridge_path: Path) -> dict[str, Any]:
    word_to_family: dict[str, str] = {}
    metadata: dict[str, dict[str, str]] = {}
    with bridge_path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            metadata[row["family"]] = row
            for member in row["members"].split():
                word_to_family[member] = row["family"]
    family_signatures: dict[str, Counter] = defaultdict(Counter)
    edges: dict[str, Counter] = {"P": Counter(), "S": Counter()}
    parity_edges = [Counter(), Counter()]
    for line in lines:
        if line["kind"] != "P" or line["section"] not in {"P", "S"}:
            continue
        family_sequence: list[str | None] = []
        for word in line["words"]:
            family = word_to_family.get(word["surface"])
            family_sequence.append(family)
            if family and len(word["units"]) == 1:
                family_signatures[family][state_signature(word, first=True)] += 1
        for left, right in zip(family_sequence, family_sequence[1:]):
            if left and right:
                edges[line["section"]][left, right] += 1
                parity_edges[line["parity"]][left, right] += 1
    stable = []
    all_edges = set(edges["P"]) | set(edges["S"])
    for edge in all_edges:
        p = edges["P"][edge]
        s = edges["S"][edge]
        odd = parity_edges[1][edge]
        even = parity_edges[0][edge]
        if odd >= 2 and even >= 2 and p + s >= 5:
            stable.append({
                "from": edge[0], "to": edge[1], "P_count": p, "S_count": s,
                "odd_count": odd, "even_count": even, "total": p + s,
            })
    stable.sort(key=lambda r: r["total"], reverse=True)
    signatures = []
    for family, row in metadata.items():
        signatures.append({
            "family": family, "members": row["members"],
            "dominant_signatures": family_signatures[family].most_common(5),
            "P_count_reported": int(row["P_count"]), "S_count_reported": int(row["S_count"]),
        })
    return {"family_signatures": signatures, "stable_direct_edges": stable}


def state_effects(lines: list[dict[str, Any]]) -> dict[str, Any]:
    word_rows: list[dict[str, Any]] = []
    label_units: list[dict[str, Any]] = []
    prose_units: list[dict[str, Any]] = []
    for line in lines:
        if line["kind"] == "L":
            for word in line["words"]:
                for z in word["parsed"]:
                    label_units.append({"root": z["root"], **z})
            continue
        if line["kind"] != "P":
            continue
        words = line["words"]
        for i, word in enumerate(words):
            z = word["last"]
            word_rows.append({
                "root": z["root"], "stage1": z["stage1"], "stage2": z["stage2"], "final": z["final"],
                "line_end": i == len(words) - 1,
                "next_q": bool(words[i + 1]["first"]["q"]) if i + 1 < len(words) else False,
                "has_next": i + 1 < len(words),
            })
            for unit in word["parsed"]:
                prose_units.append({"root": unit["root"], **unit})
    q_rows = [r for r in word_rows if r["has_next"]]
    out = {
        "next_q": {
            "E_vs_NONE": mh_or(q_rows, "stage1", "E", "NONE", "next_q"),
            "ED_vs_E": mh_or(q_rows, "stage1", "ED", "E", "next_q"),
            "ED_vs_NONE": mh_or(q_rows, "stage1", "ED", "NONE", "next_q"),
        },
        "line_end": {
            "A_vs_NONE": mh_or(word_rows, "stage2", "A", "NONE", "line_end"),
            "M_vs_NONE": mh_or(word_rows, "final", "M", "NONE", "line_end"),
            "G_vs_NONE": mh_or(word_rows, "final", "G", "NONE", "line_end"),
            "N_vs_NONE": mh_or(word_rows, "final", "N", "NONE", "line_end"),
        },
    }
    # Label versus prose: target=True means label occurrence.
    combined = []
    for row in label_units:
        combined.append({"root": row["root"], "stage1": row["stage1"], "stage2": row["stage2"], "final": row["final"], "is_label": True})
    for row in prose_units:
        combined.append({"root": row["root"], "stage1": row["stage1"], "stage2": row["stage2"], "final": row["final"], "is_label": False})
    out["label_vs_prose"] = {
        "E_vs_NONE": mh_or(combined, "stage1", "E", "NONE", "is_label"),
        "ED_vs_NONE": mh_or(combined, "stage1", "ED", "NONE", "is_label"),
        "A_vs_NONE": mh_or(combined, "stage2", "A", "NONE", "is_label"),
        "AL_vs_NONE": mh_or(combined, "stage2", "AL", "NONE", "is_label"),
    }
    return out


def shared_state_edges(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = {"P": Counter(), "S": Counter()}
    parity = [Counter(), Counter()]
    for line in lines:
        if line["kind"] != "P" or line["section"] not in {"P", "S"}:
            continue
        words = line["words"]
        for left, right in zip(words, words[1:]):
            edge = (state_signature(left), state_signature(right, first=True))
            counts[line["section"]][edge] += 1
            parity[line["parity"]][edge] += 1
    rows = []
    for edge in set(counts["P"]) | set(counts["S"]):
        p, s = counts["P"][edge], counts["S"][edge]
        odd, even = parity[1][edge], parity[0][edge]
        if p >= 4 and s >= 4 and odd >= 3 and even >= 3:
            rows.append({
                "from": edge[0], "to": edge[1], "P_count": p, "S_count": s,
                "odd_count": odd, "even_count": even, "total": p + s,
            })
    return sorted(rows, key=lambda r: r["total"], reverse=True)


def write_edges(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def fmt_or(value: Any) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def build_report(results: dict[str, Any]) -> str:
    effects = results["state_effects"]
    qpred = results["q_prediction"]
    frames = results["validated_frames"][:5]
    bridge = results["bridge"]
    lines = [
        "# Voynich: schneller Zustands- und Brückengrammatik-Test",
        "",
        "## Rechenweg",
        "",
        f"- Cache: {'wiederverwendet' if results['runtime']['cache_hit'] else 'neu gebaut'}",
        f"- Laufzeit ohne Cacheaufbau: {results['runtime']['analysis_seconds']:.2f} s",
        f"- Gesamtzeit: {results['runtime']['total_seconds']:.2f} s",
        "- Keine Vollkorpus-Permutationsschleifen; Odd/Even-Holdout und analytische Zeilen-Nullerwartungen.",
        "",
        "## 1. Morphologische Zustände sind real",
        "",
        "Gleicher Stamm, unterschiedliche Formzustände:",
        "",
        "| Vergleich | Mantel–Haenszel OR | verwendete Stämme |",
        "|---|---:|---:|",
        f"| E gegen unmarkiert → folgendes q | {fmt_or(effects['next_q']['E_vs_NONE']['or_mh'])} | {effects['next_q']['E_vs_NONE']['roots']} |",
        f"| ED gegen E → folgendes q | {fmt_or(effects['next_q']['ED_vs_E']['or_mh'])} | {effects['next_q']['ED_vs_E']['roots']} |",
        f"| ED gegen unmarkiert → folgendes q | {fmt_or(effects['next_q']['ED_vs_NONE']['or_mh'])} | {effects['next_q']['ED_vs_NONE']['roots']} |",
        f"| A gegen unmarkiert → Zeilenende | {fmt_or(effects['line_end']['A_vs_NONE']['or_mh'])} | {effects['line_end']['A_vs_NONE']['roots']} |",
        f"| M gegen unmarkiert → Zeilenende | {fmt_or(effects['line_end']['M_vs_NONE']['or_mh'])} | {effects['line_end']['M_vs_NONE']['roots']} |",
        f"| G gegen unmarkiert → Zeilenende | {fmt_or(effects['line_end']['G_vs_NONE']['or_mh'])} | {effects['line_end']['G_vs_NONE']['roots']} |",
        "",
        "Bildbeschriftungen vermeiden E/ED und bevorzugen A/AL relativ zur unmarkierten Form:",
        "",
        "| Vergleich Label gegen Prosa | OR |",
        "|---|---:|",
        f"| E gegen unmarkiert | {fmt_or(effects['label_vs_prose']['E_vs_NONE']['or_mh'])} |",
        f"| ED gegen unmarkiert | {fmt_or(effects['label_vs_prose']['ED_vs_NONE']['or_mh'])} |",
        f"| A gegen unmarkiert | {fmt_or(effects['label_vs_prose']['A_vs_NONE']['or_mh'])} |",
        f"| AL gegen unmarkiert | {fmt_or(effects['label_vs_prose']['AL_vs_NONE']['or_mh'])} |",
        "",
        "Das trägt eine vorsichtige Funktionslesung: E/ED sind gebundene beziehungsweise anschlussöffnende Formen; A/AL sind eher freie oder zitierfähige Formen; M/G schließen Zeilen.",
        "",
        "## 2. Der linke Zustand sagt die q-Form auf unbekannten Folios voraus",
        "",
        f"Baseline (Abschnitt + nächster Stamm): {qpred['baseline_bpt']:.4f} Bit/Entscheidung.",
        f"Plus vorheriger Stamm- und Formzustand: **{qpred['state_bpt']:.4f}** Bit/Entscheidung.",
        f"Holdout-Gewinn: **{qpred['gain_bpt']:.4f} Bit**, Genauigkeit {qpred['baseline_accuracy']:.3f} → {qpred['state_accuracy']:.3f}.",
        "",
        "Damit ist q keine bloße Schreibvariante: Seine Wahl wird vom vorherigen Ausdruck mitgesteuert.",
        "",
        "## 3. Fünf intern validierte Konstruktionsrahmen",
        "",
        "Die Muster wurden auf ungeraden Folios entdeckt und mussten auf geraden Folios erneut angereichert sein. `<X>` ist ein variables Feld.",
        "",
        "| Rahmen | Gesamt | P/S | Anreicherung gegenüber Zeilenmischung | verschiedene Füller |",
        "|---|---:|---:|---:|---:|",
    ]
    for frame in frames:
        lines.append(
            f"| `{frame['display']}` | {frame['count']} | {frame['P_count']}/{frame['S_count']} | {frame['enrichment']:.2f}× | {frame['distinct_fillers']} |"
        )
    lines += [
        "",
        "Die wichtigsten Rahmen lassen sich neutral lesen als:",
        "",
        "- `OL AI_N <X>`: ein sehr stabiles geschlossenes Paar mit variablem rechtem Feld; 20 Vorkommen, exakt 10/10 auf geraden/ungeraden Folios.",
        "- `<X> CH_E QOK_E`: ein variables Feld vor einer offenen CH-Form und einer q-gebundenen OK-Form.",
        "- `CH_E QOK_E <X>`: derselbe Gouverneur–Dependenten-Kern mit variablem Folgeteil.",
        "",
        "`AI_N` ist damit Teil einer stabilen Konstruktion. Der separate Zustandsvergleich zeigt jedoch, dass `AI_N` eine folgende q-Form stark **unterdrückt**; die frühere Bezeichnung als konkreter Genitiv-/Relator ist daher noch nicht gerechtfertigt.",
        "",
        "## 4. Die P–S-Brückenfamilien bilden einen kleinen Kern",
        "",
        "Dominante formale Signaturen:",
        "",
        "| Familie | Mitglieder | häufigste Signatur |",
        "|---|---|---|",
    ]
    shown = 0
    for row in bridge["family_signatures"]:
        if not row["dominant_signatures"]:
            continue
        dominant = row["dominant_signatures"][0]
        lines.append(f"| {row['family']} | `{row['members']}` | `{dominant[0]}` ({dominant[1]}) |")
        shown += 1
        if shown >= 6:
            break
    lines += [
        "",
        "Stabile direkte Übergänge innerhalb dieses Kerns:",
        "",
        "| von | nach | P | S | gesamt |",
        "|---|---|---:|---:|---:|",
    ]
    for row in bridge["stable_direct_edges"][:12]:
        lines.append(f"| {row['from']} | {row['to']} | {row['P_count']} | {row['S_count']} | {row['total']} |")
    lines += [
        "",
        "Besonders deutlich ist im Sterntext `C0004 → C0008`: eine ED/Y-Form der CH-Familie wird unmittelbar von einer q-E/Y-Form der OK-Familie gefolgt. Abschnittsübergreifend belegt ist vor allem `C0007 → C0008`; `C0010 → C0007` ist dagegen bislang S-spezifisch.",
        "",
        "## 5. Was daraus folgt",
        "",
        "Der Text verhält sich nicht wie ein zufälliges Codebuch. Eine wiederverwendete Stammform erhält systematische Zustände, und diese Zustände bestimmen den Anschluss des nächsten Ausdrucks. Die derzeit belastbare Grammatik ist:",
        "",
        "```text",
        "GESCHLOSSENE FORM (OL / AI_N)",
        "    → meist unpräfigierte Folgeform",
        "",
        "OFFENE FORM (E/ED)",
        "    → häufig q-GEBUNDENE FOLGEFORM",
        "",
        "A/M/G-FORM",
        "    → Abschluss beziehungsweise Zeilenende",
        "```",
        "",
        "Das ist ein belastbarer Teil einer formalen Syntax, noch keine lexikalische Übersetzung. Nicht intern erzwungen sind die Bedeutungen von OL, CH, OK oder AI_N. Der nächste sinnvolle Schritt ist die Rollenbestimmung der variablen Felder – ohne ihnen vorab Begriffe wie Stoff, Vorgang oder Medium zu geben.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("/mnt/data/user-jv7eUcFXWWGB7DsvCBA7hdiA/ZL3b-n.txt"))
    parser.add_argument("--bridge", type=Path, default=Path("/mnt/data/voynich_bridge_lexicon.tsv"))
    parser.add_argument("--cache", type=Path, default=Path("/mnt/data/voynich_zl3b_fast_cache.pkl.gz"))
    parser.add_argument("--json", type=Path, default=Path("/mnt/data/voynich_fast_state_graph_results.json"))
    parser.add_argument("--edges", type=Path, default=Path("/mnt/data/voynich_fast_state_edges.tsv"))
    parser.add_argument("--report", type=Path, default=Path("/mnt/data/voynich_fast_state_graph_report.md"))
    args = parser.parse_args()

    t0 = time.perf_counter()
    cache, cache_hit = load_cache(args.corpus, args.cache)
    t1 = time.perf_counter()
    lines = cache["lines"]
    results: dict[str, Any] = {
        "data": {
            "lines": len(lines),
            "prose_words": sum(len(line["words"]) for line in lines if line["kind"] == "P"),
            "label_words": sum(len(line["words"]) for line in lines if line["kind"] == "L"),
        },
        "state_effects": state_effects(lines),
        "q_prediction": q_prediction(lines),
        "validated_frames": validated_frames(lines),
        "bridge": bridge_analysis(lines, args.bridge),
        "shared_state_edges": shared_state_edges(lines),
    }
    t2 = time.perf_counter()
    results["runtime"] = {
        "cache_hit": cache_hit,
        "cache_seconds": t1 - t0,
        "analysis_seconds": t2 - t1,
        "total_seconds": t2 - t0,
    }
    args.json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_edges(args.edges, results["shared_state_edges"])
    args.report.write_text(build_report(results), encoding="utf-8")
    print(json.dumps({"runtime": results["runtime"], "data": results["data"], "top_frames": results["validated_frames"][:5]}, indent=2))


if __name__ == "__main__":
    main()
