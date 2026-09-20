#!/usr/bin/env python3
"""Run every fixed complete-paragraph case; never revise source or writing rules."""
import argparse
import concurrent.futures
import csv
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from model import solve, witness

E=Path(__file__).resolve().parents[1]
R=E.parents[2]
A=E/'artifacts'
PARENT=R/'experiments/yolo/gdt967_balneis_joint_body_term_incidence/artifacts'


def read(path): return json.loads(path.read_text())
def put(name,value): (A/name).write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')


def lockcheck():
    for name,digest in read(E/'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name


def isolated(job):
    started=time.monotonic()
    try:
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--solve-json'],
            input=json.dumps(job),text=True,capture_output=True,timeout=90)
        if result.returncode:
            return {'status':'ERROR_WORKER','exit_code':result.returncode,'elapsed_seconds':time.monotonic()-started}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {'status':'UNKNOWN_WALL_CEILING','elapsed_seconds':time.monotonic()-started}
    except Exception as exc:
        return {'status':'ERROR_WORKER_PROTOCOL','error_type':type(exc).__name__,'elapsed_seconds':time.monotonic()-started}


def fixtures():
    source=read(E/'src/SOURCE.json')
    code={a:chr(97+i//26)+chr(97+i%26) for i,a in enumerate(sorted(source['arities']))}
    results=[]
    for order,stream in source['streams'].items():
        atoms=stream['atoms'];values=[code[a] for a in atoms]
        words=[''.join(values[i:i+2]) for i in range(0,len(values),2)]
        good=solve(dict(atoms=atoms,words=words,pinned_code=code,seconds=2,projections=False))
        results.append(dict(order=order,case='known_complete_code',status=good['status'],expected='SAT'))
        broken=[words[0][:1],words[0][1:],*words[1:]]
        bad=solve(dict(atoms=atoms,words=broken,pinned_code=code,seconds=2,projections=False))
        results.append(dict(order=order,case='seam_inside_known_atom',status=bad['status'],expected='UNSAT_SOLVER'))
        assert good['status']=='SAT' and bad['status']=='UNSAT_SOLVER'
        assert witness(atoms,words,code)['valid'] and not witness(atoms,broken,code)['valid']
        empty=dict(code);empty[atoms[0]]=''
        assert not witness(atoms,words,empty)['valid']
        colliding=dict(code);colliding[atoms[0]]=code[atoms[1]]
        assert not witness(atoms,words,colliding)['valid']
        different=list(words);different[-1]+='z'
        assert not witness(atoms,different,code)['valid']
    result=dict(status='PASS',scope='Source-only pinned full-code interface and ground negatives, not semantic or full-search control',cases=results)
    put('PRE_RUN_FIXTURES.json',result)
    print(json.dumps(result,indent=2))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fixtures',action='store_true');parser.add_argument('--solve-json',action='store_true')
    args=parser.parse_args()
    if args.solve_json:
        print(json.dumps(solve(json.load(sys.stdin)),ensure_ascii=False,separators=(',',':')));return
    if args.fixtures:
        fixtures();return
    lockcheck()
    started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    source=read(E/'src/SOURCE.json');target=read(PARENT/'TARGET.json');scope=read(PARENT/'SCOPE.json')
    cases=[];pending=[]
    for ed,panel in scope.items():
        eligible={p['id']:p for p in target[ed]}
        for p in panel['rows']:
            assert not p['page'].startswith('f84')
            for order,stream in source['streams'].items():
                case=dict(edition=ed,paragraph=p['id'],page=p['page'],leaf=p['leaf'],writer=order,
                          target_groups=p['groups'],independent_confirmation_capacity=0)
                if not p['literal']:
                    case.update(status='UNKNOWN_SOURCE',ineligible_lines=p['ineligible_lines'])
                else:
                    row=eligible[p['id']]
                    assert row['page']==p['page'] and len(row['words'])==p['groups']
                    case.update(words=row['words'],loci=row['loci'],source_ids=row['source_ids'])
                    pending.append((len(cases),dict(atoms=stream['atoms'],words=row['words'],seconds=30,projections=True)))
                cases.append(case)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        work={pool.submit(isolated,job):index for index,job in pending}
        done=0
        for future in concurrent.futures.as_completed(work):
            index=work[future];cases[index].update(future.result());done+=1
            if done%8==0 or done==len(work):
                print(json.dumps({'completed':done,'of':len(work),'latest_status':cases[index]['status']}),flush=True)
    put('CASES.json',cases)
    put('SCOPE.json',scope)
    result=dict(question='Whole complete Anastasia semantic tree code',source_lines=12,source_assertions=9,
                source_atom_occurrences=111,source_atom_types=47,panels={},confirmed_words=0,
                independent_confirmation_capacity=0,significance_claim=False)
    for ed,panel in scope.items():
        result['panels'][ed]={}
        for order in source['streams']:
            rows=[c for c in cases if c['edition']==ed and c['writer']==order]
            counts={s:sum(c['status']==s for c in rows) for s in sorted({c['status'] for c in rows})}
            literal=[c for c in rows if c['status']!='UNKNOWN_SOURCE']
            sat=sum(c['status']=='SAT' for c in literal)
            unresolved=sum(c['status'].startswith(('UNKNOWN','ERROR')) for c in literal)
            if not rows:decision='NO_COMPLETE_PARAGRAPH_CAPACITY'
            elif sat:decision='COMPLETE_CONDITIONAL_WITNESSES'
            elif unresolved:decision='BOUNDED_LITERAL_SEARCH_UNRESOLVED'
            elif literal:decision='NO_LITERAL_FIT_SOURCE_UNCERTAINTY_RETAINED'
            else:decision='NO_LITERAL_CAPACITY'
            result['panels'][ed][order]=dict(status=decision,complete_paragraphs=len(rows),case_status_counts=counts,
                full_witnesses=sat,computational_unknown_or_errors=unresolved)
    put('RESULT.json',result)
    put('EXECUTION_RECEIPT.json',dict(started_utc=utc,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                   wall_seconds=time.monotonic()-started,workers=16,source_case_count=len(cases),solver_job_count=len(pending)))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n')
        w.writerow(['edition','paragraph','page','leaf','writer','predicted_source_atoms','target_groups','target_characters','status','prefix_length_bound','singleton_character_share','independent_confirmation_capacity'])
        for c in cases:
            z=c.get('necessary',{})
            w.writerow([c['edition'],c['paragraph'],c['page'],c['leaf'],c['writer'],111,c['target_groups'],z.get('target_characters',''),c['status'],z.get('prefix_length_lower_bound',''),c.get('witness',{}).get('singleton_character_share',''),0])
    lines=['# Complete conditional witness alignments','','All meanings are source/tree hypotheses, not confirmed Voynich values.']
    for c in cases:
        if c['status']!='SAT':continue
        lines += ['',f"## {c['edition']} {c['paragraph']} {c['writer']}",'',f"Whole target: `{' '.join(c['words'])}`",'','| Word index | Complete word | Ordered source atoms |','|---|---|---|']
        for i,word in enumerate(c['words']):
            parts=[x['atom'] for x in c['witness']['alignment'] if x['word_index']==i]
            lines.append(f"|{i}|{word}|{' + '.join(parts)}|")
        lines += ['','Complete source statements:']+[f"- {x['id']}: {x['provisional_gloss']}" for x in source['clauses']]
    if not any(c['status']=='SAT' for c in cases):lines += ['','No complete code witness was obtained; see every case and all unknowns in CANDIDATES.tsv.']
    (A/'COMPLETE_CANDIDATE_READINGS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
