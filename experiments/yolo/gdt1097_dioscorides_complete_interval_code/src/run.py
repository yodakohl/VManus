#!/usr/bin/env python3
"""One frozen run over every remaining literal I.1 candidate."""
import collections
import concurrent.futures
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
PARENT = ROOT/'experiments/yolo/gdt963_dioscorides_complete_content_code'
DOMAINS = ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains'


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def save(name, value):
    data = (json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
    (E/'artifacts'/name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)


def selected_inputs():
    source = read(PARENT/'src/SOURCE.json')
    atoms = next(r['atoms'] for r in source['records'] if r['id'] == 'I.1')
    targets = {r['id']:r for r in read(PARENT/'artifacts/TARGET_FRAMES.json.gz')}
    rows = read(DOMAINS/'artifacts/CASES.json')
    certs = read(DOMAINS/'artifacts/CERTIFICATES.json.gz')
    selected = [i for i,r in enumerate(rows) if r['edition']=='IT2a' and r['record']=='I.1'
                and r['status']=='NECESSARY_DOMAINS_NONEMPTY']
    jobs = []
    for i in selected:
        row = rows[i]
        frame = targets[row['target_id']]
        assert frame['eligible'] and not frame['page'].startswith('f84') and frame['page']!='f116v'
        assert len(atoms)==265 and len(frame['text'])==row['target_characters']
        domains = certs[str(i)]['final_domains']
        assert set(domains)=={a for a,c in collections.Counter(atoms).items() if c>1}
        jobs.append(dict(index=i, atoms=atoms, text=frame['text'], domains=domains))
    return rows, jobs


def isolated(job, spec, deadline):
    started = time.monotonic()
    remaining = deadline - started
    if remaining<=0:
        return dict(status='UNKNOWN_RUN_WALL_LIMIT')
    args = {k:job[k] for k in ('atoms','text','domains')}
    args.update(seconds=spec['solver_seconds'],workers=spec['solver_workers'])
    try:
        proc = subprocess.run([sys.executable,str(Path(__file__).resolve()),'--case'],
                              input=json.dumps(args),text=True,capture_output=True,
                              timeout=min(spec['case_wall_seconds'],remaining))
        if proc.returncode:
            result = dict(status='ERROR_PROCESS',returncode=proc.returncode,
                          stderr_sha256=hashlib.sha256(proc.stderr.encode()).hexdigest())
        else:
            result = json.loads(proc.stdout)
    except subprocess.TimeoutExpired:
        result = dict(status='UNKNOWN_CASE_WALL_LIMIT' if remaining>=spec['case_wall_seconds']
                      else 'UNKNOWN_RUN_WALL_LIMIT')
    result['process_wall_seconds'] = time.monotonic()-started
    return result


def main():
    import ortools
    lock = read(E/'src/PREREG_LOCK.json')
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    spec = read(E/'src/SPEC.json')
    assert ortools.__version__==spec['ortools_version']
    assert not (E/'artifacts/RESULT.json').exists(), 'No automatic repeated target run'
    rows, jobs = selected_inputs()
    assert [j['index'] for j in jobs]==spec['all_selected_case_indices']
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=spec['processes']) as pool:
        futures = {pool.submit(isolated,job,spec,started+spec['run_wall_seconds']):job['index'] for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            results[str(i)] = future.result()
            print(json.dumps(dict(index=i,page=rows[i]['page'],status=results[str(i)]['status'])),flush=True)
    fullrows = []
    for i, row in enumerate(rows):
        new = dict(index=i,**row)
        new['parent_domain_status'] = new.pop('status')
        new['status'] = results[str(i)]['status'] if str(i) in results else 'INHERITED_NOT_RETESTED'
        fullrows.append(new)
    save('SOLVER_RESULTS.json.gz',results)
    save('ALL_CASES.json.gz',fullrows)
    header = ['index','edition','page','record','parent_domain_status','status','source_atoms','target_characters']
    (E/'artifacts/CANDIDATES.tsv').write_text('\t'.join(header)+'\n'+'\n'.join(
        '\t'.join(str(r[k]) for k in header) for r in fullrows)+'\n')
    counts = collections.Counter(r['status'] for r in results.values())
    all_unsat = counts['INFEASIBLE']==len(jobs)
    sat = counts['OPTIMAL']+counts['FEASIBLE']
    result = dict(status='ALL_SEVEN_LOCAL_EQUATIONS_SOLVER_INFEASIBLE' if all_unsat else
                  'COMPLETE_LOCAL_CANDIDATES_FOUND' if sat else 'COMPLETE_LOCAL_EQUATIONS_UNRESOLVED',
                  original_cases=len(rows),newly_tested=len(jobs),statuses=counts,
                  full_local_witnesses=sat,full_four_record_witnesses=0,
                  solver_infeasible_not_independent_certificate=all_unsat,
                  it_literal_conjunction='SOLVER_INFEASIBLE' if all_unsat else 'UNRESOLVED',
                  source_unknown_cases_inherited=sum(r['status']=='INHERITED_UNKNOWN_SOURCE' for r in rows),
                  independent_confirmation_leaves=0,confirmed_words=0,significance_claim=False,
                  source_atoms_changed=0,decoder_rules_changed=0,wall_seconds=time.monotonic()-started)
    save('RESULT.json',result)
    save('EXECUTION_RECEIPT.json',dict(started_utc=utc,finished_utc=datetime.now(timezone.utc).isoformat(),
         registration_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         lock_sha256=hashlib.sha256((E/'src/PREREG_LOCK.json').read_bytes()).hexdigest(),
         ortools_version=ortools.__version__,maximum_solver_workers=spec['processes']*spec['solver_workers'],target_runs=1))
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    if '--case' in sys.argv:
        from model import solve
        print(json.dumps(solve(**json.load(sys.stdin)),ensure_ascii=False))
    else:
        main()
