from common import *
import itertools,concurrent.futures
import solver,independent,z3
from cvc5 import pythonic as c

def ground(k,before):
    if k=='FERRY':return 1-before
    if k in ('WITH_OUT','CONVEY','FINAL_TRIP'):return 1 if before==0 else None
    if k in ('EXCLUDE','WITH_RETURN','ALONE'):return 0 if before==1 else None
    return before

def known(row):
    s,g=inputs();p=read(A/'PANEL.json')[0]
    one=solver.solve([p],row['code'],g,timeout=20000,witness_limit=1)
    two=independent.check([p],row['code'],g,timeout=30000)
    assert one['status']=='SAT' and two['status']=='sat',row['id']
    bank=0
    for clause in row['parse']:
        bank=ground(clause['kind'],bank);assert bank is not None
    assert bank==1
    return dict(id=row['id'],primary=one['status'],independent=two['status'],original_known_parse_bank=True)

def main():
    s,g=inputs();fixtures=[]
    for kind in g['patterns']:
        for a,b in itertools.product(range(2),repeat=2):
            expected=ground(kind,a)==b
            z=bool(z3.is_true(z3.simplify(solver.bank_rule(z3.IntVal(a),z3.IntVal(b),kind))))
            q=c.Solver();q.add(independent.bank_rule(c.IntVal(a),c.IntVal(b),kind));cc=str(q.check())=='sat'
            assert z==cc==expected,(kind,a,b)
            fixtures.append(dict(kind=kind,before=a,after=b,valid=expected))
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:known_checks=list(pool.map(known,read(A/'ORIGINAL_CANDIDATES.json')))
    changes={}
    for name,key in [('solver.py','source_primary'),('independent.py','source_independent')]:
        import difflib
        changes[name]=list(difflib.unified_diff((R/s[key]).read_text().splitlines(),(E/'src'/name).read_text().splitlines(),fromfile='unchanged1002',tofile='necessary_bank',lineterm=''))
    put('ENCODING_CHANGES.json',changes);put('PREFLIGHT.json',dict(status='PASS',truth_table=fixtures,known_originals=known_checks,meaning='Both encodings retain every complete original dictionary; all68single-clause bank cases checked. No f50r solving before registration.'))
    print('PASS',len(fixtures),'bank transitions;',len(known_checks),'known original codes')
if __name__=='__main__':main()
