#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P460=R/'experiments/yolo/sidequest_semantic_current_prose_edition_four_hundred_sixtieth'
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
P510=R/'experiments/yolo/sidequest_semantic_core_deduplication_five_hundred_tenth'
SHORT={'AIIN':'Maß','AIN':'Portion','AIR':'Lauf','AL':'Zielstelle','AR':'von dort','CH':'abziehen','CHD':'umsetzen','CHK':'wärmen','CKH':'Durchlass','CTH':'bereit','DY':'Schluss','E':'kurz','EE':'länger','EEE':'vollständig','IIN':'Sollstufe','K':'zuführen','L':'führen','LDDY':'befestigen; Schluss','LSH':'Waschgang','O':'Arbeitsgang','OK':'ansetzen','OL':'fortsetzen','OR':'Ansatz','OT':'danach','P':'hinein','R':'abkühlen','SH':'halten','SHED':'absetzen','SOLK':'auffangen','T':'eintragen','Y':'dies','HO':'Gabe'}
EXPAND={'CKHE':['CKH','E'],'CHEO':['CH','E','O'],'LS':['OL']}
WHOLE={'PROC005':'Arbeitsfach','PROC028':'auswringen','PROC031':'Empfangsbestand','PROC043':'verwahren','PROC124':'teilen'}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 cards=read(P460/'FOUR_HUNDRED_SIXTIETH_173_CARD_CURRENT_DICTIONARY.tsv');lex=[]
 for c in cards:
  if c['card_no'] in WHOLE:
   cls='MEMORIZED_WHOLE_SIGN';parts=[c['card_no']];reading=WHOLE[c['card_no']];rule='Ganzzeichen als einen kurzen Werkstattwert lernen.'
  elif c['card_no']=='PROC169':
   cls='COMPRESSED_KNOWN_VALUE_SIGN';parts=['IIN','GRADE_II'];reading='Sollstufe · zweite';rule='Komprimiertes Zeichen auf bekannte Sollstufe II zurückführen.'
  else:
   parts=[]
   for p in c['component_parse'].split('+'):parts.extend(EXPAND.get(p,[p]))
   cls='ATOMIC_CORE_CARD' if len(parts)==1 else 'FULL_COMPONENT_COMPOSITION';reading=' · '.join(SHORT[p] for p in parts);rule='Kernwert direkt lesen.' if len(parts)==1 else 'Komponenten von links nach rechts lesen; Bildbesitzer ergänzt DIES, DORT und STELLE.'
  lex.append({'card_no':c['card_no'],'joint_tuple_id':c['joint_tuple_id'],'surfaces':c['surfaces'],'events':c['events'],'event_ids':c['event_ids'],'registers':c['registers'],'records':c['records'],'source_component_parse':c['component_parse'],'expanded_semantic_parts':'+'.join(parts),'semantic_part_count':str(len(parts)),'morphological_class':cls,'literal_pocket_reading_de':reading,'apprentice_rule_de':rule})
 write('FIVE_HUNDRED_TWELFTH_173_COMPLETE_MORPHOLOGICAL_LEXICON.tsv',lex)
 ld={x['joint_tuple_id']:x for x in lex};events=read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');er=[]
 for x in events:
  q=ld[x['joint_tuple_id']];er.append({'event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'locus':x['locus'],'surface':x['observed_surface'],'card_no':q['card_no'],'owner_code':x['owner_code'],'morphological_class':q['morphological_class'],'expanded_semantic_parts':q['expanded_semantic_parts'],'literal_card_reading_de':q['literal_pocket_reading_de'],'procedure_tokens':x['procedure_tokens'],'contextual_reading_rule':'Bind DIES/DORT/STELLE to owner; execute procedure; CLOSE only when emitted.'})
 write('FIVE_HUNDRED_TWELFTH_381_EVENT_MORPHOLOGICAL_READINGS.tsv',er)
 by=defaultdict(list)
 for x in er:by[x['statement_id']].append(x)
 sr=[]
 for st,rr in by.items():sr.append({'statement_id':st,'record':rr[0]['record'],'page':rr[0]['page'],'events':str(len(rr)),'surfaces':' '.join(x['surface'] for x in rr),'card_classes':'|'.join(x['morphological_class'] for x in rr),'literal_component_chain_de':' ; '.join(x['literal_card_reading_de'] for x in rr),'procedure_program':'>'.join(t for x in rr for t in x['procedure_tokens'].split('>')),'whole_sign_events':str(sum(x['morphological_class']=='MEMORIZED_WHOLE_SIGN' for x in rr))})
 sr.sort(key=lambda x:(x['record'],int(x['statement_id'].split('S')[1])));write('FIVE_HUNDRED_TWELFTH_116_STATEMENT_MORPHOLOGICAL_READINGS.tsv',sr)
 cnt=Counter(x['morphological_class'] for x in lex);ecnt=Counter(x['morphological_class'] for x in er);rows=[]
 for cls in ['ATOMIC_CORE_CARD','FULL_COMPONENT_COMPOSITION','COMPRESSED_KNOWN_VALUE_SIGN','MEMORIZED_WHOLE_SIGN']:rows.append({'morphological_class':cls,'card_types':str(cnt[cls]),'events':str(ecnt[cls]),'learning_mode':{'ATOMIC_CORE_CARD':'core recall','FULL_COMPONENT_COMPOSITION':'left-to-right composition','COMPRESSED_KNOWN_VALUE_SIGN':'known-value compression','MEMORIZED_WHOLE_SIGN':'whole-sign recall'}[cls]})
 write('FIVE_HUNDRED_TWELFTH_MORPHOLOGY_COUNTS.tsv',rows)
 core=read(P510/'FIVE_HUNDRED_TENTH_37_DISTINCT_SEMANTIC_CORE.tsv');md=['# Pass 512 — vollständiges morphologisches Taschenlexikon','', '## 37 Bedeutungswerte','']
 for x in core:md.append(f"- `{x['item_id']}` — {x['canonical_value_de']}")
 md+=['','## Drei abgeleitete Zeichenregeln','', '- `CKHE` → `CKH+E`: Durchlass · kurz','- `CHEO` → `CH+E+O`: abziehen · kurz · Arbeitsgang','- `LS` → `OL`: fortsetzen','', '## Eine komprimierte Stufe','', '- `daiiin` → Sollstufe II','', '## Fünf unteilbare Ganzzeichen','']
 for k,v in WHOLE.items():
  surf=next(x['surfaces'] for x in lex if x['card_no']==k);md.append(f'- `{surf}` — {v}')
 md+=['','## Gesamtbild','',f"- {cnt['FULL_COMPONENT_COMPOSITION']} Mehrteilkompositionen;",f"- {cnt['ATOMIC_CORE_CARD']} direkte Kernkarten;",f"- {cnt['COMPRESSED_KNOWN_VALUE_SIGN']} komprimiertes bekanntes Zeichen;",f"- {cnt['MEMORIZED_WHOLE_SIGN']} unteilbare Ganzzeichen.",'','Die vollständigen 173 Karten stehen in der TSV-Ausgabe; jede der 381 Prosastellen ist im Ereignisledger rückgebunden.']
 (H/'FIVE_HUNDRED_TWELFTH_POCKET_LEXICON.md').write_text('\n'.join(md)+'\n')
 summary={'status':'PASS','card_types':len(lex),'events':len(er),'statements':len(sr),'class_card_counts':dict(cnt),'class_event_counts':dict(ecnt),'distinct_semantic_values':len(core),'derived_rules':3,'compressed_signs':1,'memorized_whole_signs':5}
 (H/'FIVE_HUNDRED_TWELFTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
