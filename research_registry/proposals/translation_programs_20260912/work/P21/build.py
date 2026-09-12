import json,csv,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P21');S=D.parent/'P11/INPUT.json'
raw=json.loads(S.read_text());records={}
for r in raw['lines']:
 rid=r['locus'].split('.')[0];records.setdefault(rid,[]).extend(dict(record=rid,at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['groups'],1))
rows=[('chor','CH','Blüte','BASE','SG','Blüte'),('chol','CH','Blüte','OBJECT','SG','Samen'),('shor','SH','Frucht','BASE','SG','Frucht'),('shol','SH','Frucht','OBJECT','SG','Saft'),('keor','KE','Öl','BASE','SG','Harz'),('keol','KE','Öl','OBJECT','SG','Öl'),('cthy','CTH','Kraut','BASE','SG','Kraut'),('ctho','CTH','Kraut','OBJECT','SG','Pulver'),('cthaiin','CTH','Kraut','OBJECT','PL','Portion')]
nouns={w:dict(word=w,family=f,lemma=l,F_case=c,R_case='BASE' if c=='OBJECT' else 'OBJECT',number=n,L_lemma=k) for w,f,l,c,n,k in rows}
verbs={'daiin':('bereite',-1),'sho':('vermische',1),'qotchy':('zerkleinere',1)}
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
tab('PARADIGMS.tsv',list(nouns.values()))
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='All HERB4 paragraphs previously exposed; no independent confirmation',source_note=raw['scope']))
dump('MODEL.json',dict(nouns=nouns,verbs=verbs,role_requirement='OBJECT',binding='nearest noun in declared direction before another verb; record scope'))
bindings=[];occ=[];coverage=[]
for rid,ts in records.items():
 coverage.append(dict(record=rid,groups=len(ts),hypothesis=sum(t['word'] in nouns or t['word'] in verbs for t in ts)))
 for i,t in enumerate(ts):
  if t['word'] in nouns:occ.append(dict(record=rid,at=t['at'],**nouns[t['word']]))
  if t['word'] not in verbs:continue
  action,direction=verbs[t['word']];j=i+direction;target=None
  while 0<=j<len(ts):
   if ts[j]['word'] in verbs:break
   if ts[j]['word'] in nouns:target=ts[j];break
   j+=direction
  n=nouns[target['word']] if target else None
  bindings.append(dict(record=rid,at=t['at'],word=t['word'],action=action,direction=direction,target=target['at'] if target else '',target_word=target['word'] if target else '',family=n['family'] if n else '',F='MISSING' if not n else 'MATCH' if n['F_case']=='OBJECT' else 'FORM_CONFLICT',R='MISSING' if not n else 'MATCH' if n['R_case']=='OBJECT' else 'FORM_CONFLICT',L='BOUND' if n else 'MISSING'))
for o in occ:o['governors']=','.join(b['at'] for b in bindings if b['target']==o['at'])
tab('ALL_BINDINGS.tsv',bindings);tab('ALL_NOUN_OCCURRENCES.tsv',occ);tab('COVERAGE.tsv',coverage)
for mode in ['F','R','L']:
 alignment=[]
 for rid,ts in records.items():
  md=['# '+rid+' / '+mode,'','Alle Bedeutungen hypothetisch; ⟦…⟧ offen. BASE/OBJECT/SG/PL sind angesetzte Funktionen.','']
  for t in ts:
   w=t['word'];reading='⟦'+w+'⟧'
   if w in nouns:
    n=nouns[w];reading=n['L_lemma'] if mode=='L' else n['lemma']+' ['+n[mode+'_case']+'; '+n['number']+']'
   if w in verbs:
    b=next(x for x in bindings if x['at']==t['at']);n=nouns.get(b['target_word']);label=(n['L_lemma'] if mode=='L' else n['lemma']) if n else '?'
    if mode!='L' and n and n['number']=='PL':label='mehrere '+label+'-Einheiten'
    reading=b['action']+' '+label+' [Bezug='+b['target']+'; '+b[mode]+']'
   alignment.append(dict(record=rid,at=t['at'],word=w,reading=reading));md.append(t['at']+' '+reading)
  (D/(rid+'_'+mode+'.md')).write_text('\n'.join(md)+'\n')
 tab('ALIGNMENT_'+mode+'.tsv',alignment)
summary={m:{v:sum(b[m]==v for b in bindings) for v in set(b[m] for b in bindings)} for m in ['F','R','L']}
fam=[dict(family=f,occurrences=sum(o['family']==f for o in occ),bound_positions=len({b['target'] for b in bindings if b['family']==f}),F_matches=sum(b['family']==f and b['F']=='MATCH' for b in bindings),R_matches=sum(b['family']==f and b['R']=='MATCH' for b in bindings)) for f in ['CH','SH','KE','CTH']];tab('FAMILY_RESULTS.tsv',fam)
dump('RESULT.json',dict(groups=145,hypothesis_positions=sum(r['hypothesis'] for r in coverage),open_positions=145-sum(r['hypothesis'] for r in coverage),noun_positions=len(occ),verbs=len(bindings),summary=summary,families=fam,reused_targets={o['at']:o['governors'] for o in occ if ',' in o['governors']},ungoverned_F_objects=[o['at'] for o in occ if o['F_case']=='OBJECT' and not o['governors']],confirmed_meanings=0))
print((D/'RESULT.json').read_text())
