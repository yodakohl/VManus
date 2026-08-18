#!/usr/bin/env python3
"""Validate the GDT281 pre-score freeze independently."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):
 q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads((R/'gdt281_design.json').read_text());ck('status',d['status']=='FROZEN_BEFORE_GDT281_EXACT_CONTEXT_SCORING');ck('content',d['content_sha256']==csha(d));ck('method',d['method_sha256']==sha(R/'GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_METHOD.md'));ck('freezer',d['implementation_sha256']==sha(R/'freeze_gdt281_edge_profile_collision_sensitivity.py'))
 with (R/'gdt281_gdt280_freeze_manifest.tsv').open(encoding='utf8',newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 ck('manifest_hash',d['freeze_manifest_sha256']==sha(R/'gdt281_gdt280_freeze_manifest.tsv'));ck('manifest_count',len(rows)==15)
 for x in rows:ck('frozen:'+x['artifact'],sha(R/x['artifact'])==x['frozen_sha256'])
 ck('exact',d['context_representation']=='EXACT_IMMUTABLE_TUPLE_NO_HASH');ck('subsets',d['subset_count']==16);ck('null',d['null_worlds']==64);ck('panels',len(d['primary_native_panels'])==4 and len(d['layout_bridge_panels'])==3);ck('no_new',d['new_control_corpora']==0);ck('no_semantics',d['semantic_assignments']==d['hpr1_semantics_used']==d['voynich_substrings_mined']==0);ck('f84',all(v in (0,False) for v in d['f84'].values()))
 out={'schema':'GDT281_DESIGN_VALIDATION_V1','status':'PASS','checks':len(checks),'design_sha256':sha(R/'gdt281_design.json'),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);(R/'gdt281_design_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
