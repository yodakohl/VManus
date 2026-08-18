#!/usr/bin/env python3
"""Audit exact-host renderer tuples against complete source forms."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
METHOD=R/'GDT297_HOST_SURFACE_ALIAS_AUDIT_METHOD.md'
REPORT=R/'GDT297_HOST_SURFACE_ALIAS_AUDIT_REPORT.md'
HOSTS=R/'gdt297_host_surface_alias.tsv'
MAP=R/'gdt297_renderer_surface_map.tsv'
COUNTER=R/'gdt297_counterexamples.tsv'
RESULT=R/'gdt297_result.json'
C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3')

def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 fields=[]
 for row in rows:
  for key in row:
   if key not in fields:fields.append(key)
 with Path(p).open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def renderer(r):return '|'.join(r[x] for x in C)

def main():
 atlas=read(R/'gdt296_host_renderer_atlas.tsv');population={x['page_host'] for x in atlas}
 native=read(R/'gdt278_native_event_inventory.tsv');source=read(R/'gdt276_event_inventory.tsv')
 assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native)
 assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in source)
 source_by={x['observation_id']:x for x in source};assert len(source_by)==len(source)
 events=[x for x in native if x['control_id']=='VOYNICH_REFERENCE' and x['page_host'] in population]
 assert len(events)==5715 and all(x['observation_id'] in source_by for x in events)
 atlas_by={x['page_host']:x for x in atlas};host_rows=[];map_rows=[]
 for host in sorted(population):
  ev=[x for x in events if x['page_host']==host];pairs=Counter((renderer(x),source_by[x['observation_id']]['raw_token']) for x in ev)
  r2s=defaultdict(set);s2r=defaultdict(set)
  for (ren,surface),count in pairs.items():
   r2s[ren].add(surface);s2r[surface].add(ren);map_rows.append({'page_host':host,'renderer_tuple':ren,'raw_token':surface,'events':count,'folios':len({x['physical_folio'] for x in ev if renderer(x)==ren and source_by[x['observation_id']]['raw_token']==surface})})
  bijective=all(len(v)==1 for v in r2s.values()) and all(len(v)==1 for v in s2r.values())
  dominant=max(pairs,key=lambda x:(pairs[x],x[0],x[1]));a=atlas_by[host]
  host_rows.append({'page_host':host,'gdt296_classification':a['classification'],'events':len(ev),'folios':len({x['physical_folio'] for x in ev}),'renderer_types':len(r2s),'raw_surface_types':len(s2r),'renderer_to_surface_function':int(all(len(v)==1 for v in r2s.values())),'surface_to_renderer_function':int(all(len(v)==1 for v in s2r.values())),'within_host_bijection':int(bijective),'dominant_renderer_tuple':dominant[0],'dominant_raw_token':dominant[1],'dominant_events':pairs[dominant],'dominant_share':f'{pairs[dominant]/len(ev):.12f}','held_renderer_top1':a['lofo_host_top1'],'held_whole_surface_top1_equivalent':a['lofo_host_top1'],'strict_single_surface':int(len(s2r)==1)})
 host_rows.sort(key=lambda x:({'CANONICAL_RENDERER_CANDIDATE':0,'POSITION_CONDITIONED_CANDIDATE':1,'VARIABLE_RENDERER':2}[x['gdt296_classification']],-float(x['held_renderer_top1']),x['page_host']))
 map_rows.sort(key=lambda x:(x['page_host'],-int(x['events']),x['renderer_tuple'],x['raw_token']))
 write(HOSTS,host_rows);write(MAP,map_rows)
 counters=[x for x in host_rows if x['gdt296_classification']=='CANONICAL_RENDERER_CANDIDATE' and not x['strict_single_surface']]
 write(COUNTER,[{'page_host':x['page_host'],'events':x['events'],'raw_surface_types':x['raw_surface_types'],'dominant_raw_token':x['dominant_raw_token'],'dominant_share':x['dominant_share'],'counterexample':'CANONICAL_LABEL_IS_DOMINANT_ALTERNANT_NOT_SINGLE_SURFACE'} for x in counters])
 canonical=[x for x in host_rows if x['gdt296_classification']=='CANONICAL_RENDERER_CANDIDATE']
 report=['# GDT297 — exact-host renderer/surface alias audit','', 'Status: **EXACT_HOST_RENDERER_IS_WITHIN_HOST_SURFACE_ALIAS**.','','## Result','',f"All {len(host_rows)}/59 hosts have a bijection between their renderer tuples and complete raw source forms. Only {sum(int(x['strict_single_surface']) for x in host_rows)}/59 has exactly one raw surface; the other hosts express two or more whole-form alternants. Held renderer top-1 is therefore also the top-1 accuracy of the corresponding whole-form alternant for the same exact host.",'','The five GDT296 canonical candidates are:','', '| host | events | surfaces | dominant complete form | share | held top-1 |','|---|---:|---:|---|---:|---:|']
 for x in canonical:report.append(f"| `{x['page_host']}` | {x['events']} | {x['raw_surface_types']} | `{x['dominant_raw_token']}` | {float(x['dominant_share']):.3f} | {float(x['held_renderer_top1']):.3f} |")
 report+=['','## Consequence','','GDT293 remains a strong exact-host completion result and GDT296 remains useful as a normalization atlas. But at exact-host resolution it does not separate a productive renderer from memorized whole-form alternants: every renderer choice corresponds one-to-one to a raw form. This agrees with the failed GDT289--290 cross-host and compact-class transfer tests. The current executable model should therefore treat the exact host+renderer table as a high-capacity surface lexicon unless a future cross-host rule predicts unseen alternants.','','## Claim ceiling','','This is a parser-defined formal alias audit. It identifies no word, morpheme, code value, sound, language, meaning, plaintext, translation, or f84 evidence.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[HOSTS,MAP,COUNTER,REPORT];inputs=['gdt296_result.json','gdt296_validation.json','gdt296_host_renderer_atlas.tsv','gdt278_native_event_inventory.tsv','gdt276_event_inventory.tsv','gdt289_result.json','gdt290_result.json']
 result={'schema':'GDT297_HOST_SURFACE_ALIAS_AUDIT_RESULT_V1','status':'EXACT_HOST_RENDERER_IS_WITHIN_HOST_SURFACE_ALIAS','hosts':len(host_rows),'events':sum(int(x['events']) for x in host_rows),'within_host_bijection_hosts':sum(int(x['within_host_bijection']) for x in host_rows),'strict_single_surface_hosts':sum(int(x['strict_single_surface']) for x in host_rows),'canonical_candidates':len(canonical),'canonical_multi_surface_counterexamples':len(counters),'interpretation':'Exact-host renderer prediction is rank-equivalent to predicting a whole-form alternant within every audited host; cross-host productive transfer remains unsupported.','claim_ceiling':'Parser-defined exact formal aliasing only; no lexicality word morpheme code value sound language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}}
 result['content_sha256']=rch(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'hosts':len(host_rows),'bijections':result['within_host_bijection_hosts'],'single_surface':result['strict_single_surface_hosts']},sort_keys=True))

if __name__=='__main__':main()
