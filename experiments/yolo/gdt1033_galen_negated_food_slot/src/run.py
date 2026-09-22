#!/usr/bin/env python3
"""Fixed exact local frame test; zero fit and zero unknown-word assignment."""
from pathlib import Path
import argparse,collections,hashlib,json,re
R=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def write(n,x):(E/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
def classify_x(x,spec):
 return 'FOOD_TYPE_POSSIBLE' if x in spec['food_forms'] else 'OPEN_TYPE' if x in spec['open_forms'] else 'FIXED_TYPE_CONFLICT' if x in spec['conflict_forms'] else 'UNKNOWN_WORD'
def extract(packet,spec,lex):
 scope=[];events=[];N=set(spec['N']);food=set(spec['food_forms']);open_=set(spec['open_forms']);bad=set(spec['conflict_forms'])
 assert len(lex)==59 and set(lex)==food|open_|bad and not(food&open_ or food&bad or open_&bad)
 for reader in spec['readers']:
  seen=set()
  for p in sorted(packet[reader],key=lambda z:z['id']):
   page=p['page'];assert not page.startswith('f84') and page not in spec['forbidden_exact']
   assert int(re.match(r'f(\d+)',page)[1])==p['leaf'];assert p['id'] not in seen;seen.add(p['id'])
   row=dict(reader=reader,paragraph=p['id'],page=page,leaf=p['leaf'],groups=p['groups'],lines=[dict(locus=l['locus'],anchor_eligible=l.get('anchor_eligible')) for l in p['lines']],category='EXCLUDED_DEVELOPMENT' if p['leaf'] in spec['exclude_leaves'] else 'IN_SCOPE');scope.append(row)
   if row['category']=='EXCLUDED_DEVELOPMENT':continue
   offset=0
   for line in p['lines']:
    ws=line['words'];ids=line['source_ids'];assert len(ws)==len(ids) and line['offset']==offset
    flag=line.get('anchor_eligible')
    if flag is True:assert all(re.fullmatch('[a-z]+',w) for w in ws)
    for j,w in enumerate(ws):
     if w!=spec['S']:continue
     frame='LONG' if j>=2 and ws[j-2] in N else 'SHORT' if j>=1 and ws[j-1] in N else 'OUTSIDE_CONTRACT'
     x=ws[j-1] if frame=='LONG' else None
     out='SOURCE_UNCERTAIN' if flag is not True else 'OUTSIDE_CONTRACT' if frame=='OUTSIDE_CONTRACT' else 'SHORT_CONTEXT_REQUIRED' if frame=='SHORT' else classify_x(x,spec)
     events.append(dict(reader=reader,paragraph=p['id'],page=page,leaf=p['leaf'],locus=line['locus'],line_position=j+1,position=offset+j+1,source_id=ids[j],window_source_ids=ids[max(0,j-2):j+1],window_words=ws[max(0,j-2):j+1],anchor_eligible=flag,frame=frame,X=x,outcome=out,parent_entry=lex.get(x)))
    offset+=len(ws)
   assert offset==p['groups']
 return scope,events
def summarize(scope,events,spec):
 readers={}
 for r in spec['readers']:
  ss=[x for x in scope if x['reader']==r];ev=[x for x in events if x['reader']==r];primary=[x for x in ev if x['outcome']!='SOURCE_UNCERTAIN'];long=[x for x in primary if x['frame']=='LONG'];c=collections.Counter(x['outcome'] for x in ev)
  status='NO_OWNED_PARAGRAPH_DATA' if not ss else 'REFUTED_FIXED_LOCAL_WRITER' if c['FIXED_TYPE_CONFLICT'] else 'CONDITIONAL_COMPATIBILITY_ONLY' if c['FOOD_TYPE_POSSIBLE'] else 'NO_TYPED_DISCRIMINATION' if long else 'NO_CAPACITY'
  readers[r]=dict(paragraphs=len(ss),development_paragraphs=sum(x['category']=='EXCLUDED_DEVELOPMENT' for x in ss),scope_paragraphs=sum(x['category']=='IN_SCOPE' for x in ss),events=len(ev),primary_events=len(primary),source_uncertain_events=c['SOURCE_UNCERTAIN'],primary_long=len(long),primary_short=sum(x['frame']=='SHORT' for x in primary),primary_outside=sum(x['frame']=='OUTSIDE_CONTRACT' for x in primary),counts=dict(c),long_leaves=sorted({x['leaf'] for x in long}),status=status)
 statuses={v['status'] for v in readers.values()}
 overall=next((out for st,out in [('REFUTED_FIXED_LOCAL_WRITER','READING_SPECIFIC_COUNTEREXAMPLE'),('CONDITIONAL_COMPATIBILITY_ONLY','CONDITIONAL_COMPATIBILITY_ONLY'),('NO_TYPED_DISCRIMINATION','NO_TYPED_DISCRIMINATION')] if st in statuses),'NO_CAPACITY')
 return dict(experiment='GDT1033',status=overall,readers=readers,confirmed_words=0,independent_meaning_confirmation=0,significance_claim=False)
def self_test(spec,lex):
 def p(words,flag=True,page='f10r',leaf=10):return dict(id=page+'|fixture',page=page,leaf=leaf,groups=len(words),lines=[dict(locus=page+'.1',anchor_eligible=flag,offset=0,words=words,source_ids=[str(i) for i in range(len(words))])])
 def execute(par):return extract({'ZL3b':[par],'IT2a':[],'RF1b':[]},spec,lex)
 count=0
 for n in spec['N']:
  for x in lex:
   literal=bool(re.fullmatch('[a-z]+',x));a,b=execute(p([n,x,'lshedy'],literal));e=b[-1];assert e['frame']=='LONG' and e['X']==x
   want='FOOD_TYPE_POSSIBLE' if x in spec['food_forms'] else 'OPEN_TYPE' if x in spec['open_forms'] else 'FIXED_TYPE_CONFLICT'
   assert classify_x(x,spec)==want;assert e['outcome']==(want if literal else 'SOURCE_UNCERTAIN');count+=1
 for words,flag,want in [(['or','newword','lshedy'],True,'UNKNOWN_WORD'),(['or','lshedy'],True,'SHORT_CONTEXT_REQUIRED'),(['lshedy'],True,'OUTSIDE_CONTRACT'),(['or','qoky','lshedy'],False,'SOURCE_UNCERTAIN'),(['or','qoky','lshedy'],1,'SOURCE_UNCERTAIN'),(['or','qoky','lshedy'],None,'SOURCE_UNCERTAIN')]:
  _,b=execute(p(words,flag));assert b[0]['outcome']==want;count+=1
 q=p(['or','shedy','lshedy']);q['lines']=[dict(locus='f10r.1',anchor_eligible=True,offset=0,words=['or','shedy'],source_ids=['1','2']),dict(locus='f10r.2',anchor_eligible=True,offset=2,words=['lshedy'],source_ids=['3'])];_,b=execute(q);assert b[0]['outcome']=='OUTSIDE_CONTRACT';count+=1
 q=p([],page='f76v',leaf=76);q['lines']=[dict(locus='f76v.1',anchor_eligible=True,words=None)];assert execute(q)[1]==[];count+=1
 for page,leaf in [('f84',84),('f84r',84),('f84v',84),('f116v',116)]:
  q=p([],page=page,leaf=leaf);q['lines']=[dict(locus=page+'.1',words=None)]
  try:execute(q)
  except AssertionError:pass
  else:raise AssertionError('sealed guard missed')
  count+=1
 return dict(status='PASS',fixture_cases=count,corpus_read=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args();spec=load(E/'src/SPEC.json');par=load(R/spec['lexicon']['path']);lex={x['form']:x for x in par['frozen_parent_lexicon']+par['new_lexicon']}
 if args.self_test:print(json.dumps(self_test(spec,lex)));return
 for p,h in load(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 scope,events=extract(load(R/spec['packet']['path']),spec,lex);result=summarize(scope,events,spec)
 write('SCOPE.json',scope);write('EVENTS.json',events);write('RESULT.json',result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
