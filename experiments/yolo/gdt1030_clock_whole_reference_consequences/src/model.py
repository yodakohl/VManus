TAGS='WATER RAISES FLOAT SAND_COUNTERWEIGHT DESCENDS TURNS MOTION WHEEL AXIS THIS TRANSMITS ZODIAC GREATER_OR_SMALLER PART THIS ADJUSTS HOURS SEASONS MONTH HOLES EQUINUMEROUS DAYS WHEEL MOTION BY INDEX_USUALLY_SUN MOTION FROM_HOLE TO_ANOTHER_HOLE WHILE SHOWS SPACES HOURS COMPLETES PERIOD EACH PART ZODIAC MONTH WHOLE'.split()
POSITIONS=[list(range(1,12)),list(range(12,19))+[23,24,25],[19,20,21,22,36,37,38],list(range(26,36))+[39,40]]
def compile_reading(lines,lex,c):
 words=[w for l in lines for w in l['words']];unknown=sorted(set(words)-set(lex))
 if unknown:return dict(status='UNBOUND_FORMS',unknown=unknown,groups=len(words))
 tags=[lex[w]['value'] for w in words]
 if tags!=TAGS:return dict(status='UNBOUND_WHOLE_GRAMMAR',groups=len(words),actual_tags=tags)
 wheel='Wd' if c['change']=='SECOND_WHEEL' else 'W';direction='UP' if c['change']=='WEIGHT_UP' else 'DOWN'
 rules=[(['UP:F'],direction+':C'),([direction+':C'],'TURN:X'),(['TURN:X'],'TURN:W'),(['TURN:'+wheel],'MOVE:A'),(['MOVE:A'],'ADAPT:Hh')]
 if c['actuator']=='MANUAL':rules.append((['HUMAN_REQUEST'],'STEP:I'))
 if c['actuator']=='AUTO':rules.append((['TURN:W','ADVANCE_DUE'],'STEP:I'))
 return dict(status='COMPLETE_GRAPH',candidate=c,groups=len(words),types=len(set(words)),clauses=[dict(id='C0'+str(i+1),positions=p,values=[tags[j-1] for j in p]) for i,p in enumerate(POSITIONS)],references=dict(drive_wheel='W',display_wheel=wheel,zodiac='Z',hours='Hh',month_binder='m',month_scope=['C03','C04'],motions={7:['W','e'],24:[wheel,'A(s)','e'],27:['I','Pm']}),implicit_motion_applications=1,rules=rules,weight_direction=direction,day_owner='other(m)' if c['change']=='OTHER_MONTH' else 'm',completion_scope='HISTORY_AND_EACH_STEP' if c['change']=='EACH_STEP' else 'HISTORY',solar_scope='EVERY_INSTANCE' if c['change']=='ALWAYS_SUN' else 'USUAL_KIND',rebound=c['rebound'])
def closure(seed,rules):
 known=set(seed);proof=[]
 while True:
  added=False
  for premises,result in rules:
   if set(premises)<=known and result not in known:
    known.add(result);proof.append(dict(premises=premises,result=result));added=True
  if not added:return sorted(known),proof

def evaluate(g,f):
 assert g['status']=='COMPLETE_GRAPH'
 c=g['candidate'];bad=[];seed=[]
 if f['normal'] and f['water_raises']:seed.append('UP:F')
 if f['human_request']:seed.append('HUMAN_REQUEST')
 if f['advance_due']:seed.append('ADVANCE_DUE')
 derived,proof=closure(seed,g['rules'])
 water_only,_=closure(['UP:F'] if f['normal'] and f['water_raises'] else [],g['rules'])
 facts={'UP:F':f['water_raises'],'DOWN:C':f['weight']=='DOWN','UP:C':f['weight']=='UP','TURN:X':f['axis'],'TURN:W':f['wheels']['W'],'TURN:Wd':f['wheels']['Wd'],'MOVE:A':f['part_moves'],'ADAPT:Hh':f['adjusts'],'STEP:I':f['episode_index_step']}
 for e in derived:
  if e in facts and not facts[e]:bad.append('PREDICTED_EVENT_FALSE:'+e)
 if f['normal']:
  # Explicit normal-episode source claims include the later display even when
  # a rival disconnects its drive: lack of derivation is not a negative fact.
  for e in ['UP:F',g['weight_direction']+':C','TURN:X','TURN:W','TURN:'+g['references']['display_wheel'],'MOVE:A','ADAPT:Hh']:
   if not facts[e] and 'PREDICTED_EVENT_FALSE:'+e not in bad:bad.append('SOURCE_EVENT_FALSE:'+e)
  if len(set(f['arc_extents']))<2:bad.append('NONCONSTANT_ARC_REQUIRED')
 if f['display_wheel']!=g['references']['display_wheel']:bad.append('DISPLAY_WHEEL_IDENTITY')
 if c['actuator']!='OPEN' and f['actuator']!=c['actuator']:bad.append('EXTRA_ACTUATOR_CHOICE')
 if c['duration']=='EQUAL' and f['duration']!='EQUAL':bad.append('EXTRA_EQUAL_DURATION_CHOICE')
 if f['hour_kind']!=g['references']['hours']:bad.append('SHARED_HOUR_KIND')
 if not f['usual_solar']:bad.append('USUAL_SOLAR_KIND')
 if g['solar_scope']=='EVERY_INSTANCE' and not f['instance_solar']:bad.append('UNIVERSAL_SOLAR_INSTANCE')
 comparisons=[];histories=[];names=list(f['months'])
 for name,m in f['months'].items():
  owner=next(n for n in names if n!=name) if g['day_owner']=='other(m)' else name
  days=f['months'][owner]['days'];eq=len(m['holes'])==len(days)
  comparisons.append(dict(month=name,hole_owner=name,day_owner=owner,holes=len(m['holes']),days=len(days),equal=eq))
  if not eq:bad.append('HOLES_DAYS:'+name)
  assert m['steps'] and all(t['start']<t['end'] for t in m['steps'])
  assert all(a['end']<=b['start'] for a,b in zip(m['steps'],m['steps'][1:]))
  assert m['history_end']==m['steps'][-1]['end']
  complete=m['history_end']==m['period_end'];step_complete=[]
  for i,t in enumerate(m['steps']):
   if t['origin'] not in m['holes'] or t['destination'] not in m['holes']:bad.append('STEP_MONTH_OWNER:'+name+':'+str(i))
   if t['origin']==t['destination']:bad.append('STEP_DISTINCT_ENDPOINTS:'+name+':'+str(i))
   sc=t['end']==m['period_end'];step_complete.append(sc)
   if g['completion_scope']=='HISTORY_AND_EACH_STEP' and not sc:bad.append('EACH_STEP_COMPLETION:'+name+':'+str(i))
  if not complete:bad.append('WHOLE_HISTORY_COMPLETION:'+name)
  histories.append(dict(month=name,history_complete=complete,step_complete=step_complete,step_count=len(m['steps']),completion_inferred_from_hole_count=False))
 bad=sorted(set(bad));context=[] if f['duration']=='VARIABLE' else ['PARENT_CONTEXT_VARIES_HOUR_LENGTHS']
 return dict(status='CONTRADICTED_IN_HYPOTHETICAL_WORLD' if bad else 'COMPATIBLE_IN_HYPOTHETICAL_WORLD',violations=bad,mechanical_scope='NORMAL_EPISODE' if f['normal'] else 'NOT_APPLICABLE_BROKEN_APPARATUS',derived=derived,proof=proof,water_only_derived=water_only,display_motion_from_water='DERIVED' if 'MOVE:A' in water_only else 'NOT_DERIVED',index_step_from_water='DERIVED' if 'STEP:I' in water_only else 'NOT_DERIVED',month_completion_from_water='NOT_DERIVED',comparisons=comparisons,histories=histories,full_parent_context_violations=context,full_parent_compatible=not bad and not context,actual_manuscript_observations=0)
def projection(c,name,o):
 return dict(candidate=c['id'],case=name,status=o['status'],violations='|'.join(o['violations']) or '[]',mechanical_scope=o['mechanical_scope'],display_from_water=o['display_motion_from_water'],index_from_water=o['index_step_from_water'],month_from_water=o['month_completion_from_water'],day_owners=','.join(x['month']+'->'+x['day_owner'] for x in o['comparisons']),parent_context='|'.join(o['full_parent_context_violations']) or '[]',full_parent_compatible=int(o['full_parent_compatible']),literal_values=33-len(c['rebound']),meaning_capacity=0)
