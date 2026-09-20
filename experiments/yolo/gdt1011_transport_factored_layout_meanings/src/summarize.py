from common import *
import csv,collections
rows=read(A/'ORIGINAL_ROWS.json');valid=[r for r in rows if r['valid_variants']];extensions=read(A/'ROWS.json');v=read(A/'VALIDATION.json');assert v['status']=='PASS'
domains=[]
for family in ['FUNCTIONAL','BIJECTIVE']:
    before=[r for r in rows if family=='FUNCTIONAL' or r['bijective']];after=[r for r in before if r['valid_variants']]
    for word in sorted(rows[0]['code']):
        b=sorted({r['code'][word] for r in before});a=sorted({r['code'][word] for r in after})
        domains.append(dict(family=family,word=word,syntax_values=','.join(b),source_valid_values=','.join(a),excluded_values=','.join(sorted(set(b)-set(a))),scope='EXHAUSTIVE_WITHIN_FIXED_SOURCE_MODEL',independent_meaning_capacity=0))
with (A/'WORD_DOMAINS.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(domains[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(domains)
with (A/'SOURCE_VALID_CANDIDATES.tsv').open('w',newline='') as f:
    columns=['id','layout','bijective','valid_variants']+sorted(rows[0]['code']);w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(columns)
    for r in valid:w.writerow([r['id'],r['layout'],r['bijective'],','.join(map(str,r['valid_variants']))]+[r['code'][x] for x in columns[4:]])
layouts=[]
for layout in read(A/'LAYOUTS.json'):
    subset=[r for r in rows if r['layout']==layout['id']];good=[r for r in subset if r['valid_variants']]
    layouts.append(dict(layout=layout['id'],clause_order=','.join(c['kind'] for c in layout['layout']),complete_maps=len(subset),valid_maps=len(good),valid_settings=sum(len(r['valid_variants']) for r in good)))
with (A/'LAYOUT_OUTCOMES.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(layouts[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(layouts)
central=[dict(candidate=r['id'],variant=i,word='qokedy',value=r['code']['qokedy'],hazards=r['full_replays'][i]['hazards'],in_both_pairs=all(r['code']['qokedy'] in pair for pair in r['full_replays'][i]['hazards'])) for r in valid for i in r['valid_variants']]
assert len(central)==156 and all(x['in_both_pairs'] for x in central)
projection=['chedy','lchedy','otaiin','otedy','otor','qokedy','qoteedy','sar','shedy','sol','solkeedy']
put('CONTENT_CONSEQUENCES.json',dict(central_cargo_checks=central,exhaustive_functional_projected_tuples=len({tuple(r['code'][w] for w in projection)+(i,) for r in valid for i in r['valid_variants']}),new_fixed_values=[d for d in domains if d['family']=='FUNCTIONAL' and ',' in d['syntax_values'] and ',' not in d['source_valid_values']],claim='Source-conditioned consequences only, not word confirmation or an independently bound relation packet.'))
print(json.dumps(dict(original_maps=len(rows),valid_maps=len(valid),domains=len(domains),centrality_checks=len(central))))
