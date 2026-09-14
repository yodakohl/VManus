import csv,json,hashlib,re
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent
j=lambda n:json.loads((D/n).read_text())
source=j('SOURCE.json');res=j('RESULT.json');entries=j('DEFINITIONS.json');apps=j('APPLICATIONS.json')
for n,h in source['local_hashes'].items():assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h
assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['source_sha256']
rows=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'));assert {r['page'] for r in rows}=={'f83r'}
ts=[];expected=[];markers={};quotes={};bodies={}
for r in rows:
 words=r['zl3b_line'].split();offset=len(ts);lineats=[r['locus']+':'+str(k+1) for k in range(len(words))]
 ts.extend((r['record_id'],a,w) for a,w in zip(lineats,words))
 # Split the raw line into clauses at whole-word markers independently of builder.
 parts=re.split(r'(?<!\S)qokedy(?!\S)',r['zl3b_line'])
 start=0
 for n in range(len(parts)-1):
  marker_pos=next(i for i in range(start,len(words)) if words[i]=='qokedy')
  body=words[start:marker_pos];target=words[marker_pos+1]
  assert body and target!='qokedy'
  eid='D%02d'%(len(expected)+1)
  e={'id':eid,'record':r['record_id'],'marker':lineats[marker_pos],'marker_index':offset+marker_pos,'name':target,'name_at':lineats[marker_pos+1],'name_index':offset+marker_pos+1,'body':body,'body_loci':lineats[start:marker_pos],'status':'BOUND'}
  expected.append(e);quotes[e['name_at']]=eid;markers[e['marker']]=eid
  for at in e['body_loci']:bodies[at]=eid
  start=marker_pos+2
assert entries==expected
assert len({e['name'] for e in entries})==len(entries)==13
lex={e['name']:e for e in entries}
# Independent iterative substitution preserving the order of expansion events.
def resolve(word,cutoff):
 pending=[(word,())];leaf=[];used=[];blocked=[]
 while pending:
  w,anc=pending.pop(0)
  if w not in lex:leaf.append(w);continue
  e=lex[w]
  if cutoff is not None and e['name_index']>=cutoff:leaf.append(w);blocked.append(w);continue
  assert w not in anc,'cycle'
  used.append(e['id']);pending=[(v,anc+(w,)) for v in e['body']]+pending
 return leaf,used,blocked
appmap={a['at']:a for a in apps};total=0
for index,(rid,at,w) in enumerate(ts):
 if w not in lex or at in quotes:continue
 total+=1;a=appmap[at];s,used,blocked=resolve(w,index);f,fu,_=resolve(w,None)
 assert a['sequential_expansion']==s and a['sequential_definitions']==used and a['unintroduced_names']==blocked
 assert a['retrospective_expansion']==f and a['retrospective_definitions']==fu
 assert a['declaration_precedes']==(lex[w]['name_index']<index)
 assert a['location_role']==('DEFINITION_BODY' if at in bodies else 'OTHER_TEXT')
 assert a['future_definition_ids']==sorted(set(fu)-set(used))
for w in lex:resolve(w,None)
assert total==len(apps)==48
align=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'))
for mode in ['N','C']:
 assert [(a['record'],a['at'],a['word']) for a in align if a['mode']==mode]==ts
 for a in [a for a in align if a['mode']==mode]:
  role='MARKER' if a['at'] in markers else 'DECLARATION_TARGET' if a['at'] in quotes else 'DEFINITION_BODY' if a['at'] in bodies else 'OTHER_TEXT'
  assert a['role']==role
assert len(ts)==341 and len(rows)==51
assert res['uses_before_declaration']==sum(not a['declaration_precedes'] for a in apps)==30
assert res['uses_after_declaration']==18 and res['fully_resolved_after']==16
assert res['after_outside_definitions']==sum(a['declaration_precedes'] and a['location_role']=='OTHER_TEXT' for a in apps)==15
summary=list(csv.DictReader((D/'CANDIDATES.tsv').open(),delimiter='\t'))
c=Counter(w for _,_,w in ts)
for r in summary:
 a=[a for a in apps if a['name']==r['name']]
 assert int(r['all_occurrences'])==c[r['name']]
 assert int(r['uses'])==len(a)
 assert int(r['before_declaration'])==sum(not x['declaration_precedes'] for x in a)
 assert int(r['after_declaration'])==sum(x['declaration_precedes'] for x in a)
 assert int(r['fully_resolved_after'])==sum(x['declaration_precedes'] and not x['unintroduced_names'] for x in a)
 assert int(r['after_outside_definitions'])==sum(x['declaration_precedes'] and x['location_role']=='OTHER_TEXT' for x in a)
 assert int(r['retrospective_leaf_count'])==len(resolve(r['name'],None)[0])
assert sum(int(r['uses'])==0 for r in summary)==res['names_without_other_use']==5
# Check every dependency and whether it was introduced at the declaration.
actual=list(csv.DictReader((D/'DEPENDENCIES.tsv').open(),delimiter='\t'))
deps=[]
for e in entries:
 for at,w in zip(e['body_loci'],e['body']):
  if w in lex:deps.append({'definition':e['id'],'name':e['name'],'body_at':at,'dependency':w,'dependency_definition':lex[w]['id'],'dependency_precedes':str(lex[w]['name_index']<e['marker_index'])})
assert actual==deps and len(deps)==10
assert sum(d['dependency_precedes']=='False' for d in deps)==7
assert res['nonmarker_content_positions_untranslated']==328
matches=[]
for e in entries:
 for rid in dict.fromkeys(t[0] for t in ts):
  seq=[t for t in ts if t[0]==rid]
  for start in [i for i,t in enumerate(seq) if t[2]==e['body'][0]]:
   chunk=seq[start:start+len(e['body'])]
   if [t[2] for t in chunk]!=e['body']:continue
   outside=all(t[1] not in markers and t[1] not in quotes and t[1] not in bodies for t in chunk)
   matches.append({'definition':e['id'],'name':e['name'],'record':rid,'start':chunk[0][1],'end':chunk[-1][1],'body':' '.join(e['body']),'outside_all_definition_units':str(outside)})
assert matches==list(csv.DictReader((D/'BODY_MATCHES.tsv').open(),delimiter='\t'))
assert len(matches)==res['direct_body_matches']==14
assert not any(m['outside_all_definition_units']=='True' for m in matches)
assert res['direct_body_matches_outside_definition_units']==0
out={'status':'PASS','scope':'source hashes, 13 independently reconstructed units, all 48 sequential/retrospective applications, dependencies, cycle exclusion and all 682 aligned positions','observer_independence':False,'semantic_validation':False,'note':'N/C share substitution by construction; no external observation selects mention versus object or qokedy meaning'}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
