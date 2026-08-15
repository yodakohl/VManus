#!/usr/bin/env python3
"""Freeze noisy external identification tokens before formal scoring."""
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ARCH=ROOT/'gdt031_herbal_page_architecture.tsv'; ANNOT=ROOT/'experiments/semantic_assumptions/results/existing_human_page_annotations.tsv'; VIS=ROOT/'gdt137_herbal_visual_feature_inventory.tsv'; METHOD=ROOT/'GDT139_HERBAL_IDENTIFICATION_TOKEN_TRANSFER_METHOD.md'; OUT=ROOT/'gdt139_identification_token_inventory.tsv'; PRED=ROOT/'gdt139_prediction.json'
STOP={'possible','plant','identification','identifications','some','kind','family','like','nearly','allied','leaves','flower','flowers','common','this','with','looks','water','black','indian','good','king','left','right','species','appears','the','not','fam','no','and','or','cf'}
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def extract(s):
 s=s.replace('ELVA:','ELV:').replace('THP:','ThP:'); out=defaultdict(set)
 for m in re.finditer(r'\b(ELV|ThP):\s*(.*?)(?=\b(?:ELV|ThP):|$)',s,re.I):
  source=m.group(1).upper()
  for candidate in re.split(r'[;,]',m.group(2)):
   candidate=re.sub(r'\([^)]*\)',' ',candidate)
   words=[w for w in re.findall(r'[A-Za-z]{3,}',candidate.lower()) if w not in STOP]
   if words:out[source].add(words[0])
 return out
arch={r['page']:r for r in read(ARCH) if not r['page'].startswith('f84')}; vis={r['page']:r for r in read(VIS) if not r['page'].startswith('f84')}; assert len(arch)==len(vis)==127
ann={r['page']:r for r in read(ANNOT) if r['page'] in arch}; assert set(ann)==set(arch)
parsed={(source,page):tokens for page,row in ann.items() for source,tokens in extract(row['tentative_identifications']).items()}
freq=defaultdict(Counter); fols=defaultdict(lambda:defaultdict(set))
for (source,page),tokens in parsed.items():
 for token in tokens:freq[source][token]+=1;fols[source][token].add(arch[page]['physical_folio'])
eligible={s:sorted(t for t,n in freq[s].items() if n>=2 and len(fols[s][t])>=2) for s in ('ELV','THP')}; assert {k:len(v) for k,v in eligible.items()}=={'ELV':6,'THP':13}
columns=[f'{s}_{t.upper()}' for s in ('ELV','THP') for t in eligible[s]]; rows=[]
for source in ('ELV','THP'):
 for page in sorted(p for s,p in parsed if s==source):
  a=arch[page]; v=vis[page]; tokens=parsed[source,page]
  row={'panel':source,'page':page,'physical_folio':a['physical_folio'],'currier':a['currier'],'hand':a['hand'],'illustration_profile':a['illustration_profile'],'candidate_token_count':len(tokens),'candidate_tokens_sha256':hashlib.sha256('|'.join(sorted(tokens)).encode()).hexdigest(),'tentative_identifications_sha256':hashlib.sha256(ann[page]['tentative_identifications'].encode()).hexdigest(),'source_url':ann[page]['source_url'],'provenance':'EXISTING_HUMAN_TENTATIVE_IDENTIFICATION','semantic_role':'UNASSIGNED'}
  for c in columns:row[c]=0
  for t in eligible[source]:row[f'{source}_{t.upper()}']=int(t in tokens)
  for name in [x for x in v if x in {'DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS'}]:row['VIS_'+name]=v[name]
  row.update({'catalogue_prose_lines':a['catalogue_prose_lines'],'paragraph_starts':a['paragraph_starts'],'catalogue_label_presence':a['catalogue_label_presence'],'formal_lines':a['LINES'],'formal_groups':a['GROUPS']}); rows.append(row)
fields=list(rows[0]);
with OUT.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
panel_counts=Counter(r['panel'] for r in rows); assert panel_counts==Counter({'THP':92,'ELV':81})
prediction={'schema':'GDT139_HERBAL_IDENTIFICATION_TOKEN_TRANSFER_PREDICTION_V1','status':'FROZEN_NOISY_EXTERNAL_TOKEN_PANEL_BEFORE_FORMAL_SCORING','chronology':'Public tentative-identification text was exposed; exact extraction, eligible token set, panels, models and null were frozen before formal PAGE_HOST/raw/compiler scores were computed.','panels':dict(panel_counts),'eligible_tokens':eligible,'eligible_columns':columns,'representations':['PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE'],'k':7,'shrink':8.0,'worlds':10000,'null':'SOURCE_CURRIER_HAND_ILLUSTRATION_PROFILE_COMPLETE_TOKEN_VECTOR','nuisance':'CURRIER_HAND_ILLUSTRATION_PROFILE_LAYOUT_PLUS_12_GDT137_VISIBLE_FEATURES','outcome_caveat':'Tentative identifications are noisy human hypotheses and absence of a token is not botanical exclusion. ELV and ThP are separate source panels, not replications.','f84':{'all_f84_rows_rejected_before_retention':True,'new_f84r_access':False},'claim_ceiling':'Noisy external identification-token association only; no plant identification, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','inputs':{str(p.relative_to(ROOT)):sha(p) for p in (METHOD,ARCH,ANNOT,VIS,ROOT/'gdt137_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{OUT.name:sha(OUT)}};prediction['prediction_content_sha256']=csha(prediction);PRED.write_text(json.dumps(prediction,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':prediction['status'],'panels':prediction['panels'],'eligible':{k:len(v) for k,v in eligible.items()}},sort_keys=True))
