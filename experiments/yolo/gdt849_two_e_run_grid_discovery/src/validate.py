"""Independent regex aggregation and entropy identity; not semantic validation."""
import collections,itertools,json,math,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/n).read_text())
s=read('src/SPEC.json');hits=read('artifacts/HITS.json');cells=read('artifacts/CELLS.json');r=read('artifacts/RESULT.json');counts=collections.Counter();folios=collections.defaultdict(set)
assert len(cells)==len({x['word'] for x in cells})==36
assert len({x['source_group_id'] for x in hits})==len(hits)
for h in hits:
 assert h['page'] in s['allowed_selectors'] and not h['page'].startswith('f84')
 m=re.fullmatch(r'(ch|sh)(e{0,2})(cth|ckh)(e{0,2})y',h['ivtff_group_raw']);assert m
 p,a,k,b=m.groups();key=(h['edition'],p,k,len(a),len(b));counts[key]+=1;folios[key].add(re.match(r'f[0-9]+',h['page']).group())
for c in cells:
 assert c['word']==c['prefix']+'e'*c['outer_e']+c['kernel']+'e'*c['inner_e']+'y'
 for ed in s['editions']:
  key=(ed,c['prefix'],c['kernel'],c['outer_e'],c['inner_e']);assert c['counts'][ed]==counts[key];assert c['folios'][ed]==sorted(folios[key])
def entropy(vals):
 n=sum(vals);return -sum(v/n*math.log(v/n) for v in vals if v) if n else 0.
for st in r['strata']:
 arr=[[counts[st['edition'],st['prefix'],st['kernel'],a,b] for b in range(3)] for a in range(3)];assert arr==st['matrix'];rr=list(map(sum,arr));cc=list(map(sum,zip(*arr)));n=sum(rr);assert n==st['n']
 for a,b in itertools.product(range(3),repeat=2):assert math.isclose(st['expected'][a][b],rr[a]*cc[b]/n if n else 0.)
 mi=entropy(rr)+entropy(cc)-entropy([v for row in arr for v in row]);assert math.isclose(mi,st['mutual_information_nats'],abs_tol=1e-12)
 assert st['outer_levels']==sum(v>0 for v in rr) and st['inner_levels']==sum(v>0 for v in cc)
 assert st['both_margins_vary']==(sum(v>0 for v in rr)>1 and sum(v>0 for v in cc)>1)
for ed in s['editions']:
 sub=[x for x in r['strata'] if x['edition']==ed];n=sum(x['n'] for x in sub);ss=r['summary'][ed];assert ss['n']==n and ss['occupied']==sum(c['counts'][ed]>0 for c in cells)
 assert ss['joint_variation_strata']==sum(x['both_margins_vary'] for x in sub)
 expected=sum(x['n']*x['mutual_information_nats'] for x in sub)/n if n else 0.;assert math.isclose(ss['conditional_mutual_information_nats'],expected,abs_tol=1e-12)
assert r['hit_rows']==len(hits)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_REGEX_COUNTS_AND_ENTROPY_IDENTITY',hits=len(hits),cells=36,semantic_validation=False),indent=2)+'\n');print('PASS')
