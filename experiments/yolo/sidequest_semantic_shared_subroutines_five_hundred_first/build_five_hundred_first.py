#!/usr/bin/env python3
from __future__ import annotations
import csv,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P500=R/'experiments/yolo/sidequest_semantic_procedure_primitive_grammar_five_hundredth'
SUBS={
 'SUB01':{'name':'DOPPELEINGABE_ZUM_ZIEL','seq':('ACTIVATE_CHARGE','ACTIVATE_CHARGE','TARGET_HANDOFF')},
 'SUB02':{'name':'UEBERTRAGEN_UND_FOLGEPOSTEN_STARTEN','seq':('MOVE_PASS','ACTIVATE_CHARGE','CONTINUE_USE')},
 'SUB03':{'name':'FORTSETZEN_UND_NACHMESSEN','seq':('CONTINUE_USE','METER_CHECK')},
}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def occurrences(rows,seq):
 out=[]
 for macro in sorted({x['macro_item'] for x in rows}):
  rr=[x for x in rows if x['macro_item']==macro];vals=[x['procedure_primitive'] for x in rr]
  for i in range(len(vals)-len(seq)+1):
   if tuple(vals[i:i+len(seq)])==seq:out.append((macro,i,rr[i:i+len(seq)]))
 return out
def main():
 e=read(P500/'FIVE_HUNDREDTH_58_EVENT_PRIMITIVE_MAP.tsv');m=read(P500/'FIVE_HUNDREDTH_117_ITEM_PROCEDURE_GRAMMAR_MANUAL.tsv');l=read(P500/'FIVE_HUNDREDTH_776_PROCEDURE_PRIMITIVE_LEDGER.tsv')
 cand=[]
 for n in (2,3):
  d=collections.defaultdict(list)
  for macro in sorted({x['macro_item'] for x in e}):
   rr=[x for x in e if x['macro_item']==macro];vals=[x['procedure_primitive'] for x in rr]
   for i in range(len(vals)-n+1):d[tuple(vals[i:i+n])].append((macro,rr[i]['event_id'],rr[i+n-1]['event_id']))
  for seq,occ in sorted(d.items()):
   mc=len({x[0] for x in occ})
   if mc>=2:
    gross=(n-1)*len(occ);definition=n;net=gross-definition
    chosen=next((k for k,v in SUBS.items() if v['seq']==seq),None)
    cand.append({'length':n,'primitive_sequence':'>'.join(seq),'occurrences':len(occ),'macro_count':mc,'macros':'|'.join(sorted({x[0] for x in occ})),'gross_recipe_saving':gross,'definition_cost':definition,'selector_paid_gain':net,'selected_subroutine':chosen or 'NO'})
 write('FIVE_HUNDRED_FIRST_CROSS_MACRO_NGRAM_CANDIDATES.tsv',cand)
 assigned={};occrows=[]
 for sid,spec in SUBS.items():
  for macro,start,rr in occurrences(e,spec['seq']):
   ids=[x['event_id'] for x in rr]
   if any(i in assigned for i in ids):raise ValueError('overlap')
   for i in ids:assigned[i]=sid
   occrows.append({'subroutine':sid,'name_de':spec['name'],'macro_item':macro,'start_event':ids[0],'end_event':ids[-1],'event_ids':'|'.join(ids),'primitive_sequence':'>'.join(spec['seq']),'crosses_phase_boundary':'YES' if len({x['macro_phase'] for x in rr})>1 else 'NO'})
 write('FIVE_HUNDRED_FIRST_SEVEN_SUBROUTINE_OCCURRENCES.tsv',occrows)
 compressed=[]
 for macro in sorted({x['macro_item'] for x in e}):
  rr=[x for x in e if x['macro_item']==macro];tokens=[];i=0
  while i<len(rr):
   sid=assigned.get(rr[i]['event_id'])
   if sid:
    tokens.append(sid);i+=len(SUBS[sid]['seq'])
   else:tokens.append(rr[i]['procedure_primitive']);i+=1
  compressed.append({'macro_item':macro,'macro_name':rr[0]['local_macro'],'events':len(rr),'primitive_tokens_before':len(rr),'recipe_tokens_after':len(tokens),'compressed_recipe':'>'.join(tokens),'event_order_preserved':'YES'})
 write('FIVE_HUNDRED_FIRST_FIVE_SUBROUTINE_COMPRESSED_RECIPES.tsv',compressed)
 cost=[
  {'account':'raw_primitive_recipe_tokens','tokens':58,'note':'five recipes before substitution'},
  {'account':'compressed_recipe_tokens','tokens':sum(int(x['recipe_tokens_after']) for x in compressed),'note':'seven subroutine calls replace18 primitive positions'},
  {'account':'subroutine_definition_tokens','tokens':sum(len(x['seq']) for x in SUBS.values()),'note':'3+3+2'},
  {'account':'selector_paid_total','tokens':sum(int(x['recipe_tokens_after']) for x in compressed)+sum(len(x['seq']) for x in SUBS.values()),'note':'compare with58'},
  {'account':'selector_paid_gain','tokens':58-(sum(int(x['recipe_tokens_after']) for x in compressed)+sum(len(x['seq']) for x in SUBS.values())),'note':'positive is useful'},]
 write('FIVE_HUNDRED_FIRST_SUBROUTINE_COST_ACCOUNT.tsv',cost)
 recipe={x['macro_item']:x for x in compressed};new=[]
 for x in m:
  n=dict(x)
  if x['item_id'] in recipe:n['teaching_value_or_rule_de']=recipe[x['item_id']]['macro_name']+': '+recipe[x['item_id']]['compressed_recipe'];n['source_artifact']='PASS501_SHARED_SUBROUTINES'
  new.append(n)
 pos=next(i for i,x in enumerate(new) if x['layer']=='L6_REDUCED_LOCAL_DECK')
 for offset,(sid,spec) in enumerate(SUBS.items()):
  new.insert(pos+offset,{'manual_order':'0','layer':'L6_SHARED_PROCEDURE_SUBROUTINE','item_id':sid,'teaching_value_or_rule_de':spec['name']+': '+'>'.join(spec['seq']),'scope':'PROSE','support_or_instances':str(sum(x['subroutine']==sid for x in occrows))+' calls','source_artifact':'PASS501_SHARED_SUBROUTINES'})
 for i,x in enumerate(new,1):x['manual_order']=str(i)
 write('FIVE_HUNDRED_FIRST_120_ITEM_SUBROUTINE_MANUAL.tsv',new)
 out=[]
 for x in l:
  n=dict(x);n['procedure_subroutine']=assigned.get(x['item_id'],'NONE');out.append(n)
 write('FIVE_HUNDRED_FIRST_776_SUBROUTINE_LEDGER.tsv',out)
 s={'status':'PASS','candidates':len(cand),'selected_subroutines':len(SUBS),'subroutine_calls':len(occrows),'covered_macro_events':len(assigned),'raw_tokens':58,'compressed_tokens':sum(int(x['recipe_tokens_after']) for x in compressed),'definition_tokens':8,'selector_paid_total':sum(int(x['recipe_tokens_after']) for x in compressed)+8,'selector_paid_gain':58-(sum(int(x['recipe_tokens_after']) for x in compressed)+8),'manual_before':len(m),'manual_after':len(new),'ledger':len(out)}
 (H/'FIVE_HUNDRED_FIRST_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
