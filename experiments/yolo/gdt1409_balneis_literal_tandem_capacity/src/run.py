#!/usr/bin/env python3
"""Exact necessary source-square capacity for a nonerasing literal expansion."""
from pathlib import Path
import argparse,hashlib,itertools,json,re
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def squares(text,minimum):
 a=np.array([ord(c) for c in text],dtype=np.int32);out=[]
 for period in range(minimum,len(text)//2+1):
  mismatch=(a[:-period]!=a[period:]).astype(np.int32)
  prefix=np.concatenate((np.zeros(1,dtype=np.int32),np.cumsum(mismatch,dtype=np.int32)))
  for start in np.flatnonzero(prefix[period:]-prefix[:-period]==0):
   start=int(start);out.append((start,period))
 return sorted(out)
def brute(text,minimum):return [(i,p) for i in range(len(text)) for p in range(minimum,(len(text)-i)//2+1) if text[i:i+p]==text[i+p:i+2*p]]
def controls():
 n=0
 for L in range(13):
  for letters in itertools.product('ab',repeat=L):
   s=''.join(letters)
   for k in [1,2,6]:assert squares(s,k)==brute(s,k),(s,k);n+=1
 for text in ['abcdeXabcdeX','zzabcdeXabcdeXyy','aaaaaaaaaaaa','abcdefabcdefg','אבגדהואבגדהו','aBcdefabcdef','abcabc','']:
  assert squares(text,6)==brute(text,6)
 for values in itertools.product(['a','bc'],repeat=6):
  H=dict(zip('qokedy',values));block=''.join(H[u] for u in 'qokedy');assert len(block)>=6 and (0,len(block)) in squares(block*2,6)
 assert squares('aa',6)==[] # nulls elsewhere can make the repeated block too short
 return {'status':'PASS','binary_oracle_comparisons':n,'homomorphism_fixtures':64,'nonprimitive_squares_included':True,'null_short_block_outside_scope':True,'source_or_native_data_read':False}
def projections(s):
 path=R/s['source_path'];text=path.read_text();lines=text.splitlines(keepends=True);records=read(R/s['records_path'])
 assert sha(path)==records['source']['sha256']
 assert len(records['records'])==32 and len(records['all_header_boundaries'])==33
 offsets=[];at=0
 for line in lines:offsets.append(at);at+=len(line)
 heads={x['start_line']:x for x in records['all_header_boundaries']}
 body_offsets=[];byline={}
 for no,line in enumerate(lines,1):
  cut=0
  if no in heads or no==1:
   if no in heads:assert line.rstrip('\n')==heads[no]['header_exact']
   else:assert line.startswith('[Prologus]')
   close=line.index(']')+1;tail=line[close:];dash=re.match(r'\s*-\s*',tail)
   cut=close+(dash.end() if dash else 0)
   if not dash:assert not tail.strip(),(no,'nonempty heading tail without dash')
  chosen=list(range(offsets[no-1]+cut,offsets[no-1]+len(line)));byline[no]=chosen;body_offsets+=chosen
 selected=[];bodies=[]
 for record in records['records']:
  positions=[i for no in range(record['start_line'],record['end_line']+1) for i in byline[no]];selected+=positions;bodies.append((f"BATH_BODY_{record['record_id']:02d}",positions))
 bases=[('PUBLISHED_ALL',list(range(len(text)))),('ALL_CONTENT',body_offsets),('BATH_CONTENT',selected)]+bodies
 out=[]
 for rule in s['letter_rules']:
  for name,positions in bases:
   chars=[];origins=[]
   for i in positions:
    for c in text[i].casefold():
     if c.isalpha():chars.append({'v':'u','j':'i'}.get(c,c) if rule=='UV_IJ' else c);origins.append(i)
   normalized=''.join(chars)
   out.append({'id':rule+':'+name,'base':name,'rule':rule,'text':normalized,'source_offsets':origins,'characters':len(normalized)})
 return {'source_pin':{'path':s['source_path'],'sha256':sha(path)},'record_pin':{'path':s['records_path'],'sha256':sha(R/s['records_path'])},'projections':out}
def repeat_packet(s):
 original=read(R/s['worksheet_path'])['source_original_wrapper']['source_unit'];line=next(z for z in original['lines'] if z['metadata']['locus']=='f75v.46');pair=line['groups'][3:5]
 assert len(pair)==2 and [g[2] for g in pair]==['qokedy','qokedy']
 assert pair[0][4]==pair[1][3]=='DEFINITE_SPACE'
 assert [g[1] for g in pair]==['4','5']
 assert sum(len(x['groups']) for x in original['lines'])==77
 return {'original_source':original,'pair':pair,'required_word':'qokedy','required_units':list('qokedy'),'unit_count':6,'full_original_group_count':77}
def verifylock():
 lock=read(B/'LOCK.json')
 for p,h in lock['files'].items():assert sha(R/p)==h,p
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args();verifylock();s=read(B/'src/SPEC.json')
 if args.controls:
  x=controls();save('CONTROLS.json',x);print(json.dumps(x));raise SystemExit
 assert not(B/'artifacts/RESULT.json').exists();assert read(B/'artifacts/CONTROLS.json')['status']=='PASS'
 native=repeat_packet(s);save('NATIVE_REPEAT.json',native);p=projections(s);save('PROJECTIONS.json',p);cases=[]
 for row in p['projections']:
  hits=[]
  for start,period in squares(row['text'],s['minimum_period']):
   end=start+2*period;hits.append({'start':start,'end':end,'period':period,'block':row['text'][start:start+period],'source_start_offset':row['source_offsets'][start],'source_last_offset':row['source_offsets'][end-1]})
  cases.append({'projection_id':row['id'],'characters':row['characters'],'square_count':len(hits),'squares':hits,'decision':'SQUARE_CAPACITY_ONLY' if hits else 'NO_REQUIRED_SQUARE'})
 result={'experiment_id':'GDT1409','status':'COMPLETE_FIXED_SOURCE_SQUARE_CAPACITY','minimum_period':s['minimum_period'],'native_repeat':'qokedy qokedy','cases':cases,'word_meanings_assigned':0,'claim_ceiling':s['claim_ceiling']};save('RESULT.json',result)
 print(json.dumps({'cases':len(cases),'positive':[(r['projection_id'],r['square_count']) for r in cases if r['square_count']],'no_required_square':sum(not r['square_count'] for r in cases)},ensure_ascii=False))
