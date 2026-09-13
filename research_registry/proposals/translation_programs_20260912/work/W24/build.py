"""Frozen whole al partitive source hypotheses; no patient override."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(p):return json.loads(p.read_text())
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=js(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
flat=rows(W/'W23/SOURCE_FLAT.tsv');args=[r for r in rows(W/'W23/ARGUMENTS.tsv') if r['model']=='U'];MAT=set(js(W/'W05/SPEC.json')['material_roles']);groups=collections.defaultdict(list)
for r in flat:r['offset']=int(r['offset']);groups[r['edition'],r['paragraph']].append(r)
gloss={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
refs=[];pairs=[];bridges=[];phrases=[];comparison=[]
for (ed,p),ff in groups.items():
 byid={r['id']:r for r in ff};als=[r for r in ff if r['form']=='al']
 for x in als:
  prior=[r for r in ff if r['offset']<x['offset'] and r['role'] in MAT];prev=ff[x['offset']-1] if x['offset'] else None
  amount=prev if prev and prev['locus']==x['locus'] and prev['role']=='AMOUNT' else None
  for y in prior:pairs.append(dict(edition=ed,paragraph=p,target=x['id'],material=y['id'],form=y['form'],offset=y['offset']))
  for g in S['grammars']:
   earlier=[a for a in args if a['edition']==ed and a['paragraph']==p and a['variant']==g and byid[a['operation']]['offset']<x['offset']]
   latest=earlier[-1] if earlier else None;selected={}
   for model in S['models']:
    source=prior[-1] if model=='T' and prior else byid.get(latest['patient']) if model=='V' and latest else None
    origin=latest['operation'] if model=='V' and latest else '';debt=latest['debts'] if model=='V' and latest else ''
    # Preserve forward-bound patients of earlier written actions explicitly.
    crossed=[r for r in ff if source and min(source['offset'],x['offset'])<r['offset']<max(source['offset'],x['offset'])]
    record=dict(edition=ed,paragraph=p,grammar=g,model=model,target=x['id'],source=source['id'] if source else '',source_form=source['form'] if source else '',via_action=origin,source_after_reference=bool(source and source['offset']>x['offset']),inherited_debts=debt,unread_between=';'.join(r['id'] for r in crossed if r['role']=='OPEN'),other_materials=';'.join(r['id'] for r in crossed if r['role'] in MAT),amount=amount['id'] if amount else '',amount_form=amount['form'] if amount else '',status='UNBOUND_BASELINE' if model=='U' else 'SOURCE_BOUND_HYPOTHETICALLY' if source else 'MISSING_SOURCE')
    refs.append(record);selected[model]=record
    if amount:phrases.append(dict(record,reading=gloss.get(amount['form'],amount['form'])+' davon: '+(gloss.get(source['form'],source['form'])+' ('+source['id']+')' if source else '[Herkunft ungebunden]'),numerical_quantity='',actual_partition_event='NOT_ESTABLISHED'))
   comparison.append(dict(edition=ed,paragraph=p,grammar=g,target=x['id'],T_source=selected['T']['source'],V_source=selected['V']['source'],same_nonempty=bool(selected['T']['source'] and selected['T']['source']==selected['V']['source']),amount=amount['id'] if amount else ''))
 for ok in [r for r in ff if r['form']=='okor']:
  for al in als:
   if al['offset']>=ok['offset']:continue
   between=[r for r in ff if al['offset']<r['offset']<ok['offset']]
   bridges.append(dict(edition=ed,paragraph=p,al=al['id'],okor=ok['id'],groups_between=len(between),raw_between=' '.join(r['form'] for r in between),unread_between=';'.join(r['id'] for r in between if r['role']=='OPEN'),materials_between=';'.join(r['id'] for r in between if r['role'] in MAT),actions_between=';'.join(a['operation'] for a in args if a['edition']==ed and a['paragraph']==p and a['variant']=='B' and al['offset']<byid[a['operation']]['offset']<ok['offset']),identity='NO_WRITTEN_OUTPUT_ALIAS_ESTABLISHED'))
for n,rr in [('REFERENCES',refs),('ALL_SOURCE_PAIRS',pairs),('PARTITIVE_PHRASES',phrases),('COMPARISON',comparison),('AL_TO_OKOR',bridges)]:table(n+'.tsv',rr)
alignment=rows(W/'W23/ALIGNMENT.tsv');out=[];reader=['# W24: Vollständige W23-Lesung mit al-Herkunftsalternativen','Alle Glossen bleiben hypothetisch. W23 U/A/N-okor erhalten; T/V binden nur al, keinen späteren Patienten oder Ergebnisnamen. Anzeige der Referenzen unter M; B/J vollständig in Tabellen.']
for r in alignment:
 rr=[x for x in refs if x['edition']=='ZL3b' and x['grammar']=='M' and x['target']==r['locus']+':'+r['index']]
 note=' | '.join(x['model']+': '+(x['source_form']+' '+x['source'] if x['source'] else 'Herkunft ungebunden') for x in rr);out.append(dict(r,al_reference_M=note))
for p in dict.fromkeys(r['paragraph'] for r in out):
 reader.append('\n## '+p)
 for loc in dict.fromkeys(r['locus'] for r in out if r['paragraph']==p):
  rr=[r for r in out if r['paragraph']==p and r['locus']==loc];reader.append('\n'+loc+'\n\n'+' · '.join(r['raw']+' ['+('{A: teile ab / N: abgeteilter Anteil / U: ungelesen}' if r['raw']=='okor' else r['joint'])+(' {'+r['al_reference_M']+'}' if r['al_reference_M'] else '')+']' for r in rr))
table('ALIGNMENT.tsv',out);(E/'READING.md').write_text('\n'.join(reader)+'\n')
result=dict(reference_rows=len(refs),partitive_rows=len(phrases),source_pair_rows=len(pairs),al_to_okor_rows=len(bridges),primary_targets=sum(r['edition']=='ZL3b' and r['grammar']=='B' and r['model']=='U' for r in refs),primary_TV_same=sum(r['edition']=='ZL3b' and r['grammar']=='B' and r['same_nonempty'] for r in comparison),primary_groups=len(out),new_glosses=0,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
result['targets_by_reading']={ed:sum(r['edition']==ed and r['grammar']=='B' and r['model']=='U' for r in refs) for ed in sorted({e for e,p in groups})}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
