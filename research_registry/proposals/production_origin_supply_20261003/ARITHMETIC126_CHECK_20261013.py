#!/usr/bin/env python3
"""Replay the extracted primary calendar arithmetic, without Voynich data."""
import hashlib
import json
from pathlib import Path
D=Path(__file__).resolve().parent
SOURCE=D/'ARITHMETIC126_SOURCE_20261013.json'
s=json.loads(SOURCE.read_text());m=s['manual_reading']

def integer(v):
    n=0
    for x in v:
        assert isinstance(x,int) and 0<=x<60
        n=60*n+x
    return n

def digits(n):
    out=[]
    for _ in range(4):
        n,r=divmod(n,60);out.append(r)
    assert n==0
    return out[::-1]

def column_add(rows):
    carry=0;out=[0]*4;trace=[]
    for j in (3,2,1,0):
        raw=sum(r[j] for r in rows)
        carry_out,out[j]=divmod(raw+carry,60)
        trace.append({'column_index':j,'raw_sum':raw,'carry_in':carry,'digit':out[j],'carry_out':carry_out})
        carry=carry_out
    assert carry==0
    return out,trace

rows=[r['normalized_vector'] for r in m['components']]
assert len(rows)==6 and all(len(r)==4 for r in rows)
for r in m['components']:
    assert r['normalized_vector']==[r['printed_orders'].get(k,0) for k in ('fourths','thirds','seconds','primes')]
whole=[integer(r) for r in rows]
total=sum(whole)
assert whole==[365250,109575,7305,2191,181,2]
assert total==1326*365+1326//4+sum([31,28,31,30,31,30])+2
c1,t1=column_add(rows)
assert c1==digits(total)==m['printed_total_in_following_canon']==[2,14,35,4]
offset=m['printed_diluvium_to_christi_era_offset']
c2,t2=column_add([c1,offset]);combined=total+integer(offset)
assert c2==digits(combined)==m['printed_total_after_adding_era_offset']==[7,29,17,43]
# Arithmetic negative control: preserve all fields except one wrong final digit.
wrong=c2[:];wrong[-1]=(wrong[-1]+1)%60
assert integer(wrong)!=combined
out={'status':'PASS_SOURCE_ARITHMETIC_ONLY','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'component_days':whole,'sum_days':total,'sum_base60':c1,'era_offset_days':integer(offset),
     'combined_days':combined,'combined_base60':c2,'day_sum_carries':t1,'era_addition_carries':t2,
     'altered_output_rejected':True,
     'scope':'Replays extracted primary numerals by whole-integer and column arithmetic; does not validate a Voynich writer, key, source identity or word meaning.'}
(D/'ARITHMETIC126_VALIDATION_20261013.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
