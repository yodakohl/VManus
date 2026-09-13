from pathlib import Path
import csv,json,hashlib,itertools,collections
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(x):return json.dumps(x,sort_keys=True,ensure_ascii=False)
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
al=rows(W/'P15/ALIGNMENT_R.tsv');events=[r for r in rows(W/'P15/EVENTS.tsv') if r['model']=='R'];assert len(al)==341 and all(r['locus'].startswith('f83r.') for r in al)
records=[];states=[];data={};reader=['# W39 vollständige vergleichende Fallfassung','P15-R-Wörter unverändert; jeder Record als möglicher eigener Fall. Vergleichspaarung und kausale Wirkung unbestätigt. 341Rohgruppen,72hypothetisch zugeordnet,269offen.']
for rec in S['source_records']:
 aa=[r for r in al if r['record']==rec];ee=[r for r in events if r['record']==rec];pos={r['locus']:i for i,r in enumerate(aa)};interventions=[r for r in ee if r['kind']!='STATE'];seq=[(r['kind'],r['patient'],r['destination']) for r in interventions];first=min((pos[r['locus']] for r in interventions),default=len(aa));last=max((pos[r['locus']] for r in interventions),default=-1)
 inp=list(dict.fromkeys({'shedy':'A','lchedy':'C','qokaiin':'B'}[r['word']] for r in aa[:first] if r['word'] in ['shedy','lchedy','qokaiin']));unknown=[r['word'] for r in aa if r['kind']=='OPEN'];endpoints=[]
 for r in ee:
  if r['kind']!='STATE':continue
  bound=r['patient']!='MISSING' and r['destination']!='MISSING';terminal=pos[r['locus']]>last
  state=dict(record=rec,locus=r['locus'],patient=r['patient'],destination=r['destination'],value='filled',bound=bound,after_last_intervention=terminal,issues=r['issues']);states.append(state)
  if bound and terminal:endpoints.append((r['patient'],r['destination'],'filled'))
 issues=[dict(locus=r['locus'],issues=r['issues']) for r in ee if r['issues']!='NONE']
 d=dict(record=rec,groups=len(aa),unknown_groups=len(unknown),input_proxy=js(inp),unknown_before_first_event=sum(r['kind']=='OPEN' for r in aa[:first]),intervention_count=len(seq),interventions=js([dict(locus=r['locus'],kind=r['kind'],patient=r['patient'],destination=r['destination'],issues=r['issues']) for r in interventions]),terminal_bound_outcomes=js(endpoints),all_event_issues=js(issues),unparsed_remainder=js(unknown));records.append(d);data[rec]=dict(seq=seq,input=inp,outcomes=endpoints,issues=issues,unknown=unknown)
 reader+=['\n## '+rec,'\nAusgangsproxy: '+js(inp)+'; unaufgelöste Vorgeschichte '+str(d['unknown_before_first_event'])+' Gruppen.','\nEingriffs-/Verlaufsfolge: '+d['interventions'],'\nSpätere gebundene Endbefunde: '+js(endpoints)]
 for loc in dict.fromkeys(r['locus'].rsplit(':',1)[0] for r in aa):
  line=[r for r in aa if r['locus'].rsplit(':',1)[0]==loc];reader+=['\n'+loc+'\n\n`'+' '.join(r['word'] for r in line)+'`','\n'+' · '.join(r['word']+' ['+r['reading']+']' for r in line)]
 def witness(a,b):
  out=[]
  if len(a)==len(b):
   ii=[i for i in range(len(a)) if a[i]!=b[i]]
   if len(ii)==1:
    i=ii[0]
    if a[i][0] in ['HEAT','DIRECT'] and b[i][0] in ['HEAT','DIRECT']:out.append(dict(edit='substitute',index=i,left=a[i],right=b[i]))
  for left,right,mode in [(a,b,'delete_left'),(b,a,'delete_right')]:
   if len(left)==len(right)+1:
    for i,x in enumerate(left):
     if x[0] in ['HEAT','DIRECT'] and left[:i]+left[i+1:]==right:out.append(dict(edit=mode,index=i,event=x))
  return out
pairs=[]
for left,right in itertools.combinations(S['source_records'],2):
 a,b=data[left],data[right];ww=witness(a['seq'],b['seq']);proxy=bool(a['input']) and a['input']==b['input'];sameout=sorted(a['outcomes'])==sorted(b['outcomes']) and bool(a['outcomes']);endpoint_pair=any(x[:2]==y[:2] for x in a['outcomes'] for y in b['outcomes']);unknown_equal=a['unknown']==b['unknown'];candidate=proxy and bool(ww) and endpoint_pair
 pairs.append(dict(left=left,right=right,input_proxy_match=proxy,left_input=js(a['input']),right_input=js(b['input']),one_explicit_intervention_witnesses=js(ww),left_intervention_count=len(a['seq']),right_intervention_count=len(b['seq']),left_outcomes=js(a['outcomes']),right_outcomes=js(b['outcomes']),paired_outcome_carrier=endpoint_pair,same_outcomes=sameout,unparsed_remainder_equal=unknown_equal,left_issues=js(a['issues']),right_issues=js(b['issues']),modeled_pair_candidate=candidate,fully_controlled_pair=False,independent_confirmation_capacity=0,interpretation='input proxy omits quantities/properties and individual identity; unknown words are not inert'))
table('RECORDS.tsv',records,list(records[0]));table('ALL_STATES.tsv',states,list(states[0]));table('ALL_PAIRS.tsv',pairs,list(pairs[0]));(E/'READING.md').write_text('\n'.join(reader)+'\n')
r=dict(idea='IDEA000192',records=7,lines=51,groups=341,pairs=len(pairs),nonempty_input_proxy_matches=sum(p['input_proxy_match'] for p in pairs),one_intervention_pair_candidates=sum(bool(json.loads(p['one_explicit_intervention_witnesses'])) for p in pairs),states=len(states),terminal_bound_states=sum(s['bound'] and s['after_last_intervention'] for s in states),paired_outcome_carriers=sum(p['paired_outcome_carrier'] for p in pairs),modeled_pair_candidates=sum(p['modeled_pair_candidate'] for p in pairs),unparsed_remainder_matches=sum(p['unparsed_remainder_equal'] for p in pairs),causal_effect_claims=0,independent_confirmation_capacity=0,new_meanings=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(js(r))
