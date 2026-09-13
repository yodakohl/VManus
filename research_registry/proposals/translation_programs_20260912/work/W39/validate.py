from pathlib import Path
import csv,json,hashlib,itertools,collections
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
lex=json.loads((W/'P15/MODEL.json').read_text())['whole_word_hypotheses'];source=rows(W/'P12/PROSE.tsv');al=rows(W/'P15/ALIGNMENT_R.tsv');ev=[x for x in rows(W/'P15/EVENTS.tsv') if x['model']=='R'];R=rows(E/'RECORDS.tsv');P=rows(E/'ALL_PAIRS.tsv');T=rows(E/'ALL_STATES.tsv');reader=(E/'READING.md').read_text()
raw=[]
for line in source:
 assert line['page']=='f83r' and line['locus'].startswith('f83r.')
 words=line['zl3b_line'].split();raw.extend((line['record_id'],line['locus']+':'+str(i),w) for i,w in enumerate(words,1));assert reader.count('`'+line['zl3b_line']+'`')==1
assert raw==[(x['record'],x['locus'],x['word']) for x in al] and len(raw)==341 and len(source)==51
D={};expectedstates=[]
for r in R:
 rec=r['record'];aa=[x for x in al if x['record']==rec];ee=[x for x in ev if x['record']==rec];pos={x['locus']:i for i,x in enumerate(aa)};ops=[x for x in ee if x['word']!='qokedy'];first=min((pos[x['locus']] for x in ops),default=len(aa));last=max((pos[x['locus']] for x in ops),default=-1)
 inp=[]
 for x in aa[:first]:
  if x['word'] in ['shedy','qokaiin','lchedy']:
   v={'shedy':'A','qokaiin':'B','lchedy':'C'}[x['word']]
   if v not in inp:inp.append(v)
 unknown=[x['word'] for x in aa if x['word'] not in lex];assert len(aa)==int(r['groups']) and json.loads(r['input_proxy'])==inp and json.loads(r['unparsed_remainder'])==unknown
 assert int(r['unknown_before_first_event'])==sum(x['word'] not in lex for x in aa[:first])
 assert int(r['intervention_count'])==len(ops)
 for x in ee:
  if x['word']=='qokedy':expectedstates.append((rec,x['locus'],x['patient'],x['destination'],str(x['patient']!='MISSING' and x['destination']!='MISSING'),str(pos[x['locus']]>last),x['issues']))
 endpoints=[(x['patient'],x['destination'],'filled') for x in ee if x['word']=='qokedy' and x['patient']!='MISSING' and x['destination']!='MISSING' and pos[x['locus']]>last];assert json.loads(r['terminal_bound_outcomes'])==[list(x) for x in endpoints]
 D[rec]=dict(seq=[(x['kind'],x['patient'],x['destination']) for x in ops],input=inp,unknown=unknown,endpoints=endpoints)
assert collections.Counter(expectedstates)==collections.Counter(tuple(r[k] for k in ['record','locus','patient','destination','bound','after_last_intervention','issues']) for r in T)
assert {(p['left'],p['right']) for p in P}==set(itertools.combinations(S['source_records'],2)) and len(P)==21
for p in P:
 a,b=D[p['left']],D[p['right']];x,y=a['seq'],b['seq'];expected=[]
 # Separate direct reconstruction of all edit sites.
 for i in range(max(len(x),len(y))):
  if len(x)==len(y) and i<len(x) and x[i]!=y[i] and x[i][0] in ['HEAT','DIRECT'] and y[i][0] in ['HEAT','DIRECT'] and all(x[j]==y[j] for j in range(len(x)) if j!=i):expected.append(dict(edit='substitute',index=i,left=list(x[i]),right=list(y[i])))
  if len(x)==len(y)+1 and i<len(x) and x[i][0] in ['HEAT','DIRECT'] and tuple(y)==tuple(v for j,v in enumerate(x) if j!=i):expected.append(dict(edit='delete_left',index=i,event=list(x[i])))
  if len(y)==len(x)+1 and i<len(y) and y[i][0] in ['HEAT','DIRECT'] and tuple(x)==tuple(v for j,v in enumerate(y) if j!=i):expected.append(dict(edit='delete_right',index=i,event=list(y[i])))
 assert json.loads(p['one_explicit_intervention_witnesses'])==expected
 assert p['input_proxy_match']==str(bool(a['input']) and a['input']==b['input'])
 assert p['unparsed_remainder_equal']==str(a['unknown']==b['unknown'])
 assert not a['endpoints'] and not b['endpoints'] and p['paired_outcome_carrier']=='False' and p['modeled_pair_candidate']=='False'
res=json.loads((E/'RESULT.json').read_text());assert res['one_intervention_pair_candidates']==2 and res['nonempty_input_proxy_matches']==0 and res['terminal_bound_states']==0 and len(T)==13
out=dict(status='PASS',bound_files=len(S['inputs']),groups=341,records=7,pairs=21,all_one_edit_sites_verified=True,all_state_positions=13,terminal_bound_states=0,complete_reader=True,limits='Independent pair/coverage audit; inherited lexicon/references remain hypotheses, no independent semantic validation')
(E/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
