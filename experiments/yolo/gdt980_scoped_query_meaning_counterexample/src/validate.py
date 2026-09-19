"""Separate Prufer-tree enumeration and query evaluator; no primary imports."""
import csv, hashlib, itertools, json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
s=json.loads((E/'src/SPEC.json').read_text())
for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
    assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
nodes=s['nodes'];names=dict(zip(['FIELD','LION','BORDER','ROUND'],nodes));filters={x.upper():x for x in s['colors']}

def parse(clause):
    op=clause[-1];body=clause[:-1];qs=[]
    while body:
        assert body[0] in names
        selector=body.pop(0);unary=[]
        while body and body[0] not in names:
            a=body.pop(0);assert a in filters or a=='PARENT';unary.append(a)
        assert len(unary)<=3
        qs.append((selector,unary))
    assert (op,len(qs)) in [('NE',1),('EQ',2)]
    return op,qs
parsed={k:[parse(c[:]) for c in p] for k,p in s['programs'].items()}
for program in parsed.values():
    assert 1<=len(program)<=8
    assert {q[0] for _,qs in program for q in qs}==set(names)

def evaluate(program,w):
    def query(q):
        selected=[names[q[0]]]
        for a in q[1]:
            if a=='PARENT':selected=list({w['parent'][v] for v in selected if v in w['parent']})
            else:selected=[v for v in selected if w['colors'][v]==filters[a]]
        return frozenset(selected)
    return all(bool(query(qs[0])) if op=='NE' else query(qs[0])==query(qs[1]) for op,qs in program)

trees=[]
for seq in itertools.product(nodes,repeat=2):
    degree={n:1+seq.count(n) for n in nodes};edges=[]
    for n in seq:
        leaf=next(x for x in nodes if degree[x]==1)
        edges.append((leaf,n));degree[leaf]-=1;degree[n]-=1
    final=[x for x in nodes if degree[x]==1];edges.append(tuple(final))
    parent={};seen={s['root']}
    while len(seen)<4:
        for a,b in edges:
            if (a in seen)!=(b in seen):
                child,par=(b,a) if a in seen else (a,b);parent[child]=par;seen.add(child)
    trees.append(parent)
expected={}
for p in trees:
    for c in itertools.product(s['colors'],repeat=4):
        w={'parent':p,'colors':dict(zip(nodes,c))};key=json.dumps(w,sort_keys=True,separators=(',',':'))
        assert key not in expected
        expected[key]={n:evaluate(prog,w) for n,prog in parsed.items()}
rows=list(csv.DictReader((E/'artifacts/WORLD_TABLE.tsv').open(),delimiter='\t'))
assert len(rows)==len(expected)==4096
reference={k:s['source_scene'][k] for k in ['parent','colors']}
assert len({r['world'] for r in rows})==len(rows)
for row in rows:
    assert {n:row[n]=='True' for n in parsed}==expected[row['world']]
    assert (row['source_scene']=='True')==(json.loads(row['world'])==reference)
accounts=json.loads((E/'artifacts/ACCOUNTS.json').read_text());result=json.loads((E/'artifacts/RESULT.json').read_text())
assert len(accounts)==len(parsed)==5
assert set(a['account'] for a in accounts)==set(parsed)
code=s['fixed_code'];assert set(code)==set(s['atoms']) and len(set(code.values()))==len(code)
assert all(1<=len(v)<=3 for v in code.values())
assert all(not b.startswith(a) for a in code.values() for b in code.values() if a!=b)
for a in accounts:
    n=a['account'];assert a['clauses']==s['programs'][n]
    flat=[x for cl in a['clauses'] for x in cl];assert a['used_atoms']==sorted(set(flat))
    assert a['all_atoms_used']==(set(flat)==set(s['atoms']))
    assert a['whole_surface']== ' '.join(''.join(code[x] for x in flat[i:i+3]) for i in range(0,len(flat),3))
    assert a['grammar_valid'] and a['source_truth']==evaluate(parsed[n],reference)
    count=sum(v[n] for v in expected.values());assert a['accepted_worlds']==count
    assert a['incompatible_worlds']==count-int(a['source_truth'])
    cert=a['changed_parent_and_color_certificate']
    has_cert=any(v[n] and (w:=json.loads(k))['parent']!=reference['parent'] and w['colors']!=reference['colors'] for k,v in expected.items())
    assert (cert is not None)==has_cert
    if cert:assert evaluate(parsed[n],cert) and cert['parent']!=reference['parent'] and cert['colors']!=reference['colors']
    assert result['accounts'][n]=={k:a[k] for k in ['grammar_valid','all_atoms_used','source_truth','accepted_worlds','incompatible_worlds']}
assert result['world_count']==len(expected) and result['tree_count']==len(trees)==16
assert result['status']=='COMPLETE_ACCOUNT_TRUTH_INSUFFICIENT'
assert not result['target_access'] and not result['significance_claim'] and result['confirmed_words']==0
with (E/'artifacts/ACCOUNT_TABLE.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
assert len(table)==len(accounts)
for row,a in zip(table,accounts):assert row=={k:str(a[k]) for k in row}
checks={'status':'PASS','worlds':len(expected),'truth_cells':len(expected)*len(parsed),'accounts':len(accounts),'trees':len(trees),'independent_mechanisms':'Prufer trees and parsed expression evaluator; primary imports none','target_access':False}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
