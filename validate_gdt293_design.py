#!/usr/bin/env python3
"""Validate the GDT293 frozen design and capacity inventory."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt293_design.json';OUT=R/'gdt293_design_validation.json';COMP=['wrapper','local_frame','inner_d','right_family','dy_closure','b3']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 cc=[]
 def ck(n,v):cc.append({'check':n,'pass':bool(v)});assert v,n
 d=json.loads(D.read_text());ck('content',d['content_sha256']==csha(d));ck('status',d['status']=='FROZEN_BEFORE_GDT293_SCORING');ck('panels',len(d['panels'])==8);ck('outcome',d['primary_outcome']=='EXACT_WRAPPER_FRAME_INNERD_RIGHT_DY_B3_TUPLE');ck('components',d['component_diagnostics']==COMP);ck('models',d['models']==['LAYOUT_CONTEXT','EXACT_HOST']);ck('context',len(d['layout_context'])==9);ck('priors',d['primary_prior_mass']==11 and d['voynich_prior_sensitivities']==[5,22]);ck('no_sequence_or_glyph',d['sequential_host_features']==d['host_glyph_or_substring_features']==0);ck('null',d['null_worlds']==64 and d['null_operation'].startswith('PERMUTE_JOINT_RENDERER_'));ck('decision',d['decision']['minimum_positive_components']==4 and d['decision']['minimum_positive_folios']==60 and d['decision']['alpha']==.05);ck('prior_route',d['prior_next_host_result']=='GDT165_NEGATIVE_NOT_RERUN');ck('prohibitions',d['new_corpora']==d['new_architectures']==d['semantic_assignments']==0);ck('f84',d['f84']['input_files']==0 and not any(v for k,v in d['f84'].items() if k!='input_files'));native=rows(R/'gdt278_native_event_inventory.tsv');ck('native_no_f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));cap=rows(R/'gdt293_capacity.tsv');ck('capacity_shape',len(cap)==8 and d['capacity_sha256']==sha(R/'gdt293_capacity.tsv'))
 for panel in d['panels']:
  ev=[x for x in native if x['control_id']==panel];fol=defaultdict(set)
  for x in ev:fol[x['page_host']].add(x['physical_folio'])
  eligible=[x for x in ev if len(fol[x['page_host']])>=2];q=next(x for x in cap if x['control_id']==panel)
  ck('capacity:'+panel,int(q['events'])==len(ev)==8448 and int(q['folios'])==len({x['physical_folio'] for x in ev}) and int(q['exact_hosts'])==len(fol) and int(q['cross_folio_hosts'])==sum(len(v)>=2 for v in fol.values()) and int(q['eligible_events'])==len(eligible) and int(q['joint_renderer_classes'])==len({'|'.join(x[k] for k in COMP) for x in ev}))
 mf=rows(R/'gdt293_freeze_manifest.tsv');ck('manifest',len(mf)==6 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in mf));ck('manifest_bound',d['freeze_manifest_sha256']==sha(R/'gdt293_freeze_manifest.tsv'));ck('method',d['method_sha256']==sha(R/'GDT293_EXACT_HOST_RENDERER_COMPLETION_METHOD.md'));out={'schema':'GDT293_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(cc),'checks_total':len(cc),'checks':cc,'design_sha256':sha(D),'validator_sha256':sha(Path(__file__))};out['content_sha256']=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(cc)},sort_keys=True))
if __name__=='__main__':main()
