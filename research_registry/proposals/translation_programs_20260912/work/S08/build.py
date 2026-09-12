from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def tab(n,keys,rows):
 with (D/n).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(keys+['row_status']);w.writerows([list(r)+['recorded'] for r in rows])
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=[x for x in read(W/'S05/INPUT.tsv') if x['record']=='f29v'];lex={x['form']:x['meaning_hypothesis'] for x in read(W/'P05/LEXICON_v03.tsv')};mat=set(json.loads((W/'P05/REFERENCE_RULE_v02.json').read_text())['material_forms'])|{'odaiin'}
by={x['at']:x for x in s};tab('ALIGNMENT.tsv',['at','word','gloss'],[(x['at'],x['word'],lex.get(x['word'],'OPEN')) for x in s])
# Explicit authored bindings; moisture of interior is kept distinct from whole material.
events=[('f29v.1:6','f29v.1:7','whole_moisture','wet','action_effect'),('f29v.1:8','f29v.1:7','interior_moisture','wet','state_of_cho'),('f29v.1:10','f29v.1:11','dose_moisture','wet','dose_material_unknown'),('f29v.2:3','f29v.1:7','whole_moisture','dry','P05_double_first'),('f29v.2:4','f29v.2:1','whole_moisture','dry','P05_double_second'),('f29v.3:1','f29v.2:7','whole_moisture','dry','P05_double_first'),('f29v.3:2','f29v.2:8','whole_moisture','dry','P05_double_second'),('f29v.4:2','f29v.4:3','temperature','cool','right_target'),('f29v.4:5','f29v.4:4','temperature','cooled','left_target_prior_heat_unbound'),('f29v.4:7','f29v.4:8','temperature','warmed','right_fluid_not_ansatz')]
summary={}
for mode in ['SAME','FRESH','TIME']:
 ids={x['at']:(x['at'] if mode=='FRESH' else x['word']) for x in s if x['word'] in mat};ids['f29v.1:11']='DOSE_UNBOUND'
 tab(f'MATERIALS_{mode}.tsv',['at','word','individual'],[(x['at'],x['word'],ids[x['at']]) for x in s if x['at'] in ids])
 state={};previous={};out=[]
 for at,target,axis,value,kind in events:
  key=(ids[target],axis);old=state.get(key,'UNKNOWN');status='SET_OR_COMPATIBLE'
  if old!='UNKNOWN' and old!=value:
   status='TRANSITION_UNEXPLAINED' if mode=='TIME' else 'PERSISTENCE_CONFLICT'
  out.append((at,by[at]['word'],target,ids[target],axis,old,value,status,previous.get(key,'NONE'),kind));state[key]=value;previous[key]=at
 tab(f'EVENTS_{mode}.tsv',['at','word','target_at','individual','axis','prior','value','status','prior_event','binding'],out)
 summary[mode]={'material_individuals':len({ids[x['at']] for x in s if x['word'] in mat}),'persistence_conflicts':sum(o[7]=='PERSISTENCE_CONFLICT' for o in out),'unexplained_transitions':sum(o[7]=='TRANSITION_UNEXPLAINED' for o in out),'issue_endpoints':[(o[8],o[0],o[2]) for o in out if o[7]!='SET_OR_COMPATIBLE']}
 prose={
 'SAME':['Wurzelgut, Samen: zerkleinere ⟨beide⟩ mit ⟦ls offen⟧. Benetze Pflanzengut A. Feucht: dessen Inneres; feucht: festgelegte Dosis ⟨Stoffbezug offen⟩.','Abgetrenntes Feinpulver, je ⟨Einheit⟩. Trocken: ⟨das zuvor benetzte Pflanzengut A⟩; trocken: ⟨das Feinpulver⟩. Pflanzengut A; prüfe Pflanzenrückstand. Zerkleinerte Blüten: Teilmenge.','Trocken: ⟨Pflanzenrückstand⟩; trocken: ⟨zerkleinerte Blüten⟩. Mörser: fülle Zusatzmenge ein. Siebe ⟨Materialbezug offen⟩ in Auffanggefäß, je ⟨Einheit⟩. Lasse ⟨es⟩ stehen, bis abgesetzt.','Flüssigkeitszugabe; kühl: Ansatz X. Pflanzengut A: abgekühlt, je ⟨Einheit⟩. Erwärme Flüssigkeit ⟨für⟩ Ansatz X.'],
 'FRESH':['Wurzelgut, Samen: zerkleinere ⟨beide⟩ mit ⟦ls offen⟧. Benetze Pflanzengut A. Feucht: dessen Inneres; feucht: festgelegte Dosis ⟨Stoffbezug offen⟩.','Abgetrenntes Feinpulver, je ⟨Einheit⟩. Trocken: ⟨weiterhin Pflanzengut A aus .1⟩; trocken: ⟨das Feinpulver⟩. Pflanzengut B ⟨erst hier neu⟩; prüfe Pflanzenrückstand. Zerkleinerte Blüten: Teilmenge.','Trocken: ⟨Pflanzenrückstand⟩; trocken: ⟨zerkleinerte Blüten⟩. Mörser: fülle Zusatzmenge ein. Siebe ⟨Materialbezug offen⟩ in Auffanggefäß, je ⟨Einheit⟩. Lasse ⟨es⟩ stehen, bis abgesetzt.','Flüssigkeitszugabe; kühl: Ansatz X. Pflanzengut C ⟨neue Portion⟩: abgekühlt, je ⟨Einheit⟩. Erwärme Flüssigkeit ⟨für neuen⟩ Ansatz Y.'],
 }
 prose['TIME']=prose['SAME'].copy();prose['TIME'][1]=prose['TIME'][1].replace('das zuvor benetzte Pflanzengut A','das nun trocken genannte Pflanzengut A; Zustandswechsel unerklärt')
 text=['# S08 '+mode+' — vollständiger hypothetischer Entwurf','','⟨…⟩ kennzeichnet ergänzte Bindungen; ⟦…⟧ eine offene Quellgruppe. Keine bestätigte Übersetzung. Die feste Wortausrichtung ist maßgeblich.','']
 for n,p in enumerate(prose[mode],1):
  rr=[x for x in s if x['locus']==f'f29v.{n}'];text += [f'## f29v.{n}','','`'+' '.join(x['word'] for x in rr)+'`','',p,'']
 text+=['Ergebnis: '+json.dumps(summary[mode],ensure_ascii=False),'','Weder Erzeugung des Feinpulvers/Rückstands aus A noch spätere Rückführung sind gebunden. Abgekühlt hat keinen zuvor bezeichneten Erwärmungsschritt desselben Materials. Erwärmte Flüssigkeit ist nicht identisch mit dem kühl beschriebenen Ansatz.']
 (D/f'READING_{mode}.md').write_text('\n'.join(text).rstrip()+'\n')
js('RESULT.json',{'groups':len(s),'hypothesis_occurrences':sum(x['word'] in lex for x in s),'open_occurrences':sum(x['word'] not in lex for x in s),'events_per_model':len(events),'models':summary,'decision':'FRESH does not remove earlier wet/dry issue; TIME leaves mechanism unknown, not contradiction','confirmed_meanings':0,'held_access':False})
files=['S05/INPUT.tsv','P05/LEXICON_v03.tsv','P05/REFERENCE_RULE_v02.json','P05/REPORT.md','P12/MODEL.json','S07/REPORT.md','S08/DECISION.md']
js('SOURCE.json',{'files':[{'path':str((W/p).relative_to(R)),'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()} for p in files],'exposure':'all40groups and predecessor results already exposed','sealed':['f84','f84r'],'new_pages':False})
print((D/'RESULT.json').read_text())
