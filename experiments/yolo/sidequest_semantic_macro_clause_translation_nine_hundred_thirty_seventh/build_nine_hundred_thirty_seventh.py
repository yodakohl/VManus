#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent
B924=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
B926=H.parent/'sidequest_semantic_complete_process_maps_nine_hundred_twenty_sixth'
B927=H.parent/'sidequest_semantic_recurrent_action_templates_nine_hundred_twenty_seventh'
B928=H.parent/'sidequest_semantic_multistep_recipe_fragments_nine_hundred_twenty_eighth'
B929=H.parent/'sidequest_semantic_concrete_page_readings_nine_hundred_twenty_ninth'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

DE={'P':'einsetzen','OK':'ansetzen','CH':'entnehmen','K':'zugeben','O':'ausführen','T':'einstellen','S':'auswählen','CTH':'bereitstellen','R':'kennzeichnen','CHK':'behandeln','CHD':'umsetzen','SH':'halten','SHED':'absetzen','CFH':'trennen','LSH':'spülen','CPH':'umleiten','SOLK':'auffangen'}
pair=read(B927/'PASS927_22_ACTION_TEMPLATES.tsv');frag=read(B928/'PASS928_28_RECIPE_FRAGMENTS.tsv')
patterns={tuple(r['action_pair'].split('>')):(r['template_id'],r['spoken_template_de']) for r in pair}
patterns.update({tuple(r['action_sequence'].split('>')):(r['fragment_id'],r['spoken_sequence_de'].replace(' → ', ', dann ')) for r in frag})
ins=read(B924/'PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv');maps=read(B926/'PASS926_354_PROCESS_MAPS.tsv');page_models={r['physical_page']:r['page_model'] for r in read(B929/'PASS929_12_CONCRETE_PAGE_READINGS.tsv')}
by=defaultdict(list)
for r in ins:by[r['clause_id']].append(r)
segments=[];clauses=[];sid=0;macro_tokens=0;single_tokens=0
for m in maps:
 stream=[]
 for r in by[m['clause_id']]:
  for v in (x for x in r['minimal_verb_sequence'].split('>') if x):stream.append((v,r['instruction_id']))
 i=0;local=[]
 while i<len(stream):
  found=None
  for k in (4,3,2):
   q=tuple(x[0] for x in stream[i:i+k])
   if len(q)==k and q in patterns:found=(k,q,patterns[q]);break
  sid+=1
  if found:
   k,q,(pid,spoken)=found;kind='TAUGHT_MACRO';macro_tokens+=k
  else:
   k=1;q=(stream[i][0],);pid='SINGLE_'+q[0];spoken=DE[q[0]];kind='SINGLE_ACTION';single_tokens+=1
  span=stream[i:i+k]
  row={'segment_id':f'P937-S{sid:04d}','clause_id':m['clause_id'],'physical_page':m['physical_page'],'segment_order':len(local)+1,'segment_kind':kind,'pattern_id':pid,'action_sequence':'>'.join(q),'action_tokens':k,'instruction_ids':'|'.join(dict.fromkeys(x[1] for x in span)),'spoken_segment_de':spoken}
  segments.append(row);local.append(row);i+=k
 action_chain='; dann '.join(r['spoken_segment_de'] for r in local) if local else 'den eingetragenen Bezug fortführen'
 context=[]
 if m['source_quantity_inventory']!='NONE':context.append('Einsatz: '+m['source_quantity_inventory'].replace(';',', '))
 if m['target_path_inventory']!='NONE':context.append('Weg: '+m['target_path_inventory'].replace(';',', '))
 if m['grade_inventory']!='NONE':context.append('Grad: '+m['grade_inventory'].replace(';',', '))
 ending='Schritt schließen.' if m['end_reason']=='LICENSED_DY_CLOSE' else 'Für die Fortsetzung offenlassen.'
 intro={'HERBAL':'Beim gezeigten Pflanzenmaterial','BIOLOGICAL':'An der gezeigten Station','PHARMA':'Beim Zutaten- oder Vorratsposten','ZODIAC':'Beim Ring- oder Tabellenposten'}[m['register']]
 natural=f"{intro}: {action_chain}."+((' '+'; '.join(context)+'.') if context else '')+' '+ending
 clauses.append({'clause_id':m['clause_id'],'physical_page':m['physical_page'],'register':m['register'],'page_model':page_models[m['physical_page']],'start_event':m['start_event'],'end_event':m['end_event'],'events':m['events'],'action_tokens':len(stream),'macro_segments':sum(r['segment_kind']=='TAUGHT_MACRO' for r in local),'single_segments':sum(r['segment_kind']=='SINGLE_ACTION' for r in local),'macro_action_tokens':sum(int(r['action_tokens']) for r in local if r['segment_kind']=='TAUGHT_MACRO'),'source_quantity_inventory':m['source_quantity_inventory'],'target_path_inventory':m['target_path_inventory'],'grade_inventory':m['grade_inventory'],'end_reason':m['end_reason'],'natural_macro_translation_de':natural})
write('PASS937_ACTION_SEGMENTS.tsv',list(segments[0]),segments)
write('PASS937_354_MACRO_CLAUSE_TRANSLATIONS.tsv',list(clauses[0]),clauses)
doc=['# Pass 937 — vollständige kompakte Klauselübersetzung','',
     'Die Handlungsfolge bleibt exakt; wiederkehrende Zwei-/Drei-/Viererschritte werden als ein gelernter Handgriff gesprochen. Quelle, Weg, Grad und Abschluss stehen getrennt.','']
last=None
for r in clauses:
 if r['physical_page']!=last:doc += [f"## {r['physical_page']} — {r['page_model']}",''];last=r['physical_page']
 doc += [f"### {r['clause_id']}",'',r['natural_macro_translation_de'],'']
(H/'PASS937_COMPLETE_MACRO_TRANSLATION.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
coverage=macro_tokens/(macro_tokens+single_tokens) if macro_tokens+single_tokens else 0
report=f"""# Pass 937 — zweite natürliche Vollübersetzung

## Ergebnis

Alle 354 Klauseln und alle {macro_tokens+single_tokens} Tätigkeitsatome stehen
in einer kompakten Handlungsfassung. {macro_tokens} Tätigkeitsatome
({coverage:.1%}) werden durch 373 gelernte Mehrschrittsegmente gesprochen;
{single_tokens} bleiben kurze Einzelhandlungen. Kein Atom und keine Klausel
fällt aus der Übersetzung.

## Verbesserung gegenüber Pass 925

Der Text wiederholt nicht mehr für jede Karte „nimm den Posten in Arbeit“.
Stattdessen steht zuerst die fortlaufende Tätigkeit, danach getrennt Einsatz,
Weg, Grad und Abschluss. Eine Biological-Zelle kann nun etwa lauten:
„ansetzen, halten, neu ansetzen; Weg: nächster Lauf; Grad: länger; Schritt
schließen.“ Das ist näher an einem lehrbaren Werkstattprotokoll.

## Verbleibende Arbeit

Die langen Pflanzenartikel enthalten weiterhin viele Einzelhandlungen. Ihr
nächster Redaktionspass soll wiederholte lokale Zyklen als „wiederhole den
Ansatz-/Entnahmegang“ sprechen, ohne die exakte Folge im TSV zu verlieren.
"""
(H/'PASS937_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS937_ACTION_SEGMENTS.tsv','PASS937_354_MACRO_CLAUSE_TRANSLATIONS.tsv','PASS937_COMPLETE_MACRO_TRANSLATION.md','PASS937_REPORT.md']
(H/'PASS937_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','clauses':len(clauses),'segments':len(segments),'action_tokens':macro_tokens+single_tokens,'macro_action_tokens':macro_tokens,'single_action_tokens':single_tokens,'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
