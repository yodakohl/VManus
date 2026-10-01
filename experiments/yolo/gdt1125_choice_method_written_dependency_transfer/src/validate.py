"""Frozen-byte, scope and complete result conservation; not meaning validation."""
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    specpath = E/'src/SPEC.json'
    spec = json.loads(specpath.read_text())
    opening = json.loads((E/'artifacts/OPEN_RECEIPT.json').read_text())
    for path, expected in spec['input_hashes'].items():
        check(sha(ROOT/path) == expected, 'Frozen byte mismatch: '+path)
    check(opening['spec_sha256'] == sha(specpath), 'Opening specification mismatch')
    sourcepath = E/'artifacts/APPLICATION_PACKET.json'
    check(opening['source_packet_sha256'] == sha(sourcepath), 'Opening source mismatch')
    source = json.loads(sourcepath.read_text())
    check({g['locus'] for g in source['groups']} == set(spec['source_loci']), 'Source-locus scope mismatch')
    check(not any(g['page'].startswith('f84') or g['page']=='f116v' for g in source['groups']), 'Excluded selector')
    ids = [g['source_group_id'] for g in source['groups']]
    check(len(ids)==len(set(ids)), 'Duplicate source IDs')
    sv = json.loads((E/'artifacts/SOURCE_VALIDATION.json').read_text())
    check(sv['status']=='PASS', 'Independent source-validation status')
    fv = json.loads((E/'artifacts/FV_TRANSFER.json').read_text())
    fw = json.loads((E/'artifacts/FW_TRANSFER.json').read_text())
    current_ids = [g['source_group_id'] for g in source['groups'] if g['unit_id'].endswith('_CURRENT')]
    check(set(r['source_id'] for r in fv['rows'])==set(current_ids), 'FV current-only row conservation')
    check(len(fv['rows'])==len(current_ids), 'FV row count')
    check(fw['raw_group_count']==len(ids), 'FW all-row count')
    check(len(fv['cases'])==6 and len(fw['pair_results'])==6, 'Missing candidate/reader case')
    expected={(side,ed) for side in ['F75V','F104V'] for ed in ['ZL3b','IT2a','RF1b']}
    check({(c['unit'].split('_')[1],c['reader']) for c in fv['cases']}==expected, 'FV case identities')
    check({(c['side'],c['reader']) for c in fw['pair_results']}==expected, 'FW case identities')
    for result in [fv,fw]:
        check(result['spec_sha256']==sha(specpath), 'Transfer specification mismatch')
        check(result['source_packet_sha256']==sha(sourcepath), 'Transfer source mismatch')
        check(result['independent_confirmation_capacity']==0, 'Improper confirmation claim')
    check(fw['semantic_validation'] is False, 'Improper semantic validation claim')
    evidence={'status':'PASS' if not errors else 'FAIL','errors':errors,'scope':'Bound byte identity, source/complete-case conservation and literal artifact accounting only; no semantic or general grammar validation.','groups':len(ids),'FV_current_groups':len(current_ids),'candidate_reader_cases':12,'confirmed_words':0,'independent_confirmation_capacity':0}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
