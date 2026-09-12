import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P08');H=D.parent/'P11/INPUT.json';B=D.parent/'P12/PROSE.tsv'
nouns={'H':dict(tcho='Pflanze',cthy='Blatt',chor='Blüte',shor='Frucht',ctho='Stängel',chocthy='Mark',cthaiin='Knospe',otchol='Wurzel',qotchol='Wurzelgewebe',shan='Samen',keol='Fruchtfleisch',cthol='Rinde',okaiin='Hohlraum'),'B':dict(qokaiin='Hohlorgan',lchedy='Gewebe',shedy='Blut',qokeey='Flüssigkeit')}
relations={'A':{'H':{'daiin':'speist','shey':'enthält'},'B':{'daiin':'speist','shey':'enthält'}},'D':{'H':{'daiin':'ist Teil von','shey':'bedeckt'},'B':{'daiin':'speist','shey':'enthält'}}}
records={}
for r in json.loads(H.read_text())['lines']:
 rid=r['locus'].split('.')[0];records.setdefault(rid,[]).extend(dict(record=rid,domain='H',at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['groups'],1))
for r in csv.DictReader(B.open(),delimiter='\t'):
 rid=r['record_id'];records.setdefault(rid,[]).extend(dict(record=rid,domain='B',at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['zl3b_line'].split(),1))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
dump('SOURCE.json',dict(sources=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [H,B]],decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='All source paragraphs exposed; no independent semantic validation'))
dump('MODEL.json',dict(nouns=nouns,relations=relations,identity='same whole within record; record-local objects',binding='nearest noun in each direction before next relation or record boundary'))
edges=[];coverage=[]
for rid,ts in records.items():
 domain=ts[0]['domain'];ns=nouns[domain];coverage.append(dict(record=rid,domain=domain,groups=len(ts),hypothesis=sum(t['word'] in ns or t['word'] in ['daiin','shey'] for t in ts)))
 for i,t in enumerate(ts):
  if t['word'] not in ['daiin','shey']:continue
  ends={};gaps={}
  for side,direction in [('left',-1),('right',1)]:
   j=i+direction;found=None;gap=[]
   while 0<=j<len(ts):
    if ts[j]['word'] in ['daiin','shey']:break
    if ts[j]['word'] in ns:found=ts[j];break
    gap.append(ts[j]['at']+'='+ts[j]['word']);j+=direction
   ends[side]=found;gaps[side]=' '.join(gap if direction==1 else reversed(gap))
  left,right=ends['left'],ends['right']
  edges.append(dict(record=rid,domain=domain,at=t['at'],word=t['word'],left=left['at'] if left else '',left_word=left['word'] if left else '',right=right['at'] if right else '',right_word=right['word'] if right else '',left_gap=gaps['left'],right_gap=gaps['right'],missing=','.join(s for s in ['left','right'] if not ends[s]),self_edge=bool(left and right and left['word']==right['word'])))
tab('ALL_RELATIONS.tsv',edges);tab('COVERAGE.tsv',coverage)
chains=[]
for a in edges:
 for b in edges:
  if a is b or a['record']!=b['record'] or a['missing'] or b['missing']:continue
  if a['right']==b['left']:chains.append(dict(record=a['record'],domain=a['domain'],first=a['at'],second=b['at'],shared=a['right'],first_word=a['word'],second_word=b['word']))
# Empty tables retain a header if there is no chain.
with (D/'CHAINS.tsv').open('w') as f:
 wr=csv.DictWriter(f,fieldnames=['record','domain','first','second','shared','first_word','second_word','row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in chains)
issues=[]
for mode in ['A','D']:
 alignment=[]
 for domain in ['H','B']:
  md=['# '+mode+' / '+domain,'','Alle Beziehungen und Dingnamen hypothetisch. ⟦…⟧ bleibt offen.','']
  for rid,ts in records.items():
   if ts[0]['domain']!=domain:continue
   md+=['## '+rid,'']
   for t in ts:
    w=t['word'];reading=nouns[domain].get(w,'⟦'+w+'⟧')
    if w in ['daiin','shey']:
     e=next(e for e in edges if e['at']==t['at']);rel=relations[mode][domain][w]
     reading=nouns[domain].get(e['left_word'],'?')+' '+rel+' '+nouns[domain].get(e['right_word'],'?')+' [links='+e['left']+'; rechts='+e['right']+'; fehlend='+e['missing']+']'
     if e['self_edge']:issues.append(dict(mode=mode,record=rid,at=e['at'],relation=rel,status='STRICT_SELF_CONTRADICTION' if rel in ['enthält','ist Teil von'] else 'SELF_EXPLANATION_DEBT'))
    alignment.append(dict(record=rid,domain=domain,at=t['at'],word=w,reading=reading));md.append(t['at']+' '+reading)
   md.append('')
  (D/('CHAPTER_'+mode+'_'+domain+'.md')).write_text('\n'.join(md).rstrip()+'\n')
 tab('ALIGNMENT_'+mode+'.tsv',alignment)
 # Detect every strict directed cycle by closure on complete edges.
 for rid in records:
  es=[e for e in edges if e['record']==rid and not e['missing'] and relations[mode][e['domain']][e['word']] in ['enthält','ist Teil von']]
  # Contains is inverted to part-to-whole orientation before combining.
  graph=set((e['right_word'],e['left_word']) if relations[mode][e['domain']][e['word']]=='enthält' else (e['left_word'],e['right_word']) for e in es)
  changed=True
  while changed:
   new=graph|{(a,d) for a,b in graph for c,d in graph if b==c};changed=new!=graph;graph=new
  for node in sorted({a for a,b in graph if a==b}):issues.append(dict(mode=mode,record=rid,at=node,relation='strict containment closure',status='STRICT_CYCLE'))
tab('ISSUES.tsv',issues)
summary={domain:dict(relations=sum(e['domain']==domain for e in edges),complete=sum(e['domain']==domain and not e['missing'] for e in edges),chains=sum(c['domain']==domain for c in chains),self_edges=sum(e['domain']==domain and e['self_edge'] for e in edges)) for domain in ['H','B']}
dump('RESULT.json',dict(groups=486,hypothesis_positions=sum(c['hypothesis'] for c in coverage),open_positions=486-sum(c['hypothesis'] for c in coverage),summary=summary,relations_cards_A=2,relations_cards_D=4,issues=issues,confirmed_meanings=0))
print((D/'RESULT.json').read_text())
