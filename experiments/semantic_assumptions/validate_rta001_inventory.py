#!/usr/bin/env python3
"""Independent, nonimporting validator for the RTA001 relation inventory."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "results"
TSV = R / "rta001_relation_graph_inventory.tsv"
META = R / "rta001_relation_graph_inventory.json"
ANN = R / "existing_human_exact_locus_annotations.tsv"
CIRC = R / "special_circle_text_blind_array_inventory.tsv"
SEL = R / "rd5x3001_rosettes_doorway_selection.json"
TOP = R / "rd5x3001_rosettes_doorway_topology_result.json"


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    actual = rows(TSV); meta = json.loads(META.read_text())
    assertions = []
    def check(name, value):
        assertions.append((name, bool(value)))
        if not value: raise AssertionError(name)
    check("537 edges", len(actual) == 537)
    check("46 panels", len({x['panel_id'] for x in actual}) == 46)
    check("nine folios", len({x['physical_folio'] for x in actual}) == 9)
    check("relation counts", Counter(x['relation_type'] for x in actual) == {'CYCLIC_SUCCESSOR':484,'ROW_SUCCESSOR':40,'ROW_SKIP_ONE':13})
    check("unique edge keys", len({(x['panel_id'],x['relation_instance']) for x in actual}) == len(actual))
    check("no f57/f84", not any(x['page'] in {'f57v','f84r'} for x in actual))
    circles=defaultdict(list)
    for x in rows(CIRC): circles[x['array_id']].append(x)
    expected_cycle=set()
    for aid, group in circles.items():
        group=sorted(group,key=lambda x:int(x['slot_index'])); n=int(group[0]['slot_count'])
        if len(group)==n and n>=4 and all(x['occupancy_state']=='TRANSCRIBED' for x in group):
            for i,x in enumerate(group): expected_cycle.add((aid,x['locus'],group[(i+1)%n]['locus']))
    got_cycle={(x['panel_id'],x['source_locus'],x['target_locus']) for x in actual if x['relation_type']=='CYCLIC_SUCCESSOR'}
    check("complete cycles exact", got_cycle == expected_cycle)
    ann=rows(ANN); f75=[]
    for x in ann:
        if x['page']=='f75v' and x['unit']=='N1':
            m=re.search(r'Label L(\d+), line ([12])\.$',x['local_comment'])
            if m: f75.append((int(m.group(1)),int(m.group(2)),x['locus']))
    got_f75={(x['source_locus'],x['target_locus']) for x in actual if x['panel_id']=='RTA001|f75v|N1_TWO_LINE_STACKS'}
    lookup={(a,b):c for a,b,c in f75}
    check("f75 exact pairs", got_f75 == {(lookup[i,1],lookup[i,2]) for i in range(1,11)})
    sel=json.loads(SEL.read_text()); top=json.loads(TOP.read_text())
    check("rosettes source pass", top['status']=='PASS_LOCAL_FIVE_BY_THREE_AUTHOR_VISIBLE_SCHEMA' and len(sel['rows'])==15)
    ros=[x for x in actual if x['physical_folio']=='fRos']
    check("rosettes 15 edges", len(ros)==15 and Counter(x['relation_type'] for x in ros)=={'ROW_SUCCESSOR':10,'ROW_SKIP_ONE':5})
    check("metadata embeds exact rows", meta['rows']==actual)
    check("metadata tsv hash", meta['artifacts']['inventory_tsv_sha256']==digest(TSV))
    check("source hashes", meta['inputs']=={
        'existing_human_exact_locus_annotations_sha256':digest(ANN),
        'special_circle_text_blind_array_inventory_sha256':digest(CIRC),
        'rd5x3001_rosettes_doorway_selection_sha256':digest(SEL),
        'rd5x3001_rosettes_doorway_topology_result_sha256':digest(TOP)})
    print(json.dumps({'status':'PASS','checks':len(assertions),'inventory_sha256':digest(TSV)},sort_keys=True))

if __name__=='__main__': main()
