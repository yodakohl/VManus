#!/usr/bin/env python3
"""Independent, nonimporting validation of GDT297."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent;RESULT=R/'gdt297_result.json';OUT=R/'gdt297_validation.json';C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3')
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def ren(r):return '|'.join(r[x] for x in C)
def close(a,b):return abs(float(a)-float(b))<=5e-12

def main():
 checks=[]
 def ck(name,ok):
  checks.append((name,bool(ok)))
  if not ok:raise AssertionError(name)
 result=json.loads(RESULT.read_text());ck('result_content',result['content_sha256']==rch(result));ck('status',result['status']=='EXACT_HOST_RENDERER_IS_WITHIN_HOST_SURFACE_ALIAS')
 for group in ('inputs','documents','implementation','outputs'):
  for name,digest in result[group].items():ck(f'{group}:{name}',sha(R/name)==digest)
 atlas={x['page_host']:x for x in read(R/'gdt296_host_renderer_atlas.tsv')};published={x['page_host']:x for x in read(R/'gdt297_host_surface_alias.tsv')};maps=read(R/'gdt297_renderer_surface_map.tsv');counter=read(R/'gdt297_counterexamples.tsv')
 native=read(R/'gdt278_native_event_inventory.tsv');source=read(R/'gdt276_event_inventory.tsv');ck('no_f84_native',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native));ck('no_f84_source',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in source));source_by={x['observation_id']:x for x in source};events=[x for x in native if x['control_id']=='VOYNICH_REFERENCE' and x['page_host'] in atlas];ck('events',len(events)==5715);ck('hosts',set(published)==set(atlas) and len(atlas)==59)
 alphabet=sorted({ren(x) for x in native if x['control_id']=='VOYNICH_REFERENCE'});rank={x:i for i,x in enumerate(alphabet)};expected_maps=[];bijections=single=canonical=counters=0
 for host in sorted(atlas):
  ev=[x for x in events if x['page_host']==host];pairs=Counter((ren(x),source_by[x['observation_id']]['raw_token']) for x in ev);r2s=defaultdict(set);s2r=defaultdict(set)
  for (rr,s),n in pairs.items():r2s[rr].add(s);s2r[s].add(rr);expected_maps.append((host,rr,s,n,len({x['physical_folio'] for x in ev if ren(x)==rr and source_by[x['observation_id']]['raw_token']==s})))
  bij=all(len(v)==1 for v in r2s.values()) and all(len(v)==1 for v in s2r.values());bijections+=bij;single+=len(s2r)==1
  dominant=max(pairs,key=lambda x:(pairs[x],x[0],x[1]));top=correct=0
  for held in sorted({x['physical_folio'] for x in ev}):
   train=[x for x in ev if x['physical_folio']!=held];test=[x for x in ev if x['physical_folio']==held];counts=Counter(ren(x) for x in train);pred=max(alphabet,key=lambda x:(counts[x],-rank[x]));correct+=sum(ren(x)==pred for x in test);top+=len(test)
  acc=correct/top;a=atlas[host];p=published[host];cls=a['classification'];canonical+=cls=='CANONICAL_RENDERER_CANDIDATE';counters+=cls=='CANONICAL_RENDERER_CANDIDATE' and len(s2r)>1
  ck(f'host:{host}',p['gdt296_classification']==cls and int(p['events'])==len(ev) and int(p['folios'])==len({x['physical_folio'] for x in ev}) and int(p['renderer_types'])==len(r2s) and int(p['raw_surface_types'])==len(s2r) and int(p['renderer_to_surface_function'])==all(len(v)==1 for v in r2s.values()) and int(p['surface_to_renderer_function'])==all(len(v)==1 for v in s2r.values()) and int(p['within_host_bijection'])==bij and p['dominant_renderer_tuple']==dominant[0] and p['dominant_raw_token']==dominant[1] and int(p['dominant_events'])==pairs[dominant] and close(p['dominant_share'],pairs[dominant]/len(ev)) and close(p['held_renderer_top1'],acc) and close(p['held_whole_surface_top1_equivalent'],acc) and int(p['strict_single_surface'])==(len(s2r)==1))
 actual_maps=sorted((x['page_host'],x['renderer_tuple'],x['raw_token'],int(x['events']),int(x['folios'])) for x in maps);ck('map_rows',actual_maps==sorted(expected_maps));ck('bijection_count',bijections==result['within_host_bijection_hosts']==59);ck('single_count',single==result['strict_single_surface_hosts']==1);ck('canonical_count',canonical==result['canonical_candidates']==5);ck('counter_count',counters==result['canonical_multi_surface_counterexamples']==len(counter)==4)
 text=(R/'GDT297_HOST_SURFACE_ALIAS_AUDIT_REPORT.md').read_text();ck('report',result['status'] in text and 'no word' in text and 'f84' in text)
 cats=Counter(x.split(':',1)[0] for x,ok in checks);out={'schema':'GDT297_HOST_SURFACE_ALIAS_AUDIT_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_SOURCE_JOIN_MAPPING_FOLD_TOP1_RECONSTRUCTION','checks_total':len(checks),'checks_passed':sum(ok for x,ok in checks),'check_categories':dict(sorted(cats.items())),'failed_checks':[x for x,ok in checks if not ok],'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=rch(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'hosts':len(atlas)},sort_keys=True))
if __name__=='__main__':main()
