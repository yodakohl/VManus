"""Reproduce the separately authorized literal diagnostic; original FAIL persists."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
ADJUDICATION_SHA = '3bde00fdbe030b1aa0332a16c33425ab54e04012150d92e1f0d5da21b833d2fa'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path = E/'artifacts/SOURCE_ADJUDICATION.json'
    if sha(path) != ADJUDICATION_SHA:
        raise SystemExit('Exact adjudication evidence required')
    adjudication = json.loads(path.read_text())
    for name, expected in adjudication['protected_artifact_pins'].items():
        if sha(ROOT/name) != expected:
            raise SystemExit('Protected original artifact changed: '+name)
    original = json.loads((E/'artifacts/SOURCE_VALIDATION.json').read_text())
    if original['status'] != 'FAIL_SOURCE_REPRESENTATION' or [e['kind'] for e in original['errors']] != ['FORMAL_SUMMARY']:
        raise SystemExit('Different original failure; no diagnostic authorization')
    if not all(c['match'] for c in adjudication['per_value_comparison']):
        raise SystemExit('Actual source summary mismatch')
    for name in ['apply_fv.py','apply_fw.py']:
        subprocess.run([sys.executable,str(E/'src'/name)],cwd=ROOT,check=True)
    specpath=E/'src/SPEC.json'
    spec=json.loads(specpath.read_text())
    for name, expected in spec['input_hashes'].items():
        if sha(ROOT/name) != expected:
            raise SystemExit('Frozen input changed: '+name)
    fv=json.loads((E/'artifacts/FV_TRANSFER.json').read_text())
    fw=json.loads((E/'artifacts/FW_TRANSFER.json').read_text())
    packet=json.loads((E/'artifacts/APPLICATION_PACKET.json').read_text())
    current=[g['source_group_id'] for g in packet['groups'] if g['unit_id'].endswith('_CURRENT')]
    checks={'FV_current_only_rows':len(fv['rows'])==len(current) and set(r['source_id'] for r in fv['rows'])==set(current),'FW_all_rows':fw['raw_group_count']==len(packet['groups']),'all12cases':len(fv['cases'])==len(fw['pair_results'])==6,'original_FAIL_retained':sha(E/'artifacts/SOURCE_VALIDATION.json')==adjudication['protected_artifact_pins'][str((E/'artifacts/SOURCE_VALIDATION.json').relative_to(ROOT))],'no_semantic_PASS':fw['semantic_validation'] is False,'independent_capacity_zero':fv['independent_confirmation_capacity']==fw['independent_confirmation_capacity']==0}
    evidence={'status':'DIAGNOSTIC_REPRODUCTION_PASS' if all(checks.values()) else 'DIAGNOSTIC_REPRODUCTION_FAIL','checks':checks,'registered_source_gate':'FAIL_SOURCE_REPRESENTATION','registered_validation':'FAIL','scope':'Frozen-byte, literal case/row and unchanged-model reproduction only; no restored registered, grammar or semantic PASS.','confirmed_words':0,'independent_confirmation_capacity':0}
    (E/'artifacts/DIAGNOSTIC_VALIDATION.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence))
    return 0 if all(checks.values()) else 1


if __name__=='__main__':
    raise SystemExit(main())
