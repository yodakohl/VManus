#!/usr/bin/env python3
"""Independent complete observed-key enumeration for the fixed GDT905 model.

The primary CSP is never imported. Frozen GDT905 independent channel/CFG
helpers are reused; local word tables are rebuilt, pruned by a separate
array-based consistency pass, then exhausted with a finite Z3 model.
"""
import argparse
import collections
import csv
import gzip
import io
import hashlib
import heapq
import importlib.util
import itertools
import json
import pickle
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
import time

import numpy as np
import z3

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
OLD = ROOT/'experiments/yolo/gdt905_joint_cv_complete_passage_candidates'
BASE = ROOT/'experiments/yolo/gdt892_joint_abugida_paradigm_reconstruction'
ALPHABET = 'acdefghiklmnopqrstxy'
VOWELS = 'aeiouy'
_TABLE_CACHE = collections.OrderedDict()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def logical_json(path):
    path = Path(path)
    data = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())
    return json.loads(data),hashlib.sha256(data).hexdigest()


def helpers():
    path = OLD/'src/validate_independent.py'
    specification = importlib.util.spec_from_file_location('gdt905_independent_helpers',path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def component_inventory(vowel):
    # A private deterministic integer labeling; comparison uses component names.
    return tuple(sorted({'C:'+c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in VOWELS} | {'V:'+v for v in VOWELS if v != vowel} | {'CARRIER','VIRAMA'}))


def build_tables(words,mask,vowel,index,helper):
    singles = {c for j,c in enumerate(ALPHABET) if mask & (1 << j)}
    unique_words = sorted(set(words))
    segments = [helper.split_word(w,singles) for w in unique_words]
    assert all(x is not None for x in segments)
    codes = sorted(set(itertools.chain.from_iterable(segments)))
    assert helper.code_capacity(singles,ALPHABET,codes)
    ids = {c:i for i,c in enumerate(codes)}
    components = component_inventory(vowel)
    values = {c:i for i,c in enumerate(components)}
    tables = []
    for word,units in zip(unique_words,segments):
        columns = sorted(set(units))
        first = [units.index(c) for c in columns]
        cache_key = (vowel,helper.signature(units),tuple(first))
        cached = _TABLE_CACHE.get(cache_key)
        array = None if cached is None else cached[0]
        if array is None:
            rows = set()
            for form_index,parts in index[helper.signature(units)]:
                row = tuple(values[parts[j]] for j in first)
                assert len(set(row)) == len(row)
                rows.add(row)
            array = np.asarray(sorted(rows),dtype=np.int16).reshape((-1,len(columns)))
            array.flags.writeable = False
            supports = tuple(sum(1<<int(v) for v in np.unique(array[:,col])) for col in range(len(columns)))
            _TABLE_CACHE[cache_key] = (array,supports)
            if len(_TABLE_CACHE)>8192:
                _TABLE_CACHE.popitem(last=False)
        else:
            _TABLE_CACHE.move_to_end(cache_key)
        tables.append({'vars':tuple(ids[c] for c in columns),'rows':array,'supports':_TABLE_CACHE[cache_key][1]})
    return codes,components,tables


def reduce_tables(tables,nvars,nvalues):
    """Sound generalized arc consistency plus global singleton injection.
    This is independent array filtering, with no primary bitset domains/queues.
    """
    support_domains = [(1<<nvalues)-1 for _ in range(nvars)]
    for table in tables:
        supports = table.get('supports')
        if supports is None:
            supports = tuple(sum(1<<int(v) for v in np.unique(np.asarray(table['rows'],dtype=np.int16).reshape((-1,len(table['vars'])))[:,col])) for col in range(len(table['vars'])))
        for var,support in zip(table['vars'],supports):
            support_domains[var] &= support
            if not support_domains[var]:
                return None,{'proof':'EMPTY_INITIAL_SUPPORT_INTERSECTION','rounds':0}
    domains = [{v for v in range(nvalues) if bits&(1<<v)} for bits in support_domains]
    current = [{'vars':tuple(t['vars']),'rows':np.array(t['rows'],dtype=np.int16,copy=True).reshape((-1,len(t['vars'])))} for t in tables]
    rounds = 0
    if nvars > nvalues:
        return None,{'proof':'MORE_VARIABLES_THAN_COMPONENTS','rounds':0}
    changed = True
    while changed:
        changed = False
        rounds += 1
        singleton_values = [next(iter(d)) for d in domains if len(d)==1]
        if len(set(singleton_values)) != len(singleton_values):
            return None,{'proof':'DUPLICATE_FORCED_COMPONENT','rounds':rounds}
        used = set(singleton_values)
        for i,d in enumerate(domains):
            new = d-used if len(d)>1 else d
            if not new:
                return None,{'proof':'EMPTY_VARIABLE_DOMAIN','rounds':rounds}
            if new != d:
                domains[i] = new
                changed = True
        for table in current:
            rows = table['rows']
            if not len(rows):
                return None,{'proof':'EMPTY_WORD_TABLE','rounds':rounds}
            keep = np.ones(len(rows),dtype=bool)
            for col,var in enumerate(table['vars']):
                keep &= np.isin(rows[:,col],list(domains[var]))
            if not keep.all():
                rows = rows[keep]
                table['rows'] = rows
                changed = True
            if not len(rows):
                return None,{'proof':'EMPTY_WORD_TABLE','rounds':rounds}
            for col,var in enumerate(table['vars']):
                narrowed = domains[var] & set(rows[:,col].tolist())
                if not narrowed:
                    return None,{'proof':'EMPTY_VARIABLE_DOMAIN','rounds':rounds}
                if narrowed != domains[var]:
                    domains[var] = narrowed
                    changed = True
    return (domains,current),{'proof':'CONSISTENT_REQUIRES_EXHAUSTIVE_SOLVER','rounds':rounds,'retained_rows':sum(len(t['rows']) for t in current)}


def relation_formula(variables,rows):
    """Factored exact table formula, not a language objective or relaxation."""
    if not variables:
        return z3.BoolVal(bool(rows))
    if not rows:
        return z3.BoolVal(False)
    order = sorted(range(len(variables)),key=lambda i:(len({r[i] for r in rows}),i))
    reordered = sorted(set(tuple(r[i] for i in order) for r in rows))
    vars_ordered = [variables[i] for i in order]
    def trie(level,choices):
        if level == len(vars_ordered):
            return z3.BoolVal(True)
        grouped = collections.defaultdict(list)
        for row in choices:
            grouped[row[level]].append(row)
        return z3.Or([z3.And(vars_ordered[level]==value,trie(level+1,subrows)) for value,subrows in sorted(grouped.items())])
    return trie(0,reordered)


def enumerate_tables(tables,nvars,nvalues):
    reduced,stats = reduce_tables(tables,nvars,nvalues)
    if reduced is None:
        return [],stats
    domains,relations = reduced
    variables = [z3.Int('component_'+str(i)) for i in range(nvars)]
    solver = z3.Solver()
    solver.set(random_seed=0)
    solver.add(z3.Distinct(variables))
    for var,domain in zip(variables,domains):
        solver.add(z3.Or([var==v for v in sorted(domain)]))
    for table in relations:
        solver.add(relation_formula([variables[i] for i in table['vars']],table['rows'].tolist()))
    answers = []
    while True:
        status = solver.check()
        if status == z3.unsat:
            break
        if status != z3.sat:
            raise RuntimeError('Independent finite solver returned UNKNOWN: '+solver.reason_unknown())
        model = solver.model()
        values = tuple(model.eval(v).as_long() for v in variables)
        answers.append(values)
        # Block the ENTIRE observed key, including variables absent from any
        # particular word; never block only plaintext or a partial assignment.
        solver.add(z3.Or([v!=x for v,x in zip(variables,values)]))
    assert len(answers) == len(set(answers))
    return sorted(answers),dict(stats,proof='COMPLETE_Z3_ENUMERATION_TO_UNSAT',solutions=len(answers))


def decode_key(words,mask,vowel,observed,reference,helper):
    singles = {c for j,c in enumerate(ALPHABET) if mask & (1 << j)}
    # Read component syllables independently with explicit vowel/virama rules.
    plaintext = []
    for word in words:
        units = helper.split_word(word,singles)
        parts = [observed[u] for u in units]
        letters = []
        cursor = 0
        while cursor < len(parts):
            head = parts[cursor]
            cursor += 1
            assert head == 'CARRIER' or head.startswith('C:')
            consonant = '' if head == 'CARRIER' else head[2:]
            vocalic = vowel
            if cursor < len(parts) and parts[cursor].startswith('V:'):
                vocalic = parts[cursor][2:]
                cursor += 1
            elif cursor < len(parts) and parts[cursor]=='VIRAMA':
                assert consonant
                vocalic = ''
                cursor += 1
            letters.append(consonant+vocalic)
        plain = ''.join(letters)
        assert helper.components(plain,vowel) == tuple(parts)
        assert plain in reference['analyses']
        plaintext.append(plain)
    accepted = helper.grammar_accepts(reference['grammar'],[reference['analyses'][p] for p in plaintext])
    return {'observed_key':observed,'plaintext':plaintext,'grammar_accepted':accepted}


def synthetic_tests():
    cases = 0
    # Exhaust every relation subset for two overlapping2-column tables over
    # three values. Independent brute-force full injections are the oracle.
    rows = list(itertools.permutations(range(3),2))
    for leftmask in range(64):
        left = [r for i,r in enumerate(rows) if leftmask & (1 << i)]
        for rightmask in range(64):
            right = [r for i,r in enumerate(rows) if rightmask & (1 << i)]
            tables = [{'vars':(0,1),'rows':left},{'vars':(1,2),'rows':right}]
            expected = sorted(v for v in itertools.permutations(range(3)) if v[:2] in left and v[1:] in right)
            actual,_ = enumerate_tables(tables,3,3)
            assert actual == expected
            cases += 1
    return {'overlapping_table_pairs':cases,'oracle':'all full injective assignments','passes':True}


def validate_plan(plan_path):
    helper = helpers()
    prior_validation = json.loads((OLD/'artifacts/INDEPENDENT_VALIDATION.json').read_text())
    assert prior_validation['status'] == 'PASS'
    assert sha(OLD/'src/validate_independent.py') == prior_validation['validator_sha256']
    target_path = OLD/'artifacts/TARGET.json'
    scans_path = OLD/'artifacts/SCANS.json'
    assert sha(target_path) == prior_validation['target_sha256']
    assert sha(scans_path) == prior_validation['scans_sha256']
    target = json.loads(target_path.read_text())
    scans = json.loads(scans_path.read_text())
    fixed = {(ed,r['paragraph_id']):r for ed,rows in target['panels'].items() for r in rows if 12<=len(r['words'])<=24}
    scan_by_key = {(r['edition'],r['paragraph_id']):r for r in scans}
    plan,plan_hash = logical_json(plan_path)
    assert plan['schema_version'] == 1
    assert len(plan['paragraphs']) == len(fixed) == 49
    assert {(p['edition'],p['paragraph_id']) for p in plan['paragraphs']} == set(fixed)
    tasks = []
    summaries = []
    for p in plan['paragraphs']:
        key = (p['edition'],p['paragraph_id'])
        assert p['raw_words'] == fixed[key]['words']
        assert p['words'] == sorted(set(p['raw_words']))
        scan = scan_by_key[key]
        raw = gzip.decompress((OLD/scan['masks_path']).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == scan['uncompressed_sha256']
        masks = {int(x['mask']):int(x['inherent_bits']) for x in csv.DictReader(io.StringIO(raw.decode()))}
        assert len(masks) == scan['surviving_masks']
        covered = set()
        distinct_groups = set()
        group_ids = set()
        for group in p['groups']:
            equivalent = group['equivalent_masks']
            assert equivalent == sorted(set(equivalent)) and equivalent
            assert group['mask'] == min(equivalent)
            assert group['group_id'] not in group_ids
            group_ids.add(group['group_id'])
            segments = tuple(tuple(x) for x in group['segments'])
            assert len(segments) == len(p['words'])
            assert [''.join(x) for x in segments] == p['words']
            singles = {c for i,c in enumerate(ALPHABET) if group['mask'] & (1 << i)}
            assert tuple(helper.split_word(w,singles) for w in p['words']) == segments
            ones = {c for segment in segments for c in segment if len(c)==1}
            zeros = {c[0] for segment in segments for c in segment if len(c)==2}
            assert not ones & zeros
            onemask = sum(1 << ALPHABET.index(c) for c in ones)
            zeromask = sum(1 << ALPHABET.index(c) for c in zeros)
            assert helper.code_capacity(singles,ALPHABET,itertools.chain.from_iterable(segments))
            identity = (segments,group['inherent_bits'])
            assert identity not in distinct_groups
            distinct_groups.add(identity)
            for mask in equivalent:
                assert mask not in covered and mask in masks
                assert masks[mask] == group['inherent_bits']
                assert mask & onemask == onemask and mask & zeromask == 0
                covered.add(mask)
            for i,vowel in enumerate(VOWELS):
                if group['inherent_bits'] & (1 << i):
                    case_id = p['edition']+'_'+p['paragraph_id']+'_'+str(group['mask'])+'_'+vowel
                    tasks.append({'case_id':case_id,'edition':key[0],'paragraph_id':key[1],'mask':group['mask'],'inherent':vowel,'raw_words':p['raw_words'],'segments':group['segments']})
        assert covered == set(masks)
        summaries.append({'edition':key[0],'paragraph_id':key[1],'masks':len(masks),'exact_segmentation_groups':len(distinct_groups),'all_masks_partitioned_once':True})
    assert len({t['case_id'] for t in tasks}) == len(tasks)
    return plan_hash,tasks,{'status':'PASS','plan_logical_sha256':plan_hash,'target_sha256':sha(target_path),'scans_sha256':sha(scans_path),'paragraphs':summaries,'complete_case_count':len(tasks),'reason':'Every original mask/vowel bit occurs once in an exact-segmentation class; per-unit-start constraints independently prove all equivalent masks induce the representative segmentation.'}


_STATE = {}


def prepare_validation(cache_dir,primary_work,independent_work,plan_hash):
    helper = helpers()
    helper.CACHE = cache_dir
    reference,meta = helper.load_reference()
    indexes = {}
    for vowel in VOWELS:
        path = cache_dir/('patterns_'+vowel+'.pkl')
        assert sha(path) == meta['cache_files'][path.name]['sha256']
        with path.open('rb') as stream:
            indexes[vowel] = pickle.load(stream)
    previous,_ = logical_json(OLD/'artifacts/CANDIDATES.json')
    reuse = {}
    for paragraph in previous:
        for case in paragraph['cases']:
            if case['status']=='COMPLETE':
                cid = paragraph['edition']+'_'+paragraph['paragraph_id']+'_'+str(case['mask'])+'_'+case['inherent']
                assert cid not in reuse
                reuse[cid] = case
    _STATE.update(validator_hash=sha(Path(__file__)),helper=helper,reference=reference,indexes=indexes,reuse=reuse,primary_work=primary_work,independent_work=independent_work,plan_hash=plan_hash)


def check_case(task):
    began = time.monotonic()
    path = _STATE['primary_work']/'cases'/(task['case_id']+'.json')
    receipt = json.loads(path.read_text())
    for field in ('case_id','edition','paragraph_id','mask','inherent'):
        assert receipt[field] == task[field]
    assert receipt['status'] == 'COMPLETE'
    vowel = task['inherent']
    codes,components,tables = build_tables(task['raw_words'],task['mask'],vowel,_STATE['indexes'][vowel],_STATE['helper'])
    expected,proof = enumerate_tables(tables,len(codes),27)
    primary_components = tuple(['C:'+c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in VOWELS]+['V:'+v for v in VOWELS if v!=vowel]+['CARRIER','VIRAMA'])
    primary_ids = {c:i for i,c in enumerate(primary_components)}
    found = {}
    for assignment in expected:
        observed = {c:components[i] for c,i in zip(codes,assignment)}
        key = tuple(primary_ids[observed[c]] for c in codes)
        assert key not in found
        decoded = decode_key(task['raw_words'],task['mask'],vowel,observed,_STATE['reference'],_STATE['helper'])
        found[key] = decoded['grammar_accepted']
    primary = {}
    assert len(receipt['values']) == len(receipt['grammar_accepted'])
    for assignment,accepted in zip(receipt['values'],receipt['grammar_accepted']):
        key = tuple(assignment)
        assert len(key)==len(codes) and len(set(key))==len(key)
        assert all(type(v) is int and 0<=v<27 for v in key)
        assert type(accepted) is bool and key not in primary
        primary[key] = accepted
    assert primary == found, (task['case_id'],len(primary),len(found))
    assert receipt['stats']['complete_assignments'] == len(found)
    if receipt['origin']=='GDT905_REUSED':
        old = _STATE['reuse'][task['case_id']]
        assert old['status']=='COMPLETE' and old['stats']['complete_assignments']==len(found)
        assert old['stats']['callback_calls']==len(found)
        assert old['stats']['solutions_accepted']==sum(found.values())
    else:
        assert receipt['origin']=='GDT906_ENUMERATED'
    answer = {'schema_version':1,'case_id':task['case_id'],'status':'COMPLETE','validator_sha256':_STATE['validator_hash'],'primary_origin':receipt['origin'],'primary_receipt_sha256':sha(path),'plan_logical_sha256':_STATE['plan_hash'],'values':[list(k) for k in sorted(found)],'grammar_accepted':[found[k] for k in sorted(found)],'proof':proof,'observed_codewords':codes,'seconds':time.monotonic()-began}
    out = _STATE['independent_work']/'cases'/(task['case_id']+'.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    temp = out.with_suffix('.partial')
    temp.write_text(json.dumps(answer,sort_keys=True,separators=(',',':'))+'\n')
    temp.replace(out)
    return {'case_id':task['case_id'],'keys':len(found),'accepted':sum(found.values()),'proof':proof['proof']}


def validate_existing(independent_work,primary_work,task_by_id,plan_hash):
    complete = set()
    folder = independent_work/'cases'
    if not folder.exists():
        return complete
    for path in folder.glob('*.json'):
        record = json.loads(path.read_text())
        cid = record['case_id']
        assert cid in task_by_id and path.stem==cid
        assert record['status']=='COMPLETE' and record['plan_logical_sha256']==plan_hash
        assert record['validator_sha256']==sha(Path(__file__))
        assert record['primary_receipt_sha256']==sha(primary_work/'cases'/(cid+'.json'))
        complete.add(cid)
    return complete


def run_cases(args,plan_hash,tasks):
    assert args.cache_dir and args.primary_work_dir and args.work_dir
    assert 1<=args.workers<=32
    prepare_validation(args.cache_dir,args.primary_work_dir,args.work_dir,plan_hash)
    task_by_id = {t['case_id']:t for t in tasks}
    complete = validate_existing(args.work_dir,args.primary_work_dir,task_by_id,plan_hash)
    todo = [(0.0,j,t) for j,t in enumerate(tasks) if t['case_id'] not in complete]
    heapq.heapify(todo)
    failures = []
    pending = {}
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=mp.get_context('fork')) as executor:
        while todo or pending:
            now = time.monotonic()
            checks = 0
            while todo and todo[0][0]<=now and len(pending)<args.workers*2 and checks<4096:
                _,sequence,task = heapq.heappop(todo)
                checks += 1
                if (args.primary_work_dir/'cases'/(task['case_id']+'.json')).exists():
                    pending[executor.submit(check_case,task)] = task['case_id']
                elif args.watch:
                    heapq.heappush(todo,(now+10,sequence,task))
            if not pending:
                if todo and todo[0][0]<=time.monotonic():
                    continue
                if not args.watch or not todo:
                    break
                time.sleep(min(2,max(0.01,todo[0][0]-time.monotonic())))
                continue
            done,_ = wait(pending,timeout=2,return_when=FIRST_COMPLETED)
            for future in done:
                cid = pending.pop(future)
                try:
                    detail = future.result()
                except Exception as error:
                    failures.append({'case_id':cid,'error':repr(error)})
                    raise
                complete.add(cid)
                if detail['keys'] or len(complete)%100==0:
                    print(json.dumps({'validated_cases':len(complete),'total_cases':len(tasks),**detail}),flush=True)
    result = {'schema_version':1,'status':'PASS_COMPLETE' if len(complete)==len(tasks) else 'PARTIAL','plan_logical_sha256':plan_hash,'validator_sha256':sha(Path(__file__)),'expected_cases':len(tasks),'independently_complete_cases':len(complete),'pending_cases':len(tasks)-len(complete),'failures':failures,'claim_ceiling':'Exact observed lexical-key sets and independent fullCFG decisions compared for every completed receipt. A partial validator run does not certify full search exhaustion.'}
    (EXP/'artifacts/INDEPENDENT_COMPLETE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--cache-dir',type=Path)
    parser.add_argument('--plan',type=Path,default=EXP/'artifacts/PLAN.json')
    parser.add_argument('--check-plan',action='store_true')
    parser.add_argument('--primary-work-dir',type=Path)
    parser.add_argument('--work-dir',type=Path)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--watch',action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(synthetic_tests()))
        return
    if args.check_plan:
        plan_hash,tasks,result = validate_plan(args.plan)
        (EXP/'artifacts/INDEPENDENT_PLAN_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':'PASS','cases':len(tasks),'plan_hash':plan_hash}))
        return
    plan_hash,tasks,result = validate_plan(args.plan)
    run_cases(args,plan_hash,tasks)


if __name__ == '__main__':
    main()
