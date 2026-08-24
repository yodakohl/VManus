#!/usr/bin/env python3
from __future__ import annotations
import csv,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P499=R/'experiments/yolo/sidequest_semantic_residual_deck_collapse_four_hundred_ninety_ninth'
PRIMITIVES={
 'ACTIVATE_CHARGE':('ANSETZEN ODER BESCHICKEN','einen Batch, eine Portion oder eine Eingabe aktivieren'),
 'SOURCE_DRAW':('QUELLE ODER ABZIEHEN','aus einer Quelle speisen oder einen Ausgang abziehen'),
 'METER_CHECK':('BEMESSEN ODER PRUEFEN','Sollmaß setzen oder erneut prüfen'),
 'TARGET_HANDOFF':('ZIEL ODER UEBERGABE','eine Zieladresse setzen oder an sie übergeben'),
 'MOVE_PASS':('BEWEGEN ODER DURCHLASS','einen Posten zuführen, führen oder durchlassen'),
 'HOLD_STATE':('HALTEN ODER ZUSTAND','halten, temperieren, absetzen oder Bereitschaft feststellen'),
 'CONTINUE_USE':('FORTSETZEN ODER VERWENDEN','denselben Posten fortführen oder einsetzen'),
 'CLOSE':('SCHLIESSEN','den laufenden Arbeitsschritt beenden'),
}
MAP={
 'E102':'METER_CHECK','E103':'MOVE_PASS','E104':'TARGET_HANDOFF','E105':'SOURCE_DRAW','E106':'CONTINUE_USE','E107':'ACTIVATE_CHARGE','E108':'ACTIVATE_CHARGE','E109':'TARGET_HANDOFF','E110':'CONTINUE_USE','E111':'HOLD_STATE','E112':'MOVE_PASS','E113':'ACTIVATE_CHARGE','E114':'CONTINUE_USE','E115':'HOLD_STATE','E116':'METER_CHECK','E117':'HOLD_STATE','E118':'METER_CHECK','E119':'MOVE_PASS','E120':'CLOSE',
 'E270':'METER_CHECK','E271':'HOLD_STATE','E272':'TARGET_HANDOFF','E273':'CONTINUE_USE','E274':'METER_CHECK','E275':'HOLD_STATE','E276':'HOLD_STATE','E277':'CONTINUE_USE','E278':'TARGET_HANDOFF','E279':'HOLD_STATE','E280':'CLOSE',
 'E001':'SOURCE_DRAW','E002':'ACTIVATE_CHARGE','E003':'SOURCE_DRAW','E004':'ACTIVATE_CHARGE','E005':'TARGET_HANDOFF','E006':'SOURCE_DRAW','E007':'SOURCE_DRAW','E008':'CONTINUE_USE','E009':'METER_CHECK','E010':'ACTIVATE_CHARGE',
 'E015':'SOURCE_DRAW','E016':'HOLD_STATE','E017':'ACTIVATE_CHARGE','E018':'METER_CHECK','E019':'CONTINUE_USE','E020':'MOVE_PASS','E021':'CONTINUE_USE','E022':'METER_CHECK','E023':'TARGET_HANDOFF',
 'E074':'ACTIVATE_CHARGE','E075':'ACTIVATE_CHARGE','E076':'TARGET_HANDOFF','E077':'METER_CHECK','E078':'ACTIVATE_CHARGE','E079':'MOVE_PASS','E080':'ACTIVATE_CHARGE','E081':'CONTINUE_USE','E082':'TARGET_HANDOFF',
}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 m=read(P499/'FOUR_HUNDRED_NINETY_NINTH_116_ITEM_COLLAPSED_MANUAL.tsv');l=read(P499/'FOUR_HUNDRED_NINETY_NINTH_776_COLLAPSED_LEDGER.tsv')
 macro=[x for x in l if x['syntax_item'].startswith('W:')]
 ptab=[]
 for key,(de,rule) in PRIMITIVES.items():
  rows=[x for x in macro if MAP[x['item_id']]==key]
  ptab.append({'primitive':key,'short_value_de':de,'rule_de':rule,'events':len(rows),'macros':len({x['syntax_item'] for x in rows}),'event_ids':'|'.join(x['item_id'] for x in rows)})
 write('FIVE_HUNDREDTH_EIGHT_PROCEDURE_PRIMITIVES.tsv',ptab)
 em=[]
 for x in macro:
  em.append({'writer_order':x['writer_order'],'event_id':x['item_id'],'macro_item':x['syntax_item'],'local_macro':x['local_macro'],'macro_phase':x['macro_phase'],'component_parse':x['component_parse'],'procedure_primitive':MAP[x['item_id']],'reading_de':x['concrete_reading_de']})
 write('FIVE_HUNDREDTH_58_EVENT_PRIMITIVE_MAP.tsv',em)
 phases=[]
 for macro_id in sorted({x['macro_item'] for x in em}):
  rows=[x for x in em if x['macro_item']==macro_id]
  for phase in dict.fromkeys(x['macro_phase'] for x in rows):
   part=[x for x in rows if x['macro_phase']==phase]
   phases.append({'macro_item':macro_id,'macro_name':part[0]['local_macro'],'phase':phase,'events':len(part),'event_ids':'|'.join(x['event_id'] for x in part),'primitive_sequence':'>'.join(x['procedure_primitive'] for x in part)})
 write('FIVE_HUNDREDTH_15_PHASE_RECIPES.tsv',phases)
 recipes=[]
 for macro_id in sorted({x['macro_item'] for x in em}):
  rows=[x for x in em if x['macro_item']==macro_id]
  phase_rows=[x for x in phases if x['macro_item']==macro_id]
  recipe=' || '.join(x['primitive_sequence'] for x in phase_rows)
  recipes.append({'macro_item':macro_id,'macro_name':rows[0]['local_macro'],'events':len(rows),'phases':len(phase_rows),'compact_recipe':recipe,'unique_primitive_types':len({x['procedure_primitive'] for x in rows}),'retain_order_recipe':'YES'})
 write('FIVE_HUNDREDTH_FIVE_COMPACT_MACRO_RECIPES.tsv',recipes)
 recipe_map={x['macro_item']:x for x in recipes}
 new=[]
 for x in m:
  n=dict(x)
  if x['item_id'] in recipe_map:
   rec=recipe_map[x['item_id']];n['teaching_value_or_rule_de']=rec['macro_name']+': '+rec['compact_recipe'];n['source_artifact']='PASS500_PROCEDURE_PRIMITIVE_GRAMMAR'
  new.append(n)
 insert=next(i for i,x in enumerate(new) if x['layer']=='L6_REDUCED_LOCAL_DECK')
 rule={'manual_order':'0','layer':'L6_PROCEDURE_PRIMITIVE_GRAMMAR','item_id':'PROC_G01','teaching_value_or_rule_de':'Acht Prozessprimitive kombinieren; doppelte Primitive bedeuten echte Wiederholung; || trennt gelernte Phasen; konkrete Karten folgen ihrer Komponentenfolge.','scope':'PROSE','support_or_instances':'5 macros;58 events;15 phases','source_artifact':'PASS500_PROCEDURE_PRIMITIVE_GRAMMAR'}
 new.insert(insert,rule)
 for i,x in enumerate(new,1):x['manual_order']=str(i)
 write('FIVE_HUNDREDTH_117_ITEM_PROCEDURE_GRAMMAR_MANUAL.tsv',new)
 out=[]
 for x in l:
  n=dict(x);n['procedure_primitive']=MAP.get(x['item_id'],'NONE');out.append(n)
 write('FIVE_HUNDREDTH_776_PROCEDURE_PRIMITIVE_LEDGER.tsv',out)
 support=collections.defaultdict(set)
 for x in em:support[x['procedure_primitive']].add(x['macro_item'])
 shared=[{'primitive':k,'macro_count':len(v),'macros':'|'.join(sorted(v)),'shared_by_at_least_two':'YES' if len(v)>=2 else 'NO'} for k,v in sorted(support.items())]
 write('FIVE_HUNDREDTH_PRIMITIVE_CROSS_MACRO_SUPPORT.tsv',shared)
 s={'status':'PASS','primitives':len(PRIMITIVES),'macro_events':len(em),'phase_recipes':len(phases),'macros':len(recipes),'manual_before':len(m),'manual_after':len(new),'ledger':len(out),'all_primitives_shared_by_two':all(len(v)>=2 for v in support.values()),'macro_events_total':sum(x['local_macro']!='NONE' for x in out)}
 (H/'FIVE_HUNDREDTH_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
