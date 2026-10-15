"""Independent fixed-transfer reconstruction; never imports the runner/parser."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())
ART = HERE.parent / 'artifacts'
OPS = {'qokar', 'tol', 'daiin'}
CLASSES = {'ol':['A'], 'qol':['B'], 'chedy':['P'], 'shedy':['Q'],
           'olchedy':['A','P'], 'qolchedy':['B','P'], 'olshedy':['A','Q']}
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cls(w): return None if w in OPS else CLASSES.get(w, ['N_' + w])
def rows(u):
    return [dict(zip(u['group_columns'], r)) for l in u['lines'] for r in l['groups']]

def reconstruct(u, phase):
    rr = rows(u)
    pairs = {('ol','chedy'), ('qol','chedy'), ('ol','shedy')}
    if phase == 'PRE': pairs = {(b,a) for a,b in pairs}
    frames = [dict(id='FRAME1', quantifier='EXISTS', restriction=[], binder_source_ids=[],
                   implicit=True, variable='x1', body=[])]
    events, errors = [], []
    cursor = 0
    while cursor < len(rr):
        g = rr[cursor]; w = g['ivtff_group_raw']; sid = g['source_group_id']
        after = rr[cursor+1] if cursor+1 < len(rr) else None
        v = after['ivtff_group_raw'] if after else None
        if w in OPS:
            if w == 'daiin' or after is None or v in OPS:
                err = dict(source_ids=[sid], error='ORPHAN_DAIIN' if w == 'daiin'
                           else 'MISSING_OR_OPERATOR_BINDER_ARGUMENT')
                errors.append(err); events.append(dict(kind='ERROR', **err)); cursor += 1
                continue
            frames[-1]['closed_before_source_id'] = sid
            number = len(frames)+1
            f = dict(id='FRAME'+str(number), quantifier='EXISTS' if w=='qokar' else 'ALL',
                     restriction=cls(v), binder_source_ids=[sid,after['source_group_id']],
                     implicit=False, variable='x'+str(number), body=[])
            frames.append(f)
            events.append(dict(kind='BINDER', frame=f['id'], source_ids=f['binder_source_ids']))
            cursor += 2
            continue
        definite = after is not None and g['right_separator'] == after['left_separator'] == 'DEFINITE_SPACE'
        count = 1; f = frames[-1]
        if definite and (w,v) in pairs:
            count = 2
            node = dict(kind='LOCAL_EXISTS', predicates=cls(w)+cls(v), variable='z'+str(len(events)+1), changes_current=False)
        else:
            explicit = definite and v == 'daiin'
            count = 2 if explicit else 1
            node = dict(kind='PREDICATE', predicates=cls(w), variable=f['variable'], explicit_daiin=explicit)
        used = rr[cursor:cursor+count]
        node.update(source_ids=[r['source_group_id'] for r in used], raw=[r['ivtff_group_raw'] for r in used])
        f['body'].append(node)
        events.append(dict(kind=node['kind'], frame=f['id'], source_ids=node['source_ids']))
        cursor += count
    frames[-1]['closed_at_selected_endpoint'] = True
    assert [s for e in events for s in e['source_ids']] == [r['source_group_id'] for r in rr]
    opaque = {}
    for r in rr:
        w = r['ivtff_group_raw']
        if w not in OPS and w not in CLASSES:
            opaque.setdefault('N_'+w, []).append(r['source_group_id'])
    universals = [f for f in frames if f['quantifier']=='ALL' and set(f['restriction'])=={'A','P'}]
    sites = [n['source_ids'] for f in universals for n in f['body'] if n['kind']=='PREDICATE' and 'Q' in n['predicates']]
    local = [n['source_ids'] for f in universals for n in f['body'] if n['kind']=='LOCAL_EXISTS' and {'A','Q'} <= set(n['predicates'])]
    witnesses = [f['id'] for f in frames if f['quantifier']=='EXISTS' and {'A','P'} <= set(f['restriction'])]
    return dict(id=phase+'_'+u['edition'], phase=phase, reader=u['edition'], source_group_count=len(rr),
                source_unit=u, frames=frames, events=events, errors=errors, unknown_atoms=opaque,
                native_truth='UNASSIGNED_PREDICATE_INTERPRETATIONS',
                endpoint_status='ADDITIONAL_WINDOW_ENDPOINT_ASSUMPTION' if u['edition']=='RF1b' else 'SOURCE_FLAGGED_PARAGRAPH_ENDPOINT',
                scope_consequences=dict(AP_subset_Q_direct_body=bool(sites), source_sites=sites,
                    AP_nonempty_explicit_frames=witnesses, local_AQ_exists_under_ALL_sites=local,
                    AQ_nonempty_from_AP_and_local_exists=bool(witnesses and local)),
                status='FIXED_CONSTRUCTION_CONTRADICTED' if errors else 'FORMALLY_COMPATIBLE_UNCONFIRMED')

def main():
    # Refuse source access before a root-created complete implementation lock.
    lock = read(HERE.parent/'CODE_LOCK.json')
    locked = {x['path']:x['sha256'] for x in lock['files']}
    for p in (HERE/'run.py', HERE/'validate.py', HERE/'SPEC.json'):
        assert locked[p.relative_to(ROOT).as_posix()] == sha(p)
    for name, digest in locked.items(): assert sha(ROOT/name) == digest
    spec = read(HERE/'SPEC.json')
    for pin in spec['pins']: assert sha(ROOT/pin['path']) == pin['sha256']
    source = read(ART/'SOURCE.json'); result = read(ART/'RESULT.json')
    assert source['experiment_id'] == result['experiment_id'] == 'GDT1386'
    assert source['spec_sha256'] == result['spec_sha256'] == sha(HERE/'SPEC.json')
    assert result['source_sha256'] == sha(ART/'SOURCE.json')
    units = source['units']
    assert [u['edition'] for u in units] == spec['target']['readers']
    development = {u['edition']:u for u in read(ROOT/spec['development_source'])['units']}
    expected_sources, counts, reuse = [], {}, {}
    for u in units:
        edition = u['edition']
        assert u['boundary_status'] == ('corresponding window; no paragraph flags' if edition=='RF1b' else 'source-flagged complete paragraph')
        pin = next(p for p in spec['pins'] if p['path'].endswith('SOURCE_DISCOVERY_'+edition+'.json'))
        expected_sources.append(dict(path=pin['path'],sha256=pin['sha256']))
        cache = read(ROOT/pin['path'])
        selected = [l for l in cache['lines'] if l['metadata']['locus'] in spec['target']['loci']]
        selected.sort(key=lambda l:spec['target']['loci'].index(l['metadata']['locus']))
        assert u['group_columns'] == cache['group_columns'] and u['lines'] == selected
        assert [l['metadata']['locus'] for l in selected] == spec['target']['loci']
        for l in selected:
            m = l['metadata']
            assert m['edition'] == edition and m['page']=='f75r' and m['kind']=='P'
            assert len(l['groups']) == int(m['source_group_count'])
        rr = rows(u)
        assert len({r['source_group_id'] for r in rr}) == len(rr)
        starts = [l['metadata']['locus'] for l in selected if l['metadata']['paragraph_start']=='1']
        ends = [l['metadata']['locus'] for l in selected if l['metadata']['paragraph_end']=='1']
        assert starts == ([] if edition=='RF1b' else ['f75r.32'])
        assert ends == ([] if edition=='RF1b' else ['f75r.46'])
        if edition in spec['target']['expected_metadata_counts']:
            assert len(rr)==spec['target']['expected_metadata_counts'][edition]
        counts[edition]=dict(lines=len(selected),groups=len(rr),paragraph_start_loci=starts,paragraph_end_loci=ends)
        old={r['ivtff_group_raw'] for r in rows(development[edition])}
        words=[r['ivtff_group_raw'] for r in rr]; new=set(words)-old
        reuse[edition]=dict(development_word_types=len(old),target_word_types=len(set(words)),
            reused_word_types=len(set(words)&old),reused_positions=sum(w in old for w in words),
            new_word_types=len(new),new_positions=sum(w in new for w in words),
            new_opaque_types=sorted(new-OPS-set(CLASSES)),reused_types=sorted(set(words)&old),new_types=sorted(new))
    assert source['sources'] == expected_sources
    assert result['source_counts']==counts and result['reuse_by_reader']==reuse
    expected=[reconstruct(u,p) for p in spec['target']['phases'] for u in units]
    assert result['cases']==expected
    failures=sum(bool(c['errors']) for c in expected)
    status=('ALL_FIXED_CASES_CONTRADICTED' if failures==6 else
            'ALL_CASES_FORMALLY_COMPATIBLE_NO_MEANING_SELECTION' if failures==0 else
            'MIXED_CASE_TRANSFER_WITH_RETAINED_FAILURES')
    assert result['status']==status
    assert not any('toy_results' in c for c in result['cases'])
    assert 'toy_worlds' not in result
    report=dict(status='PASS',experiment_id='GDT1386',independent_reconstruction=True,
        blind_semantic_validation=False,semantic_confirmation=False,
        source_groups=sum(c['groups'] for c in counts.values()),cases=6,
        contradicted_cases=failures,verified_result=status,
        hashes={**{n:sha(ART/n) for n in ('SOURCE.json','RESULT.json')}, 'CODE_LOCK.json':sha(HERE.parent/'CODE_LOCK.json')},
        validator_sha256=sha(Path(__file__)),
        limits=['Independent source and fixed-grammar reconstruction; not a blind semantic test.',
                'One historically exposed physical folio; RF endpoint imposed.',
                'Error-recovery formulas are diagnostic only; uniform unknown Class typing remains unconfirmed.'])
    (ART/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True))

if __name__=='__main__': main()
