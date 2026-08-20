#!/usr/bin/env python3
"""Administrative validator for a migrated historical structured manifest.

The scientific result and its historical validation stay byte-frozen.  The
only permitted result-bound document drift is experiment.json itself, whose
old ad-hoc form is replaced by the repository's current structured schema.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import load_manifest,verify_manifest_bindings

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 folder=(ROOT/sys.argv[1]).resolve();number=folder.name[3:6];checks=[]
 def ck(name,value):assert value,name;checks.append(name)
 manifest=load_manifest(folder/"experiment.json");ck("manifest_bindings",not verify_manifest_bindings(manifest))
 result_path=folder/"artifacts"/f"gdt{number}_result.json"
 if not result_path.is_file():
  alt=sorted(p for p in (folder/"artifacts").glob(f"gdt{number}_*result.json") if "validation" not in p.name and "freeze" not in p.name)
  ck("one_result",len(alt)==1);result_path=alt[0]
 result=json.loads(result_path.read_text())
 if "content_hash" in result:
  q=dict(result);expected=q.pop("content_hash");ck("result_content",expected==hashlib.sha256(json.dumps(q,sort_keys=True,separators=(",",":")).encode()).hexdigest())
 migrated=[]
 for block in ("inputs","outputs","implementation","documents"):
  values=result.get(block,{})
  if not isinstance(values,dict):continue
  for rel,digest in values.items():
   path=ROOT/rel
   if path.name=="experiment.json" and path.parent==folder:
    ck("manifest_replaced",path.is_file() and sha(path)!=digest);migrated.append(rel)
   else:ck(f"{block}:{rel}",path.is_file() and sha(path)==digest)
 ck("one_manifest_replacement",migrated==[folder.relative_to(ROOT).as_posix()+"/experiment.json"])
 validation_path=Path(manifest["validation"]["artifact"]);historical=json.loads((ROOT/validation_path).read_text())
 ck("historical_validation_pass",historical.get("status")=="PASS")
 print(f"ADMINISTRATIVE_MANIFEST_PASS {len(checks)}/{len(checks)}")
 return 0
if __name__=="__main__":raise SystemExit(main())
