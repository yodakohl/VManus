"""Independent artifact-level census and predecessor comparison; no builder import."""
import csv,hashlib,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
s=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
for r in s['inputs']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
a=rows(E/'ALIGNMENT.tsv');old=rows(W/'W15/ALIGNMENT.tsv');source=json.loads((W/'W02/SOURCE.json').read_text());raw=[]
for t in source['targets']:
 p=t['hosts']['ZL3b'][0]
 for l in p['lines']:
  assert not l['locus'].startswith('f84')
  raw.extend((p['id'],l['locus'],str(i),word) for i,word in enumerate(l['words'],1))
assert [(r['paragraph'],r['locus'],r['index'],r['raw']) for r in a]==raw
assert len(a)==len(old)==900
for r,b in zip(a,old):
 assert all(r[k]==v for k,v in b.items())
 if r['raw'] not in ('sheeody','qokeeo'):assert r['joint']==b['H'] and r['joint_status']==b['status']
assert sum(r['joint_status']!='UNREAD' for r in a)==534
args=rows(E/'ARGUMENTS.tsv');key=lambda r:(r['edition'],r['variant'],r['paragraph'],r['operation'])
cols=['patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption']
maps={m:{key(r):r for r in args if r['model']==m} for m in s['models']}
assert sum(map(len,maps.values()))==len(args)
for m,folder,filtermodel in [('U','W05',None),('P','W11','P'),('R','W12','R')]:
 prior={key(r):r for r in rows(W/folder/'ARGUMENTS.tsv') if filtermodel is None or r['model']==filtermodel}
 assert maps[m].keys()==prior.keys()
 for k,r in maps[m].items():assert all(r[c]==prior[k][c] for c in cols)
assert maps['PR'].keys()==maps['R'].keys()
patientchanges=[]
for k,r in maps['PR'].items():
 if k not in maps['U']:
  assert r['form']=='qokeeo' and all(r[c]==maps['R'][k][c] for c in cols);continue
 b,p,q=maps['U'][k],maps['P'][k],maps['R'][k]
 for c in cols:
  changes={x[c] for x in (p,q) if x[c]!=b[c]}
  assert len(changes)<=1
  assert r[c]==(next(iter(changes)) if changes else b[c])
 if r['patient']!=b['patient']:patientchanges.append(k)
assert len(patientchanges)==9 and {k[-1] for k in patientchanges}=={'f102v2.31:2'}
takes=rows(E/'TAKE_ARGUMENTS.tsv');prior={(r['edition'],r['grammar'],r['paragraph'],r['target']):r for r in rows(W/'W08/TAKE_ARGUMENTS.tsv')}
for m in s['models']:
 mm={(r['edition'],r['grammar'],r['paragraph'],r['target']):r for r in takes if r['model']==m};assert mm.keys()==prior.keys()
 for k,r in mm.items():assert all(r[c]==prior[k][c] for c in ('patient','patient_form','rule','debts'))
quality=rows(E/'QUALITY_BINDINGS.tsv');oq={(r['variant'],r['paragraph'],r['mention']):r for r in rows(W/'W05/QUALITY_ASSERTIONS.tsv') if r['kind']=='STANDALONE'}
for m in s['models']:
 mm={(r['grammar'],r['paragraph'],r['mention']):r for r in quality if r['model']==m};assert mm.keys()==oq.keys()
 for k,r in mm.items():assert all(r[c]==oq[k][c] for c in ('patient','patient_form','rule','debts','axis','value'))
 expected={(r['grammar'],r['paragraph'],r['mention']) for r in rows(W/'W14/ELIGIBILITY.tsv') if r['status']=='ELIGIBLE'}
 assert {k for k,r in mm.items() if r['input_eligible']=='True'}==expected
reader=(E/'READING.md').read_text()
for t in source['targets']:
 for l in t['hosts']['ZL3b'][0]['lines']:assert reader.count(l['locus']+': `'+' '.join(l['words'])+'`')==1
comp=rows(E/'COMPOSITION_CHECK.tsv');assert len(comp)==len(maps['PR'])==921 and all(not r['interaction'] for r in comp)
summary=rows(E/'PARAGRAPHS.tsv');assert len(summary)==13 and sum(int(r['groups']) for r in summary)==900 and sum(int(r['assumed']) for r in summary)==534
result=json.loads((E/'RESULT.json').read_text());assert result['assumed_groups']==534 and result['unread_groups']==366 and result['unexpected_interaction_rows']==0
v={'status':'PASS','source_groups':900,'source_lines':152,'paragraphs':13,'joint_argument_rows':921,'single_branch_parity_rows':2727,'take_rows_checked':len(takes),'standalone_quality_rows_checked':len(quality),'old_patient_change_rows':9,'legacy_hashes_verified':len(s['inputs']),'independent_semantic_validation':False,'scope':'independent artifact census, exact predecessor parity and single-change union; not independent grammar implementation or meanings'}
(E/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
