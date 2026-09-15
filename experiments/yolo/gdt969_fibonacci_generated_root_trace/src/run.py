"""Fixed finite result-trace test; no learned or general-purpose decoder."""
from pathlib import Path
import argparse,collections,csv,datetime,hashlib,importlib.util,itertools,json,math,time
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
OPS=['INPUT','HIGH','ROOT','SQUARE','SUB','DOUBLE','APPEND','QUOTIENT','CHOOSE','MUL','SUB','APPEND','SQUARE','SUB','APPEND','MOD','SQUARE','MOD','MOD','ADD','MOD','MOD','CHECK']
def dump(name,x):(A/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def trace(n):
    a,b,c=n//100,(n//10)%10,n%10
    u=math.isqrt(a);s0=a-u*u;d=2*u;w=10*s0+b;e=w//d
    k=max(k for k in range(10) if 10*(w-d*k)+c-k*k>=0)
    m=d*k;v=w-m;z=10*v+c;s=z-k*k;r=10*u+k
    h=r%7;hh=h*h;j=hh%7;l=s%7;q=j+l
    assert n==r*r+s and 0<=s<=2*r and q%7==n%7
    return [n,a,u,u*u,s0,d,w,e,k,m,v,z,k*k,s,r,h,hh,j,l,q,q%7,n%7]
def source():
    with (A/'SOURCE_PROGRAMMES.tsv').open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n')
        w.writerow([f'{i+1}_{op}' for i,op in enumerate(OPS)])
        for n in range(100,10000):w.writerow(trace(n)+['CHECK'])
    dump('SOURCE_PROGRAMME_SUMMARY.json',{'programmes':9900,'range':[100,9999],
         'opcode_sequence':OPS,'numeric_outputs':22,'whole_groups':23,
         'examples':{str(n):trace(n) for n in [100,105,153,864,960,1234,6142,8171,8172,9999]},
         'scope':'generated computational outputs, not a literal historical transcript'})
def check_lock():
    for name,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
def load():
    p=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/src/run.py'
    sp=importlib.util.spec_from_file_location('unchanged928',p)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    return m.load()
def parse(words,values,width):
    """For n and width there is exactly one suffix cut at every phase."""
    opmap={};digits={};rev={}
    for i,(word,op) in enumerate(zip(words,OPS)):
        if op=='CHECK':prefix=word;number='';suffix=''
        else:
            number=str(values[i]);cut=len(word)-len(number)*width
            if cut<1:return None,('NONEMPTY_PREFIX_LENGTH',i+1)
            prefix,suffix=word[:cut],word[cut:]
        if op in opmap and opmap[op]!=prefix:return None,('OPCODE_INCONSISTENT',i+1)
        if op not in opmap and prefix in opmap.values():return None,('OPCODE_NOT_DISTINCT',i+1)
        opmap[op]=prefix
        for j,digit in enumerate(number):
            code=suffix[j*width:(j+1)*width]
            if digit in digits and digits[digit]!=code:return None,('DIGIT_INCONSISTENT',i+1)
            if code in rev and rev[code]!=digit:return None,('DIGIT_NOT_DISTINCT',i+1)
            digits[digit]=code;rev[code]=digit
    return {'width':width,'opcodes':opmap,'digits':digits},None
def combine(a,b):
    if a['width']!=b['width'] or a['opcodes']!=b['opcodes']:return None
    d=dict(a['digits']);rev={v:k for k,v in d.items()}
    for k,v in b['digits'].items():
        if k in d and d[k]!=v:return None
        if v in rev and rev[v]!=k:return None
        d[k]=v;rev[v]=k
    return {'width':a['width'],'opcodes':a['opcodes'],'digits':d}
def completion(key):
    missing=[str(d) for d in range(10) if str(d) not in key['digits']]
    available=26**key['width']-len(key['digits'])
    return {'missing_digits':missing,'distinct_completion_count':math.prod(available-i for i in range(len(missing))),
            'interpretation':'all injective unused literal[a-z] strings of the same width; no preferred completion'}
def main():
    check_lock();start=time.monotonic();panels,dens=load()
    alltargets={};results={};alljoint={}
    with (A/'CASE_CONSEQUENCES.tsv').open('w') as f:
        out=csv.writer(f,delimiter='\t',lineterminator='\n')
        out.writerow(['edition','paragraph','input','width','status','first_failed_position'])
        for ed,ps in panels.items():
            alltargets[ed]=[];records=[];singles={};eligible=[]
            for p in ps:
                if p['groups']!=23:continue
                if not all(l['anchor_eligible'] for l in p['lines']):continue
                words=[w for line in p['lines'] for w in line['words']]
                ids=[sid for line in p['lines'] for sid in line['source_ids']]
                target={k:p[k] for k in ['id','page','leaf','groups']};target.update(words=words,source_ids=ids)
                alltargets[ed].append(target);eligible.append(target)
                kmax=min(len(w)-1 for w in words[:22]);counts=collections.Counter();found=[]
                tested=0;timed=False
                for n in (range(100,10000) if kmax>0 else []):
                    if time.monotonic()-start>120:timed=True;break
                    values=trace(n)
                    for k in range(1,kmax+1):
                        candidate,reason=parse(words,values,k);tested+=1
                        if candidate is None:
                            counts[reason[0]]+=1;out.writerow([ed,p['id'],n,k,reason[0],reason[1]])
                        else:
                            candidate.update(input=n,values=values,paragraph=p['id'],leaf=p['leaf'])
                            candidate['completions']=completion(candidate);found.append(candidate)
                            out.writerow([ed,p['id'],n,k,'EXACT_SINGLE_FRAME',0])
                singles[p['id']]=found
                records.append({'paragraph':p['id'],'page':p['page'],'leaf':p['leaf'],
                    'width_upper_bound':kmax,'finite_cases':9900*max(kmax,0),'tested_cases':tested,
                    'first_failure_counts':dict(counts),'candidates':found,
                    'status':'COMPUTATION_UNKNOWN' if timed else 'SINGLE_FRAME_WITNESSES' if found else 'CONTRADICTED'})
            joint=[];jtimed=False;combos=0
            for chosen in itertools.combinations(eligible,3):
                if len({p['leaf'] for p in chosen})!=3:continue
                for triple in itertools.product(*(singles[p['id']] for p in chosen)):
                    if time.monotonic()-start>120:jtimed=True;break
                    combos+=1
                    if len({x['input'] for x in triple})!=3:continue
                    key=combine(triple[0],triple[1])
                    if key is not None:key=combine(key,triple[2])
                    if key is not None:
                        joint.append({'key':key,'completions':completion(key),
                                      'records':[{'paragraph':x['paragraph'],'leaf':x['leaf'],'input':x['input'],'values':x['values']} for x in triple]})
                if jtimed:break
            leaves=sorted({p['leaf'] for p in eligible})
            status=('INSUFFICIENT_LITERAL_THREE_LEAF_CAPACITY' if len(leaves)<3 else
                    'COMPUTATION_UNKNOWN' if jtimed or any(x['status']=='COMPUTATION_UNKNOWN' for x in records) else
                    'JOINT_CONDITIONAL_WITNESSES' if joint else 'FIXED_TRACE_MODEL_CONTRADICTED')
            results[ed]={'status':status,'eligible_physical_leaves':leaves,'records':records,
                         'joint_combinations_tested':combos,'joint_witnesses':len(joint)}
            alljoint[ed]=joint
    dump('TARGET.json',alltargets);dump('JOINT_CANDIDATES.json',alljoint)
    unresolved=any(x['status']=='COMPUTATION_UNKNOWN' or any(r['status']=='COMPUTATION_UNKNOWN' for r in x['records']) for x in results.values())
    dump('RESULT.json',{'status':'FINITE_TRACE_EVALUATION_WITH_UNKNOWNS' if unresolved else 'FINITE_TRACE_EVALUATION_COMPLETE',
         'panels':results,'denominators':dens,'elapsed_seconds':time.monotonic()-start,
         'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'significance_claim':False})
    print(json.dumps({ed:{k:v for k,v in x.items() if k!='records'} for ed,x in results.items()},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
    source() if a.source_only else main()
