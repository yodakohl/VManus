#!/usr/bin/env python3
"""Freeze GDT348 oracle-coordinate crosswalk, source split, and capacity."""
from __future__ import annotations

import csv, gzip, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt348_oracle_coordinate_transport_calibration"
ART = EXP / "artifacts"
G347 = ROOT / "experiments/yolo/gdt347_fixed_graph_control_transport/artifacts/gdt347_frozen_graph.json"
G345 = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv"
O172 = ROOT / "gdt172_sealed_oracle.json.gz"; V172 = ROOT / "gdt172_observation_corpus.json.gz"
O173 = ROOT / "gdt173_b2_sealed_oracle.json.gz"; V173 = ROOT / "gdt173_b2_observation_corpus.json.gz"
METHOD = EXP / "METHOD.md"; AUDIT = EXP / "SOURCE_AUDIT.md"
DESIGN = ART / "gdt348_design.json"; CAP = ART / "gdt348_oracle_capacity.tsv"
SALT = "GDT348_SOURCE_UNIT_SPLIT_V1"
SYSTEMS = {
    "LEXICAL_A": (O172, V172, "SYSTEM_A_V3_UNCHANGED_LITERAL"),
    "FACTORIAL_B": (O172, V172, "SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3"),
    "HUMAN_GROWN_B2": (O173, V173, "SYSTEM_B2_HUMAN_GROWN_DISTRIBUTED_CONTROL"),
}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def chash(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(p):
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)['rows']
def read_tsv(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write_tsv(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    ART.mkdir(parents=True,exist_ok=True)
    frozen=json.loads(G347.read_text()); held347=set(frozen['voynich_partition']['held_folios'])
    voy=read_tsv(G345); counts=Counter()
    for r in voy:
        if r['physical_folio'] in held347: continue
        state=json.loads(r['target_state_json']); counts[state[2]]+=1
    voy_non=[x for x,_ in sorted(((k,v) for k,v in counts.items() if k!='NONE'),key=lambda kv:(-kv[1],kv[0]))]
    assert len(voy_non)==5

    cache={}
    def payload(p):
        if p not in cache: cache[p]=load(p)
        return cache[p]
    units=sorted({r['source_unit_full'] for r in payload(O172)})
    assert len(units)==21
    order=sorted(units,key=lambda u:hashlib.sha256((SALT+'\0'+u).encode()).hexdigest())
    held=sorted(order[:5]); train=sorted(set(units)-set(held))
    capacity=[]; mappings={}
    for name,(op,_,system) in SYSTEMS.items():
        rows=[r for r in payload(op) if r['system']==system]
        assert {r['source_unit_full'] for r in rows}==set(units)
        tr=[r for r in rows if r['source_unit_full'] in train]
        rc=Counter(r['true_lexical_right'] for r in tr if r['true_lexical_right'])
        ordered=[k for k,_ in sorted(rc.items(),key=lambda kv:(-kv[1],kv[0]))]
        rmap={'':'NONE'}
        for i,key in enumerate(ordered): rmap[key]=voy_non[min(i,len(voy_non)-1)]
        mappings[name]=rmap
        capacity.append({
            'system':name,'rows':len(rows),'training_rows':len(tr),'held_rows':len(rows)-len(tr),
            'source_units':len(units),'training_units':len(train),'held_units':len(held),
            'records':len({r['true_record_id'] for r in rows}),
            'inner_d_positive':sum(r['true_lexical_left']=='d' for r in rows),
            'dy_positive':sum(r['true_closure']=='y' for r in rows),
            'b3_positive':sum(r['true_closure']=='k' for r in rows),
            'right_nonempty':sum(bool(r['true_lexical_right']) for r in rows),
            'wrapper_nonempty':sum(bool(r['true_record_operator']) for r in rows),
            'right_categories':len({r['true_lexical_right'] for r in rows}),
            'crosswalk_status':'FROZEN_CAPACITY_ONLY',
        })
    write_tsv(CAP,capacity)
    doc={
      'schema':'GDT348_ORACLE_COORDINATE_FREEZE_V1','date':'2026-08-19','status':'FROZEN_BEFORE_ORACLE_TRANSPORT_SCORING',
      'systems':list(SYSTEMS),'split':{'salt':SALT,'training_units':train,'held_units':held},
      'crosswalk':{'local_frame':'EMPTY_NONE_ELSE_O','inner_d':'TRUE_LEXICAL_LEFT_EQUALS_D','right_family_maps':mappings,
                   'right_mapping_rule':'TRAINING_FREQUENCY_RANK_TO_GDT347_TRAINING_RIGHT_FREQUENCY_RANK_RAREST_COLLAPSE',
                   'dy_closure':'TRUE_CLOSURE_EQUALS_Y','b3':'TRUE_CLOSURE_EQUALS_K','canonical_wrapper':'EMPTY_NONE_ELSE_LITERAL_Q_D_S'},
      'layout':{'same_line':['SAME_FIELD','SAME_FIELD','0','MIDDLE_OR_LAST','0'],
                'new_line':['LINE_RESET','SAME_FIELD','1','FIRST','0'],'record_crossings':'EXCLUDED'},
      'graph':{'content_sha256':frozen['content_sha256'],'topology':frozen['topology'],'selector_bits_once':frozen['selector_bits_once'],
               'weights_unchanged':True,'mapping_score_optimized':False},
      'inputs':{str(p.relative_to(ROOT)):sha(p) for p in (G347,G345,O172,V172,O173,V173,METHOD,AUDIT)},
      'outputs':{str(CAP.relative_to(ROOT)):sha(CAP)},
      'implementation':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))},
      'f84':{'opened':False,'parsed':False,'retained':False,'scored':False},'semantic_state':'UNASSIGNED'}
    doc['content_sha256']=chash(doc);DESIGN.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n')
    print('FROZEN systems=3 units=21 train=16 held=5')
if __name__=='__main__':main()
