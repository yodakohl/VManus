import json,csv,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P20');S=D.parent/'P11/INPUT.json'
tech=dict(chor='Blüte',cthy='Kraut',shor='Frucht',ctho='Stängel',chocthy='Mark',cthaiin='Knospe',keol='Öl',okaiin='Ansatz',chy='Wasser',qotaiin='Portion')
units={'d':'d','aiin':'e','ain':'a','ar':'ad','ol':'in','s':'et'};target={'de':'von/aus','da':'gib','ad':'zu','in':'in','et':'und'};whole={'daiin':'de','dain':'da','ar':'ad','ol':'in','s':'et'}
records={}
for r in json.loads(S.read_text())['lines']:
 rid=r['locus'].split('.')[0];records.setdefault(rid,[]).extend(dict(record=rid,at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['groups'],1))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='Previously exposed HERB4; Latin target strings freely assigned'))
dump('MODEL.json',dict(technical_wholes=tech,units=units,target_words=target,whole_rival=whole,priority='exact technical whitelist first; otherwise longest package with total coverage; no new whole exceptions'))
classes=[];used=[];edges=[]
for rid,ts in records.items():
 for t in ts:
  w=t['word'];parts=[];out='';kind='OPEN';reading='⟦'+w+'⟧'
  if w in tech:kind='TECH';reading=tech[w]
  else:
   j=0
   while j<len(w):
    options=[u for u in units if w.startswith(u,j)]
    if not options:break
    u=max(options,key=len);parts.append(u);j+=len(u)
   if j==len(w):
    out=''.join(units[u] for u in parts);kind='GRAMMAR' if out in target else 'TRANSLITERATED_UNREAD';reading=target.get(out,'⟦Zielstring '+out+' ungelesen⟧')
    used.extend(dict(at=t['at'],word=w,part_index=i,unit=u,target=units[u]) for i,u in enumerate(parts,1))
   else:parts=[]
  classes.append(dict(record=rid,at=t['at'],word=w,M_class=kind,parts='+'.join(parts),target=out,M_reading=reading,W_reading=tech.get(w,target.get(whole.get(w,''),'⟦'+w+'⟧'))))
 for i,t in enumerate(ts):
  if t['word'] not in whole:continue
  ends={};gaps={}
  for side,direction in [('left',-1),('right',1)]:
   if side=='left' and whole[t['word']]=='da':ends[side]=None;gaps[side]='';continue
   j=i+direction;found=None;gap=[]
   while 0<=j<len(ts):
    if ts[j]['word'] in whole:break
    if ts[j]['word'] in tech:found=ts[j];break
    gap.append(ts[j]['at']+'='+ts[j]['word']);j+=direction
   ends[side]=found;gaps[side]=' '.join(gap if direction==1 else reversed(gap))
  missing=[s for s in ['left','right'] if ends[s] is None and not(s=='left' and whole[t['word']]=='da')]
  edges.append(dict(record=rid,at=t['at'],word=t['word'],meaning=target[whole[t['word']]],left=ends['left']['at'] if ends['left'] else '',left_word=ends['left']['word'] if ends['left'] else '',right=ends['right']['at'] if ends['right'] else '',right_word=ends['right']['word'] if ends['right'] else '',left_gap=gaps['left'],right_gap=gaps['right'],missing=','.join(missing)))
tab('ALL_CLASSES.tsv',classes);tab('ALL_PACKAGE_OCCURRENCES.tsv',used);tab('ALL_GRAMMAR_BINDINGS.tsv',edges)
for mode in ['M','W']:
 alignment=[]
 for rid in records:
  md=['# '+rid+' / '+mode,'','Alle Bedeutungen und Zielschreibungen hypothetisch. Offene Gruppen bleiben sichtbar.','']
  for c in classes:
   if c['record']!=rid:continue
   reading=c[mode+'_reading'];e=next((e for e in edges if e['at']==c['at']),None)
   if e:reading=tech.get(e['left_word'],'?' if e['word']!='dain' else '')+' '+e['meaning']+' '+tech.get(e['right_word'],'?')+' [links='+e['left']+'; rechts='+e['right']+'; fehlend='+e['missing']+']'
   if mode=='M' and c['parts']:reading+=' [Pakete='+c['parts']+' → '+c['target']+']'
   alignment.append(dict(record=rid,at=c['at'],word=c['word'],reading=reading));md.append(c['at']+' '+reading)
  (D/(rid+'_'+mode+'.md')).write_text('\n'.join(md)+'\n')
 tab('ALIGNMENT_'+mode+'.tsv',alignment)
coverage=[dict(record=rid,groups=len(ts),semantic_positions=sum(c['record']==rid and c['M_class'] in ['TECH','GRAMMAR'] for c in classes),grammar_bound=sum(e['record']==rid and not e['missing'] for e in edges)) for rid,ts in records.items()];tab('COVERAGE.tsv',coverage)
tab('PACKAGE_TABLE.tsv',[dict(unit=u,target=v,occurrences=sum(p['unit']==u for p in used),source_wholes=','.join(sorted({p['word'] for p in used if p['unit']==u}))) for u,v in units.items()])
dump('RESULT.json',dict(groups=145,classes={k:sum(c['M_class']==k for c in classes) for k in ['TECH','GRAMMAR','TRANSLITERATED_UNREAD','OPEN']},semantic_positions=sum(c['M_class'] in ['TECH','GRAMMAR'] for c in classes),grammar_positions=len(edges),bound_grammar=sum(not e['missing'] for e in edges),unread_strings=[dict(at=c['at'],source=c['word'],target=c['target']) for c in classes if c['M_class']=='TRANSLITERATED_UNREAD'],new_interpreted_wholes=[c['word'] for c in classes if c['M_class']=='GRAMMAR' and c['word'] not in whole],confirmed_meanings=0,identified_phonetic_values=0))
print((D/'RESULT.json').read_text())
