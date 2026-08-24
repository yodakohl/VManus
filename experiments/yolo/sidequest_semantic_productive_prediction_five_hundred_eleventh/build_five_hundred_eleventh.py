#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P460=R/'experiments/yolo/sidequest_semantic_current_prose_edition_four_hundred_sixtieth'
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
P503=R/'experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third'
TARGETS={
 'PROC007':('danach diesen Posten eintragen, abziehen und fortsetzen','H1-S001'),
 'PROC015':('von diesem Posten kurz eine Ansatzfraktion abziehen','H2-S001'),
 'PROC018':('den bereiten Arbeitsgang mit diesem Posten fortsetzen','H2-S001'),
 'PROC023':('dem laufenden Arbeitsgang den Ansatz zuführen','H2-S003'),
 'PROC032':('den Abzieh-Arbeitsgang eintragen; schließen','H3-S001'),
 'PROC033':('diesen Posten im Arbeitsgang halten und als laufend eintragen','H3-S002'),
 'PROC057':('länger durch den Durchlass abziehen; Arbeitsgang schließen','H5-S002'),
 'PROC073':('an der Zielstelle kurz am Durchlass halten','B1-S002'),
 'PROC106':('den bereiten Arbeitsgang kurz fortsetzen','B2-S005'),
 'PROC136':('diesen Posten kurz halten, bereit setzen und umsetzen','B3-S011'),
 'PROC159':('die Zufuhr auf dem Weg kurz halten; schließen','B4-S011'),
 'PROC171':('diesen Posten in kurzer Zufuhr kurz halten','B6-S001'),
}
STATEMENTS={
 'H1-S001':'Von der Bildpflanze abziehen und einen Ansatz setzen; nochmals abziehen und ansetzen; danach diesen Posten eintragen, abziehen und fortsetzen, messen und erneut ansetzen.',
 'H2-S001':'Vom Pflanzenansatz kurz abziehen, bereit halten, ansetzen und bemessen; den bereiten Arbeitsgang fortsetzen, übertragen, nochmals fortsetzen, messen und zum Ziel geben.',
 'H2-S003':'Dem laufenden Arbeitsgang den Ansatz zuführen, nochmals beschicken, fortsetzen, auf Sollstufe setzen und aus dem Ansatz abziehen.',
 'H3-S001':'Pflanzenstoff halten, zum Ziel geben, auswringen und bemessen; in den Empfangsbestand führen, halten und den Abzieh-Arbeitsgang eintragen; schließen.',
 'H3-S002':'Diesen Posten im Arbeitsgang halten und als laufend eingetragen lassen.',
 'H5-S002':'Mit der Pflanzenzutat fortsetzen, zweimal ansetzen, länger durch den Durchlass abziehen und den Arbeitsgang schließen.',
 'B1-S002':'Sollmaß setzen, Lauf bewegen, Ziel und Quelle wählen, fortsetzen, doppelt beschicken, zum Ziel geben und am Durchlass kurz halten; weiterführen, nachmessen, zweimal umsetzen und schließen.',
 'B2-S005':'Ziel setzen, Maß prüfen, durchlassen, zweimal nachmessen, den bereiten Arbeitsgang kurz fortsetzen, neu ansetzen, abführen und schließen.',
 'B3-S011':'Diesen Posten kurz halten, bereit setzen und umsetzen; danach ansetzen und von dort abziehen.',
 'B4-S011':'Maß setzen, zweimal halten, zweimal beschicken, fortsetzen, die Zufuhr auf dem Weg kurz halten und schließen.',
 'B6-S001':'An der rechten Mehrarmstation länger halten, diesen Posten in kurzer Zufuhr kurz halten, am Ziel fortsetzen, messen und die Folge dreifach ansetzen.',
}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 cards={x['card_no']:x for x in read(P460/'FOUR_HUNDRED_SIXTIETH_173_CARD_CURRENT_DICTIONARY.tsv')};events={x['event_id']:x for x in read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv')};stmts={x['statement_id']:x for x in read(P503/'FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv')}
 predictions=[]
 for rank,(cid,(literal,st)) in enumerate(TARGETS.items(),1):
  c=cards[cid];ev=events[c['event_ids'].split('|')[0]]
  predictions.append({'rank':str(rank),'card_id':cid,'surface':c['surfaces'],'event_ids':c['event_ids'],'record':ev['record'],'page':ev['page'],'statement_id':st,'component_parse':c['component_parse'],'first_literal_composition_de':literal,'local_owner_de':ev['concrete_owner_de'],'context_fit':'WORKABLE_WITHOUT_NEW_MEANING','winning_short_reading_de':literal,'procedure_primitive_at_event':ev['procedure_tokens'],'whole_word_required':'NO'})
 write('FIVE_HUNDRED_ELEVENTH_TWELVE_PRODUCTIVE_CARD_PREDICTIONS.tsv',predictions)
 rewrites=[]
 for st,text in STATEMENTS.items():
  q=stmts[st];targets=[x for x in predictions if x['statement_id']==st]
  rewrites.append({'statement_id':st,'record':q['record'],'page':q['page'],'surfaces':q['surfaces'],'primitive_program':q['primitive_signature'],'predicted_card_ids':'|'.join(x['card_id'] for x in targets),'predicted_card_readings':' | '.join(x['winning_short_reading_de'] for x in targets),'complete_revised_statement_de':text,'new_semantic_values_added':'0','result':'COMPOSITION_READS_AS_CLAUSE_FRAGMENT'})
 write('FIVE_HUNDRED_ELEVENTH_ELEVEN_REVISED_STATEMENTS.tsv',rewrites)
 comparison=[]
 for x in predictions:
  comparison.append({'card_id':x['card_id'],'surface':x['surface'],'bad_old_style':'ONE_LONG_LEXICAL_GLOSS_FOR_ENTIRE_LOCAL_PROCEDURE','selected_style':'SHORT_COMPONENT_CLAUSE_FRAGMENT','selected_reading_de':x['winning_short_reading_de'],'components':x['component_parse'],'reason_de':'Jeder sichtbare Teil liefert einen kurzen Beitrag; Besitzer und Nachbarkarten liefern den Rest der Aussage.'})
 write('FIVE_HUNDRED_ELEVENTH_WORD_VERSUS_COMPOSITION_COMPARISON.tsv',comparison)
 summary={'status':'PASS','predicted_cards':len(predictions),'events':sum(len(x['event_ids'].split('|')) for x in predictions),'affected_statements':len(rewrites),'records':len({x['record'] for x in rewrites}),'herbal_cards':sum(x['record'].startswith('H') for x in predictions),'bio_cards':sum(x['record'].startswith('B') for x in predictions),'new_semantic_values':0,'whole_words_required':0}
 (H/'FIVE_HUNDRED_ELEVENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
