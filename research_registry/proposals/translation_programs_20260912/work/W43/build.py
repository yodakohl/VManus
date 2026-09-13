import csv,json,hashlib
from pathlib import Path
from collections import defaultdict
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text());old=Path(S['old'])
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
read=lambda p:list(csv.DictReader(Path(p).open(),delimiter='\t'))
raw=read(S['source']);assert len(raw)==341 and all(r['locus'].startswith('f83r.') for r in raw)
records=list(dict.fromkeys(r['record'] for r in raw))
def tab(name,rs,cols):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rs)
events=[];portions=[];stocks=[];summary=[];align=[];projection={}
for mode in S['modes']:
 es=read(old/('EVENTS_'+mode+'.tsv'));assert len(es)==42
 pmap={};need=defaultdict(list);order=defaultdict(int)
 for e in es:
  n=int(e['body_executions'])+int(e['status']=='EXECUTE_FILL')
  assert n in [0,1]
  if n:
   assert e['patient']!='NONE' and e['destination']!='NONE'
   order[e['record']]+=1;pid='d['+e['at']+']';tid='t['+e['at']+']'
   need[(e['record'],e['patient'])].append(pid)
   p=dict(mode=mode,record=e['record'],at=e['at'],word=e['word'],material=e['patient'],recipient=e['record']+':B',recipient_mention=e['destination'],portion=pid,amount='POSITIVE_UNKNOWN',time=tid,previous_time='NONE' if order[e['record']]==1 else 't_previous_body',time_constraint='strictly later than previous executed body; interval unknown',illustrative_time=order[e['record']],illustrative_amount=1)
   portions.append(p);pmap[e['at']]=p
 for family in S['families']:
  world=mode+'_'+family
  for e in es:
   n=int(e['body_executions'])+int(e['status']=='EXECUTE_FILL');p=pmap.get(e['at'])
   base={k:v for k,v in e.items() if k!='row_status'}
   events.append(dict(world=world,**base,executions=n,resource_role='retained batch with device' if family=='R' else 'consumptive portion to hypothetical recipient',consumption=p['portion'] if p and family=='C' else ('NONE_REQUIRED_BY_BODY' if family=='R' else 'NO_EXECUTED_BODY'),appointment=p['time'] if p and family=='C' else 'NOT_A_TREATMENT_APPOINTMENT',recipient_identity=e['record']+':B' if e['destination']!='NONE' else 'MISSING'))
  projection[world]=[{k:v for k,v in e.items() if k!='row_status'} for e in es]
  for rec in records:
   for material in ['shedy','lchedy']:
    ds=need[(rec,material)];n=len(ds)
    stocks.append(dict(world=world,record=rec,material=material,executed_bodies=n,new_portions=n if family=='C' else 0,partial_consumption='+'.join(ds) if family=='C' and ds else '0_IN_THIS_SUBSYSTEM',ending_stock='S-('+ '+'.join(ds)+')' if family=='C' and ds else 'S',unknown_initial_stock='S',illustrative_initial=n+1,illustrative_final=1 if family=='C' else n+1,not_included='unbound or unfinished operations, prior history, unknown words'))
  rs=read(old/('ALIGNMENT_'+mode+'.tsv'))
  for r in rs:
   w=r['word'];text='⟦'+w+'⟧'
   if w=='shedy':text='Material A / Mittelvorrat A'
   if w=='lchedy':text='Material C / Mittelvorrat C'
   if w=='qokaiin':text='Gerät B' if family=='R' else 'hypothetischer Behandlungsadressat B'
   if w=='chedy':text='erwärme das Material / den Vorrat'
   if w=='qokeedy':text='bearbeite den erhaltenen Ansatz' if family=='R' else 'verabreiche eine positive Teilmenge an B'
   if w=='qokeey':text='Bearbeitung läuft' if family=='R' else 'Anwendung läuft'
   if w=='qokedy':text='Bearbeitung erfolgt' if family=='R' else 'Anwendung erfolgt'
   if w=='qoteedy':text={'N':'ein Durchgang','PRE':'Ziel zuerst prüfen; Körper nur falls nötig','POST':'ein Durchgang, dann Ziel prüfen'}[mode]+' ['+('Bearbeitung' if family=='R' else 'Anwendung')+']'
   align.append(dict(world=world,record=r['record'],at=r['at'],word=w,reading=text))
 summary.append(dict(mode=mode,executed_bodies=len(pmap),new_portions_C=len(pmap),required_consumption_R=0,bound_record_recipients=len({p['record'] for p in pmap.values()}),qoteedy_statuses={e['at']:e['status'] for e in es if e['word']=='qoteedy'},projected_observation_differences=int(projection[mode+'_C']!=projection[mode+'_R']),resource_subsystem_has_free_positive_solution=True))
tab('EVENTS.tsv',events,list(events[0]));tab('PORTIONS.tsv',portions,list(portions[0]));tab('STOCKS.tsv',stocks,list(stocks[0]));tab('ALIGNMENT.tsv',align,list(align[0]))
md=['# W43 — vollständige sechs Bedeutungsentwürfe','','Keine Therapieempfehlungen oder identifizierten Personen. Alle Wörter und Ausführungen sind hypothetisch; Zahlen der Existenzbelegung sind keine Manuskriptwerte.','']
for rec in records:
 md+=['## '+rec,'']
 for line in dict.fromkeys(r['locus'] for r in raw if r['record']==rec):
  md += [line+': `'+ ' '.join(r['word'] for r in raw if r['locus']==line)+'`','']
  for mode in S['modes']:
   for family in S['families']:
    world=mode+'_'+family;md += [world+': '+' · '.join(a['reading'] for a in align if a['world']==world and a['at'].rsplit(':',1)[0]==line),'']
(D/'READING.md').write_text('\n'.join(md)+'\n')
result=dict(groups=341,records=7,event_projections=len(events),summary=summary,claim='constructive feasibility only for added resource subsystem; existing S04 missing roles and conditions unchanged',new_confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
