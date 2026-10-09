#!/usr/bin/env python3
"""Independent selector/regex/edge/count reconstruction, no runner import."""
from pathlib import Path
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
import csv,hashlib,io,json,math,multiprocessing,random,re,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
SPEC=json.loads((D/'src/SPEC.json').read_text());BY={};PAGES=[];PARSED={};TARGET={}
PATTERN=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def entropy(c):
    n=sum(c.values());return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0.
def divergence(a,b):
    aa=sum(a.values());bb=sum(b.values());s=0.
    for k in sorted(set(a)|set(b)):
        p=a.get(k,0)/aa;q=b.get(k,0)/bb;m=(p+q)/2
        if p:s+=p*math.log2(p/m)/2
        if q:s+=q*math.log2(q/m)/2
    return s
def distance_one(a,b):
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
    if abs(len(a)-len(b))!=1:return False
    if len(a)>len(b):a,b=b,a
    return any(a==b[:j]+b[j+1:] for j in range(len(b)))
def measure(words,pairs):
    wc=Counter(words);gc=Counter();lc=Counter();first=Counter();last=Counter();bc=Counter()
    for w,count in wc.items():
        g=PARSED[w];lc[len(g)]+=count;first[g[0]]+=count;last[g[-1]]+=count
        for x in g:gc[x]+=count
        for x,y in zip(g,g[1:]):bc[x,y]+=count
    previous=Counter()
    for (x,y),c in bc.items():previous[x]+=c
    n=len(words);mean=sum(k*v for k,v in lc.items())/n
    cond=-sum(c*math.log2(c/previous[x]) for (x,y),c in bc.items())/sum(bc.values())
    return {'tokens':n,'types':len(wc),'type_ratio':len(wc)/n,'mean_length':mean,
            'sd_length':math.sqrt(sum(k*k*v for k,v in lc.items())/n-mean*mean),
            'top10_share':sum(sorted(wc.values(),reverse=True)[:10])/n,
            'word_entropy':entropy(wc),'glyph_entropy':entropy(gc),'conditional_entropy':cond,
            'first_last_js':divergence(first,last),'adjacent_pairs':len(pairs),
            'exact_repeat':sum(x==y for x,y in pairs)/len(pairs),
            'edit1_repeat':sum(distance_one(PARSED[x],PARSED[y]) for x,y in pairs)/len(pairs),
            'glyph_counts':dict(gc),'length_counts':{str(k):v for k,v in lc.items()},
            'q_followed_o':bc['q','o']/previous['q'] if previous['q'] else None,
            'q_count':gc['q'],'y_final':last['y']/n}
def checks(a,b):
    limits={'mean_length':.2*b['mean_length'],'sd_length':.25*b['sd_length'],'top10_share':.05,
            'type_ratio':.05,'conditional_entropy':.30,'exact_repeat':.01,'edit1_repeat':.03,
            'first_last_js':.12,'q_followed_o':.03,'q_count':.25*b['q_count'],'y_final':.05,
            'glyph_entropy':.15,'word_entropy':.30}
    ds={k:abs(a[k]-b[k]) for k in limits}
    ds['tight_edit1']=abs(a['edit1_repeat']-b['edit1_repeat']);limits['tight_edit1']=.01
    ds['glyph_js']=divergence(a['glyph_counts'],b['glyph_counts']);limits['glyph_js']=.10
    ds['length_tv']=sum(abs(a['length_counts'].get(k,0)/a['tokens']-b['length_counts'].get(k,0)/b['tokens']) for k in set(a['length_counts'])|set(b['length_counts']))/2;limits['length_tv']=.20
    assert len(ds)==16
    return {k:{'difference':v,'limit':limits[k],'within':v<=limits[k]} for k,v in ds.items()}
def close(a,b,path=''):
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for k in a:close(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):close(x,y,path+'/'+str(i))
    elif isinstance(a,float):assert abs(a-b)<=1e-10,(path,a,b)
    else:assert a==b,(path,a,b)
def sample(seed):
    order=sorted(PAGES);random.Random(seed).shuffle(order);readings={};anchor_ids={}
    for ed in sorted(TARGET):
        words=[];ids=[];pairs=[];touched=set();prev=None
        for page in order:
            for loc,index,word,left,right in BY[ed,page]:
                if len(words)==8000:break
                if prev is not None and prev[0]==page and prev[1]==loc and prev[2]+1==index and prev[4]==left=='DEFINITE_SPACE':pairs.append((prev[3],word))
                words.append(word);ids.append(f'{ed}|{loc}|G{index:03d}');touched.add(page);prev=(page,loc,index,word,right)
            if len(words)==8000:break
        assert len(words)==8000
        if seed==1174:anchor_ids[ed]=ids
        readings[ed]={'sample_ids_sha256':digest(ids),'last_group_id':ids[-1],'pages_touched':len(touched),'metrics':measure(words,pairs)}
    comparisons={f'{ed}->{ref}':checks(r['metrics'],t) for ed,r in readings.items() for ref,t in TARGET.items()}
    pair_pass={k:all(x['within'] for x in v.values()) for k,v in comparisons.items()}
    out={'seed':seed,'readings':readings,'comparisons':comparisons,'pair_pass':pair_pass,
         'all_cross':all(pair_pass.values()),'all_matched':all(pair_pass[f'{ed}->{ed}'] for ed in TARGET)}
    if seed==1174:
        assert anchor_ids==json.loads((ROOT/SPEC['anchor_ids']).read_text())
        for ed in TARGET:close(readings[ed]['metrics'],TARGET[ed],ed)
    return out

def main():
    global BY,PAGES,PARSED,TARGET
    for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
    result=json.loads((A/'RESULT.json').read_text());TARGET=json.loads((ROOT/SPEC['reference']).read_text())['targets']
    allowed=json.loads((ROOT/SPEC['scope_spec']).read_text())['allowed'];assert len(allowed)==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',SPEC['source'],'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    BY=defaultdict(list);PAGES=set();counts=Counter()
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        if r['kind']!='P':continue
        PAGES.add(r['page'])
        if r['left_separator'] not in {'DEFINITE_SPACE','LINE_START'} or r['right_separator'] not in {'DEFINITE_SPACE','LINE_END'}:continue
        word=r['ivtff_group_raw'];gs=tuple(PATTERN.findall(word))
        if not gs or ''.join(gs)!=word:continue
        PARSED[word]=gs;BY[r['edition'],r['page']].append((r['locus'],int(r['source_group_index']),word,r['left_separator'],r['right_separator']));counts[r['edition']]+=1
    for records in BY.values():records.sort(key=lambda r:(r[0],r[1]))
    assert dict(counts)==result['eligible_groups'] and len(PAGES)==result['prose_page_universe']
    anchor=sample(1174);close(anchor,result['anchor'],'anchor')
    with ProcessPoolExecutor(max_workers=16,mp_context=multiprocessing.get_context('fork')) as pool:records=list(pool.map(sample,SPEC['seeds']))
    prior=json.loads((ROOT/SPEC['prior_frequency_control']).read_text())
    assert len(records)==len(result['samples'])==128
    for rec,saved,old in zip(records,result['samples'],prior['samples']):
        close(rec,saved,str(rec['seed']))
        for ed,v in rec['readings'].items():
            assert v['sample_ids_sha256']==old['readers'][ed]['sample_ids_sha256']
            assert v['metrics']['types']==old['readers'][ed]['types']
            assert round(v['metrics']['top10_share']*8000)==old['readers'][ed]['top10_count']
    joint=sum(r['all_cross'] for r in records);matched=sum(r['all_matched'] for r in records)
    assert result['joint_cross_passes']==joint and result['joint_matched_passes']==matched
    assert result['required_joint_passes']==122 and result['seeds']==128
    assert result['status']==('STRENGTHENED_SCREEN_OPERATIONALLY_STABLE' if joint>=122 else 'STRENGTHENED_SCREEN_OPERATIONALLY_UNSTABLE')
    for pair,total in result['pair_pass_counts'].items():assert total==sum(r['pair_pass'][pair] for r in records)
    for pair,gates in result['gate_failure_counts'].items():
        for gate,total in gates.items():assert total==sum(not r['comparisons'][pair][gate]['within'] for r in records)
    for ed,fields in result['metric_ranges'].items():
        for key,bounds in fields.items():close(bounds,[min(r['readings'][ed]['metrics'][key] for r in records),max(r['readings'][ed]['metrics'][key] for r in records)],ed+'/'+key)
    guardhash=hashlib.sha256(call.stdout.encode()).hexdigest();assert guardhash==json.loads((A/'RUN_RECEIPT.json').read_text())['guard_output_sha256']
    out={'status':'PASS','same_author':True,'runner_or_legacy_metrics_imported':False,'native_samples_verified':384,'seed1174_anchor_ids_verified':24000,'reading_pair_comparisons_verified':1152,'gates_per_pair':16,'all_prior1213_sample_id_and_frequency_checks':True,'guard_output_sha256':guardhash,'metric_tolerance':1e-10,'method':'Independent regex glyphs, original-neighbor edge selection, type-weighted glyph/bigram counts, alternate SD formula, deletion-based edit1, entropy/JS and all comparisons.','claim_ceiling':'Source and calculation validation; no independent manuscript or error-rate estimate.','completed_utc':datetime.now(timezone.utc).isoformat()}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
