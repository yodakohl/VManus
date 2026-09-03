#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


TARGETS = ("ol", "ckhy", "ols", "otar")


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = ROOT / "experiments/yolo/gdt771_complete_cache_discriminator_sufficiency"
DEFAULT_OUTPUT = EXPERIMENT / "artifacts"

TARGET_ATLAS = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv"
FRAME_ATLAS = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/FRAME_LOCUS_EVIDENCE.tsv"
INTEGRATED_READER = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
GDT770_COHORT = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament/src/COHORT_15_LINE_SPECS.tsv"
GDT770_EXCLUSIONS = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament/src/COHORT_EXCLUSION_LEDGER.tsv"
QUANTITY_ATLAS = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv"
SPECS = EXPERIMENT / "src/DISCRIMINATOR_SPECS.tsv"
BARE_VALUE_FORMS = EXPERIMENT / "src/OL_BARE_VALUE_FORMS.tsv"
LEFT_ROLE_TRANSFERS = EXPERIMENT / "src/OL_LEFT_ROLE_TRANSFERS.tsv"
RIGHT_ROLE_CROSSWALK = EXPERIMENT / "src/OL_RIGHT_ROLE_CROSSWALK.tsv"
RIGHT_ROLE_TRANSFERS = EXPERIMENT / "src/OL_RIGHT_ROLE_TRANSFERS.tsv"
ADDITIONAL_EXCLUSIONS = EXPERIMENT / "src/ADDITIONAL_EXCLUSION_SPECS.tsv"

INTEGRATED_COLUMNS = (
    "page", "locus", "token_count", "complete_line_v99r7",
    "unknown_cells_v99r7", "zl3b_line",
)

QUANTITY_COLUMNS = (
    "expression_id", "page", "physical_folio", "locus", "mode",
    "source_expression_eva", "start_ordinal", "end_ordinal", "right_surface",
    "right_ordinal", "right_reader_exact", "right_source_composed_quarantined",
    "value_label", "written_line_eva",
)

SELECTOR_COLUMNS = (
    "selector_id", "locus", "page", "physical_folio", "target_surfaces",
    "target_occurrence_count", "guard_selected", "gdt734_complete_line_v99r7",
    "gdt734_unknown_cells_v99r7", "gdt770_admitted_line", "union_admitted_line",
    "explicit_gdt770_exclusion", "explicit_gdt771_exclusion",
    "strict_discriminator_eligible", "admission_source",
    "current_reader_state", "forbidden_selector_prefix", "new_page_opened",
)

CONTEXT_COLUMNS = (
    "target_occurrence_id", "surface_provenance_only", "page", "physical_folio",
    "locus", "ordinal", "line_token_count", "line_position",
    "gdt734_complete_line_v99r7", "gdt734_unknown_cells_v99r7",
    "gdt770_admitted_line", "union_admitted_line", "explicit_gdt770_exclusion",
    "explicit_gdt771_exclusion",
    "strict_discriminator_eligible", "admission_source", "current_reader_state",
    "frame_ids", "d1_left_eligible_donors", "d1_right_eligible_donors",
    "r2_left_eligible_donors", "r2_right_eligible_donors", "written_line_eva",
    "target_default_credit", "target_role_credit", "confirmed_lexeme",
    "confirmed_plaintext", "component_export_credit",
)

OCCURRENCE_COLUMNS = (
    "discriminator_id", "predicate_code", "target_occurrence_id",
    "surface_provenance_only", "page", "physical_folio", "locus", "ordinal",
    "frame_ids", "match_detail", "gdt734_complete_line_v99r7",
    "gdt734_unknown_cells_v99r7", "gdt770_admitted_line", "union_admitted_line",
    "explicit_gdt770_exclusion", "explicit_gdt771_exclusion",
    "strict_qualified", "admission_state",
    "exclusion_reason", "written_line_eva", "semantic_identity_credit",
    "component_export_credit",
)

OL_BRANCH_COLUMNS = (
    "ol_bridge_id", "target_occurrence_id", "page", "physical_folio", "locus",
    "ordinal", "line_token_count", "left_surface", "left_ordinal",
    "left_evidence_classes", "gdt760_expression_ids", "gdt760_expression_eva",
    "bare_value_prior", "gdt769_broad_amount_value_prior",
    "conservative_left_licensed", "broad_left_licensed", "right_surface",
    "right_ordinal", "right_reader_exact", "right_source_roles",
    "right_role_sources", "right_gdt770_allowed_roles", "full_branch_ready",
    "gdt734_complete_line_v99r7", "gdt770_admitted_line",
    "explicit_gdt770_exclusion", "explicit_gdt771_exclusion",
    "strict_discriminator_eligible", "written_line_eva",
    "semantic_identity_credit", "component_export_credit",
)

SUMMARY_COLUMNS = (
    "discriminator_id", "target_surface", "predicate_code",
    "all_exact_match_occurrences", "all_exact_match_pages",
    "union_admitted_match_occurrences", "explicitly_excluded_admitted_occurrences",
    "qualified_occurrences", "qualified_distinct_pages", "strongest_page",
    "strongest_page_occurrences", "holdout_occurrences", "holdout_distinct_pages",
    "minimum_occurrences", "minimum_distinct_pages", "minimum_holdout_pages",
    "decision", "working_reading_if_pass_de", "primary_rival_de",
    "claim_if_pass_de", "confirmed_lexeme", "confirmed_plaintext",
)

OTAR_COLUMNS = (
    "candidate_id", "concrete_working_reading_de", "support_occurrences",
    "support_distinct_pages", "support_occurrence_ids", "support_pages",
    "overlap_with_primary_rival_occurrences", "exclusive_against_primary_rival_occurrences",
    "holdout_occurrences", "holdout_distinct_pages", "coverage_relation",
    "working_disposition", "confirmed_lexeme", "semantic_identity_credit",
)

DECK_COLUMNS = (
    "deck_id", "target_surface", "target_occurrence_id", "page", "locus",
    "ordinal", "deck_role", "recommended_action", "already_in_gdt770",
    "strict_qualified", "evidence_ids", "reason_de", "reader_requirement_de",
    "semantic_identity_credit",
)

DICTIONARY_COLUMNS = (
    "dictionary_id", "whole_form", "portable_structural_reading_de",
    "concrete_default_de", "confidence_level", "evidence_de",
    "counterevidence_de", "scope", "replaceable", "confirmed_lexeme",
    "confirmed_plaintext", "component_export_credit",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(columns), delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_query(
    path: Path,
    loci: Sequence[str],
    columns: Sequence[str],
    expected_stats: Mapping[str, int],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    loci = sorted(set(loci))
    if any(locus.startswith("f84") for locus in loci):
        raise AssertionError("forbidden selector entered explicit allow list")
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "locus",
    ]
    for locus in loci:
        command.extend(("--allow", locus))
    command.extend(("--columns", ",".join(columns)))
    completed = subprocess.run(
        command, cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    rows = list(csv.DictReader(completed.stdout.splitlines(), delimiter="\t"))
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise AssertionError("guard did not emit exactly one statistics line")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    if stats != expected_stats:
        raise AssertionError(f"unexpected guarded query stats for {path.name}: {stats}")
    return rows, stats


def guard_integrated_reader(
    target_rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    loci = sorted({row["locus"] for row in target_rows})
    if len(loci) != 461:
        raise AssertionError(f"expected 461 explicit selector loci, got {len(loci)}")
    rows, stats = guarded_query(
        INTEGRATED_READER, loci, INTEGRATED_COLUMNS,
        {"selected": 461, "skipped_forbidden": 0, "skipped_not_allowed": 3667},
    )
    if {row["locus"] for row in rows} != set(loci) or len(rows) != len(loci):
        raise AssertionError("guarded integrated selection is not one-to-one with allow list")
    return rows, stats


def guard_quantity_atlas(
    target_rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    loci = sorted({row["locus"] for row in target_rows})
    return guarded_query(
        QUANTITY_ATLAS, loci, QUANTITY_COLUMNS,
        {"selected": 46, "skipped_forbidden": 0, "skipped_not_allowed": 235},
    )


def frame_map(frame_rows: Sequence[Mapping[str, str]]) -> dict[str, set[str]]:
    output: dict[str, set[str]] = defaultdict(set)
    for row in frame_rows:
        output[row["target_occurrence_id"]].add(row["frame_id"])
    return output


def parsed_context(row: Mapping[str, str]) -> dict[str, object]:
    return json.loads(row["context_views"])


def donors(row: Mapping[str, str], radius: str, direction: str) -> list[dict[str, object]]:
    return [
        donor for donor in parsed_context(row)[radius]["eligible_donors"]
        if donor["direction"] == direction
    ]


def donor_text(items: Sequence[Mapping[str, object]]) -> str:
    if not items:
        return "NONE"
    values = []
    for donor in sorted(items, key=lambda item: (int(item["distance"]), int(item["ordinal"]))):
        roles = "/".join(sorted(str(value) for value in donor.get("roles", []))) or "NONE"
        features = "/".join(sorted(str(value) for value in donor.get("features", []))) or "NONE"
        values.append(
            f"{donor['surface']}@{donor['ordinal']}:d{donor['distance']}:roles={roles}:features={features}"
        )
    return " ; ".join(values)


def all_donors(row: Mapping[str, str], radius: str = "D1") -> list[dict[str, object]]:
    context = parsed_context(row)[radius]
    return list(context["eligible_donors"]) + list(context["blocked_donors"])


def direct_donor(
    row: Mapping[str, str], direction: str,
) -> dict[str, object] | None:
    matches = [
        donor for donor in all_donors(row)
        if donor["direction"] == direction and int(donor["distance"]) == 1
    ]
    if len(matches) > 1:
        raise AssertionError(f"multiple direct {direction} donors for {row['target_occurrence_id']}")
    return matches[0] if matches else None


def donor_is_reader_exact(donor: Mapping[str, object] | None) -> bool:
    return bool(
        donor
        and int(donor.get("current_clean", 0)) == 1
        and donor.get("gate_status") != "NONEXACT"
    )


def ol_left_pure(row: Mapping[str, str]) -> list[dict[str, object]]:
    matches = []
    for donor in donors(row, "D1", "LEFT"):
        roles = set(donor.get("roles", []))
        features = set(donor.get("features", []))
        if (
            roles & {"AMOUNT_VALUE", "SCALAR_VALUE"}
            and not roles & {"CONTENT_PREPARATION", "QUALITY_STAGE"}
            and "VALUE_AMOUNT" in features
        ):
            matches.append(donor)
    return matches


def build_ol_evidence(
    target_rows: Sequence[Mapping[str, str]],
    quantity_rows: Sequence[Mapping[str, str]],
    bare_values: Mapping[str, str],
    left_transfers: Mapping[tuple[str, str, str, str], Mapping[str, str]],
    crosswalk: Mapping[str, set[str]],
    transfers: Mapping[tuple[str, str, str, str], Mapping[str, str]],
) -> dict[str, dict[str, object]]:
    quantity_by_target: dict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
    for row in quantity_rows:
        if (
            row["right_surface"] == "ol"
            and row["right_reader_exact"] == "1"
            and row["right_source_composed_quarantined"] == "0"
            and int(row["end_ordinal"]) + 1 == int(row["right_ordinal"])
        ):
            quantity_by_target[(row["locus"], row["right_ordinal"])].append(row)

    evidence: dict[str, dict[str, object]] = {}
    for row in target_rows:
        if row["surface"] != "ol":
            continue
        ordinal = int(row["ordinal"])
        tokens = row["written_line_eva"].split()
        if len(tokens) != int(row["line_token_count"]) or tokens[ordinal - 1] != "ol":
            raise AssertionError(f"target token geometry changed for {row['target_occurrence_id']}")
        left_surface = tokens[ordinal - 2] if ordinal > 1 else "LINE_EDGE"
        right_surface = tokens[ordinal] if ordinal < len(tokens) else "LINE_EDGE"
        left = direct_donor(row, "LEFT")
        right = direct_donor(row, "RIGHT")
        amount_rows = quantity_by_target.get((row["locus"], row["ordinal"]), [])
        bare = (
            left_surface in bare_values
            and donor_is_reader_exact(left)
            and left is not None
            and left.get("surface") == left_surface
        )
        left_transfer_key = (row["locus"], row["ordinal"], left_surface, str(ordinal - 1))
        left_transfer = left_transfers.get(left_transfer_key)
        broad = bool(ol_left_pure(row))
        classes = []
        if amount_rows:
            classes.append("GDT760_EXACT_AMOUNT_SPAN")
        if bare:
            classes.append("LICENSED_BARE_VALUE")
        if left_transfer:
            classes.append(left_transfer["transfer_id"])
        if broad:
            classes.append("GDT769_BROAD_AMOUNT_VALUE")

        right_roles = set(str(value) for value in (right or {}).get("roles", []))
        allowed_roles: set[str] = set()
        role_sources = []
        if right and right.get("gate_status") == "ELIGIBLE" and donor_is_reader_exact(right):
            for role in right_roles:
                mapped = crosswalk.get(role, set())
                allowed_roles.update(mapped)
                if mapped:
                    role_sources.append(f"GDT769_DIRECT:{role}")
        transfer_key = (row["locus"], row["ordinal"], right_surface, str(ordinal + 1))
        transfer = transfers.get(transfer_key)
        if transfer:
            allowed_roles.update(
                value for value in transfer["gdt770_allowed_roles"].split("|") if value != "NONE"
            )
            role_sources.append(transfer["transfer_id"])
        conservative = bool(amount_rows or bare or left_transfer)
        right_exact = donor_is_reader_exact(right)
        evidence[row["target_occurrence_id"]] = {
            "left_surface": left_surface,
            "left_ordinal": ordinal - 1 if ordinal > 1 else 0,
            "left_evidence_classes": classes,
            "quantity_rows": amount_rows,
            "bare_value_prior": bare_values.get(left_surface, "NONE") if bare else "NONE",
            "broad_gdt769_amount_value_prior": broad,
            "conservative_left_licensed": conservative,
            "broad_left_licensed": conservative or broad,
            "right_surface": right_surface,
            "right_ordinal": ordinal + 1 if ordinal < len(tokens) else 0,
            "right_reader_exact": right_exact,
            "right_source_roles": right_roles,
            "right_role_sources": role_sources,
            "right_gdt770_allowed_roles": allowed_roles,
            "full_branch_ready": conservative and right_exact and bool(allowed_roles),
        }
    return evidence


def endpoint_sides(row: Mapping[str, str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    left: list[dict[str, object]] = []
    right: list[dict[str, object]] = []
    for donor in parsed_context(row)["R2"]["eligible_donors"]:
        roles = set(donor.get("roles", []))
        features = set(donor.get("features", []))
        if donor["direction"] == "LEFT" and (
            roles & {"PROCESS_PASS", "PROCESS"} or features & {"PROCESS", "PASS"}
        ):
            left.append(donor)
        if donor["direction"] == "RIGHT" and (
            roles & {"CLOSE", "RESULT", "ENDPOINT"} or features & {"CLOSE", "END_STAGE"}
        ):
            right.append(donor)
    return left, right


def gdt770_target_roles(
    rows: Sequence[Mapping[str, str]],
) -> dict[tuple[str, str, str], tuple[set[str], set[str]]]:
    output = {}
    for row in rows:
        if row["is_target"] != "1":
            continue
        output[(row["locus"], row["ordinal"], row["surface"])] = (
            {value for value in row["left_neighbor_roles"].split("|") if value != "NONE"},
            {value for value in row["right_neighbor_roles"].split("|") if value != "NONE"},
        )
    return output


def gdt770_endpoint_match(
    row: Mapping[str, str],
    role_map: Mapping[tuple[str, str, str], tuple[set[str], set[str]]],
) -> bool:
    left, right = role_map.get((row["locus"], row["ordinal"], row["surface"]), (set(), set()))
    return bool(left & {"PROCESS", "FIELD"}) and "ENDPOINT" in right


def make_predicates(
    frames: Mapping[str, set[str]],
    role_map: Mapping[tuple[str, str, str], tuple[set[str], set[str]]],
    ol_evidence: Mapping[str, Mapping[str, object]],
) -> dict[str, Callable[[Mapping[str, str]], bool]]:
    return {
        "OL_LEFT_CONSERVATIVE_AMOUNT_OR_VALUE": lambda row: row["surface"] == "ol"
        and bool(ol_evidence[row["target_occurrence_id"]]["conservative_left_licensed"]),
        "OL_LEFT_VALUE_RIGHT_READER_EXACT": lambda row: row["surface"] == "ol"
        and bool(ol_evidence[row["target_occurrence_id"]]["conservative_left_licensed"])
        and bool(ol_evidence[row["target_occurrence_id"]]["right_reader_exact"]),
        "OL_LEFT_VALUE_GDT770_TYPED_RIGHT": lambda row: (
            row["surface"] == "ol"
            and bool(ol_evidence[row["target_occurrence_id"]]["full_branch_ready"])
        ),
        "CKHY_F05_AND_F07": lambda row: row["surface"] == "ckhy"
        and {"F05_PROCESS_SLOT_FINAL", "F07_LINE_FINAL_OR_CLOSE"}
        <= frames.get(row["target_occurrence_id"], set()),
        "OLS_F02_VALUE_DIRECT": lambda row: row["surface"] == "ols"
        and "F02_VALUE_DIRECT" in frames.get(row["target_occurrence_id"], set()),
        "OTAR_SEQUENCE_BRIDGE": lambda row: row["surface"] == "otar"
        and (
            (
                "F14_MEDIAL_TWO_SIDED_LINKER" in frames.get(row["target_occurrence_id"], set())
                and bool(frames.get(row["target_occurrence_id"], set()) & {
                    "F15_STATE_TRANSITION_BRIDGE", "F16_RELATIONAL_AMOUNT_ORDER",
                })
            )
            or "F06_TARGET_BEFORE_PROCESS" in frames.get(row["target_occurrence_id"], set())
        ),
        "OTAR_NOMINAL_BRIDGE": lambda row: row["surface"] == "otar"
        and bool(frames.get(row["target_occurrence_id"], set()) & {
            "F01_AMOUNT_DIRECT", "F02_VALUE_DIRECT", "F06_TARGET_BEFORE_PROCESS",
        }),
        "OTAR_PROCESS_LEFT_ENDPOINT_RIGHT": lambda row: row["surface"] == "otar"
        and (all(bool(side) for side in endpoint_sides(row)) or gdt770_endpoint_match(row, role_map)),
    }


def match_detail(
    row: Mapping[str, str],
    predicate_code: str,
    frames: Mapping[str, set[str]],
    role_map: Mapping[tuple[str, str, str], tuple[set[str], set[str]]],
    ol_evidence: Mapping[str, Mapping[str, object]],
) -> str:
    if predicate_code.startswith("OL_LEFT_"):
        item = ol_evidence[row["target_occurrence_id"]]
        return (
            "LEFT=" + str(item["left_surface"])
            + "@" + str(item["left_ordinal"])
            + ":evidence=" + ("/".join(item["left_evidence_classes"]) or "NONE")
            + " || RIGHT=" + str(item["right_surface"])
            + "@" + str(item["right_ordinal"])
            + ":reader_exact=" + str(int(bool(item["right_reader_exact"])))
            + ":source_roles=" + ("/".join(sorted(item["right_source_roles"])) or "NONE")
            + ":allowed_roles=" + ("/".join(sorted(item["right_gdt770_allowed_roles"])) or "NONE")
        )
    if predicate_code == "OTAR_PROCESS_LEFT_ENDPOINT_RIGHT":
        left, right = endpoint_sides(row)
        frozen_left, frozen_right = role_map.get(
            (row["locus"], row["ordinal"], row["surface"]), (set(), set())
        )
        return (
            "GDT769_LEFT_PROCESS=" + donor_text(left)
            + " || GDT769_RIGHT_ENDPOINT=" + donor_text(right)
            + " || GDT770_LEFT_ROLES=" + ("/".join(sorted(frozen_left)) or "NONE")
            + " || GDT770_RIGHT_ROLES=" + ("/".join(sorted(frozen_right)) or "NONE")
        )
    return "FRAMES=" + "|".join(sorted(frames.get(row["target_occurrence_id"], set())))


def admission_state(
    locus: str,
    integrated: Mapping[str, Mapping[str, str]],
    gdt770_loci: set[str],
    excluded: Mapping[str, list[str]],
) -> str:
    base = integrated[locus]["complete_line_v99r7"] == "1" and integrated[locus]["unknown_cells_v99r7"] == "0"
    current = locus in gdt770_loci
    if not (base or current):
        return "EXACT_BUT_NOT_COMPLETE"
    if locus in excluded:
        return "ADMITTED_BUT_EXPLICITLY_EXCLUDED"
    if base and current:
        return "QUALIFIED_GDT734_AND_GDT770"
    if current:
        return "QUALIFIED_GDT770_EXTENSION"
    return "QUALIFIED_GDT734_COMPLETE_CACHE"


def strongest_holdout(rows: Sequence[Mapping[str, str]]) -> tuple[str, int, int, int]:
    counts = Counter(row["page"] for row in rows)
    if not counts:
        return "NONE", 0, 0, 0
    strongest_page, strongest_count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    return strongest_page, strongest_count, len(rows) - strongest_count, len(counts) - 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    all_target_rows = read_tsv(TARGET_ATLAS)
    target_rows = [row for row in all_target_rows if row["surface"] in TARGETS]
    if len(target_rows) != 523 or any(row["reader_exact"] != "1" for row in target_rows):
        raise AssertionError("GDT769 four-target exact cohort changed")
    if any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in target_rows):
        raise AssertionError("sealed page entered GDT769 exact target cohort")

    integrated_rows, guard_stats = guard_integrated_reader(target_rows)
    quantity_rows, quantity_guard_stats = guard_quantity_atlas(target_rows)
    integrated = {row["locus"]: row for row in integrated_rows}
    gdt770_rows = read_tsv(GDT770_COHORT)
    gdt770_loci = {row["locus"] for row in gdt770_rows}
    if len(gdt770_loci) != 15:
        raise AssertionError("GDT770 admitted-line count changed")
    exclusion_rows = read_tsv(GDT770_EXCLUSIONS)
    gdt770_exclusions: dict[str, list[str]] = defaultdict(list)
    for row in exclusion_rows:
        gdt770_exclusions[row["locus"]].append(row["exclusion_reason"])
    additional_exclusion_rows = read_tsv(ADDITIONAL_EXCLUSIONS)
    gdt771_exclusions: dict[str, list[str]] = defaultdict(list)
    for row in additional_exclusion_rows:
        gdt771_exclusions[row["locus"]].append(row["exclusion_reason"])
    exclusions: dict[str, list[str]] = defaultdict(list)
    for source in (gdt770_exclusions, gdt771_exclusions):
        for locus, reasons in source.items():
            exclusions[locus].extend(reasons)
    frames = frame_map(read_tsv(FRAME_ATLAS))
    role_map = gdt770_target_roles(gdt770_rows)
    bare_values = {
        row["surface"]: row["provenance"] for row in read_tsv(BARE_VALUE_FORMS)
        if row["plaintext_credit"] == "0"
    }
    left_transfers = {
        (row["locus"], row["target_ordinal"], row["left_surface"], row["left_ordinal"]): row
        for row in read_tsv(LEFT_ROLE_TRANSFERS)
    }
    crosswalk: dict[str, set[str]] = defaultdict(set)
    for row in read_tsv(RIGHT_ROLE_CROSSWALK):
        if row["admit_for_left_amount_branch"] == "1":
            crosswalk[row["source_role"]].add(row["gdt770_allowed_role"])
    transfers = {
        (row["locus"], row["target_ordinal"], row["right_surface"], row["right_ordinal"]): row
        for row in read_tsv(RIGHT_ROLE_TRANSFERS)
    }
    ol_evidence = build_ol_evidence(
        target_rows, quantity_rows, bare_values, left_transfers, crosswalk, transfers,
    )
    specs = read_tsv(SPECS)
    if len(specs) != 8 or len({row["discriminator_id"] for row in specs}) != 8:
        raise AssertionError("discriminator deck changed")
    predicates = make_predicates(frames, role_map, ol_evidence)
    if {row["predicate_code"] for row in specs} != set(predicates):
        raise AssertionError("predicate implementation and source deck differ")

    base_complete = {
        locus for locus, row in integrated.items()
        if row["complete_line_v99r7"] == "1" and row["unknown_cells_v99r7"] == "0"
    }
    union_admitted = base_complete | gdt770_loci
    strict_loci = union_admitted - set(exclusions)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in target_rows:
        by_locus[row["locus"]].append(row)

    selector_rows: list[dict[str, object]] = []
    for index, locus in enumerate(sorted(by_locus), start=1):
        targets_here = by_locus[locus]
        source = integrated[locus]
        base = locus in base_complete
        current = locus in gdt770_loci
        admitted = locus in union_admitted
        excluded = locus in exclusions
        selector_rows.append(
            {
                "selector_id": f"G771-S{index:04d}",
                "locus": locus,
                "page": source["page"],
                "physical_folio": targets_here[0]["physical_folio"],
                "target_surfaces": "|".join(sorted({row["surface"] for row in targets_here})),
                "target_occurrence_count": len(targets_here),
                "guard_selected": 1,
                "gdt734_complete_line_v99r7": int(base),
                "gdt734_unknown_cells_v99r7": int(source["unknown_cells_v99r7"]),
                "gdt770_admitted_line": int(current),
                "union_admitted_line": int(admitted),
                "explicit_gdt770_exclusion": int(locus in gdt770_exclusions),
                "explicit_gdt771_exclusion": int(locus in gdt771_exclusions),
                "strict_discriminator_eligible": int(locus in strict_loci),
                "admission_source": (
                    "GDT734_COMPLETE_AND_GDT770" if base and current
                    else "GDT770_ADMITTED_EXTENSION" if current
                    else "GDT734_COMPLETE_CACHE" if base
                    else "NOT_COMPLETE"
                ),
                "current_reader_state": (
                    "GDT770_CURRENT_MASKED_READER" if current
                    else "STRUCTURAL_COMPLETE_CACHE__RERENDER_REQUIRED" if base
                    else "NO_COMPLETE_READER"
                ),
                "forbidden_selector_prefix": 0,
                "new_page_opened": 0,
            }
        )

    complete_context_rows: list[dict[str, object]] = []
    for row in sorted(target_rows, key=lambda item: (item["locus"], int(item["ordinal"]), item["surface"])):
        locus = row["locus"]
        if locus not in union_admitted:
            continue
        base = locus in base_complete
        current = locus in gdt770_loci
        excluded = locus in exclusions
        complete_context_rows.append(
            {
                "target_occurrence_id": row["target_occurrence_id"],
                "surface_provenance_only": row["surface"],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": locus,
                "ordinal": int(row["ordinal"]),
                "line_token_count": int(row["line_token_count"]),
                "line_position": row["line_position"],
                "gdt734_complete_line_v99r7": int(base),
                "gdt734_unknown_cells_v99r7": int(integrated[locus]["unknown_cells_v99r7"]),
                "gdt770_admitted_line": int(current),
                "union_admitted_line": 1,
                "explicit_gdt770_exclusion": int(locus in gdt770_exclusions),
                "explicit_gdt771_exclusion": int(locus in gdt771_exclusions),
                "strict_discriminator_eligible": int(locus in strict_loci),
                "admission_source": (
                    "GDT734_COMPLETE_AND_GDT770" if base and current
                    else "GDT770_ADMITTED_EXTENSION" if current
                    else "GDT734_COMPLETE_CACHE"
                ),
                "current_reader_state": (
                    "GDT770_CURRENT_MASKED_READER" if current
                    else "STRUCTURAL_COMPLETE_CACHE__RERENDER_REQUIRED"
                ),
                "frame_ids": "|".join(sorted(frames.get(row["target_occurrence_id"], set()))) or "NONE",
                "d1_left_eligible_donors": donor_text(donors(row, "D1", "LEFT")),
                "d1_right_eligible_donors": donor_text(donors(row, "D1", "RIGHT")),
                "r2_left_eligible_donors": donor_text(donors(row, "R2", "LEFT")),
                "r2_right_eligible_donors": donor_text(donors(row, "R2", "RIGHT")),
                "written_line_eva": row["written_line_eva"],
                "target_default_credit": 0,
                "target_role_credit": 0,
                "confirmed_lexeme": 0,
                "confirmed_plaintext": 0,
                "component_export_credit": 0,
            }
        )

    ol_branch_rows: list[dict[str, object]] = []
    ol_targets = {row["target_occurrence_id"]: row for row in target_rows if row["surface"] == "ol"}
    for target_id, item in sorted(
        ol_evidence.items(), key=lambda pair: (
            ol_targets[pair[0]]["locus"], int(ol_targets[pair[0]]["ordinal"]), pair[0],
        ),
    ):
        if not item["broad_left_licensed"]:
            continue
        row = ol_targets[target_id]
        amount_rows = item["quantity_rows"]
        locus = row["locus"]
        ol_branch_rows.append(
            {
                "ol_bridge_id": "PENDING",
                "target_occurrence_id": target_id,
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "locus": locus,
                "ordinal": int(row["ordinal"]),
                "line_token_count": int(row["line_token_count"]),
                "left_surface": item["left_surface"],
                "left_ordinal": item["left_ordinal"],
                "left_evidence_classes": "|".join(item["left_evidence_classes"]) or "NONE",
                "gdt760_expression_ids": "|".join(sorted(value["expression_id"] for value in amount_rows)) or "NONE",
                "gdt760_expression_eva": "|".join(sorted({value["source_expression_eva"] for value in amount_rows})) or "NONE",
                "bare_value_prior": item["bare_value_prior"],
                "gdt769_broad_amount_value_prior": int(item["broad_gdt769_amount_value_prior"]),
                "conservative_left_licensed": int(item["conservative_left_licensed"]),
                "broad_left_licensed": int(item["broad_left_licensed"]),
                "right_surface": item["right_surface"],
                "right_ordinal": item["right_ordinal"],
                "right_reader_exact": int(item["right_reader_exact"]),
                "right_source_roles": "|".join(sorted(item["right_source_roles"])) or "NONE",
                "right_role_sources": "|".join(sorted(item["right_role_sources"])) or "NONE",
                "right_gdt770_allowed_roles": "|".join(sorted(item["right_gdt770_allowed_roles"])) or "NONE",
                "full_branch_ready": int(item["full_branch_ready"]),
                "gdt734_complete_line_v99r7": int(locus in base_complete),
                "gdt770_admitted_line": int(locus in gdt770_loci),
                "explicit_gdt770_exclusion": int(locus in gdt770_exclusions),
                "explicit_gdt771_exclusion": int(locus in gdt771_exclusions),
                "strict_discriminator_eligible": int(locus in strict_loci),
                "written_line_eva": row["written_line_eva"],
                "semantic_identity_credit": 0,
                "component_export_credit": 0,
            }
        )
    for index, row in enumerate(ol_branch_rows, start=1):
        row["ol_bridge_id"] = f"G771-O{index:03d}"

    occurrence_rows: list[dict[str, object]] = []
    strict_by_discriminator: dict[str, list[dict[str, str]]] = {}
    all_by_discriminator: dict[str, list[dict[str, str]]] = {}
    for spec in specs:
        predicate = predicates[spec["predicate_code"]]
        matches = [row for row in target_rows if predicate(row)]
        qualified = [row for row in matches if row["locus"] in strict_loci]
        all_by_discriminator[spec["discriminator_id"]] = matches
        strict_by_discriminator[spec["discriminator_id"]] = qualified
        for row in matches:
            locus = row["locus"]
            occurrence_rows.append(
                {
                    "discriminator_id": spec["discriminator_id"],
                    "predicate_code": spec["predicate_code"],
                    "target_occurrence_id": row["target_occurrence_id"],
                    "surface_provenance_only": row["surface"],
                    "page": row["page"],
                    "physical_folio": row["physical_folio"],
                    "locus": locus,
                    "ordinal": int(row["ordinal"]),
                    "frame_ids": "|".join(sorted(frames.get(row["target_occurrence_id"], set()))) or "NONE",
                    "match_detail": match_detail(
                        row, spec["predicate_code"], frames, role_map, ol_evidence,
                    ),
                    "gdt734_complete_line_v99r7": int(locus in base_complete),
                    "gdt734_unknown_cells_v99r7": int(integrated[locus]["unknown_cells_v99r7"]),
                    "gdt770_admitted_line": int(locus in gdt770_loci),
                    "union_admitted_line": int(locus in union_admitted),
                    "explicit_gdt770_exclusion": int(locus in gdt770_exclusions),
                    "explicit_gdt771_exclusion": int(locus in gdt771_exclusions),
                    "strict_qualified": int(locus in strict_loci),
                    "admission_state": admission_state(locus, integrated, gdt770_loci, exclusions),
                    "exclusion_reason": " || ".join(exclusions.get(locus, [])) or "NONE",
                    "written_line_eva": row["written_line_eva"],
                    "semantic_identity_credit": 0,
                    "component_export_credit": 0,
                }
            )
    occurrence_rows.sort(key=lambda row: (row["discriminator_id"], row["locus"], int(row["ordinal"])))

    summary_rows: list[dict[str, object]] = []
    for spec in specs:
        all_matches = all_by_discriminator[spec["discriminator_id"]]
        admitted_matches = [row for row in all_matches if row["locus"] in union_admitted]
        qualified = strict_by_discriminator[spec["discriminator_id"]]
        strongest_page, strongest_count, holdout_occurrences, holdout_pages = strongest_holdout(qualified)
        decision = "PASS_AVAILABLE" if (
            len(qualified) >= int(spec["minimum_occurrences"])
            and len({row["page"] for row in qualified}) >= int(spec["minimum_distinct_pages"])
            and holdout_pages >= int(spec["minimum_holdout_pages"])
        ) else "FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS"
        summary_rows.append(
            {
                "discriminator_id": spec["discriminator_id"],
                "target_surface": spec["target_surface"],
                "predicate_code": spec["predicate_code"],
                "all_exact_match_occurrences": len(all_matches),
                "all_exact_match_pages": len({row["page"] for row in all_matches}),
                "union_admitted_match_occurrences": len(admitted_matches),
                "explicitly_excluded_admitted_occurrences": sum(row["locus"] in exclusions for row in admitted_matches),
                "qualified_occurrences": len(qualified),
                "qualified_distinct_pages": len({row["page"] for row in qualified}),
                "strongest_page": strongest_page,
                "strongest_page_occurrences": strongest_count,
                "holdout_occurrences": holdout_occurrences,
                "holdout_distinct_pages": holdout_pages,
                "minimum_occurrences": int(spec["minimum_occurrences"]),
                "minimum_distinct_pages": int(spec["minimum_distinct_pages"]),
                "minimum_holdout_pages": int(spec["minimum_holdout_pages"]),
                "decision": decision,
                "working_reading_if_pass_de": spec["working_reading_if_pass_de"] if decision == "PASS_AVAILABLE" else "NONE",
                "primary_rival_de": spec["primary_rival_de"],
                "claim_if_pass_de": spec["claim_if_pass_de"] if decision == "PASS_AVAILABLE" else "NONE",
                "confirmed_lexeme": 0,
                "confirmed_plaintext": 0,
            }
        )

    summary_by_id = {row["discriminator_id"]: row for row in summary_rows}
    sequence = {row["target_occurrence_id"]: row for row in strict_by_discriminator["D04S_OTAR_SEQUENCE"]}
    nominal = {row["target_occurrence_id"]: row for row in strict_by_discriminator["D04N_OTAR_NOMINAL"]}
    endpoint = {row["target_occurrence_id"]: row for row in strict_by_discriminator["D04E_OTAR_ENDPOINT"]}

    def otar_row(
        candidate_id: str,
        reading: str,
        support: Mapping[str, Mapping[str, str]],
        rival: Mapping[str, Mapping[str, str]],
        relation: str,
        disposition: str,
    ) -> dict[str, object]:
        ordered = [support[key] for key in sorted(support)]
        _page, _count, holdout_occurrences, holdout_pages = strongest_holdout(ordered)
        return {
            "candidate_id": candidate_id,
            "concrete_working_reading_de": reading,
            "support_occurrences": len(support),
            "support_distinct_pages": len({row["page"] for row in ordered}),
            "support_occurrence_ids": "|".join(sorted(support)) or "NONE",
            "support_pages": "|".join(sorted({row["page"] for row in ordered})) or "NONE",
            "overlap_with_primary_rival_occurrences": len(set(support) & set(rival)),
            "exclusive_against_primary_rival_occurrences": len(set(support) - set(rival)),
            "holdout_occurrences": holdout_occurrences,
            "holdout_distinct_pages": holdout_pages,
            "coverage_relation": relation,
            "working_disposition": disposition,
            "confirmed_lexeme": 0,
            "semantic_identity_credit": 0,
        }

    sequence_contains_nominal = bool(nominal) and set(nominal) < set(sequence)
    otar_rows = [
        otar_row(
            "OTAR_SEQUENCE_THEN", "dann/weiter", sequence, nominal,
            "STRICT_SUPERSET_OF_NOMINAL_UNDER_GDT769_PREDICATES"
            if sequence_contains_nominal else "NO_STRICT_COVERAGE_RELATION",
            "DISPLAY_LEAD_ONLY__NOMINAL_AND_ENDPOINT_RIVALS_OPEN"
            if sequence_contains_nominal else "OPEN_RIVAL",
        ),
        otar_row(
            "OTAR_NOMINAL_TRANSITION", "Zwischenzubereitung", nominal, sequence,
            "STRICT_SUBSET_OF_SEQUENCE_UNDER_GDT769_PREDICATES"
            if sequence_contains_nominal else "NO_STRICT_COVERAGE_RELATION",
            "SUPPORTED_NESTED_RIVAL__NOT_ELIMINATED" if nominal else "UNSUPPORTED",
        ),
        otar_row(
            "OTAR_ENDPOINT_UNTIL", "bis zum Endzustand", endpoint, sequence,
            "EMPTY_SET" if not endpoint else "HAS_SUPPORT",
            "UNSUPPORTED_IN_AVAILABLE_CACHE" if not endpoint
            else "LOCAL_SINGLE_PAGE_RIVAL__REPLICATION_MISSING",
        ),
    ]

    gdt770_target_keys = {
        (row["locus"], row["ordinal"])
        for row in gdt770_rows if row["is_target"] == "1"
    }
    deck_rows: list[dict[str, object]] = []

    def add_deck(
        row: Mapping[str, str], role: str, action: str, evidence: str,
        reason: str, requirement: str, strict: bool,
    ) -> None:
        deck_rows.append(
            {
                "deck_id": "PENDING",
                "target_surface": row["surface"],
                "target_occurrence_id": row["target_occurrence_id"],
                "page": row["page"],
                "locus": row["locus"],
                "ordinal": int(row["ordinal"]),
                "deck_role": role,
                "recommended_action": action,
                "already_in_gdt770": int((row["locus"], row["ordinal"]) in gdt770_target_keys),
                "strict_qualified": int(strict),
                "evidence_ids": evidence,
                "reason_de": reason,
                "reader_requirement_de": requirement,
                "semantic_identity_credit": 0,
            }
        )

    for row in all_by_discriminator["D01B_OL_FULL_BRANCH"]:
        strict = row["locus"] in strict_loci
        add_deck(
            row, "OL_LEFT_VALUE_TYPED_RIGHT",
            "SCORE_ADD" if strict else "HOLD_EXCLUDED_OR_INCOMPLETE",
            match_detail(
                row, "OL_LEFT_VALUE_GDT770_TYPED_RIGHT", frames, role_map, ol_evidence,
            ),
            "Füllt den gesamten bislang unbelegten Relatorzweig." if strict
            else "Der strukturelle Treffer ist derzeit nicht streng zugelassen.",
            "Vor Score-Aufnahme aktuelle Vollzeile ohne alte Stoffhauptwörter rendern.", strict,
        )

    for row in target_rows:
        row_frames = frames.get(row["target_occurrence_id"], set())
        if (
            row["surface"] == "ckhy"
            and "F07_LINE_FINAL_OR_CLOSE" in row_frames
            and "F05_PROCESS_SLOT_FINAL" not in row_frames
            and row["locus"] in union_admitted
        ):
            strict = row["locus"] in strict_loci
            add_deck(
                row, "CKHY_FINAL_WITHOUT_PATIENT_CONTROL",
                "NEGATIVE_CONTROL_ADD" if strict else "HOLD_EXCLUDED",
                "F07_LINE_FINAL_OR_CLOSE;F05_ABSENT",
                "Finalposition allein darf nicht als Mischen gezählt werden.",
                "Nichttarget-Nachbarn aktuell und ohne Bedeutungsimport typisieren.", strict,
            )

    for row in all_by_discriminator["D03_OLS_RIGHT_VALUE"]:
        strict = row["locus"] in strict_loci
        add_deck(
            row, "OLS_RIGHT_VALUE",
            "ALREADY_GDT770" if strict else "HOLD_INCOMPLETE_OR_EXCLUDED",
            "F02_VALUE_DIRECT",
            "Direkter rechter Wertkontakt; nur ein streng vollständiger Fall verfügbar.",
            "Unvollständige Zeilen nicht durch Zielbedeutung schließen.", strict,
        )

    for row in all_by_discriminator["D04S_OTAR_SEQUENCE"]:
        strict = row["locus"] in strict_loci
        already = (row["locus"], row["ordinal"]) in gdt770_target_keys
        add_deck(
            row, "OTAR_SEQUENCE_BRIDGE",
            "ALREADY_GDT770" if strict and already else "SCORE_ADD" if strict
            else "HOLD_EXCLUDED_OR_INCOMPLETE",
            "|".join(sorted(frames.get(row["target_occurrence_id"], set()))),
            "Prüft dann/weiter gegen das verschachtelte Nominalmodell.",
            "Neue Zeile vor Reader-Ausgabe aktuell und targetmaskiert typisieren.", strict,
        )

    deck_rows.sort(key=lambda row: (
        row["target_surface"], row["locus"], int(row["ordinal"]), row["deck_role"],
    ))
    for index, row in enumerate(deck_rows, start=1):
        row["deck_id"] = f"G771-D{index:03d}"

    ol_left = summary_by_id["D01A_OL_LEFT_LICENSED"]
    ol_right_exact = summary_by_id["D01X_OL_LEFT_RIGHT_EXACT"]
    ol_full = summary_by_id["D01B_OL_FULL_BRANCH"]
    ckhy = summary_by_id["D02_CKHY_FINAL_PATIENT"]
    ols = summary_by_id["D03_OLS_RIGHT_VALUE"]
    otar_sequence = summary_by_id["D04S_OTAR_SEQUENCE"]
    otar_nominal = summary_by_id["D04N_OTAR_NOMINAL"]
    otar_endpoint = summary_by_id["D04E_OTAR_ENDPOINT"]

    dictionary_rows = [
        {
            "dictionary_id": "G771-W01",
            "whole_form": "ol",
            "portable_structural_reading_de": "kontextabhängiger Mengen-/Feldrelator; nominaler Ansatz bleibt Rivale",
            "concrete_default_de": "nach linker Menge/Wert: von/aus; vor rechter Menge: mit; sonst und",
            "confidence_level": "C1_BRANCH_AVAILABLE__C0_LEXEME",
            "evidence_de": f"{ol_left['qualified_occurrences']} konservativ lizenzierte linke Mengen-/Wertkontakte auf {ol_left['qualified_distinct_pages']} Seiten; {ol_right_exact['qualified_occurrences']} besitzen einen exakten rechten Nachbarn; {ol_full['qualified_occurrences']} Fälle auf {ol_full['qualified_distinct_pages']} Seiten erfüllen den ganzen GDT770-Zweig.",
            "counterevidence_de": "Der Branch ist jetzt testbar, aber noch nicht gegen die Nomen- und Produktmodelle neu gescort; von gegen aus bleibt ungetrennt.",
            "scope": "WHOLE_FORM_POSITIONAL_REPLACEABLE", "replaceable": 1,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        },
        {
            "dictionary_id": "G771-W02", "whole_form": "ckhy",
            "portable_structural_reading_de": "Vorgang oder Mischungskompositum; Position entscheidet lokal",
            "concrete_default_de": "nach Patient in Endlage: mischen; sonst Mischung/Aufguss offen",
            "confidence_level": "C0_SINGLE_FINAL_PATIENT",
            "evidence_de": f"Nur {ckhy['qualified_occurrences']} patientengestützter Finalfall auf {ckhy['qualified_distinct_pages']} Seite im gesamten exakten Suchraum.",
            "counterevidence_de": "Der verlangte zweite unabhängige Finalpatient fehlt; weitere Finalstellen besitzen nur Positions-, keine Patientenstütze.",
            "scope": "WHOLE_FORM_CONTEXTUAL_REPLACEABLE", "replaceable": 1,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        },
        {
            "dictionary_id": "G771-W03", "whole_form": "ols",
            "portable_structural_reading_de": "fertige oder dosierte Zubereitung; Siebvorgang bleibt Finalrival",
            "concrete_default_de": "fertige Zubereitung; in unaufgelöster Finalposition auch abseihen?",
            "confidence_level": "C0_SINGLE_COMPLETE_RIGHT_VALUE",
            "evidence_de": f"{ols['all_exact_match_occurrences']} exakte rechte Wertkontakte existieren, aber nur {ols['qualified_occurrences']} davon liegt in einer streng vollständigen Zeile.",
            "counterevidence_de": "f83r.10 und der starke Präparation-ols-Wert-Kontrast f99v.21 bleiben als genaue lokale Treffer sichtbar, aber ihre Vollzeilen enthalten drei beziehungsweise sechs offene Zellen.",
            "scope": "WHOLE_FORM_CONTEXTUAL_REPLACEABLE", "replaceable": 1,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        },
        {
            "dictionary_id": "G771-W04", "whole_form": "otar",
            "portable_structural_reading_de": "Folgen-/Feldverbinder; nominales Übergangsfeld bleibt Rivale",
            "concrete_default_de": "dann/weiter?; lokal auch Zwischenzubereitung oder bis zum Endzustand",
            "confidence_level": "C0_DISPLAY_LEAD__C0_LEXEME",
            "evidence_de": f"Das formale Folgemodell umfasst {otar_sequence['qualified_occurrences']} Fälle/{otar_sequence['qualified_distinct_pages']} Seiten und enthält die {otar_nominal['qualified_occurrences']} Nominalfälle plus zwei weitere Fälle.",
            "counterevidence_de": f"Die Mengenrelation ist prädikatsabhängig: der Nomenrivale bleibt offen, und f75r.43 liefert {otar_endpoint['qualified_occurrences']} lokalen rechten Endpunktfall ohne zweite Seite.",
            "scope": "WHOLE_FORM_WORKING_LEAD_REPLACEABLE", "replaceable": 1,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        },
    ]

    strict_context_count = sum(row["locus"] in strict_loci for row in target_rows)
    result = {
        "experiment_id": "GDT771",
        "status": "PARTIAL__461_GUARDED_LOCI__203_ADMITTED_TARGETS__195_STRICT_TARGETS__OL_LEFT_14_ON_9_PAGES_FULL_BRANCH_7_ON_6__CKHY_FINAL_PATIENT_1__OLS_RIGHT_VALUE_1__OTAR_SEQUENCE_5_NOMINAL_3_ENDPOINT_1__ZERO_CONFIRMED_LEXEMES_NO_NEW_PAGE",
        "question": "Does the already admitted complete-line cache contain the four discriminator contexts missing after GDT770?",
        "source_counts": {
            "four_target_exact_occurrences": len(target_rows),
            "explicit_selector_loci": len(selector_rows),
            "guarded_rows_selected": guard_stats["selected"],
            "guarded_rows_skipped_forbidden": guard_stats["skipped_forbidden"],
            "guarded_quantity_rows_selected": quantity_guard_stats["selected"],
            "guarded_quantity_rows_skipped_forbidden": quantity_guard_stats["skipped_forbidden"],
            "gdt734_complete_selector_loci": len(base_complete),
            "gdt770_admitted_loci": len(gdt770_loci),
            "union_admitted_loci": len(union_admitted),
            "union_admitted_target_occurrences": len(complete_context_rows),
            "strict_target_occurrences": strict_context_count,
        },
        "discriminator_decisions": {
            row["discriminator_id"]: {
                "decision": row["decision"],
                "qualified_occurrences": row["qualified_occurrences"],
                "qualified_distinct_pages": row["qualified_distinct_pages"],
                "holdout_distinct_pages": row["holdout_distinct_pages"],
            }
            for row in summary_rows
        },
        "working_interpretation": {
            "ol": "The missing left-value branch is available in seven fully typed occurrences on six pages; carry von/aus into an expanded target-masked rescore, not into confirmed plaintext.",
            "ckhy": "Only one patient-supported final case exists; keep mix operation versus mixture open.",
            "ols": "Only one complete direct-value case exists; keep finished preparation versus strain open.",
            "otar": "Sequence support strictly contains nominal support only under the GDT769 predicates and adds two cases; use dann/weiter as a display lead while the nominal rival and the single-page endpoint rival remain live.",
        },
        "otar_set_relation": {
            "sequence_occurrences": len(sequence), "nominal_occurrences": len(nominal),
            "endpoint_occurrences": len(endpoint),
            "nominal_is_strict_subset_of_sequence": sequence_contains_nominal,
            "sequence_exclusive_occurrences": len(set(sequence) - set(nominal)),
            "nominal_exclusive_occurrences": len(set(nominal) - set(sequence)),
        },
        "next_route": "GDT772 must rerender and simultaneously target-mask the seven ol full-branch occurrences and directional controls, retain patientless-final ckhy controls, and rescore the unchanged GDT770 candidate deck. The unavailable ckhy and complete ols replications remain explicit gaps for the next released four-page packet.",
        "claim_ceiling": "Context availability and replaceable whole-form renderer lead only; no confirmed lexeme, plaintext, substance identity, EVA-letter value, or component export.",
        "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "new_page_image_ocr_transcription": 0, "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0, "component_export_credit": 0,
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (
                TARGET_ATLAS, FRAME_ATLAS, INTEGRATED_READER, QUANTITY_ATLAS,
                GDT770_COHORT, GDT770_EXCLUSIONS, SPECS, BARE_VALUE_FORMS,
                LEFT_ROLE_TRANSFERS, RIGHT_ROLE_CROSSWALK, RIGHT_ROLE_TRANSFERS,
                ADDITIONAL_EXCLUSIONS,
            )
        },
    }

    if len(selector_rows) != 461 or len(complete_context_rows) != 203 or strict_context_count != 195:
        raise AssertionError("frozen core counts changed")
    expected_decisions = {
        "D01A_OL_LEFT_LICENSED": ("PASS_AVAILABLE", 14, 9),
        "D01X_OL_LEFT_RIGHT_EXACT": ("PASS_AVAILABLE", 11, 7),
        "D01B_OL_FULL_BRANCH": ("PASS_AVAILABLE", 7, 6),
        "D02_CKHY_FINAL_PATIENT": ("FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS", 1, 1),
        "D03_OLS_RIGHT_VALUE": ("FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS", 1, 1),
        "D04S_OTAR_SEQUENCE": ("PASS_AVAILABLE", 5, 4),
        "D04N_OTAR_NOMINAL": ("PASS_AVAILABLE", 3, 3),
        "D04E_OTAR_ENDPOINT": ("FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS", 1, 1),
    }
    observed_decisions = {
        row["discriminator_id"]: (
            row["decision"], row["qualified_occurrences"], row["qualified_distinct_pages"],
        )
        for row in summary_rows
    }
    if observed_decisions != expected_decisions or not sequence_contains_nominal:
        raise AssertionError(f"frozen discriminator outcome changed: {observed_decisions}")

    write_tsv(output_dir / "SELECTOR_461_GUARDED_LOCUS_INVENTORY.tsv", SELECTOR_COLUMNS, selector_rows)
    write_tsv(output_dir / "COMPLETE_203_TARGET_CONTEXT_ATLAS.tsv", CONTEXT_COLUMNS, complete_context_rows)
    write_tsv(output_dir / "OL_LEFT_BRANCH_ATLAS.tsv", OL_BRANCH_COLUMNS, ol_branch_rows)
    write_tsv(output_dir / "DISCRIMINATOR_OCCURRENCE_ATLAS.tsv", OCCURRENCE_COLUMNS, occurrence_rows)
    write_tsv(output_dir / "DISCRIMINATOR_SUMMARY.tsv", SUMMARY_COLUMNS, summary_rows)
    write_tsv(output_dir / "OTAR_IDENTITY_COVERAGE.tsv", OTAR_COLUMNS, otar_rows)
    write_tsv(output_dir / "NEXT_SCORE_DECK.tsv", DECK_COLUMNS, deck_rows)
    write_tsv(output_dir / "GDT771_4_WORKING_DICTIONARY.tsv", DICTIONARY_COLUMNS, dictionary_rows)
    write_json(output_dir / "RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
