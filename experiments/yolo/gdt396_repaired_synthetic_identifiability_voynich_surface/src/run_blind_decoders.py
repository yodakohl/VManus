#!/usr/bin/env python3
"""Run frozen GDT396 decoders on one unavailable-until-frozen seed block."""

from __future__ import annotations

import argparse
import copy
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import os
import sysconfig
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
SRC = EXP / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from decoder_api_v2 import API_VERSION, ARCHITECTURE_BINARY_PROPERTIES, BINARY_PROPERTIES, METHOD_VARIANTS, PARTITION_PROPERTIES, TABLE_FIELDS, TARGET_PROPERTIES, validate_shape  # noqa: E402
from observation_api import available_seeds, available_worlds, load_seed, load_world_block  # noqa: E402
from phase_authority import require_instrument  # noqa: E402


PHASE_BLOCK = {
    "DEVELOPMENT": "development", "QUALIFICATION": "qualification",
    "CONFIRMATION": "confirmation",
}
TRAIN_BLOCKS = {
    "DEVELOPMENT": ("legacy",),
    "QUALIFICATION": ("legacy", "development"),
    "CONFIRMATION": ("legacy", "development", "qualification"),
}
CANDIDATE_POLICY = {
    "GENERIC_RELATION": "RECORD_EXCL_SELF",
    "COORDINATOR_RELATION": "RECORD_EXCL_SELF",
    "ALTERNATIVE_RELATION": "RECORD_EXCL_SELF",
    "REFERENCE_ANAPHORA": "PRIOR_SEED_EVENTS",
    "ENTITY_REUSE_ANTECEDENT": "PRIOR_SEED_EVENTS",
}
MANIFEST_FIELDS = (
    "phase", "decoder_id", "decoder_sha256", "method_family", "world_id", "surface_id",
    "corpus_seed", "representation_id", "table_name", "rows", "relpath", "sha256",
    "model_sha256", "training_blocks", "training_events",
)
RETENTION = {
    "FULL_GROUP": {"partition_claims": {"LEXICAL_IDENTITY"}},
    "HOST_LIKE": {
        "partition_claims": {"SEMANTIC_ENTITY_IDENTITY", "HISTORICAL_ANCESTRY", "CURRENT_SHARED_MEANING", "REGISTER_REALIZATION"},
    },
    "COMPOSITE_STATE": {
        "partition_claims": {"CONSTRUCTION_CLASS", "STATE_BEFORE_IDENTITY", "STATE_AFTER_IDENTITY", "STATE_TRANSITION_IDENTITY"},
        "binary_claims": {"TEMPORAL_STATE_GATE"},
    },
    "INFERRED_COMPONENTS": {
        "partition_claims": {"CURRENT_PRODUCTIVE_COMPONENT", "FOSSIL_COMPONENT"},
        "binary_claims": {"PRODUCTIVE_MORPHOLOGY", "FOSSILIZED_MORPHOLOGY"}, "morphology_claims": {"MORPHOLOGY_ANALYSIS"},
    },
    "CONSTRUCTION_SPAN": {
        "scope_claims": {"SCOPE"},
    },
    "RECORD_TOPOLOGY": {
        "binary_claims": {"ENTITY_REUSE_PRESENT"}, "target_queries": set(TARGET_PROPERTIES), "target_ranks": set(TARGET_PROPERTIES),
        "record_partition_claims": {"RECORD_SCHEMA"},
    },
    "MULTI_RESOLUTION": {
        "partition_claims": {"FUNCTION_OPERATOR_CLASS", "SEMANTIC_CATEGORY"},
        "architecture_partition_claims": {"WORLD_ARCHITECTURE"},
        "architecture_binary_claims": set(ARCHITECTURE_BINARY_PROPERTIES),
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_model(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def require_phase_authority(phase: str) -> None:
    require_instrument(EXP, phase)


def install_decoder_audit(decoder_path: Path, output_root: Path, manifest_path:Path) -> None:
    """Deny decoder-time repository reads and process/network side effects."""

    std_roots = {
        Path(value).resolve()
        for value in (sysconfig.get_paths().get("stdlib"), sysconfig.get_paths().get("platstdlib"), sys.base_prefix)
        if value
    }
    decoder_root = decoder_path.parent.resolve()
    output_root = output_root.resolve()
    manifest_path=manifest_path.resolve()

    def allowed(path: Path) -> bool:
        resolved = path.resolve()
        return resolved == decoder_path.resolve() or resolved.is_relative_to(decoder_root) or resolved.is_relative_to(output_root) or resolved==manifest_path or any(resolved.is_relative_to(root) for root in std_roots)

    def audit(event: str, args: tuple) -> None:
        if event in {"subprocess.Popen", "os.system", "socket.__new__", "socket.connect", "socket.getaddrinfo"}:
            raise PermissionError(f"decoder runtime event prohibited: {event}")
        if event == "open" and args:
            target = args[0]
            if isinstance(target, (str, bytes, os.PathLike)) and not allowed(Path(os.fsdecode(target))):
                raise PermissionError(f"decoder runtime file access prohibited: {target}")

    sys.dont_write_bytecode = True
    sys.addaudithook(audit)


def load_decoder(path: Path):
    spec = importlib.util.spec_from_file_location(f"gdt396_decoder_{path.parent.name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    meta = module.DECODER_META
    required = {"api_version", "decoder_id", "designer_model", "method_family", "oracle_blind", "supported_representations", "supported_claim_kinds", "max_rank_by_claim_kind", "fit_scope", "transductive_within_held_seed"}
    if set(meta) != required or meta["api_version"] != API_VERSION or meta["oracle_blind"] is not True or meta["fit_scope"] != "TRAIN_ONLY_WORLD":
        raise ValueError(f"{path}: invalid DECODER_META")
    # The independently written decoders used three harmless declaration
    # dialects here (table names, endpoint families, or property names).  The
    # executable contract is the nine-table output validated below, so do not
    # rewrite their metadata after design.  Require a non-empty declaration
    # and exact rank caps for every ranked-target property; runtime completion
    # plus validate_shape enforce the actual common interface.
    if not meta["supported_claim_kinds"] or set(meta["max_rank_by_claim_kind"]) < set(TARGET_PROPERTIES):
        raise ValueError(f"{path}: incomplete claim-kind/rank declaration")
    if not callable(module.fit) or not callable(module.decode) or not callable(module.classify_world):
        raise ValueError(f"{path}: missing API function")
    return module


def add_context(rows: list[dict], phase: str, run_id: str) -> list[dict]:
    result = copy.deepcopy(rows)
    for row in result:
        row["phase"] = phase
        row["run_id"] = run_id
    return result


def complete_explicit_unsupported(outputs: dict[str,list[dict]], module, held:list[dict], representation:str)->None:
    """Make silence explicit without converting it into a positive claim."""
    first=held[0];meta=module.DECODER_META;plan=RETENTION[representation]
    def common(prop:str,variant:str="PRIMARY")->dict:
        return {"schema_version":API_VERSION,"phase":first["phase"],"run_id":first["run_id"],"world_id":first["world_id"],"corpus_seed":first["corpus_seed"],"surface_id":first["surface_id"],"representation_id":representation,"decoder_id":meta["decoder_id"],"method_variant":variant,"property_id":prop}
    events={str(row["event_id"]) for row in held}
    for row in outputs["partition_claims"]:
        if row["claim_status"]!="RESOLVED":row["cluster_id"]=""
        elif not row["cluster_id"]:row["claim_status"]="ABSTAIN"
    for row in outputs["record_partition_claims"]:
        if row["claim_status"]!="RESOLVED":row["record_schema_cluster_id"]=""
        elif not row["record_schema_cluster_id"]:row["claim_status"]="ABSTAIN"
    for row in outputs["architecture_partition_claims"]:
        if row["claim_status"]!="RESOLVED":row["architecture_cluster_id"]=""
        elif not row["architecture_cluster_id"]:row["claim_status"]="ABSTAIN"
    for row in outputs["scope_claims"]:
        if row["claim_status"]!="RESOLVED":
            row["scope_present"]=False;row["predicted_start_event_id"]="";row["predicted_end_event_id"]="";row["scope_type_id"]=""
    for row in outputs["morphology_claims"]:
        if row["claim_status"]!="RESOLVED":
            row["component_id"]="";row["start_offset"]=0;row["end_offset"]=0;row["morphology_status"]="NO_COMPONENT_CLAIM"
    for table,properties in (("partition_claims",plan.get("partition_claims",set())),("binary_claims",plan.get("binary_claims",set()))):
        for prop in properties:
            present={row["unit_id"] for row in outputs[table] if row["property_id"]==prop and row["method_variant"]=="PRIMARY"}
            for event_id in sorted(events-present):
                if table=="partition_claims":outputs[table].append(common(prop)|{"unit_type":"EVENT","unit_id":event_id,"claim_status":"UNSUPPORTED","cluster_id":"","confidence":0.0})
                else:outputs[table].append(common(prop)|{"unit_type":"EVENT","unit_id":event_id,"claim_status":"UNSUPPORTED","predicted_bool":False,"confidence":0.0})
    for prop in plan.get("target_queries",set()):
        present={row["source_event_id"] for row in outputs["target_queries"] if row["property_id"]==prop and row["method_variant"]=="PRIMARY"}
        for event_id in sorted(events-present):outputs["target_queries"].append(common(prop)|{"source_event_id":event_id,"candidate_set_id":CANDIDATE_POLICY[prop],"claim_status":"UNSUPPORTED","predicted_target_count":0,"confidence":0.0})
    if "SCOPE" in plan.get("scope_claims",set()):
        present={row["source_event_id"] for row in outputs["scope_claims"] if row["method_variant"]=="PRIMARY"}
        for event_id in sorted(events-present):outputs["scope_claims"].append(common("SCOPE")|{"source_event_id":event_id,"claim_status":"UNSUPPORTED","scope_present":False,"predicted_start_event_id":"","predicted_end_event_id":"","scope_type_id":"","confidence":0.0})
    if "MORPHOLOGY_ANALYSIS" in plan.get("morphology_claims",set()):
        present={row["event_id"] for row in outputs["morphology_claims"] if row["method_variant"]=="PRIMARY"}
        for event_id in sorted(events-present):outputs["morphology_claims"].append(common("MORPHOLOGY_ANALYSIS")|{"event_id":event_id,"component_id":"","start_offset":0,"end_offset":0,"morphology_status":"NO_COMPONENT_CLAIM","claim_status":"UNSUPPORTED","rank":1,"confidence":0.0})
    if "RECORD_SCHEMA" in plan.get("record_partition_claims",set()):
        records={str(row["record_id"]) for row in held};present={row["record_id"] for row in outputs["record_partition_claims"] if row["method_variant"]=="PRIMARY"}
        for record_id in sorted(records-present):outputs["record_partition_claims"].append(common("RECORD_SCHEMA")|{"record_id":record_id,"claim_status":"UNSUPPORTED","record_schema_cluster_id":"","confidence":0.0})
    if plan.get("architecture_partition_claims") or plan.get("architecture_binary_claims"):
        for variant in METHOD_VARIANTS:
            if not any(row["method_variant"]==variant for row in outputs["architecture_partition_claims"]):outputs["architecture_partition_claims"].append(common("WORLD_ARCHITECTURE",variant)|{"claim_status":"UNSUPPORTED","architecture_cluster_id":"","confidence":0.0})
            for prop in plan.get("architecture_binary_claims",set()):
                if not any(row["method_variant"]==variant and row["property_id"]==prop for row in outputs["architecture_binary_claims"]):outputs["architecture_binary_claims"].append(common(prop,variant)|{"claim_status":"UNSUPPORTED","predicted_bool":False,"confidence":0.0})


def legal_target(prop: str, source: dict, target: dict) -> bool:
    if prop in ("GENERIC_RELATION", "COORDINATOR_RELATION", "ALTERNATIVE_RELATION"):
        return source["record_id"] == target["record_id"] and source["event_id"] != target["event_id"]
    if prop in ("REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT"):
        return int(target["global_event_rank"]) < int(source["global_event_rank"])
    return False


def validate_claims(outputs: dict[str, list[dict]], module, held: list[dict], representation: str, phase: str, run_id: str) -> None:
    validate_shape(outputs)
    meta = module.DECODER_META
    by_event = {row["event_id"]: row for row in held}
    records = {row["record_id"] for row in held}
    expected_common = {
        "phase": phase, "run_id": run_id, "world_id": held[0]["world_id"],
        "corpus_seed": held[0]["corpus_seed"], "surface_id": held[0]["surface_id"],
        "representation_id": representation, "decoder_id": meta["decoder_id"],
    }
    query_list = [
        (row["property_id"], row["source_event_id"], row["candidate_set_id"])
        for row in outputs["target_queries"]
    ]
    if len(query_list) != len(set(query_list)):
        raise ValueError("duplicate target query key")
    query_keys = set(query_list)
    logical_fields = {
        "partition_claims": ("method_variant", "property_id", "unit_type", "unit_id"),
        "binary_claims": ("method_variant", "property_id", "unit_type", "unit_id"),
        "target_queries": ("method_variant", "property_id", "source_event_id", "candidate_set_id"),
        "target_ranks": ("method_variant", "property_id", "source_event_id", "candidate_set_id", "target_rank"),
        "scope_claims": ("method_variant", "property_id", "source_event_id"),
        "morphology_claims": ("method_variant", "property_id", "event_id", "rank"),
        "record_partition_claims": ("method_variant", "property_id", "record_id"),
        "architecture_partition_claims": ("method_variant", "property_id"),
        "architecture_binary_claims": ("method_variant", "property_id"),
    }
    for table, rows in outputs.items():
        seen = set()
        for row in rows:
            for key, value in expected_common.items():
                if str(row[key]) != str(value):
                    raise ValueError(f"{table}: context mismatch {key}")
            key = tuple(row[field] for field in logical_fields[table])
            if key in seen:
                raise ValueError(f"{table}: duplicate logical claim key")
            seen.add(key)
            event_keys = [name for name in ("unit_id", "source_event_id", "event_id") if name in row]
            for name in event_keys:
                if row.get("unit_type") == "RECORD":
                    if row[name] not in records: raise ValueError(f"{table}: bad record unit")
                elif row[name] not in by_event:
                    raise ValueError(f"{table}: bad event {row[name]}")
            if table == "record_partition_claims" and row["record_id"] not in records:
                raise ValueError("bad record claim")
            if table in {"partition_claims","binary_claims"} and row["unit_type"]!="EVENT":
                raise ValueError("event claim has invalid unit_type")
            if table=="partition_claims" and ((row["claim_status"]=="RESOLVED") != bool(row["cluster_id"])):
                raise ValueError("partition status/cluster mismatch")
            if table=="record_partition_claims" and ((row["claim_status"]=="RESOLVED") != bool(row["record_schema_cluster_id"])):
                raise ValueError("record status/cluster mismatch")
            if table=="architecture_partition_claims" and ((row["claim_status"]=="RESOLVED") != bool(row["architecture_cluster_id"])):
                raise ValueError("architecture status/cluster mismatch")
            if table == "target_queries":
                if row["candidate_set_id"] != CANDIDATE_POLICY[row["property_id"]]:
                    raise ValueError("bad candidate policy")
            if table == "target_ranks":
                qkey = (row["property_id"], row["source_event_id"], row["candidate_set_id"])
                if row["candidate_set_id"] != CANDIDATE_POLICY[row["property_id"]] or row["target_event_id"] not in by_event:
                    raise ValueError("bad target row")
                if not legal_target(row["property_id"], by_event[row["source_event_id"]], by_event[row["target_event_id"]]):
                    raise ValueError("target outside visible candidate universe")
            if table == "scope_claims" and row["claim_status"] == "RESOLVED" and row["scope_present"] is True:
                a = by_event.get(row["predicted_start_event_id"]); b = by_event.get(row["predicted_end_event_id"]); source = by_event[row["source_event_id"]]
                if not a or not b or a["record_id"] != source["record_id"] or b["record_id"] != source["record_id"] or a["record_event_ordinal"] > b["record_event_ordinal"]:
                    raise ValueError("invalid scope")
            if table=="scope_claims" and row["scope_present"] is False and (row["predicted_start_event_id"] or row["predicted_end_event_id"]):
                raise ValueError("absent scope carries endpoints")
            if table=="scope_claims" and row["claim_status"]!="RESOLVED" and (row["scope_present"] is not False or row["scope_type_id"]):
                raise ValueError("unresolved scope carries a positive/type claim")
            if table == "morphology_claims" and row["claim_status"] == "RESOLVED" and row["morphology_status"] != "NO_COMPONENT_CLAIM":
                size = len(by_event[row["event_id"]]["visible_surface"])
                if not (0 <= int(row["start_offset"]) < int(row["end_offset"]) <= size):
                    raise ValueError("invalid morphology span")
            if table=="morphology_claims":
                cap=int(meta["max_rank_by_claim_kind"].get("MORPHOLOGY_ANALYSIS",0))
                if not 1<=int(row["rank"])<=cap:
                    raise ValueError("morphology rank outside registered cap")
                if row["claim_status"]!="RESOLVED" and (row["component_id"] or int(row["start_offset"]) or int(row["end_offset"]) or row["morphology_status"]!="NO_COMPONENT_CLAIM"):
                    raise ValueError("unresolved morphology row carries a component")
        if table == "target_ranks":
            grouped = {}
            for row in rows:
                grouped.setdefault((row["property_id"], row["source_event_id"], row["candidate_set_id"]), []).append(row)
            for key, group in grouped.items():
                group.sort(key=lambda row: int(row["target_rank"]))
                ranks = [int(row["target_rank"]) for row in group]
                if ranks != list(range(1, len(group) + 1)) or any(float(group[i]["target_score"]) < float(group[i + 1]["target_score"]) for i in range(len(group) - 1)):
                    raise ValueError("noncontiguous or nonmonotone target ranks")
                if key not in query_keys:
                    raise ValueError("target ranks without query")
                cap = int(meta["max_rank_by_claim_kind"].get(key[0], 0))
                if len(group) > cap or len({row["target_event_id"] for row in group}) != len(group):
                    raise ValueError("target rank cap or uniqueness violation")
    rank_by_query = {}
    for row in outputs["target_ranks"]:
        rank_by_query.setdefault((row["property_id"], row["source_event_id"], row["candidate_set_id"]), 0)
        rank_by_query[(row["property_id"], row["source_event_id"], row["candidate_set_id"])] += 1
    for row in outputs["target_queries"]:
        key = (row["property_id"], row["source_event_id"], row["candidate_set_id"])
        if int(row["predicted_target_count"]) != rank_by_query.get(key, 0):
            raise ValueError("predicted_target_count does not match rank rows")
        if row["claim_status"] != "RESOLVED" and rank_by_query.get(key, 0):
            raise ValueError("unresolved query has ranked targets")

    # Every retained event-level endpoint must make an explicit resolved,
    # abstain, or unsupported claim for every held event.  Endpoints assigned
    # to other representation views are represented as UNSUPPORTED metric
    # rows by the scorer rather than multiplied into every claim packet.
    event_ids = set(by_event)
    for table, properties in (
        ("partition_claims", set(RETENTION[representation].get("partition_claims", set()))),
        ("binary_claims", set(RETENTION[representation].get("binary_claims", set()))),
        ("target_queries", set(RETENTION[representation].get("target_queries", set()))),
    ):
        for prop in properties:
            unit_key = "source_event_id" if table == "target_queries" else "unit_id"
            claimed = {row[unit_key] for row in outputs[table] if row["property_id"] == prop}
            if claimed != event_ids:
                raise ValueError(f"{table}/{prop}: incomplete held-event coverage")
    morph_groups = {}
    for row in outputs["morphology_claims"]:
        morph_groups.setdefault(row["event_id"], []).append(int(row["rank"]))
    for event_id, ranks in morph_groups.items():
        if sorted(ranks) != list(range(1, len(ranks) + 1)):
            raise ValueError(f"noncontiguous morphology ranks for {event_id}")


def write_tsv_gz(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                for row in rows:
                    writer.writerow({key: ("TRUE" if value else "FALSE") if type(value) is bool else value for key, value in row.items()})


def retained_outputs(outputs: dict[str, list[dict]], representation: str) -> dict[str, list[dict]]:
    plan = RETENTION[representation]
    result = {}
    for table, data in outputs.items():
        allowed = plan.get(table, set())
        result[table] = list(data) if allowed is None else [row for row in data if row["property_id"] in allowed]
    return result


def boolean_roundtrip_selftest() -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=("a", "b"), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerow({key: ("TRUE" if value else "FALSE") if type(value) is bool else value for key, value in {"a": True, "b": False}.items()})
    parsed = next(csv.DictReader(io.StringIO(buffer.getvalue()), delimiter="\t"))
    if parsed != {"a": "TRUE", "b": "FALSE"}:
        raise RuntimeError("Boolean TSV round-trip contract failed")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=tuple(PHASE_BLOCK), required=True)
    ap.add_argument("--decoder", action="append", default=[])
    ap.add_argument("--world", action="append", default=[])
    ap.add_argument("--seed", action="append", type=int, default=[])
    ap.add_argument("--surface", action="append", choices=("FREE_SURFACE", "VOYNICH_SURFACE"), default=[])
    ap.add_argument("--representation", action="append", default=[])
    ap.add_argument("--output-dir", type=Path, default=EXP / ".work/claims")
    ap.add_argument("--manifest", type=Path, default=None)
    args = ap.parse_args()
    boolean_roundtrip_selftest()
    phase = args.phase; block = PHASE_BLOCK[phase]
    require_phase_authority(phase)
    worlds = tuple(args.world) if args.world else available_worlds(block)
    seeds = tuple(args.seed) if args.seed else available_seeds(block)
    if any(seed not in available_seeds(block) for seed in seeds):
        raise ValueError("requested seed is outside the frozen phase block")
    surfaces = tuple(args.surface) if args.surface else ("FREE_SURFACE", "VOYNICH_SURFACE")
    decoder_paths = [Path(value).resolve() for value in args.decoder] if args.decoder else sorted((EXP / "decoders").glob("*/decoder.py"))
    if len(decoder_paths) != 1 or len(worlds) != 1 or len(surfaces) != 1:
        raise ValueError("one fresh process must handle exactly one decoder, world, and surface")
    manifest_path = args.manifest or (args.output_dir / f"gdt396_{phase.lower()}_claim_manifest.tsv")
    if not manifest_path.resolve().is_relative_to(args.output_dir.resolve()):
        raise ValueError("claim manifest must remain inside output-dir")
    if manifest_path.exists():
        raise RuntimeError(f"refusing to overwrite claim manifest {manifest_path}")
    claim_run_root = args.output_dir / phase.lower() / decoder_paths[0].parent.name / surfaces[0] / worlds[0]
    if claim_run_root.exists():
        raise RuntimeError(f"refusing to overwrite claim run {claim_run_root}")
    # Materialize only observation rows before the decoder runtime audit is
    # installed.  No manifest/oracle path is then available to decoder code.
    training_cache = []
    for training_block in TRAIN_BLOCKS[phase]:
        training_cache.extend(load_world_block(training_block, worlds[0], surfaces[0]))
    held_cache = {seed: load_seed(block, worlds[0], seed, surfaces[0]) for seed in seeds}
    install_decoder_audit(decoder_paths[0], claim_run_root, manifest_path)
    manifest = []
    for decoder_path in decoder_paths:
        if not decoder_path.is_relative_to((EXP / "decoders").resolve()) or decoder_path.name != "decoder.py":
            raise ValueError(f"decoder outside frozen panel root: {decoder_path}")
        module = load_decoder(decoder_path); meta = module.DECODER_META
        representations = tuple(args.representation) if args.representation else tuple(meta["supported_representations"])
        if not representations or any(value not in meta["supported_representations"] for value in representations):
            raise ValueError(f"unsupported representation requested for {meta['decoder_id']}")
        for world in worlds:
            for surface in surfaces:
                training = training_cache
                model = module.fit(copy.deepcopy(training))
                model_bytes = canonical_model(model); model_sha = hashlib.sha256(model_bytes).hexdigest()
                for seed in seeds:
                    held = add_context(held_cache[seed], phase, f"GDT396_{phase}_{world}_{surface}_{seed}")
                    for representation in representations:
                        supplied_model = copy.deepcopy(model)
                        outputs = module.decode(supplied_model, copy.deepcopy(held), representation)
                        if supplied_model != model:
                            raise RuntimeError(f"{meta['decoder_id']}: supplied model mutated")
                        rerun = module.decode(copy.deepcopy(model), copy.deepcopy(held), representation)
                        if canonical_model(outputs) != canonical_model(rerun):
                            raise RuntimeError(f"{meta['decoder_id']}: decode is not deterministic")
                        complete_explicit_unsupported(outputs,module,held,representation)
                        validate_claims(outputs, module, held, representation, phase, held[0]["run_id"])
                        outputs = retained_outputs(outputs, representation)
                        base = args.output_dir / phase.lower() / decoder_path.parent.name / surface / world / str(seed) / representation
                        for table, rows_out in outputs.items():
                            path = base / f"{table}.tsv.gz"
                            write_tsv_gz(path, TABLE_FIELDS[table], rows_out)
                            manifest.append({
                                "phase": phase, "decoder_id": meta["decoder_id"], "decoder_sha256": sha256(decoder_path),
                                "method_family": meta["method_family"], "world_id": world, "surface_id": surface,
                                "corpus_seed": seed, "representation_id": representation, "table_name": table,
                                "rows": len(rows_out), "relpath": str(path.relative_to(args.output_dir)), "sha256": sha256(path),
                                "model_sha256": model_sha, "training_blocks": ";".join(TRAIN_BLOCKS[phase]),
                                "training_events": len(training),
                            })
                        print(meta["decoder_id"], phase, world, surface, seed, representation)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(manifest)
    print(manifest_path, len(manifest), sha256(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
