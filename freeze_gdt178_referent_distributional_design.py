#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=("GDT178_REFERENT_DISTRIBUTIONAL_HOST_METHOD.md","gdt169_external_referent_candidates.tsv","gdt169_source_access_correction.json","gdt062_right_family_inventory.tsv","gdt152_relation_queries.tsv")
d={"experiment":"GDT178_REFERENT_DISTRIBUTIONAL_HOST","status":"FROZEN_BEFORE_FULL_ATLAS_DISTRIBUTIONAL_SCORING","representations":["HOST_EXACT","HOST_CHAR2","HOST_CHAR3","RAW_CHAR3","HOST_LENGTH"],"worlds":20000,"seed":17820260817,"inputs":{p:sha(p) for p in files},"f84r_accessed":False,"claim_ceiling":"anonymous externally nominated page-profile similarity only; no word meaning language plaintext or translation"}
d["content_hash"]=hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":")).encode()).hexdigest();Path("gdt178_design.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n");print(d["content_hash"])
