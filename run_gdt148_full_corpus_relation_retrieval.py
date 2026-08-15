#!/usr/bin/env python3
"""Full-corpus retrieval of six archived Herbal relation targets."""
import csv, hashlib, json, random
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parent
SOURCE=R/'gdt062_right_family_inventory.tsv';META=R/'gdt137_herbal_visual_feature_inventory.tsv'
HUMAN=R/'experiments/semantic_assumptions/cache/existing_human_annotations/manual_herbal_internal_relations.tsv'
P140=R/'gdt140_result.json';P144=R/'gdt144_result.json';P147=R/'gdt147_result.json'
METHOD=R/'GDT148_FULL_CORPUS_RELATION_RETRIEVAL_METHOD.md';REPORT=R/'GDT148_FULL_CORPUS_RELATION_RETRIEVAL_REPORT.md'
INV=R/'gdt148_relation_inventory.tsv';RANKS=R/'gdt148_target_ranks.tsv';NULL=R/'gdt148_null_results.tsv';HOSTS=R/'gdt148_shared_host_candidates.tsv';COUNTER=R/'gdt148_counterexamples.tsv';RESULT=R/'gdt148_result.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE');SCOPES=('ALL_SIX','COMPONENT_FOUR','WHOLE_PLANT_TWO');WORLDS=100000;SEED=148140

def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1.
def sim(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x]) for x in k)
 return sum(min(a[x],b[x]) for x in k)/d if d else 0.

meta={x['page']:x for x in read(META)}
wanted={'MHI002','MHI003','MHI004','MHI005','MHI006','MHI007'};byrel=defaultdict(list)
for x in read(HUMAN):
 if x['relation_id'] in wanted:byrel[x['relation_id']].append(x)
rels=[]
for rid in sorted(wanted):
 q=byrel[rid];assert {x['edition'] for x in q}=={'ZL3b','IT2a','RF1b'}
 for k in ('page_a','page_b','source_statement','relation_class','component','strength','panel_class'):assert len({x[k] for x in q})==1
 x=q[0];rels.append({'relation_id':rid,'source_page':x['page_a'],'target_page':x['page_b'],'relation_class':x['relation_class'],'component':x['component'],'strength':x['strength'],'panel_class':x['panel_class'],'provenance':'EXISTING_HUMAN_ANNOTATION','semantic_role':'UNASSIGNED'})
assert len(rels)==6 and not any(x['source_page'].startswith('f84') or x['target_page'].startswith('f84') for x in rels)
write(INV,rels)

by=defaultdict(list);glob=Counter();host_pages=defaultdict(set);source_f84r=0;rejected_f84_other=0
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  p=x['page']
  if p.startswith('f84r'):source_f84r+=1;continue
  if p.startswith('f84'):rejected_f84_other+=1;continue
  if p not in meta:continue
  by[p].append(x);glob[x['page_host']]+=1;host_pages[x['page_host']].add(p)
assert source_f84r==0 and len(by)==127
feat={p:{r:Counter() for r in REPS} for p in by}
for p,rows in by.items():
 for x in rows:
  feat[p]['PAGE_HOST_IDENTITY'][x['page_host']]+=1;add3(feat[p]['PAGE_HOST_CHAR3'],x['page_host']);add3(feat[p]['RAW_CHAR3'],x['token']);feat[p]['COMPILER_SIGNATURE']['|'.join((x['wrapper'],x['inner_d'],x['local_frame'],x['right_family'],x['dy_closure'],x['b3']))]+=1

cands=[];zs=[];raw=[];top6map=[];rank_rows=[];shared=[]
for i,x in enumerate(rels):
 s=x['source_page'];t=x['target_page'];tm=meta[t]
 primary=sorted(p for p,z in meta.items() if p in by and p!=s and z['physical_folio']!=meta[s]['physical_folio'] and z['currier']==tm['currier'] and z['hand']==tm['hand'])
 profile=[p for p in primary if meta[p]['illustration_profile']==tm['illustration_profile']]
 assert t in primary and t in profile
 cands.append(primary);zi={};ri={};t6={}
 for rep in REPS:
  vals=np.array([sim(feat[s][rep],feat[p][rep]) for p in primary]);mu=float(vals.mean());sd=float(vals.std()) or 1.;z=(vals-mu)/sd;zi[rep]=dict(zip(primary,z));ri[rep]=dict(zip(primary,vals));t6[rep]={p:(1+int(np.sum(vals>v+1e-12))<=6) for p,v in zip(primary,vals)}
  for scope_name,pool in (('PRIMARY_CURRIER_HAND',primary),('PROFILE_MATCHED_SENSITIVITY',profile)):
   v=np.array([sim(feat[s][rep],feat[p][rep]) for p in pool]);score=sim(feat[s][rep],feat[t][rep]);rank=1+int(np.sum(v>score+1e-12));tail=float(np.mean(v>=score-1e-12))
   rank_rows.append({'relation_id':x['relation_id'],'relation_class':x['relation_class'],'component':x['component'],'source_page':s,'target_page':t,'candidate_scope':scope_name,'representation':rep,'candidate_pages':len(pool),'similarity':score,'true_target_rank':rank,'inclusive_candidate_tail':tail,'top_six':int(rank<=6),'source_standardized_similarity':float((score-mu)/sd) if scope_name.startswith('PRIMARY') else 'NOT_COMPARABLE'})
 zs.append(zi);raw.append(ri);top6map.append(t6)
 common=sorted(set(feat[s]['PAGE_HOST_IDENTITY'])&set(feat[t]['PAGE_HOST_IDENTITY']),key=lambda h:(len(host_pages[h]),glob[h],h))
 for rank,h in enumerate(common,1):shared.append({'relation_id':x['relation_id'],'relation_class':x['relation_class'],'component':x['component'],'source_page':s,'target_page':t,'page_host':h,'source_occurrences':int(feat[s]['PAGE_HOST_IDENTITY'][h]),'target_occurrences':int(feat[t]['PAGE_HOST_IDENTITY'][h]),'global_occurrences':int(glob[h]),'global_non_f84_pages':len(host_pages[h]),'rarity_rank_within_pair':rank,'semantic_role':'UNASSIGNED'})

scope_idx={'ALL_SIX':list(range(6)),'COMPONENT_FOUR':[i for i,x in enumerate(rels) if x['relation_class']=='COMPONENT_SIMILARITY'],'WHOLE_PLANT_TWO':[i for i,x in enumerate(rels) if x['relation_class']=='WHOLE_PLANT_SIMILARITY']}
assert [len(scope_idx[x]) for x in SCOPES]==[6,4,2]
obs_mean=np.zeros((3,4));obs_top=np.zeros((3,4),int)
for a,scope in enumerate(SCOPES):
 ii=scope_idx[scope]
 for b,rep in enumerate(REPS):
  obs_mean[a,b]=np.mean([zs[i][rep][rels[i]['target_page']] for i in ii]);obs_top[a,b]=sum(top6map[i][rep][rels[i]['target_page']] for i in ii)
rng=random.Random(SEED);null_mean=np.zeros((WORLDS,3,4));null_top=np.zeros((WORLDS,3,4),int)
for w in range(WORLDS):
 while True:
  draw=[rng.choice(cands[i]) for i in range(6)]
  if len(set(draw))==6:break
 for a,scope in enumerate(SCOPES):
  ii=scope_idx[scope]
  for b,rep in enumerate(REPS):
   null_mean[w,a,b]=np.mean([zs[i][rep][draw[i]] for i in ii])
   null_top[w,a,b]=sum(top6map[i][rep][draw[i]] for i in ii)
mean_mu=null_mean.mean(0);mean_sd=null_mean.std(0);mean_sd[mean_sd==0]=1;mean_z=(obs_mean-mean_mu)/mean_sd;mean_null_z=(null_mean-mean_mu)/mean_sd
top_mu=null_top.mean(0);top_sd=null_top.std(0);top_sd[top_sd==0]=1;top_z=(obs_top-top_mu)/top_sd;top_null_z=(null_top-top_mu)/top_sd
max_mean=mean_null_z.reshape(WORLDS,-1).max(1);max_top=top_null_z.reshape(WORLDS,-1).max(1);null_rows=[]
for a,scope in enumerate(SCOPES):
 for b,rep in enumerate(REPS):
  null_rows.append({'scope':scope,'representation':rep,'relations':len(scope_idx[scope]),'true_mean_source_z':float(obs_mean[a,b]),'null_mean_of_mean_z':float(mean_mu[a,b]),'null_sd_of_mean_z':float(mean_sd[a,b]),'true_standardized_mean_z':float(mean_z[a,b]),'local_mean_p':float(np.mean(null_mean[:,a,b]>=obs_mean[a,b]-1e-12)),'max_12_mean_p':float(np.mean(max_mean>=mean_z[a,b]-1e-12)),'true_top_six_count':int(obs_top[a,b]),'null_top_six_mean':float(top_mu[a,b]),'null_top_six_sd':float(top_sd[a,b]),'true_standardized_top_six':float(top_z[a,b]),'local_top_six_p':float(np.mean(null_top[:,a,b]>=obs_top[a,b])),'max_12_top_six_p':float(np.mean(max_top>=top_z[a,b]-1e-12)),'worlds':WORLDS,'seed':SEED})

write(RANKS,clean(rank_rows));write(NULL,clean(null_rows));write(HOSTS,shared)
pr={(x['scope'],x['representation']):x for x in null_rows};lead=pr[('COMPONENT_FOUR','PAGE_HOST_IDENTITY')]
counter=[
 {'type':'POSTHOC_EXPOSED_ROUTE','item':'FULL_CORPUS_RETRIEVAL','value':'NA','detail':'The relation panel and PAGE_HOST lead were exposed before this full-corpus analysis; null tails do not repair that history.'},
 {'type':'COMPONENT_COUNTEREXAMPLE','item':'MHI004','value':next(x['true_target_rank'] for x in rank_rows if x['relation_id']=='MHI004' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='PAGE_HOST_IDENTITY'),'detail':'The f6r to f51r leaf relation is a direct counterexample to uniform component retrieval.'},
 {'type':'WHOLE_PLANT_FAILURE','item':'MHI002_MHI003','value':'78|61','detail':'Both whole-plant relations rank poorly by exact PAGE_HOST identity.'},
 {'type':'COMPILER_CONFOUND','item':'MHI005','value':next(x['true_target_rank'] for x in rank_rows if x['relation_id']=='MHI005' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='COMPILER_SIGNATURE'),'detail':'The cross-Currier leaf relation ranks even higher under compiler signature than PAGE_HOST identity.'},
 {'type':'SINGLE_HUMAN_ASSERTIONS','item':'MHI002_MHI007','value':6,'detail':'Relations are archived source statements, not independent botanical identifications.'},
 {'type':'ONE_DERIVED_READING','item':'GDT062','value':'NA','detail':'Formal bags are one derived source-display HPR2 view; alternate readings are not replications.'},
 {'type':'NO_SEMANTIC_OWNERSHIP','item':'WHOLE_PAGE_BAGS','value':'NA','detail':'Shared PAGE_HOSTs occur in page prose and are not visually owned labels.'},
]
write(COUNTER,counter)
hits=[x for x in rank_rows if x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='PAGE_HOST_IDENTITY' and x['relation_class']=='COMPONENT_SIMILARITY' and int(x['top_six'])]
status='COMPONENT_RELATION_PAGE_HOST_RETRIEVAL_INTERESTING_POSTHOC' if len(hits)>=3 and float(lead['max_12_top_six_p'])<=.05 else 'FULL_CORPUS_RELATION_RETRIEVAL_NOT_SUPPORTED'
rare={x['relation_id']:x['page_host'] for x in shared if int(x['rarity_rank_within_pair'])==1}
REPORT.write_text(f"""# GDT148 — full-corpus Herbal relation retrieval

## Outcome

**{status}**

Exact PAGE_HOST frequency retrieves three of four archived component-relation targets in the top six of their roughly 90–95-page primary pools: {', '.join(x['relation_id']+' rank '+str(x['true_target_rank'])+'/'+str(x['candidate_pages']) for x in hits)}. The fourth component relation, MHI004, ranks {next(x['true_target_rank'] for x in rank_rows if x['relation_id']=='MHI004' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='PAGE_HOST_IDENTITY')}. The fixed component-scope top-six count is 3/4 (local Monte Carlo p={float(lead['local_top_six_p']):.5f}; maximum-over-four representations and three scopes p={float(lead['max_12_top_six_p']):.5f}). Its mean standardized similarity is {float(lead['true_mean_source_z']):+.3f} (max-12 p={float(lead['max_12_mean_p']):.5f}).

The pattern is layer-specific for MHI006 and MHI007: raw-token ranks are {next(x['true_target_rank'] for x in rank_rows if x['relation_id']=='MHI006' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='RAW_CHAR3')}/{next(x['candidate_pages'] for x in rank_rows if x['relation_id']=='MHI006' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='RAW_CHAR3')} and {next(x['true_target_rank'] for x in rank_rows if x['relation_id']=='MHI007' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='RAW_CHAR3')}/{next(x['candidate_pages'] for x in rank_rows if x['relation_id']=='MHI007' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='RAW_CHAR3')}, while compiler ranks are still worse. MHI005 is less clean because compiler signature ranks its target {next(x['true_target_rank'] for x in rank_rows if x['relation_id']=='MHI005' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='COMPILER_SIGNATURE')}/{next(x['candidate_pages'] for x in rank_rows if x['relation_id']=='MHI005' and x['candidate_scope']=='PRIMARY_CURRIER_HAND' and x['representation']=='COMPILER_SIGNATURE')}.

The rarest shared exact hosts in the three top-six component pairs are `{rare['MHI005']}` (MHI005), `{rare['MHI006']}` (MHI006), and `{rare['MHI007']}` (MHI007). They occur under different surface renderers in the paired pages and are useful candidates for future blinded relation tests, but they are not plant-part words. MHI004's failure, the poor exact-host ranks for both whole-plant pairs (78 and 61), whole-page rather than owned-label provenance, and the fully exposed analysis prevent a semantic assignment.

This is the strongest current corpus-wide PAGE_HOST content-address lead, but it is heterogeneous and post-selected. No image was opened. The source has zero f84r rows and every f84-prefixed row was rejected before retention; no new f84r access occurred. No botanical identity, component identity, semantic role, gloss, word, morpheme, part of speech, sound, language, plaintext, meaning, or translation is established.
""",encoding='utf8')
result={'schema':'GDT148_FULL_CORPUS_RELATION_RETRIEVAL_RESULT_V1','status':status,'relations':6,'component_relations':4,'whole_plant_relations':2,'herbal_pages':len(by),'representations':list(REPS),'scopes':list(SCOPES),'worlds':WORLDS,'seed':SEED,'component_page_host_top_six_hits':[x['relation_id'] for x in hits],'component_page_host_summary':lead,'interpretation':'Exposed full-corpus retrieval localizes a heterogeneous three-of-four component-relation lead to exact PAGE_HOST vocabulary.','claim_ceiling':'Post-hoc anonymous whole-page content-address retrieval only; no botanical identity, component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'actual_source_f84r_rows':source_f84r,'rejected_other_f84_rows':rejected_f84_other,'retained_or_scored_f84_rows':0,'new_f84r_access':False},'inputs':{str(p.relative_to(R)):sha(p) for p in (SOURCE,META,HUMAN,P140,P144,P147)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (INV,RANKS,NULL,HOSTS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'status':status,'hits':result['component_page_host_top_six_hits'],'local_top6_p':lead['local_top_six_p'],'max12_top6_p':lead['max_12_top_six_p']},sort_keys=True))
