# Same-author independent declarative predictions; never imports model/executor.
REV='WHOLE MONTH ZODIAC PART EACH PERIOD COMPLETES HOURS SPACES SHOWS WHILE TO_ANOTHER_HOLE FROM_HOLE MOTION INDEX_USUALLY_SUN BY MOTION WHEEL DAYS EQUINUMEROUS HOLES MONTH SEASONS HOURS ADJUSTS THIS PART GREATER_OR_SMALLER ZODIAC TRANSMITS THIS AXIS WHEEL MOTION TURNS DESCENDS SAND_COUNTERWEIGHT FLOAT RAISES WATER'.split()
AUTO_CASES={'BASE_AUTO_VARIABLE','BASE_AUTO_EQUAL','NO_INDEX_STEP_DUE','NO_INDEX_STEP_NOT_DUE'}
EQUAL_CASES={'BASE_MANUAL_EQUAL','BASE_AUTO_EQUAL'}
def compile_reverse(lines,lex):
 words=[w for l in lines for w in l['words']]
 if any(w not in lex for w in words):return 'UNBOUND_FORMS'
 return 'COMPLETE_GRAPH' if [lex[w]['value'] for w in words[::-1]]==REV else 'UNBOUND_WHOLE_GRAMMAR'
def prediction(c,n):
 bad=[];change=c['change'];second=change=='SECOND_WHEEL';normal=n!='BROKEN_NOT_NORMAL'
 if normal:
  actual_up=n=='WEIGHT_UP';requires_up=change=='WEIGHT_UP'
  if actual_up!=requires_up:bad.append('PREDICTED_EVENT_FALSE:'+('UP:C' if requires_up else 'DOWN:C'))
  if n=='AXIS_STOPPED':bad.append('PREDICTED_EVENT_FALSE:TURN:X')
  if n=='DRIVE_WHEEL_STOPPED':bad.append('PREDICTED_EVENT_FALSE:TURN:W')
  if n=='PART_STILL':bad.append(('SOURCE_EVENT_FALSE:' if second else 'PREDICTED_EVENT_FALSE:')+'MOVE:A')
  if n=='ADJUSTMENT_ABSENT':bad.append(('SOURCE_EVENT_FALSE:' if second else 'PREDICTED_EVENT_FALSE:')+'ADAPT:Hh')
  if n=='CONSTANT_ARC':bad.append('NONCONSTANT_ARC_REQUIRED')
 if (n=='OTHER_DISPLAY_WHEEL')!=second:bad.append('DISPLAY_WHEEL_IDENTITY')
 if c['actuator']!='OPEN' and (c['actuator']=='AUTO')!=(n in AUTO_CASES):bad.append('EXTRA_ACTUATOR_CHOICE')
 if c['actuator']=='AUTO' and n=='NO_INDEX_STEP_DUE':bad.append('PREDICTED_EVENT_FALSE:STEP:I')
 if c['duration']=='EQUAL' and n not in EQUAL_CASES:bad.append('EXTRA_EQUAL_DURATION_CHOICE')
 if n=='WRONG_HOUR_KIND':bad.append('SHARED_HOUR_KIND')
 if n=='USUAL_SOLAR_FALSE':bad.append('USUAL_SOLAR_KIND')
 if change=='ALWAYS_SUN' and n=='NONSOLAR_INSTANCE':bad.append('UNIVERSAL_SOLAR_INSTANCE')
 if change=='OTHER_MONTH':
  if n not in ['EQUAL_MONTH_SIZES','CROSS_MONTH_SIZES']:
   bad.append('HOLES_DAYS:A')
   if n!='HOLE_DAY_MISMATCH':bad.append('HOLES_DAYS:B')
 else:
  if n=='HOLE_DAY_MISMATCH':bad.append('HOLES_DAYS:A')
  if n=='CROSS_MONTH_SIZES':bad+=['HOLES_DAYS:A','HOLES_DAYS:B']
 if n=='STEP_WRONG_MONTH_HOLE':bad.append('STEP_MONTH_OWNER:A:0')
 if n=='STEP_SAME_HOLE':bad.append('STEP_DISTINCT_ENDPOINTS:A:0')
 if n=='HISTORY_ENDS_EARLY':bad.append('WHOLE_HISTORY_COMPLETION:A')
 if change=='EACH_STEP' and n!='SINGLE_STEP_MONTH':bad+=['EACH_STEP_COMPLETION:A:0','EACH_STEP_COMPLETION:B:0']
 bad=sorted(set(bad));ctx=n in EQUAL_CASES
 return dict(candidate=c['id'],case=n,status='CONTRADICTED_IN_HYPOTHETICAL_WORLD' if bad else 'COMPATIBLE_IN_HYPOTHETICAL_WORLD',violations='|'.join(bad) or '[]',mechanical_scope='NORMAL_EPISODE' if normal else 'NOT_APPLICABLE_BROKEN_APPARATUS',display_from_water='DERIVED' if normal and not second else 'NOT_DERIVED',index_from_water='NOT_DERIVED',month_from_water='NOT_DERIVED',day_owners='A->B,B->A' if change=='OTHER_MONTH' else 'A->A,B->B',parent_context='PARENT_CONTEXT_VARIES_HOUR_LENGTHS' if ctx else '[]',full_parent_compatible=int(not bad and not ctx),literal_values=33-len(c['rebound']),meaning_capacity=0)
def validate_graph(g,s):
 assert g['groups']==40 and g['types']==33 and g['status']=='COMPLETE_GRAPH'
 assert sorted(p for c in g['clauses'] for p in c['positions'])==list(range(1,41))
 for a,b in zip(g['clauses'],s['whole_paragraph_productions']):assert a['id']==b['id'] and a['positions']==b['positions'] and a['values']==b['value_sequence']
 assert g['references']['month_scope']==['C03','C04'] and g['implicit_motion_applications']==1
 assert g['references']['motions'][27 if 27 in g['references']['motions'] else '27']==['I','Pm']
 assert g['references']['zodiac']=='Z' and g['references']['hours']=='Hh'
 assert g['references']['drive_wheel']=='W'
 assert g['references']['display_wheel']==('Wd' if g['candidate']['change']=='SECOND_WHEEL' else 'W')
def validate_output(g,f,o):
 seed=set()
 if f['normal'] and f['water_raises']:seed.add('UP:F')
 if f['human_request']:seed.add('HUMAN_REQUEST')
 if f['advance_due']:seed.add('ADVANCE_DUE')
 for p in o['proof']:
  assert (p['premises'],p['result']) in [(r[0],r[1]) for r in g['rules']]
  assert set(p['premises'])<=seed and p['result'] not in seed
  seed.add(p['result'])
 assert sorted(seed)==o['derived']
 for premises,result in g['rules']:
  if set(premises)<=seed:assert result in seed
 assert o['month_completion_from_water']=='NOT_DERIVED'
 assert len(o['comparisons'])==len(o['histories'])==2
 for q in o['comparisons']:
  a=f['months'][q['month']];b=f['months'][q['day_owner']]
  assert q['holes']==len(a['holes']) and q['days']==len(b['days']) and q['equal']==(q['holes']==q['days'])
 for h in o['histories']:
  m=f['months'][h['month']]
  assert h['history_complete']==(m['history_end']==m['period_end'])
  assert h['step_complete']==[t['end']==m['period_end'] for t in m['steps']]
  assert h['completion_inferred_from_hole_count'] is False
 assert o['actual_manuscript_observations']==0
