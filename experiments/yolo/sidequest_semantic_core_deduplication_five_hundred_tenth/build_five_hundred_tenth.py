#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P509=R/'experiments/yolo/sidequest_semantic_apprentice_curriculum_five_hundred_ninth'
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
P460=R/'experiments/yolo/sidequest_semantic_current_prose_edition_four_hundred_sixtieth'
RECLASS={
 'CKHE':('COMPOSE_FROM_CKH_PLUS_E','CKH+E','COMPOSITION: Durchlass kurz führen','Kein eigenes SEIHEN-Wort; SH/L-Hülle bestimmt Halten oder Führen.'),
 'CHEO':('COMPOSE_FROM_CH_PLUS_E_PLUS_O','CH+E+O','COMPOSITION: kurzer Abzieh-Arbeitsgang; Resultat Auszug','Auszug ist das Resultat der bereits gelernten drei Teile.'),
 'LS':('ALIAS_OF_OL','OL','ALIAS: fortsetzen','Einmalige Kurzkarte; Ereignisfunktion CONTINUE_USE stimmt mit OL überein.'),
 'PROC169':('COMPRESSED_GRADE_SIGN','IIN+GRADE_II','COMPRESSION: Sollstufe II','Die Karte nennt keine neue Sache, sondern eine bestimmte bekannte Stufe.'),
}
NEIGHBORS={
 'AIIN':'AIN|IIN','AIN':'AIIN|HO','AIR':'CKH|L','AL':'AR|P','AR':'AL|CH','CH':'LS|SOURCE_DRAW','CHD':'L|K','CHK':'R|SHED','CKH':'AIR|CKHE','CTH':'EEE|SH','DY':'LDDY|Y','E':'EE|EEE','EE':'E|EEE','EEE':'EE|CTH','IIN':'AIIN|PROC169','K':'P|T','L':'CHD|P','LDDY':'DY|PROC043','LSH':'SHED|CKH','O':'OK|OR','OK':'O|K','OL':'OT|LS','OR':'O|PROC031','OT':'OL|T','P':'K|L','R':'CHK|SHED','SH':'SHED|CTH','SHED':'SH|R','SOLK':'PROC031|CKH','T':'K|P','Y':'AIN|OR','HO':'AIN|OR','PROC005':'AL|O','PROC028':'CH|CKH','PROC031':'SOLK|OR','PROC043':'LDDY|DY','PROC124':'AIN|CHD'
}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 assignment=read(P509/'FIVE_HUNDRED_NINTH_124_ITEM_CURRICULUM_ASSIGNMENT.tsv');cards=[x for x in assignment if x['curriculum_bucket']=='MEMORIZE_CARD_VALUE'];audit=[]
 for x in cards:
  if x['item_id'] in RECLASS:
   decision,canonical,revised,reason=RECLASS[x['item_id']];new='NO'
  else:
   decision,canonical,revised,reason='KEEP_DISTINCT',x['item_id'],x['teaching_value_or_rule_de'],'Distinct source, target, quantity, motion, state, object or endpoint role.';new='YES'
  audit.append({'item_id':x['item_id'],'old_value_de':x['teaching_value_or_rule_de'],'nearest_candidates':NEIGHBORS.get(x['item_id'],'NONE'),'decision':decision,'canonical_semantic_source':canonical,'revised_teaching_value_de':revised,'adds_new_semantic_value':new,'reason_de':reason,'support_or_instances':x['support_or_instances'],'scope':x['scope']})
 write('FIVE_HUNDRED_TENTH_41_CARD_VALUE_OVERLAP_AUDIT.tsv',audit)
 core=[{'core_no':str(i),'item_id':x['item_id'],'canonical_value_de':x['revised_teaching_value_de'],'semantic_role':x['revised_teaching_value_de'].split(':',1)[0],'support_or_instances':x['support_or_instances'],'scope':x['scope']} for i,x in enumerate([x for x in audit if x['adds_new_semantic_value']=='YES'],1)]
 write('FIVE_HUNDRED_TENTH_37_DISTINCT_SEMANTIC_CORE.tsv',core)
 revised=[]
 for x in assignment:
  n=dict(x)
  if x['item_id'] in RECLASS:
   n['teaching_value_or_rule_de']=RECLASS[x['item_id']][2];n['curriculum_bucket']='LEARN_COMPOSITE_ALIAS_SIGN';n['lesson_block']='L2_L3';n['must_memorize']='YES';n['training_method_de']='Bekannte Kernwerte zusammensetzen oder den Alias auf seinen Kern zurückführen; keine neue Bedeutung lernen.'
  revised.append(n)
 write('FIVE_HUNDRED_TENTH_124_ITEM_DEDUPLICATED_CURRICULUM.tsv',revised)
 events=read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');d460={x['card_no']:x for x in read(P460/'FOUR_HUNDRED_SIXTIETH_173_CARD_CURRENT_DICTIONARY.tsv')}
 selected=[]
 for x in events:
  parts=x['component_parse'].replace('[','+').replace(']','').split('+');ids=[]
  for item in ('CKHE','CHEO','LS'):
   if item in parts:ids.append(item)
  if x['event_id'] in d460['PROC169']['event_ids'].split('|'):ids.append('PROC169')
  for item in ids:selected.append({'event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'surface':x['observed_surface'],'old_component_or_card':item,'old_value_de':next(y['old_value_de'] for y in audit if y['item_id']==item),'new_analysis':RECLASS[item][1],'new_value_de':RECLASS[item][2],'procedure_tokens':x['procedure_tokens'],'meaning_inventory_change':'NO_NEW_SEMANTIC_VALUE'})
 write('FIVE_HUNDRED_TENTH_EIGHT_RECLASSIFIED_EVENTS.tsv',selected)
 summary={'status':'PASS','audited_card_values':len(audit),'distinct_semantic_values':len(core),'composite_or_alias_signs':len(RECLASS),'reclassified_events':len(selected),'manual_items_unchanged':len(revised),'active_forms_and_rules_memory':37+4+9+14,'semantic_meanings_removed':['CKHE=SEIHEN','CHEO=AUSZUG_AS_ATOM','LS=ABFUEHREN','PROC169=NEW_STAGE_WORD']}
 (H/'FIVE_HUNDRED_TENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
