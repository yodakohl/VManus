#!/usr/bin/env python3
"""Build the score-blind, source-native Q20 OPEN/BODY panel."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BINDING = ROOT / "experiments/semantic_assumptions/star_morphology_entry/anonymous_unit_binding.tsv"
ALIGNMENT = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
OUT = ROOT / "q20ob001_source_panel.tsv"
AUDIT = ROOT / "q20ob001_source_panel_audit.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    bindings = read_tsv(BINDING)
    assert len(bindings) == 170
    assert len({row["unit_id"] for row in bindings}) == 170
    assert all(not row["page"].startswith("f84r") for row in bindings)
    wanted_loci = {locus for row in bindings for locus in row["line_loci"].split("|")}

    aligned: dict[str, dict[str, list[dict[str, str]]]] = {
        edition: defaultdict(list) for edition in EDITIONS
    }
    # Route on locus before retaining formal fields. No non-panel or f84r row survives.
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for source in reader:
            locus = source["locus"]
            if locus not in wanted_loci:
                continue
            assert not locus.startswith("f84r")
            edition = source["edition"]
            assert edition in aligned
            aligned[edition][locus].append(source)
    for edition in EDITIONS:
        assert set(aligned[edition]) == wanted_loci
        for locus in wanted_loci:
            aligned[edition][locus].sort(key=lambda row: int(row["source_group_index"]))
            indices = [int(row["source_group_index"]) for row in aligned[edition][locus]]
            assert indices == list(range(1, len(indices) + 1))

    output: list[dict[str, object]] = []
    per_folio: dict[str, int] = defaultdict(int)
    for binding in bindings:
        line_loci = binding["line_loci"].split("|")
        assert len(line_loci) >= 2 and line_loci[0] == binding["locus"]
        per_folio[binding["physical_folio"]] += 1
        for edition in EDITIONS:
            lines = [aligned[edition][locus] for locus in line_loci]
            open_groups = lines[0]
            body_lines = lines[1:]
            open_members = [[code for code in row["primary_sta_codes"].split()] for row in open_groups]
            body_members = [
                [[code for code in row["primary_sta_codes"].split()] for row in line]
                for line in body_lines
            ]
            open_families = [list(row["primary_sta_families"]) for row in open_groups]
            body_families = [[list(row["primary_sta_families"]) for row in line] for line in body_lines]
            assert all(len(family) == len(member) for family, member in zip(open_families, open_members, strict=True))
            assert all(
                len(family) == len(member)
                for family_line, member_line in zip(body_families, body_members, strict=True)
                for family, member in zip(family_line, member_line, strict=True)
            )
            output.append(
                {
                    "unit_id": binding["unit_id"],
                    "page": binding["page"],
                    "physical_folio": binding["physical_folio"],
                    "star_ordinal": binding["star_ordinal"],
                    "open_locus": binding["locus"],
                    "body_line_loci": "|".join(line_loci[1:]),
                    "edition": edition,
                    "record_line_count": len(line_loci),
                    "open_group_count": len(open_groups),
                    "open_member_count": sum(map(len, open_members)),
                    "body_line_count": len(body_lines),
                    "body_group_count": sum(map(len, body_lines)),
                    "body_member_count": sum(len(group) for line in body_members for group in line),
                    "open_member_groups_json": json.dumps(open_members, separators=(",", ":")),
                    "body_member_lines_json": json.dumps(body_members, separators=(",", ":")),
                    "open_family_groups_json": json.dumps(open_families, separators=(",", ":")),
                    "body_family_lines_json": json.dumps(body_families, separators=(",", ":")),
                }
            )
    fields = list(output[0])
    write_tsv(OUT, output, fields)
    member_inventories = {
        edition: sorted(
            {
                code
                for row in output
                if row["edition"] == edition
                for group in json.loads(str(row["open_member_groups_json"]))
                for code in group
            }
            | {
                code
                for row in output
                if row["edition"] == edition
                for line in json.loads(str(row["body_member_lines_json"]))
                for group in line
                for code in group
            }
        )
        for edition in EDITIONS
    }
    audit = {
        "schema": "Q20OB001_SOURCE_PANEL_AUDIT_V1",
        "status": "PASS_SCORE_BLIND_SOURCE_NATIVE_OPEN_BODY_PANEL",
        "units": len(bindings),
        "rows": len(output),
        "editions": list(EDITIONS),
        "physical_folios": sorted(per_folio),
        "units_per_physical_folio": dict(sorted(per_folio.items())),
        "record_line_count_distribution": dict(
            sorted(Counter(len(row["line_loci"].split("|")) for row in bindings).items())
        ),
        "member_inventories": member_inventories,
        "f84r_rows_retained": 0,
        "semantic_fields": False,
        "pairing_scores_computed": False,
        "inputs": {BINDING.relative_to(ROOT).as_posix(): sha(BINDING), ALIGNMENT.relative_to(ROOT).as_posix(): sha(ALIGNMENT)},
        "output": {OUT.name: sha(OUT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "claim_ceiling": "Source-native physical OPEN/BODY spans only; no semantic label, meaning, language, plaintext, or translation.",
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "units": len(bindings), "rows": len(output), "folios": len(per_folio)}, indent=2))


if __name__ == "__main__":
    main()
