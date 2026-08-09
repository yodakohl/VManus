#!/usr/bin/env python3
"""Post-hoc `ed`-resolved sensitivity for completed F69C001."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
ORIGINAL = HERE / "TARGET_RESULT.json"
OUTPUT = RESULTS / "f69c001_ed_resolved_sensitivity.json"
RUNNER_PATH = HERE / "run_f69c001_target.py"


def load_frozen_runner():
    spec = importlib.util.spec_from_file_location("f69c001_frozen_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("sensitivity artifact already exists; rerun forbidden")
    frozen = load_frozen_runner()
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    if original["decision"] != "TARGET_NONCONFIRMATION":
        raise AssertionError("unexpected frozen target decision")

    bound, provenance = frozen.validate_binding()
    resolved = dict(bound)
    resolved["IT2a"] = tuple(
        "ed" if index == 4 else surface
        for index, surface in enumerate(bound["IT2a"])
    )
    if resolved["IT2a"] != bound["ZL3b"]:
        raise AssertionError("ed resolution changed more than the disputed slot")

    tables = {
        reading: frozen.prose_tables(path)
        for reading, path in frozen.SOURCES.items()
    }
    primary, private = frozen.score_panel(resolved, tables)

    deletions = []
    for omitted in range(6):
        reduced = {
            reading: tuple(surface for index, surface in enumerate(chunks)
                           if index != omitted)
            for reading, chunks in resolved.items()
        }
        result, _ = frozen.score_panel(reduced, tables)
        deletions.append({
            "omitted_slot": omitted + 1,
            "omitted_locus": frozen.SLOTS[omitted][0],
            "combined_target_inclusive_rank": result["combined_target_inclusive_rank"],
            "reading_target_inclusive_ranks": result["reading_target_inclusive_ranks"],
            "combined_orbit_score_sha256": result["combined_orbit_score_sha256"],
        })

    shifted = dict(resolved)
    shifted["IT2a"] = resolved["IT2a"][1:] + resolved["IT2a"][:1]
    shifted_result, _ = frozen.score_panel(shifted, tables)

    truth = private["target_orbit"]
    alternatives = [
        orbit for orbit in sorted(private["combined_orbits"]) if orbit != truth
    ]
    fixture_index = int.from_bytes(
        hashlib.sha256(frozen.RANDOM_FIXTURE_SEED).digest()[:8], "big"
    ) % len(alternatives)
    chosen = alternatives[fixture_index]
    random_rank = frozen.rank_of(private["combined_orbits"], chosen)

    deletion_ranks = [row["combined_target_inclusive_rank"] for row in deletions]
    gates = {
        "unique_combined_rank1_of_60": primary["combined_target_inclusive_rank"] == 1,
        "all_individual_reading_ranks_at_most_3": all(
            rank <= 3 for rank in primary["reading_target_inclusive_ranks"].values()
        ),
        "at_least_five_deletion_ranks_at_most_2": sum(
            rank <= 2 for rank in deletion_ranks
        ) >= 5,
        "no_deletion_rank_worse_than_4": max(deletion_ranks) <= 4,
        "misaligned_reading_fixture_rejects": (
            shifted_result["combined_target_inclusive_rank"] > 1
        ),
        "deterministic_non_target_orbit_fixture_rejects": random_rank > 1,
    }
    payload = {
        "experiment": "F69C001_ED_RESOLVED_POSTHOC_SENSITIVITY",
        "status": "POSTHOC_DIAGNOSTIC_NOT_CONFIRMATION",
        "provenance_binding_sha256": provenance["binding_sha256"],
        "change": {
            "reading": "IT2a", "slot": 5, "locus": "f69r.49",
            "stored_surface": "em", "qc_surface": "ed",
            "all_other_surfaces_unchanged": True,
        },
        "original": {
            "combined_rank": original["primary"]["combined_target_inclusive_rank"],
            "individual_ranks": original["primary"]["reading_target_inclusive_ranks"],
            "deletion_ranks": [
                row["combined_target_inclusive_rank"] for row in original["deletions"]
            ],
            "gates": original["gates"],
            "decision": original["decision"],
        },
        "resolved_primary": primary,
        "resolved_deletions": deletions,
        "resolved_fixtures": {
            "misaligned_reading_target_rank": shifted_result["combined_target_inclusive_rank"],
            "deterministic_non_target_index": fixture_index,
            "deterministic_non_target_rank": random_rank,
        },
        "resolved_gates": gates,
        "all_resolved_computational_gates_pass": all(gates.values()),
        "claim_ceiling": (
            "post-hoc sensitivity to one human-adjudicated transcription only; "
            "cannot upgrade F69C001 or establish start, handedness, sound, word, "
            "root, lexeme, language, plaintext, direction name, or translation"
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    report = [
        "# F69C001 `ed`-resolved post-hoc sensitivity",
        "",
        "Status: **POST-HOC DIAGNOSTIC — NOT CONFIRMATION**",
        "",
        "Only IT2a f69r.49 was changed from its stored `em` alternative to the",
        "human-QC-preferred physical reading `ed`; all corpora and every other",
        "input, model, null, and gate remained unchanged.",
        "",
        f"- Resolved combined rank: {primary['combined_target_inclusive_rank']}/60",
        "- Resolved individual ranks: " + ", ".join(
            f"{reading} {rank}/60" for reading, rank in
            primary["reading_target_inclusive_ranks"].items()
        ),
        f"- Resolved deletion ranks: {', '.join(map(str, deletion_ranks))}/12",
        f"- Resolved computational gates: {sum(gates.values())}/{len(gates)}",
        "",
        "This calculation was prompted by the exposed target result. Even if",
        "every diagnostic gate passes, it cannot retroactively confirm F69C001",
        "or identify a joined orientation, start, handedness, sound, word, root,",
        "lexeme, language, plaintext, direction name, or translation.",
        "",
    ]
    (RESULTS / "f69c001_ed_resolved_sensitivity_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": payload["status"],
        "combined_rank": primary["combined_target_inclusive_rank"],
        "individual_ranks": primary["reading_target_inclusive_ranks"],
        "deletion_ranks": deletion_ranks,
        "gates": gates,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
