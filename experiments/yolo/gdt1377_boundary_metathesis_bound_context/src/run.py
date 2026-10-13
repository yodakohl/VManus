#!/usr/bin/env python3
"""Fixed one-site context check; no cache-wide model selection."""
import hashlib
import json
from pathlib import Path
E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
def read(p): return json.loads(p.read_text())
def save(name, value):
    (E / 'artifacts' / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
def parse(raw, units):
    ways = [[] for _ in range(len(raw) + 1)]
    ways[0] = [[]]
    for i in range(len(raw)):
        for u in units:
            if raw.startswith(u, i):
                ways[i + len(u)].extend(w + [u] for w in ways[i])
    return ways[-1][0] if len(ways[-1]) == 1 and ways[-1][0] else None

def main():
    lock = read(E / 'src/REGISTRATION_LOCK.json')
    for path, digest in lock['hashes'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    spec = read(E / 'src/SPEC.json')
    allow = ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
    assert any(line.split('\t')[0] == 'f18v' for line in allow.read_text().splitlines())
    contexts, results = {}, {}
    for ed in spec['readers']:
        entry, = [v for v in spec['inputs'] if v['path'].endswith('_' + ed + '.json')]
        raw = (ROOT / entry['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry['sha256']
        data = json.loads(raw)
        selected = [line for line in data['lines'] if line['metadata']['page'] == spec['page']
                    and line['metadata']['locus'] == spec['locus']]
        errors, rows, meta = [], [], None
        if len(selected) != 1: errors.append('unique_target_line')
        else:
            line = selected[0]; meta = line['metadata']
            if meta['edition'] != ed or meta['kind'] != 'P' or int(meta['source_group_count']) < 3:
                errors.append('metadata')
            columns = data['group_columns']; ix = columns.index('source_group_index')
            rows = [dict(zip(columns, r)) for r in line['groups'] if int(r[ix]) in spec['indices']]
            rows.sort(key=lambda r: int(r['source_group_index']))
        if [int(r['source_group_index']) for r in rows] != spec['indices']:
            errors.append('unique_original_indices')
        ids = [r['source_group_id'] for r in rows]
        if len(set(ids)) != len(rows) or any(r['source_group_id'] != f"{ed}|f18v.8|G{int(r['source_group_index']):03d}" for r in rows):
            errors.append('source_ids')
        if len(rows) != 3 or [r['ivtff_group_raw'] for r in rows[1:]] != ['sh', 'cphoy']:
            errors.append('fixed_witnesses')
        if len(rows) != 3 or any(a['right_separator'] != 'DEFINITE_SPACE' or b['left_separator'] != 'DEFINITE_SPACE'
               for a,b in zip(rows, rows[1:])):
            errors.append('shared_seams')
        parsed = [parse(r['ivtff_group_raw'], spec['units']) for r in rows]
        if len(parsed) != 3 or any(p is None for p in parsed): errors.append('complete_unique_literal_parse')
        status = 'UNSCORABLE' if errors else ('REQUIRED_RESCUE_PRESENT' if parsed[0][-1] == spec['B']
                                             else 'FIXED_KEY_EXCLUDED_AT_BOUND_CONTEXT')
        contexts[ed] = {'metadata': meta, 'groups': rows, 'source': entry}
        results[ed] = {'status': status, 'failed_gates': errors, 'parsed_groups': parsed,
                       'g001_final_unit': parsed[0][-1] if parsed and parsed[0] else None}
    save('CONTEXT.json', contexts)
    result = {'status': 'BOUND_CONTEXT_' + results[spec['primary']]['status'], 'primary': spec['primary'],
              'key': {'A': spec['A'], 'B': spec['B']}, 'readers': results,
              'claim_ceiling': 'One physical context, alternate readers separate; no key confirmation or meaning.'}
    save('RESULT.json', result)
    print(json.dumps(result, indent=2))
if __name__ == '__main__': main()
