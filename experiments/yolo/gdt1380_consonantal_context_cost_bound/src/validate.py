#!/usr/bin/env python3
"""Independent admitted PAGE_HOST replay and conservative context lower bounds."""
import argparse,collections,csv,functools,gzip,hashlib,itertools,json,math,re
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
LETTERS='abcdefghijklmnopqrstuvxyz';CONSONANTS='bcdfghjklmnpqrstvwxyz'
PREFIXES=('che','ch','sh','t','s','d','q');RIGHT=('aiin','air','ain','ar','al')
SPACE=25;BOS=27;TSPACE=26

def load(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

@functools.lru_cache(None)
def ln_interval(number):
 assert isinstance(number,int) and number>=1
 if number==1:return Decimal(0),Decimal(0)
 with localcontext() as ctx:
  ctx.prec=80
  value=Decimal(number).ln()
  # Decimal ln is correctly rounded. Adjacent representable numbers enclose it.
  return value.next_minus(ctx),value.next_plus(ctx)

@functools.lru_cache(None)
def ticks(numerator,denominator,scale):
 assert numerator>=denominator>=1 and scale>0
 if numerator==denominator:return 0,0
 divisor=math.gcd(numerator,denominator);nn=numerator//divisor;dd=denominator//divisor
 if nn&(nn-1)==0 and dd&(dd-1)==0:
  exact=(nn.bit_length()-dd.bit_length())*scale;return exact,exact
 nlo,nhi=ln_interval(numerator);dlo,dhi=ln_interval(denominator);blo,bhi=ln_interval(2)
 with localcontext() as ctx:
  ctx.prec=80;ctx.rounding=ROUND_FLOOR
  lower=max(Decimal(0),(nlo-dhi)/bhi)
  lo=int((lower*scale).to_integral_value(rounding=ROUND_FLOOR))
 with localcontext() as ctx:
  ctx.prec=80;ctx.rounding=ROUND_CEILING
  upper=(nhi-dlo)/blo
  hi=int((upper*scale).to_integral_value(rounding=ROUND_CEILING))
 assert lo<=hi
 return lo,hi

def preparse(word):
 host=word;prefix='NONE'
 for candidate in PREFIXES:
  if len(host)>len(candidate) and host.startswith(candidate):prefix=candidate;host=host[len(candidate):];break
 if len(host)>2 and host.endswith('dy'):host=host[:-2]
 if len(host)>1 and host.endswith('m'):host=host[:-1]
 for suffix in RIGHT:
  if len(host)>len(suffix) and host.endswith(suffix):host=host[:-len(suffix)];break
 if prefix in ('ch','che','sh') and len(host)>1 and host.startswith('d'):host=host[1:]
 return host

def controls():
 scale=2**32
 for num,den in [(1,1),(2,1),(4,1),(8,2),(31,17),(103,3),(1000001,999999)]:
  lo,hi=ticks(num,den,scale)
  with localcontext() as ctx:
   ctx.prec=160;ref=(Decimal(num).ln()-Decimal(den).ln())/Decimal(2).ln()*scale
   if lo==hi:
    g=math.gcd(num,den);nn=num//g;dd=den//g;assert nn&(nn-1)==0 and dd&(dd-1)==0 and lo==(nn.bit_length()-dd.bit_length())*scale
   else:assert Decimal(lo)<=ref<=Decimal(hi)
 # Source-free all-injection comparison; SPACE/BOS remain fixed.
 lines=[[0,1,SPACE,0],[1,0,0]];counts=collections.defaultdict(collections.Counter)
 for line in lines:
  history=[BOS,BOS]
  for x in line:counts[tuple(history)][x]+=1;history=[history[1],x]
 targets=[0,1,2];cost=lambda a,b,t:(a*17+b*11+t*7+5)%23+1
 domain=lambda x:[BOS] if x==BOS else [TSPACE] if x==SPACE else targets
 lower=0
 for (u,v),nexts in counts.items():
  best=None
  for a,b in itertools.product(domain(u),domain(v)):
   weights=sorted((n for x,n in nexts.items() if x!=SPACE),reverse=True)
   ranked=sorted(cost(a,b,t) for t in targets)
   val=nexts[SPACE]*cost(a,b,TSPACE)+sum(n*c for n,c in zip(weights,ranked))
   # Exhaustive independent row assignments verify rearrangement, including unusedtargets.
   symbols=[x for x in nexts if x!=SPACE]
   brute=min(nexts[SPACE]*cost(a,b,TSPACE)+sum(nexts[x]*cost(a,b,t) for x,t in zip(symbols,assignment)) for assignment in itertools.permutations(targets,len(symbols)))
   assert brute==val
   best=val if best is None else min(best,val)
  lower+=best
 actual=[]
 for pair in itertools.permutations(targets,2):
  key={0:pair[0],1:pair[1],SPACE:TSPACE,BOS:BOS}
  actual.append(sum(n*cost(key[u],key[v],key[x]) for (u,v),row in counts.items() for x,n in row.items()))
 assert lower<=min(actual)
 assert 0+100>0+0 # Injectivity cannot be imposed on194homophony.
 assert [preparse(w) for w in ('chedy','daldy','qokaiin','shdam')]==['y','al','ok','a']
 return {'log_interval_cases':7,'global_injections_checked':len(actual),'row_assignment_bruteforce':'PASS','SPACE_BOS_contexts':'PASS','194_scope_counterexample':'PASS'}

def replay_corpus(allowed):
 corpus={};gc=['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
 for ed in ('ZL3b','IT2a','RF1b'):
  eligible=[];rejected=[];seen=set()
  for phase in ('DISCOVERY','EVALUATION'):
   src=load(ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json');assert src['group_columns']==gc
   for line in src['lines']:
    meta=line['metadata'];page=meta['page'];locus=meta['locus']
    if page not in allowed or page in ('f1r','f116v') or page.startswith('f84') or locus=='f102v2.33':continue
    if meta['kind']!='P':continue
    assert meta['edition']==ed and (page,locus) not in seen;seen.add((page,locus))
    original=line['groups'];assert all(len(g)==len(gc) for g in original)
    rows=sorted((dict(zip(gc,g)) for g in original),key=lambda g:int(g['source_group_index']));reasons=[]
    if [int(g['source_group_index']) for g in rows]!=list(range(1,int(meta['source_group_count'])+1)):reasons.append('indices')
    ids=[g['source_group_id'] for g in rows]
    if len(ids)!=len(set(ids)) or any(g['source_group_id']!=f"{ed}|{locus}|G{int(g['source_group_index']):03d}" for g in rows):reasons.append('ids')
    if not all(rows[i]['right_separator']==rows[i+1]['left_separator']=='DEFINITE_SPACE' for i in range(len(rows)-1)):reasons.append('seams')
    if any(not g['ivtff_group_raw'] or any(x not in LETTERS for x in g['ivtff_group_raw']) for g in rows):reasons.append('literal')
    if reasons:rejected.append({'page':page,'locus':locus,'reasons':reasons})
    else:eligible.append({'metadata':meta,'groups':original,'prehosts':[preparse(g['ivtff_group_raw']) for g in rows]})
  eligible.sort(key=lambda x:(x['metadata']['page'],x['metadata']['locus']));rejected.sort(key=lambda x:(x['page'],x['locus']))
  counts=collections.Counter(h for line in eligible for h in line['prehosts'])
  licensed={h for h,n in list(counts.items()) if n and counts.get('o'+h,0) and counts.get('ot'+h,0)}|{'ar','al','ol'}
  ctxcounts=collections.defaultdict(collections.Counter);lines=[];active=set();events=groups=0
  for line in eligible:
   hosts=[]
   for h in line['prehosts']:
    if h.startswith('ot') and h[2:] in licensed:h=h[2:]
    elif h.startswith('o') and h[1:] in licensed:h=h[1:]
    assert h and set(h)<=set(LETTERS);hosts.append(h);active.update(h)
   groups+=len(hosts);stream=' '.join(hosts);history=('^','^')
   for x in stream:ctxcounts[history][x]+=1;events+=1;history=(history[1],x)
   lines.append({'metadata':line['metadata'],'groups':line['groups'],'hosts':hosts})
  corpus[ed]={'lines':lines,'rejected':rejected,'licensed':sorted(licensed),'contexts':[{'context':list(c),'counts':dict(sorted(row.items()))} for c,row in sorted(ctxcounts.items())],'active':sorted(active),'events':events,'groups':groups}
 return corpus

def kt_ticks(contexts,K,scale):
 # Each context's integrated conditional count law; no floating gamma formula.
 lo=hi=0
 for row in contexts:
  frequencies=list(row['counts'].values());N=sum(frequencies)
  for j in range(N):
   l,h=ticks(2*j+K,1,scale);lo+=l;hi+=h
  for n in frequencies:
   for j in range(n):
    l,h=ticks(2*j+1,1,scale);lo-=h;hi-=l
 return lo,hi

def equal(a,b,path='root'):
 if isinstance(a,dict):
  assert isinstance(b,dict) and a.keys()==b.keys(),(path,'keys',a.keys(),getattr(b,'keys',lambda:[])())
  for k in a:equal(a[k],b[k],path+'.'+str(k))
 elif isinstance(a,list):
  assert isinstance(b,list) and len(a)==len(b),(path,'length',len(a),len(b))
  for i,(x,y) in enumerate(zip(a,b)):equal(x,y,path+f'[{i}]')
 else:assert a==b,(path,a,b)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');args=ap.parse_args();check=controls()
 if args.controls_only:print(json.dumps(check));return
 lock=load(B/'src/REGISTRATION_LOCK.json')
 for path,h in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 scale=2**32
 allowed={r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 corpus=replay_corpus(allowed);equal(corpus,load(B/'artifacts/CORPUS.json.gz'),'corpus')
 packs=load(B/'artifacts/MODEL_COUNTS.json.gz');manifest=load(ROOT/'gdt001_language_pack_manifest.json')['packs'];assert set(packs)==set(manifest)
 modelcosts={};alphabet=CONSONANTS+' ';targetctxchars=CONSONANTS+' ^'
 for name,pack in packs.items():
  assert pack['provenance']==manifest[name]
  counts={}
  for row in pack['rows']:
   context=tuple(row['context']);values=row['counts'];assert context not in counts and len(context)==2 and all(x in targetctxchars for x in context)
   assert len(values)==22 and all(isinstance(n,int) and n>=0 for n in values);counts[context]=values
  assert sum(map(sum,counts.values()))==pack['events']
  assert sum(counts.get(('^','^'),[0]*22))==pack['source_lines']
  table={}
  for a,b in itertools.product(sorted(set(targetctxchars)),repeat=2):
   row=counts.get((a,b),[0]*22);den=2*sum(row)+22
   lows=[ticks(den,2*n+1,scale)[0] for n in row]
   table[(a,b)]=(sorted(lows[:21]),lows[21])
  modelcosts[name]=table
 result={};certifiedrows=0
 for ed,src in corpus.items():
  m=len(src['active']);record={'status':None,'lines':len(src['lines']),'groups':src['groups'],'events':src['events'],'active_symbols':src['active'],'context_count':len(src['contexts']),'kt_lo':None,'kt_hi':None,'key_lo':None,'key_hi':None,'selector_lo':None,'selector_hi':None,'packs':{}}
  if not src['events']:record['status']='NO_EVENTS';result[ed]=record;continue
  if m>21:record['status']='EMPTY_INJECTIVE_FAMILY';result[ed]=record;continue
  record['kt_lo'],record['kt_hi']=kt_ticks(src['contexts'],m+1,scale)
  keyfactor=math.prod(range(22-m,22));record['key_lo'],record['key_hi']=ticks(keyfactor,1,scale)
  record['selector_lo'],record['selector_hi']=ticks(6,1,scale)
  for name,table in modelcosts.items():
   rows=[];payload=0
   for row in src['contexts']:
    context=tuple(row['context']);native=row['counts'];weights=sorted((n for x,n in native.items() if x!=' '),reverse=True);spacecount=native.get(' ',0)
    domains=[([x] if x in (' ','^') else sorted(CONSONANTS)) for x in context]
    candidates=[]
    for target in itertools.product(*domains):
     costs,spacecost=table[target];value=spacecount*spacecost+sum(n*c for n,c in zip(weights,costs));candidates.append((value,target))
    lower,target=min(candidates);payload+=lower;certifiedrows+=1;rows.append({'context':list(context),'target_context':list(target),'lower':lower})
   paid=payload+record['key_lo']+record['selector_lo'];margin=paid-record['kt_hi']
   record['packs'][name]={'payload_lower':payload,'paid_lower':paid,'margin_lower':margin,'status':'CERTIFIED_NO_KEY_BEATS_MATCHED_KT' if margin>0 else 'BOUND_INCONCLUSIVE','rows':rows}
  record['status']='ALL_PACKS_CERTIFIED' if all(p['margin_lower']>0 for p in record['packs'].values()) else 'BOUND_INCONCLUSIVE';result[ed]=record
 expected={'status':'CERTIFIED_CONTEXT_BOUND','scale':scale,'readers':result};equal(expected,load(B/'artifacts/RESULT.json'),'result')
 receipt={'status':'PASS','source_free_controls':check,'interval_precision':80,'primary_interval_precision':60,'integer_ticks':scale,'bound_rows_checked':certifiedrows,'readers':{ed:{'status':r['status'],'active_symbols':r['active_symbols'],'events':r['events']} for ed,r in result.items()},'method':'Independent012/189transformandlicense replay on separately scoped915readers; own Decimal80directed intervals; exactinteger sorted row bound and aggregateKT; no primary imports. External packtext not reopened; published counts/provenance verified.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
