"""Independent full-window census using direct equality and minimal periods."""
import collections,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
s=json.loads((E/'src/SPEC.json').read_text());hits=read('HITS.json');result=read('RESULT.json');expectedhits=[];higher=[];totalgroups=0;ids=set()
for ed in s['editions']:
 source=read(f'SOURCE_{ed}.json');assert source['group_columns']==s['group_columns'];expectedwindows=[];den={p:collections.Counter(candidate=0,eligible=0,nonprimitive_tandem=0,primitive_tandem=0) for p in s['periods']};highlines=set()
 for li,line in enumerate(source['lines']):
  m=line['metadata'];assert m['edition']==ed and m['page'] in s['allowed_selectors'] and not m['page'].startswith('f84');gg=[dict(zip(source['group_columns'],g)) for g in line['groups']];totalgroups+=len(gg)
  for g in gg:assert g['source_group_id'] not in ids;ids.add(g['source_group_id'])
  for p in s['periods']:
   for start in range(len(gg)-2*p+1):
    block=gg[start:start+2*p];eligible=True
    for offset in range(1,len(block)):
     a,b=block[offset-1],block[offset]
     if int(b['source_group_index'])!=int(a['source_group_index'])+1 or a['right_separator']!='DEFINITE_SPACE' or b['left_separator']!='DEFINITE_SPACE':eligible=False
    raw=[g['ivtff_group_raw'] for g in block];tandem=eligible and all(raw[i]==raw[i+p] for i in range(p));minimal=None
    if tandem:
     for q in range(1,p+1):
      if all(raw[i]==raw[i-q] for i in range(q,2*p)):minimal=q;break
    primitive=minimal==p;expectedwindows.append([li,start,p,int(eligible),int(tandem),int(primitive)])
    den[p]['candidate']+=1;den[p]['eligible']+=eligible;den[p]['nonprimitive_tandem']+=tandem and not primitive;den[p]['primitive_tandem']+=primitive
    if primitive:
     expectedhits.append(dict(edition=ed,locus=m['locus'],page=m['page'],folio=re.match(r'f[0-9]+',m['page']).group(),period=p,start_index=block[0]['source_group_index'],source_ids=[g['source_group_id'] for g in block],groups=raw,line_array_index=li))
     if p>1:highlines.add(li)
 assert read(f'WINDOWS_{ed}.json')['rows']==expectedwindows
 for p in s['periods']:assert result['summary'][ed][str(p)]==dict(den[p],folios=sorted({h['folio'] for h in expectedhits if h['edition']==ed and h['period']==p}))
 for li in sorted(highlines):higher.append(dict(edition=ed,line=source['lines'][li]))
assert hits==expectedhits;assert read('HIGHER_PERIOD_LINES.json')['lines']==higher
assert result['hit_rows']==len(hits) and result['higher_period_source_lines']==len(higher)
assert totalgroups==read('GUARD.json')['stats']['selected']
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_FULL_SOURCE_WINDOW_AND_PRIMITIVE_PERIOD_CENSUS',source_groups=totalgroups,hits=len(hits),semantic_validation=False),indent=2)+'\n');print('PASS')
