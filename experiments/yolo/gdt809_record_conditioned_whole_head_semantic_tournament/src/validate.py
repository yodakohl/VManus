#!/usr/bin/env python3
"""Independent GDT809 validator; never imports or executes the builder.

The frozen sources are reconstructed through the selector-first query guard.
Checks are grouped scientific contracts, not a replay of builder assertions.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").is_file() and (p / ".git").exists())
BASE = Path(__file__).resolve().parents[1]
SRC = BASE / "src"
ART = BASE / "artifacts"
YOLO = ROOT / "experiments/yolo"
RAW = {
    "lines": ROOT / "transcription/voynich_zl3b_lines.tsv",
    "tokens": ROOT / "transcription/voynich_zl3b_tokens.tsv",
    "cross": ROOT / "transcription/voynich_cross_transcription_lines.tsv",
}
INPUTS = {
    "allow": YOLO / "gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv",
    "deck": YOLO / "gdt760_quantity_bilateral_content_attachment/artifacts/CONTENT_ANCHOR_35_CANDIDATE_DECK.tsv",
    "attach": YOLO / "gdt760_quantity_bilateral_content_attachment/artifacts/CONTENT_45_ATTACHMENT_ATLAS.tsv",
    "value": YOLO / "gdt764_bounded_value_field_dispatch/artifacts/X_DAIIN_9_EXACT_BIGRAM_ATLAS.tsv",
    "visual": YOLO / "gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv",
    "events": YOLO / "gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_1777_CORE_EVENT_ATLAS.tsv",
    "q152": YOLO / "gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_Q152_EXACT_QUARANTINE.tsv",
}
SEALS = {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
RECORD_FIELDS = ("section", "language", "hand", "line_position", "paragraph_line_position", "targetfree_line_length_bin")
CHECKS = []


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def block(name, detail=""):
    CHECKS.append({"check": name, "status": "PASS", "detail": detail})


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def read_tsv(path):
    require(path not in RAW.values(), "mixed transcription may only use guarded_query")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def table(name):
    return read_tsv(ART / (name if name.endswith(".tsv") else f"GDT809_{name}.tsv"))


def parts(value):
    return {x for x in str(value).split("|") if x and x != "NONE"}


def packed(values):
    return "|".join(str(x) for x in values) or "NONE"


def same(actual, expected, label):
    for key, value in expected.items():
        require(key in actual, f"{label}: missing field {key}")
        if isinstance(value, float):
            require(actual[key] != "NA" and math.isclose(float(actual[key]), value, rel_tol=2e-10, abs_tol=2e-11),
                    f"{label}: {key} {actual[key]!r} != {value!r}")
        else:
            require(str(actual[key]) == str(value), f"{label}: {key} {actual[key]!r} != {value!r}")


def keyed(rows, keys):
    result = {tuple(row[k] for k in keys): row for row in rows}
    require(len(result) == len(rows), f"duplicate keys: {keys}")
    return result


def pagekey(page):
    m = re.fullmatch(r"f(\d+)([rv])(\d*)", page)
    require(m is not None, f"unrecognized selector: {page}")
    return int(m[1]), m[2] == "v", int(m[3] or 0), page


def folio(page):
    return re.match(r"f\d+[rv]", page)[0]


def position(index, count):
    return "SINGLE" if count == 1 else "FIRST" if index == 1 else "LAST" if index == count else "MIDDLE"


def direction(score):
    return "NA" if score is None else "EXPANDED" if score > 0 else "BASE" if score < 0 else "TIE"


def distance(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        old, row = row, [i]
        for j, y in enumerate(b, 1):
            row.append(min(old[j] + 1, row[j - 1] + 1, old[j - 1] + (x != y)))
    return row[-1]


def registration():
    manifest = json.loads((BASE / "experiment.json").read_text())
    require(manifest["experiment_id"] == "GDT809" and manifest["sealed_data"] == SEALS, "manifest identity/seals")
    require(manifest.get("question") and manifest.get("claim_ceiling"), "manifest question and claim ceiling required")
    registered = {}
    for item in manifest["inputs"] + manifest["outputs"]:
        name = item["path"]
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "manifest path escapes repository")
        require(name not in registered, f"duplicate input/output: {name}")
        registered[name] = item
        path = ROOT / name
        require(path.is_file(), f"manifest file missing: {name}")
        require(digest(path) == item["sha256"], f"manifest hash mismatch: {name}")
    required_inputs = set(INPUTS.values()) | set(RAW.values()) | set(SRC.glob("*SPECS.tsv"))
    input_paths = {item["path"] for item in manifest["inputs"]}
    require({relative(p) for p in required_inputs} <= input_paths, "manifest does not bind all consumed sources/specs")
    require({relative(SRC / "run.py"), relative(Path(__file__).resolve())} <= set(registered), "implementation not manifest bound")
    tree = ast.parse((SRC / "run.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            require(node.module != "validate", "builder must not call validator to produce evidence")
    block("manifest_hashes_and_seals", f"{len(registered)} manifest-bound files")
    pool = read_tsv(SRC / "HEAD_POOL_SPECS.tsv")
    spec = {r["surface"]: r for r in pool}
    deck = {r["content_surface"]: r for r in read_tsv(INPUTS["deck"])}
    values = read_tsv(INPUTS["value"])
    value_heads = {r["x_surface"] for r in values}
    q152 = {r["surface"] for r in read_tsv(INPUTS["q152"])}
    require((len(pool), len(spec), len(deck), len(value_heads), len(q152)) == (41, 41, 35, 6, 152), "source pool cardinalities")
    require(set(spec) == set(deck) | value_heads, "head pool not exact inherited union")
    active = set(spec) - q152
    ed1 = {head for head in active if min(distance(head, q) for q in q152) > 1}
    require((len(active), len(set(spec) & q152), len(ed1)) == (35, 6, 18), "exact/ED1 head masks")
    for head, row in spec.items():
        role = deck[head]["current_content_axes"] if head in deck else next(r["x_selected_field_type"] for r in values if r["x_surface"] == head)
        source = "GDT760_AMOUNT_CONTENT" if head in deck else "GDT764_X_DAIIN"
        same(row, {"active_after_q152": int(head in active), "q152_exact_excluded": int(head in q152),
                   "registered_prior_role": role, "source_pool": source, "literal_credit": 0}, head)
    require({r["surface"] for r in pool if r["balanced_four_cell_head"] == "1"} == {"dal", "qoty", "sheor", "cheo", "cheal", "chckhey"}, "balanced head block")
    require({r["surface"] for r in pool if r["preexisting_semantic_sentinel"] == "1"} == {"cthy"}, "sentinel disclosure")
    block("inherited_head_pool_and_quarantine", "41 inherited / 35 active / 6 exact exclusions / 18 ED1-safe")
    decisions = {r["decision_id"]: r for r in read_tsv(SRC / "RELATION_DECISION_SPECS.tsv")}
    thresholds = {"D01": ("GE", "4"), "D02": ("GE", "4"), "D03": ("GE", "1.25"), "D04": ("LE", "4"),
                  "D05": ("GE", "0.80"), "D06": ("GE", "3"), "D07": ("EQ", "1"), "D08": ("EQ", "1"),
                  "D09": ("EQ", "1"), "D10": ("EQ", "1"), "D11": ("EQ", "0"), "D12": ("GE", "3"), "D13": ("GE", "2")}
    for name, (op, value) in thresholds.items():
        require(name in decisions and decisions[name]["operator"] == op and float(decisions[name]["threshold"]) == float(value), f"decision contract {name}")
    policies = {"D04": "NULL_SCORE_TIES_COUNT_AGAINST", "D05": "ZERO_DIRECTION_FAILS", "D07": "ZERO_DIRECTION_FAILS",
                "D08": "NO_SEMANTIC_IDENTITY_CREDIT", "D09": "NO_AUTOMATIC_IDENTITY_PROMOTION", "D10": "UNOBSERVED_IS_NOT_FALSE",
                "D11": "UNOBSERVED_IS_NOT_COUNTEREVIDENCE", "D13": "EXACT_TOP_TIE_BLOCKS_SINGLETON_NOT_APPLICABLE"}
    for name, policy in policies.items():
        require(decisions[name]["ties_policy"] == policy, f"tie/uncertainty policy {name}")
    require(decisions["D14"]["metric"] == "identity_promotion_authorized" and decisions["D14"]["threshold"] == "0", "no literal promotion authority")
    profiles = read_tsv(SRC / "SEMANTIC_PROFILE_SPECS.tsv")
    require(len({p["candidate_id"] for p in profiles}) == len(profiles), "duplicate candidate IDs")
    require(all(p["literal_credit"] == "0" for p in profiles), "candidate spelling has literal credit")
    require({"aqua", "vinum", "oleum", "sal", "folium/folia", "radix", "flos", "semen", "pulvis", "lignum", "tere", "misce", "cola"} <= {p["historical_lemma"] for p in profiles}, "required concrete candidate omitted")
    block("decision_and_candidate_contracts", f"{len(decisions)} gates / {len(profiles)} historical profiles")
    return manifest, spec, active, ed1, q152, profiles


def guarded_query(path, pages, columns, query_id):
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", relative(path), "--selector", "page"]
    for page in sorted(pages, key=pagekey):
        cmd += ["--allow", page]
    cmd += ["--columns", ",".join(columns), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    completed = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    require(completed.returncode == 0, f"guard query failed: {query_id}")
    stat_lines = [s[12:] for s in completed.stderr.splitlines() if s.startswith("GUARD_STATS ")]
    require(len(stat_lines) == 1, "guard statistics missing")
    stats = json.loads(stat_lines[0])
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    require(all(r["page"] in pages and not r["page"].startswith("f84") for r in rows), "guard emitted forbidden selector")
    return rows, {"query_id": query_id, "source_path": relative(path), "selector_column": "page", "allowed_value_count": len(pages),
                  "output_columns": ",".join(columns), "forbidden_prefixes": "f84|f84r", "selected_rows": stats["selected"],
                  "skipped_forbidden_rows": stats["skipped_forbidden"], "skipped_not_allowed_rows": stats["skipped_not_allowed"], "query_returncode": 0}


def corpus():
    pages = [r["page"] for r in read_tsv(INPUTS["allow"])]
    require(len(pages) == len(set(pages)) == 179 and not any(p.startswith("f84") for p in pages), "179-page selector scope")
    lines, ls = guarded_query(RAW["lines"], pages, ("page", "locus", "line_number", "section", "language", "hand", "paragraph_start", "paragraph_end", "token_count", "eva_clean"), "ZL3B_LINES_179")
    tokens, ts = guarded_query(RAW["tokens"], pages, ("page", "locus", "token_index", "eva", "section", "language", "hand"), "ZL3B_TOKENS_179")
    cross, cs = guarded_query(RAW["cross"], pages, ("page", "locus", "all_three_present", "all_present_exact", "zl3b_clean", "it2a_clean", "rf1b_clean"), "CROSS_READER_LINES_179")
    require((len(lines), len(tokens), len(cross)) == (4137, 32339, 4137), "guarded cache counts")
    cross_map = keyed(cross, ("page", "locus"))
    token_map = defaultdict(list)
    for token in tokens:
        token_map[token["page"], token["locus"]].append(token)
    ordered = sorted(lines, key=lambda r: (pagekey(r["page"]), int(r["line_number"])))
    paragraph, serial = [], 0
    for row in ordered:
        key = row["page"], row["locus"]
        local = sorted(token_map[key], key=lambda r: int(r["token_index"]))
        require([int(t["token_index"]) for t in local] == list(range(1, len(local) + 1)), "noncontiguous token indexes")
        words = [t["eva"] for t in local]
        require(" ".join(words) == row["eva_clean"] == cross_map[key]["zl3b_clean"] and len(words) == int(row["token_count"]), f"reader/token parity {row['locus']}")
        counts = [Counter(cross_map[key][reader].split()) for reader in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        ranks, stable = Counter(), []
        for word in words:
            ranks[word] += 1
            stable.append(ranks[word] <= min(count[word] for count in counts))
        row.update(words=words, stable=stable)
        if row["paragraph_start"] == "1":
            require(not paragraph, "nested strict paragraph")
            paragraph = [row]
        elif paragraph:
            require(paragraph[0]["page"] == row["page"], "paragraph crosses selector")
            paragraph.append(row)
        if row["paragraph_end"] == "1":
            require(paragraph, "orphan paragraph end")
            serial += 1
            for index, member in enumerate(paragraph, 1):
                member.update(paragraph_id=f"G809-P{serial:04d}", paragraph_line_index=index, paragraph_line_count=len(paragraph))
            paragraph = []
    require(not paragraph, "unclosed paragraph")
    strict = [r for r in ordered if "paragraph_id" in r]
    require((serial, len(strict), sum(len(r["words"]) for r in strict)) == (665, 3807, 31938), "strict paragraph reconstruction")
    published = table("GUARDED_QUERY_STATS")
    require(len(published) == 3, "guard census rows")
    for actual, expected in zip(published, (ls, ts, cs)):
        same(actual, expected, "guard stats")
    block("guarded_corpus_and_alternate_reader_rank_stability", "179 selectors / 4137 lines / 32339 tokens / 665 strict paragraphs")
    return ordered, {(r["page"], r["locus"]): r for r in ordered}


def contacts(events, line_map, heads):
    edges = []
    windows = defaultdict(lambda: defaultdict(list))
    for event in events:
        line = line_map[event["page"], event["locus"]]
        pivot = int(event["token_index"])
        require(line["words"][pivot - 1] == event["surface"], "CORE pivot identity drift")
        require(folio(event["page"]) == event["physical_folio"], "CORE physical-folio drift")
        for idx in range(max(1, pivot - 2), min(len(line["words"]), pivot + 2) + 1):
            head = line["words"][idx - 1]
            if idx == pivot or head not in heads or not line["stable"][idx - 1]:
                continue
            edges.append((event["event_id"], head, idx - pivot))
            windows[event["event_id"]][head].append(idx - pivot)
    unique = {event: next(iter(local)) for event, local in windows.items() if len(local) == 1}
    return edges, windows, unique


def validate_contacts(events, line_map, active, ed1, spec):
    pool = table("HEAD_POOL_CENSUS")
    require(len(pool) == 41, "head census row count")
    q152 = {r["surface"] for r in read_tsv(INPUTS["q152"])}
    for row in pool:
        head = row["surface"]
        same(row, spec[head], "pool source row")
        minimum = min(distance(head, q) for q in q152)
        same(row, {"ed1_minimum_to_q152": minimum, "ed1_safe_from_q152": int(minimum > 1), "component_export_credit": 0,
                   "observed_source_pool": spec[head]["source_pool"], "observed_source_role": spec[head]["registered_prior_role"],
                   "source_pool_evidence_channel": "OBSERVED_SOURCE_MEMBERSHIP", "source_role_evidence_channel": "INHERITED_SEMANTIC_PRIOR",
                   "source_role_is_observed_identity": 0, "source_provenance": relative(INPUTS["deck"] if spec[head]["source_pool"] == "GDT760_AMOUNT_CONTENT" else INPUTS["value"]),
                   "head_status": "ACTIVE_EXACT_HEAD" if head in active else "EXACT_Q152_EXCLUDED"}, head)
    edge, window, unique = contacts(events, line_map, active)
    lookup = {r["event_id"]: r for r in events}
    require((len(edge), sum(map(len, window.values())), len(window), len({lookup[e]["physical_folio"] for e in window}), len(unique)) == (211, 209, 199, 103, 189), "exact relation capacity")
    rows = table("211_HEAD_PIVOT_OCCURRENCE_EDGES")
    require(Counter((r["event_id"], r["head"], int(r["signed_offset"])) for r in rows) == Counter(edge), "exact occurrence edges not source reconstruction")
    for row in rows:
        event = lookup[row["event_id"]]
        same(row, {"axis": event["axis"], "expanded_label": event["expanded_label"], "pivot_surface": event["surface"],
                   "page": event["page"], "physical_folio": event["physical_folio"], "locus": event["locus"],
                   "head_token_index": int(event["token_index"]) + int(row["signed_offset"]), "rank_stable_head": 1}, "contact coordinate")
    links = table("209_HEAD_PIVOT_LINKS")
    require(set(keyed(links, ("event_id", "head"))) == {(e, h) for e, hs in window.items() for h in hs}, "distinct link identities")
    for row in links:
        hs = window[row["event_id"]]
        same(row, {"signed_offsets": packed(sorted(hs[row["head"]])), "head_occurrence_edges": len(hs[row["head"]]),
                   "distinct_heads_in_window": len(hs), "primary_unique_head_window": int(len(hs) == 1),
                   "weighted_sensitivity_weight": 1 / len(hs)}, "window capacity/weight")
    published = table("189_UNIQUE_HEAD_WINDOWS")
    require({r["event_id"]: r["head"] for r in published} == unique and len(published) == len(unique), "primary unique-head windows")
    ed_edges, ed_windows, ed_unique = contacts(events, line_map, ed1)
    require((len(ed_edges), sum(map(len, ed_windows.values())), len(ed_windows), len(ed_unique)) == (91, 90, 86, 82), "rebuilt ED1 relation capacity")
    block("exact_and_rebuilt_ED1_contact_capacity", "211/209/199/103/189 exact; 18 heads and 91/90/86/82 ED1")
    return (window, unique), (ed_windows, ed_unique)


def occurrence_atlas(lines, events, active, q152):
    discovery = {(r["page"], r["locus"], int(r["content_ordinal"])) for r in read_tsv(INPUTS["attach"]) if r["content_surface"] in active}
    discovery |= {(r["page"], r["locus"], int(r["x_ordinal"])) for r in read_tsv(INPUTS["value"]) if r["x_surface"] in active}
    pivots = defaultdict(list)
    for e in events:
        pivots[e["page"], e["locus"]].append(int(e["token_index"]))
    visuals = keyed(read_tsv(INPUTS["visual"]), ("source_selector", "locus", "token_ordinal_in_line", "surface"))
    landmarks = read_tsv(SRC / "LANDMARK_SPECS.tsv")
    expected = []
    for line in lines:
        for idx, head in enumerate(line["words"], 1):
            if head not in active or not line["stable"][idx - 1]:
                continue
            distances = [abs(idx - j) for j in pivots[line["page"], line["locus"]]]
            disc = (line["page"], line["locus"], idx) in discovery
            external = not disc and min(distances, default=999) > 2
            visual = visuals.get((line["page"], line["locus"], str(idx), head), {})
            tags, hits = set(), []
            for landmark in landmarks if external else []:
                for other, word in enumerate(line["words"], 1):
                    if other != idx and abs(other - idx) <= int(landmark["maximum_radius"]) and word in parts(landmark["surfaces"]):
                        tags.add(landmark["structural_tag"])
                        hits.append(f"{landmark['landmark_id']}:{landmark['structural_tag']}:{word}@{other - idx:+d}")
            strict = "paragraph_id" in line
            expected.append({"head": head, "page": line["page"], "physical_folio": folio(line["page"]), "locus": line["locus"],
                             "line_number": line["line_number"], "token_index": idx, "line_token_count": len(line["words"]),
                             "line_position": position(idx, len(line["words"])), "section": line["section"], "language": line["language"], "hand": line["hand"],
                             "rank_stable_all_three": 1, "strict_paragraph": int(strict), "paragraph_id": line.get("paragraph_id", "NONE"),
                             "paragraph_line_index": line.get("paragraph_line_index", "NA"), "paragraph_line_count": line.get("paragraph_line_count", "NA"),
                             "paragraph_line_position": position(line["paragraph_line_index"], line["paragraph_line_count"]) if strict else "OUTSIDE",
                             "targetfree_line_length_bin": int(math.log2(1 + sum(w not in q152 for w in line["words"]))),
                             "source_discovery_coordinate": int(disc), "minimum_core_pivot_distance": min(distances) if distances else "NONE",
                             "strict_external_occurrence": int(external), "landmark_tags": packed(sorted(tags)), "landmark_hits": packed(sorted(hits)),
                             "visual_occurrence_kind": visual.get("occurrence_kind", "NONE"), "visual_topology_family": visual.get("topology_family", "NONE"),
                             "visual_context_scope": visual.get("context_scope", "NONE"), "visual_owner_id": visual.get("context_owner_id", "NONE"),
                             "visual_evidence_channel": "CACHED_CONTEXT_NOT_TOKEN_PART_OWNER" if visual else "UNOBSERVED",
                             "visual_source_provenance": relative(INPUTS["visual"]) if visual else "NONE",
                             "occurrence_source_provenance": packed(relative(RAW[key]) for key in ("lines", "tokens", "cross")),
                             "written_line_eva": " ".join(line["words"]), "literal_credit": 0, "component_export_credit": 0})
    published = table("1032_HEAD_OCCURRENCE_ATLAS")
    require(len(expected) == len(published) == 1032, "stable head occurrence count")
    for actual, correct in zip(published, expected):
        same(actual, correct, "exact head occurrence")
    external = [r for r in expected if r["strict_external_occurrence"]]
    external_rows = table("EXTERNAL_HEAD_OCCURRENCES")
    require(len(external_rows) == len(external), "external mask count")
    for actual, correct in zip(external_rows, external):
        same(actual, correct, "external head occurrence")
    block("whole_occurrences_external_masks_landmarks_and_exact_visual_joins", f"1032 stable heads / {len(external)} external")
    return external


def association(events, unique, head, axis, labels, excluded=None):
    cells, contacted = [0, 0, 0, 0], set()
    for event in events:
        if event["axis"] != axis or event["physical_folio"] == excluded:
            continue
        target = unique.get(event["event_id"]) == head
        label = labels[event["event_id"]]
        cells[(0 if target else 2) + (0 if label else 1)] += 1
        if target:
            contacted.add(event["physical_folio"])
    a, b, c, d = cells
    return a, b, math.log((a + .5) * (d + .5) / ((b + .5) * (c + .5))), contacted


def all_rotations(events):
    groups = defaultdict(list)
    for event in events:
        key = tuple(event[field] for field in ("axis", "carrier", "section", "language", "hand", "targetfree_line_length_bin"))
        groups[key].append(event)
    result = [{e["event_id"]: int(e["expanded_label"]) for e in events}]
    mobility = [0.0]
    ordered_groups = [sorted(group, key=lambda r: (pagekey(r["page"]), int(r["line_number"]), int(r["token_index"]), r["event_id"])) for group in groups.values()]
    for k in range(1, 25):
        labels = {}
        for group in ordered_groups:
            for i, event in enumerate(group):
                labels[event["event_id"]] = int(group[(i - k) % len(group)]["expanded_label"])
        result.append(labels)
        mobility.append(sum(labels[e["event_id"]] != int(e["expanded_label"]) for e in events) / len(events))
    return result, mobility


def event_fields(event, line_map):
    line = line_map[event["page"], event["locus"]]
    return {"section": event["section"], "language": event["language"], "hand": event["hand"],
            "line_position": position(int(event["token_index"]), int(event["line_token_count"])),
            "paragraph_line_position": position(line["paragraph_line_index"], line["paragraph_line_count"]),
            "targetfree_line_length_bin": event["targetfree_line_length_bin"]}


def external_record(events, axis, excluded, external, line_map):
    training = [e for e in events if e["axis"] == axis and e["physical_folio"] not in excluded]
    cell_counts = Counter((e["carrier"], e["expanded_label"]) for e in training)
    vocab = {field: set() for field in RECORD_FIELDS}
    counts = defaultdict(float)
    totals = defaultdict(float)
    for event in training:
        label = int(event["expanded_label"])
        weight = 1 / cell_counts[event["carrier"], event["expanded_label"]]
        for field, value in event_fields(event, line_map).items():
            vocab[field].add(value)
            counts[field, label, value] += weight
            totals[field, label] += weight
    scores = []
    for occurrence in external:
        score = 0.0
        for field in RECORD_FIELDS:
            nvalues = len(vocab[field])
            if nvalues:
                value = str(occurrence[field])
                positive = (counts[field, 1, value] + .5) / (totals[field, 1] + .5 * nvalues)
                negative = (counts[field, 0, value] + .5) / (totals[field, 0] + .5 * nvalues)
                score += math.log(positive / negative)
        scores.append(score)
    mean = math.fsum(scores) / len(scores) if scores else None
    return mean, training


def relation_validation(events, line_map, external, active, ed1, contact_sets):
    require(len(events) == 1777 and len(keyed(events, ("event_id",))) == 1777, "CORE 1777 event identity")
    rotations, mobility = all_rotations(events)
    null_rows = table("RELATION_NULL_SCORES")
    nulls = keyed(null_rows, ("population", "head", "axis", "null_id"))
    require(len(nulls) == (70 + 36) * 25, "complete exact/ED1 null grid")
    record_rows = keyed(table("EXTERNAL_RECORD_PROFILES"), ("population", "head", "axis"))
    require(len(record_rows) == 106, "complete external record profile grid")
    exact_rows = table("HEAD_AXIS_RELATION_SCORECARD")
    ed1_rows = table("ED1_HEAD_AXIS_SENSITIVITY")
    require(len(exact_rows) == len(ed1_rows) == 70, "exact and ED1 scorecard grid")
    expected_pairs = {(h, a) for h in active for a in ("L", "DY")}
    require(set(keyed(exact_rows, ("head", "axis"))) == expected_pairs and set(keyed(ed1_rows, ("head", "axis"))) == expected_pairs, "scorecard head/axis membership")
    for population, heads, rows, (windows, unique) in zip(("EXACT35", "ED1_SAFE18"), (active, ed1), (exact_rows, ed1_rows), contact_sets):
        weighted = defaultdict(float)
        lookup = {e["event_id"]: e for e in events}
        for eid, local in windows.items():
            event = lookup[eid]
            for head in local:
                weighted[head, event["axis"], int(event["expanded_label"])] += 1 / len(local)
        for row in rows:
            head, axis = row["head"], row["axis"]
            if head not in heads:
                same(row, {"head_ed1_safe": 0, "direction": "REMOVED_ED1", "local_association_pass": 0,
                           "relation_conditioned_record_head": 0, "haldane_log_or": "NA", "external_record_compatibility_mean_score": "NA"}, "removed ED1 head")
                continue
            if population == "ED1_SAFE18":
                same(row, {"head_ed1_safe": 1}, "safe ED1 head")
            values = [association(events, unique, head, axis, label) for label in rotations]
            a, b, logor, folios = values[0]
            for k, (na, nb, value, _) in enumerate(values):
                ident = "OBSERVED" if not k else f"K{k:02d}"
                actual = nulls[population, head, axis, ident]
                same(actual, {"expanded_contacts": na, "base_contacts": nb, "haldane_log_or": value,
                              "absolute_log_or": abs(value), "changed_label_fraction": mobility[k],
                              "observed_reference": int(k == 0), "ties_count_against_head": 1}, f"null {population}/{head}/{axis}/{ident}")
            rank = 1 + sum(abs(value[2]) >= abs(logor) - 1e-12 for value in values[1:])
            jack = [association(events, unique, head, axis, rotations[0], f)[2] for f in sorted(folios)]
            sign_agreement = sum(v * logor > 0 for v in jack) / len(jack) if jack else 0.0
            outside = [e for e in external if e["head"] == head and e["strict_paragraph"] and e["physical_folio"] not in folios]
            mean, training = external_record(events, axis, folios, outside, line_map)
            training_folios = {e["physical_folio"] for e in training}
            training_selectors = {e["page"] for e in training}
            overlap_folios = training_folios & {e["physical_folio"] for e in outside}
            overlap_selectors = training_selectors & {e["page"] for e in outside}
            overlap_occurrences = sum(e["physical_folio"] in training_folios for e in outside)
            direction_agrees = int(mean is not None and mean * logor > 0)
            local = int(a + b >= 4 and len(folios) >= 4 and abs(logor) >= 1.25 and rank <= 4 and sign_agreement >= .8)
            relation = int(local and len(outside) >= 3 and direction_agrees)
            wa, wb = weighted[head, axis, 1], weighted[head, axis, 0]
            axis_events = [e for e in events if e["axis"] == axis]
            total_a = sum(int(e["expanded_label"]) for e in axis_events)
            total_b = len(axis_events) - total_a
            weighted_or = math.log((wa + .5) * (total_b - wb + .5) / ((wb + .5) * (total_a - wa + .5)))
            expected = {"population": population, "primary_unique_events": a + b, "primary_contact_folios": len(folios),
                        "expanded_contacts": a, "base_contacts": b, "haldane_log_or": logor, "absolute_haldane_log_or": abs(logor),
                        "direction": direction(logor), "target_rotation_absolute_rank": rank,
                        "target_rotation_denominator": 25, "leave_one_contact_folio_sign_agreement": sign_agreement,
                        "weighted_expanded_contacts": wa, "weighted_base_contacts": wb, "weighted_haldane_log_or": weighted_or,
                        "weighted_direction_agrees": int(weighted_or * logor > 0), "folio_disjoint_external_occurrences": len(outside),
                        "folio_disjoint_external_folios": len({e["physical_folio"] for e in outside}),
                        "external_record_compatibility_mean_score": mean if mean is not None else "NA",
                        "external_record_compatibility_direction": direction(mean),
                        "external_record_compatibility_direction_agrees": direction_agrees,
                        "record_training_external_overlap_folios": len(overlap_folios),
                        "record_training_external_overlap_occurrences": overlap_occurrences,
                        "record_compatibility_not_independent_semantics": 1,
                        "local_association_pass": local, "relation_conditioned_record_head": relation,
                        "literal_credit": 0, "component_export_credit": 0}
            same(row, expected, f"relation {population}/{head}/{axis}")
            prof = record_rows[population, head, axis]
            same(prof, {"excluded_contact_folios": packed(sorted(folios)), "record_model_training_events": len(training),
                        "record_model_training_folios": len(training_folios), "folio_disjoint_external_occurrences": len(outside),
                        "folio_disjoint_external_folios": len({e["physical_folio"] for e in outside}),
                        "external_record_compatibility_mean_score": mean if mean is not None else "NA",
                        "external_record_compatibility_direction": expected["external_record_compatibility_direction"],
                        "direction_agrees": direction_agrees, "model_features": packed(RECORD_FIELDS),
                        "record_training_external_overlap_folios": len(overlap_folios),
                        "record_training_external_overlap_occurrences": overlap_occurrences,
                        "evidence_channel": "FORMAL_RECORD_COMPATIBILITY"}, f"record model {population}/{head}/{axis}")
            if "record_training_external_overlap_selectors" in prof:
                require(parts(prof["record_training_external_overlap_selectors"]) == overlap_selectors, "record selector overlap")
            if "record_training_external_overlap_folio_ids" in prof:
                require(parts(prof["record_training_external_overlap_folio_ids"]) == overlap_folios, "record physical-folio overlap")
    block("independent_exact_and_ED1_full_Haldane_rotation_jackknife_and_record_models", "106 head/axis models; 2650 observed/null cells; explicit external training overlap")
    return exact_rows, ed1_rows


def feature_validation(external, spec, active, relations, ed1_relations):
    deck = {r["content_surface"]: r for r in read_tsv(INPUTS["deck"])}
    value_rows = read_tsv(INPUTS["value"])
    manual = defaultdict(set)
    for row in read_tsv(SRC / "MANUAL_EVIDENCE_SPECS.tsv"):
        if row["measurement_state"] != "PRIOR":
            manual[row["surface"]] |= parts(row["evidence_tags"])
        require(row["literal_credit"] == "0" and (ROOT / row["source_report"]).is_file(), "manual evidence provenance")
    relation_map = keyed(relations, ("head", "axis"))
    ed1_map = keyed(ed1_relations, ("head", "axis"))
    published = keyed(table("HEAD_FEATURE_PROFILES"), ("head",))
    require(set(published) == {(h,) for h in active}, "35 feature profiles")
    feature_sets = {}
    for head in sorted(active):
        values = [r for r in external if r["head"] == head]
        tags = set(manual[head])
        role = spec[head]["registered_prior_role"]
        if "GDT760_AMOUNT_CONTENT" in spec[head]["source_pool"]:
            tags.add("SOURCE_CONTENT_HEAD")
        if "GDT764_X_DAIIN" in spec[head]["source_pool"]:
            tags |= {"SOURCE_VALUE_FIELD_HEAD", "VALUE_FIELD_ANY"}
        for prior in ("DRY", "MOIST", "HOT", "COLD", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "AMOUNT", "QUALITY"):
            if prior in role:
                tags.add(f"PRIOR_{prior}")
        if head in deck:
            amount = deck[head]
            for tag, condition in (("AMOUNT_CONTACT_ANY", int(amount["amount_attachment_occurrences"]) > 0),
                                   ("AMOUNT_CONTACT_RECURRENT", int(amount["amount_attachment_occurrences"]) >= 2),
                                   ("AMOUNT_CONTACT_3_FOLIOS", int(amount["amount_attachment_pages"]) >= 3)):
                if condition:
                    tags.add(tag)
        if any(r["x_surface"] == head and r["selected_local_dispatch"] == "QUALITY_GRADE_III" for r in value_rows):
            tags |= {"GDT764_QUALITY_GRADE_FIELD", "EXACT_QUALITY_VALUE_PARALLEL"}
        physical = {r["physical_folio"] for r in values}
        if len(physical) >= 3:
            tags.add("EXTERNAL_3_FOLIOS")
        n = len(values)
        herbal = sum(r["section"] == "H" for r in values)
        share = herbal / n if n else 0.0
        first = sum(r["line_position"] == "FIRST" for r in values)
        last = sum(r["line_position"] == "LAST" for r in values)
        strict = [r for r in values if r["strict_paragraph"]]
        para_first = sum(r["paragraph_line_position"] == "FIRST" for r in strict)
        conditions = {"HERBAL_DOMINANT_75": n and share >= .75, "HERBAL_DOMINANT_90": n and share >= .90,
                      "NONHERBAL_DOMINANT_75": n and 1 - share >= .75, "LINE_FIRST_20": n and first / n >= .20,
                      "LINE_LAST_20": n and last / n >= .20, "PARAGRAPH_START_20": len(strict) and para_first / len(strict) >= .20}
        tags |= {tag for tag, present in conditions.items() if present}
        nearby = defaultdict(set)
        for row in values:
            for tag in parts(row["landmark_tags"]):
                nearby[tag].add(row["physical_folio"])
        for tag, name in (("NEAR_CHOR_SHOR", "NEAR_CHOR_SHOR_2_FOLIOS"), ("NEAR_CTHY", "NEAR_CTHY_2_FOLIOS"),
                          ("NEAR_VALUE_FORM", "NEAR_VALUE_FORM_2_FOLIOS"), ("NEAR_AMOUNT_FORM", "NEAR_AMOUNT_2_FOLIOS")):
            if len(nearby[tag]) >= 2:
                tags.add(name)
        visual = Counter(r["visual_topology_family"] for r in values)
        for topology, tag in (("WHOLE_PLANT_ARTICLE", "VISUAL_WHOLE_PLANT_3"), ("POOL_APPARATUS_NETWORK", "VISUAL_POOL_3"),
                              ("MATERIAL_REGISTER", "VISUAL_MATERIAL_3"), ("RADIAL_ARRAY", "VISUAL_RADIAL_3"), ("TEXT_BLOCK", "VISUAL_TEXT_3")):
            if visual[topology] >= 3:
                tags.add(tag)
        if {"PRIOR_MOIST", "PRIOR_PREPARATION"} <= tags:
            tags.add("MEDIUM_ROLE_PROXY")
        if "PRIOR_PREPARATION" in tags and tags & {"PRIOR_MOIST", "PRIOR_COLD", "PRIOR_CLOSE"}:
            tags.add("LIQUID_OR_PRODUCT_PROXY")
        if {"PRIOR_DRY", "PRIOR_MATERIAL"} <= tags and "PRIOR_PREPARATION" not in tags:
            tags.add("DRY_INGREDIENT_PROXY")
        if "SOURCE_VALUE_FIELD_HEAD" in tags and tags & {"PRIOR_QUALITY", "PRIOR_COLD", "PRIOR_HOT", "PRIOR_DRY", "PRIOR_MOIST"}:
            tags.add("QUALITY_VALUE_FIELD")
        summaries = []
        for axis in ("L", "DY"):
            row, ed = relation_map[head, axis], ed1_map[head, axis]
            if row["relation_conditioned_record_head"] == "1":
                tags |= {f"REL_{axis}_{row['direction']}", "REL_EXTERNAL_RECORD_AGREES"}
                summaries.append(f"{axis}:{row['direction']}:rank{row['target_rotation_absolute_rank']}")
                if ed["relation_conditioned_record_head"] == "1" and ed["direction"] == row["direction"]:
                    tags.add("REL_ED1_SAFE")
        actual = published[head,]
        require(parts(actual["evidence_features"]) == tags, f"feature producer mismatch {head}: expected-only {tags - parts(actual['evidence_features'])}, actual-only {parts(actual['evidence_features']) - tags}")
        same(actual, {"external_occurrences": n, "external_folios": len(physical), "external_herbal_occurrences": herbal,
                      "external_herbal_share": share, "external_line_first": first, "external_line_last": last,
                      "external_paragraph_first_lines": para_first, "near_chor_shor_folios": len(nearby["NEAR_CHOR_SHOR"]),
                      "near_cthy_folios": len(nearby["NEAR_CTHY"]), "near_value_form_folios": len(nearby["NEAR_VALUE_FORM"]),
                      "near_amount_form_folios": len(nearby["NEAR_AMOUNT_FORM"]), "visual_whole_plant_occurrences": visual["WHOLE_PLANT_ARTICLE"],
                      "visual_pool_occurrences": visual["POOL_APPARATUS_NETWORK"], "visual_material_occurrences": visual["MATERIAL_REGISTER"],
                      "visual_radial_occurrences": visual["RADIAL_ARRAY"], "relation_summary": packed(summaries), "literal_credit": 0,
                      "component_export_credit": 0}, f"feature statistics {head}")
        feature_sets[head] = tags
    block("independent_feature_producers_and_provenance", "formal profiles and inherited display priors remain distinct from identity")
    return feature_sets, published


# These are the validator's measurement contract, independently enumerated.
# A named but unavailable gate is not a negative observation.
PRIORS = {"PRIOR_" + name for name in ("DRY", "MOIST", "HOT", "COLD", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "AMOUNT", "QUALITY")} | {
    "MEDIUM_ROLE_PROXY", "LIQUID_OR_PRODUCT_PROXY", "DRY_INGREDIENT_PROXY", "QUALITY_VALUE_FIELD",
    "GDT764_QUALITY_GRADE_FIELD", "EXACT_QUALITY_VALUE_PARALLEL"}
UNAVAILABLE = {
    "PATIENT_MEDIUM_DURATION_OR_PROCESS", "QUALIFIED_OR_ADMIN_MEDIUM", "PRODUCED_RESULT_OR_MEASURED_MIXING_MEDIUM", "SALT_SPECIFIC_ANCHOR",
    "MANUAL_LEAF_OWNER_MULTI_FOLIO", "MANUAL_ROOT_OWNER_MULTI_FOLIO", "MANUAL_FLOWER_OWNER_MULTI_FOLIO", "MANUAL_SEED_OWNER_MULTI_FOLIO",
    "MULTI_NAME_INGREDIENT_LIST", "POWDER_SPECIFIC_ANCHOR", "MANUAL_WOOD_OWNER_MULTI_FOLIO", "SOLID_PATIENT_THEN_MIX_OR_SIEVE",
    "MULTIPLE_PATIENTS_THEN_NEXT_STEP", "UPSTREAM_LIQUID_THEN_RESULT", "PATIENT_HOT_PROCESS_ENDPOINT", "PATIENT_DRY_PROCESS_FORM_OR_STORAGE",
    "MANUAL_VESSEL_OWNER_MULTI_FOLIO", "QUALITY_IDENTITY_DIRECTION_ANCHOR", "MANUAL_AERIAL_HERB_OWNER_MULTI_FOLIO", "BOTANICAL_HEAD_DISCRIMINATING_SIGNATURE",
}


def producer_contract():
    producers = {}
    def add(features, channel, *paths):
        for feature in features:
            require(feature not in producers, "duplicate independent feature producer")
            producers[feature] = channel, {relative(p) for p in paths}
    add(PRIORS, "INHERITED_SEMANTIC_PRIOR", SRC / "HEAD_POOL_SPECS.tsv", INPUTS["deck"], INPUTS["value"])
    add(["SOURCE_CONTENT_HEAD"], "SOURCE_POOL_MEMBERSHIP", INPUTS["deck"])
    add(["SOURCE_VALUE_FIELD_HEAD"], "SOURCE_POOL_MEMBERSHIP", INPUTS["value"])
    add(["VALUE_FIELD_ANY"], "OBSERVED_EXACT_X_DAIIN_FRAME", INPUTS["value"])
    add(["AMOUNT_CONTACT_ANY", "AMOUNT_CONTACT_RECURRENT", "AMOUNT_CONTACT_3_FOLIOS"], "OBSERVED_INHERITED_ATTACHMENT_COORDINATES", INPUTS["deck"], INPUTS["attach"])
    add(["EXTERNAL_3_FOLIOS", "HERBAL_DOMINANT_75", "HERBAL_DOMINANT_90", "NONHERBAL_DOMINANT_75", "LINE_FIRST_20", "LINE_LAST_20", "PARAGRAPH_START_20"],
        "OBSERVED_CACHED_REGISTER_POSITION", *RAW.values())
    add(["NEAR_CHOR_SHOR_2_FOLIOS", "NEAR_CTHY_2_FOLIOS", "NEAR_VALUE_FORM_2_FOLIOS", "NEAR_AMOUNT_2_FOLIOS"],
        "OBSERVED_EXACT_LANDMARK_PROXIMITY", SRC / "LANDMARK_SPECS.tsv", RAW["tokens"], RAW["cross"])
    add(["VISUAL_WHOLE_PLANT_3", "VISUAL_POOL_3", "VISUAL_MATERIAL_3", "VISUAL_RADIAL_3", "VISUAL_TEXT_3"], "CACHED_VISUAL_CONTEXT_NOT_TOKEN_OWNER", INPUTS["visual"])
    add(["REL_L_BASE", "REL_L_EXPANDED", "REL_DY_BASE", "REL_DY_EXPANDED", "REL_EXTERNAL_RECORD_AGREES", "REL_ED1_SAFE"],
        "FORMAL_RECORD_COMPATIBILITY", INPUTS["events"], SRC / "RELATION_DECISION_SPECS.tsv", SRC / "run.py")
    add(["BOTANICAL_PAGE_CONTEXT_MULTI_FOLIO"], "INHERITED_REPORTED_BOTANICAL_CONTEXT", YOLO / "gdt625_ordered_quality_state_transitions/REPORT.md", SRC / "MANUAL_EVIDENCE_SPECS.tsv")
    return producers


def static_semantic_contract(profiles, manifest):
    producers = producer_contract()
    require(set(producers).isdisjoint(UNAVAILABLE), "unobserved gates cannot have measurement producers")
    used = set()
    for profile in profiles:
        for field in ("required_features", "positive_features", "hard_negative_features", "candidate_specific_gate"):
            terms = parts(profile[field])
            require(terms <= producers.keys() | UNAVAILABLE, f"unknown feature spelling in {profile['candidate_id']}/{field}: {terms - (producers.keys() | UNAVAILABLE)}")
            used |= terms
        require(parts(profile["candidate_specific_gate"]), f"empty identity gate: {profile['candidate_id']}")
    # Require the builder's static absent-evidence vocabulary to agree with the
    # independent registry, without importing any implementation function.
    tree = ast.parse((SRC / "run.py").read_text())
    static_gate = next(node.value for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "GATE_REQUIREMENTS" for t in node.targets))
    require(set(ast.literal_eval(static_gate)) == UNAVAILABLE, "builder absent-evidence gate registry drift")
    bound = {item["path"] for item in manifest["inputs"] + manifest["outputs"]}
    for channel, paths in producers.values():
        require(paths <= bound, f"feature producer provenance missing from manifest: {channel}")
    leaves = {p["historical_lemma"]: p for p in profiles}
    require({"folium/folia", "herba", "OPAQUE_BOTANICAL_HEAD"} <= leaves.keys(), "botanical alternatives omitted")
    for field in ("required_features", "positive_features", "hard_negative_features"):
        require(len({leaves[lemma][field] for lemma in ("folium/folia", "herba", "OPAQUE_BOTANICAL_HEAD")}) == 1, "leaf/herba/opaque must share botanical context")
    manual = read_tsv(SRC / "MANUAL_EVIDENCE_SPECS.tsv")
    for row in manual:
        require(parts(row["evidence_tags"]) <= producers.keys() and not parts(row["evidence_tags"]) & UNAVAILABLE, "manual context fabricated an identity gate")
        require(row["source_report"] in bound, "manual evidence source report not manifest bound")
    block("static_semantic_gate_coverage_and_botanical_equal_evidence", f"{len(used)} referenced terms, {len(UNAVAILABLE)} explicitly unobserved requirements")
    return producers


def feature_state(feature, features, producers):
    if feature in UNAVAILABLE:
        return "UNOBSERVED"
    require(feature in producers, f"unregistered measurement: {feature}")
    if feature in PRIORS:
        return "PRIOR_PRESENT" if feature in features else "PRIOR_NOT_LISTED"
    return "OBSERVED_PRESENT" if feature in features else "OBSERVED_NOT_MET"


def feature_provenance_validation(feature_sets, rows, producers):
    for head, present in feature_sets.items():
        row = rows[head,]
        require(not present & UNAVAILABLE, "unobserved gate materialized as evidence")
        require(parts(row["inherited_prior_features"]) == present & PRIORS, "prior-feature partition")
        require(parts(row["observed_compatibility_features"]) == present - PRIORS, "observed compatibility partition")
        require(parts(row["evidence_channels"]) == {producers[t][0] for t in present}, "feature channel census")
        require(parts(row["source_provenance"]) == {p for t in present for p in producers[t][1]}, "feature source provenance")
        require(row["independent_candidate_identity_evidence"] == "UNOBSERVED", "context promoted to independent identity evidence")
    block("per_feature_prior_observation_and_source_partitions")


def artifact_and_ceiling_validation(manifest, active, ed1, external, relations, semantics, profiles):
    result = json.loads((ART / "RESULT.json").read_text())
    require(result["experiment_id"] == "GDT809" and result["sealed_data"] == SEALS, "result identity and seals")
    same(result["source_census"], {"selectors": 179, "lines": 4137, "tokens": 32339, "strict_paragraphs": 665}, "result source census")
    same(result["head_census"], {"source_union": 41, "active_exact_heads": len(active), "ed1_safe_heads": len(ed1), "rank_stable_occurrences": 1032,
                                 "strict_external_occurrences": len(external)}, "result head census")
    same(result["relation_census"], {"occurrence_edges": 211, "distinct_links": 209, "contacted_pivots": 199, "contacted_folios": 103,
                                     "unique_head_windows": 189, "target_rotations": 24}, "result relation census")
    same(result["ed1_census"], {"occurrence_edges": 91, "distinct_links": 90, "contacted_pivots": 86, "unique_head_windows": 82}, "result ED1 census")
    selected = [f"{r['head']}:{r['axis']}:{r['direction']}" for r in relations if r["relation_conditioned_record_head"] == "1"]
    require(result["relation_census"]["selected_relation_heads"] == selected, "selected relation census")
    identities = [f"{r['head']}:{r['historical_lemma']}" for r in semantics if r["decision"] == "PROVISIONAL_COMPLETE_WHOLE_IDENTITY"]
    same(result["semantic_census"], {"historical_candidates": len(profiles), "candidate_rows": len(profiles) * 35, "working_dictionary_rows": 35,
                                     "confirmed_lexemes": 0, "component_exports": 0}, "semantic census")
    require(result["semantic_census"]["provisional_identities"] == identities, "identity census")
    hashes = result["artifact_sha256"]
    inventory = {p.name for p in ART.glob("GDT809_*") if p.suffix in {".tsv", ".json"}} | {"SOURCE_LOCK.tsv"}
    require(set(hashes) == inventory, f"artifact hash census mismatch: missing {inventory - hashes.keys()}, extra {hashes.keys() - inventory}")
    for name, sha in hashes.items():
        require(digest(ART / name) == sha, f"result artifact hash mismatch: {name}")
    for path in ART.glob("GDT809_*.tsv"):
        for row in read_tsv(path):
            for field, value in row.items():
                if field in {"page", "source_selector", "locus", "physical_folio", "physical_page", "pivot_locus", "target_locus"}:
                    require(not value.startswith("f84"), f"sealed data in {path.name}/{field}")
                if field in {"literal_credit", "semantic_credit", "component_export_credit", "confirmed_lexeme", "automatic_semantic_promotion"}:
                    require(value == "0", f"semantic promotion credit in {path.name}/{field}")
    source_lock = keyed(table("SOURCE_LOCK.tsv"), ("path",))
    bound = {item["path"]: item for item in manifest["inputs"] + manifest["outputs"]}
    minimum = {item["path"] for item in manifest["inputs"]} | {relative(SRC / "run.py"), relative(SRC / "validate.py")}
    require({r[0] for r in source_lock} >= minimum, "source lock missing consumed implementation/input")
    for (path,), row in source_lock.items():
        require(path in bound and row["sha256"] == bound[path]["sha256"] == digest(ROOT / path), f"source lock drift: {path}")
        require(row["manifest_hash_match"] == "1", "unbound source lock")
        if path in {relative(p) for p in RAW.values()}:
            require(row["access_mode"] == "MANIFEST_HASH__GUARDED_QUERY_ONLY", "raw source not guard-only")
    block("result_censuses_artifact_hashes_source_lock_and_zero_export_ceiling", f"{len(hashes)} hashed base artifacts")
    return result


def edge_validation(relations):
    packet_path = ART / "GDT809_GDT388_RELATION_PACKET.tsv"
    rows = read_tsv(packet_path)
    selected = {(r["head"], r["axis"], r["direction"]) for r in relations if r["relation_conditioned_record_head"] == "1"}
    require(len(rows) == len(selected), "GDT388 packet selected-relation census")
    actual = set()
    for row in rows:
        head = row["pivot_visual_id"].removeprefix("EXACT_HEAD_")
        m = re.fullmatch(r"FORMAL_HEAD_TO_(L|DY)_(BASE|EXPANDED)", row["relation_type"])
        require(m is not None, "GDT388 formal relation type")
        actual.add((head, m[1], m[2]))
        same(row, {"geometry_only_selection": "FALSE", "formal_access_state": "FORMAL_ACCESSED",
                   "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION", "page_crop_sha256": "NONE",
                   "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE"}, "packet provenance failure disclosed")
    require(actual == selected, "GDT388 packet association identities")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", relative(packet_path)], cwd=ROOT, text=True, capture_output=True)
    require(completed.returncode == (1 if rows else 0) and not completed.stderr, "GDT388 gate must fail closed")
    gate = json.loads(completed.stdout)
    require(gate == json.loads((ART / "GDT809_GDT388_EDGE_INTAKE.json").read_text()), "GDT388 independent intake differs")
    status = "INVALID_PACKET" if rows else "VALID_ACQUISITION_NOT_SCORE_READY"
    require(gate["score_ready"] is False and gate["eligible_edges"] == 0 and gate["status"] == status, "GDT388 semantic score authorization")
    require(gate["errors"] == [f"edge row {n}: formal access is not sealed" for n in range(2, len(rows) + 2)], "GDT388 unexpected error cause")
    block("executable_GDT388_capacity_holdout_provenance_mobile_null_gate", f"{status} / 0 eligible / score_ready=false")


def candidate_numbers(profile, features, producers):
    required, positive, negative, gate = [parts(profile[f]) for f in ("required_features", "positive_features", "hard_negative_features", "candidate_specific_gate")]
    all_terms = required | positive | negative | gate
    states = {term: feature_state(term, features, producers) for term in all_terms}
    observed = {term for term, state in states.items() if state == "OBSERVED_PRESENT"}
    inherited = features & all_terms & PRIORS
    mr, mp, mn, mg = [terms & observed for terms in (required, positive, negative, gate)]
    return {
        "score": 2 * len(mr) + len(mp) - 2 * len(mn),
        "score_channel": "OBSERVED_CONTEXT_COMPATIBILITY_NOT_IDENTITY",
        "inherited_prior_score": 2 * len(required & inherited) + len(positive & inherited) - 2 * len(negative & inherited),
        "inherited_prior_discriminatory_credit": 0, "matched_inherited_prior_features": packed(sorted(inherited)),
        "required_matches": len(mr), "required_total": len(required - PRIORS), "required_complete": int(mr == required - PRIORS),
        "matched_required_features": packed(sorted(mr)), "missing_required_features": packed(sorted(required - PRIORS - observed)),
        "inherited_prior_required_features": packed(sorted(required & PRIORS)), "positive_matches": len(mp), "positive_total": len(positive - PRIORS),
        "matched_positive_features": packed(sorted(mp)), "hard_negative_matches": len(mn), "matched_hard_negative_features": packed(sorted(mn)),
        "unobserved_hard_negative_features": packed(sorted(negative & UNAVAILABLE)),
        "candidate_gate_matches": len(mg), "candidate_gate_total": len(gate), "candidate_gate_complete": int(mg == gate),
        "candidate_gate_state": "UNOBSERVED" if gate & UNAVAILABLE else "OBSERVED",
        "candidate_gate_reachable_from_current_inputs": int(gate <= producers.keys() and not gate & PRIORS),
        "missing_candidate_gate": packed(sorted(gate - observed)),
        "feature_measurement_states": packed(f"{term}:{states[term]}" for term in sorted(states)),
        "evidence_channels": packed(sorted({producers[t][0] for t in observed})),
        "source_provenance": packed(sorted({p for t in observed for p in producers[t][1]})),
        "inherited_prior_source_provenance": packed(sorted({p for t in inherited for p in producers[t][1]})),
        "formal_ed1_relation_present": int("REL_ED1_SAFE" in features),
        "literal_identity_promotion_authorized": 0, "literal_credit": 0, "component_export_credit": 0,
    }


def family_numbers(row, family):
    scores = [int(r["score"]) for r in family]
    rival_scores = [int(r["score"]) for r in family if r["candidate_id"] != row["candidate_id"]]
    rank = 1 + sum(value > int(row["score"]) for value in scores)
    margin = int(row["score"]) - max(rival_scores) if rival_scores else "NA"
    margin_pass = rank == 1 and (not rival_scores or margin >= 2)
    readiness = bool(margin_pass and int(row["required_complete"]) and int(row["candidate_gate_complete"])
                     and not int(row["hard_negative_matches"]) and int(row["external_folios"]) >= 3)
    return {"family_rank": rank, "family_size": len(family), "family_top_tie_count": scores.count(max(scores)),
            "family_margin": margin, "family_margin_status": "MEASURED_CONTEXT_SCORE_MARGIN" if rival_scores else "SINGLETON_NOT_APPLICABLE",
            "family_margin_gate_pass": int(margin_pass), "exploratory_candidate_readiness": int(readiness),
            "decision": "EXPLORATORY_RIVAL__IDENTITY_GATE_UNOBSERVED" if row["candidate_gate_state"] == "UNOBSERVED" else "EXPLORATORY_RIVAL__NO_LITERAL_PROMOTION_AUTHORITY"}


def semantic_validation(profiles, features, feature_rows, producers):
    actual_rows = table("SEMANTIC_CANDIDATE_SCOREBOARD")
    actual = keyed(actual_rows, ("head", "candidate_id"))
    expected_keys = {(h, p["candidate_id"]) for h in features for p in profiles}
    require(set(actual) == expected_keys, "complete semantic tournament head/candidate grid")
    rebuilt = []
    for head, present in sorted(features.items()):
        for profile in profiles:
            metrics = candidate_numbers(profile, present, producers)
            expected = {**profile, **metrics, "head": head, "external_folios": int(feature_rows[head,]["external_folios"]),
                        "original_18_candidate": int(profile["candidate_id"] in {f"S{i:02d}" for i in range(1, 19)}),
                        "candidate_scope": "OPAQUE_NULL" if profile["historical_lemma"] == "OPAQUE_BOTANICAL_HEAD" else "EXPLORATORY_HISTORICAL_RIVAL"}
            for source_only in ("required_features", "positive_features", "hard_negative_features", "candidate_specific_gate"):
                del expected[source_only]
            same(actual[head, profile["candidate_id"]], expected, f"candidate {head}/{profile['candidate_id']}")
            rebuilt.append(expected)
    grouped = defaultdict(list)
    for row in rebuilt:
        grouped[row["head"], row["family"]].append(row)
    for rows in grouped.values():
        for row in rows:
            expected = family_numbers(row, rows)
            same(actual[row["head"], row["candidate_id"]], expected, "candidate family rank/margin")
            row.update(expected)
    coverage = table("CANDIDATE_GATE_COVERAGE")
    actual_coverage = keyed(coverage, ("head", "candidate_id", "candidate_gate_feature"))
    coverage_keys = {(h, p["candidate_id"], term) for h in features for p in profiles for term in parts(p["candidate_specific_gate"])}
    require(set(actual_coverage) == coverage_keys, "candidate-specific gate coverage census")
    for profile in profiles:
        for head, present in features.items():
            for term in parts(profile["candidate_specific_gate"]):
                row = actual_coverage[head, profile["candidate_id"], term]
                state = feature_state(term, present, producers)
                source = producers.get(term)
                same(row, {"candidate_de": profile["candidate_de"], "gate_state": state,
                           "observed_gate_value": int(state == "OBSERVED_PRESENT") if source else "NA",
                           "registered_producer_available": int(source is not None),
                           "gate_reachable_from_current_inputs": int(source is not None and term not in PRIORS),
                           "evidence_channel": source[0] if source else "UNOBSERVED_CANDIDATE_SPECIFIC_EVIDENCE",
                           "source_provenance": packed(sorted(source[1])) if source else "NONE",
                           "requirement_spec_source": relative(SRC / "SEMANTIC_PROFILE_SPECS.tsv"),
                           "unobserved_is_not_counterevidence": 1, "literal_identity_promotion_authorized": 0,
                           "confirmed_lexeme": 0, "component_export_credit": 0}, "identity evidence state")
                require(row["required_new_discriminator"], "unobserved gate lacks requested discriminator")
    dictionary = keyed(table("35_WORKING_DICTIONARY"), ("head",))
    require(set(dictionary) == {(h,) for h in features}, "one dictionary card per head")
    for head in features:
        values = sorted((r for r in rebuilt if r["head"] == head), key=lambda r: (-r["score"], r["candidate_id"]))
        best = values[0]
        tied = [r for r in values if r["score"] == best["score"]]
        feature_row = feature_rows[head,]
        expected = {"structural_role_default_de": feature_row["role_default_de"], "structural_role_evidence_channel": "INHERITED_SEMANTIC_PRIOR",
                    "registered_prior_role": feature_row["registered_prior_role"], "best_concrete_candidate_de": packed(r["candidate_de"] for r in tied),
                    "best_historical_lemma": packed(r["historical_lemma"] for r in tied), "best_candidate_score": best["score"],
                    "best_candidate_decision": best["decision"], "confidence": "C0_EXPLORATORY_CONTEXT_TIE" if len(tied) > 1 else "C0_EXPLORATORY_CONTEXT_RANK",
                    "top_tied_candidate_ids": packed(r["candidate_id"] for r in tied), "top_tie_count": len(tied),
                    "second_candidate_de": values[1]["candidate_de"], "third_candidate_de": values[2]["candidate_de"],
                    "relation_summary": feature_row["relation_summary"],
                    "observed_context_compatibility": packed(sorted({term for r in tied for field in ("matched_required_features", "matched_positive_features") for term in parts(r[field])})),
                    "inherited_prior_support": packed(sorted({term for r in tied for term in parts(r["matched_inherited_prior_features"])})),
                    "unobserved_identity_gates": packed(sorted({term for r in tied for term in parts(r["missing_candidate_gate"])})),
                    "observed_profile_counterevidence": packed(sorted({term for r in tied for term in parts(r["matched_hard_negative_features"])})),
                    "unobserved_evidence_is_not_falsehood": 1, "literal_identity_selected": 0, "hypothesis_not_plaintext": 1,
                    "confirmed_lexeme": 0, "component_export_credit": 0}
        same(dictionary[head,], expected, f"tie-preserving dictionary {head}")
    block("independent_candidate_scores_competition_ranks_margins_and_dictionary_ties", f"{len(rebuilt)} scores / {len(coverage)} gate states / 35 dictionary cards")
    return actual_rows


def regression_tests(profiles, producers):
    # Injecting an unavailable gate name into a feature set must not produce an
    # observation. This also distinguishes unknown negatives from measured ones.
    fixture = {"required_features": "SOURCE_CONTENT_HEAD", "positive_features": "NONE",
               "hard_negative_features": "MANUAL_ROOT_OWNER_MULTI_FOLIO", "candidate_specific_gate": "MANUAL_LEAF_OWNER_MULTI_FOLIO"}
    metrics = candidate_numbers(fixture, {"SOURCE_CONTENT_HEAD", "MANUAL_LEAF_OWNER_MULTI_FOLIO", "MANUAL_ROOT_OWNER_MULTI_FOLIO"}, producers)
    require(metrics["candidate_gate_complete"] == 0 and metrics["hard_negative_matches"] == 0 and metrics["candidate_gate_state"] == "UNOBSERVED", "unavailable evidence must neither win nor become a negative")
    row = {**metrics, "candidate_id": "FIXTURE_A", "external_folios": 9}
    require(family_numbers(row, [row])["exploratory_candidate_readiness"] == 0, "unobserved singleton fabricated identity readiness")
    by_lemma = {p["historical_lemma"]: p for p in profiles}
    broad_botanical = {"SOURCE_CONTENT_HEAD", "PRIOR_MATERIAL", "HERBAL_DOMINANT_90", "BOTANICAL_PAGE_CONTEXT_MULTI_FOLIO",
                       "AMOUNT_CONTACT_ANY", "NEAR_CHOR_SHOR_2_FOLIOS", "VISUAL_WHOLE_PLANT_3", "REL_L_BASE", "REL_EXTERNAL_RECORD_AGREES"}
    rivals = [candidate_numbers(by_lemma[lemma], broad_botanical, producers) for lemma in ("folium/folia", "herba", "OPAQUE_BOTANICAL_HEAD")]
    require(len({r["score"] for r in rivals}) == 1 and all(r["candidate_gate_complete"] == 0 for r in rivals), "leaf/herba/opaque equal-evidence regression")
    family = [{**r, "candidate_id": f"TEST_{i}", "external_folios": 6} for i, r in enumerate(rivals)]
    require(all(family_numbers(r, family)["family_rank"] == 1 and family_numbers(r, family)["family_margin"] == 0 and not family_numbers(r, family)["family_margin_gate_pass"] for r in family), "score ties must preserve all alternatives")
    singleton = family_numbers(family[0], [family[0]])
    require(singleton["family_margin"] == "NA" and singleton["family_margin_status"] == "SINGLETON_NOT_APPLICABLE", "singleton must not fabricate rival margin")
    plain = candidate_numbers(fixture, {"SOURCE_CONTENT_HEAD"}, producers)
    prior_fixture = {**fixture, "positive_features": "PRIOR_HOT|PRIOR_DRY|PRIOR_MOIST"}
    augmented = candidate_numbers(prior_fixture, {"SOURCE_CONTENT_HEAD", "PRIOR_HOT", "PRIOR_DRY", "PRIOR_MOIST"}, producers)
    require(plain["score"] == augmented["score"] and augmented["inherited_prior_score"] == 3, "inherited meanings must not add discriminatory score")
    block("counterfactual_semantic_regressions", "unavailable gate; unknown negative; leaf/herba/opaque equal evidence; top ties; singleton NA; prior zero-credit")


def joint_validation():
    validator = SRC / "validate_joint.py"
    require(validator.is_file(), "independent joint paragraph validator missing")
    completed = subprocess.run([sys.executable, relative(validator), "--no-write"], cwd=ROOT, text=True, capture_output=True)
    require(completed.returncode == 0, f"independent joint paragraph validation failed: {completed.stdout.strip()} {completed.stderr.strip()}")
    output = json.loads(completed.stdout)
    require(output.get("status") == "PASS", "joint paragraph validator did not pass")
    block("independent_joint_paragraph_candidate_scope_and_prediction_validation", f"{output.get('checks_passed', 'all')} joint checks passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registration", action="store_true", help="validate frozen source/spec contracts without scoring")
    parser.add_argument("--no-write", action="store_true", help="never write a validation artifact")
    args = parser.parse_args()
    error = None
    try:
        manifest, spec, active, ed1, q152, profiles = registration()
        producers = static_semantic_contract(profiles, manifest)
        regression_tests(profiles, producers)
        if not args.registration:
            lines, line_map = corpus()
            events = read_tsv(INPUTS["events"])
            contact_sets = validate_contacts(events, line_map, active, ed1, spec)
            external = occurrence_atlas(lines, events, active, q152)
            relations, ed1_relations = relation_validation(events, line_map, external, active, ed1, contact_sets)
            features, feature_rows = feature_validation(external, spec, active, relations, ed1_relations)
            feature_provenance_validation(features, feature_rows, producers)
            semantic = semantic_validation(profiles, features, feature_rows, producers)
            edge_validation(relations)
            artifact_and_ceiling_validation(manifest, active, ed1, external, relations, semantic, profiles)
            joint_validation()
    except (AssertionError, KeyError, ValueError, OSError, StopIteration) as exc:
        error = f"{type(exc).__name__}: {exc}".replace(str(ROOT), "<REPOSITORY>")
    report = {"experiment_id": "GDT809", "status": "FAIL" if error else "PASS", "mode": "REGISTRATION" if args.registration else "FULL_INDEPENDENT",
              "checks": len(CHECKS), "check_results": CHECKS, "errors": [error] if error else [], "sealed_data": SEALS,
              "validator_sha256": digest(Path(__file__).resolve()), "builder_imported": False, "confirmed_lexemes": 0,
              "automatic_semantic_promotion": False}
    if not args.no_write:
        target = ART / ("REGISTERED_VALIDATION.json" if args.registration else "VALIDATION.json")
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("experiment_id", "status", "mode", "checks", "errors")}, sort_keys=True))
    return int(error is not None)


if __name__ == "__main__":
    raise SystemExit(main())
