#!/usr/bin/env python3
"""Independent integrity validation of the pre-score GDT277 freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def rows(p):
 with (R/p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
checks=[]
def ck(name,v):checks.append({'check':name,'pass':bool(v)});assert v,name
d=json.loads((R/'gdt277_design.json').read_text());fm=rows('gdt277_gdt276_freeze_manifest.tsv');cm=rows('gdt277_control_manifest.tsv')
ck('status_frozen',d['status']=='FROZEN_BEFORE_GDT277_SCORING');ck('five_controls',len(cm)==5==len(d['control_ids']));ck('five_worlds',len(d['instrument']['models'])==5);ck('events_4476',d['matched_view']['events']==sum(map(int,d['matched_view']['length_quotas'].values()))==4476)
ck('gdt276_files_current',all(sha(x['artifact'])==x['frozen_sha256'] for x in fm));ck('gdt276_manifest_count',len(fm)==16);ck('control_observations_current',all(sha(x['observation_input'])==x['observation_sha256'] for x in cm));ck('control_oracles_current',all(sha(x['oracle_or_pair_input'])==x['oracle_or_pair_sha256'] for x in cm));ck('oracle_not_scored',all(x['oracle_used_for_scoring']=='0' for x in cm));ck('no_f84_inputs',all('f84' not in x['observation_input'].lower() and 'f84' not in x['oracle_or_pair_input'].lower() for x in cm));ck('semantic_assignments_zero',d['semantic_assignments']==0);ck('f84_flags_false',not any(d['f84'].values()))
q=dict(d);h=q.pop('content_sha256');ck('content_hash',hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()==h)
out={'schema':'GDT277_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'design_sha256':sha('gdt277_design.json')};out['content_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt277_design_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
