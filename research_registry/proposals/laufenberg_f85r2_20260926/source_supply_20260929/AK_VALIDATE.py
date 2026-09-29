#!/usr/bin/env python3
"""Replay source identities and complete-unit label inventory, not meanings."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
receipt=json.loads((HERE/'AK_INPUTS.json').read_text())
checks=[]
for row in receipt['files']:
 checks.append({'check':'sha256 '+row['path'],'pass':hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']})
source=json.loads((HERE/'AG_COMPLETE_FREE.json').read_text())
account=json.loads((HERE/'AK_LABEL_ACCOUNT.json').read_text())
old=set('olkain qol sheedy qokeor qokal or qokar ol chey aiin qokeey qoqokeey'.split())
new=set(account['new_values'])
for unit, expected in zip(source['units'],account['readers']):
 forms=[g[2] for line in unit['lines'] for g in line['groups']]
 actual={'groups':len(forms),'old_label_positions':sum(f in old for f in forms),'new_label_positions':sum(f in new for f in forms),'any_label_positions':sum(f in old|new for f in forms),'no_label_positions':sum(f not in old|new for f in forms)}
 checks.append({'check':'inventory '+expected['edition'],'pass':all(expected[k]==v for k,v in actual.items()),'actual':actual})
result={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','kind':'Source identity and complete-inventory arithmetic only; not semantic validation','check_count':len(checks),'checks':checks,'unknown_total':sum(r['no_label_positions'] for r in account['readers']),'semantic_tests':0}
(HERE/'AK_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
raise SystemExit(0 if result['status']=='PASS' else 1)
