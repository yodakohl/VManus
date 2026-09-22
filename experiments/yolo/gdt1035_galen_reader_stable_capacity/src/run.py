#!/usr/bin/env python3
"""Complete occurrence audit; unchanged source bound, no decoder."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,itertools,json,re
ROOT=Path(__file__).resolve().parents[4]; EXP=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def lcs(a,b):
 t=[[0]*(len(b)+1) for _ in range(len(a)+1)]
 for i in range(len(a)-1,-1,-1):
  for j in range(len(b)-1,-1,-1):
   t[i][j]=1+t[i+1][j+1] if a[i]==b[j] else max(t[i+1][j],t[i][j+1])
 return t

def align(a,b):
 s=lcs(a,b);p=[[0]*(len(b)+1) for _ in range(len(a)+1)]
 for i in range(len(a)):
  for j in range(len(b)):
   p[i+1][j+1]=1+p[i][j] if a[i]==b[j] else max(p[i][j+1],p[i+1][j])
 out=[]
 for i,w in enumerate(a):
  partners=[j for j,v in enumerate(b) if w==v and p[i][j]+1+s[i+1][j+1]==s[0][0]]
  forced=lcs(a[:i]+a[i+1:],b)[0][0]<s[0][0]
  status='UNIQUE_FORCED_EXACT' if forced and len(partners)==1 else 'FORCED_MULTIPLE_PARTNERS' if forced else 'OPTIONAL_EXACT' if partners else 'NO_EXACT_ALIGNMENT'
  literal=bool(re.fullmatch('[a-z]+',w))
  out.append(dict(reference_index=i+1,word=w,possible_partners=[j+1 for j in partners],forced=forced,status=status,literal=literal,qualifies=literal and status=='UNIQUE_FORCED_EXACT',optimum=s[0][0]))
 return out

def selftest():
 # Independent exhaustive matching enumeration for small synthetic strings.
 def allm(a,b,i=0,j=0):
  choices={()}
  for x in range(i,len(a)):
   for y in range(j,len(b)):
    if a[x]==b[y]:choices|={((x,y),)+z for z in allm(a,b,x+1,y+1)}
  return choices
 strings=[x for n in range(4) for x in itertools.product('ab',repeat=n)];n=0
 for a in strings:
  for b in strings:
   ms=allm(a,b);m=max(map(len,ms));best=[x for x in ms if len(x)==m]
   for i,row in enumerate(align(a,b)):
    pp=sorted({y+1 for z in best for x,y in z if x==i});f=all(any(x==i for x,y in z) for z in best)
    assert row['possible_partners']==pp and row['forced']==f
   n+=1
 assert not align(['[a:o]'],['[a:o]'])[0]['qualifies']
 return dict(status='PASS',exhaustive_string_pairs=n,uncertain_raw_group_fixture=True,target_opened=False)

def execute():
 spec=load(EXP/'src/SPEC.json');parent=ROOT/spec['parent']
 for p,h in load(parent/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 old=load(parent/'src/SPEC.json');packet=load(ROOT/spec['packet'])
 counts={p:{f:Counter() for f in ['A','B']} for p in spec['panels']}; scopes=[];allrows=[]
 assert packet.get('RF1b',[])==[]
 for rec in old['records']:
  ps={}
  for reader in ['ZL3b','IT2a']:
   selected=[]
   for p in packet[reader]:
    if p['id']!=rec['paragraph']:continue
    assert not p['page'].startswith('f84') and p['page']!='f116v';selected.append(p)
   assert len(selected)==1,(reader,rec['paragraph']);ps[reader]=selected[0]
  zz,ii=ps['ZL3b'],ps['IT2a'];assert zz['leaf']==ii['leaf'] and zz['page']==ii['page']
  assert len({x['locus'] for x in zz['lines']})==len(zz['lines'])
  assert len({x['locus'] for x in ii['lines']})==len(ii['lines'])
  it={x['locus']:x for x in ii['lines']};assert set(it)=={x['locus'] for x in zz['lines']}
  scope=dict(section=rec['section'],family=rec['family'],paragraph=rec['paragraph'],page=zz['page'],leaf=zz['leaf'],readers=ps);scopes.append(scope)
  assert sum(len(x['words']) for x in zz['lines'])==rec['groups']==zz['groups']
  assert sum(len(x['words']) for x in ii['lines'])==ii['groups']
  parent_scope=next(x for x in load(parent/'artifacts/SCOPE.json') if x['section']==rec['section'])
  assert [w for x in zz['lines'] for w in x['words']]==[x['word'] for x in parent_scope['positions']]
  for reader,panel in [('ZL3b','ZL_ALL_LITERAL_GROUPS'),('IT2a','IT_ALL_LITERAL_GROUPS')]:
   for x in ps[reader]['lines']:
    assert len(x['words'])==len(x['source_ids'])
    counts[panel][rec['family']].update(w for w in x['words'] if re.fullmatch('[a-z]+',w))
  for zl in zz['lines']:
   il=it[zl['locus']]
   for row in align(zl['words'],il['words']):
    row.update(section=rec['section'],family=rec['family'],paragraph=rec['paragraph'],locus=zl['locus'],source_id=zl['source_ids'][row['reference_index']-1],reference_line_eligible=zl['anchor_eligible'],alternate_line_eligible=il['anchor_eligible'],partner_source_ids=[il['source_ids'][j-1] for j in row['possible_partners']])
    allrows.append(row)
    if row['qualifies']:counts['UNIQUE_FORCED_COMMON'][rec['family']][row['word']]+=1
 caps=load(parent/'artifacts/WORD_DOMAINS.json')['pool_capacities'];capacity=load(parent/'artifacts/CERTIFICATE.json')['certificate']['size'];assert capacity==21
 universe=sorted({w for c in counts.values() for cc in c.values() for w in cc});tables=[];results={}
 for panel,cc in counts.items():
  rows=[]
  for w in universe:
   a,b=cc['A'][w],cc['B'][w];required=min(a,b)
   possible=[c['id'] for c in caps if c['A_capacity']>=a and c['B_capacity']>=b] if required else []
   rows.append(dict(panel=panel,word=w,A=a,B=b,required_pairs=required,possible_pools=possible,decision='EMPTY_NECESSARY_DOMAIN' if required and not possible else 'NECESSARY_DOMAIN_NONEMPTY' if required else 'NOT_SHARED'))
  k=sum(r['required_pairs'] for r in rows);empty=[r['word'] for r in rows if r['decision']=='EMPTY_NECESSARY_DOMAIN']
  results[panel]=dict(A_positions=sum(cc['A'].values()),B_positions=sum(cc['B'].values()),shared_types=sum(r['required_pairs']>0 for r in rows),required_pairs=k,capacity=capacity,empty_domains=empty,decision='REFUTED_FIXED_SHARED_CODE' if k>capacity or empty else 'NO_DECISION')
  tables+=rows
 result=dict(experiment='GDT1035',reference_positions=len(allrows),qualifying_positions=sum(r['qualifies'] for r in allrows),panels=results,confirmed_words=0,independent_readers=False,independent_meaning_capacity=0,significance_claim=False)
 for n,d in [('SCOPE.json',scopes),('ALIGNMENTS.json',allrows),('CANDIDATES.json',tables),('RESULT.json',result)]:dump(EXP/'artifacts'/n,d)
 with (EXP/'artifacts/CANDIDATES.csv').open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(tables[0]));wr.writeheader();wr.writerows([{**r,'possible_pools':'|'.join(r['possible_pools'])} for r in tables])
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:print(json.dumps(selftest()));return
 for p,h in load(EXP/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 print(json.dumps(execute()))
if __name__=='__main__':main()
