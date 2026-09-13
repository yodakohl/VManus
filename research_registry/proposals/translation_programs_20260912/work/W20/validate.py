"""Independent source census and prescribed one-action patient replacement."""
import csv,hashlib,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
s=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
for f in s['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
lex={r['form']:r['role'] for r in rows(W/'W02/LEXICON.tsv')};lex.update({w:o['role'] for w,o in read(W/'W05/SPEC.json')['word_overrides'].items()});lex.update(sheeody='MATERIAL',qokeeo='ACTION');assert lex['cho']=='REGION'
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];flats={};targetset=set()
for ed,ll in alt.items():
 lines={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84')
   if ed=='ZL3b':assert lines[loc]==line['words']
   flat.extend((loc+':'+str(i),w) for i,w in enumerate(lines[loc],1))
  flats[(ed,p['id'])]=flat
  targetset.update((ed,p['id'],loc) for loc,w in flat if w=='r')
base=[r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'];key=lambda r:(r['edition'],r['paragraph'],r.get('grammar',r.get('variant')),r['operation']);bm={key(r):r for r in base};overrides={}
targets=rows(E/'TARGETS.tsv');assert len(targets)==36 and {(r['edition'],r['paragraph'],r['target']) for r in targets}==targetset
for r in targets:
 ed,p,g=r['edition'],r['paragraph'],r['grammar'];flat=flats[(ed,p)];pos={loc:i for i,(loc,w) in enumerate(flat)};words=dict(flat);off=pos[r['target']];aa=[a for a in base if (a['edition'],a['paragraph'],a['variant'])==(ed,p,g)]
 previous=sorted((pos[a['operation']],a) for a in aa if pos[a['operation']]<off);following=sorted((pos[a['operation']],a) for a in aa if pos[a['operation']]>off);materials=[loc for loc,w in flat[:off] if lex.get(w) in ('MATERIAL','MATERIAL_DOSE')]
 prev=previous[-1][1];nxt=following[0][1];anchor=materials[-1]
 assert r['prior_action']==prev['operation'] and r['next_action']==nxt['operation'] and r['P_material']==anchor
 assert r['old_patient']==nxt['patient'] and r['new_patient']==anchor and r['new_form']==words[anchor]
 order=lambda a:(max(pos[a[k]] for k in ('operation','patient','coingredient') if a[k]),pos[a['operation']])
 assert r['T_order']==('ALREADY_ORDERED' if order(prev)<order(nxt) else 'ORDER_CONFLICT')
 k=(ed,p,g,nxt['operation'])
 if k in overrides:assert overrides[k]==anchor
 overrides[k]=anchor
out=rows(E/'ARGUMENTS.tsv');assert len(out)==len(base)*2==1842
for model in ['T','P']:
 mm={key(r):r for r in out if r['model']==model};assert mm.keys()==bm.keys()
 for k,r in mm.items():
  old=bm[k]
  for col in ['edition','paragraph','variant','operation','form','meaning','coingredient','shared_run']:assert r[col]==old[col]
  assert r['patient']==(overrides.get(k,old['patient']) if model=='P' else old['patient'])
  if model=='T' or k not in overrides:assert all(r[c]==v for c,v in old.items() if c!='model')
expectedfuture=set()
for r in targets:
 pos={loc:i for i,(loc,w) in enumerate(flats[(r['edition'],r['paragraph'])])}
 for a in out:
  if (a['edition'],a['paragraph'],a['variant'])==(r['edition'],r['paragraph'],r['grammar']) and pos[a['operation']]>pos[r['target']]:expectedfuture.add((a['edition'],a['paragraph'],a['variant'],a['model'],r['target'],a['operation'],a['patient']))
f=rows(E/'FUTURES.tsv');assert len(f)==len(expectedfuture)==528 and {(r['edition'],r['paragraph'],r['grammar'],r['model'],r['target'],r['operation'],r['patient']) for r in f}==expectedfuture
q=rows(E/'QUALITY_BINDINGS.tsv');assert len(q)==180 and all(r['old_patient']==r['new_patient'] for r in q)
groups=collections.defaultdict(set)
for a in out:
 if a['shared_run']:groups[(a['edition'],a['paragraph'],a['variant'],a['model'],a['shared_run'])].add(a['patient'])
assert all(len(v)==1 for v in groups.values()) and not rows(E/'SHARED_GROUP_CONFLICTS.tsv')
reader=(E/'READING.md').read_text()
for t in source['targets']:
 for line in t['hosts']['ZL3b'][0]['lines']:assert reader.count(line['locus']+': `'+' '.join(line['words'])+'`')==1
assert all(bm[k]['patient'] for k in overrides)
v={'status':'PASS','source_r_mentions':len(targetset),'candidate_rows':36,'action_rows':1842,'all_future_rows':528,'unique_overridden_actions':len(overrides),'primary_r_mentions':5,'alternate_r_mentions':{'IT2a':3,'RF1b':4},'legacy_files_verified':len(s['inputs']),'scope':'independent raw target and binding/future census; quality patient preservation only, not new semantic evidence'}
(E/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
