"""Apply the frozen P14 contracts to the registered exposed projection."""
import csv
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
D=Path(__file__).parent
spec=json.loads((D/'SPEC.json').read_text())
for name,digest in spec['source_hashes'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
model=json.loads(Path(spec['model']).read_text())
materials,qualities,values,verbs=[model[k] for k in ['materials','qualities','values','verbs']]
raw=list(csv.DictReader(Path(spec['source']).open(),delimiter='\t'))
assert len(raw)==spec['groups']
records={}
for r in raw:
    assert r['paragraph'] in spec['paragraphs'] and not r['locus'].startswith('f84')
    records.setdefault(r['paragraph'],[]).append(dict(record=r['paragraph'],line=r['locus'],at=r['id'],word=r['form']))
def tab(name,rows,columns):
    with (D/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=columns+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader()
        w.writerows(dict(r,row_status='recorded') for r in rows)
def dump(name,data): (D/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def eliminate(equations):
    nodes=sorted({n for e in equations for n in e['terms']})
    n=len(nodes); count=len(equations)
    rows=[]
    for i,e in enumerate(equations):
        row=[F(e['terms'].get(node,0)) for node in nodes]+[F(-int(e['value']==v)) for v in 'ABC']
        rows.append(row+[F(int(i==j)) for j in range(count)])
    pivot=0
    for col in range(n+3):
        k=next((j for j in range(pivot,count) if rows[j][col]),None)
        if k is None: continue
        rows[pivot],rows[k]=rows[k],rows[pivot]
        scale=rows[pivot][col];rows[pivot]=[x/scale for x in rows[pivot]]
        for j in range(count):
            if j!=pivot:
                scale=rows[j][col];rows[j]=[a-scale*b for a,b in zip(rows[j],rows[pivot])]
        pivot+=1
    constraints=[]
    for row in rows:
        if not any(row[:n]) and any(row[n:n+3]):
            constraints.append(dict(log_value_coefficients={v:str(row[n+i]) for i,v in enumerate('ABC')},witness={equations[j]['at']:str(x) for j,x in enumerate(row[n+3:]) if x}))
    return dict(nodes=nodes,equations=equations,rank=pivot,value_constraint_rank=len(constraints),constraints=constraints,positive_all_one_solution=True)
fields=[];actions=[];readings=[];summary={};algebra={}
for scope in spec['scopes']:
    sf=[];sa=[]
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
                sf.append(dict(scope=scope,record=rid,at=t['at'],word=w,value=values[w],material=current['at'] if current else '',material_word=current['word'] if current else '',quality=quality['at'] if quality else '',quality_word=quality['word'] if quality else '',denominator=previous['at'] if previous else '',denominator_word=previous['word'] if previous else '',G_missing=','.join(k for k,b in [('material',not current),('quality',not quality)] if b),M_missing='material' if not current else '',R_missing=','.join(k for k,b in [('material',not current),('denominator',not previous)] if b)))
            if w in verbs:
                target=None
                for u in ts[i+1:]:
                    if scope=='LINE' and u['line']!=t['line']:break
                    if u['word'] in verbs or u['word'] in values:break
                    if u['word'] in materials:target=u;break
                sa.append(dict(scope=scope,record=rid,at=t['at'],word=w,target=target['at'] if target else '',target_word=target['word'] if target else ''))
    fields.extend(sf);actions.extend(sa)
    for mode in ['M','R']:
        eq=[]
        for f in sf:
            if f[mode+'_missing']:continue
            terms={f['record']+':'+f['material_word']:1}
            if mode=='R':terms[f['record']+':'+f['denominator_word']]=-1
            else:terms[f['record']+':UNIT_U']=-1
            eq.append(dict(at=f['at'],terms=terms,value=f['value']))
        algebra[scope+'_'+mode]=eliminate(eq)
    byat={f['at']:f for f in sf};act={a['at']:a for a in sa}
    for rid,ts in records.items():
        for t in ts:
            w=t['word'];base=materials.get(w,qualities.get(w,'⟦'+w+'⟧'))
            if w in verbs:base=verbs[w]+' '+materials.get(act[t['at']]['target_word'],'?')+' [Bezug='+act[t['at']]['target']+']'
            row=dict(scope=scope,record=rid,at=t['at'],word=w)
            for mode in ['G','M','R']:
                reading=base
                if w in values:
                    f=byat[t['at']];name=materials.get(f['material_word'],'?');v=f['value']
                    if mode=='G':reading=name+': '+qualities.get(f['quality_word'],'?')+' im Grad '+v+' [Skala offen]'
                    if mode=='M':reading=name+': Menge '+v+'·U'
                    if mode=='R':reading='Masse('+name+') / Masse('+materials.get(f['denominator_word'],'?')+') = '+v
                    reading+=' [fehlend='+f[mode+'_missing']+']'
                row[mode]=reading
            readings.append(row)
    summary[scope]=dict(value_positions=len(sf),bound={m:sum(not f[m+'_missing'] for f in sf) for m in ['G','M','R']},actions=len(sa),bound_actions=sum(bool(a['target']) for a in sa),value_constraint_ranks={m:algebra[scope+'_'+m]['value_constraint_rank'] for m in ['M','R']})
tab('FIELDS.tsv',fields,list(fields[0]));tab('ACTIONS.tsv',actions,list(actions[0]));tab('READINGS.tsv',readings,list(readings[0]));dump('ALGEBRA.json',algebra)
known=set(materials)|set(qualities)|set(values)|set(verbs)
coverage=[dict(record=rid,groups=len(ts),assumed=sum(t['word'] in known for t in ts),open=sum(t['word'] not in known for t in ts)) for rid,ts in records.items()]
tab('COVERAGE.tsv',coverage,list(coverage[0]))
md=['# W40 — vollständiger Lesungsvergleich','','Alle Bedeutungen, Einheiten und Beziehungen sind Hypothesen. Offene Wörter bleiben erhalten; keine fertige Übersetzung. Die alten P14-Glossen ersetzen nicht W38.','']
for rid,ts in records.items():
    md+=['## '+rid,'']
    for line in dict.fromkeys(t['line'] for t in ts):
        md += [line+': `'+ ' '.join(t['word'] for t in ts if t['line']==line)+'`','']
        for scope in spec['scopes']:
            rr=[r for r in readings if r['scope']==scope and r['record']==rid and r['at'].rsplit(':',1)[0]==line]
            for mode in ['G','M','R']:md += [scope+'/'+mode+': '+' · '.join(r[mode] for r in rr),'']
(D/'READING.md').write_text('\n'.join(md)+'\n')
result=dict(groups=len(raw),paragraphs=len(records),lines=len({r['locus'] for r in raw}),assumed_positions=sum(r['assumed'] for r in coverage),open_positions=sum(r['open'] for r in coverage),summary=summary,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
dump('RESULT.json',result)
print(json.dumps(result,indent=2))
