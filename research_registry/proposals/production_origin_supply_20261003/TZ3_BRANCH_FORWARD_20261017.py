#!/usr/bin/env python3
"""Three source-only calls of the unchanged TZ3 partial writer; no inverse."""
from pathlib import Path
import hashlib,json
from TZ3_FORWARD_20261017 import forward
D=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
writer=D/'TZ3_FORWARD_20261017.py'
assert digest(writer)=='9d46fb662101ad642cd0dbb6b668458644b6b374f57730e2781ae892ee10e202'
r=json.loads((D/'TZ3_BRANCH_SOURCE_RECEIPT_20261017.json').read_text())
out=[]
for f in r['forms']:
    row=dict(f)
    try:row.update(status='COMPLETE_SOURCE_FORWARD_ONLY',output=forward(f['form']))
    except ValueError as e:row.update(status='UNASSIGNED_NO_COMPLETION',output=None,error=str(e))
    out.append(row)
p=D/'TZ3_FULL_PARAGRAPH_ACCOUNT_20261017.json'
a=json.loads(p.read_text())
positions=[{'source_group_id':g['source_group_id'],'raw':g['raw'],'left_separator':g['left_separator'],'right_separator':g['right_separator'],'meaning':'UNASSIGNED'} for line in a['lines'] for g in line['groups'] if g['raw']=='qokeey']
print(json.dumps({'status':'EXPLORATORY_SOURCE_CONSEQUENCE_NOT_NATIVE_VALIDATION','writer_sha256':digest(writer),'source_receipt_sha256':digest(D/'TZ3_BRANCH_SOURCE_RECEIPT_20261017.json'),'inputs':out,'old_paragraph_account_sha256':digest(p),'known_qokeey_positions_only':positions,'native_meanings_assigned':0,'limits':['nativeformsalreadyexposed; no blindprediction','noinverse/sourcepreimageselected','all120oldparagraphmeaningsstillUNASSIGNED','unassignedaisnotrepaired']},ensure_ascii=False,indent=2))
