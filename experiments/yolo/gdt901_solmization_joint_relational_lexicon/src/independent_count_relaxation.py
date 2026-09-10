#!/usr/bin/env python3
"""Independent count/head relaxation. SAT is NOT a full model witness.

Finite integer tables enforce counts including zero, two injective assignments,
and first raw words. Word order and root/affix equations are intentionally absent.
The shared budget includes input loading, constraint construction, and checking.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
import z3
from independent_role_domains import audit_source, record_digest, CASES


def sha(b):
    return hashlib.sha256(b).hexdigest()


def solve(records, paragraphs, domains, deadline):
    started = time.monotonic()
    atoms = sorted(domains)
    assert set(atoms) == {a for r in records for a in r['sequence']}
    assert len({r['id'] for r in records}) == len(records)
    assert len({p['id'] for p in paragraphs}) == len(paragraphs)
    words = sorted({w for values in domains.values() for w in values})
    wi = {w:i for i,w in enumerate(words)}
    ds = {a:[wi[w] for w in domains[a]] for a in atoms}
    pc = [Counter(p['words']) for p in paragraphs]
    rc = [Counter(r['sequence']) for r in records]
    solver = z3.Solver()
    solver.set(threads=1, random_seed=0)
    x = {a:z3.Int('form_'+str(i)) for i,a in enumerate(atoms)}
    y = [z3.Int('paragraph_'+str(i)) for i in range(len(records))]
    def checktime():
        if time.monotonic() >= deadline:
            raise TimeoutError
    def member(v, values):
        return z3.Or([v == n for n in values])
    try:
        for a in atoms:
            checktime()
            solver.add(member(x[a],ds[a]))
        solver.add(z3.Distinct(list(x.values())),z3.Distinct(y))
        for i,r in enumerate(records):
            checktime()
            # These are exactly the first-word relation and its required count.
            possible = [j for j,p in enumerate(paragraphs) if p['words'] and
                        p['words'][0] in domains[r['head_atom']] and
                        pc[j][p['words'][0]] == rc[i][r['head_atom']]]
            solver.add(member(y[i],possible))
            solver.add(z3.Or([z3.And(y[i] == j,
                           x[r['head_atom']] == wi[paragraphs[j]['words'][0]])
                           for j in possible]))
            for a in atoms:
                checktime()
                required = rc[i][a]
                # A forbidden table for zero, an allowed table otherwise.
                # Equal paragraph-support sets share a disjunction of word IDs.
                grouped = {}
                for w in ds[a]:
                    support = tuple(j for j in possible if
                                    (pc[j][words[w]] != 0 if required == 0
                                     else pc[j][words[w]] == required))
                    if support:
                        grouped.setdefault(support,[]).append(w)
                table = z3.Or([z3.And(member(x[a],values),member(y[i],support))
                               for support,values in grouped.items()])
                solver.add(z3.Not(table) if required == 0 else table)
        checktime()
        build = time.monotonic()-started
        solver.set(timeout=max(1,int((deadline-time.monotonic())*1000)))
        status = solver.check()
        out = {'solver_status':str(status).upper(),'build_seconds':build}
        if status == z3.unknown:
            out['reason_unknown'] = solver.reason_unknown()
        elif status == z3.sat:
            model = solver.model()
            code = {a:words[model.eval(x[a]).as_long()] for a in atoms}
            chosen = [model.eval(v).as_long() for v in y]
            assert len(set(code.values())) == len(code)
            assert len(set(chosen)) == len(chosen)
            for i,j in enumerate(chosen):
                assert paragraphs[j]['words'][0] == code[records[i]['head_atom']]
                assert all(pc[j][code[a]] == rc[i][a] for a in atoms)
            out.update(relaxed_form_words=code,relaxed_paragraph_assignments=[
                {'source_id':r['id'],'target_id':paragraphs[j]['id']}
                for r,j in zip(records,chosen)],exact_python_replay='PASS')
    except TimeoutError:
        out = {'solver_status':'UNKNOWN','reason_unknown':'shared budget exhausted during construction'}
    out['status'] = {'SAT':'RELAXATION_SAT_NOT_FULL_WITNESS',
                     'UNSAT':'FULL_CASE_UNSAT_BY_COUNT_HEAD_RELAXATION',
                     'UNKNOWN':'FULL_CASE_UNRESOLVED'}[out['solver_status']]
    out['elapsed_solver_seconds'] = time.monotonic()-started
    return out


def self_test():
    def run(rs,ps,ds):
        return solve(rs,ps,ds,time.monotonic()+10)['solver_status']
    def r(name,seq): return {'id':name,'head_atom':seq[0],'sequence':seq}
    def p(name,seq): return {'id':name,'words':seq}
    assert run([r('a',['H','A','B'])],[p('p',['h','b','a'])],
               {'H':['h'],'A':['a'],'B':['b']}) == 'SAT' # order intentionally absent
    assert run([r('a',['H','A'])],[p('p',['h','a'])],
               {'H':['h'],'A':['h']}) == 'UNSAT' # injectivity
    assert run([r('a',['H']),r('b',['H'])],[p('p',['h'])],{'H':['h']}) == 'UNSAT'
    assert run([r('a',['H']),r('b',['J','A'])],
               [p('p',['h','a']),p('q',['j','a'])],
               {'H':['h'],'J':['j'],'A':['a']}) == 'UNSAT' # zero counts
    assert run([r('a',['H','A'])],[p('p',['a','h'])],
               {'H':['h'],'A':['a']}) == 'UNSAT' # head
    assert solve([r('a',['H'])],[p('p',['h'])],{'H':['h']},
                 time.monotonic()-1)['solver_status'] == 'UNKNOWN'
    print('PASS: six synthetic count/head, injectivity, capacity, zero, order-scope and budget checks')


def main():
    started = time.monotonic()
    ap = argparse.ArgumentParser()
    for arg in ['source','observer','model-spec','target','domains','output']:
        ap.add_argument('--'+arg,type=Path)
    ap.add_argument('--case-index',type=int,choices=range(10))
    ap.add_argument('--panel',default='IT2a')
    ap.add_argument('--budget-seconds',type=float,default=1200)
    ap.add_argument('--self-test',action='store_true')
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    assert args.budget_seconds >= 0
    raw = {k:getattr(args,k).read_bytes() for k in
           ['source','observer','model_spec','target','domains']}
    data = {k:json.loads(v) for k,v in raw.items()}
    assert sha(raw['source']) == data['model_spec']['source_sha256']
    assert sha(raw['observer']) in [r['sha256'] for r in data['source']['source_receipts']]
    records = audit_source(data['source'],data['observer'],data['model_spec'])[args.case_index]
    receipt = data['domains']
    assert receipt['panel'] == args.panel
    for k in ['source','observer','model_spec','target']:
        assert receipt[k+'_sha256'] == sha(raw[k])
    case = receipt['cases'][args.case_index]
    assert case['case_index'] == args.case_index and case['partition'] == CASES[args.case_index]
    assert case['compiled_record_sha256'] == record_digest(records)
    result = solve(records,data['target']['panels'][args.panel],case['domains'],
                   started+args.budget_seconds)
    result.update(schema='GDT901_INDEPENDENT_COUNT_HEAD_RELAXATION_V1',
                  case_index=args.case_index,partition=CASES[args.case_index],panel=args.panel,
                  budget_seconds=args.budget_seconds,elapsed_total_seconds=time.monotonic()-started,
                  solver_version=z3.get_version_string(),solver_threads=1,
                  code_sha256=sha(Path(__file__).read_bytes()),
                  compiled_record_sha256=record_digest(records),
                  bindings={k+'_sha256':sha(v) for k,v in raw.items()},
                  ignored_constraints=['full projected word order','shared semantic roots and role prefixes/suffixes'],
                  interpretation='UNSAT excludes the full case; SAT only supplies a count/head relaxation assignment.')
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'case_index':args.case_index,'status':result['status'],
                      'elapsed_total_seconds':result['elapsed_total_seconds']}))


if __name__ == '__main__':
    main()
