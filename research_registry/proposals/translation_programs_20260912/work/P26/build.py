import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P26')
S=D.parent/'P12/PROSE.tsv'
records={}
for r in csv.DictReader(S.open(),delimiter='\t'):
 records.setdefault(r['record_id'],[]).extend(dict(record=r['record_id'],at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['zl3b_line'].split(),1))
lex={'qokaiin':'Material A','shedy':'Material B','lchedy':'Gefäß','chedy':'erhitze','qokeedy':'überführe','qokedy':'ist vorbereitet','qoky':'Verfahren V / Ansatz'}
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(n,rs):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rs)
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='Previously read P12/P15/P07 and current discovery; no confirmation partition'))
dump('MODEL.json',dict(lexicon=lex,definition='f83r.6:5–9',parameters=['material','vessel'],steps=['heat material','transfer material to vessel'],definition_marker='f83r.6:9',scope='record',identity='same material form denotes same object within record',state='heat resets transferred state; transfer after heat yields prepared'))
results={};allstates={}
for mode in ['M','N']:
 events=[];calls=[];alignment=[];md=['# '+mode+' — vollständige kurze Lesung','','Alle Glossen und Bezüge sind Hypothesen. ⟦…⟧ bleibt offen.',''];expanded=['# M — vollständig expandierte Lesung','','Nur feste zwei Schritte pro Aufruf; ungebundene Parameter bleiben Fragezeichen.','']
 for rid,ts in records.items():
  mat=ves=None;state={};md+=['## '+rid,''];expanded+=['## '+rid,'']
  for i,t in enumerate(ts):
   w=t['word'];at=t['at'];reading=lex.get(w,'⟦'+w+'⟧');exp=reading
   if w in ['qokaiin','shedy']:mat=t
   if w=='lchedy':ves=t
   if w in ['chedy','qokeedy','qokedy','qoky']:
    before=state.get(mat['word'],{}) if mat else {};before=dict(before);target=None;missing=[];producer='';kind=w
    if w=='qokeedy':
     for u in ts[i+1:]:
      if u['word'] in ['chedy','qokeedy','qokedy','qoky','qokaiin','shedy']:break
      if u['word']=='lchedy':target=u;break
    if w=='qoky':target=ves
    if mat is None:missing.append('material')
    if w in ['qokeedy','qoky'] and target is None:missing.append('vessel')
    mname=lex[mat['word']] if mat else '?';vname=('Gefäß@'+target['at']) if target else '?'
    if w=='chedy':
     reading='erhitze '+mname
     if not missing:state[mat['word']]=dict(heat=at,prepared='',vessel='')
    elif w=='qokeedy':
     reading='überführe '+mname+' in '+vname
     if not missing:state[mat['word']]=dict(heat=before.get('heat',''),prepared=at if before.get('heat') else '',vessel=target['at'])
    elif w=='qokedy':
     producer=before.get('prepared','');reading=mname+' ist vorbereitet'
    else:
     if mode=='M' and at=='f83r.6:9':kind='definition';reading='Diese beiden Schritte heißen V';exp=reading
     elif mode=='M':
      kind='call';reading='V('+mname+', '+vname+')';exp='erhitze '+mname+'; überführe '+mname+' in '+vname
      if not missing:state[mat['word']]=dict(heat=at+'#1',prepared=at+'#2',vessel=target['at'])
     else:kind='noun';reading='Ansatz aus '+mname+' in '+vname;exp=reading
    after=state.get(mat['word'],{}) if mat else {}
    e=dict(record=rid,at=at,word=w,kind=kind,material=mat['at'] if mat else '',material_word=mat['word'] if mat else '',vessel=target['at'] if target else '',missing=','.join(missing),before=json.dumps(before,sort_keys=True),after=json.dumps(after,sort_keys=True),producer=producer,reprocess=str(kind=='call' and bool(before.get('prepared'))).lower())
    events.append(e)
    if w=='qoky':calls.append(dict(e,expansion=exp))
    reading+=' [Materialbezug='+e['material']+'; Gefäßbezug='+e['vessel']+'; offen='+e['missing']+'; Ergebnisbeleg='+producer+']'
    if w!='qoky':exp=reading
    else:exp+=' [offen='+e['missing']+']'
   alignment.append(dict(record=rid,at=at,word=w,reading=reading,expanded=exp));md.append(at+' '+reading);expanded.append(at+' '+exp)
  md.append('');expanded.append('')
 table('EVENTS_'+mode+'.tsv',events);table('CALLS_'+mode+'.tsv',calls);table('ALIGNMENT_'+mode+'.tsv',alignment)
 (D/('READING_'+mode+'.md')).write_text('\n'.join(md).rstrip()+'\n')
 if mode=='M':(D/'EXPANDED_M.md').write_text('\n'.join(expanded).rstrip()+'\n')
 states=[e for e in events if e['word']=='qokedy'];allstates[mode]={e['at']:e for e in states}
 results[mode]=dict(qoky_occurrences=len(calls),calls=sum(e['kind']=='call' for e in calls),complete_calls=sum(e['kind']=='call' and not e['missing'] for e in calls),reprocess_calls=sum(e['reprocess']=='true' for e in calls),explicit_actions=sum(e['word'] in ['chedy','qokeedy'] for e in events),complete_explicit_actions=sum(e['word'] in ['chedy','qokeedy'] and not e['missing'] for e in events),states=len(states),traced_states=sum(bool(e['producer']) for e in states),materialless_states=sum(not e['material'] for e in states))
comparison=[dict(at=p,material=allstates['M'][p]['material'],M_producer=allstates['M'][p]['producer'],N_producer=allstates['N'][p]['producer'],M_only=str(bool(allstates['M'][p]['producer']) and not allstates['N'][p]['producer']).lower()) for p in allstates['M']]
table('ALL_STATE_COMPARISONS.tsv',comparison)
coverage=[dict(record=rid,groups=len(ts),hypothesis=sum(t['word'] in lex for t in ts)) for rid,ts in records.items()];table('COVERAGE.tsv',coverage)
dump('RESULT.json',dict(groups=sum(map(len,records.values())),hypothesis_positions=sum(r['hypothesis'] for r in coverage),open_positions=sum(r['groups']-r['hypothesis'] for r in coverage),summary=results,M_only_states=[r['at'] for r in comparison if r['M_only']=='true'],confirmed_meanings=0))
print((D/'RESULT.json').read_text())
