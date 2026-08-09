#!/usr/bin/env python3
"""Independent reconstruction of the complete opening/onset rule atlas."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
TARGET_VALIDATION = RESULTS / "source_native_opening_onset_target_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_RULE_ATLAS_SPEC.md"
BUILDER = BASE / "build_source_native_opening_onset_rule_atlas.py"
PAIR_TSV = RESULTS / "source_native_opening_onset_rule_pairs.tsv"
ONSET_TSV = RESULTS / "source_native_opening_onset_rule_states.tsv"
PRODUCTION = RESULTS / "source_native_opening_onset_rule_atlas.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_onset_rule_atlas_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_rule_atlas_validation.json"
REPORT = RESULTS / "source_native_opening_onset_rule_atlas_validation_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    TARGET_VALIDATION: "4de622cdb7e0d79466931ce6dfb49ec1d9ba062393575ffe91d9a8d1a2e4c812",
    SPEC: "ca880279bcc9cbdaf84dc4032b818dd59a2ab48e19849963fe23c5902b2e1825",
    BUILDER: "f3246b6098553c836e0bb4ee664ae8a99a20953d8b4e8dfd585e3583e9cd227a",
    PAIR_TSV: "f1537e1ce3dcb00ccc73df54a9c38fd5ae2d8353ce2e37b71fd67413327d7510",
    ONSET_TSV: "bc860d9de5fbd3f762bb18a4c4191f0f970bd4f6947d6a28079699404ccfe6ce",
    PRODUCTION: "f59debe239170cf6f3a0d52f09aeb03b87480a0748ccdd9bc7e1ff17b0617cac",
    PRODUCTION_REPORT: "ffed35a88c769af48acbae3ff8b6a85d33e842fb14a174fc605d1d365c7045f7",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
PAIR_FIELDS = ("family_remainder", "onset_triplet", "onset_consensus", "rows", "folios", "none", "da", "raw_da_fraction", "expected_da_fraction", "residual_da_fraction", "positive_cells", "zero_cells", "negative_cells", "loo_reusable", "loo_rows")
ONSET_FIELDS = ("onset_triplet", "onset_consensus", "bases", "rows", "folios", "none", "da", "raw_da_fraction", "expected_da_fraction", "residual_da_fraction", "positive_bases", "zero_bases", "negative_bases")
CLAIM = "Complete post-confirmation descriptive decomposition of the confirmed within-base onset compatibility only; no new confirmation, allomorphy, harmony, orthography, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows."


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def split(surface: str) -> tuple[str, str, int]:
    prefix = next((value for value in PREFIXES if surface.startswith(value)), "")
    return prefix or "NONE", surface[len(prefix):], len(prefix)


def ratio(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def signs(values) -> tuple[int, int, int]:
    values = list(values)
    return sum(x > 0 for x in values), sum(x == 0 for x in values), sum(x < 0 for x in values)


def tsv_bytes(fields, rows) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


def reconstruct(source_rows: list[dict], panel_rows: list[dict], quota_rows: list[dict]):
    if len(source_rows) != 26184 or len({row["consensus_group_id"] for row in source_rows}) != 26184:
        raise ValueError("source")
    if len(panel_rows) != 1207 or len({row["unit_id"] for row in panel_rows}) != 1207:
        raise ValueError("panel")
    quota = {(row["base_id"], row["physical_folio"]): (int(row["da_count"]), int(row["total_count"])) for row in quota_rows if int(row["none_count"]) and int(row["da_count"])}
    if len(quota_rows) != 1763 or len(quota) != 197:
        raise ValueError("quotas")
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, remainder, cut = split(row["family_surface"])
        if state not in {"NONE", "DA"} or not remainder:
            continue
        sequences = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if any(len(sequence) != int(row["symbol_count"]) for sequence in sequences) or any(len(sequence[cut:]) != len(remainder) for sequence in sequences):
            raise ValueError("members")
        onset = tuple(sequence[cut] for sequence in sequences)
        identity = opaque("U", row["consensus_group_id"])
        if identity in hidden:
            raise ValueError("duplicate hidden")
        hidden[identity] = state, remainder, opaque("B", remainder), onset, opaque("O", "|".join(onset))
    joined = []
    cells = defaultdict(list)
    for row in panel_rows:
        if row["unit_id"] not in hidden:
            raise ValueError("join")
        state, remainder, base_id, onset, onset_id = hidden[row["unit_id"]]
        if base_id != row["base_id"] or onset_id != row["onset_id"] or row["onset_consensus"] != str(int(len(set(onset)) == 1)):
            raise ValueError("binding")
        record = {"state": state, "remainder": remainder, "base": base_id, "onset": onset, "folio": row["physical_folio"]}
        joined.append(record)
        cells[(base_id, row["physical_folio"])].append(record)
    if set(cells) != set(quota) or Counter(row["state"] for row in joined) != Counter({"NONE": 892, "DA": 315}):
        raise ValueError("geometry")
    for key, records in cells.items():
        if len(records) != quota[key][1] or sum(row["state"] == "DA" for row in records) != quota[key][0]:
            raise ValueError("quota drift")
    pairs, onsets = defaultdict(list), defaultdict(list)
    for row in joined:
        pairs[(row["remainder"], row["onset"])].append(row)
        onsets[row["onset"]].append(row)
    if len(pairs) != 95 or len(onsets) != 25 or len({row["remainder"] for row in joined}) != 44:
        raise ValueError("inventory")
    pair_rows, residuals = [], {}
    for key in sorted(pairs):
        records = pairs[key]
        grouped = defaultdict(list)
        for row in records:
            grouped[(row["base"], row["folio"])].append(row)
        expected, cell_values = Fraction(0), []
        for cell, values in grouped.items():
            local_expected = Fraction(len(values) * quota[cell][0], quota[cell][1])
            expected += local_expected
            cell_values.append(Fraction(sum(row["state"] == "DA" for row in values)) - local_expected)
        da = sum(row["state"] == "DA" for row in records)
        residual = Fraction(da) - expected
        residuals[key] = residual
        positive, zero, negative = signs(cell_values)
        folios = len({row["folio"] for row in records})
        pair_rows.append({
            "family_remainder": key[0], "onset_triplet": "/".join(key[1]),
            "onset_consensus": str(int(len(set(key[1])) == 1)), "rows": str(len(records)),
            "folios": str(folios), "none": str(len(records) - da), "da": str(da),
            "raw_da_fraction": ratio(Fraction(da, len(records))),
            "expected_da_fraction": ratio(expected), "residual_da_fraction": ratio(residual),
            "positive_cells": str(positive), "zero_cells": str(zero), "negative_cells": str(negative),
            "loo_reusable": str(int(folios >= 2)), "loo_rows": str(len(records) if folios >= 2 else 0),
        })
    onset_rows = []
    for onset in sorted(onsets):
        records = onsets[onset]
        expected = sum((Fraction(quota[(row["base"], row["folio"])][0], quota[(row["base"], row["folio"])][1]) for row in records), Fraction(0))
        da = sum(row["state"] == "DA" for row in records)
        base_residuals = defaultdict(Fraction)
        for base in {row["remainder"] for row in records}:
            base_residuals[base] += residuals[(base, onset)]
        positive, zero, negative = signs(base_residuals.values())
        onset_rows.append({
            "onset_triplet": "/".join(onset), "onset_consensus": str(int(len(set(onset)) == 1)),
            "bases": str(len(base_residuals)), "rows": str(len(records)),
            "folios": str(len({row["folio"] for row in records})), "none": str(len(records) - da), "da": str(da),
            "raw_da_fraction": ratio(Fraction(da, len(records))), "expected_da_fraction": ratio(expected),
            "residual_da_fraction": ratio(Fraction(da) - expected), "positive_bases": str(positive),
            "zero_bases": str(zero), "negative_bases": str(negative),
        })
    base_directions = defaultdict(set)
    for (base, _), value in residuals.items():
        if value:
            base_directions[base].add(1 if value > 0 else -1)
    sign_summary = signs(residuals.values())
    strongest = sorted(pairs, key=lambda key: (-abs(residuals[key]), key[0], key[1]))[:12]
    strongest_rows = [{"family_remainder": base, "onset_triplet": "/".join(onset), "residual_da_fraction": ratio(residuals[(base, onset)])} for base, onset in strongest]
    summary = {
        "rows": len(joined), "quota_cells": len(cells), "family_remainders": 44,
        "base_onset_pairs": len(pair_rows), "onset_triplets": len(onset_rows),
        "none_rows": 892, "da_rows": 315,
        "loo_reusable_rows": sum(int(row["loo_rows"]) for row in pair_rows),
        "positive_pair_residuals": sign_summary[0], "zero_pair_residuals": sign_summary[1], "negative_pair_residuals": sign_summary[2],
        "bases_with_both_residual_directions": sum(value == {1, -1} for value in base_directions.values()),
        "deterministic_pair_states": sum(int(row["da"]) in {0, int(row["rows"])} for row in pair_rows),
        "onsets_shared_across_bases": sum(int(row["bases"]) >= 2 for row in onset_rows),
    }
    return pair_rows, onset_rows, summary, strongest_rows, cells, quota


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures, checks = [], 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, "hash:" + path.name)
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    with PANEL.open(encoding="utf-8", newline="") as handle:
        panel = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quotas = list(csv.DictReader(handle, delimiter="\t"))
    pairs, onsets, summary, strongest, cells, quota = reconstruct(source, panel, quotas)
    check(tsv_bytes(PAIR_FIELDS, pairs) == PAIR_TSV.read_bytes(), "pair bytes")
    check(tsv_bytes(ONSET_FIELDS, onsets) == ONSET_TSV.read_bytes(), "onset bytes")
    production = json.loads(PRODUCTION.read_text())
    check(production["summary"] == summary, "summary")
    check(production["strongest_absolute_pair_residuals"] == strongest, "strongest")
    gates = {
        "exact_1207_rows_197_cells_44_bases": summary["rows"] == 1207 and summary["quota_cells"] == 197 and summary["family_remainders"] == 44,
        "exact_892_NONE_315_DA": summary["none_rows"] == 892 and summary["da_rows"] == 315,
        "exact_95_pairs_25_onsets": summary["base_onset_pairs"] == 95 and summary["onset_triplets"] == 25,
        "exact_1141_loo_reusable_rows": summary["loo_reusable_rows"] == 1141,
        "all_quotas_exact": all(len(records) == quota[key][1] and sum(record["state"] == "DA" for record in records) == quota[key][0] for key, records in cells.items()),
        "no_event_identity_output": all("unit" not in field and "locus" not in field and "page" not in field for field in (*PAIR_FIELDS, *ONSET_FIELDS)),
    }
    check(production["gates"] == gates and all(gates.values()), "gates")
    check(production["pair_tsv_sha256"] == sha(PAIR_TSV) and production["onset_tsv_sha256"] == sha(ONSET_TSV), "bindings")
    check(production["inputs"] == {path.name: sha(path) for path in list(FROZEN)[:6]}, "inputs")
    check(production["status"] == "PASS_COMPLETE_POST_CONFIRMATION_RULE_ATLAS" and production["decision"] == "USE_COMPLETE_TABLE_FOR_MECHANISM_DESIGN_ONLY", "decision")
    check(production["claim_ceiling"] == CLAIM and production["unit_locus_page_identities_stored"] == production["english_glosses"] == 0, "ceiling")
    strongest_text = ", ".join(f"`{row['family_remainder']} | {row['onset_triplet']}` ({row['residual_da_fraction']})" for row in strongest)
    expected_report = f"""# Complete opening/onset rule atlas

Status: **{production['status']}**

All **{summary['rows']:,}** frozen rows decompose into
**{summary['base_onset_pairs']}** exact base/onset states and
**{summary['onset_triplets']}** onset triplets. Relative to exact base/folio
quotas, pair residuals are positive/zero/negative in
**{summary['positive_pair_residuals']} / {summary['zero_pair_residuals']} /
{summary['negative_pair_residuals']}** states; **{summary['bases_with_both_residual_directions']}**
bases contain both directions. **{summary['deterministic_pair_states']}** pair
states have raw `DA` rate zero or one, without a minimum-support claim.

The twelve largest absolute quota residuals are: {strongest_text}.

This is complete descriptive localization of the already confirmed formal
compatibility. It supplies no allomorphy, harmony, morphology, meaning,
plaintext, or translation.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")
    mutations = {}
    for name, source_case, panel_case in (
        ("missing_source", source[:-1], panel),
        ("missing_panel", source, panel[:-1]),
        ("duplicate_panel", source, panel + [panel[0]]),
    ):
        try:
            reconstruct(source_case, panel_case, quotas)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    wrong = [dict(row) for row in panel]
    wrong[0]["base_id"] = "B" + "0" * 16
    try:
        reconstruct(source, wrong, quotas)
    except ValueError:
        mutations["wrong_binding"] = True
    else:
        mutations["wrong_binding"] = False
    changed = [dict(row) for row in quotas]
    changed[0]["da_count"] = str(int(changed[0]["da_count"]) + 1)
    try:
        reconstruct(source, panel, changed)
    except ValueError:
        mutations["quota_drift"] = True
    else:
        mutations["quota_drift"] = False
    check(all(mutations.values()) and len(mutations) == 5, "mutations")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_RULE_ATLAS_VALIDATION",
        "status": "PASS_INDEPENDENT_COMPLETE_RULE_ATLAS_RECONSTRUCTION",
        "checks": checks, "failures": [], "summary": summary, "gates": gates,
        "mutations": mutations, "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR), "unit_locus_page_identities_stored": 0,
        "english_glosses": 0, "claim_ceiling": CLAIM,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening/onset rule atlas validation

Status: **{result['status']}**

Independent code reconstructs all 1,207 source joins, 197 quotas, 95 pair
rows, 25 onset rows, exact TSV and report bytes, every summary/gate, and five
mutations in **{checks}** checks.

This validates complete descriptive localization of the prior confirmation
only. It supplies no allomorphy, harmony, morphology, meaning, plaintext, or
translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()
