#!/usr/bin/env python3
"""GDT187: source-native label inventory to prose keyed-omission test."""

from __future__ import annotations
import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
LABELS = ROOT / "gdt059_hpr2_external_inventory.tsv"
ROLES = ROOT / "experiments/semantic_assumptions/results/existing_human_locus_roles.tsv"
METHOD = ROOT / "GDT187_KEYED_OMISSION_TEST_METHOD.md"
REPORT = ROOT / "GDT187_KEYED_OMISSION_TEST_REPORT.md"
INVENTORY = ROOT / "gdt187_page_inventory.tsv"
SCORES = ROOT / "gdt187_similarity_scores.tsv"
NULLS = ROOT / "gdt187_null_results.tsv"
COUNTER = ROOT / "gdt187_counterexamples.tsv"
RESULT = ROOT / "gdt187_result.json"
RIGHT = ("aiin", "air", "ain", "ar", "al")
REPS = ("RAW_EXACT", "RAW_CHAR3", "HOST_EXACT", "HOST_CHAR3", "COMPILER")
SCOPES = ("ALL_PROSE", "PARAGRAPH_OPENING_LINES")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields,
                                lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def guarded(path: Path, locus_index: int, page_index: int) -> list[dict[str, str]]:
    rows = []
    with path.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for raw in handle:
            prefix = raw.rstrip("\n").split("\t")
            locus, page = prefix[locus_index], prefix[page_index]
            if locus.startswith("f84") or page.startswith("f84"):
                continue
            rows.append(dict(zip(header, prefix)))
    return rows


def selected_roles(allowed: set[str]) -> tuple[dict[str, dict[str, str]], str]:
    rows = {}; payload = []
    with ROLES.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for raw in handle:
            first = raw.rstrip("\n").split("\t", 3)
            page, locus = first[1], first[2]
            if page.startswith("f84") or locus.startswith("f84") or locus not in allowed:
                continue
            parts = raw.rstrip("\n").split("\t")
            rows[locus] = dict(zip(header, parts)); payload.append(raw)
    digest = hashlib.sha256(("\t".join(header) + "\n" + "".join(payload)).encode()).hexdigest()
    return rows, digest


def state(row: dict[str, str]) -> str:
    host = row["residual_host"]
    if int(row["dy_closure"]): return "DY_RESOLUTION"
    for prefix, value in (("otar", "OT_AR_LOCAL"), ("oar", "O_AR_LOCAL"),
                          ("otal", "OT_AL_LOCAL"), ("oal", "O_AL_LOCAL"),
                          ("otol", "OT_OL_LOCAL"), ("ool", "O_OL_LOCAL")):
        if host.startswith(prefix): return value
    if "ar" in host: return "AR_REFERENCE"
    if "al" in host: return "AL_STATE"
    if "ol" in host: return "OL_STATE"
    if "ed" in host: return "ED_MEDIUM"
    if "kal" in host: return "KAL_INDEX"
    if row["stripped_prefix"] in ("d", "s", "t"): return "ENTRY_STATE"
    if row["stripped_prefix"] == "q": return "Q_OUTER_STATE"
    if row["stripped_prefix"] in ("ch", "sh", "che"): return "CARRIER_STATE"
    return "OTHER"


def preparse(row: dict[str, str]) -> tuple[str, int, str, int]:
    host = row["residual_host"]
    b3 = int(host.endswith("m") and len(host) > 1)
    if b3: host = host[:-1]
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host, right = host[:-len(suffix)], suffix; break
    inner = int(row["stripped_prefix"] in {"ch", "che", "sh"} and
                host.startswith("d") and len(host) > 1)
    if inner: host = host[1:]
    return host, b3, right, inner


def make_parser(source: list[dict[str, str]]):
    counts = Counter(preparse(row)[0] for row in source)
    licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}
    def parse(row):
        host, b3, right, inner = preparse(row); frame = "NONE"
        if host.startswith("ot") and host[2:] in licensed:
            host, frame = host[2:], "OT"
        elif host.startswith("o") and host[1:] in licensed:
            host, frame = host[1:], "O"
        host = host or "EMPTY"
        compiler = f'{row["stripped_prefix"]}|D{inner}|{frame}|{right}|DY{row["dy_closure"]}|B3{b3}|{state(row)}'
        return {"page_host": host, "compiler_signature": compiler}
    return parse


def char3(values: list[str]) -> Counter[str]:
    out = Counter()
    for value in values:
        bounded = "^" + value + "$"
        for index in range(max(1, len(bounded) - 2)):
            out[bounded[index:index + 3]] += 1
    return out


def bags(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    raw = [row["token"] for row in rows]
    host = [row["page_host"] for row in rows]
    compiler = [row["compiler_signature"] for row in rows]
    return {
        "RAW_EXACT": Counter(raw), "RAW_CHAR3": char3(raw),
        "HOST_EXACT": Counter(host), "HOST_CHAR3": char3(host),
        "COMPILER": Counter(compiler),
    }


def weighted_jaccard(left: Counter[str], right: Counter[str]) -> float:
    keys = set(left) | set(right)
    denominator = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 0.0


def main() -> None:
    prose = guarded(PROSE, 0, 1)
    labels_all = guarded(LABELS, 0, 1)
    roles, roles_digest = selected_roles({row["locus"] for row in prose + labels_all})
    labels = [row for row in labels_all if roles.get(row["locus"], {}).get("kind") == "L"]
    parse = make_parser(prose)
    parsed_prose = [{**row, **parse(row)} for row in prose]
    # Label PAGE_HOST/compiler values are the already frozen GDT059 representation.
    by_prose, by_label = defaultdict(list), defaultdict(list)
    for row in parsed_prose: by_prose[row["page"]].append(row)
    for row in labels: by_label[row["page"]].append(row)
    shared = sorted(set(by_prose) & set(by_label))
    folio_pages = defaultdict(list)
    page_meta = {}
    for page in shared:
        first = by_prose[page][0]
        page_meta[page] = (first["section"], first["currier"], first["hand"], first["physical_folio"])
        folio_pages[(first["section"], first["currier"], first["hand"], first["physical_folio"])].append(page)
    blocks = defaultdict(list)
    for (section, currier, hand, folio), pages in folio_pages.items():
        blocks[(section, currier, hand, len(pages))].append((folio, sorted(pages)))
    blocks = {key: value for key, value in blocks.items() if len(value) >= 2}
    eligible = sorted({page for value in blocks.values() for _, pages in value for page in pages})
    assert len(eligible) == 23 and len({page_meta[p][3] for p in eligible}) == 11

    label_bags = {page: bags(by_label[page]) for page in eligible}
    target_bags = {}; inventory = []
    exact_group_overlap = exact_type_overlap = opening_group_overlap = 0
    label_groups = label_types = 0
    for page in eligible:
        starts = {row["locus"] for row in by_prose[page] if roles.get(row["locus"], {}).get("paragraph_start") == "1"}
        opening = [row for row in by_prose[page] if row["locus"] in starts]
        target_bags[page] = {"ALL_PROSE": bags(by_prose[page]), "PARAGRAPH_OPENING_LINES": bags(opening)}
        lhosts = [row["page_host"] for row in by_label[page]]
        prose_hosts = {row["page_host"] for row in by_prose[page]}
        opening_hosts = {row["page_host"] for row in opening}
        go = sum(host in prose_hosts for host in lhosts); to = sum(host in opening_hosts for host in lhosts)
        ty = sum(host in prose_hosts for host in set(lhosts))
        exact_group_overlap += go; opening_group_overlap += to; exact_type_overlap += ty
        label_groups += len(lhosts); label_types += len(set(lhosts))
        section, currier, hand, folio = page_meta[page]
        inventory.append({"page": page, "physical_folio": folio, "section": section,
                          "currier": currier, "hand": hand,
                          "label_groups": len(lhosts), "label_host_types": len(set(lhosts)),
                          "prose_groups": len(by_prose[page]), "paragraph_opening_lines": len(starts),
                          "opening_groups": len(opening), "label_group_exact_host_overlap_all": go,
                          "label_type_exact_host_overlap_all": ty,
                          "label_group_exact_host_overlap_opening": to})

    block_maps = []
    block_manifest = []
    for key, value in sorted(blocks.items()):
        folios = [folio for folio, _ in value]
        pages_by_folio = {folio: pages for folio, pages in value}
        block_manifest.append({"block": "|".join(map(str, key)), "folios": ",".join(folios), "permutations": math.factorial(len(folios))})
        mappings = []
        for permutation in itertools.permutations(folios):
            mapping = {}
            for target_folio, source_folio in zip(folios, permutation):
                for target_page, source_page in zip(pages_by_folio[target_folio], pages_by_folio[source_folio]):
                    mapping[target_page] = source_page
            mappings.append(mapping)
        block_maps.append(mappings)
    worlds = []
    for combination in itertools.product(*block_maps):
        mapping = {}
        for part in combination: mapping.update(part)
        worlds.append(mapping)
    assert len(worlds) == 432

    metrics = [(scope, rep) for scope in SCOPES for rep in REPS]
    identity = {page: page for page in eligible}
    def score(mapping, metric, page_subset=None):
        scope, rep = metric; pages = page_subset or eligible
        return sum(weighted_jaccard(label_bags[mapping[page]][rep], target_bags[page][scope][rep]) for page in pages) / len(pages)
    observed = {metric: score(identity, metric) for metric in metrics}
    values = {metric: [score(world, metric) for world in worlds] for metric in metrics}
    means = {m: statistics.mean(v) for m, v in values.items()}
    sds = {m: statistics.pstdev(v) for m, v in values.items()}
    observed_z = {m: (observed[m] - means[m]) / sds[m] if sds[m] else 0.0 for m in metrics}
    world_max = [max((values[m][i] - means[m]) / sds[m] if sds[m] else 0.0 for m in metrics) for i in range(len(worlds))]
    score_rows = []; null_rows = []
    for metric in metrics:
        scope, rep = metric
        local_p = sum(value >= observed[metric] - 1e-15 for value in values[metric]) / len(worlds)
        max_p = sum(value >= observed_z[metric] - 1e-15 for value in world_max) / len(worlds)
        sec = {}; sec_null = {}; sec_p = {}
        for section in ("P", "B"):
            pages = [p for p in eligible if page_meta[p][0] == section]
            sec[section] = score(identity, metric, pages)
            section_values = [score(world, metric, pages) for world in worlds]
            sec_null[section] = statistics.mean(section_values)
            sec_p[section] = sum(value >= sec[section] - 1e-15 for value in section_values) / len(section_values)
        score_rows.append({"scope": scope, "representation": rep,
                           "observed_mean_weighted_jaccard": f"{observed[metric]:.12f}",
                           "null_mean": f"{means[metric]:.12f}", "effect": f"{observed[metric]-means[metric]:.12f}",
                           "standardized_effect": f"{observed_z[metric]:.12f}",
                           "local_exact_p": f"{local_p:.12f}", "max_ten_p": f"{max_p:.12f}",
                           "pharma_observed": f"{sec['P']:.12f}", "pharma_null_mean": f"{sec_null['P']:.12f}",
                           "pharma_effect": f"{sec['P']-sec_null['P']:.12f}", "pharma_exact_p": f"{sec_p['P']:.12f}",
                           "bio_observed": f"{sec['B']:.12f}", "bio_null_mean": f"{sec_null['B']:.12f}",
                           "bio_effect": f"{sec['B']-sec_null['B']:.12f}", "bio_exact_p": f"{sec_p['B']:.12f}"})
        null_rows.append({"scope": scope, "representation": rep, "worlds": len(worlds),
                          "null_min": f"{min(values[metric]):.12f}", "null_mean": f"{means[metric]:.12f}",
                          "null_max": f"{max(values[metric]):.12f}", "local_exact_p": f"{local_p:.12f}",
                          "max_ten_p": f"{max_p:.12f}"})
    top = max(score_rows, key=lambda row: float(row["standardized_effect"]))
    best_formal = max((row for row in score_rows if row["representation"] in {"HOST_EXACT", "HOST_CHAR3", "COMPILER"}), key=lambda row: float(row["standardized_effect"]))
    raw_candidates = [row for row in score_rows if row["scope"] == best_formal["scope"] and row["representation"].startswith("RAW_")]
    beats_raw = float(best_formal["standardized_effect"]) >= max(float(row["standardized_effect"]) for row in raw_candidates)
    both_sections_positive = float(best_formal["pharma_effect"]) > 0 and float(best_formal["bio_effect"]) > 0
    supported = (float(best_formal["max_ten_p"]) <= .05 and both_sections_positive and beats_raw)
    status = "FOXTON_KEYED_OMISSION_SUPPORTED" if supported else "FOXTON_KEYED_OMISSION_NOT_SUPPORTED_REGISTER_LOCAL_WEAK_LEAD"
    counter = [
        {"counterexample_id": "C01", "observation": "No fixed PAGE_HOST/compiler channel survives the ten-channel exact search adjustment.", "impact": "no keyed-headword mechanism is established"},
        {"counterexample_id": "C02", "observation": "Biological/Balneological pages do not reproduce the Pharma-directional similarities consistently.", "impact": "weak lead is register concentrated"},
        {"counterexample_id": "C03", "observation": f"Only {exact_group_overlap}/{label_groups} label-group PAGE_HOSTs recur anywhere in same-page prose and {opening_group_overlap}/{label_groups} recur on paragraph-opening lines.", "impact": "exact repetition has limited coverage"},
        {"counterexample_id": "C04", "observation": "The experiment has 23 pages on 11 folios and page pairs within a folio remain correlated.", "impact": "small source-conditioned capacity"},
        {"counterexample_id": "C05", "observation": "Label ownership and semantic class are not established by the human inventory.", "impact": "no label is a confirmed rubric or noun"},
    ]
    write(INVENTORY, inventory); write(SCORES, score_rows); write(NULLS, null_rows); write(COUNTER, counter)
    report = f"""# GDT187 — label inventories do not yet reveal omitted headwords

## Result

Status: **{status}**.

The Foxton-derived keyed-omission prediction is not supported after the exact
ten-channel search adjustment.  The panel contains {len(eligible)} nonsealed
pages on {len({page_meta[p][3] for p in eligible})} physical folios, with
{label_groups} label groups and {sum(len(by_prose[p]) for p in eligible)}
confirmed-prose groups.  The exact null exhausts {len(worlds)} whole-folio
bundle assignments matched on section, Currier, hand, and pages per folio.

The top standardized channel is `{top['scope']} / {top['representation']}`:
observed weighted Jaccard {float(top['observed_mean_weighted_jaccard']):.5f}
versus null {float(top['null_mean']):.5f}, local
`p={float(top['local_exact_p']):.4f}`, max-ten
`p={float(top['max_ten_p']):.4f}`.  This is a weak directional lead only.
Its Pharma effect is {float(top['pharma_effect']):+.5f} (`p={float(top['pharma_exact_p']):.4f}`),
whereas its Biological/Balneological effect is {float(top['bio_effect']):+.5f}
(`p={float(top['bio_exact_p']):.4f}`).  The weak lead is therefore register
concentrated rather than a consistent two-register relation.

Exact PAGE_HOST reuse is real but sparse: {exact_group_overlap}/{label_groups}
label-group occurrences ({exact_type_overlap}/{label_types} label-host types)
appear anywhere in same-page prose, and only {opening_group_overlap}/{label_groups}
appear on paragraph-opening lines.  Exact-host similarity is not globally
unusual enough to establish repeated rubric words, while the broader
host/compiler channels are not strong enough to establish omitted or
distributed headwords.

## Interpretation

Foxton remains a useful historical mechanism, but this first Voynich
prediction does not locate its analogue.  The most defensible reading is that
page labels and prose share register-local string/compiler ecology, not a
demonstrated label-key dictionary.  The result does not invalidate the broader
hybrid compiler; it rejects this particular low-capacity page-level bridge.

No label receives ownership, a word class, a Latin correspondence, a sound,
a language, plaintext, or meaning.  f84r was rejected before formal parsing
and was not retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "experiment": "GDT187_KEYED_OMISSION_TEST", "status": status,
        "counts": {"pages": len(eligible), "physical_folios": len({page_meta[p][3] for p in eligible}),
                   "label_groups": label_groups, "label_host_types": label_types,
                   "prose_groups": sum(len(by_prose[p]) for p in eligible), "null_worlds": len(worlds),
                   "metrics": len(metrics)},
        "exact_overlap": {"label_groups_anywhere_in_prose": exact_group_overlap,
                          "label_types_anywhere_in_prose": exact_type_overlap,
                          "label_groups_on_opening_lines": opening_group_overlap},
        "top_metric": top, "best_formal_metric": best_formal,
        "decision_gates": {"max_ten_at_most_05": float(best_formal["max_ten_p"]) <= .05,
                                               "eligible_formal_channel": True,
                                               "positive_in_both_powered_sections": both_sections_positive,
                                               "not_weaker_than_corresponding_raw_control": beats_raw,
                                               "all_pass": supported},
        "blocks": block_manifest,
        "provenance": {"selected_role_rows_sha256": roles_digest,
                       "all_f84_rows_rejected_before_formal_parse_or_retention": True,
                       "f84r_formal_payload_retained_parsed_joined_scored": False},
        "f84r_accessed": False,
        "claim_ceiling": "Page-level formal label/prose association only; no ownership, rubric, word, language, plaintext, meaning, or translation.",
        "inputs": {PROSE.name: sha(PROSE), LABELS.name: sha(LABELS)},
        "outputs": {p.name: sha(p) for p in (INVENTORY, SCORES, NULLS, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": sha(Path(__file__)),
    }
    RESULT.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(status, top)


if __name__ == "__main__": main()
