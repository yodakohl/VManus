import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P07')
S=D.parent/'P12/PROSE.tsv'
rows=list(csv.DictReader(S.open(),delimiter='\t'))
records={}
for r in rows:
 records.setdefault(r['record_id'],[]).extend(dict(record=r['record_id'],panel=r['panel_id'],locus=r['locus'],pos=i,word=w) for i,w in enumerate(r['zl3b_line'].split(),1))
sites={'qokaiin':('Hand','Einlass'),'lchedy':('Rumpf','Mittelbecken'),'shedy':('Unterkörper','Auslass')}
ops={'qokeey':'Wasser','chedy':'spüle','qokeedy':'leite Wasser weiter','qokedy':'ist benetzt'}
def dump(name,obj): (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def tsv(name,data):
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(data[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in data)
def ref(t):return t['locus']+':'+str(t['pos'])
dump('MODEL.json',dict(sites=sites,operators=ops,scope=['RECORD','PANEL'],unknown='visible unresolved groups; intervening content may invalidate bindings'))
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),groups=sum(map(len,records.values())),records=list(records),exposure='Previously exposed in P12/P15; images viewed natively again; no held data',sealed=['f84','f84r'],decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()))
summary={};coverage=[]
for rid,ts in records.items(): coverage.append(dict(record=rid,groups=len(ts),hypothesis=sum(t['word'] in sites or t['word'] in ops for t in ts)))
tsv('COVERAGE.tsv',coverage)
for scope in ['RECORD','PANEL']:
 events=[];bindings={};site=water=None;wet={};lastpanel=None
 for rid,ts in records.items():
  if scope=='RECORD' or ts[0]['panel']!=lastpanel:site=water=None;wet={}
  lastpanel=ts[0]['panel']
  for j,t in enumerate(ts):
   w=t['word'];p=ref(t)
   if w in sites:site=t
   elif w=='qokeey':water=t
   elif w in ['chedy','qokeedy','qokedy']:
    target=None
    if w=='qokeedy':
     for u in ts[j+1:]:
      if u['word'] in ['chedy','qokeedy','qokedy']:break
      if u['word'] in sites:target=u;break
    missing=[]
    if site is None:missing.append('site')
    if w!='qokedy' and water is None:missing.append('water')
    if w=='qokeedy' and target is None:missing.append('target')
    prior=wet.get(site['word'],'') if site else ''
    e=dict(record=rid,at=p,word=w,site=ref(site) if site else '',site_word=site['word'] if site else '',water=ref(water) if water and w!='qokedy' else '',target=ref(target) if target else '',target_word=target['word'] if target else '',missing=','.join(missing),wet_producer=prior if w=='qokedy' else '',cross_record=','.join(k for k,v in [('site',site),('water',water if w!='qokedy' else None)] if v and v['record']!=rid))
    events.append(e);bindings[p]=e
    if not missing and w!='qokedy':wet[(target if w=='qokeedy' else site)['word']]=p
 tsv('EVENTS_'+scope+'.tsv',events)
 summary[scope]=dict(events=len(events),actions=sum(e['word']!='qokedy' for e in events),complete_actions=sum(e['word']!='qokedy' and not e['missing'] for e in events),missing_roles={k:sum(k in e['missing'].split(',') for e in events) for k in ['site','water','target']},states=sum(e['word']=='qokedy' for e in events),traced_states=sum(e['word']=='qokedy' and bool(e['wet_producer']) for e in events),cross_record_events=sum(bool(e['cross_record']) for e in events))
 for wi,world in enumerate(['BODY','STATION']):
  align=[];md=['# '+world+' / '+scope,'','Alle Werte hypothetisch; ⟦…⟧ bleibt offen. Bindungen gelten nur unter den Annahmen in DECISION.md.','']
  for rid,ts in records.items():
   md.extend(['## '+rid,''])
   for t in ts:
    w=t['word'];p=ref(t);reading=sites[w][wi] if w in sites else ops.get(w,'⟦'+w+'⟧')
    e=bindings.get(p)
    if e:reading+=' [Ort='+ (sites[e['site_word']][wi] if e['site_word'] else '?')+'; Bezug='+e['site']+'; Wasser='+e['water']+'; Ziel='+(sites[e['target_word']][wi] if e['target_word'] else '—')+'; Lücken='+e['missing']+'; Benetzungsbeleg='+e['wet_producer']+']'
    align.append(dict(record=rid,at=p,word=w,reading=reading));md.append(p+' '+reading)
   md.append('')
  tsv('ALIGNMENT_'+world+'_'+scope+'.tsv',align)
  (D/('READING_'+world+'_'+scope+'.md')).write_text('\n'.join(md).rstrip()+'\n')
dump('RESULT.json',dict(groups=341,hypothesis_positions=sum(x['hypothesis'] for x in coverage),open_positions=341-sum(x['hypothesis'] for x in coverage),summary=summary,semantic_discriminator=False,confirmed_meanings=0))
print(json.dumps(summary,indent=2))
