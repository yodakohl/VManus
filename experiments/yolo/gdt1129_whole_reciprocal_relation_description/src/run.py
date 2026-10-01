from pathlib import Path
import json, hashlib
D = Path(__file__).resolve().parents[1]

def main():
    plan = json.loads((D / 'src/AUTHOR_PLAN.json').read_text())
    raw = Path(plan['source']).read_bytes()
    checks = {'source_identity': hashlib.sha256(raw).hexdigest() == plan['source_sha256']}
    source = json.loads(raw)
    for reader, expected in plan['scope'].items():
        rows = source['raw'][reader]
        checks[reader + '_five_lines'] = len(rows) == 5
        checks[reader + '_leaf'] = all(row['metadata']['page'] == 'f75v' for row in rows)
        checks[reader + '_groups'] = sum(len(row['groups']) for row in rows) == expected
        checks[reader + '_loci'] = [row['metadata']['locus'] for row in rows] == ['f75v.' + str(i) for i in range(38,43)]
        ids = [g['source_group_id'] for row in rows for g in row['groups']]
        checks[reader + '_ids'] = len(ids) == len(set(ids)) == expected
        checks[reader + '_paragraph_capacity'] = len(source['paragraphs'][reader]) == (0 if reader == 'RF1b' else 1)
    manifest = json.loads((D / 'experiment.json').read_text())
    checks['sealed'] = manifest['sealed_data'] == {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'}
    result = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'claim_ceiling': 'Source identity and preregistration accounting only; no semantic or author validation.', 'checks': checks}
    (D / 'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2) + '\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'semantic_validation':False}))
    return 0 if all(checks.values()) else 1

if __name__ == '__main__':
    raise SystemExit(main())
