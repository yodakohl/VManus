"""Locked fixed-scope wrapper around the byte-frozen R771 primary parser."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    # Lock verification precedes every target cache read.
    lock = load(EXP / 'CODE_LOCK.json')
    assert lock['locked_utc']
    locked = {entry['path']: entry['sha256'] for entry in lock['files']}
    for path in [HERE / 'run.py', HERE / 'validate.py', HERE / 'SPEC.json']:
        relative = str(path.relative_to(ROOT))
        assert relative in locked and sha(path) == locked[relative], relative
    for relative, expected in locked.items():
        assert sha(ROOT / relative) == expected, relative
    spec_path = HERE / 'SPEC.json'
    spec = load(spec_path)
    assert spec['experiment_id'] == 'GDT1386'
    for pin in spec['pins']:
        assert sha(ROOT / pin['path']) == pin['sha256'], pin['path']
    target = spec['target']
    assert target['page'] == 'f75r'
    assert target['loci'] == [f'f75r.{i}' for i in range(32, 47)]
    plan = load(ROOT / spec['model_plan'])
    development = load(ROOT / spec['development_source'])
    sys.dont_write_bytecode = True
    ms = importlib.util.spec_from_file_location('frozen_r771_primary', ROOT / spec['model_builder'])
    primary = importlib.util.module_from_spec(ms)
    ms.loader.exec_module(primary)
    units, sources, counts, reuse = [], [], {}, {}
    for reader in target['readers']:
        pin = next(p for p in spec['pins'] if p['path'].endswith(f'/SOURCE_DISCOVERY_{reader}.json'))
        cached = load(ROOT / pin['path'])
        selected = [line for line in cached['lines'] if line['metadata']['page'] == target['page']
                    and line['metadata']['locus'] in target['loci']]
        selected.sort(key=lambda line: target['loci'].index(line['metadata']['locus']))
        assert [l['metadata']['locus'] for l in selected] == target['loci']
        assert all(l['metadata']['edition'] == reader and l['metadata']['kind'] == 'P' for l in selected)
        for line in selected:
            assert len(line['groups']) == int(line['metadata']['source_group_count'])
            assert [int(g[1]) for g in line['groups']] == list(range(1, len(line['groups']) + 1))
        starts = [l['metadata']['locus'] for l in selected if l['metadata']['paragraph_start'] == '1']
        ends = [l['metadata']['locus'] for l in selected if l['metadata']['paragraph_end'] == '1']
        if reader in target['own_paragraph_flags']:
            assert starts == ['f75r.32'] and ends == ['f75r.46']
        else:
            assert starts == ends == []
        total = sum(len(l['groups']) for l in selected)
        if reader in target['expected_metadata_counts']:
            assert total == target['expected_metadata_counts'][reader]
        counts[reader] = dict(lines=len(selected), groups=total, paragraph_start_loci=starts, paragraph_end_loci=ends)
        unit = dict(edition=reader, boundary_status='source-flagged complete paragraph'
                    if reader in target['own_paragraph_flags'] else 'corresponding window; no paragraph flags',
                    group_columns=cached['group_columns'], lines=selected)
        units.append(unit)
        sources.append(dict(path=pin['path'], sha256=pin['sha256']))
        old = next(u for u in development['units'] if u['edition'] == reader)
        rawcol = cached['group_columns'].index('ivtff_group_raw')
        oldcol = old['group_columns'].index('ivtff_group_raw')
        old_types = {g[oldcol] for l in old['lines'] for g in l['groups']}
        words = [g[rawcol] for l in selected for g in l['groups']]
        types, new = set(words), set(words) - old_types
        classified = set(plan['semantics']['primitive_classes']) | set(plan['semantics']['finite_joined_classes'])
        opaque = new - classified - {'qokar', 'tol', 'daiin'}
        reused_positions = sum(w in old_types for w in words)
        reuse[reader] = dict(development_word_types=len(old_types), target_word_types=len(types),
                             reused_word_types=len(types & old_types), reused_positions=reused_positions,
                             new_word_types=len(new), new_positions=total-reused_positions,
                             new_opaque_types=sorted(opaque), reused_types=sorted(types & old_types), new_types=sorted(new))
    source = dict(experiment_id='GDT1386', spec_sha256=sha(spec_path), sources=sources, units=units)
    artifacts = EXP / 'artifacts'
    source_path = artifacts / 'SOURCE.json'
    write(source_path, source)
    cases = []
    for phase in target['phases']:
        for unit in units:
            case = primary.parse(unit, phase, plan['semantics'])
            case['status'] = 'FIXED_CONSTRUCTION_CONTRADICTED' if case['errors'] else 'FORMALLY_COMPATIBLE_UNCONFIRMED'
            cases.append(case)
    failed = sum(bool(c['errors']) for c in cases)
    status = ('ALL_FIXED_CASES_CONTRADICTED' if failed == len(cases) else
              'ALL_CASES_FORMALLY_COMPATIBLE_NO_MEANING_SELECTION' if failed == 0 else
              'MIXED_CASE_TRANSFER_WITH_RETAINED_FAILURES')
    result = dict(experiment_id='GDT1386', spec_sha256=sha(spec_path), source_sha256=sha(source_path),
                  status=status, cases=cases, reuse_by_reader=reuse, source_counts=counts,
                  limits=['Exposed same physical folio as development; no independent confirmation folios.',
                          'Alternate readers and two fixed phases are not independent tests.',
                          'All exact parser errors reject that case; subsequent recovery frames are diagnostic only.',
                          'Unknown exact wholes retain the frozen broad Class default; formal compatibility is not translation.',
                          'RF endpoint is imposed; original flags and annotations remain unchanged.',
                          'No toy truth evaluation, native predicate interpretation or after-exposure repair.'])
    write(artifacts / 'RESULT.json', result)
    print(json.dumps(dict(status=status, cases=len(cases), failed_cases=failed, source_counts=counts), sort_keys=True))

if __name__ == '__main__':
    main()
