#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P483=R/'experiments/yolo/sidequest_semantic_form_classes_four_hundred_eighty_third';P503=R/'experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third'
GLOSS={
 'PG001':'Örtlichen Halte- oder Zustandsschritt ausführen; schließen.',
 'PG002':'Den laufenden Posten bewegen oder durchlassen; schließen.',
 'PG003':'Den Posten ansetzen oder beschicken; schließen.',
 'PG004':'Fortsetzen, zwei Halte- oder Zustandsschritte ausführen; schließen.',
 'PG005':'Zwei Halte- oder Zustandsschritte ausführen; schließen.',
 'PG006':'Zweimal ansetzen oder beschicken, halten; schließen.',
 'PG007':'Ansetzen oder beschicken, halten; schließen.',
 'PG008':'Bemessen oder prüfen, zweimal ansetzen oder beschicken, halten; schließen.',
 'PG009':'Ziel oder Übergabe setzen, halten; schließen.',
}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 old=read(P483/'FOUR_HUNDRED_EIGHTY_THIRD_116_FORM_CLASS_ASSIGNMENTS.tsv');new=read(P503/'FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv');od={x['statement_id']:x for x in old};nd={x['statement_id']:x for x in new}
 cross=[]
 for st in nd:
  o=od[st];n=nd[st]
  cross.append({'statement_id':st,'record':n['record'],'page':n['page'],'old_form_class':o['form_class_id'],'old_phase_chain':o['phase_chain'],'new_program_id':n['program_id'],'new_primitive_signature':n['primitive_signature'],'new_support':n['program_support'],'new_status':n['program_status'],'relation':('OLD_AND_NEW_RECURRENT' if o['form_class_id']!='LOCAL_FORM' and n['program_status']=='RECURRENT' else 'OLD_RECURRENT_NOW_UNIQUE' if o['form_class_id']!='LOCAL_FORM' else 'NEW_RECURRENT_FROM_OLD_LOCAL' if n['program_status']=='RECURRENT' else 'LOCAL_BOTH')})
 write('FIVE_HUNDRED_FOURTH_116_OLD_NEW_FORM_CROSSWALK.tsv',cross)
 rec=read(P503/'FIVE_HUNDRED_THIRD_NINE_RECURRENT_PROGRAMS.tsv');selected=[]
 for x in rec:selected.append({'form_program_id':'BIO_'+x['program_id'],'source_program_id':x['program_id'],'primitive_signature':x['primitive_signature'],'support_statements':x['support'],'records':x['records'],'statement_ids':x['statements'],'apprentice_rule_de':GLOSS[x['program_id']],'owner_source_path_rule':'READ_SEPARATELY_FROM_OWNER_AND_CLAUSE_REGISTERS'})
 write('FIVE_HUNDRED_FOURTH_NINE_SELECTED_BIO_FORM_PROGRAMS.tsv',selected)
 lost=[x for x in cross if x['relation']=='OLD_RECURRENT_NOW_UNIQUE'];gain=[x for x in cross if x['relation']=='NEW_RECURRENT_FROM_OLD_LOCAL']
 write('FIVE_HUNDRED_FOURTH_FOUR_OLD_FALSE_RECURRENCES.tsv',lost);write('FIVE_HUNDRED_FOURTH_SIX_NEW_RECURRENCES.tsv',gain)
 manual=read(P503/'FIVE_HUNDRED_THIRD_120_ITEM_STATEMENT_PROGRAM_MANUAL.tsv');base=[x for x in manual if x['layer']!='L4_BIO_FORM_CARD'];pos=next(i for i,x in enumerate(base) if x['layer']=='L5_LEARNED_WHOLE_CARD')
 forms=[]
 for x in selected:forms.append({'manual_order':'0','layer':'L4_BIO_PRIMITIVE_PROGRAM','item_id':x['form_program_id'],'teaching_value_or_rule_de':x['apprentice_rule_de']+' ['+x['primitive_signature']+']','scope':'BIOLOGICAL','support_or_instances':x['support_statements'],'source_artifact':'PASS504_RECONCILED_BIO_PROGRAMS'})
 base[pos:pos]=forms
 for i,x in enumerate(base,1):x['manual_order']=str(i)
 write('FIVE_HUNDRED_FOURTH_122_ITEM_RECONCILED_MANUAL.tsv',base)
 ledger=read(P503/'FIVE_HUNDRED_THIRD_776_STATEMENT_PROGRAM_LEDGER.tsv');recids={x['source_program_id'] for x in selected};out=[]
 for x in ledger:
  n=dict(x);n['old_bio_form_class']=od[x['statement_or_locus']]['form_class_id'] if x['domain']=='PROSE' else 'NONE';n['bio_form_program']='BIO_'+x['statement_program'] if x['domain']=='PROSE' and x['statement_program'] in recids else 'NONE';out.append(n)
 write('FIVE_HUNDRED_FOURTH_776_RECONCILED_FORM_LEDGER.tsv',out)
 s={'status':'PASS','statements':len(cross),'old_form_cards':7,'old_recurrent_statements':sum(x['old_form_class']!='LOCAL_FORM' for x in cross),'new_form_programs':len(selected),'new_recurrent_statements':sum(x['new_status']=='RECURRENT' for x in cross),'old_recurrent_now_unique':len(lost),'new_recurrent_from_old_local':len(gain),'overlap_recurrent':sum(x['relation']=='OLD_AND_NEW_RECURRENT' for x in cross),'manual_before':len(manual),'manual_after':len(base),'ledger':len(out)};(H/'FIVE_HUNDRED_FOURTH_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
