#!/usr/bin/env python3
"""Reproduce native-observation inventory, never infer glyphs or meanings."""
from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
def collect():
    out={"experiment":"GDT1044","status":"AMBIGUITY_RETAINED_SEED_READER_SPECIFIC","semantic_test":False,"registered_lines":["f85r2.2","f85r2.20"],"groups_per_observer":13,"observers":{}}
    for name in ["ROOT","B"]:
        j=json.loads((B/f"artifacts/OBSERVER_{name}.json").read_text())
        out["observers"][name]={"recorded_groups":len(j["groups"]),"positions":[[g["locus"],g["position"]] for g in j["groups"]],"human_reading_required":True}
    out["claim_ceiling"]="Mechanical inventory only. Read REPORT and frozen observations for agreements, disagreements and visual uncertainty; no vote selects a canonical transcript or meaning."
    return out
if __name__=="__main__":
    p=B/"artifacts/RESULT.json"
    p.write_text(json.dumps(collect(),indent=2)+"\n")
    print("26 complete-line group records inventoried; no glyph or meaning validation")
