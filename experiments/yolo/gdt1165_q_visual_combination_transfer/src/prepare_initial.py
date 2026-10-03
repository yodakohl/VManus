#!/usr/bin/env python3
"""Guarded source projection and literal joins only; no visual association fitting."""
import csv,gzip,hashlib,io,json,subprocess
from pathlib import Path
from collections import Counter,defaultdict
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2]
SOURCE='experiments/yolo/gdt1157_cross_situational_visual_words/artifacts/INPUT.json'
CAP='research_registry/proposals/production_origin_supply_20261003/Q_VISUAL_COMBINATION_CAPACITY.json'
SEP='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
DY='gdt278_native_event_inventory.tsv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def query(path,cols,pages,out):
    cmd=['./vmanus-exp','query-tsv',path,'--selector','page','--columns',cols]
    for page in pages:cmd+=['--allow',page]
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,check=True)
    (EXP/'artifacts'/out).write_bytes(gzip.compress(r.stdout,mtime=0))
    rows=list(csv.DictReader(io.StringIO(r.stdout.decode()),delimiter='\t'))
    assert set(x['page'] for x in rows)<=set(pages)
    return rows,{'command':cmd,'guard_stderr':r.stderr.decode(),'projection':'artifacts/'+out,'projection_sha256':sha(EXP/'artifacts'/out),'source_sha256':sha(ROOT/path),'selected_rows':len(rows)}
def main():
    cap=json.loads((ROOT/CAP).read_text());assert sha(ROOT/SOURCE)==cap['source_sha256']
    x=json.loads((ROOT/SOURCE).read_text());pages=x['pages'];assert len(pages)==38 and all(p not in ('f84','f84r','f116v') for p in pages)
    pairs=[p for p in cap['all_pairs'] if p['eligible']];assert len(pairs)==12
    assert all(x['metadata'][p]=={'section':'H','currier':'A','hand':'1'} for p in pages)
    sep,sr=query(SEP,'edition,page,locus,source_group_index,source_group_count,ivtff_group_raw',pages,'SEPARATOR_PROJECTION.tsv.gz')
    dy,dr=query(DY,'page,locus,group_index,dy_closure,source_surface_sha256',pages,'DY_PROJECTION.tsv.gz')
    zl=[r for r in sep if r['edition']=='ZL3b'];assert len({(r['locus'],r['source_group_index']) for r in zl})==len(zl)
    groups={(r['locus'],int(r['source_group_index'])):r for r in zl};legacy=defaultdict(list)
    for r in dy:legacy[(r['locus'],int(r['group_index']))].append(r)
    pagecounts=Counter(r['page'] for r in zl);leaf=dict(zip(pages,x['leaf_ids']));lookup={}
    for i,p in enumerate(pairs):
        assert p['prefixed']=='q'+p['base']
        for q,w in enumerate([p['base'],p['prefixed']]):assert w not in lookup;lookup[w]=(i,q)
    events=[]
    for r in zl:
        word=r['ivtff_group_raw']
        if word not in lookup:continue
        family,q=lookup[word];idx=int(r['source_group_index']);count=int(r['source_group_count']);prev=groups.get((r['locus'],idx-1));matches=[]
        if prev is not None:
            h=hashlib.sha256(prev['ivtff_group_raw'].encode()).hexdigest();matches=[z for z in legacy[(r['locus'],idx-1)] if z['source_surface_sha256']==h]
        values={int(z['dy_closure']) for z in matches};known=idx==1 or len(values)==1
        value=0 if idx==1 or not known else next(iter(values))
        events.append({'family':family,'base':pairs[family]['base'],'sourceid':f"ZL3b|{r['locus']}|{idx}",'page':r['page'],'leaf':leaf[r['page']],'locus':r['locus'],'index':idx,'count':count,'raw':word,'q':q,'prev_formal_DY':value,'prev_DY_unknown':int(not known),'line_start':int(idx==1),'relativepos':(idx-1)/max(count-1,1),'page_n_groups':pagecounts[r['page']],'previous_raw':None if prev is None else prev['ivtff_group_raw'],'previous_match_rows':len(matches)})
    actual={(e['page'],e['raw']) for e in events};mismatches=[]
    for pageidx,page in enumerate(pages):
        for word in lookup:
            expected=int(x['word_presence'][pageidx][x['words'].index(word)]);observed=int((page,word) in actual)
            if expected!=observed:mismatches.append({'page':page,'word':word,'expected':expected,'observed':observed})
    obj={k:x[k] for k in ['pages','leaf_ids','metadata','features','codes_A_B','consensus','representation']}
    obj.update({'experiment':'GDT1165','reader':'ZL3b','pairs':[{'base':p['base'],'prefixed':p['prefixed']} for p in pairs],'base_words':[p['base'] for p in pairs],'base_presence':[[row[x['words'].index(p['base'])] for p in pairs] for row in x['word_presence']],'q_events':events,'page_n_groups':[pagecounts[p] for p in pages],'presence_mismatches':mismatches,'source_1157_sha256':sha(ROOT/SOURCE)})
    dump(EXP/'src/INPUT.json',obj)
    receipt={'experiment':'GDT1165','status':'SOURCE_PREPARATION_PASS' if not mismatches else 'SOURCE_PRESENCE_MISMATCH_STOP','bindings':{p:sha(ROOT/p) for p in [SOURCE,CAP,SEP,DY]},'prepare_sha256':sha(Path(__file__)),'input_sha256':sha(EXP/'src/INPUT.json'),'guards':[sr,dr],'pages':len(pages),'families':len(pairs),'presence_comparisons':38*24,'presence_mismatches':mismatches,'events':len(events),'events_by_family':dict(Counter(e['base'] for e in events)),'previous_DY_unknown':sum(e['prev_DY_unknown'] for e in events),'all_metadata':'H/A/1','semantic_associations_computed':False,'excluded_pair':[p['base'] for p in cap['all_pairs'] if not p['eligible']]}
    dump(EXP/'artifacts/SOURCE_RECEIPT.json',receipt);print(json.dumps({k:receipt[k] for k in ['status','events','previous_DY_unknown','presence_mismatches']}))
if __name__=='__main__':main()
