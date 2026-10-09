"""Key-free necessary bounds; no fitting, native meanings or source substitution."""
import gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def save(name,x):(A/(name+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digits(v,b):
 if v==0:return [0]
 out=[]
 while v:v,d=divmod(v,b);out.append(d)
 return out[::-1]
def integer(ds,b):
 v=0
 for d in ds:v=v*b+d
 return v
def min_base(threshold,power):
 lo,hi=1,2
 while hi**power<=threshold:hi*=2
 while hi-lo>1:
  mid=(lo+hi)//2
  if mid**power<=threshold:lo=mid
  else:hi=mid
 return hi
def fixtures():
 checked=0
 for n in range(3,6):
  for k in range(1,6):
   for v in range(n**k):
    src=digits(v,n);src=[0]*(k-len(src))+src
    r=max(len(list(g)) for _,g in itertools.groupby(src));out=digits(v,3)
    assert integer(out,3)==v and v<n**k
    for s in [1,2]:
     if len(out)<=s:assert k<=r+s
    if len(out)>=2:assert n**(r+len(out))>3**(len(out)-1)
    checked+=1
 # A final END=0 block has padding zeros not present in source.
 source=[1,2,1,2,1];k=5;end=0;packed=source+[end]+[0]*4
 groups=[digits(integer(packed[i:i+k],3),3) for i in range(0,len(packed),k)]
 assert groups[-1]==[0] and max(len(list(g)) for _,g in itertools.groupby(source))==1 and k>1+1
 # Exhaustive short source messages, including encoded spaces (digit1), with
 # END=0 and END=3; exact k padding/readback, no disappearing boundaries.
 roundtrips=0
 for end in [0,3]:
  alphabet=[x for x in range(4) if x!=end]
  for length in range(6):
   for src in itertools.product(alphabet,repeat=length):
    for k in range(1,5):
     padded=list(src)+[end];padded += [0]*((-len(padded))%k)
     out=[digits(integer(padded[i:i+k],4),3) for i in range(0,len(padded),k)]
     recovered=[]
     for group in out:
      ds=digits(integer(group,3),4);recovered += [0]*(k-len(ds))+ds
     j=recovered.index(end);assert recovered[:j]==list(src) and all(v==0 for v in recovered[j+1:]);roundtrips+=1
 return {'status':'PASS','leading_zero_cases':checked,'roundtrips':roundtrips,'terminal_exception':{'source':source,'R':1,'k':5,'END':0,'final_output':[0],'naive_nonterminal_bound_would_fail':True}}
def main():
 spec=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 assert not (A/'RESULT.json').exists(),'Do not overwrite a result'
 fix=fixtures();source=json.loads((ROOT/next(p for p in spec['input_hashes'] if p.endswith('SOURCE_TEXTS.json'))).read_text());native=json.loads(gzip.decompress((ROOT/next(p for p in spec['input_hashes'] if p.endswith('.gz'))).read_bytes()))
 source_bounds={};targets={};comparisons=[]
 for book in spec['books']:
  recipes=source[book];assert all(isinstance(w,str) and w for r in recipes for w in r['words'])
  stream='\n'.join(' '.join(r['words']) for r in recipes);counts=[];offset=0
  for char,g in itertools.groupby(stream):
   n=len(list(g));counts.append((char,n,offset));offset+=n
  R=max(n for _,n,_ in counts);witnesses=[{'character':c,'length':n,'offset':o} for c,n,o in counts if n==R];minimum=len(set(stream))+1
  source_bounds[book]={'recipes':len(recipes),'words':sum(len(r['words']) for r in recipes),'characters':len(stream),'content_character_types':len(set(stream)),'minimum_alphabet_with_END':minimum,'supported_up_to82':minimum<=82,'R':R,'max_run_count':len(witnesses),'first_max_run_witnesses':witnesses[:8],'stream_sha256':hashlib.sha256(stream.encode()).hexdigest()}
 for ed in spec['readers']:
  rows=native[ed]
  for r in rows:assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and not r['page'].startswith('f84') and r['page']!='f116v'
  select=lambda pred:[{'id':r['id'],'page':r['page'],'locus':r['locus'],'raw':r['ivtff_group_raw'],'units':r['units']} for r in rows if pred(r)]
  short=select(lambda r:len(r['units'])==1);ol=select(lambda r:r['ivtff_group_raw']=='ol');primary=select(lambda r:r['ivtff_group_raw']==spec['native_primary_long_form'] and r['locus']==spec['native_primary_locus']);Lmax=max(len(r['units']) for r in rows);longest=select(lambda r:len(r['units'])==Lmax)
  assert short and ol and primary and all(len(r['units'])==11 for r in primary)
  targets[ed]={'strict_groups':len(rows),'one_unit_occurrences':len(short),'one_unit_types':sorted({r['raw'] for r in short}),'ol_occurrences':len(ol),'primary_L':11,'max_L':Lmax,'short_witnesses':short,'ol_witnesses':ol,'primary_witnesses':primary,'max_witnesses':longest}
  for book,sb in source_bounds.items():
   for label,s in [('ONE_UNIT',1),('OL_TWO_UNITS',2)]:
    for longlabel,L in [('FIXED11',11),('MAXIMUM',Lmax)]:
     power=sb['R']+s;threshold=22**(L-1);base=min_base(threshold,power);excluded=82**power<=threshold
     comparisons.append({'book':book,'reader':ed,'short_tier':label,'long_tier':longlabel,'s':s,'L':L,'R':sb['R'],'k_upper':power,'minimum_base_necessary':base,'length_threshold':str(threshold),'base82_capacity':str(82**power),'status':'UNSUPPORTED_SOURCE_ALPHABET' if not sb['supported_up_to82'] else 'EXCLUDED' if excluded else 'NOT_EXCLUDED'})
 primary=[r for r in comparisons if r['short_tier']=='ONE_UNIT' and r['long_tier']=='FIXED11'];status='ALL_FIXED_SOURCES_PRIMARY_EXCLUDED' if all(r['status']=='EXCLUDED' for r in primary) else 'PRIMARY_NOT_UNIFORMLY_EXCLUDED'
 save('SOURCE_BOUNDS',source_bounds);save('TARGET_WITNESSES',targets);save('FIXTURES',fix);save('RESULT',{'status':status,'comparisons':comparisons,'scope':'Exact fixed-source ordinary radix block family only, N22..82; global key/order/k-independent necessary bounds, not general cipher/language exclusion or native meaning.'})
 print(json.dumps({'status':status,'sources':{b:{k:v for k,v in d.items() if k not in ['first_max_run_witnesses','stream_sha256']} for b,d in source_bounds.items()},'targets':{ed:{k:v for k,v in d.items() if not k.endswith('witnesses')} for ed,d in targets.items()},'primary_bounds':[r for r in primary if r['reader']=='ZL3b']},indent=2))
if __name__=='__main__':main()
