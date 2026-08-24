#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P513=R/'experiments/yolo/sidequest_semantic_seventeen_card_deck_five_hundred_thirteenth'
P512=R/'experiments/yolo/sidequest_semantic_complete_morph_lexicon_five_hundred_twelfth'
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 components=read(P513/'FIVE_HUNDRED_THIRTEENTH_TWENTY_TWO_EMBEDDED_ONLY_CORE_VALUES.tsv');lex=read(P512/'FIVE_HUNDRED_TWELFTH_173_COMPLETE_MORPHOLOGICAL_LEXICON.tsv');events=read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');event_by={x['event_id']:x for x in events};examples=[];strips=[]
 for rank,comp in enumerate(sorted(components,key=lambda x:(-int(x['host_events']),x['component_id'])),1):
  hosts=[x for x in lex if comp['component_id'] in x['expanded_semantic_parts'].split('+')];hosts.sort(key=lambda x:(-int(x['events']),x['card_no']))
  chosen=[];used_records=set()
  for host in hosts:
   if len(chosen)>=3:break
   recs=set(host['records'].split('|'))
   if not chosen or recs-used_records:chosen.append(host);used_records|=recs
  for host in hosts:
   if len(chosen)>=3:break
   if host not in chosen:chosen.append(host)
  ids=[]
  for n,host in enumerate(chosen,1):
   ev=event_by[host['event_ids'].split('|')[0]];parts=host['expanded_semantic_parts'].split('+');marked='+'.join(f'[{p}]' if p==comp['component_id'] else p for p in parts);eid=f"STRIP{rank:02d}_EX{n}"
   examples.append({'example_id':eid,'strip_no':str(rank),'component_id':comp['component_id'],'value_de':comp['value_de'],'host_card_no':host['card_no'],'host_surfaces':host['surfaces'],'highlighted_parse':marked,'event_id':ev['event_id'],'statement_id':ev['statement_id'],'record':ev['record'],'page':ev['page'],'owner_code':ev['owner_code'],'procedure_tokens':ev['procedure_tokens'],'literal_host_reading_de':host['literal_pocket_reading_de']});ids.append(eid)
  strips.append({'strip_no':str(rank),'component_id':comp['component_id'],'back_value_de':comp['value_de'],'host_card_types':comp['host_card_types'],'host_events':comp['host_events'],'selected_example_ids':'|'.join(ids),'selected_examples':str(len(ids)),'standalone_exact_card':'NO','teaching_instruction_de':'Markierten Bestandteil in jeder Wirtkarte sprechen; übrige Bestandteile danach links nach rechts ergänzen.'})
 write('FIVE_HUNDRED_FOURTEENTH_TWENTY_TWO_COMPONENT_STRIPS.tsv',strips);write('FIVE_HUNDRED_FOURTEENTH_HOST_EXAMPLES.tsv',examples)
 event_morph=read(P512/'FIVE_HUNDRED_TWELFTH_381_EVENT_MORPHOLOGICAL_READINGS.tsv');coverage=[]
 for x in event_morph:
  if x['morphological_class'] in {'ATOMIC_CORE_CARD','MEMORIZED_WHOLE_SIGN'}:mode='SEVENTEEN_EXACT_CARD_DECK'
  elif x['morphological_class']=='FULL_COMPONENT_COMPOSITION':mode='TWENTY_TWO_COMPONENT_STRIPS'
  else:mode='ONE_COMPRESSED_STAGE_NOTE'
  coverage.append({'event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'surface':x['surface'],'morphological_class':x['morphological_class'],'teaching_mode':mode,'teaching_item_ids':x['expanded_semantic_parts'],'reading_de':x['literal_card_reading_de']})
 write('FIVE_HUNDRED_FOURTEENTH_381_TEACHING_COVERAGE.tsv',coverage)
 lines=['# Pass 514 — zweiundzwanzig Komponentenstreifen','']
 bystrip=defaultdict(list)
 for x in examples:bystrip[x['strip_no']].append(x)
 for s in strips:
  lines.extend([f"## Streifen {s['strip_no']}: `{s['component_id']}`",'',f"**Rückseite:** {s['back_value_de']}",f"**Wirtskarten:** {s['host_card_types']} Typen / {s['host_events']} Ereignisse",''])
  for x in bystrip[s['strip_no']]:lines.append(f"- `{x['host_surfaces']}` · `{x['highlighted_parse']}` · {x['statement_id']} bei `{x['owner_code']}`")
  lines.append('')
 (H/'FIVE_HUNDRED_FOURTEENTH_PRINTABLE_COMPONENT_STRIPS.md').write_text('\n'.join(lines).rstrip()+'\n')
 modes=defaultdict(int)
 for x in coverage:modes[x['teaching_mode']]+=1
 summary={'status':'PASS','component_strips':len(strips),'host_examples':len(examples),'min_examples':min(int(x['selected_examples']) for x in strips),'max_examples':max(int(x['selected_examples']) for x in strips),'coverage_events':len(coverage),'exact_deck_events':modes['SEVENTEEN_EXACT_CARD_DECK'],'component_strip_events':modes['TWENTY_TWO_COMPONENT_STRIPS'],'compressed_note_events':modes['ONE_COMPRESSED_STAGE_NOTE'],'total_physical_teaching_items':17+22+1}
 (H/'FIVE_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
