"""Frozen P12 participant bindings with explicit worker-custody hypotheses."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path(__file__).parent
S=json.loads((D/'SPEC.json').read_text())
for name,h in S['hashes'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h
source=list(csv.DictReader(Path(S['source']).open(),delimiter='\t'))
records={r:[] for r in S['records']}
for row in source:
 assert row['page']=='f83r' and row['record_id'] in records
 for i,w in enumerate(row['zl3b_line'].split(),1):records[row['record_id']].append(dict(record=row['record_id'],line=row['locus'],at=row['locus']+':'+str(i),word=w))
assert sum(map(len,records.values()))==341
refs={(r['model'],r['mention']):r for r in csv.DictReader(Path(S['references']).open(),delimiter='\t') if r['model'] in S['reference_models'] and r['identity']=='REUSE'}
def js(x):return json.dumps(x,sort_keys=True,ensure_ascii=False)
def tab(name,rows,columns):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=columns+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rows)
all_events=[];alignment=[];chains=[];summaries=[]
for ref in S['reference_models']:
 for model in S['models']:
  world=ref+'_'+model;events=[]
  for rid,ts in records.items():
   actor=rid+':A0';recipient='MISSING';owners={};origins={};problems=[];last_marker='';markers=[];transfers={}
   for t in ts:
    w=t['word'];before=dict(actor=actor,recipient=recipient,owners=dict(owners),origins=dict(origins));reading='⟦'+w+'⟧';event=None
    if w in ['shedy','lchedy']:
     reading={'shedy':'Flüssigkeit A','lchedy':'Zusatzstoff C'}[w]
    elif w=='qokaiin':
     recipient=rid+':B';reading='Gefäß B' if model=='V' else 'empfangender Bearbeiter B'
    elif w=='qoky':
     status='OPEN';issues=[]
     if model=='H1':
      reading='Der genannte Empfänger arbeitet weiter'
      if recipient=='MISSING':issues=['MISSING_RECIPIENT'];status='UNBOUND';actor='MISSING'
      else:status='ROLE_REPEATED' if actor==recipient else 'ACTOR_CHANGED';actor=recipient;last_marker=t['at'];markers.append((t['at'],actor))
     event=dict(kind='MARKER',patient='NA',destination=recipient,status=status,issues=','.join(issues) or 'NONE',owner_before='NA',owner_after='NA',owner_origin='NA')
    elif w in ['chedy','qokeedy']:
     r=refs[(ref,t['at'])];p=r['patient'];dst=r['destination'];issues=[]
     if p=='MISSING':issues.append('MISSING_PATIENT')
     if w=='qokeedy' and dst=='MISSING':issues.append('MISSING_DESTINATION')
     own=owners.get(p,'UNKNOWN');origin=origins.get(p,'NONE');status='UNBOUND' if issues else 'BOUND_NO_CUSTODY_TEST'
     if model!='V':
      if actor=='MISSING':issues.append('MISSING_ACTOR')
      if w=='qokeedy' and actor!='MISSING' and dst!='MISSING' and actor==dst:issues.append('SELF_TRANSFER')
      if p!='MISSING' and actor!='MISSING' and own!='UNKNOWN' and own!=actor:issues.append('ACCESS_CONFLICT')
      if issues:status='CONFLICT' if any(x in issues for x in ['SELF_TRANSFER','ACCESS_CONFLICT']) else 'UNBOUND'
      else:
       status='INITIAL_REQUIREMENT' if own=='UNKNOWN' else 'ACCESS_MATCH'
       if own=='UNKNOWN':owners[p]=actor;origins[p]=t['at']
       if w=='qokeedy':owners[p]=dst;origins[p]=t['at'];transfers[p]=dict(at=t['at'],from_actor=actor,to_actor=dst,prior_problems=list(problems))
       elif p in transfers and actor==transfers[p]['to_actor'] and last_marker:
        tr=transfers[p];positions={u['at']:i for i,u in enumerate(ts)}
        for marker,marker_actor in markers:
         if marker_actor==actor and positions[tr['at']]<positions[marker]<positions[t['at']]:
          between=ts[positions[tr['at']]+1:positions[t['at']]]
          chains.append(dict(world=world,record=rid,transfer=tr['at'],marker=marker,later_action=t['at'],patient=p,actor=actor,intervening_raw=' '.join(u['word'] for u in between),prior_problem=','.join(problems) or 'NONE'))
     reading=('Erwärme ' if w=='chedy' else ('Fülle ein: ' if model=='V' else 'Übergib an B: '))+p+' [Akteur='+actor+('; Empfänger='+dst if w=='qokeedy' else '')+']'
     event=dict(kind='HEAT' if w=='chedy' else 'TRANSFER',patient=p,destination=dst,status=status,issues=','.join(issues) or 'NONE',owner_before=own,owner_after=owners.get(p,'UNKNOWN'),owner_origin=origin)
    after=dict(actor=actor,recipient=recipient,owners=dict(owners),origins=dict(origins))
    if event:
     event=dict(world=world,record=rid,at=t['at'],word=w,actor_before=before['actor'],actor_after=actor,**event,prior_problem=','.join(problems) or 'NONE',before=js(before),after=js(after))
     if event['issues']!='NONE':problems.append(t['at'])
     events.append(event);all_events.append(event)
    alignment.append(dict(world=world,record=rid,at=t['at'],word=w,reading=reading,before=js(before),after=js(after)))
  count=Counter(e['status'] for e in events);issue=Counter(k for e in events for k in e['issues'].split(',') if k!='NONE')
  summaries.append(dict(world=world,actions=sum(e['kind']!='MARKER' for e in events),markers=sum(e['kind']=='MARKER' for e in events),status=js(dict(count)),issues=js(dict(issue)),chains=sum(c['world']==world for c in chains)))
tab('EVENTS.tsv',all_events,list(all_events[0]));tab('ALIGNMENT.tsv',alignment,list(alignment[0]));tab('CANDIDATES.tsv',summaries,list(summaries[0]))
tab('CHAINS.tsv',chains,['world','record','transfer','marker','later_action','patient','actor','intervening_raw','prior_problem'])
md=['# W41 — sechs vollständige Arbeitsfassungen','','Alle Rollen und Wortwerte sind unbestätigte Hypothesen; ⟦…⟧ ungelesen.','']
for rid,ts in records.items():
 md+=['## '+rid,'']
 for line in dict.fromkeys(t['line'] for t in ts):
  md += [line+': `'+ ' '.join(t['word'] for t in ts if t['line']==line)+'`','']
  for ref in S['reference_models']:
   for model in S['models']:
    world=ref+'_'+model
    rs=[r for r in alignment if r['world']==world and r['record']==rid and r['at'].rsplit(':',1)[0]==line]
    md += [world+': '+' · '.join(r['reading'] for r in rs),'']
(D/'READING.md').write_text('\n'.join(md)+'\n')
known={'shedy','lchedy','qokaiin','chedy','qokeedy'}
result=dict(records=len(records),lines=len(source),groups=341,baseline_assumed=sum(t['word'] in known for ts in records.values() for t in ts),marker_occurrences=sum(t['word']=='qoky' for ts in records.values() for t in ts),candidates=summaries,chain_count=len(chains),distinct_transfer_action_pairs=len({(c['world'],c['transfer'],c['later_action']) for c in chains}),independent_confirmation_capacity=0,confirmed_words=0,held_access=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
