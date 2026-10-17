#!/usr/bin/env python3
"""One bounded source-forward wordgraph case; reuse frozen exact search code."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def save(n,x):
 p=A/n;assert not p.exists(),str(p);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def config(locked=True):
 s=read(E/'src/SPEC.json')
 if locked:
  for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 for p,h in s['frozen_predecessor_sha256'].items():assert sha(ROOT/p)==h,p
 assert sha(ROOT/s['source_xml'])==s['source_sha256']
 return s
def inputs(s):
 data=read(A/'SOURCE_PROJECTION.json');rs=[r['words'] for r in data['records']];assert rs and all(rs)
 assert sorted({w for r in rs for w in r})==data['words']
 assert sorted(set(''.join(data['words'])))==data['alphabet']
 assert sorted({(a,b) for r in rs for a,b in zip(r,r[1:])})==[tuple(p) for p in data['edges']]
 return data,rs
def engine():return module('gdt1426_old_dfs','experiments/yolo/gdt1420_forward_merger_shared_key/src/run.py')
def prepare():
 s=config(False);parser=module('gdt1426_old_parser','experiments/yolo/gdt1418_latent_source_bigram_key/src/run.py')
 old=read(ROOT/s['native_source']);rows=[x for x in old['groups'] if x['edition']==s['native_edition']];assert len(rows)==s['native_groups']==59
 raw=[x['group']['ivtff_group_raw'] for x in rows];groups=[parser.parse(w,s['signs']) for w in raw];assert all(groups)
 assert all(''.join(g)==w for w,g in zip(raw,groups))
 save('NATIVE_INPUT.json',{'source':s['native_source'],'source_sha256':sha(ROOT/s['native_source']),'edition':'IT2a','loci':[x['locus'] for x in rows],'ids':[x['group']['source_group_id'] for x in rows],'raw_groups':raw,'groups':groups,'parse_contract':'Existing fixed22unit unique segmentation, no E/C meanings or new raw query','group_count':59,'active_units':sorted({u for g in groups for u in g})})
 print(json.dumps({'prepared_native_groups':59,'active_units':len({u for g in groups for u in g})}))
def gate():
 s=config();data,rs=inputs(s);old=engine();fixtures=old.controls();alpha=data['alphabet'];idx=next((i for i,r in enumerate(rs) if len(r)>=s['control_words']),None)
 if idx is None:
  save('CONTROL_PRIMARY.json',{'status':'DOMAIN_ABSENT','reason':'No accepted source record of32words'});return
 words=rs[idx][:s['control_words']];key={c:s['signs'][j%s['control_mapping_modulo']] for j,c in enumerate(alpha)};groups=[[key[c] for c in w] for w in words];active=set(''.join(words));by={}
 for c,u in key.items():by.setdefault(u,[]).append(c)
 packet={'source_record_index':idx,'source_body_child_index':data['records'][idx]['body_child_index'],'planted_words':words,'planted_key':key,'groups':groups,'active_collision_classes':[v for v in by.values() if len([c for c in v if c in active])>=2],'source_free_controls':fixtures,'gate':'ANY valid full word/key/edge certificate; no exact-recovery or uniqueness requirement','source_projection_sha256':sha(A/'SOURCE_PROJECTION.json')}
 save('CONTROL_INPUT.json',packet);t=time.monotonic();result=old.solve(groups,rs,s,s['primary_seconds']);elapsed=time.monotonic()-t
 save('CONTROL_PRIMARY.json',{'status':result['status'],'result':result,'elapsed_seconds':elapsed,'input_sha256':sha(A/'CONTROL_INPUT.json')});print(json.dumps({'primary_control':result['status'],'elapsed_seconds':elapsed}),flush=True)
def native():
 s=config();g=read(A/'GATE_VALIDATION.json')
 if g['status']!='PASS':
  save('NATIVE_STOP.json',{'status':'CONTROL_STOP_NO_NATIVE_TEST','native_cases_executed':0,'reason':g['status']});print('CONTROL_STOP_NO_NATIVE_TEST');return
 data,rs=inputs(s);p=read(A/'NATIVE_INPUT.json');t=time.monotonic();result=engine().solve(p['groups'],rs,s,s['primary_seconds']);elapsed=time.monotonic()-t
 save('RESULT.json',{'experiment_id':'GDT1426','status':result['status'],'result':result,'elapsed_seconds':elapsed,'groups':p['groups'],'native_input_sha256':sha(A/'NATIVE_INPUT.json'),'source_projection_sha256':sha(A/'SOURCE_PROJECTION.json'),'gate_sha256':sha(A/'GATE_VALIDATION.json'),'claim_ceiling':s['claim_ceiling']});print(json.dumps({'primary_native':result['status'],'elapsed_seconds':elapsed}),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');a=p.parse_args()
 if a.prepare:prepare()
 elif a.gate:gate()
 elif a.native:native()
 else:p.error('choose one phase')
if __name__=='__main__':main()
