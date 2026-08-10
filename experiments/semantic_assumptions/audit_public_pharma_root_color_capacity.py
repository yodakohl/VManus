#!/usr/bin/env python3
"""Audit public pharmaceutical-label root-colour capacity without scoring text.

The 1998 Stolfi/Grove label catalogue is public human metadata, not a
user-supplied image interpretation.  This audit asks a narrower question:
after conservative colour parsing and current-locus mapping, do explicit
dark/light root states have independently documented one-to-one label
ownership on more than one physical folio?

Voynich strings are co-located in one mapping table but are never selected,
copied, transformed, or scored.  OCR and automated image analysis are absent.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ANNOTATIONS = RESULTS / "existing_human_label_annotations.tsv"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
ATLAS_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
OUT_TSV = RESULTS / "public_pharma_root_color_candidates.tsv"
OUT_JSON = RESULTS / "public_pharma_root_color_capacity.json"
REPORT = RESULTS / "public_pharma_root_color_capacity_report.md"

PUBLIC_URL = (
    "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
    "work/Notes/614/labtit-best.idx"
)
PUBLIC_SHA256 = "9267a2bbf2d485320ce8baaa2e3eeaccb6be7a02aa81ee9422a39ba00bef420a"

EXPECTED_INPUTS = {
    "results/existing_human_label_annotations.tsv":
        "93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6",
    "results/existing_human_current_locus_crosswalk.tsv":
        "4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc",
    "results/existing_human_exact_locus_annotations.tsv":
        "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
}

PARTIAL_COLOUR = re.compile(
    r"\b(?:alternating|twotone|two[ -]?tone|strip(?:e|ed|es)|"
    r"speckl\w*|mostly|cent(?:er|re)|spots?|edges?|shad\w*|between|btwn)\b",
    re.I,
)

FIELDS = (
    "source_record_id", "source_page", "physical_folio", "source_location",
    "source_object_guess", "source_comment", "root_state", "state_rule",
    "primary_current_mapping", "mapped_locus", "manual_pairing_class",
    "local_relation_tags", "detailed_root_state", "state_comparison",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def physical_folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    assert match
    return match.group(0)


def root_state(comment: str, object_guess: str, certainty: str) -> tuple[str, str] | None:
    """Return only conservative, unhedged, non-mixed root colour states."""
    text = comment.strip().lower()
    obj = object_guess.lower()
    if (
        certainty != "UNHEDGED"
        or "?" in obj
        or "not labeled" in text
        or "faded" in text
        or "alternating" in text
    ):
        return None

    if obj == "root":
        states = re.findall(r"\b(dark|light)\b", text)
        if len(states) == 1 and not PARTIAL_COLOUR.search(text):
            return states[0].upper(), "DIRECT_ROOT_OBJECT"
        return None

    if obj != "plant":
        return None
    found: list[str] = []
    for clause in re.split(r"[,;]|\s+-\s+", text):
        if not re.search(r"\broots?\b", clause):
            continue
        states = set(re.findall(r"\b(dark|light)\b", clause))
        if len(states) == 1 and "?" not in clause and not PARTIAL_COLOUR.search(clause):
            found.append(next(iter(states)))
        elif states:
            return None
    if len(found) == 1:
        return found[0].upper(), "EXPLICIT_ROOT_CLAUSE"
    return None


def mapped_exact_locus(annotation: dict[str, str], crosswalk: dict[str, str]) -> str:
    """Restore the legacy f101 panel name used by the exact-comment table."""
    locus = crosswalk["current_locus"]
    if annotation["page"] in {"f101v1", "f101v2"} and locus.startswith("f101v."):
        return annotation["page"] + locus[len("f101v"):]
    return locus


def pairing_class(unit_text: str) -> str:
    text = unit_text.lower()
    if re.search(r"pairing is (?:quite )?clear|pairing seems clear|each plant is labeled", text):
        return "PUBLIC_CLEAR_PAIRING"
    if re.search(
        r"not clear how|we assum|we presum|likely to be associated|"
        r"seems safer to assign|perhaps associated|apparently placed|generally seems",
        text,
    ):
        return "PUBLIC_ASSUMED_OR_AMBIGUOUS"
    if re.search(
        r"there (?:are|appears to be) (?:\w+|\d+) (?:plants|labels).*"
        r"(?:\w+|\d+) (?:plants|labels)",
        text,
    ):
        return "PUBLIC_COUNT_ONLY"
    return "NO_PUBLIC_PAIRING_STATEMENT"


def canonical_write(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")

    actual_inputs = {
        str(path.relative_to(BASE)): sha(path)
        for path in (ANNOTATIONS, CROSSWALK, EXACT)
    }
    assert actual_inputs == EXPECTED_INPUTS
    validation = json.loads(ATLAS_VALIDATION.read_text(encoding="utf-8"))
    assert validation["status"] == "PASS_EXISTING_HUMAN_ANNOTATION_ATLAS_VALIDATION"
    assert validation["source_hashes"][
        "experiments/semantic_assumptions/cache/existing_human_annotations/labtit-best.idx"
    ] == PUBLIC_SHA256

    annotations = read_tsv(ANNOTATIONS)
    crosswalk = {row["source_record_id"]: row for row in read_tsv(CROSSWALK)}
    exact_rows = read_tsv(EXACT)
    exact_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    exact_by_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in exact_rows:
        exact_by_locus[row["locus"]].append(row)
        exact_by_unit[(row["page"], row["unit"])].append(row)

    candidates: list[dict[str, str]] = []
    for annotation in annotations:
        parsed = root_state(
            annotation["comments"], annotation["object_guess"], annotation["certainty"]
        )
        if annotation["section"] != "pharma" or annotation["object_class"] != "P" or not parsed:
            continue
        state, rule = parsed
        mapping = crosswalk[annotation["source_record_id"]]
        locus = mapped_exact_locus(annotation, mapping)
        local_rows = exact_by_locus.get(locus, [])
        if local_rows:
            unit = local_rows[0]["unit"]
            unit_text = " ".join(
                row["local_comment"] for row in exact_by_unit[(local_rows[0]["page"], unit)]
            )
            pclass = pairing_class(unit_text)
            relations = sorted({
                tag
                for row in local_rows
                for tag in row["local_relation_tags"].split(";")
                if tag
            })
            detailed = root_state(local_rows[0]["local_comment"], "plant", "UNHEDGED")
            detailed_state = detailed[0] if detailed else "UNKNOWN"
        else:
            pclass = "NO_EXACT_ANNOTATION"
            relations = []
            detailed_state = "UNKNOWN"
        comparison = (
            "UNKNOWN" if detailed_state == "UNKNOWN"
            else "AGREE" if detailed_state == state
            else "CONFLICT"
        )
        candidates.append({
            "source_record_id": annotation["source_record_id"],
            "source_page": annotation["page"],
            "physical_folio": physical_folio(annotation["page"]),
            "source_location": annotation["location"],
            "source_object_guess": annotation["object_guess"],
            "source_comment": annotation["comments"],
            "root_state": state,
            "state_rule": rule,
            "primary_current_mapping": mapping["primary_eligible"],
            "mapped_locus": locus,
            "manual_pairing_class": pclass,
            "local_relation_tags": ";".join(relations),
            "detailed_root_state": detailed_state,
            "state_comparison": comparison,
        })

    assert len(candidates) == 82
    assert Counter(row["root_state"] for row in candidates) == {"DARK": 42, "LIGHT": 40}
    assert len({row["physical_folio"] for row in candidates}) == 6
    all_by_folio = defaultdict(Counter)
    for row in candidates:
        all_by_folio[row["physical_folio"]][row["root_state"]] += 1
    assert sorted(folio for folio, counts in all_by_folio.items() if len(counts) == 2) == [
        "f100", "f101", "f88", "f89", "f99"
    ]

    primary = [row for row in candidates if row["primary_current_mapping"] == "1"]
    assert len(primary) == 56
    assert Counter(row["root_state"] for row in primary) == {"DARK": 28, "LIGHT": 28}
    pair_counts = Counter(row["manual_pairing_class"] for row in primary)
    assert pair_counts == {
        "PUBLIC_ASSUMED_OR_AMBIGUOUS": 32,
        "PUBLIC_COUNT_ONLY": 14,
        "NO_PUBLIC_PAIRING_STATEMENT": 6,
        "PUBLIC_CLEAR_PAIRING": 4,
    }
    clear = [row for row in primary if row["manual_pairing_class"] == "PUBLIC_CLEAR_PAIRING"]
    assert [row["source_record_id"] for row in clear] == [
        "STOLFI_BEST_1391", "STOLFI_BEST_1393", "STOLFI_BEST_1395", "STOLFI_BEST_1401"
    ]
    assert {row["physical_folio"] for row in clear} == {"f100"}
    assert Counter(row["root_state"] for row in clear) == {"DARK": 2, "LIGHT": 2}
    assert Counter(row["state_comparison"] for row in clear) == {"AGREE": 3, "CONFLICT": 1}
    conflict = [row for row in clear if row["state_comparison"] == "CONFLICT"]
    assert len(conflict) == 1
    assert conflict[0]["source_record_id"] == "STOLFI_BEST_1395"
    assert conflict[0]["root_state"] == "LIGHT" and conflict[0]["detailed_root_state"] == "DARK"
    corroborated = [row for row in clear if row["state_comparison"] == "AGREE"]
    assert Counter(row["root_state"] for row in corroborated) == {"DARK": 2, "LIGHT": 1}

    lines = ["\t".join(FIELDS)]
    for row in candidates:
        lines.append("\t".join(row[field].replace("\t", " ").replace("\n", " ") for field in FIELDS))
    canonical_write(OUT_TSV, "\n".join(lines) + "\n")

    gates = {
        "public_source_hash_bound": True,
        "strict_nonmixed_root_states_found": len(candidates) == 82,
        "strict_states_span_five_two_state_folios_before_ownership": True,
        "primary_current_mapping_is_balanced_28_28": True,
        "clear_pairing_has_two_states_on_two_physical_folios": False,
        "all_clear_pairing_states_are_cross_description_stable": False,
        "zero_voynich_strings_scored": True,
        "zero_ocr_or_automated_vision": True,
    }
    result = {
        "experiment": "PUBLIC_PHARMA_ROOT_COLOR_CAPACITY",
        "status": "STOP_UNSCORED_CLEAR_PAIRING_CONTRAST_ONE_FOLIO_AND_ONE_SOURCE_CONFLICT",
        "inputs": actual_inputs,
        "public_source": {"url": PUBLIC_URL, "sha256": PUBLIC_SHA256},
        "strict_source_candidates": {
            "records": len(candidates),
            "states": dict(sorted(Counter(row["root_state"] for row in candidates).items())),
            "physical_folios": sorted({row["physical_folio"] for row in candidates}),
            "two_state_folios": sorted(
                folio for folio, counts in all_by_folio.items() if len(counts) == 2
            ),
            "by_folio": {
                folio: dict(sorted(counts.items())) for folio, counts in sorted(all_by_folio.items())
            },
        },
        "primary_mapped_candidates": {
            "records": len(primary),
            "states": dict(sorted(Counter(row["root_state"] for row in primary).items())),
            "pairing_classes": dict(sorted(pair_counts.items())),
        },
        "clear_pairing_panel": {
            "records": len(clear),
            "physical_folios": ["f100"],
            "source_states": dict(sorted(Counter(row["root_state"] for row in clear).items())),
            "cross_description_comparison": dict(
                sorted(Counter(row["state_comparison"] for row in clear).items())
            ),
            "conflict": {
                "source_record_id": conflict[0]["source_record_id"],
                "older_catalogue_state": conflict[0]["root_state"],
                "detailed_comment_state": conflict[0]["detailed_root_state"],
                "adjudication": "UNKNOWN",
            },
            "corroborated_states": dict(
                sorted(Counter(row["root_state"] for row in corroborated).items())
            ),
        },
        "gates": gates,
        "decision": "STOP_BEFORE_ANY_VOYNICH_FORM_OR_GRAMMAR_SCORE",
        "claim_ceiling": (
            "The public 1998 catalogue contains a real dark/light root-description contrast, "
            "but its one-to-one ownership evidence does not transfer: only four strict mapped "
            "records sit in manually described clear-pairing units, all on f100, and one older "
            "LIGHT description conflicts with a later detailed DARK-root description. The "
            "contrast is useful source metadata but cannot identify a Voynich root-colour word, "
            "stem, construction, meaning, plaintext, or translation."
        ),
    }
    canonical_write(OUT_JSON, json.dumps(result, indent=2, sort_keys=True) + "\n")

    report = f"""# Public pharmaceutical root-colour capacity audit

Status: **{result['status']}**

This was checked against public human data, not a user-supplied plant reading. The public 1998
Stolfi/Grove catalogue yields **82** conservative, unhedged, non-mixed root-colour records:
42 DARK and 40 LIGHT across six physical folios. Before ownership is considered, both states
occur on five folios. No missing mention was read as a negative state.

That attractive count does not survive the ownership gate. Only **56** records have a primary
current-locus map (28/28 DARK/LIGHT). Public manual layout prose classifies 32 as assumed or
ambiguous pairings, 14 as count-only rows, six without a pairing statement, and only **four** as
explicitly clear pairings. All four clear cases are on f100. Their old catalogue states are 2/2,
but the later detailed public description agrees on three and calls the root in
`STOLFI_BEST_1395` DARK where the older catalogue called it LIGHT. That state remains UNKNOWN.

Therefore there is no independently transferable clear-pairing panel. Scoring stems or grammar
would simply repeat the closed proximity/assumed-ownership route. No Voynich form was scored;
no OCR or automated image analysis was used.

Decision: **STOP_BEFORE_ANY_VOYNICH_FORM_OR_GRAMMAR_SCORE**. Reopen only with explicit clear
label-to-root pairings and stable DARK/LIGHT states on at least two physical folios per state.

Public catalogue: {PUBLIC_URL}
"""
    canonical_write(REPORT, report)
    print(json.dumps({"records": len(candidates), "status": result["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
