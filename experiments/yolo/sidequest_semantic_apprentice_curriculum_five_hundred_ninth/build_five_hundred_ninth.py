#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P508=R/'experiments/yolo/sidequest_semantic_astro_compiler_five_hundred_eighth'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def bucket(layer):
 if layer in {'L1_SHARED_COMPONENT','L5_LEARNED_WHOLE_CARD'}:return 'MEMORIZE_CARD_VALUE'
 if layer in {'L2_OWNER_CLASS','L2_ASTRO_NAMESPACE'}:return 'READ_FROM_VISIBLE_ADDRESS_ATLAS'
 if layer in {'L3_SHARED_SENTENCE_MOTIF','L4_BIO_PRIMITIVE_PROGRAM'}:return 'PRACTISE_AS_MOTOR_TEMPLATE'
 if layer in {'L6_REDUCED_LOCAL_DECK'}:return 'COPY_FROM_LOCAL_EXEMPLAR'
 if layer in {'L8_RENDERER_HABIT','L9_GENERATIVE_ALLOGRAPH'}:return 'LEARN_GRAPHIC_RULE'
 return 'LEARN_WORKFLOW_RULE'
def lesson(cat):return {'MEMORIZE_CARD_VALUE':'L1_L2','PRACTISE_AS_MOTOR_TEMPLATE':'L3','LEARN_WORKFLOW_RULE':'L3_L4','READ_FROM_VISIBLE_ADDRESS_ATLAS':'L4_L6','LEARN_GRAPHIC_RULE':'L5','COPY_FROM_LOCAL_EXEMPLAR':'L6'}[cat]
def main():
 manual=read(P508/'FIVE_HUNDRED_EIGHTH_124_ITEM_TEN_PAGE_MANUAL.tsv');rows=[]
 for x in manual:
  c=bucket(x['layer']);rows.append({**x,'curriculum_bucket':c,'lesson_block':lesson(c),'must_memorize':'YES' if c in {'MEMORIZE_CARD_VALUE','LEARN_WORKFLOW_RULE','LEARN_GRAPHIC_RULE'} else 'NO','training_method_de':{'MEMORIZE_CARD_VALUE':'Karte zeigen, kurzen Wert sprechen, in zwei echten Kontexten schreiben.','READ_FROM_VISIBLE_ADDRESS_ATLAS':'Bildort zeigen und direkt dort nachschlagen; keine Namensliste auswendig lernen.','PRACTISE_AS_MOTOR_TEMPLATE':'Mehrfach als Kartenfolge kopieren, danach Besitzer austauschen.','LEARN_WORKFLOW_RULE':'Regel aufsagen, eine Aussage vorwärts schreiben und rückwärts prüfen.','LEARN_GRAPHIC_RULE':'Körper schreiben und Wrapper nach Register/Position ergänzen.','COPY_FROM_LOCAL_EXEMPLAR':'Nicht analysieren; am lokalen Muster wiedererkennen und kopieren.'}[c]})
 write('FIVE_HUNDRED_NINTH_124_ITEM_CURRICULUM_ASSIGNMENT.tsv',rows)
 counts=Counter(x['curriculum_bucket'] for x in rows);summary=[]
 order=['MEMORIZE_CARD_VALUE','LEARN_WORKFLOW_RULE','LEARN_GRAPHIC_RULE','PRACTISE_AS_MOTOR_TEMPLATE','READ_FROM_VISIBLE_ADDRESS_ATLAS','COPY_FROM_LOCAL_EXEMPLAR']
 for c in order:summary.append({'curriculum_bucket':c,'items':str(counts[c]),'cognitive_load':('CORE_MEMORY' if c=='MEMORIZE_CARD_VALUE' else 'RULE_MEMORY' if c in {'LEARN_WORKFLOW_RULE','LEARN_GRAPHIC_RULE'} else 'PRACTICE_NOT_LEXICAL_MEMORY' if c=='PRACTISE_AS_MOTOR_TEMPLATE' else 'LOOKUP_NOT_MEMORY' if c=='READ_FROM_VISIBLE_ADDRESS_ATLAS' else 'LOCAL_COPY_NOT_MEMORY'),'workshop_instruction_de':next(x['training_method_de'] for x in rows if x['curriculum_bucket']==c)})
 write('FIVE_HUNDRED_NINTH_MEMORY_LOAD.tsv',summary)
 lessons=[
  ('1','Kartenkern I','Die 35 gemeinsamen Komponenten in kleinen Reihen lernen.','35 components','Komponente sehen und ihren kurzen Werkstattwert nennen.'),
  ('2','Kartenkern II','Sechs gelernte Ganzkarten hinzufügen und Komponenten gegen Ganzkarten unterscheiden.','6 whole cards','Zwölf gemischte Karten ohne Zerlegung korrekt wählen.'),
  ('3','Ablauf','Fünf-Zustands-Maschine, neun Satzmotive und neun Bio-Standardwege schreiben.','18 templates + automaton','Eine offene Herbal- und drei geschlossene Bio-Aussagen erzeugen.'),
  ('4','Besitzer und Register','Vierundzwanzig Prosa-Besitzer direkt im Bild finden; Herbal offen, Bio zellenweise schreiben.','24 prose owners + 2 habits','Bei sichtbarem Wechsel Besitzer zurücksetzen, Syntax aber bei Bedarf fortführen.'),
  ('5','Schriftoberfläche','Neun Wrappergewohnheiten und fünf Allographregeln üben.','14 graphic rules','Kartenkörper in drei Positionen schreiben; seltene Form als Exemplar erkennen.'),
  ('6','Himmel und Abschluss','Dreizehn Astro-Namensräume mit LOCATE-READ-RECORD-RESET sowie lokale Exemplarstücke üben.','13 namespaces + 5 local items','Je einen Locus auf f67, f68 und f69 kopieren, ohne Richtung oder Seitenkey zu erfinden.'),
 ]
 lesson_rows=[{'day':a,'lesson':b,'content_de':c,'inventory':d,'completion_test_de':e} for a,b,c,d,e in lessons];write('FIVE_HUNDRED_NINTH_SIX_DAY_LESSON_PLAN.tsv',lesson_rows)
 ledger=read(P508/'FIVE_HUNDRED_EIGHTH_776_TEN_PAGE_COMPILER_LEDGER.tsv');pages=['f10r','f11r','f55v','f56r','f81v','f82r','f83r','f67r2','f68r1','f69v'];practice=[]
 for page in pages:
  rr=[x for x in ledger if x['page']==page];domain=rr[0]['domain']
  practice.append({'page':page,'domain':domain,'visible_items':str(len(rr)),'exercise_de':('Besitzer bestimmen; erste vollständige Aussage mit Karten und Automatenzuständen vorwärts/rückwärts schreiben.' if domain=='PROSE' else 'Ersten lokalen Namensraum und einen Locus wählen; gesamte Etikette kopieren; danach RESET.'),'forbidden_shortcut_de':('Zeilenende als Satzende behandeln' if domain=='PROSE' else 'Start, Drehrichtung oder Seitenkey erfinden'),'pass_condition_de':'Alle sichtbaren Elemente in Originalreihenfolge und richtiger lokaler Bindung.'})
 write('FIVE_HUNDRED_NINTH_TEN_PAGE_PRACTICE_SHEET.tsv',practice)
 pocket=['# Pass 509 — Taschenhandbuch für die kleine Werkstatt','', '## Was wirklich auswendig gelernt wird','', '- 35 kurze Komponentenwerte;','- 6 unteilbare Ganzkarten;','- 9 Ablaufregeln einschließlich Fünf-Zustands-Maschine;','- 14 graphische Körper-/Wrapperregeln.','', 'Bildbesitzer, Astro-Namensräume, Satzschablonen und fünf lokale Sonderstücke werden gezeigt, geübt oder aus dem Exemplar kopiert; sie sind kein zusätzlicher Wortschatz.','', '## Prosa in einem Atemzug','', 'Bildbesitzer wählen → Herbal oder Bio wählen → Primitive setzen → Karten wählen → Oberfläche schreiben → offen fortführen oder schließen → rücklesen.','', '## Astro in einem Atemzug','', 'Namensraum wählen → sichtbaren Locus adressieren → lokale Etikette kopieren → eintragen → vollständig zurücksetzen.','', '## Drei eiserne Werkstattregeln','', '1. Ein Zeilenende beendet keine Aussage.','2. Ein Besitzerwechsel setzt den Gegenstand zurück, nicht zwingend den Arbeitsablauf.','3. Eine Schlusskarte führt erst ihre örtliche Handlung aus und schließt danach.','', '## Was der Lehrling nicht können muss','', '- keine Sprache oder Lautung benennen;','- keinen f68↔f69-Schlüssel kennen;','- keine Drehrichtung raten;','- seltene Allographen frei erzeugen;','- jedes Bildobjekt mit einem eigenen Wort benennen.']
 (H/'FIVE_HUNDRED_NINTH_POCKET_MANUAL.md').write_text('\n'.join(pocket)+'\n')
 b={'status':'PASS','manual_items':len(rows),'memorized_card_values':counts['MEMORIZE_CARD_VALUE'],'workflow_rules':counts['LEARN_WORKFLOW_RULE'],'graphic_rules':counts['LEARN_GRAPHIC_RULE'],'practice_templates':counts['PRACTISE_AS_MOTOR_TEMPLATE'],'visible_address_atlas':counts['READ_FROM_VISIBLE_ADDRESS_ATLAS'],'local_exemplar_items':counts['COPY_FROM_LOCAL_EXEMPLAR'],'hard_memory_total':counts['MEMORIZE_CARD_VALUE']+counts['LEARN_WORKFLOW_RULE']+counts['LEARN_GRAPHIC_RULE'],'lessons':len(lesson_rows),'practice_pages':len(practice),'covered_visible_items':sum(int(x['visible_items']) for x in practice)}
 (H/'FIVE_HUNDRED_NINTH_BUILD_SUMMARY.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
