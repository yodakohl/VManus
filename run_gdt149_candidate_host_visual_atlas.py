#!/usr/bin/env python3
"""Post-hoc visual-feature atlas for four GDT148 PAGE_HOST candidates."""
import csv, hashlib, json, random
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
SOURCE=R/'gdt062_right_family_inventory.tsv';VIS=R/'gdt137_herbal_visual_feature_inventory.tsv';P148=R/'gdt148_result.json';SHARED=R/'gdt148_shared_host_candidates.tsv'
METHOD=R/'GDT149_CANDIDATE_HOST_VISUAL_ATLAS_METHOD.md';REPORT=R/'GDT149_CANDIDATE_HOST_VISUAL_ATLAS_REPORT.md';ATLAS=R/'gdt149_candidate_host_visual_atlas.tsv';OCC=R/'gdt149_candidate_host_occurrences.tsv';COUNTER=R/'gdt149_counterexamples.tsv';RESULT=R/'gdt149_result.json'
HOSTS=('pch','olo','kor','oko');FEATURES=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS');WORLDS=100000;SENS_WORLDS=50000;SEED=149148
ORIGIN={'pch':('MHI005','f50r','f6r'),'olo':('MHI006','f19r','f2v'),'kor':('MHI007','f90r1','f3v'),'oko':('MHI007','f90r1','f3v')}
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def strata(rows):
 g=defaultdict(list)
 for i,x in enumerate(rows):g[(x['currier'],x['hand'],x['illustration_profile'])].append(i)
 return list(g.values())
def expected(X,Y,groups):
 e=np.zeros((len(X),Y.shape[1]))
 for ii in groups:e+=X[:,ii].sum(1)[:,None]*Y[ii].mean(0)[None,:]
 return e
def permute_scores(X,Y,groups,n,seed):
 e=expected(X,Y,groups);rng=random.Random(seed);out=np.zeros((n,len(X),Y.shape[1]),dtype=np.float32);base=np.arange(len(Y))
 for w in range(n):
  p=base.copy()
  for ii in groups:
   q=ii[:];rng.shuffle(q);p[ii]=q
  out[w]=X@Y[p]-e
 return X@Y-e,out

vis=read(VIS);pages=[x['page'] for x in vis];assert len(vis)==127 and not any(p.startswith('f84') for p in pages)
shared=read(SHARED);assert {x['page_host'] for x in shared if x['relation_id']=='MHI005' and x['rarity_rank_within_pair']=='1'}=={'pch'}
assert {x['page_host'] for x in shared if x['relation_id']=='MHI006' and x['rarity_rank_within_pair']=='1'}=={'olo'}
assert [x['page_host'] for x in shared if x['relation_id']=='MHI007' and int(x['rarity_rank_within_pair'])<=2]==['kor','oko']
by=defaultdict(list);f84r=0;other=0
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84r'):f84r+=1;continue
  if x['page'].startswith('f84'):other+=1;continue
  if x['page'] in pages and x['page_host'] in HOSTS:by[x['page_host']].append(x)
assert f84r==0
X=np.array([[any(x['page']==p for x in by[h]) for p in pages] for h in HOSTS],float);Y=np.array([[int(x[f]) for f in FEATURES] for x in vis],float);groups=strata(vis);obs,null=permute_scores(X,Y,groups,WORLDS,SEED)
mu=null.mean(0);sd=null.std(0);sd[sd==0]=1;z=(obs-mu)/sd;zn=(null-mu)/sd;mx=zn.reshape(WORLDS,-1).max(1)
sens={}
for a,h in enumerate(HOSTS):
 excluded=set(ORIGIN[h][1:]);keep=[i for i,p in enumerate(pages) if p not in excluded];rv=[vis[i] for i in keep];xx=X[a:a+1,keep];yy=Y[keep];oo,nn=permute_scores(xx,yy,strata(rv),SENS_WORLDS,SEED+100+a);sens[h]=(oo[0],nn[:,0,:],xx[0],yy)
rows=[]
for a,h in enumerate(HOSTS):
 for b,f in enumerate(FEATURES):
  so,sn,sx,sy=sens[h];local=float(np.mean(null[:,a,b]>=obs[a,b]-1e-12));sp=float(np.mean(sn[:,b]>=so[b]-1e-12));maxp=float(np.mean(mx>=z[a,b]-1e-12))
  label='INTERESTING_EXPLORATORY' if maxp<=.05 else 'PROVISIONAL_POSTSELECTED' if local<=.05 and so[b]>0 else 'WEAK' if local<=.10 else 'NO_SIGNAL'
  rows.append({'page_host':h,'origin_relation':ORIGIN[h][0],'visual_feature':f,'host_pages':int(X[a].sum()),'feature_positive_pages':int(Y[:,b].sum()),'host_feature_positive_pages':int(np.sum(X[a]*Y[:,b])),'within_stratum_effect':float(obs[a,b]),'standardized_effect_z':float(z[a,b]),'local_enrichment_p':local,'max_48_p':maxp,'endpoint_excluded_host_pages':int(sx.sum()),'endpoint_excluded_host_feature_positive_pages':int(np.sum(sx*sy[:,b])),'endpoint_excluded_effect':float(so[b]),'endpoint_excluded_local_p':sp,'label':label,'semantic_role':'UNASSIGNED'})
rows.sort(key=lambda x:(-float(x['standardized_effect_z']),x['page_host'],x['visual_feature']));write(ATLAS,clean(rows))
occ=[]
vmap={x['page']:x for x in vis}
for h in HOSTS:
 for x in sorted(by[h],key=lambda q:(q['page'],q['locus'],int(q['group_index']))):
  occ.append({'page_host':h,'origin_relation':ORIGIN[h][0],'locus':x['locus'],'page':x['page'],'physical_folio':x['physical_folio'],'currier':x['currier'],'hand':x['hand'],'surface_token':x['token'],'wrapper':x['wrapper'],'local_frame':x['local_frame'],'right_family':x['right_family'],'dy_closure':x['dy_closure'],'b3':x['b3'],'visible_positive_features':'|'.join(f for f in FEATURES if vmap[x['page']][f]=='1'),'semantic_role':'UNASSIGNED'})
write(OCC,occ)
lead=next(x for x in rows if x['page_host']=='kor' and x['visual_feature']=='BULB_OR_TUBER_ROOT')
counter=[
 {'type':'SEARCH_CORRECTION_FAILURE','item':'KOR_BULB_OR_TUBER_ROOT','value':lead['max_48_p'],'detail':'The strongest local cell does not survive the fixed four-host by twelve-feature max correction.'},
 {'type':'DIRECT_RELATION_COUNTEREXAMPLE','item':'f3v','value':0,'detail':'The MHI007 target is not marked BULB_OR_TUBER_ROOT by the frozen GDT137 feature inventory despite the human bulbs relation statement.'},
 {'type':'HOST_COUNTEREXAMPLES','item':'KOR_NON_BULB_PAGES','value':int(lead['host_pages'])-int(lead['host_feature_positive_pages']),'detail':'Five of eight Herbal pages containing exact KOR lack the frozen bulb/tuber-root feature.'},
 {'type':'ENDPOINT_EXCLUDED_WEAKNESS','item':'KOR_BULB_OR_TUBER_ROOT','value':lead['endpoint_excluded_local_p'],'detail':'After removing both MHI007 pages, the direction remains but is only weak.'},
 {'type':'RELATION_CLASS_DIRECTION_CONFLICT','item':'OLO_BULB_OR_TUBER_ROOT','value':'MHI006_FLOWER_ORIGIN','detail':'OLO was nominated by a flower-similarity relation, yet its only weak visual tendency is bulb/root rather than a flower feature.'},
 {'type':'WHOLE_PAGE_NO_OWNERSHIP','item':'ALL_CANDIDATES','value':'NA','detail':'Candidate occurrences are prose/page presences, not authorially owned plant labels.'},
 {'type':'COARSE_VISUAL_SCHEMA','item':'GDT137_12_FEATURES','value':12,'detail':'Absence means no catalogue regex hit, not a verified visual negative.'},
 {'type':'EXPOSED_POSTSELECTION','item':'GDT148_CANDIDATES','value':4,'detail':'Candidates were nominated after relation retrieval; this is hypothesis generation only.'},
]
write(COUNTER,counter)
status='KOR_BULB_OR_TUBER_ROOT_PROVISIONAL_POSTSELECTED_SEED' if lead['label']=='PROVISIONAL_POSTSELECTED' else 'CANDIDATE_HOST_VISUAL_ATLAS_NO_SIGNAL'
REPORT.write_text(f"""# GDT149 — candidate-host visual atlas

## Outcome

**{status}**

The strongest of the fixed 48 host/feature cells is exact `kor` versus the pre-existing `BULB_OR_TUBER_ROOT` page feature. `kor` occurs on {lead['host_pages']} Herbal pages; {lead['host_feature_positive_pages']} carry the feature. The Currier/hand/illustration-profile matched effect is {float(lead['within_stratum_effect']):+.3f} (z {float(lead['standardized_effect_z']):+.3f}, local p={float(lead['local_enrichment_p']):.5f}), but the maximum-over-48 p is {float(lead['max_48_p']):.5f}. Removing both MHI007 relation pages leaves {lead['endpoint_excluded_host_feature_positive_pages']}/{lead['endpoint_excluded_host_pages']} positive pages and a positive effect (local p={float(lead['endpoint_excluded_local_p']):.5f}).

This is a concrete but dirty semantic seed: future new Herbal observations containing exact `kor` can prospectively predict an elevated chance of bulb/tuber-root geometry. It is not a gloss. Five of eight current `kor` pages lack the feature, the MHI007 target f3v itself lacks the frozen flag, and catalogue-regex absence is not a verified visual negative. `olo` has a weaker bulb/root tendency even though it was nominated by a flower-similarity relation, a direct warning that the relation witnesses need not encode the named component. `pch` and `oko` produce no corrected feature association.

All 48 cells, all {len(occ)} candidate occurrences, relation-endpoint-excluded sensitivities, and counterexamples are published. No image was opened. The source has zero f84r rows; {other} other-f84 rows were rejected before retention and no new f84r access occurred. No host is assigned a plant-part meaning, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.
""",encoding='utf8')
result={'schema':'GDT149_CANDIDATE_HOST_VISUAL_ATLAS_RESULT_V1','status':status,'herbal_pages':len(vis),'candidate_hosts':list(HOSTS),'visual_features':list(FEATURES),'cells':len(rows),'worlds':WORLDS,'sensitivity_worlds':SENS_WORLDS,'seed':SEED,'lead':lead,'interpretation':'Post-hoc candidate semantic atlas nominates a weak exact-KOR/bulb-or-tuber-root page association.','claim_ceiling':'Prospective visual-feature seed only; no host meaning, role, word, morpheme, POS, sound, language, plaintext, or translation.','f84':{'actual_source_f84r_rows':f84r,'rejected_other_f84_rows':other,'retained_or_scored_f84_rows':0,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (SOURCE,VIS,P148,SHARED)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (ATLAS,OCC,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':status,'lead_local_p':lead['local_enrichment_p'],'lead_max48_p':lead['max_48_p'],'endpoint_excluded_p':lead['endpoint_excluded_local_p']},sort_keys=True))
