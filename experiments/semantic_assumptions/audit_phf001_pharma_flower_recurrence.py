#!/usr/bin/env python3
"""Bounded flower-count ownership and exact-label recurrence screen."""
from __future__ import annotations
import argparse,csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions';R=B/'results'
METHOD=B/'PHF001_PHARMA_FLOWER_COUNT_AND_EXACT_RECURRENCE_METHOD.md'
ANN=R/'existing_human_label_annotations.tsv';XW=R/'existing_human_current_locus_crosswalk.tsv';OLD=R/'pharma_root_color_native_visual_ownership.tsv'
OUT=R/'phf001_pharma_flower_recurrence.json';REPORT=R/'phf001_pharma_flower_recurrence_report.md'
INPUT_HASHES={'existing_human_label_annotations.tsv':'93b14fb00801ee401df018447730c2e2a1036a9aa36135aca44125c177524ed6','existing_human_current_locus_crosswalk.tsv':'4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc','pharma_root_color_native_visual_ownership.tsv':'eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b'}
IMAGES={'1037112':('88r',2714,3735,'a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013'),'1006233':('88v and 89r',9078,3777,'3b553c70d0c068cb39a276d391127165c5d9d868ec08e7f5eb2e73b32bb95d1e'),'1006250':('101v left',2698,3779,'1122f1b13afdf1509402334816f95e5e9baa2b6c94aa9e347b04aa2e4e54f36b'),'1006251':('101v right and 102r',8176,3864,'30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94'),'1006252':('102v left',2981,3795,'8cdb1030d805b968932146124915cb0d86f7abf853167ffec028b59599820fad'),'1006253':('102v right',2838,3697,'e3ed770ad77b1c1127b8e60b2ee2d9e226ab4089d4861b85dbf22299925397ce')}
REVIEW={'STOLFI_BEST_1069':('AMBIGUOUS_NONBIJECTIVE_ROW','1037112','PUBLIC_COMMENT_SAYS_SIX_LABELS_FOR_FOUR_PLANTS'),'STOLFI_BEST_1113':('CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL','1006233','ROW_ALIGNMENT_AND_LOCAL_WHITESPACE'),'STOLFI_BEST_1422':('AMBIGUOUS_FOLDOUT_X_POSITION','1006250','LEGACY_X_POSITION_BETWEEN_NEIGHBOURS'),'STOLFI_BEST_1433':('AMBIGUOUS_FOLDOUT_PANEL_POSITION','1006251','LEGACY_PANEL_ROW_MAPPING_NOT_SINGULAR'),'STOLFI_BEST_1474':('CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL','1006252','ROW_ALIGNMENT_AND_LOCAL_WHITESPACE')}
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def folio(p):return re.match(r'f\d+',p).group()
def state(text):
 t=text.lower();a=bool(re.search(r'(?<!\w)flower(?!s|\w)',t));b=bool(re.search(r'(?<!\w)flowers(?!\w)',t))
 return 'SINGLE_FLOWER' if a and not b else ('MULTIPLE_FLOWERS' if b and not a else None)
def build():
 for p in (ANN,XW,OLD):
  if sha(p)!=INPUT_HASHES[p.name]:raise ValueError(f'input drift {p.name}')
 ann=read(ANN);xw={r['source_record_id']:r for r in read(XW)};old=read(OLD);ad={r['source_record_id']:r for r in ann}
 rows=[]
 for r in ann:
  s=state(r['comments'])
  if r['section']=='pharma' and r['certainty']=='UNHEDGED' and r['object_guess'] in {'plant','root'} and s:rows.append((s,r,xw[r['source_record_id']]))
 primary=[z for z in rows if z[2]['primary_eligible']=='1'];prior={r['source_record_id']:r for r in old};old_clear={k for k,r in prior.items() if r['visual_grade']=='CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL'}
 queue={r['source_record_id'] for s,r,x in primary if folio(r['page']) in {'f88','f101','f102'} and r['source_record_id'] not in prior}
 if queue!=set(REVIEW):raise ValueError(f'review queue drift {queue}')
 clear=old_clear|{k for k,v in REVIEW.items() if v[0]=='CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL'};owned=[z for z in primary if z[1]['source_record_id'] in clear]
 def summary(z):return {'rows':len(z),'states':dict(Counter(x[0] for x in z)),'folios_by_state':{s:sorted({folio(r['page']) for q,r,x in z if q==s},key=lambda f:int(f[1:])) for s in ('SINGLE_FLOWER','MULTIPLE_FLOWERS')}}
 owned_sum=summary(owned);mixed=sorted((f for f in {folio(r['page']) for s,r,x in owned} if {s for s,r,x in owned if folio(r['page'])==f}=={'SINGLE_FLOWER','MULTIPLE_FLOWERS'}),key=lambda f:int(f[1:]))
 all_clear_ids=old_clear|{'STOLFI_BEST_1113','STOLFI_BEST_1474'};stable=[]
 for k in sorted(all_clear_ids):
  x=xw[k];vals=tuple(x[e].replace(' ','') for e in ('ZL3b_text','IT2a_text','RF1b_text'))
  if x['all_three_present']=='1' and len(set(vals))==1:stable.append((k,folio(ad[k]['page']),vals[0]))
 by=defaultdict(list)
 for k,f,v in stable:by[v].append((k,f))
 repeats=[v for v in by.values() if len(v)>1];cross=[v for v in repeats if len({x[1] for x in v})>1]
 gates={'both_flower_states_at_least_four_owned':min(owned_sum['states'].values())>=4,'both_flower_states_span_four_folios':all(len(owned_sum['folios_by_state'][s])>=4 for s in owned_sum['folios_by_state']),'three_mixed_folios':len(mixed)>=3,'any_cross_folio_exact_label_repeat':bool(cross)}
 result={'experiment':'PHF001_PHARMA_FLOWER_COUNT_AND_EXACT_RECURRENCE','schema':'PHF001_RESULT_V1','status':'STOP_NO_TRANSFERABLE_FLOWER_COUNT_AND_ZERO_EXACT_RECURRENCE','decision':'CLOSE_PHARMA_FLOWER_COUNT_AND_EXACT_LABEL_RECURRENCE','counts':{'human_explicit_flower_count':summary(rows),'primary_mapped_flower_count':summary(primary),'clear_owned_flower_count':owned_sum,'mixed_owned_folios':mixed,'all_clear_owned_cells':len(all_clear_ids),'all_reading_literal_stable_clear_cells':len(stable),'recurrent_complete_literal_types':len(repeats),'cross_folio_recurrent_complete_literal_types':len(cross)},'review':{'preselected_records':len(REVIEW),'grades':dict(Counter(x[0] for x in REVIEW.values())),'records':{k:{'grade':v[0],'canvas_id':v[1],'basis':v[2]} for k,v in REVIEW.items()},'official_images':{k:{'label':v[0],'width':v[1],'height':v[2],'sha256':v[3],'url':f'https://collections.library.yale.edu/iiif/2/{k}/full/full/0/default.jpg'} for k,v in IMAGES.items()}},'gates':gates,'access':{'complete_literal_surfaces_displayed_in_development_diagnostic':True,'formal_roots_or_roles_accessed':False,'ocr_clip_embedding_or_automated_vision_used':False,'machine_authored_native_visual_judgments':True},'inputs':{str(METHOD.relative_to(ROOT)):sha(METHOD),**{str(p.relative_to(ROOT)):sha(p) for p in (ANN,XW,OLD)}},'claim_ceiling':'The public human descriptions plus bounded native inspection do not supply a transferable singular/plural flower contrast, and no complete literal label repeats among the clear owned cells. No FLOWER, count, plant name, word, sound, language, cipher, plaintext, meaning, or translation follows.'}
 report=f"# PHF001 pharmaceutical flower-count and exact-recurrence screen\n\nStatus: **STOP — NO TRANSFERABLE FLOWER COUNT AND ZERO EXACT RECURRENCE**.\n\nThe human catalogue contains **{len(rows)}** explicit singular/plural flower descriptions: **{Counter(x[0] for x in rows)['SINGLE_FLOWER']} singular** and **{Counter(x[0] for x in rows)['MULTIPLE_FLOWERS']} plural**. **{len(primary)}** have a primary current-locus map. Reusing the frozen ownership audit and reviewing five preselected official-image records yields **{len(owned)}** clear owned flower-count labels: **{owned_sum['states']['SINGLE_FLOWER']} singular** on {', '.join(owned_sum['folios_by_state']['SINGLE_FLOWER'])} and **{owned_sum['states']['MULTIPLE_FLOWERS']} plural** on {', '.join(owned_sum['folios_by_state']['MULTIPLE_FLOWERS'])}. Only {', '.join(mixed)} mix states. The plural state remains confined to two folios.\n\nAcross all **{len(all_clear_ids)}** clear owned pharmaceutical cells, **{len(stable)}** have one identical complete compact literal surface in ZL3b, IT2a, and RF1b. **None repeats**, within or across folios. A development diagnostic exposed those surfaces after ownership selection, so this is an exploratory zero-recurrence result, not an analyst-blind target test.\n\nNo formal root/role or image recognizer was used. This supplies no FLOWER/count word, plant name, sound, language, cipher, plaintext, meaning, or translation.\n"
 return result,report
def main():
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');q=a.parse_args();r,m=build()
 if q.write:
  if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
  OUT.write_bytes(canon(r));REPORT.write_text(m,encoding='utf-8')
 else:print(canon(r).decode(),end='')
if __name__=='__main__':main()
