"""Independent regex/table reader for known-source teaching streams."""
import collections,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def independent_read(s):
 palette='aoeindqysrlmktp';digits=palette[:7];literal='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -';lookup={digits[j//7]+digits[j%7]:c for j,c in enumerate(literal)}
 h,f,g,a,t,k,z,end=palette[7:];s=re.sub('[ \t\r\n]','',s)
 if not s or any(c not in palette for c in s):raise ValueError('alphabet')
 dc='['+digits+']+';pattern=re.compile(re.escape(h)+re.escape(f).join('('+dc+')' for _ in range(5))+re.escape(g)+'((?:'+a+t+'*'+k+t+'*'+z+')+)'+end);rowpat=re.compile(a+'('+t+'*)'+k+'('+t+'*)'+z)
 pos=0;out=[]
 while pos<len(s):
  m=pattern.match(s,pos)
  if not m:raise ValueError('frame')
  fields=[]
  for payload in m.groups()[:5]:
   if len(payload)%2:raise ValueError('odd')
   try:value=''.join(lookup[payload[i:i+2]] for i in range(0,len(payload),2))
   except KeyError:raise ValueError('literal')
   if not value or all(c==' ' for c in value):raise ValueError('empty')
   fields.append(value)
  if fields[0]==fields[1] or re.fullmatch('0|[1-9][0-9]{0,3}',fields[4]) is None:raise ValueError('header')
  total=int(fields[4]);rows=[[len(q[0]),len(q[1])] for q in rowpat.findall(m.group(6))]
  if not rows or any(sum(q)!=total for q in rows):raise ValueError('total')
  b=dict(zip(['left','right','batch','unit'],fields[:4]));b.update(total=total,rows=rows);out.append(b);pos=m.end()
 return out

def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 spec=json.loads((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json').read_text());assert ''.join(spec['signs'][:15])=='aoeindqysrlmktp' and len(spec['signs'])==22
 r=json.loads((B/'artifacts/RESULT.json').read_text());source=json.loads((B/'src/FIXTURES.json').read_text());assert r['fixtures']==source and independent_read(r['encoded_stream'])==source and independent_read(r['wrapped_24'])==source
 assert all(len(x)<=24 for x in r['wrapped_24'].splitlines());assert ''.join(r['wrapped_24'].splitlines())==r['encoded_stream']
 cases=json.loads((B/'artifacts/CASES.json').read_text());assert len(cases)==13;totalrows=0
 for n,c in enumerate(cases):
  assert c['source']['total']==n and c['source']['rows']==[[a,n-a] for a in range(n+1)] and independent_read(c['encoded'])==[c['source']]
  rows=c['row_strings'];assert rows==['l'+'m'*a+'k'+'m'*(n-a)+'t' for a in range(n+1)] and len(set(rows))==n+1 and all(len(x)==n+3 for x in rows)
  signatures={tuple(sorted(collections.Counter(x[i-1:i+1] for i in range(1,len(x))).items())) for x in rows[1:-1]};assert len(signatures)<=1;totalrows+=len(rows)
 invalid=json.loads((B/'artifacts/INVALID_CASES.json').read_text());assert len(invalid)==11
 for c in invalid:
  try:independent_read(c['encoded'])
  except ValueError:pass
  else:raise AssertionError(c['name'])
 changes=json.loads((B/'artifacts/CONTENT_CHANGES.json').read_text())
 for c in changes.values():assert independent_read(c['encoded'])==[c['source']]
 for b,c in zip(source,r['costs']):
  header=2*(sum(len(b[k]) for k in ['left','right','batch','unit'])+len(str(b['total'])))+6;rows=len(b['rows'])*(b['total']+3);assert c=={'header':header,'rows':rows,'END':1,'total':header+rows+1}
 assert sum(c['total'] for c in r['costs'])==len(r['encoded_stream']);assert r['source_blocks']==3 and r['source_rows']==11 and r['exhaustive_allocations']==totalrows==91 and r['sign_slots_used']==15 and r['native_status']=='NO_NATIVE_BINDING_NO_STATISTICAL_FIT'
 v={'status':'PASS_SOURCE_KNOWN_MODULE_ONLY','fixture_blocks':3,'fixture_rows':11,'exhaustive_allocations':91,'malformed_streams_rejected':11,'total_fixture_units':len(r['encoded_stream']),'method':'Independentregexheader/rowparserandliteralcodetable,fullsourceandcostcomparisons;no primaryimport.','limits':'No nativeworddecoding,statisticalfit,historicalattestationorfullprosegrammar.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
if __name__=='__main__':main()
