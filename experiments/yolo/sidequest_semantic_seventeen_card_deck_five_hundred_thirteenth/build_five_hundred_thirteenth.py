#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P512=R/'experiments/yolo/sidequest_semantic_complete_morph_lexicon_five_hundred_twelfth'
P510=R/'experiments/yolo/sidequest_semantic_core_deduplication_five_hundred_tenth'
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def top(c):return '|'.join(f'{k}:{v}' for k,v in c.most_common(5)) if c else 'NONE'
def main():
 lex=read(P512/'FIVE_HUNDRED_TWELFTH_173_COMPLETE_MORPHOLOGICAL_LEXICON.tsv');deck=[x for x in lex if x['morphological_class'] in {'ATOMIC_CORE_CARD','MEMORIZED_WHOLE_SIGN'}];events=read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');card_by_tuple={x['joint_tuple_id']:x for x in lex};by_st=defaultdict(list)
 for x in events:by_st[x['statement_id']].append(x)
 occ=[];neighbors={x['card_no']:{'left':Counter(),'right':Counter(),'prim':Counter()} for x in deck}
 deck_ids={x['card_no'] for x in deck}
 for st,rr in by_st.items():
  for i,x in enumerate(rr):
   card=card_by_tuple[x['joint_tuple_id']]
   if card['card_no'] not in deck_ids:continue
   left='START' if i==0 else rr[i-1]['observed_surface'];right='END' if i==len(rr)-1 else rr[i+1]['observed_surface'];n=neighbors[card['card_no']];n['left'][left]+=1;n['right'][right]+=1;n['prim'][x['procedure_tokens']]+=1
   occ.append({'card_no':card['card_no'],'event_id':x['event_id'],'statement_id':st,'record':x['record'],'page':x['page'],'owner_code':x['owner_code'],'left_surface':left,'surface':x['observed_surface'],'right_surface':right,'back_value_de':card['literal_pocket_reading_de'],'procedure_tokens':x['procedure_tokens'],'three_card_context':f'{left} [{x["observed_surface"]}] {right}'})
 write('FIVE_HUNDRED_THIRTEENTH_99_DECK_OCCURRENCES.tsv',occ)
 fronts=[]
 for number,c in enumerate(deck,1):
  ex=next(x for x in occ if x['card_no']==c['card_no']);n=neighbors[c['card_no']]
  fronts.append({'deck_no':str(number),'card_no':c['card_no'],'front_surfaces':c['surfaces'],'back_value_de':c['literal_pocket_reading_de'],'card_kind':c['morphological_class'],'occurrences':c['events'],'dominant_procedure_tokens':top(n['prim']),'common_left_neighbors':top(n['left']),'common_right_neighbors':top(n['right']),'real_example_event':ex['event_id'],'real_example_statement':ex['statement_id'],'real_example_owner':ex['owner_code'],'real_example_context':ex['three_card_context'],'apprentice_prompt_de':'Vorderseite erkennen; Wert sprechen; Besitzer nennen; linken und rechten Nachbarn lesen.'})
 write('FIVE_HUNDRED_THIRTEENTH_SEVENTEEN_CARD_DECK.tsv',fronts)
 core=read(P510/'FIVE_HUNDRED_TENTH_37_DISTINCT_SEMANTIC_CORE.tsv');atomic_parts={x['expanded_semantic_parts'] for x in deck if x['morphological_class']=='ATOMIC_CORE_CARD'};embedded=[]
 for x in core:
  if x['item_id'].startswith('PROC') or x['item_id'] in atomic_parts:continue
  hosts=[c for c in lex if x['item_id'] in c['expanded_semantic_parts'].split('+')]
  embedded.append({'component_id':x['item_id'],'value_de':x['canonical_value_de'],'host_card_types':str(len(hosts)),'host_events':str(sum(int(c['events']) for c in hosts)),'example_host_card':hosts[0]['card_no'],'example_surface':hosts[0]['surfaces'],'example_parse':hosts[0]['expanded_semantic_parts'],'teaching_need':'EMBEDDED_COMPONENT_STRIP_REQUIRED'})
 write('FIVE_HUNDRED_THIRTEENTH_TWENTY_TWO_EMBEDDED_ONLY_CORE_VALUES.tsv',embedded)
 lines=['# Pass 513 — siebzehn echte Lehrkarten','']
 for x in fronts:
  lines.extend([f"## Karte {x['deck_no']}: `{x['front_surfaces']}`",'',f"**Rückseite:** {x['back_value_de']}",f"**Typ:** {x['card_kind']} · **Vorkommen:** {x['occurrences']}",f"**Häufig links:** `{x['common_left_neighbors']}`",f"**Häufig rechts:** `{x['common_right_neighbors']}`",f"**Echtes Beispiel:** {x['real_example_statement']} bei `{x['real_example_owner']}` — `{x['real_example_context']}`",''])
 (H/'FIVE_HUNDRED_THIRTEENTH_PRINTABLE_DECK.md').write_text('\n'.join(lines).rstrip()+'\n')
 summary={'status':'PASS','deck_cards':len(fronts),'atomic_core_cards':sum(x['card_kind']=='ATOMIC_CORE_CARD' for x in fronts),'whole_sign_cards':sum(x['card_kind']=='MEMORIZED_WHOLE_SIGN' for x in fronts),'deck_occurrences':len(occ),'embedded_only_core_values':len(embedded),'deck_event_share':round(len(occ)/381,6)}
 (H/'FIVE_HUNDRED_THIRTEENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
