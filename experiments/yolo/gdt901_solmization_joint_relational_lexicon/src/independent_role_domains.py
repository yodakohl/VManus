#!/usr/bin/env python3
"""Independent necessary domains for the ten frozen role-alias partitions.

Only the independent 35-atom helper is reused. No primary source compiler or
fitter is imported. Root/affix equations are deliberately relaxed: emptiness
remains a sound exclusion; nonempty domains do not prove morphology or order.
"""
import argparse
import hashlib
import json
from pathlib import Path
from independent_domains import PITCHES, TYPES, DIRECTIONS, independent_compile, domains

PITCH_PARTITIONS = [[0,0],[0,1]]
VOICE_PARTITIONS = [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[0,1,2]]
CASES = [{'pitch':p,'voice':v} for p in PITCH_PARTITIONS for v in VOICE_PARTITIONS]
COUNTS = [35,41,41,41,47,42,48,48,48,54]


def compile_roles(observer, case):
    """Role positions come directly from B's membership/mutation records."""
    assert case in CASES
    phead, porigin = case['pitch']
    vmember, vfrom, vto = case['voice']
    ids = {f'P{i+1:02}':name for i,name in enumerate(PITCHES)}
    records = []
    for i,row in enumerate(observer['records']):
        name = PITCHES[i]
        assert row['pitch_id'] == f'P{i+1:02}'
        def pitch(value, role):
            return f'PITCH:{role}:{value}'
        def voice(value, role):
            return f'VOICE:{role}:{value}'
        def origin(oid):
            value = ids[oid]
            return 'SELF' if value == name else pitch(value,porigin)
        head = pitch(name,phead)
        sequence = [head]
        for m in row['voice_memberships_in_written_order']:
            sequence += [voice(m['voice'],vmember), 'CANTUS:'+TYPES[m['cantus_type']],
                         origin(m['origin_pitch_id'])]
        assert len(row['directed_mutations']) == row['mutation_count_explicit']
        for n,e in enumerate(row['directed_mutations'],1):
            assert e['listed_ordinal'] == n
            sequence += [voice(e['from_voice'],vfrom), voice(e['to_voice'],vto),
                         'DIRECTION:'+DIRECTIONS[e['direction']],
                         'CANTUS:'+TYPES[e['destination_cantus_type']],
                         origin(e['destination_origin_pitch_id'])]
        if row['explicit_zero']:
            assert not row['directed_mutations']
            sequence.append('ZERO')
        records.append({'id':name,'head_atom':head,'sequence':sequence})
    assert len(records) == 22
    return records


def record_digest(records):
    return hashlib.sha256((json.dumps(records,ensure_ascii=False,sort_keys=True,
                                      separators=(',',':'))+'\n').encode()).hexdigest()


def audit_source(source, observer, spec):
    assert spec['cases'] == CASES
    assert spec['form_counts'] == COUNTS
    assert independent_compile(observer) == source['records']
    compiled = [compile_roles(observer,c) for c in CASES]
    for i,records in enumerate(compiled):
        assert len({a for r in records for a in r['sequence']}) == COUNTS[i]
    # The merged-role case is exactly the original model up to atom renaming.
    def unrole(atom):
        if atom.startswith(('PITCH:','VOICE:')):
            family,block,value = atom.split(':',2)
            assert block == '0'
            return family+':'+value
        return atom
    merged = [{'id':r['id'],'head_atom':unrole(r['head_atom']),
               'sequence':[unrole(a) for a in r['sequence']]} for r in compiled[0]]
    assert merged == source['records']
    return compiled


def self_test(observer):
    # Feasible synthetic morphology: one shared prefix per family/class and
    # one nonempty root per semantic value, with empty suffix. Background is
    # one globally unassigned type. No actual manuscript data is involved.
    for i,case in enumerate(CASES):
        records = compile_roles(observer,case)
        atoms = sorted({a for r in records for a in r['sequence']})
        assert len(atoms) == COUNTS[i]
        code = {}
        for a in atoms:
            if a.startswith(('PITCH:','VOICE:')):
                family,block,value = a.split(':',2)
                code[a] = family.lower()+block+'_'+'r'+value+'z'
            else:
                code[a] = 'plain_'+a.replace(':','_')
        assert len(set(code.values())) == len(code)
        targets = [{'id':r['id'],'words':[code[r['sequence'][0]],'background']+
                    [code[a] for a in r['sequence'][1:]]+['background']} for r in records]
        result = domains(records,targets)
        assert not result['empty_domains']
        assert all(code[a] in result['domains'][a] for a in atoms)
    print('PASS: all10 B-derived role compilations preserve explicit synthetic root/affix witnesses')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source',type=Path)
    p.add_argument('--observer',type=Path,required=True)
    p.add_argument('--model-spec',type=Path)
    p.add_argument('--target',type=Path)
    p.add_argument('--panel',default='IT2a')
    p.add_argument('--output',type=Path)
    p.add_argument('--source-only',action='store_true')
    p.add_argument('--self-test',action='store_true')
    a = p.parse_args()
    ob = a.observer.read_bytes(); observer = json.loads(ob)
    if a.self_test:
        self_test(observer);return
    if a.source is None or a.model_spec is None:
        p.error('source and model-spec required')
    sb,mb = a.source.read_bytes(),a.model_spec.read_bytes()
    source,spec = json.loads(sb),json.loads(mb)
    assert hashlib.sha256(sb).hexdigest() == spec['source_sha256']
    assert hashlib.sha256(ob).hexdigest() in [r['sha256'] for r in source['source_receipts']]
    compiled = audit_source(source,observer,spec)
    if a.source_only:
        print(json.dumps({'source_audit':'PASS','form_counts':COUNTS,
                          'compiled_record_sha256':[record_digest(r) for r in compiled]}))
        return
    if a.target is None or a.output is None:
        p.error('target and output required for domain checks')
    tb = a.target.read_bytes(); target = json.loads(tb)
    cases = []
    for i,(case,records) in enumerate(zip(CASES,compiled)):
        result = domains(records,target['panels'][a.panel])
        result.update(case_index=i,partition=case,compiled_record_sha256=record_digest(records))
        cases.append(result)
    excluded = [r['case_index'] for r in cases if r['empty_domains'] or r['capacity_failure']]
    output = {'schema':'GDT901_INDEPENDENT_ROLE_DOMAINS_V1',
              'status':'FULL_TEN_PARTITION_MODEL_UNSAT_NECESSARY_CONDITION' if len(excluded)==10
                       else 'SURVIVING_PARTITIONS_FULL_MODEL_UNRESOLVED',
              'source_sha256':hashlib.sha256(sb).hexdigest(),
              'model_spec_sha256':hashlib.sha256(mb).hexdigest(),
              'observer_sha256':hashlib.sha256(ob).hexdigest(),
              'target_sha256':hashlib.sha256(tb).hexdigest(),
              'panel':a.panel,'cases':cases,'excluded_partition_indices':excluded,
              'independent_B_source_compile':'PASS_ALL10; MERGED_CASE_EXACTLY_ORIGINAL_UP_TO_RENAMING',
              'root_affix_equations_fitted':False,'full_order_fit_performed':False,
              'proof':['Distinct realized form atoms have distinct whole-word values by the registered model.',
                       'The word count in each selected raw paragraph therefore equals its realized-form count, even when forms share a semantic root. Global background cannot erase a mapped word.',
                       'Distinct paragraph assignments imply target histogram capacity at every count including zero; a head form additionally needs a first-word occurrence.',
                       'An empty realized-form domain excludes that entire partition. The union is excluded only when every one of the ten partitions is excluded.',
                       'Ignoring shared root/affix equations is a relaxation and cannot remove a valid morphological witness. Nonempty domains are not SAT or identification.']}
    a.output.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(output['status'])


if __name__ == '__main__':
    main()
