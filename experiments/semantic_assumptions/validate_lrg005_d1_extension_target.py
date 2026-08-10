#!/usr/bin/env python3
"""Clean-room reconstruction of the frozen LRG005 target."""
from __future__ import annotations
import os
for v in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[v]="32"
import csv,hashlib,json,math,re
from collections import Counter
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=HERE/"results";FREEZE=HERE/"LRG005_TARGET_FREEZE.json";G=R/"source_sta_family_consensus_groups.tsv";P=R/"lrg005_d1_extension_capacity.tsv";Q=R/"lrg005_d1_extension_quotas.tsv";SC=R/"lrg005_d1_specificity_capacity.json";PROD=R/"lrg005_d1_extension_target.json";REPORT=R/"lrg005_d1_extension_target_report.md";OUT=R/"lrg005_d1_extension_target_validation.json";OUTR=R/"lrg005_d1_extension_target_validation_report.md";F=("zl_sta_codes","it_sta_codes","rf_sta_codes");A=8192;SEED=510052026;checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ah(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def fol(p):
 m=re.fullmatch(r'(f\d+)(?:[rv](?:\d+)?)?',p);need(m is not None,'page');return m.group(1)
def uid(x):return 'LRG005-U'+hashlib.sha256(('LRG005-D1|'+x).encode()).hexdigest()[:20]
def seq(r):return tuple(r[x] for x in F)
def main():
 need(PROD.is_file() and REPORT.is_file(),'target absent');freeze=json.loads(FREEZE.read_text());need(freeze['status']=='FROZEN_LRG005_D1_EXTENSION_TARGET','freeze');need(freeze['result_paths']==[str(p.relative_to(ROOT)) for p in (PROD,REPORT,OUT,OUTR)],'result paths')
 for rel,expected in freeze['frozen_files'].items():need(sha(ROOT/rel)==expected,'freeze drift')
 groups=tab(G);panel=tab(P);quotas=tab(Q);lookup={uid(r['consensus_group_id']):r for r in groups};need(len(panel)==536 and len(quotas)==68 and all(r['unit_id'] in lookup for r in panel),'join');prose=[r for r in groups if r['strict_zero_alternative']=='1' and r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE'];b=Counter();a=Counter();d=Counter()
 for r in prose:
  f=fol(r['page']);s=seq(r);b[f,s]+=1;parts=[x.split() for x in s]
  if all(len(x)>=2 for x in parts):
   suffix=tuple(' '.join(x[1:]) for x in parts);a[f,suffix]+=1
   if all(x[0]=='D1' for x in parts):d[f,suffix]+=1
 def total(c):
  z=Counter()
  for (_f,s),n in c.items():z[s]+=n
  return z
 tb,ta,td=map(total,(b,a,d));scores=[];labels=[]
 for p in panel:
  r=lookup[p['unit_id']];f=p['physical_folio'];s=seq(r);nb=tb[s]-b[f,s];na=ta[s]-a[f,s];nd=td[s]-d[f,s];no=na-nd;need(min(nb,no,nd)>=0,'counts');scores.append((math.log((nd+.5)/(nb+.5)),math.log((nd+.5)/(no+.5))));labels.append(1 if r['kind']=='L' else 0 if r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE' else -1)
 s=np.asarray(scores);y=np.asarray(labels,dtype=np.int8);need(-1 not in y and int(y.sum())==144,'roles');need(ah(s)==json.loads(SC.read_text())['score_matrix_sha256'],'score hash');cell=np.asarray([r['cell_id'] for r in panel]);folio=np.asarray([r['physical_folio'] for r in panel]);section=np.asarray([r['section'] for r in panel]);quota={r['cell_id']:int(r['label_rows']) for r in quotas};cells=tuple(sorted(quota));folios=tuple(sorted(set(folio),key=lambda x:int(x[1:])));need(len(folios)==13,'folios')
 for c in cells:need(int(y[cell==c].sum())==quota[c],'quota')
 coef=np.zeros((A,len(y)));rng=np.random.default_rng(SEED)
 for c in cells:
  idx=np.flatnonzero(cell==c);f=str(folio[idx[0]]);nc=len(set(cell[folio==f]));h=quota[c];lo=len(idx)-h;coef[:,idx]=-1/(len(folios)*nc*lo);chosen=idx[np.argpartition(rng.random((A,len(idx))),h-1,axis=1)[:,:h]];coef[np.arange(A)[:,None],chosen]=1/(len(folios)*nc*h)
 null=coef@s;fe=[]
 for f in folios:
  vals=[]
  for c in sorted(set(cell[folio==f])):
   idx=np.flatnonzero(cell==c);hi=idx[y[idx]==1];lo=idx[y[idx]==0];vals.append(s[hi].mean(0)-s[lo].mean(0))
  fe.append(np.stack(vals).mean(0))
 fe=np.stack(fe);nums=np.asarray([int(f[1:]) for f in folios]);sf=np.asarray([str(section[np.flatnonzero(folio==f)[0]]) for f in folios]);metrics=[]
 for j,name in enumerate(('D1_BARE','D1_OTHER')):
  vals=fe[:,j];t=float(vals.mean());mu=float(null[:,j].mean());sd=float(null[:,j].std(ddof=0));p=(1+int(np.count_nonzero(null[:,j]>=t)))/(A+1);z=(t-mu)/sd;sec={x:float(vals[sf==x].mean()) for x in ('B','P')};par={'ODD':float(vals[nums%2==1].mean()),'EVEN':float(vals[nums%2==0].mean())};sb=min(sec.values())/max(sec.values()) if max(sec.values())>0 else float('-inf');pb=min(par.values())/max(par.values()) if max(par.values())>0 else float('-inf');dele=[float(np.delete(vals,k).mean()) for k in range(13)];con=float(np.max(np.abs(vals))/np.abs(vals).sum());gates={'p_at_most_001':p<=.01,'z_at_least_3':z>=3,'effect_at_least_010':t>=.10,'support_at_least_10':int(np.count_nonzero(vals>0))>=10,'both_sections_at_least_005':min(sec.values())>=.05,'section_balance_at_least_035':sb>=.35,'both_parities_at_least_005':min(par.values())>=.05,'parity_balance_at_least_035':pb>=.35,'all_deletions_at_least_005':min(dele)>=.05,'concentration_at_most_030':con<=.30};metrics.append({'channel':name,'effect':t,'null_mean':mu,'null_sd':sd,'z':z,'p':p,'positive_folios':int(np.count_nonzero(vals>0)),'folio_effects':{f:float(v) for f,v in zip(folios,vals,strict=True)},'section_effects':sec,'section_balance_ratio':sb,'parity_effects':par,'parity_balance_ratio':pb,'minimum_deletion':min(dele),'maximum_absolute_folio_concentration':con,'null_sha256':ah(null[:,j]),'gates':gates,'passes':all(gates.values())})
 evaluation={'metrics':metrics,'joint_pass':all(m['passes'] for m in metrics),'score_sha256':ah(s),'label_sha256':ah(y)};passed=evaluation['joint_pass'];status='CONFIRMED_D1_SPECIFIC_CROSS_REGISTER_EXTENSION_RELATION' if passed else 'FINAL_NONCONFIRMATION_LRG005_D1_EXTENSION';decision='AUTHORIZE_D1_EXTENDED_AND_BARE_A_STRUCTURAL_TAGS_AFTER_VALIDATION' if passed else 'CLOSE_EXACT_LRG005_RELATION';prod=json.loads(PROD.read_text());expected={'status':status,'decision':decision,'claim_ceiling':'A pass establishes only a D1-specific exact cross-register extended/bare construction relation among conditioned A-initial groups. It does not establish a prefix classifier morpheme POS sound word language cipher meaning plaintext or translation.','freeze_sha256':sha(FREEZE),'score_capacity_sha256':sha(SC),'calibration_sha256':sha(R/'lrg005_target_blind_calibration.json'),'calibration_validation_sha256':sha(R/'lrg005_target_blind_calibration_validation.json'),'counts':{'rows':536,'labels':144,'prose':392,'cells':68,'folios':13,'channels':2},'coefficient_sha256':ah(coef),'score_matrix_sha256':ah(s),'evaluation':evaluation,'individual_rows_emitted':False,'row_scores_emitted':False,'member_sequences_emitted':False,'source_surfaces_emitted':False};need(prod==expected,'full result');lines=['# LRG005 D1-specific extension target','',f'Status: **{status}**.','',f'Joint two-channel pass: **{passed}**.','','| channel | effect | p | z | positive folios | B | P | odd | even | section balance | parity balance | min deletion | concentration | pass |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|',*[f"| {m['channel']} | {m['effect']:+.9f} | {m['p']:.9f} | {m['z']:.4f} | {m['positive_folios']}/13 | {m['section_effects']['B']:+.9f} | {m['section_effects']['P']:+.9f} | {m['parity_effects']['ODD']:+.9f} | {m['parity_effects']['EVEN']:+.9f} | {m['section_balance_ratio']:.4f} | {m['parity_balance_ratio']:.4f} | {m['minimum_deletion']:+.9f} | {m['maximum_absolute_folio_concentration']:.4f} | {m['passes']} |" for m in metrics],'',f'Decision: **{decision}**.','','No row score, member sequence, source surface, prefix function, word, POS, sound, meaning, plaintext, or translation is emitted.',''];need(REPORT.read_text()=='\n'.join(lines),'report');result={'status':'PASS_CLEAN_LRG005_TARGET_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'report_sha256':sha(REPORT),'registered_relation':bool(passed)};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG005 target validation','',f"Status: **{result['status']}**.",'',f"Clean code reconstructs the score matrix, real role quotas, both statistics, nulls, folio/section/parity gates, decision, and report in **{checks}** checks with zero discrepancies.",'','The result remains structural only; no prefix function or meaning follows.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
