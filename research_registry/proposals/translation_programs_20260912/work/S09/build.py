from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def tab(n,ks,rs):
 with (D/n).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(ks+['row_status']);w.writerows([list(r)+['recorded'] for r in rs])
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=[x for x in read(W/'S05/INPUT.tsv') if x['record']=='f29v'];lex={x['form']:x['meaning_hypothesis'] for x in read(W/'P05/LEXICON_v03.tsv')};order={x['at']:i for i,x in enumerate(s)}
e=read(W/'S08/EVENTS_TIME.tsv');e.append({'at':'f29v.3:11','word':'sy','target_at':'OPEN','individual':'OPEN','axis':'settling','value':'settled','binding':'she3:9_otey3:10_sy3:11'})
e.sort(key=lambda x:order[x['at']]);effects={'shytchy','shot'};summary={}
tab('ALIGNMENT.tsv',['at','word','gloss'],[(x['at'],x['word'],lex.get(x['word'],'OPEN')) for x in s])
for mode in ['REPORT','REQUIRE','MIX']:
 state={};rows=[]
 for x in e:
  key=(x['individual'],x['axis']);prior=state.get(key,'UNKNOWN')
  if x['word'] in effects:state[key]=x['value'];continue
  req=mode=='REQUIRE' or (mode=='MIX' and x['word']=='sy')
  if req:status='UNKNOWN' if prior=='UNKNOWN' else ('SUPPORTED_BY_ASSUMED_EFFECT' if prior==x['value'] else 'CONTRARY_TO_LAST_EFFECT')
  else:
   status='REPORTED_NO_INDEPENDENT_CHECK' if prior in {'UNKNOWN',x['value']} else 'REPORTED_TRANSITION_UNEXPLAINED'
   if x['individual']!='OPEN':state[key]=x['value']
  rows.append((x['at'],x['word'],x['target_at'],x['individual'],x['axis'],x['value'],'REQUIREMENT' if req else 'REPORT',prior,status,'NO_INDEPENDENT_FULFILMENT'))
 tab(f'QUALITIES_{mode}.tsv',['at','word','target_at','individual','axis','value','mode','prior_effect_or_report','status','verification'],rows)
 summary[mode]={'qualities':len(rows),'requirements':sum(x[6]=='REQUIREMENT' for x in rows),'contrary_to_last_effect':sum(x[8]=='CONTRARY_TO_LAST_EFFECT' for x in rows),'unknown_requirements':sum(x[8]=='UNKNOWN' for x in rows),'reported_unexplained_transitions':sum(x[8]=='REPORTED_TRANSITION_UNEXPLAINED' for x in rows),'endpoint':'reported_reached_but_patient_unbound' if mode=='REPORT' else 'desired_reaching_unknown_patient_unbound'}
 text=[f'# S09 {mode} — vollständige Lesung mit expliziter Modalität','','Alle Wortwerte sind unveränderte P05-Hypothesen; offene Gruppe ls bleibt sichtbar. Die Rollenangaben nach jeder Zeile sind zusätzliche Satzdeutung, keine neu entzifferten Wörter.','']
 for locus in dict.fromkeys(x['locus'] for x in s):
  ss=[x for x in s if x['locus']==locus];text += ['## '+locus,'','`'+' '.join(x['word'] for x in ss)+'`','',' · '.join(lex.get(x['word'],'⟦OPEN: '+x['word']+'⟧') for x in ss),'']
  for x in rows:
   if x[0].rsplit(':',1)[0]==locus:text += [f"{x[0]}: {('Gefordert' if x[6]=='REQUIREMENT' else 'Berichtet')}: {x[3]} / {x[4]} = {x[5]}. Konto: {x[8]}. Keine unabhängig gelesene Erfüllung.",'']
  if locus=='f29v.3':text += [('Zusammenhang: Lasse ⟨ungebundenes Material⟩ stehen, bis es abgesetzt ist; der Endzustand wird hier als erreicht berichtet.' if mode=='REPORT' else 'Zusammenhang: Lasse ⟨ungebundenes Material⟩ stehen, bis es abgesetzt ist; das Erreichen ist eine offene Zielbedingung.'),'']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
tab('UNTIL_CHAIN.tsv',['mode','action','connector','quality','patient','endpoint_status','duration','independent_later_observation'],[(m,'f29v.3:9 she','f29v.3:10 otey','f29v.3:11 sy','OPEN',summary[m]['endpoint'],'UNKNOWN','NONE') for m in summary])
js('RESULT.json',{'groups':len(s),'hypothesis_occurrences':sum(x['word'] in lex for x in s),'models':summary,'written_until_chains':1,'bound_until_patients':0,'independent_fulfilment_checks':0,'decision':'Requirements do not cause transitions; endpoint reading remains unverified;stop local P05 modal repairs','confirmed_meanings':0,'held_access':False})
files=['S05/INPUT.tsv','P05/LEXICON_v03.tsv','S08/EVENTS_TIME.tsv','P11/REPORT.md','P14/REPORT.md','P15/REPORT.md','S04/REPORT.md','S09/DECISION.md']
js('SOURCE.json',{'files':[{'path':str((W/p).relative_to(R)),'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()} for p in files],'exposure':'all40targetgroups previously seen','sealed':['f84','f84r'],'new_pages':False})
print((D/'RESULT.json').read_text())
