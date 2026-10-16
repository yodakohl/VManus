"""Finite vocabulary support for shared modular packet sums; not a decipherer."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from itertools import product
import argparse, hashlib, json, re, signal, subprocess, sys, tempfile, time
import z3

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
ART = BASE / 'artifacts'
SPEC = BASE / 'src/SPEC.json'
LOCK = BASE / 'src/REGISTRATION_LOCK.json'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def parse(raw, signs):
    # Cap path multiplicity at two; only a unique complete path supplies weights.
    paths = [[] for _ in range(len(raw) + 1)]
    paths[0] = [()]
    for i in range(len(raw)):
        for prefix in paths[i]:
            for j, sign in enumerate(signs):
                if raw.startswith(sign, i):
                    dest = i + len(sign)
                    if len(paths[dest]) < 2:
                        paths[dest].append(prefix + (j,))
    if not raw or len(paths[-1]) != 1:
        return None
    c = Counter(paths[-1][0])
    return [c[i] for i in range(len(signs))]


def vocab_regex(words):
    trie = {}
    for word in words:
        node = trie
        for ch in word:
            node = node.setdefault(ch, {})
        node[None] = True
    def emit(node):
        choices = [z3.Re('')] if None in node else []
        for ch in sorted(k for k in node if k is not None):
            prefix, child = ch, node[ch]
            while None not in child and len(child) == 1:
                nxt = next(iter(child)); prefix += nxt; child = child[nxt]
            if len(child) == 1 and None in child:
                choices.append(z3.Re(prefix))
            else:
                choices.append(z3.Concat(z3.Re(prefix), emit(child)))
        assert choices
        return choices[0] if len(choices) == 1 else z3.Union(*choices)
    v = emit(trie)
    return z3.Concat(v, z3.Star(z3.Concat(z3.Re(' '), v)))


def model(vectors, signs, words, modulus=27):
    solver = z3.Solver()
    weights = [z3.Int('w_' + str(i)) for i in range(len(signs))]
    for w in weights:
        solver.add(w >= 0, w < modulus)
    plaintext = z3.String('plaintext')
    solver.add(z3.Length(plaintext) == len(vectors))
    chars = []
    for i, counts in enumerate(vectors):
        c = z3.Int('c_' + str(i)); chars.append(c)
        solver.add(c >= 0, c < modulus)
        if counts is not None:
            solver.add(c == z3.Sum([n * w for n, w in zip(counts, weights) if n]) % modulus)
        solver.add(z3.StrToCode(z3.SubString(plaintext, i, 1)) == z3.If(c == 0, 32, 96 + c))
    solver.add(z3.InRe(plaintext, vocab_regex(words)))
    return solver, weights, chars, plaintext


def valid_text(text, words):
    return bool(text) and all(part in words for part in text.split(' '))


def pattern_hits(words):
    return [dict(word=w, offset_zero_based=i, substring=w[i:i+5])
            for w in sorted(words) for i in range(len(w)-4)
            if w[i] == w[i+1] == w[i+4] and w[i+2] == w[i+3]]


def controls():
    fixtures = [([[1, 0]], {'a'}), ([[1, 0], [1, 0]], {'ab'}),
                ([[1, 0], None, [0, 1]], {'a', 'b'}),
                ([[1, 1], [2, 0], [0, 2]], {'a', 'b', 'ab'}),
                ([None, None], {'a'}), ([[1, 0], [0, 1]], {'a', 'ab', 'b'})]
    for vectors, words in fixtures:
        brute = False
        for weights in product(range(3), repeat=2):
            domains = [range(3) if c is None else [sum(n*w for n,w in zip(c, weights)) % 3] for c in vectors]
            for chars in product(*domains):
                text = ''.join(' ' if x == 0 else chr(96+x) for x in chars)
                brute |= valid_text(text, words)
        s, ws, cs, txt = model(vectors, ['x', 'y'], words, 3)
        s.set(timeout=5000, random_seed=0)
        outcome = s.check()
        assert outcome != z3.unknown
        assert (outcome == z3.sat) == brute
        if outcome == z3.sat:
            assert valid_text(s.model().eval(txt).as_string(), words)
    assert parse('ch', ['c','h','ch']) is None
    assert parse('ch', ['c','ch']) == [0,1]
    assert parse('x@1;', ['x']) is None
    assert parse('', ['x']) is None
    assert parse('xxxx', ['x']) == [4]
    grammar = vocab_regex({'a','ab','b'})
    for text in ('', ' a', 'a ', 'a  b', 'a', 'ab', 'a b', 'b ab a', 'ba'):
        assert z3.is_true(z3.simplify(z3.InRe(z3.StringVal(text), grammar))) == valid_text(text, {'a','ab','b'})
    small = {''.join(x) for x in product('abc', repeat=5)}
    assert len(pattern_hits(small)) == 9
    assert pattern_hits({'aaaaa'})[0]['substring'] == 'aaaaa'
    assert not pattern_hits({'ababa'})
    return dict(status='PASS', aabba_exhaustive_words=243, exhaustive_modular_fixtures=len(fixtures), parser_fixtures=5,
                vocabulary_spacing_fixtures=9, z3_version=z3.get_version_string(), native_access=False)


class BuildTimeout(Exception):
    pass


def worker(request, destination):
    job = read(request); result = dict(job['metadata'])
    result.update(status='UNKNOWN', reason=None, model_build_seconds=None, solve_seconds=None,
                  weights=None, plaintext=None, words=None, source_character_values=None)
    if not job['vectors'] or not job['words']:
        result['reason'] = 'EMPTY_INPUT_OR_NO_ELIGIBLE_VOCABULARY'
        save(destination, result); return
    start = time.monotonic()
    signal.signal(signal.SIGALRM, lambda *args: (_ for _ in ()).throw(BuildTimeout()))
    signal.setitimer(signal.ITIMER_REAL, job['execution']['model_build_seconds'])
    try:
        solver, weights, chars, text = model(job['vectors'], job['signs'], job['words'])
        result['model_build_seconds'] = time.monotonic() - start
        signal.setitimer(signal.ITIMER_REAL, 0)
        solver.set(timeout=1000 * job['execution']['solver_seconds'], random_seed=0)
        started = time.monotonic(); outcome = solver.check()
        result['solve_seconds'] = time.monotonic() - started
        result['solver_statistics'] = str(solver.statistics())
        result['constraint_sha256'] = hashlib.sha256(solver.sexpr().encode()).hexdigest()
        if outcome == z3.sat:
            m = solver.model()
            result.update(status='SAT', reason='COMPLETE_RELAXED_SUPPORT_WITNESS',
                          weights=[m.eval(w, model_completion=True).as_long() for w in weights],
                          plaintext=m.eval(text).as_string(),
                          source_character_values=[m.eval(c).as_long() for c in chars])
            result['words'] = result['plaintext'].split(' ')
            assert valid_text(result['plaintext'], set(job['words']))
            assert len(result['plaintext']) == len(job['vectors'])
            for c, vector in zip(result['source_character_values'], job['vectors']):
                assert vector is None or c == sum(n*w for n,w in zip(vector,result['weights'])) % 27
        elif outcome == z3.unsat:
            result.update(status='UNSAT', reason='Z3_FINITE_SUPPORT_CONTRADICTION')
        else:
            result['reason'] = 'SOLVER_UNKNOWN: ' + solver.reason_unknown()
    except BuildTimeout:
        result['reason'] = 'MODEL_BUILD_TIMEOUT'
        result['model_build_seconds'] = time.monotonic() - start
    except Exception as exc:
        result.update(status='UNKNOWN', reason='MODEL_OR_WITNESS_ERROR:' + type(exc).__name__,
                      weights=None, plaintext=None, words=None, source_character_values=None)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    save(destination, result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--worker', nargs=2, metavar=('REQUEST','OUTPUT'))
    args = parser.parse_args()
    if args.controls:
        result = controls(); save(ART/'CONTROLS.json', result); print(json.dumps(result)); return
    if args.worker:
        worker(*args.worker); return
    spec, lock = read(SPEC), read(LOCK)
    hashes = {x['path']:x['sha256'] for x in lock['files']}
    required = {str(p.relative_to(ROOT)) for p in (SPEC,Path(__file__).resolve(),BASE/'src/validate.py',BASE/'METHOD.md',BASE/'PREREGISTRATION.md')}
    required.update(x['path'] for x in spec['inputs'])
    assert required <= hashes.keys()
    for path, digest in hashes.items():
        assert sha(ROOT/path) == digest, path
    for x in spec['inputs']:
        assert sha(ROOT/x['path']) == x['sha256'], x['path']
    source, manifest = read(ROOT/spec['source']), read(ROOT/spec['pack_manifest'])
    assert sorted(u['edition'] for u in source['units']) == ['IT2a','RF1b','ZL3b']
    prepared = []
    for unit in source['units']:
        rows = [dict(zip(unit['group_columns'],row)) for line in unit['lines'] for row in line['groups']]
        vectors = [parse(row['ivtff_group_raw'], spec['signs']) for row in rows]
        assert len({r['source_group_id'] for r in rows}) == len(rows)
        prepared.append((unit['edition'],rows,vectors,unit['boundary_status']))
    pattern = spec['fixed_support_prefilter']
    pre_readers = {}
    for reader, rows, vectors, boundary in prepared:
        if reader not in pattern['readers']:
            continue
        selected = [r for r in rows if r['source_group_id'].split('|')[1] == pattern['source_locus']
                    and int(r['source_group_index']) in pattern['group_indices']]
        assert [int(r['source_group_index']) for r in selected] == pattern['group_indices']
        assert [r['ivtff_group_raw'] for r in selected] == pattern['raw']
        assert all(r['source_group_id'] == reader+'|'+pattern['source_locus']+'|G'+str(i).zfill(3)
                   for r,i in zip(selected,pattern['group_indices']))
        assert all(a['right_separator'] == b['left_separator'] == 'DEFINITE_SPACE'
                   for a,b in zip(selected,selected[1:]))
        assert all(parse(r['ivtff_group_raw'],spec['signs']) is not None for r in selected)
        indices = [rows.index(r) for r in selected]
        assert indices == list(range(indices[0],indices[0]+5))
        pre_readers[reader] = dict(source_ids=[r['source_group_id'] for r in selected],raw=pattern['raw'])
    banks = {}
    for pack in spec['languages']:
        path = ROOT/'.gdt001/language_packs'/ (pack+'.txt')
        assert sha(path) == manifest['packs'][pack]['prepared_sha256']
        words = set(path.read_text(encoding='utf-8').split())
        assert words and all(re.fullmatch('[a-z]+',w) for w in words)
        banks[pack] = sorted(words)
    pre_packs = {}
    for pack, words in banks.items():
        hits = pattern_hits(words)
        pre_packs[pack] = dict(vocabulary_size=len(words),matching_word_count=len({h['word'] for h in hits}),
                               matching_substring_count=len(hits),witnesses=hits)
    save(ART/'PREFILTER.json',dict(pattern_spec=pattern,readers=pre_readers,packs=pre_packs))
    (ART/'SOURCE.json').write_bytes((ROOT/spec['source']).read_bytes())
    save(ART/'INPUT_MANIFEST.json', dict(spec_sha256=sha(SPEC),lock_sha256=sha(LOCK),
        inputs=spec['inputs'],signs=spec['signs'],z3_version=z3.get_version_string(),
        vocabularies={p:dict(size=len(ws),sha256=hashlib.sha256(('\n'.join(ws)+'\n').encode()).hexdigest()) for p,ws in banks.items()}))
    jobs=[]
    for reader, rows, vectors, boundary in prepared:
        for pack in spec['languages']:
            words=[w for w in banks[pack] if len(w)<=len(rows)]
            metadata=dict(case_id=reader+'__'+pack,reader=reader,pack=pack,source_group_count=len(rows),
                parsed_groups=sum(v is not None for v in vectors),free_groups=sum(v is None for v in vectors),
                source_ids=[r['source_group_id'] for r in rows],boundary_status=boundary,
                vocabulary_size=len(banks[pack]),eligible_vocabulary_size=len(words),
                eligible_vocabulary_sha256=hashlib.sha256(('\n'.join(words)+'\n').encode()).hexdigest())
            applied = reader in pre_readers
            hitcount = pre_packs[pack]['matching_substring_count'] if applied else None
            metadata.update(prefilter_applied=applied,prefilter_matching_substrings=hitcount,
                            mechanism='PREFILTER' if applied and hitcount==0 else 'SOLVER')
            jobs.append(dict(metadata=metadata, vectors=vectors,words=words,signs=spec['signs'],execution=spec['execution']))
    def launch(job):
        if job['metadata']['mechanism'] == 'PREFILTER':
            return dict(job['metadata'],status='UNSAT',reason='NECESSARY_AABBA_WORD_SUBSTRING_ABSENT',
                        model_build_seconds=0,solve_seconds=0,weights=None,plaintext=None,words=None,
                        source_character_values=None)
        with tempfile.TemporaryDirectory(prefix='gdt1388_') as folder:
            request=Path(folder)/'request.json'; destination=Path(folder)/'answer.json';save(request,job)
            try:
                proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(request),str(destination)],
                                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=spec['execution']['outer_case_seconds'])
                if proc.returncode==0 and destination.exists(): return read(destination)
                reason='WORKER_EXIT_'+str(proc.returncode)
            except subprocess.TimeoutExpired:
                reason='OUTER_CASE_TIMEOUT'
            return dict(job['metadata'],status='UNKNOWN',reason=reason,model_build_seconds=None,solve_seconds=None,
                        weights=None,plaintext=None,words=None,source_character_values=None)
    with ThreadPoolExecutor(max_workers=min(6,spec['execution']['max_workers'])) as pool:
        cases=list(pool.map(launch,jobs))
    result=dict(status='MODULAR_PARAGRAPH_VOCABULARY_SUPPORT',cases=cases,
                decision_counts=dict(Counter(c['status'] for c in cases)),
                claim_ceiling='Necessary fixed packet/inventory support only; SAT is not a complete writer or meaningful text. UNKNOWN excludes nothing.')
    assert len(cases)==18
    save(ART/'RESULT.json',result)
    print(json.dumps(result['decision_counts']))


if __name__=='__main__':
    main()
