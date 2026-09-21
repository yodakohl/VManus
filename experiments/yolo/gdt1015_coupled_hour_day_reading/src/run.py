"""Evaluate the frozen hypothetical argument; no lexical/grammar search."""
from pathlib import Path
import json,hashlib,itertools,csv,collections
P=Path(__file__).resolve().parents[1]; A=P/'artifacts'
def read(p): return json.loads(p.read_text())
def save(n,x): (A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def check_lock():
 for f,h in read(P/'CANDIDATE_LOCK.json')['files'].items(): assert hashlib.sha256((P/f).read_bytes()).hexdigest()==h,f

def main():
 check_lock();m=read(P/'MODEL_v01.json');s=read(P/'src/SOURCE.json');lex=m['lexicon'];words=s['words']
 assert [w for r in s['records'] for w in r['raw'].split()]==words
 cursor=1
 for c in m['clauses']:
  assert c['start']==cursor and c['words']==words[c['start']-1:c['end']]
  assert c['pattern']==[lex[w]['value'] for w in c['words']];cursor=c['end']+1
 assert cursor==81 and set(lex)==set(words)
 inherited={'qokedy':'DAY','qokeedy':'HOUR','qokaiin':'RULER','lchedy':'NIGHT','cheey':'NEXT_MEMBER'}
 assert all(lex[w]['value']==v for w,v in inherited.items())
 values={'SEVEN':7,'TWENTY_FOUR':24,'THREE':3,'ONE_MEMBER':1}
 number=lambda pos:values[lex[words[pos-1]]['value']]
 n,hours,cycles=number(10),number(41),number(52)
 skips=[number(66),number(67)]
 assert (n,hours,cycles,skips)==(7,24,3,[1,1])
 remainder=hours-cycles*n; assert 0<=remainder<n
 rows=[];settings=[];names=m['arithmetic']['label_order_for_source_example']
 for candidate in m['candidates']:
  o=candidate['overrides']; night='night_direction' in o or 'night_reset' in o
  for d in (range(1,hours) if night else [None]):
   setting=candidate['id']+(f'_LIGHT{d:02d}' if d is not None else '')
   for phase in range(n):
    trace=[phase]
    for departure in range(hours):
     if o.get('night_reset') and departure+1==d: nxt=phase
     else:nxt=(trace[-1]+(-1 if o.get('night_direction')==-1 and departure>=d else 1))%n
     trace.append(nxt)
    endpoint=hours-1 if o.get('method_a_endpoint')=='last' else hours
    a=trace[endpoint]
    jump=(max(skips) if o.get('double_unit')=='same_skipped_member' else sum(skips))+1
    if o.get('selection')=='one_past_first_unskipped':jump+=1
    b=(phase+jump)%n
    c11=a==b;c12=True if o.get('comparison')=='B_B' else a==b
    source_continuity=all(y==(x+1)%n for x,y in zip(trace,trace[1:]))
    rows.append(dict(setting=setting,candidate=candidate['id'],daylight_hours=d,initial_phase=phase,
     initial_ruler=names[phase],hour_trace_indices=trace,hour_trace_names=[names[x] for x in trace],
     method_a_hour_offset=endpoint,method_a_ruler_index=a,method_a_ruler=names[a],
     method_b_steps=jump,method_b_ruler_index=b,method_b_ruler=names[b],
     complete_cycles_removed=cycles,remainder=remainder,C11_same=c11,C12_agrees=c12,
     argument_coherent=c11 and c12,source_continuous_hours=source_continuity,
     extra_scope_assumptions=candidate['grammar_changes'],new_word_changes=candidate['word_changes']))
   group=rows[-n:]
   settings.append(dict(setting=setting,candidate=candidate['id'],daylight_hours=d,
    all_phases_coherent=all(x['argument_coherent'] for x in group),passing_phases=sum(x['argument_coherent'] for x in group),
    source_continuous_hours=all(x['source_continuous_hours'] for x in group),
    source_example_A=group[0]['method_a_ruler'],source_example_B=group[0]['method_b_ruler'],
    C12_tautological=o.get('comparison')=='B_B'))
 save('ROWS.json',rows);save('SETTINGS.json',settings)
 fields=['setting','candidate','daylight_hours','all_phases_coherent','passing_phases','source_continuous_hours','source_example_A','source_example_B','C12_tautological']
 with (A/'SETTINGS.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(settings)
 candidates=[]
 for c in m['candidates']:
  ss=[r for r in settings if r['candidate']==c['id']];passes=[r for r in ss if r['all_phases_coherent']]
  candidates.append(dict(candidate=c['id'],settings=len(ss),coherent_settings=len(passes),
   coherent_daylight_counts=[r['daylight_hours'] for r in passes if r['daylight_hours'] is not None],
   failed_daylight_counts=[r['daylight_hours'] for r in ss if not r['all_phases_coherent'] and r['daylight_hours'] is not None],
   status='CONDITIONAL_COHERENCE' if len(passes)==len(ss) else 'POSSIBLE_WITH_UNBOUND_DAYLIGHT_COUNT' if passes else 'DECLARED_ARGUMENT_CONTRADICTION',
   independent_meaning_capacity=0,word_changes=c['word_changes'],grammar_changes=c['grammar_changes']))
 save('CANDIDATES.json',candidates)
 # Exhaust label permutations as symmetry, without assigning planet names to target words.
 permutations=0;comparisons=0
 for renaming in itertools.permutations(range(n)):
  permutations+=1
  for r in rows:
   assert (renaming[r['method_a_ruler_index']]==renaming[r['method_b_ruler_index']])==r['C11_same']
   comparisons+=1
 save('SYMMETRY.json',dict(label_permutations=permutations,setting_phase_comparisons=comparisons,selected_planet_names=0))
 result=dict(experiment='GDT1015',status='COMPLETE_EXPLORATORY_READING_CONSEQUENCES_CHECKED',raw_groups=len(words),types=len(lex),
  inherited_hypotheses=len(inherited),new_word_values=len(lex)-len(inherited),singleton_types=sum(v==1 for v in collections.Counter(words).values()),
  invented_clause_templates=len(m['clauses']),candidates=candidates,settings=len(settings),phase_cases=len(rows),
  coherent_settings=sum(r['all_phases_coherent'] for r in settings),label_permutations=permutations,
  confirmed_words=0,independent_meaning_capacity=0,significance=False,
  manuscript_result='All groups can be assigned one explicit repeated-word-consistent lexicon and twelve supplied templates. Meaning remains unbound.',
  calculation_result='Recorded in SETTINGS/ROWS; coherence is conditional on chosen meanings, numbers, grammar and references.')
 save('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
