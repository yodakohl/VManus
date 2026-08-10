#!/usr/bin/env python3
"""Apply the frozen arithmetic-order correction to the clean LRG005 validator."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ORIGINAL=HERE/"validate_lrg005_d1_extension_target.py"
AMENDMENT=HERE/"LRG005_TARGET_VALIDATION_AMENDMENT.json"
TARGET=HERE/"results"/"lrg005_d1_extension_target.json"
REPORT=HERE/"results"/"lrg005_d1_extension_target_report.md"

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->None:
    amendment=json.loads(AMENDMENT.read_text(encoding="utf-8"))
    if amendment["status"]!="FROZEN_LRG005_VALIDATOR_ARITHMETIC_ORDER_CORRECTION":raise RuntimeError("amendment status")
    expected={"original_validator":sha(ORIGINAL),"target":sha(TARGET),"report":sha(REPORT),"corrected_validator":sha(Path(__file__))}
    if amendment["hashes"]!=expected:raise RuntimeError("amendment hash drift")
    source=ORIGINAL.read_text(encoding="utf-8")
    old_stack="fe=np.stack(fe);nums=np.asarray([int(f[1:]) for f in folios])"
    new_stack="fe=np.stack(fe);observed=fe.mean(axis=0);nums=np.asarray([int(f[1:]) for f in folios])"
    old_effect="vals=fe[:,j];t=float(vals.mean());mu=float(null[:,j].mean())"
    new_effect="vals=fe[:,j];t=float(observed[j]);mu=float(null[:,j].mean())"
    if source.count(old_stack)!=1 or source.count(old_effect)!=1:raise RuntimeError("correction anchors drift")
    corrected=source.replace(old_stack,new_stack).replace(old_effect,new_effect)
    namespace={"__name__":"__main__","__file__":str(ORIGINAL.resolve())}
    exec(compile(corrected,str(ORIGINAL),"exec"),namespace)

if __name__=="__main__":main()
