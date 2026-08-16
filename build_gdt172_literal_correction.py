#!/usr/bin/env python3
"""Replace only GDT171's literal payload with the unchanged source form."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent
OLD_OBS = R / "gdt171_observation_corpus.json.gz"
OLD_ORACLE = R / "gdt171_sealed_oracle.json.gz"
OLD_FREEZE = R / "gdt171_source_observation_oracle_freeze.json"
LOOKUP = R / "gdt171_sealed_lexical_lookup.tsv"
MANIFEST = R / "gdt171_register_folio_manifest.tsv"
SCHEMA = R / "gdt171_observation_schema.tsv"
METHOD = R / "GDT172_LITERAL_ESCAPE_CORRECTION_METHOD.md"
OBS = R / "gdt172_observation_corpus.json.gz"
ORACLE = R / "gdt172_sealed_oracle.json.gz"
AUDIT = R / "gdt172_literal_change_audit.tsv"
FREEZE = R / "gdt172_source_literal_correction_freeze.json"

SYSTEM_MAP = {
    "SYSTEM_A_V2": "SYSTEM_A_V3_UNCHANGED_LITERAL",
    "SYSTEM_B_V2": "SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle:
        return json.load(handle)


def write_gzip(path: Path, payload) -> None:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle:
            handle.write(raw)


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    old_obs_payload, old_oracle_payload = load(OLD_OBS), load(OLD_ORACLE)
    old_obs, old_oracle = old_obs_payload["rows"], old_oracle_payload["rows"]
    assert old_obs_payload["schema"] == "GDT171_STRICT_OBSERVATION_CORPUS_V1"
    assert old_oracle_payload["schema"] == "GDT171_SEALED_ORACLE_V1"
    assert len(old_obs) == len(old_oracle) == 30428
    old_truth = {x["observation_id"]: x for x in old_oracle}
    assert len(old_truth) == len(old_oracle)

    new_obs: list[dict] = []
    new_oracle: list[dict] = []
    counts = Counter()
    lengths = Counter()
    by_world = Counter()
    for observation in old_obs:
        truth = old_truth[observation["observation_id"]]
        obs2 = dict(observation)
        truth2 = dict(truth)
        truth2["system"] = SYSTEM_MAP[truth["system"]]
        status = truth["lexical_status"]
        counts[status] += 1
        by_world[observation["world_view"], status] += 1
        if status == "FREQUENT_LEXICAL_ID":
            assert obs2["surface_group"] == observation["surface_group"]
            counts["frequent_surface_changed"] += obs2["surface_group"] != observation["surface_group"]
        else:
            assert status == "LITERAL_ESCAPE" and truth["true_literal_escape"] == "w"
            old_surface = observation["surface_group"]
            truth2["canonical_host"] = truth["source_form"]
            truth2["rendered_host"] = truth["source_form"]
            truth2["scribe_render_rule"] = "IDENTITY_UNCHANGED_SOURCE_GRAPHEMATIC_LITERAL"
            prefix = truth2["true_record_operator"] + truth2["true_line_frame"] + truth2["true_literal_escape"] + truth2["true_lexical_left"]
            suffix = truth2["true_lexical_right"] + truth2["true_field_marker"] + truth2["true_positional_right"] + truth2["true_closure"]
            obs2["surface_group"] = prefix + truth2["rendered_host"] + suffix
            counts["literal_surface_changed"] += obs2["surface_group"] != old_surface
            lengths["old_literal_surface_chars"] += len(old_surface)
            lengths["new_literal_surface_chars"] += len(obs2["surface_group"])
        new_obs.append(obs2)
        new_oracle.append(truth2)

    assert counts["frequent_surface_changed"] == 0
    assert counts["literal_surface_changed"] == counts["LITERAL_ESCAPE"]
    assert [x["observation_id"] for x in new_obs] == [x["observation_id"] for x in old_obs]
    assert all({k: v for k, v in x.items() if k != "surface_group"} == {k: v for k, v in y.items() if k != "surface_group"}
               for x, y in zip(new_obs, old_obs))

    audit_rows = []
    for world in ("CONTROL_P", "CONTROL_Q"):
        literal_n = by_world[world, "LITERAL_ESCAPE"]
        old_chars = sum(len(x["surface_group"]) for x in old_obs if x["world_view"] == world and old_truth[x["observation_id"]]["lexical_status"] == "LITERAL_ESCAPE")
        new_chars = sum(len(x["surface_group"]) for x in new_obs if x["world_view"] == world and old_truth[x["observation_id"]]["lexical_status"] == "LITERAL_ESCAPE")
        audit_rows.append({"world_view": world, "frequent_rows": by_world[world, "FREQUENT_LEXICAL_ID"],
                           "frequent_surface_changes": 0, "literal_rows": literal_n,
                           "literal_surface_changes": literal_n,
                           "old_literal_mean_surface_length": old_chars / literal_n,
                           "new_literal_mean_surface_length": new_chars / literal_n})

    write_gzip(OBS, {"schema": "GDT172_STRICT_OBSERVATION_CORPUS_V1", "rows": new_obs})
    write_gzip(ORACLE, {"schema": "GDT172_SEALED_ORACLE_V1", "rows": sorted(new_oracle, key=lambda x: x["observation_id"])})
    write_tsv(AUDIT, audit_rows)

    old_freeze = json.loads(OLD_FREEZE.read_text())
    freeze = {
        "schema": "GDT172_SOURCE_LITERAL_CORRECTION_FREEZE_V1",
        "status": "FROZEN_LITERAL_ONLY_CORRECTION_BEFORE_BLIND_RERUN",
        "parent_status": old_freeze["status"],
        "change": "LITERAL_ESCAPE_MARKER_PLUS_UNCHANGED_SOURCE_GRAPHEMATIC_FORM",
        "invariants": {
            "observation_ids_order_and_layout_exact": True,
            "frequent_lexical_assignments_exact": True,
            "frequent_surface_rows_byte_identical": True,
            "outer_fields_unchanged_on_all_rows": True,
            "system_b_architecture": "EXPLICIT_FACTORIAL_DISTRIBUTED_CONTROL_NOT_HISTORICAL_NATURALISTIC",
            "system_b_384_row_table_unchanged": True,
            "b2_noncartesian_table": "NOT_BUILT_DEFERRED",
        },
        "counts": {
            "observation_rows": len(new_obs), "oracle_rows": len(new_oracle),
            "frequent_rows": counts["FREQUENT_LEXICAL_ID"], "literal_rows": counts["LITERAL_ESCAPE"],
            "frequent_surface_changes": counts["frequent_surface_changed"],
            "literal_surface_changes": counts["literal_surface_changed"],
            "content_folios": old_freeze["counts"]["content_folios"],
        },
        "observation_allowed_fields": old_freeze["observation_allowed_fields"],
        "observation_forbidden_fields": old_freeze["observation_forbidden_fields"],
        "inputs": {p.name: sha(p) for p in (OLD_OBS, OLD_ORACLE, OLD_FREEZE, LOOKUP, MANIFEST, SCHEMA)},
        "outputs": {p.name: sha(p) for p in (OBS, ORACLE, AUDIT)},
        "commitments": {"observation_content_sha256": csha(new_obs), "oracle_content_sha256": csha(sorted(new_oracle, key=lambda x: x["observation_id"])), "audit_content_sha256": csha(audit_rows)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "documents": {METHOD.name: sha(METHOD)},
        "no_voynich_tuning": True, "voynich_inputs": 0, "f84_access": False,
        "claim_ceiling": "Synthetic literal-channel sensitivity freeze only; no Voynich word, code value, language, meaning, plaintext, or translation.",
    }
    freeze["freeze_content_sha256"] = csha(freeze)
    FREEZE.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], **freeze["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
