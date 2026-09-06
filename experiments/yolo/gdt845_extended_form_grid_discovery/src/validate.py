import itertools,json,math,re
from pathlib import Path
from collections import Counter
E=Path(__file__).resolve().parents[1]
s=json.loads((E/'src/SPEC.json').read_text());hits=json.loads((E/'artifacts/HITS.json').read_text());cells=json.loads((E/'artifacts/CELLS.json').read_text());result=json.loads((E/'artifacts/RESULT.json').read_text())
assert len(cells)==72 and len({r['word'] for r in cells})==72
assert len({r['source_group_id'] for r in hits})==len(hits)
assert all(r['page'] in s['allowed_selectors'] and not r['page'].startswith('f84') for r in hits)
for cell in cells:
    expected_word=cell['wrapper']+cell['head']+cell['middle']+'e'*cell['e']+'d'*cell['d']+'y';assert expected_word==cell['word']
    for ed in s['editions']:
        selected=[r for r in hits if r['edition']==ed and r['ivtff_group_raw']==expected_word]
        assert len(selected)==cell['counts'][ed]
        assert sorted({re.match(r'f[0-9]+',r['page']).group() for r in selected})==cell['folios'][ed]
for row in result['summary']:
    totals=Counter();joint=0
    for hit in hits:
        if hit['edition']!=row['edition']:continue
        m=re.fullmatch(r'(qo|o)?([kt])(ch|sh)(e{0,2})(d?)y',hit['ivtff_group_raw']);assert m
        w,h,c,e,d=m.groups()
        if (w or '')!=row['wrapper']:continue
        totals[h,c,'n']+=1;totals[h,c,'e']+=len(e)==2;totals[h,c,'d']+=bool(d);joint+=len(e)==2 and bool(d)
    exp=sum(totals[h,c,'e']*totals[h,c,'d']/totals[h,c,'n'] for h,c in itertools.product(s['heads'],s['middles']) if totals[h,c,'n'])
    assert joint==row['observed'] and math.isclose(exp,row['expected'])
(E/'artifacts/VALIDATION.json').write_text(json.dumps({'status':'PASS_SOURCE_INVENTORY_AND_INDEPENDENT_REGEX_AGGREGATION','cells':72,'hits':len(hits),'semantic_validation':False},indent=2)+'\n');print('PASS')
