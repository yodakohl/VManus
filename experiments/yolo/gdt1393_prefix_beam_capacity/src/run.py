"""Frozen source-only prefix beams; comparison with truth is a separate stage."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import time
import numpy as np
E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E/'artifacts'
OLD = ROOT/'experiments/yolo/gdt1390_modular_cumulative_blind_control/artifacts'
RANK = ROOT/'research_registry/proposals/production_origin_supply_20261003/C1064_PREFIX_RANK_RESULT_20261016.json'
WIDTH, DEPTH = 65536, 10

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_text())

def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')

def rel(path):
    return str(path.relative_to(ROOT))

def check_lock():
    path = E/'CODE_LOCK.json'
    lock = read(path)
    assert lock['locked_utc']
    entries = {x['path']: x['sha256'] for x in lock['files']}
    required = [E/'src/run.py', E/'src/validate.py', E/'PREREGISTRATION.md', E/'METHOD.md', OLD/'MODELS.json', OLD/'CASES.json', RANK]
    for p in required:
        assert rel(p) in entries and sha(p) == entries[rel(p)], rel(p)
    # Only the declared code/model/control-coefficient files may be accessed.
    # In particular never iterate arbitrary lock entries that might include truth.
    manifest = read(OLD/'MODELS.json')
    for entry in manifest['models']:
        p = ROOT/entry['path']
        assert entry['path'] in entries and sha(p) == entries[entry['path']] == entry['sha256']
    return path, manifest

def choose(codes, scores, width):
    """Top score then smallest fixed-length base27 prefix, including boundary ties."""
    assert len(codes) == len(scores) and np.isfinite(scores).all()
    if len(codes) <= width:
        indices = np.arange(len(codes))
    else:
        threshold = np.partition(scores, len(scores)-width)[len(scores)-width]
        higher = np.flatnonzero(scores > threshold)
        tied = np.flatnonzero(scores == threshold)
        need = width-len(higher)
        assert 0 < need <= len(tied)
        if need < len(tied):
            tied = tied[np.argpartition(codes[tied], need-1)[:need]]
        indices = np.concatenate((higher, tied))
    indices = indices[np.lexsort((codes[indices], -scores[indices]))]
    return np.ascontiguousarray(codes[indices], dtype='<i8'), np.ascontiguousarray(scores[indices], dtype='<f8')

def beam(table, width=WIDTH, depth=DEPTH):
    assert table.shape == (20440,27) and np.isfinite(table).all()
    codes, scores = np.array([0], dtype=np.int64), np.array([0.0], dtype=np.float64)
    steps = []
    for t in range(depth):
        if t == 0:
            context = np.zeros(len(codes), dtype=np.int64)
        elif t == 1:
            context = 1+codes%27
        elif t == 2:
            context = 28+codes%729
        else:
            context = 757+codes%19683
        children = (codes[:,None]*27+np.arange(27, dtype=np.int64)).reshape(-1)
        values = (scores[:,None]+table[context,:]).reshape(-1)
        codes, scores = choose(children, values, width)
        steps.append(dict(depth=t+1, count=len(codes), codes_rank_order_sha256=hashlib.sha256(codes.tobytes()).hexdigest(),
                          score_min=float(scores.min()), score_max=float(scores.max()), score_mean=float(scores.mean())))
    return codes, scores, steps

def generate(out):
    lockpath, manifest = check_lock()
    assert not (A/'BEAMS.json').exists() and not (A/'BEAMS_SEAL.json').exists()
    rank = read(RANK)
    assert len(rank['cases']) == 18
    assert rank['hashes'][rel(OLD/'CASES.json')] == sha(OLD/'CASES.json')
    assert all(c['snapshots']['10']['fully_free']==10 and c['snapshots']['10']['fully_determined']==c['snapshots']['10']['partial']==0 for c in rank['cases'])
    out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    inputs = {rel(p):sha(p) for p in [OLD/'MODELS.json', OLD/'CASES.json', RANK]}
    entries = []
    for item in manifest['models']:
        path = ROOT/item['path']
        model = read(path)
        assert model['language'] == item['language']
        table = np.asarray(model['logp'], dtype=np.float64)
        codes, scores, steps = beam(table)
        numerical = np.argsort(codes)
        cp = out/(item['language']+'_codes.npy')
        sp = out/(item['language']+'_scores.npy')
        assert not cp.exists() and not sp.exists()
        np.save(cp, codes[numerical], allow_pickle=False)
        np.save(sp, scores[numerical], allow_pickle=False)
        inputs[item['path']] = sha(path)
        entries.append(dict(language=item['language'], model_path=item['path'], model_sha256=sha(path), steps=steps,
                            final_codes_file=cp.name, final_scores_file=sp.name,
                            final_codes_sha256=sha(cp), final_scores_sha256=sha(sp)))
    result = dict(experiment_id='GDT1393', status='SIX_FIXED_PREFIX_BEAMS_FROZEN_NO_TRUTH_READ', width=WIDTH, depth=DEPTH,
                  lock_sha256=sha(lockpath), input_hashes=inputs, cases_sha256=sha(OLD/'CASES.json'), prefix_rank_sha256=sha(RANK),
                  languages=entries, wall_seconds=time.monotonic()-started,
                  truth_access=False, limits=['Independent forward beams, not globally top10-character strings or exact MAP.',
                    'No new key fitting, affine-state search, native data, source language selection or source-mixture replacement.',
                    'Final arrays are runtime artifacts; names only, no local absolute paths retained.'])
    save(A/'BEAMS.json', result)
    print(json.dumps(dict(status=result['status'], languages=len(entries), width=WIDTH, depth=DEPTH, beams_sha256=sha(A/'BEAMS.json'))))

def compare(out, truth_path):
    lockpath, manifest = check_lock()
    seal = read(A/'BEAMS_SEAL.json')
    assert seal['sealed_utc']
    assert seal['beams_sha256'] == sha(A/'BEAMS.json')
    beams = read(A/'BEAMS.json')
    assert beams['lock_sha256'] == sha(lockpath) and beams['width']==WIDTH and beams['depth']==DEPTH
    assert beams['cases_sha256'] == sha(OLD/'CASES.json') and beams['prefix_rank_sha256'] == sha(RANK)
    assert not (A/'COMPARISON.json').exists()
    sets = {}
    for entry in beams['languages']:
        cp, sp = out/entry['final_codes_file'], out/entry['final_scores_file']
        assert sha(cp)==entry['final_codes_sha256'] and sha(sp)==entry['final_scores_sha256']
        codes = np.load(cp, allow_pickle=False)
        assert len(codes)==WIDTH and np.all(codes[:-1]<codes[1:])
        sets[entry['language']] = codes
    # First truth read occurs here, after all six outputs and their seal exist.
    truth = read(truth_path)
    public = {c['id']:c['units'] for c in read(OLD/'CASES.json')['cases']}
    assert len(truth['cases'])==len(public)==18 and {c['id'] for c in truth['cases']}==set(public)
    records = []
    for case in truth['cases']:
        assert case['units']==public[case['id']]
        assert len(case['text'])==len(case['units']) and len(case['text'])>=DEPTH
        code = 0
        for char in case['text'][:DEPTH]:
            assert char==' ' or 'a'<=char<='z'
            code = code*27+(0 if char==' ' else ord(char)-96)
        hits = {}
        for lang, codes in sets.items():
            i = int(np.searchsorted(codes, code))
            hits[lang] = i<len(codes) and int(codes[i])==code
        records.append(dict(id=case['id'], kind=case['kind'], message_length=len(case['text']),
                            prefix_code=code, in_beams=hits, in_any_beam=any(hits.values())))
    positives = [r for r in records if r['kind']=='POSITIVE']
    negatives = [r for r in records if r['kind']=='NEGATIVE']
    assert len(positives)==12 and len(negatives)==6
    passed = all(r['in_any_beam'] for r in positives)
    result = dict(experiment_id='GDT1393', status='PREFIX_GATE_PASS_RECOVERY_NOT_ESTABLISHED' if passed else 'PREFIX_GATE_FAIL_NO_FULL_BEAM_ENGINE',
                  beams_sha256=sha(A/'BEAMS.json'), beams_seal_sha256=sha(A/'BEAMS_SEAL.json'), truth_sha256=sha(truth_path),
                  cases_sha256=sha(OLD/'CASES.json'), lock_sha256=sha(lockpath), cases=records,
                  positive_prefix_hits=sum(r['in_any_beam'] for r in positives), positive_cases=12,
                  negative_prefix_hits=sum(r['in_any_beam'] for r in negatives), negative_cases=6,
                  scope='Necessary prefix retention only on previously exposed historical controls; no native reading, key recovery or meaning.',
                  decision='Stop this exact six-beam/width65536 forward proposal if any positive prefix was pruned; no width/restart/source repair.')
    save(A/'COMPARISON.json', result)
    print(json.dumps({k:result[k] for k in ['status','positive_prefix_hits','positive_cases','negative_prefix_hits','negative_cases']}))

def controls():
    for scores in [np.zeros(100), np.array([float(i%7) for i in range(100)])]:
        codes = np.arange(100, dtype=np.int64)[::-1]
        for width in [1,7,64,100]:
            c,s = choose(codes,scores,width)
            expected = np.lexsort((codes,-scores))[:width]
            assert np.array_equal(c,codes[expected]) and np.array_equal(s,scores[expected])
    table = np.full((20440,27), -np.log(27.0))
    c,s,steps = beam(table,width=7,depth=10)
    assert np.array_equal(c,np.arange(7)) and all(x['count']==7 for x in steps)
    print(json.dumps(dict(status='PASS_SOURCE_FREE_SELECTION_AND_UNIFORM_BEAM_FIXTURE', truth_access=False)))

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--generate',action='store_true');g.add_argument('--compare',action='store_true');g.add_argument('--controls',action='store_true')
    p.add_argument('--output-dir',type=Path);p.add_argument('--truth',type=Path)
    args = p.parse_args()
    if args.controls:
        assert args.output_dir is None and args.truth is None
        controls()
    else:
        assert args.output_dir is not None
        if args.generate:
            assert args.truth is None
            generate(args.output_dir)
        else:
            assert args.truth is not None
            compare(args.output_dir,args.truth)

if __name__=='__main__':main()
