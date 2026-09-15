"""Post-result transparent rendering and small witnesses; never changes selection."""
import csv
import gzip
import hashlib
import itertools
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]


def rows(name):
    with (E / 'artifacts' / name).open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def main():
    source = json.loads((E / 'src/SOURCE.json').read_text())
    target = {(r['edition'], r['locus']): r for r in rows('COMPLETE_TARGET_RECORDS.tsv')}
    details = json.loads((E / 'artifacts/CANDIDATE_DETAILS.json').read_text())
    predictions = rows('ALL_PREDICTIONS.tsv')
    surviving = {(r['edition'], r['candidate']) for r in details if r['P_status'] != 'CONTRADICTED'}
    render = []
    witnesses = []
    for edition, candidate in sorted(surviving):
        current = [r for r in predictions if r['candidate'] == candidate]
        m = {int(r['source_row']): r['locus'] for r in current}
        for p in current:
            t = target[edition, p['locus']]
            render.append({'edition': edition, **p, 'observed_raw_groups': t['raw_groups'],
                           'whole_known': t['literal_known'], 'root_units': t['units'],
                           'claim': 'CONDITIONAL_P_PREDICTION_ONLY; MODEL_C_CONTRADICTED'})
        if candidate != 'R16':
            continue
        for atom in source['atoms']:
            observed = [(n, set(target[edition, m[n]]['units'].split(',')))
                        for n in atom['rows'] if target[edition, m[n]]['root_known'] == '1']
            common = set.intersection(*(v for _, v in observed)) if observed else None
            cert = {'edition': edition, 'candidate': candidate, 'atom': atom['id'],
                    'source_positive_rows': atom['rows'],
                    'known_positive_loci': [m[n] for n, _ in observed],
                    'positive_unit_intersection': None if common is None else sorted(common)}
            if common == set():
                for k in range(2, len(observed) + 1):
                    found = False
                    for subset in itertools.combinations(observed, k):
                        if not set.intersection(*(v for _, v in subset)):
                            cert['small_positive_conflict'] = [
                                {'source_row': n, 'locus': m[n], 'units': sorted(v)} for n, v in subset]
                            found = True
                            break
                    if found:
                        break
            elif common:
                cert['remaining_units_contradicted_by_negative_rows'] = {
                    u: [{'source_row': n, 'locus': locus} for n, locus in m.items()
                        if n != 22 and n not in atom['rows'] and target[edition, locus]['root_known'] == '1'
                        and u in target[edition, locus]['units'].split(',')] for u in sorted(common)}
            witnesses.append(cert)
    with (E / 'artifacts/REMAINING_P_READINGS.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(render[0]), delimiter='\t'); w.writeheader(); w.writerows(render)
    (E / 'artifacts/R16_COMPONENT_WITNESSES.json').write_text(json.dumps(witnesses, indent=2) + '\n')
    # Publish the exact complete large audit as deterministic gzip, not a selected subset.
    p = E / 'artifacts/ALL_COMPONENT_CONSEQUENCES.tsv'
    payload = p.read_bytes()
    packed = gzip.compress(payload, mtime=0)
    p.with_suffix(p.suffix + '.gz').write_bytes(packed)
    receipt = {'plain_path': str(p.relative_to(E)), 'plain_bytes': len(payload),
               'plain_sha256': hashlib.sha256(payload).hexdigest(),
               'gzip_path': str(p.with_suffix(p.suffix + '.gz').relative_to(E)), 'gzip_bytes': len(packed),
               'gzip_sha256': hashlib.sha256(packed).hexdigest(),
               'roundtrip': gzip.decompress(packed) == payload,
               'rows_excluding_header': len(payload.splitlines()) - 1}
    (E / 'artifacts/COMPONENT_STORAGE.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'full_remaining_P_reading_rows': len(render), 'R16_witnesses': len(witnesses), 'component_storage': receipt}))


if __name__ == '__main__':
    main()
