from pathlib import Path
from datetime import datetime, timezone
import gzip, json, hashlib
from engine import derive

D = Path(__file__).resolve().parents[1]
A = D / 'artifacts'
S = json.loads((D / 'src/SPEC.json').read_text())


def main():
    assert not (A / 'RESULT.json').exists(), 'Do not overwrite retained result'
    lock = json.loads((A / 'REGISTRATION_LOCK.json').read_text())
    for p, h in lock['files'].items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == h, p
    data = json.loads(gzip.decompress(Path(S['source']).read_bytes()))
    result = {'experiment': 'GDT1234', 'started_utc': datetime.now(timezone.utc).isoformat(), 'readers': {}}
    for reader in S['readers']:
        rows = data[reader]
        W = {tuple(r['units']) for r in rows}
        assert all(w and set(w) <= set(S['signs']) for w in W)
        cert = derive(W, S['runtime_seconds_per_reader'])
        (A / ('CERTIFICATE_' + reader + '.json.gz')).write_bytes(gzip.compress(json.dumps(cert, separators=(',', ':')).encode(), mtime=0))
        result['readers'][reader] = {'groups': len(rows), 'types': len(W), 'closure_status': cert['status'],
                                     'closure_size': len(cert['nodes']), 'rounds': cert['rounds'],
                                     'summary': cert.get('summary')}
    result['status'] = 'COMPLETE_NECESSARY_BOUNDS' if all(x['closure_status'] == 'COMPLETE' for x in result['readers'].values()) else 'UNKNOWN_INCOMPLETE'
    result['completed_utc'] = datetime.now(timezone.utc).isoformat()
    (A / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print({'status': result['status'], 'completed_utc': result['completed_utc'], 'readers': {
        k: {'closure': v['closure_size'], 'forced': v['summary']['F'] if v['summary'] else None,
            'bound': v['summary']['necessary_nontrivial_bound'] if v['summary'] else None,
            'basis': v['summary']['prefix_basis_size'] if v['summary'] else None} for k, v in result['readers'].items()}})


if __name__ == '__main__':
    main()
