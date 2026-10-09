import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def main():
    lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    raw=(P/'artifacts/OBSERVATION.json').read_bytes();o=json.loads(raw);seal=json.loads((P/'artifacts/OBSERVATION_SEAL.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==seal['sha256']
    assert o['category'] in ['YES','NO','UNCERTAIN']
    assert o['page']=='f100r' and o['target']=='GDT861 T100 first long prose baseline'
    if o['category']!='UNCERTAIN':assert o['localized'] and o['endpoint_groups_delimited']
    status={'YES':'ADJACENT_GROUP_SCOPE_CONTRADICTED','NO':'NO_COMPLETE_INTERVENING_GROUP_LOCAL','UNCERTAIN':'UNRESOLVED_ENDPOINT_GROUP_SCOPE'}[o['category']]
    r={'status':status,'category':o['category'],'observation_sha256':seal['sha256'],'claim_ceiling':'One informed local graphic judgment only; no semantic scope, native word boundary, new alphabet, independent confirmation or meaning'}
    (P/'artifacts/RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
