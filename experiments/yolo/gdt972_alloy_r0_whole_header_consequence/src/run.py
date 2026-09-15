"""Necessary R0 header census; no general code or arithmetic decoder."""
from pathlib import Path
import argparse, collections, csv, datetime, hashlib, json, time
E=Path(__file__).resolve().parents[1]
R=E.parents[2]
D=R/'research_registry/work_batches/ten_hours_20260915'
P=R/'experiments/yolo/gdt970_rota_whole_part_conjugacy/artifacts/PARAGRAPHS.json'
S=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json'
AT=[0,1,3,5,7,9,11]
NU=[2,4,6,8,10]
RULES=['MIN_GROUPS','ATOMIC_WIDTH','ATOMIC_DISTINCT','ATOMIC_PREFIX_FREE','NUMERIC_WIDTH','GRADE_DISTINCT','NUM_PREFIX_DOMAIN']

def write(n,x): (E/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def incompatible(a,b): return a.startswith(b) or b.startswith(a)
def inspect(words):
    flags={k:None for k in RULES};flags['MIN_GROUPS']=len(words)>=14
    domains=[]
    if len(words)>=12:
        atoms=[words[i] for i in AT]; nums=[words[i] for i in NU]
        flags['ATOMIC_WIDTH']=all(1<=len(x)<=8 for x in atoms)
        flags['ATOMIC_DISTINCT']=len(set(atoms))==7
        flags['ATOMIC_PREFIX_FREE']=not any(incompatible(a,b) for i,a in enumerate(atoms) for b in atoms[i+1:])
        flags['NUMERIC_WIDTH']=all(2<=len(x)<=32 for x in nums)
        flags['GRADE_DISTINCT']=len(set(nums[:4]))==4
        for k in range(1,min(8,min(map(len,nums))-1)+1):
            prefix=nums[0][:k]
            if all(w.startswith(prefix) for w in nums) and all(not incompatible(prefix,w) for w in atoms):domains.append(prefix)
        flags['NUM_PREFIX_DOMAIN']=bool(domains)
    contradictions=[k for k in RULES if flags[k] is False]
    return dict(header=words[:12],conditions=flags,num_prefixes=domains,contradictions=contradictions,decision=contradictions[0] if contradictions else 'NECESSARY_HEADER_ONLY')

def preflight():
    g=json.loads((D/'ALLOY_FINITE_GRAMMAR.json').read_text())
    key={a:chr(97+i//26)+chr(97+i%26) for i,a in enumerate(g['renderer']['atoms'])}
    cases={};sourcewords=[]
    for name,txt in g['metalanguage_accounts'].items():
        words=[]
        for token in txt.split():
            if ':' in token:
                kind,digits=token.split(':');words.append(key[kind]+''.join(key[x] for x in digits))
            else:words.append(key[token])
        x=inspect(words);assert all(x['conditions'].values()) and key['NUM'] in x['num_prefixes']
        cases[name]=dict(word_count=len(words),decision=x['decision'],num_prefixes=x['num_prefixes'])
        sourcewords.append(words)
    base=sourcewords[0];tests={}
    mutations={'MIN_GROUPS':base[:13]}
    for rule,pos,value in [('ATOMIC_WIDTH',0,'z'*9),('ATOMIC_DISTINCT',1,base[0]),('ATOMIC_PREFIX_FREE',0,base[1][:1]),('NUMERIC_WIDTH',2,'z'),('GRADE_DISTINCT',2,base[4]),('NUM_PREFIX_DOMAIN',2,'zz'+base[2])]:
        w=base.copy();w[pos]=value;mutations[rule]=w
    for rule,w in mutations.items():
        x=inspect(w);assert x['conditions'][rule] is False
        tests[rule]=dict(decision=x['decision'],contradictions=x['contradictions'])
    write('PREFLIGHT.json',dict(status='PASS_SOURCE_SYNTHETICS_ONLY',complete_generated_accounts=cases,negative_fixtures=tests,synthetic_key=key,target_access=False))
    print('PASS:3 complete generated accounts and7 fixed corruptions; no target access')

def main():
    a=argparse.ArgumentParser();a.add_argument('--preflight',action='store_true');args=a.parse_args()
    if args.preflight:return preflight()
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for n,h in lock['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    allowed=set(json.loads(S.read_text())['allowed_selectors']);assert len(allowed)==179 and not any(x.startswith('f84') or x=='f116v' for x in allowed)
    panels=json.loads(P.read_text());rows=[];summary={}
    for ed,paras in panels.items():
        first=collections.Counter();every=collections.Counter();leaves=set();eligible=0;survivors=[]
        for p in paras:
            assert p['page'] in allowed and not p['page'].startswith('f84') and p['page']!='f116v'
            words=[w for line in p['lines'] for w in line['words']]
            assert ' '.join(words)==p['full_text']
            row=dict(edition=ed,id=p['id'],page=p['page'],leaf=p['leaf'],eligible=p['literal_eligible'],defects=p['defects'],group_count=len(words))
            if p['literal_eligible']:
                assert words and all(w and all('a'<=c<='z' for c in w) for w in words)
                eligible+=1;leaves.add(p['leaf']);row.update(inspect(words));first[row['decision']]+=1;every.update(row['contradictions'])
                if row['decision']=='NECESSARY_HEADER_ONLY':survivors.append(p['id'])
            else:row.update(header=None,conditions={k:None for k in RULES},num_prefixes=[],contradictions=[],decision='UNKNOWN_NONLITERAL_COMPLETE')
            rows.append(row)
        summary[ed]=dict(complete_paragraphs=len(paras),literal_paragraphs=eligible,literal_leaves=len(leaves),unknown_nonliteral=len(paras)-eligible,first_failure_or_survival_counts=dict(first),all_failure_counts=dict(every),survivors=survivors,independent_confirmation_capacity=0)
    total=sum(len(x['survivors']) for x in summary.values())
    result=dict(status='ALL_LITERAL_R0_HEADERS_CONTRADICTED' if total==0 else 'NECESSARY_HEADER_SURVIVORS_NO_FULL_READING',started_utc=start,elapsed_seconds=time.monotonic()-t,panels=summary,complete_rows=len(rows),literal_rows=sum(x['literal_paragraphs'] for x in summary.values()),survivors=total,full_code_or_arithmetic_tested=False,translated_words=0,reserve_access=False,independent_confirmation_capacity=0)
    write('PREDICTIONS.json',rows);write('RESULT.json',result)
    with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['edition','paragraph','page','physical_leaf','eligibility','groups','header',*RULES,'NUM_prefixes','all_contradictions','decision','independent_confirmation'])
        for x in rows:w.writerow([x['edition'],x['id'],x['page'],x['leaf'],'LITERAL' if x['eligible'] else json.dumps(x['defects'],separators=(',',':')),x['group_count'],json.dumps(x['header'],separators=(',',':')),*[str(x['conditions'][k]) for k in RULES],json.dumps(x['num_prefixes'],separators=(',',':')),json.dumps(x['contradictions'],separators=(',',':')),x['decision'],0])
    print(json.dumps(result))
if __name__=='__main__':main()
