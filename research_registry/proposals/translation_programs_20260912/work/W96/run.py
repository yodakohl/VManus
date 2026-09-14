import json,csv,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent
for f,h in json.loads((D/'SOURCE.json').read_text())['hashes'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
ps=[p for p in json.loads((B/'W89/PARAGRAPHS.json').read_text()) if p['page']=='f2v'];assert len(ps)==2
qualities={'qoty':('temperature','COLD','kalt'),'shol':('moisture','WET','feucht'),'chol':('moisture','DRY','trocken')};values={'dair':'A','daiin':'C'}
rows=[];events=[];summary=[];md=['# W96 — vollständige f2v-Gegenlesungen','', 'Alle deutschen Werte sind Hypothesen. ⟦…⟧ bleibt ungelesen. Keine Fassung ist eine vollständige Übersetzung.','']
for p in ps:
 ts=[dict(word=w,at=at,line=l['locus']) for l in p['lines'] for w,at in zip(l['words'],l['source_ids'])]
 for identity in ['SAME','NEW']:
  mentions={};n=0
  for t in ts:
   if t['word']=='chor':n+=1;mentions[t['at']]='X1' if identity=='SAME' else 'X'+str(n)
  for mode in ['MASS','GRADE']:
   state={};last='';qhistory=[];amounts={};conflicts=[];missing=[];local=[]
   for i,t in enumerate(ts):
    w=t['word'];gloss='⟦'+w+'⟧';target='';status='UNREAD'
    if w=='chor':
     last=mentions[t['at']];gloss='Gegenstand '+last+' der Klasse chor';target=last;status='MENTION_ASSUMED'
    elif w in qualities:
     target=mentions[ts[i+1]['at']] if i+1<len(ts) and ts[i+1]['line']==t['line'] and ts[i+1]['word']=='chor' else last
     axis,val,meaning=qualities[w];key=(target,axis)
     conflict=bool(target and key in state and state[key]!=val)
     status='CONFLICT' if conflict else 'PROPERTY_ASSUMED' if target else 'MISSING_TARGET'
     if conflict:conflicts.append(t['at'])
     if target and not conflict:state[key]=val
     qhistory.append(dict(at=t['at'],line=t['line'],target=target,axis=axis,property=meaning))
     gloss=(target or '?')+' ist '+meaning+' ['+status+']'
    elif w in values:
     target=last;v=values[w]
     if mode=='MASS':
      amounts.setdefault(target,[]).append(v);status='AMOUNT_ASSUMED' if target else 'MISSING_TARGET';gloss='Menge('+ (target or '?') +')='+v+'·U'
     else:
      q=next((q for q in reversed(qhistory) if q['target']==target and q['line']==t['line']),None)
      status='GRADE_ASSUMED' if target and q else 'MISSING_AXIS'
      if status=='MISSING_AXIS':missing.append(t['at'])
      gloss=(target or '?')+': '+(q['property'] if q else '?Eigenschaft')+' im Grad '+v+' ['+status+']'
    a=dict(edition=p['edition'],identity=identity,mode=mode,at=t['at'],word=w,target=target,status=status,reading=gloss)
    rows.append(a);local.append(a)
    if status!='UNREAD':events.append(a)
   equal=any('A' in vs and 'C' in vs for vs in amounts.values())
   summary.append(dict(edition=p['edition'],identity=identity,mode=mode,groups=len(ts),hypothesis_positions=sum(a['status']!='UNREAD' for a in local),open_positions=sum(a['status']=='UNREAD' for a in local),conflicts=conflicts,missing_axes=missing,forces_A_equals_C=equal,final_states=[dict(target=k[0],axis=k[1],value=v) for k,v in state.items()]))
   md+=['## '+p['edition']+' / '+identity+' / '+mode,'']
   by={a['at']:a for a in local}
   for l in p['lines']:
    md += [l['locus']+' `'+ ' '.join(l['words'])+'`','', ' · '.join(by[at]['reading'] for at in l['source_ids']),'']
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
for name,rr in [('ALIGNMENT.tsv',rows),('EVENTS.tsv',events)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rr)
(D/'RESULT.json').write_text(json.dumps(dict(drafts=summary,decision='NO_SCOPE_OR_IDENTITY_WINNER',confirmed_meanings=0,reserved_access=False),ensure_ascii=False,indent=2)+'\n')
# Technical completeness checks; no separate semantic observer.
for p in ps:
 expected=[(at,w) for l in p['lines'] for at,w in zip(l['source_ids'],l['words'])]
 for ident in ['SAME','NEW']:
  for mode in ['MASS','GRADE']:assert [(r['at'],r['word']) for r in rows if (r['edition'],r['identity'],r['mode'])==(p['edition'],ident,mode)]==expected
assert all(len(s['conflicts'])==(s['identity']=='SAME') for s in summary)
assert all(len(s['missing_axes'])==(s['mode']=='GRADE') for s in summary)
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',scope='all eight source-aligned drafts and reported consequences',independent_validator=False,meaning_confirmation=False),indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
