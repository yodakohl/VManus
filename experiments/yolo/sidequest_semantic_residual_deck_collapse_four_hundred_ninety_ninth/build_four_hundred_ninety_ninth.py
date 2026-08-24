#!/usr/bin/env python3
from __future__ import annotations
import csv,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P498=R/'experiments/yolo/sidequest_semantic_b2_hold_pass_use_four_hundred_ninety_eighth'
WHOLE_MAP={'WHOLE[cheey|shey]':'PROC031','WHOLE[ches]':'PROC124','WHOLE[daiiin]':'PROC169'}
RULE='OWNER ODER AKTIVEN POSTEN UEBERNEHMEN; QUELLE MASS ZIEL UND HANDLUNG NACH BEDARF SETZEN; BEI NEUEM POSTEN WIEDERHOLEN; SCHLUSS NUR AM KLAUSELENDE'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 m=read(P498/'FOUR_HUNDRED_NINETY_EIGHTH_164_ITEM_B2_DECOMPOSED_MANUAL.tsv');l=read(P498/'FOUR_HUNDRED_NINETY_EIGHTH_776_B2_DECOMPOSED_LEDGER.tsv')
 count=collections.Counter(x['syntax_item'] for x in l)
 remove=[x for x in m if x['item_id'].startswith('X:') or x['item_id'].startswith('R0')]
 inv=[]
 for x in remove:
  typ='STATEMENT_RESIDUAL' if x['item_id'].startswith('X:') else 'SMALL_RECURRENT_RESIDUAL'
  inv.append({'old_item_id':x['item_id'],'old_type':typ,'support_statements':x['support_or_instances'],'ledger_events':count[x['item_id']],'old_value_de':x['teaching_value_or_rule_de'],'replacement':'G01 + COMPONENT_CHAIN OR LEARNED_WHOLE_CARD','retain_as_word':'NO','retain_as_procedure_macro':'NO'})
 write('FOUR_HUNDRED_NINETY_NINTH_49_REMOVED_LOCAL_ITEMS.tsv',inv)
 remap=[]
 out=[]
 for x in l:
  n=dict(x)
  if x['syntax_item'].startswith('X:') or x['syntax_item'].startswith('R0'):
   old=x['syntax_item'];target=WHOLE_MAP.get(x['component_parse'],'COMPONENT_CHAIN:'+x['component_parse'])
   n['semantic_layer']='GENERAL_CLAUSE_GRAMMAR_PLUS_EXISTING_LEXICON'
   n['syntax_item']=target
   remap.append({'writer_order':x['writer_order'],'event_id':x['item_id'],'statement':x['statement_or_locus'],'old_local_item':old,'component_parse':x['component_parse'],'new_syntax_item':target,'concrete_reading_de':x['concrete_reading_de'],'local_value_removed':'YES'})
  out.append(n)
 write('FOUR_HUNDRED_NINETY_NINTH_204_EVENT_REMAP.tsv',remap)
 kept=[x for x in m if not (x['item_id'].startswith('X:') or x['item_id'].startswith('R0'))]
 g={'manual_order':'0','layer':'L6_GENERAL_LOCAL_CLAUSE_GRAMMAR','item_id':'CLAUSE_G01','teaching_value_or_rule_de':RULE,'scope':'PROSE','support_or_instances':'49 old local items;204 events','source_artifact':'PASS499_RESIDUAL_COLLAPSE'}
 # Insert directly before the retained procedure macros.
 pos=next(i for i,x in enumerate(kept) if x['layer']=='L6_REDUCED_LOCAL_DECK')
 kept.insert(pos,g)
 for i,x in enumerate(kept,1):x['manual_order']=str(i)
 write('FOUR_HUNDRED_NINETY_NINTH_116_ITEM_COLLAPSED_MANUAL.tsv',kept)
 write('FOUR_HUNDRED_NINETY_NINTH_776_COLLAPSED_LEDGER.tsv',out)
 macros=[]
 for x in kept:
  if x['item_id'].startswith('W:'):
   macros.append({'item_id':x['item_id'],'statement':x['support_or_instances'],'event_count':count[x['item_id']],'macro_de':x['teaching_value_or_rule_de'],'why_retained':'PROCEDURE_ORDER_NOT_LEXICAL_VALUE'})
 write('FOUR_HUNDRED_NINETY_NINTH_FIVE_RETAINED_PROCEDURE_MACROS.tsv',macros)
 layers=collections.Counter(x['layer'] for x in kept)
 layer_rows=[{'layer':k,'items':v,'role':('LOCAL_PROCEDURE_MEMORY' if k=='L6_REDUCED_LOCAL_DECK' else 'GENERAL_CLAUSE_RULE' if k=='L6_GENERAL_LOCAL_CLAUSE_GRAMMAR' else 'UNCHANGED')} for k,v in sorted(layers.items())]
 write('FOUR_HUNDRED_NINETY_NINTH_116_ITEM_LAYER_SUMMARY.tsv',layer_rows)
 summary={'status':'PASS','manual_before':len(m),'removed_local_items':len(remove),'added_general_rules':1,'manual_after':len(kept),'old_local_deck_items':54,'new_local_deck_items_including_rule':6,'retained_procedure_macros':len(macros),'remapped_events':len(remap),'ledger':len(out),'whole_card_remaps':sum(x['new_syntax_item'].startswith('PROC') for x in remap),'component_chain_remaps':sum(x['new_syntax_item'].startswith('COMPONENT_CHAIN:') for x in remap),'macro_events_total':sum(x['local_macro']!='NONE' for x in out)}
 (H/'FOUR_HUNDRED_NINETY_NINTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
