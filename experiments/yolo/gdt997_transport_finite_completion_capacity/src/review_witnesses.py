"""Post-result audit of all saved witnesses; never refits or changes meanings."""
import collections,csv,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
cfg=read(E/'src/SPEC.json');rows=read(A/'ROWS.json');src=read(R/cfg['source_paragraphs']);ps={ed+'|'+p['id']:p for ed,xs in src.items() for p in xs};oldlex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']}
selected=[r for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='COHERENT_LOCAL_EXTENSION'];pairs=[];compatible=set()
for a,b in itertools.combinations(selected,2):
 da=a['shared']['aliases'];db=b['shared']['aliases'];common=sorted(da.keys()&db.keys());conflicts=[dict(raw=w,left=da[w],right=db[w]) for w in common if da[w]!=db[w]]
 pairs.append(dict(left=a['id'],right=b['id'],shared_words=common,conflicts=conflicts,compatible=not conflicts))
 if not conflicts:compatible.add(frozenset((a['id'],b['id'])))
ids=[r['id'] for r in selected];subsets=[]
for size in range(1,len(ids)+1):
 for ss in itertools.combinations(ids,size):
  if all(frozenset(p) in compatible for p in itertools.combinations(ss,2)):subsets.append(set(ss))
maximal=[sorted(s) for s in subsets if not any(s<t for t in subsets)]
alignment=[];table=[]
for row in selected:
 p=ps[row['id']];words=[w for l in p['lines'] for w in l['words']];locs=[l['locus'] for l in p['lines'] for w in l['words']];local=[i+1 for l in p['lines'] for i,w in enumerate(l['words'])]
 symbols={**oldlex,**row['shared']['aliases']};owners={i:c['kind'] for c in row['shared']['parse'] for i in range(c['start'],c['end'])}
 for i,w in enumerate(words):alignment.append(dict(id=row['id'],position=i+1,locus=locs[i],group=local[i],raw=w,symbol=symbols[w],clause=owners[i],status='OLD_HYPOTHESIS' if w in oldlex else 'NEW_ALIAS_HYPOTHESIS'))
 alternative_rows=[dict(id=r['id'],status=r['status'],groups=r['groups'],partition=r['partition']) for r in rows if r['paragraph']==row['paragraph'] and r['id']!=row['id']]
 c=next(c for c in row['cases'] if c['status']=='COHERENT_WITNESS');path=next(x for x in c['paths'] if x['consistent']);then=sum(x['kind']=='THEN' for x in row['shared']['parse'])
 table.append(dict(id=row['id'],groups=len(words),known_groups=row['known_groups'],known_values=[dict(raw=w,symbol=oldlex[w]) for w in words if w in oldlex],new_types=len(row['shared']['aliases']),then_occurrences=then,then_distinct_aliases=sum(v=='THEN' for v in row['shared']['aliases'].values()),cargo=c['program']['cargo'],hazards=c['program']['hazards'],voyages=len(path['trace'])-1,strict_anchor_eligible=row['strict_anchor_eligible'],alternate_same_boundaries=alternative_rows,independent_meaning_capacity=0))
out=dict(status='POST_RESULT_SAVED_WITNESS_AUDIT',candidates=table,pairs=pairs,maximal_compatible_saved_subsets=maximal,limits='No joint refit;incompatible first witnesses do not exclude alternative shared dictionaries;0confirmedwords,no probability,no grammar repair')
(A/'WITNESS_INTERPRETATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
with (A/'FULL_NEW_WITNESS_READINGS.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(alignment[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(alignment)
print(json.dumps(out,ensure_ascii=False))
