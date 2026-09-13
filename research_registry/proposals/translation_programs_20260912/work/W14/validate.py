"""Independent source eligibility and complete expected event-delta check."""
import csv,collections,json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(p):return json.loads(p.read_text())
s=js(E/'SPEC.json')
for f in s['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
flat={};lex={r['form']:r['role'] for r in rows(W/'W02/LEXICON.tsv')}
for t in js(W/'W02/SOURCE.json')['targets']:
 p=t['hosts']['ZL3b'][0];rr=[]
 for l in p['lines']:
  assert not l['locus'].startswith('f84')
  rr.extend((l['locus']+':'+str(i),l['locus'],word) for i,word in enumerate(l['words'],1))
 flat[p['id']]=rr
args=rows(W/'W05/ARGUMENTS.tsv');qualities=[q for q in rows(W/'W05/QUALITY_ASSERTIONS.tsv') if q['kind']=='STANDALONE'];eligible=set()
census={(r['grammar'],r['paragraph'],r['mention']):r for r in rows(E/'ELIGIBILITY.tsv')};assert len(census)==len(qualities)==90
for q in qualities:
 rr=flat[q['paragraph']];pos={x[0]:i for i,x in enumerate(rr)};qpos=pos[q['mention']];m=q['patient']
 ok=bool(m and qpos>0 and rr[qpos-1][0]==m and rr[qpos-1][1]==rr[qpos][1] and lex.get(rr[qpos-1][2]) in ('MATERIAL','MATERIAL_DOSE'))
 aa=[a for a in args if a['edition']=='ZL3b' and a['variant']==q['variant'] and a['paragraph']==q['paragraph'] and a['patient']==m]
 ok=ok and any(rr[pos[a['operation']]][1]==rr[qpos][1] and pos[a['operation']]<pos[m] for a in aa)
 key=(q['variant'],q['paragraph'],q['mention']);assert (census[key]['status']=='ELIGIBLE')==ok
 if ok:eligible.add(key)
assert {g for g,p,l in eligible}=={'J','M'} and {l for g,p,l in eligible}=={'f102v2.35:8'}
old={}
for r in rows(W/'W10/EVENTS.tsv'):
 if r['world'].startswith('E|ZL3b|'):old[(r['candidate'],r['world'],r['event'])]=r
new=rows(E/'EVENTS.tsv');assert len(new)==2*len(old)==4704
seen=set();changes=0;order=collections.defaultdict(list)
for r in new:
 key=(r['candidate'],r['world'],r['source_event']);before=old[key];uid=(r['timing'],)+key;assert uid not in seen;seen.add(uid)
 expected=before.copy();delta=r['timing']=='I' and '|f102v2|' in r['world'] and r['world'].split('|')[2] in ('J','M')
 expected_before=json.loads(before['before']);expected_after=json.loads(before['after'])
 if delta and r['location'] in ('f102v2.35:5','f102v2.35:6','f102v2.35:8'):
  changes+=1
  if r['kind']=='QUALITY':
   expected_before={};expected_after={'PHYSICAL:thermal':'cold'};expected.update(status='INITIAL_CONSTRAINT',state_origin='',order='56')
  else:
   expected_before['PHYSICAL:thermal']='cold'
   if r['location']=='f102v2.35:5':expected_after['PHYSICAL:thermal']='cold'
 assert json.loads(r['before'])==expected_before and json.loads(r['after'])==expected_after,(uid,r['location'])
 for k in ('kind','location','patient','object','second','assertion','status','debts','state_origin','order'):assert r[k]==expected[k],(uid,k)
 order[(r['timing'],r['candidate'],r['world'])].append(r)
assert changes==12
for (timing,c,world),rr in order.items():
 seq=[r['location'] for r in sorted(rr,key=lambda x:int(x['execution_index']))]
 if timing=='I' and '|f102v2|' in world and world.split('|')[2] in ('J','M'):assert seq.index('f102v2.35:7')<seq.index('f102v2.35:8')<seq.index('f102v2.35:5')<seq.index('f102v2.35:6')
final=rows(E/'FINAL_STATES.tsv');fm={(r['chol'],r['world'],r['timing'],r['object']):json.loads(r['state']) for r in final}
for (c,w,t,o),value in fm.items():assert value==fm[(c,w,'O' if t=='I' else 'I',o)]
base=rows(W/'W10/ALIGNMENT.tsv');out=rows(E/'ALIGNMENT.tsv');assert len(base)==len(out)==900
for a,b in zip(base,out):
 for k,v in a.items():assert b[k]==v
alt=js(W/'W02/ALTERNATE_LINES.json')['readings']
for r in rows(E/'ALTERNATE_TARGET_LINES.tsv'):
 l=next(l for l in alt[r['edition']] if l['metadata']['locus']==r['locus']);assert r['raw_line']==' '.join(g['ivtff_group_raw'] for g in l['groups'])
result={'status':'PASS','source_and_preregistration_hashes':True,'quality_census':90,'eligible_grammar_rows':2,'physical_target_loci':1,'all_event_rows_checked':len(new),'changed_rows':changes,'all_final_states_equal':True,'primary_groups':900,'semantic_validation':False,'independent_confirmation_capacity':0}
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
