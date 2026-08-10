#!/usr/bin/env python3
"""Controls and one target for the public f67/f68 circular class-phase test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
METHOD = BASE / "CIRCLE_EDITORIAL_CLASS_PHASE_METHOD.md"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PAGES_SOURCE = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
CONTROLS = RESULTS / "circle_editorial_class_phase_controls.json"
CONTROL_REPORT = RESULTS / "circle_editorial_class_phase_controls_report.md"
OUT = RESULTS / "circle_editorial_class_phase.json"
REPORT = RESULTS / "circle_editorial_class_phase_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
FOLIO_PAGES = {
    "f67": ("f67r1", "f67r2", "f67v1", "f67v2"),
    "f68": ("f68r1", "f68r2", "f68r3", "f68v1", "f68v2", "f68v3"),
}
OBSERVED = {
    "f67": ("A", "A", "A", "C"),
    "f68": ("A", "A", "A", "C", "A", "C"),
}
TOL = 1e-15


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def rotate(values: tuple[str, ...], shift: int) -> tuple[str, ...]:
    return tuple(values[(index - shift) % len(values)] for index in range(len(values)))


def phase_assignments(labels: dict[str, tuple[str, ...]]) -> list[dict[str, tuple[str, ...]]]:
    rows = [
        {folio: rotate(labels[folio], shift) for folio, shift in zip(FOLIO_PAGES, shifts)}
        for shifts in itertools.product(*(range(len(FOLIO_PAGES[folio])) for folio in FOLIO_PAGES))
    ]
    keys = {tuple((folio, row[folio]) for folio in FOLIO_PAGES) for row in rows}
    if len(rows) != len(keys):
        raise AssertionError("phase assignments are not unique")
    return rows


def page_pairs(folio: str) -> list[tuple[str, str]]:
    pages = FOLIO_PAGES[folio]
    return [(pages[i], pages[j]) for i in range(len(pages)) for j in range(i + 1, len(pages))]


def evaluate(matrices: dict, labels: dict[str, tuple[str, ...]], views: tuple[str, ...] = VIEWS) -> dict[str, object]:
    z = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    diagnostics = {}
    for reading in READINGS:
        diagnostics[reading] = {}
        for view in views:
            diagnostics[reading][view] = {}
            for folio in FOLIO_PAGES:
                pairs = page_pairs(folio)
                values = [matrices[reading][view][folio][pair] for pair in pairs]
                center = statistics.fmean(values)
                scale = math.sqrt(statistics.fmean((value - center) ** 2 for value in values))
                diagnostics[reading][view][folio] = {"mean": center, "population_sd": scale}
                if not math.isfinite(scale) or scale <= 0:
                    return {"eligible": False, "reason": f"zero_or_nonfinite_sd:{reading}:{view}:{folio}"}
                for pair, value in zip(pairs, values):
                    z[reading][view][folio][pair] = (value - center) / scale

    assignments = phase_assignments(labels)
    orbit = []
    for assignment in assignments:
        reading_scores = {}
        reading_folio = {}
        for reading in READINGS:
            reading_folio[reading] = {}
            for folio in FOLIO_PAGES:
                pages = FOLIO_PAGES[folio]
                state = dict(zip(pages, assignment[folio]))
                per_view = []
                for view in views:
                    same = [z[reading][view][folio][pair] for pair in page_pairs(folio) if state[pair[0]] == state[pair[1]]]
                    different = [z[reading][view][folio][pair] for pair in page_pairs(folio) if state[pair[0]] != state[pair[1]]]
                    if not same or not different:
                        raise AssertionError("phase has empty comparison class")
                    per_view.append(statistics.fmean(same) - statistics.fmean(different))
                reading_folio[reading][folio] = statistics.fmean(per_view)
            reading_scores[reading] = statistics.fmean(reading_folio[reading].values())
        orbit.append({
            "assignment": {folio: list(assignment[folio]) for folio in FOLIO_PAGES},
            "reading_scores": reading_scores,
            "reading_folio_contributions": reading_folio,
            "robust_score": min(reading_scores.values()),
        })
    observed = {folio: tuple(labels[folio]) for folio in FOLIO_PAGES}
    observed_row = next(row for row in orbit if all(tuple(row["assignment"][folio]) == observed[folio] for folio in FOLIO_PAGES))
    observed_score = float(observed_row["robust_score"])
    rank = 1 + sum(float(row["robust_score"]) > observed_score + TOL for row in orbit)
    tied = sum(abs(float(row["robust_score"]) - observed_score) <= TOL for row in orbit)
    return {
        "eligible": True,
        "views": list(views),
        "phase_count": len(orbit),
        "observed_assignment": {folio: list(observed[folio]) for folio in FOLIO_PAGES},
        "observed_reading_scores": observed_row["reading_scores"],
        "observed_reading_folio_contributions": observed_row["reading_folio_contributions"],
        "observed_robust_score": observed_score,
        "inclusive_rank": rank,
        "tied": tied,
        "exact_one_sided_p": sum(float(row["robust_score"]) >= observed_score - TOL for row in orbit) / len(orbit),
        "standardization_diagnostics": diagnostics,
        "orbit_sha256": object_sha(orbit),
        "orbit_robust_scores": [float(row["robust_score"]) for row in orbit],
    }


def synthetic_matrices(class_by_folio: dict[str, tuple[str, ...]]) -> dict:
    output = {reading: {view: {} for view in VIEWS} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            for folio in FOLIO_PAGES:
                state = dict(zip(FOLIO_PAGES[folio], class_by_folio[folio]))
                output[reading][view][folio] = {
                    pair: .9 if state[pair[0]] == state[pair[1]] else .1
                    for pair in page_pairs(folio)
                }
    return output


def passes(item: dict[str, object]) -> bool:
    return (
        item.get("eligible") is True
        and item.get("inclusive_rank") == item.get("tied") == 1
        and all(value > 0 for value in item.get("observed_reading_scores", {}).values())
        and all(
            value > 0
            for by_folio in item.get("observed_reading_folio_contributions", {}).values()
            for value in by_folio.values()
        )
    )


def run_controls() -> None:
    if CONTROLS.exists() or CONTROL_REPORT.exists():
        raise SystemExit("refusing overwrite")
    distributed_matrix = synthetic_matrices(OBSERVED)
    distributed = evaluate(distributed_matrix, OBSERVED)

    one_folio_states = {"f67": OBSERVED["f67"], "f68": rotate(OBSERVED["f68"], 1)}
    one_folio = evaluate(synthetic_matrices(one_folio_states), OBSERVED)

    disagreement_matrix = synthetic_matrices(OBSERVED)
    disagree_states = {folio: rotate(OBSERVED[folio], 1) for folio in FOLIO_PAGES}
    disagreement_matrix["RF1b"] = synthetic_matrices(disagree_states)["RF1b"]
    disagreement = evaluate(disagreement_matrix, OBSERVED)

    ordinal_matrix = {reading: {view: {} for view in VIEWS} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            for folio, pages in FOLIO_PAGES.items():
                ordinal_matrix[reading][view][folio] = {
                    pair: 1.0 / (1.0 + abs(pages.index(pair[0]) - pages.index(pair[1])))
                    for pair in page_pairs(folio)
                }
    ordinal = evaluate(ordinal_matrix, OBSERVED)

    affine_matrix = {
        reading: {
            view: {
                folio: {pair: value * (1.2 + .1 * view_index) + reading_index for pair, value in distributed_matrix[reading][view][folio].items()}
                for folio in FOLIO_PAGES
            }
            for view_index, view in enumerate(VIEWS)
        }
        for reading_index, reading in enumerate(READINGS)
    }
    affine = evaluate(affine_matrix, OBSERVED)
    complement = {folio: tuple("C" if value == "A" else "A" for value in OBSERVED[folio]) for folio in FOLIO_PAGES}
    complemented = evaluate(distributed_matrix, complement)

    checks = {
        "exact_24_unique_phases": distributed.get("phase_count") == 24,
        "distributed_plant_unique_rank_one": distributed.get("inclusive_rank") == distributed.get("tied") == 1,
        "distributed_plant_both_folios_all_readings": all(value > 0 for row in distributed.get("observed_reading_folio_contributions", {}).values() for value in row.values()),
        "one_folio_plant_rejected": not passes(one_folio),
        "third_reading_disagreement_rejected": not passes(disagreement),
        "ordinal_distance_rejected": not passes(ordinal),
        "positive_affine_invariant": (
            affine.get("inclusive_rank") == distributed.get("inclusive_rank")
            and affine.get("tied") == distributed.get("tied")
            and abs(float(affine.get("exact_one_sided_p", 1)) - float(distributed.get("exact_one_sided_p", 0))) <= TOL
            and max(abs(left - right) for left, right in zip(affine.get("orbit_robust_scores", []), distributed.get("orbit_robust_scores", []))) <= TOL
        ),
        "class_complement_invariant": complemented.get("orbit_robust_scores") == distributed.get("orbit_robust_scores") and complemented.get("observed_robust_score") == distributed.get("observed_robust_score"),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE_CONTROLS",
        "status": status,
        "inputs": {path.name: sha(path) for path in (METHOD, Path(__file__))},
        "checks": checks,
        "summaries": {
            "distributed": distributed,
            "one_folio": one_folio,
            "reading_disagreement": disagreement,
            "ordinal_distance": ordinal,
            "affine": affine,
            "complemented": complemented,
        },
        "target_accessed": False,
        "claim_ceiling": "Synthetic class-phase scorer validation only; no manuscript class, object, word, meaning, or translation.",
    }
    CONTROLS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CONTROL_REPORT.write_text(
        "# Circle editorial-class phase controls\n\n"
        f"Status: **{status}**\n\n"
        "The exact 24-phase scorer recovers a distributed two-folio plant, rejects one-folio, reading-disagreement, and ordinal-distance controls, and preserves positive-affine and class-complement invariance. No manuscript target source was opened.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "checks": checks}, sort_keys=True))


def feature_values(row: dict[str, str]) -> dict[str, list[str]]:
    families = list(row["primary_sta_families"])
    members = row["primary_sta_codes"].split()
    output = {
        f"FAMILY_N{size}": ["".join(families[start:start + size]) for start in range(len(families) - size + 1)]
        for size in range(2, 6)
    }
    output.update({
        f"MEMBER_N{size}": ["-".join(members[start:start + size]) for start in range(len(members) - size + 1)]
        for size in range(1, 4)
    })
    output["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return output


def weighted_jaccard(left: Counter[str], right: Counter[str]) -> float:
    inventory = sorted(set(left) | set(right))
    denominator = sum(max(left[item], right[item]) for item in inventory)
    return sum(min(left[item], right[item]) for item in inventory) / denominator if denominator else 0.0


def run_target() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    if not CONTROLS.exists():
        raise SystemExit("controls absent")
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    expected_control_inputs = {path.name: sha(path) for path in (METHOD, Path(__file__))}
    if controls.get("status") != "PASS" or controls.get("inputs") != expected_control_inputs or controls.get("target_accessed") is not False:
        raise SystemExit("control binding failed")

    public_rows = {row["page"]: row for row in read_tsv(PAGES_SOURCE)}
    if len(public_rows) != 228 or any(row["tentative_identifications_are_role_evidence"] != "0" for row in public_rows.values()):
        raise AssertionError("public source gate changed")
    derived = {}
    for folio, pages in FOLIO_PAGES.items():
        derived[folio] = []
        for page in pages:
            description = public_rows[page]["general_description"].lower()
            astronomical = "this is an astronomical page" in description
            cosmological = "this is a so-called cosmological page" in description
            if astronomical == cosmological:
                raise AssertionError(f"ambiguous public class: {page}")
            derived[folio].append("A" if astronomical else "C")
        derived[folio] = tuple(derived[folio])
    if derived != OBSERVED:
        raise AssertionError("public class vector changed")

    metadata_rows = read_tsv(META)
    metadata = {row["source_group_id"]: row for row in metadata_rows}
    if len(metadata) != len(metadata_rows):
        raise AssertionError("duplicate metadata group ID")
    counters = defaultdict(Counter)
    target_groups = alternatives = 0
    page_group_counts = defaultdict(int)
    target_pages = {page for pages in FOLIO_PAGES.values() for page in pages}
    for row in read_tsv(ALIGN):
        info = metadata.get(row["source_group_id"])
        if info is None:
            raise AssertionError("alignment group missing metadata")
        if info["page"] not in target_pages or info["kind"] != "C":
            continue
        target_groups += 1
        if int(row["alternative_site_count"]):
            alternatives += 1
            continue
        page_group_counts[(info["page"], row["edition"])] += 1
        for view, values in feature_values(row).items():
            counters[(info["page"], row["edition"], view)].update(values)
    expected_count_keys = {(page, reading) for page in target_pages for reading in READINGS}
    if set(page_group_counts) != expected_count_keys or min(page_group_counts.values()) <= 0:
        raise AssertionError("incomplete target page-reading panel")

    matrices = {reading: {view: {} for view in VIEWS} for reading in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            for folio in FOLIO_PAGES:
                matrices[reading][view][folio] = {
                    pair: weighted_jaccard(counters[(pair[0], reading, view)], counters[(pair[1], reading, view)])
                    for pair in page_pairs(folio)
                }
    primary = evaluate(matrices, OBSERVED)
    deletions = {
        view: evaluate(matrices, OBSERVED, tuple(candidate for candidate in VIEWS if candidate != view))
        for view in VIEWS
    }
    gates = {
        "controls_bound_and_pass": True,
        "exact_24_unique_phases": primary.get("phase_count") == 24,
        "unique_rank_one": primary.get("inclusive_rank") == primary.get("tied") == 1,
        "all_readings_positive": all(value > 0 for value in primary.get("observed_reading_scores", {}).values()),
        "both_folios_positive_every_reading": all(value > 0 for row in primary.get("observed_reading_folio_contributions", {}).values() for value in row.values()),
        "every_view_deletion_rank_at_most_2": all(item.get("inclusive_rank", 99) <= 2 for item in deletions.values()),
        "every_view_deletion_readings_positive": all(all(value > 0 for value in item.get("observed_reading_scores", {}).values()) for item in deletions.values()),
        "every_view_deletion_folios_positive": all(all(value > 0 for row in item.get("observed_reading_folio_contributions", {}).values() for value in row.values()) for item in deletions.values()),
        "zero_english_glosses": True,
    }
    confirmed = all(gates.values())
    status = "CONFIRMED_PUBLIC_CIRCLE_EDITORIAL_CLASS_PHASE" if confirmed else "FINAL_NONCONFIRMATION_PUBLIC_CIRCLE_EDITORIAL_CLASS_PHASE"
    decision = "RETAIN_EDITORIAL_CLASS_ALIGNED_CIRCULAR_REGISTER" if confirmed else "CLOSE_FIXED_F67_F68_EDITORIAL_CLASS_PHASE_ROUTE"
    result = {
        "experiment": "CIRCLE_EDITORIAL_CLASS_PHASE",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PAGES_SOURCE, METHOD, Path(__file__), CONTROLS)},
        "source_scope": {
            "folio_pages": {folio: list(pages) for folio, pages in FOLIO_PAGES.items()},
            "public_class_vectors": {folio: list(values) for folio, values in OBSERVED.items()},
            "target_C_groups": target_groups,
            "excluded_alternative_groups": alternatives,
            "page_reading_zero_alternative_group_counts": {f"{page}|{reading}": page_group_counts[(page, reading)] for page, reading in sorted(page_group_counts)},
        },
        "primary": primary,
        "view_deletions": deletions,
        "gates": gates,
        "claim_ceiling": "Alignment of complete circular profiles with the public editorial astronomical/cosmological distinction on f67/f68 only; no authorial category, object, name, word, sound, language, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Circle editorial-class phase\n\n"
        f"Status: **{status}**\n\n"
        f"The public f67/f68 astronomical/cosmological class phase ranks {primary.get('inclusive_rank')} of 24 exact phase-preserving rotations (p={primary.get('exact_one_sided_p'):.6f}). Reading scores are {primary.get('observed_reading_scores')}; folio contributions are {primary.get('observed_reading_folio_contributions')}.\n\n"
        f"Decision: **{decision}**. This is an editorial page-class test, not an object, word, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "rank": primary.get("inclusive_rank"), "p": primary.get("exact_one_sided_p"), "scores": primary.get("observed_reading_scores")}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--controls", action="store_true")
    group.add_argument("--target", action="store_true")
    args = parser.parse_args()
    run_controls() if args.controls else run_target()


if __name__ == "__main__":
    main()
