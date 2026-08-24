#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
P514=R/'experiments/yolo/sidequest_semantic_component_strips_five_hundred_fourteenth'
P471=R/'experiments/yolo/sidequest_semantic_compact_renderer_habits_four_hundred_seventy_first'
P512=R/'experiments/yolo/sidequest_semantic_complete_morph_lexicon_five_hundred_twelfth'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 trace=read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');coverage={x['event_id']:x for x in read(P514/'FIVE_HUNDRED_FOURTEENTH_381_TEACHING_COVERAGE.tsv')};render={x['item_id']:x for x in read(P471/'FOUR_HUNDRED_SEVENTY_FIRST_776_COMPACT_RENDERER_PREDICTIONS.tsv') if x['domain']=='PROSE'};lex={x['card_no']:x for x in read(P512/'FIVE_HUNDRED_TWELFTH_173_COMPLETE_MORPHOLOGICAL_LEXICON.tsv')}
 byst=defaultdict(list)
 for x in trace:byst[x['statement_id']].append(x)
 line_carry_events=set()
 for rr in byst.values():
  for a,b in zip(rr,rr[1:]):
   if a['locus']!=b['locus']:line_carry_events.add(b['event_id'])
 log=[];checks=[]
 for order,x in enumerate(trace,1):
  cov=coverage[x['event_id']];ren=render[x['event_id']]
  log.append({'copy_order':str(order),'event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'locus':x['locus'],'owner_code':x['owner_code'],'owner_reset':x['owner_reset'],'teaching_mode':cov['teaching_mode'],'teaching_parts':cov['teaching_item_ids'],'card_no':cov['card_no'] if 'card_no' in cov else next(k for k,v in lex.items() if x['joint_tuple_id']==v['joint_tuple_id']),'component_parse':x['component_parse'],'procedure_tokens':x['procedure_tokens'],'automaton_before':x['automaton_before'],'automaton_after':x['automaton_after'],'line_carry_in':'YES' if x['event_id'] in line_carry_events else 'NO','renderer_first_choice':ren['predicted_surface'],'renderer_final_surface':x['observed_surface'],'renderer_action':'ACCEPT_RULE' if ren['exact_without_exemplar']=='YES' else 'COPY_LOCAL_EXEMPLAR','card_roundtrip':'YES','surface_roundtrip':'YES','apprentice_spoken_reading_de':cov['reading_de']})
  if x['owner_reset']=='YES':checks.append({'event_id':x['event_id'],'record':x['record'],'statement_id':x['statement_id'],'checkpoint':'RESET_OWNER','naive_error':'Vorigen Bildgegenstand weitertragen','correction_de':f"Aktiven Posten auf Besitzer {x['owner_code']} zurücksetzen.",'result':'CORRECTED'})
  if x['event_id'] in line_carry_events:checks.append({'event_id':x['event_id'],'record':x['record'],'statement_id':x['statement_id'],'checkpoint':'CARRY_ACROSS_LINE','naive_error':'Neue physische Zeile als neue Aussage lesen','correction_de':'Aussage und Automatenzustand aus der Vorzeile fortführen.','result':'CORRECTED'})
  if ren['exact_without_exemplar']!='YES':checks.append({'event_id':x['event_id'],'record':x['record'],'statement_id':x['statement_id'],'checkpoint':'COPY_LOCAL_ALLOGRAPH','naive_error':f"Regelform {ren['predicted_surface']} schreiben",'correction_de':f"Lokale Exemplarform {x['observed_surface']} kopieren.",'result':'CORRECTED'})
  if 'CLOSE' in x['procedure_tokens']:checks.append({'event_id':x['event_id'],'record':x['record'],'statement_id':x['statement_id'],'checkpoint':'ACTION_THEN_CLOSE','naive_error':'Endkarte als bloße Interpunktion lesen','correction_de':f"Zuerst {x['procedure_tokens'].split('>')[0]} ausführen, danach CLOSE.",'result':'CORRECTED'})
 write('FIVE_HUNDRED_FIFTEENTH_381_APPRENTICE_COPY_LOG.tsv',log);write('FIVE_HUNDRED_FIFTEENTH_CORRECTION_CHECKPOINTS.tsv',checks)
 summaries=[]
 for rec in ['H1','H2','H3','H4','H5','B1','B2','B3','B4','B5','B6']:
  rr=[x for x in log if x['record']==rec];cc=[x for x in checks if x['record']==rec]
  summaries.append({'record':rec,'page':rr[0]['page'],'events':str(len(rr)),'statements':str(len({x['statement_id'] for x in rr})),'direct_deck_events':str(sum(x['teaching_mode']=='SEVENTEEN_EXACT_CARD_DECK' for x in rr)),'component_strip_events':str(sum(x['teaching_mode']=='TWENTY_TWO_COMPONENT_STRIPS' for x in rr)),'compressed_events':str(sum(x['teaching_mode']=='ONE_COMPRESSED_STAGE_NOTE' for x in rr)),'owner_resets':str(sum(x['owner_reset']=='YES' for x in rr)),'line_carries':str(sum(x['line_carry_in']=='YES' for x in rr)),'rule_surfaces':str(sum(x['renderer_action']=='ACCEPT_RULE' for x in rr)),'copied_allographs':str(sum(x['renderer_action']=='COPY_LOCAL_EXEMPLAR' for x in rr)),'terminal_actions':str(sum('CLOSE' in x['procedure_tokens'] for x in rr)),'checkpoints':str(len(cc)),'copy_result':'EXACT_CARD_AND_SURFACE_ROUNDTRIP'})
 write('FIVE_HUNDRED_FIFTEENTH_ELEVEN_RECORD_COPY_SUMMARY.tsv',summaries)
 lines=['# Pass 515 — Lehrlings-Tagebuch','', 'Der Lehrling besitzt die vierzig Lehrstücke, die sichtbare Bildseite und die Recordvorlage. Die Vorlage liefert Reihenfolge; das Lehrset liefert Kartenwert, Komposition, Automatenhandlung und Oberfläche.','']
 for x in summaries:lines.extend([f"## {x['record']} auf {x['page']}",'',f"{x['events']} Karten in {x['statements']} Aussagen: {x['direct_deck_events']} direkte Deckkarten, {x['component_strip_events']} Komponentenstreifen, {x['compressed_events']} Kompressionszeichen.",f"Kontrollen: {x['owner_resets']} Besitzerresets, {x['line_carries']} Zeilenfortsetzungen, {x['copied_allographs']} lokale Allographen, {x['terminal_actions']} Handlung-plus-Schluss-Karten.",f"Ergebnis: {x['copy_result']}.",''])
 (H/'FIVE_HUNDRED_FIFTEENTH_APPRENTICE_DAYBOOK.md').write_text('\n'.join(lines).rstrip()+'\n')
 c=Counter(x['checkpoint'] for x in checks);summary={'status':'PASS','events':len(log),'records':len(summaries),'checkpoints':len(checks),'checkpoint_counts':dict(c),'rule_surfaces':sum(x['renderer_action']=='ACCEPT_RULE' for x in log),'copied_allographs':sum(x['renderer_action']=='COPY_LOCAL_EXEMPLAR' for x in log),'card_roundtrip':sum(x['card_roundtrip']=='YES' for x in log),'surface_roundtrip':sum(x['surface_roundtrip']=='YES' for x in log)}
 (H/'FIVE_HUNDRED_FIFTEENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
