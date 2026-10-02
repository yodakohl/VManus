#!/usr/bin/env python3
"""Frozen whole-neighbour prediction; no guessed semantic values."""
import csv, gzip, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[2]
SERIES=re.compile(r'^(.*?)a(i{1,3})n$'); ECHO=re.compile(r'^.*ai+n$'); PURE=re.compile(r'^[a-z]+$')
def load(p): return json.loads(p.read_text())
def write(name,x):
    if name in ('EVENTS.json','FOLDS.json','PREDICTIONS.json'):
        data=(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n').encode()
        (P/'artifacts'/(name+'.gz')).write_bytes(gzip.compress(data,mtime=0))
    else:
        (P/'artifacts'/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def mean(xs): return sum(xs)/len(xs) if xs else None
def loss(y,p):return -math.log(p if y else 1-p)
def table(name,rows):
    fields=list(rows[0]) if rows else ['empty']
    with (P/'artifacts'/name).open('w') as f:
        w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def extract():
    source=load(P/'src/SOURCE.json')
    for x in source['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
    for path,h in load(P/'src/PREREG_LOCK.json')['hashes'].items():assert hashlib.sha256((P/path).read_bytes()).hexdigest()==h
    allowed=set(load(ROOT/source['inputs'][0]['path'])['allowed_selectors']);assert not {'f84','f84r','f116v'} & allowed
    events=[];audit={};seen=set()
    for ed in ('ZL3b','IT2a','RF1b'):
        counts=Counter()
        for part in ('DISCOVERY','EVALUATION'):
            src=load(ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{part}_{ed}.json')
            for row in src['lines']:
                m=row['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
                if m['kind']!='P':continue
                gs=[dict(zip(src['group_columns'],g)) for g in row['groups']]
                assert len(gs)==int(m['source_group_count'])
                counts['P_groups']+=len(gs)
                for i,g in enumerate(gs):
                    raw=g['ivtff_group_raw'];pure=bool(PURE.fullmatch(raw));match=SERIES.fullmatch(raw) if pure else None
                    if not pure:
                        counts['uncertain_groups']+=1
                        if 'ain' in raw or 'aiin' in raw:counts['uncertain_literal_ain_or_aiin']+=1
                        continue
                    if not match:
                        if 'aiin' in raw:counts['other_pure_containing_aiin']+=1
                        continue
                    stem,minims=match.groups();tail='a'+minims+'n';counts[tail]+=1
                    gid=g['source_group_id'];assert gid not in seen;seen.add(gid)
                    idx=int(g['source_group_index']);n=int(m['source_group_count']);position='SINGLE' if n==1 else 'FINAL' if idx==n else 'PENULTIMATE' if idx==n-1 else 'EARLIER'
                    event={'edition':ed,'id':gid,'page':m['page'],'locus':m['locus'],'index':idx,'source_group_count':n,'raw':raw,'stem':stem,'tail':tail,'y':len(minims)-1,'leaf':int(re.match(r'^f([0-9]+)',m['page']).group(1)),'cell':[m['section'],m['currier'],m['hand'],position]}
                    for side,j in [('left',i-1),('right',i+1)]:
                        reason='ELIGIBLE';word=None
                        if j<0 or j>=len(gs):reason='LINE_EDGE'
                        else:
                            a,b=(gs[j],g) if side=='left' else (g,gs[j]);other=gs[j]
                            if int(b['source_group_index'])!=int(a['source_group_index'])+1:reason='INDEX_GAP'
                            elif a['right_separator']!='DEFINITE_SPACE' or b['left_separator']!='DEFINITE_SPACE':reason='UNCERTAIN_SEAM'
                            elif not PURE.fullmatch(other['ivtff_group_raw']):reason='UNCERTAIN_NEIGHBOUR'
                            elif ECHO.fullmatch(other['ivtff_group_raw']):reason='SERIES_ECHO_MASKED'
                            else:word=other['ivtff_group_raw']
                        event[side]=word;event[side+'_status']=reason
                    events.append(event)
        audit[ed]=dict(counts)
    return events,audit

def fit(train):
    p0=(sum(x['y'] for x in train)+1)/(len(train)+2)
    cells=defaultdict(lambda:[0,0]); neighbours={side:defaultdict(lambda:[0,0]) for side in ('left','right')}
    for x in train:
        c=tuple(x['cell']);cells[c][0]+=1;cells[c][1]+=x['y']
        for side in neighbours:
            if x[side] is not None:
                v=neighbours[side][(c,x[side])];v[0]+=1;v[1]+=x['y']
    return p0,cells,neighbours

def main():
    events,audit=extract(); predictions=[];folds=[]
    for ed in ('ZL3b','IT2a','RF1b'):
        data=[x for x in events if x['edition']==ed and x['y'] in (0,1)];testsets=defaultdict(list)
        for x in data:testsets[(x['stem'],x['leaf']%5)].append(x)
        for (stem,fold),tests in sorted(testsets.items()):
            train=[x for x in data if x['stem']!=stem and x['leaf']%5!=fold]
            p0,cells,neighbours=fit(train)
            folds.append({'edition':ed,'stem':stem,'fold':fold,'train_events':len(train),'test_events':len(tests),'train_leaves':sorted({x['leaf'] for x in train}),'test_leaves':sorted({x['leaf'] for x in tests}),'train_stems':sorted({x['stem'] for x in train})})
            for x in tests:
                c=tuple(x['cell']);n,k=cells.get(c,(0,0));B=(k+20*p0)/(n+20);ps={'B':B};support={}
                for side,model in [('left','L'),('right','R')]:
                    n1,k1=neighbours[side].get((c,x[side]),(0,0)) if x[side] is not None else (0,0)
                    ps[model]=(k1+20*B)/(n1+20);support[side+'_training_support']=n1
                ps['C']=(ps['L']+ps['R'])/2
                pred={**x,'fold':fold,**support}
                for model,prob in ps.items():pred['p_'+model]=prob;pred['loss_'+model]=loss(x['y'],prob);pred['prediction_'+model]=stem+('aiin' if prob>=.5 else 'ain')
                predictions.append(pred)
    results={};leafrows=[];stemrows=[]
    for ed in ('ZL3b','IT2a','RF1b'):
        results[ed]={'inventory':audit[ed],'strata':{}}
        for st in ('BARE','NONBARE'):
            data=[x for x in predictions if x['edition']==ed and (x['stem']=='')==(st=='BARE')]
            leaves=sorted({x['leaf'] for x in data});stems=sorted({x['stem'] for x in data});both=[s for s in stems if {x['y'] for x in data if x['stem']==s}=={0,1}]
            cap=(len(data)>=30 and len(leaves)>=5 and bool(both)) if st=='BARE' else (len(data)>=100 and len(leaves)>=5 and len(both)>=2)
            vals={'events':len(data),'leaves':len(leaves),'prefixes':len(stems),'prefixes_with_both_tails':both,'ain':sum(x['y']==0 for x in data),'aiin':sum(x['y']==1 for x in data),'capacity':cap,'left_supported_events':sum(x['left_training_support']>0 for x in data),'right_supported_events':sum(x['right_training_support']>0 for x in data),'context_status_counts':{side:dict(Counter(x[side+'_status'] for x in data)) for side in ('left','right')}}
            for model in ('B','L','R','C'):
                vals['event_loss_'+model]=mean([x['loss_'+model] for x in data]);vals['accuracy_'+model]=mean([float(x['prediction_'+model]==x['raw']) for x in data])
            for model in ('L','R','C'):
                gains=[mean([x['loss_B']-x['loss_'+model] for x in data if x['leaf']==leaf]) for leaf in leaves]
                vals['leaf_macro_gain_'+model]=mean(gains);vals['event_gain_'+model]=mean([x['loss_B']-x['loss_'+model] for x in data]);vals['prefix_macro_gain_'+model]=mean([mean([x['loss_B']-x['loss_'+model] for x in data if x['stem']==s]) for s in stems])
            for field,values,output in [('leaf',leaves,leafrows),('stem',stems,stemrows)]:
                for v in values:
                    group=[x for x in data if x[field]==v];output.append({'edition':ed,'stratum':st,field:v,'events':len(group),'gain_C':mean([x['loss_B']-x['loss_C'] for x in group]),'gain_L':mean([x['loss_B']-x['loss_L'] for x in group]),'gain_R':mean([x['loss_B']-x['loss_R'] for x in group])})
            results[ed]['strata'][st]=vals
    decisions={}
    for st in ('BARE','NONBARE'):
        rows=[results[ed]['strata'][st] for ed in ('ZL3b','IT2a')]
        decisions[st]='INSUFFICIENT_CAPACITY' if not all(x['capacity'] for x in rows) else 'TRANSFER_SUPPORTED_LIMITED' if all(x['leaf_macro_gain_C']>=.01 for x in rows) else 'NO_MATERIAL_TRANSFER'
    bare=decisions['BARE']=='TRANSFER_SUPPORTED_LIMITED';bound=decisions['NONBARE']=='TRANSFER_SUPPORTED_LIMITED'
    overall='JOINT_BARE_BOUND_TRANSFER' if bare and bound else 'BOUND_ONLY' if bound else 'BARE_ONLY' if bare else 'NO_JOINT_TRANSFER'
    write('EVENTS.json',events);write('FOLDS.json',folds);write('PREDICTIONS.json',predictions)
    table('LEAF_RESULTS.tsv',leafrows);table('PREFIX_RESULTS.tsv',stemrows)
    table('PREDICTION_TABLE.tsv',[{k:x[k] for k in ('edition','id','raw','stem','leaf','fold','left','right','p_B','p_L','p_R','p_C','prediction_C','left_training_support','right_training_support')} for x in predictions])
    result={'experiment':'GDT1148','decision':overall,'stratum_decisions':decisions,'readers':results,'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'significance':'NOT_CLAIMED'};write('RESULT.json',result)
    print(json.dumps({'decision':overall,'strata':decisions,'summary':{e:{s:{k:v[k] for k in ('events','leaves','prefixes','ain','aiin','capacity','leaf_macro_gain_C','leaf_macro_gain_L','leaf_macro_gain_R')} for s,v in r['strata'].items()} for e,r in results.items()}},indent=2))
if __name__=='__main__':main()
