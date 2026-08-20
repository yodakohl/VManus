#!/usr/bin/env python3
"""Validate one new paired GDT396 seed block before blind decoding."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import hmac
import json
import struct
from pathlib import Path

from phase_authority import require_instrument


def find_repo_root(start: Path)->Path:
    for candidate in (start,*start.parents):
        if (candidate/"AGENTS.md").is_file() and (candidate/".git").exists():return candidate
    raise RuntimeError("repository root not found")


ROOT=find_repo_root(Path(__file__).resolve());EXP=ROOT/"experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface";CORPORA=EXP/".work/corpora";MAGIC=b"GDT396VS1\0";ALPHABET=24


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda:fh.read(1<<20),b""):h.update(block)
    return h.hexdigest()


def rows(path:Path)->list[dict]:
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt",encoding="utf-8",newline="") as fh:return list(csv.DictReader(fh,delimiter="\t"))


def atoms(path:Path)->list[tuple[int,...]]:
    out=[]
    with gzip.open(path,"rb") as fh:
        if fh.read(len(MAGIC))!=MAGIC:raise ValueError("bad atom magic")
        count=struct.unpack(">I",fh.read(4))[0]
        for _ in range(count):
            size=struct.unpack(">H",fh.read(2))[0];value=fh.read(size)
            if len(value)!=size or not value or any(x>=ALPHABET for x in value):raise ValueError("bad atom payload")
            out.append(tuple(value))
        if fh.read(1):raise ValueError("trailing atom payload")
    return out


def mapping(salt:bytes,world:str,native:str)->dict[str,tuple[int,int]]:
    def rank(label:bytes)->bytes:return hmac.new(salt,b"GDT396-VS1\0"+world.encode("ascii")+b"\0"+label,hashlib.sha256).digest()
    ranked=[(rank(bytes((a,b))),a,b) for a in range(ALPHABET) for b in range(ALPHABET)];ranked.sort()
    ordered=sorted(native,key=lambda value:(rank(value.encode("utf-8")),value))
    return {symbol:(ranked[i][1],ranked[i][2]) for i,symbol in enumerate(ordered)}


def trace(free:list[dict],oracle:list[dict])->str:
    payload={"trace":[{k:v for k,v in row.items() if k!="visible_group"} for row in free],"oracle":oracle}
    return hashlib.sha256((json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()).hexdigest()


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--phase",choices=("qualification","confirmation"),required=True);args=ap.parse_args();phase=args.phase
    try:
        require_instrument(EXP,phase.upper());authority_pass=True
    except (FileNotFoundError,KeyError,RuntimeError,ValueError):
        authority_pass=False
    checks={"authority_pass":authority_pass}
    source=CORPORA/f"gdt396_{phase}_paired_manifest.tsv";corrected=CORPORA/f"gdt396_{phase}_paired_manifest_v2.tsv";data=rows(corrected)
    expected=set(range(3961000,3961005)) if phase=="qualification" else set(range(3962000,3962005))
    checks["cartesian_50"] = len(data)==50 and {r["world_id"] for r in data}=={f"W{i:02d}" for i in range(1,11)} and {int(r["corpus_seed"]) for r in data}==expected
    checks["source_manifest_bound"]=all(r["source_manifest_sha256"]==sha256(source) for r in data)
    salt=bytes.fromhex((EXP/".work/sealed/surface_salt.hex").read_text().strip());commit=json.loads((EXP/"artifacts/gdt396_protocol_freeze.json").read_text())["mapping_salt_commitment"]
    checks["salt_commitment"]=hashlib.sha256(b"GDT396-SURFACE-SALT-V1\0"+salt).hexdigest()==commit
    metas={world:json.loads((CORPORA/"sealed"/world/"world_meta.json").read_text()) for world in {r["world_id"] for r in data}}
    hash_ok=pair_ok=atom_ok=trace_ok=endpoints=True;events=0
    for item in data:
        paths={key:(CORPORA/item[key.replace("_sha256","_relpath")]) for key in ("free_observation_sha256","voynich_metadata_sha256","voynich_surface_sha256","oracle_sha256")}
        hash_ok &= all(sha256(path)==item[key] for key,path in paths.items())
        free=rows(paths["free_observation_sha256"]);meta=rows(paths["voynich_metadata_sha256"]);payload=atoms(paths["voynich_surface_sha256"]);oracle=rows(paths["oracle_sha256"]);events+=len(free)
        pair_ok &= len(free)==len(meta)==len(payload)==len(oracle)==int(item["events"])
        mp=mapping(salt,item["world_id"],metas[item["world_id"]]["alphabet"]);ids={r["event_id"] for r in free}
        for i,(a,b,c,d) in enumerate(zip(free,meta,payload,oracle,strict=True)):
            pair_ok &= all(a[k]==b[k] for k in a if k!="visible_group") and b["surface_channel"]=="VOYNICH_SURFACE" and int(b["surface_payload_index"])==i and a["event_id"]==d["event_id"]
            atom_ok &= c==tuple(x for ch in a["visible_group"] for x in mp[ch])
            for field in ("relation_target_event_id","scope_start_event_id","scope_end_event_id"):
                endpoints &= d[field] in {"NONE",""} or all(v in ids for v in d[field].split("|"))
        trace_ok &= trace(free,oracle)==item["hidden_trace_sha256"]
    checks.update(file_hashes=hash_ok,paired_trace=pair_ok,atom_channel_exact=atom_ok,trace_digest_exact=trace_ok,oracle_endpoints_valid=endpoints)
    result={"schema":"GDT396_PHASE_CORPUS_VALIDATION_V1","status":"PASS" if all(checks.values()) else "FAIL","phase":phase.upper(),"checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"paired_corpora":len(data),"paired_events":events,"source_manifest_sha256":sha256(source),"corrected_manifest_sha256":sha256(corrected),"validator_sha256":sha256(Path(__file__)),"voynich_rows":0,"f84":{"opened":False,"rows":0},"f84r":{"opened":False,"rows":0}}
    out=EXP/f"artifacts/gdt396_{phase}_corpus_validation.json";out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,indent=2,sort_keys=True));return 0 if result["status"]=="PASS" else 1


if __name__=="__main__":raise SystemExit(main())
