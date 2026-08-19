#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,importlib.util,json,math,re,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV,canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt366_matched_reproductive_delta';ART=EXP/'artifacts';FREEZE=ART/'gdt366_freeze.json';FEATURES=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal/artifacts/gdt365_feature_manifest.tsv';FORMAL=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv';PAGESRC=ROOT/'experiments/semantic_assumptions/results/existing_human_page_annotations.tsv';HELPER=ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/src/run.py';INVENTORY=ART/'gdt366_null_folio_inventory.tsv';COUNTER=ART/'gdt366_counterexamples.tsv';RESULT=ART/'gdt366_result.json';REPORT=EXP/'REPORT.md'
spec=importlib.util.spec_from_file_location('gdt363_frozen',HELPER);assert spec and spec.loader;g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 h=p.open('w',encoding='utf-8',newline='');w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);h.close()
def cosine(a,b):
 d=float(np.linalg.norm(a)*np.linalg.norm(b));return float(a@b/d) if d>1e-15 else 0.0
def main():
 names=[r['formal_feature'] for r in read(FEATURES)];reader=GuardedTSV(FORMAL,selector_column='page',forbidden_prefixes=('f84',),forbidden_action='skip');allrows=list(reader);rows=[r for r in allrows if r['section']=='H' and r['currier']=='A' and r['hand']=='1' and re.fullmatch(r'f\d+[rv]',r['page'])];by=defaultdict(list)
 for r in rows:by[r['page']].append(r)
 folios=defaultdict(dict)
 for p in by:
  m=re.fullmatch(r'(f\d+)([rv])',p);folios[m.group(1)][m.group(2)]=p
 eligible={f:sides for f,sides in folios.items() if set(sides)=={'r','v'}};allowed={p for sides in eligible.values() for p in sides.values()};pr=GuardedTSV(PAGESRC,selector_column='page',allowed_values=allowed,forbidden_prefixes=('f84',),forbidden_action='skip');quire={r['page']:r['quire'] for r in pr};eligible={f:s for f,s in eligible.items() if set(s.values())<=set(quire)}
 vals={};strict={}
 for p in {x for s in eligible.values() for x in s.values()}:
  vals[p]=g.family_events(by[p])[0];sr=[r for r in by[p] if r['strict_zero_alternative']=='1'];strict[p]=g.family_events(sr)[0]
 fs=sorted(eligible,key=lambda x:int(x[1:]));pages=sorted({p for f in fs for p in eligible[f].values()});X=np.asarray([[vals[p].get(n,0) for n in names] for p in pages]);XS=np.asarray([[strict[p].get(n,0) for n in names] for p in pages]);sd=X.std(0);sds=XS.std(0);mask=sd>1e-12;masks=sds>1e-12;index={p:i for i,p in enumerate(pages)}
 Z=X[:,mask]/sd[mask];ZS=XS[:,masks]/sds[masks];delta={f:Z[index[eligible[f]['r']]]-Z[index[eligible[f]['v']]] for f in fs};deltas={f:ZS[index[eligible[f]['r']]]-ZS[index[eligible[f]['v']]] for f in fs}
 # Frozen semantic direction only chooses signs; no feature is selected.
 d4=delta['f4'];d17=-delta['f17'];observed=cosine(d4,d17);s4=deltas['f4'];s17=-deltas['f17'];strict_cos=cosine(s4,s17)
 null=[]
 for i,a in enumerate(fs):
  qa=quire[eligible[a]['r']]
  for b in fs[i+1:]:
   if qa==quire[eligible[b]['r']]:continue
   base=cosine(delta[a],delta[b])
   for sa in (-1,1):
    for sb in (-1,1):null.append({'folio_a':a,'folio_b':b,'sign_a':sa,'sign_b':sb,'cosine':base*sa*sb})
 tail=sum(x['cosine']>=observed-1e-15 for x in null);p=tail/len(null);values=np.asarray([x['cosine'] for x in null]);status='MATCHED_DELTA_INTERESTING_EXPLORATORY' if observed>0 and strict_cos>0 and p<=.05 else ('WEAK_ALIGNED_DELTA' if observed>0 else 'MATCHED_DELTA_NOT_ALIGNED')
 f8=delta['f8'];secondary={'f8_none_minus_flower_cosine_to_f4_berry_minus_flower':cosine(f8,d4),'f8_none_minus_flower_cosine_to_f17_berry_minus_flower':cosine(f8,d17)}
 inv=[]
 for f in fs:
  inv.append({'physical_folio':f,'recto_page':eligible[f]['r'],'verso_page':eligible[f]['v'],'quire':quire[eligible[f]['r']],'recto_groups':len(by[eligible[f]['r']]),'verso_groups':len(by[eligible[f]['v']])})
 write(INVENTORY,inv);higher=sorted((x for x in null if x['cosine']>=observed-1e-15),key=lambda x:-x['cosine'])[:20];write(COUNTER,[{'rank':i+1,**{k:(f'{v:.12f}' if k=='cosine' else v) for k,v in x.items()},'reason':'NULL_DELTA_PAIR_AT_LEAST_AS_ALIGNED_AS_VISUAL_PAIR'} for i,x in enumerate(higher)] or [{'rank':0,'folio_a':'NONE','folio_b':'NONE','sign_a':0,'sign_b':0,'cosine':'0','reason':'NO_NULL_EXCEEDANCE'}])
 payload={'schema':'GDT366_RESULT_V1','status':status,'primary':{'f4_berry_minus_flower':'f4r-f4v','f17_berry_minus_flower':'f17v-f17r','cosine':observed,'strict_only_cosine':strict_cos,'exact_inclusive_p':p,'null_tail':tail,'null_size':len(null)},'secondary_unscored':secondary,'capacity':{'eligible_Herbal_A_hand1_complete_rv_folios':len(fs),'distinct_quire_signed_pair_worlds':len(null),'fixed_features':len(names),'nonzero_dispersion_features':int(mask.sum()),'strict_nonzero_dispersion_features':int(masks.sum())},'null_summary':{'mean':float(values.mean()),'sd':float(values.std()),'q95':float(np.quantile(values,.95)),'maximum':float(values.max())},'postexposure':True,'access':{'new_images_or_catalogues_opened':False,'f84_rows_retained_parsed_joined_scored':False,'formal_guard_skipped_f84':reader.stats.skipped_forbidden,'page_guard_skipped_f84':pr.stats.skipped_forbidden},'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (FREEZE,FEATURES,FORMAL,PAGESRC,EXP/'METHOD.md',HELPER)},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'outputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (INVENTORY,COUNTER)},'claim_ceiling':'REPLICATED_WITHIN_FOLIO_ANONYMOUS_FORMAL_PAGE_PROFILE_CHANGE_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM'};payload['content_hash']=hashlib.sha256(canonical_json_bytes(payload)).hexdigest();RESULT.write_bytes(canonical_json_bytes(payload))
 REPORT.write_text(f"""# GDT366 matched reproductive delta report

Status: **{status}**.

## Result

The 227-feature standardized `BERRY - FLOWER` deltas on f4 and f17 have cosine **{observed:+.6f}**. The all-strict-row sensitivity is **{strict_cos:+.6f}**. Across {len(null):,} exact signed pairs of distinct-quire Herbal-A/hand-1 recto-verso controls, {tail:,} are at least as aligned (`p={p:.6f}`; null 95th percentile {np.quantile(values,.95):+.6f}).

The direction was fixed from existing human annotations: f4r-f4v and f17v-f17r. Their opposite page-side orientation prevents a constant recto-verso effect from producing the shared sign. No individual family was selected or inspected.

The different f8 `NO_FRUIT_OR_FLOWER - FLOWER` contrast is unscored: cosine {secondary['f8_none_minus_flower_cosine_to_f4_berry_minus_flower']:+.6f} to f4 and {secondary['f8_none_minus_flower_cosine_to_f17_berry_minus_flower']:+.6f} to f17.

## Limits

This is fully postexposure and rests on exactly two visually nominated folios. A positive cosine is a distributed page-profile lead, not a lexical marker. Higher or equal unrelated control pairs are listed explicitly.

The formal guard skipped {reader.stats.skipped_forbidden} f84-prefixed rows before parsing and retained no f84 data. No image or catalogue was opened. Nothing here identifies BERRY, FLOWER, a plant, word, role, sound, language, plaintext, meaning, or translation.
""",encoding='utf-8')
if __name__=='__main__':main()
