#!/usr/bin/env python3
"""One-shot frozen CCT001 target runner."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from cho_che_canonical_transfer_core import compact_score, score_world, validate_masked_geometry

B = Path(__file__).resolve().parent
R = B / "results"
FREEZE = B / "CCT001_TARGET_FREEZE.json"
PANEL = R / "cho_che_canonical_transfer_masked_panel.tsv"
SOURCE = R / "source_separator_transcription.tsv"
OUT = R / "cho_che_canonical_transfer_target.json"
REPORT = R / "cho_che_canonical_transfer_target.md"
VALIDATION_OUT = R / "cho_che_canonical_transfer_target_validation.json"
VALIDATION_REPORT = R / "cho_che_canonical_transfer_target_validation.md"
SITE = re.compile(r"(ch|sh)([oe])")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def absence() -> dict[str, bool]:
    return {p.name: not p.exists() for p in (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)}


def target_events():
    masked = list(csv.DictReader(PANEL.open(), delimiter="\t"))
    validate_masked_geometry(masked)
    source = {}
    for row in csv.DictReader(SOURCE.open(), delimiter="\t"):
        key = row["source_group_id"]
        if key in source:
            raise RuntimeError("duplicate source_group_id")
        source[key] = row
    events = []
    for row in masked:
        raw = source.get(row["source_group_id"])
        if raw is None:
            raise RuntimeError("missing target source row")
        for field in ("edition", "locus", "page"):
            if raw[field] != row[field]:
                raise RuntimeError(f"source crosswalk drift: {field}")
        if raw["clean_ascii_fragment_count"] != "1":
            raise RuntimeError("fragment drift")
        surface = raw["clean_ascii_fragments"]
        sites = list(SITE.finditer(surface))
        if len(sites) != 1 or sites[0].group(1) != row["site_prefix"] or len(surface) != int(row["ascii_length"]):
            raise RuntimeError("site drift")
        match = sites[0]
        index = match.end() - 1
        realization = surface[index]
        canonical = surface[:index] + "X" + surface[index+1:]
        events.append({"event_id": row["source_group_id"], "edition": row["edition"], "leaf": row["physical_folio"], "side": row["side"], "state": int(row["page_state"]), "scope": row["grammar_scope"], "prefix": row["site_prefix"], "raw_type": surface, "canonical_type": canonical, "realization": realization, "length": len(surface), "site_index": index})
    if len(events) != 2223 or len({x["event_id"] for x in events}) != 2223:
        raise RuntimeError("target identity")
    return events


def install(j: bytes, m: bytes) -> None:
    if not all(absence().values()):
        raise FileExistsError("target or validation output exists")
    with tempfile.TemporaryDirectory(prefix="cct001t_", dir=R) as d:
        a, b = Path(d)/"j", Path(d)/"m"
        a.write_bytes(j); b.write_bytes(m)
        if not all(absence().values()):
            raise FileExistsError("concurrent target output")
        os.link(a, OUT)
        try: os.link(b, REPORT)
        except Exception: OUT.unlink(missing_ok=True); raise


def main():
    if not FREEZE.exists(): raise SystemExit("missing freeze")
    freeze = json.loads(FREEZE.read_text())
    if freeze.get("status") != "FROZEN_CCT001_TARGET_AND_VALIDATION_ABSENT" or set(freeze.get("files", {})) != set(freeze.get("required_files", [])):
        raise SystemExit("freeze schema")
    paths = {p.name:p for p in (B/"CHO_CHE_CANONICAL_TRANSFER_TARGET_METHOD.md", B/"CHO_CHE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_SPEC.md", B/"cho_che_canonical_transfer_core.py", B/"run_cho_che_canonical_transfer_target.py", B/"validate_cho_che_canonical_transfer_target.py", PANEL, SOURCE, R/"cho_che_canonical_transfer_capacity_validation.json", R/"cho_che_canonical_transfer_synthetic_preflight.json", R/"cho_che_canonical_transfer_synthetic_preflight_validation.json")}
    if set(paths) != set(freeze["files"]): raise SystemExit("freeze allowlist")
    for name, path in paths.items():
        if sha(path) != freeze["files"][name]: raise SystemExit(f"hash: {name}")
    before = absence()
    if not all(before.values()) or before != freeze["output_absence"]: raise SystemExit("output absence")
    events = target_events()
    score = compact_score(score_world(events))
    scientific = score.get("gates", {})
    core_names = ("capacity","primary_state_excess","matched_merge_advantage","state_orbit_p","merger_null_p","reading_state_excess","leaf_support","loo_gain","concentration")
    if score.get("status") == "STOP_INSUFFICIENT_COLLISION_CAPACITY":
        decision = "STOP_INSUFFICIENT_CANONICAL_COLLISION_CAPACITY"
    elif score["passes"]:
        decision = "CONFIRM_USEFUL_GENERAL_CANONICAL_TRANSFER"
    elif all(scientific.get(k, False) for k in core_names) and not all(scientific.get(k, False) for k in ("prose_state_excess","prose_support","diagnostic_state_excess","diagnostic_support","prefix_gain")):
        decision = "NONCONFIRM_GENERAL_CANONICAL_TRANSFER_DOMAIN_OR_PREFIX_LIMITED"
    else:
        decision = "NONCONFIRM_CANONICAL_TRANSFER"
    result = {"experiment":"CCT001_CHO_CHE_CANONICAL_TRANSFER_TARGET", "status":"PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION", "decision":decision, "freeze_sha256":sha(FREEZE), "inputs":{name:sha(path) for name,path in paths.items()}, "target_rows":len(events), "score":score, "individual_types_emitted":0, "individual_templates_emitted":0, "english_glosses":0, "claim_ceiling":"At most useful transferable formal support for one-character canonicalization; no word sound phonology language cipher plaintext meaning or translation."}
    if decision == "CONFIRM_USEFUL_GENERAL_CANONICAL_TRANSFER":
        summary = "All registered capacity, state-excess, complexity-matched merger, reading, folio, domain, prefix, deletion, and concentration gates pass."
    elif decision == "NONCONFIRM_GENERAL_CANONICAL_TRANSFER_DOMAIN_OR_PREFIX_LIMITED":
        summary = "Core transfer gates pass, but the preregistered domain or prefix distribution gates fail; the general collapse is not confirmed."
    elif decision == "STOP_INSUFFICIENT_CANONICAL_COLLISION_CAPACITY":
        summary = "The frozen collision-pair capacity gate fails, so no target score is interpreted."
    else:
        summary = "The frozen canonical-transfer representation fails one or more core registered gates."
    report = f"# CCT001 `cho/che` canonical-transfer target\n\nStatus: **PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION**  \nDecision: **{decision}**\n\n{summary} The run joined exactly {len(events):,} frozen target rows and emitted no individual type or template. Independent reconstruction is mandatory.\n"
    if not all(absence().values()): raise SystemExit("late output appearance")
    install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode())
    print(json.dumps({"status":result["status"],"decision":decision,"target_rows":len(events),"capacity":score.get("capacity"),"gates":score.get("gates")},sort_keys=True))

if __name__ == "__main__": main()
