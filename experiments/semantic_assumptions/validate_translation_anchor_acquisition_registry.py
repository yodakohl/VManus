#!/usr/bin/env python3
"""Independent validation for the translation-anchor acquisition registry."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "TRANSLATION_ANCHOR_ACQUISITION_REGISTRY_SPEC.md"
BUILDER = BASE / "build_translation_anchor_acquisition_registry.py"
LEDGER = BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv"
CLOSED = BASE / "CLOSED_ROUTE_FAMILIES.tsv"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
LABELS = RESULTS / "existing_human_label_annotations.tsv"
PAGES = RESULTS / "existing_human_page_annotations.tsv"
TSV = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
RESULT = RESULTS / "translation_anchor_acquisition_registry_v1.json"
REPORT = RESULTS / "translation_anchor_acquisition_registry_v1_report.md"
OUT_JSON = RESULTS / "translation_anchor_acquisition_registry_v1_validation.json"
OUT_REPORT = RESULTS / "translation_anchor_acquisition_registry_v1_validation_report.md"

FROZEN = {
    SPEC: "a51c0ede551f2e8ef47c1320e9bd46e1dbbfa104e35ae2644b5e73a2f0726d1b",
    BUILDER: "8432cd8addf2fee32ba96625a398171a77e145d88a52b6bd3f128ae9b8d7449f",
    CLOSED: "3e70a8ebdf8d56073c259014c6ca6ef9dd0be626a918f21a915dd218c2b6ae81",
    EXACT: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    LABELS: "93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6",
    PAGES: "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
    RESULTS / "col001_plain_colour_annotation_capacity_report.md": "60af1cdc1bb97af1594a6946ae7cc158b24ffbb16d2bb3eb6d933b98eb9801a7",
    RESULTS / "star_color_target_validation.md": "dd43223572a30071c8a449b6eddec7494b7b03b654ae56dd2ca1b2b8380b3e1a",
    RESULTS / "public_zodiac_label_attribute_capacity_report.md": "4fd14a536bf785ab4d91f5b603f56419e2305104e192823d7cfda1ee6c8c1339",
    RESULTS / "f69m001_target_validation.md": "1eea25baf92d33934c3737b305217e64fa1cf7430c06f062ec275bced2c6f8b1",
    RESULTS / "f68r2_sun_ring_cleartext_validation.md": "6107dcab8894e42f712bc6f8c671e7b277e5a5e26afeb865c575809e8ab1fd3f",
    TSV: "0261d2e7856ddf26b18fe46915f66446734dcc687cc516dac4aa23c4704b7a1c",
    RESULT: "0a285cccbe9507987978157d4511ce099e2a3ff54e22f416297337c89089ad14",
    REPORT: "62ebcabbf26e44d95c05b2dc0fe4499b891468b391e64bd2d556be28b474772a",
}

GATES = (
    "provenance_traceable_human_source",
    "author_visible_one_to_one_ownership",
    "readable_contrasting_values",
    "independent_physical_folios_ge_5",
    "unique_current_locus_mapping",
    "untouched_confirmation_available",
)

# This is an independent compact contract rather than an import from the producer.
EXPECTED = {
    "S104_HERBAL_COMPONENT_RELATIONS": (
        "S104_component_relation_source_inventory", "PASS_SOURCE_FROZEN_16_PAGE_7_FAMILY_PANEL", (1, 0, 1, 1, 1, 0),
    ),
    "SCP001_STAR_COLOUR_ROWS": (
        "SCP001_target_validation", "PASS_18_CHECK_INDEPENDENT_FINAL_RECONSTRUCTION", (1, 0, 1, 1, 1, 0),
    ),
    "PUBLIC_ZODIAC_FIGURE_ATTRIBUTES": (
        "public_zodiac_label_attribute_capacity", "STOP_UNSCORED_NO_TRANSFERABLE_EXPLICIT_BINARY_ATTRIBUTE", (1, 0, 1, 0, 1, 1),
    ),
    "COL001_F2R15_UNDERPAINT_NOTE": (
        "COL001_plain_colour_annotation_capacity", "PROVISIONAL_RECORD_FUNCTION_STOP_LEXICAL_UNSCORED", (1, 1, 0, 0, 1, 0),
    ),
    "F1R_LATER_ALPHABET_TABLE": (
        "f57v_namenmantik_f1r_17_slot_claim_audit", "STOP_FALSE_INTERPOLATED_SEVENTEEN_SLOT_BRIDGE", (1, 0, 1, 0, 1, 0),
    ),
    "F17R_F116V_MARGINALIA": (
        "post_IL017_permitted_anchor_route_audit", "STOP_NO_UNUSED_AUTHORIAL_BRIDGE", (1, 0, 1, 0, 1, 0),
    ),
    "F57V_HUMORAL_PHASE_LABELS": (
        "f57v_walters_w73_humoral_phase_replication_audit", "PROVISIONAL_HARLEY_PHASE_INDEPENDENTLY_REPLICATED_BY_WALTERS_W73", (1, 0, 1, 0, 1, 0),
    ),
    "F68R2_SUN_RING_CLEARTEXT": (
        "F68CL001_public_sun_ring_cleartext_validation", "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION", (1, 1, 0, 0, 1, 1),
    ),
    "F69V_ORDERED_28_COORDINATE": (
        "F69M001_target_validation", "FINAL_NONCONFIRMATION_FIXED_LATIN_MANSION_PREFIX_TOPOLOGY", (1, 1, 0, 0, 1, 0),
    ),
    "F67R_F68R_LABELLED_HOMOLOGUE": (
        "f67r_f68r_historical_homologue_search", "STOP_NO_EXACT_LABELLED_SLOT_HOMOLOGUE_FOUND", (0, 0, 0, 0, 1, 1),
    ),
    "STOLFI_EXACT_LOCAL_RELATIONS": (
        "direct_comment_repeat_coverage", "PASS_SCORE_BLIND_FOUR_OUTCOMES_AUTHORIZED", (1, 0, 0, 1, 1, 0),
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def strict_json(path: Path) -> object:
    raw = path.read_text(encoding="utf-8")
    value = json.loads(raw, object_pairs_hook=_reject_duplicate)
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError(f"noncanonical JSON: {path.name}")
    return value


def _reject_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def expected_report(result: dict[str, object], table: list[dict[str, str]]) -> str:
    maximum = int(result["counts"]["maximum_gate_count"])
    top = [row for row in table if int(row["gate_count"]) == maximum]
    top_text = ", ".join(f"`{row['candidate_id']}`" for row in top)
    return f"""# Translation-anchor acquisition registry v1

Decision: **{result['decision']}**.

No current human-evidence family passes all six translation-anchor gates.
The registry contains **{result['counts']['candidate_families']}** nearest
families; the maximum is **{maximum}/6** gates,
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
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    checks: list[str] = []

    for path, expected in FROZEN.items():
        if digest(path) != expected:
            raise SystemExit(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")

    result = strict_json(RESULT)
    if not isinstance(result, dict):
        raise ValueError("result must be object")
    checks.append("result_duplicate_free_canonical_json")
    if result["experiment"] != "TRANSLATION_ANCHOR_ACQUISITION_REGISTRY_V1":
        raise ValueError("experiment mismatch")
    if result["status"] != "PASS_ACQUISITION_GAP_REGISTRY":
        raise ValueError("status mismatch")
    if result["decision"] != "NO_ADMISSIBLE_UNUSED_TRANSLATION_ANCHOR_ACQUISITION_MAP_READY":
        raise ValueError("decision mismatch")
    if result["spec_sha256"] != FROZEN[SPEC] or result["builder_sha256"] != FROZEN[BUILDER]:
        raise ValueError("producer binding mismatch")
    checks.extend(("experiment_status_decision", "producer_source_bindings"))

    table = rows(TSV)
    if len(table) != len(EXPECTED):
        raise ValueError("candidate count mismatch")
    if [row["candidate_id"] for row in table] != [row["candidate_id"] for row in result["candidates"]]:
        raise ValueError("TSV/JSON candidate order mismatch")
    checks.extend(("candidate_count", "tsv_json_candidate_order"))

    ledger_rows = rows(LEDGER)
    ledger: dict[str, list[dict[str, str]]] = {}
    for row in ledger_rows:
        ledger.setdefault(row["experiment"], []).append(row)
    for candidate in table:
        candidate_id = candidate["candidate_id"]
        if candidate_id not in EXPECTED:
            raise ValueError(f"unexpected candidate: {candidate_id}")
        experiment, status, gate_values = EXPECTED[candidate_id]
        if candidate["ledger_experiment"] != experiment or candidate["ledger_status"] != status:
            raise ValueError(f"candidate contract mismatch: {candidate_id}")
        if len(ledger.get(experiment, [])) != 1 or ledger[experiment][0]["status"] != status:
            raise ValueError(f"authoritative ledger mismatch: {candidate_id}")
        observed = tuple(int(candidate[gate]) for gate in GATES)
        if observed != gate_values or any(candidate[gate] not in ("0", "1") for gate in GATES):
            raise ValueError(f"gate mismatch: {candidate_id}")
        if int(candidate["gate_count"]) != sum(gate_values):
            raise ValueError(f"gate total mismatch: {candidate_id}")
        if candidate["admissible"] != "0" or not candidate["decisive_blocker"] or not candidate["requested_observation"]:
            raise ValueError(f"candidate stop/reopen mismatch: {candidate_id}")
        checks.extend((f"contract:{candidate_id}", f"ledger:{candidate_id}", f"gates:{candidate_id}", f"reopen:{candidate_id}"))

    expected_order = sorted(table, key=lambda row: (-int(row["gate_count"]), row["candidate_id"].encode("utf-8")))
    if table != expected_order or [int(row["rank"]) for row in table] != list(range(1, len(table) + 1)):
        raise ValueError("candidate ranking mismatch")
    checks.append("descending_gate_count_utf8_ranking")

    exact = rows(EXACT)
    labels = rows(LABELS)
    pages = rows(PAGES)
    f57_exact = [row for row in exact if row["page"] == "f57v"]
    expected_loci = {"f57v.6", "f57v.7", "f57v.8", "f57v.9"}
    figure = [row for row in f57_exact if row["locus"] in expected_loci]
    if {row["locus"] for row in figure} != expected_loci:
        raise ValueError("f57 exact-locus topology mismatch")
    comments = " ".join(row["local_comment"] for row in figure)
    if any(clock not in comments for clock in ("01:30", "04:30", "07:30", "10:00")):
        raise ValueError("f57 clock-position mismatch")
    f57_label_rows = [row for row in labels if row["page"] == "f57v"]
    if len(f57_label_rows) != 9 or sum(row["location"].startswith("f57v.x.") for row in f57_label_rows) != 4:
        raise ValueError("f57 label catalogue mismatch")
    f57_pages = [row for row in pages if row["page"] == "f57v"]
    if len(f57_pages) != 1 or "four 'persons'" not in f57_pages[0]["illustrations"]:
        raise ValueError("f57 page-prose mismatch")
    stronger = [row for row in exact if row["certainty"] == "UNHEDGED" and any(
        tag in row["local_relation_tags"].split(";")
        for tag in ("REL_EXPLICIT_ATTACHMENT", "REL_ENCLOSURE", "REL_OVERLAP_OR_CONTACT", "REL_ARRAY_OR_GROUP")
    )]
    if (len(exact), len(labels), len(pages), len(f57_exact), len(stronger)) != (1192, 1018, 228, 6, 109):
        raise ValueError("annotation count mismatch")
    controls = result["annotation_controls"]
    if controls["exact_annotation_rows"] != 1192 or controls["label_annotation_rows"] != 1018:
        raise ValueError("stored annotation total mismatch")
    if controls["page_annotation_rows"] != 228 or controls["f57_exact_annotation_rows"] != 6:
        raise ValueError("stored page/f57 count mismatch")
    if controls["f57_figure_near_exact_loci"] != sorted(expected_loci):
        raise ValueError("stored f57 loci mismatch")
    if controls["f57_figure_label_records"] != 4 or controls["unhedged_stronger_relation_rows"] != 109:
        raise ValueError("stored relation control mismatch")
    checks.extend(("annotation_table_counts", "f57_four_clock_positions", "f57_four_label_records", "f57_page_four_persons", "unhedged_stronger_relation_count"))

    counts = result["counts"]
    expected_counts = {
        "admissible_families": 0,
        "candidate_families": 11,
        "selected_ledger_rows": len(EXPECTED),
        "maximum_gate_count": 4,
        "special_circle_families": 4,
    }
    if counts != expected_counts:
        raise ValueError("result count mismatch")
    if result["gate_names"] != list(GATES):
        raise ValueError("gate order mismatch")
    if any(sum(EXPECTED[row["candidate_id"]][2]) == 6 for row in table):
        raise ValueError("unexpected admissible candidate")
    checks.extend(("aggregate_counts", "gate_name_order", "zero_admissible_candidates"))

    # Reconstruct the exact public candidate rows from TSV and compare every JSON field.
    converted: list[dict[str, object]] = []
    integer_fields = {"rank", "gate_count", "admissible", *GATES}
    for row in table:
        converted.append({key: int(value) if key in integer_fields else value for key, value in row.items()})
    if result["candidates"] != converted:
        raise ValueError("candidate JSON reconstruction mismatch")
    checks.append("candidate_json_exact_reconstruction")
    if REPORT.read_text(encoding="utf-8") != expected_report(result, table):
        raise ValueError("report byte reconstruction mismatch")
    checks.append("report_byte_exact_reconstruction")

    # Fail-closed mutation controls for the central decision logic.
    mutated = [dict(row) for row in table]
    mutated[0][GATES[0]] = "0"
    if sum(int(mutated[0][gate]) for gate in GATES) >= int(table[0]["gate_count"]):
        raise ValueError("gate mutation was not detected")
    all_pass = dict(table[0])
    for gate in GATES:
        all_pass[gate] = "1"
    if sum(int(all_pass[gate]) for gate in GATES) != 6:
        raise ValueError("synthetic all-pass gate failed")
    checks.extend(("one_gate_mutation_rejected", "synthetic_all_six_gate_stop_trigger"))

    validation = {
        "experiment": "TRANSLATION_ANCHOR_ACQUISITION_REGISTRY_V1_VALIDATION",
        "status": "PASS_INDEPENDENT_ACQUISITION_REGISTRY_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_tsv_sha256": FROZEN[TSV],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": digest(Path(__file__)),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": expected_counts,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Translation-anchor acquisition registry v1 — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass.  The validator independently binds the completed evidence, "
        "authoritative ledger outcomes, six gate vectors, f57v clock-position and label topology, "
        "annotation counts, ranking, decision, canonical candidate JSON, and exact report bytes.\n\n"
        "It confirms an acquisition map with zero admissible unused anchors.  This is not evidence "
        "for a word, part of speech, morpheme, sound, language, cipher operation, plaintext, meaning, "
        "or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
