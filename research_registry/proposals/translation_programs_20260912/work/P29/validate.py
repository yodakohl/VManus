"""Independent fixed ordinal correspondence audit. No semantic truth claim."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P29')
def rr(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
src=json.loads((D/'SOURCE.json').read_text())
for p,h in src['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
history=json.loads((D/'HISTORICAL_CLAUSES.json').read_text());assert len(history)==16
assert [h['id'] for h in history]==[f'S{i:02}' for i in range(16)]
assert ' '.join(h['latin'] for h in history)+'\n'==(D/'HISTORICAL_TEXT.txt').read_text()
assert sum(h['family']=='HEAT' for h in history)==4 and sum(h['family']=='FILTER' for h in history)==3
assert 'ad ignem' in history[6]['latin'] and history[6]['family']=='HEAT'
assert not any(h['family']=='REST' for h in history)
assert 'mediam partem' in history[4]['latin'] and 'usque ad mane' in history[3]['latin']
orig=json.loads((D.parent/'P11/INPUT.json').read_text())['lines'];flat=[]
for line in orig:
 for i,w in enumerate(line['groups'],1):flat.append((line['locus'].split('.')[0],line['locus'],f'{line["locus"]}:{i}',w))
assert [(r['record'],r['line'],r['locus'],r['word']) for r in rr('INPUT.tsv')]==flat
models=json.loads((D.parent/'P05/MODELS.json').read_text());assert len(models['v01'])==len(models['v03'])==52
assert {w for w in models['v01'] if models['v01'][w]!=models['v03'][w]}=={'qotchy','qotcheaiin','shan','sy'}
materials={r['word'] for r in csv.DictReader((D.parent/'P11/COMMON_LEXICON.tsv').open(),delimiter='\t') if r['type']=='MATERIAL' and r['word'] in models['v03']}|{'odan'}
families={'chetchy':'GRIND','shytchy':'WET','chey':'CHECK','shey':'POUR','qotchy':'SIEVE','she':'REST','shot':'HEAT','cphos':'GRIND','shckhy':'MIX','otchy':'TAKE','skey':'RETAIN','cpho':'GRIND','chy':'PROCESS'}
materials-=set(families)
events=rr('TARGET_EVENTS.tsv');pairs=rr('SOURCE_TARGET_TABLE.tsv');inv=rr('ORDER_CONFLICTS.tsv');results=json.loads((D/'RESULT.json').read_text())
expected_inversions=[]
for mode,version in [('A','v03'),('R','v01')]:
 expected=[]
 for j,t in enumerate(flat):
  if t[3] not in families:continue
  fam='FILTER' if mode=='R' and t[3]=='qotchy' else families[t[3]]
  prior=[r for r in expected if r['record']==t[0] and r['family']==fam];n=len(prior)
  eligible=[h for h in history if h['family']==fam];partner=eligible[n] if n<len(eligible) else None
  prevmat=[k for k in range(j) if flat[k][0]==t[0] and flat[k][3] in materials];target=prevmat[-1] if prevmat else None
  if t[3]=='shytchy':
   target=None
   for k in range(j+1,len(flat)):
    if flat[k][1]!=t[1] or flat[k][3] in families:break
    if flat[k][3] in materials:target=k;break
  expected.append(dict(record=t[0],locus=t[2],family=fam,occurrence=str(n+1),source_partner=partner['id'] if partner else 'NONE',source_order=str(partner['order']) if partner else '-1',material=flat[target][3] if target is not None else 'NA',material_source=flat[target][2] if target is not None else 'NA'))
 actual=[e for e in events if e['mode']==mode];assert len(actual)==len(expected)==17
 for a,e in zip(actual,expected):assert all(a[k]==v for k,v in e.items()),(a,e)
 for rec in dict.fromkeys(t[0] for t in flat):
  es=[e for e in expected if e['record']==rec];paired=[e for e in es if e['source_partner']!='NONE']
  for i,a in enumerate(paired):
   for b in paired[i+1:]:
    if int(a['source_order'])>int(b['source_order']):expected_inversions.append((mode,rec,a['locus'],b['locus'],a['source_partner'],b['source_partner']))
  ps=[p for p in pairs if p['mode']==mode and p['record']==rec];assert len(ps)==16
  for h,p in zip(history,ps):
   target=next((e for e in paired if e['source_partner']==h['id']),None)
   assert p['source_id']==h['id'] and p['target_locus']==(target['locus'] if target else 'NONE')
   assert p['source_conditions']==h['conditions']
  c=results['models'][mode]['paragraphs'][rec]
  assert c['family_pairs']==len(paired) and c['source_unmatched']==16-len(paired) and c['target_unmatched']==len(es)-len(paired)
 align=rr(f'ALIGNMENT_{mode}.tsv');assert [(r['record'],r['line'],r['locus'],r['word']) for r in align]==flat
 assert sum(r['kind']=='OPEN' for r in align)==55
 assert all(r['rendering']=='⟦'+r['word']+'⟧' for r in align if r['kind']=='OPEN')
 text=(D/f'READING_{mode}.md').read_text();assert all('`'+l['raw_line']+'`' in text for l in orig)
assert [(i['mode'],i['record'],i['target_earlier'],i['target_later'],i['source_earlier_in_target'],i['source_later_in_target']) for i in inv]==expected_inversions
assert len(pairs)==128 and len(inv)==4 and results['source_identity_selected'] is False
receipt={'status':'PASS','source_hashes':len(src['inputs']),'historical_clauses':16,'source_text_reconstruction':True,'source_completeness':'manual primary-text review; hash/reconstruction is not independent manuscript collation','full_groups_per_reading':145,'independent_event_rows':34,'complete_source_target_rows':128,'independent_order_inversions':4,'checks':['all four global word revisions','prefix/forward participant binding','fixed ordinal family correspondence','every unmatched source and target event','all order conflicts','complete autonomous readings'],'limit':'Internal reproducibility, no calibrated source probability or word meaning proof.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
