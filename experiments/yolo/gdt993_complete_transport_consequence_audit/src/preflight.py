import datetime,json
from pathlib import Path
from model import parse_all,compile_reading,execute
from validate import regex_parses,replay
E=Path(__file__).resolve().parents[1];spec=json.loads((E/'src/SPEC.json').read_text())
v={k:vals[0] for k,vals in spec['variants'].items()}
# Constructed symbolic fixtures, never the actual63-group manuscript paragraph.
head='INIT CARGOS COLOC M HOME GOAL FAR_BANK WITHOUT_HARM HARM UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M AT_MOST_ONE BESIDES M EXAMPLE W'
move='WITH_TRIP B TAKE_OUT G'
rule='C PAIRED_WITH UNATTENDED G WOULD_BE UNSAFE'
end='THUS ALL UNHARMED THERE ATTENDED_BY M'
checks=[]
for name,text in [('one_trip_incomplete_goal',head+' '+move+' '+rule+' '+end),('duplicate_outward_trip',head+' '+move+' '+move+' '+rule+' '+end)]:
 words=text.split();ps=parse_all(words,spec);assert ps==regex_parses(words,spec) and len(ps)==1
 program=compile_reading(ps[0],v);actual=execute(program,v);expected,hazards,refs=replay(ps[0],v);assert actual==expected;assert program['hazards']==hazards and program['references']==refs
 assert not any(p['consistent'] for p in actual)
 if name=='one_trip_incomplete_goal':assert actual[0]['physical_complete'] and actual[0]['goal_reached'] is False
 else:assert actual[0]['physical_failure']['reasons']==['NO_INTERBANK_CROSSING']
 checks.append(dict(name=name,groups=len(words),status='PASS'))
for text in ['THEN UNKNOWN','WITH_TRIP M TAKE_OUT G','INIT CARGOS COLOC M']:
 assert parse_all(text.split(),spec)==regex_parses(text.split(),spec)==[]
 checks.append(dict(name='malformed:'+text,status='PASS'))
try:compile_reading(parse_all(['THEN'],spec)[0],v)
except ValueError as ex:assert str(ex)=='MISSING_OR_DUPLICATE_INITIAL'
else:raise AssertionError('missing initial accepted')
checks.append(dict(name='incomplete_paragraph_declarations',status='PASS'))
out=dict(status='PASS',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,actual_target_consequences_executed=False)
(E/'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
