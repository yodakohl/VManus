"""Execute declared readings and census fixed bilateral chey frames."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def dump(n,x):(E/'artifacts'/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(n,rows,fields):
    with (E/'artifacts'/n).open('w') as f:
        w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
def execute(ends,model):
    x,y,z,w=ends
    left=(y,x);right=(w,z)
    if model['operator']=='DESCRIBE':
        return dict(status='DESCRIPTIVE_UNSCORED',initial=None,final=None,trace=[],asserted_edges=[left,right],error=None)
    state=left[0];trace=[];iterations=2 if model['tail']=='REPEAT' else 1
    for cycle in range(iterations):
        steps=[left,right] if model['operator']=='THEN' else [left]
        if model['operator']=='NOT' and left==right:
            return dict(status='INTERNAL_CONTRADICTION',initial=left[0],final=state,trace=trace,error='SAME_INSTRUCTION_AFFIRMS_AND_FORBIDS_SAME_ROUTE')
        for step,(source,target) in enumerate(steps):
            trace.append(dict(iteration=cycle+1,step=step+1,state_before=state,required_source=source,destination=target,enabled=state==source))
            if state!=source:
                return dict(status='INTERNAL_CONTRADICTION',initial=left[0],final=state,trace=trace,error='SOURCE_PREREQUISITE_FAIL')
            state=target
    return dict(status='COHERENT_UNCONFIRMED',initial=left[0],final=state,trace=trace,error=None)
def main():
    for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    spec=json.loads((E/'src/SPEC.json').read_text());models=json.loads((E/'src/CANDIDATES.json').read_text())
    ps=json.loads((R/spec['paragraphs']).read_text());families=json.loads((R/spec['families']).read_text())
    allowed=set(json.loads((R/spec['scope']).read_text())['allowed_selectors'])
    pairs={(a+x,b+y):(a+'/'+b,x+y) for a,b in families for x in 'rl' for y in 'rl'}
    vocab=set(models[0]['lexicon']);assert all(set(m['lexicon'])==vocab for m in models)
    contexts=collections.defaultdict(list);counts=collections.defaultdict(collections.Counter)
    for n in spec['snapshots']:
        data=json.loads((R/n).read_text())
        for row in data['lines']:
            meta=row['metadata'];assert meta['page'] in allowed and not meta['page'].startswith('f84') and meta['page']!='f116v'
            if meta['kind']!='P':continue
            gs=[dict(zip(data['group_columns'],g)) for g in row['groups']]
            ed=meta['edition'];counts[ed].update(g['ivtff_group_raw'] for g in gs if g['ivtff_group_raw'] in vocab)
            if meta['locus'] in spec['context_loci']:contexts[ed].append(dict(metadata=meta,groups=gs))
    for ed in contexts:
        contexts[ed].sort(key=lambda r:int(r['metadata']['source_row_index']))
        assert [r['metadata']['locus'] for r in contexts[ed]]==spec['context_loci']
    dump('COMPLETE_CONTEXT.json',contexts)
    alignment=[]
    for ed,lines in contexts.items():
        for model in models:
            for line in lines:
                for g in line['groups']:
                    word=g['ivtff_group_raw']
                    alignment.append(dict(edition=ed,model=model['id'],locus=line['metadata']['locus'],source_id=g['source_group_id'],raw=word,left_separator=g['left_separator'],right_separator=g['right_separator'],value=model['lexicon'].get(word,'UNREAD'),hypothetical=word in vocab))
    table('ALIGNMENT.tsv',alignment,list(alignment[0]))
    countrows=[dict(edition=ed,word=word,occurrences=counts[ed][word]) for ed in ['ZL3b','IT2a','RF1b'] for word in sorted(vocab)]
    table('WORD_COUNTS.tsv',countrows,list(countrows[0]))
    all_chey=[];frames=[];frame_paras={}
    for ed,paras in ps.items():
        for p in paras:
            assert p['page'] in allowed and not p['page'].startswith('f84') and p['page']!='f116v'
            for line in p['lines']:
                for i,word in enumerate(line['words']):
                    if word!='chey':continue
                    row=dict(id='H%04d'%(len(all_chey)+1),edition=ed,paragraph=p['id'],leaf=p['leaf'],locus=line['locus'],index=i,source_id=line['source_ids'][i],line=line['words'],line_eligible=line['anchor_eligible'],status='')
                    if not line['anchor_eligible']:row['status']='INELIGIBLE_LINE'
                    elif i<2 or i+2>=len(line['words']):row['status']='NO_TWO_SIDED_SAME_LINE_WINDOW'
                    else:
                        left=pairs.get(tuple(line['words'][i-2:i]));right=pairs.get(tuple(line['words'][i+1:i+3]))
                        if left is None or right is None:row['status']='OUTSIDE_FIXED_FAMILY_INVENTORY'
                        elif left[0]!=right[0]:row['status']='DIFFERENT_FIXED_FAMILIES'
                        else:
                            row['status']='QUALIFYING';row['family']=left[0];row['ends']=left[1]+right[1]
                            row['words']=line['words'][i-2:i+3];frames.append(row)
                            frame_paras[ed+'|'+p['id']]=p
                    all_chey.append(row)
    predictions=[]
    for frame in frames:
        for model in models:
            outcome=execute(frame['ends'],model)
            predictions.append(dict(frame=frame['id'],edition=frame['edition'],locus=frame['locus'],leaf=frame['leaf'],family=frame['family'],model=model['id'],seed=frame['locus']==spec['target'],**outcome))
    # The raw seed is known before the census; require its exact fixed IT words.
    target=next(r for r in contexts['IT2a'] if r['metadata']['locus']==spec['target'])
    words=[g['ivtff_group_raw'] for g in target['groups']]
    assert words==['qoqokeey','olkain','qol','sheedy','qokeor','sheedy','qokal','or','chey','qokar','ol','aiin']
    local=[dict(model=m['id'],**execute('lrrl',m)) for m in models]
    summary=dict(status='COMPLETE_TRIAL_READINGS_NO_INDEPENDENT_MEANING_SELECTION',confirmed_words=0,significance_claim=False,reserve_access=False,
        target=spec['target'],local_outcomes=local,panels={})
    for ed,paras in ps.items():
        rows=[x for x in all_chey if x['edition']==ed];fs=[x for x in frames if x['edition']==ed]
        summary['panels'][ed]=dict(paragraphs=len(paras),all_chey=len(rows),frame_statuses=dict(collections.Counter(x['status'] for x in rows)),qualifying_frames=len(fs),outside_seed_frames=sum(x['locus']!=spec['target'] for x in fs),physical_leaves=sorted({x['leaf'] for x in fs}),independent_meaning_confirmation=0)
    for n,x in [('ALL_CHEY',all_chey),('FRAMES',frames),('PREDICTIONS',predictions),('FRAME_PARAGRAPHS',frame_paras),('RESULT',summary)]:dump(n+'.json',x)
    rows=[dict(model=x['model'],status=x['status'],initial=x['initial'],final=x['final'],error=x['error'] or '',independent_confirmation=0) for x in local]
    table('CANDIDATE_TABLE.tsv',rows,list(rows[0]))
    report=['# Complete hypothetical readings and entire context','','All word values are stipulated. UNREAD groups remain literal. Only the seed is wholly covered.','']
    for model in models:
        report += ['## '+model['id'],'',model['complete_reading'],'']
        for ed,lines in contexts.items():
            report += ['### '+ed,'']
            for line in lines:
                ws=[g['ivtff_group_raw'] for g in line['groups']]
                report += [line['metadata']['locus']+': `'+ ' '.join(ws)+'`','',' · '.join(model['lexicon'].get(w,'⟦'+w+'⟧') for w in ws),'']
    (E/'artifacts/READINGS.md').write_text('\n'.join(report))
    print(json.dumps(summary))
if __name__=='__main__':main()
