import csv,json,hashlib
from fractions import Fraction
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P14');S=D.parent/'P11/INPUT.json';L=D.parent/'P11/COMMON_LEXICON.tsv'
materials={r['word']:r['value'] for r in csv.DictReader(L.open(),delimiter='\t') if r['type']=='MATERIAL'}
qualities={'chol':'trocken','shol':'feucht','shy':'feucht'};values={'dair':'A','dain':'B','daiin':'C'};verbs={'sho':'füge hinzu','qotchy':'zerkleinere'}
records={}
for r in json.loads(S.read_text())['lines']:
 rid=r['locus'].split('.')[0];records.setdefault(rid,[]).extend(dict(record=rid,line=r['locus'],at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['groups'],1))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),lexicon=str(L),lexicon_sha256=hashlib.sha256(L.read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='All HERB4 and prior glosses exposed; all meaning assumptions provisional'))
dump('MODEL.json',dict(materials=materials,qualities=qualities,values=values,verbs=verbs,scopes=['RECORD','LINE'],dimensions=dict(G='ordinal quality grade',M='mass in unknown record unit U',R='mass/mass ratio with positional denominator')))
summary={}
for scope in ['RECORD','LINE']:
 fields=[];actions=[]
 for rid,ts in records.items():
  current=previous=quality=None;lastline=None
  for i,t in enumerate(ts):
   w=t['word']
   if scope=='LINE' and t['line']!=lastline:current=previous=quality=None
   lastline=t['line']
   if w in materials:
    if current and current['word']!=w:previous=current
    current=t;quality=None
   if w in qualities:quality=t
   if w in values:
    missing_material=not current
    fields.append(dict(record=rid,at=t['at'],word=w,value=values[w],material=current['at'] if current else '',material_word=current['word'] if current else '',quality=quality['at'] if quality else '',quality_word=quality['word'] if quality else '',denominator=previous['at'] if previous else '',denominator_word=previous['word'] if previous else '',G_missing=','.join(k for k,b in [('material',missing_material),('quality',not quality)] if b),M_missing='material' if missing_material else '',R_missing=','.join(k for k,b in [('material',missing_material),('denominator',not previous)] if b)))
   if w in verbs:
    target=None
    for u in ts[i+1:]:
     if scope=='LINE' and u['line']!=t['line']:break
     if u['word'] in verbs or u['word'] in values:break
     if u['word'] in materials:target=u;break
    actions.append(dict(record=rid,at=t['at'],word=w,target=target['at'] if target else '',target_word=target['word'] if target else ''))
 tab('FIELDS_'+scope+'.tsv',fields);tab('ACTIONS_'+scope+'.tsv',actions)
 for mode in ['G','M','R']:
  alignment=[]
  for rid,ts in records.items():
   md=['# '+rid+' / '+mode+' / '+scope,'','Alle Werte und Bedeutungen hypothetisch; ⟦…⟧ offen.','']
   for t in ts:
    w=t['word'];reading=materials.get(w,qualities.get(w,'⟦'+w+'⟧'))
    if w in verbs:
     a=next(a for a in actions if a['at']==t['at']);reading=verbs[w]+' '+materials.get(a['target_word'],'?')+' [Bezug='+a['target']+']'
    if w in values:
     f=next(f for f in fields if f['at']==t['at']);name=materials.get(f['material_word'],'?');v=f['value']
     if mode=='G':reading=name+': '+qualities.get(f['quality_word'],'?')+' im Grad '+v+' [Skala unbekannt]'
     if mode=='M':reading=name+': Menge '+v+'·U [U unbenannte Masseneinheit]'
     if mode=='R':reading='Masse('+name+') / Masse('+materials.get(f['denominator_word'],'?')+') = '+v
     reading+=' [Träger='+f['material']+'; Achse='+f['quality']+'; Nenner='+f['denominator']+'; fehlend='+f[mode+'_missing']+']'
    alignment.append(dict(record=rid,at=t['at'],word=w,reading=reading));md.append(t['at']+' '+reading)
   (D/(rid+'_'+mode+'_'+scope+'.md')).write_text('\n'.join(md)+'\n')
  tab('ALIGNMENT_'+mode+'_'+scope+'.tsv',alignment)
 # Eliminate only material columns, preserving symbolic log-value columns.
 edges=[f for f in fields if not f['R_missing']];nodes=sorted({f['record']+':'+f[k] for f in edges for k in ['material_word','denominator_word']});matrix=[]
 for f in edges:
  row=[Fraction(0) for _ in range(len(nodes)+3)];row[nodes.index(f['record']+':'+f['material_word'])]+=1;row[nodes.index(f['record']+':'+f['denominator_word'])]-=1;row[len(nodes)+'ABC'.index(f['value'])]-=1;matrix.append(row)
 pivot=0
 for col in range(len(nodes)):
  k=next((k for k in range(pivot,len(matrix)) if matrix[k][col]),None)
  if k is None:continue
  matrix[pivot],matrix[k]=matrix[k],matrix[pivot];scale=matrix[pivot][col];matrix[pivot]=[v/scale for v in matrix[pivot]]
  for j in range(len(matrix)):
   if j!=pivot:
    factor=matrix[j][col];matrix[j]=[a-factor*b for a,b in zip(matrix[j],matrix[pivot])]
  pivot+=1
 constraints=[[str(v) for v in row[len(nodes):]] for row in matrix if not any(row[:len(nodes)]) and any(row[len(nodes):])]
 dump('RATIO_ELIMINATION_'+scope+'.json',dict(nodes=nodes,edges=[dict(at=f['at'],numerator=f['record']+':'+f['material_word'],denominator=f['record']+':'+f['denominator_word'],value=f['value']) for f in edges],material_rank=pivot,value_constraints=constraints,meaning='Coefficients of log(A),log(B),log(C); equality to zero; free values if empty'))
 summary[scope]=dict(values=len(fields),bound={m:sum(not f[m+'_missing'] for f in fields) for m in ['G','M','R']},actions=len(actions),bound_actions=sum(bool(a['target']) for a in actions),ratio_edges=len(edges),ratio_constraints=len(constraints))
known=set(materials)|set(qualities)|set(values)|set(verbs)
coverage=[dict(record=rid,groups=len(ts),hypothesis=sum(t['word'] in known for t in ts)) for rid,ts in records.items()];tab('COVERAGE.tsv',coverage)
dump('RESULT.json',dict(groups=145,hypothesis_positions=sum(r['hypothesis'] for r in coverage),open_positions=145-sum(r['hypothesis'] for r in coverage),summary=summary,confirmed_meanings=0,identified_numbers=0))
print((D/'RESULT.json').read_text())
contrasts=[];chains=[]
for scope in ['RECORD','LINE']:
 fs=list(csv.DictReader((D/('FIELDS_'+scope+'.tsv')).open(),delimiter='\t'))
 edges=[f for f in fs if not f['R_missing']]
 for e in edges:
  numerator_values={f['value'] for f in fs if f['record']==e['record'] and f['material_word']==e['material_word'] and not f['M_missing']}
  denominator_values={f['value'] for f in fs if f['record']==e['record'] and f['material_word']==e['denominator_word'] and not f['M_missing']}
  for v in sorted(numerator_values & denominator_values):contrasts.append(dict(scope=scope,at=e['at'],numerator=e['material_word'],denominator=e['denominator_word'],shared_M_value=v,M_implied_ratio='1',R_stated_ratio=e['value']))
  for e2 in edges:
   if e['record']==e2['record'] and e['denominator_word']==e2['material_word']:
    chains.append(dict(scope=scope,first=e2['at'],second=e['at'],numerator=e['material_word'],middle=e['denominator_word'],denominator=e2['denominator_word'],implied_ratio=e['value']+'*'+e2['value'],status='derived under R, not a written closing equation'))
tab('M_R_CONTRASTS.tsv',contrasts);tab('RATIO_CHAINS.tsv',chains)
