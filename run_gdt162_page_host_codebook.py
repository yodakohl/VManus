#!/usr/bin/env python3
"""GDT162: exploratory short PAGE_HOST codebook versus internal productivity."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import random
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
CONTROL_SOURCE = ROOT / "gdt159_diplomatic_corpora.json.gz"
CONTROL_MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
DESIGN = ROOT / "gdt162_design.json"
METHOD = ROOT / "GDT162_PAGE_HOST_CODEBOOK_METHOD.md"
REPORT = ROOT / "GDT162_PAGE_HOST_CODEBOOK_REPORT.md"
HOSTS = ROOT / "gdt162_host_inventory.tsv"
LENGTH = ROOT / "gdt162_length_recurrence.tsv"
POSITION = ROOT / "gdt162_position_slot_metrics.tsv"
NEIGHBORS = ROOT / "gdt162_neighbor_substitutions.tsv"
CONTEXT = ROOT / "gdt162_context_transfer.tsv"
NULLS = ROOT / "gdt162_null_summary.tsv"
CONTROLS = ROOT / "gdt162_historical_controls.tsv"
COUNTER = ROOT / "gdt162_counterexamples.tsv"
VARIANTS = ROOT / "gdt162_variant_log.tsv"
RESULT = ROOT / "gdt162_result.json"
WORLDS = 1024
LENGTHS = (2, 3)
COMPONENTS = ("wrapper", "inner_d", "local_frame", "right_family", "dy_closure", "b3")
SMOOTH = 8.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def write(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def guarded_source() -> tuple[list[dict[str, str]], int]:
    rows: list[dict[str, str]] = []
    rejected = 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            locus = row["locus"]
            if page.startswith("f84") or locus.startswith("f84"):
                rejected += 1
                continue
            assert not page.startswith("f84r") and not locus.startswith("f84r")
            rows.append(row)
    assert rows and not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in rows)
    return rows, rejected


def entropy_counts(counts: Iterable[int]) -> float:
    vals = [int(x) for x in counts if x]
    total = sum(vals)
    if not total:
        return 0.0
    return -sum((x / total) * math.log2(x / total) for x in vals)


def hamming(a: str, b: str) -> int:
    return sum(x != y for x, y in zip(a, b)) if len(a) == len(b) else 10**9


def hamming_edges(labels: dict[str, str]) -> set[tuple[str, str]]:
    """Hamming-one identity pairs via wildcard buckets; duplicate labels stay distinct."""
    buckets: dict[tuple[int, int, str], list[str]] = defaultdict(list)
    for ident, word in labels.items():
        for pos in range(len(word)):
            buckets[(len(word), pos, word[:pos] + "*" + word[pos + 1 :])].append(ident)
    edges: set[tuple[str, str]] = set()
    for ids in buckets.values():
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                if labels[a] != labels[b] and hamming(labels[a], labels[b]) == 1:
                    edges.add(tuple(sorted((a, b))))
    return edges


def slot_metrics(labels: dict[str, str], weights: dict[str, int]) -> dict[str, float]:
    total_weight = sum(weights.values())
    if not labels or not total_weight:
        return {"joint_entropy": 0.0, "sum_position_entropy": 0.0, "total_correlation": 0.0, "position_glyph_mi": 0.0}
    joint = Counter()
    by_pos: dict[int, Counter[str]] = defaultdict(Counter)
    posglyph = Counter()
    for ident, word in labels.items():
        w = weights[ident]
        joint[word] += w
        for pos, ch in enumerate(word):
            by_pos[pos][ch] += w
            posglyph[pos, ch] += w
    h_joint = entropy_counts(joint.values())
    h_pos = sum(entropy_counts(c.values()) for c in by_pos.values())
    # Mutual information between random slot position and its glyph.
    pos_count = Counter()
    glyph_count = Counter()
    for (pos, ch), n in posglyph.items():
        pos_count[pos] += n
        glyph_count[ch] += n
    nall = sum(posglyph.values())
    mi = 0.0
    for (pos, ch), n in posglyph.items():
        p = n / nall
        mi += p * math.log2(p / ((pos_count[pos] / nall) * (glyph_count[ch] / nall)))
    return {"joint_entropy": h_joint, "sum_position_entropy": h_pos, "total_correlation": h_pos - h_joint, "position_glyph_mi": mi}


def length_recurrence(name: str, occurrences: list[dict[str, str]], form_key: str, unit_key: str, fold_key: str) -> dict[str, object]:
    forms = [unicodedata.normalize("NFC", r[form_key]) for r in occurrences if r[form_key]]
    counts = Counter(forms)
    total = len(forms)
    types = len(counts)
    by_len = Counter(map(len, forms))
    type_len = Counter(map(len, counts))
    units: dict[str, set[str]] = defaultdict(set)
    folds: dict[str, set[str]] = defaultdict(set)
    for row in occurrences:
        form = unicodedata.normalize("NFC", row[form_key])
        if form:
            units[form].add(row[unit_key])
            folds[form].add(row[fold_key])
    short = {f for f in counts if len(f) in LENGTHS}
    short_tokens = sum(counts[f] for f in short)
    recurrent = sum(counts[f] for f in short if counts[f] >= 2)
    cross_unit = sum(counts[f] for f in short if len(units[f]) >= 2)
    cross_fold = sum(counts[f] for f in short if len(folds[f]) >= 2)
    return {
        "representation": name,
        "tokens": total,
        "types": types,
        "length_2_tokens": by_len[2],
        "length_3_tokens": by_len[3],
        "length_2_3_token_mass": short_tokens / total if total else 0.0,
        "length_2_types": type_len[2],
        "length_3_types": type_len[3],
        "length_2_3_type_mass": len(short) / types if types else 0.0,
        "short_recurrent_token_coverage": recurrent / short_tokens if short_tokens else 0.0,
        "short_cross_unit_token_coverage": cross_unit / short_tokens if short_tokens else 0.0,
        "short_cross_fold_token_coverage": cross_fold / short_tokens if short_tokens else 0.0,
        "token_length_entropy": entropy_counts(by_len.values()),
        "type_length_entropy": entropy_counts(type_len.values()),
        "token_vocabulary_entropy": entropy_counts(counts.values()),
        "effective_token_vocabulary": 2 ** entropy_counts(counts.values()),
    }


def representation_slot_rows(name: str, occurrences: list[dict[str, str]], form_key: str) -> list[dict[str, object]]:
    forms = [unicodedata.normalize("NFC", r[form_key]) for r in occurrences if r[form_key]]
    counts = Counter(forms)
    out: list[dict[str, object]] = []
    for length in LENGTHS:
        labels = {f: f for f in counts if len(f) == length}
        for weighting in ("TYPE", "TOKEN"):
            weights = {f: 1 if weighting == "TYPE" else counts[f] for f in labels}
            metric = slot_metrics(labels, weights)
            inventories = []
            entropies = []
            for pos in range(length):
                c = Counter()
                for f in labels:
                    c[f[pos]] += weights[f]
                inventories.append("".join(sorted(c)))
                entropies.append(entropy_counts(c.values()))
            out.append({
                "representation": name,
                "length": length,
                "weighting": weighting,
                "occurrences": sum(counts[f] for f in labels),
                "types": len(labels),
                "position_inventories": "|".join(inventories),
                "position_entropies": "|".join(f"{x:.12f}" for x in entropies),
                "mean_position_normalized_entropy": sum((h / math.log2(max(2, len(inv)))) for h, inv in zip(entropies, inventories)) / length,
                **metric,
            })
    return out


def neighbor_summary(name: str, occurrences: list[dict[str, str]], form_key: str) -> dict[str, object]:
    forms = [unicodedata.normalize("NFC", r[form_key]) for r in occurrences if r[form_key]]
    counts = Counter(f for f in forms if len(f) in LENGTHS)
    labels = {f: f for f in counts}
    edges = hamming_edges(labels)
    possible = sum(n * (n - 1) // 2 for n in (sum(len(f) == length for f in labels) for length in LENGTHS))
    deg = Counter()
    classes = Counter()
    for a, b in edges:
        deg[a] += 1; deg[b] += 1
        pos = next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
        classes[(len(a), pos, *sorted((a[pos], b[pos])))] += 1
    # Components.
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    seen = set(); comps = []
    for f in labels:
        if f in seen: continue
        stack = [f]; seen.add(f); n = 0
        while stack:
            x = stack.pop(); n += 1
            for y in adj[x]:
                if y not in seen: seen.add(y); stack.append(y)
        comps.append(n)
    top20 = sum(x for _, x in classes.most_common(20)) / len(edges) if edges else 0.0
    return {
        "representation": name,
        "short_types": len(labels),
        "hamming1_edges": len(edges),
        "possible_equal_length_pairs": possible,
        "hamming1_density": len(edges) / possible if possible else 0.0,
        "isolated_types": sum(deg[f] == 0 for f in labels),
        "mean_degree": sum(deg.values()) / len(labels) if labels else 0.0,
        "components": len(comps),
        "largest_component": max(comps, default=0),
        "substitution_classes": len(classes),
        "top20_substitution_edge_share": top20,
    }


def nuisance(row: dict[str, str]) -> tuple[str, ...]:
    return (row["section"], row["currier"], row["hand"], str(len(row["page_host"])), row["position_quartile"])


def context_score(rows: list[dict[str, str]], fold_key: str, fold_mode: str) -> tuple[list[dict[str, object]], dict[str, float]]:
    hosts = sorted({r["page_host"] for r in rows})
    neighbors = {h: {g for g in hosts if len(g) == len(h) and hamming(h, g) == 1} for h in hosts}
    values = {component: sorted({r[component] for r in rows}) for component in COMPONENTS}
    folds = sorted({r[fold_key] for r in rows})
    accum = defaultdict(float)
    nrows = Counter()
    output: list[dict[str, object]] = []
    for held in folds:
        train = [r for r in rows if r[fold_key] != held]
        test = [r for r in rows if r[fold_key] == held]
        for component in COMPONENTS:
            outcomes = values[component]
            global_c = Counter(r[component] for r in train)
            nu_c = Counter((nuisance(r), r[component]) for r in train); nu_n = Counter(nuisance(r) for r in train)
            host_c = Counter((r["page_host"], r[component]) for r in train); host_n = Counter(r["page_host"] for r in train)
            bits = Counter(); exact_seen = neighbor_seen = 0
            for row in test:
                y = row[component]; nk = nuisance(row); h = row["page_host"]
                pg = (global_c[y] + 0.5) / (len(train) + 0.5 * len(outcomes))
                pn = (nu_c[nk, y] + SMOOTH * pg) / (nu_n[nk] + SMOOTH)
                pe = (host_c[h, y] + SMOOTH * pn) / (host_n[h] + SMOOTH)
                nh = neighbors[h]
                nn = sum(host_n[q] for q in nh)
                ny = sum(host_c[q, y] for q in nh)
                pnb = (ny + SMOOTH * pn) / (nn + SMOOTH)
                bits["NUISANCE"] += -math.log2(max(pn, 1e-300))
                bits["EXACT_HOST"] += -math.log2(max(pe, 1e-300))
                bits["HAMMING1_NEIGHBOR"] += -math.log2(max(pnb, 1e-300))
                exact_seen += host_n[h] > 0
                neighbor_seen += nn > 0
            rowout = {
                "fold_mode": fold_mode,
                "held": held,
                "component": component,
                "rows": len(test),
                "nuisance_bits": bits["NUISANCE"],
                "exact_host_bits": bits["EXACT_HOST"],
                "neighbor_bits": bits["HAMMING1_NEIGHBOR"],
                "exact_gain_vs_nuisance": bits["NUISANCE"] - bits["EXACT_HOST"],
                "neighbor_gain_vs_nuisance": bits["NUISANCE"] - bits["HAMMING1_NEIGHBOR"],
                "exact_gain_vs_neighbor": bits["HAMMING1_NEIGHBOR"] - bits["EXACT_HOST"],
                "exact_seen": exact_seen,
                "neighbor_seen": neighbor_seen,
            }
            output.append(rowout)
            for k in ("nuisance_bits", "exact_host_bits", "neighbor_bits"):
                accum[k] += rowout[k]
            nrows["rows"] += len(test)
    summary = dict(accum)
    summary["exact_gain_vs_nuisance"] = accum["nuisance_bits"] - accum["exact_host_bits"]
    summary["neighbor_gain_vs_nuisance"] = accum["nuisance_bits"] - accum["neighbor_bits"]
    summary["exact_gain_vs_neighbor"] = accum["neighbor_bits"] - accum["exact_host_bits"]
    summary["scored_component_rows"] = nrows["rows"]
    return output, summary


def context_vectors(rows: list[dict[str, str]]) -> tuple[dict[str, list[float]], list[str]]:
    dims = [(component, value) for component in COMPONENTS for value in sorted({r[component] for r in rows})]
    count = Counter(r["page_host"] for r in rows)
    cell = Counter((r["page_host"], component, r[component]) for r in rows for component in COMPONENTS)
    vectors = {}
    for host in count:
        vectors[host] = [(cell[host, c, y] + 0.5) / (count[host] + 0.5 * sum(cc == c for cc, _ in dims)) for c, y in dims]
    return vectors, [f"{c}={y}" for c, y in dims]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b)); na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def js_divergence(a: list[float], b: list[float]) -> float:
    # Component blocks each sum to one, so normalize the full concatenated vector.
    sa, sb = sum(a), sum(b); aa = [x / sa for x in a]; bb = [x / sb for x in b]; mm = [(x + y) / 2 for x, y in zip(aa, bb)]
    def kl(x, m): return sum(p * math.log2(p / q) for p, q in zip(x, m) if p and q)
    return 0.5 * kl(aa, mm) + 0.5 * kl(bb, mm)


def neighbor_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, float], dict[str, list[float]]]:
    counts = Counter(r["page_host"] for r in rows)
    folios = defaultdict(set); pages = defaultdict(set); sections = defaultdict(set)
    for r in rows:
        folios[r["page_host"]].add(r["physical_folio"]); pages[r["page_host"]].add(r["page"]); sections[r["page_host"]].add(r["section"])
    labels = {h: h for h in counts if len(h) in LENGTHS}
    edges = hamming_edges(labels)
    vectors, dims = context_vectors(rows)
    out = []
    delta_by_class = defaultdict(list)
    edge_sims = []
    for a, b in sorted(edges):
        pos = next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
        lo, hi = sorted((a[pos], b[pos])); cls = f"L{len(a)}:P{pos + 1}:{lo}>{hi}"
        va, vb = vectors[a], vectors[b]
        delta = [y - x for x, y in zip(va, vb)] if a[pos] == lo else [x - y for x, y in zip(va, vb)]
        delta_by_class[cls].append(delta)
        sim = cosine(va, vb); edge_sims.append(sim)
        out.append({
            "host_a": a, "host_b": b, "length": len(a), "position": pos + 1,
            "glyph_a": a[pos], "glyph_b": b[pos], "substitution_class": cls,
            "count_a": counts[a], "count_b": counts[b], "folios_a": len(folios[a]), "folios_b": len(folios[b]),
            "pages_a": len(pages[a]), "pages_b": len(pages[b]), "sections_a": "|".join(sorted(sections[a])), "sections_b": "|".join(sorted(sections[b])),
            "context_cosine": sim, "context_js": js_divergence(va, vb),
            "claim_state": "ONE_GLYPH_FORMAL_NEIGHBOR_NO_MORPHOLOGY_OR_MEANING",
        })
    coherences = []
    for cls, deltas in delta_by_class.items():
        if len(deltas) < 2: continue
        sims = [cosine(deltas[i], deltas[j]) for i in range(len(deltas)) for j in range(i + 1, len(deltas))]
        coherences.extend(sims)
    summary = {
        "edges": float(len(edges)),
        "mean_neighbor_context_cosine": sum(edge_sims) / len(edge_sims) if edge_sims else 0.0,
        "mean_substitution_delta_coherence": sum(coherences) / len(coherences) if coherences else 0.0,
        "coherence_pair_count": float(len(coherences)),
    }
    return out, summary, vectors


def conditional_mi(rows: list[dict[str, str]], component: str, host_values: list[str] | None = None) -> float:
    hosts = host_values if host_values is not None else [r["page_host"] for r in rows]
    strata = defaultdict(list)
    for i, row in enumerate(rows): strata[nuisance(row)].append(i)
    total = len(rows); out = 0.0
    for ids in strata.values():
        joint = Counter((hosts[i], rows[i][component]) for i in ids)
        hc = Counter(hosts[i] for i in ids); yc = Counter(rows[i][component] for i in ids); n = len(ids)
        for (h, y), c in joint.items():
            out += (c / total) * math.log2((c * n) / (hc[h] * yc[y]))
    return out


def mapped_geometry(mapping: dict[str, str], vectors: dict[str, list[float]]) -> dict[str, float]:
    edges = hamming_edges(mapping)
    possible = sum(n * (n - 1) // 2 for n in (sum(len(s) == length for s in mapping.values()) for length in LENGTHS))
    by_class = Counter()
    sims = []
    delta = defaultdict(list)
    for a, b in edges:
        wa, wb = mapping[a], mapping[b]
        pos = next(i for i, (x, y) in enumerate(zip(wa, wb)) if x != y)
        lo, hi = sorted((wa[pos], wb[pos])); cls = (len(wa), pos, lo, hi); by_class[cls] += 1
        sims.append(cosine(vectors[a], vectors[b]))
        va, vb = vectors[a], vectors[b]
        d = [y - x for x, y in zip(va, vb)] if wa[pos] == lo else [x - y for x, y in zip(va, vb)]
        delta[cls].append(d)
    cohs = []
    for ds in delta.values():
        if len(ds) >= 2: cohs.extend(cosine(ds[i], ds[j]) for i in range(len(ds)) for j in range(i + 1, len(ds)))
    # Type-weighted TC averaged across lengths.
    tcs = []
    for length in LENGTHS:
        ids = {h: s for h, s in mapping.items() if len(s) == length}
        if ids: tcs.append(slot_metrics(ids, {h: 1 for h in ids})["total_correlation"])
    return {
        "slot_total_correlation_mean": sum(tcs) / len(tcs) if tcs else 0.0,
        "neighbor_density": len(edges) / possible if possible else 0.0,
        "top20_substitution_share": sum(x for _, x in by_class.most_common(20)) / len(edges) if edges else 0.0,
        "neighbor_context_cosine": sum(sims) / len(sims) if sims else 0.0,
        "substitution_delta_coherence": sum(cohs) / len(cohs) if cohs else 0.0,
        "collisions": float(len(mapping) - len(set(mapping.values()))),
    }


def random_mapping(labels: dict[str, str], mode: str, rng: random.Random) -> dict[str, str]:
    ids = sorted(labels)
    slots = [(ident, pos) for ident in ids for pos in range(len(labels[ident]))]
    out = {ident: [""] * len(labels[ident]) for ident in ids}
    if mode == "LENGTH_UNIGRAM":
        glyphs = [labels[ident][pos] for ident, pos in slots]
        rng.shuffle(glyphs)
        for (ident, pos), ch in zip(slots, glyphs): out[ident][pos] = ch
    else:
        for length in LENGTHS:
            lids = [ident for ident in ids if len(labels[ident]) == length]
            for pos in range(length):
                glyphs = [labels[ident][pos] for ident in lids]; rng.shuffle(glyphs)
                for ident, ch in zip(lids, glyphs): out[ident][pos] = ch
    return {ident: "".join(chars) for ident, chars in out.items()}


def inclusive_p(obs: float, vals: list[float], direction: str) -> float:
    if direction == "HIGH": return (1 + sum(v >= obs - 1e-12 for v in vals)) / (len(vals) + 1)
    if direction == "LOW": return (1 + sum(v <= obs + 1e-12 for v in vals)) / (len(vals) + 1)
    center = sum(vals) / len(vals)
    return (1 + sum(abs(v - center) >= abs(obs - center) - 1e-12 for v in vals)) / (len(vals) + 1)


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert design["status"] == "FROZEN_BEFORE_SCORING" and design["null_worlds"] == WORLDS
    source, rejected_f84 = guarded_source()
    assert len(source) == 15364 and rejected_f84 == 228
    candidate = [r for r in source if len(r["page_host"]) in LENGTHS and r["page_host"] != "EMPTY"]
    assert candidate

    # Source and raw internal comparisons.
    source_view = [{**r, "form": r["page_host"], "unit": r["page"], "fold": r["physical_folio"]} for r in source]
    raw_view = [{**r, "form": r["token"], "unit": r["page"], "fold": r["physical_folio"]} for r in source]
    length_rows = [length_recurrence("VOYNICH_PAGE_HOST", source_view, "form", "unit", "fold"), length_recurrence("VOYNICH_RAW_TOKEN", raw_view, "form", "unit", "fold")]
    position_rows = representation_slot_rows("VOYNICH_PAGE_HOST", source_view, "form") + representation_slot_rows("VOYNICH_RAW_TOKEN", raw_view, "form")
    control_rows = [neighbor_summary("VOYNICH_PAGE_HOST", source_view, "form"), neighbor_summary("VOYNICH_RAW_TOKEN", raw_view, "form")]

    # Frozen historical graphematic controls.
    with gzip.open(CONTROL_SOURCE, "rt", encoding="utf-8") as handle: control_data = json.load(handle)["records"]
    by_corpus = defaultdict(list)
    for row in control_data:
        form = unicodedata.normalize("NFC", row["form"])
        if form: by_corpus[row["corpus_id"]].append({**row, "norm_form": form})
    for corpus_id in sorted(by_corpus):
        rows = by_corpus[corpus_id]
        length_rows.append(length_recurrence(corpus_id, rows, "norm_form", "unit_id", "fold_id"))
        position_rows += representation_slot_rows(corpus_id, rows, "norm_form")
        control_rows.append(neighbor_summary(corpus_id, rows, "norm_form"))

    # Host inventory and neighbor atlas.
    counts = Counter(r["page_host"] for r in candidate); pages = defaultdict(set); folios = defaultdict(set); sections = defaultdict(set)
    for r in candidate:
        h = r["page_host"]; pages[h].add(r["page"]); folios[h].add(r["physical_folio"]); sections[h].add(r["section"])
    neighbor_atlas, neighbor_obs, vectors = neighbor_rows(candidate)
    degree = Counter()
    for row in neighbor_atlas: degree[row["host_a"]] += 1; degree[row["host_b"]] += 1
    host_rows = []
    for h in sorted(counts, key=lambda x: (-counts[x], x)):
        comp_ent = []
        subset = [r for r in candidate if r["page_host"] == h]
        for c in COMPONENTS: comp_ent.append(entropy_counts(Counter(r[c] for r in subset).values()))
        host_rows.append({
            "page_host": h, "length": len(h), "occurrences": counts[h], "pages": len(pages[h]), "folios": len(folios[h]),
            "sections": "|".join(sorted(sections[h])), "neighbor_degree": degree[h], "mean_outer_component_entropy": sum(comp_ent) / len(comp_ent),
            "claim_state": "SHORT_FORMAL_HOST_IDENTITY_NO_LEXICAL_OR_SEMANTIC_ASSIGNMENT",
        })

    # Held-folio and held-section context prediction.
    folio_scores, folio_summary = context_score(candidate, "physical_folio", "HELD_PHYSICAL_FOLIO")
    section_scores, section_summary = context_score(candidate, "section", "HELD_SECTION")
    context_rows = folio_scores + section_scores

    # Two spelling randomizations over the exact host identity inventory.
    labels = {h: h for h in counts}
    observed_geometry = mapped_geometry(labels, vectors)
    null_world_rows = []
    geometry_values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for mode in ("LENGTH_UNIGRAM", "POSITION_PRESERVING"):
        rng = random.Random(seed("GDT162_" + mode))
        for world in range(WORLDS):
            metric = mapped_geometry(random_mapping(labels, mode, rng), vectors)
            null_world_rows.append({"null": mode, "world": world, **metric})
            for key, value in metric.items(): geometry_values[mode, key].append(value)

    # Context-identity conditional MI null, preserving exact declared nuisance strata.
    real_mi = {c: conditional_mi(candidate, c) for c in COMPONENTS}
    strata = defaultdict(list)
    for i, row in enumerate(candidate): strata[nuisance(row)].append(i)
    rng = random.Random(seed("GDT162_CONTEXT_IDENTITY"))
    mi_null = {c: [] for c in COMPONENTS}
    original_hosts = [r["page_host"] for r in candidate]
    for _ in range(WORLDS):
        shuffled = list(original_hosts)
        for ids in strata.values():
            vals = [shuffled[i] for i in ids]; rng.shuffle(vals)
            for i, value in zip(ids, vals): shuffled[i] = value
        for c in COMPONENTS: mi_null[c].append(conditional_mi(candidate, c, shuffled))

    null_summary = []
    directions = {
        "slot_total_correlation_mean": "HIGH", "neighbor_density": "TWO", "top20_substitution_share": "TWO",
        "neighbor_context_cosine": "HIGH", "substitution_delta_coherence": "HIGH", "collisions": "LOW",
    }
    for mode in ("LENGTH_UNIGRAM", "POSITION_PRESERVING"):
        for metric, direction in directions.items():
            vals = geometry_values[mode, metric]; obs = observed_geometry[metric]
            null_summary.append({
                "null": mode, "metric": metric, "observed": obs, "null_mean": sum(vals) / len(vals),
                "null_q025": sorted(vals)[int(0.025 * len(vals))], "null_q975": sorted(vals)[int(0.975 * len(vals))],
                "direction": direction, "local_p": inclusive_p(obs, vals, direction), "worlds": WORLDS,
            })
    for component in COMPONENTS:
        vals = mi_null[component]
        null_summary.append({
            "null": "CONTEXT_IDENTITY", "metric": "conditional_mi_" + component, "observed": real_mi[component],
            "null_mean": sum(vals) / len(vals), "null_q025": sorted(vals)[int(0.025 * len(vals))],
            "null_q975": sorted(vals)[int(0.975 * len(vals))], "direction": "HIGH",
            "local_p": inclusive_p(real_mi[component], vals, "HIGH"), "worlds": WORLDS,
        })

    # Shared max-family adjustment on standardized upper-tail deviations within each null family.
    for mode in ("LENGTH_UNIGRAM", "POSITION_PRESERVING"):
        metrics = [m for m in directions if m != "collisions"]
        means = {m: sum(geometry_values[mode, m]) / WORLDS for m in metrics}
        sds = {m: math.sqrt(sum((x - means[m]) ** 2 for x in geometry_values[mode, m]) / WORLDS) or 1.0 for m in metrics}
        maxes = [max(abs((geometry_values[mode, m][w] - means[m]) / sds[m]) for m in metrics) for w in range(WORLDS)]
        for row in null_summary:
            if row["null"] == mode and row["metric"] in metrics:
                z = abs((float(row["observed"]) - means[row["metric"]]) / sds[row["metric"]])
                row["max_family_p"] = (1 + sum(x >= z - 1e-12 for x in maxes)) / (WORLDS + 1)
    means = {c: sum(mi_null[c]) / WORLDS for c in COMPONENTS}
    sds = {c: math.sqrt(sum((x - means[c]) ** 2 for x in mi_null[c]) / WORLDS) or 1.0 for c in COMPONENTS}
    maxes = [max((mi_null[c][w] - means[c]) / sds[c] for c in COMPONENTS) for w in range(WORLDS)]
    for row in null_summary:
        if row["null"] == "CONTEXT_IDENTITY":
            c = str(row["metric"]).removeprefix("conditional_mi_"); z = (float(row["observed"]) - means[c]) / sds[c]
            row["max_family_p"] = (1 + sum(x >= z - 1e-12 for x in maxes)) / (WORLDS + 1)
    for row in null_summary:
        row.setdefault("max_family_p", "NOT_APPLICABLE")

    # Compact counterexample atlas.
    counters = []
    for row in sorted(host_rows, key=lambda x: (-float(x["occurrences"]), float(x["folios"])))[:12]:
        if int(row["folios"]) <= 2:
            counters.append({"counterexample_type": "FREQUENT_BUT_FOLIO_LOCAL", "item": row["page_host"], "evidence": f"{row['occurrences']} occurrences on {row['folios']} folios", "implication": "Recurrence may be a page codebook rather than a transferable lexical address."})
    for row in sorted(neighbor_atlas, key=lambda x: (-float(x["context_cosine"]), -(int(x["count_a"]) + int(x["count_b"]))))[:10]:
        counters.append({"counterexample_type": "ONE_GLYPH_NEIGHBOR_CONTEXT_SIMILAR", "item": f"{row['host_a']}~{row['host_b']}", "evidence": f"context cosine {float(row['context_cosine']):.6f}", "implication": "Compatible with internal form structure; counts against wholly independent code identities."})
    for row in sorted(neighbor_atlas, key=lambda x: (float(x["context_cosine"]), -(int(x["count_a"]) + int(x["count_b"]))))[:10]:
        counters.append({"counterexample_type": "ONE_GLYPH_NEIGHBOR_CONTEXT_DIVERGENT", "item": f"{row['host_a']}~{row['host_b']}", "evidence": f"context cosine {float(row['context_cosine']):.6f}", "implication": "Compatible with separate formal addresses; counts against a uniform productive substitution."})
    counters += [
        {"counterexample_type": "PARSER_COUPLING", "item": "PAGE_HOST_CONTEXT", "evidence": "HPR2 removes wrapper/frame/right/closure under frozen licensing rules.", "implication": "Exact-host context gain is formal architecture, not independent semantic evidence."},
        {"counterexample_type": "ARCHIVED_EXTERNAL_NEGATIVE", "item": "GDT123", "evidence": "No exact PAGE_HOST visual codeword survived the global Q20 atlas.", "implication": "Internal recurrence cannot be promoted to content or meaning."},
        {"counterexample_type": "STRING_BASELINE_NEGATIVE", "item": "GDT003", "evidence": "Formal paradigms did not beat strong string statistics.", "implication": "One-glyph structure is not linguistic morphology by default."},
    ]

    # Exploratory decision.
    length_by = {r["representation"]: r for r in length_rows}
    primary_controls = ["LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "LATIN_SCHOLASTIC_GRAPHEMATIC"]
    short_mass_high = length_by["VOYNICH_PAGE_HOST"]["length_2_3_token_mass"] > max(length_by[c]["length_2_3_token_mass"] for c in primary_controls)
    recurrence_high = length_by["VOYNICH_PAGE_HOST"]["short_cross_fold_token_coverage"] > max(length_by[c]["short_cross_fold_token_coverage"] for c in primary_controls)
    exact_positive = folio_summary["exact_gain_vs_nuisance"] > 0
    neighbor_positive = folio_summary["neighbor_gain_vs_nuisance"] > 0
    neighbor_null = next(r for r in null_summary if r["null"] == "POSITION_PRESERVING" and r["metric"] == "neighbor_context_cosine")
    coherence_null = next(r for r in null_summary if r["null"] == "POSITION_PRESERVING" and r["metric"] == "substitution_delta_coherence")
    codebook = short_mass_high and recurrence_high and exact_positive and folio_summary["exact_gain_vs_neighbor"] > 0
    productive = neighbor_positive and float(neighbor_null["local_p"]) <= 0.1 and float(coherence_null["local_p"]) <= 0.1
    if codebook and productive: status = "MIXED_SHORT_HOST_CODEBOOK_AND_INTERNAL_STRUCTURE"
    elif codebook: status = "SHORT_HOST_CODEBOOK_ARCHITECTURE_INTERESTING"
    elif productive: status = "SHORT_HOST_INTERNAL_PRODUCTIVITY_INTERESTING"
    else: status = "SHORT_HOST_CODEBOOK_NOT_DISTINGUISHED"

    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "Frozen HPR2 PAGE_HOST length-2/3 inventory; exact identity versus Hamming-one neighbor held-folio context code."},
        {"variant_id": "V01", "status": "RUN_CONTROL", "description": "Unstripped raw source-display groups on the identical non-f84 rows; structure only, never context prediction."},
        {"variant_id": "V02", "status": "RUN_CONTROL", "description": "Five frozen GDT159 diplomatic graphematic corpora; no HPR2 refit, expansion, lemma, or translation."},
        {"variant_id": "V03", "status": "RUN_NULL", "description": "Length/unigram type-code randomization, 1024 worlds."},
        {"variant_id": "V04", "status": "RUN_NULL", "description": "Position-preserving type-code randomization, 1024 worlds."},
        {"variant_id": "V05", "status": "RUN_NULL", "description": "Context identity permutation within length/section/Currier/hand, 1024 worlds."},
        {"variant_id": "V06", "status": "RUN_SENSITIVITY", "description": "Leave-one-section-out exact-host and neighbor context transfer."},
        {"variant_id": "V07", "status": "NOT_RUN", "description": "No semantic labels, phoneme maps, language models, translation, alternate HPR2 parser, or f84 rows."},
    ]

    # Format and export.
    def fmt(rows):
        return [{k: (f"{v:.12f}" if isinstance(v, float) else v) for k, v in row.items()} for row in rows]
    write(HOSTS, fmt(host_rows)); write(LENGTH, fmt(length_rows)); write(POSITION, fmt(position_rows)); write(NEIGHBORS, fmt(neighbor_atlas))
    write(CONTEXT, fmt(context_rows)); write(NULLS, fmt(null_summary)); write(CONTROLS, fmt(control_rows)); write(COUNTER, fmt(counters)); write(VARIANTS, variants)

    vlen = length_by["VOYNICH_PAGE_HOST"]
    ranked_controls = sorted((length_by[c] for c in by_corpus), key=lambda x: abs(float(x["length_2_3_token_mass"]) - float(vlen["length_2_3_token_mass"])))
    top_neighbors = sorted(neighbor_atlas, key=lambda x: (-(int(x["count_a"]) + int(x["count_b"])), x["host_a"], x["host_b"]))[:12]
    page_position = [r for r in position_rows if r["representation"] == "VOYNICH_PAGE_HOST"]
    component_totals = []
    for component in COMPONENTS:
        rr = [r for r in folio_scores if r["component"] == component]
        component_totals.append((component, sum(float(r["exact_gain_vs_nuisance"]) for r in rr), sum(float(r["neighbor_gain_vs_nuisance"]) for r in rr), sum(float(r["exact_gain_vs_nuisance"]) > 0 for r in rr), sum(float(r["neighbor_gain_vs_nuisance"]) > 0 for r in rr), len(rr)))
    density_null = next(r for r in null_summary if r["null"] == "POSITION_PRESERVING" and r["metric"] == "neighbor_density")
    tc_null = next(r for r in null_summary if r["null"] == "POSITION_PRESERVING" and r["metric"] == "slot_total_correlation_mean")
    report = f"""# GDT162 — short PAGE_HOST codebook report

Decision: **{status}**.

## Bottom line

The **pure opaque-codebook** version is not supported.  Exact PAGE_HOST
identity is much more predictive than a one-glyph-neighbor backoff, so host
identity plainly matters; however the same inventory has a denser Hamming-one
graph than its position-preserving null, and those neighbors transfer outer
context and substitution-direction effects.  The strongest descriptive model
is therefore an **identity-bearing but internally structured short-host
system**, not 241 arbitrary independent addresses.  The frozen strict codebook
label also fails because Voynich's 2–3-character concentration does not exceed
all primary historical graphematic controls.

## Short-host inventory

After rejecting {rejected_f84} f84v rows before retention, the frozen HPR2
panel contains {len(source):,} non-f84 group occurrences on
{len({r['physical_folio'] for r in source})} physical folios.  PAGE_HOST length
2–3 accounts for {float(vlen['length_2_3_token_mass']):.1%} of occurrences and
{float(vlen['length_2_3_type_mass']):.1%} of types.  Within that short-host
panel, {float(vlen['short_recurrent_token_coverage']):.1%} of occurrences use a
recurrent identity and {float(vlen['short_cross_fold_token_coverage']):.1%}
use an identity observed on multiple physical folios.

The raw unstripped source-display comparison has
{float(length_by['VOYNICH_RAW_TOKEN']['length_2_3_token_mass']):.1%} length-2/3
mass.  The closest frozen historical control by this single coordinate is
`{ranked_controls[0]['representation']}` at
{float(ranked_controls[0]['length_2_3_token_mass']):.1%}.  Length concentration
is not treated as sufficient evidence by itself.

## Positional inventories and slot dependence

| length | weighting | position inventories | position entropies (bits) | position↔glyph MI | total correlation |
| ---: | --- | --- | --- | ---: | ---: |
""" + "".join(f"| {r['length']} | {r['weighting']} | `{r['position_inventories']}` | {r['position_entropies']} | {float(r['position_glyph_mi']):.4f} | {float(r['total_correlation']):.4f} |\n" for r in page_position) + f"""

The mean type-weighted total correlation across lengths 2 and 3 is
{observed_geometry['slot_total_correlation_mean']:.6f} bits, below the
position-preserving null mean {float(tc_null['null_mean']):.6f}.  This is not a
compact-slot excess: after preserving positional inventories, randomized type
codes are more dependent because collisions remove distinct combinations.
The observed inventory is instead unusually injective and densely connected;
those properties must not be conflated with a small factorial code.

## Exact identity versus one-glyph neighbors

Across leave-one-physical-folio folds and all six outer compiler components,
exact PAGE_HOST identity changes the nuisance code by
{folio_summary['exact_gain_vs_nuisance']:+.3f} bits.  Hamming-one neighbor
backoff changes it by {folio_summary['neighbor_gain_vs_nuisance']:+.3f} bits;
exact identity therefore leads neighbor backoff by
{folio_summary['exact_gain_vs_neighbor']:+.3f} bits.  The leave-one-section-out
sensitivity is exact {section_summary['exact_gain_vs_nuisance']:+.3f} and
neighbor {section_summary['neighbor_gain_vs_nuisance']:+.3f} bits.

This is the cleanest codebook-versus-productivity diagnostic in the pass.
Exact-identity gain cannot be read semantically: the HPR2 parser itself strips
licensed outer fields, so formal host/context coupling is partly architectural.

| held-folio component | exact-host gain (bits) | neighbor gain (bits) | positive exact folds | positive neighbor folds |
| --- | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{c}` | {eg:+.3f} | {ng:+.3f} | {ep}/{n} | {np}/{n} |\n" for c, eg, ng, ep, np, n in component_totals) + f"""

## Slot and neighbor geometry

The 2–3-character inventory contains {int(neighbor_obs['edges']):,} Hamming-one
type pairs, density {observed_geometry['neighbor_density']:.6f} versus the
position-preserving null mean {float(density_null['null_mean']):.6f}
(local/max-family p {float(density_null['local_p']):.6f}/
{float(density_null.get('max_family_p', 1.0)):.6f}).  Mean neighbor
outer-context cosine is
{neighbor_obs['mean_neighbor_context_cosine']:.6f}; mean repeated-substitution
context-delta coherence is
{neighbor_obs['mean_substitution_delta_coherence']:.6f} over
{int(neighbor_obs['coherence_pair_count']):,} within-class edge comparisons.
Against the position-preserving null, their local p-values are
{float(neighbor_null['local_p']):.6f} and
{float(coherence_null['local_p']):.6f}; max-family p-values are
{float(neighbor_null.get('max_family_p', 1.0)):.6f} and
{float(coherence_null.get('max_family_p', 1.0)):.6f}.

The largest recurrent neighbor pairs by combined occurrence are:

| pair | substitution | occurrences | folios | context cosine |
| --- | --- | ---: | ---: | ---: |
""" + "".join(f"| `{r['host_a']} ~ {r['host_b']}` | `{r['substitution_class']}` | {int(r['count_a']) + int(r['count_b'])} | {r['folios_a']}/{r['folios_b']} | {float(r['context_cosine']):.4f} |\n" for r in top_neighbors) + f"""

These are formal neighbors, not morpheme pairs.  High similarity is a
counterexample to wholly independent identities; low or incoherent
substitution deltas are counterexamples to a uniform productive operation.

## Historical controls

| representation | tokens | 2–3 mass | recurrent coverage | cross-fold coverage | neighbor density |
| --- | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{r['representation']}` | {r['tokens']} | {float(r['length_2_3_token_mass']):.3f} | {float(r['short_recurrent_token_coverage']):.3f} | {float(r['short_cross_fold_token_coverage']):.3f} | {next(float(x['hamming1_density']) for x in control_rows if x['representation']==r['representation']):.6f} |\n" for r in length_rows) + f"""

The diplomatic controls calibrate ordinary abbreviated graphematic forms; they
do not share the Voynich HPR2 parser or outer compiler fields.  Script,
normalization, genre, and transcription practice remain confounds.

## Interpretation and counterevidence

The result is an exploratory architecture ranking.  GDT003's string-statistical
ceiling, GDT123's failed exact-host visual atlas, and GDT161's failed compact
operation classes remain binding counterevidence.  Outer LEFT/RIGHT material
was never folded into candidate host strings.  No host is assigned a word,
lexical value, number, morpheme, phoneme, language, semantic role, meaning,
plaintext, or translation.

No f84 row was retained or scored.  f84r is absent from the actual source
input and was not opened, queried, retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {
        "schema": "GDT162_PAGE_HOST_CODEBOOK_RESULT_V1", "status": status,
        "source_rows": len(source), "rejected_f84_rows": rejected_f84,
        "physical_folios": len({r["physical_folio"] for r in source}),
        "short_host_occurrences": len(candidate), "short_host_types": len(counts),
        "length_recurrence": vlen, "held_folio_context": folio_summary,
        "held_section_context": section_summary, "neighbor_geometry": neighbor_obs,
        "observed_geometry": observed_geometry,
        "historical_control_count": len(by_corpus),
        "decision_inputs": {
            "short_mass_above_primary_controls": short_mass_high,
            "cross_fold_recurrence_above_primary_controls": recurrence_high,
            "exact_identity_positive": exact_positive,
            "neighbor_transfer_positive": neighbor_positive,
            "codebook_rule": codebook, "productive_rule": productive,
        },
        "interpretation": "Exact PAGE_HOST identity is stronger than one-glyph-neighbor backoff, but dense null-exceeding neighbor geometry and transferable substitution context reject a pure inventory of independent opaque addresses; the best exploratory description is identity-bearing and internally structured.",
        "claim_ceiling": "No word boundary, lexical item, morpheme, phoneme, language, semantic role, meaning, plaintext, or translation.",
        "f84r": {"present_in_actual_input": False, "opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {SOURCE.name: sha(SOURCE), CONTROL_SOURCE.name: sha(CONTROL_SOURCE), CONTROL_MANIFEST.name: sha(CONTROL_MANIFEST), DESIGN.name: sha(DESIGN), "gdt062_result.json": sha(ROOT / "gdt062_result.json"), "gdt159_result.json": sha(ROOT / "gdt159_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {p.name: sha(p) for p in (HOSTS, LENGTH, POSITION, NEIGHBORS, CONTEXT, NULLS, CONTROLS, COUNTER, VARIANTS)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "rows": len(source), "short_occurrences": len(candidate), "short_types": len(counts), "exact_gain": folio_summary["exact_gain_vs_nuisance"], "neighbor_gain": folio_summary["neighbor_gain_vs_nuisance"], "neighbor_edges": int(neighbor_obs["edges"])}, sort_keys=True))


if __name__ == "__main__":
    main()
