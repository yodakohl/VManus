#!/usr/bin/env python3
"""Reveal only the ten occupants fixed by CSRMS001's published masked selection."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SELECTION = RESULTS / "csrms001_masked_recurrent_slot_selection.json"
SELECTION_TSV = RESULTS / "csrms001_masked_recurrent_slot_selection.tsv"
SELECTION_VALIDATION = RESULTS / "csrms001_masked_recurrent_slot_selection_validation.json"
SOURCE = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
SPEC = BASE / "CSRMS001_OCCUPANT_UNMASK_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT_TSV = RESULTS / "csrms001_occupant_unmask.tsv"
OUT_JSON = RESULTS / "csrms001_occupant_unmask.json"
OUT_REPORT = RESULTS / "csrms001_occupant_unmask_report.md"

FROZEN = {
    SELECTION: "e5c02c3ae7aa4376075e1e7310dad457e06bffc8384aa9deb611ff3299f3f270",
    SELECTION_TSV: "75077c41057f1dc0169add9f9f10356e5c8a676d1c6c8222301cff8dc47e4c86",
    SELECTION_VALIDATION: "bc268a3006eff3a5cfaf3a62240c5e46d28605f3fabfe05137bfdd72769835c9",
    SOURCE: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
}
FORMAL = re.compile(
    r"^([SFCL]):([^{}]+)\{adj=([^;]+);fl=([^;]+);ec=([^;]+);"
    r"o=([0-9]+);c=([0-9]+);p=([^{};]+)\}$"
)
FIELDS = (
    "occurrence_order", "record_order", "segment_id", "page", "physical_folio",
    "section", "currier", "hand", "record_length", "occupant_ordinal",
    "family_surface", "exact_sta_member_group", "zl_basic_eva_lossy",
    "it_basic_eva_lossy", "rf_basic_eva_lossy", "current_formal_expression",
    "current_formal_shell",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode()


def support(rows: list[dict[str, object]], field: str) -> list[dict[str, object]]:
    counts = Counter(str(row[field]) for row in rows)
    folios: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        folios[str(row[field])].add(int(row["physical_folio"]))
    return [
        {"value": value, "occurrences": count, "physical_folios": len(folios[value])}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].encode()))
    ]


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite CSRMS001 unmask outputs")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    validation = json.loads(SELECTION_VALIDATION.read_text(encoding="utf-8"))
    if selection["decision"] != "AUTHORIZE_ONE_EXACT_OCCUPANT_UNMASK":
        raise SystemExit("selection did not authorize unmask")
    if validation["status"] != "PASS_INDEPENDENT_FILLER_BLIND_SELECTION_RECONSTRUCTION":
        raise SystemExit("selection validation did not pass")
    if selection["selection"]["context_sha256"] != "f3f01eff8d68b91ac36c224c6965a622e817997b56ab4fca507a6041dda0ae96":
        raise SystemExit("context drift")

    with SELECTION_TSV.open(encoding="utf-8", newline="") as handle:
        frozen_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(frozen_rows) != 10:
        raise SystemExit("frozen row count drift")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source = {row["record_order"]: row for row in csv.DictReader(handle, delimiter="\t")}

    revealed: list[dict[str, object]] = []
    for frozen in frozen_rows:
        row = source[frozen["record_order"]]
        for key in ("segment_id", "page", "section", "currier", "hand"):
            if row[key] != frozen[key]:
                raise ValueError(f"frozen metadata drift: {key}")
        length = int(frozen["record_length"])
        ordinal = int(frozen["occupant_ordinal"])
        if length != 5 or ordinal != 3 or int(row["group_count"]) != length:
            raise ValueError("frozen geometry drift")
        families = row["family_expression"].split(" ")
        zl_members = row["zl_sta_expression"].split(" | ")
        it_members = row["it_sta_expression"].split(" | ")
        rf_members = row["rf_sta_expression"].split(" | ")
        evas = [row[f"{reading}_basic_eva_lossy_expression"].split(" ")
                for reading in ("zl", "it", "rf")]
        formal = row["formal_expression"].split(" | ")
        if not all(len(items) == length for items in (families, zl_members, it_members,
                                                       rf_members, *evas, formal)):
            raise ValueError("occupant expression length drift")
        index = ordinal - 1
        if not (zl_members[index] == it_members[index] == rf_members[index]):
            raise ValueError("selected occupant is not exact-member stable")
        match = FORMAL.fullmatch(formal[index])
        if not match or match.group(2) != families[index]:
            raise ValueError("formal occupant drift")
        position, _, adjacency, first_last, edge_core, opening, closing, _ = match.groups()
        current_shell = f"{position}|adj={adjacency}|fl={first_last}|ec={edge_core}|o={opening}|c={closing}"
        revealed.append({
            "occurrence_order": int(frozen["occurrence_order"]),
            "record_order": int(row["record_order"]), "segment_id": row["segment_id"],
            "page": row["page"], "physical_folio": int(frozen["physical_folio"]),
            "section": row["section"], "currier": row["currier"], "hand": row["hand"],
            "record_length": length, "occupant_ordinal": ordinal,
            "family_surface": families[index],
            "exact_sta_member_group": zl_members[index],
            "zl_basic_eva_lossy": evas[0][index], "it_basic_eva_lossy": evas[1][index],
            "rf_basic_eva_lossy": evas[2][index],
            "current_formal_expression": formal[index], "current_formal_shell": current_shell,
        })
    revealed.sort(key=lambda row: int(row["occurrence_order"]))

    family = support(revealed, "family_surface")
    member = support(revealed, "exact_sta_member_group")
    shell = support(revealed, "current_formal_shell")
    flags = {
        "FAMILY_RECURRENCE": family[0]["occurrences"] >= 5 and family[0]["physical_folios"] >= 5,
        "MEMBER_RECURRENCE": member[0]["occurrences"] >= 4 and member[0]["physical_folios"] >= 4,
        "CURRENT_SHELL_RECURRENCE": shell[0]["occurrences"] >= 7 and shell[0]["physical_folios"] >= 6,
    }
    passed = any(flags.values())
    status = "PASS_DESCRIPTIVE_RECURRENT_FILLER_CLASS" if passed else "STOP_DIVERSE_OCCUPANTS_NO_RECURRENT_FILLER_CLASS"
    decision = "RETAIN_ANONYMOUS_FORMAL_RECURRENCE_FOR_NEW_TEST" if passed else "CLOSE_RECURRENT_SLOT_FILLER_ROUTE"

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(revealed)
    result = {
        "experiment": "CSRMS001_FROZEN_SLOT_OCCUPANT_UNMASK",
        "status": status,
        "decision": decision,
        "frozen_context_sha256": selection["selection"]["context_sha256"],
        "counts": {"occupants": len(revealed), "physical_folios": 9, "sections": 2,
                   "distinct_families": len(family), "distinct_exact_members": len(member),
                   "distinct_current_shells": len(shell)},
        "family_support": family,
        "member_support": member,
        "current_shell_support": shell,
        "flags": flags,
        "thresholds": {
            "FAMILY_RECURRENCE": {"minimum_occurrences": 5, "minimum_physical_folios": 5},
            "MEMBER_RECURRENCE": {"minimum_occurrences": 4, "minimum_physical_folios": 4},
            "CURRENT_SHELL_RECURRENCE": {"minimum_occurrences": 7, "minimum_physical_folios": 6},
        },
        "inputs": {path.name: sha(path) for path in FROZEN} | {
            SPEC.name: sha(SPEC), RUNNER.name: sha(RUNNER),
        },
        "outputs": {OUT_TSV.name: sha(OUT_TSV)},
        "background_comparison_performed": False,
        "alternative_context_search_performed": False,
        "english_glosses": 0,
        "claim_ceiling": (
            "This is a descriptive reveal of ten preselected formal occupants. Even a recurrence "
            "does not establish a lexical slot, synonymy, POS, morpheme, word, sound, language, "
            "cipher operation, plaintext, meaning, or translation."
        ),
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
        "# CSRMS001 frozen-slot occupant unmask\n\n"
        f"Status: **{status}**\n\n"
        f"The one-time reveal opens exactly **{len(revealed)}** occupants fixed by the public "
        f"masked selection. They comprise **{len(family)}** family surfaces, **{len(member)}** "
        f"exact member groups, and **{len(shell)}** current formal shells. The recurrence flags "
        f"are `{json.dumps(flags, sort_keys=True, separators=(',', ':'))}`.\n\n"
        "No background comparison, alternative-context search, fitted model, or English gloss "
        "was used. The rows are anonymous formal occupants, not words or translations.\n\n"
        f"Decision: **{decision}**.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
