"""Replay fixed source attachment policies; no manuscript parser or semantics."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
rows=list(csv.DictReader((P/'FH_CONSEQUENCES.tsv').open(),delimiter='\t'))
products=[('LEAD','WHITE_LEAD'),('COPPER','VERDIGRIS')]
written_oven_type='WHITE_LEAD'
latest=products[-1][1]
all_outputs=[x[1]for x in products]
named=[x[1]for x in products if x[1]==written_oven_type]
assert latest!=written_oven_type
assert set(all_outputs)!={written_oven_type}
assert named==[written_oven_type]
assert len(rows)==6 and len({r['policy']for r in rows})==6
assert rows[2]['decision']==rows[3]['decision']=='TYPE_COMPATIBLE_IDENTITY_UNDETERMINED'
print(json.dumps({'status':'SOURCE_ATTACHMENT_POLICY_REPLAY_PASS','policies':6,'latest_generic':latest,'all_outputs':all_outputs,'named_type':named,'instance_identity_selected':False,'target_access':False,'manuscript_test_executed':False,'confirmed_words':0},indent=2))
