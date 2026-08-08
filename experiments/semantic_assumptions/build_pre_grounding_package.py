#!/usr/bin/env python3
"""Build a clean, meaning-free package for later authorial grounding.

The package uses only the three locked manual transcriptions, the confirmed
formal parser, the primary confirmed role edges, and active structural budget
artifacts.  It deliberately imports no archived semantic/contextual overlay.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
ARCHIVE = BASE / "archive_pre_reset_2026-08-06" / "semantic_assumptions"
RESULTS = HERE / "results"
CORE_INPUT = RESULTS / "minimal_lexical_anchor_budget.json"
COVERAGE_INPUT = RESULTS / "unseen_combination_coverage_audit.json"
HYBRID_INPUT = RESULTS / "hybrid_anchor_budget.json"
EDGE_INPUT = ARCHIVE / "results" / "exact_role_transition_atlas_results.json"
PRIMARY_EVIDENCE = HERE / "grammar" / "PRIMARY_EVIDENCE.tsv"
OUTPUT_INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
OUTPUT_LOCI = RESULTS / "pre_grounding_locus_atlas.tsv"
OUTPUT_ROOTS = RESULTS / "pre_grounding_root_atlas.tsv"
OUTPUT_TUPLES = RESULTS / "pre_grounding_tuple_atlas.tsv"
OUTPUT_RELATIONS = RESULTS / "pre_grounding_relation_atlas.tsv"
OUTPUT_MANIFEST = RESULTS / "pre_grounding_package_manifest.json"
OUTPUT_REPORT = RESULTS / "pre_grounding_package_report.md"

SOURCES = {
    "ZL3b": BASE / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": BASE / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": BASE / "transcription" / "sources" / "RF1b-e.txt",
}

sys.path.insert(0, str(ARCHIVE))
from common import parse_rows  # noqa: E402
from run_initial_bare_carrier_state_system import carrier_root  # noqa: E402
from run_internal_utterance_grammar import line_nodes  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: Iterable[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def tuple_text(root: tuple[str, ...]) -> str:
    return "+".join(root)


def counter_text(counter: Counter, limit: int | None = None) -> str:
    rows = counter.most_common(limit)
    return ";".join(f"{value}:{count}" for value, count in rows)


def root_label(root: str, core_ids: dict[str, str]) -> str:
    return core_ids.get(root, f"R:{root}")


def node_text(node, core_ids: dict[str, str], hybrid_atoms: set[str], hybrid_tuples: set[tuple[str, ...]]) -> str:
    roots = "+".join(root_label(root, core_ids) for root in node.roots)
    roles = "+".join(node.roles)
    if node.roots in hybrid_tuples:
        hybrid = "EXACT"
    elif set(node.roots) <= hybrid_atoms:
        hybrid = "COMP"
    else:
        hybrid = "OPEN"
    return f"{node.surface}={roots}[{roles}]{{H95:{hybrid}}}"


def line_scope(row) -> str:
    return "CONFIRMED_PROSE" if row.kind == "P" and row.language in {"A", "B"} else "DIAGNOSTIC_NONPROSE"


def stable_set_text(values: list[set[str]], operation: str) -> str:
    if not values:
        return ""
    selected = set.intersection(*values) if operation == "intersection" else set.union(*values)
    return ";".join(sorted(selected))


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    core_payload = json.loads(CORE_INPUT.read_text(encoding="utf-8"))
    coverage_payload = json.loads(COVERAGE_INPUT.read_text(encoding="utf-8"))
    hybrid_payload = json.loads(HYBRID_INPUT.read_text(encoding="utf-8"))
    edge_payload = json.loads(EDGE_INPUT.read_text(encoding="utf-8"))
    core = tuple(core_payload["core_roots"])
    core_ids = {root: f"C{index:02d}" for index, root in enumerate(core, 1)}
    core_set = set(core)
    supported = set(hybrid_payload["supported_component_atoms"])
    sparse = set(hybrid_payload["sparse_atomic_candidates"])
    if supported | sparse != core_set or supported & sparse:
        raise RuntimeError("hybrid 21/13 partition does not equal core34")
    hybrid95 = hybrid_payload["solutions"]["worst_reading"]["0.950"]
    hybrid_atoms = set(hybrid95["component_atoms"])
    hybrid_tuples = {tuple(value.split("+")) for value in hybrid95["exact_tuples"]}
    positive_edges = set(edge_payload["confirmed_positive_pairs"])

    rows_by_edition = {}
    for edition, path in SOURCES.items():
        selected = parse_rows(path)
        mapping = {row.locus: row for row in selected}
        if len(mapping) != len(selected):
            raise RuntimeError(f"duplicate loci in {edition}")
        rows_by_edition[edition] = mapping

    interlinear_rows = []
    line_cache: dict[tuple[str, str], dict[str, Any]] = {}
    root_profiles = {edition: defaultdict(lambda: {
        "all_count": 0, "prose_count": 0, "pages": set(), "sections": set(),
        "kinds": Counter(), "roles": Counter(), "standalone": 0, "compound": 0,
        "line_start": 0, "line_end": 0, "selector": 0, "dependent": 0,
        "left_neighbors": Counter(), "right_neighbors": Counter(),
        "tuple_partners": Counter(),
    }) for edition in SOURCES}
    tuple_profiles = {edition: defaultdict(lambda: {
        "all_count": 0, "prose_count": 0, "pages": set(), "sections": set(),
        "kinds": Counter(), "roles": Counter(), "line_start": 0, "line_end": 0,
        "surfaces": Counter(),
    }) for edition in SOURCES}
    relation_profiles = {edition: defaultdict(lambda: {
        "count": 0, "pages": set(), "sections": set(), "role_edges": Counter(),
    }) for edition in SOURCES}

    for edition, rows in rows_by_edition.items():
        for locus, row in rows.items():
            nodes = line_nodes(row)
            scope = line_scope(row)
            exact_edges = []
            if scope == "CONFIRMED_PROSE":
                for index, (left, right) in enumerate(zip(nodes, nodes[1:]), 1):
                    role_edge = f"{left.last_role}>{right.first_role}"
                    if role_edge in positive_edges:
                        exact_edges.append(f"W{index}>W{index + 1}:{role_edge}")
            root_sequence = tuple(node.roots for node in nodes)
            role_sequence = tuple(node.roles for node in nodes)
            fully_core = sum(set(node.roots) <= core_set for node in nodes)
            hybrid_covered = sum(
                node.roots in hybrid_tuples or set(node.roots) <= hybrid_atoms
                for node in nodes
            )
            item = {
                "edition": edition,
                "locus": locus,
                "page": row.page,
                "section": row.section,
                "currier": row.language,
                "hand": row.hand,
                "code": row.code,
                "kind": row.kind,
                "grammar_scope": scope,
                "paragraph_state": "OPEN" if row.paragraph_start else "CONT",
                "line_carrier": (carrier_root(row.words[0]) or "") if scope == "CONFIRMED_PROSE" and row.words else "",
                "word_count": len(nodes),
                "surface": " ".join(row.words),
                "root_sequence": " ".join(tuple_text(node.roots) for node in nodes),
                "role_sequence": " ".join("+".join(node.roles) for node in nodes),
                "formal_interlinear": " | ".join(
                    node_text(node, core_ids, hybrid_atoms, hybrid_tuples) for node in nodes
                ),
                "confirmed_edges": ";".join(exact_edges),
                "core34_covered_words": fully_core,
                "hybrid95_covered_words": hybrid_covered,
            }
            interlinear_rows.append(item)
            line_cache[(edition, locus)] = {
                **item,
                "root_sequence_value": root_sequence,
                "role_sequence_value": role_sequence,
                "core_atoms": {root for node in nodes for root in node.roots if root in core_set},
                "edge_set": set(exact_edges),
            }

            for word_index, node in enumerate(nodes):
                tuple_profile = tuple_profiles[edition][node.roots]
                tuple_profile["all_count"] += 1
                tuple_profile["prose_count"] += int(scope == "CONFIRMED_PROSE")
                tuple_profile["pages"].add(row.page)
                tuple_profile["sections"].add(row.section)
                tuple_profile["kinds"][row.kind] += 1
                if scope == "CONFIRMED_PROSE":
                    tuple_profile["roles"]["+".join(node.roles)] += 1
                    tuple_profile["line_start"] += int(word_index == 0)
                    tuple_profile["line_end"] += int(word_index == len(nodes) - 1)
                tuple_profile["surfaces"][node.surface] += 1

                for root_index, (root, role) in enumerate(zip(node.roots, node.roles)):
                    profile = root_profiles[edition][root]
                    profile["all_count"] += 1
                    profile["prose_count"] += int(scope == "CONFIRMED_PROSE")
                    profile["pages"].add(row.page)
                    profile["sections"].add(row.section)
                    profile["kinds"][row.kind] += 1
                    if scope == "CONFIRMED_PROSE":
                        profile["roles"][role] += 1
                        profile["line_start"] += int(word_index == 0)
                        profile["line_end"] += int(word_index == len(nodes) - 1)
                    profile["standalone"] += int(len(node.roots) == 1)
                    profile["compound"] += int(len(node.roots) > 1)
                    profile["tuple_partners"].update(
                        partner for index, partner in enumerate(node.roots) if index != root_index
                    )
                    if word_index > 0:
                        profile["left_neighbors"].update(nodes[word_index - 1].roots)
                    if word_index + 1 < len(nodes):
                        profile["right_neighbors"].update(nodes[word_index + 1].roots)

            if scope == "CONFIRMED_PROSE":
                for left, right in zip(nodes, nodes[1:]):
                    role_edge = f"{left.last_role}>{right.first_role}"
                    relation = relation_profiles[edition][(left.roots, right.roots)]
                    relation["count"] += 1
                    relation["pages"].add(row.page)
                    relation["sections"].add(row.section)
                    relation["role_edges"][role_edge] += 1
                    if role_edge in positive_edges:
                        root_profiles[edition][left.last_root]["selector"] += 1
                        root_profiles[edition][right.first_root]["dependent"] += 1

    interlinear_fields = [
        "edition", "locus", "page", "section", "currier", "hand", "code", "kind",
        "grammar_scope", "paragraph_state", "line_carrier", "word_count", "surface",
        "root_sequence", "role_sequence", "formal_interlinear", "confirmed_edges",
        "core34_covered_words", "hybrid95_covered_words",
    ]
    interlinear_rows.sort(key=lambda row: (row["edition"], row["page"], row["locus"]))
    write_tsv(OUTPUT_INTERLINEAR, interlinear_rows, interlinear_fields)

    locus_rows = []
    all_loci = sorted(set().union(*(set(rows) for rows in rows_by_edition.values())))
    for locus in all_loci:
        items = [line_cache[(edition, locus)] for edition in SOURCES if (edition, locus) in line_cache]
        editions = [item["edition"] for item in items]
        exact_surface = len(items) == len(SOURCES) and len({item["surface"] for item in items}) == 1
        exact_roots = len(items) == len(SOURCES) and len({item["root_sequence_value"] for item in items}) == 1
        exact_roles = len(items) == len(SOURCES) and len({item["role_sequence_value"] for item in items}) == 1
        if len(items) < len(SOURCES):
            status = "MISSING_READING"
        elif exact_surface:
            status = "EXACT_SURFACE"
        elif exact_roots:
            status = "EXACT_ROOT_SEQUENCE"
        elif exact_roles:
            status = "ROLE_SEQUENCE_ONLY"
        else:
            status = "READING_DISAGREEMENT"
        primary = next((item for item in items if item["edition"] == "ZL3b"), items[0])
        locus_rows.append({
            "locus": locus,
            "page": primary["page"],
            "section": primary["section"],
            "currier": primary["currier"],
            "hand": primary["hand"],
            "kind": primary["kind"],
            "readings_present": ";".join(editions),
            "reading_status": status,
            "exact_surface_all": int(exact_surface),
            "exact_root_sequence_all": int(exact_roots),
            "exact_role_sequence_all": int(exact_roles),
            "word_counts": ";".join(f"{item['edition']}:{item['word_count']}" for item in items),
            "stable_core_atoms": stable_set_text([item["core_atoms"] for item in items], "intersection"),
            "union_core_atoms": stable_set_text([item["core_atoms"] for item in items], "union"),
            "stable_confirmed_edges": stable_set_text([item["edge_set"] for item in items], "intersection"),
            "union_confirmed_edges": stable_set_text([item["edge_set"] for item in items], "union"),
            "minimum_core34_word_coverage": min(item["core34_covered_words"] / max(item["word_count"], 1) for item in items),
            "minimum_hybrid95_word_coverage": min(item["hybrid95_covered_words"] / max(item["word_count"], 1) for item in items),
        })
    locus_fields = [
        "locus", "page", "section", "currier", "hand", "kind", "readings_present",
        "reading_status", "exact_surface_all", "exact_root_sequence_all", "exact_role_sequence_all",
        "word_counts", "stable_core_atoms", "union_core_atoms", "stable_confirmed_edges",
        "union_confirmed_edges", "minimum_core34_word_coverage", "minimum_hybrid95_word_coverage",
    ]
    write_tsv(OUTPUT_LOCI, locus_rows, locus_fields)

    all_roots = sorted(set().union(*(
        set(profiles) for profiles in root_profiles.values()
    )))
    root_rows = []
    for root in all_roots:
        if root in supported:
            hybrid_class = "SUPPORTED_COMPONENT"
        elif root in sparse:
            hybrid_class = "SPARSE_CORE_ATOM"
        else:
            hybrid_class = "NONCORE"
        row = {
            "root": root,
            "core_id": core_ids.get(root, ""),
            "hybrid_class": hybrid_class,
            "present_all_readings": int(all(root in root_profiles[edition] for edition in SOURCES)),
        }
        dominant_roles = []
        for edition in SOURCES:
            profile = root_profiles[edition].get(root)
            prefix = f"{edition}_"
            if profile is None:
                for field in (
                    "all_count", "prose_count", "pages", "sections", "standalone_share",
                    "line_start_share", "line_end_share", "selector", "dependent",
                    "dominant_role", "role_counts", "kind_counts", "left_neighbors",
                    "right_neighbors", "tuple_partners",
                ):
                    row[prefix + field] = ""
                continue
            prose = profile["prose_count"]
            count = profile["all_count"]
            dominant = profile["roles"].most_common(1)[0][0] if profile["roles"] else ""
            if dominant:
                dominant_roles.append(dominant)
            row.update({
                prefix + "all_count": count,
                prefix + "prose_count": prose,
                prefix + "pages": len(profile["pages"]),
                prefix + "sections": len(profile["sections"]),
                prefix + "standalone_share": profile["standalone"] / count if count else 0.0,
                prefix + "line_start_share": profile["line_start"] / prose if prose else 0.0,
                prefix + "line_end_share": profile["line_end"] / prose if prose else 0.0,
                prefix + "selector": profile["selector"],
                prefix + "dependent": profile["dependent"],
                prefix + "dominant_role": dominant,
                prefix + "role_counts": counter_text(profile["roles"]),
                prefix + "kind_counts": counter_text(profile["kinds"]),
                prefix + "left_neighbors": counter_text(profile["left_neighbors"], 8),
                prefix + "right_neighbors": counter_text(profile["right_neighbors"], 8),
                prefix + "tuple_partners": counter_text(profile["tuple_partners"], 8),
            })
        row["stable_dominant_role"] = dominant_roles[0] if len(dominant_roles) == len(SOURCES) and len(set(dominant_roles)) == 1 else ""
        root_rows.append(row)
    root_fields = ["root", "core_id", "hybrid_class", "present_all_readings", "stable_dominant_role"] + [
        f"{edition}_{field}" for edition in SOURCES for field in (
            "all_count", "prose_count", "pages", "sections", "standalone_share",
            "line_start_share", "line_end_share", "selector", "dependent",
            "dominant_role", "role_counts", "kind_counts", "left_neighbors",
            "right_neighbors", "tuple_partners",
        )
    ]
    write_tsv(OUTPUT_ROOTS, root_rows, root_fields)

    all_tuples = sorted(set().union(*(set(profiles) for profiles in tuple_profiles.values())))
    tuple_rows = []
    for root in all_tuples:
        if set(root) <= supported:
            structural_class = "SUPPORTED_COMPONENT_TUPLE"
        elif set(root) <= core_set:
            structural_class = "CORE34_SPARSE_OR_MIXED"
        else:
            structural_class = "NONCORE_PRESENT"
        if root in hybrid_tuples:
            hybrid95_unit = "ATOMIC_SINGLETON" if len(root) == 1 else "EXACT_TUPLE_EXCEPTION"
        elif set(root) <= hybrid_atoms:
            hybrid95_unit = "COMPOSED_FROM_SELECTED_ATOMS"
        else:
            hybrid95_unit = "UNCOVERED_AT_95"
        row = {
            "root_tuple": tuple_text(root),
            "atom_count": len(root),
            "structural_class": structural_class,
            "hybrid95_status": hybrid95_unit,
            "present_all_readings": int(all(root in tuple_profiles[edition] for edition in SOURCES)),
        }
        for edition in SOURCES:
            profile = tuple_profiles[edition].get(root)
            prefix = f"{edition}_"
            if profile is None:
                for field in ("count", "prose_count", "pages", "sections", "dominant_role_pattern", "role_patterns", "kind_counts", "top_surfaces", "line_start_share", "line_end_share"):
                    row[prefix + field] = ""
                continue
            prose = profile["prose_count"]
            row.update({
                prefix + "count": profile["all_count"],
                prefix + "prose_count": prose,
                prefix + "pages": len(profile["pages"]),
                prefix + "sections": len(profile["sections"]),
                prefix + "dominant_role_pattern": profile["roles"].most_common(1)[0][0] if profile["roles"] else "",
                prefix + "role_patterns": counter_text(profile["roles"]),
                prefix + "kind_counts": counter_text(profile["kinds"]),
                prefix + "top_surfaces": counter_text(profile["surfaces"], 8),
                prefix + "line_start_share": profile["line_start"] / prose if prose else 0.0,
                prefix + "line_end_share": profile["line_end"] / prose if prose else 0.0,
            })
        tuple_rows.append(row)
    tuple_fields = ["root_tuple", "atom_count", "structural_class", "hybrid95_status", "present_all_readings"] + [
        f"{edition}_{field}" for edition in SOURCES for field in (
            "count", "prose_count", "pages", "sections", "dominant_role_pattern",
            "role_patterns", "kind_counts", "top_surfaces", "line_start_share", "line_end_share",
        )
    ]
    write_tsv(OUTPUT_TUPLES, tuple_rows, tuple_fields)

    all_relations = sorted(set().union(*(set(profiles) for profiles in relation_profiles.values())))
    relation_rows = []
    for left, right in all_relations:
        row = {
            "left_tuple": tuple_text(left),
            "right_tuple": tuple_text(right),
            "present_all_readings": int(all((left, right) in relation_profiles[edition] for edition in SOURCES)),
        }
        stable_positive = []
        for edition in SOURCES:
            profile = relation_profiles[edition].get((left, right))
            prefix = f"{edition}_"
            if profile is None:
                row.update({prefix + "count": "", prefix + "pages": "", prefix + "sections": "", prefix + "role_edges": ""})
                stable_positive.append(set())
            else:
                row.update({
                    prefix + "count": profile["count"],
                    prefix + "pages": len(profile["pages"]),
                    prefix + "sections": len(profile["sections"]),
                    prefix + "role_edges": counter_text(profile["role_edges"]),
                })
                stable_positive.append(set(profile["role_edges"]) & positive_edges)
        row["stable_confirmed_role_edges"] = stable_set_text(stable_positive, "intersection")
        relation_rows.append(row)
    relation_fields = ["left_tuple", "right_tuple", "present_all_readings", "stable_confirmed_role_edges"] + [
        f"{edition}_{field}" for edition in SOURCES for field in ("count", "pages", "sections", "role_edges")
    ]
    write_tsv(OUTPUT_RELATIONS, relation_rows, relation_fields)

    status_counts = Counter(row["reading_status"] for row in locus_rows)
    scope_counts = Counter(row["grammar_scope"] for row in interlinear_rows)
    manifest = {
        "decision": "PRE_GROUNDING_INFORMATION_PACKAGE_COMPLETE",
        "english_lexical_glosses": 0,
        "core_atoms": len(core),
        "supported_components": len(supported),
        "sparse_core_atoms": len(sparse),
        "hybrid95_units": len(hybrid_atoms) + len(hybrid_tuples),
        "hybrid95_component_atoms": len(hybrid_atoms),
        "hybrid95_exact_exceptions": len(hybrid_tuples),
        "interlinear_rows": len(interlinear_rows),
        "physical_loci": len(locus_rows),
        "root_types": len(root_rows),
        "tuple_types": len(tuple_rows),
        "adjacent_tuple_relations": len(relation_rows),
        "scope_counts": dict(scope_counts),
        "reading_status_counts": dict(status_counts),
        "confirmed_role_edges": sorted(positive_edges),
        "inputs": {
            **{edition: sha256(path) for edition, path in SOURCES.items()},
            "core": sha256(CORE_INPUT),
            "coverage": sha256(COVERAGE_INPUT),
            "hybrid": sha256(HYBRID_INPUT),
            "role_edges": sha256(EDGE_INPUT),
            "primary_evidence": sha256(PRIMARY_EVIDENCE),
        },
    }
    output_paths = [OUTPUT_INTERLINEAR, OUTPUT_LOCI, OUTPUT_ROOTS, OUTPUT_TUPLES, OUTPUT_RELATIONS]
    manifest["outputs"] = {path.name: {"sha256": sha256(path), "bytes": path.stat().st_size} for path in output_paths}
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    OUTPUT_REPORT.write_text(f"""# Pre-grounding structural information package

Decision: **PRE_GROUNDING_INFORMATION_PACKAGE_COMPLETE**.

This clean package contains every available manual-transcription locus and no
English lexical gloss.  Confirmed prose grammar is kept separate from
diagnostic projections on labels and other non-prose text.  ZL3b, IT2a, and
RF1b remain alternate readings of the same physical loci.

| artifact | rows | purpose |
|---|---:|---|
| `{OUTPUT_INTERLINEAR.name}` | {len(interlinear_rows)} | complete reading-specific surface/root/role interlinear |
| `{OUTPUT_LOCI.name}` | {len(locus_rows)} | physical-locus agreement and uncertainty across readings |
| `{OUTPUT_ROOTS.name}` | {len(root_rows)} | root occurrence, role, boundary, neighbor and tuple-partner profiles |
| `{OUTPUT_TUPLES.name}` | {len(tuple_rows)} | exact root-tuple inventory and hybrid-coverage state |
| `{OUTPUT_RELATIONS.name}` | {len(relation_rows)} | all prose adjacent-tuple counts and role-edge profiles |

Grammar scopes: {dict(scope_counts)}.  Reading agreement states:
{dict(status_counts)}.

The hybrid 95% layer contains **{len(hybrid_atoms)} candidate component atoms**
and **{len(hybrid_tuples)} exact exceptions**.  `COMP`, `EXACT`, and `OPEN` in
the interlinear are acquisition states, not morphemes, words, or meanings.

Pair counts and non-prose role projections are diagnostic inventories.  Only
the six role transitions listed in the manifest inherit confirmed status, and
the aggregate adjacency relation—not each listed lexical pair—is confirmed.

The package is now the input boundary for any later manually authored
image/grammar hypothesis: a proposed meaning must survive all occurrences,
formal roles, readings, sections, and counterexamples shown here.  No OCR,
automated image recognition, dictionary, contextual overlay, or proposed
English gloss was loaded.
""", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
