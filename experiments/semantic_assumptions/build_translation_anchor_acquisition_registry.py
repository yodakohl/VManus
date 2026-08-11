#!/usr/bin/env python3
"""Build the translation-anchor acquisition registry from completed evidence."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
LEDGER = BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv"
CLOSED = BASE / "CLOSED_ROUTE_FAMILIES.tsv"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
LABELS = RESULTS / "existing_human_label_annotations.tsv"
PAGES = RESULTS / "existing_human_page_annotations.tsv"
REPORTS = {
    "COL001": RESULTS / "col001_plain_colour_annotation_capacity_report.md",
    "SCP001": RESULTS / "star_color_target_validation.md",
    "ZODIAC": RESULTS / "public_zodiac_label_attribute_capacity_report.md",
    "F69M001": RESULTS / "f69m001_target_validation.md",
    "F68CL001": RESULTS / "f68r2_sun_ring_cleartext_validation.md",
}
SPEC = BASE / "TRANSLATION_ANCHOR_ACQUISITION_REGISTRY_SPEC.md"
OUT_TSV = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
OUT_JSON = RESULTS / "translation_anchor_acquisition_registry_v1.json"
OUT_REPORT = RESULTS / "translation_anchor_acquisition_registry_v1_report.md"

FROZEN = {
    CLOSED: "3e70a8ebdf8d56073c259014c6ca6ef9dd0be626a918f21a915dd218c2b6ae81",
    EXACT: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    LABELS: "93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6",
    PAGES: "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
    REPORTS["COL001"]: "60af1cdc1bb97af1594a6946ae7cc158b24ffbb16d2bb3eb6d933b98eb9801a7",
    REPORTS["SCP001"]: "dd43223572a30071c8a449b6eddec7494b7b03b654ae56dd2ca1b2b8380b3e1a",
    REPORTS["ZODIAC"]: "4fd14a536bf785ab4d91f5b603f56419e2305104e192823d7cfda1ee6c8c1339",
    REPORTS["F69M001"]: "1eea25baf92d33934c3737b305217e64fa1cf7430c06f062ec275bced2c6f8b1",
    REPORTS["F68CL001"]: "6107dcab8894e42f712bc6f8c671e7b277e5a5e26afeb865c575809e8ab1fd3f",
}

GATES = (
    "provenance_traceable_human_source",
    "author_visible_one_to_one_ownership",
    "readable_contrasting_values",
    "independent_physical_folios_ge_5",
    "unique_current_locus_mapping",
    "untouched_confirmation_available",
)

DECLARATIONS = (
    {
        "candidate_id": "S104_HERBAL_COMPONENT_RELATIONS",
        "ledger_experiment": "S104_component_relation_source_inventory",
        "expected_status": "PASS_SOURCE_FROZEN_16_PAGE_7_FAMILY_PANEL",
        "scope": "16 Herbal pages; seven human component-relation families; 11 exact-new edges",
        "gates": (1, 0, 1, 1, 1, 0),
        "decisive_blocker": "No author-visible component-to-text ownership; endpoints and relation family were already exposed.",
        "requested_observation": "A page-disjoint human diplomatic source giving singular author-visible component captions with explicit negative or contrasting values on at least five new folios.",
        "evidence_path": "ACTIVE_EXPERIMENT_LEDGER.tsv:S104_component_relation_source_inventory",
    },
    {
        "candidate_id": "SCP001_STAR_COLOUR_ROWS",
        "ledger_experiment": "SCP001_target_validation",
        "expected_status": "PASS_18_CHECK_INDEPENDENT_FINAL_RECONSTRUCTION",
        "scope": "120 red/yellow star-marker rows on nine pages and seven physical folios",
        "gates": (1, 0, 1, 1, 1, 0),
        "decisive_blocker": "Marker colour is an author-visible coordinate, not one-to-one evidence that the attached text spells the colour; the frozen target is consumed and nonconfirming.",
        "requested_observation": "A new folio-held panel whose author-visible captions explicitly name independently readable marker values rather than merely carrying coloured markers.",
        "evidence_path": "results/star_color_target_validation.md",
    },
    {
        "candidate_id": "PUBLIC_ZODIAC_FIGURE_ATTRIBUTES",
        "ledger_experiment": "public_zodiac_label_attribute_capacity",
        "expected_status": "STOP_UNSCORED_NO_TRANSFERABLE_EXPLICIT_BINARY_ATTRIBUTE",
        "scope": "300 public zodiac label records; strongest barrel contrast confined to f70-f72 with all negatives on f72",
        "gates": (1, 0, 1, 0, 1, 1),
        "decisive_blocker": "Ownership is inferred from spacing/order and every usable opposing state is one-folio or one-example.",
        "requested_observation": "Explicit label-to-figure connectors or diplomatic owner mappings with both attribute states represented on at least five physical folios.",
        "evidence_path": "results/public_zodiac_label_attribute_capacity_report.md",
    },
    {
        "candidate_id": "COL001_F2R15_UNDERPAINT_NOTE",
        "ledger_experiment": "COL001_plain_colour_annotation_capacity",
        "expected_status": "PROVISIONAL_RECORD_FUNCTION_STOP_LEXICAL_UNSCORED",
        "scope": "one Voynich-script record f2r.15 under green paint; twelve other colour notes use plain alphabet",
        "gates": (1, 1, 0, 0, 1, 0),
        "decisive_blocker": "Only one Voynich-script under-paint note exists, so there is no readable contrasting value or held replication.",
        "requested_observation": "A second provenance-clean Voynich-script note under paint with an independently readable different colour, or the same complete phrase under another green-painted part on a new folio.",
        "evidence_path": "results/col001_plain_colour_annotation_capacity_report.md",
    },
    {
        "candidate_id": "F1R_LATER_ALPHABET_TABLE",
        "ledger_experiment": "f57v_namenmantik_f1r_17_slot_claim_audit",
        "expected_status": "STOP_FALSE_INTERPOLATED_SEVENTEEN_SLOT_BRIDGE",
        "scope": "three later-hand 26-row columns: Latin a-z, Voynich-like glyphs, shifted Latin",
        "gates": (1, 0, 1, 0, 1, 0),
        "decisive_blocker": "The table is probably Marci-era later-reader marginalia and its glyph order does not match f57v or establish the main script's values.",
        "requested_observation": "A qualified complete row-by-row diplomatic reading plus independent evidence that the middle column encodes the main manuscript script rather than a later reader's exercise.",
        "evidence_path": "ACTIVE_EXPERIMENT_LEDGER.tsv:f57v_namenmantik_f1r_17_slot_claim_audit",
    },
    {
        "candidate_id": "F17R_F116V_MARGINALIA",
        "ledger_experiment": "post_IL017_permitted_anchor_route_audit",
        "expected_status": "STOP_NO_UNUSED_AUTHORIAL_BRIDGE",
        "scope": "partly readable plain-script marginalia adjacent to Voynich-script material",
        "gates": (1, 0, 1, 0, 1, 0),
        "decisive_blocker": "No explicit equivalence relation links any readable marginal word to a Voynich string, and the readings remain disputed.",
        "requested_observation": "Independently convergent paleographic readings plus an explicit authorial equivalence, correction, pointer, or repeated bilingual pairing.",
        "evidence_path": "ACTIVE_EXPERIMENT_LEDGER.tsv:post_IL017_permitted_anchor_route_audit",
    },
    {
        "candidate_id": "F57V_HUMORAL_PHASE_LABELS",
        "ledger_experiment": "f57v_walters_w73_humoral_phase_replication_audit",
        "expected_status": "PROVISIONAL_HARLEY_PHASE_INDEPENDENTLY_REPLICATED_BY_WALTERS_W73",
        "scope": "one f57v four-person wheel; four figure-near labels and four radial titles; replicated historical Hot-Moist-Cold-Dry page phase",
        "gates": (1, 0, 1, 0, 1, 0),
        "decisive_blocker": "The historical phase fixes a diagram-role analogy, but the labels are spatially near figures without an author-drawn one-to-one value relation; all local binary patterns are geometry-confounded and exposed.",
        "requested_observation": "A complete readable homologue with the same four-person and two-label-register topology, preserved start/orientation, and explicit slot ownership, or an independent Voynich folio repeating the same owned four-role mapping.",
        "evidence_path": "ACTIVE_EXPERIMENT_LEDGER.tsv:f57v_walters_w73_humoral_phase_replication_audit",
    },
    {
        "candidate_id": "F68R2_SUN_RING_CLEARTEXT",
        "ledger_experiment": "F68CL001_public_sun_ring_cleartext_validation",
        "expected_status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "scope": "one text sequence inside the f68r2 Sun ring",
        "gates": (1, 1, 0, 0, 1, 1),
        "decisive_blocker": "Human sources cannot determine whether the ending is plain cleartext or ordinary Voynich script; ZL/RF and IT disagree materially.",
        "requested_observation": "A qualified full paleographic reading of the complete ring string, with script identity and uncertainty documented independently of a proposed Sun gloss.",
        "evidence_path": "results/f68r2_sun_ring_cleartext_validation.md",
    },
    {
        "candidate_id": "F69V_ORDERED_28_COORDINATE",
        "ledger_experiment": "F69M001_target_validation",
        "expected_status": "FINAL_NONCONFIRMATION_FIXED_LATIN_MANSION_PREFIX_TOPOLOGY",
        "scope": "28 inward radial labels with a fixed public cyclic coordinate on one physical folio",
        "gates": (1, 1, 0, 0, 1, 0),
        "decisive_blocker": "The coordinate is explicit but carries no readable authorial values; the fixed Agrippa mansion roster failed deeper topology and uniqueness gates.",
        "requested_observation": "A second independently fixed roster or a readable authorial slot legend that determines start, direction, and all 28 values without selecting a spelling roster post hoc.",
        "evidence_path": "results/f69m001_target_validation.md",
    },
    {
        "candidate_id": "F67R_F68R_LABELLED_HOMOLOGUE",
        "ledger_experiment": "f67r_f68r_historical_homologue_search",
        "expected_status": "STOP_NO_EXACT_LABELLED_SLOT_HOMOLOGUE_FOUND",
        "scope": "f67r1, f67r2, f68r1, f68r2, and f68r3 special-circle panels",
        "gates": (0, 0, 0, 0, 1, 1),
        "decisive_blocker": "No thirteenth-to-fifteenth-century readable witness matches any full panel slot-for-slot; known analogues are topology-mismatched.",
        "requested_observation": "A newly catalogued complete readable homologue fixing text ownership, register cardinalities, start, direction, and slot correspondence for one full panel.",
        "evidence_path": "ACTIVE_EXPERIMENT_LEDGER.tsv:f67r_f68r_historical_homologue_search",
    },
    {
        "candidate_id": "STOLFI_EXACT_LOCAL_RELATIONS",
        "ledger_experiment": "direct_comment_repeat_coverage",
        "expected_status": "PASS_SCORE_BLIND_FOUR_OUTCOMES_AUTHORIZED",
        "scope": "1,192 exact/comment-indexed loci; 109 unhedged stronger attachment/enclosure/contact/wrap/grouping rows",
        "gates": (1, 0, 0, 1, 1, 0),
        "decisive_blocker": "These are modern human descriptions and proximity relations, not author-visible readable text-to-value assignments; repeated-role tests are already consumed.",
        "requested_observation": "Author-visible connectors or captions that replace modern inferred proximity with singular ownership and readable varying values on new folios.",
        "evidence_path": "results/existing_human_exact_locus_annotations.tsv",
    },
)

FIELDS = (
    "rank", "candidate_id", "ledger_experiment", "ledger_status", "scope",
    *GATES, "gate_count", "admissible", "decisive_blocker",
    "requested_observation", "evidence_path",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def ledger_index() -> dict[str, dict[str, str]]:
    rows = strict_rows(LEDGER)
    selected = {str(item["ledger_experiment"]) for item in DECLARATIONS}
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["experiment"], []).append(row)
    for experiment in selected:
        if len(grouped.get(experiment, [])) != 1:
            raise ValueError(f"selected ledger experiment is not unique: {experiment}")
    return {experiment: grouped[experiment][0] for experiment in selected}


def annotation_controls() -> dict[str, object]:
    exact = strict_rows(EXACT)
    labels = strict_rows(LABELS)
    pages = strict_rows(PAGES)
    f57_exact = [row for row in exact if row["page"] == "f57v"]
    f57_labels = [row for row in labels if row["page"] == "f57v"]
    f57_page = [row for row in pages if row["page"] == "f57v"]
    figure_loci = {"f57v.6", "f57v.7", "f57v.8", "f57v.9"}
    exact_figure = [row for row in f57_exact if row["locus"] in figure_loci]
    if {row["locus"] for row in exact_figure} != figure_loci:
        raise ValueError("f57v figure-near exact-locus mapping drift")
    comments = " ".join(row["local_comment"] for row in exact_figure)
    for clock in ("01:30", "04:30", "07:30", "10:00"):
        if clock not in comments:
            raise ValueError(f"missing f57v clock position: {clock}")
    if len(f57_page) != 1 or "four 'persons'" not in f57_page[0]["illustrations"]:
        raise ValueError("f57v page description drift")
    f57_human_labels = [row for row in f57_labels if row["location"].startswith("f57v.x.")]
    if len(f57_human_labels) != 4:
        raise ValueError("f57v figure label inventory drift")
    context_counts: dict[str, int] = {}
    for row in exact:
        context_counts[row["context_class"]] = context_counts.get(row["context_class"], 0) + 1
    stronger = [row for row in exact if row["certainty"] == "UNHEDGED" and any(
        tag in row["local_relation_tags"].split(";")
        for tag in ("REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT", "REL_ARRAY_OR_GROUP")
    )]
    return {
        "exact_annotation_rows": len(exact),
        "label_annotation_rows": len(labels),
        "page_annotation_rows": len(pages),
        "f57_exact_annotation_rows": len(f57_exact),
        "f57_label_catalogue_rows": len(f57_labels),
        "f57_figure_near_exact_loci": sorted(figure_loci),
        "f57_figure_label_records": len(f57_human_labels),
        "unhedged_stronger_relation_rows": len(stronger),
        "context_counts": dict(sorted(context_counts.items())),
    }


def report(result: dict[str, object], rows: list[dict[str, object]]) -> str:
    top = [row for row in rows if int(row["gate_count"]) == result["counts"]["maximum_gate_count"]]
    top_text = ", ".join(f"`{row['candidate_id']}`" for row in top)
    return f"""# Translation-anchor acquisition registry v1

Decision: **{result['decision']}**.

No current human-evidence family passes all six translation-anchor gates.
The registry contains **{result['counts']['candidate_families']}** nearest
families; the maximum is **{result['counts']['maximum_gate_count']}/6** gates,
reached by {top_text}.  Gate count is a routing aid, not confidence.

The two leading high-coverage panels still fail for different reasons.  The
S104 Herbal component relations have multiple pages and readable human
categories but no author-visible component-to-text ownership and no untouched
lexical holdout.  SCP001 has seven folios and readable red/yellow marker
states, but marker colour is not proof that attached text spells the colour,
and its frozen structural target is already consumed and nonconfirming.

The strongest unscored record-level clue remains `f2r.15`: it may be a
pre-paint instruction associated with a green leaf, but it is the only
Voynich-script colour note.  The strongest special-circle semantic clue
remains f57v's replicated Hot–Moist–Cold–Dry diagram-role phase.  Its four
figure-near labels are current-locus mapped at 01:30, 04:30, 07:30, and 10:00,
but proximity is not an author-drawn one-to-one value assignment and all
available local patterns are exposed and geometry-confounded.  Therefore the
registry does **not** gloss those labels or `f2r.15`.

The TSV gives one concrete new observation that would reopen each family.
Until one of those observations exists, another model, threshold, GPU search,
spelling roster, or decoder claim cannot resolve the missing semantic
permutation.

This registry supplies no word, part of speech, morpheme, sound, language,
cipher operation, plaintext, meaning, or translation.
"""


def main() -> None:
    outputs = (OUT_TSV, OUT_JSON, OUT_REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite acquisition-registry artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen evidence mismatch: {path.name}")
    closed_text = CLOSED.read_text(encoding="utf-8")
    for route in ("LEXICAL_GLOSSES_FROM_FORMAL_ROLES", "SELF_CORRECTIONS_AND_BILINGUAL_KEYS", "ZODIAC_AND_ASTRONOMICAL_DICTIONARIES"):
        if route not in closed_text:
            raise ValueError(f"missing closed-route family: {route}")
    for key, path in REPORTS.items():
        if not path.read_text(encoding="utf-8").strip():
            raise ValueError(f"empty report: {key}")

    ledger = ledger_index()
    rows: list[dict[str, object]] = []
    for declaration in DECLARATIONS:
        entry = ledger.get(str(declaration["ledger_experiment"]))
        if entry is None:
            raise ValueError(f"missing ledger experiment: {declaration['ledger_experiment']}")
        if entry["status"] != declaration["expected_status"]:
            raise ValueError(f"ledger status drift: {declaration['ledger_experiment']}")
        gates = tuple(int(value) for value in declaration["gates"])
        if len(gates) != len(GATES) or any(value not in (0, 1) for value in gates):
            raise ValueError("invalid gate declaration")
        gate_count = sum(gates)
        row: dict[str, object] = {
            "candidate_id": declaration["candidate_id"],
            "ledger_experiment": declaration["ledger_experiment"],
            "ledger_status": entry["status"],
            "scope": declaration["scope"],
            "gate_count": gate_count,
            "admissible": int(gate_count == len(GATES)),
            "decisive_blocker": declaration["decisive_blocker"],
            "requested_observation": declaration["requested_observation"],
            "evidence_path": declaration["evidence_path"],
        }
        row.update(dict(zip(GATES, gates)))
        rows.append(row)
    rows.sort(key=lambda row: (-int(row["gate_count"]), str(row["candidate_id"]).encode("utf-8")))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    if any(int(row["admissible"]) for row in rows):
        raise SystemExit("admissible anchor found: preregistration required before any score")

    controls = annotation_controls()
    counts = {
        "candidate_families": len(rows),
        "admissible_families": 0,
        "maximum_gate_count": max(int(row["gate_count"]) for row in rows),
        "special_circle_families": sum(str(row["candidate_id"]).startswith(("F57", "F67", "F68", "F69")) for row in rows),
        "selected_ledger_rows": len(ledger),
    }
    result = {
        "experiment": "TRANSLATION_ANCHOR_ACQUISITION_REGISTRY_V1",
        "status": "PASS_ACQUISITION_GAP_REGISTRY",
        "decision": "NO_ADMISSIBLE_UNUSED_TRANSLATION_ANCHOR_ACQUISITION_MAP_READY",
        "spec_sha256": sha(SPEC),
        "builder_sha256": sha(Path(__file__)),
        "input_sha256": {str(path.relative_to(BASE)): sha(path) for path in sorted(FROZEN, key=lambda item: str(item))},
        "ledger_row_bindings": {str(row["ledger_experiment"]): str(row["ledger_status"]) for row in rows},
        "annotation_controls": controls,
        "counts": counts,
        "gate_names": list(GATES),
        "candidates": rows,
        "claim_ceiling": "Acquisition routing only; no Voynich word, POS, morpheme, sound, language, cipher, plaintext, meaning, or translation.",
    }

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(report(result, rows), encoding="utf-8")


if __name__ == "__main__":
    main()
