#!/usr/bin/env python3
"""Summarize fixed manual observations; does not infer glyphs or meanings."""
from pathlib import Path
import json, csv, collections
BASE = Path(__file__).resolve().parents[1]
IDS = [f"{r}_{q}" for r in ("N1", "D1") for q in ("NE", "SE", "SW", "NW")]
VERDICTS = {"EXPLICIT_PATH", "POSSIBLE_UNBOUND", "SEPARATED_NO_CUE", "UNRESOLVED"}
def build():
    readers = []
    for name in ("ROOT_OBSERVATIONS.json", "READER_B.json"):
        obj = json.loads((BASE / "artifacts" / name).read_text())
        cases = obj["cases"]
        rows = {r.get("case", r.get("case_id")): r for r in cases}
        assert len(cases) == len(rows) == 8 and set(rows) == set(IDS)
        assert all(r["verdict"] in VERDICTS for r in rows.values())
        readers.append(rows)
    rows = []
    for case in IDS:
        a,b = (r[case]["verdict"] for r in readers)
        rows.append(dict(case=case,root=a,reader_b=b,agreement=a==b,explicit_path_nominated=a==b=="EXPLICIT_PATH"))
    result = dict(experiment="GDT1169",case_count=8,reader_counts=[dict(collections.Counter(r[i]["verdict"] for i in IDS)) for r in readers],explicit_paths_by_reader=[[i for i in IDS if r[i]["verdict"]=="EXPLICIT_PATH"] for r in readers],explicit_agreed_paths=[r["case"] for r in rows if r["explicit_path_nominated"]],disagreements=[r["case"] for r in rows if not r["agreement"]],confirmed_voynich_words=0,independent_confirmation_leaves=0,scope="Native layout only; absence of explicit cue does not disprove implicit continuation")
    return rows,result
if __name__ == "__main__":
    rows,result=build()
    with (BASE/"artifacts/CASES.tsv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
    (BASE/"artifacts/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
