#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,importlib.util,json,re,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV,canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt366_matched_reproductive_delta';ART=EXP/'artifacts';RESULT=ART/'gdt366_result.json';FORMAL=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv';PAGESRC=ROOT/'experiments/semantic_assumptions/results/existing_human_page_annotations.tsv';FEATURES=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal/artifacts/gdt365_feature_manifest.tsv';HELPER=ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/src/run.py';OUT=ART/'gdt366_validation.json'
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def cos(a,b):return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)))
def main():
 c=[]
 def ck(n,v,d=''):c.append({'name':n,'pass':bool(v),'detail':d});assert v,(n,d)
 names=[r['formal_feature'] for r in read(FEATURES)];reader=GuardedTSV(FORMAL,selector_column='page',forbidden_prefixes=('f84',),forbidden_action='skip');raw=list(reader);rows=[r for r in raw if r['section']=='H' and r['currier']=='A' and r['hand']=='1' and re.fullmatch(r'f\d+[rv]',r['page'])];by=defaultdict(list)
 for r in rows:by[r['page']].append(r)
 folios=defaultdict(dict)
 for p in by:m=re.fullmatch(r'(f\d+)([rv])',p);folios[m.group(1)][m.group(2)]=p
 eligible={f:s for f,s in folios.items() if set(s)=={'r','v'}};allowed={p for s in eligible.values() for p in s.values()};pr=GuardedTSV(PAGESRC,selector_column='page',allowed_values=allowed,forbidden_prefixes=('f84',),forbidden_action='skip');quire={r['page']:r['quire'] for r in pr};eligible={f:s for f,s in eligible.items() if set(s.values())<=set(quire)};fs=sorted(eligible,key=lambda x:int(x[1:]));ck('folios_45',len(fs)==45,len(fs));ck('targets_present',{'f4','f8','f17'}<=set(fs));ck('no_f84',not any(p.startswith('f84') for s in eligible.values() for p in s.values()))
 spec=importlib.util.spec_from_file_location('gdt363_validator',HELPER);assert spec and spec.loader;g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);vals={p:g.family_events(by[p])[0] for p in allowed};strict={p:g.family_events([r for r in by[p] if r['strict_zero_alternative']=='1'])[0] for p in allowed};pages=sorted(allowed);idx={p:i for i,p in enumerate(pages)};X=np.asarray([[vals[p].get(n,0) for n in names] for p in pages]);XS=np.asarray([[strict[p].get(n,0) for n in names] for p in pages]);sd=X.std(0);sds=XS.std(0);Z=X[:,sd>1e-12]/sd[sd>1e-12];ZS=XS[:,sds>1e-12]/sds[sds>1e-12];delta={f:Z[idx[eligible[f]['r']]]-Z[idx[eligible[f]['v']]] for f in fs};deltas={f:ZS[idx[eligible[f]['r']]]-ZS[idx[eligible[f]['v']]] for f in fs};obs=cos(delta['f4'],-delta['f17']);strict_obs=cos(deltas['f4'],-deltas['f17']);ck('observed',abs(obs+0.06777984620647914)<1e-12,obs);ck('strict',abs(strict_obs+0.09970409984290764)<1e-12,strict_obs)
 null=[]
 for i,a in enumerate(fs):
  for b in fs[i+1:]:
   if quire[eligible[a]['r']]==quire[eligible[b]['r']]:continue
   base=cos(delta[a],delta[b]);null += [base,-base,-base,base]
 tail=sum(x>=obs-1e-15 for x in null);ck('null_3508',len(null)==3508,len(null));ck('tail_2666',tail==2666,tail);ck('p',abs(tail/len(null)-.7599771949828963)<1e-14)
 inv=read(ART/'gdt366_null_folio_inventory.tsv');ck('inventory',len(inv)==45 and {r['physical_folio'] for r in inv}==set(fs));result=json.loads(RESULT.read_text());q=dict(result);d=q.pop('content_hash');ck('status',result['status']=='MATCHED_DELTA_NOT_ALIGNED');ck('result_math',result['primary']['null_tail']==tail and result['primary']['null_size']==len(null));ck('content_hash',hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d);ck('input_hashes',all(sha256_file(ROOT/k)==v for k,v in result['inputs'].items()));ck('implementation_hashes',all(sha256_file(ROOT/k)==v for k,v in result['implementation'].items()));ck('output_hashes',all(sha256_file(ROOT/k)==v for k,v in result['outputs'].items()));report=(EXP/'REPORT.md').read_text();ck('report_result','cosine **-0.067780**' in report);ck('report_ceiling','Nothing here identifies BERRY, FLOWER' in report);ck('report_f84','retained no f84 data' in report)
 p={'schema':'GDT366_VALIDATION_V1','status':'PASS','checks':c,'pass_count':sum(x['pass'] for x in c),'check_count':len(c),'scope':'INDEPENDENT_GUARDED_SOURCE_FEATURE_DELTA_AND_EXACT_NULL_RECONSTRUCTION','result_sha256':sha256_file(RESULT),'validator_sha256':sha256_file(Path(__file__)),'documents':{str(x.relative_to(ROOT)):sha256_file(x) for x in (EXP/'METHOD.md',EXP/'REPORT.md')},'f84_accessed':False};p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();OUT.write_bytes(canonical_json_bytes(p));print(f"PASS {p['pass_count']}/{p['check_count']}")
if __name__=='__main__':main()
