#!/usr/bin/env python3
import argparse,collections,csv,hashlib,io,itertools,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(name,x): (E/'artifacts'/name).write_text(enc(x))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def leaf(p):return re.match(r'f[0-9]+',p)[0]
def query(s,stage):
    allowed=s['discovery_selectors' if stage=='DISCOVERY' else 'transfer_selectors'];argv=['./vmanus-exp','query-tsv',s['source_atlas'],'--selector','page']
    for p in allowed:argv+=['--allow',p]
    argv+=['--columns',','.join(s['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
    proc=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,check=True);guards=[json.loads(x[len('GUARD_STATS '):]) for x in proc.stderr.splitlines() if x.startswith('GUARD_STATS ')]
    rd=csv.DictReader(io.StringIO(proc.stdout),delimiter='\t');assert rd.fieldnames==s['columns'];by=collections.defaultdict(list);n=0
    for r in rd:
        assert r['page'] in allowed and not r['page'].startswith('f84');by[r['edition'],r['locus']].append(r);n+=1
    assert len(guards)==1 and n==guards[0]['selected'];readings={ed:[] for ed in s['editions']};gc=s['group_columns']
    for (ed,loc),rr in sorted(by.items()):
        rr.sort(key=lambda r:int(r['source_group_index']));meta={k:v for k,v in rr[0].items() if k not in gc};assert all({k:v for k,v in r.items() if k not in gc}==meta for r in rr)
        readings[ed].append({'metadata':meta,'groups':[[r[k] for k in gc] for r in rr]})
    out={'group_columns':gc,'readings':readings};save(stage+'_SOURCE.json',out);save(stage+'_GUARD.json',{'command':argv,'stats':guards[0],'projection_sha256':hashlib.sha256(proc.stdout.encode()).hexdigest()});return out

def observations(lines,gc):
    obs=[];counts=collections.Counter()
    for line in lines:
        m=line['metadata'];gg=[dict(zip(gc,g)) for g in line['groups']]
        if m['kind']!='P':continue
        counts['prose_lines']+=1
        if len(gg)!=int(m['source_group_count']) or [int(g['source_group_index']) for g in gg]!=list(range(1,len(gg)+1)):
            counts['incomplete_lines']+=1;continue
        for size in (1,2,3):
            for start in range(len(gg)-size-1):
                span=gg[start:start+size+2];counts['raw_windows']+=1
                if not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in span):continue
                if not all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(span,span[1:])):continue
                obs.append({'page':m['page'],'locus':m['locus'],'start':start+1,'hand':m['hand'],'section':m['section'],'middle':[g['ivtff_group_raw'] for g in span[1:-1]],'flanks':[span[0]['ivtff_group_raw'],span[-1]['ivtff_group_raw']],'source_ids':[g['source_group_id'] for g in span]});counts['eligible_'+str(size)]+=1
    return obs,dict(counts)

def rules(obs,s):
    by=collections.defaultdict(lambda:[[],[]])
    for i,o in enumerate(obs):by[tuple(o['flanks'])][len(o['middle'])>1].append(i)
    rr=collections.defaultdict(lambda:collections.defaultdict(list));joins=0
    for flank,(ss,ll) in sorted(by.items()):
        for i,j in itertools.product(ss,ll):
            a,b=obs[i],obs[j]
            if leaf(a['page'])==leaf(b['page']):continue
            rr[a['middle'][0],tuple(b['middle'])][flank].append([i,j]);joins+=1
    output=[]
    for (short,long),contexts in sorted(rr.items()):
        kind='echo' if short in long else 'spacing' if short==''.join(long) else 'nonshort' if len(short)>=sum(map(len,long)) else 'proper'
        leaves=sorted({leaf(obs[i]['page']) for pp in contexts.values() for p in pp for i in p});hands=collections.Counter((obs[i]['hand'],obs[j]['hand']) for pp in contexts.values() for i,j in pp)
        output.append({'short':short,'long':list(long),'kind':kind,'contexts':[{'flanks':list(f),'pairs':pp} for f,pp in sorted(contexts.items())],'leaves':leaves,'hand_pairs':[[a,b,n] for (a,b),n in sorted(hands.items())],'qualified':kind=='proper' and len(contexts)>=s['minimum_contexts'] and len(leaves)>=s['minimum_leaves']})
    return output,joins

def analyze(src,s,stage):
    out={};summary={}
    for ed in s['editions']:
        obs,c=observations(src['readings'][ed],src['group_columns']);rr,joins=rules(obs,s);out[ed]={'observations':obs,'rules':rr};save(stage+'_'+ed+'.json',out[ed]);summary[ed]={**c,'cross_leaf_pairs':joins,'rules':len(rr),'proper_rules':sum(r['kind']=='proper' for r in rr),'recurrent_proper_rules':sum(r['kind']=='proper' and len(r['contexts'])>=2 for r in rr),'qualified_rules':sum(r['qualified'] for r in rr)}
    return out,summary

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cached',action='store_true');a=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text())
    for b in s['input_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    src=json.loads((E/'artifacts/DISCOVERY_SOURCE.json').read_text()) if a.cached else query(s,'DISCOVERY');disc,summ=analyze(src,s,'DISCOVERY')
    frozen={ed:[r for r in d['rules'] if r['qualified']] for ed,d in disc.items()};save('FROZEN_RULES.json',frozen);save('RULE_LOCK.json',{'spec_sha256':sha(E/'src/SPEC.json'),'source_sha256':sha(E/'artifacts/DISCOVERY_SOURCE.json'),'rules_sha256':sha(E/'artifacts/FROZEN_RULES.json')})
    result={'discovery':summ,'transfer_accessed':False,'status':'NO_RECURRENT_SHORT_LONG_RULE','claim_ceiling':'Literal context census; no abbreviation or meaning established.'}
    if any(frozen.values()):
        src=json.loads((E/'artifacts/TRANSFER_SOURCE.json').read_text()) if a.cached else query(s,'TRANSFER');trans,ts=analyze(src,s,'TRANSFER');hits={}
        for ed,rr in frozen.items():
            idx={(r['short'],tuple(r['long'])):r for r in trans[ed]['rules']};hits[ed]=[]
            for r in rr:
                matched=idx.get((r['short'],tuple(r['long'])));old={tuple(c['flanks']) for c in r['contexts']};new=[] if matched is None else [c for c in matched['contexts'] if tuple(c['flanks']) not in old]
                hits[ed].append({'short':r['short'],'long':r['long'],'new_contexts':new,'transfer':bool(new)})
        save('TRANSFER_PREDICTIONS.json',hits);result.update(transfer_accessed=True,transfer=ts,status='FROZEN_RULE_TRANSFER_EVALUATED',transferred_rules={ed:sum(r['transfer'] for r in rr) for ed,rr in hits.items()})
    save('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
