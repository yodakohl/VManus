#!/usr/bin/env python3
"""Run the frozen PRC001 exact dark-root marker target once."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "PRC001_DARK_ROOT_MARKER_TARGET_SPEC.md"
PANEL = RESULTS / "pharma_root_color_native_visual_ownership.tsv"
PANEL_VALIDATION = RESULTS / "pharma_root_color_native_visual_ownership_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
GROUPS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
OUT = RESULTS / "prc001_dark_root_marker_target.json"
REPORT = RESULTS / "prc001_dark_root_marker_target_report.md"

EXPECTED = {
    SPEC: "ebb43c0f45fefa91f01400ab646de409741e64d34f1c7b763f708bae9952253e",
    PANEL: "eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b",
    PANEL_VALIDATION: "2eb90320045ac0742294f649f73ec4beff00028ca7e94523490af3535d6da03c",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    GROUPS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def canonical_sha(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def group_features(row: dict[str, str]) -> set[str]:
    family = row["family_surface"]
    features: set[str] = set()
    for n in range(1, min(3, len(family)) + 1):
        features.update(
            f"F:N:{n}:{family[start:start+n]}"
            for start in range(len(family) - n + 1)
        )
        features.add(f"F:P:{n}:{family[:n]}")
        features.add(f"F:S:{n}:{family[-n:]}")
    features.add(f"F:W:{family}")

    codes = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
    if codes[0] == codes[1] == codes[2]:
        member = codes[0]
        for n in range(1, min(3, len(member)) + 1):
            features.update(
                f"M:N:{n}:{' '.join(member[start:start+n])}"
                for start in range(len(member) - n + 1)
            )
            features.add(f"M:P:{n}:{' '.join(member[:n])}")
            features.add(f"M:S:{n}:{' '.join(member[-n:])}")
        features.add(f"M:W:{' '.join(member)}")
    return features


def build_label_features(
    panel_rows: list[dict[str, str]], group_lookup: dict[str, list[dict[str, str]]]
) -> tuple[dict[str, set[str]], list[str]]:
    out: dict[str, set[str]] = {}
    problems: list[str] = []
    for panel in panel_rows:
        source_id = panel["source_record_id"]
        locus = panel["mapped_locus"]
        rows = sorted(group_lookup.get(locus, []), key=lambda row: int(row["consensus_group_index"]))
        if not rows:
            problems.append(f"{source_id}:MISSING_LOCUS")
            continue
        counts = {int(row["consensus_group_count"]) for row in rows}
        expected_indices = list(range(1, len(rows) + 1))
        actual_indices = [int(row["consensus_group_index"]) for row in rows]
        if (
            {row["locus"] for row in rows} != {locus}
            or {row["page"] for row in rows} != {panel["source_page"]}
            or any(row["kind"] != "L" or row["grammar_scope"] != "LABEL" for row in rows)
            or any(row["strict_zero_alternative"] != "1" for row in rows)
            or counts != {len(rows)}
            or actual_indices != expected_indices
        ):
            problems.append(f"{source_id}:STRUCTURE")
            continue
        current: set[str] = set()
        bad = False
        for row in rows:
            family = row["family_surface"]
            code_fields = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
            if not family or any(not codes or "".join(code[0] for code in codes) != family for codes in code_fields):
                bad = True
                break
            current.update(group_features(row))
        if bad or not current:
            problems.append(f"{source_id}:CODE_FAMILY")
            continue
        out[source_id] = current
    return out, problems


def delta(feature: str, rows: list[dict[str, str]], features: dict[str, set[str]], dark_ids: set[str]) -> float:
    dark = [int(feature in features[row["source_record_id"]]) for row in rows if row["source_record_id"] in dark_ids]
    light = [int(feature in features[row["source_record_id"]]) for row in rows if row["source_record_id"] not in dark_ids]
    if not dark or not light:
        raise AssertionError("empty state partition")
    return sum(dark) / len(dark) - sum(light) / len(light)


def feature_scores(
    candidates: list[str], by_folio: dict[str, list[dict[str, str]]],
    features: dict[str, set[str]], dark_ids: set[str],
) -> list[tuple[float, float, str, float, float]]:
    scored = []
    for feature in candidates:
        d89 = delta(feature, by_folio["f89"], features, dark_ids)
        d100 = delta(feature, by_folio["f100"], features, dark_ids)
        scored.append((min(d89, d100), (d89 + d100) / 2, feature, d89, d100))
    return scored


def winner(
    candidates: list[str], by_folio: dict[str, list[dict[str, str]]],
    features: dict[str, set[str]], dark_ids: set[str],
) -> tuple[float, float, str, float, float]:
    scored = feature_scores(candidates, by_folio, features, dark_ids)
    return sorted(scored, key=lambda item: (-item[0], -item[1], item[2].encode()))[0]


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite of target outputs")
    for path, expected in EXPECTED.items():
        if digest(path) != expected:
            raise SystemExit(f"input hash mismatch: {path}")
    panel_validation = json.loads(PANEL_VALIDATION.read_text(encoding="utf-8"))
    group_validation = json.loads(GROUPS_VALIDATION.read_text(encoding="utf-8"))
    if panel_validation["status"] != "PASS_SOURCE_IMAGE_BINDINGS_AND_GATE_RECONSTRUCTION":
        raise SystemExit("ownership validation not passed")
    if not str(group_validation["status"]).startswith("PASS"):
        raise SystemExit("consensus validation not passed")

    panel = [row for row in table(PANEL) if row["eligible"] == "1"]
    mixed = [row for row in panel if row["physical_folio"] in {"f89", "f100"}]
    transfer = [row for row in panel if row["physical_folio"] == "f102"]
    by_folio = {folio: [row for row in mixed if row["physical_folio"] == folio] for folio in ("f89", "f100")}
    margins = {
        folio: Counter(row["root_state"] for row in rows)
        for folio, rows in by_folio.items()
    }

    group_lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in table(GROUPS):
        group_lookup[row["locus"]].append(row)

    # Build and filter discovery features without using the state labels.
    discovery_features, problems = build_label_features(mixed, group_lookup)
    all_discovery = sorted(set().union(*discovery_features.values()), key=lambda value: value.encode()) if discovery_features else []
    candidates = []
    for feature in all_discovery:
        total = sum(feature in discovery_features[row["source_record_id"]] for row in mixed)
        if total < 3:
            continue
        if all(
            0 < sum(feature in discovery_features[row["source_record_id"]] for row in by_folio[folio]) < len(by_folio[folio])
            for folio in ("f89", "f100")
        ):
            candidates.append(feature)

    capacity = {
        "eligible_labels": len(panel),
        "discovery_labels": len(mixed),
        "transfer_labels": len(transfer),
        "discovery_margins": {folio: dict(sorted(counts.items())) for folio, counts in margins.items()},
        "transfer_states": dict(sorted(Counter(row["root_state"] for row in transfer).items())),
        "reconstruction_problems": problems,
        "unfiltered_features": len(all_discovery),
        "filtered_features": len(candidates),
        "filtered_feature_sha256": canonical_sha(candidates) if candidates else None,
        "exact_worlds": 1540,
    }
    capacity_pass = (
        len(panel) == 21
        and len(mixed) == 19
        and len(transfer) == 2
        and margins == {"f89": Counter({"LIGHT": 9, "DARK": 2}), "f100": Counter({"LIGHT": 6, "DARK": 2})}
        and Counter(row["root_state"] for row in transfer) == {"DARK": 2}
        and not problems
        and len(discovery_features) == 19
        and len(candidates) >= 4
        and len(list(itertools.combinations(range(11), 2))) * len(list(itertools.combinations(range(8), 2))) == 1540
    )
    if not capacity_pass:
        result = {
            "experiment": "PRC001_DARK_ROOT_MARKER_TARGET",
            "status": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "decision": "STOP_UNPOWERED_BEFORE_STATE_SCORE",
            "inputs": {str(path.relative_to(BASE)): expected for path, expected in EXPECTED.items()},
            "capacity": capacity,
            "gates": {"capacity": False},
            "claim_ceiling": "No formal marker or semantic result was scored.",
        }
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT.write_text("# PRC001 dark-root marker target\n\nStatus: **STOP_UNPOWERED_BEFORE_STATE_SCORE**\n", encoding="utf-8")
        return

    observed_dark = {row["source_record_id"] for row in mixed if row["root_state"] == "DARK"}
    observed = winner(candidates, by_folio, discovery_features, observed_dark)
    observed_score, observed_mean, winning_feature, d89, d100 = observed

    ids89 = [row["source_record_id"] for row in by_folio["f89"]]
    ids100 = [row["source_record_id"] for row in by_folio["f100"]]
    null_maxima: list[float] = []
    for dark89 in itertools.combinations(ids89, 2):
        for dark100 in itertools.combinations(ids100, 2):
            world_dark = set(dark89) | set(dark100)
            null_maxima.append(winner(candidates, by_folio, discovery_features, world_dark)[0])
    assert len(null_maxima) == 1540
    exact_p = sum(value >= observed_score for value in null_maxima) / len(null_maxima)

    # The winner is now fixed. Only now open the f102 formal features.
    transfer_features, transfer_problems = build_label_features(transfer, group_lookup)
    transfer_ids = [row["source_record_id"] for row in transfer]
    transfer_presence = {
        source_id: winning_feature in transfer_features.get(source_id, set())
        for source_id in transfer_ids
    }

    deletion = {}
    for source_id in sorted(observed_dark):
        reduced_dark = observed_dark - {source_id}
        reduced_by_folio = {
            folio: [row for row in rows if row["source_record_id"] != source_id]
            for folio, rows in by_folio.items()
        }
        deletion[source_id] = {
            "f89_delta": delta(winning_feature, reduced_by_folio["f89"], discovery_features, reduced_dark),
            "f100_delta": delta(winning_feature, reduced_by_folio["f100"], discovery_features, reduced_dark),
        }

    gates = {
        "capacity": True,
        "exact_max_feature_p_at_most_0_01": exact_p <= 0.01,
        "winning_score_at_least_0_50": observed_score >= 0.50,
        "both_discovery_folio_deltas_at_least_0_50": min(d89, d100) >= 0.50,
        "winner_present_in_both_f102_dark_labels": not transfer_problems and all(transfer_presence.values()),
        "all_discovery_dark_deletions_retain_both_deltas_at_least_0_50": all(
            min(values.values()) >= 0.50 for values in deletion.values()
        ),
        "all_reading_consensus_reconstruction": not problems and not transfer_problems,
    }
    passed = all(gates.values())
    decision = (
        "PASS_RECURRENT_FORMAL_FEATURE_ASSOCIATED_WITH_HUMAN_DARK_ROOT_STATE"
        if passed else
        "FINAL_NONCONFIRMATION_NO_RECURRENT_DARK_ASSOCIATED_FORMAL_MARKER"
    )
    result = {
        "experiment": "PRC001_DARK_ROOT_MARKER_TARGET",
        "status": decision,
        "decision": decision,
        "inputs": {str(path.relative_to(BASE)): expected for path, expected in EXPECTED.items()},
        "capacity": capacity,
        "target": {
            "winning_feature": winning_feature,
            "winning_score": observed_score,
            "winning_mean_delta": observed_mean,
            "discovery_folio_deltas": {"f89": d89, "f100": d100},
            "exact_p": exact_p,
            "inclusive_tail_count": sum(value >= observed_score for value in null_maxima),
            "null_worlds": len(null_maxima),
            "null_maxima": null_maxima,
            "null_maxima_sha256": hashlib.sha256(json.dumps(null_maxima, separators=(",", ":")).encode()).hexdigest(),
            "transfer_presence": transfer_presence,
            "transfer_reconstruction_problems": transfer_problems,
            "dark_deletion_deltas": deletion,
        },
        "gates": gates,
        "claim_ceiling": (
            "A pass would establish only that one frozen source-native formal feature is associated "
            "with the inherited human DARK-root drawing state across this small panel. It would not "
            "establish the word DARK or ROOT, a plant name, sound, language, cipher, plaintext, "
            "meaning, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# PRC001 dark-root marker target\n\n"
        f"Status: **{decision}**\n\n"
        f"The target-blind filter retained **{len(candidates)}** formal features. The frozen "
        f"winner is `{winning_feature}` with minimum cross-folio delta **{observed_score:.6f}** "
        f"(f89={d89:.6f}, f100={d100:.6f}); its exact max-feature p-value is "
        f"**{exact_p:.6f}** ({sum(value >= observed_score for value in null_maxima)}/1540).\n\n"
        f"Transfer presence on the two untouched f102 DARK labels is "
        f"`{json.dumps(transfer_presence, sort_keys=True)}`.\n\n"
        f"Decision: **{decision}**.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
